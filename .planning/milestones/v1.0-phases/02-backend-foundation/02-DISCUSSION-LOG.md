# Phase 2: Backend Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-21
**Phase:** 2-Backend Foundation
**Areas discussed:** Project structure, PostgreSQL schema & entities, Redis role, HMAC auth design, Audit log immutability, Tenant provisioning

---

## Project Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Same repo, same package | One pyproject.toml, one Python package | |
| Same repo, separate package | Same repo, backend has own pyproject.toml under backend/ | ✓ |
| Separate repos | FastAPI in its own repo | |

**User's choice:** Same repo, separate package
**Notes:** Backend gets its own `pyproject.toml` under `backend/`. Simulator remains at root `src/ccam_sim/`.

---

## PostgreSQL Schema & Entities

| Option | Description | Selected |
|--------|-------------|----------|
| Flat tenant-scoped | All entities have tenant_id + ULID PK, simple RLS | |
| Hierarchical | tenant → users, menu_items with FK relationships | |
| Start flat, evolve | Begin flat, add FKs as Phase 3-4 needs emerge | ✓ |

**User's choice:** Start flat, evolve
**Notes:** ULID PKs + tenant_id on all entities. Alembic for migrations, SQLAlchemy ORM.

---

## Redis Role

| Option | Description | Selected |
|--------|-------------|----------|
| Session + cache only | No background processing | |
| Task queue + cache + sessions | Redis for all three, ARQ for queue | ✓ |
| Start cache-only, add queue later | Task queue in Phase 4 | |

**User's choice:** Task queue + cache + sessions
**Notes:** ARQ as the async task queue. Redis provisioned and connected from Phase 2 start.

---

## HMAC Authentication

| Option | Description | Selected |
|--------|-------------|----------|
| Standard HMAC-SHA256 | base64 key, HMAC-SHA256 signature, bcrypt storage, versioned rotation | ✓ |
| JWT-based with HMAC signing | Key → JWT exchange, token refresh | |
| Simple static bearer token | Plain bearer, no request signing | |

**User's choice:** Standard HMAC-SHA256
**Notes:** Key format: base64(random 32 bytes). Signature covers body + timestamp + path. Versioned for rotation.

---

## Audit Log Immutability

| Option | Description | Selected |
|--------|-------------|----------|
| PostgreSQL + RLS | INSERT-only on audit_log table | ✓ |
| Hash chain | SHA256 of previous entry in each new entry | |
| Both RLS + hash chain | Defense in depth | |

**User's choice:** PostgreSQL + RLS
**Notes:** Application DB user has no UPDATE/DELETE on audit_log. Each entry: action, actor, target, before/after diff, timestamp, tenant_id.

**Follow-up — Audit detail:**

| Option | Description | Selected |
|--------|-------------|----------|
| Action-level events | Log action, actor, target, timestamp | |
| Action + before/after diff | Log action + diff of what changed | ✓ |
| Action + full snapshot | Log action + complete entity state | |

**User's choice:** Action + before/after diff

---

## Tenant Provisioning

| Option | Description | Selected |
|--------|-------------|----------|
| CLI command | ccam-backend provision-tenant CLI | ✓ |
| REST API endpoint | POST /admin/tenants | |
| CLI first, API later | CLI for Phase 2, REST in Phase 3 | ✓ |

**User's choice:** CLI first, API later

---

## OpenCode's Discretion

- **Deployment config:** Dockerfile (multi-stage), Helm chart, docker-compose for dev, GitHub Actions CI
- **Testing strategy:** pytest + pytest-asyncio + TestContainers + FastAPI TestClient

## Deferred Ideas

- REST API for tenant provisioning — Phase 3
- Audit hash chain — not needed for v1
