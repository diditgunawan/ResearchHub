# Benchmark runbook: first baseline numbers (suite B2, SYNERGY)

Goal: produce the first real, reproducible numbers for screening prioritisation so thresholds can be set from evidence (blueprint 21, QAS-033). The sandbox that built this package cannot reach the dataset hosts, so **run this on your own machine**. No benchmark results exist yet.

## 1. Set up (Windows PowerShell; same commands on macOS and Linux)
```powershell
python -m venv .venv-bench
.\.venv-bench\Scripts\Activate.ps1
pip install -r scripts\benchmark\requirements.txt
python -m pytest scripts\benchmark -q        # expect: 11 passed
```

## 2. Get three reviews from SYNERGY
`synergy-dataset` is the maintainers' package. Its commands are `list`, `show`, `get`, `attribute`. It downloads label files from DataverseNL and builds records through the OpenAlex API, so it needs internet, and OpenAlex may require an API key (check the package and OpenAlex docs).
```powershell
synergy list                      # shows dataset names, sizes, inclusion counts: pick a small, a medium, and a large review
synergy get -d NAME1 NAME2 NAME3 -o data\synergy
```
The command prints a legal note and asks you to accept it; read it. Each output file is `<name>.csv` with `title`, `abstract`, `label_included` (the format the runner reads). Do not commit `data\`. Record the package version (`pip show synergy-dataset`) and the dataset version.

## 3. Run the baselines (3 seeds each)
```powershell
python scripts\benchmark\run_screening_benchmark.py --dir data\synergy --ranker random --seeds 3 --out results\b2_random.json
python scripts\benchmark\run_screening_benchmark.py --dir data\synergy --ranker active --seeds 3 --out results\b2_active.json
```
Each run prints a Markdown table and writes JSON plus `.md` next to it. `random` is the floor. `active` is a simple TF-IDF plus logistic regression simulation with 1 relevant and 1 irrelevant prior record, retraining every 10 records (change with `--batch`). It is a **reference baseline, not ASReview**.
Optional keyword baseline: give each review's title as the query with `--queries queries.json` (a JSON map from file stem to query string).

## 4. Run the reference tool (QAS-034)
Install ASReview LAB in a **separate** environment and use its own simulation feature on the same CSVs, with the same priors and seeds where it allows. Follow the current ASReview documentation for flags; they are not reproduced here because they change between versions. Verify its licence first (ADR-008). Report its WSS@95, WSS@100, and recall next to ours.

## 5. Plug in the app's own ranker
Write `rank(records, query, seed) -> list[int]` that returns every record index exactly once, best first, then run `--ranker yourpkg.module:rank`. The runner rejects rankers that skip or repeat records.

## 6. How to read results
| Metric | Meaning | Good direction |
|---|---|---|
| WSS@95 | Share of screening saved versus random order when 95% of included records are found | Higher; negative means worse than random |
| WSS@100 | Same at 100% recall | Higher |
| recall@10/20/30% | Share of included records found after screening that fraction | Higher |
| ATD | Average position of included records as a fraction of the list | Lower |
Look at the **per-review** table, not only the median: a few reviews usually dominate the average. Reviews with very few included records give noisy numbers.

## 7. Record the result (then set thresholds)
Copy `templates/ADR_BENCHMARK_BASELINE.md` into `blueprints/adr/`, fill in the medians and per-review table, the dataset and package versions, seeds, git sha, and machine. Only after that set release thresholds relative to the best baseline (for example, the app's median WSS@95 not more than 10 percentage points below ASReview on the same reviews). Never tune on the reviews you report.

## 8. Caveats
SYNERGY reviews are mostly biomedical; results may not carry over to other fields. The `active` baseline is deliberately simple. Priors count as screened, which is conservative. Confirm SYNERGY's licence in blueprint 11 before sharing derived data.
