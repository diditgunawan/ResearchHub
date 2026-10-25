# ADR-007: Evidence-first mapping; gap ≠ novelty; structure, not prose
- Status: accepted
## Context
Mapping tools can over-claim (novelty, "gaps") and can look authoritative while being opaque. PaperTree-style audit tables and Open Knowledge Maps' metadata-only stance show a safer pattern.
## Decision
Core mapping is non-generative (embeddings + statistics + rules), deterministic, and evidence-backed per placement. Output wording is relative ("closest in the analyzed set"). The module never writes related-work text. LLMs only constrain-label clusters and reword evidence, labelled and logged.
## Consequences
+ Auditable, reproducible, honest. − Less "magic" than fully generative tools; requires fixture-based calibration.
