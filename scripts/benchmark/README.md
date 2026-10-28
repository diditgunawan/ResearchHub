# Benchmark harness (QAS-033/034, blueprint 21)
`metrics.py` pure-Python metrics (WSS@R, recall@fraction, ATD, duplicate-pair PRF, Cohen's kappa, PRISMA reconciliation). `run_screening_benchmark.py` scores any ranker on a labelled CSV. `test_metrics.py` proves the formulas with hand-computed values. Datasets are downloaded on demand and never committed; record versions, seeds, git sha, and model ids with every result.

See `docs/BENCHMARK_RUNBOOK.md` for exact commands to produce the first real SYNERGY baseline. Rankers: random, keyword, active (simulated active learning, needs scikit-learn), or your own plug-in. 11 tests.
