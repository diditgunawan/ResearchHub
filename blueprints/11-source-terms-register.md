# 11 — Source & Terms Register

**Agents MUST re-verify each row at build time (rule G3) and fill `Verified on` + `Link`.** Values below are starting hypotheses, not facts to rely on.

| Source | Use in app | What to verify | Auth / limits (verify) | Licence/terms (verify) | Verified on | Link |
|---|---|---|---|---|---|---|
| OpenAlex | works, authors, venues, citations, abstracts (often inverted index) | endpoints, pagination, current auth requirement, rate limits, abstract availability | | data licence & attribution | | |
| Crossref REST | DOI metadata, reference checks, retraction/update info | polite-pool requirements (mailto), rate limits, update-type fields | | metadata licence | | |
| PubMed E-utilities | biomedical search/import | API key effect on rate limits, usage policy | | NLM terms | | |
| Unpaywall | OA full-text location | email param, daily limits | | terms | | |
| Semantic Scholar API (optional) | extra citations/embeddings | key requirement, limits, allowed use | | API licence | | |
| CORE / Europe PMC (v2) | OA full text | limits, reuse rights | | | | |
| DOAJ | journal OA/quality signal | API/dump access | | | | |
| Scopus source list | quartile data | **whether storing/redisplaying is allowed** | | Elsevier licence | | |
| SINTA (Indonesia) | national journal rank | **whether bulk collection/redisplay is allowed; ask owners** | | | | |
| Zotero Web API | optional import/export | user-supplied key flow, limits | | | | |
| Retraction data (via Crossref/Retraction Watch dataset) | retraction flags | dataset licence, update cadence | | | | |
| LLM provider(s) | synthesis, extraction, rerank | data retention/training opt-out, regions, pricing | | | | |
| Embedding provider/model | vectors | dimensions (schema uses 1024), licence | | | | |

## Never integrate
Sites that disallow automated access or forbid scraping in terms (including commercial competitors' apps), shadow libraries, or paywalled full text without a licence.

## Added v0.2 (mapping references)
| Source / component | Use in app | What to verify | Auth / limits (verify) | Licence/terms (verify) | Verified on | Link |
|---|---|---|---|---|---|---|
| BASE (Bielefeld Academic Search Engine) | Optional broad multilingual source for topic maps (OKMaps draws on it per their site) | Access method, registration/whitelisting, rate limits, reuse and redisplay rights | | | | |
| Open Knowledge Maps source code (GitHub org `OpenKnowledgeMaps`) | Possible reference/reuse | Licence per repository, copyleft implications, attribution, whether our hosting triggers obligations; follow ADR-008 | | Per-repo licence; site content stated as CC BY 4.0 | | |
| PaperTree | Idea reference only | No code/data/visual reuse; no automated access without permission | n/a | Not open source as far as seen | | |
| PDF extraction (e.g., GROBID or equivalent) | Metadata/reference extraction for uploads | Licence, deployment model, accuracy on ID/EN papers | | | | |
| Keyphrase/clustering libraries | MAP features | Licences, maintenance, pinned versions (ENG-020) | | | | |
