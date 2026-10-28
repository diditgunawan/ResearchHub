# LIB requirements
| ID | Level | Requirement |
|----|-------|-------------|
| LIB-001 | MUST | Support import of RIS, BibTeX, CSV (with column mapping), and CSL-JSON. |
| LIB-002 | MUST | Imports run as background jobs with progress and are idempotent per file hash + project. |
| LIB-003 | MUST | Parsing enforces limits: file ≤ 25 MB, ≤ 50,000 records, 60 s CPU; violations produce a clear error. |
| LIB-004 | MUST | Every import yields a parse report (imported/skipped/error with reason and line ref) stored and downloadable. |
| LIB-005 | MUST | Records match to existing works by DOI/PMID, then fuzzy rules; unmatched create minimal works flagged `source=import`. |
| LIB-006 | MUST | Enrichment never overwrites user-provided fields; it fills nulls only. |
| LIB-007 | MUST | Dedup candidates enter a review queue; merge stores `merge_snapshot`; undo restores exact prior state. |
| LIB-008 | MUST | Collections (tree), tags, and notes are project-scoped and soft-deletable. |
| LIB-009 | MUST | Export in RIS, BibTeX, CSL-JSON, CSV; round-trip preserves title, authors, year, venue, DOI, abstract, keywords. |
| LIB-010 | MUST | User file uploads validate MIME by content sniffing, size ≤ 50 MB, AV scan, and are stored in private object storage with sha256. |
| LIB-011 | MUST | Text extracted from user files is chunked into project-scoped chunks only (`scope='user_file'`). |
| LIB-012 | MUST | Citation formatting uses CSL styles via a maintained CSL processor; ≥ 5 common styles bundled. |
| LIB-013 | MUST | Imported text is treated as untrusted: sanitized for display; URLs inside are never fetched server-side. |
| LIB-014 | SHOULD | Zotero import via user API key or file; keys encrypted at rest; feature optional. |
| LIB-015 | MUST | Library list supports 5,000 items with server-side pagination, sort, filter; p95 ≤ 1.5 s. |
| LIB-016 | MUST | Deleting an item/file is soft first, hard-purged within 30 days; export includes user notes. |
| LIB-017 | MUST | PDF uploads offer `extract_only` mode: after successful extraction the original is deleted and only derived data is kept; deletion is verified and audited; failed extractions purge the file within 24 h. |
| LIB-018 | SHOULD | Interoperability: import Rayyan CSV and RIS exports and ASReview-style CSV (title, abstract, label); export ASReview-compatible CSV; imported decisions are stored as `imported` records and never counted as a reviewer's own decision; round-trip fixtures pass. |
