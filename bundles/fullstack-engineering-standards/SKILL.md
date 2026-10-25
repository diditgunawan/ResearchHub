---
name: fullstack-engineering-standards
description: Engineering standards protocol for the whole codebase — monorepo layout, FastAPI/SQLAlchemy/Alembic backend, React/TypeScript frontend, contract-first OpenAPI, auth and project roles, background jobs, error format, logging/tracing, pagination, i18n (EN/ID), accessibility and dependency policy. Use this skill for ANY coding task in this project — new endpoints, models, migrations, UI components, jobs, config, auth, forms — even small ones, and whenever scaffolding or refactoring.
---

# Fullstack Engineering Standards Protocol (ENG)

Goal: consistent, typed, testable code that agents (and humans) can extend without drift.

## Preconditions
Read `AGENTS.md`, `blueprints/02-architecture.md`, `03-data-model.sql`, `04-openapi.yaml`, `references/requirements.md`, `references/repo-layout.md`. Always load `qa-security-deployment`.

## Protocol
**P1 — Contract first.** Change `blueprints/04-openapi.yaml` (or `packages/contracts/openapi.yaml`) *before* code. Generate TS client/types and Pydantic models from it or validate against it in CI.
**P2 — Schema via migrations.** Never edit DB by hand. Alembic revision per change; `upgrade` and `downgrade` both implemented and tested; no destructive change without a two-step migration (add → backfill → switch → drop).
**P3 — Module boundaries.** Follow `router → service → repository/models`. Routers only parse/validate and call services; services hold business rules and authorization checks; no cross-module imports except via `service` interfaces.
**P4 — AuthN/Z.** Magic-link login, secure httpOnly sameSite cookies, CSRF protection; every project route runs `require_role(project_id, role)` in the service layer; deny by default.
**P5 — Errors.** RFC 7807 `application/problem+json` with `code` and `request_id`. No stack traces to clients.
**P6 — Jobs.** Long work (imports, enrichment, indexing, synthesis, exports) runs in workers with `dedupe_key`, idempotent handlers, retry policy, and visible status.
**P7 — Observability.** `request_id` middleware; JSON logs; OTel spans around connectors, DB, and LLM calls; never log user content or secrets.
**P8 — Frontend.** React + TS strict; server state via TanStack Query; generated API client; every view has loading/empty/error states; forms validated with the same schema as the API; keyboard accessible; i18n keys not literals.
**P9 — i18n & a11y.** `en` and `id` locale files; ICU messages; WCAG 2.2 AA; axe in e2e.
**P10 — Dependencies.** Minimal; pinned via lockfile; prefer releases ≥ 14 days old; new dependency requires a one-line justification in the PR and an ADR if it's a framework/service.
**P11 — Docs.** Update README/runbooks/ADRs; keep `.env.example` in sync.

## Hard rules
- MUST NOT bypass the service layer for authorization.
- MUST NOT write endpoints not present in the OpenAPI contract.
- MUST NOT commit generated secrets, `.env`, or credentials.
- MUST NOT add a UI string without an i18n key.

## Definition of Done
Relevant `ENG-*` MUSTs pass; lint/type/test green locally; contract updated; migration tested up/down; handoff written.
