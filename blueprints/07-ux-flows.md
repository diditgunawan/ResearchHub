# 07 — UX Flows & Screens

## Information architecture
Home (projects) → Project: Search · Library · Screening · Synthesis · Map & lineage · Position & gaps · Check · Journals (Settings in account menu). Prototype v0.1: `prototype/`.

## Screens
1. **Search** — query bar, filters (year, OA, type, language), per-source status chips, result cards (title, authors, venue, year, OA badge, citations, "source: OpenAlex · fetched 2026-10-24"), bulk "Add to library".
2. **Work detail** — metadata, abstract, identifiers, OA link, cited-by/references tabs, citation graph (lazy), retraction badge.
3. **Library** — table + collection tree, tag filters, duplicates banner, import/export buttons, per-item notes, attach PDF.
4. **Import report** — counts, errors with row refs, "review N possible duplicates".
5. **Dedup queue** — side-by-side diff, merge/keep-separate, undo.
6. **Protocol** — question, framework fields, criteria lists, dates; version history.
7. **Screening** — focus card: title, abstract with highlighted include/exclude keywords, buttons Include / Maybe / Exclude (+reason), keyboard (I/M/E, ←/→), progress, optional AI suggestion panel (collapsed by default, shows rationale, labelled "suggestion").
8. **Conflicts & agreement** — list, resolve, kappa.
9. **PRISMA** — live flow diagram, export.
10. **Synthesis** — question box, scope selector, run progress (SSE), answer with numbered inline citations; hover shows chunk text + work; verification badges; refusal state; "Extraction table" tab.
11. **Check** — paste reference list/upload; per-item status table; AI-use disclosure generator.
12. **Journals** — paste title+abstract, filters, ranked cards with score breakdown + data freshness, compare drawer, checklist.
13. **Settings** — profile, locale, quotas/usage, export/delete data, API keys (Zotero), members.

## UX rules
- Never show an unverified claim without a visible "unverified" state.
- AI content always labelled and visually distinct.
- Empty/error/loading states for every screen; optimistic UI only for non-audit actions.
- Keyboard-first for screening; WCAG 2.2 AA; color is never the sole signal.
- Copy is bilingual-ready (no concatenated strings).
- Show data freshness and source on every external datum.

## Mapping screens (v0.2)
14. **Topic map** — scope picker (search results / library subset), run button, bubble view + list alternative, cluster drawer (keywords, top papers, language mix), add-to-library, export.
15. **Lineage views** — tabs: Botanical tree · Lineage map · Audit table (same data); badges root/placed/needs-review; evidence tooltip; override control with history.
16. **Position my paper** — paste title+abstract or upload; result card: closest family (+ runner-up), top-3 parents with Cit/Sem/Kw/Chr bars, shared vs distinctive concepts; banner "closest in the analyzed set".
17. **Gap view** — four tabs (unresolved conditions, future work, lineage gaps, data quality); banner "gaps are relative to the papers you analyzed"; each row links to source excerpt.
18. **PDF upload dialog** — choose *Keep original* or *Extract-only (delete original after extraction)*; progress per file; per-file report.
UX rules additions: every canvas view has a table equivalent; no placement shown without an evidence link; avoid visual identity borrowed from reference products.
