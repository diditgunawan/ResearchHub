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

## Added v0.6 (evidence-synthesis ecosystem)
| Source / tool | Use | What to verify | Auth / limits (verify) | Licence/terms (verify) | Verified on | Link |
|---|---|---|---|---|---|---|
| Awesome Evidence Synthesis Tools (list) | Reference index for tools, categories | Attribution wording | n/a | CC BY 4.0 (LICENSE file read 27 Oct 2026) | 2026-10-27 | github.com/evidencesynthesis-tools/awesome-evidence-synthesis |
| SYNERGY dataset | Benchmarks B1 to B3, B6 | Dataset licence, version, OpenAlex id fields, download method | `synergy-dataset` package | Check DataverseNL record (DOI 10.34894/HE6NAQ) | | github.com/asreview/synergy-dataset |
| SciLitBench | Benchmark B4 | Licence, frozen splits, access | | Check paper and repository | | arxiv.org/abs/2609.05505 |
| ASReview LAB | Baseline for B2 | Licence, version, model names, install | | Verify before any reuse (ADR-008) | | asreview.ai |
| ASySD, synthesisr | Baselines for B1 | Licence, R version, input format | | Verify | | camaradesuk.github.io/ASySD, martinwestgate.com/synthesisr |
| PRISMA 2020 flow generator | Reference for B5 | Input CSV schema, licence | | Verify | | estech.shinyapps.io/PRISMA_flowdiagram_latest |
| GROBID | PDF extraction baseline | Licence, deployment, accuracy | | Verify | | grobid.github.io |
| DenseReviewer, LatteReview, PROMETHEUS, LLAssist, prismAId, ReAct-ExtrAct | Design references for screening and extraction | Licence, maturity | | Verify before reuse | | see list |
| CitationChaser, Paperfetcher, litsearchr, SRA Polyglot | Reference for snowballing and search strategy | Licence, API dependencies (Lens, Crossref, COCI) | | Verify | | see list |
| RobotReviewer, robvis, Critiplot | Risk-of-bias references and export targets | Licence, instruments covered | | Verify | | see list |
| MedSci Skills | Structural reference for skill suites | Licence (MIT stated in list), scope | | Verify | | github.com/Aperivue/medsci-skills |

