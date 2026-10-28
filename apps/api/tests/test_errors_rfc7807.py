import pytest
from httpx import AsyncClient

# SYNTHETIC TEST FIXTURE (ENG-006: RFC 7807 Problem Details)

@pytest.mark.asyncio
async def test_unauthorized_returns_rfc7807(client: AsyncClient):
    """ENG-006: Unauthorized request must return RFC 7807 problem details with code and request_id."""
    response = await client.get("/me")
    assert response.status_code == 401
    assert "X-Request-ID" in response.headers
    
    data = response.json()
    assert data["type"] == "about:blank"
    assert data["status"] == 401
    assert data["title"] == "Unauthorized"
    assert data["code"] == "AUTH_REQUIRED"
    assert data["request_id"] == response.headers["X-Request-ID"]
    assert "detail" in data


@pytest.mark.asyncio
async def test_project_not_found_returns_rfc7807(client: AsyncClient):
    """ENG-006: Nonexistent resource query returns RFC 7807 problem details."""
    # Authenticate first
    from tests.conftest import get_test_link_token
    token = await get_test_link_token("tester@example.org")
    sess_res = await client.post("/auth/session", json={"token": token})
    session_token = sess_res.json()["session_token"]
    
    headers = {"Authorization": f"Bearer {session_token}"}
    response = await client.get("/projects/non-existent-uuid-9999", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == 404
    assert data["code"] == "PROJECT_NOT_FOUND"
    assert data["title"] == "Not Found"
    assert data["request_id"] == response.headers["X-Request-ID"]
