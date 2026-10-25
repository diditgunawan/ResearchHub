# Ready-to-paste prompts for agents

## Universal preamble (prepend to every prompt)
"You are continuing the ResearchForge project. First read docs/PROJECT_STATE.md and AGENTS.md, then follow the routing table to load the relevant bundle SKILL.md files. Cite requirement IDs in tests and commits. Stop and report if a gate fails (G11). When done, update docs/PROJECT_STATE.md and write a handoff using templates/HANDOFF.md."

## M0 — Foundations
"Task: M0-1 and M0-2 from blueprints/10-roadmap-backlog.md. Bundles: fullstack-engineering-standards, qa-security-deployment. Scaffold the monorepo per references/repo-layout.md, get `make dev` healthy, then create the baseline Alembic migration from blueprints/03-data-model.sql, run it on a real Postgres with pgvector, fix schema issues, implement DB role grants for append-only tables, and propose the embedding-dimension decision as an ADR."

## M1 — Data & Library
"Task: M1. Bundles: scholarly-data-ingestion, library-reference-management (+ENG, QAS). Start by verifying the OpenAlex, Crossref, PubMed, and Unpaywall rows in blueprints/11-source-terms-register.md and recording date and links. Implement the SourceConnector interface, OpenAlex and Crossref connectors with recorded fixtures, federated search with source_status, import/export for RIS/BibTeX/CSV/CSL-JSON, and the dedup review queue. Exit criteria: DAT-001..018, LIB-001..016."

## M2 — Screening
"Task: M2. Bundle: screening-prisma-workflow (+ENG, QAS, ETH if AI suggestions). Implement protocol versions, dual blind screening, append-only decisions with DB grants, conflicts, kappa, PRISMA counts with reconciliation. Build UI from prototype/screen-specs.md screen 2. Exit criteria: SCR-001..018."

## M3 — Synthesis & Integrity
"Task: M3. Bundles: grounded-synthesis-rag, research-integrity-ai-ethics (+ENG, QAS). Before coding, resolve contract gaps 1–2 in PROJECT_STATE (reviewed flag, remove claim). Implement chunking, hybrid retrieval, extraction, claim-level citations, verifier pass, refusal, quotas, AI-use log, disclosure generator, reference checks. Build the golden eval set loader. Exit criteria: SYN-001..020, ETH-001..014."

## M3b — Literature Mapping
"Task: M3b. Bundles: literature-mapping-positioning, research-integrity-ai-ethics, library-reference-management (LIB-017), scholarly-data-ingestion (DAT-019). Implement topic map, families, lineage with evidence, audit table, overrides, positioning, gap signals, extract-only uploads. Use bundle references/algorithms.md; do not change weights without an ADR. Build the golden mapping fixtures (QAS-025). Exit criteria: MAP-001..019, DAT-019, LIB-017, ETH-015."

## M4 — Journals
"Task: M4. Bundle: journal-matching-submission (+ETH, ENG, QAS). First verify data rights for every journal field (JRN-001); omit anything unclear. Implement journal profiles, filters, explainable matching, checklist, freshness labels, and the labelled eval set. Exit criteria: JRN-001..012."

## M5 — Hardening & launch
"Task: M5. Bundles: qa-security-deployment, research-integrity-ai-ethics, fullstack-engineering-standards. Close all MUST gaps using blueprints/14-traceability-matrix.csv; run the release checklist; complete runbooks in docs/runbooks/ and docs/subprocessors.md; run security, a11y, load, and AI evals. Exit criteria: QAS-007..025, ENG-013..020."

## Reviewer agent
"Review the open PR against templates/PR_CHECKLIST.md and the cited requirement IDs. For each MUST ID, find the covering test and confirm it asserts the requirement. Check tenant isolation, role checks, logging of user content, AI labelling, and relative-claim wording. Report pass/fail per ID; do not approve with failures."

## Contract-sync agent
"Compare apps/api routes and apps/web API usage with blueprints/04-openapi.yaml. List drift, missing responses/schemas, and gaps in docs/PROJECT_STATE.md (Known issues). Propose OpenAPI changes as a standalone PR. Do not change implementation."

## Design-implementation agent
"Implement the design system from prototype/design-tokens.json as Tailwind/CSS variables and the component inventory in prototype/screen-specs.md. Build components with real buttons/labels, loading/empty/error states, i18n keys, and axe checks. Do not copy the prototype HTML."
