# Plan 01-04 Summary: Test Suite

**Status:** Complete
**Date:** 2026-06-21

## What Was Built

1. **Test fixtures** — 3 new edge-case YAML scenarios:
   - `overload_scenario.yaml` (staff_count=0 → Gate 1)
   - `negative_stock_scenario.yaml` (stock=-50 → Gate 1)
   - `infinite_loop_scenario.yaml` (max_steps=0 → Gate 1)

2. **Shared conftest** (`tests/conftest.py`) — pytest fixtures: `simple_scenario`, `overload_scenario`, `negative_stock_scenario`, `infinite_loop_scenario`, `seeded_rng`, `empty_state`, `cli_runner`

3. **Engine unit tests** (6 files, 29 tests):
   - `test_demand.py` — arrival generation, time bounds, zero rate, determinism (6 tests)
   - `test_order.py` — arrival→order conversion, item counts 1-5, field presence, determinism (5 tests)
   - `test_kitchen.py` — station init, order completion, determinism (3 tests)
   - `test_stock.py` — stock consumption, stockout/waste with low stock, stock init (3 tests)
   - `test_kpi.py` — KPIResult type, attribute presence, numeric values, stockout freq, throughput (5 tests)
   - `test_safety.py` — Gate 1 (valid, negative stock, zero staff, max_steps=0) + Gate 2 (valid, negative stock, step exceeded) (7 tests)

4. **Determinism tests** (`test_determinism.py`) — SIM-08 verification (7 tests):
   - Same seed → identical KPIs, event counts, step counts
   - Different seeds → different results
   - Three runs with same seed → identical
   - JSON output determinism

5. **CLI integration tests** (`test_cli.py`) — end-to-end via Click CliRunner (8 tests):
   - `--help`, `simulate --help`
   - Valid scenario → JSON output with all 5 KPIs
   - `--output` file write
   - `--quiet` suppresses stderr
   - Non-existent file → exit code 2
   - Safety rejection → exit code 1
   - CLI determinism

## Files Created

- `tests/conftest.py`
- `tests/test_demand.py`
- `tests/test_order.py`
- `tests/test_kitchen.py`
- `tests/test_stock.py`
- `tests/test_kpi.py`
- `tests/test_safety.py`
- `tests/test_determinism.py`
- `tests/test_cli.py`
- `tests/fixtures/overload_scenario.yaml`
- `tests/fixtures/negative_stock_scenario.yaml`
- `tests/fixtures/infinite_loop_scenario.yaml`

## Files Modified

- `pyproject.toml` (added pytest dev dependency)

## Bugs Fixed During Execution

- **Kitchen determinism test:** Missing `SimState` import in closure
- **KPI test kw_only:** `StockoutEvent` and `OrderCompleted` require keyword arguments (kw_only=True dataclasses)
- **CLI nonexistent test:** Click's built-in `Path(exists=True)` exits code 2, not 1

## Verification

- Full test suite: **44 passed, 0 failed**
- Deterministic replay proven: same YAML + seed → identical KPI output (SIM-08)
- CLI integration confirmed: all commands, options, error paths
- Safety rejection confirmed: all 3 Gate 1 rules, both Gate 2 rules
