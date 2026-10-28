import pytest
from httpx import AsyncClient

# SYNTHETIC TEST FIXTURE (ENG-008: Role-Based Access Control Matrix)

async def create_authenticated_user(client: AsyncClient, email: str) -> dict:
    from tests.conftest import get_test_link_token
    token = await get_test_link_token(email)
    sess_res = await client.post("/auth/session", json={"token": token})
    session_token = sess_res.json()["session_token"]
    user = sess_res.json()["user"]
    return {
        "user": user,
        "headers": {"Authorization": f"Bearer {session_token}"},
    }


@pytest.mark.asyncio
async def test_project_creation_and_owner_assignment(client: AsyncClient):
    """ENG-008: Project creator automatically acquires 'owner' role."""
    lead = await create_authenticated_user(client, "lead.author@lab.org")
    
    res = await client.post(
        "/projects",
        json={"name": "Systematic Review 2026", "description": "AI in Medicine"},
        headers=lead["headers"],
    )
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Systematic Review 2026"
    assert data["role"] == "owner"
    assert data["owner_id"] == lead["user"]["id"]


@pytest.mark.asyncio
async def test_owner_can_add_reviewer_member(client: AsyncClient):
    """ENG-008: Project owner can invite secondary reviewer with role 'reviewer'."""
    owner = await create_authenticated_user(client, "pi@university.edu")
    
    # Create project
    proj_res = await client.post(
        "/projects",
        json={"name": "Cancer Biomarkers Review"},
        headers=owner["headers"],
    )
    project_id = proj_res.json()["id"]

    # Add reviewer
    member_res = await client.post(
        f"/projects/{project_id}/members",
        json={"email": "reviewer2@university.edu", "role": "reviewer"},
        headers=owner["headers"],
    )
    assert member_res.status_code == 200
    member_data = member_res.json()
    assert member_data["email"] == "reviewer2@university.edu"
    assert member_data["role"] == "reviewer"

    # Verify membership list
    list_res = await client.get(f"/projects/{project_id}/members", headers=owner["headers"])
    assert list_res.status_code == 200
    emails = [m["email"] for m in list_res.json()]
    assert "pi@university.edu" in emails
    assert "reviewer2@university.edu" in emails


@pytest.mark.asyncio
async def test_reviewer_cannot_add_members_forbidden(client: AsyncClient):
    """ENG-008: Reviewer cannot invite other members (Forbidden 403)."""
    owner = await create_authenticated_user(client, "lead@lab.org")
    reviewer = await create_authenticated_user(client, "screener@lab.org")

    # Owner creates project
    proj_res = await client.post("/projects", json={"name": "Genomics Study"}, headers=owner["headers"])
    project_id = proj_res.json()["id"]

    # Owner adds reviewer
    await client.post(
        f"/projects/{project_id}/members",
        json={"email": reviewer["user"]["email"], "role": "reviewer"},
        headers=owner["headers"],
    )

    # Reviewer attempts to add another member -> 403 Forbidden
    forbidden_res = await client.post(
        f"/projects/{project_id}/members",
        json={"email": "intruder@external.org", "role": "reviewer"},
        headers=reviewer["headers"],
    )
    assert forbidden_res.status_code == 403
    assert forbidden_res.json()["code"] == "INSUFFICIENT_PROJECT_ROLE"


@pytest.mark.asyncio
async def test_non_member_cannot_access_project_idor_prevention(client: AsyncClient):
    """ENG-008: Non-member cannot view or access another tenant's project."""
    user1 = await create_authenticated_user(client, "user1@domain.com")
    user2 = await create_authenticated_user(client, "user2@domain.com")

    # User 1 creates project
    proj_res = await client.post("/projects", json={"name": "Private Project"}, headers=user1["headers"])
    project_id = proj_res.json()["id"]

    # User 2 attempts to view -> 404 Not Found (prevent leaking project existence)
    denied_res = await client.get(f"/projects/{project_id}", headers=user2["headers"])
    assert denied_res.status_code == 404
    assert denied_res.json()["code"] == "PROJECT_NOT_FOUND"
