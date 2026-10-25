# 06 — Security & Privacy

## Data classification
| Class | Examples | Handling |
|---|---|---|
| Public | works metadata, journal data | Shared tables; cacheable |
| Confidential | user libraries, notes, decisions | Project-scoped; encrypted at rest; ACL |
| Highly confidential | unpublished manuscripts, uploaded PDFs | Private object storage, no global indexes, no logs, deletion SLA |
| Secrets | API keys, tokens | Env/secret manager only |

## Threat model (STRIDE-lite)
| Threat | Example | Control |
|---|---|---|
| Spoofing | Stolen magic-link | Single-use, 15 min TTL, bound to device hint; rate limit |
| Tampering | Edit screening log | Append-only table, no UPDATE/DELETE grants, audit events |
| Repudiation | Reviewer denies decision | Immutable decisions with user id + timestamp |
| Info disclosure | Cross-project leak via RAG | `project_id` filter in every retrieval query; tests with 2 tenants (QAS-009) |
| DoS | Expensive synthesis spam | Quotas, per-IP + per-user rate limits, job concurrency caps |
| Elevation | Viewer posts decisions | Server-side role checks; tests per role |
| Prompt injection | Malicious abstract text | Untrusted delimiters, no tool access from synthesis, output schema, verifier pass |
| SSRF | Import via URL | No server-side fetch of user URLs; allow-listed connectors only |
| Supply chain | Malicious dependency | Lockfiles, pinned versions, audit in CI, ≥14-day-old releases preferred |

## Controls checklist (maps to QAS bundle)
HTTPS + HSTS · secure, httpOnly, sameSite cookies · CSRF protection · CSP · input validation (Pydantic) · output encoding · file upload checks (type, size, AV scan, no execution) · rate limiting · secrets scanning · dependency/SAST/container scanning · least-privilege DB roles · backups encrypted + restore-tested · security headers · audit logging · LLM Top-10 review.

## Privacy
- Lawful basis & consent captured; privacy policy and terms published before launch.
- Regional laws to review with counsel before launch: Indonesia UU PDP, Taiwan PDPA, EU GDPR (if EU users). Not legal advice — obtain review.
- Data minimization; retention: logs 30 d, deleted projects purge 30 d, backups 35 d.
- Export (JSON + original formats) and delete flows (E7-S2).
- Sub-processor list (LLM, hosting, email) kept in `docs/subprocessors.md`.

## Mapping & uploads (v0.2)
| Threat / concern | Control |
|---|---|
| Malicious PDF upload | Type sniffing, size ≤ limits, AV scan, parse in sandboxed worker, no external fetch; fail closed |
| Manuscript leakage via positioning | Private scope, `retain_text=false` default, results store vectors/derived data only, never log text, delete on request |
| Extract-only mode failure | Original deleted after successful extraction; deletion verified and audited; failed extraction keeps file only until retry window (≤ 24 h) then purges |
| Excerpt copyright exposure in gap view | Excerpts ≤ 300 chars, only from open-access or user-owned text, always linked to source |
| Over-claiming from analysis | Persistent banner and wording rules (MAP-015/017, ETH-015) |
