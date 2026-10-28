# PROJECT_STATE (agents update after every task)
Last updated: 2026-10-25 by Claude (audit + mastermind plan v2)

## v0.7 UPDATE — B2 runner ready, no real numbers yet (27 Oct 2026)
- `scripts/benchmark/run_screening_benchmark.py` now supports random, keyword, and a simulated active-learning ranker, multi-review aggregation, seeds, JSON and Markdown output; 11 tests pass (synthetic fixture only).
- **No benchmark results exist.** The build sandbox cannot reach DataverseNL or the OpenAlex API, so SYNERGY could not be downloaded. Follow `docs/BENCHMARK_RUNBOOK.md` on your machine, then record medians with `templates/ADR_BENCHMARK_BASELINE.md`.

## v0.6 UPDATE — ecosystem references and benchmarking (27 Oct 2026)
- Added the Awesome Evidence Synthesis Tools index (140 open-source tools, CC BY 4.0) as reference, supporting-tool map, protocol map, and benchmark baselines: blueprints 20 and 21, ADR-012, register rows, 9 new requirements (DAT-021, LIB-018, SCR-019..021, MAP-020, ENG-031, QAS-033/034; total 198).
- Benchmark harness started and proven: `scripts/benchmark/` (metrics hand-verified, 8 tests pass).
- ResearchHub (github.com/diditgunawan/ResearchHub): **no commits since 257b7e3**; single branch, no tags. Status unchanged: truth audit 8 pass / 6 fail of 14. Next action is the Phase 0b prompt in docs/AGENT_PROMPTS.md.

## v0.5 REVIEW — upgrade verification (26 Oct 2026, repo HEAD 257b7e3)
Independent review of the upgrade claimed in CLAUDE_UPGRADE_AUDIT_HANDOFF_NOTES.md. **Verdict: request changes.** Real progress: single-use links, server sessions, truthful provenance fields, strict gate restored (hash matches), relevance floor against zero-score works, OpenAlex key as query parameter, frontend builds. **Not fixed or relabelled:** header backdoor returns login token under default config and the SPA sends it (ENG-029); first anonymous caller becomes admin; passkeys do no WebAuthn verification (ENG-028); hard-coded journal DOIs moved into data/seed_journals.json with false provenance (JRN-013, QAS-032); worker handlers are `asyncio.sleep` simulations on an in-memory queue (ENG-030); verdicts are model self-reports or hard-coded 'supported' (SYN-023); gateway prices $0.15/$0.60 vs current $0.75/$3.75 per 1M (ETH-017); mapping still records embedding_model text-embedding-3-small with no embeddings; gap-discovery pipeline exists only as prose; '46 passed' needs a leftover local DB (clean clone: 45 pass, 1 fail) (QAS-031); notes say React 19, package.json has 18.3.1.
**Gate now:** `truth_audit.py` has 14 probes. Upgraded repo: 8 pass / 6 fail (P9 header backdoor, P10 anonymous admin, P11 relevance floor, P12 passkey, P13 shipped records, P14 simulated workers). Original repo: 2 pass / 11 fail. Phase 0 is not done until all 14 pass.

## READ FIRST — v0.4 status
- An implementation exists (ResearchHub repo: FastAPI + React). Independent audit (25 Oct 2026) reproduced **3 critical and 3 high defects**: login token returned to anyone (account takeover under default config), fabricated AI provenance (model, tokens, cost, false disclosure text), circular verification with a bypassable sufficiency gate; plus an unverifiable hard-coded journal catalog, immortal sessions, and a loosened coverage gate.
- **Baseline:** `python scripts/truth_audit.py --repo <repo> --pin scripts/integrity.sha256` currently reports **0 pass / 8 fail**. Phase 0 exit = all pass (blueprint 18).
- **Access decision (owner, 2026-10-25):** run `single_owner` — one account is both system admin and user; keep every multi-user flow (blueprint 17, ADR-009). Do not delete flows.
- **Scale decision:** build for Tier M (middle scale) now; blueprint 16, ADR-010/011.
- **Positioning:** general research platform worldwide; Indonesian/ASEAN support is a locale pack that adds value.
- **Do next:** Phase 0 in `blueprints/18-roadmap-v2.md`, using the Phase 0 prompt in `docs/AGENT_PROMPTS.md`.


## Current milestone
**Pre-M0** — specification complete (package v0.3). **No application code exists yet.** Next: M0 Foundations.

## Done (with requirement IDs / artifacts)
- Blueprints 00–15 incl. PRD, architecture, SQL schema, OpenAPI, AI spec, security, UX, tests, ops, roadmap, source register, glossary, reference analysis; ADR-001..008.
- 9 skill bundles (DAT, LIB, SCR, SYN, JRN, ETH, ENG, QAS, MAP): 165 requirements, 155 MUST; traceability matrix `blueprints/14-traceability-matrix.csv`.
- Scripts: `validate_bundles.py` (structure, IDs, cross-refs, OpenAPI, SQL), `check_requirement_coverage.py` (QAS-004).
- UI/UX prototype v0.1 (5 static screens): design canvas source + standalone HTML + tokens + screen specs (`prototype/`).
- Validation evidence: OpenAPI passes `openapi-spec-validator`; SQL parses with the Postgres parser (`pglast`, 54 statements). **SQL has not been executed on a live Postgres.**

## In progress
- Nothing. No agent has claimed a task.

## Next recommended
Bundles: `fullstack-engineering-standards` + `qa-security-deployment` → **M0-1** monorepo scaffold, then M0-2 baseline migration (this is where the SQL is first executed). See `docs/DEVELOPMENT_GUIDE.md` §4 and `docs/AGENT_PROMPTS.md`.

## Assumptions (G10)
| # | Assumption | Date | Reversible? |
|---|---|---|---|
| A1 | Stack: FastAPI + SQLAlchemy/Alembic, Postgres 16 + pgvector, Redis + arq, React + TS + Vite, Docker Compose | 2026-10-24 | Yes via ADR before M0 |
| A2 | "ResearchForge" is a placeholder product name | 2026-10-24 | Yes |
| A3 | Embedding dimension is 1024 (`vector(1024)` in schema); chosen model must output 1024 or schema changes | 2026-10-24 | Costly after data exists; decide at M0-2 |
| A4 | UI languages: English + Indonesian (SHOULD) | 2026-10-24 | Yes |
| A5 | Scoring weights/thresholds in MAP and JRN specs are uncalibrated defaults | 2026-10-24 | Yes; calibrate on fixtures (QAS-025, JRN-012) |
| A6 | Prototype uses sample data and a cool scholarly palette; no brand decided | 2026-10-24 | Yes |
| A7 | Auth is magic-link + sessions (no passwords) | 2026-10-24 | Yes via ADR |

## Open questions for the human (decide before the noted milestone)
1. Product name, domain, and licence for our own code (before M0 public repo).
2. Hosting target and budget (before M5; affects ADR on deploy).
3. LLM provider(s) and embedding model; data-retention/training opt-out terms (before M3).
4. Reuse Open Knowledge Maps code, or reimplement? Requires licence check (ADR-008) (before M3b).
5. BASE access (registration/whitelisting) and whether to include it (before M3b, DAT-019).
6. Scopus/SINTA data rights for journal metrics (before M4, JRN-001).
7. Primary discipline for golden sets (RAG, lineage, journal evals) (before M3).
8. Who performs legal review for UU PDP / PDPA / GDPR (before M5).

## Source register status (G3)
Rows verified: **0/18** — see `blueprints/11-source-terms-register.md`. Every connector task starts by verifying its row.

## Known issues / tech debt
- **API contract gaps found while building the prototype** (fix in `blueprints/04-openapi.yaml` before the relevant milestone):
  1. No endpoint to mark an AI output as human-reviewed (needed for ETH-003; screen 3 "Mark as reviewed").
  2. No endpoint/action for "Remove claim" on a synthesis run (screen 3).
  3. Library add has no way to acknowledge adding a retracted work (screen 1 "Add anyway").
  4. Map-run polling/SSE endpoint not defined (only POST + GET).
  5. No endpoint to list/seed `exclusion_reasons` per project.
- Many OpenAPI responses are stubs (`description: OK`) without schemas; fill per milestone, contract tests need them.
- SQL: audit/append-only guarantees (no UPDATE/DELETE grants on `screening_decisions`) are comments only; implement role grants in the baseline migration; consider RLS (ENG/QAS).
- SQL not executed on a live Postgres; generated column `title_norm` and HNSW index need a smoke test.
- Prototype is static (no clickable flows) and covers 5 of 18 blueprint screens (see `prototype/README.md`).
- Prototype canvas files use the Claude Design runtime format; use `prototype/standalone/` outside Claude.
- Scoring defaults, thresholds, and test targets are proposals, not validated.
