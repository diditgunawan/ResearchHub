# 00 — Vision & Scope

## Vision
A research workspace that takes a researcher from a question to a defensible, citation-verified evidence base and a submission-ready manuscript plan, with every AI step transparent, logged, and under human control.

## Problem
Researchers juggle separate tools for searching (aggregators), screening (systematic-review software), evidence synthesis (AI search), and journal selection. Data moves by manual export/import, provenance is lost, and AI tools can fabricate citations.

## Principles
1. **Grounded or silent** — generated claims cite retrieved sources, or the system says it doesn't know.
2. **Human in the loop** — AI suggests; people decide.
3. **Open data first** — built on open scholarly APIs; every source's terms recorded.
4. **Auditable** — screening decisions, AI usage, and data provenance are logged.
5. **Small and finishable** — a thesis-compatible scope; integrate (Zotero) rather than rebuild.

## In scope (v1)
Search & import; library & dedup; PRISMA-style screening with PRISMA 2020 flow counts; grounded evidence synthesis with citation verification; AI-use disclosure helper; journal matching with filters; EN/ID interface (SHOULD).

## Out of scope (v1)
Meta-analysis statistics (forest plots) — v2. Patent search. Full manuscript ghost-writing. "Humanizer"/AI-detector evasion (never). Native mobile apps. Scraping any site that disallows it. Institutional SSO (v2).

## Personas
- **P1 PhD student (primary)** — runs a literature review, needs rigor and speed.
- **P2 Supervisor/co-reviewer** — second screener, resolves conflicts, reads synthesis.
- **P3 Early-career author** — picks a journal and checks readiness.

## Success metrics
- Time from question to a screened set of 200 records ≤ 1 working day.
- Citation precision (cited chunk supports claim) ≥ 95% on golden set; fabricated citations reaching users = 0.
- ≥ 90% of imported references deduplicated correctly on test corpus.
- PRISMA counts reproducible from the decision log with zero manual edits.

## Constraints
Solo/small-team build; free-tier-friendly infra; open-data rate limits; configurable per-user weekly LLM budget.

## Top risks
| Risk | Mitigation |
|---|---|
| Hallucinated citations | Retrieval-only citations + verification pass (SYN, ETH) |
| API terms/limits change | Source-terms register, adapters behind an interface (DAT) |
| Scope creep | Roadmap gates; ADR for additions (AGENTS G12) |
| Privacy of unpublished work | No training on user data, retention limits (ETH, QAS) |
| Coverage bias (English, STEM) | Disclose coverage, multi-source search (DAT, ETH) |
