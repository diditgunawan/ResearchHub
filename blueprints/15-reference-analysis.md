# 15 — Reference Analysis (idea sources)

These products are **idea references**. We reimplement *functions* on open data with our own design. We do not copy code, UI, copy, branding, or data (ADR-001), except open-source code reused strictly under its licence (ADR-008).

Evidence base: pages for Consensus, JurnalHub, Open Knowledge Maps, and PaperTree were read on 2026-10-24. **Rayyan's site blocked automated access, so its row relies on general knowledge, not a fresh read.** Re-check all claims before relying on them.

| Reference | Core idea | What we adopt (as our own implementation) | What we deliberately do not adopt | Posture |
|---|---|---|---|---|
| **Rayyan** (systematic-review screening) | Collaborative screening with blind mode, conflict handling | Bundle `screening-prisma-workflow` (SCR) | Proprietary UI, any code or data | Ideas only; not fetched |
| **Consensus** (AI academic search) | Question → evidence synthesis over peer-reviewed papers | Bundle `grounded-synthesis-rag` (SYN) with claim-level citations + verification | Their index, ranking, "meter" visuals, branding | Ideas only |
| **JurnalHub** (Indonesian research portal, 14 tools) | Journal match with Scopus/Sinta filters, SLR/PRISMA, AI peer review, citation map, AI-use disclosure | Bundle `journal-matching-submission` (JRN); AI-use disclosure helper (ETH); i18n EN/ID | "Humanizer" (detector evasion, ADR-006); copy, pricing, credit system | Ideas only |
| **Open Knowledge Maps** (non-profit topic maps) | Clusters search results into a visual overview of themes; claims results rest only on underlying metadata; ~400M outputs, 400+ languages, via BASE; open-source software; embeddable components | Topic map (MAP-001..006): metadata-only labels, multilingual clustering, click-through, determinism; optional BASE connector (DAT-019) after terms check; "grounded or silent" principle matches ours | Their data pipeline and branding; reusing code only per ADR-008 | Open source (verify licence); content CC BY 4.0 per their site |
| **PaperTree** (Indonesian related-work mapper) | Turns a paper collection into families, lineage with evidence (citation/semantic/keyword/chronology), "position my paper", research-gap view, audit table with confidence, privacy-by-workflow (PDFs deleted after extraction), explicitly does **not** write related work | Bundle `literature-mapping-positioning` (MAP-007..019); extract-only PDF mode (LIB-017); gap ≠ novelty wording (ETH-015); evidence-first audit table | Their visuals/art, naming, copy, code; session limits (we use accounts and projects) | Ideas only (no open-source claim seen) |

## Gaps these references revealed in our v0.1 blueprints
1. No discovery/overview step before screening → added topic map (E8-S1).
2. No structure-of-literature output (families, lineage) → added (E8-S2..S3).
3. No "where does my paper fit" feature → added with strict wording rules (E8-S4).
4. No privacy mode for uploaded PDFs beyond retention SLAs → added extract-only mode (LIB-017).
5. No guard against over-claiming "gaps" → added MAP-017, ETH-015.
6. Open-source reuse policy was silent (G4 forbade copying competitors) → ADR-008.

## Build-vs-link decision for topic maps
Option A: build our own (MAP-001..006) so maps integrate with our library and screening. Option B: link out to Open Knowledge Maps for ad-hoc exploration and import resulting records. Default: A for integration, with B documented in the UI help as an alternative. Revisit if maintenance cost exceeds value.

## Update v0.6: evidence-synthesis ecosystem
Added a sixth reference class: the open-source evidence-synthesis tool index (140 tools, CC BY 4.0). It confirms the market splits into many single-purpose open tools (search, screening, extraction, bias, meta-analysis) with no single audited workspace, which supports our integrated-and-verified positioning, and it shows where users already expect interoperability (Rayyan exports, PRISMA generator, ASReview datasets). Gaps found in our spec: search log and snowballing, prioritised screening, protocol and PRISMA exports, risk-of-bias handling, benchmarks. See blueprints 20 and 21 and ADR-012.

