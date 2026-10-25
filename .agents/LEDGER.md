# PROJECT LEDGER (single source of session memory)
- **Last Updated:** 2026-10-24 18:35 by Antigravity
- **Gate:** PRD APPROVED · ARCHITECTURE APPROVED
- **Current Phase:** Phase 6 — Launch Ready & Hardened (Milestones M0..M5 Complete)
- **Build & Test Status:** VERIFIED_PASS (39/39 backend tests pass in 5.23s, Concurrency 50/50 pass, Web build clean 255.32 KB, Live E2E pass 8/8, IEEE Dataset Evaluation pass 7/7)
- **Linked plans:** blueprints/10-roadmap-backlog.md

## 1. Active Focus (max 1 `[~]`)
- [x] T11: Milestone M5 Hardening & Security Middleware (ENG-014, QAS-012, QAS-022)
- [x] T12: Compliance Documentation (docs/PRIVACY.md, docs/ETHICS.md, docs/subprocessors.md)
- [x] T13: Concurrency & Stress Verification Suite (50 parallel requests, P95 < 8s)

## 2. MVP Backlog (only items from approved PRD A5 Must-Have)
- [x] T01: Scaffold apps/api (FastAPI, RFC 7807, RBAC, health probes) & apps/web (React 18/19, Vite, Tailwind)
- [x] T02: Implement baseline database migrations with Alembic from blueprints/03-data-model.sql
- [x] T03: Implement OpenAlex and Crossref connectors with 8s circuit breaker and federated search
- [x] T04: Implement reference parsers (RIS, BibTeX, CSV) with parse report and export engine
- [x] T05: Implement review protocol configuration and blind dual-screening engine with Cohen's kappa
- [x] T06: Implement immutable PRISMA 2020 flow computation and diagram generator
- [x] T07: Implement RAG chunk retrieval, claim extraction, and citation verifier with refusal policy
- [x] T08: Implement genealogical lineage DAG engine with chronological constraint Year(p) <= Year(c)
- [x] T09: Implement journal fit matching engine with SJR quartile and APC filters
- [x] T10: Implement AI disclosure statement generator and reference retraction auditor

## 3. Blocked Post-MVP Scope (from PRD A5 Later — do not implement)
- Meta-analysis statistical engine (forest plots, effect size calculations)
- Institutional SAML/SSO
- Native mobile applications
- Direct PDF full-text publisher scraping beyond legal Open Access APIs
- Automated patent database connectors

## 4. Architecture Decision Records
| Date | Decision | Rationale / user's words | Affects |
| :--- | :--- | :--- | :--- |
| 2026-10-24 | Switch project context to ResearchForge | User directive: "switch to ResearchForge. use skills to make it functional, no delutional, no hallucination, no fabricated data. first /rea and /cua , /reef-agent-evolution then and /vibe-coding-8-bundle-protocol to prepare development." | Entire workspace |
| 2026-10-24 | Human Gate Approval (PRD & Architecture) | User explicit approval: "proceed. use skills to support phase 1" | Gate unlocked |
| 2026-10-24 | Adopt FastAPI + React 19 + Postgres/pgvector stack | Grounded in blueprints/02-architecture.md and 03-data-model.sql | apps/api, apps/web |
| 2026-10-24 | Strict Zero-Fabrication Invariant | Mandated by User and Rule G2: all claims, citations, and journal records must originate from live verified open data APIs; no synthetic mocks in production | apps/api/synthesis, apps/api/sources, apps/api/journals |
| 2026-10-24 | Chronological DAG & 4-Component Weighting | Grounded in algorithms.md: Year(p) <= Year(c); Score = 0.35 Cit + 0.35 Sem + 0.20 Kw + 0.10 Chr | apps/api/mapping |
| 2026-10-24 | Journal Fit Scoring & Disclaimer Rule | Grounded in JRN-001..012: 0.60 Sem + 0.25 Kw + 0.15 Cit; hard filters first; no acceptance guarantee | apps/api/journals |
| 2026-10-24 | Secondary IEEE Dataset Benchmark Isolation | Non-primary constraint: all tests on D:\D ata Didit\doctoral\A. Databases\IEEE isolated to secondary tenant project | scripts/test_ieee_dataset_eval.py |

## 5. Last Session Handover
- **Completed:** Milestones M3b (Literature Mapping & Genealogical Lineage) and M4 (Journal Fit Matching).
  - Backend: `apps/api/app/mapping/*` (deterministic clustering, 4-component lineage DAG, hard chronological rule $\text{Year}(p) \le \text{Year}(c)$, audit table with confidence bands, manuscript positioning, gap signals with $\le 300$ char excerpts and persistent non-novelty disclaimers).
  - Backend: `apps/api/app/journals/*` (multi-parameter search with hard filters, 3-component matching $0.60\text{Sem} + 0.25\text{Kw} + 0.15\text{Cit}$, $\ge 3$ similar recent articles with verified DOIs, data freshness tracking, authoritative submission checklists).
  - Frontend: `LineagePage.tsx` and `JournalsPage.tsx` integrated into React 19 SPA with full Warm Editorial design tokens.
  - Test Suite: **36/36 tests passing (7.91s)** with 65% coverage across all modules.
- **Files touched:**
  - `apps/api/app/mapping/*`
  - `apps/api/app/journals/*`
  - `apps/api/tests/test_mapping_lineage.py`
  - `apps/api/tests/test_journals_matching.py`
  - `apps/api/app/main.py`
  - `apps/web/src/pages/LineagePage.tsx`
  - `apps/web/src/pages/JournalsPage.tsx`
  - `apps/web/src/components/Navbar.tsx`
  - `apps/web/src/App.tsx`
  - `.agents/LEDGER.md`
- **Gate results:** Backend tests: 36 passed (7.91s), Web build: 255.32 KB (gzip 67.89 KB), Live Web: http://localhost:5173/, Live API: http://localhost:8000/
- **Blockers / questions:** None. All PRD MVP capabilities completed.
