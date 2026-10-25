# ResearchForge — Master Agent Protocol (AGENTS.md)

> Drop this file in the repo root (also usable as `CLAUDE.md`, `.cursorrules`, or `.github/copilot-instructions.md`).
> It routes any AI coding agent to the right **bundle** (skill) and enforces rules that apply to every task.

## 0. What we are building
A single web application for researchers (primary user: PhD students) covering the pipeline
**find → map → library → screen (PRISMA) → grounded synthesis → position & write/check → choose journal**,
built on **open scholarly data** and our own code. Full spec: `blueprints/`.

## 1. Startup routine (every session, every agent)
1. Read `docs/PROJECT_STATE.md` (create from `templates/PROJECT_STATE.md` if missing).
2. Read `blueprints/00-vision-scope.md` and `blueprints/01-prd.md` if you have not this session.
3. Identify the task's phase using the routing table below; load **every** matching bundle's `SKILL.md`.
4. Follow each bundle's protocol, in order, including its **gates**.
5. Before finishing: run the bundle's Definition of Done, update `docs/PROJECT_STATE.md`, write a handoff note.

## 2. Routing table
| If the task touches…                                            | Load bundle                         | Req prefix |
|-----------------------------------------------------------------|-------------------------------------|-----------|
| External scholarly APIs, metadata, dedup, caching               | `scholarly-data-ingestion`          | DAT |
| Import/export, collections, PDFs, citation formatting, Zotero   | `library-reference-management`      | LIB |
| Screening, inclusion criteria, PRISMA, reviewer agreement       | `screening-prisma-workflow`         | SCR |
| Retrieval, embeddings, LLM answers, citations in generated text | `grounded-synthesis-rag`            | SYN |
| Journals, matching score, filters, submission checklists        | `journal-matching-submission`       | JRN |
| Topic maps, families, lineage, positioning, research gaps | `literature-mapping-positioning` | MAP |
| ANY AI-generated output, disclosure, retractions, privacy of manuscripts | `research-integrity-ai-ethics` | ETH |
| ANY code: structure, API, DB, frontend, auth, i18n, a11y        | `fullstack-engineering-standards`   | ENG |
| ANY merge/release: tests, security, CI/CD, observability, privacy | `qa-security-deployment`          | QAS |

Rules of thumb: **ETH loads with SYN, JRN, and MAP always. ENG and QAS load with everything.**

## 3. Global rules (apply to all bundles)
- **G1 No fabrication.** Never invent a citation, DOI, author, statistic, API field, or journal metric. Unknown → say so, or fetch it.
- **G2 Traceability.** Every scholarly claim shown to a user must trace to a stored record (work id + chunk id or field + source + fetched_at).
- **G3 Verify at build time.** API limits, auth, and licences change. Before integrating a source, read its *current* docs/terms and update `blueprints/11-source-terms-register.md` with date + link.
- **G4 Respect third parties.** Do not scrape sites that disallow automated access or forbid it in their terms. Do not copy competitors' code, UI copy, branding, or assets. Functional ideas are free; their implementation is not ours to copy. Open-source code may be reused only under its verified licence per ADR-008 (register + attribution + ADR).
- **G5 Human decides.** AI may suggest; a human makes inclusion/exclusion, authorship, and submission decisions. No auto-decisions persisted without a human action.
- **G6 No detector evasion.** Do not build "humanizers", AI-detector bypass, or features whose purpose is concealing AI use.
- **G7 Secrets.** Never commit secrets. Use env vars; maintain `.env.example`. Never log secrets, tokens, or manuscript text.
- **G8 Small verified steps.** One concern per PR; tests ship with code; migrations are reversible and idempotent.
- **G9 Decisions are recorded.** Non-trivial choices get an ADR (`templates/ADR.md` → `blueprints/adr/`).
- **G10 Assumptions are logged.** If ambiguity is non-blocking, choose the simplest option and log it under *Assumptions* in `docs/PROJECT_STATE.md`. Ask the human only when blocked or when the choice is costly to reverse.
- **G11 Fail loudly at gates.** If a gate fails, stop, report which requirement ID failed and why, and propose a fix. Never skip a gate or weaken a requirement silently.
- **G12 Minimal footprint.** Do not add dependencies, services, or features not in the roadmap without an ADR.
- **G13 Relative claims.** Analysis outputs describe the analyzed set only; never claim global novelty (MAP-015/017, ETH-015).

## 4. Requirement language
MUST / MUST NOT = blocking gate. SHOULD = expected, deviation needs a logged reason. MAY = optional.
Every requirement has an ID (e.g., `DAT-007`); cite IDs in commits, PRs, and tests (`# covers DAT-007`).

## 5. Handoff note (end of every task)
Use `templates/HANDOFF.md`: what was done, requirement IDs satisfied, open items, assumptions, next recommended bundle.

## 6. Build order (default)
M0 Foundations (ENG, QAS) → M1 Data & Library (DAT, LIB) → M2 Screening (SCR) → M3 Synthesis (SYN, ETH) → M3b Mapping (MAP, ETH, LIB, DAT) → M4 Journals (JRN) → M5 Hardening & launch (QAS, ETH). Details: `blueprints/10-roadmap-backlog.md`.
