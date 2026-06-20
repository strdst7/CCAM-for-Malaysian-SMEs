"""Tests for KPI engine."""
import random
from ccam_sim.engines.kpi import kpi_engine
from ccam_sim.models import SimState
from ccam_sim.models.events import StockoutEvent, OrderCompleted

ATTRS = ["stockout_frequency", "waste_rate", "bottleneck_frequency",
         "order_completion_time_minutes", "throughput_orders_per_hour"]


class TestKPIEngine:
    def test_sets_kpis(self, empty_state):
        assert kpi_engine(empty_state).kpis is not None

    def test_all_kpi_attributes(self, empty_state):
        from ccam_sim.models import KPIResult
        kpi = kpi_engine(empty_state).kpis
        assert isinstance(kpi, KPIResult)
        for a in ATTRS:
            assert hasattr(kpi, a)

    def test_kpis_numeric(self, empty_state):
        kpi = kpi_engine(empty_state).kpis
        for a in ATTRS:
            assert isinstance(getattr(kpi, a), (int, float))

    def test_stockout_frequency(self, simple_scenario):
        state = SimState(rng=random.Random(42), scenario=simple_scenario)
        state.events.append(StockoutEvent(time_us=1000, ingredient="rice", requested_qty=5, available_qty=2, order_id=1))
        kpi = kpi_engine(state).kpis
        assert abs(kpi.stockout_frequency - 1.0/simple_scenario.simulation.total_hours) < 0.001

    def test_throughput(self, simple_scenario):
        state = SimState(rng=random.Random(42), scenario=simple_scenario)
        state.events.append(OrderCompleted(time_us=1000, order_id=1, completion_time_minutes=5, total_prep_time_seconds=300, station_ids=["a"]))
        state.events.append(OrderCompleted(time_us=2000, order_id=2, completion_time_minutes=8, total_prep_time_seconds=300, station_ids=["a"]))
        kpi = kpi_engine(state).kpis
        assert abs(kpi.throughput_orders_per_hour - 2.0/simple_scenario.simulation.total_hours) < 0.001
