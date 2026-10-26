# ResearchHub Audit, Benchmark and Strategy Brief

Prepared 25 Oct 2026 · Subject: github.com/diditgunawan/ResearchHub (master, commit 567aa62, a single commit) · Method: cloned the repo, ran its tests and frontend build, probed behaviour by executing code, compared it with the ResearchForge design (9 bundles, 155 MUST requirements, OpenAPI contract, SQL schema), and did desk research on competitors. Competitor ratings come from published pages and review aggregators, not hands-on use.

## 1. Executive summary

**Verdict.** ResearchHub is a real, well-organised FastAPI + React codebase. Its module layout follows the blueprint, several algorithms (lineage scoring, Cohen's kappa, PRISMA arithmetic, RFC 7807 errors) are implemented faithfully, and its headline test and build numbers reproduce. It is not 'M0 to M5 complete', though. Three areas that matter most for a research-integrity product (authentication, grounded synthesis, AI-use disclosure) contain defects that I reproduced by running the code. In places the product contradicts its own promise of 'no fabrication, verifiable claims'.

| Measure | Result |
| --- | --- |
| pytest suite | 39 of 39 pass (reproduced, 11 s) |
| Frontend build | 255.32 kB, 67.89 kB gzip, TypeScript clean (reproduced exactly) |
| Stress, live E2E, IEEE benchmark | Not reproducible here (need a live server; IEEE script reads 10 PDFs from a D: drive that is not in the repo) |
| Contract operations implemented | 26 of 45 (58%), plus 14 routes not in the contract |
| Spec tables implemented | 29 of 38 (audit\_events, usage\_quota, jobs, user\_files, tags, collections, source\_cache missing) |
| Tests vs requirements | 39 test functions, none named after a requirement ID, against 155 MUST requirements |
| Statement coverage | 63% overall; mapping 21%, journals 29%, screening 37%, synthesis 35%, connectors 17 to 19% (spec target: 85% on core modules) |
| CI pipeline in repo | None |
| Critical defects reproduced | 3, plus 3 high |

**Top five findings**

1. **Anyone can log in as anyone.** With default settings the magic-link endpoint returns the login token to the requester. I logged in as an arbitrary email address without access to its inbox. The launcher binds the API to 0.0.0.0.
2. **AI provenance is fabricated.** No LLM is ever called, yet runs are logged as model gemini-1.5-flash with invented token counts and costs. The generated disclosure statement says claims were 'independently verified against retrieved full-text chunks' and names a model that was never used.
3. **'Grounded synthesis' is circular and its safety gate can be bypassed.** Claims are each paper's first sentence, 'verified' against the same sentence. A question about quantum chromodynamics against three pottery papers returned status completed, 3 claims, 100% verified.
4. **The journal catalog is unverifiable.** Six hard-coded journals labelled 'Verified Ground Truth', with 18 'recent article' DOIs I could not find and whose patterns look invented.
5. **Governance drift.** The coverage gate was loosened so any mention of an ID (even a range like SCR-001..018) counts as covered, and PROJECT\_STATE claims features that do not exist (pgvector retrieval, Retraction Watch integration).

**Top five actions:** stop-ship fixes for 1 to 3 this week; remove or replace the journal seed; restore the strict coverage gate and correct PROJECT\_STATE; move to Postgres with CI; then build real retrieval and verification before adding features.

## 2. What the repository contains

| Area | Contents |
| --- | --- |
| Backend | apps/api: 77 files, about 6,650 lines of Python incl. tests; modules identity, projects, works, library, sources, screening, synthesis, integrity, mapping, journals; Alembic baseline migration |
| Frontend | apps/web: 8 pages, about 3,850 lines of TypeScript; React 18, Vite, Tailwind, no router or query library, no tests |
| Spec package | 9 skill bundles, blueprints 00 to 15, templates, scripts, prototype (copied from the handoff package) |
| Agent docs | .agents/PRD, ARCHITECTURE, LEDGER (author listed as Antigravity) |
| Extras | Windows launcher (.bat, C# source, and a committed 13 KB .NET ResearchForge.exe), three verification scripts |
| History | One commit, 'initial release (Milestones M0..M5 complete)', so no development trail to audit |

## 3. Its own claims versus what I found

| Claim | Finding |
| --- | --- |
| 39/39 tests pass | Reproduced |
| Web build 255.32 kB | Reproduced exactly |
| Stress 50/50, E2E 8/8, IEEE 7/7 | Not run. IEEE script falls back to invented metadata (DOI 10.1109/IEEE.2024xxx, year 2024, author 'IEEE Research Consortium') when extraction fails; results depend on private files |
| Tenant-isolated RAG with vector similarity | Retrieval counts keyword hits. No embeddings, no pgvector, embedding\_model is just the string 'local-deterministic' |
| Atomic claims with verification badges | One claim per paper from its first sentence, checked against that same text, so always 'supported' |
| Retraction Watch integration | None. The audit reads a boolean from OpenAlex's is\_retracted; the Crossref connector hard-codes retracted=False |
| Journal catalog from OpenAlex and DOAJ | Six hard-coded records; no ingestion code |
| Bilingual ICMJE/COPE-compliant disclosure | Text asserts verification that did not happen and names an unused model |
| Postgres 16 + pgvector, Redis queue, React 19, TanStack Query | Default DB is SQLite; no Postgres, Redis or LLM dependencies; React 18; no TanStack Query |
| Milestones M0 to M5 complete | 26 of 45 contract operations; no dedup, topic map, extractions, export or delete, logout, SSE, AI screening suggestions, PDF upload |

## 4. Benchmark against the design proposal

### 4.1 Verdict by bundle

| Bundle | Verdict | Evidence |
| --- | --- | --- |
| DAT data ingestion | Partial | OpenAlex and Crossref connectors with 8 s timeouts, no retries. No dedup (model imported, never used). OpenAlex key is sent as a header while the docs use a query parameter; default key is empty, and the old mailto polite pool was retired on 13 Feb 2026 |
| LIB library | Partial | RIS, BibTeX, CSV parsers with line-referenced reports and export are good. No dedup queue, collections, tags, uploads, or extract-only mode |
| SCR screening | Largely implemented | Versioned protocols, append-only decisions, exclusion reasons, conflicts, kappa, PRISMA arithmetic. Gaps: full-text queue lists every library item regardless of title/abstract outcome; kappa returns 1.0 when pe is 1 (spec says n/a); no blind flag on the protocol; no AI suggestions |
| **SYN synthesis** | **Facade** | **See findings 2 and 3; no hybrid retrieval, no extraction run, no SSE, no quotas** |
| **JRN journals** | **Facade** | **Six seeded journals; scoring uses the spec weights, but nothing real to score** |
| **ETH integrity** | **Partial, misleading** | **Reference audit only checks a local flag and missing DOI; disclosure inaccurate; no reviewed flag** |
| MAP mapping | Partial | Lineage formula, bands, chronology rule, positioning, gap signals, overrides present. Topic map absent. Run record claims embedding\_model text-embedding-3-small but TF-IDF is used |
| ENG engineering | Partial | RFC 7807, request IDs, RBAC, health probes, security headers are good. Auth flaws, SQLite default, no i18n, no export or delete |
| **QAS quality** | **Weak** | **No CI, no named tests, low core coverage, loosened gate** |

### 4.2 Contract conformance

Not implemented: DELETE /auth/session, GET /journals/search, DELETE /me, POST /me/export, dedup candidates and decision, POST /projects/{id}/exports, POST extractions, lineage gaps path, PUT/DELETE node override, POST/GET maps and map export, GET positioning/{id}, POST screening/suggestions, synthesis events (SSE), GET works/{id}/citations. Drift: override is POST instead of PUT/DELETE, gaps path differs, and 14 routes exist outside the contract.

### 4.3 Test and gate quality

The suite is real and useful (tenant isolation, RBAC, parsers, kappa, PRISMA, lineage). But 39 tests cannot cover 155 MUST requirements. The repo's check\_requirement\_coverage.py now accepts an ID found anywhere in test text and expands ranges like SCR-001..018 into every ID, which produces 98 of 155 'covered'. A strict count of tests named for an ID is zero. That change weakens the QAS-004 gate silently, against rule G11.

## 5. Findings and fixes

| # | Severity | Finding | Evidence | Fix |
| --- | --- | --- | --- | --- |
| 1 | Critical | Account takeover under default config | APP\_ENV defaults to local; /auth/magic-link returns the token; any email can log in; cookie not Secure; .bat binds 0.0.0.0 | Never return tokens by API; send email; dev login only behind an explicit flag on 127.0.0.1; refuse to boot in prod with default secret or env |
| 2 | Critical | Fabricated AI provenance and false disclosure | Probe: models\_used gemini-1.5-flash, 360 tokens, cost 0.0005 with no LLM call; statement claims independent verification | Log model 'none (rule-based)'; remove untrue sentences; derive text only from real usage; or implement real model calls and record true usage |
| 3 | Critical | Circular verification and gate bypass | Probe: irrelevant query returned completed, 3 claims, 100% verified; code includes zero-score works whenever library size is at most the limit | Relevance threshold before the sufficiency gate; sentence-level BM25 plus embeddings; verifier independent of the generator; tests with irrelevant and adversarial queries |
| 4 | High | Unverifiable journal and article data | Sequential DOI patterns (e.g. ...01001-x, 01002-y, 01003-z; pone.0298101/02/03); searches found none | Delete the seed or mark it demo-only; ingest DOAJ and OpenAlex with provenance; verify licences for Scopus and SINTA fields |
| 5 | High | Weak sessions | Magic links reusable within 15 minutes; session tokens never expire (a token dated 1970 was accepted); no logout, revocation, rate limit, or CSRF | Single-use tokens in DB; expiry check; logout; rate limits; CSRF protection |
| 6 | High | Governance and reporting drift | Loosened gate; PROJECT\_STATE overclaims; benchmark fabricates fallbacks | Restore strict gate; make status claims machine-derived; remove fallbacks from benchmarks |
| 7 | Medium | Contract and schema drift | 19 operations and 9 tables missing | Close gaps by milestone; run contract tests in CI |
| 8 | Medium | OpenAlex access | Header instead of query parameter; no key by default | Use api\_key query parameter; require a key; handle metered limits |
| 9 | Medium | Tests and CI | 63% coverage; no CI; no frontend tests | CI with lint, type, tests, scans; one named test per MUST ID |
| 10 | Medium | Docs versus code | Postgres, Redis, React 19 claimed | Either adopt them or correct the docs |
| 11 | Low | Screening edge cases | Full-text queue, kappa n/a rule | Fix and test |
| 12 | Low | Binary in git | 13 KB ResearchForge.exe committed | Publish builds as release artifacts with checksums |

## 6. What is genuinely good

The architecture is clean and navigable. Errors follow RFC 7807 with request IDs. Tenant isolation and RBAC have tests. Screening arithmetic (kappa, PRISMA reconciliation) is correct for the main path. The lineage engine follows the written formula, enforces the chronology rule, and keeps evidence per link. Parsers report by line. The frontend compiles with no TypeScript errors and builds as claimed. For a single-commit build this is a substantial head start. The problems are about honesty of labels and depth, and they are fixable.

## 7. Competitive brief

### 7.1 Scope and context

Decision informed: product strategy and what to build next for a doctoral-research workspace. Focus: full product comparison. Date: Oct 2026; pricing and features change quickly and sources disagree, so verify before budgeting.

### 7.2 Competitive set

- **Direct:** Rayyan (screening), Elicit (screening, extraction, reports), Consensus (evidence search), JurnalHub (Indonesian all-in-one portal), Covidence and DistillerSR (enterprise reviews).
- **Indirect:** ResearchRabbit, Litmaps, Connected Papers (citation maps), Open Knowledge Maps (topic maps), PaperTree (lineage and positioning).
- **Adjacent:** Zotero, general deep-research assistants at roughly $17 to $20 per month, Semantic Scholar.
- **Substitutes:** Excel plus Zotero plus a general chatbot; supervisors checking by hand.

### 7.3 Competitor overview

| Product | Positioning | Scale | Price as reported | Momentum |
| --- | --- | --- | --- | --- |
| Rayyan | AI-powered systematic review platform | Imports from databases | Free tier (3 reviews, 2 reviewers); about $5 to $8 per seat per month; academic institutional about $25 per licence per month | Adding AI extraction layer (ResearchPilot) |
| Elicit | AI research assistant: search, screen, extract, report | 125M to 138M papers | Free; Pro about $39 to $49 per month; Scale or Team about $65 to $169; sources differ | Self-reports validation against 994 Cochrane reviews; moving to usage pools |
| Consensus | AI academic search engine with Consensus Meter | 200M to 250M papers | Free; Pro about $12 to $15; Deep $45 to $65; Teams custom | Deep Search, medical mode, apps inside ChatGPT, Claude and Copilot, API |
| ResearchRabbit / Litmaps / Connected Papers | Citation-network discovery and monitoring | 270M to 310M catalogues | Free to about $10 per month | ResearchRabbit reported as acquired by Litmaps; premium tier added Oct 2025 |
| Open Knowledge Maps | Non-profit topic maps from metadata | About 400M outputs, 400+ languages | Free; membership-funded | Open source |
| PaperTree | Families, lineage, positioning, gaps with an audit table | User PDFs | Free, community-funded | Indonesian origin |
| JurnalHub | Integrated portal for Indonesian academics | OpenAlex-based | Credit-based (site read 24 Oct 2026) | Claims 14 tools incl. journal match with Scopus and SINTA filters |

### 7.4 Feature comparison

Scale: Strong, Adequate, Weak, Absent, '-' = not evidenced. Competitor cells are desk-research judgments. ResearchHub 'as built' reflects my audit.

| Capability | ResearchHub as built | Spec target | Rayyan | Elicit | Consensus | Map tools | PaperTree | JurnalHub (claimed) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Large-corpus discovery | Weak | Adequate | Absent | Strong | Strong | Strong | Absent | Adequate |
| Duplicate detection | Absent | Strong | Strong | - | Absent | Absent | Absent | - |
| Blind dual screening, conflicts | Adequate | Strong | Strong | Weak | Absent | Absent | Absent | Adequate |
| PRISMA flow computed | Adequate | Strong | Adequate | Adequate | Absent | Absent | Absent | Adequate |
| AI screening and extraction | Absent | Adequate | Adequate | Strong | Absent | Absent | Absent | - |
| Cited synthesis | Weak | Strong | Absent | Strong | Strong | Absent | Absent | Adequate |
| Independent claim verification | Weak | Strong | Absent | Adequate | Adequate | Absent | Absent | - |
| Topic or citation map | Absent | Adequate | Absent | Absent | Absent | Strong | Strong | Adequate |
| Lineage with evidence audit | Adequate | Strong | Absent | Absent | Absent | Absent | Strong | Absent |
| Manuscript positioning | Adequate | Adequate | Absent | Absent | Absent | Absent | Strong | - |
| Journal fit with quartile and APC | Weak | Adequate | Absent | Absent | Absent | Absent | Absent | Strong |
| Accurate AI-use disclosure | Weak | Strong | Absent | Absent | Absent | Absent | Absent | Adequate |
| Indonesian and ASEAN context | Adequate | Strong | Weak | Weak | Weak | Adequate | Strong | Strong |
| Price to a student | Free (self-host) | n/a | Strong | Adequate | Adequate | Strong | Strong | Adequate |

Why these matter: screening, dedup and PRISMA decide whether a review is publishable; verification decides whether anyone can trust the AI output; locale decides adoption in the target market.

### 7.5 Strengths and weaknesses

- **Rayyan.** Strengths: academic-friendly pricing, blind review and conflicts, dedup widely regarded as best in category. Weaknesses: screening-centred, little discovery or synthesis, English-heavy coverage, less audit depth than Covidence.
- **Elicit.** Strengths: end-to-end review workflow, extraction tables, published validation. Weaknesses: independent studies report search sensitivity around 39 to 40% against about 94.5% for traditional searches; extraction errors; pricey; real-time collaboration only on top tiers; journals may not accept 'we used Elicit' as search documentation.
- **Consensus.** Strengths: fast orientation, Consensus Meter, huge corpus, distribution inside general assistants. Weaknesses: peer-reviewed literature only, no screening or reproducible protocol, Deep Search caps.
- **Citation-map tools.** Strengths: excellent exploration, free tiers, alerts. Weaknesses: no screening, limited export, recommendations vary by field.
- **Open Knowledge Maps.** Strengths: non-profit, open, multilingual, metadata-only honesty. Weaknesses: overview only, no workflow.
- **PaperTree.** Strengths: evidence-first lineage, audit table, privacy by design. Weaknesses: small set sizes, no search, no screening.
- **JurnalHub.** Strengths: local focus on Scopus and SINTA, broad toolset. Weaknesses: breadth over depth; includes features (humanizer-style tools) that raise integrity concerns; claims are marketing until tested.

### 7.6 Opportunities

1. **Verified evidence trail.** No competitor combines screening, PRISMA, cited synthesis, lineage, and an honest AI-use record in one auditable workspace.
2. **Indonesia and ASEAN first.** Bilingual workflow, SINTA and Garuda-aware journal fit, UU PDP-aware privacy. Global tools treat this as an afterthought.
3. **Trust layer.** Reference check, claim verifier and accurate disclosure as a standalone value that works on output from any AI tool.
4. **Supervisor and examiner view.** A read-only audit trail committees can inspect.
5. **Open-data transparency** where AI tools hide their retrieval.

### 7.7 Threats

- Elicit and Consensus keep moving into systematic-review workflows; Rayyan is adding AI extraction.
- General deep-research assistants at about $17 to $20 per month set the price anchor and are embedding academic search (Consensus now runs inside ChatGPT, Claude and Copilot).
- Free incumbents (ResearchRabbit, Rayyan free tier, Open Knowledge Maps) cap willingness to pay.
- OpenAlex now requires keys with metered use ($1 per day free with a key, $0.10 keyless), raising cost and fragility for a live-API architecture.
- A trust incident (fabricated data or a false disclosure) would be fatal for an integrity-positioned product. Nightmare scenario: a user publishes with ResearchHub's disclosure text and a reviewer finds it untrue.

### 7.8 Strategic implications

- **Build or accelerate:** real verification, dedup, accurate disclosure, PRISMA-grade audit trail, bilingual UX, Rayyan/Zotero import-export.
- **Differentiate:** auditability, honest labelling, locale, supervisor view.
- **Achieve parity only:** discovery breadth (use OpenAlex bulk snapshot plus targeted APIs), basic screening ergonomics, price (free for students).
- **Deprioritize:** journal catalog until licensed data exists, topic map (Open Knowledge Maps already serves it; link out), native launcher.
- **Positioning statement:** For doctoral researchers in Indonesia and wider ASEAN who must defend their literature review and journal choice, ResearchHub is a verified-evidence workspace that keeps an auditable trail from search to screening to cited synthesis to submission. Unlike AI search tools that give fluent answers, every claim and placement shows its evidence, and the tool says when it does not know.
- **Monitor:** Elicit and Consensus changelogs, Rayyan AI releases, OpenAlex pricing, journal and publisher AI-policy changes, PaperTree and JurnalHub launches.

## 8. Product brainstorm

### 8.1 Frame

Why now: the build looks finished, so the real question is whether it is the right product. Constraint: one builder plus agents; free-tier infrastructure. A great outcome: one sharp wedge you can prove with five real users.

### 8.2 Problem and job

When I must write a defensible literature review and choose a journal, I want a traceable path from question to cited evidence to submission, so I can defend my method to my supervisor, examiners and reviewers. The emotional job is confidence that nothing is fabricated; the social job is looking rigorous. What people fire to hire this: Zotero, Excel, Rayyan, a general chatbot, JurnalHub. The costly failure is not slowness; it is being caught with a bad citation or an undisclosed AI use.

### 8.3 Assumptions, ranked by risk

| # | Assumption | Evidence today | Cheapest test |
| --- | --- | --- | --- |
| 1 (riskiest) | Doctoral students will accept extra rigor and friction in exchange for defensibility | None | Concierge: run 5 real reviews through screening, PRISMA and lineage; measure time and trust |
| 2 | A solo build can differentiate where funded tools lead on AI quality | Competitors fund large models | Do not compete on synthesis; compete on audit and verification |
| 3 | Open data is enough, including Indonesian journals | OpenAlex now metered; local coverage unverified | Sample 50 Indonesian papers and check presence and metadata quality |
| 4 | Someone pays (student, supervisor, or institution) | None | Interview supervisors and library staff; fake-door a licence page |
| 5 | Verification can be real without heavy infrastructure | Current verifier is circular | Build a labelled set of 100 claims; compare an NLI or LLM verifier with human labels |

### 8.4 How might we

- HMW let a doctoral student show an examiner exactly how every cited claim was checked?
- HMW make an honest 'I do not know' feel useful rather than broken?
- HMW give supervisors a read-only audit trail without extra work for students?
- HMW serve Indonesian-language literature as a first-class source?
- HMW prevent a false AI-use statement from ever being generated?

### 8.5 Options (divergent)

1. **Trust layer:** reference checker, claim verifier and disclosure generator that works on any AI output.
2. **Indonesia-first review workspace:** bilingual screening, PRISMA, SINTA-aware journal fit.
3. **Lineage and positioning studio:** the PaperTree-style niche, with open data.
4. **Committee audit workspace:** student works, supervisor audits.
5. **Plugin approach:** verification and PRISMA audit added to Zotero or Rayyan exports.
6. **Remove something:** no generative synthesis at all; ship deterministic evidence tables plus audit.
7. **Do the opposite:** an explicitly AI-free structure notebook that logs human decisions.
8. **Open-source reference implementation** for universities and grant funders.

### 8.6 My opinion

Pick options 1 and 2 with the honesty of 6. The trust layer is where competitors are weakest and your spec is strongest, and Indonesia-first is a market where global tools are thin. Do not build a bigger feature list. The current repository is a feature-parity trap: nine bundles of breadth, with the three claims that matter most (verified, accurate, secure) not yet true. Integrate for discovery instead of rebuilding it. Anti-patterns to name: solutioning before framing, demo-ware shaped like product, and self-reported green dashboards.

### 8.7 Opportunity tree

- **Outcome:** a doctoral student defends their literature review with a verifiable trail.
  - Opportunity: citations might be wrong → solution: reference checker with DOI resolution and retraction status → experiment: run on 5 real reference lists and count real errors found.
  - Opportunity: AI use must be disclosed → solution: disclosure built from real logs → experiment: supervisors rate accuracy and usefulness.
  - Opportunity: screening is tedious and contested → solution: blind dual screening with live PRISMA → experiment: time one real screening of 200 records.
  - Opportunity: where does my paper fit → solution: lineage with evidence → experiment: users compare against their own mental map.

### 8.8 Set aside for now

Topic map (link to Open Knowledge Maps), journal catalog, native launcher, extra bundles, mobile.

## 9. Remediation roadmap

| When | Work | Exit check |
| --- | --- | --- |
| This week (stop-ship) | Fix findings 1 to 3; correct disclosure text and model fields; remove or flag the journal seed; restore strict coverage gate; correct PROJECT\_STATE | Probes from this audit fail to reproduce; negative tests added |
| Weeks 2 to 3 | Single-use links, expiry, logout, rate limits, email delivery; Postgres plus Alembic on CI; OpenAlex key via query parameter; dedup queue; route parity | CI green; contract tests pass |
| Weeks 4 to 6 | Real retrieval (BM25 plus embeddings), independent verifier, extraction, SSE, quotas; one named test per MUST requirement | Golden set meets thresholds in the AI spec |
| Weeks 7 to 10 | Licensed journal ingestion, i18n (EN and ID), a11y and e2e tests, audit\_events and export or delete | Release checklist completed |
| Weeks 10 to 12 | Pilot with 5 to 10 doctoral students and 2 supervisors | Trust and time-saved measured; decide on pricing |

Acceptance tests to add first: replayed magic link rejected; expired session rejected; irrelevant query refused; disclosure lists only models actually called; journal records carry source and fetch date; full-text queue contains only items advanced from title and abstract.

## 10. Method, limits and sources

What I ran: git clone of the public repo; pytest with coverage; npm ci, tsc and vite build; route comparison against the OpenAPI contract; schema comparison; scripted probes with the app's own test client. What I did not do: run the stress, E2E or IEEE scripts; review every line; test the UI in a browser; resolve DOIs against Crossref (not reachable from my environment, so DOI findings rest on web searches finding nothing plus structural patterns, which is strong evidence but not proof). Competitor ratings are desk research.

Sources (accessed Oct 2026): consensus.app, jurnalhub.id, openknowledgemaps.org, papertree.id (read 24 Oct); Rayyan: us.fitgap.com/products/rayyan, theaiagentindex.com/agents/rayyan, casrai.org/guides/rayyan; Consensus: us.fitgap.com/products/061882/consensus, toolsforhumans.ai, theaiagentindex.com/agents/consensus; Elicit: fast.io/resources/elicit-ai-review-2026, aiproductivity.ai/pricing/elicit, academy.techpresso.co/reviews/is-elicit-worth-it, casrai.org/compare/elicit-vs-consensus; map tools: casrai.org/compare/connected-papers-alternatives, tooliverse.ai comparisons, theaiagentindex.com comparisons; OpenAlex: developers.openalex.org/api-reference/authentication, blog.openalex.org, casrai.org/news/openalex-api-keys-mandatory-usage-based-pricing-2026. Prices differ across sources and change often.
