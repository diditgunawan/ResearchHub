# Retraction & correction check
1. Source: confirm current open dataset/API (e.g., Crossref update metadata incl. Retraction Watch data) in the source register; record licence and cadence.
2. Match by normalized DOI; also match against `relations` (retraction notice → original).
3. Statuses: retracted · expression_of_concern · corrected · none_found · unknown (source unavailable).
4. Store `works.retracted` + `retraction_checked_at`; refresh weekly for library items, on-demand for search results.
5. UI: red badge "Retracted" with link to notice; synthesis excludes retracted works by default (user-overridable with warning); exports include status column.
6. Never state "no retraction exists"; state "none found as of {date} in {source}".
