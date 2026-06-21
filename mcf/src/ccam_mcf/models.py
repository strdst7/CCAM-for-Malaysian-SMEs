"""Microflow data models and bytecode instruction format."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ccam_mcf.exceptions import CompileError


class Opcode(Enum):
    LOAD = "load"            # load value from context source path
    LOAD_CONST = "ldc"       # load a literal constant
    COMPARE = "cmp"          # compare top-of-stack values using operator
    JUMP_IF_FALSE = "jif"    # jump to target if false
    JUMP = "jmp"             # unconditional jump to target
    CALL = "call"            # call action by name with params
    RETURN = "ret"           # return from microflow with result


@dataclass
class Instruction:
    opcode: Opcode
    args: dict = field(default_factory=dict)
    target: int | None = None  # instruction index for jump instructions


@dataclass
class Bytecode:
    instructions: list[Instruction]
    step_ids: list[str]          # step id at each instruction index
    constants: dict[str, Any] = field(default_factory=dict)
    version: int = 1


@dataclass
class Trigger:
    event: str


@dataclass
class ConditionStep:
    id: str
    source: str              # dot-path into context payload, e.g. "payload.total"
    operator: str            # "eq", "neq", "gt", "gte", "lt", "lte"
    value: Any               # literal value to compare against
    then: str                # step_id to jump to if condition true
    else_: str               # step_id to jump to if condition false


@dataclass
class ActionStep:
    id: str
    action: str              # action name, e.g. "order.approve"
    params: dict             # parameters to pass to the action


@dataclass
class SwitchStep:
    id: str
    source: str
    cases: dict[str, str]    # value -> step_id
    default: str             # step_id when no case matches


@dataclass
class MicroflowDef:
    name: str
    version: int
    triggers: list[Trigger]
    steps: list[ConditionStep | ActionStep | SwitchStep]
    description: str = ""
