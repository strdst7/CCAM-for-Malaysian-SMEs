"""High-level menu engineering engine.

Orchestrates:
1. Input validation (safety checks)
2. MILP optimization (OR-Tools)
3. Post-optimization safety validation
4. Returns safe recommendations
"""
from ccam_menu.models import MenuItem, MenuConstraints, OptimizationObjective, MenuRecommendation
from ccam_menu.safety import MenuSafetyConstraints
from ccam_menu.solver import MenuSolver
from ccam_menu.exceptions import MenuError, SafetyViolationError


class MenuEngine:
    """Menu engineering engine with safety-gated optimization.

    Usage:
        engine = MenuEngine()
        recommendation = engine.optimize(items)
    """

    def __init__(
        self,
        constraints: MenuConstraints | None = None,
        objective: OptimizationObjective | None = None,
        safety: MenuSafetyConstraints | None = None,
    ):
        self._constraints = constraints or MenuConstraints()
        self._objective = objective or OptimizationObjective()
        self._safety = safety or MenuSafetyConstraints()

    def optimize(
        self,
        items: list[MenuItem],
        strict_safety: bool = True,
    ) -> MenuRecommendation:
        """Run safety-gated menu optimization.

        Args:
            items: Current menu items to optimize.
            strict_safety: If True, raises SafetyViolationError on violations.
                          If False, filters out unsafe changes.

        Returns:
            MenuRecommendation with price changes, removals, and projections.

        Raises:
            SafetyViolationError: If strict_safety=True and violations found.
            MenuError: On solver or input errors.
        """
        # ── Step 1: Validate input ──
        input_violations = self._safety.validate_input(items)
        if input_violations and strict_safety:
            raise SafetyViolationError("; ".join(input_violations))

        # ── Step 2: Run MILP solver ──
        solver = MenuSolver(items, self._constraints, self._objective)
        recommendation = solver.optimize()

        if recommendation.solver_status == "infeasible":
            return recommendation

        # ── Step 3: Post-optimization safety validation ──
        try:
            self._safety.validate_recommendation(items, recommendation)
            recommendation.safety_checks_passed = True
        except SafetyViolationError:
            if strict_safety:
                raise
            # Filter unsafe changes
            recommendation = self._safety.filter_unsafe_changes(items, recommendation)

        return recommendation


# Convenience function
def optimize_menu(
    items: list[MenuItem],
    constraints: MenuConstraints | None = None,
    objective: OptimizationObjective | None = None,
) -> MenuRecommendation:
    """Optimize a menu with safety-gated MILP solver."""
    engine = MenuEngine(constraints, objective)
    return engine.optimize(items)
