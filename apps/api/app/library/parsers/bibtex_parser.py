import re
from typing import Dict, Any, List
from app.sources.base import normalize_doi


def parse_bibtex_text(content: str) -> Dict[str, Any]:
    """LIB-001 & LIB-004: Parses BibTeX content into canonical work records with parse report."""
    records: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    skipped = 0

    # Pattern matching: @type{cite_key, field = {val}, ...}
    entry_pattern = re.compile(r"@([a-zA-Z]+)\s*\{\s*([^,]+),", re.MULTILINE)
    field_pattern = re.compile(r'([a-zA-Z0-9_\-]+)\s*=\s*(?:\{([^}]*)\}|"([^"]*)"|([0-9]+))', re.DOTALL)

    entries = re.split(r"(?=@(?:article|book|inproceedings|techreport|misc|phdthesis)\b)", content, flags=re.IGNORECASE)

    for idx, block in enumerate(entries):
        block = block.strip()
        if not block.startswith("@"):
            continue

        match = entry_pattern.search(block)
        if not match:
            continue

        work_type = match.group(1).lower()
        fields: Dict[str, str] = {}
        for fmatch in field_pattern.finditer(block):
            field_name = fmatch.group(1).lower()
            val = fmatch.group(2) or fmatch.group(3) or fmatch.group(4) or ""
            fields[field_name] = val.strip()

        title = fields.get("title", "")
        # Clean LaTeX braces from title
        title = re.sub(r"[{}]", "", title).strip()

        if not title:
            errors.append({"entry_index": idx + 1, "reason": "Missing required title field"})
            skipped += 1
            continue

        # Authors: split by "and"
        authors_raw = fields.get("author", "")
        authors = [a.strip() for a in re.split(r"\band\b", authors_raw, flags=re.IGNORECASE) if a.strip()]

        # Year
        year_val = None
        if fields.get("year"):
            ym = re.search(r"\b(19\d\d|20\d\d)\b", fields["year"])
            if ym:
                year_val = int(ym.group(1))

        venue = fields.get("journal") or fields.get("booktitle") or fields.get("publisher")
        doi = normalize_doi(fields.get("doi"))
        abstract = fields.get("abstract")

        records.append({
            "work_type": work_type,
            "title": title,
            "authors": authors,
            "year": year_val,
            "venue": venue,
            "doi": doi,
            "abstract": abstract,
        })

    return {
        "imported": len(records),
        "skipped": skipped,
        "errors": errors,
        "records": records,
    }
