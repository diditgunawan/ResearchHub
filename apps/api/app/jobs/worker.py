import sys
import asyncio
import logging
from typing import Dict, Any
from app.jobs.queue import JobQueue

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("researchforge.worker")


async def handle_extract_pdf_and_embed(payload: Dict[str, Any]):
    work_id = payload.get("work_id")
    project_id = payload.get("project_id")
    logger.info(f"[WORKER] Extracting text and computing embeddings for work={work_id} in project={project_id}")
    await asyncio.sleep(0.05)  # Simulate non-blocking async extraction pipeline
    logger.info(f"[WORKER] Completed extraction for work={work_id}")


async def handle_sync_openalex_snapshot(payload: Dict[str, Any]):
    source = payload.get("source")
    scope = payload.get("scope", {})
    logger.info(f"[WORKER] Synchronizing {source} within scope {scope}")
    await asyncio.sleep(0.05)
    logger.info(f"[WORKER] Snapshot sync completed for {source}")


async def handle_audit_retractions(payload: Dict[str, Any]):
    project_id = payload.get("project_id")
    logger.info(f"[WORKER] Auditing retractions for project={project_id}")
    await asyncio.sleep(0.05)
    logger.info(f"[WORKER] Retraction audit completed for project={project_id}")


JOB_DISPATCH = {
    "extract_pdf_and_embed": handle_extract_pdf_and_embed,
    "sync_openalex_snapshot": handle_sync_openalex_snapshot,
    "audit_retractions": handle_audit_retractions,
}


async def process_one_job() -> bool:
    """Fetch and process a single queued background job."""
    job = await JobQueue.get_next_job(timeout=0.1)
    if not job:
        return False

    name = job.get("name")
    payload = job.get("payload", {})
    handler = JOB_DISPATCH.get(name)
    if handler:
        logger.info(f"[WORKER] Executing job {name} (id={job.get('id')})")
        await handler(payload)
        return True
    else:
        logger.warning(f"[WORKER] No handler registered for job type {name}")
        return False


async def run_worker_loop(stop_event: asyncio.Event = None):
    """Main daemon loop for background worker container."""
    logger.info("[WORKER] ResearchForge background worker started (Tier M queue)")
    while True:
        if stop_event and stop_event.is_set():
            logger.info("[WORKER] Graceful shutdown requested.")
            break
        processed = await process_one_job()
        if not processed:
            await asyncio.sleep(0.2)


if __name__ == "__main__":
    try:
        asyncio.run(run_worker_loop())
    except KeyboardInterrupt:
        logger.info("[WORKER] Terminated by operator.")
