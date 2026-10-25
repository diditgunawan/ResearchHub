# Views and audit surface
## Shared analysis → three views
1. **Topic map** (discovery): bubbles/treemap; size = members; hover = label + keywords + top papers; list alternative; export.
2. **Botanical tree** (landscape): time on one axis (older = near roots, newer = canopy), branches = families, leaves = papers; hover/click opens paper + evidence. *Use our own visual style; no reuse of PaperTree art or naming.*
3. **Lineage map** (precision): expandable parent–child tree; node badges: root / placed / needs-review; edge tooltip shows component scores.
4. **Audit table** (evidence): columns — Paper, Year, Branch, Parent, Evidence (cit/sem/kw/chr chips), Confidence, Status, Missing metadata, Overridden?; filters for status/confidence/branch; CSV export.
## Position panel
Closest family + runner-up; top-3 parents with breakdown bars (Cit/Sem/Kw/Chr); shared vs distinctive concepts; evidence list; disclaimer banner.
## Gap panel
Tabs: Unresolved conditions · Future-work signals · Lineage gaps · Data quality. Each row: signal, frequency, source papers (links), excerpt, extractor version. Banner always visible: "Gaps are relative to the papers you analyzed."
## Accessibility
Every canvas/SVG view has a table equivalent; keyboard focus order; color never the only signal (use shapes/labels); reduced-motion respected.
## Export
CSV (audit), SVG/PNG (views), JSON (full analysis incl. evidence), BibTeX/RIS of any cluster/family.
