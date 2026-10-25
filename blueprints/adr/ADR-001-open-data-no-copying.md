# ADR-001: Build on open scholarly data; no scraping or copying of competitors
- Status: accepted
## Context
The product is inspired by the functions of existing tools (screening apps, AI evidence search, journal portals). Their code, UI, copy, data, and brand are their property; some disallow automated access.
## Decision
Implement functions independently using open APIs/datasets and our own design. Record every source's terms in `11-source-terms-register.md`. Never scrape or fetch from sites that disallow it.
## Consequences
+ Legal and ethical clarity; stable data supply. − Coverage depends on open data; some proprietary metrics (e.g., certain journal rankings) need licences or are omitted.
