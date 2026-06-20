# Plan 01-02 Summary: CLI, Safety Layer & Output Formatter

**Status:** Complete
**Date:** 2026-06-21

## What Was Built

1. **Click CLI** (`cli.py`, `__main__.py`) — `ccam-sim simulate` command with `--seed`, `--output`, `--quiet` options
2. **Safety Layer** (`safety.py`) — Gate 1 (static: no negative stock, staff≥1, max_steps>0) + Gate 2 (per-tick: no negative stock, step limit)
3. **Output Formatter** (`output.py`) — `format_kpi_json()` producing structured JSON with 5 KPIs + events summary, `format_summary()` producing human-readable box-drawing table
4. **Scenario loader enhancement** — `resolve_scenario_path()` with .yaml/.yml extension fallback

## Files Created

- `src/ccam_sim/cli.py`
- `src/ccam_sim/__main__.py`
- `src/ccam_sim/safety.py`
- `src/ccam_sim/output.py`

## Files Modified

- `src/ccam_sim/models/loader.py` (added `resolve_scenario_path`)

## Verification

- `ccam-sim --help` shows simulate subcommand
- Safety rejects negative stock, zero staff, max_steps=0
- Safety rejects negative stock at runtime, step limit exceeded
- JSON output has all 5 KPI keys + events_summary
- Human-readable summary has box drawing characters + KPI labels
- Handles null KPI gracefully (defaults to 0)
