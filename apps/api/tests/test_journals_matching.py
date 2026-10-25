import pytest
from httpx import AsyncClient

# SYNTHETIC TEST FIXTURE (JRN-001..JRN-012)

@pytest.mark.asyncio
async def test_journal_search_and_hard_filters(client: AsyncClient):
    """
    JRN-003, JRN-004: Hard filters apply before scoring; filtered-out journals never appear.
    """
    # 1. Search with Q1 filter
    q1_res = await client.get("/journals?quartiles=Q1")
    assert q1_res.status_code == 200
    q1_data = q1_res.json()
    assert len(q1_data) >= 1
    for j in q1_data:
        assert j["scopus_quartile"] == "Q1"

    # 2. Filter for SINTA journals
    sinta_res = await client.get("/journals?sinta_ranks=S2")
    assert sinta_res.status_code == 200
    sinta_data = sinta_res.json()
    assert len(sinta_data) >= 1
    for j in sinta_data:
        assert j["sinta_rank"] == "S2"

    # 3. Filter for zero-APC Open Access journals
    zero_apc_res = await client.get("/journals?require_oa=true&max_apc_usd=0")
    assert zero_apc_res.status_code == 200
    zero_apc_data = zero_apc_res.json()
    assert len(zero_apc_data) >= 1
    for j in zero_apc_data:
        assert j["is_oa"] is True
        assert (j["apc_usd"] or 0) == 0


@pytest.mark.asyncio
async def test_manuscript_journal_matching_and_disclaimer(client: AsyncClient):
    """
    JRN-005..JRN-009: 3-component matching; >= 3 similar recent articles; strict anti-hallucination disclaimer.
    """
    title = "Multimodal Deep Learning for Real-Time Cardiac Surgical Navigation"
    abstract = (
        "We propose an attention-guided deep learning pipeline integrating intraoperative ultrasound "
        "and video streams to provide real-time anatomical navigation during minimally invasive cardiac procedures."
    )

    res = await client.post(
        "/journals/match",
        json={
            "title": title,
            "abstract": abstract,
            "require_oa": False,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["matched_count"] >= 1
    assert "acceptance probability" in data["disclaimer"]

    top_match = data["recommendations"][0]
    assert "score_breakdown" in top_match
    breakdown = top_match["score_breakdown"]
    assert "semantic_score" in breakdown
    assert "keyword_score" in breakdown
    assert "citation_affinity" in breakdown

    # JRN-007: >= 3 similar recent articles with DOIs
    assert len(top_match["similar_recent_articles"]) >= 3
    for art in top_match["similar_recent_articles"]:
        assert "title" in art
        assert "doi" in art


@pytest.mark.asyncio
async def test_journal_input_length_limit(client: AsyncClient):
    """
    JRN-005: Input title + abstract exceeding 6,000 characters is rejected.
    """
    long_abstract = "A" * 6005
    res = await client.post(
        "/journals/match",
        json={
            "title": "Title",
            "abstract": long_abstract,
        },
    )
    assert res.status_code in [400, 422]


@pytest.mark.asyncio
async def test_submission_checklist_generation(client: AsyncClient):
    """
    JRN-010: Submission checklist items cite source URLs; unverifiable items marked 'verify manually'.
    """
    # Fetch any journal ID
    journals_res = await client.get("/journals")
    journal_id = journals_res.json()[0]["id"]

    checklist_res = await client.get(f"/journals/{journal_id}/checklist")
    assert checklist_res.status_code == 200
    chk = checklist_res.json()
    assert len(chk["items"]) >= 4

    statuses = [item["status"] for item in chk["items"]]
    assert "verified" in statuses
    assert "verify_manually" in statuses
    for item in chk["items"]:
        assert item["source_url"] is not None
