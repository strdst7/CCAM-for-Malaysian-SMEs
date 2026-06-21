"""CCAM Microflow — deterministic DSL interpreter for microflow orchestration."""
__version__ = "0.1.0"
from ccam_mcf.compiler import compile_microflow
from ccam_mcf.executor import BytecodeExecutor, MicroflowContext
from ccam_mcf.models import MicroflowDef, Trigger, ConditionStep, ActionStep, SwitchStep, Bytecode, Instruction, Opcode, CompileError

__all__ = [
    "compile_microflow",
    "BytecodeExecutor", "MicroflowContext",
    "MicroflowDef", "Trigger", "ConditionStep", "ActionStep", "SwitchStep",
    "Bytecode", "Instruction", "Opcode", "CompileError",
]
