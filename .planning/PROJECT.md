# CCAM — Conversational Commerce Automation Mesh

## What This Is

CCAM converts unstructured WhatsApp messages from Malaysian F&B customers into structured, auditable, simulatable business workflows. It automates ordering, invoicing, menu optimization, procurement, POS syncing, forecasting, and reporting — governed by a deterministic digital twin simulator that validates every change before it reaches a real restaurant.

## Core Value

Nothing touches a real restaurant until the simulator proves it's safe.

## Requirements

### Validated

These capabilities exist in the current codebase and inform the rebuild:

- ✓ WhatsApp message ingestion via webhook — existing
- ✓ Structured order extraction via Gemini NLP — existing
- ✓ Order CRUD with confidence scoring — existing
- ✓ Invoice generation with payment links — existing
- ✓ Parser audit logging — existing
- ✓ Human-in-the-loop correction workflow — existing
- ✓ Workflow DSL definition management — existing
- ✓ Tenant provisioning — existing
- ✓ Dashboard with KPIs and charts — existing
- ✓ Dark cyberpunk UI theme (Tailwind v4) — existing

### Active

- [ ] **SIM-01**: Deterministic digital twin simulator (CLI) that runs scenario YAMLs and outputs KPIs
- [ ] **SIM-02**: Demand generator — synthetic message/order generation from scenario parameters
- [ ] **SIM-03**: Order generator — converts synthetic demand into structured orders
- [ ] **SIM-04**: Kitchen engine — station load, prep-time, bottleneck, and throughput simulation
- [ ] **SIM-05**: Stock engine — stock consumption, stockout detection, waste tracking
- [ ] **SIM-06**: KPI engine — computes stockout frequency, waste rate, bottleneck frequency, order completion time, throughput
- [ ] **SIM-07**: Ground-up backend on FastAPI + PostgreSQL + Kubernetes
- [ ] **SIM-08**: Tenant isolation and deterministic audit logging throughout
- [ ] **SIM-09**: Simulator API endpoint (`POST /simulate`)
- [ ] **SIM-10**: Safety layer — gates changes behind simulator KPI thresholds

### Out of Scope

- Mobile offline-sync app — defer until core platform stable
- Full billing/quota system — basic usage tracking in v1, full billing later
- Multi-region failover — single-region for v1
- POS vendor adapters — adapter interface defined but vendor-specific implementations deferred
- Supplier connector — supplier adapter interface defined, implementations deferred
- Real parser engine (DistilBERT) — Gemini-based parsing continues until simulator validates need for custom ML
- Real menu engineering MILP solver — simulated in v1, real solver later
- Notification engine — basic notifications only, multi-channel dispatch deferred

## Context

The current codebase is a Firebase AI Studio applet (React 19 + Vite 6 + Express 4 + Firebase 12 + Gemini) with a monolithic SPA architecture. It has no test infrastructure, no deterministic simulation (mock data only), permissive Firestore security rules, no authentication, and no job queue. The spec calls for a ground-up rebuild on FastAPI + PostgreSQL + Kubernetes with deterministic simulation as the governing subsystem.

This is a complete architectural replacement, not an incremental migration.

## Constraints

- **Tech stack**: FastAPI (Python), PostgreSQL, Redis, Kubernetes — per full spec
- **Simulator-first**: No subsystem deploys to production until the simulator validates it
- **Determinism**: All subsystems must produce identical outputs for identical inputs
- **Tenant isolation**: Every entity scoped to tenant_id, no cross-tenant leakage
- **CLI-first**: v1 simulator ships as a CLI before any API or UI
- **Auditability**: Every action logged to immutable, tenant-scoped audit log
- **Idempotency**: All worker jobs and API writes must be safe to retry
- **Safety layer**: Hard rules that cannot be overridden by any subsystem

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Ground-up rebuild vs incremental migration | Architectural mismatch between Firebase/Express and FastAPI/PostgreSQL/K8s is too wide for incremental approach | — Pending |
| Simulator as Phase 1 | Simulator is the governor of all other subsystems; build the "physics engine" first | — Pending |
| CLI-first simulator (no API/UI in v1) | Fastest path to a deterministic, testable, CI-integratable engine | — Pending |
| Python for simulator (FastAPI ecosystem) | ML ecosystem (DistilBERT, Prophet, MILP solvers) is Python-native; TypeScript retained for frontend | — Pending |
| Deterministic simulation with seeded RNG | Reproducibility is non-negotiable for regression testing and safety gating | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-21 after initialization*
