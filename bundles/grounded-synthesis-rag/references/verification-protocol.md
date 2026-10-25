# Verification protocol
1. Collect claims with citation chunk ids.
2. For each claim, fetch cited chunk texts from DB (not from model output).
3. Call verifier (cheaper model OK; batch ≤ 10 claims; temperature 0).
4. Apply policy: supported → keep; partially_supported → keep with ⚠ badge and show the supporting excerpt; unsupported → drop (default) and log; if > 30% of claims dropped → mark run "low confidence" and show retrieval list instead of a narrative.
5. Spot-check sample (5%) in nightly evals with human labels; track verifier–human agreement; alert if < 90%.
6. Store verdicts; UI shows badges and hover evidence.
