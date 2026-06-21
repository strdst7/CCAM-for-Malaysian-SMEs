class CompileError(Exception):
    """Raised when microflow YAML compilation fails due to structural invalidity."""


class ExecError(Exception):
    """Raised during bytecode execution (e.g., unknown action, field access error)."""
