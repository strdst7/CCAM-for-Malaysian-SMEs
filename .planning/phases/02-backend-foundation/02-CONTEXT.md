# Phase 2: Backend Foundation - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning

<domain>
## Phase Boundary

A tenant-isolated FastAPI + PostgreSQL + Redis backend with HMAC-signed API authentication and an immutable audit log. This is the data and API layer that Phase 3 (simulator-backend integration) and Phase 4 (microflows/workers) will build on. Phase 2 delivers the foundation — no simulator integration, no microflows, no frontend.

**What is delivered:**
- FastAPI application boots with PostgreSQL and Redis connected and healthy
- Database schema with tenant-scoped entities (tenant, user, menu_item, pos_sku, stock_event, simulation_run)
- Tenant isolation enforced at database row level (RLS)
- HMAC-SHA256 API key authentication
- Immutable, append-only audit log (RLS-enforced INSERT-only)
- CLI command for tenant provisioning
- Docker, Kubernetes (Helm), and local dev setup

</domain>

<decisions>
## Implementation Decisions

### Project Structure
- **D-01:** Same repository, separate Python packages. Backend gets its own `pyproject.toml` under `backend/` directory. Simulator remains at root as `src/ccam_sim/`. Backend import name: `ccam_backend`.

### PostgreSQL Schema & Entities
- **D-02:** Entity relationships start flat (all entities scoped by `tenant_id` + ULID PK). Foreign keys and complex relationships added as Phase 3-4 needs emerge. No over-engineering upfront.
- **D-03:** SQLAlchemy for ORM, Alembic for schema migrations.

### Redis Role
- **D-04:** Redis handles all three: session storage, caching, and async task queue. ARQ library for the task queue (async-native, FastAPI-compatible).
- **D-05:** Task queue infrastructure built in Phase 2 even though Phase 4 uses it — Redis is provisioned and connected from day one.

### HMAC Authentication
- **D-06:** Standard HMAC-SHA256. API key = base64(random 32 bytes). Request is signed with HMAC-SHA256 of body + timestamp + path. Key stored as bcrypt hash in DB. Rotation via key versioning (`key_v1`, `key_v2`).

### Audit Log Immutability
- **D-07:** PostgreSQL row-level security (RLS) enforces INSERT-only on `audit_log` table. Application database user never has UPDATE/DELETE privileges on this table.
- **D-08:** Each audit entry logs: action, actor (user_id or system), target entity + ID, before/after JSON diff, timestamp, tenant_id. No hash chain (RLS is sufficient for v1).

### Tenant Provisioning
- **D-09:** CLI command first (e.g., `ccam-backend provision-tenant --name "Kedai Kopi"`). REST API endpoint deferred to Phase 3 when a management UI exists. CLI avoids chicken-and-egg auth bootstrap problem.

### OpenCode's Discretion
- **Deployment config:** Dockerfile (multi-stage Python), Helm chart for Kubernetes, docker-compose for local dev with PostgreSQL + Redis sidecars. GitHub Actions CI.
- **Testing strategy:** pytest with pytest-asyncio for async tests. TestContainers for PostgreSQL/Redis integration tests. FastAPI TestClient for endpoint tests. HMAC auth tests with known keys. Audit immutability tests verifying RLS blocks UPDATE/DELETE.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Definition & Requirements
- `.planning/ROADMAP.md` §35-48 — Phase 2 goal, dependencies, success criteria
- `.planning/REQUIREMENTS.md` §20-26 — BCK-01 through BCK-05 requirements
- `.planning/PROJECT.md` — Project constraints (tenant isolation, auditability, FastAPI stack)

### Architecture & Stack
- `.planning/codebase/STACK.md` — Current tech stack (being replaced, but Python ecosystem context)
- `.planning/codebase/ARCHITECTURE.md` — Current architecture patterns and anti-patterns
- `.planning/codebase/INTEGRATIONS.md` — External integration patterns (Firebase, Gemini)

### Phase 1 (Simulator, consumable by Phase 2+)
- `src/ccam_sim/` — Simulator is importable as a Python library (`from ccam_sim import ...`)
- `.planning/phases/01-simulator-core/01-04-SUMMARY.md` — Simulator test suite and verification

### Technology References
- FastAPI docs: Application setup, dependency injection, middleware
- SQLAlchemy + Alembic: Async SQLAlchemy with FastAPI, Alembic migrations
- ARQ docs: Async Redis task queue for FastAPI

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/ccam_sim/` — The entire simulator is importable as a Python library. Phase 2 does NOT integrate it yet (Phase 3 adds `POST /simulate`), but the backend package structure should support importing `ccam_sim`.
- `.venv/` — uv-based virtual environment already exists. Backend package should use uv too.

### Established Patterns
- **uv + pyproject.toml:** Phase 1 uses uv for dependency management. Backend follows the same tooling.
- **pytest:** Phase 1 established pytest. Backend extends with pytest-asyncio and TestContainers.
- **Determinism principle:** Audit log entries should be deterministic where possible (same action → same log structure).

### Integration Points
- Backend will be imported by Phase 3 (simulation API) and Phase 4 (microflows/workers)
- Simulator package (`ccam_sim`) must remain importable from backend code (`backend/` directory)
- The existing Firebase/Express monolith (`server.ts`, `src/`) is being replaced — no integration with it

</code_context>

<specifics>
No specific references requested — standard FastAPI + SQLAlchemy patterns apply.

</specifics>

<deferred>

- **REST API for tenant provisioning** — deferred to Phase 3 (management UI)
- **Audit hash chain (cryptographic tamper evidence)** — not needed for v1; RLS is sufficient

</deferred>

---

*Phase: 2-Backend Foundation*
*Context gathered: 2026-06-21*
