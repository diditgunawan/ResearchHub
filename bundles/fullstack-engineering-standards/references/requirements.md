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
| ENG-021 | MUST | Instance access modes `single_owner` and `multi_user` exist; invitation, role, quota, admin, and audit flows are implemented and tested in both modes; `single_owner` closes registration and lets one account hold `system_admin` and normal-user capabilities. |
| ENG-022 | MUST | Authentication tokens and links are never returned by any HTTP response outside the test runner; local dev login prints the link to the server console, works only on loopback with `APP_ENV=local`. |
| ENG-023 | MUST | Sessions are server-side, hashed at rest, idle-expire at 12 h and absolute-expire at 7 d, rotate on login and privilege change, and are revocable (logout, admin, credential change). |
| ENG-024 | MUST | Login, link-request, and expensive endpoints are rate-limited per IP and per user with backoff; limits are configurable and tested. |
| ENG-025 | MUST | A production boot guard refuses to start with default secrets, `APP_ENV=local`, SQLite, dev login enabled, wildcard CORS, or missing HTTPS configuration. |
| ENG-026 | MUST | The owner can register passkeys (WebAuthn) and receives hashed one-time recovery codes; admin actions require step-up authentication within 10 minutes and are written to `audit_events`. |
| ENG-027 | SHOULD | Postgres 16 is the default database in every non-test environment; SQLite is allowed only in unit tests. |
| ENG-028 | MUST | Passkeys use a maintained WebAuthn library: challenges are stored server-side, single-use, expire in 5 minutes, and are bound to origin and RP id; registration verifies attestation, login verifies the signature and sign-count; no endpoint accepts a bare credential id. |
| ENG-029 | MUST | The first owner is created only by a CLI command, a one-time setup secret, or a pre-configured owner email; anonymous HTTP never creates an administrator; no test-echo header, debug flag, or equivalent returns a token in any environment reachable from a network. |
| ENG-030 | MUST | Background handlers perform real work or are absent; a stub is labelled `stub`, never counted as delivered, and never advertised in docs; the queue is durable (Redis or database-backed) before any claim of Tier M readiness. |
| ENG-031 | MAY | Analysis-ready export of study characteristics and extracted effect fields as CSV compatible with common meta-analysis tools; meta-analysis itself stays out of scope for v1 (ADR-012). |
