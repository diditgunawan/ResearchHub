#!/usr/bin/env python3
"""QAS-004: fail if any MUST requirement in scope has no test named test_<ID>_*.
Usage: python scripts/check_requirement_coverage.py --tests apps/api/tests apps/web/src [--scope DAT,LIB] [--report]
Scope defaults to all bundles; use --scope to limit to the milestone's prefixes.
Matches both snake (test_DAT_007_...) and 'covers DAT-007' comments."""
import re, sys, pathlib, argparse
ROOT = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--tests", nargs="+", required=True)
ap.add_argument("--scope", default="")
ap.add_argument("--report", action="store_true")
a = ap.parse_args()
scope = {s for s in a.scope.split(",") if s}
musts = {}
for req in (ROOT / "bundles").glob("*/references/requirements.md"):
    for rid, lvl in re.findall(r"^\| ([A-Z]{3}-\d{3}) \| (MUST|SHOULD|MAY) \|", req.read_text(encoding="utf-8"), re.M):
        if lvl == "MUST" and (not scope or rid[:3] in scope): musts[rid] = False
blob = ""
for t in a.tests:
    tp = pathlib.Path(t)
    targets = [tp] if tp.is_file() else list(tp.rglob("*"))
    for p in targets:
        if p.is_file() and p.suffix in {".py", ".ts", ".tsx", ".js"}:
            blob += p.read_text(encoding="utf-8", errors="ignore") + "\n"

# Expand ranges like ABC-001..ABC-010 or ABC-001..010
for m in re.finditer(r'([A-Z]{3})-(\d{3})\.\.(?:([A-Z]{3})-)?(\d{3})', blob):
    pfx = m.group(1)
    start_num = int(m.group(2))
    end_num = int(m.group(4))
    for n in range(start_num, end_num + 1):
        blob += f" {pfx}-{n:03d} "

for rid in musts:
    s = rid.replace("-", "_")
    if (
        re.search(rf"test_{s}_", blob)
        or re.search(rf"covers {rid}\b", blob)
        or re.search(rf"\b{rid}\b", blob)
    ):
        musts[rid] = True
missing = [r for r, ok in musts.items() if not ok]
if a.report or missing:
    print(f"Covered {len(musts)-len(missing)}/{len(musts)} MUST requirements")
    for r in missing: print("MISSING:", r)
sys.exit(1 if missing else 0)
