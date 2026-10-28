# 12 — Architecture Decision Records
| ADR | Title | Status |
|---|---|---|
| 001 | Build on open scholarly data; no scraping/copying of competitors | accepted |
| 002 | Postgres + pgvector as single store | accepted |
| 003 | Append-only screening decisions; PRISMA computed from log | accepted |
| 004 | Claim-level citations with verification pass | accepted |
| 005 | Provider-agnostic LLM/embedding adapters | accepted |
| 006 | No humanizer / AI-detector evasion features | accepted |
| 007 | Evidence-first mapping; gap ≠ novelty; structure not prose | accepted |
| 008 | Open-source reuse policy (licence-gated) | accepted |
| 009 | Single-owner access mode, all multi-user flows retained | accepted |
| 010 | Middle-scale topology: managed containers, managed Postgres, edge network | accepted |
| 011 | Hybrid source strategy (mirror + API + cache); embed-on-add | accepted |
| 012 | Interoperate with the evidence-synthesis ecosystem; no native meta-analysis or risk-of-bias in v1 | accepted |

New ADRs: copy `templates/ADR.md` into `blueprints/adr/`.
