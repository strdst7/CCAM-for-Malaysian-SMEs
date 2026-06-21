"""Exceptions for the menu engineering engine."""

class MenuError(Exception):
    """Base exception for menu engine errors."""

class SafetyViolationError(MenuError):
    """Raised when optimization would violate a hard safety constraint."""

class SolverError(MenuError):
    """Raised when the MILP solver fails or infeasible."""

class ValidationError(MenuError):
    """Raised when input data fails validation."""
