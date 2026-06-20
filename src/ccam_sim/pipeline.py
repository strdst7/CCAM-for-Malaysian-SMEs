"""Simulation pipeline — chains all 5 engines with safety per-tick enforcement.

This is the main entry point for running simulations. Imported by:
- CLI (ccam_sim.cli) for the `simulate` command
- Phase 3 FastAPI for REST API simulation
"""

from ccam_sim.models import Scenario, SimState
from ccam_sim.rand import create_rng
from ccam_sim.engines.demand import demand_generator
from ccam_sim.engines.order import order_generator
from ccam_sim.engines.kitchen import kitchen_engine
from ccam_sim.engines.stock import stock_engine
from ccam_sim.engines.kpi import kpi_engine
from ccam_sim.safety import check_per_tick, SafetyError


def run_simulation(scenario: Scenario, seed: int) -> SimState:
    """Run deterministic simulation from scenario YAML data.

    Args:
        scenario: Parsed and validated Scenario dataclass.
        seed: Integer RNG seed for deterministic replay.

    Returns:
        SimState with populated kpis and events after full simulation.

    Raises:
        SafetyError: If a per-tick safety check fails during simulation.
    """
    rng = create_rng(seed)
    state = SimState(
        rng=rng,
        scenario=scenario,
        seed=seed,
    )

    total_hours = scenario.simulation.total_hours
    tick_interval_minutes = scenario.simulation.tick_interval_minutes
    max_steps = scenario.simulation.max_steps
    tick_duration_us = tick_interval_minutes * 60 * 1_000_000
    total_duration_us = int(total_hours * 3_600_000_000)

    state = demand_generator(state)

    state = order_generator(state)

    state.step = 0
    state.time_us = 0

    while state.time_us < total_duration_us and state.step < max_steps:
        state.step += 1

        state = kitchen_engine(state)

        state = stock_engine(state)

        check_per_tick(state)

        state.time_us += tick_duration_us

    state = kpi_engine(state)

    state.simulated_hours = total_hours

    return state
