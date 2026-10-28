# QAS requirements
| ID | Level | Requirement |
|----|-------|-------------|
| QAS-001 | MUST | CI runs lint, type-check, unit, integration, and build on every PR; main protected. |
| QAS-002 | MUST | Lint/type failures block merge (ruff, mypy, ESLint, tsc). |
| QAS-003 | MUST | Unit coverage ≥ 85% on core modules (dedup, normalization, kappa, PRISMA, parsers, scoring). |
| QAS-004 | MUST | A script verifies every MUST requirement ID in scope has ≥ 1 test named `test_<ID>_*`; missing coverage fails CI. |
| QAS-005 | MUST | Secret scanning runs pre-commit and in CI; leaked secrets block merge and trigger rotation. |
| QAS-006 | MUST | Shared fixtures exist: two tenants, role matrix users, recorded connector responses, golden RAG set loader. |
| QAS-007 | MUST | Integration tests use real Postgres+pgvector and Redis (testcontainers). |
| QAS-008 | MUST | Every migration is tested upgrade→downgrade→upgrade on a populated fixture DB. |
| QAS-009 | MUST | Tenant isolation tests prove no cross-project reads/writes in library, screening, retrieval, synthesis, files. |
| QAS-010 | MUST | Role-matrix tests cover owner/reviewer/viewer for every project route. |
| QAS-011 | MUST | Connector tests use scrubbed fixtures (success, empty, malformed, 429, timeout). |
| QAS-012 | MUST | schemathesis (or equivalent) runs against the OpenAPI contract; no 5xx and no schema violations. |
| QAS-013 | MUST | Playwright e2e covers search→import→dedup→screen→PRISMA→synthesis→export and auth flows. |
| QAS-014 | MUST | axe-core runs on core screens; no serious/critical violations. |
| QAS-015 | MUST | SAST, dependency audit, and container scan run in CI; high/critical findings block unless an ADR accepts risk with expiry. |
| QAS-016 | MUST | DAST baseline (e.g., ZAP) runs on staging per release; findings triaged. |
| QAS-017 | MUST | k6 load tests meet PRD latency targets for search, decisions, and synthesis queueing. |
| QAS-018 | MUST | AI evals (SYN-018, JRN-012) run nightly and pre-release; threshold regressions block release. |
| QAS-019 | MUST | Metrics/alerts exist for error rate, queue depth, connector errors, LLM cost/quota, latency, cert expiry. |
| QAS-020 | MUST | Backups verified by a documented restore test at least quarterly; RPO/RTO documented. |
| QAS-021 | MUST | Release checklist executed and recorded; rollback plan documented and rehearsed on staging. |
| QAS-022 | MUST | Retention jobs, export, and deletion flows implemented and tested; sub-processor list current. |
| QAS-023 | MUST | Runbooks exist for connector outage, LLM outage, queue backlog, cost spike, data deletion request, security incident. |
| QAS-024 | MUST | Security headers (HSTS, CSP, X-Content-Type-Options, frame protections), cookie flags, and rate limits are asserted by automated tests. |
| QAS-025 | MUST | Golden mapping fixtures (determinism, chronology rule, cluster NMI, lineage top-1/top-3, evidence integrity, wording scan, manuscript privacy) run in CI and pre-release; threshold regressions block release. |
| QAS-026 | MUST | `scripts/truth_audit.py` runs in CI against the built app; any failed probe (token disclosure, replay, session expiry, irrelevant-query gate, provenance honesty, hard-coded records, gate-script integrity) blocks merge. |
| QAS-027 | MUST | The requirement-coverage gate counts only test functions named `test_<ID>_*` (or an explicit `covers` marker inside a test body); ranges are never expanded; changes to the gate script need an ADR and code-owner approval (hash pinned in `scripts/integrity.sha256`). |
| QAS-028 | MUST | Middle-scale load test (k6): 50 req/s mixed workload for 30 min and a 1 h soak; p95 targets in blueprint 16 met; no 5xx above 0.1%. |
| QAS-029 | MUST | Network checks in staging: origin accepts only edge ranges, database and Redis have no public address, egress limited to the allow-list, no public SSH; verified by an automated scan. |
| QAS-030 | SHOULD | Before launch: replica failover drill, point-in-time restore drill, and queue dead-letter replay drill, each documented with timings. |
| QAS-031 | MUST | The test suite passes from a clean clone with no pre-existing database, files, or environment state; CI runs from a fresh checkout and the number of passing tests quoted in reports is the CI number. |
| QAS-032 | MUST | Audit probes test the attack, not only the happy path (header and parameter variants, bootstrap race, bare-credential login); a fix that only relabels or relocates the offending data or code path (for example moving hard-coded records into a data file) does not satisfy a probe. |
| QAS-033 | MUST | The benchmark harness (`scripts/benchmark`) runs suites B1 to B5 on pinned public datasets nightly and before release; each result records dataset version, seed, git sha, and model ids; regressions beyond thresholds recorded in an ADR block release; datasets are never committed; synthetic data is labelled synthetic. |
| QAS-034 | SHOULD | Results are reported next to reference tools at pinned versions (ASySD or synthesisr for dedup, ASReview LAB for screening prioritisation, the official PRISMA generator for flow numbers, GROBID for extraction), each licence-checked under ADR-008 and run in an isolated environment. |
