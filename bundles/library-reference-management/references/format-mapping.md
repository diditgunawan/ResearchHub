# Format mapping (core fields)
| Canonical | RIS | BibTeX | CSL-JSON |
|---|---|---|---|
| title | TI / T1 | title | title |
| authors | AU / A1 | author (and-separated) | author[] {family,given} |
| year | PY / Y1 | year | issued.date-parts[0][0] |
| venue | JO / JF / T2 | journal / booktitle | container-title |
| volume/issue/pages | VL / IS / SP-EP | volume / number / pages | volume / issue / page |
| DOI | DO | doi | DOI |
| abstract | AB | abstract | abstract |
| keywords | KW (repeatable) | keywords | keyword |
| type | TY | entry type | type |
| url | UR | url | URL |
Edge cases to test: unicode names, braces/LaTeX escapes in BibTeX, multi-line abstracts, repeated KW tags, missing ER terminator, DOI as URL, duplicate DOIs in one file, CSV with BOM and semicolons.
