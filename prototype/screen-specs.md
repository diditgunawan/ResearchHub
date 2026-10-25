# Screen specifications (prototype v0.1 → implementation)

Common to all screens: left nav (220 px) · AppShell with project switcher · every AI element labelled (ETH-001) · loading/empty/error states (ENG-015) · i18n keys, no literals (ENG-013) · WCAG 2.2 AA (ENG-014) · keyboard operable · min target 44 px · data freshness + source on external data.

## Screen 1 — Search & topic map (`Main.dc.html`)
- **Purpose:** discover works; see themes before importing. **Stories:** E1-S1, E1-S2, E8-S1.
- **Requirements:** DAT-003..006, DAT-014, DAT-016; ETH-007 (retraction badge); MAP-001..006; LIB-005.
- **API:** `GET /works/search` (returns `source_status`), `POST /projects/{id}/library/items`, `POST /projects/{id}/maps`, `GET /projects/{id}/maps/{runId}`, `GET .../export`.
- **Components:** SearchBar, FilterChips, SourceStatusChips (ok/timeout/error), WorkCard (title, authors, venue, year, badges, provenance line, actions), RetractedBadge + NoticeLink, MissingAbstractChip, TopicMapPanel (bubbles sized by count, list alternative, add-cluster, export), LanguageChip.
- **States to add:** searching (skeleton cards), zero results (suggest refining), all sources failed (retry), rate-limited (DAT-004 message), map too large (>500, MAP-002), map running (progress), retracted-add confirmation dialog.
- **Rules:** partial results always labelled; missing fields shown as "not available"; cluster labels from metadata; same inputs+seed → same map.

## Screen 2 — Screening (`Screening.dc.html`)
- **Purpose:** blind dual screening with auditability. **Stories:** E3-S2..S5.
- **Requirements:** SCR-001..018; ETH-001 (suggestion labelled); ENG-014.
- **API:** `GET .../screening/queue?stage=`, `POST .../screening/decisions`, `GET .../screening/conflicts`, `POST .../screening/resolutions`, `GET .../screening/agreement`, `GET .../prisma`, `POST .../screening/suggestions`.
- **Components:** StageTabs, ProgressBar, ProtocolChip, BlindChip, ScreeningCard (title, meta, abstract with criteria highlights + legend), DecisionButtons (Include/Maybe/Exclude) + ReasonSelect (required on exclude), KeyboardHelp, AiSuggestionPanel (locked until decision when blind), CriteriaPanel, PrismaMiniTable, AgreementStat.
- **States to add:** queue empty, conflict list, protocol-changed banner, undo toast (creates superseding row), offline/retry, viewer role read-only.
- **Rules:** blind enforcement is server-side (SCR-006); AI never auto-applies (SCR-015); PRISMA numbers computed, never typed.

## Screen 3 — Grounded synthesis (`Synthesis.dc.html`)
- **Purpose:** claim-level cited answers with verification. **Stories:** E4-S1..S3, E5-S1.
- **Requirements:** SYN-001..020; ETH-001..003, ETH-012; QAS-018.
- **API:** `POST .../synthesis`, `GET .../synthesis/{runId}`, `GET .../synthesis/{runId}/events` (SSE), `POST .../extractions`.
- **Components:** ScopeChip, TabBar (Answer / Extraction table / Retrieved), QuestionCard, AiLabel (model, date), VerificationSummaryChips, ClaimList (claim text + CitationButtons + VerificationChip), EvidenceDrawer (chunk excerpt, verifier note, open work, remove claim), CoverageNotes, ReviewedButton, CopyWithCitations.
- **States to add:** queued/running with SSE stages (retrieving → extracting → drafting → verifying), refusal state listing what was searched (SYN-005), retrieval-only fallback (SYN-016), quota exhausted (SYN-015), low-confidence run (>30% claims dropped).
- **Contract gaps:** reviewed-flag endpoint and remove-claim action are missing (see PROJECT_STATE known issues 1–2).
- **Rules:** no claim without citation + verification status; excerpts short, sourced; retracted works flagged.

## Screen 4 — Lineage & audit (`Lineage.dc.html`)
- **Purpose:** show how approaches evolved with evidence. **Stories:** E8-S2, E8-S3, E8-S7.
- **Requirements:** MAP-007..014, MAP-019; QAS-025.
- **API:** `POST .../lineage`, `GET .../lineage/{runId}`, `GET .../lineage/{runId}/audit` (also CSV), `PUT/DELETE .../nodes/{workId}/override`.
- **Components:** RunHeader (scope size, run id, seed, reproducible), ViewTabs (Botanical tree / Lineage map / Audit table), LineageGraph (nodes: root/placed/needs-review; edges), NodeDetailCard (confidence + four evidence scores + chronology), AuditTable (sortable/filterable, CSV), OverrideDialog (history, reset).
- **States to add:** building run, failed run, Unplaced bucket, override history, table-only accessible view for the graph, botanical tree view (own visual language; not yet designed).
- **Rules:** nothing rendered without evidence (MAP-012); Low confidence → no auto-parent (MAP-009); parent year ≤ child year (MAP-008).

## Screen 5 — Position & gaps (`Position.dc.html`)
- **Purpose:** position a manuscript; surface in-set gaps. **Stories:** E8-S4, E8-S5.
- **Requirements:** MAP-015..018; ETH-015; MAP-016 privacy.
- **API:** `POST .../positioning`, `GET .../positioning/{id}`, `GET .../lineage/{runId}/gaps`.
- **Components:** RelativeClaimBanner (persistent), ManuscriptInput (+ upload, text-not-retained chip, opt-in retain), PositionResultCard (closest family, fit chip, runner-up), ParentTable (component scores), ConceptChips (shared vs distinctive), GapPanel (4 tabs; row = signal, frequency, source link, excerpt ≤ 300 chars, extractor version).
- **States to add:** computing, no lineage run yet (prompt to build), manuscript too short, retain-text consent dialog, gap tabs 2–4 content.
- **Rules:** wording "closest in the analyzed set"; never "novel/first"; copy scan in CI.

## Not yet prototyped (from `blueprints/07-ux-flows.md`)
Work detail & citation graph (2) · Library with collections (3) · Import report (4) · Dedup queue (5) · Protocol editor (6) · Conflicts & agreement (8) · PRISMA diagram (9) · Reference check & AI-use disclosure (11) · Journals match & checklist (12) · Settings/export/delete/members (13) · PDF upload dialog with Extract-only (18) · Botanical tree view · Auth/login · Empty states. Prototype these before or alongside the milestone that implements them.

## Information architecture delta
Nav in prototype: Search · Library · Screening · Synthesis · Map & lineage · Position & gaps · Journals · Check. (Blueprint 07 IA listed Search · Library · Screening · Synthesis · Check · Journals · Settings; mapping items were added; Settings moves to the account menu.)
