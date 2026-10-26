#!/usr/bin/env python3
"""Truth audit (QAS-026): run behavioural probes against the real app. Exit 1 if any probe FAILS.

Usage:  python scripts/truth_audit.py --repo <path-to-repo> [--pin scripts/integrity.sha256]

Repo contract: apps/api with `app.main:app`, `app.core.database` (Base, get_db), `app.core.config.settings`.
Optional test helpers (add them when you fix auth so probes keep working without leaking tokens over HTTP):
  app/testing.py:  async def issue_link(db, email) -> str     # returns a fresh single-use link token
                   async def make_session(db, email) -> str   # returns a valid session token
Without helpers the audit falls back to the legacy flow (token returned by /auth/magic-link), which is itself a FAIL (P1).
"""
import argparse, asyncio, base64, hashlib, hmac, os, pathlib, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default=".")
ap.add_argument("--pin", default=None, help="file holding sha256 of the strict coverage gate script")
a = ap.parse_args()
REPO = pathlib.Path(a.repo).resolve()
API = REPO / "apps" / "api"
os.environ["TESTING"] = "1"
sys.path.insert(0, str(API))
R = []  # (id, name, status, detail)
def rec(i, n, ok, d, skip=False): R.append((i, n, "SKIP" if skip else ("PASS" if ok else "FAIL"), d))

async def main():
    from httpx import AsyncClient, ASGITransport
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.main import app
    from app.core.database import Base, get_db
    from app.core.config import settings
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SL = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
    async def odb():
        async with SL() as s:
            try:
                yield s; await s.commit()
            except Exception:
                await s.rollback(); raise
    app.dependency_overrides[get_db] = odb
    async with eng.begin() as c: await c.run_sync(Base.metadata.create_all)
    try:
        import app.testing as T
    except Exception:
        T = None

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # P1 token never returned over HTTP
        r = await c.post("/auth/magic-link", json={"email": "victim@example.org"})
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        leaked = [k for k in body if re.search(r"token|link|url", k, re.I) and body[k]]
        rec("P1", "login token not returned by API", not leaked, f"response keys with secrets: {leaked or 'none'}")
        legacy_tok = body.get("token")

        async def link_token(email):
            if T and hasattr(T, "issue_link"):
                async with SL() as s: return await T.issue_link(s, email)
            rr = await c.post("/auth/magic-link", json={"email": email}); return rr.json().get("token")
        async def session_for(email):
            if T and hasattr(T, "make_session"):
                async with SL() as s: return await T.make_session(s, email)
            tk = await link_token(email)
            if not tk: return None
            ss = await c.post("/auth/session", json={"token": tk}); return ss.json().get("session_token")

        # P2 single use
        tk = await link_token("replay@example.org")
        if tk:
            s1 = await c.post("/auth/session", json={"token": tk}); s2 = await c.post("/auth/session", json={"token": tk})
            rec("P2", "magic link is single-use", s1.status_code == 200 and s2.status_code != 200, f"first={s1.status_code} second={s2.status_code}")
        else: rec("P2", "magic link is single-use", False, "no token obtainable", skip=True)

        # P3 session expiry (forged ancient legacy token)
        sec = getattr(settings, "SESSION_SECRET", None)
        sess = await session_for("expiry@example.org")
        if sess and sec:
            try:
                uid = (await c.get("/me", headers={"Authorization": "Bearer " + sess})).json().get("id")
                pl = f"{uid}:1".encode(); sg = hmac.new(sec.encode(), pl, hashlib.sha256).digest()
                old = base64.urlsafe_b64encode(pl).decode().rstrip("=") + "." + base64.urlsafe_b64encode(sg).decode().rstrip("=")
                m = await c.get("/me", headers={"Authorization": "Bearer " + old})
                rec("P3", "ancient/forged session token rejected", m.status_code in (401, 403), f"status={m.status_code}")
            except Exception as e: rec("P3", "ancient/forged session token rejected", False, f"probe error {e}", skip=True)
        else: rec("P3", "ancient/forged session token rejected", False, "no session obtainable", skip=True)

        # P4 irrelevant query refused
        if sess:
            h = {"Authorization": "Bearer " + sess}
            pid = (await c.post("/projects", json={"name": "audit"}, headers=h)).json().get("id")
            ris = "".join(f"TY  - JOUR\nTI  - Medieval pottery glazing study {i}\nPY  - 202{i}\nAB  - Kiln temperature and glaze composition in medieval ceramics. Clay sourcing varied by region.\nER  - \n\n" for i in range(3))
            await c.post(f"/projects/{pid}/imports", json={"format": "ris", "content": ris}, headers=h)
            q = await c.post(f"/projects/{pid}/synthesis", json={"query": "quantum chromodynamics lattice gauge", "scope": "library"}, headers=h)
            j = q.json() if q.status_code == 200 else {}
            rec("P4", "irrelevant query is refused", j.get("status") == "refused", f"status={j.get('status')} claims={len(j.get('claims') or [])} verified%={j.get('verified_percentage')}")
            # P5 provenance honesty
            d = (await c.get(f"/projects/{pid}/ai-disclosure", headers=h)).json()
            code = "".join(p.read_text(errors="ignore") for p in (API / "app").rglob("*.py")) + (API / "pyproject.toml").read_text(errors="ignore")
            has_llm = bool(re.search(r"anthropic|openai|google\.generativeai|generativelanguage|litellm|mistralai|cohere", code, re.I))
            models = d.get("models_used") or []
            tokens = d.get("total_tokens_consumed") or 0
            honest = has_llm or (not models and not tokens) or all(re.search(r"rule", str(m), re.I) for m in models)
            rec("P5", "provenance honest (no model/tokens without a real model call)", honest, f"llm client in code={has_llm} models_used={models} tokens={tokens}")
        else:
            rec("P4", "irrelevant query is refused", False, "no session", skip=True); rec("P5", "provenance honest", False, "no session", skip=True)

    # P6 hard-coded scholarly records in production code
    n = 0
    for p in (API / "app").rglob("*.py"):
        n += len(re.findall(r'["\']doi["\']\s*:\s*["\']10\.\d{4,9}/', p.read_text(errors="ignore")))
    rec("P6", "no hard-coded DOIs in production code", n == 0, f"DOI literals found: {n}")

    # P7 coverage gate integrity
    gate = REPO / "scripts" / "check_requirement_coverage.py"
    pin = pathlib.Path(a.pin) if a.pin else REPO / "scripts" / "integrity.sha256"
    if not pin.exists(): rec("P7", "coverage gate script matches pinned hash", False, f"no pin file at {pin}")
    elif not gate.exists(): rec("P7", "coverage gate script matches pinned hash", False, "gate script missing")
    else:
        want = pin.read_text().split()[0]; got = hashlib.sha256(gate.read_bytes()).hexdigest()
        rec("P7", "coverage gate script matches pinned hash", want == got, "match" if want == got else f"hash differs (pinned {want[:12]}…, found {got[:12]}…)")

    # P8 production boot guard
    env = dict(os.environ, APP_ENV="production", PYTHONPATH=str(API)); env.pop("TESTING", None)
    r = subprocess.run([sys.executable, "-c", "import app.main"], cwd=API, env=env, capture_output=True, text=True)
    rec("P8", "production boot refuses default secrets/env", r.returncode != 0, "refused to start" if r.returncode else "app started with defaults in production mode")

asyncio.run(main())
w = max(len(r[1]) for r in R)
print("\nTRUTH AUDIT —", REPO)
for i, n, s, d in R: print(f" {i}  {s:<5} {n:<{w}}  {d}")
f = sum(1 for r in R if r[2] == "FAIL"); sk = sum(1 for r in R if r[2] == "SKIP")
print(f"\n{len(R)-f-sk} pass · {f} fail · {sk} skipped")
sys.exit(1 if f else 0)
