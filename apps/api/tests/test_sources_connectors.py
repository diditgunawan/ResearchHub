import pytest
from app.sources.base import normalize_doi, reconstruct_inverted_index, BaseSourceConnector, SourceTimeout
from app.sources.schemas import SearchQuery, SearchPage, WorkRecord
from app.sources.federated import FederatedSearchService

# SYNTHETIC TEST FIXTURE (DAT-005, DAT-006, DAT-007, DAT-010)

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
