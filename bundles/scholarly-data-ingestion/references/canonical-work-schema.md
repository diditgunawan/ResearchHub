# Canonical WorkRecord (connector output → `works`)
| Field | Type | Rules |
|---|---|---|
| doi | str? | normalized lowercase, no prefix |
| openalex_id / pmid | str? | source ids as given |
| title | str | required; trimmed; HTML stripped |
| abstract | str? | reconstructed/sanitized; ≤ 20k chars |
| year | int? | publication year |
| work_type | str? | article, review, preprint, book-chapter, ... |
| language | str? | ISO 639-1 if given |
| authors[] | {name, orcid?, position} | order preserved |
| venue | {name, issn_l?, openalex_id?}? | |
| is_oa / oa_url | bool? / str? | oa_url must be a direct landing/PDF link from source |
| cited_by_count | int? | source-labelled |
| retracted | bool | false unless source says otherwise |
| relations[] | {type, target_id} | erratum_of, preprint_of, version_of |
| provenance | {field: {source, fetched_at}} | required for each populated field |
