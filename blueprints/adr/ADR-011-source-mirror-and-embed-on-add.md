# ADR-011: Hybrid source strategy (local mirror + live API + cache) and embed-on-add vectors
- Status: accepted · Date: 2026-10-25
## Context
Since 13 Feb 2026 OpenAlex requires API keys and meters usage; a free key gives about a dollar of daily usage. Tier M estimates ≈ 4,800 searches/day. Embedding every work is too costly and large.
## Options
### A. Live API only
Simple; costs and rate limits grow with users; outage risk. 
### B. Local mirror of a selected snapshot + live API for fresh and long tail + cache (chosen)
Moderate effort; predictable cost; fast local search; snapshot is free to download.
### C. Full mirror
Too large for Tier M storage and index budgets.
## Decision
B, with scope set in `source_mirror_state` (years, types, optionally disciplines). Embed only works that enter a library or synthesis scope. Source terms re-verified per DAT-001; API key sent as `api_key` query parameter (DAT-020).
## Consequences
Easier: speed, cost control. Harder: ingestion job, freshness policy, licence record. Revisit: users demand global semantic search or mirror exceeds 10M rows.
