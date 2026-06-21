# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-21)

**Core value:** Nothing touches a real restaurant until the simulator proves it's safe.
**Current focus:** Phase 5 — Advanced Engines

## Current Position

Phase: 5 of 5 (Advanced Engines)
Plan: 4 of 4 in current phase
Status: Complete — 4 plans executed across 2 waves
Last activity: 2026-06-21 — Phase 5 executed (all 5 engines: parser, menu, forecast, procurement, notification + backend integration)

Progress: [####################] 100% (4 of 4 plans complete)

## Performance Metrics

**Velocity:**
- Total plans completed: 9
- Plans planned: 2 (Phase 4)
- Total execution time: N/A

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 - Simulator Core | 4 | Complete | N/A |
| 2 - Backend Foundation | 3 | Complete | N/A |
| 3 - Simulator-Backend Integration | 2 | Complete | ~4 min |
| 4 - Microflows & Worker Jobs | 2 | Complete | 9 min |
| 5 - Advanced Engines | 4 | Complete | ~9 min |

**Recent Trend:**
- Last plans: 02-03 → 03-01 → 03-02 → 04-01 → 04-02 → 05-01 → 05-02 → 05-03 → 05-04
- Trend: Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 5 delivered

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- (Roadmap): 5-phase structure approved — Simulator-first, CLI-first, deterministic simulation with seeded RNG
- (Architecture): Ground-up rebuild on FastAPI + PostgreSQL + Kubernetes — Firebase/Express monolith replaced
- (Governance): Simulator is the governor of all subsystems — no production change without validation
- (Architecture): Python 3.14 + Click + PyYAML + pytest + uv — deterministic CLI simulator
- (Data): KPIResult typed dataclass (not plain dicts)
- (RNG): Isolated random.Random(seed) instances, never global random.seed()
- (Time): Integer microseconds for simulation time
- (Pipeline): demand → order → kitchen → stock → kpi
- (Safety): Gate 1 at load, Gate 2 per-tick
- (Events): kw_only=True on all event dataclasses
- (Phase 2): Same repo, separate packages (backend/ + ccam_sim/)
- (Phase 2): Flat tenant-scoped schema with ULID PKs + tenant_id, Alembic migrations
- (Phase 2): Redis for sessions + cache + ARQ task queue
- (Phase 2): HMAC-SHA256 auth with versioned key rotation (body+path+timestamp, 300s skew)
- (Phase 2): RLS-enforced INSERT-only audit log with before/after diffs
- (Phase 2): CLI-first tenant provisioning, REST deferred to Phase 3
- (Phase 2): Multi-stage Dockerfile, Helm chart (6 templates), GitHub Actions CI
- (Phase 2): Ruff + mypy lint/typecheck enforced in CI
- (Phase 2): API key format `v1:base64(32 bytes)`, bcrypt hashed, versioned rotation
- (Phase 3): Scenario has its own versioned DB table (scenarios) with version_number and is_latest
- (Phase 3): POST /simulate accepts inline YAML, structured JSON, or saved scenario ref
- (Phase 3): POST /simulate runs synchronous simulator via loop.run_in_executor (thread pool)
- (Phase 3): SafetyError from simulator returns HTTP 400 with detail message
- (Phase 3): seed is optional; server auto-generates if omitted and returns it in response
- (Phase 3): GET /simulate/{run_id} tenant-scoped retrieval with KPI snapshot
- (Phase 3): All simulation actions audit-logged (completed/rejected/failed)
- (Phase 4): Stack-based VM for microflow DSL — 7 opcodes (LOAD/LOAD_CONST/COMPARE/JUMP_IF_FALSE/JUMP/CALL/RETURN)
- (Phase 4): Two-pass compilation: validate → resolve refs → detect cycles → linearize DAG → emit instructions with jump fixup
- (Phase 4): Switch step emits LOAD per case (COMPARE consumes both stack values)
- (Phase 4): Action handlers injected via dict (not imported) — standalone library
- (Phase 4): actions={} in MicroflowContext is intentional — action registration is deployment-specific and deferred
- (Phase 4): Worker runs independently from FastAPI (arq ccam_backend.workers.mcf_worker.WorkerSettings)
- (Phase 4): Audit logging at enqueue time only — avoids worker coupling to audit infra
- (Phase 4): Status transitions are server-only via SQLAlchemy; no client-accessible status update endpoint
- (Phase 4): DLQ is same DB table (status='dlq') — no separate queue in v1

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| REST API | Tenant provisioning API | Deferred to Phase 3 | 2026-06-21 |
| Audit | Cryptographic hash chain for audit log | Not needed for v1 | 2026-06-21 |

## Session Continuity

Last session: 2026-06-21 (Phase 5 complete — Advanced Engines)
Stopped at: Plan 05-04 delivered — 4 of 4 plans complete in Phase 5
Resume file: .planning/phases/05-advanced-engines/

### Phase 4 Deliverables

| Plan | Files | Purpose |
|------|-------|---------|
| 04-01 | `mcf/` (7 files) | Microflow DSL compiler + bytecode executor library (MCF-01) |
| 04-02 | `backend/` (7 created, 4 modified) | ARQ worker job infrastructure with retry/DLQ/idempotency (MCF-02) |

### Phase 5 Decisions

- (Phase 5): ROADMAP overrides stale PROJECT.md Out of Scope — all 5 engines in scope
- (Phase 5): Standalone packages under `engines/` with own `pyproject.toml` — names: `ccam_parser`, `ccam_menu`, `ccam_forecast`, `ccam_procurement`, `ccam_notification`
- (Phase 5): Parser regex-first (80%+ patterns), DistilBERT NER ONNX fallback when confidence < 0.6
- (Phase 5): Menu uses Google OR-Tools CP-SAT MILP solver with hard safety constraints (no negative margin, no price below cost)
- (Phase 5): Forecast ensemble all 3 (LSTM + Prophet + ARIMA), simulator-generated training data, batch retraining via ARQ worker
- (Phase 5): LSTM requires tensorflow (optional dep — cp314 has no TF wheels); Prophet + ARIMA work without it
- (Phase 5): Procurement ABC adapter interface with v1 email-based PDF PO adapter (SendGrid/SMTP)
- (Phase 5): Notifications email (SendGrid/SMTP) + in-app (in-memory store) only in v1
- (Phase 5): Sim validation required for menu + forecast changes before production
- (Phase 5): Safety gate (INT-04) still deferred — not in Phase 5 scope

### Plans Completed

- 04-01: Microflow DSL Compiler & Bytecode Executor Library — 3 tasks, 7 files
- 04-02: ARQ Worker Job Infrastructure — 3 tasks, 7 files created, 4 files modified
- 05-01: Parser + Menu Engine — 2 tasks, 14 files
- 05-02: Forecast Engine — 3 tasks, 11 files
- 05-03: Procurement + Notification Engine — 2 tasks, 16 files
- 05-04: Backend Integration — 3 tasks, 15 files created/modified

### Phase 5 Deliverables

| Plan | Files | Purpose |
|------|-------|---------|
| 05-01 | `engines/parser/` (7 files) | Regex-first + DistilBERT ONNX NER parser pipeline (ENG-01) |
| 05-01 | `engines/menu/` (7 files) | OR-Tools CP-SAT MILP solver with safety constraints (ENG-02) |
| 05-02 | `engines/forecast/` (11 files) | LSTM + Prophet + ARIMA ensemble, trainer, ARQ worker (ENG-03) |
| 05-03 | `engines/procurement/` (8 files) | Supplier ABC, PDF PO gen, email adapter (ENG-04) |
| 05-03 | `engines/notification/` (8 files) | Email + in-app channels, notification router (ENG-05) |
| 05-04 | `backend/` (15 files) | 3 DB models, migration 004, 5 API routers, 2 ARQ workers, main.py wiring |
