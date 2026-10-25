import httpx
from typing import Optional, List
from datetime import datetime, timezone
from app.sources.base import BaseSourceConnector, normalize_doi, reconstruct_inverted_index, SourceError, SourceTimeout, SourceRateLimited
from app.sources.schemas import SearchQuery, SearchPage, WorkRecord, AuthorRecord, VenueRecord
from app.core.config import settings


class OpenAlexConnector(BaseSourceConnector):
    """OpenAlex API connector conforming to DAT-001..DAT-010."""
    name = "openalex"
    BASE_URL = "https://api.openalex.org"

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.client = client

    def _get_headers(self) -> dict:
        headers = {"User-Agent": f"ResearchForge/0.1.0 (mailto:{settings.OPENALEX_MAILTO})"}
        if settings.OPENALEX_API_KEY:
            headers["api_key"] = settings.OPENALEX_API_KEY
        return headers

    def _normalize_item(self, item: dict) -> WorkRecord:
        raw_doi = item.get("doi")
        doi = normalize_doi(raw_doi)
        
        # Authors
        authors: List[AuthorRecord] = []
        for idx, auth in enumerate(item.get("authorships", [])):
            author_obj = auth.get("author", {})
            name = author_obj.get("display_name")
            if name:
                orcid = author_obj.get("orcid")
                authors.append(AuthorRecord(name=name, orcid=orcid, position=idx + 1))

        # Venue
        venue = None
        primary_location = item.get("primary_location") or {}
        source_obj = primary_location.get("source") or {}
        if source_obj.get("display_name"):
            venue = VenueRecord(
                name=source_obj.get("display_name"),
                issn_l=source_obj.get("issn_l"),
                openalex_id=source_obj.get("id"),
            )

        # Abstract from inverted index
        abstract = reconstruct_inverted_index(item.get("abstract_inverted_index"))

        # OA info
        open_access = item.get("open_access") or {}
        is_oa = open_access.get("is_oa", False)
        oa_url = open_access.get("oa_url")

        return WorkRecord(
            doi=doi,
            openalex_id=item.get("id"),
            title=item.get("title") or "Untitled Work",
            abstract=abstract,
            year=item.get("publication_year"),
            work_type=item.get("type") or "article",
            language=item.get("language") or "en",
            authors=authors,
            venue=venue,
            is_oa=is_oa,
            oa_url=oa_url,
            cited_by_count=item.get("cited_by_count", 0),
            retracted=item.get("is_retracted", False),
            provenance={
                "source": self.name,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    async def search(self, query: SearchQuery) -> SearchPage:
        params = {
            "search": query.q,
            "per-page": min(query.page_size, 100),
        }
        if query.cursor:
            params["cursor"] = query.cursor

        filters = []
        if query.year_from:
            filters.append(f"from_publication_date:{query.year_from}-01-01")
        if query.year_to:
            filters.append(f"to_publication_date:{query.year_to}-12-31")
        if query.oa_only:
            filters.append("is_oa:true")
        if filters:
            params["filter"] = ",".join(filters)

        try:
            timeout = httpx.Timeout(8.0)
            async with (self.client or httpx.AsyncClient(timeout=timeout)) as client:
                res = await client.get(f"{self.BASE_URL}/works", params=params, headers=self._get_headers())
                if res.status_code == 429:
                    raise SourceRateLimited(self.name)
                if res.status_code != 200:
                    raise SourceError(self.name, f"HTTP {res.status_code}: {res.text[:200]}")

                data = res.json()
                meta = data.get("meta", {})
                results = data.get("results", [])
                items = [self._normalize_item(r) for r in results]

                return SearchPage(
                    items=items,
                    next_cursor=meta.get("next_cursor"),
                    total_estimate=meta.get("count"),
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
                res = await client.get(f"{self.BASE_URL}/works/doi:{clean_doi}", headers=self._get_headers())
                if res.status_code == 404:
                    return None
                if res.status_code == 429:
                    raise SourceRateLimited(self.name)
                if res.status_code != 200:
                    raise SourceError(self.name, f"HTTP {res.status_code}")
                return self._normalize_item(res.json())
        except httpx.TimeoutException:
            raise SourceTimeout(self.name, 8.0)
        except Exception as e:
            raise SourceError(self.name, str(e))
