"""Deterministic bytecode executor for compiled microflows."""
from typing import Any, Callable

from ccam_mcf.models import Bytecode, Instruction, Opcode
from ccam_mcf.exceptions import ExecError


class MicroflowContext:
    """Execution context holding input payload, memory, and action registry.

    Attributes:
        payload: Input data for the microflow (e.g., event payload).
        memory: Runtime variable store for step output sharing.
        actions: Named action handlers registered externally.
    """

    def __init__(
        self,
        payload: dict | None = None,
        memory: dict | None = None,
        actions: dict[str, Callable] | None = None,
    ):
        self.payload = payload or {}
        self.memory = memory or {}
        self.actions = actions or {}


class BytecodeExecutor:
    """Deterministic bytecode executor.

    Executes Bytecode instructions sequentially, maintaining determinism
    (same bytecode + same context -> same output across all runs).

    The executor uses a simple stack machine model:
    - LOAD/LOAD_CONST push values onto the value stack.
    - COMPARE pops two values, pushes boolean result.
    - JUMP_IF_FALSE conditionally jumps based on top-of-stack.
    - CALL pops params, invokes registered action, pushes result.
    - RETURN pops final result and returns it.
    """

    def __init__(self, bytecode: Bytecode, context: MicroflowContext):
        self._bytecode = bytecode
        self._context = context
        self._ip = 0                 # instruction pointer
        self._stack: list[Any] = []  # value stack

    def run(self, seed: int | None = None) -> Any:
        """Execute bytecode deterministically.

        Args:
            seed: Optional RNG seed for deterministic randomness in actions.
                  Not used internally (executor is pure) but passed through
                  to action handlers.

        Returns:
            Value returned by the final RETURN instruction.
            If no RETURN is reached, returns None.

        Raises:
            ExecError: On action not found, field access failure, etc.
        """
        self._ip = 0
        self._stack.clear()

        while self._ip < len(self._bytecode.instructions):
            instr = self._bytecode.instructions[self._ip]

            if instr.opcode == Opcode.LOAD:
                self._execute_load(instr)
                self._ip += 1
            elif instr.opcode == Opcode.LOAD_CONST:
                self._execute_load_const(instr)
                self._ip += 1
            elif instr.opcode == Opcode.COMPARE:
                self._execute_compare(instr)
                self._ip += 1
            elif instr.opcode == Opcode.JUMP_IF_FALSE:
                jumped = self._execute_jump_if_false(instr)
                if not jumped:
                    self._ip += 1
            elif instr.opcode == Opcode.JUMP:
                self._execute_jump(instr)
                # IP is modified by the jump; do NOT increment
            elif instr.opcode == Opcode.CALL:
                self._execute_call(instr)
                self._ip += 1
            elif instr.opcode == Opcode.RETURN:
                return self._execute_return()
            else:
                raise ExecError(f"Unknown opcode: {instr.opcode}")

        return None  # No RETURN reached

    # ---- Source resolution --------------------------------------------------

    def _resolve_source(self, source: str) -> Any:
        """Resolve dot-notation path against context objects.

        Supports:
        - ``payload.field.nested`` — walks ``context.payload``
        - ``memory.key`` — walks ``context.memory``
        """
        if not source:
            raise ExecError("Empty source path")

        parts = source.split(".")
        root_name = parts[0]

        if root_name == "payload":
            obj = self._context.payload
        elif root_name == "memory":
            obj = self._context.memory
        else:
            raise ExecError(
                "Unknown source root '%s'. Use 'payload.' or 'memory.'" % root_name
            )

        for part in parts[1:]:
            if isinstance(obj, dict):
                if part not in obj:
                    raise ExecError(
                        "Field '%s' not found in %s path '%s'" % (part, root_name, source)
                    )
                obj = obj[part]
            else:
                raise ExecError(
                    "Cannot navigate into non-dict value at '%s' in path '%s'" % (part, source)
                )

        return obj

    # ---- Instruction handlers -----------------------------------------------

    def _execute_load(self, instr: Instruction) -> None:
        source = instr.args.get("source", "")
        value = self._resolve_source(source)
        self._stack.append(value)

    def _execute_load_const(self, instr: Instruction) -> None:
        value = instr.args.get("value")
        self._stack.append(value)

    def _execute_compare(self, instr: Instruction) -> None:
        if len(self._stack) < 2:
            raise ExecError("COMPARE requires 2 values on stack")
        b = self._stack.pop()
        a = self._stack.pop()
        operator = instr.args.get("operator", "eq")

        compare_ops = {
            "eq": a == b,
            "neq": a != b,
            "gt": a > b,
            "gte": a >= b,
            "lt": a < b,
            "lte": a <= b,
        }
        if operator not in compare_ops:
            raise ExecError("Unknown operator '%s'" % operator)
        self._stack.append(compare_ops[operator])

    def _execute_jump_if_false(self, instr: Instruction) -> bool:
        """Execute conditional jump. Returns True if jump was taken."""
        if not self._stack:
            raise ExecError("JUMP_IF_FALSE requires a value on stack")
        condition = self._stack.pop()
        if not condition:
            if instr.target is not None:
                self._ip = instr.target
                return True
            else:
                raise ExecError("JUMP_IF_FALSE missing target")
        return False

    def _execute_jump(self, instr: Instruction) -> None:
        if instr.target is not None:
            self._ip = instr.target
        else:
            raise ExecError("JUMP missing target")

    def _execute_call(self, instr: Instruction) -> None:
        action_name = instr.args.get("action", "")
        if not action_name:
            raise ExecError("CALL missing action name")

        handler = self._context.actions.get(action_name)
        if handler is None:
            raise ExecError(
                "Unknown action '%s'. No handler registered in context.actions." % action_name
            )

        params = instr.args.get("params", {})
        try:
            result = handler(params)
            self._stack.append(result)
        except Exception as e:
            raise ExecError("Action '%s' failed: %s" % (action_name, e))

    def _execute_return(self) -> Any:
        if self._stack:
            return self._stack.pop()
        return None
