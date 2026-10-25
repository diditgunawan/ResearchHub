# Runbooks (QAS-023) — create each as its own file before launch
| Runbook | Trigger | Minimum contents |
|---|---|---|
| connector-outage.md | Source error rate high / circuit open | Identify source, confirm via smoke test, communicate partial results, disable connector flag, recovery check |
| llm-outage.md | Provider errors/latency | Switch to retrieval-only mode (SYN-016), failover model if configured, user messaging |
| queue-backlog.md | Queue depth alert | Scale workers, inspect stuck jobs, idempotent replay |
| cost-spike.md | LLM cost > 80% budget | Identify feature/user, apply quotas, pause expensive jobs |
| data-deletion-request.md | User/legal request | Verify identity, run deletion job, verify purge incl. backups timeline, confirm to user |
| security-incident.md | Suspected breach | Contain, rotate secrets, assess scope, notify per law, post-mortem |
