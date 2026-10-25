---
name: scholarly-data-ingestion
description: Protocol for building and changing anything that fetches, normalizes, caches, or deduplicates scholarly metadata from external sources (OpenAlex, Crossref, PubMed, Unpaywall, Semantic Scholar, DOAJ). Use this skill whenever the task mentions search connectors, API clients, rate limits, DOIs, canonical Work records, metadata normalization, abstracts, citation graphs, caching, provenance, or dedup of works, even if the user doesn't say "ingestion". Also use before adding any new external data source.
---

# Scholarly Data Ingestion Protocol (DAT)

Goal: reliable, polite, provenance-tracked ingestion of open scholarly data into the canonical `works` model (`blueprints/03-data-model.sql`).

## Preconditions
- Read `AGENTS.md` global rules (G1–G12) and `references/requirements.md`.
- Load `fullstack-engineering-standards` and `qa-security-deployment`.

## Protocol
**P1 — Verify the source (gate DAT-001).** Open the source's *current* docs and terms. Update the row in `blueprints/11-source-terms-register.md` (auth, limits, licence, date, link). If terms forbid the planned use, STOP and report. Broad multilingual sources such as BASE (used by Open Knowledge Maps) are candidates only after this check (DAT-019).
**P2 — Implement behind the interface.** One connector per source implementing `SourceConnector` (see `references/connector-interface.md`). No source-specific logic outside `app/sources/<name>/`.
**P3 — Normalize.** Map to the canonical Work schema (`references/canonical-work-schema.md`). Normalize DOI (lowercase, strip `https://doi.org/`), reconstruct abstracts if delivered as inverted index, trim whitespace, keep original language.
**P4 — Provenance.** For each populated field record `{source, fetched_at}` in `works.provenance`. Never overwrite a field from a higher-trust source with a lower-trust one (trust order in requirements DAT-009).
**P5 — Be polite and resilient.** Identify the app (User-Agent + contact email/mailto where the source asks), respect documented limits, exponential backoff with jitter, per-source circuit breaker, timeouts (8 s default), cache with TTL, and request coalescing.
**P6 — Federated search.** Fan out in parallel, merge by identifiers, return per-source status (`ok|timeout|error`) — partial results are acceptable and labelled.
**P7 — Dedup.** Exact: DOI/PMID/OpenAlex id. Fuzzy: normalized title similarity + year ± 1 + first-author surname (+ venue). Thresholds: ≥ 0.95 auto-link as same work, 0.85–0.95 → review queue, < 0.85 distinct. Hard-negative rules: errata/corrections/comments, preprint-vs-published are *linked*, not merged.
**P8 — Test with recorded fixtures.** Record real responses (scrubbed), assert normalization, pagination, error paths. Add one nightly live smoke test, non-blocking.
**P9 — Document.** Update `docs/PROJECT_STATE.md`, the source register, and an ADR if a new source was added.

## Hard rules
- MUST NOT scrape HTML of sites that disallow automated access or forbid it (G4).
- MUST NOT guess missing metadata. Missing = `null`.
- MUST NOT call external APIs from the browser; only from API/workers.
- MUST NOT store more raw payload than needed (size cap; no full-text from unlicensed sources).

## Definition of Done
All `DAT-*` MUSTs relevant to the change pass; tests named `test_DAT_###_*`; register row current; no secrets committed; handoff note written.

## Handoffs
→ `library-reference-management` (records exist) · → `grounded-synthesis-rag` (abstracts/OA text for chunking) · → `research-integrity-ai-ethics` (retraction flags) · → `literature-mapping-positioning` (abstracts, languages, reference lists, concepts).
