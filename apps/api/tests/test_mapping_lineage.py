import pytest
from httpx import AsyncClient

# SYNTHETIC TEST FIXTURE (MAP-001..MAP-019)

async def setup_mapping_environment(client: AsyncClient):
    """Creates user, project, and imports a 4-paper chronological literature set."""
    from tests.conftest import get_test_link_token
    token = await get_test_link_token("curator@lab.org")
    sess = await client.post("/auth/session", json={"token": token})
    headers = {"Authorization": f"Bearer {sess.json()['session_token']}"}

    proj = await client.post("/projects", json={"name": "Generative AI in Clinical Informatics"}, headers=headers)
    project_id = proj.json()["id"]

    # 4 Chronological Papers:
    # Paper 1 (2021) - Foundational Transformer for Clinical Text
    # Paper 2 (2023) - Clinical NER with Few-Shot Transformers (cites Paper 1)
    # Paper 3 (2024) - LLMs for Automated Discharge Summaries (cites Paper 2)
    # Paper 4 (2022) - Rule-based NLP Baseline
    ris_content = """
TY  - JOUR
TI  - Foundational Transformer Architecture for Clinical Records
PY  - 2021
DO  - 10.1016/j.jbi.2021.103001
AB  - We present self-attention transformer models pre-trained on clinical notes. Limitation of this study is high computational cost.
ER  - 

TY  - JOUR
TI  - Clinical Named Entity Recognition via Few-Shot Transformers
PY  - 2023
DO  - 10.1016/j.jbi.2023.103002
AB  - Enhancing clinical named entity extraction with sparse attention. Future work will investigate cross-lingual clinical NLP.
ER  - 

TY  - JOUR
TI  - Large Language Models for Automated Hospital Discharge Summaries
PY  - 2024
DO  - 10.1016/j.jbi.2024.103003
AB  - Evaluating clinical safety of generative models in patient discharge summaries. Remains challenging to eliminate subtle hallucinations.
ER  - 

TY  - JOUR
TI  - Rule-Based Natural Language Processing in Medical Coding
PY  - 2022
DO  - 10.1016/j.jbi.2022.103004
AB  - Deterministic expert rules for automated ICD coding.
ER  - 
"""
    await client.post(
        f"/projects/{project_id}/imports",
        json={"format": "ris", "content": ris_content},
        headers=headers,
    )

    return {
        "headers": headers,
        "project_id": project_id,
    }


@pytest.mark.asyncio
async def test_lineage_mapping_and_chronological_constraint(client: AsyncClient):
    """
    MAP-001, MAP-007, MAP-008: Generate lineage DAG.
    Verify that every edge parent Year <= child Year (no backwards chronological edges).
    """
    env = await setup_mapping_environment(client)
    pid = env["project_id"]
    headers = env["headers"]

    # Trigger lineage run
    res = await client.post(
        f"/projects/{pid}/lineage",
        json={"kind": "lineage", "scope_type": "library_all", "seed": 42},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["record_count"] == 4
    assert len(data["nodes"]) == 4

    # MAP-008 Hard Rule: Parent year <= Child year
    nodes_by_id = {n["work_id"]: n for n in data["nodes"]}
    for edge in data["edges"]:
        parent = nodes_by_id.get(edge["parent_work_id"])
        child = nodes_by_id.get(edge["child_work_id"])
        if parent and child and parent["year"] and child["year"]:
            assert parent["year"] <= child["year"], f"Chronology violated: {parent['year']} > {child['year']}"


@pytest.mark.asyncio
async def test_lineage_audit_table_and_confidence_bands(client: AsyncClient):
    """
    MAP-009, MAP-011: Audit table lists every paper with confidence bands and summary metrics.
    """
    env = await setup_mapping_environment(client)
    pid = env["project_id"]
    headers = env["headers"]

    # Trigger lineage
    run_res = await client.post(f"/projects/{pid}/lineage", json={"kind": "lineage"}, headers=headers)
    run_id = run_res.json()["run_id"]

    # Query audit table
    audit_res = await client.get(f"/projects/{pid}/lineage/{run_id}/audit", headers=headers)
    assert audit_res.status_code == 200
    audit = audit_res.json()
    assert audit["total_records"] == 4
    assert "summary" in audit
    assert audit["summary"]["roots"] >= 1
    assert len(audit["rows"]) == 4

    # Verify each row contains evidence components
    for row in audit["rows"]:
        assert "role" in row
        assert "confidence_band" in row
        assert "evidence" in row
        if row["evidence"]:
            assert "cit" in row["evidence"]
            assert "sem" in row["evidence"]
            assert "kw" in row["evidence"]
            assert "chr" in row["evidence"]


@pytest.mark.asyncio
async def test_user_override_lineage_node(client: AsyncClient):
    """
    MAP-013: User overrides parent/branch; tracks user identity and preserves machine evidence.
    """
    env = await setup_mapping_environment(client)
    pid = env["project_id"]
    headers = env["headers"]

    run_res = await client.post(f"/projects/{pid}/lineage", json={"kind": "lineage"}, headers=headers)
    graph = run_res.json()
    run_id = graph["run_id"]
    child_work_id = graph["nodes"][1]["work_id"]
    new_parent_id = graph["nodes"][0]["work_id"]

    # Submit user override
    override_res = await client.post(
        f"/projects/{pid}/lineage/{run_id}/override",
        json={"work_id": child_work_id, "parent_work_id": new_parent_id, "reason": "Expert historical connection"},
        headers=headers,
    )
    assert override_res.status_code == 200
    overridden = override_res.json()
    assert overridden["parent_work_id"] == new_parent_id
    assert overridden["user_override"] is not None
    assert overridden["user_override"]["reason"] == "Expert historical connection"


@pytest.mark.asyncio
async def test_manuscript_positioning_and_gap_signals(client: AsyncClient):
    """
    MAP-015, MAP-016, MAP-017: Manuscript positioning returns top-3 parents without claiming global novelty.
    Gap signals extract excerpts <= 300 chars.
    """
    env = await setup_mapping_environment(client)
    pid = env["project_id"]
    headers = env["headers"]

    run_res = await client.post(f"/projects/{pid}/lineage", json={"kind": "lineage"}, headers=headers)
    run_id = run_res.json()["run_id"]

    # Position manuscript
    pos_res = await client.post(
        f"/projects/{pid}/positioning",
        json={
            "lineage_run_id": run_id,
            "title": "Clinical Agentic LLMs in Hospital Readmission Prevention",
            "abstract": "We evaluate generative language models for reducing hospital readmission risks in cardiology patients.",
            "retain_text": False,
        },
        headers=headers,
    )
    assert pos_res.status_code == 200
    pos = pos_res.json()
    assert "top_parents" in pos
    assert len(pos["top_parents"]) <= 3
    assert "Closest in the analyzed set" in pos["disclaimer"]
    assert "novelty" in pos["disclaimer"].lower()

    # Query gap signals (MAP-017)
    gaps_res = await client.get(f"/projects/{pid}/gaps/{run_id}", headers=headers)
    assert gaps_res.status_code == 200
    gaps = gaps_res.json()
    assert len(gaps) >= 1
    for g in gaps:
        assert g["kind"] in ["future_work", "unresolved_condition", "lineage_gap", "data_quality"]
        if g["excerpt"]:
            assert len(g["excerpt"]) <= 300
        assert "not constitute global novelty" in g["disclaimer"]
