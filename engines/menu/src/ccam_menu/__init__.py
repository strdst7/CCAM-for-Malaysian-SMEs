"""CCAM Menu Engineering Engine — OR-Tools MILP solver with safety-constrained menu optimization."""
__version__ = "0.1.0"

from ccam_menu.engine import MenuEngine, optimize_menu
from ccam_menu.models import (
    MenuItem, MenuConstraints, OptimizationObjective,
    PriceChange, MenuRecommendation,
)
from ccam_menu.safety import MenuSafetyConstraints
from ccam_menu.solver import MenuSolver
from ccam_menu.exceptions import MenuError, SafetyViolationError, SolverError, ValidationError

__all__ = [
    "MenuEngine", "optimize_menu",
    "MenuItem", "MenuConstraints", "OptimizationObjective",
    "PriceChange", "MenuRecommendation",
    "MenuSafetyConstraints",
    "MenuSolver",
    "MenuError", "SafetyViolationError", "SolverError", "ValidationError",
]
