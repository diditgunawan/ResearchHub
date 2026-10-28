#!/usr/bin/env python3
"""Lint the ResearchForge agent protocol package.
Checks: frontmatter, line limits, requirement ID sequences/levels, reference files,
router coverage, roadmap exit-criteria ranges, blueprint presence, OpenAPI/SQL sanity.
Usage: python scripts/validate_bundles.py [--write-index]
"""
import re, sys, csv, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUNDLES = {
    "scholarly-data-ingestion": ("DAT", 21),
    "library-reference-management": ("LIB", 18),
    "screening-prisma-workflow": ("SCR", 21),
    "grounded-synthesis-rag": ("SYN", 23),
    "journal-matching-submission": ("JRN", 13),
    "research-integrity-ai-ethics": ("ETH", 17),
    "literature-mapping-positioning": ("MAP", 20),
    "fullstack-engineering-standards": ("ENG", 31),
    "qa-security-deployment": ("QAS", 34),
}
errors, warnings = [], []
err = errors.append
warn = warnings.append
all_reqs = []  # (id, level, bundle, text)

def read(p): return p.read_text(encoding="utf-8")

for name, (prefix, expected) in BUNDLES.items():
    d = ROOT / "bundles" / name
    skill = d / "SKILL.md"
    if not skill.exists():
        err(f"{name}: missing SKILL.md"); continue
    txt = read(skill)
    m = re.match(r"^---\nname: (.+)\ndescription: (.+)\n---\n", txt, re.S)
    if not m: err(f"{name}: bad frontmatter"); continue
    if m.group(1).strip() != name: err(f"{name}: frontmatter name mismatch ({m.group(1).strip()})")
    desc = m.group(2).strip()
    if len(desc) > 1024: err(f"{name}: description {len(desc)} chars > 1024")
    if len(desc) < 150: warn(f"{name}: description is short; make it 'pushy' with triggers")
    if len(txt.splitlines()) > 500: err(f"{name}: SKILL.md > 500 lines")
    for sec in ("## Protocol", "## Hard rules", "## Definition of Done"):
        if sec not in txt: err(f"{name}: missing section '{sec}'")
    for ref in re.findall(r"`references/([\w\-.]+)`", txt):
        if not (d / "references" / ref).exists(): err(f"{name}: SKILL.md references missing file references/{ref}")
    req = d / "references" / "requirements.md"
    if not req.exists(): err(f"{name}: missing references/requirements.md"); continue
    rows = re.findall(rf"^\| ({prefix}-(\d{{3}})) \| (MUST|SHOULD|MAY) \| (.+) \|$", read(req), re.M)
    nums = [int(r[1]) for r in rows]
    if nums != list(range(1, expected + 1)):
        err(f"{name}: requirement IDs should be {prefix}-001..{prefix}-{expected:03d} sequential; got {len(nums)} ({nums[:3]}...{nums[-3:]})")
    for rid, _, lvl, text in rows:
        all_reqs.append((rid, lvl, name, text.strip()))

ids = {r[0] for r in all_reqs}
if len(ids) != len(all_reqs): err("duplicate requirement IDs")

# Router coverage
agents = read(ROOT / "AGENTS.md")
for name, (prefix, _) in BUNDLES.items():
    if f"`{name}`" not in agents: err(f"AGENTS.md routing table missing bundle {name}")

# Roadmap exit ranges
road = read(ROOT / "blueprints" / "10-roadmap-backlog.md")
for pfx, a, b in re.findall(r"\b([A-Z]{3})-(\d{3})\.\.(\d{3})\b", road):
    for n in range(int(a), int(b) + 1):
        if f"{pfx}-{n:03d}" not in ids: err(f"roadmap references missing requirement {pfx}-{n:03d}")

# Blueprints present
need = ["00-vision-scope.md","01-prd.md","02-architecture.md","03-data-model.sql","04-openapi.yaml",
        "05-rag-and-ai-spec.md","06-security-privacy.md","07-ux-flows.md","08-test-strategy.md",
        "09-deployment-ops.md","10-roadmap-backlog.md","11-source-terms-register.md","12-adr-index.md","13-glossary.md",
        "15-reference-analysis.md","16-scale-architecture.md","17-access-model.md","18-roadmap-v2.md","20-evidence-synthesis-ecosystem.md","21-benchmarking-plan.md","03b-data-model-v2.sql","adr/ADR-007-evidence-first-mapping.md","adr/ADR-008-open-source-reuse-policy.md","adr/ADR-009-single-owner-access-mode.md","adr/ADR-010-middle-scale-topology.md","adr/ADR-011-source-mirror-and-embed-on-add.md","adr/ADR-012-interoperate-not-rebuild.md"]
for f in need:
    if not (ROOT / "blueprints" / f).exists(): err(f"blueprints/{f} missing")
for f in ["docker-compose.yml", ".env.example", "Makefile"]:
    if not (ROOT / "blueprints" / "scaffold" / f).exists(): err(f"scaffold/{f} missing")
for f in ["docs/PROJECT_STATE.md","docs/DEVELOPMENT_GUIDE.md","docs/AGENT_PROMPTS.md","prototype/README.md","prototype/screen-specs.md","prototype/design-tokens.json"]:
    if not (ROOT / f).exists(): err(f"{f} missing")
for f in ["ADR.md","PROJECT_STATE.md","HANDOFF.md","PR_CHECKLIST.md"]:
    if not (ROOT / "templates" / f).exists(): err(f"templates/{f} missing")

# Requirement IDs mentioned anywhere must exist
for p in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.yaml")):
    for rid in set(re.findall(r"\b(?:DAT|LIB|SCR|SYN|JRN|ETH|ENG|QAS|MAP)-\d{3}\b", read(p))):
        if rid not in ids: err(f"{p.relative_to(ROOT)} cites unknown requirement {rid}")

# OpenAPI + SQL sanity
try:
    import yaml
    spec = yaml.safe_load(read(ROOT / "blueprints" / "04-openapi.yaml"))
    if not spec.get("paths"): err("OpenAPI has no paths")
    try:
        from openapi_spec_validator import validate as _oas_validate
        _oas_validate(spec)
    except ImportError:
        warn("openapi-spec-validator not installed; skipped strict OpenAPI validation (pip install openapi-spec-validator)")
    except Exception as e:
        err(f"OpenAPI invalid: {str(e)[:200]}")
except ImportError:
    warn("PyYAML not installed; skipped OpenAPI parse")
except Exception as e:
    err(f"OpenAPI parse error: {e}")
sql = read(ROOT / "blueprints" / "03-data-model.sql")
try:
    import pglast
    pglast.parse_sql(sql)
    pglast.parse_sql(read(ROOT / "blueprints" / "03b-data-model-v2.sql"))
except ImportError:
    warn("pglast not installed; skipped SQL syntax parse (pip install pglast)")
except Exception as e:
    err(f"SQL syntax error: {str(e)[:200]}")
for t in ["works","screening_decisions","chunks","synthesis_runs","journals","ai_usage_log","map_runs","lineage_nodes","lineage_edges","positioning_runs","gap_signals"]:
    if f"CREATE TABLE {t}" not in sql: err(f"SQL missing table {t}")

if "--write-index" in sys.argv:
    out = ROOT / "blueprints" / "14-traceability-matrix.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id","level","bundle","requirement","test_name_hint","status"])
        for rid, lvl, b, t in all_reqs:
            w.writerow([rid, lvl, b, t, f"test_{rid.replace('-','_')}_*", "todo"])
    print(f"wrote {out.relative_to(ROOT)} ({len(all_reqs)} requirements)")

for w_ in warnings: print("WARN:", w_)
for e in errors: print("ERROR:", e)
musts = sum(1 for r in all_reqs if r[1] == "MUST")
print(f"\nBundles: {len(BUNDLES)} | Requirements: {len(all_reqs)} (MUST {musts}) | Errors: {len(errors)} | Warnings: {len(warnings)}")
sys.exit(1 if errors else 0)
