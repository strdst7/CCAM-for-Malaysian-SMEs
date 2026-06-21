# Phase 3: Simulator-Backend Integration - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 3 wires the simulator engine (`ccam_sim` package) into the backend REST API. This includes a `POST /simulate` endpoint that wraps `run_simulation()`, versioned scenario CRUD with full REST endpoints, simulation run persistence, and tenant provisioning via REST API. The safety gate (INT-04) is deferred to Phase 4.

**What is delivered:**
- `POST /api/v1/simulate` — run simulation with inline YAML or structured JSON (or reference a saved scenario by ID/name)
- `GET /api/v1/simulate/{run_id}` — retrieve past simulation run results
- Scenario CRUD at `/api/v1/scenarios` — versioned scenarios with full RESTful endpoints
- Tenant provisioning at `POST /api/v1/tenants` with `SETUP_TOKEN` env var for bootstrap
- Simulation runs persisted in `simulation_runs` table with KPI snapshots

**What is NOT delivered (deferred):**
- Safety gate enforcement (INT-04) — deferred to Phase 4 when there are actual changes to gate

</domain>

<decisions>
## Implementation Decisions

### Scenario Storage
- **D-01:** Scenario has its own versioned DB table (`scenarios`) with `version_number` and `is_latest` columns. Each update creates a new row (immutable version history).
- **D-02:** POST /simulate accepts both: (a) inline YAML string in `scenario_yaml` field, or (b) structured JSON fields matching the Scenario dataclass, or (c) `scenario_id` / `scenario_name` referencing a saved scenario.
- **D-03:** Post /simulate resolves scenario references by `scenario_id` (ULID) or `scenario_name` (resolves to latest active version).
- **D-04:** Full RESTful CRUD on scenarios: POST (create), GET (list), GET /{id} (read), PUT /{id} (update — creates new version), DELETE /{id} (soft-delete via `is_active`).
- **D-05:** Scenario model fields: `id`, `tenant_id`, `name`, `description`, `yaml`, `version_number`, `is_latest`, `is_active`, `tags` (JSON), `created_at`, `updated_at`.

### Simulation Execution
- **D-06:** POST /simulate runs the simulator synchronously via `loop.run_in_executor(None, run_simulation)` (thread pool). No ARQ background job — result is immediate.
- **D-07:** Response returns full KPIResult + metadata (`run_id`, `seed`, `duration_ms`, scenario info) in the response body.
- **D-08:** Safety gate rejections (`SafetyError`) return HTTP 400 with `{"detail": "reason"}`.
- **D-09:** Input accepts both YAML string (`{"scenario_yaml": "..."}`) and structured JSON fields. Backend dispatches to `load_scenario()` or direct dataclass construction.
- **D-10:** `seed` is optional. If provided, use it (deterministic replay). If omitted, server generates a random seed and includes it in the response.
- **D-11:** GET /api/v1/simulate/{run_id} returns the stored SimulationRun with KPIs, status, input, seed.

### API URL Structure
- **D-12:** Flat under `/api/v1/`: `/api/v1/simulate`, `/api/v1/simulate/{run_id}`, `/api/v1/scenarios`, `/api/v1/scenarios/{id}`, `/api/v1/tenants`.

### Safety Gate
- **D-13:** INT-04 safety gate entirely deferred to Phase 4. Phase 3 implements no safety gate code — not even a standalone function.

### Tenant Provisioning
- **D-14:** POST /api/v1/tenants included in Phase 3. Creates Tenant + Admin User + API key + audit log entries (mirrors CLI `provision-tenant` logic).
- **D-15:** Endpoint is public but gated by `SETUP_TOKEN` environment variable. Request must include `Authorization: Bearer <setup_token>`. Token set during deployment, can be rotated.

### Audit Logging
- **D-16:** All scenario CRUD operations, simulation runs, and tenant provisioning actions are audit-logged using the Phase 2 `AuditLogger`.

### OpenCode's Discretion
- Thread pool size for run_in_executor: default Python thread pool is sufficient for v1.
- Scenario YAML size limit: 1MB as a reasonable default (configurable).
- Detailed Pydantic schemas for request/response bodies are implementation details.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Definition & Requirements
- `.planning/ROADMAP.md` §52-62 — Phase 3 goal, dependencies, success criteria
- `.planning/REQUIREMENTS.md` §28-33 — INT-01 through INT-04 requirements

### Simulator (consumable library)
- `src/ccam_sim/__init__.py` — Public API: `run_simulation()`, `load_scenario()`, `Scenario`, `SimState`
- `src/ccam_sim/pipeline.py` — `run_simulation()` implementation (sync function)
- `src/ccam_sim/safety.py` — `validate_scenario()` gate 1, `check_per_tick()` gate 2, `SafetyError`
- `src/ccam_sim/models/scenario.py` — `Scenario` dataclass definition
- `src/ccam_sim/models/kpi_result.py` — `KPIResult` dataclass definition
- `src/ccam_sim/models/state.py` — `SimState` with `station_states`, `stock_levels`, `events`

### Backend (existing)
- `backend/src/ccam_backend/main.py` — FastAPI app with AuthMiddleware, lifespan, route mounting
- `backend/src/ccam_backend/api/health.py` — Existing router pattern for new routes
- `backend/src/ccam_backend/api/deps.py` — `get_db()` and `get_redis_client()` dependency injection
- `backend/src/ccam_backend/models/simulation_run.py` — Existing `SimulationRun` model
- `backend/src/ccam_backend/models/__init__.py` — All entity models
- `backend/src/ccam_backend/audit/logger.py` — `AuditLogger` for audit logging actions
- `backend/src/ccam_backend/auth/middleware.py` — `PUBLIC_PATHS` for unauthenticated routes
- `backend/src/ccam_backend/cli/tenant.py` — CLI tenant provisioning logic to mirror in REST

### Prior Phase Context
- `.planning/phases/02-backend-foundation/02-CONTEXT.md` — Phase 2 implementation decisions (D-01 through D-09)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ccam_sim` package: Fully importable, sync `run_simulation()` can be called from thread pool. Already tested with 44 tests.
- Phase 2 `AuditLogger`: Ready for Phase 3 actions. `logger.log(tenant_id, action, actor_type, actor_id, target_type, target_id, before, after)`.
- Phase 2 `get_db()` / `get_redis_client()` dependencies: Standard pattern for new endpoints.
- Phase 2 DI pattern (`api/deps.py`): Extend with `get_tenant_id()` from `request.state.tenant_id`.
- Phase 2 CLI `_provision_tenant()`: Core tenant creation logic can be shared with the REST endpoint.

### Established Patterns
- **Router-per-resource:** Each resource domain gets its own `APIRouter` (e.g., `api/simulate.py`, `api/scenarios.py`, `api/tenants.py`), mounted in `main.py`.
- **Auth via middleware:** `AuthMiddleware` checks HMAC-SHA256. Public paths in `PUBLIC_PATHS` set. New public paths (e.g., POST /tenants with setup token, health) must be added there.
- **Async DB sessions:** All DB access through `get_db()` async generator.

### Integration Points
- `main.py` adds new routers: `app.include_router(simulate_router, prefix="/api/v1")`, etc.
- POST /tenants needs special auth handling: bypass HMAC auth in middleware (add to PUBLIC_PATHS), authenticate via `Authorization: Bearer <setup_token>` check inline.
- `PUBLIC_PATHS` in `middleware.py` needs: `/api/v1/tenants` added.
- Simulation runs store `tenant_id` from `request.state.tenant_id` (set by AuthMiddleware).
- Scenario model is new — needs a new SQLAlchemy entity, Alembic migration 002.

</code_context>

<specifics>
## Specific Ideas

No specific references — standard FastAPI + SQLAlchemy patterns apply.

</specifics>

<deferred>
## Deferred Ideas

- **Safety gate enforcement (INT-04):** Deferred to Phase 4 when menu/procurement/microflow endpoints exist to gate against.

</deferred>

---

*Phase: 3-Simulator-Backend Integration*
*Context gathered: 2026-06-21*
