import pytest
from httpx import AsyncClient

# SYNTHETIC TEST FIXTURE (SCR-001..SCR-013)

async def setup_review_environment(client: AsyncClient):
    """Creates owner, reviewer2, and a project with 3 imported works."""
    # Owner
    owner_link = await client.post("/auth/magic-link", json={"email": "owner.pi@university.edu"})
    owner_sess = await client.post("/auth/session", json={"token": owner_link.json()["token"]})
    owner_headers = {"Authorization": f"Bearer {owner_sess.json()['session_token']}"}

    # Reviewer 2
    rev_link = await client.post("/auth/magic-link", json={"email": "reviewer2@university.edu"})
    rev_sess = await client.post("/auth/session", json={"token": rev_link.json()["token"]})
    rev_headers = {"Authorization": f"Bearer {rev_sess.json()['session_token']}"}

    # Create project
    proj_res = await client.post("/projects", json={"name": "Clinical NLP Systematic Review"}, headers=owner_headers)
    project_id = proj_res.json()["id"]

    # Add reviewer2 to project
    await client.post(
        f"/projects/{project_id}/members",
        json={"email": "reviewer2@university.edu", "role": "reviewer"},
        headers=owner_headers,
    )

    # Import 3 works via RIS
    sample_ris = """
TY  - JOUR
TI  - Study 1: Transformer Models for Clinical NER
AU  - Author, One
PY  - 2023
DO  - 10.1001/jama.2023.001
ER  - 

TY  - JOUR
TI  - Study 2: Rule-Based Medical Coding in Oncology
AU  - Author, Two
PY  - 2022
DO  - 10.1001/jama.2022.002
ER  - 

TY  - JOUR
TI  - Study 3: Large Language Models in Patient Discharge
AU  - Author, Three
PY  - 2024
DO  - 10.1001/jama.2024.003
ER  - 
"""
    await client.post(
        f"/projects/{project_id}/imports",
        json={"format": "ris", "content": sample_ris},
        headers=owner_headers,
    )

    # Get work IDs from library
    lib_res = await client.get(f"/projects/{project_id}/library/items", headers=owner_headers)
    works = lib_res.json()["items"]

    return {
        "project_id": project_id,
        "owner_headers": owner_headers,
        "rev_headers": rev_headers,
        "works": works,
    }


@pytest.mark.asyncio
async def test_screening_requires_protocol(client: AsyncClient):
    """SCR-001: Submitting screening decision without protocol v1 is rejected."""
    env = await setup_review_environment(client)
    work_id = env["works"][0]["work_id"]

    res = await client.post(
        f"/projects/{env['project_id']}/screening/decisions",
        json={"work_id": work_id, "stage": "title_abstract", "verdict": "include"},
        headers=env["owner_headers"],
    )
    assert res.status_code == 400
    assert res.json()["code"] == "PROTOCOL_REQUIRED"


@pytest.mark.asyncio
async def test_protocol_creation_and_exclusion_reasons(client: AsyncClient):
    """SCR-001, SCR-002, SCR-005: Create protocol and verify seeded controlled reasons."""
    env = await setup_review_environment(client)
    pid = env["project_id"]

    # Create protocol
    p_res = await client.post(
        f"/projects/{pid}/protocols",
        json={
            "question": "What is the clinical efficacy of transformer agents?",
            "pico": {"P": "Hospitalized Patients", "I": "LLM Agents", "C": "Standard of Care", "O": "Discharge Accuracy"},
            "inclusion_criteria": "Peer-reviewed, empirical data, >= 50 patients",
            "exclusion_criteria": "Animal models, editorials",
        },
        headers=env["owner_headers"],
    )
    assert p_res.status_code == 200
    assert p_res.json()["version"] == 1

    # Verify controlled exclusion reasons
    reasons_res = await client.get(f"/projects/{pid}/exclusion-reasons", headers=env["owner_headers"])
    assert reasons_res.status_code == 200
    codes = [r["code"] for r in reasons_res.json()]
    assert "WRONG_POPULATION" in codes
    assert "EDITORIAL_OR_COMMENTARY" in codes


@pytest.mark.asyncio
async def test_exclusion_requires_reason_code(client: AsyncClient):
    """SCR-005: Exclude verdicts must supply a controlled reason code."""
    env = await setup_review_environment(client)
    pid = env["project_id"]
    work_id = env["works"][0]["work_id"]

    # Create protocol first
    await client.post(
        f"/projects/{pid}/protocols",
        json={"question": "Test Question"},
        headers=env["owner_headers"],
    )

    # Attempt exclude without reason code
    res = await client.post(
        f"/projects/{pid}/screening/decisions",
        json={"work_id": work_id, "stage": "title_abstract", "verdict": "exclude"},
        headers=env["owner_headers"],
    )
    assert res.status_code == 400
    assert res.json()["code"] == "REASON_REQUIRED"


@pytest.mark.asyncio
async def test_blind_screening_and_conflict_resolution(client: AsyncClient):
    """SCR-006, SCR-008, SCR-009: Disagreement creates conflict; closed only by owner resolution."""
    env = await setup_review_environment(client)
    pid = env["project_id"]
    work_id = env["works"][0]["work_id"]

    # Setup protocol
    await client.post(f"/projects/{pid}/protocols", json={"question": "Research Review"}, headers=env["owner_headers"])

    # 1. Owner votes INCLUDE
    await client.post(
        f"/projects/{pid}/screening/decisions",
        json={"work_id": work_id, "stage": "title_abstract", "verdict": "include"},
        headers=env["owner_headers"],
    )

    # 2. Reviewer 2 votes EXCLUDE
    await client.post(
        f"/projects/{pid}/screening/decisions",
        json={"work_id": work_id, "stage": "title_abstract", "verdict": "exclude", "reason_code": "WRONG_POPULATION"},
        headers=env["rev_headers"],
    )

    # 3. Conflict queue shows mismatch
    conflicts_res = await client.get(f"/projects/{pid}/screening/conflicts", headers=env["owner_headers"])
    assert conflicts_res.status_code == 200
    conflicts = conflicts_res.json()
    assert len(conflicts) == 1
    assert conflicts[0]["work_id"] == work_id
    assert len(conflicts[0]["decisions"]) == 2

    # 4. Reviewer 2 tries to resolve -> 403 Forbidden (SCR-009)
    forbidden_res = await client.post(
        f"/projects/{pid}/screening/resolutions",
        json={"work_id": work_id, "stage": "title_abstract", "final_verdict": "include", "rationale": "Overridden"},
        headers=env["rev_headers"],
    )
    assert forbidden_res.status_code == 403

    # 5. Owner resolves conflict to INCLUDE
    resolve_res = await client.post(
        f"/projects/{pid}/screening/resolutions",
        json={"work_id": work_id, "stage": "title_abstract", "final_verdict": "include", "rationale": "Relevant population"},
        headers=env["owner_headers"],
    )
    assert resolve_res.status_code == 200

    # 6. Conflict is now cleared
    cleared_conflicts = await client.get(f"/projects/{pid}/screening/conflicts", headers=env["owner_headers"])
    assert len(cleared_conflicts.json()) == 0


@pytest.mark.asyncio
async def test_cohens_kappa_calculation(client: AsyncClient):
    """SCR-010: Categorical Cohen's kappa computation with high agreement."""
    env = await setup_review_environment(client)
    pid = env["project_id"]
    await client.post(f"/projects/{pid}/protocols", json={"question": "Agreement Test"}, headers=env["owner_headers"])

    # Both reviewers agree on Study 1 and Study 2 (Include), disagree on Study 3
    w1, w2, w3 = env["works"][0]["work_id"], env["works"][1]["work_id"], env["works"][2]["work_id"]

    # Owner decisions
    await client.post(f"/projects/{pid}/screening/decisions", json={"work_id": w1, "stage": "title_abstract", "verdict": "include"}, headers=env["owner_headers"])
    await client.post(f"/projects/{pid}/screening/decisions", json={"work_id": w2, "stage": "title_abstract", "verdict": "exclude", "reason_code": "NON_ENGLISH"}, headers=env["owner_headers"])
    await client.post(f"/projects/{pid}/screening/decisions", json={"work_id": w3, "stage": "title_abstract", "verdict": "include"}, headers=env["owner_headers"])

    # Reviewer 2 decisions
    await client.post(f"/projects/{pid}/screening/decisions", json={"work_id": w1, "stage": "title_abstract", "verdict": "include"}, headers=env["rev_headers"])
    await client.post(f"/projects/{pid}/screening/decisions", json={"work_id": w2, "stage": "title_abstract", "verdict": "exclude", "reason_code": "NON_ENGLISH"}, headers=env["rev_headers"])
    await client.post(f"/projects/{pid}/screening/decisions", json={"work_id": w3, "stage": "title_abstract", "verdict": "exclude", "reason_code": "WRONG_OUTCOME"}, headers=env["rev_headers"])

    # Compute agreement
    agree_res = await client.get(f"/projects/{pid}/screening/agreement", headers=env["owner_headers"])
    assert agree_res.status_code == 200
    kappa_data = agree_res.json()
    assert kappa_data["total_dual_reviewed"] == 3
    # 2 agreements out of 3 -> po = 0.6667
    assert kappa_data["observed_agreement"] == 0.6667
    assert kappa_data["cohen_kappa"] is not None


@pytest.mark.asyncio
async def test_prisma_2020_flow_reconciliation(client: AsyncClient):
    """SCR-011, SCR-012, SCR-013: PRISMA 2020 flow counts with zero reconciliation discrepancies."""
    env = await setup_review_environment(client)
    pid = env["project_id"]
    await client.post(f"/projects/{pid}/protocols", json={"question": "PRISMA Test"}, headers=env["owner_headers"])

    # Exclude 1 study at TA
    w1 = env["works"][0]["work_id"]
    await client.post(
        f"/projects/{pid}/screening/decisions",
        json={"work_id": w1, "stage": "title_abstract", "verdict": "exclude", "reason_code": "WRONG_POPULATION"},
        headers=env["owner_headers"],
    )

    prisma_res = await client.get(f"/projects/{pid}/prisma", headers=env["owner_headers"])
    assert prisma_res.status_code == 200
    pdata = prisma_res.json()
    boxes = pdata["boxes"]
    assert boxes["identified"] == 3
    assert boxes["records_screened"] == 3
    assert boxes["excluded_ta"] == 1
    assert boxes["reports_sought"] == 2
    assert boxes["reports_assessed_ft"] == 2
    assert boxes["studies_included"] == 2

    # Reconciliation check must be cleanly true
    assert pdata["reconciliation"]["ok"] is True
    assert len(pdata["reconciliation"]["issues"]) == 0
