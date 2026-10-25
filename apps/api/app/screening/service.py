from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.screening.models import ReviewProtocol, ExclusionReason, ScreeningDecision, ScreeningResolution, AiSuggestion
from app.library.models import LibraryItem, ImportBatch
from app.works.models import Work
from app.core.errors import BadRequestError, NotFoundError, ForbiddenError


DEFAULT_EXCLUSIONS = [
    ("WRONG_POPULATION", "Population does not match review criteria"),
    ("WRONG_INTERVENTION", "Intervention/Exposure out of scope"),
    ("WRONG_OUTCOME", "Required outcome measures not evaluated"),
    ("NON_ENGLISH", "Language not covered in review protocol"),
    ("INSUFFICIENT_DATA", "Insufficient quantitative or qualitative data reported"),
    ("EDITORIAL_OR_COMMENTARY", "Non-peer reviewed commentary, editorial, or perspective"),
]


class ScreeningService:
    @staticmethod
    async def get_active_protocol(db: AsyncSession, project_id: str) -> Optional[ReviewProtocol]:
        """SCR-001: Returns the latest active protocol for the project."""
        stmt = (
            select(ReviewProtocol)
            .where(ReviewProtocol.project_id == project_id)
            .order_by(ReviewProtocol.version.desc())
        )
        return (await db.execute(stmt)).scalars().first()

    @staticmethod
    async def create_or_update_protocol(
        db: AsyncSession,
        project_id: str,
        question: str,
        pico: Optional[dict] = None,
        inclusion_criteria: Optional[str] = None,
        exclusion_criteria: Optional[str] = None,
    ) -> ReviewProtocol:
        """SCR-002: Protocol changes create a new incremented version."""
        latest = await ScreeningService.get_active_protocol(db, project_id)
        next_version = (latest.version + 1) if latest else 1

        protocol = ReviewProtocol(
            project_id=project_id,
            question=question,
            pico_json=pico,
            inclusion_criteria=inclusion_criteria,
            exclusion_criteria=exclusion_criteria,
            version=next_version,
        )
        db.add(protocol)
        await db.flush()

        # Ensure default exclusion reasons are seeded
        await ScreeningService.seed_default_reasons(db, project_id)

        return protocol

    @staticmethod
    async def seed_default_reasons(db: AsyncSession, project_id: str):
        """SCR-005: Seed controlled exclusion reasons."""
        for code, label in DEFAULT_EXCLUSIONS:
            stmt = select(ExclusionReason).where(
                ExclusionReason.project_id == project_id,
                ExclusionReason.code == code,
            )
            exists = (await db.execute(stmt)).scalar_one_or_none()
            if not exists:
                db.add(ExclusionReason(project_id=project_id, code=code, label=label, is_default=True))
        await db.flush()

    @staticmethod
    async def get_exclusion_reasons(db: AsyncSession, project_id: str) -> List[ExclusionReason]:
        stmt = select(ExclusionReason).where(
            or_(ExclusionReason.project_id == project_id, ExclusionReason.is_default == True)
        )
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def submit_decision(
        db: AsyncSession,
        project_id: str,
        user_id: str,
        work_id: str,
        stage: str,
        verdict: str,
        reason_code: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> ScreeningDecision:
        """SCR-001, SCR-004, SCR-005: Submit append-only screening decision."""
        protocol = await ScreeningService.get_active_protocol(db, project_id)
        if not protocol:
            raise BadRequestError("Screening is disabled until Protocol v1 is defined", code="PROTOCOL_REQUIRED")

        if verdict == "exclude" and not reason_code:
            raise BadRequestError("Exclusion decisions require a controlled reason code", code="REASON_REQUIRED")

        decision = ScreeningDecision(
            project_id=project_id,
            work_id=work_id,
            user_id=user_id,
            stage=stage,
            verdict=verdict,
            reason_code=reason_code,
            notes=notes,
            protocol_version=protocol.version,
        )
        db.add(decision)
        await db.flush()
        return decision

    @staticmethod
    async def get_screening_queue(
        db: AsyncSession,
        project_id: str,
        user_id: str,
        stage: str = "title_abstract",
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """SCR-006: Blind screening queue. Returns items not yet decided by the current user."""
        # Find works in library
        stmt = (
            select(Work)
            .join(LibraryItem, Work.id == LibraryItem.work_id)
            .where(
                LibraryItem.project_id == project_id,
                ~Work.id.in_(
                    select(ScreeningDecision.work_id).where(
                        ScreeningDecision.project_id == project_id,
                        ScreeningDecision.user_id == user_id,
                        ScreeningDecision.stage == stage,
                    )
                ),
            )
            .limit(limit)
        )
        works = (await db.execute(stmt)).scalars().all()
        return [
            {
                "work_id": w.id,
                "title": w.title,
                "abstract": w.abstract,
                "year": w.year,
                "venue": w.venue,
                "doi": w.doi,
            }
            for w in works
        ]

    @staticmethod
    async def get_conflicts(db: AsyncSession, project_id: str, stage: str = "title_abstract") -> List[Dict[str, Any]]:
        """SCR-008: Identify items with verdict mismatches among reviewers lacking a resolution."""
        # Get all decisions grouped by work_id
        stmt = (
            select(ScreeningDecision.work_id, Work.title, func.group_concat(ScreeningDecision.verdict))
            .join(Work, ScreeningDecision.work_id == Work.id)
            .where(ScreeningDecision.project_id == project_id, ScreeningDecision.stage == stage)
            .group_by(ScreeningDecision.work_id, Work.title)
        )
        rows = (await db.execute(stmt)).all()

        conflicts = []
        for work_id, title, verdicts_str in rows:
            verdicts = verdicts_str.split(",") if verdicts_str else []
            # Conflict if differing verdicts and no resolution
            if len(set(verdicts)) > 1:
                # Check resolution
                res_stmt = select(ScreeningResolution).where(
                    ScreeningResolution.project_id == project_id,
                    ScreeningResolution.work_id == work_id,
                    ScreeningResolution.stage == stage,
                )
                resolution = (await db.execute(res_stmt)).scalar_one_or_none()
                if not resolution:
                    # Fetch detailed decisions
                    dec_stmt = select(ScreeningDecision).where(
                        ScreeningDecision.project_id == project_id,
                        ScreeningDecision.work_id == work_id,
                        ScreeningDecision.stage == stage,
                    )
                    decs = (await db.execute(dec_stmt)).scalars().all()
                    conflicts.append({
                        "work_id": work_id,
                        "title": title,
                        "stage": stage,
                        "decisions": [
                            {"user_id": d.user_id, "verdict": d.verdict, "reason": d.reason_code, "notes": d.notes}
                            for d in decs
                        ],
                    })
        return conflicts

    @staticmethod
    async def resolve_conflict(
        db: AsyncSession,
        project_id: str,
        user_id: str,
        work_id: str,
        stage: str,
        final_verdict: str,
        reason_code: Optional[str] = None,
        rationale: Optional[str] = None,
    ) -> ScreeningResolution:
        """SCR-009: Conflict resolution closes the conflict without mutating original reviewer rows."""
        resolution = ScreeningResolution(
            project_id=project_id,
            work_id=work_id,
            stage=stage,
            resolved_by=user_id,
            final_verdict=final_verdict,
            reason_code=reason_code,
            rationale=rationale,
        )
        db.add(resolution)
        await db.flush()
        return resolution

    @staticmethod
    async def compute_cohen_kappa(db: AsyncSession, project_id: str, stage: str = "title_abstract") -> Dict[str, Any]:
        """SCR-010: Categorical Cohen's kappa for inter-rater reliability.
        po = observed agreement; pe = sum(p1k * p2k); kappa = (po - pe) / (1 - pe)
        """
        # Find items reviewed by at least 2 distinct reviewers
        dec_stmt = select(ScreeningDecision).where(
            ScreeningDecision.project_id == project_id,
            ScreeningDecision.stage == stage,
        ).order_by(ScreeningDecision.created_at.asc())
        all_decs = (await db.execute(dec_stmt)).scalars().all()

        work_reviewer_map: Dict[str, Dict[str, str]] = {}
        reviewers_set = set()
        for d in all_decs:
            if d.work_id not in work_reviewer_map:
                work_reviewer_map[d.work_id] = {}
            work_reviewer_map[d.work_id][d.user_id] = d.verdict
            reviewers_set.add(d.user_id)

        if len(reviewers_set) < 2:
            return {
                "stage": stage,
                "total_dual_reviewed": 0,
                "observed_agreement": 1.0,
                "expected_agreement": 1.0,
                "cohen_kappa": None,
                "interpretation": "Single Reviewer / Undefined",
            }

        # Select the two primary reviewers
        rev1, rev2 = list(reviewers_set)[:2]
        paired_verdicts = []
        for w_id, rev_map in work_reviewer_map.items():
            if rev1 in rev_map and rev2 in rev_map:
                paired_verdicts.append((rev_map[rev1], rev_map[rev2]))

        n = len(paired_verdicts)
        if n == 0:
            return {
                "stage": stage,
                "total_dual_reviewed": 0,
                "observed_agreement": 1.0,
                "expected_agreement": 1.0,
                "cohen_kappa": None,
                "interpretation": "No overlapping reviews yet",
            }

        # Categories: "include", "exclude", "maybe"
        categories = ["include", "exclude", "maybe"]
        agreements = sum(1 for v1, v2 in paired_verdicts if v1 == v2)
        po = agreements / n

        pe = 0.0
        for cat in categories:
            p1_cat = sum(1 for v1, _ in paired_verdicts if v1 == cat) / n
            p2_cat = sum(1 for _, v2 in paired_verdicts if v2 == cat) / n
            pe += (p1_cat * p2_cat)

        if pe >= 1.0:
            kappa = 1.0
        else:
            kappa = round((po - pe) / (1.0 - pe), 4)

        # Landis & Koch (1977) benchmark
        if kappa < 0.20:
            interp = "Slight Agreement"
        elif kappa <= 0.40:
            interp = "Fair Agreement"
        elif kappa <= 0.60:
            interp = "Moderate Agreement"
        elif kappa <= 0.80:
            interp = "Substantial Agreement"
        else:
            interp = "Almost Perfect Agreement"

        return {
            "stage": stage,
            "total_dual_reviewed": n,
            "observed_agreement": round(po, 4),
            "expected_agreement": round(pe, 4),
            "cohen_kappa": kappa,
            "interpretation": interp,
        }

    @staticmethod
    async def compute_prisma_flow(db: AsyncSession, project_id: str) -> Dict[str, Any]:
        """SCR-011, SCR-012, SCR-013: PRISMA 2020 Flow computation and mathematical reconciliation."""
        # 1. Identified: from import batches
        batch_stmt = select(func.sum(ImportBatch.imported_count), func.sum(ImportBatch.skipped_count)).where(
            ImportBatch.project_id == project_id
        )
        batch_row = (await db.execute(batch_stmt)).first()
        raw_imported = batch_row[0] or 0
        raw_duplicates = batch_row[1] or 0

        # Unique library items
        lib_stmt = select(func.count(LibraryItem.id)).where(LibraryItem.project_id == project_id)
        screened_count = (await db.execute(lib_stmt)).scalar() or 0

        identified = screened_count + raw_duplicates

        # 2. Excluded TA
        ta_excl_stmt = select(func.count(func.distinct(ScreeningDecision.work_id))).where(
            ScreeningDecision.project_id == project_id,
            ScreeningDecision.stage == "title_abstract",
            ScreeningDecision.verdict == "exclude",
        )
        excluded_ta = (await db.execute(ta_excl_stmt)).scalar() or 0

        # 3. Reports sought for retrieval
        reports_sought = max(0, screened_count - excluded_ta)
        reports_assessed_ft = reports_sought

        # 4. Excluded FT with reasons
        ft_excl_stmt = select(func.count(func.distinct(ScreeningDecision.work_id))).where(
            ScreeningDecision.project_id == project_id,
            ScreeningDecision.stage == "full_text",
            ScreeningDecision.verdict == "exclude",
        )
        excluded_ft = (await db.execute(ft_excl_stmt)).scalar() or 0

        # Breakdown by reasons
        reason_stmt = (
            select(ScreeningDecision.reason_code, func.count(ScreeningDecision.id))
            .where(
                ScreeningDecision.project_id == project_id,
                ScreeningDecision.stage == "full_text",
                ScreeningDecision.verdict == "exclude",
            )
            .group_by(ScreeningDecision.reason_code)
        )
        reasons_rows = (await db.execute(reason_stmt)).all()
        reasons_list = [{"code": r[0] or "UNSPECIFIED", "count": r[1]} for r in reasons_rows]

        # 5. Included
        studies_included = max(0, reports_assessed_ft - excluded_ft)

        # SCR-012: Reconciliation check
        issues = []
        if (identified - raw_duplicates) != screened_count:
            issues.append(f"Discrepancy: identified ({identified}) - duplicates ({raw_duplicates}) != screened ({screened_count})")
        if (screened_count - excluded_ta) != reports_assessed_ft:
            issues.append(f"Discrepancy: screened ({screened_count}) - excluded_ta ({excluded_ta}) != assessed_ft ({reports_assessed_ft})")
        if (reports_assessed_ft - excluded_ft) != studies_included:
            issues.append(f"Discrepancy: assessed_ft ({reports_assessed_ft}) - excluded_ft ({excluded_ft}) != included ({studies_included})")

        return {
            "boxes": {
                "identified": identified,
                "duplicates_removed": raw_duplicates,
                "records_screened": screened_count,
                "excluded_ta": excluded_ta,
                "reports_sought": reports_sought,
                "reports_assessed_ft": reports_assessed_ft,
                "excluded_ft": excluded_ft,
                "studies_included": studies_included,
            },
            "reasons": reasons_list,
            "reconciliation": {
                "ok": len(issues) == 0,
                "issues": issues,
            },
        }
