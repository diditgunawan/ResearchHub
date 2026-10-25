import pytest
from httpx import AsyncClient

# SYNTHETIC TEST FIXTURE (ENG-001, ENG-006, ENG-010)

@pytest.mark.asyncio
async def test_healthz_returns_200_and_request_id(client: AsyncClient):
    """ENG-001 & ENG-006: Healthz probe must return 200 OK and X-Request-ID header."""
    response = await client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "researchforge-api"
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"].startswith("rf-")


@pytest.mark.asyncio
async def test_readyz_returns_200_database_status(client: AsyncClient):
    """ENG-001: Readiness probe verifies database availability."""
    response = await client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_custom_request_id_propagation(client: AsyncClient):
    """ENG-010: Client-provided X-Request-ID header must be preserved in response."""
    custom_id = "client-trace-12345"
    response = await client.get("/healthz", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id
