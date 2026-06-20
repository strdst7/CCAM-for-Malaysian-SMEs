"""Kitchen engine — station load simulation, prep-time accumulation, bottleneck detection."""

from ccam_sim.models import SimState, StationState, OrderCompleted, BottleneckEvent


def kitchen_engine(state: SimState) -> SimState:
    """Process one tick of kitchen simulation."""
    scenario = state.scenario
    tick_duration_seconds = scenario.simulation.tick_interval_minutes * 60.0

    if not state.station_states:
        for station in scenario.stations:
            state.station_states[station.id] = StationState(
                station_id=station.id,
                staff_count=station.staff_count,
            )

    for order in state.current_orders:
        if order["arrival_time_us"] > state.time_us:
            continue

        if not order.get("station_prep"):
            order["station_prep"] = {}

        for item in order["items"]:
            station_id = item.get("station", "")
            prep_seconds = item.get("prep_time_seconds", 0)

            if station_id not in order["station_prep"]:
                order["station_prep"][station_id] = 0.0

            if "prep_progress" not in item:
                item["prep_progress"] = 0.0

            station_state = state.station_states.get(station_id)
            if station_state:
                capacity_this_tick = station_state.staff_count * tick_duration_seconds
                remaining = prep_seconds - item["prep_progress"]

                if remaining > 0:
                    processed = min(remaining, capacity_this_tick)
                    item["prep_progress"] += processed
                    station_state.total_utilization_seconds += processed

    backlog_by_station: dict[str, float] = {}
    for order in state.current_orders:
        if order["arrival_time_us"] > state.time_us:
            continue
        for item in order["items"]:
            station_id = item.get("station", "")
            prep_seconds = item.get("prep_time_seconds", 0)
            progress = item.get("prep_progress", 0)
            remaining = prep_seconds - progress
            if remaining > 0:
                backlog_by_station[station_id] = backlog_by_station.get(station_id, 0.0) + remaining

    for station_id, backlog in backlog_by_station.items():
        station_state = state.station_states.get(station_id)
        if station_state:
            station_state.current_backlog_seconds = backlog
            capacity_this_tick = station_state.staff_count * tick_duration_seconds
            if capacity_this_tick > 0 and backlog > capacity_this_tick * 3:
                state.events.append(BottleneckEvent(
                    time_us=state.time_us,
                    station_id=station_id,
                    backlog_seconds=backlog,
                    capacity_seconds=capacity_this_tick,
                    duration_seconds=tick_duration_seconds,
                ))
                station_state.bottleneck_seconds += tick_duration_seconds

    completed_orders = []
    for i, order in enumerate(state.current_orders):
        all_completed = True
        total_prep = 0.0
        station_ids = set()
        for item in order["items"]:
            prep = item.get("prep_time_seconds", 0)
            progress = item.get("prep_progress", 0)
            if progress < prep:
                all_completed = False
                break
            total_prep += prep
            station_ids.add(item.get("station", ""))

        if all_completed:
            completion_time_minutes = (state.time_us - order["arrival_time_us"]) / 60_000_000.0
            state.events.append(OrderCompleted(
                time_us=state.time_us,
                order_id=order["order_id"],
                completion_time_minutes=completion_time_minutes,
                total_prep_time_seconds=total_prep,
                station_ids=list(station_ids),
            ))
            completed_orders.append(i)

    for i in reversed(completed_orders):
        state.current_orders.pop(i)

    return state
