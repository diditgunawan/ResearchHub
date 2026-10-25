# PROJECT_STATE (Single Source of Project Evolution)
**Last updated:** October 2026 by Antigravity (Phase 6 Launch Ready & Hardened)

## Current Milestone
**Phase 6: Launch Ready & Hardened (Milestones M0 through M5 Complete)**
All foundational, core application, and hardening milestones are implemented, passing full unit tests, live end-to-end simulation, concurrency stress verification, and external IEEE dataset benchmarks.

---

## Completed Milestones (with Requirement IDs & Artifacts)

### M0: Foundations (ENG-001..012, QAS-001..006)
- **RFC 7807 Problem Details**: Comprehensive middleware and custom exception handlers returning structured `request_id`, status, code, and instance across all API responses.
- **Passwordless Magic-Link Auth**: Ephemeral token issuance, session exchange, and HTTP-only session cookie handling.
- **Tenant RBAC Matrix**: Project membership enforcement (`owner`, `reviewer`, `viewer`).
- **Health & Readiness Probes**: `/healthz` (liveness) and `/readyz` (database connectivity).

### M1: Data & Library (DAT-001..018, LIB-001..016)
- **Federated Scholarly Search**: Connectors for OpenAlex and Crossref with 8.0s circuit breaker and polite `mailto:` headers.
- **Bibliographic Parsers**: Line-referenced parser for RIS, BibTeX, and CSV with parse report generation and roundtrip export engine.
- **Library Management**: Server-side paginated library queries and collections.

### M2: Systematic Screening & PRISMA 2020 (SCR-001..018)
- **Versioned Review Protocols**: PICO criteria modeling with immutable version increments.
- **Blind Dual-Reviewer Workflow**: Independent screening queues and append-only decision logging.
- **Inter-Rater Reliability Engine**: Exact mathematical computation of Observed Agreement ($P_o$) and Cohen's Kappa ($\kappa$).
- **PRISMA 2020 Flow Engine**: Mathematical arithmetic reconciliation ($\Delta = 0$) across identification, screening, exclusion, and inclusion stages.

### M3: Grounded Synthesis & AI Ethics (SYN-001..020, ETH-001..014)
- **Tenant-Isolated RAG Engine**: Vector similarity retrieval gated on project tenancy.
- **Sufficiency Gate Refusal Policy**: Hard refusal (`INSUFFICIENT_EVIDENCE`) when distinct retrieved works $< 3$.
- **Atomic Claim Extraction**: Every claim mapped to citation chunk UUIDs with verification badges (`supported` / `partially_supported`).
- **Retraction Watch Integration**: Reference integrity auditor scanning target DOIs.
- **Bilingual AI Disclosure**: Auto-generator producing ICMJE/COPE-compliant English and SINTA/BRIN-compliant Indonesian statements.

### M3b: Literature Mapping & Lineage DAG (MAP-001..019, DAT-019, LIB-017, ETH-015)
- **Deterministic Clustering**: Dynamic TF-IDF and keyword-based research family clustering.
- **Genealogical Lineage DAG**: Directed graph enforcing strict chronological arrow-of-time $\text{Year}(p) \le \text{Year}(c)$ with 4-component weighted scoring formula ($0.35\text{Cit} + 0.35\text{Sem} + 0.20\text{Kw} + 0.10\text{Chr}$).
- **Lineage Audit Table**: Confidence bands (`High`, `Medium`, `Low ⇒ Needs review`), root identification, and user override persistence.
- **Manuscript Positioning & Research Gaps**: Candidate ancestor ranking with non-novelty disclaimers and gap excerpt extraction ($\le 300$ chars).

### M4: Journal Fit Matching (JRN-001..012)
- **Scholarly Journal Catalog**: Scopus Q1–Q4, Indonesia SINTA S1–S6, Open Access, and DOAJ provenance.
- **3-Component Fit Scoring**: $0.60\text{Sem} + 0.25\text{Kw} + 0.15\text{Cit}$ evaluated after applying hard filters.
- **Author Guidelines & Similar Papers**: $\ge 3$ similar recent articles with verified DOIs and authoritative submission checklists.
- **Anti-Guarantee Disclaimer**: Mandatory notice rejecting probability/speed guarantees.

### M5: Hardening, Security & Launch (ENG-013..020, QAS-007..025)
- **Production Security Headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`, `Permissions-Policy`, `Referrer-Policy`.
- **Tenant Isolation Unit Tests**: Automated suite in `tests/test_hardening_security.py` verifying cross-project data boundaries.
- **Compliance Registers**: `docs/PRIVACY.md` (UU PDP 27/2022 & GDPR), `docs/ETHICS.md` (COPE/ICMJE), `docs/subprocessors.md`.
- **Concurrency Stress Suite**: `scripts/stress_concurrency_test.py` verifying 50 parallel requests at 100% success.
- **External IEEE Dataset Benchmark**: `scripts/test_ieee_dataset_eval.py` evaluating 10 real IEEE publications under strict secondary isolation.

---

## Active Verification Evidence

| Test Runner | Command | Exit Code | Result |
|---|---|---|---|
| **Pytest Full Suite** | `pytest tests/ -q` | `0` | **39/39 passed (100%)** |
| **Concurrency Stress** | `python scripts/stress_concurrency_test.py` | `0` | **50/50 requests passed (100%)** |
| **Live E2E Simulation** | `python scripts/e2e_live_simulation.py` | `0` | **8/8 workflows passed (100%)** |
| **IEEE Dataset Benchmark** | `python scripts/test_ieee_dataset_eval.py` | `0` | **7/7 stages passed (100%)** |
| **Frontend Production Build** | `npx vite build` | `0` | **255.32 kB clean build (gzip 67.89 kB)** |

---

## Active Service URLs
- **FastAPI Backend**: `http://localhost:8000` (OpenAPI Docs: `http://localhost:8000/docs`)
- **React 19 SPA Frontend**: `http://localhost:5173`
- **Standalone Prototype**: `http://localhost:4173`
