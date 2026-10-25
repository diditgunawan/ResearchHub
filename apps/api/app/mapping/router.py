from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.identity.router import get_current_user
from app.identity.schemas import UserResponse
from app.projects.service import ProjectService
from app.works.models import Work
from app.mapping.models import (
    MapRun, MapCluster, MapClusterMember, LineageNode, LineageEdge, PositioningRun, GapSignal
)
from app.mapping.schemas import (
    MapRunCreate, LineageGraphResponse, MapClusterResponse, ClusterMemberInfo,
    LineageNodeResponse, LineageEdgeResponse, AuditTableResponse, UserOverrideRequest,
    ManuscriptPositioningRequest, ManuscriptPositioningResponse, GapSignalResponse
)
from app.mapping.service import MappingService

router = APIRouter(prefix="", tags=["Literature Mapping & Lineage"])


@router.post("/projects/{project_id}/lineage", response_model=LineageGraphResponse)
async def create_lineage_run(
    project_id: str,
    req: MapRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """MAP-001, MAP-002, MAP-007..MAP-010: Generate genealogical lineage DAG with chronological constraints."""
    await ProjectService.get_project_with_role(db, project_id, current_user.id)

    run = await MappingService.run_lineage_mapping(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        scope_type=req.scope_type,
        work_ids=req.work_ids,
        seed=req.seed,
    )

    return await get_lineage_graph(project_id, run.id, db, current_user)


@router.get("/projects/{project_id}/lineage/{run_id}", response_model=LineageGraphResponse)
async def get_lineage_graph(
    project_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve full lineage DAG with families, nodes, and component evidence edges."""
    await ProjectService.get_project_with_role(db, project_id, current_user.id)

    # Fetch run
    run_res = await db.execute(select(MapRun).where(MapRun.id == run_id, MapRun.project_id == project_id))
    run = run_res.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Lineage run not found")

    # Fetch clusters
    c_res = await db.execute(select(MapCluster).where(MapCluster.run_id == run_id))
    clusters = c_res.scalars().all()

    # Fetch nodes
    n_res = await db.execute(select(LineageNode).where(LineageNode.run_id == run_id))
    nodes = n_res.scalars().all()

    # Fetch edges
    e_res = await db.execute(select(LineageEdge).where(LineageEdge.run_id == run_id))
    edges = e_res.scalars().all()

    # Fetch works for title & doi resolution
    work_ids = [n.work_id for n in nodes]
    w_res = await db.execute(select(Work).where(Work.id.in_(work_ids)))
    works_map = {w.id: w for w in w_res.scalars().all()}

    # Format clusters response
    cluster_responses = []
    for c in clusters:
        # Fetch members
        mem_res = await db.execute(select(MapClusterMember).where(MapClusterMember.cluster_id == c.id))
        members = mem_res.scalars().all()
        m_infos = []
        for m in members:
            w = works_map.get(m.work_id)
            if w:
                m_infos.append(ClusterMemberInfo(
                    work_id=w.id,
                    title=w.title,
                    year=w.year,
                    membership_score=m.membership_score or 1.0,
                ))
        cluster_responses.append(MapClusterResponse(
            id=c.id,
            label=c.label,
            label_source=c.label_source,
            keywords=c.keywords or [],
            size=c.size,
            is_other=c.is_other,
            members=m_infos,
        ))

    # Format nodes response
    cluster_labels = {c.id: c.label for c in clusters}
    node_responses = []
    roots = []
    for n in nodes:
        w = works_map.get(n.work_id)
        parent_w = works_map.get(n.parent_work_id) if n.parent_work_id else None
        if n.role == "root":
            roots.append(n.work_id)

        node_responses.append(LineageNodeResponse(
            work_id=n.work_id,
            title=w.title if w else "Unknown Work",
            year=w.year if w else None,
            doi=w.doi if w else None,
            family_id=n.family_id,
            family_label=cluster_labels.get(n.family_id, "Unplaced") if n.family_id else "Unplaced",
            role=n.role,
            parent_work_id=n.parent_work_id,
            parent_title=parent_w.title if parent_w else None,
            confidence=n.confidence,
            confidence_band=n.confidence_band,
            evidence=n.evidence or {},
            missing_flags=n.missing_flags or [],
            user_override=n.user_override,
        ))

    edge_responses = [
        LineageEdgeResponse(
            parent_work_id=e.parent_work_id,
            child_work_id=e.child_work_id,
            score=e.score,
            evidence=e.evidence or {},
        )
        for e in edges
    ]

    return LineageGraphResponse(
        run_id=run.id,
        project_id=project_id,
        record_count=run.record_count or len(nodes),
        families=cluster_responses,
        nodes=node_responses,
        edges=edge_responses,
        roots=roots,
        status=run.status,
        created_at=run.created_at,
    )


@router.get("/projects/{project_id}/lineage/{run_id}/audit", response_model=AuditTableResponse)
async def get_lineage_audit_table(
    project_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """MAP-011: Audit table listing branch, parent, evidence types, confidence bands, and missing flags."""
    graph = await get_lineage_graph(project_id, run_id, db, current_user)

    summary = {
        "high": sum(1 for n in graph.nodes if n.confidence_band == "high"),
        "medium": sum(1 for n in graph.nodes if n.confidence_band == "medium"),
        "low": sum(1 for n in graph.nodes if n.confidence_band == "low"),
        "roots": len(graph.roots),
        "needs_review": sum(1 for n in graph.nodes if n.role == "needs_review"),
    }

    return AuditTableResponse(
        run_id=run_id,
        total_records=len(graph.nodes),
        rows=graph.nodes,
        summary=summary,
    )


@router.post("/projects/{project_id}/lineage/{run_id}/override", response_model=LineageNodeResponse)
async def override_lineage_node(
    project_id: str,
    run_id: str,
    req: UserOverrideRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """MAP-013: User overrides of parent or branch; preserves machine evidence unchanged and tracks user identity."""
    await ProjectService.get_project_with_role(db, project_id, current_user.id)

    node_res = await db.execute(
        select(LineageNode).where(LineageNode.run_id == run_id, LineageNode.work_id == req.work_id)
    )
    node = node_res.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found in this lineage run")

    # Record previous values
    previous = {
        "parent_work_id": node.parent_work_id,
        "family_id": node.family_id,
        "role": node.role,
    }

    if req.parent_work_id is not None:
        node.parent_work_id = req.parent_work_id
        node.role = "placed"
    if req.family_id is not None:
        node.family_id = req.family_id

    node.user_override = {
        "by": current_user.id,
        "at": datetime.now(timezone.utc).isoformat(),
        "reason": req.reason,
        "previous": previous,
    }

    await db.commit()
    await db.refresh(node)

    w_res = await db.execute(select(Work).where(Work.id == node.work_id))
    w = w_res.scalar_one_or_none()
    parent_w = None
    if node.parent_work_id:
        pw_res = await db.execute(select(Work).where(Work.id == node.parent_work_id))
        parent_w = pw_res.scalar_one_or_none()

    return LineageNodeResponse(
        work_id=node.work_id,
        title=w.title if w else "Unknown Work",
        year=w.year if w else None,
        doi=w.doi if w else None,
        family_id=node.family_id,
        family_label="Custom Override",
        role=node.role,
        parent_work_id=node.parent_work_id,
        parent_title=parent_w.title if parent_w else None,
        confidence=node.confidence,
        confidence_band=node.confidence_band,
        evidence=node.evidence or {},
        missing_flags=node.missing_flags or [],
        user_override=node.user_override,
    )


@router.post("/projects/{project_id}/positioning", response_model=ManuscriptPositioningResponse)
async def position_manuscript(
    project_id: str,
    req: ManuscriptPositioningRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """MAP-015, MAP-016: Position manuscript relative to analyzed set; never claims global novelty."""
    await ProjectService.get_project_with_role(db, project_id, current_user.id)

    res = await MappingService.position_manuscript(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        lineage_run_id=req.lineage_run_id,
        title=req.title,
        abstract=req.abstract,
        references=req.references,
        retain_text=req.retain_text,
    )
    return ManuscriptPositioningResponse(**res)


@router.get("/projects/{project_id}/gaps/{run_id}", response_model=List[GapSignalResponse])
async def get_gap_signals(
    project_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """MAP-017: Return typed gap signals with persistent non-novelty disclaimer."""
    await ProjectService.get_project_with_role(db, project_id, current_user.id)

    gaps_res = await db.execute(select(GapSignal).where(GapSignal.run_id == run_id))
    gaps = gaps_res.scalars().all()

    work_ids = [g.work_id for g in gaps if g.work_id]
    w_res = await db.execute(select(Work).where(Work.id.in_(work_ids)))
    works = {w.id: w.title for w in w_res.scalars().all()}

    return [
        GapSignalResponse(
            id=g.id,
            kind=g.kind,
            work_id=g.work_id,
            work_title=works.get(g.work_id),
            excerpt=g.excerpt,
            frequency=g.frequency,
            confidence=g.confidence,
        )
        for g in gaps
    ]
