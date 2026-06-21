---
phase: 04-microflows-worker-jobs
plan: 01
subsystem: microflow-dsl
tags: [yaml, bytecode, compiler, executor, stack-vm, pyyaml, pytest]

requires:
  - phase: 03-simulator-backend-integration
    provides: Dataclass-based model patterns, seeded determinism convention

provides:
  - YAML-to-bytecode compiler (compile_microflow)
  - Deterministic stack-based bytecode executor (BytecodeExecutor)
  - MicroflowContext with payload/memory/action registry
  - Bytecode instruction set (7 opcodes)
  - YAML data models (MicroflowDef, ConditionStep, ActionStep, SwitchStep)

affects:
  - 04-microflows-worker-jobs phase (Plan 02 — ARQ worker jobs)

tech-stack:
  added:
    - ccam-mcf package (hatchling, pyyaml)
    - pytest for unit tests
  patterns:
    - Stack-based VM for deterministic execution
    - DAG linearization via DFS with jump target fixup
    - DFS coloring for cycle detection in step DAG
    - Action registry pattern (functions injected, not imported)

key-files:
  created:
    - mcf/pyproject.toml
    - mcf/src/ccam_mcf/__init__.py
    - mcf/src/ccam_mcf/models.py
    - mcf/src/ccam_mcf/compiler.py
    - mcf/src/ccam_mcf/executor.py
    - mcf/src/ccam_mcf/exceptions.py
    - mcf/tests/test_mcf_unit.py
  modified: []

key-decisions:
  - "Stack-based VM (not register-based) — simpler to implement and test, sufficient for microflow DSL"
  - "Two-pass compilation: first DFS to detect cycles, then DFS for instruction emission with jump fixup"
  - "Switch step emits LOAD per case (not once) — COMPARE opcode consumes both stack values"
  - "Action handlers injected via dict (not imported) — keeps library standalone and testable"

patterns-established:
  - "Compiler: validate → resolve refs → detect cycles → linearize DAG → emit instructions"
  - "Executor: instruction pointer increment only after non-jump instructions"
  - "Error handling: CompileError for compilation, ExecError for runtime"

requirements-completed: [MCF-01]
duration: 18min
completed: 2026-06-21
---

# Phase 4 Plan 01: Microflow DSL Compiler & Bytecode Executor Library

**Standalone ccam-mcf library with YAML-to-bytecode compiler, deterministic stack-based VM executor, and comprehensive test suite — forms the core execution primitive for all microflow orchestration**

## Performance

- **Duration:** 18 min
- **Started:** 2026-06-21T12:29:30Z
- **Completed:** 2026-06-21T12:47:30Z
- **Tasks:** 3
- **Files created:** 7
- **Tests:** 15 (all passing)

## Accomplishments

- **Package scaffold:** `mcf/` project with pyyaml dependency, hatchling build system, and clean public API via `__init__.py`
- **YAML data models:** `MicroflowDef`, `ConditionStep`, `ActionStep`, `SwitchStep`, `Trigger`, `Bytecode`, `Instruction`, `Opcode` enum — all `@dataclass` types
- **Compiler:** `compile_microflow(yaml_str) -> Bytecode` with structural validation (top-level fields, per-step type checks, operator validation), cross-reference resolution, DFS cycle detection, and DAG-to-bytecode linearization with jump target fixup
- **Executor:** `BytecodeExecutor.run() -> Any` with 7-opcode stack-based VM supporting LOAD/LOAD_CONST/COMPARE/JUMP_IF_FALSE/JUMP/CALL/RETURN, context source path resolution (`payload.*`, `memory.*`), and action registry pattern
- **Comprehensive test suite:** 15 tests covering compilation validation (empty YAML, bad step types, bad operators, unknown refs, cycles), execution (action dispatch, condition true/false routing, switch routing, determinism over 5 runs), and error handling (unknown action, missing field, empty bytecode)

## Task Commits

Each task was committed atomically:

1. **Task 1: Microflow data models, bytecode format, and package scaffold** — `faaf08f` (feat)
2. **Task 2: YAML-to-bytecode compiler with structural validation** — `77b4df4` (feat)
3. **Task 3: Deterministic bytecode executor and comprehensive test suite** — `0a641d0` (feat)

## Files Created/Modified

- `mcf/pyproject.toml` — Standalone ccam-mcf package configuration with pyyaml dependency
- `mcf/src/ccam_mcf/__init__.py` — Public API exports (compile_microflow, BytecodeExecutor, MicroflowContext, all model types)
- `mcf/src/ccam_mcf/models.py` — Microflow data models and bytecode instruction format (7 opcodes, 4 step types, Bytecode/Instruction)
- `mcf/src/ccam_mcf/compiler.py` — YAML-to-bytecode compiler with structural validation and DAG linearization
- `mcf/src/ccam_mcf/executor.py` — Deterministic stack-based bytecode executor with action registry
- `mcf/src/ccam_mcf/exceptions.py` — CompileError and ExecError exception classes
- `mcf/tests/test_mcf_unit.py` — 15-unit test suite covering compiler and executor

## YAML Microflow Format Specification

```yaml
name: microflow_name          # required, non-empty string
version: 1                    # required, positive integer
triggers:                     # optional
  - event: order.created      # non-empty string
steps:                        # required, non-empty list
  - id: step_id               # unique within microflow
    type: condition           # "condition" | "action" | "switch"
    if:                       # required for condition
      source: payload.field   # dot-path into context
      operator: gt            # eq, neq, gt, gte, lt, lte
      value: 0                # literal comparison value
    then: target_step         # step_id for true branch
    else: target_step         # step_id for false branch
  - id: step_id
    type: action
    action: order.approve     # action name string
    params: {}                # dict of parameters
  - id: step_id
    type: switch
    switch:
      source: payload.type    # dot-path into context
      cases:                  # value -> step_id mapping
        A: handle_a
        B: handle_b
      default: handle_default # step_id when no case matches
```

## Bytecode Instruction Set

| Opcode | Mnemonic | Args | Behavior |
|--------|----------|------|----------|
| LOAD | load | `source` (dot-path) | Push context value onto stack |
| LOAD_CONST | ldc | `value` (literal) | Push constant onto stack |
| COMPARE | cmp | `operator` (eq/neq/gt/gte/lt/lte) | Pop b, pop a, push (a op b) |
| JUMP_IF_FALSE | jif | `target` (instruction index) | Pop cond, jump if falsy |
| JUMP | jmp | `target` (instruction index) | Unconditional jump |
| CALL | call | `action`, `params` | Invoke registered handler, push result |
| RETURN | ret | — | Pop result and return from microflow |

## Compilation Algorithm Summary

1. **Parse:** `yaml.safe_load(yaml_str)` — reject non-dict/empty
2. **Validate top-level:** name (non-empty string), version (positive int), steps (non-empty list), triggers (optional list with event)
3. **Validate per-step:** type-specific field checks (if.source/operator/value/then/else for conditions, action/params for actions, switch.source/cases/default for switches), cross-reference resolution (all step refs must exist)
4. **Cycle detection:** DFS coloring (VISITING/VISITED) — raise CompileError on back-edge
5. **DAG linearization:** DFS from entry point, emitting instructions for each step type, with JUMP_IF_FALSE for condition/switch branching and JUMP for case/default targets. Jump targets resolved in fixup pass.

## Decisions Made

- **Stack-based VM over register-based:** Simpler implementation, natural fit for deeply-nested conditions and switches. 7 opcodes is minimal but sufficient.
- **Two-pass linearization:** First DFS for cycle detection, second DFS for instruction emission with deferred jump target fixup (collect fixup tuples: instruction_idx -> target_step_id, resolve after all instructions emitted).
- **Switch emits LOAD per case:** COMPARE consumes both stack operands. Loading source once and comparing against multiple values doesn't work without DUP opcode. Each case gets its own LOAD to keep VM minimal.
- **Action registry (not imported handlers):** Functions injected via `MicroflowContext.actions = {}`, keeping the library standalone, testable, and backend-agnostic.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Executor increments IP after jump instructions**
- **Found during:** task 3 (test_execute_condition_false failing)
- **Issue:** The `run()` loop unconditionally incremented `self._ip` after every instruction, including JUMP/JUMP_IF_FALSE. When a jump modified the IP, the post-instruction `+= 1` would skip past the target.
- **Fix:** Changed run loop to only increment IP after non-jump instructions. JUMP/JUMP_IF_FALSE modify IP internally without subsequent increment. Added boolean return from `_execute_jump_if_false` to signal whether a jump was taken.
- **Files modified:** `mcf/src/ccam_mcf/executor.py`
- **Verification:** test_execute_condition_true/false, test_execute_switch, test_execute_determinism all pass
- **Committed in:** `0a641d0` (task 3 commit)

**2. [Rule 1 - Bug] Switch step did not emit case target code blocks**
- **Found during:** task 3 (test_execute_switch failing with CompileError about unreachable steps)
- **Issue:** The switch step's instruction emission only produced the routing table (LOAD + LOAD_CONST + COMPARE + JUMP_IF_FALSE + JUMP per case, plus default JUMP) but never emitted the actual case target step instructions. The JUMP fixups pointed to step blocks that were never emitted.
- **Fix:** Added `_emit_step()` calls for each case target and the default step after the switch routing, with RETURN after each.
- **Files modified:** `mcf/src/ccam_mcf/compiler.py`
- **Verification:** test_execute_switch passes
- **Committed in:** `0a641d0` (task 3 commit)

**3. [Rule 1 - Bug] Switch single LOAD consumed by COMPARE for first case**
- **Found during:** task 3 (test_execute_switch failing with ExecError "COMPARE requires 2 values on stack")
- **Issue:** The plan's spec said `LOAD source, then for each case: LOAD_CONST case_value, COMPARE eq`. But COMPARE pops both operands, consuming the source value on first comparison. Subsequent case checks have no source value to compare.
- **Fix:** Changed switch to emit LOAD source for each case individually (inside the per-case loop), so each COMPARE gets its own source value.
- **Files modified:** `mcf/src/ccam_mcf/compiler.py`
- **Verification:** test_execute_switch passes
- **Committed in:** `0a641d0` (task 3 commit)

**4. [Rule 3 - Blocking] Forward imports in __init__.py require stubs**
- **Found during:** task 1 (package verification failing)
- **Issue:** The `__init__.py` eagerly imports `compile_microflow` from `compiler.py` and `BytecodeExecutor/MicroflowContext` from `executor.py`, which don't exist at task 1.
- **Fix:** Created stub files for compiler.py and executor.py with minimal implementations to satisfy imports, then replaced with full implementations in tasks 2 and 3.
- **Files modified:** `mcf/src/ccam_mcf/compiler.py`, `mcf/src/ccam_mcf/executor.py` (initially as stubs)
- **Verification:** Package imports successfully after stubs, full imports after task 2/3
- **Committed in:** `faaf08f` (task 1 commit)

---

**Total deviations:** 4 auto-fixed (3 bugs, 1 blocking)
**Impact on plan:** All auto-fixes necessary for correctness. No scope creep — each fix directly enabled failing tests to pass.

## Threat Flags

None — no new threat surface introduced beyond what the plan's `<threat_model>` describes.

## Issues Encountered

- **Cycle detection vs. field-not-found test:** The plan's test for field-not-found used a self-looping condition (then/else both pointing to itself). This correctly triggers cycle detection as a CompileError before execution. Fixed test to use non-cyclic flow.
- **Stack machine semantics for switch:** COMPARE consumes both stack operands, making the plan's single-LOAD-per-switch approach infeasible without a DUP opcode. Chose to emit LOAD per case rather than adding DUP (minimalist VM).

## Test Results

```
============================= 15 passed in 0.04s ==============================
```

| Test Group | Tests | Status |
|------------|-------|--------|
| TestCompiler | 7 | ✅ All passed |
| TestExecutor | 8 | ✅ All passed |
| **Total** | **15** | **✅ All passed** |

## External Import Verification

```
python -c "from ccam_mcf import compile_microflow, BytecodeExecutor; print('OK')"
→ OK
```

## Next Phase Readiness

- **ccam-mcf library is ready** for consumption by Plan 02 (ARQ worker jobs)
- Key interfaces: `compile_microflow(yaml_str) -> Bytecode`, `BytecodeExecutor(bytecode, context).run() -> Any`
- Pattern for registering actions: `MicroflowContext(actions={"name": handler_fn})`
- Determinism proven: same bytecode + same context = same output across 5 runs

## Self-Check: PASSED

- [x] All 7 files exist
- [x] All 3 commits exist (faaf08f, 77b4df4, 0a641d0)
- [x] All 15 tests pass
- [x] External import works

---
*Phase: 04-microflows-worker-jobs*
*Completed: 2026-06-21*
