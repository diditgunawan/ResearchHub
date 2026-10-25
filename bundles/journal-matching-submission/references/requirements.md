# JRN requirements
| ID | Level | Requirement |
|----|-------|-------------|
| JRN-001 | MUST | Each journal data field's source and licence/terms for storage and redisplay are verified and recorded before ingestion. |
| JRN-002 | MUST | Journals store `data_as_of` and provenance per field; UI always shows source and date for metrics. |
| JRN-003 | MUST | Journal search supports filters: category/field, quartile (if licensed), indexing (DOAJ etc.), OA, APC (none/≤ amount), language, country, publisher, free text. |
| JRN-004 | MUST | Hard filters apply before scoring; filtered-out journals never appear. |
| JRN-005 | MUST | Match input is title + abstract (+ optional keywords); max 6,000 characters; input is not stored unless user saves it to a project. |
| JRN-006 | MUST | Score components (semantic, keyword/topic, citation affinity) and weights are returned and displayed; weights configurable server-side. |
| JRN-007 | MUST | Each recommendation lists ≥ 3 similar recent articles from that journal with DOIs when available. |
| JRN-008 | MUST | UI/API never show acceptance probability or guarantees; copy reviewed against a disclaimer list. |
| JRN-009 | MUST | Quality signals are factual and verifiable (indexing, OA model, APC); no "predatory/safe" labels; verification guide shown. |
| JRN-010 | MUST | Submission checklist items cite source URL/line; unverifiable items are marked "verify manually". |
| JRN-011 | MUST | Data older than 12 months is visibly marked stale; refresh jobs scheduled. |
| JRN-012 | MUST | Offline eval set (≥ 60 labelled abstracts) tracks top-5 hit rate; regression below threshold blocks release. |
