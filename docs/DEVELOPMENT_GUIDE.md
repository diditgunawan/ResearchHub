# Development Guide for continuing agents

## 1. What you are inheriting
A complete **specification** (blueprints, 9 skill bundles, 165 numbered requirements) and a **UI prototype**. There is no application code yet. Your job is to build it milestone by milestone, following the bundles' protocols and gates.

## 2. Read order (do this every new session)
1. `docs/PROJECT_STATE.md` — what is true now, open questions, known gaps.
2. `AGENTS.md` — router and 13 global rules (G1–G13).
3. `blueprints/00-vision-scope.md` → `01-prd.md` → `02-architecture.md`.
4. `blueprints/10-roadmap-backlog.md` — your milestone and exit criteria.
5. The bundle(s) the router sends you to: `bundles/<name>/SKILL.md` + `references/`.
6. For UI work: `prototype/README.md`, `prototype/screen-specs.md`, `prototype/design-tokens.json`.
7. Contracts: `blueprints/03-data-model.sql`, `blueprints/04-openapi.yaml`.
8. Only then, `blueprints/05`–`09`, `11`, `15` as needed.

## 3. Operating loop (per task)
1. Claim the task in `docs/PROJECT_STATE.md` (In progress) — one agent per bundle/task at a time.
2. List requirement IDs in scope (`blueprints/14-traceability-matrix.csv`).
3. Update the contract first (OpenAPI/SQL via migration) — ENG-002, ENG-004.
4. Write tests named `test_<ID>_<behavior>`; then implement.
5. Run gates: `make lint type test`, `python scripts/validate_bundles.py`, `python scripts/check_requirement_coverage.py --tests apps/api/tests apps/web/src --scope <PREFIXES>`.
6. Record ADRs for non-trivial choices; update PROJECT_STATE (Done, assumptions, issues); write `templates/HANDOFF.md`.
7. Commit messages: `feat(DAT-007): normalize DOIs` — cite IDs; one concern per PR; PR uses `templates/PR_CHECKLIST.md`.

## 4. First tasks (M0, from the roadmap)
| Task | Do | Done when |
|---|---|---|
| M0-1 | Create the repo from this package (copy `AGENTS.md`, `blueprints/`, `templates/`, `docs/`, `prototype/`, `scripts/`, `bundles/` → `.claude/skills/` or equivalent). Add `apps/api`, `apps/web`, `packages/contracts` per `bundles/fullstack-engineering-standards/references/repo-layout.md`; copy scaffold files to root | `make dev` boots all services; `/healthz`, `/readyz` return 200 |
| M0-2 | Baseline Alembic migration from `blueprints/03-data-model.sql` (**first execution of the SQL**): fix any issues, implement role grants for append-only tables, decide embedding dimension (A3) | up/down/up clean on empty and populated DB (QAS-008) |
| M0-3 | Magic-link auth + sessions | ENG-007 tests incl. expiry, reuse, rate limit |
| M0-4 | Projects, members, role middleware | role-matrix tests (ENG-008, QAS-010) |
| M0-5 | CI per `blueprints/09-deployment-ops.md` and `bundles/qa-security-deployment/references/ci-pipeline.md` | green on main |
| M0-6 | Logging, tracing, RFC 7807 errors | `request_id` in logs and error bodies |

## 5. Multi-agent coordination rules
- **Migrations have one owner at a time.** Announce in PROJECT_STATE before creating a revision; rebase before merge; never edit applied migrations.
- **Contract changes go first** in their own PR (OpenAPI/SQL), so frontend and backend agents can work in parallel.
- Suggested parallel lanes after M0: (a) DAT+LIB, (b) frontend shell + design system from tokens, (c) QAS fixtures/evals. SCR starts after LIB items exist; SYN after DAT chunks exist; MAP after LIB + embeddings.
- Never edit another agent's claimed area without noting it in PROJECT_STATE.
- If a bundle requirement is wrong or impossible: propose a change in an ADR and update `requirements.md` + regenerate the matrix (`python scripts/validate_bundles.py --write-index`). Do not silently skip a MUST (G11).

## 6. Using the prototype
- It communicates layout, states, wording rules, and component inventory; it is **not** production code and uses sample data.
- Implement from `design-tokens.json` and `screen-specs.md`, not by copying the HTML. Add loading/empty/error states (ENG-015), i18n keys (ENG-013), and WCAG 2.2 AA checks (ENG-014).
- Wording rules shown in the prototype are requirements: AI labels (ETH-001), relative analysis wording (ETH-015, MAP-015/017).

## 7. Things not to do
Do not scrape or copy Rayyan, Consensus, JurnalHub, Open Knowledge Maps, PaperTree, or others (G4; reuse of open-source code only under ADR-008). Do not build detector-evasion features (G6/ADR-006). Do not claim novelty in any output (G13). Do not log manuscript text or secrets (G7).

## 8. Definition of "project complete" for v1
All MUST requirements pass; release checklist (`bundles/qa-security-deployment/references/release-checklist.md`) completed; evals meet thresholds; source register fully verified; legal review recorded.
