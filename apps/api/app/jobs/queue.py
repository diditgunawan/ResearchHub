import logging
import asyncio
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("researchforge.jobs")

_QUEUE_MAP: Dict[Any, asyncio.Queue] = {}


def _get_queue() -> asyncio.Queue:
    loop = asyncio.get_running_loop()
    if loop not in _QUEUE_MAP:
        _QUEUE_MAP[loop] = asyncio.Queue()
    return _QUEUE_MAP[loop]


class JobQueue:
    """Tier M asynchronous job queue client (Blueprint 16 / ADR-010)."""

    @staticmethod
    async def enqueue(job_name: str, payload: Dict[str, Any]) -> str:
        """Enqueue an asynchronous task for background worker processing."""
        job_id = f"job-{job_name}-{payload.get('project_id', 'global')}-{asyncio.get_running_loop().time()}"
        job_record = {
            "id": job_id,
            "name": job_name,
            "payload": payload,
            "status": "queued",
        }
        logger.info(f"[JOB ENQUEUED] {job_name} ({job_id})")
        await _get_queue().put(job_record)
        return job_id

    @staticmethod
    async def get_next_job(timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Fetch next pending job from the queue."""
        try:
            return await asyncio.wait_for(_get_queue().get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None


async def enqueue_pdf_extract(work_id: str, project_id: str, storage_path: str) -> str:
    return await JobQueue.enqueue("extract_pdf_and_embed", {
        "work_id": work_id,
        "project_id": project_id,
        "storage_path": storage_path,
    })


async def enqueue_openalex_sync(source: str = "openalex_snapshot", scope: Optional[dict] = None) -> str:
    return await JobQueue.enqueue("sync_openalex_snapshot", {
        "source": source,
        "scope": scope or {"years": [2020, 2026], "types": ["article", "review"]},
    })


async def enqueue_retraction_audit(project_id: str) -> str:
    return await JobQueue.enqueue("audit_retractions", {
        "project_id": project_id,
    })
