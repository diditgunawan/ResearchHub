# 02 — System Architecture

## Context
Users (browser) → Web app → API → {Postgres+pgvector, Redis, Object storage} and external {OpenAlex, Crossref, PubMed, Unpaywall, Semantic Scholar (optional), LLM provider}.

## Component diagram
```mermaid
flowchart LR
  U[Browser SPA<br/>React+TS] -->|HTTPS JSON| API[FastAPI<br/>REST + SSE]
  API --> DB[(Postgres<br/>+ pgvector)]
  API --> R[(Redis<br/>cache + queue)]
  API --> S3[(Object storage<br/>PDFs, exports)]
  W[Workers<br/>arq/Celery] --> DB
  W --> R
  W --> S3
  API -->|enqueue| R
  W --> CON[Source connectors]
  CON --> OA[OpenAlex]
  CON --> CR[Crossref]
  CON --> PM[PubMed E-utils]
  CON --> UP[Unpaywall]
  W --> LLM[LLM adapter] --> LP[LLM provider(s)]
  W --> EMB[Embedding adapter]
```

## Modules (backend `app/`)
`identity` · `projects` · `sources` (connectors) · `works` (canonical records, dedup) · `library` (collections, import/export, files) · `screening` · `retrieval` (index, hybrid search) · `synthesis` (RAG, verification) · `integrity` (DOI/retraction checks, disclosure) · `journals` · `mapping` (topic maps, families, lineage, positioning, gaps) · `jobs` · `billing_quota` · `audit`.
Each module: `router.py`, `service.py`, `models.py`, `schemas.py`, `tests/`. Cross-module calls go through `service` interfaces only.

## Key flows
**Search/import:** UI → `/works/search` → connector fan-out (async, timeouts) → normalize → upsert `works` → return ids; heavy enrichment queued.
**Screening decision:** UI → `POST /screening/decisions` → validates role/stage → append-only insert → recompute counters (materialized by query) → emits audit event.
**Synthesis:** UI → `POST /synthesis` → job → retrieve (BM25+vector) → rerank → extract → draft with chunk-id citations → verify each claim → store run (inputs, chunks, prompts hash, model, cost) → stream result via SSE.
**Journal match:** abstract → embed → compare to journal profile vectors → combine with keyword + hard filters → explainable score.

## Technology choices (see ADRs)
| Concern | Choice | Why |
|---|---|---|
| API | FastAPI, Pydantic v2, SQLAlchemy 2, Alembic | Typed, OpenAPI-first |
| DB | Postgres 16 + pgvector + pg_trgm + FTS | One store for relational, vector, text |
| Queue | Redis + arq (or Celery) | Simple, async-friendly |
| Frontend | React + TypeScript + Vite + Tailwind + TanStack Query | Fast iteration |
| Auth | Email magic link + OAuth (OIDC); sessions via secure cookies | No password storage v1 |
| Files | S3-compatible (MinIO local) | Portable |
| LLM | Provider-agnostic adapter | Avoid lock-in; swap models |
| Observability | OpenTelemetry, structured JSON logs, Sentry-compatible | Standard |
| Deploy | Docker Compose (dev), single VM or PaaS (v1) | Cheap, simple |

## Data ownership & boundaries
- `works` are **shared, global, deduplicated metadata** (public data only).
- `library_items`, `decisions`, `notes`, `files`, `synthesis_runs` are **tenant (project) scoped**.
- User uploads (PDFs, manuscripts) never enter shared tables or global indexes.

## Failure & resilience
Connector timeouts 8 s, retries with jitter (max 3), circuit breaker per source; partial results labelled by source; jobs idempotent with dedupe keys; LLM failures degrade to retrieval-only results.

## Multi-tenancy
Row-level project scoping enforced in service layer and by Postgres RLS (SHOULD) on project tables.

## Mapping module (added v0.2)
- **Inputs:** scope = search result set or library subset; works' embeddings (shared `Embedder`), concepts, reference lists (from connectors), OA/user text for gap signals.
- **Flow:** `POST /maps` → job → feature prep → cluster → label → persist `map_runs/map_clusters` → UI. `POST /lineage` → job → families → edge scoring → bands → persist `lineage_nodes/edges`. `POST /positioning` → manuscript in private scope → compare → persist derived results only. `POST /gaps` → extract signals → persist excerpts ≤ 300 chars.
- **Determinism:** fixed seeds and pinned algorithm versions stored in `map_runs.params`.
- **Frontend:** one analysis payload feeds tree, lineage, and table views (no recompute); every view has a table alternative.
- **Dependencies (verify per ENG-020):** clustering (hdbscan/scikit-learn), community detection (igraph/leidenalg or networkx), keyphrases (YAKE/KeyBERT-style or own c-TF-IDF), optional PDF extraction (e.g., GROBID service) — each needs an ADR if a new service.
