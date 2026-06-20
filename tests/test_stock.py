"""Tests for stock engine."""
from ccam_sim.engines.demand import demand_generator
from ccam_sim.engines.order import order_generator
from ccam_sim.engines.kitchen import kitchen_engine
from ccam_sim.engines.stock import stock_engine
from ccam_sim.models import StockConsumed, StockoutEvent, WasteEvent, OrderCompleted


def _run(state, ticks):
    state = order_generator(demand_generator(state))
    for step in range(ticks):
        state.step = step
        state.time_us = step * state.scenario.simulation.tick_interval_minutes * 60 * 1_000_000
        state = kitchen_engine(state)
        state = stock_engine(state)
    return state


class TestStockEngine:
    def test_consumes_for_completed(self, simple_scenario):
        import random
        from ccam_sim.models import SimState
        state = _run(SimState(rng=random.Random(42), scenario=simple_scenario), 100)
        if [e for e in state.events if isinstance(e, OrderCompleted)]:
            assert len([e for e in state.events if isinstance(e, StockConsumed)]) > 0

    def test_stockouts_with_low_stock(self, simple_scenario):
        import random
        from ccam_sim.models import SimState, Scenario
        low = Scenario(simulation=simple_scenario.simulation,
                       demand_pattern=simple_scenario.demand_pattern,
                       menu=simple_scenario.menu, stations=simple_scenario.stations,
                       stock={k: 0.5 for k in simple_scenario.stock},
                       supplier_delays=simple_scenario.supplier_delays)
        state = _run(SimState(rng=random.Random(42), scenario=low), 200)
        assert len([e for e in state.events if isinstance(e, StockoutEvent)]) > 0
        assert len([e for e in state.events if isinstance(e, WasteEvent)]) > 0

    def test_initializes_stock(self, empty_state):
        state = stock_engine(empty_state)
        for ing, qty in state.scenario.stock.items():
            assert state.stock_levels.get(ing) == qty
