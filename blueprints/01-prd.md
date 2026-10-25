# 01 — Product Requirements Document

## Epics and user stories (acceptance = Given/When/Then, summarized)
| ID | Story | Acceptance |
|----|-------|-----------|
| E1-S1 | As a user I search scholarly works by keyword/question and filter by year, type, OA, language. | Results ≤ 3 s p95 from cache/index; filters combinable; each result shows source + fetched date. |
| E1-S2 | I open a work and see abstract, authors, venue, DOI, citations, references, OA link. | Missing fields shown as "not available", never guessed. |
| E1-S3 | I explore a citation network (cited-by / references) from one work. | Depth ≤ 2; expands lazily; add-to-library from graph. |
| E2-S1 | I import RIS/BibTeX/CSV/CSL-JSON and PubMed/other exports. | Parse report: imported / skipped / errors with line refs. |
| E2-S2 | I deduplicate; ambiguous pairs go to a review queue. | Merge is reversible; provenance of both kept. |
| E2-S3 | I organize into collections/tags, attach my own PDFs, export any format. | Round-trip import→export preserves core fields. |
| E3-S1 | I define a review protocol (question, PICO/PEO, criteria, databases, dates). | Versioned; changes logged. |
| E3-S2 | I screen title/abstract then full text with controlled exclusion reasons. | Keyboard-first UI; decision log immutable. |
| E3-S3 | A second reviewer screens blindly; conflicts are resolved by a third action. | Agreement (Cohen's kappa) displayed; unresolved conflicts block advance. |
| E3-S4 | I get a PRISMA 2020 flow diagram computed from decisions. | Numbers equal log counts; export SVG/PNG/CSV. |
| E3-S5 | Optional AI suggestions with rationale for screening. | Never auto-applied; suggestion + human decision both logged. |
| E4-S1 | I ask a research question and get a synthesis grounded in my library or search results. | Every claim has ≥1 citation to a retrieved chunk; verification status visible. |
| E4-S2 | I see per-study structured extraction (population, method, finding, limitations). | Editable by user; edits tracked. |
| E4-S3 | System refuses when evidence is insufficient. | Refusal text lists what was searched. |
| E5-S1 | I generate an AI-use disclosure statement from my logged usage. | Matches log; editable; copy/export. |
| E5-S2 | I check my reference list: unresolved DOIs, retractions, mismatches. | Report with per-item status and links. |
| E6-S1 | I paste title+abstract and get ranked journals with explainable scores and filters (quartile, APC, OA, language, indexing). | Each score shows components and data freshness date; no acceptance-probability claims. |
| E6-S2 | I get a submission-readiness checklist for a chosen journal. | Sourced from journal's author guidelines URL (user-confirmed). |
| E7-S1 | I manage projects, invite collaborators with roles (owner/reviewer/viewer). | ACL enforced server-side. |
| E7-S2 | I export or delete all my data. | Export within 24 h; deletion complete within 30 days. |
| E8-S1 | I turn a search result set or library subset into a topic map of themes. | Clusters sized by members; labels from metadata; click-through lists; add cluster to library; deterministic re-run. |
| E8-S2 | I see my library organized into research families. | Min size 3; others "Unplaced"; each placement links to evidence. |
| E8-S3 | I trace how approaches evolved (parent–child lineage) and audit the evidence. | Chronology rule enforced; confidence bands; Low ⇒ Needs review; table + CSV. |
| E8-S4 | I add my manuscript and see its closest family and likely parent papers. | Top-3 parents with component scores; shared vs distinctive concepts; wording "closest in the analyzed set". |
| E8-S5 | I see gaps and unresolved issues in my analyzed set. | Typed signals with source excerpts; persistent "not global novelty" banner. |
| E8-S6 | I upload PDFs for mapping in extract-only mode. | Original PDF deleted after successful extraction; derived data kept. |
| E8-S7 | I correct a placement manually. | Override tracked; evidence unchanged; reset available. |

## Functional requirements (FR) — summary index
FR-DAT (E1) · FR-LIB (E2) · FR-SCR (E3) · FR-SYN (E4) · FR-ETH (E5) · FR-JRN (E6) · FR-ENG (E7, platform) · FR-MAP (E8). Detailed, testable requirements live in each bundle's `references/requirements.md` with IDs.

## Non-functional requirements
| Area | Requirement |
|---|---|
| Performance | Search p95 ≤ 3 s; library page load ≤ 1.5 s for 5k items; synthesis first token ≤ 5 s, full ≤ 60 s |
| Scale (v1) | 1k users, 5k works/library, 500k works cached |
| Availability | 99.5% monthly (v1) |
| Security | OWASP ASVS L2 target; LLM Top-10 mitigations (see 06) |
| Privacy | No model training on user content; manuscript text never in logs; export/delete |
| Accessibility | WCAG 2.2 AA |
| i18n | EN + ID (SHOULD), UTF-8 everywhere, locale-aware dates |
| Observability | Structured logs, traces, per-feature LLM cost metrics |
| Cost | Hard per-user weekly LLM budget; global monthly cap with alert at 80% |

## Release criteria for v1
All MUST requirements pass; golden-set evals meet thresholds (05); security checklist (06) complete; legal/source register current (11).
