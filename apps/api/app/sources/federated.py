import asyncio
import time
from typing import List, Dict, Optional
from app.sources.base import BaseSourceConnector, SourceTimeout, SourceRateLimited, SourceError
from app.sources.schemas import SearchQuery, WorkRecord, SourceStatus, FederatedSearchResponse
from app.sources.openalex import OpenAlexConnector
from app.sources.crossref import CrossrefConnector


class FederatedSearchService:
    def __init__(self, connectors: Optional[List[BaseSourceConnector]] = None):
        self.connectors = connectors or [OpenAlexConnector(), CrossrefConnector()]

    async def _execute_connector(
        self, connector: BaseSourceConnector, query: SearchQuery
    ) -> tuple[SourceStatus, List[WorkRecord]]:
        start_t = time.perf_counter()
        try:
            page = await connector.search(query)
            latency_ms = int((time.perf_counter() - start_t) * 1000)
            status = SourceStatus(
                source=connector.name,
                status="ok",
                latency_ms=latency_ms,
                items_count=len(page.items),
            )
            return status, page.items
        except SourceTimeout:
            latency_ms = int((time.perf_counter() - start_t) * 1000)
            return SourceStatus(
                source=connector.name,
                status="timeout",
                latency_ms=latency_ms,
                items_count=0,
                error_message="Source search timed out after 8 seconds",
            ), []
        except SourceRateLimited as e:
            latency_ms = int((time.perf_counter() - start_t) * 1000)
            return SourceStatus(
                source=connector.name,
                status="rate_limited",
                latency_ms=latency_ms,
                items_count=0,
                error_message=f"Rate limit exceeded (retry after {e.retry_after}s)",
            ), []
        except Exception as e:
            latency_ms = int((time.perf_counter() - start_t) * 1000)
            return SourceStatus(
                source=connector.name,
                status="error",
                latency_ms=latency_ms,
                items_count=0,
                error_message=str(e),
            ), []

    async def search(self, query: SearchQuery) -> FederatedSearchResponse:
        """DAT-005 & DAT-006: Fan-out federated query with per-source status and resilient deduplication."""
        tasks = [self._execute_connector(conn, query) for conn in self.connectors]
        results = await asyncio.gather(*tasks)

        source_statuses: List[SourceStatus] = []
        all_items: List[WorkRecord] = []
        seen_dois: set = set()

        for status, items in results:
            source_statuses.append(status)
            for item in items:
                if item.doi:
                    if item.doi in seen_dois:
                        continue
                    seen_dois.add(item.doi)
                all_items.append(item)

        return FederatedSearchResponse(
            items=all_items,
            source_status=source_statuses,
            total_results=len(all_items),
        )
