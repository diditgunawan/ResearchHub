# MAP requirements
| ID | Level | Requirement |
|----|-------|-------------|
| MAP-001 | MUST | Every map/lineage run has an explicit scope (search result set or library subset); scope, parameters, seed, embedding model, and code version are stored in `map_runs`. |
| MAP-002 | MUST | Runs are capped (default 500 records); larger scopes are refused with guidance; records lacking a title are excluded and reported. |
| MAP-003 | MUST | Runs are deterministic: identical inputs, parameters, seed, and models produce identical clusters/lineage (tested). |
| MAP-004 | MUST | Cluster labels derive from metadata keywords (deterministic c-TF-IDF); optional LLM labels are constrained to the cluster's keyword set, marked AI-generated, and logged per ETH. |
| MAP-005 | MUST | Clustering uses multilingual embeddings so mixed-language sets work; record language per item and show language mix. |
| MAP-006 | MUST | Topic map UI sizes clusters by member count, supports click-through lists and "add cluster to library", exports PNG/SVG/CSV, and offers an accessible table/list alternative. |
| MAP-007 | MUST | Lineage edges use only in-set evidence: citation, semantic similarity, keyword/concept overlap, chronology; each edge stores its component scores. |
| MAP-008 | MUST | Chronology hard rule: a parent's year ≤ child's year; same-year links require citation evidence. |
| MAP-009 | MUST | Confidence bands (High/Medium/Low) follow `algorithms.md`; Low confidence yields "Needs review" and no auto-assigned parent. |
| MAP-010 | MUST | Families are produced by the documented algorithm with a minimum size (default 3); others are "Unplaced"; roots are identified by rule, not guessed. |
| MAP-011 | MUST | The audit table lists every paper with branch, parent, evidence types, confidence, status, and missing-metadata flags; it is sortable, filterable, searchable, and CSV-exportable. |
| MAP-012 | MUST | Every visual placement (map, tree, lineage) links to its audit row and stored evidence; nothing is rendered without evidence. |
| MAP-013 | MUST | User overrides of parent/branch are allowed, tracked (who, when, previous value), keep machine evidence unchanged, and can be reset. |
| MAP-014 | MUST | Data-quality gaps (missing abstract, DOI, year, references, keywords) are flagged with reason codes and surfaced in the table. |
| MAP-015 | MUST | Manuscript positioning returns closest family, top-3 parent candidates with component scores, and shared vs distinctive concepts; copy says "closest in the analyzed set" and never claims novelty. |
| MAP-016 | MUST | Manuscript text is processed in private scope; `retain_text=false` by default; only derived vectors/results persist; deletion on request; never logged. |
| MAP-017 | MUST | The gap view emits typed signals (unresolved condition, future-work, lineage gap, data-quality), each with source work, ≤ 300-character excerpt from open-access or user-owned text, and extractor version; a persistent banner states a gap is not global novelty. |
| MAP-018 | MUST | The module never generates related-work prose; optional AI may only rewrite evidence summaries, labelled and logged per ETH-001/ETH-002. |
| MAP-019 | SHOULD | Botanical tree, lineage map, and table views share one analysis without recomputation; lineage diagram exports to SVG/PNG using our own visual language. |
