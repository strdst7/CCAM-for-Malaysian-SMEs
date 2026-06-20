"""Tests for safety layer — Gate 1 and Gate 2."""
import pytest
import random
from ccam_sim.safety import validate_scenario, check_per_tick, SafetyError
from ccam_sim.models import SimState, Scenario, SimulationConfig, Station


class TestSafetyGate1:
    def test_valid_passes(self, simple_scenario):
        validate_scenario(simple_scenario)

    def test_rejects_negative_stock(self, negative_stock_scenario):
        with pytest.raises(SafetyError, match="[Nn]egative"):
            validate_scenario(negative_stock_scenario)

    def test_rejects_zero_staff(self, overload_scenario):
        with pytest.raises(SafetyError, match="staff_count"):
            validate_scenario(overload_scenario)

    def test_rejects_max_steps_zero(self, infinite_loop_scenario):
        with pytest.raises(SafetyError, match="max_steps"):
            validate_scenario(infinite_loop_scenario)


class TestSafetyGate2:
    def test_valid_passes(self, empty_state):
        check_per_tick(empty_state)

    def test_rejects_negative_stock(self, simple_scenario):
        state = SimState(rng=random.Random(42), scenario=simple_scenario, stock_levels={"x": -1})
        with pytest.raises(SafetyError):
            check_per_tick(state)

    def test_rejects_step_exceeded(self, simple_scenario):
        state = SimState(rng=random.Random(42), scenario=simple_scenario, step=99999, stock_levels={"x": 1})
        with pytest.raises(SafetyError):
            check_per_tick(state)
