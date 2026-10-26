import pytest
from app.jobs.queue import (
    JobQueue,
    enqueue_pdf_extract,
    enqueue_openalex_sync,
    enqueue_retraction_audit,
)
from app.jobs.worker import process_one_job

# SYNTHETIC TEST FIXTURE (Tier M Scale Architecture: Background Job Queues per Blueprint 16)


@pytest.mark.asyncio
async def test_job_enqueue_and_worker_execution():
    """Verify background job dispatch and worker execution in Tier M topology."""
    # 1. Enqueue PDF extraction job
    job_id_pdf = await enqueue_pdf_extract(
        work_id="work-uuid-1234",
        project_id="proj-uuid-5678",
        storage_path="uploads/proj-5678/study.pdf",
    )
    assert job_id_pdf.startswith("job-extract_pdf_and_embed")

    # 2. Worker executes job
    processed = await process_one_job()
    assert processed is True

    # 3. Queue should now be empty
    empty_run = await process_one_job()
    assert empty_run is False


@pytest.mark.asyncio
async def test_multi_job_queue_pipeline():
    """Verify multiple heterogeneous jobs are processed in sequence."""
    j1 = await enqueue_openalex_sync(source="openalex_snapshot", scope={"years": [2024, 2026]})
    j2 = await enqueue_retraction_audit(project_id="proj-batch-999")

    assert j1 is not None
    assert j2 is not None

    p1 = await process_one_job()
    assert p1 is True

    p2 = await process_one_job()
    assert p2 is True

    p3 = await process_one_job()
    assert p3 is False
