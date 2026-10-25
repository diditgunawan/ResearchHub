from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.sources.schemas import SearchQuery, FederatedSearchResponse, WorkRecord
from app.sources.federated import FederatedSearchService
from app.works.models import Work, Author, WorkAuthor

router = APIRouter(prefix="/works", tags=["works"])
federated_search = FederatedSearchService()


async def upsert_work_record(db: AsyncSession, item: WorkRecord) -> str:
    """Idempotently persist or locate canonical work record in works table (DAT-011)."""
    work = None
    if item.doi:
        stmt = select(Work).where(Work.doi == item.doi)
        work = (await db.execute(stmt)).scalar_one_or_none()
    elif item.openalex_id:
        stmt = select(Work).where(Work.openalex_id == item.openalex_id)
        work = (await db.execute(stmt)).scalar_one_or_none()

    if not work:
        work = Work(
            doi=item.doi,
            openalex_id=item.openalex_id,
            pmid=item.pmid,
            title=item.title,
            abstract=item.abstract,
            year=item.year,
            venue=item.venue.name if item.venue else None,
            work_type=item.work_type,
            is_oa=item.is_oa,
            oa_url=item.oa_url,
            cited_by_count=item.cited_by_count,
            retracted=item.retracted,
        )
        db.add(work)
        await db.flush()

        # Add authors
        for idx, auth_rec in enumerate(item.authors):
            auth_stmt = select(Author).where(Author.name == auth_rec.name)
            author = (await db.execute(auth_stmt)).scalar_one_or_none()
            if not author:
                author = Author(name=auth_rec.name, orcid=auth_rec.orcid)
                db.add(author)
                await db.flush()

            wa = WorkAuthor(work_id=work.id, author_id=author.id, position=idx + 1)
            db.add(wa)
        await db.flush()

    return work.id


@router.get("/search", response_model=FederatedSearchResponse)
async def search_works(
    q: str = Query(..., min_length=1, description="Keywords or search query"),
    year_from: Optional[int] = Query(None, ge=1800, le=2100),
    year_to: Optional[int] = Query(None, ge=1800, le=2100),
    oa_only: bool = Query(False),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = SearchQuery(
        q=q,
        year_from=year_from,
        year_to=year_to,
        oa_only=oa_only,
        page_size=page_size,
    )
    res = await federated_search.search(query)

    # Cache/upsert results to works table asynchronously
    for item in res.items:
        try:
            await upsert_work_record(db, item)
        except Exception:
            pass  # Non-blocking caching

    return res


@router.get("/{work_id}")
async def get_work(work_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Work).where(Work.id == work_id)
    work = (await db.execute(stmt)).scalar_one_or_none()
    if not work:
        raise NotFoundError(f"Work '{work_id}' not found", code="WORK_NOT_FOUND")

    # Fetch authors
    auth_stmt = (
        select(Author.name, Author.orcid, WorkAuthor.position)
        .join(WorkAuthor, Author.id == WorkAuthor.author_id)
        .where(WorkAuthor.work_id == work.id)
        .order_by(WorkAuthor.position.asc())
    )
    authors_rows = (await db.execute(auth_stmt)).all()

    return {
        "id": work.id,
        "doi": work.doi,
        "openalex_id": work.openalex_id,
        "pmid": work.pmid,
        "title": work.title,
        "abstract": work.abstract,
        "year": work.year,
        "venue": work.venue,
        "work_type": work.work_type,
        "is_oa": work.is_oa,
        "oa_url": work.oa_url,
        "cited_by_count": work.cited_by_count,
        "retracted": work.retracted,
        "authors": [{"name": r[0], "orcid": r[1], "position": r[2]} for r in authors_rows],
        "created_at": work.created_at,
    }
