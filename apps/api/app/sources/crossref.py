import httpx
from typing import Optional, List
from datetime import datetime, timezone
from app.sources.base import BaseSourceConnector, normalize_doi, SourceError, SourceTimeout, SourceRateLimited
from app.sources.schemas import SearchQuery, SearchPage, WorkRecord, AuthorRecord, VenueRecord
from app.core.config import settings


class CrossrefConnector(BaseSourceConnector):
    """Crossref API connector conforming to DAT-001..DAT-010."""
    name = "crossref"
    BASE_URL = "https://api.crossref.org"

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.client = client

    def _get_headers(self) -> dict:
        return {"User-Agent": f"ResearchForge/0.1.0 (mailto:{settings.CROSSREF_MAILTO})"}

    def _normalize_item(self, item: dict) -> WorkRecord:
        raw_doi = item.get("DOI")
        doi = normalize_doi(raw_doi)

        # Title
        titles = item.get("title", [])
        title = titles[0] if titles else "Untitled Work"

        # Authors
        authors: List[AuthorRecord] = []
        for idx, auth in enumerate(item.get("author", [])):
            given = auth.get("given", "")
            family = auth.get("family", "")
            name = f"{given} {family}".strip() or auth.get("name") or "Unknown Author"
            orcid = auth.get("ORCID")
            authors.append(AuthorRecord(name=name, orcid=orcid, position=idx + 1))

        # Venue
        venue = None
        container = item.get("container-title", [])
        if container:
            issn_list = item.get("ISSN", [])
            venue = VenueRecord(
                name=container[0],
                issn_l=issn_list[0] if issn_list else None,
            )

        # Year from published date parts
        year = None
        published = item.get("published") or item.get("created") or {}
        date_parts = published.get("date-parts", [[]])
        if date_parts and date_parts[0]:
            year = date_parts[0][0]

        return WorkRecord(
            doi=doi,
            title=title,
            abstract=item.get("abstract"),  # often None or JATS XML in Crossref
            year=year,
            work_type=item.get("type", "journal-article"),
            authors=authors,
            venue=venue,
            cited_by_count=item.get("is-referenced-by-count", 0),
            retracted=False,
            provenance={
                "source": self.name,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    async def search(self, query: SearchQuery) -> SearchPage:
        params = {
            "query": query.q,
            "rows": min(query.page_size, 100),
        }
        filters = []
        if query.year_from:
            filters.append(f"from-pub-date:{query.year_from}")
        if query.year_to:
            filters.append(f"until-pub-date:{query.year_to}")
        if filters:
            params["filter"] = ",".join(filters)

        try:
            timeout = httpx.Timeout(8.0)
            async with (self.client or httpx.AsyncClient(timeout=timeout)) as client:
                res = await client.get(f"{self.BASE_URL}/works", params=params, headers=self._get_headers())
                if res.status_code == 429:
                    raise SourceRateLimited(self.name)
                if res.status_code != 200:
                    raise SourceError(self.name, f"HTTP {res.status_code}")

                message = res.json().get("message", {})
                items = [self._normalize_item(i) for i in message.get("items", [])]

                return SearchPage(
                    items=items,
                    total_estimate=message.get("total-results"),
                    source=self.name,
                )
        except httpx.TimeoutException:
            raise SourceTimeout(self.name, 8.0)
        except (SourceError, SourceTimeout, SourceRateLimited):
            raise
        except Exception as e:
            raise SourceError(self.name, str(e))

    async def get_by_doi(self, doi: str) -> Optional[WorkRecord]:
        clean_doi = normalize_doi(doi)
        if not clean_doi:
            return None
        try:
            timeout = httpx.Timeout(8.0)
            async with (self.client or httpx.AsyncClient(timeout=timeout)) as client:
                res = await client.get(f"{self.BASE_URL}/works/{clean_doi}", headers=self._get_headers())
                if res.status_code == 404:
                    return None
                if res.status_code == 429:
                    raise SourceRateLimited(self.name)
                if res.status_code != 200:
                    raise SourceError(self.name, f"HTTP {res.status_code}")
                return self._normalize_item(res.json().get("message", {}))
        except httpx.TimeoutException:
            raise SourceTimeout(self.name, 8.0)
        except Exception as e:
            raise SourceError(self.name, str(e))
