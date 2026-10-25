# ADR-003: Append-only screening decisions; PRISMA computed from log
- Status: accepted
## Decision
`screening_decisions` and `screening_resolutions` are insert-only (no UPDATE/DELETE grants). Changes are new rows with `supersedes_id`. PRISMA counts and kappa are derived by query, never stored manually.
## Consequences
+ Auditability, reproducibility. − Slightly heavier queries (mitigate with views/materialized views).
