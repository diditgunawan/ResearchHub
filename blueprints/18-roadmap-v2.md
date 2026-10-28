# 18 — Roadmap v2 (supersedes the milestone order in 10 where they conflict)

Source: audit of the ResearchHub implementation (25 Oct 2026), competitive brief, product brainstorm. Format: Now / Next / Later with exit gates. Roadmap v1 (`10-roadmap-backlog.md`) stays as the feature backlog.

## Status overview
Implementation exists (FastAPI + React). Three critical defects reproduced (auth, provenance, synthesis gate). 26 of 45 contract operations built. Priority is **truth and safety first, then scale foundations, then research power**.

## Now — Phase 0 "Truth and Safety" (weeks 0–2)
| Item | Requirements | Exit |
|---|---|---|
| Single-owner access mode, tokens never returned, boot guard | ENG-021, 022, 025 | `truth_audit.py` P1–P3 pass; both-mode tests pass |
| Server-side sessions, single-use links, rate limits | ENG-023, 024 | replay and expiry tests pass |
| Truthful provenance and honest disclosure | ETH-016 | model never logged without call; disclosure rewritten |
| Relevance floor and independent verifier | SYN-021, 022 | irrelevant query refused; circularity test fails bad claims |
| Remove hard-coded journal records (demo flag only) | JRN-013 | no DOI literals in app code |
| Restore strict coverage gate, correct PROJECT_STATE | QAS-026, 027 | gate hash pinned; state file machine-checked |
Gate G0: `python scripts/truth_audit.py --repo . --pin scripts/integrity.sha256` exits 0 on all 14 probes (P1–P14), and tests pass from a clean clone (QAS-031). Round 1 of the upgrade reached 8 of 14; see PROJECT_STATE.

## Next — Phase 1 "Scale foundations" (weeks 2–6)
Postgres + Alembic + PgBouncer in all non-test environments (ENG-027); Redis queue and rate limiting; object storage + AV scan; CI with scans; staging environment; OpenAlex key fix and mirror design (DAT-020, ADR-011); dedup queue; contract parity (close 19 missing operations); one named test per MUST ID; passkeys and recovery codes (ENG-026); admin console v1.
Add the benchmark harness skeleton with B5 and a first B2 baseline (QAS-033, scripts/benchmark) so later calibration has data; add the search log (DAT-021).
Gate G1: contract tests green; CI green; staging mirrors production topology; QAS-029 network scan passes.

## Next — Phase 2 "Evidence engine" (weeks 6–10)
Hybrid retrieval (FTS + vector + rerank) with embed-on-add; real model gateway with truthful usage events; extraction runs; SSE progress; quotas and budgets; verifier evaluation against a labelled set; golden evals in CI.
Prioritised screening with logged models and advisory stopping diagnostics (SCR-019); B1 to B4 runs with baselines (QAS-033/034); thresholds recorded in an ADR, relevance floor calibrated on SYNERGY and golden sets.
Gate G2: SYN thresholds in blueprint 05 met on the golden set; cost per run within budget.

## Later — Phase 3 "Research power" (weeks 10–14)
Licensed journal ingestion (DOAJ/OpenAlex first; Scopus/SINTA only if rights allow); lineage polish; positioning; topic map or deliberate link-out; i18n `en` + `id` + locale-pack mechanism; accessibility and e2e suites; audit_events everywhere; export and delete.
Interoperability and exports: Rayyan and ASReview CSV (LIB-018), protocol export (SCR-020), PRISMA generator-compatible export (SCR-021), evidence-map exports (MAP-020), analysis-ready export (ENG-031).
Gate G3: a11y and e2e green; JRN-001 register verified.

## Later — Phase 4 "Pilot and launch readiness" (weeks 14–18)
Load test at Tier M (QAS-028); failover and restore drills (QAS-030); penetration test; privacy documents and sub-processor register; staging rehearsal of switch to `multi_user`; pilot with 10 researchers across disciplines and regions plus 2 supervisors.
Gate G4: release checklist complete; pilot trust and time-saved metrics reviewed; owner decides when to flip `ACCESS_MODE`.

## North-star and KPIs
| KPI | Target |
|---|---|
| Share of shown claims with an independent verification verdict | 100% (extractive labelled as such) |
| Fabricated citations or provenance entries reaching users | 0 |
| Time from question to screened 200 records | ≤ 1 working day |
| Pilot users who would defend the audit trail to a supervisor | ≥ 7 of 10 |
| p95 SLOs at Tier M | met for 2 consecutive weeks |

## Risks and dependencies
| Risk | Mitigation |
|---|---|
| Another loosened gate or self-reported green | Hash-pinned gate script; truth audit in CI; code owners |
| OpenAlex metering raises cost | Snapshot mirror + cache + budget alerts |
| Model quality or cost surprises | Gateway with budgets; golden-set evaluation before each model change |
| Journal data rights | Verify per field; omit if unclear |
| Scope creep | Roadmap gates; ADR for additions |
| Single builder fatigue | Agent lanes, small PRs, weekly truth audit |

## Agent lanes
Lane A security and access (ENG-021..026, QAS-026/029) · Lane B data and sources (DAT, LIB, ADR-011) · Lane C evidence engine (SYN, ETH) · Lane D frontend and design (ENG-013..016, prototype tokens) · Lane E quality and delivery (QAS). Rule: contract and migration changes land first, one migration owner at a time.

## Changes this update
Added Phase 0 ahead of all feature work; moved topic map to Later; added access mode, scale foundations, and truth gate; journals demoted until licensed data exists; added 17 requirements from audit findings.
