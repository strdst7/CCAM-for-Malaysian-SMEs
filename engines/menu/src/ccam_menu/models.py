"""Data models for menu optimization."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MenuItem:
    """A single menu item in the optimization scope."""
    id: str
    name: str
    category: str                     # "main", "side", "drink", "special"
    current_price_cents: int
    cost_cents: int                   # ingredient cost
    margin_cents: int                 # current_price - cost
    margin_pct: float                 # margin/cost, e.g. 0.65 for 65%
    prep_time_seconds: int
    avg_daily_orders: float           # from historical/KPI data
    is_active: bool = True


@dataclass
class MenuConstraints:
    """Constraints for the optimization problem."""
    min_price_cents: int = 100         # minimum price for any item (RM1)
    max_price_cents: int = 50000       # maximum price (RM500)
    min_margin_pct: float = 0.20       # minimum 20% margin on all items
    max_items_per_category: int = 15   # cap items per category
    min_items_per_category: int = 2    # minimum variety per category
    max_total_items: int = 80          # total menu size cap


@dataclass
class OptimizationObjective:
    """Optimization objective weights."""
    profit_weight: float = 0.5         # maximize profit contribution
    variety_weight: float = 0.2        # maintain category variety
    simplicity_weight: float = 0.1     # prefer fewer items (operational)
    price_stability_weight: float = 0.2  # minimize price changes


@dataclass
class PriceChange:
    """A recommended price change for a menu item."""
    item_id: str
    item_name: str
    old_price_cents: int
    new_price_cents: int
    change_pct: float
    reason: str = ""


@dataclass
class MenuRecommendation:
    """Complete menu optimization recommendation."""
    changes: list[PriceChange] = field(default_factory=list)
    items_to_remove: list[str] = field(default_factory=list)
    items_to_add: list[MenuItem] = field(default_factory=list)
    projected_profit_cents: int = 0
    current_profit_cents: int = 0
    safety_checks_passed: bool = False
    safety_violations: list[str] = field(default_factory=list)
    solver_status: str = ""            # "optimal", "feasible", "infeasible", "error"
    optimization_score: float = 0.0    # 0-100 quality score
