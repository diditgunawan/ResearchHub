# Product Requirements Document (PRD)

Gate-Status: APPROVED | Approved-By: user | Date: 2026-10-24

## A1. Product Overview
- **Product:** ResearchForge — an end-to-end, zero-hallucination academic research workspace integrating scholarly search, reference deduplication, PRISMA 2020 systematic screening, citation-grounded evidence synthesis, genealogical lineage mapping, and journal fit matching.
- **Platform:** Web Application (FastAPI backend + React/TypeScript SPA frontend)
- **Audience:** PhD students, systematic review authors, academic co-reviewers, and research supervisors.
- **Goals:**
  1. Reduce literature search, screening, and PRISMA count extraction time from weeks to <= 1 working day.
  2. Maintain 0% fabricated citations and >= 95% citation claim precision on benchmark evaluation sets.
  3. Ensure >= 90% automated deduplication precision and 100% auditable PRISMA 2020 flow counts.
  4. Provide transparent, explainable journal fit matching without false acceptance probability claims.

## A2. Problems & Goals
- **Problem to solve:** Academic researchers juggle 4-6 disjoint tools (aggregators, reference managers, screening apps, RAG synthesizers, journal finders) resulting in broken provenance, tedious manual import/export, and AI fabrication risks.
- **What success looks like:** A researcher imports 200+ scholarly works, completes blind multi-reviewer screening with automated Cohen's kappa and PRISMA 2020 diagram generation, runs grounded synthesis where every claim has a verifiable chunk citation (or explicit refusal), and visualizes the research family lineage DAG.

## A3. Target Users
- **Primary User:** PhD Student / Lead Researcher (conducts literature reviews, manages library, performs primary screening, runs synthesis, drafts manuscript plan).
- **Team Member:** Supervisor / Co-Reviewer (performs blind secondary screening, resolves classification conflicts, audits evidence synthesis).
- **Admin:** System / Project Admin (manages project memberships, monitors LLM token quota caps, exports audit logs).

## A4. Core Features
- **MVP scope (summary):** Scholarly Search & Open Connector import, Library & Deduplication, Systematic Screening with PRISMA 2020 Flow, Grounded Synthesis with Citation Verifier, Genealogical Lineage & Topic Mapping, and Journal Fit Matcher.
- **Authentication:** Email magic link + OAuth/OIDC with HTTP-only secure cookie sessions (no plaintext passwords).
- **Collaboration:** Project-level RBAC (Owner, Reviewer, Viewer), blind dual-screening with conflict resolution.
- **Dashboard:** Centralized project dashboard showing library statistics, screening queue progress, PRISMA flow chart, active synthesis runs, and lineage map status.
- **Notifications:** In-app status badges and SSE event streams for asynchronous background tasks (enrichment, embedding, RAG synthesis, clustering).
- **Projects:** Multi-tenant project workspace model with complete data isolation (tenant-scoped library, screening, synthesis, and private manuscript uploads).
- **Settings:** Project-level criteria configuration (PICO/PEO, exclusion reasons), LLM provider configuration, weekly token quotas, and full data export/deletion.
- **Other domain features:** Genealogical lineage DAG (Score = 0.35*Cit + 0.35*Sem + 0.20*Kw + 0.10*Chr with Year(p) <= Year(c) hard chronological constraint), journal fit matcher, reference retraction checker, and AI-use disclosure generator.

## A5. MVP Scope
**Must Have (build first — active scope)**
- [ ] User authentication via magic links & session cookies
- [ ] Project creation, member invitations, and RBAC (Owner/Reviewer/Viewer)
- [ ] Scholarly search integration with OpenAlex, Crossref, and PubMed connectors
- [ ] Reference import (RIS, BibTeX, CSV) and reversible deduplication queue
- [ ] Protocol configuration (PICO/PEO, exclusion reasons) & blind dual-reviewer screening
- [ ] Automated PRISMA 2020 flow counts and diagram generation (SVG/PNG/CSV)
- [ ] Citation-grounded synthesis engine with mandatory claim verification and refusal policy
- [ ] Genealogical lineage tree builder and research family clustering
- [ ] Journal fit matching with quartile, APC, and indexing filters
- [ ] AI usage disclosure generator & reference integrity audit (retractions/DOIs)

**Later (post-MVP — blocked until this PRD is amended by the user)**
- Meta-analysis statistical engine (forest plots, effect size calculations)
- Institutional SAML/SSO
- Native mobile applications
- Direct PDF full-text publisher scraping beyond legal Open Access APIs
- Automated patent database connectors

## A6. Acceptance Criteria
- **Critical flows work:**
  1. Ingestion: Query OpenAlex/Crossref -> normalize -> upsert `works` -> import to project library.
  2. Screening: Define protocol -> dual blind screening -> compute Cohen's kappa -> resolve conflicts -> generate verified PRISMA 2020 diagram.
  3. Synthesis: Query question -> hybrid BM25+vector retrieve chunks -> extract & synthesize -> verify all chunk claims -> stream output with citations (or refuse if coverage < 70%).
  4. Lineage: Select corpus -> cluster research families -> enforce chronological constraint Year(p) <= Year(c) -> compute lineage scores -> render family tree.
- **Edge cases covered:** Empty library search, network timeout/connector rate limit with exponential backoff, malformed RIS/BibTeX syntax, single-reviewer protocol fallback, claims with insufficient evidence triggering structured refusal, duplicate file upload detection.
- **Build and tests pass:** Backend `pytest -v --cov=app` exit 0, Frontend `pnpm test` and `pnpm build` exit 0, `python ~/.agents/skills/vibe-coding-gate/scripts/gate_check.py` exit 0.

## Change Log
| Date | Change | Requested by |
| :--- | :--- | :--- |
| 2026-10-24 | Initial draft synthesized from blueprints (00-vision-scope.md, 01-prd.md) and user specifications | Antigravity Orchestrator |
