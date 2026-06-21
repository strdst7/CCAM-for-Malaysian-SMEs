# Phase 5: Advanced Engines - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves the discussion flow.

**Date:** 2026-06-21
**Phase:** 05-advanced-engines
**Mode:** discuss (default interactive)

## Areas Discussed

### 1. Scope: PROJECT.md vs ROADMAP.md conflict
- **User selection:** ROADMAP wins — all 5 engines in scope
- **Decision:** PROJECT.md Out of Scope entries are stale; ROADMAP Phase 5 requirements (ENG-01 through ENG-05) take priority

### 2. Engine packaging strategy
- **User selection:** Standalone packages
- **Decision:** Each engine under `engines/` with own `pyproject.toml`, matching `ccam_sim` pattern

### 3. MILP solver for menu engineering (ENG-03)
- **User selection:** Google OR-Tools
- **Decision:** OR-Tools for MILP; fastest C++ backend with Python bindings

### 4. Forecast model strategy (ENG-04)
- **User selection:** Ensemble all 3 (LSTM + Prophet + ARIMA)
- **Decision:** All three models run independently, weighted by recent accuracy

### 5. Notification channels in v1 (ENG-05)
- **User selection:** Email + in-app only
- **Decision:** WhatsApp and push deferred post-v1

### 6. Simulator validation scope
- **User selection:** Menu + forecast only
- **Decision:** Parser (HITL-corrected) and notifications skip sim validation; procurement is advisory

### 7. Parser: regex vs NER balance (ENG-01 follow-up)
- **User selection:** Regex-first, NER fallback
- **Decision:** Regex handles 80%+ of common patterns; DistilBERT only when regex confidence < threshold

### 8. DistilBERT runtime
- **User selection:** ONNX Runtime
- **Decision:** CPU-optimized ONNX, ~50MB model, no GPU required

### 9. Forecast training pipeline (ENG-03 follow-up)
- **User selection:** Simulator-generated + batch training
- **Decision:** Training data from simulator scenarios; batch training via ARQ worker; models versioned via Git LFS

### 10. Model storage
- **User selection:** Filesystem + Git LFS
- **Decision:** ONNX/Prophet/ARIMA models stored on filesystem, tracked via Git LFS

### 11. Procurement adapter design (ENG-04 follow-up)
- **User selection:** Abstract base class with pluggable adapters
- **Decision:** ABC with `order_ingredients()`, `generate_po()`, `send_po()`, `track_status()`; v1 ships email-based PO

### 12. Number of v1 supplier adapters
- **User selection:** One: email-based PO delivery
- **Decision:** Email-based PDF PO delivery for v1; supplier-specific API adapters deferred

## Summary

12 questions asked across 6 primary areas + 4 follow-up areas. All decisions locked. Scope resolved (ROADMAP wins). No scope creep — deferred items captured.
