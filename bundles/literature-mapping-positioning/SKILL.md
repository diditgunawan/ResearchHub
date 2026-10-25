---
name: literature-mapping-positioning
description: Protocol for evidence-based literature mapping — topic maps that cluster search results into themes, research families, method-lineage trees (parent–child evolution of approaches), an audit table with confidence per placement, "position my manuscript" comparison against the literature, and research-gap signals within the analyzed set. Use this skill whenever a task involves topic maps, clustering papers, bubble/tree/lineage visualizations, related-work structure, positioning a paper among prior work, research gaps, "how did this method evolve", or visual overviews of a field, even if the user just says "map my literature" or "show me the landscape".
---

# Literature Mapping & Positioning Protocol (MAP)

Goal: give researchers a defensible *structure* for their literature — themes, lineage, position, and gaps — where every placement is backed by stored evidence. The module structures; it never writes the related-work section for the user.

Idea references (ideas only, no code/UI/asset copying): Open Knowledge Maps (metadata-only topic maps), PaperTree (families, lineage, positioning, audit table). See `blueprints/15-reference-analysis.md`.

## Preconditions
Read `AGENTS.md`, `references/requirements.md`, `references/algorithms.md`, `references/views-and-audit.md`. Always load `research-integrity-ai-ethics`, `fullstack-engineering-standards`, `qa-security-deployment`. Load `scholarly-data-ingestion` when new metadata/abstract/reference fields are needed and `library-reference-management` for PDF uploads.

## Protocol
**P1 — Scope and cap.** A map run takes an explicit scope (a search result set or a library subset), capped (default 500 records). Record scope, parameters, seed, embedding model and versions in `map_runs`. Same inputs ⇒ same output.
**P2 — Prepare features.** Multilingual embeddings of title+abstract; concept terms (keyphrases) from metadata/text; completeness flags (missing abstract/DOI/year/references/keywords) with reason codes. Never impute missing data.
**P3 — Topic map (discovery view).** Cluster the scope into themes; label clusters from metadata keywords (deterministic c-TF-IDF). Optional LLM label is constrained to the cluster's keyword set, labelled AI, and logged (ETH). Sized by member count; click-through to lists; "add cluster to library".
**P4 — Families and lineage (structure view).** Build families by the documented algorithm; assign parent–child links using four evidence types: citation, semantic, keyword/concept, chronology. Apply the chronology hard rule. Store component scores per edge; map to confidence bands; Low ⇒ "Needs review", no auto-parent.
**P5 — Evidence on every placement.** No node, edge, or cluster is rendered without a stored evidence record reachable from its audit row.
**P6 — Audit table.** One row per paper: branch, parent, evidence types, confidence, status, missing-metadata flags; sort/filter/search; CSV export.
**P7 — Overrides.** Users may change parent/branch; log who/when/previous; keep machine evidence untouched; provide reset.
**P8 — Position my manuscript.** Compare a user manuscript (title+abstract, or text/PDF) to families and works; return closest family, top-3 likely parents with component scores, shared vs distinctive concepts. Copy says "closest in the analyzed set". Manuscript text is private, not retained by default.
**P9 — Gap signals.** Typed signals (unresolved condition, future-work, lineage gap, data-quality gap), each with source work, ≤ 300-char excerpt from open-access or user-owned text, extractor version. Banner: a gap in this set is not a claim of global novelty.
**P10 — Views.** Three views over one analysis (botanical tree, lineage map, table) without recomputation; accessible list alternative; SVG/PNG/CSV exports. Use our own visual language.
**P11 — Privacy.** PDF uploads for mapping support *extract-only* mode: validate → extract → delete original → keep only derived data (see LIB-017).
**P12 — Reuse policy.** If tempted to reuse open-source code (e.g., from Open Knowledge Maps' repositories), follow ADR-008: verify the licence, record it in the register, attribute, and write an ADR. Otherwise reimplement from the ideas.

## Hard rules
- MUST NOT claim novelty, "first", or "gap in the field" — only "in the analyzed set".
- MUST NOT place a node without stored evidence, or auto-parent below the confidence threshold.
- MUST NOT generate related-work prose for the user (G6/ETH-008).
- MUST NOT copy PaperTree/OKMaps branding, artwork, copy, or code (outside ADR-008).
- MUST NOT log manuscript text or store it unless the user opts in.

## Definition of Done
Relevant `MAP-*` MUSTs pass; determinism test green; golden mapping fixtures meet thresholds (QAS-025); audit/evidence links verified in e2e; handoff written.

## Handoffs
← `library-reference-management` (items, uploads) · ← `scholarly-data-ingestion` (metadata, references) · ↔ `research-integrity-ai-ethics` (wording, logging) · → `grounded-synthesis-rag` (a family/cluster can be the scope of a synthesis).
