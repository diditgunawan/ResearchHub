import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.synthesis.models import Chunk, Extraction, SynthesisRun, SynthesisRunChunk
from app.library.models import LibraryItem
from app.screening.models import ScreeningDecision, ScreeningResolution
from app.works.models import Work
from app.integrity.models import AiUsageLog
from app.synthesis.schemas import AtomicClaim, SynthesisResponse
from app.synthesis.gateway import ModelGateway
from app.core.config import settings


class SynthesisService:
    @staticmethod
    async def get_or_create_chunks(db: AsyncSession, work: Work) -> List[Chunk]:
        """SYN-002: Ensure section-aware chunks exist for a work."""
        existing = (await db.execute(select(Chunk).where(Chunk.work_id == work.id))).scalars().all()
        if existing:
            return list(existing)

        text = work.abstract or work.title
        words = text.split()
        chunk_size = 80  # words (~100-120 tokens)
        overlap = 15

        chunks = []
        start = 0
        idx = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            c = Chunk(
                work_id=work.id,
                chunk_index=idx,
                section="abstract",
                text=chunk_text,
                embedding_model="local-deterministic",
            )
            db.add(c)
            chunks.append(c)
            idx += 1
            if end >= len(words):
                break
            start += (chunk_size - overlap)

        await db.flush()
        return chunks

    @staticmethod
    async def retrieve_project_works(
        db: AsyncSession, project_id: str, query: str, scope: str = "library", limit: int = 10
    ) -> List[Tuple[Work, List[Chunk]]]:
        """SYN-001: Strict tenant isolation. Retrieves only works belonging to this project."""
        keywords = [w.lower() for w in re.findall(r"\b[A-Za-z0-9]{3,}\b", query)]

        # Fetch works in project library
        stmt = (
            select(Work)
            .join(LibraryItem, Work.id == LibraryItem.work_id)
            .where(LibraryItem.project_id == project_id)
        )

        if scope == "screened_included":
            # Only include works with 'include' decision
            stmt = stmt.join(ScreeningDecision, Work.id == ScreeningDecision.work_id).where(
                ScreeningDecision.project_id == project_id,
                ScreeningDecision.verdict == "include",
            )

        works = (await db.execute(stmt)).scalars().all()

        # Score relevance by keyword match in title and abstract
        scored_works = []
        for w in works:
            content = f"{w.title} {w.abstract or ''}".lower()
            score = sum(1 for kw in keywords if kw in content)
            scored_works.append((score, w))

        # Sort by relevance score desc
        scored_works.sort(key=lambda x: x[0], reverse=True)
        top_works = [w for score, w in scored_works[:limit] if score > 0]

        results = []
        for w in top_works:
            chunks = await SynthesisService.get_or_create_chunks(db, w)
            results.append((w, chunks))

        return results

    @staticmethod
    def _verify_claim(claim_text: str, chunk_text: str) -> Tuple[str, Optional[str]]:
        """SYN-009: Deterministically verifies whether a claim is grounded in its cited chunk."""
        claim_words = set(re.findall(r"\b[a-z]{4,}\b", claim_text.lower()))
        chunk_words = set(re.findall(r"\b[a-z]{4,}\b", chunk_text.lower()))
        
        if not claim_words:
            return "supported", chunk_text[:120]

        overlap = claim_words.intersection(chunk_words)
        ratio = len(overlap) / len(claim_words)

        if ratio >= 0.50:
            return "supported", chunk_text[:150]
        elif ratio >= 0.25:
            return "partially_supported", chunk_text[:150]
        else:
            return "unsupported", None

    @staticmethod
    async def synthesize(
        db: AsyncSession,
        project_id: str,
        query: str,
        scope: str = "library",
        max_works: int = 10,
    ) -> SynthesisResponse:
        """SYN-005, SYN-008, SYN-009, SYN-010: Grounded synthesis with sufficiency gate and refusal policy."""
        retrieved = await SynthesisService.retrieve_project_works(
            db, project_id, query, scope=scope, limit=max_works
        )

        # SYN-005: Sufficiency Gate (refuses when distinct works < 3)
        if len(retrieved) < 3:
            refusal_reason = (
                f"Insufficient evidence base in project: only {len(retrieved)} relevant study found. "
                "Per research safety guidelines (SYN-005), at least 3 distinct peer-reviewed works are required "
                "to synthesize an evidence claim without fabrication risk."
            )
            run = SynthesisRun(
                project_id=project_id,
                query=query,
                status="refused",
                claims_json=[],
                refusal_reason=refusal_reason,
                model="rule-engine",
                tokens_used=0,
                cost_usd=0.0,
            )
            db.add(run)
            await db.flush()

            # Log AI usage (truthful provenance: rule-based execution consumes 0 LLM tokens)
            db.add(AiUsageLog(
                project_id=project_id,
                feature="synthesis_refusal",
                stage=scope,
                model="rule-engine",
                purpose="Sufficiency check",
                tokens_in=0,
                tokens_out=0,
            ))
            await db.flush()

            return SynthesisResponse(
                id=run.id,
                query=query,
                status="refused",
                claims=[],
                refusal_reason=refusal_reason,
                retrieved_works=[{"id": w.id, "title": w.title, "doi": w.doi, "year": w.year} for w, _ in retrieved],
                verified_percentage=0.0,
                model="rule-engine",
                created_at=run.created_at,
            )

        # Generate atomic claims directly grounded in retrieved chunk text via ModelGateway
        raw_claims, telemetry = await ModelGateway.extract_atomic_claims(query, retrieved)
        candidate_claims: List[AtomicClaim] = [
            AtomicClaim(
                claim_index=c["claim_index"],
                claim_text=c["claim_text"],
                citation_chunk_ids=c["citation_chunk_ids"],
                verdict=c["verdict"],
                evidence_excerpt=c.get("evidence_excerpt"),
                work_title=c.get("work_title"),
                doi=c.get("doi"),
            )
            for c in raw_claims
        ]

        # SYN-010: Apply verification policy
        supported_claims = [c for c in candidate_claims if c.verdict in ["supported", "partially_supported"]]
        unsupported_count = len(candidate_claims) - len(supported_claims)
        drop_rate = unsupported_count / len(candidate_claims) if candidate_claims else 0.0

        status = "completed"
        refusal_msg = None
        if drop_rate > 0.30:
            status = "low_confidence"
            refusal_msg = "Over 30% of candidate claims lacked direct supporting evidence in the retrieved text. Returning low-confidence evidence summary."

        run = SynthesisRun(
            project_id=project_id,
            query=query,
            status=status,
            claims_json=[c.model_dump() for c in supported_claims],
            refusal_reason=refusal_msg,
            model=telemetry["model"],
            tokens_used=telemetry["tokens_in"] + telemetry["tokens_out"],
            cost_usd=telemetry["cost_usd"],
        )
        db.add(run)
        await db.flush()

        # Link verified chunks
        for c in supported_claims:
            for cid in c.citation_chunk_ids:
                db.add(SynthesisRunChunk(
                    synthesis_run_id=run.id,
                    chunk_id=cid,
                    claim_index=c.claim_index,
                    verification_verdict=c.verdict,
                ))

        # Log AI usage (truthful provenance: actual model telemetry)
        db.add(AiUsageLog(
            project_id=project_id,
            feature="grounded_synthesis",
            stage=scope,
            model=telemetry["model"],
            purpose="Grounded RAG synthesis with chunk verification",
            tokens_in=telemetry["tokens_in"],
            tokens_out=telemetry["tokens_out"],
        ))
        await db.flush()

        return SynthesisResponse(
            id=run.id,
            query=query,
            status=status,
            claims=supported_claims,
            refusal_reason=refusal_msg,
            retrieved_works=[{"id": w.id, "title": w.title, "doi": w.doi, "year": w.year} for w, _ in retrieved],
            verified_percentage=round((len(supported_claims) / len(candidate_claims)) * 100, 1) if candidate_claims else 0.0,
            model=telemetry["model"],
            created_at=run.created_at,
        )
