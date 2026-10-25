# CI pipeline (GitHub Actions or equivalent)
PR: checkout → cache → ruff/mypy → eslint/tsc → unit (py/ts) → integration (services) → contract (schemathesis) → requirement-coverage check → secret scan → SAST (semgrep/bandit) → SCA (pip-audit, npm audit) → build images → container scan (trivy).
Main: PR jobs → deploy staging → migrations → e2e (Playwright + axe) → DAST baseline (weekly/pre-release).
Nightly: AI evals (golden set), live connector smoke (non-blocking), dependency audit, k6 smoke.
Release tag: all above → manual approval → migration dry-run on staging snapshot → deploy prod → smoke tests → announce.
Artifacts: coverage, eval report, SBOM, scan reports retained 90 days.
