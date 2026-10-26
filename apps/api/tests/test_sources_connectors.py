import pytest
import httpx
from httpx import AsyncClient
from app.sources.base import normalize_doi, reconstruct_inverted_index, BaseSourceConnector, SourceTimeout
from app.sources.schemas import SearchQuery, SearchPage, WorkRecord
from app.sources.federated import FederatedSearchService
from app.sources.openalex import OpenAlexConnector
from app.core.config import settings
from app.library.service import LibraryService
from app.works.models import Work
from app.synthesis.models import Chunk
from sqlalchemy import select

# SYNTHETIC TEST FIXTURE (DAT-005, DAT-006, DAT-007, DAT-010, DAT-020, ADR-011)


def test_doi_normalization():
    """DAT-007: DOIs must be normalized to lowercase with all URL prefixes stripped."""
    assert normalize_doi("https://doi.org/10.1038/s41586-020-2649-2") == "10.1038/s41586-020-2649-2"
    assert normalize_doi("http://dx.doi.org/10.1016/J.CELL.2024.01.001") == "10.1016/j.cell.2024.01.001"
    assert normalize_doi("doi: 10.1145/3318464.3389700") == "10.1145/3318464.3389700"
    assert normalize_doi("invalid-doi-format") is None
    assert normalize_doi(None) is None


def test_abstract_inverted_index_reconstruction():
    """DAT-010: Inverted indexes from OpenAlex must be reconstructed deterministically."""
    sample_index = {
        "Deep": [0],
        "learning": [1],
        "in": [2],
        "systematic": [3],
        "reviews.": [4],
    }
    reconstructed = reconstruct_inverted_index(sample_index)
    assert reconstructed == "Deep learning in systematic reviews."
    assert reconstruct_inverted_index(None) is None
    assert reconstruct_inverted_index({}) is None


class MockFastConnector(BaseSourceConnector):
    name = "mock_openalex"

    async def search(self, query: SearchQuery) -> SearchPage:
        return SearchPage(
            items=[
                WorkRecord(
                    doi="10.1038/nature12345",
                    title="Foundation Models in Academic Discovery",
                    year=2024,
                )
            ],
            source=self.name,
        )

    async def get_by_doi(self, doi: str):
        return None


class MockTimingOutConnector(BaseSourceConnector):
    name = "mock_crossref_slow"

    async def search(self, query: SearchQuery) -> SearchPage:
        raise SourceTimeout(self.name, 8.0)

    async def get_by_doi(self, doi: str):
        return None


@pytest.mark.asyncio
async def test_federated_search_resilience_to_timeouts():
    """DAT-005 & DAT-006: A timeout in one source must not fail the overall federated search."""
    service = FederatedSearchService(connectors=[MockFastConnector(), MockTimingOutConnector()])
    query = SearchQuery(q="foundation models")

    response = await service.search(query)

    assert response.total_results == 1
    assert len(response.items) == 1
    assert response.items[0].doi == "10.1038/nature12345"

    # Verify per-source status tracking
    statuses = {s.source: s.status for s in response.source_status}
    assert statuses["mock_openalex"] == "ok"
    assert statuses["mock_crossref_slow"] == "timeout"


@pytest.mark.asyncio
async def test_openalex_api_key_query_param_metered():
    """DAT-020 & ADR-011: Verify metered API key is sent as query parameter and header."""
    settings.OPENALEX_API_KEY = "test-openalex-metered-key"
    captured_request = {}

    def handler(request: httpx.Request):
        captured_request["params"] = str(request.url.query, "utf-8")
        captured_request["headers"] = dict(request.headers)
        return httpx.Response(
            200,
            json={
                "meta": {"count": 1, "next_cursor": None},
                "results": [
                    {
                        "id": "https://openalex.org/W9999",
                        "title": "Quantum Metric Analysis",
                        "publication_year": 2025,
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)
    connector = OpenAlexConnector(client=client)

    res = await connector.search(SearchQuery(q="quantum metric"))
    assert len(res.items) == 1
    assert "api_key=test-openalex-metered-key" in captured_request["params"]
    assert captured_request["headers"]["api_key"] == "test-openalex-metered-key"


@pytest.mark.asyncio
async def test_embed_on_add_discipline(client: AsyncClient):
    """ADR-011: Works only generate embeddings/chunks once added to project library."""
    from app.core.database import async_session_maker
    async with async_session_maker() as db:
        work = Work(
            title="Graph Neural Networks in Molecular Synthesis",
            year=2024,
            abstract="We present graph representations for synthesis pathway discovery and chemical analysis.",
        )
        db.add(work)
        await db.commit()
        await db.refresh(work)

        # Before entering library, zero chunks exist
        chunks_before = (await db.execute(select(Chunk).where(Chunk.work_id == work.id))).scalars().all()
        assert len(chunks_before) == 0

        # Add to library
        item = await LibraryService.add_to_library(db, project_id="proj-demo-123", work_id=work.id)
        await db.commit()

        # After entering library, chunks are immediately computed
        chunks_after = (await db.execute(select(Chunk).where(Chunk.work_id == work.id))).scalars().all()
        assert len(chunks_after) > 0
        assert chunks_after[0].work_id == work.id
