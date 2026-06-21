# Phase 5: Advanced Engines - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Production-grade ML/algorithmic engines for WhatsApp message parsing, menu optimization, demand forecasting, automated procurement, and multi-channel notifications. Each engine is a standalone package under `engines/` that sits on top of the simulator core (Phase 1), backend foundation (Phase 2), simulator-backend integration (Phase 3), and microflow/worker infrastructure (Phase 4). The safety gate (INT-04/MCF-03/MCF-04) is NOT delivered in Phase 5 — remains deferred.

**What is delivered:**
- Parser engine with hybrid regex pipeline + DistilBERT NER (ONNX), regex-first with NER fallback
- Menu engineering engine with Google OR-Tools MILP solver, safety-constrained recommendations
- Forecast engine with LSTM + Prophet + ARIMA ensemble, simulator-generated training, batch retraining
- Procurement engine with pluggable supplier adapters (ABC pattern), v1 ships email-based PO delivery
- Notification engine with multi-channel routing, v1 ships email (SendGrid/SMTP) and in-app notifications
- All engines surfaced via REST API under `/api/v1/`

**What is NOT delivered:**
- WhatsApp Business API integration — deferred post-v1
- Push notifications (FCM) — deferred post-v1
- Supplier-specific API adapters — v1 uses email-based PO only
- Safety gate enforcement (INT-04) — remains deferred
</domain>

<decisions>
## Implementation Decisions

### Scope
- **D-01:** All 5 engines are in scope (ENG-01 through ENG-05). ROADMAP.md overrides the stale PROJECT.md Out of Scope entries. DistilBERT parser, MILP solver, and multi-channel notifications proceed as specified.

### Engine Packaging
- **D-02:** Each engine is a standalone Python package under `engines/` with its own `pyproject.toml`, matching the `ccam_sim` pattern. Names: `ccam_parser`, `ccam_menu`, `ccam_forecast`, `ccam_procurement`, `ccam_notification`.
- **D-03:** Each engine exposes a clean public API (sync functions). Backend imports and wraps them in async endpoints via `run_in_executor` or ARQ worker jobs as appropriate.

### Parser Engine (ENG-01)
- **D-04:** Regex-first pipeline handles 80%+ of common Malaysian F&B patterns (Nasi Lemak, Teh Tarik, RM prices). DistilBERT NER activates only when regex confidence < threshold.
- **D-05:** DistilBERT runs via ONNX Runtime (CPU-optimized, ~50MB model). No GPU required. No raw PyTorch/huggingface transformers in production.
- **D-06:** Output includes structured order fields + confidence score per field + overall confidence.

### Menu Engineering Engine (ENG-02)
- **D-07:** Google OR-Tools for MILP solver. Handles integer constraints (e.g., "pick exactly 3 specials") and linear constraints (margin floors, price bounds).
- **D-08:** Safety constraints are hard-coded rules: no negative margin suggestions, no price below cost, no removal of all low-cost items. These are non-overridable.
- **D-09:** Menu changes require simulator validation pass before production deployment.

### Forecast Engine (ENG-03)
- **D-10:** Ensemble all 3 models: LSTM (TensorFlow/Keras), Prophet (Meta/Stan), ARIMA (statsmodels). Each model runs independently, outputs are weighted by recent accuracy.
- **D-11:** Training data sourced from simulator-generated demand patterns (not production data for v1). Batch training runs via ARQ worker job (weekly/daily cadence).
- **D-12:** Trained models stored on filesystem as ONNX (LSTM) + serialized Prophet/ARIMA objects. Versioned via Git LFS.
- **D-13:** Forecast changes require simulator validation pass before production deployment.

### Procurement Engine (ENG-04)
- **D-14:** Pluggable supplier adapters via abstract base class (ABC) with interface: `order_ingredients()`, `generate_po()`, `send_po()`, `track_status()`.
- **D-15:** v1 ships one adapter: email-based PDF purchase order delivery. Supplier-specific API adapters deferred.
- **D-16:** Purchase orders follow a template format. Supplier contact info stored per-tenant in configuration.

### Notification Engine (ENG-05)
- **D-17:** v1 ships two channels: email (SendGrid/SMTP) and in-app notifications (SSE or polling).
- **D-18:** WhatsApp Business API and push notifications (FCM) are deferred post-v1.

### Simulator Validation
- **D-19:** Menu optimization (ENG-02) and forecast (ENG-03) changes require simulator validation before production deployment. Parser output (HITL-corrected) and notifications skip sim validation. Procurement changes are advisory — human reviews before acting.

### OpenCode's Discretion
- Exact regex patterns for the parser regex engine
- ONNX model conversion pipeline details
- Training frequency (daily vs weekly)
- SSE vs polling for in-app notifications
- PDF generation library for procurement POs
- SendGrid vs SMTP implementation details
- Forecast model weighting strategy
- ARQ job timeout and retry configuration per engine task

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Definition & Requirements
- `.planning/ROADMAP.md` §83-96 — Phase 5 goal, dependencies, success criteria
- `.planning/REQUIREMENTS.md` §44-48 — ENG-01 through ENG-05 requirements

### Prior Context
- `.planning/phases/03-simulator-backend-integration/03-CONTEXT.md` — Phase 3 decisions (sim endpoint, scenario CRUD, tenant API)
- `.planning/phases/04-microflows-worker-jobs/04-CONTEXT.md` — Phase 4 decisions (DSL, ARQ worker, job API)

### Backend (existing patterns)
- `backend/src/ccam_backend/main.py` — FastAPI app with route mounting, lifespan
- `backend/src/ccam_backend/api/deps.py` — `get_db()`, `get_redis_client()` DI pattern
- `backend/src/ccam_backend/api/jobs.py` — ARQ job enqueue pattern (reusable for training jobs)
- `backend/src/ccam_backend/workers/mcf_worker.py` — ARQ worker pattern (reusable for forecast training)

### Prior CONTEXT files
- `.planning/phases/02-backend-foundation/02-CONTEXT.md` — D-04 (Redis/ARQ), D-05 (task queue)
- `.planning/phases/03-simulator-backend-integration/03-CONTEXT.md` — D-06 (thread pool), D-12 (URL structure)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **ARQ worker infrastructure** (Phase 4): Retry/DLQ, idempotency keys, job API pattern. Reusable for forecast batch training and procurement PO dispatch.
- **ccam_sim package**: Importable as library for simulator validation passes. Menu changes run through `run_simulation()` before deployment.
- **Router-per-resource pattern** (Phase 3): Each engine gets its own `APIRouter`, mounted in `main.py` under `/api/v1/`.
- **`run_in_executor` pattern** (Phase 3, D-06): Sync engine functions wrapped via thread pool for async FastAPI endpoints.

### Established Patterns
- **Pyproject.toml per package**: Each engine replicates `src/ccam_sim/pyproject.toml` structure.
- **Auth via middleware**: New engine endpoints behind HMAC auth (`PUBLIC_PATHS` pattern).
- **Async DB sessions**: Engines needing persistence (procurement POs, notification logs) extend existing models.

### Integration Points
- **`main.py`**: Mounts 5 new routers (one per engine) under `/api/v1/`.
- **`PUBLIC_PATHS`**: Parser webhook endpoint likely needs to be public (WhatsApp webhook) — add to middleware allowlist.
- **Worker jobs**: Forecast training and PO dispatch use ARQ worker infrastructure from Phase 4.

### Creative Options
- Parser webhook can reuse POST /api/v1/jobs from Phase 4 instead of a dedicated endpoint — enqueue parsing job, webhook returns 202 with job_id.
- Forecast training can piggyback on the existing ARQ worker pattern in `mcf_worker.py`.

</code_context>

<specifics>
## Specific Ideas

- "Regex-first, NER fallback" — parser processes most messages without ML inference, keeping latency and cost low for common patterns.
- Forecast models should be trainable without production data — simulator-generated demand patterns are sufficient for v1.

</specifics>

<deferred>
## Deferred Ideas

- WhatsApp Business API integration — post-v1, requires Meta business verification (~weeks)
- Push notifications via FCM — post-v1
- Supplier-specific API adapters (SYF Resources, etc.) — post-v1
- Safety gate enforcement (INT-04/MCF-03/MCF-04) — remains deferred from Phase 3/4
- Online/incremental learning for forecast models — too complex for v1

</deferred>

---

*Phase: 05-advanced-engines*
*Context gathered: 2026-06-21*
