# Hand-computed checks. Run: python -m pytest scripts/benchmark -q
import csv, json, subprocess, sys, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import metrics as M, run_screening_benchmark as R

def test_QAS_033_wss_hand_computed():
    labels = [1,0,1,0,0,0,0,0,0,1]               # N=10, 3 relevant
    assert M.screened_for_recall(labels, .6) == 3  # 2/3 >= 0.6 after 3
    assert M.wss(labels, .6) == pytest.approx(0.3) # (10-3)/10 - 0.4
    assert M.wss(labels, .95) == pytest.approx(-0.05)  # needs all 10: 0 - 0.05

def test_QAS_033_perfect_ranking_wss95():
    labels = [1,1,1] + [0]*7
    assert M.wss(labels, .95) == pytest.approx(0.65)   # (10-3)/10 - 0.05

def test_QAS_033_recall_at_and_atd():
    labels = [1,0,1,0,0,0,0,0,0,1]
    assert M.recall_at(labels, .3) == pytest.approx(2/3)
    assert M.atd(labels) == pytest.approx((1+3+10)/3/10)

def test_QAS_033_pair_prf():
    p, r, f = M.pair_prf([("a","b"),("c","d")], [("b","a"),("e","f")])
    assert (p, r, f) == pytest.approx((0.5, 0.5, 0.5))

def test_QAS_033_kappa_and_undefined_case():
    a = [1,1,1,1,1,0,0,0,0,0]; b = [1,1,1,1,0,1,0,0,0,0]
    assert M.cohens_kappa(a, b) == pytest.approx(0.6)
    assert M.cohens_kappa([1,1,1], [1,1,1]) is None      # pe = 1 -> undefined (SCR-010)

def test_QAS_033_prisma_reconciliation():
    assert M.prisma_reconciles(412, 61, 351, 237, 114, 80, 34) == []
    assert "identified - duplicates != screened" in M.prisma_reconciles(412, 60, 351, 237, 114, 80, 34)

def test_QAS_033_empty_and_no_relevant_rejected():
    with pytest.raises(ValueError): M.wss([], .95)
    with pytest.raises(ValueError): M.wss([0,0,0], .95)

def test_QAS_033_harness_runs_end_to_end(tmp_path):
    p = tmp_path / "fixture.csv"        # TEST FIXTURE ONLY: tiny synthetic table to exercise the harness
    rows = [("heat mortality older adults", "cardiac deaths", 1), ("pottery glaze", "kiln clay", 0),
            ("heat and cardiac risk", "older adults", 1), ("medieval ceramics", "region clay", 0), ("lattice gauge", "quantum", 0)]
    with open(p, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["title","abstract","label_included"]); w.writerows(rows)
    res = R.evaluate(R.load(p), R.rank_keyword, query="heat cardiac older", seed=0)
    assert res["relevant"] == 2 and res["recall@30%"] > 0 and res["wss95"] > 0
    out = subprocess.run([sys.executable, str(pathlib.Path(R.__file__)), "--dataset", str(p), "--ranker", "random", "--seeds", "2", "--out", str(tmp_path / "o.json")], capture_output=True, text=True)
    assert out.returncode == 0 and "B2 screening" in out.stdout
    assert json.load(open(tmp_path / "o.json"))["suite"] == "B2-screening" and (tmp_path / "o.md").exists()


def _fixture(n_pos=12, n_neg=88, seed=3):
    """TEST FIXTURE ONLY: synthetic records whose relevant class uses a distinct vocabulary."""
    import random
    rng = random.Random(seed)
    pos_words = "heat cardiac mortality older admissions hospital exposure".split()
    neg_words = "pottery glaze kiln ceramics lattice quantum gauge medieval clay region".split()
    common = "study analysis results method sample".split()
    def rec(words, label):
        return {"title": " ".join(rng.sample(words, 3) + rng.sample(common, 1)), "abstract": " ".join(rng.choices(words + common, k=14)), "label": label}
    recs = [rec(pos_words, 1) for _ in range(n_pos)] + [rec(neg_words, 0) for _ in range(n_neg)]
    rng.shuffle(recs); return recs

def test_QAS_033_active_ranker_returns_each_record_once_and_is_deterministic():
    pytest.importorskip("sklearn")
    recs = _fixture()
    a = R.rank_active(recs, "", seed=0, batch=5); b = R.rank_active(recs, "", seed=0, batch=5)
    assert sorted(a) == list(range(len(recs))) and a == b

def test_QAS_033_active_beats_random_on_separable_fixture():
    pytest.importorskip("sklearn")
    recs = _fixture()
    act = R.evaluate(recs, lambda r, q, s: R.rank_active(r, q, s, batch=5), seed=0)
    rnd = [R.evaluate(recs, R.rank_random, seed=s)["wss95"] for s in range(10)]
    assert act["wss95"] > max(rnd) and act["recall@20%"] >= 0.9

def test_QAS_033_summarise_and_markdown():
    per = [{"wss95": .5, "wss100": .4, "recall@10%": .6, "recall@20%": .8, "recall@30%": .9, "atd": .3, "n": 10, "relevant": 2},
           {"wss95": .7, "wss100": .6, "recall@10%": .8, "recall@20%": .9, "recall@30%": 1.0, "atd": .2, "n": 20, "relevant": 4}]
    s = R.summarise(per)
    assert s["wss95"]["median"] == pytest.approx(0.6) and s["wss95"]["max"] == 0.7
    md = R.markdown({"ranker": "x", "seeds": 1, "reviews": {"a": per[0]}, "summary": s})
    assert "| wss95 |" in md and "| a | 10 | 2 |" in md
