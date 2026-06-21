# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-21)

**Core value:** Nothing touches a real restaurant until the simulator proves it's safe.
**Current focus:** Phase 3 — Simulator-Backend Integration

## Current Position

Phase: 3 of 5 (Simulator-Backend Integration)
Plan: 0 of 2 in current phase
Status: Planned
Last activity: 2026-06-21 — Phase 2 complete (3 plans, 8 models, CLI, Docker, Helm, CI)

Progress: [██████░░░░] 60% (complete)

## Performance Metrics

**Velocity:**
- Total plans completed: 7
- Plans planned: 2 (Phase 3)
- Total execution time: N/A

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 - Simulator Core | 4 | Complete | N/A |
| 2 - Backend Foundation | 3 | Complete | N/A |

**Recent Trend:**
- Last 5 plans: 01-04 → 02-01 → 02-02 → 02-03 consecutive completion
- Trend: Phase 1 + Phase 2 delivered, Phase 3 planned

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

Last session: 2026-06-21 (Phase 2 complete)
Stopped at: Phase 2 delivered — 3 plans, 8 unit tests passing, 5 skipped (DB-dependent)
Resume file: .planning/phases/03-simulator-integration/

### Plan 02-03 Deliverables

| File | Purpose |
|------|---------|
| `backend/src/ccam_backend/cli/__init__.py` | CLI package init |
| `backend/src/ccam_backend/cli/tenant.py` | `ccam-backend provision-tenant` Click command |
| `backend/Dockerfile` | Multi-stage Docker build (uv → slim runtime) |
| `backend/.dockerignore` | Docker build context exclusions |
| `backend/helm/ccam-backend/Chart.yaml` | Helm chart metadata |
| `backend/helm/ccam-backend/values.yaml` | Helm configuration values |
| `backend/helm/ccam-backend/templates/_helpers.tpl` | Helm named templates |
| `backend/helm/ccam-backend/templates/configmap.yaml` | ConfigMap (env vars) |
| `backend/helm/ccam-backend/templates/secret.yaml` | Secret (HMAC key) |
| `backend/helm/ccam-backend/templates/deployment.yaml` | K8s Deployment |
| `backend/helm/ccam-backend/templates/service.yaml` | K8s Service |
| `backend/helm/ccam-backend/templates/migration-job.yaml` | Alembic migration Job |
| `.github/workflows/backend.yml` | CI pipeline (lint, test, docker) |
| `backend/tests/test_cli.py` | CLI unit tests |

### Bugs Fixed During Execution

1. **HMAC verify_signature**: Both `main.py` and `middleware.py` were calling `verify_signature` without the `signature_b64` argument (5 args instead of 6)
2. **Redis close**: `close()` deprecated; changed to `aclose()` for both Redis client and ARQ pool
3. **Lint auto-fixes**: 7 F401 unused imports removed + `== True` → truth check in `api_keys.py`
4. **Mypy type errors**: 5 errors fixed — async generator return types, `RedisSettings.from_url` (didn't exist), `wait_closed` (didn't exist)
5. **Test infrastructure**: httpx ASGITransport doesn't trigger lifespan; added manual `lifespan_context` fixture
