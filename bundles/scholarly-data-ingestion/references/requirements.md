# DAT requirements
| ID | Level | Requirement |
|----|-------|-------------|
| DAT-001 | MUST | Before using a source, its current terms/auth/limits are verified and recorded in the source register with date and link. |
| DAT-002 | MUST | Every source is accessed via a connector implementing `SourceConnector`; the rest of the app never imports source-specific code. |
| DAT-003 | MUST | External calls are made server-side only, with an identifying User-Agent and required contact/mailto/API-key parameters. |
| DAT-004 | MUST | Rate limits are enforced client-side below the documented maximum; HTTP 429/5xx use exponential backoff with jitter (max 3 retries). |
| DAT-005 | MUST | Each connector has a timeout (default 8 s), circuit breaker, and returns structured errors; one failing source never fails a federated search. |
| DAT-006 | MUST | Federated search responses include `source_status` per source and label partial results. |
| DAT-007 | MUST | DOIs are normalized (lowercase, no URL prefix); invalid DOIs are rejected into the import/ingest report, not stored. |
| DAT-008 | MUST | Missing fields are stored as `NULL`; no inference or fabrication of metadata, authors, or abstracts. |
| DAT-009 | MUST | `works.provenance` records `{source, fetched_at}` per populated field; field-level conflict resolution uses trust order: Crossref (bibliographic fields) > OpenAlex > PubMed (biomedical) > others; user edits outrank all. |
| DAT-010 | MUST | Abstracts delivered as inverted indexes are reconstructed deterministically; abstracts are length-capped and sanitized (no HTML injection). |
| DAT-011 | MUST | Identifier upserts are idempotent (unique DOI/PMID/OpenAlex id); concurrent ingests do not create duplicates. |
| DAT-012 | MUST | Fuzzy dedup uses the thresholds in SKILL.md P7; scores and decisions are stored; auto-links are reversible. |
| DAT-013 | MUST | Errata/corrections/retraction notices and preprint↔published pairs are linked via relation, never silently merged. |
| DAT-014 | MUST | Responses are cached with per-source TTL (default search 1 h, work 7 d, citations 24 h) and a cache key containing normalized params. |
| DAT-015 | SHOULD | Citation graph expansion is lazy, depth ≤ 2, and capped (default 200 nodes) with "load more". |
| DAT-016 | MUST | Pagination uses the source's cursor mechanism; deep paging beyond a cap (default 1,000 results) is refused with guidance to refine the query. |
| DAT-017 | MUST | Connector tests use recorded, scrubbed fixtures covering success, empty, malformed, 429, and timeout; a nightly live smoke test is non-blocking. |
| DAT-018 | MUST | No scraping of sites that disallow automated access or forbid it in terms; adding a new source requires an ADR. |
| DAT-019 | SHOULD | An optional BASE (or similar broad multilingual) connector may be added only after its access policy and reuse rights are verified (DAT-001) and an ADR is written; sources feeding topic maps must expose title, abstract, language, and year or be flagged incomplete. |
| DAT-020 | MUST | OpenAlex credentials are sent as the `api_key` query parameter; a key is required outside local dev; the connector tracks metered usage (rate-limit endpoint), degrades to the local mirror/cache when the daily budget is exhausted, and never relies on the retired `mailto` polite pool. |
| DAT-021 | SHOULD | Every search writes a search-log row (PRISMA-S style): source, platform or API, exact query string, filters, date and time, result count, fetched count; backward and forward citation chasing (depth at most 2) records its seed work and provenance; the log exports as a table; optional query translation between sources is tested on recorded examples. |
