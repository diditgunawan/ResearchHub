# 09 — Deployment & Operations

## Environments
`local` (docker compose) · `staging` (auto-deploy main) · `production` (manual promote, tagged release).

## Services
api, worker, web (static/CDN), postgres, redis, minio/S3, optional reverse proxy (Caddy/Traefik).

## Configuration (env vars; see scaffold/.env.example)
DATABASE_URL, REDIS_URL, S3_*, SESSION_SECRET, EMAIL_SMTP_*, OPENALEX_*, CROSSREF_MAILTO, NCBI_API_KEY, UNPAYWALL_EMAIL, LLM_PROVIDER/LLM_API_KEY, EMBEDDING_MODEL, QUOTA_*, SENTRY_DSN, OTEL_*.
Rules: no defaults for secrets; app refuses to boot in production with dev defaults.

## CI/CD (GitHub Actions or equivalent)
lint+typecheck → unit → integration → contract → build images → SAST/SCA/container scan → e2e (staging) → deploy. Nightly: AI evals, live connector smoke, dependency audit.

## Release process
Semantic versioning; changelog; migration dry-run on staging snapshot; feature flags for risky features; rollback = previous image + down-migration plan documented in PR.

## Observability
Structured JSON logs with `request_id`; OpenTelemetry traces (API→worker→connector→LLM); metrics: request latency, job duration, connector error rate per source, LLM tokens/cost per feature, quota rejections; alerts: error rate, queue depth, cost > 80% budget, cert expiry.

## Backups & DR
Postgres PITR/daily snapshots (35 d), object storage versioning, quarterly restore test, RPO 24 h / RTO 8 h (v1).

## Runbooks (create in `docs/runbooks/`)
Connector outage · LLM provider outage (degrade to retrieval-only) · Queue backlog · Cost spike · Data deletion request · Security incident.
