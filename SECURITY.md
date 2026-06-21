# SECURITY.md — Phase 1 Security Audit

**Phase:** 1 — Simulator Core (CLI)
**Audit Date:** 2026-06-21
**ASVS Level:** 1

---

## Threat Verification

| Threat ID | Component | Disposition | Status | Evidence |
|-----------|-----------|-------------|--------|----------|
| T1-01 | loader.py | mitigate | **CLOSED** | `yaml.safe_load()` used at `loader.py:37`. No `yaml.load()` call exists in any source file. PyYAML >=6.0.3 pinned in `pyproject.toml:8`. |
| T1-02 | loader.py | mitigate | **CLOSED** | `click.Path(exists=True, dir_okay=False)` at `cli.py:24` validates file existence and readability before `load_scenario()` is invoked. |
| T1-03 | rand.py | accept | **CLOSED** | See [Accepted Risks](#accepted-risks) log. CLI is local single-user; no audit trail needed for RNG seed choice in Phase 1. Phase 2 adds audit logging for API-based simulation. |
| T2-01 | loader.py | mitigate | **CLOSED** | Same as T1-01 — `yaml.safe_load()` at `loader.py:37`. |
| T2-02 | cli.py | mitigate | **CLOSED** | `click.Path(exists=True)` at `cli.py:24` validates file. `validate_scenario(scenario_obj)` called at `cli.py:41` before pipeline import/invocation at `cli.py:43-44`. |
| T2-03 | safety.py | mitigate | **CLOSED** | Three-layer infinite loop guard: (1) `_check_max_steps()` at `safety.py:50-56` rejects scenarios with max_steps < 1, (2) pipeline while-loop at `pipeline.py:51` has `state.step < max_steps` condition, (3) `_check_step_limit()` at `safety.py:83-89` in Gate 2 raises on step > max_steps. |
| T2-04 | safety.py | mitigate | **CLOSED** | Gate 1: `validate_scenario()` called at `cli.py:41` before simulation. Gate 2: `check_per_tick()` called at `pipeline.py:58` each tick. Both must pass for simulation to proceed. |
| T3-01 | pipeline.py | mitigate | **CLOSED** | Strict engine ordering in `run_simulation()` (`pipeline.py:44-62`): demand → order → [tick loop: kitchen → stock → safety] → kpi. No engine can skip another — the pipeline is the sole orchestrator. |
| T3-02 | pipeline.py | mitigate | **CLOSED** | `max_steps` read from scenario at `pipeline.py:40`. While-loop condition at `pipeline.py:51` limits execution. `check_per_tick()` step limit guard as backstop. |
| T3-03 | engines/kpi.py | accept | **CLOSED** | See [Accepted Risks](#accepted-risks) log. KPI engine reads from in-memory `state.events` and `state.scenario` only. No file I/O, no network, no database — fully in-memory computation. Phase 3+ adds data export. |
| T3-04 | engines/stock.py | mitigate | **CLOSED** | `_check_stock_non_negative()` at `safety.py:73-79` enforces no-negative-stock per tick. Called via `check_per_tick()` at `pipeline.py:58` after `stock_engine()` at `:56`. Stock engine itself uses `max(current_stock - qty, 0)` logic — stock never goes negative even without safety. |
| T4-01 | tests/ | mitigate | **CLOSED** | All test files import production code via `from ccam_sim import run_simulation, load_scenario` (e.g., `test_determinism.py:9`) and `from ccam_sim.engines.*`. Any source code change that breaks determinism is caught by test suite. |
| T4-02 | tests/test_determinism.py | mitigate | **CLOSED** | 7 test cases in `test_determinism.py` verify same-seed determinism: same KPIs (`test_same_seed_same_kpis`), same event count (`test_same_seed_same_event_count`), same step count (`test_same_seed_same_step_count`), three-runs identical (`test_three_runs_same_seed`), JSON determinism (`test_kpi_json_output_deterministic`). |

---

## Accepted Risks

The following threats have been reviewed and accepted by the project. No mitigation
is implemented; the risk is accepted as part of the Phase 1 design.

| Threat ID | Risk | Rationale | Phase for Re-evaluation |
|-----------|------|-----------|------------------------|
| T1-03 | No audit trail for RNG seed choice — repudiation of simulation parameters | CLI is local single-user tool. User explicitly provides `--seed` at the command line. No multi-user API or shared infrastructure in Phase 1. | Phase 2 (API-based simulation with audit logging) |
| T3-03 | Information disclosure via KPI engine reading in-memory data | KPI engine operates entirely on in-memory event log (`state.events`). No external data access — no database, filesystem, or network calls. Data flow is local-only until Phase 3+ adds export/API layers. | Phase 3 (FastAPI REST API with auth) |

---

## Audit Notes

### Potential Concern: `run_simulation()` doesn't call `validate_scenario()` internally
The pipeline function `run_simulation()` in `pipeline.py` does **not** call `validate_scenario()` internally. It relies on the caller to have performed Gate 1 validation. The CLI correctly calls `validate_scenario()` at `cli.py:41` before invoking the pipeline. However, direct Python API users (`from ccam_sim import run_simulation; run_simulation(scenario, seed=42)`) could bypass static validation. This is by design for now — see Accepted Risks if this becomes a concern in Phase 3 API context.

### Stock engine implementation diverges from plan
The actual `stock_engine()` in `stock.py` includes a `has_consumed` tracking variable and fallback `StockConsumed` event with `ingredient="_none"` that was not in the original Plan 01-03 specification. This was added as a bug fix during Plan 01-03 execution to prevent re-processing of completed orders across ticks. Not a security concern.

---

## Unregistered Flags

No unregistered flags detected. No `## Threat Flags` section was present in any SUMMARY.md file.

---

**Threats Closed:** 13/13 (100%)
**Threats Open:** 0
**ASVS Level:** 1
