"""Tests for demand generator — Poisson process arrival generation."""
import pytest
from ccam_sim.engines.demand import demand_generator
from ccam_sim.models import SimState, DemandArrival


class TestDemandGenerator:
    def test_generates_arrivals(self, empty_state):
        state = demand_generator(empty_state)
        arrivals = [e for e in state.events if isinstance(e, DemandArrival)]
        assert len(arrivals) > 0

    def test_arrivals_have_time_us(self, empty_state):
        state = demand_generator(empty_state)
        for a in [e for e in state.events if isinstance(e, DemandArrival)]:
            assert a.time_us > 0
            assert isinstance(a.time_us, int)

    def test_arrivals_within_window(self, empty_state):
        max_us = int(empty_state.scenario.simulation.total_hours * 3_600_000_000)
        state = demand_generator(empty_state)
        for a in [e for e in state.events if isinstance(e, DemandArrival)]:
            assert a.time_us < max_us

    def test_zero_rate_no_arrivals(self):
        from ccam_sim.models import Scenario, SimulationConfig, DemandBlock
        import random
        s = Scenario(simulation=SimulationConfig(total_hours=8),
                     demand_pattern=[DemandBlock(0, 8, 0, {})],
                     menu=[], stations=[], stock={}, supplier_delays={})
        state = SimState(rng=random.Random(42), scenario=s)
        state = demand_generator(state)
        assert len([e for e in state.events if isinstance(e, DemandArrival)]) == 0

    def test_deterministic(self, simple_scenario):
        import random
        s1 = demand_generator(SimState(rng=random.Random(42), scenario=simple_scenario))
        s2 = demand_generator(SimState(rng=random.Random(42), scenario=simple_scenario))
        t1 = [e.time_us for e in s1.events if isinstance(e, DemandArrival)]
        t2 = [e.time_us for e in s2.events if isinstance(e, DemandArrival)]
        assert t1 == t2

    def test_different_seed(self, simple_scenario):
        import random
        s1 = demand_generator(SimState(rng=random.Random(42), scenario=simple_scenario))
        s2 = demand_generator(SimState(rng=random.Random(99), scenario=simple_scenario))
        t1 = [e.time_us for e in s1.events if isinstance(e, DemandArrival)]
        t2 = [e.time_us for e in s2.events if isinstance(e, DemandArrival)]
        assert t1 != t2
