# ADR-009: Single-owner access mode with all multi-user flows retained
- Status: accepted · Date: 2026-10-25 · Deciders: product owner
## Context
Audit found anyone-can-login, replayable links, and immortal sessions. Product owner wants one account acting as administrator and user now, with no flows removed, and a later switch to many users.
## Options
### A. Delete multi-user code, hard-wire one user
Complexity low now, high later (rewrite). Cost: rework. Scalability: poor. **Rejected:** violates "do not remove flows".
### B. Keep flows; closed registration; one account holds `system_admin` + normal user (chosen)
Complexity medium. Cost: tests in two modes. Scalability: flip a setting. Security: smaller attack surface now.
### C. Put an external identity provider in front only
Complexity low, but hides app-level authorization gaps and ties to a vendor. **Rejected as sole control;** allowed as extra gate.
## Decision
Option B. Settings `ACCESS_MODE`, `registration`; system-admin flag separate from project roles; passkey + single-use link + recovery codes; server-side sessions; step-up for admin actions. Details in blueprint 17.
## Consequences
Easier: safe public exposure now; later multi-user launch. Harder: two-mode test matrix, admin console must exist from day one. Revisit: add organisation/workspace layer at Tier L.
## Action items
1. [ ] ENG-021..026 · 2. [ ] migrations in 03b · 3. [ ] QAS-026 truth audit in CI
