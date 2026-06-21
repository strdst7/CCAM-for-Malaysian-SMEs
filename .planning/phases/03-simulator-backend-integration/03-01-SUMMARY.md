---
phase: 03-simulator-backend-integration
plan: 01
subsystem: backend
tags:
  - integrate
  - simulate
  - api
  - models
  - schemas
  - migration
depends_on:
  requires:
    - "Phase 1 (ccam_sim deterministic simulator engine)"
    - "Phase 2 (FastAPI backend foundation with models, auth, audit)"
  provides:
    - "Scenario versioned SQLAlchemy model"
    - "Pydantic request/response schemas"
    - "POST /api/v1/simulate endpoint"
    - "GET /api/v1/simulate/{run_id} endpoint"
    - "Alembic migration 002 for scenarios table"
  affects:
    - "backend/src/ccam_backend/main.py (new router mounted)"
    - "backend/pyproject.toml (ccam-sim dependency added)"
    - "backend/src/ccam_backend/models/__init__.py (Scenario registered)"
tech-stack:
  added:
    - "ccam-sim (editable path dependency via uv)"
  patterns:
    - "Thread pool execution for sync simulator: loop.run_in_executor(None, run_simulation)"
    - "AuditLogger integration for all simulation actions (completed/rejected/failed)"
    - "Dual input mode: inline YAML string or structured JSON fields"
    - "SafetyError -> HTTP 400 with descriptive detail"
key-files:
  created:
    - "backend/src/ccam_backend/models/scenario.py"
    - "backend/src/ccam_backend/schemas/simulation.py"
    - "backend/src/ccam_backend/schemas/__init__.py"
    - "backend/src/ccam_backend/api/simulate.py"
    - "backend/alembic/versions/002_create_scenarios.py"
  modified:
    - "backend/src/ccam_backend/models/__init__.py"
    - "backend/src/ccam_backend/main.py"
    - "backend/pyproject.toml"
decisions:
  - "D-05: Scenario model fields: id, tenant_id, name, description, yaml, version_number, is_latest, is_active, tags, created_at, updated_at"
  - "D-06: POST /simulate runs via loop.run_in_executor(None, run_simulation) thread pool"
  - "D-07: Response returns full KPIResult + metadata (run_id, seed, duration_ms)"
  - "D-08: SafetyError -> HTTP 400 with detail message"
  - "D-09: Input accepts both YAML string and structured JSON fields"
  - "D-10: seed is optional; auto-generated if omitted"
  - "D-11: GET /simulate/{run_id} returns stored SimulationRun with KPIs"
  - "D-16: All simulation actions audit-logged via AuditLogger"
metrics:
  duration_minutes: 3
  completed_date: "2026-06-21"
---

# Phase 3 Plan 01: Simulation Endpoint Foundation Summary

Integrated the deterministic simulator engine (`ccam_sim`) into the FastAPI backend REST API by creating the Scenario versioned model, Pydantic schemas, and POST/GET simulate endpoints with thread-pool execution, audit logging, and run persistence.

## Requirements Fulfilled

- **INT-01**: POST /simulate API endpoint wrapping the simulator engine — complete
- **INT-03**: Simulation run storage with KPI snapshots — complete

## Key Deliverables

### 1. Scenario Model + Migration
- Versioned `scenarios` table with ULID PK, tenant FK, name, description, YAML, version_number, is_latest, is_active, and tags
- Composite indexes for (tenant_id, name, is_latest) and (tenant_id, created_at) queries
- Alembic migration 002 chains from 001

### 2. Pydantic Schemas
- `SimulateRequestBody` — accepts inline YAML, structured JSON fields, or saved scenario reference
- `SimulateResponse` — run_id, seed, duration_ms, KPIResult
- `SimulationRunMetadata` — full run details for GET endpoint
- `KPIResultResponse` — mirrors ccam_sim KPIResult dataclass
- `ErrorResponse` — standard error shape

### 3. Simulation Endpoints
- **POST /api/v1/simulate** — runs deterministic simulation via thread pool:
  - YAML input → `load_scenario()` → `run_in_executor`
  - Structured JSON → direct dataclass construction
  - Safety gate rejection → HTTP 400
  - All results persisted with KPI snapshots
  - Audit-logged on completion, rejection, or failure
- **GET /api/v1/simulate/{run_id}** — retrieves past run with tenant-scoped query

### 4. Dependency Wiring
- `ccam-sim` added as editable path dependency via `uv add --editable ../`
- `simulate_router` mounted at `/api/v1` in main.py

## Known Stubs

| File | Line | Stub | Reason |
|------|------|------|--------|
| `backend/src/ccam_backend/api/simulate.py` | ~166 | `"Saved scenario reference not yet implemented"` (HTTP 501) | Saved scenario resolution depends on Scenario CRUD endpoints from plan 03-02 |

## Deviations from Plan

None — plan executed exactly as written.

## Threat Surface

No new threat surface introduced beyond the plan's threat register (T-03-01 through T-03-05).

## Self-Check

- [x] Scenario model imports correctly
- [x] Migration 002 chains from 001 (Revises: 001)
- [x] Simulate router imports correctly
- [x] Simulate router mounted in main.py (include_router found)
- [x] ccam_sim importable from backend
- [x] Schemas validation works (SimulateRequestBody created and validated)
- [x] 3 tasks completed, 4 commits created

## Self-Check: PASSED
