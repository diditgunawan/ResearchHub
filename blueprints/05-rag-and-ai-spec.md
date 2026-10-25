# 05 — RAG & AI Specification

## 1. Principles
Grounded or silent · claim-level citations · verify before display · human review · provider-agnostic · cost-capped.

## 2. Pipeline
1. **Scope** — corpus = project library (+ optional fresh search). Public works and the user's private files are separate scopes; private chunks are retrievable only inside their project.
2. **Index** — chunk abstracts and open-access full text (~300–500 tokens, 15% overlap, section-aware). Store `embedding_model`; re-embed on model change via job.
3. **Query understanding** — rewrite question; decompose into ≤4 sub-questions; extract constraints (population, years).
4. **Retrieve** — hybrid: Postgres FTS (BM25-like) top 50 + vector top 50 → reciprocal rank fusion → rerank (cross-encoder or LLM reranker) → top K (default 12–20).
5. **Sufficiency check** — if < N distinct works (default 3) or top rerank score below threshold → **refuse** with what was searched.
6. **Extract** — per work, structured JSON (population, design, intervention/exposure, outcome, key finding, effect size if stated, limitations) each field with supporting chunk ids; null if absent.
7. **Synthesize** — draft answer composed of atomic **claims**; each claim must list ≥1 chunk id from the retrieved set. Output JSON → rendered markdown.
8. **Verify** — for every claim, an independent verification call (NLI-style prompt) judges `supported | partially_supported | unsupported` against cited chunk text only. Unsupported claims are removed or flagged; run stores verdicts.
9. **Citation integrity** — all cited chunk→work links must exist in DB; DOI present when available; retracted works flagged.
10. **Persist** — store run, retrieved chunks with ranks, model, prompt hashes, tokens, cost.

## 3. Prompt contracts (templates in bundle reference)
- System prompts forbid outside knowledge for scholarly claims; allow only retrieved evidence.
- Retrieved text is delimited and labelled **untrusted data**; instructions inside it are ignored (prompt-injection defense).
- Output schema enforced via JSON mode/tool-call + Pydantic validation; invalid → one repair attempt → fail closed.

## 4. "Agreement meter" (optional, v1.1)
If implemented: per-question tally of studies whose extracted finding direction is yes/no/mixed, shown with N, study designs, and an explicit statement that it is a summary of retrieved studies — not a verdict on truth. Never presented without the list of underlying studies.

## 5. Quality targets (golden set ≥ 100 Q/A items, per discipline sample)
| Metric | Target |
|---|---|
| Citation precision (cited chunk supports claim, human-labelled) | ≥ 95% |
| Faithfulness (verifier agrees with human) | ≥ 90% agreement |
| Fabricated citation / non-existent id shown | 0 |
| Refusal correctness on unanswerable set | ≥ 90% |
| Recall@20 on labelled relevant works | ≥ 80% |
| p95 latency full run | ≤ 60 s |
Evals run in CI nightly and before release (QAS-018).

## 6. Models & cost
LLM and embedding providers behind `LLMClient` / `Embedder` interfaces; config chooses model per task (cheap model for rewrite/extract, stronger for synthesis/verify). Per-user weekly credit quota; hard stop with clear message; per-feature cost dashboards.

## 7. Safety
No user-content training; provider settings must disable retention where available; redact emails/PII from prompts only when not needed for the task; log token counts, never text.

## 8. LLM use in mapping (v0.2)
Core mapping (clusters, families, lineage, positioning, gap signals) is **non-generative**: embeddings + statistics + rules, so results are reproducible and auditable. LLM use is optional and limited to (a) short cluster labels constrained to the cluster's own keywords and (b) rewording evidence summaries. Both are labelled AI-generated, logged (ETH-001/002), post-checked (labels may contain only terms from the keyword set), and never create placements. No related-work prose is generated (MAP-018).
