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