"""Unit tests for ccam_mcf — compiler and executor."""
import pytest

from ccam_mcf import compile_microflow, BytecodeExecutor, MicroflowContext
from ccam_mcf.models import Bytecode, Instruction, Opcode
from ccam_mcf.exceptions import CompileError, ExecError


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def simple_microflow_yaml():
    return """
name: test_flow
version: 1
triggers:
  - event: order.created
steps:
  - id: step1
    type: action
    action: test.greet
    params:
      message: hello
"""


@pytest.fixture
def condition_microflow_yaml():
    return """
name: condition_test
version: 1
steps:
  - id: check
    type: condition
    if:
      source: payload.total
      operator: gt
      value: 0
    then: approve
    else: reject
  - id: approve
    type: action
    action: order.approve
    params: {}
  - id: reject
    type: action
    action: order.reject
    params:
      reason: invalid
"""


# ── Compiler Tests ─────────────────────────────────────────────────────────


class TestCompiler:
    def test_compile_action_only(self, simple_microflow_yaml):
        bc = compile_microflow(simple_microflow_yaml)
        assert len(bc.instructions) >= 1
        assert bc.step_ids[0] == "step1"
        assert bc.instructions[-1].opcode == Opcode.RETURN

    def test_compile_condition(self, condition_microflow_yaml):
        bc = compile_microflow(condition_microflow_yaml)
        assert len(bc.instructions) >= 3
        assert bc.instructions[-1].opcode == Opcode.RETURN

    def test_compile_empty_yaml(self):
        with pytest.raises(CompileError):
            compile_microflow("")

    def test_compile_invalid_step_type(self):
        with pytest.raises(CompileError, match="unknown_step"):
            compile_microflow("""
name: bad
version: 1
steps:
  - id: x
    type: unknown_step
""")

    def test_compile_bad_operator(self):
        with pytest.raises(CompileError, match="operator"):
            compile_microflow("""
name: bad
version: 1
steps:
  - id: x
    type: condition
    if:
      source: payload.x
      operator: bad_op
      value: 1
    then: x
    else: x
""")

    def test_compile_unresolved_step_ref(self):
        with pytest.raises(CompileError, match="nonexistent"):
            compile_microflow("""
name: bad
version: 1
steps:
  - id: a
    type: condition
    if:
      source: payload.x
      operator: eq
      value: 1
    then: nonexistent
    else: a
""")

    def test_compile_cycle_detection(self):
        with pytest.raises(CompileError, match="[Cc]ycle"):
            compile_microflow("""
name: cycle
version: 1
steps:
  - id: a
    type: condition
    if:
      source: payload.x
      operator: eq
      value: 1
    then: b
    else: b
  - id: b
    type: condition
    if:
      source: payload.x
      operator: eq
      value: 1
    then: a
    else: a
""")


# ── Executor Tests ─────────────────────────────────────────────────────────


class TestExecutor:
    def test_execute_action_only(self):
        microflow = """
name: test
version: 1
steps:
  - id: greet
    type: action
    action: greet
    params:
      name: world
"""
        bc = compile_microflow(microflow)
        results = []
        ctx = MicroflowContext(actions={
            "greet": lambda p: results.append(p) or "Hello, %s!" % p["name"],
        })
        output = BytecodeExecutor(bc, ctx).run()
        assert results == [{"name": "world"}]
        assert output == "Hello, world!"

    def test_execute_condition_true(self, condition_microflow_yaml):
        bc = compile_microflow(condition_microflow_yaml)
        executed = []
        ctx = MicroflowContext(
            payload={"total": 100},
            actions={
                "order.approve": lambda p: executed.append("approve") or "approved",
                "order.reject": lambda p: executed.append("reject") or "rejected",
            },
        )
        output = BytecodeExecutor(bc, ctx).run()
        assert executed == ["approve"], "Expected approve path, got %s" % executed
        assert output == "approved"

    def test_execute_condition_false(self, condition_microflow_yaml):
        bc = compile_microflow(condition_microflow_yaml)
        executed = []
        ctx = MicroflowContext(
            payload={"total": -5},
            actions={
                "order.approve": lambda p: executed.append("approve") or "approved",
                "order.reject": lambda p: executed.append("reject") or "rejected",
            },
        )
        output = BytecodeExecutor(bc, ctx).run()
        assert executed == ["reject"], "Expected reject path, got %s" % executed
        assert output == "rejected"

    def test_execute_switch(self):
        microflow = """
name: route
version: 1
steps:
  - id: route_step
    type: switch
    switch:
      source: payload.type
      cases:
        A: handle_a
        B: handle_b
      default: handle_default
  - id: handle_a
    type: action
    action: handler
    params: {case: A}
  - id: handle_b
    type: action
    action: handler
    params: {case: B}
  - id: handle_default
    type: action
    action: handler
    params: {case: default}
"""
        bc = compile_microflow(microflow)
        results = []
        ctx = MicroflowContext(
            payload={"type": "B"},
            actions={"handler": lambda p: results.append(p) or "handled_%s" % p["case"]},
        )
        output = BytecodeExecutor(bc, ctx).run()
        assert results == [{"case": "B"}]
        assert output == "handled_B"

    def test_execute_determinism(self):
        """Same input -> same output across multiple runs."""
        microflow = """
name: det
version: 1
steps:
  - id: check
    type: condition
    if:
      source: payload.value
      operator: gte
      value: 10
    then: big
    else: small
  - id: big
    type: action
    action: classify
    params: {size: big}
  - id: small
    type: action
    action: classify
    params: {size: small}
"""
        bc = compile_microflow(microflow)
        ctx = MicroflowContext(
            payload={"value": 15},
            actions={"classify": lambda p: p["size"]},
        )
        results = [BytecodeExecutor(bc, ctx).run() for _ in range(5)]
        assert all(r == "big" for r in results), "Determinism violated: %s" % results

    def test_execute_unknown_action(self):
        bc = compile_microflow("""
name: bad
version: 1
steps:
  - id: x
    type: action
    action: nonexistent
    params: {}
""")
        ctx = MicroflowContext()
        with pytest.raises(ExecError, match="nonexistent"):
            BytecodeExecutor(bc, ctx).run()

    def test_execute_field_not_found(self):
        microflow = """
name: bad
version: 1
steps:
  - id: check
    type: condition
    if:
      source: payload.missing
      operator: eq
      value: 1
    then: done
    else: done
  - id: done
    type: action
    action: noop
    params: {}
"""
        bc = compile_microflow(microflow)
        ctx = MicroflowContext(payload={})
        with pytest.raises(ExecError, match="missing"):
            BytecodeExecutor(bc, ctx).run()

    def test_empty_steps_returns_none(self):
        bc = Bytecode(instructions=[], step_ids=[], constants={})
        output = BytecodeExecutor(bc, MicroflowContext()).run()
        assert output is None
