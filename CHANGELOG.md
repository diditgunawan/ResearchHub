# Changelog
## v0.7 — 2026-10-27
- B2 screening runner upgraded (active-learning simulation, multi-review, seeds, Markdown/JSON); tests 8 to 11; docs/BENCHMARK_RUNBOOK.md; templates/ADR_BENCHMARK_BASELINE.md; benchmark requirements file. No real results yet (dataset hosts unreachable from the build sandbox).
## v0.6 — 2026-10-27
- Added blueprint 20 (ecosystem references, supporting tools, protocols), blueprint 21 (benchmarking plan), ADR-012, benchmark harness (metrics, runner, 8 tests), register rows, glossary terms, roadmap items, Phase 0b and benchmark agent prompts.
- 9 new requirements (198 total). Awesome list attribution: CC BY 4.0.
## v0.5 — 2026-10-26 (upgrade verification)
- Reviewed ResearchHub upgrade (HEAD 257b7e3) against its handoff notes; findings in PROJECT_STATE and the review document.
- truth_audit.py extended from 8 to 14 probes (P9 header backdoor, P10 anonymous admin, P11 relevance floor, P12 bare-credential passkey login, P13 shipped records, P14 simulated workers). Upgraded repo: 8 pass / 6 fail.
- New requirements: ENG-028..030, QAS-031/032, ETH-017, SYN-023 (total 189 requirements).
## v0.4 — 2026-10-25 (mastermind plan v2)
- Audit of the ResearchHub implementation turned into 17 new requirements (DAT-020, ETH-016, SYN-021/022, JRN-013, ENG-021..027, QAS-026..030) and rules G14/G15.
- New blueprints: 16 scale architecture (Tier M), 17 access model (single-owner mode, all flows kept), 18 roadmap v2, 03b schema delta; ADR-009/010/011.
- New gate: scripts/truth_audit.py (8 behavioural probes) + hash-pinned coverage script. Baseline on ResearchHub: 0 pass / 8 fail.
## v0.3 — 2026-10-24
- Added UI/UX prototype v0.1 (5 screens), design tokens, screen specs, standalone HTML.
- Added handoff docs: PROJECT_STATE, DEVELOPMENT_GUIDE, AGENT_PROMPTS, subprocessors stub, runbooks index, MANIFEST.
- Fixed OpenAPI contract defects (unquoted commas split fields; 24 missing path parameters); now passes openapi-spec-validator. Validator script also checks OpenAPI/SQL when tools are installed.
## v0.2
- Added bundle 9 `literature-mapping-positioning` (MAP-001..019) from Open Knowledge Maps and PaperTree ideas; DAT-019, LIB-017, ETH-015, QAS-025; ADR-007/008; blueprint 15; schema/API/UX/test additions; roadmap M3b.
## v0.1
- 8 skill bundles, AGENTS.md router, blueprints 00–14, templates, scaffold, scripts.
