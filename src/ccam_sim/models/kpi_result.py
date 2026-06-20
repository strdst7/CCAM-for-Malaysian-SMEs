"""KPI result dataclass — typed output from KPI engine."""

from dataclasses import dataclass


@dataclass
class KPIResult:
    """Typed KPI computation result.

    All fields computed from simulation event log by kpi_engine.
    Used by output.py to produce JSON and human-readable summaries.
    """
    stockout_frequency: float
    waste_rate: float
    bottleneck_frequency: float
    order_completion_time_minutes: float
    throughput_orders_per_hour: float

    total_orders_placed: int
    total_orders_completed: int
    total_stockouts: int
    total_waste_events: int
    total_bottleneck_minutes: float
    total_revenue: float
