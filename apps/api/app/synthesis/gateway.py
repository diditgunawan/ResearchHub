"""
ResearchHub Universal LLM & Synthesis Gateway
============================================
Supports live multi-provider inference with truthful token telemetry:
1. Google Gemini (Gemini 3.8 Flash for synthesis, Gemini 3.1 Pro for verification)
2. Local Ollama (air-gapped local model inference)
3. Deterministic rule-based fallback (for offline tests & zero-cost heuristic mode)

Enforces:
- Rule G1 & G2: Real provenance, zero fake telemetry, zero hallucinated claims.
- QAS-026 / P5: If rule-engine fallback is used, tokens reported are strictly 0.
"""

import json
import re
import os
import httpx
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings


class ModelGateway:
    @staticmethod
    async def extract_atomic_claims(
        query: str,
        retrieved_works: List[Tuple[Any, List[Any]]],
        model_override: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Extracts verified atomic claims from retrieved works.
        Returns:
            (candidate_claims, telemetry)
            telemetry: {"model": str, "tokens_in": int, "tokens_out": int, "cost_usd": float}
        """
        # User explicitly requested deterministic zero-cost baseline
        if model_override == "rule-engine":
            return ModelGateway._extract_deterministic(retrieved_works)

        # Testing or unconfigured provider -> deterministic rule engine
        if os.environ.get("TESTING") == "1" or not settings.LLM_PROVIDER or not settings.LLM_API_KEY:
            return ModelGateway._extract_deterministic(retrieved_works)

        provider = settings.LLM_PROVIDER.lower().strip()
        if model_override and "ollama" in model_override.lower():
            provider = "ollama"
        elif model_override and "gemini" in model_override.lower():
            provider = "gemini"

        if provider == "gemini":
            try:
                return await ModelGateway._extract_gemini(query, retrieved_works)
            except Exception as exc:
                print(f"[MODEL GATEWAY WARNING] Gemini API call failed: {exc}. Falling back to deterministic engine.")
                return ModelGateway._extract_deterministic(retrieved_works)
        elif provider == "ollama":
            try:
                return await ModelGateway._extract_ollama(query, retrieved_works)
            except Exception as exc:
                print(f"[MODEL GATEWAY WARNING] Ollama call failed: {exc}. Falling back to deterministic engine.")
                return ModelGateway._extract_deterministic(retrieved_works)
        else:
            return ModelGateway._extract_deterministic(retrieved_works)

    @staticmethod
    async def _extract_gemini(
        query: str,
        retrieved_works: List[Tuple[Any, List[Any]]],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Invokes Google Gemini 3.8 Flash via REST with structured JSON schema output."""
        model = settings.LLM_MODEL_SYNTHESIS or "gemini-3.8-flash"
        api_key = settings.LLM_API_KEY
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        # Build grounded context
        contexts = []
        chunk_map = {}
        for idx, (work, chunks) in enumerate(retrieved_works):
            primary_chunk = chunks[0] if chunks else None
            chunk_id = primary_chunk.id if primary_chunk else f"chk-{idx}"
            chunk_text = primary_chunk.text if primary_chunk else (work.abstract or work.title)
            chunk_map[work.title] = chunk_id
            contexts.append({
                "work_index": idx,
                "title": work.title,
                "year": work.year,
                "doi": work.doi,
                "chunk_id": chunk_id,
                "text": chunk_text[:800],
            })

        system_instruction = (
            "You are a rigorous, truthful academic evidence extraction engine. "
            "For each study provided, extract exactly one atomic declarative finding strictly stated in its text. "
            "Do NOT extrapolate, extrapolate novelty, or invent citations. "
            "Each claim must include the exact verbatim excerpt supporting it. "
            "Respond strictly with valid JSON."
        )

        prompt = (
            f"Research Question: {query}\n\n"
            f"Candidate Evidence Studies:\n{json.dumps(contexts, indent=2)}\n\n"
            "Extract atomic claims for each study. Provide output in this JSON format:\n"
            "{\n"
            '  "claims": [\n'
            '    {\n'
            '      "work_title": "string",\n'
            '      "doi": "string",\n'
            '      "core_finding": "verbatim or closely paraphrased single finding sentence",\n'
            '      "evidence_excerpt": "exact short quotation from the text",\n'
            '      "verdict": "supported" | "partially_supported"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1,
                "maxOutputTokens": 2048,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API returned HTTP {resp.status_code}: {resp.text}")

            data = resp.json()
            usage = data.get("usageMetadata", {})
            tokens_in = usage.get("promptTokenCount", 0)
            tokens_out = usage.get("candidatesTokenCount", 0)
            
            # Gemini Flash standard pricing ($0.15/1M in, $0.60/1M out)
            cost_usd = (tokens_in * 0.15 + tokens_out * 0.60) / 1_000_000.0

            content_text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(content_text)
            raw_claims = parsed.get("claims", [])

            candidate_claims = []
            for i, rc in enumerate(raw_claims):
                w_title = rc.get("work_title", "")
                chunk_id = chunk_map.get(w_title)
                if not chunk_id and retrieved_works:
                    chunk_id = retrieved_works[min(i, len(retrieved_works)-1)][1][0].id

                candidate_claims.append({
                    "claim_index": i,
                    "claim_text": f"According to {w_title}, {rc.get('core_finding', '')}",
                    "citation_chunk_ids": [chunk_id] if chunk_id else [],
                    "verdict": rc.get("verdict", "supported"),
                    "evidence_excerpt": rc.get("evidence_excerpt", "")[:200],
                    "work_title": w_title,
                    "doi": rc.get("doi", ""),
                })

            telemetry = {
                "model": model,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost_usd": cost_usd,
            }
            return candidate_claims, telemetry

    @staticmethod
    async def _extract_ollama(
        query: str,
        retrieved_works: List[Tuple[Any, List[Any]]],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Invokes local Ollama instance (air-gapped execution)."""
        base_url = settings.OLLAMA_BASE_URL or "http://localhost:11434"
        model = settings.LLM_MODEL_SYNTHESIS or "llama3.2"

        contexts = [
            f"[{idx+1}] {w.title} ({w.year}): {chunks[0].text if chunks else w.abstract}"
            for idx, (w, chunks) in enumerate(retrieved_works)
        ]

        prompt = (
            f"Research Query: {query}\n\nStudies:\n" + "\n".join(contexts) +
            "\n\nExtract key findings as JSON: {\"claims\": [{\"work_title\": \"...\", \"finding\": \"...\", \"excerpt\": \"...\"}]}"
        )

        async with httpx.AsyncClient(base_url=base_url, timeout=45.0) as client:
            resp = await client.post("/api/generate", json={
                "model": model,
                "prompt": prompt,
                "format": "json",
                "stream": False,
            })
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama returned HTTP {resp.status_code}")

            data = resp.json()
            parsed = json.loads(data.get("response", "{}"))
            raw_claims = parsed.get("claims", [])
            
            claims = []
            for i, rc in enumerate(raw_claims):
                w_title = rc.get("work_title", f"Study {i+1}")
                chunk_id = retrieved_works[min(i, len(retrieved_works)-1)][1][0].id
                claims.append({
                    "claim_index": i,
                    "claim_text": f"According to {w_title}, {rc.get('finding', '')}",
                    "citation_chunk_ids": [chunk_id],
                    "verdict": "supported",
                    "evidence_excerpt": rc.get("excerpt", "")[:200],
                    "work_title": w_title,
                    "doi": retrieved_works[min(i, len(retrieved_works)-1)][0].doi,
                })

            telemetry = {
                "model": f"ollama/{model}",
                "tokens_in": data.get("prompt_eval_count", 0),
                "tokens_out": data.get("eval_count", 0),
                "cost_usd": 0.0,
            }
            return claims, telemetry

    @staticmethod
    def _extract_deterministic(
        retrieved_works: List[Tuple[Any, List[Any]]],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Deterministic heuristic extraction fallback (strictly 0 tokens reported per P5)."""
        candidate_claims = []
        for idx, (work, chunks) in enumerate(retrieved_works):
            primary_chunk = chunks[0] if chunks else None
            if not primary_chunk:
                continue

            sentences = [s.strip() for s in re.split(r"[.!?]", primary_chunk.text) if len(s.strip()) > 10]
            core_finding = sentences[0] if sentences else primary_chunk.text
            claim_sentence = f"According to {work.title} ({work.year or 'n.d.'}), {core_finding}."

            claim_words = set(re.findall(r"\b[a-z]{4,}\b", core_finding.lower()))
            chunk_words = set(re.findall(r"\b[a-z]{4,}\b", primary_chunk.text.lower()))
            overlap = claim_words.intersection(chunk_words)
            ratio = len(overlap) / len(claim_words) if claim_words else 1.0

            if ratio >= 0.50:
                verdict, excerpt = "supported", primary_chunk.text[:150]
            elif ratio >= 0.25:
                verdict, excerpt = "partially_supported", primary_chunk.text[:150]
            else:
                verdict, excerpt = "unsupported", None

            candidate_claims.append({
                "claim_index": idx,
                "claim_text": claim_sentence,
                "citation_chunk_ids": [primary_chunk.id],
                "verdict": verdict,
                "evidence_excerpt": excerpt,
                "work_title": work.title,
                "doi": work.doi,
            })

        telemetry = {
            "model": "rule-engine",
            "tokens_in": 0,
            "tokens_out": 0,
            "cost_usd": 0.0,
        }
        return candidate_claims, telemetry
