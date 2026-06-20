"""Stock engine — ingredient consumption, stockout detection, waste tracking."""

from ccam_sim.models import (
    SimState, OrderCompleted, StockConsumed, StockoutEvent, WasteEvent, OrderPlaced,
)


def stock_engine(state: SimState) -> SimState:
    """Process stock consumption for all completed orders in this tick."""
    processed_order_ids = set()
    for event in state.events:
        if isinstance(event, StockConsumed):
            processed_order_ids.add(event.order_id)

    scenario = state.scenario
    menu_map = {item.id: item for item in scenario.menu}

    if not state.stock_levels:
        state.stock_levels = dict(scenario.stock)

    completed_events = [
        e for e in state.events
        if isinstance(e, OrderCompleted) and e.order_id not in processed_order_ids
    ]

    for completed in completed_events:
        order_placed = None
        for e in state.events:
            if isinstance(e, OrderPlaced) and e.order_id == completed.order_id:
                order_placed = e
                break
        if order_placed is None:
            continue

        has_consumed = False

        for item in order_placed.items:
            item_id = item.get("item_id", "")
            menu_item = menu_map.get(item_id)
            if menu_item is None:
                continue

            for ingredient, qty_needed in menu_item.ingredients.items():
                current_stock = state.stock_levels.get(ingredient, 0.0)
                if current_stock >= qty_needed:
                    state.stock_levels[ingredient] = current_stock - qty_needed
                    state.events.append(StockConsumed(
                        time_us=state.time_us,
                        ingredient=ingredient, qty=qty_needed,
                        order_id=completed.order_id, unit_cost=0.0,
                    ))
                    has_consumed = True
                elif current_stock > 0:
                    state.stock_levels[ingredient] = 0.0
                    state.events.append(StockConsumed(
                        time_us=state.time_us,
                        ingredient=ingredient, qty=current_stock,
                        order_id=completed.order_id, unit_cost=0.0,
                    ))
                    state.events.append(StockoutEvent(
                        time_us=state.time_us, ingredient=ingredient,
                        requested_qty=qty_needed, available_qty=current_stock,
                        order_id=completed.order_id,
                    ))
                    state.events.append(WasteEvent(
                        time_us=state.time_us, ingredient=ingredient,
                        qty=qty_needed - current_stock, waste_cost=0.0,
                        reason="stockout_shortfall",
                    ))
                    has_consumed = True
                else:
                    state.events.append(StockConsumed(
                        time_us=state.time_us,
                        ingredient=ingredient, qty=0.0,
                        order_id=completed.order_id, unit_cost=0.0,
                    ))
                    state.events.append(StockoutEvent(
                        time_us=state.time_us, ingredient=ingredient,
                        requested_qty=qty_needed, available_qty=0.0,
                        order_id=completed.order_id,
                    ))
                    state.events.append(WasteEvent(
                        time_us=state.time_us, ingredient=ingredient,
                        qty=qty_needed, waste_cost=0.0,
                        reason="stockout_unavailable",
                    ))
                    has_consumed = True

        if not has_consumed:
            state.events.append(StockConsumed(
                time_us=state.time_us,
                ingredient="_none", qty=0.0,
                order_id=completed.order_id, unit_cost=0.0,
            ))

    return state
