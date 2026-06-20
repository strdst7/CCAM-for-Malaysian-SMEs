# Plan 01-03 Summary: Five-Engine Pipeline

**Status:** Complete
**Date:** 2026-06-21

## What Was Built

1. **Demand generator** (`engines/demand.py`) — Poisson process synthetic customer arrivals via `expovariate()`
2. **Order generator** (`engines/order.py`) — Converts demand to structured orders with weighted item selection, 1-5 items per order
3. **Kitchen engine** (`engines/kitchen.py`) — Station load simulation with prep-time accumulation, per-staff capacity, bottleneck detection at 3x capacity threshold
4. **Stock engine** (`engines/stock.py`) — Ingredient deduction per completed order, stockout detection, waste tracking, partial fulfillment
5. **KPI engine** (`engines/kpi.py`) — Computes 5 rate-based KPIs + 6 event count aggregates into typed `KPIResult` dataclass
6. **Pipeline** (`pipeline.py`) — Chains all engines: demand → order → [tick loop: kitchen → stock → safety] → kpi

## Files Created

- `src/ccam_sim/engines/__init__.py`
- `src/ccam_sim/engines/demand.py`
- `src/ccam_sim/engines/order.py`
- `src/ccam_sim/engines/kitchen.py`
- `src/ccam_sim/engines/stock.py`
- `src/ccam_sim/engines/kpi.py`
- `src/ccam_sim/pipeline.py`

## Files Modified

- `src/ccam_sim/__init__.py` (added public API exports: run_simulation, load_scenario, Scenario, SimState)

## Verification

- Pipeline runs end-to-end with `simple_restaurant.yaml` + seed 42
- Determinism: same scenario + seed produces identical KPIResult
- 184 orders placed, 182 completed in 480 steps (8 hours)
- Stockouts: 783 events (stockout_freq = 97.88/hr — ingredients deplete naturally)
- Waste rate: 0.96 (near-total consumption)
- Bottleneck freq: 11.88/hr (3 stations, 4 staff)
- Order completion time: 2.41 min mean
- Throughput: 22.75 orders/hr
- CLI outputs JSON + human-readable summary

## Bugs Fixed During Execution

- **Kitchen time gate:** Orders not processed until `arrival_time_us <= state.time_us` (prevents negative completion times)
- **Stock processed-order tracking:** Always create StockConsumed event so `processed_order_ids` prevents re-processing orders every tick (was producing 42K stockout events)
- **Backlog computation:** Changed from accumulator to fresh-computed sum of remaining prep work (fixes false-positive bottleneck inflation)
