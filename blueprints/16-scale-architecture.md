# 16 — Scale Architecture (v0.4)  ·  target: MIDDLE SCALE ("Tier M")

Scope: general research use worldwide. Indonesian/ASEAN support is a locale pack that adds value, not a limit.

## 1. Tiers and triggers
| Tier | Who | Shape | Move up when |
|---|---|---|---|
| S — Solo | One owner (admin + user) | Single host, Docker Compose, Postgres, local object store | Second real user needed, or public URL wanted |
| **M — Middle (build now)** | ≤ 5,000 registered, ≈ 600 daily, ≈ 120 concurrent peak | Managed containers + managed Postgres/Redis/object store behind an edge network | p95 SLOs missed 2 weeks running; DB CPU > 60% sustained; vector rows > 5M |
| L — Large | 50k+ users, multi-institution | Kubernetes, dedicated vector store, replicas, multi-region | Not planned; revisit with funding |

## 2. Tier M design targets and load estimate
Assumptions (revisit after pilot): 5,000 registered; 600 daily active; 120 concurrent peak; ≈ 0.4 request/s per active peak user; 400 requests per active user per day.
| Item | Estimate |
|---|---|
| API traffic | avg ≈ 2.8 req/s; **design for 50 req/s peak** (10× burst) |
| Synthesis runs | ≈ 240/day; ≈ 20 model calls each; budget cap $1,500/month, alert at 80% |
| Searches against sources | ≈ 4,800/day → exceeds a free OpenAlex key allowance → **local mirror + cache** (see ADR-011) |
| Works metadata | ≈ 4M rows ≈ 10 GB |
| Embedded chunks | ≈ 2M × (1.5 KB text + 2 KB half-precision vector) ≈ 8 GB + HNSW index ≈ 6–8 GB |
| Screening decisions | ≈ 90k/day ≈ 33M/year ≈ 8 GB/year |
| Usage and audit events | ≈ 100k/day; partition monthly |
| User PDFs (object store) | ≈ 250–300 GB |
| Database year 1 | ≈ 60–90 GB; 500 GB NVMe is ample; 32 GB RAM keeps the HNSW index and hot set in memory |
SLOs: search p95 ≤ 3 s · screening decision p95 ≤ 150 ms · list pages p95 ≤ 300 ms · synthesis p95 ≤ 60 s · availability 99.5% monthly · RPO 15 min · RTO 4 h.

## 3. Topology
```
Users ─► Cloudflare (DNS, TLS, CDN, WAF, rate limits, DDoS)
             │  static SPA from CDN        │ /api/*, /admin/* (admin also behind Cloudflare Access)
             ▼                             ▼
        Object/CDN origin        Load balancer (accepts Cloudflare ranges only)
                                           │
                       ┌───────────────────┴───────────────────┐
                       ▼ private app subnet                    ▼ private app subnet
                 API containers x2–3                     Worker containers x2–4
                 (FastAPI, stateless)                    queues: ingest · embed · llm · export · scan
                       │        │         │                    │        │         │
                       ▼        ▼         ▼                    ▼        ▼         ▼
                 PgBouncer   Redis    Object store       Postgres  Redis   Object store (+ AV scanner)
                       │   (cache, rate    (PDFs, exports,   (primary + replica, PITR)
                       ▼    limit, queue)   backups)
                 Postgres 16 + pgvector (private data subnet)
   Egress: NAT with allow-list ► OpenAlex · Crossref · PubMed · Unpaywall · LLM/embedding providers · SMTP
   Observability: logs, metrics, traces ► Grafana stack or managed + Sentry-compatible errors
```

## 4. Servers and platform
Provider-neutral spec (map to AWS, GCP, or a container PaaS; verify current instance names and prices):
| Component | Spec (Tier M) | Notes |
|---|---|---|
| Edge | Cloudflare plan with WAF and rate limiting | Access policy on `/admin/*`; authenticated origin pulls |
| API | 2–3 containers × (2 vCPU, 4 GB); autoscale on CPU/RPS | Stateless; graceful shutdown; health + readiness probes |
| Workers | 2–4 containers × (4 vCPU, 8 GB); autoscale on queue depth | One process type per queue; concurrency caps |
| Postgres | 1 primary 8 vCPU / 32 GB / 500 GB NVMe + 1 replica (HA and read) | pgvector, pg_trgm; PgBouncer; WAL archiving to object store (PITR) |
| Redis | 2–4 GB managed | Cache, rate-limit counters, job queue; AOF for queue DB |
| Object store | S3-compatible, versioning, server-side encryption, lifecycle rules | Presigned URLs; private buckets |
| AV scanner | 1 vCPU container | Scans every upload before parse |
| Region | One region near the largest user group (e.g., Singapore for APAC) | Second region only at Tier L |
Order-of-magnitude monthly cost: infrastructure a few hundred to ~one thousand USD, plus LLM and OpenAlex usage (budgeted separately). Use provider calculators; do not budget from this line.

## 5. Network
- VPC with three layers: public (load balancer only), private app, private data. Databases and Redis have no public address.
- Origin accepts traffic only from Cloudflare ranges with authenticated origin pulls; direct-to-origin requests are dropped.
- Egress only through NAT/proxy with a domain allow-list (sources, model providers, SMTP, package mirrors during build only).
- No public SSH. Operator access through a cloud session manager or private mesh VPN with SSO + passkey.
- Admin paths require identity-aware proxy **and** in-app step-up (see 17).
- TLS 1.2+ everywhere; HSTS only over HTTPS; certificates automated; internal traffic encrypted where the platform allows.

## 6. Security architecture
| Layer | Controls |
|---|---|
| Identity | Passkey + single-use email link + recovery codes; server-side revocable sessions; step-up for admin; rate limits |
| Authorization | System-admin flag plus project roles; deny by default; Postgres row-level security on tenant tables; two-tenant tests |
| Data | Encryption at rest and in transit; secrets in a secret manager; no user text in logs; export and delete flows |
| Uploads | Type sniffing, size caps, AV scan, sandboxed parsing, no server-side URL fetch |
| LLM | OWASP LLM Top 10 review; untrusted-text delimiting; no tools for synthesis models; budgets and quotas; truthful usage logging |
| Supply chain | Lockfiles, pinned base images by digest, SCA + SAST + container scan, SBOM, signed images, ≥ 14-day-old dependencies |
| Operations | Immutable infrastructure, audit log of admin actions, backup restore tests, incident runbooks |
| Privacy | Retention schedule, sub-processor register, regional-law review (UU PDP, PDPA, GDPR) with counsel |

## 7. Backend design
- **Modular monolith** (keep): FastAPI, SQLAlchemy 2, Alembic, Pydantic v2. Extract workers first; extract services only on evidence.
- **Contract-first:** OpenAPI under `/api/v1`; generated TypeScript client; breaking changes need a version bump.
- **Jobs:** Redis-backed queues (arq); idempotency keys on POST; `jobs` table for status; retries with jitter; dead-letter queue; cancellation.
- **Streaming:** Server-Sent Events for run progress; polling fallback.
- **Caching:** works by id (ETag, 7 d), search results (1 h), source responses (per-source TTL), rate-limit counters in Redis.
- **Backpressure:** 429 with Retry-After; per-user concurrency caps for synthesis and exports.
- **LLM gateway:** one adapter layer with provider routing, per-task models, timeouts, budgets, and **truthful usage events** (provider, model, tokens, cost, request id). No fabricated numbers.
- **Sources strategy:** see ADR-011 (mirror of selected OpenAlex snapshot + live API fallback + cache).
- **Retrieval:** embed only works that enter a library or a synthesis scope; hybrid search (FTS + vector + rerank); halfvec storage; HNSW tuned (m 16, ef_construction 64, ef_search 40–100) and benchmarked on the golden set.

## 8. Frontend design
React + TypeScript + Vite static build on the CDN; React Router; TanStack Query; generated API client; i18next with `en` default and `id` locale pack (more locales pluggable); design tokens from `prototype/design-tokens.json`; strict CSP with nonces and no inline script; error boundaries; Sentry-compatible reporting; route-level code splitting (≤ 250 KB gzip initial JS per route); WCAG 2.2 AA; keyboard-first screening; feature flags; PWA/offline queue later. UI additions: first-run owner wizard, Admin console, Security settings (passkeys, sessions), Evidence & Method drawer on every AI or analysis output, run provenance panel, quota and budget meter.

## 9. Data design (see `03b-data-model-v2.sql`)
Server-side sessions and single-use link tables; invitations; truthful `llm_usage_events`; journal–article links to real works; monthly partitions for events; row-level security templates; half-precision vectors; retention policies. Keep `works` shared and tenant data project-scoped.

## 10. Reliability
Rolling deploys, expand/contract migrations, PITR (35 d), nightly logical dump to a second bucket, replica failover drill before launch, queue dead-letter alerts, circuit breakers per source, degrade to retrieval-only when models fail.

## 11. Observability and cost control
Structured logs with request ids; OpenTelemetry traces across API → worker → source → model; metrics: latency, error rate, queue depth, source errors, model tokens and cost per feature, OpenAlex metered spend, DB CPU/IO, replica lag, cert expiry. Alerts: SLO burn, queue depth, cost at 80% of budget, failed backups.

## 12. Environments and delivery
`local` (Compose), `staging` (production-like, synthetic data), `production`. CI: lint, types, tests, contract, truth audit, scans, build, deploy to staging, e2e, manual promote. Migrations as a pre-deploy job.

## 13. Trade-offs and what to revisit
| Decision | Trade-off | Revisit when |
|---|---|---|
| Modular monolith | Simpler; one deploy unit | Team > 6 or one module dominates load |
| Postgres + pgvector | One store, transactional | > 5M vectors or HNSW build times hurt |
| Managed containers over Kubernetes | Less control, far less ops | Need multi-region or custom networking |
| Single region | Cheaper, simpler | Users outside the region report latency > 300 ms |
| Embed-on-add | Smaller index, cheaper | Users expect global semantic search |
