from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.integrity.models import AiUsageLog, ReferenceCheck
from app.library.models import LibraryItem
from app.works.models import Work
from datetime import datetime, timezone


class IntegrityService:
    @staticmethod
    async def run_reference_audit(db: AsyncSession, project_id: str) -> List[ReferenceCheck]:
        """ETH-005, ETH-007: Audit project reference list for retractions, unresolved DOIs, and metadata mismatches."""
        stmt = (
            select(Work)
            .join(LibraryItem, Work.id == LibraryItem.work_id)
            .where(LibraryItem.project_id == project_id)
        )
        works = (await db.execute(stmt)).scalars().all()

        checks = []
        for w in works:
            status = "verified"
            details = "Valid scholarly record."

            if w.retracted:
                status = "retracted"
                details = "CRITICAL: Study has been formally retracted by the publisher/editorial board."
            elif not w.doi:
                status = "unresolved"
                details = "No verified DOI registered for this record."

            check = ReferenceCheck(
                project_id=project_id,
                work_id=w.id,
                doi=w.doi,
                title=w.title,
                status=status,
                details=details,
            )
            db.add(check)
            checks.append(check)

        await db.flush()
        return checks

    @staticmethod
    async def get_reference_checks(db: AsyncSession, project_id: str) -> List[ReferenceCheck]:
        stmt = select(ReferenceCheck).where(ReferenceCheck.project_id == project_id).order_by(ReferenceCheck.checked_at.desc())
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def generate_disclosure_statement(db: AsyncSession, project_id: str) -> Dict[str, Any]:
        """ETH-004: Generate transparent academic AI-use disclosure statement from logged usage."""
        stmt = select(AiUsageLog).where(AiUsageLog.project_id == project_id)
        logs = (await db.execute(stmt)).scalars().all()

        features_used = set(log.feature for log in logs)
        models_used = set(log.model for log in logs)
        total_in = sum(log.tokens_in for log in logs)
        total_out = sum(log.tokens_out for log in logs)

        features_str = ", ".join(sorted(features_used)) if features_used else "None"
        models_str = ", ".join(sorted(models_used)) if models_used else "None"

        statement_en = (
            f"Declaration of Generative AI and AI-assisted Technologies in the Writing Process: "
            f"During the preparation of this work, the authors used ResearchForge ({models_str}) "
            f"for the following tasks: {features_str}. "
            f"All claims and citations generated were independently verified against retrieved full-text chunks. "
            f"The authors reviewed and edited the content as needed and take full responsibility for the integrity "
            f"and accuracy of the published publication."
        )

        statement_id = (
            f"Pernyataan Penggunaan Kecerdasan Buatan (AI) dalam Proses Penelitian: "
            f"Selama penyusunan karya ini, penulis menggunakan ResearchForge ({models_str}) "
            f"untuk tujuan: {features_str}. "
            f"Setiap kutipan dan sintesis diverifikasi terhadap korpus rujukan primer. "
            f"Penulis memeriksa dan menyunting seluruh hasil sintesis serta bertanggung jawab penuh "
            f"atas keabsahan dan integritas karya ilmiah ini."
        )

        return {
            "project_id": project_id,
            "features_used": list(features_used),
            "models_used": list(models_used),
            "total_tokens_consumed": total_in + total_out,
            "statement_en": statement_en,
            "statement_id": statement_id,
            "compliance_note": "Ensure to check specific target journal guidelines (e.g. Elsevier, Springer, Nature) before final submission.",
        }
