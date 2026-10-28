# ADR-012: Interoperate with the evidence-synthesis ecosystem; do not rebuild meta-analysis or risk-of-bias in v1
- Status: accepted · Date: 2026-10-27
## Context
The awesome-evidence-synthesis index lists 140 open-source tools, including 52 for meta-analysis and statistics and 7 for risk of bias. Rebuilding them would dilute the verified-evidence-workspace wedge and add statistical risk.
## Options
### A. Rebuild meta-analysis and risk-of-bias natively
High effort, high statistical-correctness risk, competes with mature tools.
### B. Export analysis-ready data and record instruments; benchmark against reference tools (chosen)
Moderate effort; keeps focus on search, screening, audit, verification, mapping.
### C. Embed an R/Python statistics service
Possible later; adds deployment and licence complexity.
## Decision
Option B. Provide CSV exports compatible with common meta-analysis tools (ENG-031), record the risk-of-bias instrument per protocol, and benchmark screening, dedup, extraction, and reporting against open reference tools at pinned versions (QAS-034). Revisit when pilot users ask for native analysis.
## Consequences
Easier: scope, correctness, partnerships. Harder: users switch tools for statistics. Revisit: v2 appraisal module.
## Action items
1. [ ] ENG-031 export · 2. [ ] benchmark baselines · 3. [ ] register licences
