# Journal match scoring (v1)
score = 100 × (w_s · S + w_k · K + w_c · C), defaults w_s=0.6, w_k=0.25, w_c=0.15, weights sum to 1.
- **S semantic**: cosine(embedding(title+abstract), journal.profile_embedding), min-max scaled over candidate set to [0,1].
- **K keyword/topic**: Jaccard/BM25 overlap between extracted keywords/OpenAlex topics of the input and the journal's top topics.
- **C citation affinity**: share of the user's project library (or the abstract's likely references, if provided) published in the journal, saturating at 10 items.
Hard filters first. Ties broken by S. Return components, top-matching topics, 3–5 similar articles. Document any weight change in an ADR and re-run eval (JRN-012).
Display copy rules: "Fit score" (not "chance"); show "Based on {N} recent articles, data as of {date}".
