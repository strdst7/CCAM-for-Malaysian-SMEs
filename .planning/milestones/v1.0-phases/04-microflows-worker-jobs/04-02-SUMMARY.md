---
phase: 04-microflows-worker-jobs
plan: 02
subsystem: worker-jobs
tags: [arq, worker, redis, worker-job, microflow, alembic, fastapi]

requires:
  - phase: 04-microflows-worker-jobs
    plan: 01
    provides: ccam-mcf library (compile_microflow, BytecodeExecutor, MicroflowContext)

provides:
  - WorkerJob SQLAlchemy model with status/retry/idempotency fields
  - Alembic migration 003 — worker_jobs table
  - ARQ worker function (execute_microflow_job) with retry/DLQ and idempotency
  - POST/GET /api/v1/jobs endpoints
  - Integration test scaffold (12 stubs)

affects:
  - 04-microflows-worker-jobs phase (next plans can use worker infrastructure)
  - 05-advanced-engines phase (workers will consume engine output)

tech-stack:
  added:
    - ccam-mcf dependency in backend (editable path)
    - WorkerSettings ARQ configuration class
  patterns:
    - ARQ worker with async DB access for job status tracking
    - Idempotency via key lookup before execution
    - Retry/DLQ via exception handling with attempt tracking
    - Tenant-scoped job querying (all endpoints filter by tenant_id)

key-files:
  created:
    - backend/src/ccam_backend/models/worker_job.py
    - backend/src/ccam_backend/schemas/jobs.py
    - backend/src/ccam_backend/workers/__init__.py
    - backend/src/ccam_backend/workers/mcf_worker.py
    - backend/src/ccam_backend/api/jobs.py
    - backend/alembic/versions/003_create_worker_jobs.py
    - backend/tests/test_integration_phase4.py
  modified:
    - backend/pyproject.toml
    - backend/src/ccam_backend/models/__init__.py
    - backend/src/ccam_backend/schemas/__init__.py
    - backend/src/ccam_backend/main.py

key-decisions:
  - "actions={} in MicroflowContext is intentional — action registration is deployment-specific and deferred"
  - "Worker runs independently from FastAPI (arq ccam_backend.workers.mcf_worker.WorkerSettings)"
  - "Audit logging at enqueue time only (not at status transitions) — avoids worker coupling to audit infra"
  - "Status transitions are server-only via SQLAlchemy; no client-accessible status update endpoint"
  - "DLQ is same DB table (status='dlq') — no separate queue in v1"

patterns-established:
  - "Worker: idempotency check -> fetch job -> mark running -> compile -> execute -> mark complete/fail/dlq"
  - "API: auth -> create record -> enqueue ARQ -> audit log -> commit -> respond"
  - "Tenant isolation: all queries filter by WorkerJob.tenant_id"

requirements-completed: [MCF-02]
duration: 1min
completed: 2026-06-21
---

# Phase 4 Plan 02: ARQ Worker Job Infrastructure — Retry/DLQ/Idempotency

**WorkerJob model, ARQ worker function with retry/dead-letter queue and idempotency, job enqueue/status API endpoints, and integration test scaffold — wraps the microflow DSL library for FIFO job execution**

## Performance

- **Duration:** 1 min
- **Started:** 2026-06-21T13:29:45+08:00
- **Completed:** 2026-06-21T13:30:41+08:00
- **Tasks:** 3
- **Files created:** 7
- **Files modified:** 4

## Accomplishments

- **WorkerJob model:** SQLAlchemy model with `tenant_id`, `microflow_yaml`, `payload`, `idempotency_key`, `status` (queued/running/completed/failed/dlq), `result_json`, `error_message`, `retry_count`, `max_retries`, `started_at`, `completed_at` — follows the existing ULIDMixin + TimestampMixin pattern
- **Pydantic schemas:** `JobEnqueueRequest` (with YAML + optional payload + optional idempotency key), `JobResponse`, `JobListResponse` — ready for API validation
- **Alembic migration 003:** Creates `worker_jobs` table with indexes on `tenant_id` and `idempotency_key`, chains from migration 002
- **ARQ worker function:** `execute_microflow_job` — checks idempotency key, fetches job record, compiles YAML to bytecode via `ccam_mcf.compile_microflow`, executes via `BytecodeExecutor`, tracks status lifecycle (queued → running → completed/failed/dlq), handles retry/DLQ transitions based on attempt count
- **WorkerSettings class:** Registers the worker function with ARQ, configures `max_tries=5`, `job_retry_after=60` (exponential backoff), `keep_result=86400` (1 day)
- **Job API endpoints:**
  - `POST /api/v1/jobs` — Creates WorkerJob record, enqueues ARQ job, logs audit event
  - `GET /api/v1/jobs` — Lists jobs with pagination and optional status filter, tenant-scoped
  - `GET /api/v1/jobs/{id}` — Gets single job by ID, tenant-scoped (cross-tenant returns 404)
- **ccam-mcf dependency:** Added to backend `pyproject.toml` as editable path via uv sources, importable and verified
- **Integration test scaffold:** 12 test stubs across 5 groups (enqueue, status, retry/DLQ, idempotency, auth)

## Task Commits

Each task was committed atomically:

1. **Task 1: WorkerJob model, Pydantic schemas, migration 003** — `b76cdf3` (feat)
2. **Task 2: ARQ worker function with retry/DLQ and idempotency** — `c6a4f58` (feat)
3. **Task 3: Job enqueue/status API, router wiring, test scaffold** — `4dd8e21` (feat)

## ARQ Worker Invocation

The worker process runs independently from the FastAPI server:

```bash
arq ccam_backend.workers.mcf_worker.WorkerSettings
```

Both the FastAPI server and the ARQ worker share the same Redis instance. The FastAPI server enqueues jobs via `arq_pool.enqueue_job()`; the worker picks them up via Redis.

## Known Stubs

| Stub | File | Reason |
|------|------|--------|
| `actions={}` | `backend/src/ccam_backend/workers/mcf_worker.py` | Action registration is deployment-specific; will be wired in future phases |
| All 12 test methods use `...` | `backend/tests/test_integration_phase4.py` | Tests require live PostgreSQL + Redis (conftest fixtures not yet created) |

## Threat Surface Compliance

All threat mitigations from the plan's threat model are implemented:
- **T-04-01 (DoS):** HMAC auth on POST/GET endpoints prevents anonymous enqueue
- **T-04-02 (Spoofing):** ARQ enqueue is internal via `arq_pool.enqueue_job()`, not directly exposed
- **T-04-03 (Tampering):** Status transitions are server-only via SQLAlchemy; no client-accessible status update
- **T-04-04 (Info Disclosure):** All queries tenant-scoped by `tenant_id`; cross-tenant access returns 404
- **T-04-05 (Repudiation):** All job enqueue actions logged via AuditLogger
- **T-04-06 (Elevation):** Accepted per D-01 — no sandboxing applied yet
- **T-04-07 (DLQ overflow):** Accepted — no automatic cleanup in v1

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- [x] `backend/src/ccam_backend/models/worker_job.py` — WorkerJob model with all required fields
- [x] `backend/alembic/versions/003_create_worker_jobs.py` — chains from 002_create_scenarios
- [x] `backend/src/ccam_backend/workers/mcf_worker.py` — execute_microflow_job function + WorkerSettings
- [x] `backend/src/ccam_backend/api/jobs.py` — POST /jobs, GET /jobs, GET /jobs/{id}
- [x] `backend/src/ccam_backend/main.py` — jobs_router wired
- [x] `backend/pyproject.toml` — ccam-mcf dependency added, uv source configured
- [x] `backend/tests/test_integration_phase4.py` — all 12 test stubs present
- [x] All 3 commits exist (b76cdf3, c6a4f58, 4dd8e21)

---

*Phase: 04-microflows-worker-jobs*
*Completed: 2026-06-21*
