"""Safety layer — static validation (Gate 1) and per-tick enforcement (Gate 2).

Gate 1 is called once after scenario loading, before simulation begins.
Gate 2 is called every tick during simulation to enforce runtime invariants.
"""

from ccam_sim.models import Scenario, SimState


class SafetyError(Exception):
    """Raised when a safety rule is violated."""


def validate_scenario(scenario: Scenario) -> None:
    """Gate 1 — Validate scenario before simulation begins.

    Checks:
    1. No negative initial stock levels
    2. No station with staff_count < 1
    3. max_steps > 0 (infinite loop guard)

    Raises:
        SafetyError: On first violation with descriptive message.
    """
    _check_negative_stock(scenario)
    _check_station_utilization(scenario)
    _check_max_steps(scenario)


def _check_negative_stock(scenario: Scenario) -> None:
    """Rule: No ingredient can have negative initial stock."""
    for ingredient, qty in scenario.stock.items():
        if qty < 0:
            raise SafetyError(
                f"Negative stock for '{ingredient}': {qty}. "
                f"All stock levels must be >= 0."
            )


def _check_station_utilization(scenario: Scenario) -> None:
    """Rule: No station can have staff_count less than 1."""
    for station in scenario.stations:
        if station.staff_count < 1:
            raise SafetyError(
                f"Station '{station.id}' has staff_count={station.staff_count}. "
                f"Each station must have at least 1 staff member."
            )


def _check_max_steps(scenario: Scenario) -> None:
    """Rule: max_steps must be > 0 (infinite loop guard)."""
    if scenario.simulation.max_steps < 1:
        raise SafetyError(
            f"simulation.max_steps={scenario.simulation.max_steps}. "
            f"max_steps must be greater than 0 to prevent infinite loops."
        )


def check_per_tick(state: SimState) -> None:
    """Gate 2 — Enforce runtime invariants after each simulation tick.

    Checks:
    1. No ingredient stock went negative this tick
    2. Step limit not exceeded (infinite loop guard)

    Raises:
        SafetyError: On first violation with descriptive message.
    """
    _check_stock_non_negative(state)
    _check_step_limit(state)


def _check_stock_non_negative(state: SimState) -> None:
    """Rule: No ingredient stock level can go below 0."""
    for ingredient, qty in state.stock_levels.items():
        if qty < 0:
            raise SafetyError(
                f"Stock for '{ingredient}' went negative: {qty}. "
                f"Stock level must never drop below 0."
            )


def _check_step_limit(state: SimState) -> None:
    """Rule: step count must not exceed max_steps (infinite loop guard)."""
    if state.step > state.scenario.simulation.max_steps:
        raise SafetyError(
            f"Step limit exceeded: {state.step} > {state.scenario.simulation.max_steps}. "
            f"Simulation terminated — possible infinite loop."
        )


def _check_backlog_bounds(state: SimState) -> None:
    """Rule: No station backlog can exceed 10x its per-tick capacity.

    Defined but not called in Plan 02. Will be called in Plan 03 after
    the kitchen engine populates station_states.
    """
    tick_duration_seconds = state.scenario.simulation.tick_interval_minutes * 60.0
    for station_id, st in state.station_states.items():
        capacity_per_tick = st.staff_count * tick_duration_seconds
        if capacity_per_tick > 0 and st.current_backlog_seconds > capacity_per_tick * 10:
            raise SafetyError(
                f"Station '{station_id}' backlog ({st.current_backlog_seconds:.1f}s) "
                f"exceeded 10x capacity ({capacity_per_tick * 10:.1f}s). "
                f"Unstable backlog detected."
            )
