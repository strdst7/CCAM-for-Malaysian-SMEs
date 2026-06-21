"""Microflow execution worker — consumes ARQ jobs, executes DSL bytecode, tracks status."""
from datetime import datetime, timezone
from sqlalchemy import select
from ccam_backend.database import async_session_factory
from ccam_backend.models.worker_job import WorkerJob
from ccam_backend.redis_client import _redis_settings_from_url
from ccam_backend.config import settings
from ccam_mcf import compile_microflow, BytecodeExecutor, MicroflowContext


async def execute_microflow_job(ctx, microflow_yaml: str, payload: dict | None,
                                job_id: str, idempotency_key: str | None = None) -> dict:
    """Execute a microflow DSL definition as an ARQ worker job.

    Idempotency: if idempotency_key is provided and a completed job exists
    with the same key, return the stored result without re-executing.

    Status lifecycle: queued -> running -> completed|failed|dlq

    Retry/DLQ: ARQ retries on function exception. After max_retries
    attempts, this function catches the final failure and sets status to 'dlq'.
    """
    async with async_session_factory() as db:
        # --- Idempotency check ---
        if idempotency_key:
            result = await db.execute(
                select(WorkerJob).where(
                    WorkerJob.idempotency_key == idempotency_key,
                    WorkerJob.status == "completed",
                )
            )
            existing = result.scalar_one_or_none()
            if existing is not None:
                # Return stored result without re-execution
                return {"status": "completed", "job_id": existing.id,
                        "result": existing.result_json, "replayed": True}

        # --- Fetch job record ---
        result = await db.execute(select(WorkerJob).where(WorkerJob.id == job_id))
        job = result.scalar_one_or_none()
        if job is None:
            raise ValueError(f"Job {job_id} not found")

        # --- Mark as running ---
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)  # type: ignore[arg-type]
        await db.flush()

        try:
            # --- Compile YAML to bytecode ---
            bytecode = compile_microflow(microflow_yaml)

            # --- Create execution context ---
            context = MicroflowContext(
                payload=payload or {},
                memory={},
                actions={},  # Actions registered separately per deployment
            )

            # --- Execute deterministically ---
            executor = BytecodeExecutor(bytecode, context)
            result_value = executor.run(seed=42)

            # --- Mark as completed ---
            job.status = "completed"
            job.result_json = {"output": result_value}
            job.completed_at = datetime.now(timezone.utc)  # type: ignore[arg-type]

            await db.commit()
            return {"status": "completed", "job_id": job_id,
                    "result": result_value, "replayed": False}

        except Exception as e:
            job.retry_count += 1
            job.error_message = str(e)

            # --- Check if max retries exhausted -> DLQ ---
            attempt = ctx.get("job_try", 1)
            max_tries = getattr(ctx.get("worker"), "max_tries", 5) if ctx.get("worker") else 5

            if attempt >= max_tries:
                job.status = "dlq"
                job.completed_at = datetime.now(timezone.utc)  # type: ignore[arg-type]
                await db.commit()
                return {"status": "dlq", "job_id": job_id, "error": str(e)}
            else:
                # Let ARQ handle the retry (exception propagates -> ARQ retries)
                job.status = "failed"
                await db.commit()
                raise


class WorkerSettings:
    """ARQ worker configuration for microflow execution."""
    functions = [execute_microflow_job]
    redis_settings = _redis_settings_from_url(settings.redis_url)
    max_tries = 5                # Total attempts (initial + 4 retries)
    job_retry_after = 60         # Base delay seconds (ARQ applies exponential backoff)
    keep_result = 86400          # Keep job results for 1 day
    keep_result_failed = 86400   # Keep failed job results for 1 day
