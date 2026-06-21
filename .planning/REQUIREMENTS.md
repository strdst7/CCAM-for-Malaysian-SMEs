# Requirements: CCAM

**Defined:** 2026-06-21
**Core Value:** Nothing touches a real restaurant until the simulator proves it's safe.

## v1 Requirements

### Simulator Core (Phase 1)

- [ ] **SIM-01**: CLI accepts scenario YAML with demand pattern, menu config, prep times, station mapping, staff count, stock levels, supplier delays
- [ ] **SIM-02**: Demand generator synthesizes message traffic from scenario parameters with seeded determinism
- [ ] **SIM-03**: Order generator converts synthetic demand into structured order objects
- [ ] **SIM-04**: Kitchen engine simulates station load, prep-time accumulation, bottleneck detection, and throughput
- [ ] **SIM-05**: Stock engine simulates stock consumption, stockout events, and waste tracking
- [ ] **SIM-06**: KPI engine computes stockout frequency, waste rate, bottleneck frequency, order completion time, throughput
- [ ] **SIM-07**: CLI outputs structured KPI results as JSON and human-readable summary
- [ ] **SIM-08**: Deterministic replay — same scenario YAML + seed produces identical output
- [ ] **SIM-09**: Safety layer enforces hard rules (no negative stock, no overload > 120%, no infinite loops)

### Backend Foundation (Phase 2)

- [ ] **BCK-01**: FastAPI application with PostgreSQL, Redis, and tenant-scoped data model
- [ ] **BCK-02**: Tenant, user, menu_item, pos_sku, stock_event, simulation_run entities with ULID primary keys
- [ ] **BCK-03**: Tenant isolation enforced at database row level
- [ ] **BCK-04**: HMAC-signed API authentication with API keys
- [ ] **BCK-05**: Immutable, append-only audit log for all subsystem actions

### Simulator-Backend Integration (Phase 3)

- [x] **INT-01**: `POST /simulate` API endpoint wrapping the simulator engine
- [ ] **INT-02**: Scenario CRUD — save, load, list scenario YAMLs
- [x] **INT-03**: Simulation run storage with KPI snapshots
- [ ] **INT-04**: Safety gate — blocks menu/procurement/microflow changes if simulator KPIs fail thresholds

### Microflows & Worker Jobs (Phase 4)

- [ ] **MCF-01**: Microflow DSL interpreter (bytecode compiler + deterministic executor)
- [ ] **MCF-02**: Worker job system with FIFO queues, retry logic, dead-letter queue
- [ ] **MCF-03**: Microflow safety layer (no loops, no recursion, no privilege escalation)
- [ ] **MCF-04**: Simulator validates all microflow changes before deployment

### Advanced Engines (Phase 5)

- [ ] **ENG-01**: Parser engine (hybrid regex + DistilBERT NER) with confidence scoring
- [ ] **ENG-02**: Menu engineering engine (MILP solver) with safety-constrained recommendations
- [ ] **ENG-03**: Forecast engine (multi-model ensemble: LSTM, Prophet, ARIMA)
- [ ] **ENG-04**: Procurement engine with supplier adapter interface and PO generation
- [ ] **ENG-05**: Notification engine with multi-channel routing (WhatsApp, email, push, in-app)

## v2 Requirements

### Deferred

- **MOB-01**: Mobile app with offline SQLite store and delta sync
- **BLG-01**: Full billing system with usage metering, tiered pricing, invoice generation
- **POS-01**: Vendor-specific POS adapters (StoreHub, Slurp, Qashier, etc.)
- **SUP-01**: Vendor-specific supplier adapters
- **UI-01**: Simulator dashboard with timeline graphs, station heatmaps, stock curves
- **OPS-01**: Multi-region failover (MY → SG)
- **SEC-01**: SOC 2 / ISO 27001 certification processes

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time chat / WebSocket API | REST + polling sufficient for v1; WebSocket complexity deferred |
| Customer-facing mobile app | Staff operational app is priority; customer interaction stays on WhatsApp |
| Multi-language UI | English + Malay for v1; Chinese and others deferred |
| On-premise deployment | Cloud-only (Kubernetes) for v1 |
| Third-party delivery integration | GrabFood/FoodPanda integration deferred to v2+ |
| Video/image parsing | Text-only WhatsApp parsing for v1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SIM-01 | Phase 1 | Pending |
| SIM-02 | Phase 1 | Pending |
| SIM-03 | Phase 1 | Pending |
| SIM-04 | Phase 1 | Pending |
| SIM-05 | Phase 1 | Pending |
| SIM-06 | Phase 1 | Pending |
| SIM-07 | Phase 1 | Pending |
| SIM-08 | Phase 1 | Pending |
| SIM-09 | Phase 1 | Pending |
| BCK-01 | Phase 2 | Pending |
| BCK-02 | Phase 2 | Pending |
| BCK-03 | Phase 2 | Pending |
| BCK-04 | Phase 2 | Pending |
| BCK-05 | Phase 2 | Pending |
| INT-01 | Phase 3 | Complete |
| INT-02 | Phase 3 | Pending |
| INT-03 | Phase 3 | Complete |
| INT-04 | Phase 3 | Pending |
| MCF-01 | Phase 4 | Pending |
| MCF-02 | Phase 4 | Pending |
| MCF-03 | Phase 4 | Pending |
| MCF-04 | Phase 4 | Pending |
| ENG-01 | Phase 5 | Pending |
| ENG-02 | Phase 5 | Pending |
| ENG-03 | Phase 5 | Pending |
| ENG-04 | Phase 5 | Pending |
| ENG-05 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 27 total
- Mapped to phases: 27
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-21*
*Last updated: 2026-06-21 after roadmap creation*
