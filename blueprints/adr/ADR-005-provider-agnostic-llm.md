# ADR-005: Provider-agnostic LLM and embedding adapters
- Status: accepted
## Decision
All model calls go through `LLMClient` and `Embedder` interfaces with per-task model config, retries, budgets, and token/cost accounting. No provider SDK imported outside `app/llm/`.
## Consequences
+ Swap models, run evals across providers. − Lowest-common-denominator features unless extended behind the interface.
