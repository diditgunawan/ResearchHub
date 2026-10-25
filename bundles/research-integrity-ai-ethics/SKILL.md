---
name: research-integrity-ai-ethics
description: Protocol for research integrity and responsible AI in an academic tool — citation verification, retraction checks, AI-use logging and disclosure statements, labelling AI output, privacy of unpublished manuscripts, coverage-bias disclosure, and refusal of detector-evasion ("humanizer") features. Use this skill ALWAYS alongside any task that generates AI text, touches journals or manuscripts, handles user-uploaded documents, or concerns disclosure, plagiarism, authorship, retractions, or academic ethics, even if the user doesn't mention ethics.
---

# Research Integrity & AI Ethics Protocol (ETH)

Goal: help researchers do honest work faster; never help conceal AI use or fabricate evidence.

## Preconditions
Read `AGENTS.md` and `references/requirements.md`; templates in `references/ai-disclosure-templates.md`; retraction method in `references/retraction-check.md`.

## Protocol
**P1 — Classify the feature.** Does it (a) generate text, (b) transform user text, (c) judge/rank, (d) handle private documents? Map to required controls in `requirements.md`.
**P2 — Label.** All AI-generated or AI-modified content carries a visible "AI-generated" marker and a link to how it was produced (model, date, verification status).
**P3 — Log usage.** Each AI feature call writes `ai_usage_log` (feature, stage, model, purpose, human_reviewed flag) with no content text. The user can mark outputs as reviewed.
**P4 — Disclosure generator.** Build statements from the log using templates; user edits before copying; add a note to check the target journal's own AI policy.
**P5 — Verify citations.** Provide a reference-check job: resolve each DOI/reference via Crossref/OpenAlex, compare title/year/first author, flag mismatches, unresolved, retracted/corrected. Never auto-"fix" without user confirmation.
**P6 — Retractions.** Use the retraction/update signals available via Crossref (verify current data source in register); flag in library, search, synthesis. Show date checked.
**P7 — Authorship boundary.** Writing helpers are limited to modes: outline suggestions, critique/feedback, language editing, structure checks. Do not produce a full manuscript presented as the user's finished work; do not generate fabricated data, references, or peer-review text meant to be submitted as a real review.
**P8 — Detector evasion = out.** Do not build or tune anything whose purpose is to defeat AI-detection or hide AI involvement (ADR-006). If asked, decline and offer language editing + disclosure.
**P9 — Privacy.** Unpublished manuscripts and uploads: private scope, no training use, minimal retention, excluded from logs, deletion honoured; choose provider settings accordingly and record in `docs/subprocessors.md`.
**P10 — Coverage & bias.** Show a "Coverage notes" panel: sources searched, known gaps (language, region, discipline, recency), and AI limitations. Include in exports.
**P11 — Human accountability.** UI wording reminds authors they remain responsible for content and citations.
**P12 — Relative claims (ETH-015).** Mapping, positioning, and gap outputs may only say what holds *in the analyzed set*. Block copy that claims novelty, "first", or absence of prior work; run the wording scan in CI.

## Hard rules
- MUST NOT store or log manuscript text or prompts/completions with user content.
- MUST NOT implement humanizer/detector-evasion.
- MUST NOT display AI output without label.
- MUST NOT assert legal or institutional compliance; advise checking policies.

## Definition of Done
Relevant `ETH-*` MUSTs pass; templates reviewed; labelling and logging tests green; handoff written.
