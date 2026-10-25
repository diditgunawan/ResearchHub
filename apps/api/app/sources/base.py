import re
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
from app.sources.schemas import SearchQuery, SearchPage, WorkRecord


class SourceError(Exception):
    """Base error for external scholarly sources."""
    def __init__(self, source: str, message: str, code: str = "SOURCE_ERROR"):
        self.source = source
        self.code = code
        super().__init__(f"[{source}] {message}")


class SourceTimeout(SourceError):
    def __init__(self, source: str, timeout_seconds: float = 8.0):
        super().__init__(source, f"Request timed out after {timeout_seconds}s", code="SOURCE_TIMEOUT")


class SourceRateLimited(SourceError):
    def __init__(self, source: str, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(source, f"Rate limited. Retry after {retry_after}s", code="SOURCE_RATE_LIMITED")


def normalize_doi(raw_doi: Optional[str]) -> Optional[str]:
    """DAT-007: DOIs are normalized to lowercase without URL prefixes or leading/trailing whitespace."""
    if not raw_doi:
        return None
    cleaned = raw_doi.strip().lower()
    cleaned = re.sub(r"^https?://(dx\.)?doi\.org/", "", cleaned)
    cleaned = re.sub(r"^doi:\s*", "", cleaned)
    # Basic DOI validation pattern (starts with 10.xxxx)
    if not re.match(r"^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$", cleaned):
        return None
    return cleaned


def reconstruct_inverted_index(inverted_index: Optional[Dict[str, List[int]]]) -> Optional[str]:
    """DAT-010: Deterministically reconstruct abstract text from OpenAlex inverted index structure."""
    if not inverted_index or not isinstance(inverted_index, dict):
        return None

    # Map position -> word
    position_word_map: Dict[int, str] = {}
    for word, positions in inverted_index.items():
        if isinstance(positions, list):
            for pos in positions:
                position_word_map[pos] = word

    if not position_word_map:
        return None

    max_pos = max(position_word_map.keys())
    words = [position_word_map.get(i, "") for i in range(max_pos + 1)]
    reconstructed = " ".join(words).strip()
    return reconstructed if reconstructed else None


class BaseSourceConnector(ABC):
    """DAT-002: Source connector contract."""
    name: str

    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchPage:
        """Search works by keyword and filters."""
        pass

    @abstractmethod
    async def get_by_doi(self, doi: str) -> Optional[WorkRecord]:
        """Fetch canonical record by normalized DOI."""
        pass
