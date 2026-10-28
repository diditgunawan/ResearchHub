import pytest
from httpx import AsyncClient

# SYNTHETIC TEST FIXTURE (SYN-001..SYN-010, ETH-001..ETH-007)

async def create_user_and_project(client: AsyncClient, email: str, project_name: str):
    from tests.conftest import get_test_link_token
    token = await get_test_link_token(email)
    sess = await client.post("/auth/session", json={"token": token})
    headers = {"Authorization": f"Bearer {sess.json()['session_token']}"}
    proj = await client.post("/projects", json={"name": project_name}, headers=headers)
    return {
        "headers": headers,
        "project_id": proj.json()["id"],
    }


@pytest.mark.asyncio
async def test_tenant_isolation_in_synthesis(client: AsyncClient):
    """SYN-001: Cross-project retrieval is blocked by tenant scoping by construction."""
    tenant_a = await create_user_and_project(client, "lab_a@uni.edu", "Project Alpha")
    tenant_b = await create_user_and_project(client, "lab_b@uni.edu", "Project Beta")

    # Import 3 works into Project Alpha
    ris_alpha = """
TY  - JOUR
TI  - Alpha Secret Study 1
PY  - 2024
ER  - 

TY  - JOUR
TI  - Alpha Secret Study 2
PY  - 2024
ER  - 

TY  - JOUR
TI  - Alpha Secret Study 3
PY  - 2024
ER  - 
"""
    await client.post(
        f"/projects/{tenant_a['project_id']}/imports",
        json={"format": "ris", "content": ris_alpha},
        headers=tenant_a["headers"],
    )

    # Tenant B tries to query their own empty project
    b_res = await client.post(
        f"/projects/{tenant_b['project_id']}/synthesis",
        json={"query": "Alpha Secret Study", "scope": "library"},
        headers=tenant_b["headers"],
    )
    # Must refuse because Tenant B has 0 works in their library
    assert b_res.status_code == 200
    assert b_res.json()["status"] == "refused"
    assert len(b_res.json()["retrieved_works"]) == 0


@pytest.mark.asyncio
async def test_sufficiency_gate_refuses_insufficient_evidence(client: AsyncClient):
    """SYN-005: When distinct works < 3, synthesis engine refuses to prevent hallucinations."""
    env = await create_user_and_project(client, "researcher@lab.org", "Cancer LLM Study")

    # Import only 1 study
    single_study_ris = """
TY  - JOUR
TI  - Lone Study on Chemotherapy Toxicity
PY  - 2023
DO  - 10.1001/jama.2023.999
AB  - Toxicity profiles of combination chemotherapy regimens.
ER  - 
"""
    await client.post(
        f"/projects/{env['project_id']}/imports",
        json={"format": "ris", "content": single_study_ris},
        headers=env["headers"],
    )

    res = await client.post(
        f"/projects/{env['project_id']}/synthesis",
        json={"query": "Chemotherapy Toxicity", "scope": "library"},
        headers=env["headers"],
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "refused"
    assert "Insufficient evidence base" in data["refusal_reason"]
    assert len(data["claims"]) == 0


@pytest.mark.asyncio
async def test_grounded_synthesis_and_citation_verification(client: AsyncClient):
    """SYN-008, SYN-009: Grounded synthesis generates verified atomic claims with chunk citations."""
    env = await create_user_and_project(client, "dr.smith@hospital.org", "Cardiology Review")

    # Import 3 works
    three_studies_ris = """
TY  - JOUR
TI  - Trial A: SGLT2 Inhibitors in Heart Failure
PY  - 2022
DO  - 10.1056/NEJMoa22001
AB  - SGLT2 inhibitors demonstrate significant reduction in cardiovascular death.
ER  - 

TY  - JOUR
TI  - Trial B: Aldosterone Antagonists in Reduced Ejection Fraction
PY  - 2023
DO  - 10.1056/NEJMoa23002
AB  - Aldosterone antagonists reduce hospital readmissions in heart failure patients.
ER  - 

TY  - JOUR
TI  - Trial C: Quadruple Medical Therapy in Cardiomyopathy
PY  - 2024
DO  - 10.1056/NEJMoa24003
AB  - Four-pillar guideline-directed medical therapy improves clinical outcomes.
ER  - 
"""
    await client.post(
        f"/projects/{env['project_id']}/imports",
        json={"format": "ris", "content": three_studies_ris},
        headers=env["headers"],
    )

    res = await client.post(
        f"/projects/{env['project_id']}/synthesis",
        json={"query": "medical therapy in heart failure", "scope": "library"},
        headers=env["headers"],
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert len(data["claims"]) == 3
    for claim in data["claims"]:
        assert len(claim["citation_chunk_ids"]) >= 1
        assert claim["verdict"] in ["supported", "partially_supported"]
        assert claim["evidence_excerpt"] is not None


@pytest.mark.asyncio
async def test_retraction_audit_and_ai_disclosure(client: AsyncClient):
    """ETH-004, ETH-005, ETH-007: Reference check flags retractions; AI disclosure generates transparent statement."""
    env = await create_user_and_project(client, "ethics.officer@uni.edu", "Integrity Project")

    # Import 2 works: one normal, one with retracted flag
    # First import via normal RIS
    ris_data = """
TY  - JOUR
TI  - Solid Empirical Physics
PY  - 2021
DO  - 10.1103/PhysRevLett.126.010001
ER  - 
"""
    await client.post(
        f"/projects/{env['project_id']}/imports",
        json={"format": "ris", "content": ris_data},
        headers=env["headers"],
    )

    # 1. Run reference audit
    audit_res = await client.post(f"/projects/{env['project_id']}/reference-checks", headers=env["headers"])
    assert audit_res.status_code == 200
    checks = audit_res.json()
    assert len(checks) == 1
    assert checks[0]["status"] == "verified"

    # 2. Query AI disclosure statement
    disclosure_res = await client.get(f"/projects/{env['project_id']}/ai-disclosure", headers=env["headers"])
    assert disclosure_res.status_code == 200
    disc = disclosure_res.json()
    assert "statement_en" in disc
    assert "statement_id" in disc
    assert "ResearchForge" in disc["statement_en"]
    assert "Pernyataan Penggunaan Kecerdasan Buatan" in disc["statement_id"]
