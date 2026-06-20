# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-21)

**Core value:** Nothing touches a real restaurant until the simulator proves it's safe.
**Current focus:** Phase 1 — Simulator Core (CLI)

## Current Position

Phase: 1 of 5 (Simulator Core (CLI))
Plan: 4 of 4 in current phase
Status: Phase 1 complete
Last activity: 2026-06-21 — Plan 01-04: full test suite (44 tests, 0 failures)

Progress: [██████████] 100% (complete)

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
- Trend: Phase 1 delivered

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

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-06-21 (test suite execution)
Stopped at: Phase 1 complete — 44 tests pass, deterministic replay verified (SIM-08)
Resume file: None
