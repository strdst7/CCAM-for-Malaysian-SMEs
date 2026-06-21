"""Job enqueue and status API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ccam_backend.api.deps import get_db, get_redis_client
from ccam_backend.auth.middleware import verify_hmac
from ccam_backend.models.worker_job import WorkerJob
from ccam_backend.schemas.jobs import JobEnqueueRequest, JobResponse, JobListResponse
from ccam_backend.audit.logger import AuditLogger
import redis.asyncio as aioredis

router = APIRouter(tags=["jobs"])


def _job_to_response(job: WorkerJob) -> JobResponse:
    return JobResponse(
        id=job.id,
        tenant_id=job.tenant_id,
        status=job.status,
        microflow_yaml=job.microflow_yaml,
        payload=job.payload,
        idempotency_key=job.idempotency_key,
        result=job.result_json,
        error_message=job.error_message,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        created_at=job.created_at,            # type: ignore[arg-type]
        started_at=job.started_at,             # type: ignore[arg-type]
        completed_at=job.completed_at,          # type: ignore[arg-type]
    )


@router.post("/jobs", response_model=JobResponse, status_code=201)
async def enqueue_job(
    request: Request,
    body: JobEnqueueRequest,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(verify_hmac),
    redis: aioredis.Redis = Depends(get_redis_client),
):
    """Enqueue a microflow job for execution.

    Accepts inline microflow YAML + optional payload + optional idempotency_key.
    Creates a WorkerJob record (status=queued) and enqueues an ARQ job.
    """
    tenant_id, signed_key = auth
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Create job record
    job = WorkerJob(
        tenant_id=tenant_id,
        microflow_yaml=body.microflow_yaml,
        payload=body.payload,
        idempotency_key=body.idempotency_key,
        status="queued",
        max_retries=5,
    )
    db.add(job)
    await db.flush()

    # Enqueue ARQ job
    from ccam_backend.redis_client import arq_pool
    if arq_pool is None:
        raise HTTPException(status_code=503, detail="ARQ pool not initialized")

    await arq_pool.enqueue_job(
        "execute_microflow_job",
        body.microflow_yaml,
        body.payload,
        job.id,
        body.idempotency_key,
    )

    # Audit log
    logger = AuditLogger(db)
    await logger.log(
        tenant_id=tenant_id,
        action="job.enqueued",
        actor_type="api_key",
        actor_id=signed_key[:16] if signed_key else "unknown",
        target_type="worker_job",
        target_id=job.id,
        after={
            "microflow_name": None,  # Not parsed at enqueue time
            "idempotency_key": body.idempotency_key,
        },
    )

    await db.commit()
    return _job_to_response(job)


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    request: Request,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(verify_hmac),
    page: int = 1,
    page_size: int = 50,
    status_filter: str | None = None,
):
    """List worker jobs for the tenant, newest first.

    Optional status_filter: queued, running, completed, failed, dlq
    """
    tenant_id, _ = auth
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Count
    count_query = select(func.count()).select_from(WorkerJob).where(
        WorkerJob.tenant_id == tenant_id,
    )
    if status_filter:
        count_query = count_query.where(WorkerJob.status == status_filter)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch page
    query = (
        select(WorkerJob)
        .where(WorkerJob.tenant_id == tenant_id)
        .order_by(WorkerJob.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if status_filter:
        query = query.where(WorkerJob.status == status_filter)
    result = await db.execute(query)
    jobs = result.scalars().all()

    items = [_job_to_response(j) for j in jobs]
    return JobListResponse(items=items, total=total)


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    request: Request,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(verify_hmac),
):
    """Get a specific worker job by ID with its status and result."""
    tenant_id, _ = auth
    if tenant_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    result = await db.execute(
        select(WorkerJob).where(
            WorkerJob.id == job_id,
            WorkerJob.tenant_id == tenant_id,
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return _job_to_response(job)
