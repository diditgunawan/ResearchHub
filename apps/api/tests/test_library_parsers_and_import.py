import pytest
from httpx import AsyncClient
from app.library.parsers.ris_parser import parse_ris_text
from app.library.parsers.bibtex_parser import parse_bibtex_text
from app.library.parsers.csv_parser import parse_csv_text

# SYNTHETIC TEST FIXTURE (LIB-001, LIB-004, LIB-009)

def test_ris_parser_success_and_error_reporting():
    """LIB-001 & LIB-004: RIS parser extracts fields and reports missing required fields with line references."""
    ris_content = """
TY  - JOUR
TI  - Grounded Artificial Intelligence in Scientific Research
AU  - Didit, A.
AU  - Sutanto, B.
PY  - 2024
JO  - Journal of Artificial Intelligence Research
DO  - 10.1613/jair.1.12345
AB  - An empirical investigation into zero-hallucination agent architectures.
ER  - 

TY  - CONF
AU  - Nameless Author
PY  - 2025
ER  - 
"""
    result = parse_ris_text(ris_content)
    assert result["imported"] == 1
    assert result["skipped"] == 1
    assert len(result["errors"]) == 1
    assert "Missing required title" in result["errors"][0]["reason"]
    
    rec = result["records"][0]
    assert rec["title"] == "Grounded Artificial Intelligence in Scientific Research"
    assert rec["doi"] == "10.1613/jair.1.12345"
    assert rec["year"] == 2024
    assert len(rec["authors"]) == 2


def test_bibtex_parser_success():
    """LIB-001: BibTeX parser handles multiple entries and authors delimited by 'and'."""
    bib_content = """
@article{vaswani2017attention,
  title = {Attention Is All You Need},
  author = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki},
  journal = {Advances in Neural Information Processing Systems},
  year = {2017},
  doi = {10.5555/3295222.3295349}
}
"""
    result = parse_bibtex_text(bib_content)
    assert result["imported"] == 1
    rec = result["records"][0]
    assert rec["title"] == "Attention Is All You Need"
    assert rec["year"] == 2017
    assert len(rec["authors"]) == 3
    assert rec["doi"] == "10.5555/3295222.3295349"


def test_csv_parser_success():
    """LIB-001: CSV parser detects title, authors, year, and DOI headers."""
    csv_content = """Title,Authors,Year,Venue,DOI
PRISMA 2020 Statement,Page MJ; McKenzie JE,2021,BMJ,10.1136/bmj.n71
"""
    result = parse_csv_text(csv_content)
    assert result["imported"] == 1
    rec = result["records"][0]
    assert rec["title"] == "PRISMA 2020 Statement"
    assert rec["year"] == 2021
    assert rec["venue"] == "BMJ"
    assert rec["doi"] == "10.1136/bmj.n71"
    assert len(rec["authors"]) == 2


@pytest.mark.asyncio
async def test_library_import_and_export_roundtrip(client: AsyncClient):
    """LIB-002, LIB-004, LIB-009: Import RIS text into project library and export back to BibTeX and CSV."""
    # 1. Authenticate user and create project
    from tests.conftest import get_test_link_token
    token = await get_test_link_token("lib.owner@lab.org")
    sess = await client.post("/auth/session", json={"token": token})
    headers = {"Authorization": f"Bearer {sess.json()['session_token']}"}

    proj = await client.post("/projects", json={"name": "Evidence Base Library"}, headers=headers)
    project_id = proj.json()["id"]

    # 2. Import RIS content
    ris_data = """
TY  - JOUR
TI  - Deep Residual Learning for Image Recognition
AU  - He, Kaiming
AU  - Zhang, Xiangyu
PY  - 2016
JO  - CVPR
DO  - 10.1109/CVPR.2016.90
AB  - Deep convolutional networks for visual recognition.
ER  - 
"""
    import_res = await client.post(
        f"/projects/{project_id}/imports",
        json={"format": "ris", "content": ris_data},
        headers=headers,
    )
    assert import_res.status_code == 200
    batch = import_res.json()
    assert batch["imported_count"] == 1
    assert batch["skipped_count"] == 0

    # 3. Query library items
    lib_res = await client.get(f"/projects/{project_id}/library/items", headers=headers)
    assert lib_res.status_code == 200
    items = lib_res.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Deep Residual Learning for Image Recognition"
    assert items[0]["doi"] == "10.1109/cvpr.2016.90"

    # 4. Export library as BibTeX
    export_bib = await client.get(f"/projects/{project_id}/exports?format=bibtex", headers=headers)
    assert export_bib.status_code == 200
    assert "@article" in export_bib.text
    assert "Deep Residual Learning" in export_bib.text

    # 5. Export library as CSV
    export_csv = await client.get(f"/projects/{project_id}/exports?format=csv", headers=headers)
    assert export_csv.status_code == 200
    assert "Title,Year,Venue,DOI,Abstract" in export_csv.text
    assert "10.1109/cvpr.2016.90" in export_csv.text
