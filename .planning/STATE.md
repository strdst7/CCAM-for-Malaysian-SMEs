# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-21)

**Core value:** Nothing touches a real restaurant until the simulator proves it's safe.
**Current focus:** Phase 4 — Microflows & Worker Jobs

## Current Position

Phase: 4 of 5 (Microflows & Worker Jobs)
Plan: 1 of 2 in current phase
Status: Executing
Last activity: 2026-06-21 — Plan 04-01 complete (DSL compiler + bytecode executor library)

Progress: [████████████░░░░░░░░] 50% (1/2 plans)

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
| 4 - Microflows & Worker Jobs | 1 | In progress | 18 min |

**Recent Trend:**
- Last plans: 02-03 → 03-01 → 03-02 → 04-01
- Trend: Phase 1 + Phase 2 + Phase 3 + Plan 04-01 delivered

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

Last session: 2026-06-21 (Plan 04-01 complete — Microflow DSL compiler + bytecode executor library)
Stopped at: Plan 04-01 delivered — 1 of 2 plans complete in Phase 4
Resume file: .planning/phases/04-microflows-worker-jobs/04-02-PLAN.md

### Plan 04-01 Deliverables

| File | Purpose |
|------|---------|
| `mcf/pyproject.toml` | Standalone ccam-mcf package configuration |
| `mcf/src/ccam_mcf/__init__.py` | Public API exports |
| `mcf/src/ccam_mcf/models.py` | Microflow data models + bytecode instruction format |
| `mcf/src/ccam_mcf/compiler.py` | YAML-to-bytecode compiler with validation |
| `mcf/src/ccam_mcf/executor.py` | Deterministic stack-based bytecode executor |
| `mcf/src/ccam_mcf/exceptions.py` | CompileError and ExecError |
| `mcf/tests/test_mcf_unit.py` | 15-unit test suite (all pass) |

### Bugs Fixed During Execution

1. **Executor IP increment after jumps**: `run()` loop unconditionally advanced `self._ip += 1` after every instruction, including JUMP/JUMP_IF_FALSE — caused skipped targets
2. **Switch step not emitting case blocks**: JUMP fixups pointed to step blocks that were never emitted
3. **Switch single LOAD consumed by COMPARE**: First case's COMPARE consumed the source value, subsequent cases had nothing to compare
4. **Package forward imports**: `__init__.py` imported compiler/executor modules before they existed — required stub files
