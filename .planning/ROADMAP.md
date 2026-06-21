# Roadmap: CCAM — Conversational Commerce Automation Mesh

## Overview

CCAM converts unstructured WhatsApp messages from Malaysian F&B customers into structured, auditable, simulatable business workflows. The roadmap builds from the ground up in 5 phases: first the deterministic digital twin simulator (the "governor" of the entire system), then the tenant-isolated backend, then the integration layer that wires simulator to backend, then the microflow/worker engine, and finally the advanced ML engines. Nothing touches a real restaurant until the simulator proves it's safe.

## Phases

- [x] **Phase 1: Simulator Core (CLI)** — Deterministic digital twin CLI with demand, order, kitchen, stock, and KPI engines plus safety layer
- [x] **Phase 2: Backend Foundation** — FastAPI + PostgreSQL + Redis on Kubernetes with tenant isolation and audit logging
- [ ] **Phase 3: Simulator-Backend Integration** — API gateway for simulation, scenario CRUD, and safety gate enforcement
- [ ] **Phase 4: Microflows & Worker Jobs** — DSL interpreter, bytecode executor, FIFO job queues with retry/DLQ
- [ ] **Phase 5: Advanced Engines** — Parser (DistilBERT), Menu Engineering (MILP), Forecast (LSTM/Prophet/ARIMA), Procurement, Notification

## Phase Details

### Phase 1: Simulator Core (CLI)
**Goal**: A deterministic digital twin simulator CLI that validates restaurant operations through scenario YAMLs — the "governor" that all other phases depend on.
**Depends on**: Nothing (first phase)
**Requirements**: SIM-01, SIM-02, SIM-03, SIM-04, SIM-05, SIM-06, SIM-07, SIM-08, SIM-09
**Success Criteria** (what must be TRUE):
  1. User can run `ccam-sim simulate scenario.yaml --seed 42` and receive structured JSON KPIs plus a human-readable summary
  2. Same scenario YAML + same seed always produces identical KPI output (deterministic replay verified)
  3. Safety layer rejects scenarios with negative stock, >120% station overload, or infinite loops with clear error messages
  4. KPI output includes stockout frequency, waste rate, bottleneck frequency, order completion time, and throughput
  5. All five engines (demand generator, order generator, kitchen engine, stock engine, KPI engine) produce coherent end-to-end simulation results from a single scenario YAML
**Plans**: 4 plans across 3 waves

Plans:
- [x] 01-01-PLAN.md — Project scaffold, data models, RNG manager, scenario loader
- [x] 01-02-PLAN.md — Click CLI, safety layer (Gate 1 + Gate 2), output formatters
- [x] 01-03-PLAN.md — Five engine pipeline (demand → order → kitchen → stock → KPI)
- [x] 01-04-PLAN.md — Full test suite with determinism verification, CLI integration tests

### Phase 2: Backend Foundation
**Goal**: A tenant-isolated FastAPI + PostgreSQL + Redis backend running on Kubernetes with HMAC authentication and an immutable audit log.
**Depends on**: Phase 1
**Requirements**: BCK-01, BCK-02, BCK-03, BCK-04, BCK-05
**Success Criteria** (what must be TRUE):
  1. FastAPI application boots on Kubernetes with PostgreSQL and Redis connected and healthy
  2. New tenants can be provisioned — all entities (tenant, user, menu_item, pos_sku, stock_event, simulation_run) are scoped to tenant_id via ULID primary keys
  3. API requests require HMAC-signed API keys; requests without valid authentication return 401
  4. Every subsystem action is recorded in an immutable, append-only, tenant-scoped audit log
  5. Database row-level tenant isolation prevents cross-tenant data leakage (verified by test)
**Plans**: 3 plans across 3 waves

Plans:
- [x] 02-01-PLAN.md — Data Foundation: package scaffold, all entity models (8 tables), Alembic migration, docker-compose for PostgreSQL + Redis
- [x] 02-02-PLAN.md — API & Auth: FastAPI app, HMAC-SHA256 middleware, audit logger, RLS policies, health endpoint, Redis/ARQ connectivity
- [x] 02-03-PLAN.md — CLI & Infrastructure: tenant provisioning CLI, Dockerfile/Helm chart, GitHub Actions CI, integration tests

### Phase 3: Simulator-Backend Integration
**Goal**: The simulator CLI engine is exposed as a REST API endpoint, scenarios are manageable via CRUD, and the safety gate enforces simulator validation before any production change.
**Depends on**: Phase 1, Phase 2
**Requirements**: INT-01, INT-02, INT-03, INT-04
**Success Criteria** (what must be TRUE):
   1. User/developer can call `POST /simulate` with scenario parameters and receive KPI results identical to the CLI
   2. User/developer can create, read, list, update, and delete scenario YAMLs via REST API
   3. Every simulation run is persisted with its full KPI snapshot and input parameters for audit/history
   4. Safety gate blocks menu, procurement, and microflow changes when simulator KPIs fail configured thresholds, returning a clear reason for the block
   5. The safety gate cannot be bypassed by any API caller — it enforces hard rules at the integration layer
**Plans**: 2 plans across 2 waves

Plans:
- [x] 03-01-PLAN.md — Simulation endpoint foundation: Scenario model, migration, Pydantic schemas, POST/GET simulate endpoints
- [x] 03-02-PLAN.md — Scenario CRUD, tenant provisioning API, saved-scenario refs, integration tests

### Phase 4: Microflows & Worker Jobs
**Goal**: A deterministic microflow DSL system with a bytecode interpreter, worker job queues with retry/dead-letter handling, all validated by the simulator before deployment.
**Depends on**: Phase 3
**Requirements**: MCF-01, MCF-02, MCF-03 (deferred), MCF-04 (deferred)
**Success Criteria** (what must be TRUE):
  1. User can write microflow DSL scripts that compile to bytecode and execute deterministically (same input → same output)
  2. Worker jobs process FIFO queues with configurable retry logic; failed jobs land in a dead-letter queue for inspection
  3. Worker jobs are idempotent — replaying a completed job does not produce duplicate side effects
  > MCF-03 (safety layer) and MCF-04 (simulator gate) deferred to a future phase per design decision D-01.
**Plans**: 2 plans across 2 waves

Plans:
- [x] 04-01-PLAN.md — Microflow DSL compiler + bytecode executor library (MCF-01)
- [x] 04-02-PLAN.md — ARQ worker job infrastructure with retry/DLQ/idempotency (MCF-02)

### Phase 5: Advanced Engines
**Goal**: Production-grade ML engines for WhatsApp message parsing, menu optimization, demand forecasting, automated procurement, and multi-channel notifications.
**Depends on**: Phase 4
**Requirements**: ENG-01, ENG-02, ENG-03, ENG-04, ENG-05
**Success Criteria** (what must be TRUE):
  1. Parser engine extracts structured orders from raw WhatsApp messages with confidence scoring (hybrid regex + DistilBERT NER)
  2. Menu engineering engine recommends pricing and menu optimizations constrained by safety rules (no negative margin suggestions, etc.)
  3. Forecast engine produces accurate demand predictions using an ensemble of LSTM, Prophet, and ARIMA models
  4. Procurement engine generates purchase orders via a supplier adapter interface with configurable lead times
  5. Notification engine routes messages through WhatsApp, email, push, and in-app channels with templated content
**Plans**: 4 plans across 2 waves

Plans:
- [ ] 05-01-PLAN.md — Parser engine (ENG-01) + Menu engineering engine (ENG-02) — regex/NLP parsing + MILP menu optimization
- [ ] 05-02-PLAN.md — Forecast engine (ENG-03) — LSTM + Prophet + ARIMA ensemble demand forecasting
- [ ] 05-03-PLAN.md — Procurement engine (ENG-04) + Notification engine (ENG-05) — supplier ABC, PO gen, multi-channel notifications
- [ ] 05-04-PLAN.md — Backend API integration — 5 routers, DB models, migrations, ARQ worker registration

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Simulator Core (CLI) | 4/4 | Complete | 2026-06-21 |
| 2. Backend Foundation | 3/3 | Complete | 2026-06-21 |
| 3. Simulator-Backend Integration | 2/2 | Complete | 2026-06-21 |
| 4. Microflows & Worker Jobs | 2/2 | Complete | 2026-06-21 |
| 5. Advanced Engines | 0/4 | Planned | - |
