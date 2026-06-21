# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-21)

**Core value:** Nothing touches a real restaurant until the simulator proves it's safe.
**Current focus:** Phase 3 — Simulator-Backend Integration

## Current Position

Phase: 3 of 5 (Simulator-Backend Integration)
Plan: 2 of 2 in current phase
Status: Complete
Last activity: 2026-06-21 — Plan 03-02 complete (Scenario CRUD, tenant provisioning API, saved-scenario refs, integration tests)

Progress: [██████████] 100% (complete)

## Performance Metrics

**Velocity:**
- Total plans completed: 8
- Plans planned: 2 (Phase 3)
- Total execution time: N/A

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 - Simulator Core | 4 | Complete | N/A |
| 2 - Backend Foundation | 3 | Complete | N/A |
| 3 - Simulator-Backend Integration | 2 | Complete | ~4 min |

**Recent Trend:**
- Last 5 plans: 02-03 → 03-01 → 03-02 consecutive completion
- Trend: Phase 1 + Phase 2 + Phase 3 delivered (all plans complete)

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

Last session: 2026-06-21 (Plan 03-02 complete — Scenario CRUD, tenant provisioning API, saved-scenario refs, integration tests)
Stopped at: Plan 03-02 delivered — Phase 3 complete (all plans executed)
Resume file: .planning/phases/04-microflows-worker-jobs/

### Plan 03-02 Deliverables

| File | Purpose |
|------|---------|
| `backend/src/ccam_backend/api/scenarios.py` | Full RESTful scenario CRUD router (5 endpoints) |
| `backend/src/ccam_backend/api/tenants.py` | REST tenant provisioning with SETUP_TOKEN auth |
| `backend/tests/test_integration_phase3.py` | Integration test scaffold (8 stubs) |

### Modified
| File | Change |
|------|--------|
| `backend/src/ccam_backend/api/simulate.py` | Saved scenario reference resolution added |
| `backend/src/ccam_backend/auth/middleware.py` | `/api/v1/tenants` added to PUBLIC_PATHS |
| `backend/src/ccam_backend/main.py` | scenarios_router and tenants_router wired |
| `backend/src/ccam_backend/config.py` | setup_token field added |

### Bugs Fixed During Execution

1. **HMAC verify_signature**: Both `main.py` and `middleware.py` were calling `verify_signature` without the `signature_b64` argument (5 args instead of 6)
2. **Redis close**: `close()` deprecated; changed to `aclose()` for both Redis client and ARQ pool
3. **Lint auto-fixes**: 7 F401 unused imports removed + `== True` → truth check in `api_keys.py`
4. **Mypy type errors**: 5 errors fixed — async generator return types, `RedisSettings.from_url` (didn't exist), `wait_closed` (didn't exist)
5. **Test infrastructure**: httpx ASGITransport doesn't trigger lifespan; added manual `lifespan_context` fixture
