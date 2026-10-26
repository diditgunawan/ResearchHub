# ResearchForge Mastermind Plan v2

Prepared 26 Oct 2026 · Built from: the ResearchHub code audit, the competitive brief, the product brainstorm, and the system-design, architecture and roadmap methods. Companion files are in package v0.4 (blueprints 16, 17, 18, schema delta 03b, ADR-009 to 011, and scripts/truth\_audit.py). This document is the one-page brain for the whole project: what we are building, how it is accessed, how it scales, and what happens next.

## 1. The plan at a glance

| Topic | Decision |
| --- | --- |
| Product | A verified-evidence research workspace for **any research context worldwide**. Indonesian and ASEAN support is a locale pack that adds value, not a limit. |
| Wedge | Trust: every claim, placement and AI use shows real evidence, and the tool says when it does not know. |
| Access now | **Single-owner mode.** One account is both administrator and user. Every multi-user flow stays built and tested. |
| Scale now | **Middle scale (Tier M):** up to 5,000 registered users, about 600 daily, 120 concurrent at peak, 50 requests per second design peak. |
| Order of work | Truth and safety first, then scale foundations, then the evidence engine, then research power, then pilot. |
| Safety net | A truth-audit script with 8 behavioural probes. It fails 8 of 8 on the current ResearchHub code. Phase 0 is done when all pass. |

## 2. Strategy upgrade

**What changed.** The audit showed the code has good bones but the three claims that matter most (secure, verified, honestly disclosed) were not true. Competitors are strong on corpus size and AI extraction (Elicit, Consensus), screening (Rayyan), and maps (Litmaps, ResearchRabbit, Open Knowledge Maps). None combines a PRISMA-grade audit trail, independent verification and an accurate AI-use record in one place. That gap is the opportunity.

**Positioning.** For researchers in any field who must defend their literature review and journal choice, ResearchForge is a verified-evidence workspace that keeps an auditable trail from search to screening to cited synthesis to submission. Unlike AI search tools that give fluent answers, every claim and placement shows its evidence.

**Four pillars.** Verify (citation and claim checks, truthful AI log). Audit (blind screening, computed PRISMA, evidence per link). Position (lineage, manuscript fit, in-set gaps, always worded as relative to the analysed set). Locale (multi-language interface and local data sources, starting with English and Indonesian).

**What we will not do.** Compete on model quality or corpus size; claim novelty; build detector-evasion tools; keep unlicensed or invented data; copy competitors.

**Riskiest assumptions and cheapest tests.** (1) Researchers accept extra rigor for defensibility: run five real reviews end to end and measure trust and time. (2) Open data is enough: sample 50 papers from several regions and check coverage. (3) Verification can be real: label 100 claims and compare the verifier with humans. (4) Someone pays: interview supervisors and library staff before building billing.

## 3. Access model: one account, two hats, nothing deleted

The owner asked for one user who is both access administrator and user, without removing related flows. The design keeps everything and closes the door.

- **Settings.** ACCESS\_MODE is single\_owner now and multi\_user later. Registration is closed in single-owner mode.
- **Two hats.** system\_admin is an instance-level flag, separate from project roles. The owner holds both, and the interface has a normal workspace and an Admin console in the same login.
- **Flows kept.** Invitations, roles, quotas, audit log, session management and the admin console are all built and tested in both modes. In single-owner mode they work on the one account and invitations stay off until the admin enables them.
- **Sign-in.** Passkey as primary, single-use email link as fallback, one-time recovery codes for emergencies. Local development prints the link in the server console on loopback only. No token is ever returned in an HTTP response.
- **Sessions.** Stored on the server, hashed, idle expiry 12 hours, absolute expiry 7 days, revocable, rotated on login and on privilege change.
- **Admin safety.** Admin actions need a fresh passkey or link within 10 minutes and are written to an append-only audit log.
- **Going multi-user later.** Flip the setting, choose invite-only or open registration, turn on email delivery and quotas, then pass the staging load and network gates. No rewrite.

## 4. Middle-scale blueprint

### 4.1 Targets and load estimate

| Item | Estimate |
| --- | --- |
| Traffic | Average about 3 requests per second; design for 50 at peak |
| Synthesis | About 240 runs per day, about 20 model calls each, budget cap $1,500 per month with alert at 80% |
| Source searches | About 4,800 per day, more than a free OpenAlex key allows, so use a local mirror plus cache |
| Data | About 4M works (10 GB), 2M embedded chunks (about 8 GB plus 6 to 8 GB index), decisions about 8 GB per year, PDFs about 300 GB |
| Database year 1 | 60 to 90 GB on 500 GB NVMe with 32 GB RAM |
| Service goals | Search 3 s, screening decision 150 ms, lists 300 ms, synthesis 60 s (all p95); 99.5% availability; recovery point 15 minutes; recovery time 4 hours |

These are planning assumptions. Re-measure after the pilot.

### 4.2 Architecture

```
Users -> Cloudflare (DNS, TLS, CDN, WAF, rate limits)
           |-- static SPA from CDN
           '-- /api and /admin (admin also behind Cloudflare Access)
                 -> Load balancer (edge ranges only)
                      -> API containers x2-3 (FastAPI, stateless)
                      -> Worker containers x2-4 (ingest, embed, llm, export, scan queues)
                           -> PgBouncer -> Postgres 16 + pgvector (primary + replica, PITR)
                           -> Redis (cache, rate limit, queue)
                           -> Object store (PDFs, exports, backups) + AV scanner
           Egress allow-list: OpenAlex, Crossref, PubMed, Unpaywall, model providers, SMTP
           Observability: logs, metrics, traces, error tracking
```

### 4.3 Servers and platform

| Part | Specification |
| --- | --- |
| Edge | Cloudflare with WAF, rate limiting, identity-aware access for admin paths |
| API | 2 to 3 containers, 2 vCPU and 4 GB each, autoscale on load |
| Workers | 2 to 4 containers, 4 vCPU and 8 GB each, autoscale on queue depth |
| Postgres | Primary 8 vCPU, 32 GB, 500 GB NVMe, plus one replica; PgBouncer; continuous archiving for point-in-time restore |
| Redis | 2 to 4 GB managed |
| Object store | S3-compatible, versioned, encrypted, private, presigned links |
| Region | One, near the largest user group (for example Singapore for Asia-Pacific) |

Platform choice: managed containers plus managed database and cache, not Kubernetes (ADR-010). Start on a single host with Compose for solo use and reuse the same images at Tier M. Monthly infrastructure is roughly a few hundred to about a thousand dollars; model and OpenAlex usage are budgeted separately. Use provider calculators before committing.

### 4.4 Network and security

- Three network layers: public (load balancer only), private application, private data. Databases and Redis have no public address.
- The origin accepts traffic only from the edge with authenticated origin pulls. Outbound traffic goes through an allow-listed NAT or proxy. No public SSH; operators use a session manager or private mesh VPN with SSO and passkey.
- Application security: deny-by-default authorization, row-level security on tenant tables, upload scanning and sandboxed parsing, strict content security policy, secrets in a secret manager, no user text in logs, signed and pinned container images, dependency and container scanning, append-only audit trail.
- AI security: untrusted-text delimiting, no tools for synthesis models, budgets and quotas, and truthful usage records only.
- Privacy: retention schedule, export and delete flows, sub-processor register, review of Indonesian UU PDP, Taiwan PDPA and EU GDPR with qualified counsel.

### 4.5 Backend and frontend design

- **Backend.** Keep the modular monolith (FastAPI, SQLAlchemy, Alembic). Contract-first API with generated client. Redis-backed job queues with idempotency keys, retries with jitter and a dead-letter queue. Server-sent events for run progress. Backpressure with Retry-After. One model gateway with budgets and truthful usage events.
- **Data sources.** Mirror a selected slice of the free OpenAlex snapshot locally, use the live API for fresh and long-tail items, cache everything, send the API key as a query parameter, and embed only works that enter a library or synthesis (ADR-011).
- **Retrieval.** Hybrid full-text plus vector plus rerank, half-precision vectors, index parameters tuned on the golden set.
- **Frontend.** React and TypeScript static build on the CDN, React Router, TanStack Query, generated client, i18next with English default and Indonesian pack, design tokens, strict CSP, route-level code splitting under 250 KB, WCAG 2.2 AA, keyboard-first screening, error boundaries.

### 4.6 UI and UX upgrade

Keep the calm scholarly look from the prototype. Add: first-run owner wizard; Admin console; Security settings (passkeys, sessions, recovery codes); an Evidence and Method drawer on every AI or analysis output that states what is real and what is rule-based; run provenance panel; quota and budget meter; reflective one-line prompts per workflow step; empty, loading and error states everywhere. Wording rules stay: AI content labelled, analysis relative to the analysed set, gaps never called novelty.

### 4.7 Database schema

The v0.4 delta (blueprint 03b) adds: instance settings; single-use login links; server-side sessions; passkey credentials; recovery codes; invitations; a provenance mode on AI usage (llm or rule\_based) with a constraint that real models need a provider; a partitioned model-usage events table; admin flag and request ids on audit events; journal-to-article links that point to real works; a source mirror state table; retention policies; plus templates for half-precision vectors and row-level security. It parses cleanly with the Postgres parser; the first live run is part of Phase 1.

### 4.8 Reliability, observability, cost

Rolling deploys with expand-contract migrations; 35-day point-in-time restore plus nightly dumps to a second bucket; circuit breakers per source; fallback to retrieval-only if models fail. Track latency, errors, queue depth, source errors, tokens and cost per feature, OpenAlex spend, database load, replica lag, certificate expiry. Alert on service-goal burn, cost at 80% of budget and failed backups.

### 4.9 When to move beyond middle scale

Consider Tier L when service goals are missed two weeks running, database CPU stays above 60%, or vectors exceed about 5 million. Then add a dedicated vector store, more replicas, and possibly Kubernetes and a second region.

## 5. Plan v2: phases and gates

| Phase | Weeks | Work | Gate |
| --- | --- | --- | --- |
| 0 Truth and safety | 0 to 2 | Single-owner access, no tokens over HTTP, server-side sessions, single-use links, rate limits, boot guard, truthful provenance and disclosure, relevance floor, independent verifier, remove hard-coded journals, restore strict coverage gate | truth\_audit exits 0 |
| 1 Scale foundations | 2 to 6 | Postgres and Alembic everywhere, Redis queue and limits, object store with scanning, CI with scans, staging, OpenAlex key fix and mirror design, dedup, contract parity, one named test per MUST, passkeys, admin console v1 | Contract and CI green; network scan passes |
| 2 Evidence engine | 6 to 10 | Hybrid retrieval, real model gateway with true usage, extraction, SSE, quotas, verifier evaluation, golden evals in CI | Quality thresholds met within budget |
| 3 Research power | 10 to 14 | Licensed journal data, lineage polish, positioning, topic map or link-out, i18n, accessibility and e2e, export and delete | Accessibility and e2e green |
| 4 Pilot and launch readiness | 14 to 18 | Load and soak tests, failover and restore drills, penetration test, privacy documents, staging rehearsal of multi-user, pilot with 10 researchers and 2 supervisors | Release checklist done; owner decides when to open registration |

KPIs: 100% of shown claims carry an independent verdict (extractive ones labelled); zero fabricated citations or provenance entries; question to screened 200 records within a working day; at least 7 of 10 pilot users would defend the audit trail to a supervisor; service goals met two weeks running.

Agent lanes: A security and access; B data and sources; C evidence engine; D frontend and design; E quality and delivery. Contract and migration changes land first; one migration owner at a time.

## 6. Control tower

**Truth gate.** Run python scripts/truth\_audit.py --repo your-repo --pin scripts/integrity.sha256 on every merge. Baseline on ResearchHub today: 0 pass, 8 fail (token returned, link replay, immortal session, irrelevant query accepted, false provenance, 18 hard-coded DOIs, loosened coverage gate, production boots with defaults).

**Decisions made.** Single-owner access with flows kept (ADR-009). Middle-scale topology (ADR-010). Hybrid source strategy and embed-on-add (ADR-011). Earlier: open data first, append-only screening log, claim-level citations, no detector evasion, relative wording.

**Top risks.** Loosened gates or self-reported green (hash-pinned gate, truth audit, code owners). OpenAlex metering (mirror, cache, alerts). Model cost or quality surprises (gateway budgets, golden set before any model change). Journal data rights (verify per field, omit if unclear). Scope creep (phase gates, ADRs). Builder fatigue (agent lanes, small changes, weekly audit).

**Decisions needed from the owner.** Product name and code licence. Hosting provider and budget. Model and embedding provider with retention terms. Whether to reuse Open Knowledge Maps code or link out. Which journal data sources you can legally use. Discipline mix for golden sets and the pilot. Who performs legal review.

## 7. How to run this

1. Give the Phase 0 prompt in docs/AGENT\_PROMPTS.md to your coding agent. It starts with the access model and the truth-audit failures.
2. After each task, run the truth audit and the package validator; update docs/PROJECT\_STATE.md.
3. Do not start the evidence engine or journals until gate G0 and G1 pass.
4. Run the five-researcher test during Phase 1 so the roadmap reacts to real use.

## 8. Package map (v0.4)

README and MANIFEST list all 100 files. New in v0.4: blueprints 16 (scale), 17 (access), 18 (roadmap), 03b (schema delta); ADR-009, 010, 011; 17 new requirements (182 total, 170 MUST); rules G14 (truthful provenance) and G15 (access mode); scripts truth\_audit.py and integrity.sha256; updated PROJECT\_STATE and agent prompts.
