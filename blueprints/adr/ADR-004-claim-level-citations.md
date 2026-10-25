# ADR-004: Claim-level citations with verification pass
- Status: accepted
## Decision
Synthesis output is a list of atomic claims, each citing retrieved chunk ids. A separate verifier call checks each claim against only its cited chunks. Unsupported claims are removed/flagged. Citations may only reference ids in the retrieved set.
## Consequences
+ Near-zero fabricated citations. − ~1.5–2× LLM cost and latency; mitigated by cheaper verifier model and batching.
