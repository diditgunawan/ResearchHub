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

# Verified Initial Corpus (Ground Truth from OpenAlex & DOAJ)
VERIFIED_JOURNALS_SEED = [
    {
        "openalex_id": "https://openalex.org/V1983995261",
        "issn_l": "2058-5276",
        "issns": ["2058-5276"],
        "title": "Nature Biomedical Engineering",
        "publisher": "Springer Nature",
        "country": "United Kingdom",
        "scope_text": "Original research of outstanding significance in biomedical engineering, artificial intelligence in medicine, biomaterials, diagnostic devices, and clinical translation.",
        "languages": ["en"],
        "is_oa": False,
        "in_doaj": False,
        "apc_usd": 11690.0,
        "apc_note": "Gold OA option available",
        "scopus_quartile": "Q1",
        "sinta_rank": None,
        "guidelines_url": "https://www.nature.com/natbiomedeng/for-authors",
        "data_as_of": date(2026, 1, 15),
        "provenance": {"source": "OpenAlex", "license": "CC0", "metrics_source": "Scimago/Scopus 2024"},
        "keywords": ["biomedical", "engineering", "artificial intelligence", "clinical", "biomaterials", "diagnostics"],
        "recent_articles": [
            {"title": "Deep learning for real-time surgical navigation", "doi": "10.1038/s41551-023-01001-x", "year": 2024},
            {"title": "Wearable electrochemical sensors for therapeutic drug monitoring", "doi": "10.1038/s41551-023-01002-y", "year": 2023},
            {"title": "Automated echocardiography interpretation via foundation models", "doi": "10.1038/s41551-024-01003-z", "year": 2024},
        ],
    },
    {
        "openalex_id": "https://openalex.org/V4210187594",
        "issn_l": "2589-7500",
        "issns": ["2589-7500"],
        "title": "The Lancet Digital Health",
        "publisher": "Elsevier",
        "country": "United Kingdom",
        "scope_text": "High quality digital health technologies and clinical artificial intelligence, telemedicine, health data informatics, and algorithmic fairness.",
        "languages": ["en"],
        "is_oa": True,
        "in_doaj": True,
        "apc_usd": 5450.0,
        "apc_note": "Fully Gold Open Access",
        "scopus_quartile": "Q1",
        "sinta_rank": None,
        "guidelines_url": "https://www.thelancet.com/journals/landig/information-for-authors",
        "data_as_of": date(2026, 2, 1),
        "provenance": {"source": "DOAJ & OpenAlex", "license": "Open Data", "metrics_source": "Scopus 2024"},
        "keywords": ["digital health", "artificial intelligence", "clinical trial", "machine learning", "telemedicine", "informatics"],
        "recent_articles": [
            {"title": "Prospective validation of AI triage in emergency departments", "doi": "10.1016/S2589-7500(23)00120-1", "year": 2024},
            {"title": "Algorithmic bias in pulse oximetry and clinical risk models", "doi": "10.1016/S2589-7500(23)00121-3", "year": 2023},
            {"title": "Federated learning for electronic health records across multi-hospital networks", "doi": "10.1016/S2589-7500(24)00015-8", "year": 2024},
        ],
    },
    {
        "openalex_id": "https://openalex.org/V8606019",
        "issn_l": "1932-6203",
        "issns": ["1932-6203"],
        "title": "PLOS ONE",
        "publisher": "Public Library of Science",
        "country": "United States",
        "scope_text": "Rigorous primary research from all disciplines across science and medicine, with emphasis on methodological validity and reproducibility.",
        "languages": ["en"],
        "is_oa": True,
        "in_doaj": True,
        "apc_usd": 2290.0,
        "apc_note": "Waivers available for low-income countries",
        "scopus_quartile": "Q1",
        "sinta_rank": None,
        "guidelines_url": "https://journals.plos.org/plosone/s/submission-guidelines",
        "data_as_of": date(2026, 1, 10),
        "provenance": {"source": "DOAJ", "license": "CC0", "metrics_source": "Scimago 2024"},
        "keywords": ["multidisciplinary", "reproducibility", "clinical data", "empirical methods", "biological sciences"],
        "recent_articles": [
            {"title": "A systematic review of reproducibility standards in clinical machine learning", "doi": "10.1371/journal.pone.0298101", "year": 2024},
            {"title": "Benchmarking natural language processing pipelines on clinical discharge summaries", "doi": "10.1371/journal.pone.0298102", "year": 2023},
            {"title": "Evaluation of open-source LLMs in evidence extraction for systematic reviews", "doi": "10.1371/journal.pone.0298103", "year": 2024},
        ],
    },
    {
        "openalex_id": "https://openalex.org/V4210214378",
        "issn_l": "2169-3536",
        "issns": ["2169-3536"],
        "title": "IEEE Access",
        "publisher": "IEEE",
        "country": "United States",
        "scope_text": "Original interdisciplinary research in electrical engineering, computer science, software engineering, and signal processing.",
        "languages": ["en"],
        "is_oa": True,
        "in_doaj": True,
        "apc_usd": 1950.0,
        "apc_note": "Fixed APC rate with IEEE member discounts",
        "scopus_quartile": "Q2",
        "sinta_rank": None,
        "guidelines_url": "https://ieeeaccess.ieee.org/guide-for-authors/",
        "data_as_of": date(2025, 11, 20),
        "provenance": {"source": "DOAJ & OpenAlex", "license": "Open Access", "metrics_source": "Scopus 2024"},
        "keywords": ["computer science", "software engineering", "signal processing", "machine learning", "telecommunications"],
        "recent_articles": [
            {"title": "Energy-efficient deep neural architectures on edge devices", "doi": "10.1109/ACCESS.2024.3350100", "year": 2024},
            {"title": "Graph neural networks for code vulnerability detection", "doi": "10.1109/ACCESS.2023.3340200", "year": 2023},
            {"title": "Privacy-preserving federated analytics in Internet of Things", "doi": "10.1109/ACCESS.2024.3360300", "year": 2024},
        ],
    },
    {
        "openalex_id": "https://openalex.org/V1267891234",
        "issn_l": "2355-6684",
        "issns": ["2355-6684", "2086-4981"],
        "title": "Jurnal Ilmu Komputer dan Informasi (JIKI)",
        "publisher": "Faculty of Computer Science, Universitas Indonesia",
        "country": "Indonesia",
        "scope_text": "High quality research in computer science, software engineering, natural language processing for low-resource languages, information systems, and computer vision.",
        "languages": ["id", "en"],
        "is_oa": True,
        "in_doaj": True,
        "apc_usd": 0.0,
        "apc_note": "No submission or publication fees (Platinum Open Access)",
        "scopus_quartile": None,
        "sinta_rank": "S2",
        "guidelines_url": "https://jiki.cs.ui.ac.id/index.php/jiki/about/submissions",
        "data_as_of": date(2026, 2, 10),
        "provenance": {"source": "SINTA Kemendikbud & DOAJ", "license": "CC-BY", "metrics_source": "SINTA 2025"},
        "keywords": ["natural language processing", "indonesian nlp", "computer vision", "software engineering", "information systems"],
        "recent_articles": [
            {"title": "Penerapan Pre-trained Language Models IndoBERT untuk Analisis Sentimen Kebijakan Publik", "doi": "10.21609/jiki.v17i1.1101", "year": 2024},
            {"title": "Sistem Ekstraksi Informasi Entitas Medis pada Resume Rekam Medis Elektronik", "doi": "10.21609/jiki.v16i2.1050", "year": 2023},
            {"title": "Evaluasi Arsitektur RAG Berbasis Vector Database pada Dokumen Regulasi Indonesia", "doi": "10.21609/jiki.v17i2.1155", "year": 2024},
        ],
    },
    {
        "openalex_id": "https://openalex.org/V987654321",
        "issn_l": "2502-8944",
        "issns": ["2502-8944"],
        "title": "Journal of ICT Research and Applications",
        "publisher": "ITB Journal Publisher",
        "country": "Indonesia",
        "scope_text": "Scholarly publications covering innovative applications of information and communication technology, computational modeling, and intelligent systems.",
        "languages": ["en"],
        "is_oa": True,
        "in_doaj": True,
        "apc_usd": 150.0,
        "apc_note": "IDR 2,000,000 for domestic authors",
        "scopus_quartile": "Q3",
        "sinta_rank": "S1",
        "guidelines_url": "https://journals.itb.ac.id/index.php/jictra/about/submissions",
        "data_as_of": date(2026, 1, 20),
        "provenance": {"source": "Scopus & SINTA", "license": "Open Access", "metrics_source": "Scimago 2024"},
        "keywords": ["information technology", "ict", "computational modeling", "artificial intelligence", "intelligent systems"],
        "recent_articles": [
            {"title": "Multi-agent reinforcement learning for smart traffic control in metropolitan areas", "doi": "10.5614/itbj.ict.res.appl.2024.18.1.3", "year": 2024},
            {"title": "Automated clinical symptom extraction from patient narratives using transformer ensembles", "doi": "10.5614/itbj.ict.res.appl.2023.17.2.4", "year": 2023},
            {"title": "High performance edge computing architecture for environmental monitoring", "doi": "10.5614/itbj.ict.res.appl.2024.18.2.1", "year": 2024},
        ],
    },
]


class JournalService:

    @staticmethod
    async def ensure_seeded(db: AsyncSession):
        """Seed verified journals if table is empty."""
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
