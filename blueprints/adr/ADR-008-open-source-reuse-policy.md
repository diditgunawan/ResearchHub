# ADR-008: Open-source reuse policy (licence-gated)
- Status: accepted
## Context
G4 forbids copying third-party code. Some references (e.g., Open Knowledge Maps) publish open-source software, which may be reused under its licence.
## Decision
Reuse open-source code only if (1) the licence is verified per repository and recorded in the register, (2) it is compatible with our distribution/hosting model (note copyleft/network clauses), (3) attribution and notices are preserved, (4) an ADR records the component and licence. Closed products (no licence granting reuse) remain ideas-only. Branding, artwork, and copy are never reused unless the licence explicitly permits.
## Consequences
+ Legal clarity and optional speed-up. − Licence review overhead; may prefer reimplementation.
