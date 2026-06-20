import pytest
import random
from pathlib import Path
from ccam_sim.models import load_scenario, Scenario, SimState
from ccam_sim.rand import create_rng


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def simple_scenario() -> Scenario:
    return load_scenario(str(FIXTURES_DIR / "simple_restaurant.yaml"))


@pytest.fixture
def overload_scenario() -> Scenario:
    return load_scenario(str(FIXTURES_DIR / "overload_scenario.yaml"))


@pytest.fixture
def negative_stock_scenario() -> Scenario:
    return load_scenario(str(FIXTURES_DIR / "negative_stock_scenario.yaml"))


@pytest.fixture
def infinite_loop_scenario() -> Scenario:
    return load_scenario(str(FIXTURES_DIR / "infinite_loop_scenario.yaml"))


@pytest.fixture
def seeded_rng() -> random.Random:
    return create_rng(42)


@pytest.fixture
def empty_state(simple_scenario, seeded_rng) -> SimState:
    return SimState(rng=seeded_rng, scenario=simple_scenario)


@pytest.fixture
def cli_runner():
    from click.testing import CliRunner
    return CliRunner()
