# ADR-002: Postgres + pgvector as the single store
- Status: accepted
## Context
Need relational data, full-text, and vector search at ≤ ~500k works / few million chunks in v1.
## Options
1. Postgres+pgvector+FTS. 2. Postgres + dedicated vector DB + search engine.
## Decision
Option 1. Re-evaluate at > 5M chunks or p95 retrieval > 800 ms.
## Consequences
+ Simple ops, transactional tenancy. − Scaling ceiling; HNSW build/memory tuning needed.
