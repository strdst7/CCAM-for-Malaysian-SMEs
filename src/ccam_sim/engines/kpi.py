"""KPI engine — computes simulation metrics from event log into typed KPIResult."""

from ccam_sim.models import SimState, KPIResult
from ccam_sim.models.events import (
    StockoutEvent, WasteEvent, BottleneckEvent, OrderCompleted, StockConsumed,
    OrderPlaced,
)


def kpi_engine(state: SimState) -> SimState:
    """Compute KPIs and event count aggregates from the simulation event log.

    Returns state with state.kpis set to a typed KPIResult instance (not a dict).
    """
    events = state.events
    total_hours = state.scenario.simulation.total_hours
    if total_hours <= 0:
        total_hours = 1.0

    stockout_events = [e for e in events if isinstance(e, StockoutEvent)]
    waste_events = [e for e in events if isinstance(e, WasteEvent)]
    bottleneck_events = [e for e in events if isinstance(e, BottleneckEvent)]
    completed_orders = [e for e in events if isinstance(e, OrderCompleted)]
    placed_orders = [e for e in events if isinstance(e, OrderPlaced)]

    consumed_events = [e for e in events if isinstance(e, StockConsumed)]
    total_consumed = sum(e.qty for e in consumed_events)
    total_waste_qty = sum(e.qty for e in waste_events)

    total_bottleneck_minutes = sum(
        e.duration_seconds / 60.0 for e in bottleneck_events
    )

    completion_times = [e.completion_time_minutes for e in completed_orders]
    mean_completion = (
        sum(completion_times) / len(completion_times)
        if completion_times else 0.0
    )

    state.kpis = KPIResult(
        stockout_frequency=len(stockout_events) / total_hours,
        waste_rate=total_waste_qty / max(total_consumed, 1.0),
        bottleneck_frequency=total_bottleneck_minutes / total_hours,
        order_completion_time_minutes=mean_completion,
        throughput_orders_per_hour=len(completed_orders) / total_hours,
        total_orders_placed=len(placed_orders),
        total_orders_completed=len(completed_orders),
        total_stockouts=len(stockout_events),
        total_waste_events=len(waste_events),
        total_bottleneck_minutes=total_bottleneck_minutes,
        total_revenue=0.0,
    )

    return state
