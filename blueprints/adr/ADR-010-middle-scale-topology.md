# ADR-010: Middle-scale topology — managed containers, managed Postgres, edge network
- Status: accepted · Date: 2026-10-25
## Context
Target: ≤ 5,000 registered, ≈ 120 concurrent peak, 50 req/s design peak, small team, free-tier-friendly early.
## Options
### A. Single VM with Docker Compose
Complexity low; cost lowest; scalability limited; single point of failure; fine for Tier S.
### B. Managed containers + managed Postgres/Redis/object store + Cloudflare edge (chosen)
Complexity medium; cost moderate; autoscaling workers; HA database; least ops per capability.
### C. Kubernetes
Complexity high; cost and ops high; unnecessary at this size.
## Decision
Option B for Tier M, reusing the same images as Tier S Compose. Region near largest user group; one region only.
## Consequences
Easier: HA, backups, scaling workers. Harder: network and secret setup; vendor-specific bits (keep behind env and Terraform modules). Revisit: p95 SLO misses, DB CPU > 60%, need for multi-region.
## Action items
1. [ ] Terraform/Pulumi modules · 2. [ ] staging mirror · 3. [ ] load test (QAS-028)
