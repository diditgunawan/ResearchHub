# 17 — Access Model: Single-Owner Mode with Every Flow Kept (v0.4)

## 1. Principle
Do not delete multi-user flows. Run the deployment with **one account that is both administrator and user**. Every invitation, role, quota, audit, and admin flow stays implemented and tested; registration is simply closed. When the platform is ready for many users, flip a setting. No rewrite.

## 2. Modes
| Setting | `single_owner` (now) | `multi_user` (later) |
|---|---|---|
| `ACCESS_MODE` | `single_owner` | `multi_user` |
| Registration | Closed; only the bootstrapped owner exists | `invite_only` or `open` (admin setting) |
| Owner account | System admin **and** normal user (two hats, one login) | Same, plus other users |
| Invitation and member flows | Implemented, callable by admin, tested; invite email sent only if admin enables | Enabled |
| Quotas and budgets | Enforced (cost cap applies to owner too, adjustable) | Enforced per user and plan |
| Admin console | Present; shows the single account and instance settings | Full user management |
| Tests | Run the suite under both modes (QAS) | Same |

## 3. Roles and capabilities
| Capability | system_admin | project owner | reviewer | viewer |
|---|---|---|---|---|
| Instance settings, users, invitations, quotas, source keys, model budgets | ✔ | – | – | – |
| View audit log of all admin actions | ✔ | – | – | – |
| Create/delete own projects, manage members | ✔ (as owner) | ✔ | – | – |
| Make screening decisions | ✔ (as member) | ✔ | ✔ | – |
| Read project data | ✔ (as member) | ✔ | ✔ | ✔ |
`system_admin` is an instance-level flag on the user, **separate** from project roles. The owner holds both. Admin actions are never implied by project ownership.

## 4. Bootstrap and lifecycle
1. First boot with no users: the app refuses logins and prints a one-time setup instruction. Operator runs `python -m app.cli bootstrap-owner --email <owner>`.
2. The command creates the owner (`is_system_admin = true`), a personal project, 10 recovery codes (shown once, stored hashed), and `instance_settings.registration = closed`.
3. Owner signs in with email link, registers a passkey, and downloads recovery codes.
4. Ownership transfer: admin creates a second admin, then demotes self (needs step-up).
5. Recovery: recovery code → forces new passkey and invalidates old sessions. Break-glass: `bootstrap-owner --reset-credentials` on the host, logged.
6. Moving to many users: set `ACCESS_MODE=multi_user`, set registration policy, configure email delivery and quotas, run the staging load and security gates (QAS-028/029).

## 5. Authentication
| Method | Use | Rules |
|---|---|---|
| Passkey (WebAuthn) | Primary | Resident or non-resident keys; sign-count checks; ≥ 2 registered recommended |
| Email magic link | Fallback and first login | Single-use, 15 min, only sent to a registered email, token hashed at rest, never returned by any API |
| Recovery codes | Account recovery | One-time, hashed, 10 issued, regenerate on use of 3 |
| Network gate | Optional extra | Identity-aware proxy (e.g., Cloudflare Access or private mesh VPN) in front of `/admin/*` |
| Dev login | Local only | Allowed when `APP_ENV=local` and bound to 127.0.0.1; prints the link to the server console; **never** returns a token in an HTTP response; disabled by the production boot guard |

## 6. Sessions
Server-side session table; random 256-bit id, hash stored; idle timeout 12 h, absolute 7 d; rotate on login, privilege change, and step-up; revoke on logout, password-less credential change, and admin action; cookie `Secure; HttpOnly; SameSite=Lax`; CSRF token for state-changing requests; list and revoke sessions in Security settings.

## 7. Admin console (scope)
Instance settings (mode, registration policy, allowed email domains) · users and roles · invitations · quotas and model/OpenAlex budgets · source and model keys (write-only fields) · active sessions · audit log viewer with export · retention and deletion jobs · health and queue status. In `single_owner` mode these screens work on the single account and are covered by tests.

## 8. Step-up and audit
Admin actions require step-up (passkey or fresh link) within 10 minutes. Every admin action writes `audit_events` with actor, `actor_is_admin`, entity, before/after metadata, IP, request id. Audit rows are append-only.

## 9. Test matrix (QAS)
| Test | single_owner | multi_user |
|---|---|---|
| Registration closed / invite flow | ✔ closed returns 403; invite endpoint admin-only | ✔ |
| Token never in API response | ✔ | ✔ |
| Magic link replay and expiry | ✔ | ✔ |
| Session idle/absolute expiry, logout, revocation | ✔ | ✔ |
| Step-up required for admin actions | ✔ | ✔ |
| Role matrix (admin, owner, reviewer, viewer) | ✔ | ✔ |
| Production boot guard | ✔ | ✔ |

## 10. Audit findings this model fixes
Anyone-can-login (token returned, default env local) → token never returned, dev login console-only. Replayable links → single-use. Immortal sessions → server-side expiry and revocation. Default secrets → boot guard (ENG-025).
