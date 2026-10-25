---
name: qa-security-deployment
description: Quality, security, privacy and release protocol — test pyramid, requirement-ID coverage checks, tenant-isolation and role tests, contract tests, AI evals, SAST/SCA/container/DAST scanning, CI/CD, observability and alerts, backups, retention and deletion, incident runbooks and release checklist. Use this skill before merging or releasing ANY change, and whenever a task mentions tests, CI, security review, deployment, monitoring, privacy, GDPR/PDPA, or "is this ready to ship", even if the user only says "make it production-ready".
---

# QA, Security & Deployment Protocol (QAS)

Goal: nothing merges or ships unless it is tested, secure, observable, reversible, and compliant with its own requirements.

## Preconditions
Read `AGENTS.md`, `blueprints/06-security-privacy.md`, `08-test-strategy.md`, `09-deployment-ops.md`, `references/requirements.md`, `references/ci-pipeline.md`, `references/release-checklist.md`.

## Protocol
**P1 — Plan tests with the change.** For each requirement ID touched, write tests named `test_<ID>_<behavior>`. CI fails when a MUST ID in scope lacks a covering test (QAS-004).
**P2 — Pyramid.** Unit → integration (real Postgres/Redis via testcontainers) → contract (OpenAPI) → e2e (critical paths) → AI evals (golden set, incl. mapping fixtures per QAS-025) → a11y → load.
**P3 — Tenant & role safety.** Maintain two-tenant fixtures and the role matrix; any query touching tenant tables needs a test proving isolation.
**P4 — Security gates.** Secret scanning (pre-commit + CI), SAST, dependency audit, container scan, DAST baseline on staging; high/critical findings block merge/release unless an ADR documents an accepted risk with expiry.
**P5 — LLM security.** Review against OWASP LLM Top-10 each release: prompt injection, insecure output handling (sanitize rendered markdown), data leakage, excessive agency (none), cost abuse (quotas), supply chain.
**P6 — CI/CD.** Follow `ci-pipeline.md`; main is always deployable; staging auto-deploys; production is a tagged, manual promotion with migration dry-run.
**P7 — Observability.** Dashboards and alerts per `09`; add metrics for any new job/connector/LLM call.
**P8 — Privacy ops.** Implement retention (logs 30 d, deleted projects 30 d, backups 35 d), export/delete flows, sub-processor list, and consent records; flag for human legal review before launch (not legal advice).
**P9 — Release.** Run `release-checklist.md`; record result in `docs/PROJECT_STATE.md`.
**P10 — Fail loudly.** On any failed gate: stop, report requirement ID and evidence, propose a fix. Never lower thresholds to pass.

## Hard rules
- MUST NOT merge with failing or skipped-without-reason tests.
- MUST NOT disable security scanners to get green.
- MUST NOT ship without a rollback path.
- MUST NOT test against production data.

## Definition of Done
Relevant `QAS-*` MUSTs pass; PR checklist (`templates/PR_CHECKLIST.md`) complete; handoff written.
