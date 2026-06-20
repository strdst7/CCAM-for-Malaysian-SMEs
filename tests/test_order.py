"""Tests for order generator."""
from ccam_sim.engines.demand import demand_generator
from ccam_sim.engines.order import order_generator
from ccam_sim.models import DemandArrival, OrderPlaced


class TestOrderGenerator:
    def test_converts_arrivals(self, empty_state):
        state = order_generator(demand_generator(empty_state))
        assert len([e for e in state.events if isinstance(e, OrderPlaced)]) > 0

    def test_items_1_to_5(self, empty_state):
        state = order_generator(demand_generator(empty_state))
        for o in [e for e in state.events if isinstance(e, OrderPlaced)]:
            assert 1 <= len(o.items) <= 5

    def test_items_have_fields(self, empty_state):
        state = order_generator(demand_generator(empty_state))
        for o in [e for e in state.events if isinstance(e, OrderPlaced)]:
            for item in o.items:
                assert "item_id" in item and "prep_time_seconds" in item and "station" in item

    def test_current_orders_populated(self, empty_state):
        state = order_generator(demand_generator(empty_state))
        assert len(state.current_orders) > 0

    def test_deterministic(self, simple_scenario):
        import random
        from ccam_sim.models import SimState
        def run():
            s = SimState(rng=random.Random(42), scenario=simple_scenario)
            s = order_generator(demand_generator(s))
            return [e for e in s.events if isinstance(e, OrderPlaced)]
        o1, o2 = run(), run()
        assert len(o1) == len(o2)
        for a, b in zip(o1, o2):
            assert a.order_id == b.order_id
