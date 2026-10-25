import re
from typing import Dict, Any, List
from app.sources.base import normalize_doi


def parse_ris_text(content: str) -> Dict[str, Any]:
    """LIB-001 & LIB-004: Parses RIS text and generates structured records with line-referenced parse report."""
    lines = content.splitlines()
    records: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    skipped = 0

    current_entry: Dict[str, Any] = {"authors": []}
    in_record = False
    start_line = 1

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        # Tag format: XX  - value
        match = re.match(r"^([A-Z0-9]{2})\s*-\s*(.*)$", line)
        if not match:
            continue

        tag, value = match.group(1), match.group(2).strip()

        if tag == "TY":
            in_record = True
            start_line = line_num
            current_entry = {
                "work_type": value.lower(),
                "authors": [],
                "title": "",
                "year": None,
                "venue": None,
                "doi": None,
                "abstract": None,
            }
        elif in_record:
            if tag in ["TI", "T1"]:
                current_entry["title"] = value
            elif tag in ["AU", "A1"]:
                current_entry["authors"].append(value)
            elif tag in ["PY", "Y1"]:
                # Extract 4-digit year
                year_match = re.search(r"\b(19\d\d|20\d\d)\b", value)
                if year_match:
                    current_entry["year"] = int(year_match.group(1))
            elif tag in ["JO", "JF", "JA", "T2"]:
                current_entry["venue"] = value
            elif tag in ["DO", "DI"]:
                current_entry["doi"] = normalize_doi(value)
            elif tag in ["AB", "N2"]:
                current_entry["abstract"] = value
            elif tag == "ER":
                # End of record
                if current_entry.get("title"):
                    records.append(current_entry)
                else:
                    errors.append({
                        "line": start_line,
                        "reason": "Missing required title field (TI/T1)",
                    })
                    skipped += 1
                in_record = False
                current_entry = {"authors": []}

    return {
        "imported": len(records),
        "skipped": skipped,
        "errors": errors,
        "records": records,
    }
