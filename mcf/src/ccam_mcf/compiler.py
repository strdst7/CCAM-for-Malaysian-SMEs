"""Microflow YAML-to-bytecode compiler with structural validation."""
import yaml

from ccam_mcf.models import (
    Bytecode,
    ConditionStep,
    Instruction,
    Opcode,
    Trigger,
)
from ccam_mcf.exceptions import CompileError


def _validate_top_level(data: dict) -> tuple[str, int, list, list]:
    """Validate and return (name, version, steps_data, triggers_data)."""
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise CompileError("Field 'name' must be a non-empty string")

    version = data.get("version")
    if not isinstance(version, int) or version < 1:
        raise CompileError("Field 'version' must be a positive integer, got %r" % version)

    steps_data = data.get("steps", [])
    if not isinstance(steps_data, list) or not steps_data:
        raise CompileError("Field 'steps' must be a non-empty list")

    triggers_data = data.get("triggers", [])
    if triggers_data:
        if not isinstance(triggers_data, list):
            raise CompileError("Field 'triggers' must be a list")
        for i, t in enumerate(triggers_data):
            if not isinstance(t, dict):
                raise CompileError("Trigger at index %d: must be a mapping" % i)
            event = t.get("event")
            if not event or not isinstance(event, str):
                raise CompileError("Trigger at index %d: 'event' must be a non-empty string" % i)

    return name, version, steps_data, triggers_data


def _parse_triggers(triggers_data: list) -> list[Trigger]:
    """Parse trigger definitions."""
    return [Trigger(event=t["event"]) for t in triggers_data]


def _validate_condition(step_id: str, sd: dict) -> dict:
    """Validate a condition step and return normalized data."""
    if_data = sd.get("if")
    if not isinstance(if_data, dict):
        raise CompileError("Step '%s': 'if' must be a mapping" % step_id)

    source = if_data.get("source")
    if not isinstance(source, str) or not source:
        raise CompileError("Step '%s': 'if.source' must be a non-empty string" % step_id)

    operator = if_data.get("operator")
    valid_ops = {"eq", "neq", "gt", "gte", "lt", "lte"}
    if operator not in valid_ops:
        raise CompileError(
            "Step '%s': 'if.operator' must be one of %s, got '%s'" % (step_id, sorted(valid_ops), operator)
        )

    value = if_data.get("value")

    then_ref = sd.get("then")
    else_ref = sd.get("else")
    if not isinstance(then_ref, str) or not then_ref:
        raise CompileError("Step '%s': 'then' must be a non-empty string" % step_id)
    if not isinstance(else_ref, str) or not else_ref:
        raise CompileError("Step '%s': 'else' must be a non-empty string" % step_id)

    return {
        "type": "condition",
        "source": source,
        "operator": operator,
        "value": value,
        "then": then_ref,
        "else": else_ref,
    }


def _validate_action(step_id: str, sd: dict) -> dict:
    """Validate an action step and return normalized data."""
    action = sd.get("action")
    if not isinstance(action, str) or not action:
        raise CompileError("Step '%s': 'action' must be a non-empty string" % step_id)

    params = sd.get("params", {})
    if not isinstance(params, dict):
        raise CompileError("Step '%s': 'params' must be a mapping" % step_id)

    return {
        "type": "action",
        "action": action,
        "params": params,
    }


def _validate_switch(step_id: str, sd: dict) -> dict:
    """Validate a switch step and return normalized data."""
    switch_data = sd.get("switch")
    if not isinstance(switch_data, dict):
        raise CompileError("Step '%s': 'switch' must be a mapping" % step_id)

    source = switch_data.get("source")
    if not isinstance(source, str) or not source:
        raise CompileError("Step '%s': 'switch.source' must be a non-empty string" % step_id)

    cases = switch_data.get("cases", {})
    if not isinstance(cases, dict):
        raise CompileError("Step '%s': 'switch.cases' must be a mapping" % step_id)

    for case_key, case_val in cases.items():
        if not isinstance(case_val, str):
            raise CompileError(
                "Step '%s': case '%s' must map to a step id string, got %s" % (step_id, case_key, type(case_val).__name__)
            )

    default = switch_data.get("default")
    if not isinstance(default, str) or not default:
        raise CompileError("Step '%s': 'switch.default' must be a non-empty string" % step_id)

    return {
        "type": "switch",
        "source": source,
        "cases": cases,
        "default": default,
    }


def _validate_steps(steps_data: list) -> dict[str, dict]:
    """Parse and validate all steps, returning step_id -> normalized data dict."""
    step_dict: dict[str, dict] = {}
    seen_ids: set[str] = set()

    for i, sd in enumerate(steps_data):
        if not isinstance(sd, dict):
            raise CompileError("Step at index %d: must be a mapping" % i)

        step_id = sd.get("id")
        if not step_id or not isinstance(step_id, str):
            raise CompileError("Step at index %d: 'id' must be a non-empty string" % i)
        if step_id in seen_ids:
            raise CompileError("Duplicate step id '%s'" % step_id)
        seen_ids.add(step_id)

        step_type = sd.get("type")
        if step_type == "condition":
            step_dict[step_id] = _validate_condition(step_id, sd)
        elif step_type == "action":
            step_dict[step_id] = _validate_action(step_id, sd)
        elif step_type == "switch":
            step_dict[step_id] = _validate_switch(step_id, sd)
        else:
            raise CompileError(
                "Step '%s': unknown step type '%s'. Must be one of: condition, action, switch" % (step_id, step_type)
            )

    return step_dict


def _get_step_refs(sd: dict) -> list[str]:
    """Get all step references (outgoing edges) from a normalized step."""
    if sd["type"] == "condition":
        return [sd["then"], sd["else"]]
    elif sd["type"] == "switch":
        return list(sd["cases"].values()) + [sd["default"]]
    return []  # action steps have no outgoing refs


def _resolve_refs(step_dict: dict[str, dict]) -> None:
    """Validate that all step references exist. Raises CompileError if not."""
    for step_id, sd in step_dict.items():
        for ref in _get_step_refs(sd):
            if ref not in step_dict:
                raise CompileError("Step '%s' references unknown step '%s'" % (step_id, ref))


def _detect_cycles(step_dict: dict[str, dict], entry: str) -> None:
    """Detect cycles in the step DAG using DFS coloring."""
    VISITING, VISITED = 1, 2
    state: dict[str, int] = {}

    def _dfs(step_id: str, path: list[str]) -> None:
        state[step_id] = VISITING
        for ref in _get_step_refs(step_dict[step_id]):
            if ref not in state:
                _dfs(ref, path + [ref])
            elif state[ref] == VISITING:
                raise CompileError("Cycle detected involving step: '%s'" % ref)
        state[step_id] = VISITED

    _dfs(entry, [entry])


def _linearize(step_dict: dict[str, dict], entry: str) -> Bytecode:
    """Compile validated step dict into linear bytecode.

    Uses DFS traversal: condition steps emit their 'then' branch before
    their 'else' branch, with JUMP_IF_FALSE skipping to else on false.
    Each terminal path ends with a RETURN instruction.

    Jump targets are resolved in a fixup pass after all instructions
    are emitted.
    """
    instructions: list[Instruction] = []
    step_ids: list[str] = []
    constants: dict[str, object] = {}
    emitted: set[str] = set()
    step_start: dict[str, int] = {}  # step_id -> instruction index
    fixups: list[tuple[int, str]] = []  # (instruction_index, target_step_id)

    def _emit_step(step_id: str) -> None:
        """Emit instructions for a step and recursively for its branches."""
        if step_id in emitted:
            return
        emitted.add(step_id)
        step_start[step_id] = len(instructions)

        sd = step_dict[step_id]

        if sd["type"] == "action":
            instructions.append(Instruction(
                opcode=Opcode.CALL,
                args={"action": sd["action"], "params": sd["params"]},
            ))
            step_ids.append(step_id)
            instructions.append(Instruction(opcode=Opcode.RETURN))
            step_ids.append(step_id)

        elif sd["type"] == "condition":
            # LOAD source
            instructions.append(Instruction(opcode=Opcode.LOAD, args={"source": sd["source"]}))
            step_ids.append(step_id)
            # LOAD_CONST value
            instructions.append(Instruction(opcode=Opcode.LOAD_CONST, args={"value": sd["value"]}))
            step_ids.append(step_id)
            # COMPARE operator
            instructions.append(Instruction(opcode=Opcode.COMPARE, args={"operator": sd["operator"]}))
            step_ids.append(step_id)
            # JUMP_IF_FALSE -> else branch (placeholder target, fixed up later)
            jif_idx = len(instructions)
            instructions.append(Instruction(opcode=Opcode.JUMP_IF_FALSE))
            step_ids.append(step_id)
            fixups.append((jif_idx, sd["else"]))

            # Emit then branch (fall-through when condition is true)
            _emit_step(sd["then"])

            # RETURN after then branch
            instructions.append(Instruction(opcode=Opcode.RETURN))
            step_ids.append(step_id)

            # Emit else branch
            _emit_step(sd["else"])

            # RETURN after else branch
            instructions.append(Instruction(opcode=Opcode.RETURN))
            step_ids.append(step_id)

        elif sd["type"] == "switch":
            # LOAD source
            instructions.append(Instruction(opcode=Opcode.LOAD, args={"source": sd["source"]}))
            step_ids.append(step_id)

            case_items = list(sd["cases"].items())
            case_jif_indices: list[int] = []

            for case_value, case_target in case_items:
                # LOAD_CONST case_value, COMPARE eq
                instructions.append(Instruction(opcode=Opcode.LOAD_CONST, args={"value": case_value}))
                step_ids.append(step_id)
                instructions.append(Instruction(opcode=Opcode.COMPARE, args={"operator": "eq"}))
                step_ids.append(step_id)

                # JUMP_IF_FALSE -> next case check (placeholder)
                jif_idx = len(instructions)
                instructions.append(Instruction(opcode=Opcode.JUMP_IF_FALSE))
                step_ids.append(step_id)
                case_jif_indices.append(jif_idx)

                # JUMP -> case target step
                jump_idx = len(instructions)
                instructions.append(Instruction(opcode=Opcode.JUMP))
                step_ids.append(step_id)
                fixups.append((jump_idx, case_target))

            # After all cases: JUMP to default
            default_jump_idx = len(instructions)
            instructions.append(Instruction(opcode=Opcode.JUMP))
            step_ids.append(step_id)
            fixups.append((default_jump_idx, sd["default"]))

            # Fix up case JUMP_IF_FALSE targets (local forward refs)
            for i, jif_idx in enumerate(case_jif_indices):
                if i + 1 < len(case_items):
                    # Jump to the next case's LOAD_CONST (skip past JUMP)
                    instructions[jif_idx].target = jif_idx + 2
                else:
                    # Last case: jump to default JUMP
                    instructions[jif_idx].target = default_jump_idx

    _emit_step(entry)

    # Fix up all jump targets to final step positions
    for instr_idx, target_step_id in fixups:
        if target_step_id in step_start:
            instructions[instr_idx].target = step_start[target_step_id]
        else:
            raise CompileError(
                "Step '%s' is referenced but unreachable from entry point" % target_step_id
            )

    # Detect dead code: warn about steps never visited (not a hard error per plan)
    unreachable = [sid for sid in step_dict if sid not in emitted]
    if unreachable:
        pass  # Plan says warn but don't fail

    return Bytecode(instructions=instructions, step_ids=step_ids, constants=constants)


def compile_microflow(yaml_str: str) -> Bytecode:
    """Compile a YAML microflow definition into deterministic bytecode.

    Args:
        yaml_str: Raw YAML string defining the microflow.

    Returns:
        Bytecode with linearized instructions and resolved jump targets.

    Raises:
        CompileError: If the YAML is structurally invalid (bad types, unknown
                      step refs, cycles, missing required fields).
    """
    if not yaml_str or not yaml_str.strip():
        raise CompileError("YAML input is empty")

    data = yaml.safe_load(yaml_str)

    if data is None:
        raise CompileError("YAML input is empty (parsed to None)")
    if not isinstance(data, dict):
        raise CompileError("YAML root must be a mapping (dict), got %s" % type(data).__name__)
    if not data:
        raise CompileError("YAML definition is empty (no fields)")

    name, version, steps_data, triggers_data = _validate_top_level(data)
    triggers = _parse_triggers(triggers_data) if triggers_data else []

    step_dict = _validate_steps(steps_data)

    entry = steps_data[0]["id"]
    _resolve_refs(step_dict)
    _detect_cycles(step_dict, entry)

    bytecode = _linearize(step_dict, entry)
    return bytecode
