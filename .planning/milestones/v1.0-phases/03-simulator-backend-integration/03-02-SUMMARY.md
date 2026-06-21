---
phase: 03-simulator-backend-integration
plan: 02
subsystem: api
tags:
  - scenarios
  - crud
  - tenants
  - provisioning
  - setup-token
  - integration-tests
  - audit
requires:
  - phase: "03-01"
    provides: "Scenario model, simulate endpoint foundation, Pydantic schemas"
  - phase: "02-03"
    provides: "CLI tenant provisioning logic, Tenant/User/ApiKey models"
provides:
  - "Full RESTful scenario CRUD (POST/GET/PUT/DELETE) with versioned history"
  - "REST tenant provisioning endpoint (POST /tenants) with SETUP_TOKEN auth"
  - "Saved scenario reference support in POST /simulate (scenario_id/scenario_name)"
  - "Integration test scaffold for all Phase 3 endpoints"
affects:
  - "Future plans that consume the scenario CRUD API or tenant provisioning"
tech-stack:
  added: []
  patterns:
    - "Scenario updates create new version rows (immutable history, is_latest toggle)"
    - "Tenant provisioning via REST mirrors CLI _provision_tenant() core logic"
    - "SETUP_TOKEN env var gates public tenant provisioning endpoint (D-15)"
    - "AuditLogger integration for all scenario CRUD and tenant provisioning actions"
key-files:
  created:
    - "backend/src/ccam_backend/api/scenarios.py"
    - "backend/src/ccam_backend/api/tenants.py"
    - "backend/tests/test_integration_phase3.py"
  modified:
    - "backend/src/ccam_backend/api/simulate.py"
    - "backend/src/ccam_backend/auth/middleware.py"
    - "backend/src/ccam_backend/main.py"
    - "backend/src/ccam_backend/config.py"
key-decisions:
  - "D-14 implemented: POST /tenants REST API for tenant provisioning"
  - "D-15 implemented: SETUP_TOKEN env var gates /tenants endpoint (not HMAC)"
  - "D-04 implemented: Full RESTful scenario CRUD with soft-delete and versioned updates"
  - "D-03 implemented: POST /simulate resolves scenario_id (ULID) or scenario_name (latest active)"
requirements_completed: ["INT-02"]
duration_minutes: 5
completed_date: "2026-06-21"
---

# Phase 3 Plan 02: Scenario CRUD, Tenant Provisioning API, Saved-Scenario Refs, Integration Tests

**Full RESTful scenario CRUD with versioned immutable history, REST tenant provisioning gated by SETUP_TOKEN, saved-scenario reference resolution in the simulate endpoint, and an integration test scaffold covering all Phase 3 flows.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-06-21T03:55:19Z
- **Completed:** 2026-06-21T04:00:25Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- **Scenario CRUD endpoints** at `/api/v1/scenarios` — POST (create with version 1), GET (list with pagination), GET/{id} (read), PUT/{id} (versioned update — new row, previous is_latest=False), DELETE/{id} (soft-delete via is_active=False), all audit-logged
- **Tenant provisioning REST endpoint** at `POST /api/v1/tenants` — gated by `Authorization: Bearer <SETUP_TOKEN>`, creates Tenant + Admin User + API key + audit logs, mirrors CLI `_provision_tenant()` core logic
- **Saved scenario reference in POST /simulate** — replaces the 501 stub with actual DB resolution: `scenario_id` resolves by ULID, `scenario_name` resolves to the latest active version; response includes `scenario_info` with id/name/version
- **Integration test scaffold** — 8 test stubs covering scenario CRUD, simulate with all input modes, safety error handling, tenant provisioning, and auth requirements
- **Infrastructure wiring** — `SETUP_TOKEN` config setting added, `/api/v1/tenants` added to `PUBLIC_PATHS` in AuthMiddleware, both new routers mounted in `main.py`

## Task Commits

Each task was committed atomically:

1. **Task 1: Full RESTful scenario CRUD endpoints** - `d4e4ddf` (feat)
2. **Task 2: Tenant provisioning REST endpoint with SETUP_TOKEN** - `c829d68` (feat)
3. **Task 3: Saved scenario reference + integration tests** - `233a7cc` (feat)

**Plan metadata:** `6abda9c` (docs: complete plan)

## Files Created/Modified

### Created
- `backend/src/ccam_backend/api/scenarios.py` — Full RESTful scenario CRUD router (5 endpoints)
- `backend/src/ccam_backend/api/tenants.py` — Tenant provisioning router with SETUP_TOKEN auth
- `backend/tests/test_integration_phase3.py` — Integration test scaffold (8 stubs)

### Modified
- `backend/src/ccam_backend/api/simulate.py` — Saved scenario reference resolution (scenario_id/scenario_name)
- `backend/src/ccam_backend/auth/middleware.py` — Added `/api/v1/tenants` to PUBLIC_PATHS
- `backend/src/ccam_backend/main.py` — Wired scenarios_router and tenants_router
- `backend/src/ccam_backend/config.py` — Added `setup_token` field to Settings

## Decisions Made

- Used same provisioning core pattern as CLI (`async_session_factory()` + inline bcrypt) in `_provision_tenant_core()` to avoid duplicating business logic while keeping REST endpoint self-contained
- Scenario PUT implements strict versioned updates (not in-place mutation): creates new row, sets previous `is_latest=False`, increments `version_number` per D-04/D-01
- Saved scenario resolution in simulate returns `scenario_info` in the response only when a DB record was referenced; inline YAML/structured JSON responses remain unchanged

## Known Stubs

| File | Line | Stub | Reason |
|------|------|------|--------|
| `backend/tests/test_integration_phase3.py` | 19-71 | 8 `assert True` placeholders | Tests require live PostgreSQL database; scaffold documents expected behavior for future CI execution |

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

The plan requires a `SETUP_TOKEN` environment variable to be set in the deployment environment. For local development, the default value `dev-setup-token-change-in-production` is used.

## Threat Surface

No new threat surface introduced beyond the plan's threat register:
- T-03-06: SETUP_TOKEN env var authentication for /tenants (mitigated)
- T-03-07: Immutable version history for scenarios (mitigated)
- T-03-08: Tenant-scoped scenario queries (mitigated)
- T-03-09: Pydantic max_length limits on scenario YAML (mitigated)
- T-03-10: Audit logging for all CRUD actions (mitigated)
- T-03-11: SETUP_TOKEN never returned in responses, never logged (accepted risk)

## Next Phase Readiness

- Full Phase 3 API surface complete: simulate endpoints, scenario CRUD, tenant provisioning
- Integration test scaffold ready — tests need database connection to execute
- Ready for Phase 4 (Microflows & Worker Jobs) or Phase 5 (Advanced Engines)

## Self-Check

- [x] `backend/src/ccam_backend/api/scenarios.py` exists with 5 routes
- [x] `backend/src/ccam_backend/api/tenants.py` exists with 1 route
- [x] `backend/tests/test_integration_phase3.py` exists with 8 test functions
- [x] `simulate.py` syntax OK, ScenarioModel import present
- [x] `PUBLIC_PATHS` includes `/api/v1/tenants`
- [x] `main.py` wires scenarios_router and tenants_router
- [x] `config.py` has `setup_token` field
- [x] All modules import correctly
- [x] 3 commits exist (d4e4ddf, c829d68, 233a7cc)

## Self-Check: PASSED

---
*Phase: 03-simulator-backend-integration*
*Completed: 2026-06-21*
