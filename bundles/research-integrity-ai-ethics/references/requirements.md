# ETH requirements
| ID | Level | Requirement |
|----|-------|-------------|
| ETH-001 | MUST | All AI-generated/modified content is visibly labelled with model, date, and verification status. |
| ETH-002 | MUST | Every AI feature call writes `ai_usage_log` (feature, stage, model, purpose, human_reviewed) without content text. |
| ETH-003 | MUST | Users can mark AI outputs as human-reviewed; the flag feeds disclosure statements. |
| ETH-004 | MUST | The disclosure generator uses the usage log and templates, is editable, and states that journal-specific AI policies must be checked. |
| ETH-005 | MUST | Reference-check job resolves DOIs/references, compares title/year/first author, and reports verified / unresolved / mismatch / retracted per item. |
| ETH-006 | MUST | Reference checks never auto-modify the user's references; changes require explicit confirmation. |
| ETH-007 | MUST | Retraction/correction status is checked via the registered data source, shown with check date in library, search, synthesis. |
| ETH-008 | MUST | Writing-assist modes are limited to outline, critique, language editing, structure checks; no fabricated data/references/peer-review text. |
| ETH-009 | MUST | No feature is built to evade AI detectors or conceal AI use; requests are declined with an alternative. |
| ETH-010 | MUST | Unpublished manuscripts/uploads are private-scoped, excluded from logs and global indexes, not used for training, deleted on request within SLA. |
| ETH-011 | MUST | Provider settings for retention/training opt-out are recorded in `docs/subprocessors.md` and checked in release checklist. |
| ETH-012 | MUST | A Coverage Notes panel lists sources searched, known gaps, and AI limitations; included in exports. |
| ETH-013 | SHOULD | UI copy reminds authors they remain accountable for all content and citations. |
| ETH-014 | MUST | Disclosure and labelling features have automated tests; copy reviewed for no compliance guarantees. |
| ETH-015 | MUST | Outputs of mapping, positioning, and gap analysis use relative wording ("in the analyzed set"), never claim novelty/first/no prior work, and automated copy scans enforce this. |