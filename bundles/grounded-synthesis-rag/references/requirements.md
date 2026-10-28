# SYN requirements
| ID | Level | Requirement |
|----|-------|-------------|
| SYN-001 | MUST | Retrieval queries for private scopes always include `project_id` filtering; cross-project retrieval is impossible by construction and covered by a 2-tenant test. |
| SYN-002 | MUST | Chunking is section-aware, 300–500 tokens with ~15% overlap; chunk text, ordinal, section, and `embedding_model` stored. |
| SYN-003 | MUST | Indexing jobs are idempotent and resumable; model change triggers versioned re-embedding without downtime. |
| SYN-004 | MUST | Retrieval is hybrid (FTS + vector) with reciprocal rank fusion and a reranker; ranks and scores are stored per run. |
| SYN-005 | MUST | A sufficiency gate refuses when distinct works < N (default 3) or top rerank score < threshold; refusal lists what was searched. |
| SYN-006 | MUST | Per-study extraction returns the defined fields with supporting chunk ids; absent info is `null`, never inferred. |
| SYN-007 | MUST | Users can edit extractions; edits set `edited_by_user` and are tracked. |
| SYN-008 | MUST | Synthesis output is validated JSON of atomic claims; each claim has ≥ 1 citation id from the retrieved set; invalid output gets one repair attempt then fails closed. |
| SYN-009 | MUST | Every claim is independently verified against only its cited chunks; verdict stored and displayed. |
| SYN-010 | MUST | Claims with `unsupported` verdict are removed from the answer or clearly flagged; `partially_supported` are flagged. |
| SYN-011 | MUST | Citation integrity gate: every cited chunk → work exists; retracted works are flagged; DOIs shown when known. |
| SYN-012 | MUST | Retrieved text is delimited and treated as untrusted; synthesis/verifier/extraction models have no tool access. |
| SYN-013 | MUST | Prompt-injection tests (malicious abstracts) pass: injected instructions do not alter output format, leak prompts, or add uncited claims. |
| SYN-014 | MUST | LLM/embedding calls go through provider-agnostic adapters with timeouts, retries, token/cost accounting. |
| SYN-015 | MUST | Per-user weekly quota and global monthly budget enforced before work starts; clear message on exhaustion. |
| SYN-016 | MUST | On LLM failure, return retrieval-only results (ranked works/chunks) with an explanatory notice. |
| SYN-017 | MUST | Runs persist question, retrieval config, chunk ids/ranks, model names, prompt hashes, tokens, cost, claims, verdicts; prompts/completions text not logged. |
| SYN-018 | MUST | A golden eval set (≥ 100 items incl. unanswerable and adversarial) runs nightly and pre-release; thresholds from `05 §5`. |
| SYN-019 | SHOULD | Streaming progress via SSE (retrieving, extracting, drafting, verifying). |
| SYN-020 | MUST | Any aggregate "agreement" display lists all underlying studies, N, designs, and a method disclaimer; otherwise not shown. |
| SYN-021 | MUST | A relevance floor is applied before the sufficiency gate: works or chunks with zero or sub-threshold relevance are never retrieved, even when the library is small; an irrelevant-query test must produce a refusal. |
| SYN-022 | MUST | The verifier is independent of the generator: it reads cited chunk text from the database and judges the claim text; a claim built by copying the cited sentence is labelled `extractive` and not counted as verified; a circularity test proves unsupported claims can fail. |
| SYN-023 | MUST | The relevance threshold is calibrated on the golden set; a single shared generic term never satisfies it; a verdict must come from a check independent of the generating call (a model's self-reported verdict, or a hard-coded default of 'supported', is not verification). |
