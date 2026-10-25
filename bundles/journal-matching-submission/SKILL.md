---
name: journal-matching-submission
description: Protocol for the journal database, explainable journal-matching score, hard filters (quartile, APC, open access, language, indexing), data-freshness labelling, journal-quality signals and submission-readiness checklists. Use this skill whenever a task involves choosing or recommending journals, Scopus/Sinta/DOAJ data, quartiles, APC, scope matching, "where should I publish", journal embeddings, or manuscript submission checklists, even if phrased as "find me a journal for my abstract".
---

# Journal Matching & Submission Protocol (JRN)

Goal: transparent, honest journal recommendations built from licensed/open data, with visible freshness and no false promises.

## Preconditions
Read `AGENTS.md`, `references/requirements.md`, `references/scoring-spec.md`; load `research-integrity-ai-ethics` (always), `scholarly-data-ingestion`, `fullstack-engineering-standards`, `qa-security-deployment`.

## Protocol
**P1 — Verify journal data rights (gate JRN-001).** For each field source (OpenAlex sources, DOAJ, Scopus source list, SINTA, publisher pages), confirm in the source register whether storing and redisplaying is permitted. If unclear or forbidden: omit the field, or ask the data owner; never scrape.
**P2 — Build the journal profile.** Per journal: metadata, scope text, languages, OA/APC flags, indexing flags, `guidelines_url`, `data_as_of`. Profile embedding = normalized mix of scope-text embedding and centroid of recent article embeddings (last 3 years, sample ≤ 200).
**P3 — Match.** Input title + abstract (+ keywords). Compute components (see `scoring-spec.md`): semantic similarity, keyword/topic overlap, venue-citation affinity (journals frequently cited by the user's library), then apply hard filters *before* ranking.
**P4 — Explain.** Return score (0–100) with component breakdown, matched topics, similar recent articles (linked, with DOI), and `data_as_of`. Never output "probability of acceptance" or implied guarantees.
**P5 — Quality signals.** Show indexing facts (e.g., in DOAJ), APC, OA model, and a caution panel with how to verify a journal (publisher identity, indexing in claimed databases, editorial board, peer-review process). Do not label journals "predatory"; surface verifiable signals only.
**P6 — Checklist.** Given a journal and a user-confirmed `guidelines_url`, generate a checklist (word limit, abstract format, reference style, ethics statements, AI-use policy) with each item citing the source line/URL; items the system cannot confirm are marked "verify manually".
**P7 — Freshness.** Show `data_as_of`; mark stale (> 12 months) data; schedule refresh jobs.
**P8 — Evaluate.** Maintain labelled set (≥ 60 abstracts with known good venues); report top-5 hit rate and keep it above threshold.

## Hard rules
- MUST NOT show metrics (quartile, rank, APC) without source and date.
- MUST NOT store/redisplay licensed data against its terms.
- MUST NOT claim acceptance likelihood.
- MUST NOT label a journal "predatory" or "safe".

## Definition of Done
Relevant `JRN-*` MUSTs pass; evals ≥ threshold; source register rows verified; handoff written.
