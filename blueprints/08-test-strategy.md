# 08 — Test Strategy

| Layer | Tooling | Scope | Gate |
|---|---|---|---|
| Unit | pytest, vitest | pure logic: normalization, dedup scoring, kappa, PRISMA counts, parsers | ≥ 85% on core modules |
| Integration | pytest + testcontainers (Postgres/Redis) | repos, migrations, jobs, RLS/tenancy | all pass |
| Connector | recorded fixtures (vcr/respx) | each source adapter; contract drift check weekly vs live (non-blocking) | fixtures + 1 live smoke nightly |
| Contract | schemathesis vs `04-openapi.yaml` | API conformance | no 5xx, schema-valid |
| E2E | Playwright | search→import→screen→PRISMA→synthesis→export | critical paths green |
| AI evals | golden set + judge + human labels | citation precision, faithfulness, refusal | thresholds in 05 §5 |
| Security | bandit/semgrep, pip-audit/npm audit, trivy, ZAP baseline | SAST/SCA/container/DAST | no high/critical |
| Accessibility | axe-core in Playwright | key screens | no serious violations |
| Load | k6 | search, screening decisions, synthesis queue | p95 targets in PRD |

## Required test data
- 2 tenants with overlapping works (isolation tests).
- RIS/BibTeX/CSV edge cases (unicode, missing DOI, duplicate DOIs, malformed).
- Dedup corpus with labelled duplicates (≥ 300 pairs incl. hard negatives: same title different year; erratum; preprint vs published).
- Screening scenarios: 2 reviewers, conflicts, protocol version change mid-stage.
- Golden RAG set (≥ 100) incl. unanswerable and adversarial (prompt-injection abstracts).

## Test naming
`test_<req-id>_<behavior>` e.g. `test_SCR_011_prisma_counts_match_log`. CI fails if a MUST requirement ID has no covering test (QAS-004).

## Mapping tests (v0.2)
| Test | Detail | Initial target (calibrate on fixtures) |
|---|---|---|
| Determinism | same inputs/seed/models ⇒ identical clusters and lineage | exact match |
| Chronology rule | no parent newer than child; same-year requires citation | 0 violations |
| Confidence bands | boundary cases at 0.55 / 0.75; Low never auto-parented | all pass |
| Cluster quality | labelled fixture corpus (≥ 150 works, ≥ 5 themes, mixed EN/ID) | NMI ≥ 0.6 |
| Lineage accuracy | expert-labelled fixture (≥ 60 works, ≥ 3 families) | parent top-1 ≥ 60%, top-3 ≥ 80% |
| Evidence integrity | every rendered node/edge has evidence row | 100% |
| Override audit | override tracked, reset restores machine result | pass |
| Positioning wording | copy scan for forbidden terms ("novel", "first to", "no prior work") | 0 hits |
| Manuscript privacy | text absent from DB/logs when `retain_text=false`; deletion verified | pass |
| Extract-only | original removed after success; failure path purges ≤ 24 h | pass |
| Gap excerpts | length ≤ 300, source linked, OA/user-owned only | pass |
