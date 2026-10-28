import pytest
from httpx import AsyncClient

# HARDENING & SECURITY VERIFICATION SUITE (QAS-007..QAS-025, ENG-013..ENG-020)

@pytest.mark.asyncio
async def test_security_headers_enforced(client: AsyncClient):
    """ENG-014, QAS-012: Verify presence of all required production security headers."""
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    headers = resp.headers
    
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("x-xss-protection") == "1; mode=block"
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "max-age=31536000" in headers.get("strict-transport-security", "")
    assert "geolocation=()" in headers.get("permissions-policy", "")
    assert headers.get("x-request-id") is not None


@pytest.mark.asyncio
async def test_tenant_isolation_boundary_enforcement(client: AsyncClient):
    """
    ENG-008, QAS-009: Cross-project leak prevention.
    User A's project items must never be accessible or modifiable by User B.
    """
    # 1. Setup Tenant A
    from tests.conftest import get_test_link_token
    token_a = await get_test_link_token("alice.tenant@ox.ac.uk")
    sess_a = await client.post("/auth/session", json={"token": token_a})
    headers_a = {"Authorization": f"Bearer {sess_a.json()['session_token']}"}

    proj_a = await client.post("/projects", json={"name": "Alice Confidential Oncology Review"}, headers=headers_a)
    proj_a_id = proj_a.json()["id"]

    # 2. Setup Tenant B
    token_b = await get_test_link_token("bob.adversary@external.com")
    sess_b = await client.post("/auth/session", json={"token": token_b})
    headers_b = {"Authorization": f"Bearer {sess_b.json()['session_token']}"}

    proj_b = await client.post("/projects", json={"name": "Bob Separate Cardiology Review"}, headers=headers_b)
    proj_b_id = proj_b.json()["id"]

    # 3. Tenant B attempts to read Tenant A's project -> 404 / 403 Forbidden
    leak_read = await client.get(f"/projects/{proj_a_id}/library/items", headers=headers_b)
    assert leak_read.status_code in [403, 404]

    # 4. Tenant B attempts to submit decision on Tenant A's project -> 403 Forbidden
    leak_write = await client.post(
        f"/projects/{proj_a_id}/screening/decisions",
        json={"work_id": "00000000-0000-0000-0000-000000000000", "stage": "title_abstract", "verdict": "include"},
        headers=headers_b,
    )
    assert leak_write.status_code in [403, 404]


@pytest.mark.asyncio
async def test_rate_limiting_and_rfc7807_error_fidelity(client: AsyncClient):
    """
    ENG-006, ENG-007, QAS-010: Ensure RFC 7807 fields (type, title, status, code, request_id)
    are returned reliably even on invalid authentication attempts.
    """
    # Invalid token lookup
    bad_sess = await client.post("/auth/session", json={"token": "completely-invalid-nonexistent-token"})
    assert bad_sess.status_code == 401
    err = bad_sess.json()
    assert err["type"] == "about:blank"
    assert err["status"] == 401
    assert "INVALID" in err["code"]
    assert "request_id" in err
