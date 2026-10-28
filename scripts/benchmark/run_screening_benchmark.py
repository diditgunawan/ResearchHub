#!/usr/bin/env python3
"""Screening-prioritisation benchmark, suite B2 (blueprint 21, QAS-033).

Input: labelled CSV(s) with columns title, abstract, label_included (the format written by `synergy get`).
Rankers return the ORDER in which a reviewer would screen the records:
  random   : shuffled order (floor baseline)
  keyword  : records matching the query terms first (needs --query or a queries JSON)
  active   : simulated active learning (TF-IDF + logistic regression, retrained every --batch records),
             the standard simulation protocol: start from 1 relevant + 1 irrelevant prior record, always screen the
             top-ranked unscreened record, reveal its true label, retrain. Needs scikit-learn.
  pkg.mod:fn : your own ranker `rank(records, query, seed) -> list[int]` (the app's ranker plugs in here)
Priors count as screened and are placed first (conservative). Metrics: WSS@95, WSS@100, recall at 10/20/30% screened, ATD.

Examples:
  python scripts/benchmark/run_screening_benchmark.py --dir data/synergy --ranker active --seeds 3 --out results/b2_active.json
  python scripts/benchmark/run_screening_benchmark.py --dataset one.csv --ranker keyword --query "heat mortality"
Datasets are downloaded on demand and NEVER committed. Thresholds are set in an ADR after baselines run."""
import argparse, csv, datetime, importlib, json, pathlib, random, re, statistics, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import metrics as M

def rank_random(records, query, seed):
    idx = list(range(len(records))); random.Random(seed).shuffle(idx); return idx

def rank_keyword(records, query, seed):
    q = set(re.findall(r"[a-z]{3,}", query.lower()))
    def score(r): return len(q & set(re.findall(r"[a-z]{3,}", (r["title"] + " " + r["abstract"]).lower())))
    return sorted(range(len(records)), key=lambda i: (-score(records[i]), i))

def rank_active(records, query, seed, batch=10):
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
    except ImportError as e:
        raise SystemExit("ranker 'active' needs scikit-learn: pip install scikit-learn numpy") from e
    n = len(records); y = [r["label"] for r in records]
    pos = [i for i in range(n) if y[i] == 1]; neg = [i for i in range(n) if y[i] == 0]
    if not pos or not neg: raise ValueError("need at least one relevant and one irrelevant record")
    rng = random.Random(seed)
    X = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=1).fit_transform(
        [(r["title"] + " " + r["abstract"]).strip() or "empty" for r in records])
    order = [rng.choice(pos), rng.choice(neg)]; seen = set(order)
    while len(order) < n:
        train = sorted(seen)
        clf = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed)
        clf.fit(X[train], [y[i] for i in train])
        rest = [i for i in range(n) if i not in seen]
        scores = clf.decision_function(X[rest])
        ranked = [rest[j] for j in sorted(range(len(rest)), key=lambda j: (-scores[j], rest[j]))]
        take = ranked[:batch]
        order.extend(take); seen.update(take)
    return order

BUILTIN = {"random": rank_random, "keyword": rank_keyword, "active": rank_active}

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [{"title": r.get("title") or "", "abstract": r.get("abstract") or "", "label": int(r["label_included"])} for r in rows]

def evaluate(records, ranker, query="", seed=0):
    order = ranker(records, query, seed)
    assert sorted(order) == list(range(len(records))), "ranker must return every record exactly once"
    labels = [records[i]["label"] for i in order]
    return {"n": len(labels), "relevant": sum(labels), "wss95": M.wss(labels, .95), "wss100": M.wss(labels, 1.0),
            "recall@10%": M.recall_at(labels, .10), "recall@20%": M.recall_at(labels, .20),
            "recall@30%": M.recall_at(labels, .30), "atd": M.atd(labels)}

KEYS = ["wss95", "wss100", "recall@10%", "recall@20%", "recall@30%", "atd"]

def summarise(per_review):
    out = {}
    for k in KEYS:
        v = [r[k] for r in per_review]
        out[k] = {"median": statistics.median(v), "mean": statistics.mean(v), "min": min(v), "max": max(v)}
    return out

def markdown(res):
    lines = [f"### B2 screening: ranker `{res['ranker']}`, {len(res['reviews'])} review(s), seeds {res['seeds']}", "",
             "| metric | median | mean | min | max |", "|---|---|---|---|---|"]
    for k, s in res["summary"].items():
        lines.append(f"| {k} | {s['median']:.3f} | {s['mean']:.3f} | {s['min']:.3f} | {s['max']:.3f} |")
    lines += ["", "| review | records | included | WSS@95 (mean over seeds) | recall@20% |", "|---|---|---|---|---|"]
    for name, r in res["reviews"].items():
        lines.append(f"| {name} | {r['n']} | {r['relevant']} | {r['wss95']:.3f} | {r['recall@20%']:.3f} |")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True); g.add_argument("--dataset"); g.add_argument("--dir")
    ap.add_argument("--ranker", default="random"); ap.add_argument("--query", default="")
    ap.add_argument("--queries", help="JSON mapping dataset file stem to a query string (for the keyword ranker)")
    ap.add_argument("--seeds", type=int, default=1); ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--out"); a = ap.parse_args()
    if a.ranker in BUILTIN:
        ranker = BUILTIN[a.ranker]
        if a.ranker == "active": ranker = lambda r, q, s: rank_active(r, q, s, batch=a.batch)
    else:
        mod, fn = a.ranker.split(":"); ranker = getattr(importlib.import_module(mod), fn)
    files = [pathlib.Path(a.dataset)] if a.dataset else sorted(pathlib.Path(a.dir).glob("*.csv"))
    if not files: raise SystemExit("no CSV files found")
    queries = json.load(open(a.queries)) if a.queries else {}
    reviews = {}
    for f in files:
        recs = load(f); runs = [evaluate(recs, ranker, queries.get(f.stem, a.query), s) for s in range(a.seeds)]
        reviews[f.stem] = {k: (runs[0][k] if k in ("n", "relevant") else statistics.mean(x[k] for x in runs)) for k in runs[0]}
    try: sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception: sha = ""
    res = {"suite": "B2-screening", "ranker": a.ranker, "seeds": a.seeds, "batch": a.batch if a.ranker == "active" else None,
           "git_sha": sha, "date": datetime.date.today().isoformat(), "reviews": reviews,
           "summary": summarise(list(reviews.values()))}
    if a.out:
        pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump(res, open(a.out, "w"), indent=1); open(pathlib.Path(a.out).with_suffix(".md"), "w").write(markdown(res))
    print(markdown(res))

if __name__ == "__main__": main()
