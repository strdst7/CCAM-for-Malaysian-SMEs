from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass(kw_only=True)
class SimulationEvent:
    time_us: int
    type: str = ""


@dataclass(kw_only=True)
class DemandArrival(SimulationEvent):
    type: str = "demand_arrival"


@dataclass(kw_only=True)
class OrderPlaced(SimulationEvent):
    order_id: int
    items: List[Dict]
    type: str = "order_placed"


@dataclass(kw_only=True)
class OrderCompleted(SimulationEvent):
    order_id: int
    completion_time_minutes: float
    total_prep_time_seconds: float
    station_ids: List[str]
    type: str = "order_completed"


@dataclass(kw_only=True)
class StockoutEvent(SimulationEvent):
    ingredient: str
    requested_qty: float
    available_qty: float
    order_id: int
    type: str = "stockout"


@dataclass(kw_only=True)
class BottleneckEvent(SimulationEvent):
    station_id: str
    backlog_seconds: float
    capacity_seconds: float
    duration_seconds: float
    type: str = "bottleneck"


@dataclass(kw_only=True)
class WasteEvent(SimulationEvent):
    ingredient: str
    qty: float
    waste_cost: float
    reason: str = "expired"
    type: str = "waste"


@dataclass(kw_only=True)
class StockConsumed(SimulationEvent):
    ingredient: str
    qty: float
    order_id: int
    unit_cost: float = 0.0
    type: str = "stock_consumed"
