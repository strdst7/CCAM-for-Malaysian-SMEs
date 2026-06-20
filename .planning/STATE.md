# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-21)

**Core value:** Nothing touches a real restaurant until the simulator proves it's safe.
**Current focus:** Phase 2 — Backend Foundation

## Current Position

Phase: 2 of 5 (Backend Foundation)
Plan: 0 of 0 in current phase
Status: Context gathered, ready for planning
Last activity: 2026-06-21 — Phase 2 context captured (6 areas discussed)

Progress: [░░░░░░░░░░] 0% (planned)

## Performance Metrics

**Velocity:**
- Total plans completed: 4
- Average duration: N/A
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 - Simulator Core | 4 | Complete | N/A |

**Recent Trend:**
- Last 5 plans: 01-01 → 01-04 consecutive completion
- Trend: Phase 1 delivered, Phase 2 context gathered

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
- (Phase 2): HMAC-SHA256 auth with versioned key rotation
- (Phase 2): RLS-enforced INSERT-only audit log with before/after diffs
- (Phase 2): CLI-first tenant provisioning, REST deferred to Phase 3

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

Last session: 2026-06-21 (Phase 2 context discussion)
Stopped at: Phase 2 context gathered — 6 decisions captured
Resume file: .planning/phases/02-backend-foundation/02-CONTEXT.md
