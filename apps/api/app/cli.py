"""
ResearchHub Administrative & Operational CLI (Blueprint 17 & ENG-029)
=====================================================================
Usage:
  python -m app.cli bootstrap-owner --email owner@example.org
"""

import asyncio
import sys
import argparse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import async_session_factory
from app.identity.models import User, InstanceSetting
from app.identity.service import IdentityService


async def bootstrap_owner(email: str):
    clean_email = email.strip().lower()
    async with async_session_factory() as db:
        user = await IdentityService.get_user_by_email(db, clean_email)
        if user:
            user.is_system_admin = True
            print(f"[CLI] Existing user {clean_email} promoted to system administrator.")
        else:
            user = User(email=clean_email, is_system_admin=True)
            db.add(user)
            print(f"[CLI] Bootstrapped new system administrator: {clean_email}")

        # Ensure instance setting registration is closed in single-owner mode
        inst_stmt = select(InstanceSetting).where(InstanceSetting.key == "access_config")
        inst = (await db.execute(inst_stmt)).scalar_one_or_none()
        if not inst:
            inst = InstanceSetting(
                key="access_config",
                value={"access_mode": "single_owner", "registration": "closed"},
            )
            db.add(inst)
        else:
            val = dict(inst.value or {})
            val["access_mode"] = "single_owner"
            val["registration"] = "closed"
            inst.value = val

        await db.commit()
        print("[CLI] Instance settings configured: ACCESS_MODE=single_owner, REGISTRATION=closed.")


def main():
    parser = argparse.ArgumentParser(description="ResearchHub Administrative CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    owner_parser = subparsers.add_parser("bootstrap-owner", help="Bootstrap instance owner as system administrator")
    owner_parser.add_argument("--email", required=True, help="Administrator email address")

    args = parser.parse_args()
    if args.command == "bootstrap-owner":
        asyncio.run(bootstrap_owner(args.email))


if __name__ == "__main__":
    main()
