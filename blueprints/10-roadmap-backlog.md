# 10 — Roadmap & Backlog

Each milestone ends with: all listed requirement IDs passing, demo script run, `docs/PROJECT_STATE.md` updated.

| M | Name | Bundles | Outcome | Exit criteria (requirement IDs) |
|---|---|---|---|---|
| M0 | Foundations | ENG, QAS | Repo, CI, auth, projects, empty UI shell, migrations, observability | ENG-001..012, QAS-001..006 |
| M1 | Data & Library | DAT, LIB | Federated search, work detail, import/export, dedup, collections | DAT-001..018, LIB-001..016 |
| M2 | Screening | SCR | Protocol, dual screening, conflicts, kappa, PRISMA flow | SCR-001..018 |
| M3 | Synthesis & Integrity | SYN, ETH | Grounded synthesis w/ verification, extraction, ref checks, disclosure | SYN-001..020, ETH-001..014 |
| M3b | Literature Mapping | MAP, ETH, LIB, DAT | Topic map, families, lineage, audit table, positioning, gap view, extract-only uploads | MAP-001..019, DAT-019, LIB-017, ETH-015 |
| M4 | Journals | JRN | Journal DB, matching, filters, checklist | JRN-001..012 |
| M5 | Hardening & Launch | QAS, ETH, ENG | Evals, security review, load test, privacy docs, i18n, a11y | QAS-007..025, ENG-013..020 |

## M0 stories (example detail; agents derive others the same way)
| ID | Story | Acceptance |
|---|---|---|
| M0-1 | Monorepo scaffold (`apps/api`, `apps/web`, `packages/contracts`) | `make dev` boots all services; health endpoints 200 |
| M0-2 | Baseline migration from `03-data-model.sql` | Alembic up/down clean on empty DB |
| M0-3 | Magic-link auth + sessions | Rate-limited; tests for expiry/reuse |
| M0-4 | Projects + roles + ACL middleware | Role matrix tests pass |
| M0-5 | CI pipeline per 09 | Pipeline green on main; fails on lint/type/test errors |
| M0-6 | Logging/tracing/error format (RFC 7807) | `request_id` in logs and error bodies |

## Backlog rules
- Ticket template: *Goal, Bundles, Requirement IDs, Acceptance, Out of scope, Test plan*.
- Definition of Ready: requirement IDs listed, API contract updated, test plan written.
- Definition of Done: bundle DoD + QAS merge gate + docs updated.

## v2 candidates (do not build in v1)
Meta-analysis module · institutional SSO · Zotero two-way sync · agreement meter · embeddable map widget (cf. Open Knowledge Maps custom integrations) · non-article outputs (datasets, software) · live-updating maps · additional connectors (CORE, Europe PMC, DOAJ search) · mobile PWA offline screening.
