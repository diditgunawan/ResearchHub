# Connector interface (Python, reference)
```python
from typing import Protocol, Iterable, Optional
from dataclasses import dataclass

@dataclass
class SearchQuery:
    q: str
    year_from: int | None = None
    year_to: int | None = None
    oa_only: bool = False
    language: str | None = None
    cursor: str | None = None
    page_size: int = 25

@dataclass
class SearchPage:
    items: list["WorkRecord"]     # canonical-work-schema.md
    next_cursor: str | None
    total_estimate: int | None
    source: str
    fetched_at: str               # ISO-8601 UTC

class SourceConnector(Protocol):
    name: str                      # "openalex" | "crossref" | "pubmed" | ...
    def search(self, query: SearchQuery) -> SearchPage: ...
    def get_by_id(self, id_type: str, value: str) -> Optional["WorkRecord"]: ...
    def get_references(self, work_id: str, limit: int = 200) -> Iterable["WorkRecord"]: ...
    def get_cited_by(self, work_id: str, limit: int = 200) -> Iterable["WorkRecord"]: ...
    def health(self) -> dict: ...  # for source_status & smoke tests
```
Connector contract: raises `SourceTimeout`, `SourceRateLimited(retry_after)`, `SourceError(code)`; never returns partially-normalized records; logs request id + latency, never payload bodies.
