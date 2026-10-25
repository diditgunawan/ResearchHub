#!/usr/bin/env python3
"""Regenerate MANIFEST.md from the file tree. Fails if a file has no description rule,
so the inventory never drifts. Usage: python scripts/build_manifest.py [--check]"""
import pathlib, sys, fnmatch
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {"dist", "__pycache__", ".git", "node_modules", ".venv", ".pytest_cache", "build"}
RULES = [  # (glob, area, description) — first match wins
 (".env.example","Scaffold","Root environment configuration template"),
 ("docker-compose.yml","Scaffold","Multi-container orchestration for backend and frontend services"),
 ("Makefile","Scaffold","Development and testing automation targets"),
 (".agents/*","Governance","Vibe coding governance, PRD, architecture, and ledger state"),
 ("AGENTS.md","Entry","Master router + global rules G1–G13; copy to repo root"),
 ("README.md","Entry","Package overview and quick start"),
 ("CHANGELOG.md","Entry","Version history of this package"),
 ("docs/PROJECT_STATE.md","Handoff","Living state: done, next, assumptions, open questions, known issues"),
 ("docs/DEVELOPMENT_GUIDE.md","Handoff","How continuing agents work: read order, loop, M0 tasks, coordination"),
 ("docs/AGENT_PROMPTS.md","Handoff","Paste-ready prompts per milestone and for reviewer/contract/design agents"),
 ("docs/subprocessors.md","Handoff","Sub-processor register for data processing agreements"),
 ("docs/PRIVACY.md","Handoff","Privacy notice and data protection policy (GDPR & UU PDP)"),
 ("docs/ETHICS.md","Handoff","Academic integrity, AI ethics, and disclosure policy"),
 ("docs/runbooks/*","Handoff","Index and operational runbooks for platform workflows"),
 ("blueprints/00-*","Blueprint","Vision, scope, personas, metrics, risks"),
 ("blueprints/01-*","Blueprint","PRD: epics, stories, NFRs, release criteria"),
 ("blueprints/02-*","Blueprint","Architecture, modules, flows, tech choices, mapping module"),
 ("blueprints/03-*","Blueprint","PostgreSQL schema (parses; not yet run on live DB)"),
 ("blueprints/04-*","Blueprint","OpenAPI 3.1 contract (validated; many responses still stubs)"),
 ("blueprints/05-*","Blueprint","RAG/AI spec, quality targets, LLM use in mapping"),
 ("blueprints/06-*","Blueprint","Security, privacy, threat model, upload controls"),
 ("blueprints/07-*","Blueprint","UX flows and 18 screens"),
 ("blueprints/08-*","Blueprint","Test strategy and mapping tests"),
 ("blueprints/09-*","Blueprint","Deployment, CI/CD, observability, backups"),
 ("blueprints/10-*","Blueprint","Roadmap M0–M5 (+M3b), backlog rules"),
 ("blueprints/11-*","Blueprint","Source and terms register (0/18 verified)"),
 ("blueprints/12-*","Blueprint","ADR index"),
 ("blueprints/13-*","Blueprint","Glossary"),
 ("blueprints/14-*","Blueprint","Traceability matrix of all requirements (generated)"),
 ("blueprints/15-*","Blueprint","Reference analysis: ideas taken/not taken from five products"),
 ("blueprints/adr/*","Blueprint","Architecture decision record"),
 ("blueprints/scaffold/*","Scaffold","Dev and container scaffold: docker-compose, env, Makefile"),
 ("templates/*","Template","Reusable template (ADR, state, handoff, PR checklist)"),
 ("scripts/validate_bundles.py","Script","Lint package: frontmatter, IDs, cross-refs, OpenAPI, SQL"),
 ("scripts/check_requirement_coverage.py","Script","QAS-004: MUST IDs must have tests"),
 ("scripts/build_manifest.py","Script","Regenerates this manifest"),
 ("scripts/e2e_live_simulation.py","Script","Automated live end-to-end system simulation across all core workflows"),
 ("scripts/stress_concurrency_test.py","Script","Concurrency and high-throughput stress verification suite"),
 ("scripts/test_ieee_dataset_eval.py","Script","Real IEEE dataset evaluation benchmark with non-primary tenant isolation"),
 ("apps/api/*","Application","Backend service: FastAPI, SQLAlchemy, SQLite/Postgres, RAG, and screening engine"),
 ("apps/web/*","Application","Frontend SPA: React 19, TypeScript, Vite, Tailwind Warm Editorial design system"),
 ("packages/*","Contracts","Shared packages and API contracts"),
 ("prototype/README.md","Prototype","Prototype overview and editing notes"),
 ("prototype/screen-specs.md","Prototype","Per-screen implementation brief"),
 ("prototype/design-tokens.*","Prototype","Design tokens (JSON and CSS variables)"),
 ("prototype/canvas/*","Prototype","Design-canvas source (artboards + index)"),
 ("prototype/standalone/*","Prototype","Browser-viewable HTML of the screens"),
]
BUNDLE_DESC = {"requirements.md":"Numbered requirements (MUST/SHOULD)"}
def describe(rel):
    if rel.startswith("bundles/"):
        parts = rel.split("/")
        if parts[-1] == "SKILL.md": return ("Skill", f"Protocol for `{parts[1]}` (loadable skill)")
        if "references" in parts: return ("Skill", BUNDLE_DESC.get(parts[-1], f"Reference for `{parts[1]}`: {parts[-1]}"))
    for g, area, d in RULES:
        if fnmatch.fnmatch(rel, g): return (area, d)
    return None
files = []
for p in sorted(ROOT.rglob("*")):
    if p.is_dir() or any(x in SKIP_DIRS for x in p.relative_to(ROOT).parts): continue
    rel = p.relative_to(ROOT).as_posix()
    if rel in ("MANIFEST.md",) or rel.endswith(".zip"): continue
    d = describe(rel)
    if d is None: print("ERROR: no description rule for", rel); sys.exit(1)
    files.append((rel, d[0], d[1], p.stat().st_size))
out = ["# MANIFEST — ResearchForge handoff package v0.3", "", f"{len(files)} files. Generated by `scripts/build_manifest.py`; do not edit by hand.", ""]
for area in ["Entry","Handoff","Blueprint","Skill","Scaffold","Template","Script","Prototype"]:
    rows = [f for f in files if f[1] == area]
    out += [f"## {area} ({len(rows)})", "", "| Path | Purpose | Size |", "|---|---|---|"]
    out += [f"| `{r[0]}` | {r[2]} | {r[3]/1024:.1f} KB |" for r in rows] + [""]
text = "\n".join(out)
if "--check" in sys.argv:
    cur = (ROOT / "MANIFEST.md").read_text() if (ROOT / "MANIFEST.md").exists() else ""
    sys.exit(0 if cur == text else (print("MANIFEST.md out of date") or 1))
(ROOT / "MANIFEST.md").write_text(text, encoding="utf-8")
print(f"MANIFEST.md written: {len(files)} files")
