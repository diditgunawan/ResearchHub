.PHONY: dev test lint type migrate evals audit
dev:      ; docker compose up --build
migrate:  ; docker compose run --rm api alembic upgrade head
test:     ; docker compose run --rm api pytest -q && (cd apps/web && npm test --silent)
lint:     ; docker compose run --rm api ruff check . && (cd apps/web && npm run lint)
type:     ; docker compose run --rm api mypy app && (cd apps/web && npm run typecheck)
evals:    ; docker compose run --rm api python -m evals.run --suite golden
audit:    ; docker compose run --rm api pip-audit && (cd apps/web && npm audit --audit-level=high)
