# PRISMA 2020 flow computation
Boxes (computed): 
1. Records identified — sum of `import_batches.stats.imported` grouped by `source_label` (databases) + other methods.
2. Duplicates removed — count of dedup merges/auto-links within this project.
3. Records screened — unique items entering title/abstract.
4. Records excluded (TA) — items finally excluded at TA.
5. Reports sought for retrieval / not retrieved — user-marked flag on FT-pending items.
6. Reports assessed for eligibility — items entering full text (retrieved).
7. Reports excluded (FT) with reasons — grouped by reason code.
8. Studies included — final FT_included.
Output JSON: `{boxes:{...}, reasons:[{code,label,count}], reconciliation:{ok:bool, issues:[]}}`; exports: SVG, PNG, CSV. Show warning banner when any stage has unresolved items.
