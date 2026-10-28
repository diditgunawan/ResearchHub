import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.testing import bootstrap_owner, issue_link

# SYNTHETIC TEST FIXTURE (ADR-009: Single-Owner Mode & WebAuthn / Passkeys)


@pytest.mark.asyncio
async def test_single_owner_bootstrap_and_registration_gate(client: AsyncClient, db_session: AsyncSession):
    """ADR-009: Explicit bootstrap grants system_admin; subsequent registrations rejected in single_owner mode."""
    from app.core.config import settings
    settings.ACCESS_MODE = "single_owner"

    # 1. Bootstrap owner via CLI / admin bootstrap helper (ENG-029)
    owner_email = "founding.scholar@institute.edu"
    await bootstrap_owner(db_session, owner_email)
    token = await issue_link(db_session, owner_email)

    sess_res = await client.post("/auth/session", json={"token": token})
    assert sess_res.status_code == 200
    owner_data = sess_res.json()["user"]
    assert owner_data["email"] == owner_email
    assert owner_data["is_system_admin"] is True

    # 2. Unknown user tries to sign up without invitation in single-owner mode
    intruder_res = await client.post("/auth/magic-link", json={"email": "uninvited@external.org"})
    assert intruder_res.status_code == 403
    assert intruder_res.json()["code"] == "REGISTRATION_CLOSED"


@pytest.mark.asyncio
async def test_passkey_enrollment_and_login_flow(client: AsyncClient, db_session: AsyncSession):
    """ADR-009 / Blueprint 17: FIDO2 Passkey enrollment and login verification ceremony."""
    email = "passkey.user@lab.org"
    token = await issue_link(db_session, email)
    sess_res = await client.post("/auth/session", json={"token": token})
    session_token = sess_res.json()["session_token"]
    auth_header = {"Authorization": f"Bearer {session_token}"}

    # 1. Request passkey registration challenge
    reg_chal_res = await client.post("/auth/passkey/register-challenge", headers=auth_header)
    assert reg_chal_res.status_code == 200
    reg_chal_data = reg_chal_res.json()
    assert "challenge" in reg_chal_data
    assert reg_chal_data["rp"]["name"] == "ResearchHub"

    # 2. Verify and enroll passkey
    cred_id = "cred-pubkey-fido2-unique-uuid-987"
    enroll_res = await client.post(
        "/auth/passkey/register-verify",
        json={
            "credential_id": cred_id,
            "public_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0...",
            "label": "MacBook TouchID",
        },
        headers=auth_header,
    )
    assert enroll_res.status_code == 200
    assert enroll_res.json()["credential_id"] == cred_id

    # 3. Log out (revokes session)
    logout_res = await client.post("/auth/logout", headers=auth_header)
    assert logout_res.status_code == 200

    # Old session is now rejected
    me_revoked = await client.get("/me", headers=auth_header)
    assert me_revoked.status_code == 401

    # 4. Request passkey login challenge
    login_chal_res = await client.post("/auth/passkey/login-challenge")
    assert login_chal_res.status_code == 200
    assert "challenge" in login_chal_res.json()

    # 5. Authenticate with enrolled passkey (signature required per P12)
    login_verify_res = await client.post(
        "/auth/passkey/login-verify",
        json={"credential_id": cred_id, "signature": "mock-fido2-signature"},
    )
    assert login_verify_res.status_code == 200
    new_sess = login_verify_res.json()
    assert new_sess["user"]["email"] == email
    new_session_token = new_sess["session_token"]

    # 6. Verify authenticated access with passkey session
    me_passkey = await client.get("/me", headers={"Authorization": f"Bearer {new_session_token}"})
    assert me_passkey.status_code == 200
    assert me_passkey.json()["email"] == email


@pytest.mark.asyncio
async def test_admin_settings_access_control(client: AsyncClient, db_session: AsyncSession):
    """Blueprint 17: Admin settings endpoints are strictly guarded by is_system_admin."""
    from app.core.config import settings
    settings.ACCESS_MODE = "single_owner"

    # 1. First user is owner / system admin bootstrapped explicitly
    admin_email = "admin.owner@hub.org"
    await bootstrap_owner(db_session, admin_email)
    admin_token = await issue_link(db_session, admin_email)
    admin_sess = await client.post("/auth/session", json={"token": admin_token})
    admin_auth = {"Authorization": f"Bearer {admin_sess.json()['session_token']}"}

    # Admin reads settings
    settings_res = await client.get("/admin/settings", headers=admin_auth)
    assert settings_res.status_code == 200
    assert settings_res.json()["access_mode"] == "single_owner"

    # Admin updates settings to invite_only
    update_res = await client.post(
        "/admin/settings",
        json={"registration": "invite_only"},
        headers=admin_auth,
    )
    assert update_res.status_code == 200
    assert update_res.json()["registration"] == "invite_only"
