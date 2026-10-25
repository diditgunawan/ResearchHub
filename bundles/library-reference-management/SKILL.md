---
name: library-reference-management
description: Protocol for the researcher's reference library — importing and exporting RIS, BibTeX, CSV, CSL-JSON, collections and tags, attaching a user's own PDFs, duplicate review and merging, citation formatting with CSL, and optional Zotero interoperability. Use this skill whenever a task involves bibliographies, reference imports/exports, parse reports, deduplicating a user's imported records, folders/collections, PDF attachments, or formatting citations (APA, Vancouver, IEEE, etc.), even if the user only says "reference manager" or "bibliography".
---

# Library & Reference Management Protocol (LIB)

Goal: a trustworthy, lossless-as-possible project library whose imports are transparent and whose merges are reversible.

## Preconditions
Read `AGENTS.md`; load `scholarly-data-ingestion` (for Work upserts), `fullstack-engineering-standards`, `qa-security-deployment`. Read `references/requirements.md` and `references/format-mapping.md`.

## Protocol
**P1 — Parse safely.** Parse in a worker with size/time limits using vetted parsers (RIS, BibTeX, CSL-JSON, CSV with user-confirmed column mapping). Never `eval`; never trust encodings (detect, default UTF-8).
**P2 — Produce a parse report.** Per row: imported / skipped / error + reason + line reference. Store in `import_batches.report`. UI shows counts and downloadable error list.
**P3 — Resolve to works.** Match by DOI/PMID first; else fuzzy match (DAT dedup rules); else create a minimal Work flagged `source=import`. Optionally enrich later via connectors (job) — enrichment never overwrites user-provided fields.
**P4 — Dedup review.** Candidates go to the review queue; merging stores a `merge_snapshot` so undo is exact. Keep both records' provenance.
**P5 — Organize.** Collections (tree), tags, notes; all project-scoped; soft-delete.
**P6 — Files.** Users may upload their own PDFs: validate type/size, AV scan, store in private object storage, compute sha256, extract text in a worker, scope chunks to the project only (never public index).
**P6b — Extract-only mode (LIB-017).** Offer *Keep original* or *Extract-only*. In extract-only: validate → extract text/metadata/references → verify success → delete original → keep derived data only → audit the deletion.
**P7 — Export.** RIS, BibTeX, CSL-JSON, CSV; round-trip tests import→export→import must preserve core fields (title, authors, year, venue, DOI, abstract, keywords).
**P8 — Citation formatting.** Use CSL styles with a maintained CSL processor; ship a small default style set; allow user-selected style; never hand-roll formatters.
**P9 — Zotero (optional, SHOULD).** One-way import via user-supplied API key or exported file; keys encrypted at rest; never required.

## Hard rules
- MUST NOT silently drop records or fields; every skip is reported.
- MUST NOT merge irreversibly.
- MUST NOT put user PDFs or text into shared/global tables or indexes.
- MUST NOT fetch URLs found inside imported files.

## Definition of Done
Relevant `LIB-*` MUSTs pass; round-trip fixtures green; malicious-file tests green; handoff written.

## Handoffs
→ `screening-prisma-workflow` (library items are screened) · → `grounded-synthesis-rag` (chunks from user files) · → `research-integrity-ai-ethics` (reference checks) · → `literature-mapping-positioning` (library subsets and uploads feed maps).
