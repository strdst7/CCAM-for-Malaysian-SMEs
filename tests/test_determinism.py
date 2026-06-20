"""Deterministic replay tests — SIM-08: same YAML + seed = identical output.

This is the most important test in Phase 1. If this test fails,
the simulator is NOT deterministic and cannot serve as the system governor.
"""

import pytest
import json
from ccam_sim import run_simulation, load_scenario


class TestDeterministicReplay:
    """Core determinism tests — SIM-08 requirement."""

    def test_same_seed_same_kpis(self, simple_scenario):
        r1 = run_simulation(simple_scenario, seed=42)
        r2 = run_simulation(simple_scenario, seed=42)
        assert r1.kpis == r2.kpis, (
            f"Determinism violation! KPIs differ with same seed.\n"
            f"Run 1: {r1.kpis}\nRun 2: {r2.kpis}"
        )

    def test_same_seed_same_event_count(self, simple_scenario):
        r1 = run_simulation(simple_scenario, seed=42)
        r2 = run_simulation(simple_scenario, seed=42)
        assert len(r1.events) == len(r2.events), (
            f"Event count differs: {len(r1.events)} vs {len(r2.events)}"
        )

    def test_same_seed_same_step_count(self, simple_scenario):
        r1 = run_simulation(simple_scenario, seed=42)
        r2 = run_simulation(simple_scenario, seed=42)
        assert r1.step == r2.step, (
            f"Step count differs: {r1.step} vs {r2.step}"
        )

    def test_different_seed_different_kpis(self, simple_scenario):
        r1 = run_simulation(simple_scenario, seed=42)
        r2 = run_simulation(simple_scenario, seed=99)
        assert r1.kpis != r2.kpis or len(r1.events) != len(r2.events), (
            "Different seeds produced near-identical results (very unlikely)"
        )

    def test_three_runs_same_seed(self, simple_scenario):
        results = [run_simulation(simple_scenario, seed=42).kpis for _ in range(3)]
        assert results[0] == results[1] == results[2], (
            "Three runs with same seed produced different KPIs"
        )

    def test_deterministic_across_scenarios(self):
        scenarios = [
            load_scenario("tests/fixtures/simple_restaurant.yaml"),
        ]
        for sc in scenarios:
            r1 = run_simulation(sc, seed=42)
            r2 = run_simulation(sc, seed=42)
            assert r1.kpis == r2.kpis, f"Determinism failed for scenario"

    def test_kpi_json_output_deterministic(self, simple_scenario):
        from ccam_sim.output import format_kpi_json
        r1 = run_simulation(simple_scenario, seed=42)
        r2 = run_simulation(simple_scenario, seed=42)
        j1 = format_kpi_json(r1)
        j2 = format_kpi_json(r2)
        assert j1 == j2, "JSON output differs with same seed"
        parsed = json.loads(j1)
        assert "kpis" in parsed
        assert "simulation" in parsed
