"""OR-Tools MILP solver for menu optimization.

Problem formulation:
- Decision variables: price change delta for each item, binary keep/remove
- Constraints: price bounds, margin floors, category variety, total size
- Objective: maximize weighted profit + variety + simplicity + price stability
"""

from ccam_menu.models import (
    MenuItem, MenuConstraints, OptimizationObjective,
    PriceChange, MenuRecommendation,
)
from ccam_menu.exceptions import SolverError


class MenuSolver:
    """OR-Tools MILP solver for menu price and assortment optimization.

    Usage:
        solver = MenuSolver(items, constraints)
        recommendation = solver.optimize()
    """

    def __init__(
        self,
        items: list[MenuItem],
        constraints: MenuConstraints | None = None,
        objective: OptimizationObjective | None = None,
    ):
        self._items = items
        self._constraints = constraints or MenuConstraints()
        self._objective = objective or OptimizationObjective()
        self._solver = None
        self._price_vars = {}   # item_id -> price variable
        self._keep_vars = {}    # item_id -> binary keep variable

    def optimize(self) -> MenuRecommendation:
        """Run the MILP optimization and return recommendations.

        Returns a MenuRecommendation with suggested price changes,
        items to remove, and projected profit.
        """
        if not self._items:
            return MenuRecommendation(solver_status="infeasible")

        try:
            from ortools.sat.python import cp_model
        except ImportError:
            raise SolverError("ortools is not installed")

        model = cp_model.CpModel()
        self._solver = cp_model.CpSolver()
        self._solver.parameters.max_time_in_seconds = 10  # Safety limit (T-05-03)

        # ── Decision variables ──
        for item in self._items:
            # Binary: keep (1) or remove (0) this item
            self._keep_vars[item.id] = model.NewBoolVar(f"keep_{item.id}")

            # Price change delta (integer cents, positive = increase, negative = decrease)
            # Bounded by safety rules (-30% to +50% of current price)
            max_dec = int(item.current_price_cents * 0.30)
            max_inc = int(item.current_price_cents * 0.50)
            delta_domain = cp_model.Domain(-max_dec, max_inc)
            self._price_vars[item.id] = model.NewIntVarFromDomain(
                delta_domain, f"delta_{item.id}"
            )

        # ── Constraints ──

        # 1. Price bounds (from MenuConstraints)
        for item in self._items:
            new_price = item.current_price_cents + self._price_vars[item.id]
            model.Add(new_price >= self._constraints.min_price_cents).OnlyEnforceIf(
                self._keep_vars[item.id]
            )
            model.Add(new_price <= self._constraints.max_price_cents).OnlyEnforceIf(
                self._keep_vars[item.id]
            )

        # 2. Margin floor (price - cost >= min_margin_pct * cost)
        for item in self._items:
            new_price = item.current_price_cents + self._price_vars[item.id]
            min_margin_cents = int(self._constraints.min_margin_pct * item.cost_cents)
            model.Add(new_price >= item.cost_cents + min_margin_cents).OnlyEnforceIf(
                self._keep_vars[item.id]
            )

        # 3. Category min/max
        categories = set(i.category for i in self._items)
        for cat in categories:
            cat_vars = [self._keep_vars[i.id] for i in self._items if i.category == cat]
            if cat_vars:
                model.Add(sum(cat_vars) >= self._constraints.min_items_per_category)
                model.Add(sum(cat_vars) <= self._constraints.max_items_per_category)

        # 4. Total menu size cap
        model.Add(sum(self._keep_vars.values()) <= self._constraints.max_total_items)

        # ── Objective: maximize weighted score ──
        obj_terms = []

        # Profit contribution (conditional on keep)
        for item in self._items:
            new_price = item.current_price_cents + self._price_vars[item.id]
            # Variable: profit contribution if kept, 0 if removed
            max_profit = item.current_price_cents + int(item.current_price_cents * 0.50) - item.cost_cents
            profit_var = model.NewIntVar(0, max(max_profit, 1), f"profit_{item.id}")
            model.Add(profit_var == new_price - item.cost_cents).OnlyEnforceIf(self._keep_vars[item.id])
            model.Add(profit_var == 0).OnlyEnforceIf(self._keep_vars[item.id].Not())
            weight = int(self._objective.profit_weight * 100)
            obj_terms.append(weight * profit_var)

        # Variety bonus: prefer keeping items in diverse categories
        for item in self._items:
            variety_bonus = int(self._objective.variety_weight * 100)
            # Conditional bonus: variety_bonus if kept, 0 if removed
            bonus_var = model.NewIntVar(0, variety_bonus, f"variety_{item.id}")
            model.Add(bonus_var == variety_bonus).OnlyEnforceIf(self._keep_vars[item.id])
            model.Add(bonus_var == 0).OnlyEnforceIf(self._keep_vars[item.id].Not())
            obj_terms.append(bonus_var)

        # Price stability: penalize large changes (absolute delta)
        for item in self._items:
            penalty = int(self._objective.price_stability_weight * 100)
            max_abs = int(item.current_price_cents * 0.5)
            abs_change = model.NewIntVar(0, max(max_abs, 1), f"abs_{item.id}")
            model.AddAbsEquality(abs_change, self._price_vars[item.id])
            obj_terms.append(-penalty * abs_change)

        model.Maximize(sum(obj_terms))

        # ── Solve ──
        status = self._solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return self._build_recommendation(cp_model, status)
        else:
            return MenuRecommendation(
                solver_status="infeasible" if status == cp_model.INFEASIBLE else "error"
            )

    def _build_recommendation(self, cp_model, status: int) -> MenuRecommendation:
        """Build recommendation from solver solution."""
        changes = []
        items_to_remove = []
        projected_profit = 0
        current_profit = 0

        for item in self._items:
            keep = self._solver.Value(self._keep_vars[item.id])
            delta = self._solver.Value(self._price_vars[item.id])

            current_margin = item.current_price_cents - item.cost_cents
            current_profit += current_margin * int(item.avg_daily_orders)

            if keep:
                new_price = item.current_price_cents + delta
                new_margin = new_price - item.cost_cents
                projected_profit += new_margin * int(item.avg_daily_orders)

                if delta != 0:
                    changes.append(PriceChange(
                        item_id=item.id,
                        item_name=item.name,
                        old_price_cents=item.current_price_cents,
                        new_price_cents=new_price,
                        change_pct=(delta / item.current_price_cents) if item.current_price_cents > 0 else 0,
                        reason="Price optimization via MILP solver",
                    ))
            else:
                items_to_remove.append(item.id)

        status_str = "optimal" if status == cp_model.OPTIMAL else "feasible"

        return MenuRecommendation(
            changes=changes,
            items_to_remove=items_to_remove,
            projected_profit_cents=projected_profit,
            current_profit_cents=current_profit,
            safety_checks_passed=False,  # Must be validated by safety module
            solver_status=status_str,
            optimization_score=min(100, int(
                (projected_profit / max(current_profit, 1)) * 50 + 50
            )),
        )

    @property
    def solve_time_seconds(self) -> float:
        """Return the solver's wall time."""
        if self._solver:
            return self._solver.WallTime()
        return 0.0
