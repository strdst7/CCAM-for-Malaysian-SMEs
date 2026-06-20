"""Order generator — converts synthetic demand into structured orders."""

from ccam_sim.models import SimState, DemandArrival, OrderPlaced


def order_generator(state: SimState) -> SimState:
    """Convert each DemandArrival event into an OrderPlaced event."""
    rng = state.rng
    scenario = state.scenario

    menu_map = {item.id: item for item in scenario.menu}

    demand_arrivals = [e for e in state.events if isinstance(e, DemandArrival)]
    existing_orders = [e for e in state.events if isinstance(e, OrderPlaced)]
    next_order_id = len(existing_orders) + 1

    for arrival in demand_arrivals:
        arrival_hours = arrival.time_us / 3_600_000_000.0
        active_block = None
        for block in scenario.demand_pattern:
            if block.start_hour <= arrival_hours < block.end_hour:
                active_block = block
                break
        if active_block is None:
            if scenario.demand_pattern:
                active_block = scenario.demand_pattern[-1]
            else:
                continue

        num_items = rng.randint(1, 5)
        items = []
        if active_block.item_weights:
            item_ids = list(active_block.item_weights.keys())
            weights = list(active_block.item_weights.values())
            selected_ids = rng.choices(item_ids, weights=weights, k=num_items)
            for item_id in selected_ids:
                menu_item = menu_map.get(item_id)
                if menu_item:
                    items.append({
                        "item_id": item_id,
                        "name": menu_item.name,
                        "prep_time_seconds": menu_item.prep_time_seconds,
                        "station": menu_item.station,
                        "ingredients": dict(menu_item.ingredients),
                    })
        elif scenario.menu:
            for _ in range(num_items):
                item = rng.choice(scenario.menu)
                items.append({
                    "item_id": item.id,
                    "name": item.name,
                    "prep_time_seconds": item.prep_time_seconds,
                    "station": item.station,
                    "ingredients": dict(item.ingredients),
                })

        if items:
            order_event = OrderPlaced(
                time_us=arrival.time_us,
                order_id=next_order_id,
                items=items,
            )
            state.events.append(order_event)
            state.current_orders.append({
                "order_id": next_order_id,
                "items": items,
                "arrival_time_us": arrival.time_us,
                "station_prep": {},
            })
            next_order_id += 1

    return state
