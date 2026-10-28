import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.testing import issue_link

# SYNTHETIC TEST FIXTURE (ENG-007: Single-use Magic Link & Session Management)

@pytest.mark.asyncio
async def test_magic_link_flow_and_session_cookie(client: AsyncClient, db_session: AsyncSession):
    """ENG-007: Full passwordless auth flow via magic link and secure session cookie."""
    email = "researcher.phd@university.edu"
    
    # 1. Request magic link (HTTP response never leaks token)
    link_res = await client.post("/auth/magic-link", json={"email": email})
    assert link_res.status_code == 200
    assert link_res.json().get("token") is None

    # Obtain single-use link token via testing helper (ENG-022 / P1 / P9)
    token = await issue_link(db_session, email)
    assert token is not None

    # 2. Redeem magic link token
    sess_res = await client.post("/auth/session", json={"token": token})
    assert sess_res.status_code == 200
    sess_data = sess_res.json()
    assert sess_data["user"]["email"] == email
    session_token = sess_data["session_token"]

    # Verify session cookie was set with HttpOnly
    assert "set-cookie" in sess_res.headers
    assert "rf_session" in sess_res.headers["set-cookie"]
    assert "HttpOnly" in sess_res.headers["set-cookie"]

    # 3. Access /me using Bearer token
    me_res = await client.get("/me", headers={"Authorization": f"Bearer {session_token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # 4. Access /me using session cookie
    me_cookie_res = await client.get("/me", cookies={"rf_session": session_token})
    assert me_cookie_res.status_code == 200
    assert me_cookie_res.json()["email"] == email


@pytest.mark.asyncio
async def test_invalid_magic_link_token_rejected(client: AsyncClient):
    """ENG-007: Malformed or forged magic link tokens must be rejected with 401."""
    response = await client.post("/auth/session", json={"token": "tampered.token.signature"})
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_MAGIC_LINK"
