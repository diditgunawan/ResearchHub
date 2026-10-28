# SCR requirements
| ID | Level | Requirement |
|----|-------|-------------|
| SCR-001 | MUST | Each review project has a versioned protocol; screening is disabled until protocol v1 exists. |
| SCR-002 | MUST | Protocol edits create a new version; every decision stores `protocol_version`. |
| SCR-003 | MUST | Stages `title_abstract` and `full_text` are supported; items advance per `state-machine.md`. |
| SCR-004 | MUST | `screening_decisions` and `screening_resolutions` are append-only (DB grants enforce); corrections use `supersedes_id`. |
| SCR-005 | MUST | Exclude decisions require a reason from the controlled list; project may add reasons; global defaults seeded. |
| SCR-006 | MUST | Blind mode hides other reviewers' decisions and AI suggestions at the API level until the caller has decided on that item/stage. |
| SCR-007 | MUST | Roles enforced server-side: owner (all), reviewer (decide), viewer (read). |
| SCR-008 | MUST | A verdict mismatch among required reviewers creates a conflict; unresolved conflicts block stage completion. |
| SCR-009 | MUST | Conflicts are closed only by a resolution row from an authorized resolver; reviewers' original decisions remain. |
| SCR-010 | MUST | Raw agreement and Cohen's kappa are computed per stage from the log; kappa is undefined (shown as "n/a") when expected agreement = 1 or n < 2 reviewers. |
| SCR-011 | MUST | PRISMA 2020 flow counts are computed from import batches + decision log; no manual overrides. |
| SCR-012 | MUST | PRISMA endpoint verifies reconciliation (identified − duplicates = screened; screened − excluded = assessed; assessed − excluded = included) and returns discrepancies when violated. |
| SCR-013 | MUST | Full-text exclusion counts are broken down by reason in the PRISMA output. |
| SCR-014 | MUST | AI suggestions include rationale mapped to protocol criteria, model name, prompt hash; stored separately from decisions. |
| SCR-015 | MUST | AI suggestions are never applied automatically and never count as a reviewer; UI labels them "suggestion". |
| SCR-016 | SHOULD | Record whether each human decision matched the displayed AI suggestion (for transparency, never to coerce). |
| SCR-017 | MUST | Screening UI supports keyboard shortcuts, resume, undo-last (via superseding row), and meets WCAG 2.2 AA. |
| SCR-018 | MUST | Decision log export (CSV) includes item id, DOI, stage, reviewer, verdict, reason, timestamp, protocol version. |

## Cohen's kappa
For two reviewers over N items with categorical verdicts: po = observed agreement; pe = Σ_k (p1k · p2k); κ = (po − pe) / (1 − pe). Compute only on items both reviewed in that stage. 'maybe' is its own category unless configured otherwise.
| SCR-019 | SHOULD | Prioritised screening ranks unscreened records with an open, logged model; it shows stopping diagnostics (for example consecutive irrelevant records, estimated recall) as advice only; it never auto-excludes; each ranking batch stores model name, version, seed, and training-set size; blind mode is unaffected. |
| SCR-020 | SHOULD | Protocol export with registry-style fields (question, framework, eligibility, databases, dates, planned methods, risk-of-bias instrument) usable for PROSPERO or OSF registration; versioned, with a deviations log. |
| SCR-021 | SHOULD | PRISMA outputs include a CSV compatible with the official PRISMA 2020 flow-diagram generator input and a 27-item checklist skeleton with locations; every figure equals the computed flow (SCR-011). |
