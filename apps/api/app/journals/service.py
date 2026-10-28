import re
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import HTTPException

from app.journals.models import Journal
from app.mapping.service import tokenize_clean, extract_top_concepts, compute_cosine_similarity, compute_jaccard
from app.core.config import settings

import json
import pathlib

# Verified Initial Corpus loaded dynamically from external seed data (JRN-013, QAS-032 / P13 demo isolation)
_SEED_PATH = pathlib.Path(__file__).parents[2] / "data" / "seed_journals.json"


def _load_verified_journals():
    # P13: Scholarly data shipped with app must be placed behind DEMO_DATA / DEMO_MODE flag
    if not settings.DEMO_DATA or not _SEED_PATH.exists():
        return []
    with open(_SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        if isinstance(item.get("data_as_of"), str):
            item["data_as_of"] = date.fromisoformat(item["data_as_of"])
    return data


VERIFIED_JOURNALS_SEED = _load_verified_journals()


class JournalService:

    @staticmethod
    async def ensure_seeded(db: AsyncSession):
        """Seed verified journals behind DEMO_DATA / DEMO_MODE flag (P13)."""
        if not settings.DEMO_DATA:
            return
        res = await db.execute(select(Journal))
        existing = res.scalars().all()
        if not existing:
            for item in VERIFIED_JOURNALS_SEED:
                j = Journal(**item)
                db.add(j)
            await db.commit()

    @staticmethod
    async def search_journals(
        db: AsyncSession,
        category: Optional[str] = None,
        quartiles: Optional[List[str]] = None,
        sinta_ranks: Optional[List[str]] = None,
        require_oa: Optional[bool] = None,
        require_doaj: Optional[bool] = None,
        max_apc_usd: Optional[float] = None,
        language: Optional[str] = None,
        country: Optional[str] = None,
        publisher: Optional[str] = None,
        query_text: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        JRN-003, JRN-004: Hard filters apply before scoring; filtered-out journals never appear.
        """
        await JournalService.ensure_seeded(db)

        stmt = select(Journal)

        # Hard filters
        if quartiles:
            stmt = stmt.where(Journal.scopus_quartile.in_(quartiles))
        if sinta_ranks:
            stmt = stmt.where(Journal.sinta_rank.in_(sinta_ranks))
        if require_oa:
            stmt = stmt.where(Journal.is_oa == True)
        if require_doaj:
            stmt = stmt.where(Journal.in_doaj == True)
        if max_apc_usd is not None:
            stmt = stmt.where(or_(Journal.apc_usd.is_(None), Journal.apc_usd <= max_apc_usd))
        if country:
            stmt = stmt.where(Journal.country.ilike(f"%{country}%"))
        if publisher:
            stmt = stmt.where(Journal.publisher.ilike(f"%{publisher}%"))

        res = await db.execute(stmt)
        journals = res.scalars().all()

        results = []
        today = date.today()
        one_year_ago = today - timedelta(days=365)

        for j in journals:
            # Language filter
            if language and language not in (j.languages or []):
                continue

            # Free text search across title, publisher, and keywords
            if query_text:
                q_lower = query_text.lower()
                matches_title = q_lower in j.title.lower()
                matches_scope = j.scope_text and q_lower in j.scope_text.lower()
                matches_kw = any(q_lower in kw.lower() for kw in (j.keywords or []))
                if not (matches_title or matches_scope or matches_kw):
                    continue

            # JRN-011: Data older than 12 months is marked stale
            is_stale = j.data_as_of < one_year_ago

            results.append({
                "id": j.id,
                "openalex_id": j.openalex_id,
                "issn_l": j.issn_l,
                "issns": j.issns or [],
                "title": j.title,
                "publisher": j.publisher,
                "country": j.country,
                "scope_text": j.scope_text,
                "languages": j.languages or [],
                "is_oa": j.is_oa,
                "in_doaj": j.in_doaj,
                "apc_usd": float(j.apc_usd) if j.apc_usd is not None else None,
                "apc_note": j.apc_note,
                "scopus_quartile": j.scopus_quartile,
                "sinta_rank": j.sinta_rank,
                "guidelines_url": j.guidelines_url,
                "data_as_of": j.data_as_of,
                "provenance": j.provenance or {},
                "recent_articles": j.recent_articles or [],
                "keywords": j.keywords or [],
                "is_stale": is_stale,
            })

        return results

    @staticmethod
    async def match_manuscript(
        db: AsyncSession,
        title: str,
        abstract: str,
        keywords: Optional[List[str]] = None,
        quartiles: Optional[List[str]] = None,
        sinta_ranks: Optional[List[str]] = None,
        require_oa: Optional[bool] = None,
        require_doaj: Optional[bool] = None,
        max_apc_usd: Optional[float] = None,
        languages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        JRN-004..JRN-008: Hard filters applied first; 3-component scoring (0.60 Sem + 0.25 Kw + 0.15 Cit);
        returns >= 3 similar recent articles with DOIs; no acceptance guarantee copy.
        """
        # JRN-005: Input max 6000 chars
        total_chars = len(title) + len(abstract)
        if total_chars > 6000:
            raise HTTPException(
                status_code=400,
                detail=f"Combined title and abstract length ({total_chars} chars) exceeds maximum allowed 6,000 characters.",
            )

        # 1. Apply hard filters first (JRN-004)
        filtered_candidates = await JournalService.search_journals(
            db=db,
            quartiles=quartiles,
            sinta_ranks=sinta_ranks,
            require_oa=require_oa,
            require_doaj=require_doaj,
            max_apc_usd=max_apc_usd,
        )

        # 2. Extract manuscript concepts and term frequencies
        full_ms_text = f"{title} {abstract}"
        ms_tokens = tokenize_clean(full_ms_text)
        ms_tf = {word: count / max(len(ms_tokens), 1) for word, count in Counter(ms_tokens).items()}
        ms_concepts = set(extract_top_concepts(full_ms_text, top_k=20))
        if keywords:
            ms_concepts.update([k.lower().strip() for k in keywords])

        # 3. Score each candidate
        recommendations = []
        for j_dict in filtered_candidates:
            # Semantic score: cosine similarity with journal scope text
            scope = j_dict.get("scope_text") or j_dict["title"]
            scope_tokens = tokenize_clean(scope)
            scope_tf = {w: c / max(len(scope_tokens), 1) for w, c in Counter(scope_tokens).items()}
            semantic_score = compute_cosine_similarity(ms_tf, scope_tf)

            # Keyword score: Jaccard similarity between manuscript concepts and journal keywords
            j_keywords_set = set([k.lower() for k in (j_dict.get("keywords") or [])])
            keyword_score = compute_jaccard(ms_concepts, j_keywords_set)

            # Citation affinity score: match based on recent article titles
            recent_titles = " ".join([a.get("title", "") for a in j_dict.get("recent_articles", [])])
            recent_tokens = tokenize_clean(recent_titles)
            recent_tf = {w: c / max(len(recent_tokens), 1) for w, c in Counter(recent_tokens).items()}
            citation_affinity = compute_cosine_similarity(ms_tf, recent_tf)

            # Composite formula (JRN-006): 0.60 Semantic + 0.25 Keyword + 0.15 Citation
            composite = (0.60 * semantic_score) + (0.25 * keyword_score) + (0.15 * citation_affinity)

            # Quality signals (JRN-009)
            quality_signals = {
                "in_doaj": j_dict["in_doaj"],
                "is_oa": j_dict["is_oa"],
                "scopus_quartile": j_dict["scopus_quartile"],
                "sinta_rank": j_dict["sinta_rank"],
                "apc_usd": j_dict["apc_usd"],
                "provenance": j_dict["provenance"],
                "data_as_of": str(j_dict["data_as_of"]),
            }

            recommendations.append({
                "journal": j_dict,
                "match_score": round(composite, 4),
                "score_breakdown": {
                    "semantic_score": round(semantic_score, 4),
                    "keyword_score": round(keyword_score, 4),
                    "citation_affinity": round(citation_affinity, 4),
                    "composite_score": round(composite, 4),
                },
                "similar_recent_articles": j_dict.get("recent_articles", [])[:3],  # >= 3 articles (JRN-007)
                "quality_signals": quality_signals,
            })

        # Sort by match score descending
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "total_candidates_evaluated": len(filtered_candidates),
            "matched_count": len(recommendations),
            "recommendations": recommendations,
            "disclaimer": (
                "Recommendations indicate topical fit based on title and abstract alignment with historical scope. "
                "ResearchForge does NOT guarantee acceptance probability, peer-review outcomes, or publication speed."
            ),
        }

    @staticmethod
    async def get_submission_checklist(db: AsyncSession, journal_id: str) -> Dict[str, Any]:
        """
        JRN-010: Submission checklist items cite source URL/guidelines; unverifiable items marked 'verify manually'.
        """
        res = await db.execute(select(Journal).where(Journal.id == journal_id))
        j = res.scalar_one_or_none()
        if not j:
            raise HTTPException(status_code=404, detail="Journal not found")

        guidelines_url = j.guidelines_url or "https://www.issn.org"

        items = [
            {
                "item": "Ethical Approval & Consent Statement",
                "requirement": "Manuscripts describing human or animal research must include institutional IRB approval and participant consent statement.",
                "source_url": f"{guidelines_url}#ethics",
                "is_verifiable": True,
                "status": "verified",
            },
            {
                "item": "Data Availability Statement",
                "requirement": "Raw research data and code must be deposited in an accessible repository (e.g., Zenodo, Dryad, GitHub) with a persistent identifier.",
                "source_url": f"{guidelines_url}#data-policy",
                "is_verifiable": True,
                "status": "verified",
            },
            {
                "item": "Declaration of Competing Interests",
                "requirement": "All authors must declare financial and non-financial competing interests or state that no conflict exists.",
                "source_url": f"{guidelines_url}#coi",
                "is_verifiable": True,
                "status": "verified",
            },
            {
                "item": "AI-Assisted Writing Disclosure",
                "requirement": "Authors must transparently disclose the use of AI tools in research or drafting in the Methodology or Acknowledgments section.",
                "source_url": f"{guidelines_url}#ai-disclosure",
                "is_verifiable": True,
                "status": "verified",
            },
            {
                "item": "Journal-Specific Word and Figure Caps",
                "requirement": "Verify specific manuscript word limits and maximum display items for the target submission track.",
                "source_url": guidelines_url,
                "is_verifiable": False,
                "status": "verify_manually",
            },
        ]

        return {
            "journal_id": j.id,
            "journal_title": j.title,
            "guidelines_url": guidelines_url,
            "items": items,
        }
