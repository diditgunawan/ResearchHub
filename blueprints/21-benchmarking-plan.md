# 21 — Benchmarking Plan (v0.6)

Purpose: replace self-reported "all green" with external, repeatable measurement; also supply the labelled data that the relevance floor (SYN-023), prioritised screening (SCR-019), and verifier (SYN-022) need for calibration. Harness: `scripts/benchmark/` (metrics proven by unit tests). Datasets are downloaded on demand and never committed.

## 1. Datasets (verified to exist, 27 Oct 2026; licence to confirm in blueprint 11)
| Dataset | What it is | Use |
|---|---|---|
| **SYNERGY** (De Bruin et al. 2023, DOI 10.34894/HE6NAQ) | 169,288 works from 26 systematic reviews; 2,834 labelled included (1.67%); titles, abstracts, references, topics; obtain via the `synergy-dataset` Python package | B1 dedup (as a record source), B2 screening, B3 search recall, B6 citation-evidence checks |
| **Cohen collection** (curated medical review datasets, referenced by ASReview studies) | Earlier labelled screening sets, one derived set is a known hard case | B2 secondary suite |
| **SciLitBench** (arXiv 2609.05505) | Multi-stage benchmark from one real review: frozen splits for abstract screening, full-text decisions, extraction over 888 full texts, six fields | B4 extraction and synthesis grounding |
| Our golden sets (blueprint 05, QAS-025) | Claims with human labels; unanswerable and adversarial queries; labelled lineage fixture | B4, B6, relevance floor calibration |
| Synthetic perturbation set (built from SYNERGY) | Real records with injected duplicates (case, punctuation, missing DOI, abbreviated journal) | B1; labelled **synthetic** in every report |

## 2. Suites, metrics, baselines
| Suite | Task | Metrics | Baselines |
|---|---|---|---|
| B1 Dedup | Find duplicate pairs | Pair precision, recall, F1 | ASySD, synthesisr (pinned versions) |
| B2 Screening prioritisation | Rank records, reviewer screens from top | WSS@95, WSS@100, recall at 10/20/30% screened, average time to discovery | Random; keyword match to the review title; ASReview LAB default and multilingual models |
| B3 Search recall | Query built from the review question against the federated search | Recall@50 and @200 of included works | OpenAlex direct query; BM25 on title |
| B4 Extraction and synthesis | Extract fields; produce cited claims; refuse when thin | Field accuracy and F1; verbatim-excerpt presence; citation precision; verifier-human agreement; refusal correctness; cost and latency per run | GROBID plus rules for structure; model-only without retrieval |
| B5 Reporting | PRISMA counts, kappa, checklists | Exact equality with official PRISMA generator input; kappa equals reference implementation | Official PRISMA 2020 generator |
| B6 Mapping | Lineage parent accuracy; cluster quality | Top-1 and top-3 parent accuracy on labelled fixture; NMI; determinism | Citation links as weak truth where available |
| B7 Load | Mixed workload at Tier M | p95 latency, error rate (QAS-028) | None |

## 3. Acceptance thresholds
Do not invent numbers. Run baselines first; record medians per suite in an ADR; then set thresholds relative to the best baseline (for example, B2 median WSS@95 not more than 10 percentage points below ASReview on the same reviews). Hard rules that need no calibration: PRISMA counts reconcile exactly (B5); citation precision and fabricated-citation rate follow blueprint 05 (zero fabricated).

## 4. Harness design
1. `scripts/benchmark/metrics.py` (done, 8 unit tests).
2. `run_screening_benchmark.py` accepts any ranker with the signature `rank(records, query, seed)`.
3. Add per-suite runners that write JSON: suite, dataset version, seed, git sha, model ids, date, metrics, baseline results.
4. Nightly CI and pre-release: run B1–B5 on pinned dataset versions; publish a Markdown report; regressions beyond ADR thresholds block release (QAS-033).
5. Keep reference tools in an isolated environment and report them next to ours (QAS-034).
6. Report honestly: show weak suites, not only strong ones; flag synthetic data; never tune on a suite's test split.

## 5. Order of work
First B5 (cheap, exact), then B2 on three SYNERGY reviews, then B1, then B3, then B4 once the verifier is independent. B2 and B4 unlock calibration of SCR-019, SYN-021/023.
