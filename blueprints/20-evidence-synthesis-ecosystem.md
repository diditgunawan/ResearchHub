# 20 — Evidence-Synthesis Ecosystem: references, protocols, tools (v0.6)

Source index: *Awesome Evidence Synthesis Tools* (github.com/evidencesynthesis-tools/awesome-evidence-synthesis, licence **CC BY 4.0**, read 27 Oct 2026, 140 tools in 10 categories, activity Feb–Aug 2026). Attribution: tool names and categories below are adapted from that list. The list indexes **open-source tools only**; it has no benchmark datasets and no protocol documents, so those come from the sources named in sections 3 and in blueprint 21.
Rule: reference tools are for ideas, interoperation, and baselines. Reuse of code follows ADR-008 (verify licence per tool). Each tool's licence is **not** assumed from the list; record it in blueprint 11.

## 1. How each category maps to our bundles
| List category (tools in list) | Our bundle | Use | Gap it reveals |
|---|---|---|---|
| Literature Search (13): OpenAlex, CitationChaser, Paperfetcher, citracer, litsearchr, searchbuildR, SRA Polyglot, PubMed Search Tester, europepmc, CiteSource, SRA2, TERA Explorer, PyMedTermino | DAT | We already use OpenAlex. Others are reference designs | **No search-strategy log, no query translation between databases, no citation snowballing, no source-contribution analysis** → DAT-021 |
| Text Mining & NLP (6): PubTator 3.0, BioTextQuest, LitLLMs, QuickUMLS, MetaNLP, SciSpaCy | MAP, SYN | Concept extraction for lineage and gaps; BioTextQuest and our topic map solve the same discovery problem | Biomedical entity linking is optional later |
| Screening (10): ASReview, ReviewAid, Abstrackr, revtools, metagear, RobotSearch, DenseReviewer, rayyanR, RefRandomiser, Trial2rev | SCR | **Baselines and design reference** for prioritised screening; rayyanR shows demand for Rayyan-export interop; RefRandomiser supports double screening | **No prioritised screening, no stopping diagnostics** → SCR-019; Rayyan interop → LIB-018 |
| Data Extraction & Cleaning (12): GROBID, prismAId, ReAct-ExtrAct, Auto-STEED, WebPlotDigitizer, Engauge, metaDigitise, SurvdigitizeR, Taguette, QualCoder, MSE FINDR, Tabula | LIB, SYN | GROBID for PDF to structured text (already in register); ReAct-ExtrAct and prismAId are source-grounded extraction designs | Figure digitising and qualitative coding stay out of v1 |
| Risk of Bias (7): RobotReviewer, RCT-Reviewer, robvis, Critiplot, NOS-TLPlot, Metatron, CINeMA | new (v2) | Reference for an appraisal module; robvis and Critiplot name common instruments (RoB 2, ROBINS-I, QUADAS-2, MMAT, ROBIS, GRADE, NOS, JBI) | **No risk-of-bias or certainty-of-evidence module in the spec**; decision in ADR-012: export, do not rebuild, in v1 |
| Reference Management (3): ASySD, synthesisr, HAWC | LIB | ASySD and synthesisr are **dedup baselines**; HAWC is a transparency-first review CMS to study | None |
| Workflow & Automation (12): Colandr, SyRF, PredicTER, metaverse, PRISMA 2020 flow generator, ROSES flowchart, PROMETHEUS, LLAssist, ProfOlaf, LatteReview, MedSci Skills, EvidenceSynthesis | SCR, SYN, process | PRISMA 2020 generator is the **reference output for our flow**; PROMETHEUS and LatteReview are LLM pipelines (human-centred local vs multi-agent) for design contrast; MedSci Skills is an MIT Claude Code skill suite for evidence synthesis, a structural reference for our skills | Our PRISMA export should match the official generator's input |
| Visualization & Reporting (15): EviAtlas, VOSviewer, bibliometrix, Open Knowledge Maps, CorTexT, flowchart, forest plot tools | MAP | Evidence-map and network exports; Open Knowledge Maps already referenced | Export formats → MAP-020 |
| Meta-analysis (39) and Statistics (13): metafor, meta, netmeta, PyMARE, JASP, and others | out of scope v1 | Provide an analysis-ready export; do not rebuild statistics (ADR-012) | → ENG-031 |

## 2. Supporting tools: how we use them
| Role | Tools | Rule |
|---|---|---|
| Baseline in benchmarks | ASReview LAB (screening ranking), ASySD and synthesisr (dedup), PRISMA 2020 generator (flow numbers), GROBID (PDF extraction) | Pin versions; record licences; run in a separate environment; never vendor their code |
| Interoperate | Rayyan exports (via CSV/RIS), ASReview CSV, Zotero RIS/CSL, VOSviewer/EviAtlas files, metafor/PyMARE CSV | Import and export only; imported decisions are tagged `imported` |
| Reference design | LatteReview, PROMETHEUS, LLAssist, prismAId, ReAct-ExtrAct, DenseReviewer | Read for ideas; any reuse needs ADR-008 |
| Optional later | RobotReviewer/RCT-Reviewer, robvis, SciSpaCy, QuickUMLS, PubTator 3.0 | Evaluate per milestone with the register |

## 3. Supporting protocols and reporting standards
From the tool list: **PRISMA 2020** (flow diagram generator), **ROSES** (environmental evidence reporting), and risk-of-bias or certainty instruments named by robvis and Critiplot (RoB 2, ROBINS-I, QUADAS-2, MMAT, ROBIS, GRADE, NOS, JBI tools). Standard references **not in the list** that the app should also support (verify current versions): **PRISMA-S** (reporting of searches), and protocol registration with **PROSPERO** or **OSF**.
| Standard | What the app does |
|---|---|
| PRISMA 2020 | Computed flow (SCR-011/012) plus export compatible with the official generator and a 27-item checklist skeleton (SCR-021) |
| PRISMA-S | Search log with source, platform, exact query, filters, date, hit count (DAT-021) |
| Protocol registration | Protocol export with registry-style fields and deviation log (SCR-020) |
| ROSES | Flow output option in a later locale/discipline pack |
| RoB and GRADE instruments | v1: record the instrument chosen in the protocol and export extracted fields for robvis; native module is a v2 decision |

## 4. New requirements from this review
DAT-021 search log and snowballing · LIB-018 Rayyan and ASReview interop · SCR-019 prioritised screening with stopping diagnostics (advisory only) · SCR-020 protocol export · SCR-021 PRISMA generator-compatible export · MAP-020 evidence-map exports · ENG-031 analysis-ready export · QAS-033 benchmark harness · QAS-034 baselines against reference tools. Details in each bundle's requirements file.

## 5. Licence and attribution
The awesome list is CC BY 4.0: keep attribution to *Awesome Evidence Synthesis Tools* wherever its entries or categories are reproduced. Tools it lists meet its own inclusion test (OSI-approved licence, public code), but **verify each licence yourself** before reuse, especially copyleft terms for a hosted service.
