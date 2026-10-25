# Repo layout
```
/
├─ AGENTS.md  README.md  Makefile  docker-compose.yml  .env.example
├─ apps/
│  ├─ api/            FastAPI (app/, alembic/, tests/, evals/)
│  │   app/{identity,projects,sources,works,library,screening,retrieval,synthesis,integrity,journals,jobs,quota,audit,llm}/
│  └─ web/            React+TS (src/{routes,features,components,i18n,api,lib}/, e2e/)
├─ packages/contracts/  openapi.yaml + generated clients
├─ blueprints/  templates/  bundles/  docs/ (PROJECT_STATE.md, runbooks/, subprocessors.md)
└─ .github/workflows/
```
Conventions: Python 3.12, `snake_case`; TS strict, `PascalCase` components; one feature per folder; tests next to code (`tests/`), named by requirement ID.
Definition of Ready: contract + requirement IDs + test plan. Definition of Done: gates green, docs updated.
