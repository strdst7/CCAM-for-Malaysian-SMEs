# CCAM — Project Guide

## GSD Workflow

This project uses GSD (Get Shit Done) workflow methodology.

### Commands

- `/gsd-plan-phase <N>` — Plan a phase with task breakdown
- `/gsd-execute-phase <N>` — Execute a planned phase
- `/gsd-progress` — Show project state and progress
- `/gsd-transition` — Transition between phases (update requirements, decisions)
- `/gsd-map-codebase` — Generate/refresh codebase mapping docs
- `/gsd-discuss-phase <N>` — Explore and clarify a phase before planning
- `/gsd-code-review` — Automated code review against requirements
- `/gsd-ui-phase <N>` — Generate UI design contract (frontend phases)

### Project Context

- `.planning/PROJECT.md` — Project definition and constraints
- `.planning/ROADMAP.md` — Phase structure and success criteria
- `.planning/REQUIREMENTS.md` — Checkable requirements with REQ-IDs
- `.planning/STATE.md` — Current position and accumulated context
- `.planning/config.json` — Workflow preferences
- `.planning/codebase/` — Codebase mapping documents

### Core Value

Nothing touches a real restaurant until the simulator proves it's safe.

### Current Phase

Phase 1: Simulator Core (CLI) — Deterministic digital twin CLI with demand, order, kitchen, stock, and KPI engines plus safety layer.

### Requirements Coverage

27 v1 requirements across 5 phases. See `.planning/REQUIREMENTS.md` for traceability.
