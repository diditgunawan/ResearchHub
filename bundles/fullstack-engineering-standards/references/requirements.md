# ENG requirements
| ID | Level | Requirement |
|----|-------|-------------|
| ENG-001 | MUST | Monorepo layout per `repo-layout.md`; `make dev` boots all services; health endpoints (`/healthz`, `/readyz`) exist. |
| ENG-002 | MUST | API is contract-first: OpenAPI is updated before implementation; CI verifies implementation ⊆ contract. |
| ENG-003 | MUST | Config is read from environment, validated at boot (Pydantic Settings); production refuses dev defaults/empty secrets. |
| ENG-004 | MUST | Alembic migrations are reversible, tested up/down, and non-destructive via multi-step patterns. |
| ENG-005 | MUST | Backend follows router→service→repository boundaries; no cross-module imports except through service interfaces. |
| ENG-006 | MUST | Errors use RFC 7807 with stable `code` and `request_id`; no stack traces or internal ids leak. |
| ENG-007 | MUST | Auth uses single-use, 15-min magic links, secure/httpOnly/sameSite cookies, session rotation, CSRF protection, rate limits. |
| ENG-008 | MUST | Authorization (owner/reviewer/viewer) is enforced server-side in services; deny by default; covered by role-matrix tests. |
| ENG-009 | MUST | Background jobs are idempotent with `dedupe_key`, bounded retries, status API, and cancellation where applicable. |
| ENG-010 | MUST | JSON logs with `request_id`; OTel traces across API→worker→connector→LLM; user content and secrets never logged. |
| ENG-011 | MUST | List endpoints use cursor pagination with max page size (default 25, max 100). |
| ENG-012 | MUST | Static quality gates: ruff + mypy (strict on new code), ESLint + TS strict; failures block merge. |
| ENG-013 | SHOULD | UI supports `en` and `id` via ICU message catalogs; no hard-coded user-facing strings; locale-aware dates/numbers. |
| ENG-014 | MUST | Frontend meets WCAG 2.2 AA on core screens; axe checks run in e2e. |
| ENG-015 | MUST | Frontend uses generated API client; every view has loading, empty, and error states; optimistic updates only for non-audit actions. |
| ENG-016 | SHOULD | Performance budgets: initial JS ≤ 250 KB gz per route, LCP ≤ 2.5 s on mid-tier mobile profile. |
| ENG-017 | SHOULD | Risky features sit behind feature flags with documented rollback. |
| ENG-018 | MUST | README, runbooks, ADRs, `.env.example`, and `docs/PROJECT_STATE.md` are updated with each relevant change. |
| ENG-019 | MUST | `/me/export` and `/me` DELETE are implemented end-to-end with job status and tests. |
| ENG-020 | MUST | Dependencies are pinned by lockfile, minimal, preferably ≥ 14 days old; additions need justification (and ADR for frameworks/services). |
