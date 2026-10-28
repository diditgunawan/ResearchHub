#!/usr/bin/env python3
"""Regenerate MANIFEST.md from the file tree. Fails if a file has no description rule,
so the inventory never drifts. Usage: python scripts/build_manifest.py [--check]"""
import pathlib, sys, fnmatch
ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {"dist", "__pycache__", ".git", "node_modules"}
RULES = [  # (glob, area, description) — first match wins
 ("AGENTS.md","Entry","Master router + global rules G1–G13; copy to repo root"),
 ("README.md","Entry","Package overview and quick start"),
 ("CHANGELOG.md","Entry","Version history of this package"),
 ("docs/PROJECT_STATE.md","Handoff","Living state: done, next, assumptions, open questions, known issues"),
 ("docs/DEVELOPMENT_GUIDE.md","Handoff","How continuing agents work: read order, loop, M0 tasks, coordination"),
 ("docs/AGENT_PROMPTS.md","Handoff","Paste-ready prompts per milestone and for reviewer/contract/design agents"),
 ("docs/BENCHMARK_RUNBOOK.md","Handoff","Exact steps to produce the first real SYNERGY baseline and record it"),
 ("docs/subprocessors.md","Handoff","Stub: sub-processor register (fill before launch)"),
 ("docs/runbooks/README.md","Handoff","Index/stubs for six required runbooks"),
 ("blueprints/00-*","Blueprint","Vision, scope, personas, metrics, risks"),
 ("blueprints/01-*","Blueprint","PRD: epics, stories, NFRs, release criteria"),
 ("blueprints/02-*","Blueprint","Architecture, modules, flows, tech choices, mapping module"),
 ("blueprints/03-*","Blueprint","PostgreSQL schema (parses; not yet run on live DB)"),
 ("blueprints/03b-*","Blueprint","Schema delta v0.4: access model, truthful AI accounting, scale, journal integrity, RLS template"),
 ("blueprints/16-*","Blueprint","Scale architecture (Tier M): capacity, topology, servers, network, security, backend/frontend design"),
 ("blueprints/17-*","Blueprint","Access model: single-owner mode with all multi-user flows kept"),
 ("blueprints/18-*","Blueprint","Roadmap v2: phases, gates, KPIs, risks, agent lanes"),
 ("blueprints/20-*","Blueprint","Evidence-synthesis ecosystem: tool map, supporting protocols, gaps (adapted from CC BY 4.0 index)"),
 ("blueprints/21-*","Blueprint","Benchmarking plan: datasets, suites, metrics, baselines, thresholds policy"),
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
 ("blueprints/scaffold/docker-compose.yml","Scaffold","Dev services: Postgres+pgvector, Redis, MinIO, Mailpit, api/worker/web"),
 ("blueprints/scaffold/.env.example","Scaffold","Environment variable template (no secrets)"),
 ("blueprints/scaffold/Makefile","Scaffold","dev/test/lint/type/migrate/evals/audit targets"),
 ("templates/*","Template","Reusable template (ADR, state, handoff, PR checklist)"),
 ("scripts/validate_bundles.py","Script","Lint package: frontmatter, IDs, cross-refs, OpenAPI, SQL"),
 ("scripts/check_requirement_coverage.py","Script","QAS-004: MUST IDs must have tests"),
 ("scripts/truth_audit.py","Script","QAS-026: behavioural probes (auth, provenance, gate, hard-coded data, boot guard)"),
 ("scripts/integrity.sha256","Script","Pinned hash of the strict coverage gate script"),
 ("scripts/benchmark/*","Script","Benchmark harness: metrics, screening runner, hand-verified tests"),
 ("scripts/build_manifest.py","Script","Regenerates this manifest"),
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
out = ["# MANIFEST — ResearchForge handoff package v0.7", "", f"{len(files)} files. Generated by `scripts/build_manifest.py`; do not edit by hand.", ""]
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
