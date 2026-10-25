# Algorithms (v1 defaults — change only via ADR + re-run golden fixtures)

## 1. Features
- `emb(w)`: multilingual embedding of title + abstract (fallback title only; flag `no_abstract`).
- `concepts(w)`: top-15 keyphrases (author keywords if present, else RAKE/YAKE-style or c-TF-IDF over the scope). Normalize case/lemma.
- Completeness flags: `no_abstract`, `no_doi`, `no_year`, `no_refs`, `no_keywords`.

## 2. Topic map (discovery)
1. k-NN graph on `emb`; cluster with HDBSCAN (min_cluster_size = max(3, 1% of N)) or agglomerative with k chosen by silhouette in [4, 12]; fixed `seed`.
2. Noise points → "Other" bubble (kept visible, never hidden).
3. Label: top 3 c-TF-IDF terms per cluster (metadata only). Optional LLM label = short phrase composed only from those terms; reject outputs containing other nouns (post-check).
4. Output: clusters {id, label, keywords[], size, members[w, membership_score]}.

## 3. Families (structure)
1. Combined graph: edges = kNN semantic (cosine ≥ 0.55) ∪ in-set citation edges (weight 1.0) ∪ bibliographic coupling (Jaccard of reference lists ≥ 0.1, scaled).
2. Community detection (Leiden or Louvain, fixed seed). Min family size 3 else "Unplaced".
3. Family label = top c-TF-IDF terms within family.

## 4. Parent–child lineage
For each child `c` in a family, candidates `p` in the same family (or cross-family only with direct citation) with `year(p) ≤ year(c)`; same year only with `Cit = 1`.
Evidence components in [0,1]:
- `Cit`: 1.0 if `c` directly cites `p` (reference in scope); else coupling-based 0–0.6.
- `Sem`: cosine(emb(c), emb(p)) min-max scaled over candidates.
- `Kw`: Jaccard(concepts(c), concepts(p)).
- `Chr`: 1.0 if 0 < Δyear ≤ 3; linear decay to 0.3 at Δyear = 12; 0.6 if Δyear = 0.
`score = 0.35·Cit + 0.35·Sem + 0.20·Kw + 0.10·Chr`.
Bands: **High** score ≥ 0.75 and (Cit ≥ 0.6 or at least two of Sem/Kw/Chr ≥ 0.7); **Medium** 0.55–0.75; **Low** < 0.55.
Parent = argmax score if band ≥ Medium **and** (Cit > 0 or band = High). Else status `needs_review`, parent null.
Roots: earliest node(s) of a family, or nodes with no eligible candidate ≥ Low and highest in-set cited-by count; mark `root`.
Missing-metadata nodes → status `needs_review` with reason codes; never imputed.
Store `evidence = {cit, sem, kw, chr, shared_concepts[], citing_path?}` per edge.

## 5. Positioning
Input: manuscript title+abstract (+ optional text/PDF extract). Compute `emb(m)`, `concepts(m)`.
- Closest family = max cosine to family centroid; also report runner-up.
- Top-3 parents = highest `score` using the same components with `Chr` computed from manuscript year (current year if unknown) and `Cit` from manuscript references if supplied (else 0).
- Shared concepts = concepts(m) ∩ concepts(parent); distinctive = high-tf-idf concepts in m with prevalence < 10% among family members.
- Fit label: Strong ≥ 0.75, Moderate 0.55–0.75, Weak < 0.55 (relative to analyzed set).
- Copy: "Closest in the analyzed set: …" — never "novel", "first", or "no prior work".

## 6. Gap signals
- `future_work` / `unresolved_condition`: sentence patterns (EN + ID lists maintained in code) such as "future work", "remains challenging", "limitation", "not addressed", "unclear", "belum", "keterbatasan"; extract only from OA full text or user-owned text; cluster similar sentences across papers; report frequency and papers.
- `lineage_gap`: leaf nodes older than 3 years with no successor in set; families with weak (Low) links to newer work. Tag "may reflect how the set was collected".
- `data_quality`: completeness flags.
- Each signal: `{kind, work_id, chunk_id, excerpt ≤ 300 chars, extractor_version, confidence}`.
