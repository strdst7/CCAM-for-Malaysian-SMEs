"""Tests for kitchen engine."""
from ccam_sim.engines.demand import demand_generator
from ccam_sim.engines.order import order_generator
from ccam_sim.engines.kitchen import kitchen_engine
from ccam_sim.models import OrderCompleted, StationState, SimState


def _run_ticks(state, n):
    for step in range(n):
        state.step = step
        state.time_us = step * state.scenario.simulation.tick_interval_minutes * 60 * 1_000_000
        state = kitchen_engine(state)
    return state


class TestKitchenEngine:
    def test_initializes_stations(self, empty_state):
        state = _run_ticks(order_generator(demand_generator(empty_state)), 1)
        assert len(state.station_states) == len(state.scenario.stations)

    def test_orders_complete(self, simple_scenario):
        import random
        from ccam_sim.models import SimState
        state = SimState(rng=random.Random(42), scenario=simple_scenario)
        state = _run_ticks(order_generator(demand_generator(state)), 50)
        assert len([e for e in state.events if isinstance(e, OrderCompleted)]) > 0

    def test_deterministic(self, simple_scenario):
        import random
        def run(seed):
            s = SimState(rng=random.Random(seed), scenario=simple_scenario)
            s = _run_ticks(order_generator(demand_generator(s)), 20)
            return [e.order_id for e in s.events if isinstance(e, OrderCompleted)]
        assert run(42) == run(42)
