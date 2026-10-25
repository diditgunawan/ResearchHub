import csv
import io
import re
from typing import Dict, Any, List
from app.sources.base import normalize_doi


def parse_csv_text(content: str) -> Dict[str, Any]:
    """LIB-001 & LIB-004: Parses CSV records with dynamic column mapping and parse report."""
    records: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    skipped = 0

    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        return {"imported": 0, "skipped": 0, "errors": [{"line": 1, "reason": "Empty CSV or missing headers"}], "records": []}

    # Normalize header mapping
    header_map = {}
    for col in reader.fieldnames:
        clean_col = col.strip().lower()
        if clean_col in ["title", "article title", "document title"]:
            header_map["title"] = col
        elif clean_col in ["author", "authors", "creator"]:
            header_map["authors"] = col
        elif clean_col in ["year", "publication year", "pub_year"]:
            header_map["year"] = col
        elif clean_col in ["journal", "venue", "source title", "publication"]:
            header_map["venue"] = col
        elif clean_col in ["doi", "digital object identifier"]:
            header_map["doi"] = col
        elif clean_col in ["abstract", "description"]:
            header_map["abstract"] = col

    if "title" not in header_map:
        return {
            "imported": 0,
            "skipped": 0,
            "errors": [{"line": 1, "reason": "No 'title' column recognized in headers"}],
            "records": [],
        }

    for row_idx, row in enumerate(reader, start=2):
        raw_title = row.get(header_map["title"], "").strip()
        if not raw_title:
            errors.append({"line": row_idx, "reason": "Empty title"})
            skipped += 1
            continue

        # Authors
        authors_raw = row.get(header_map.get("authors", ""), "").strip()
        authors = [a.strip() for a in re.split(r"[;,|]", authors_raw) if a.strip()] if authors_raw else []

        # Year
        year_val = None
        raw_year = row.get(header_map.get("year", ""), "").strip()
        if raw_year:
            ym = re.search(r"\b(19\d\d|20\d\d)\b", raw_year)
            if ym:
                year_val = int(ym.group(1))

        venue = row.get(header_map.get("venue", ""), "").strip() or None
        doi = normalize_doi(row.get(header_map.get("doi", ""), ""))
        abstract = row.get(header_map.get("abstract", ""), "").strip() or None

        records.append({
            "title": raw_title,
            "authors": authors,
            "year": year_val,
            "venue": venue,
            "doi": doi,
            "abstract": abstract,
            "work_type": "article",
        })

    return {
        "imported": len(records),
        "skipped": skipped,
        "errors": errors,
        "records": records,
    }
