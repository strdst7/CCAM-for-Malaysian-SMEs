---
status: complete
phase: 01-simulator-core
source: 01-01-SUMMARY.md, 01-02-SUMMARY.md, 01-03-SUMMARY.md, 01-04-SUMMARY.md
started: 2026-06-21T08:01:31Z
updated: 2026-06-21T08:06:00Z
---

## Current Test

[testing complete]

## Tests

### 1. CLI simulate command
expected: Run `ccam-sim simulate tests/fixtures/simple_restaurant.yaml --seed 42`. Output should be structured JSON with all 5 KPIs as top-level keys.
result: pass

### 2. Deterministic replay
expected: Run the same command again with seed 42. Output must be byte-identical to the first run.
result: pass

### 3. Different seed produces different results
expected: Run with `--seed 1`. KPIs should differ from seed 42 run.
result: pass

### 4. Safety — negative stock rejection
expected: Run `ccam-sim simulate tests/fixtures/negative_stock_scenario.yaml --seed 42`. Command should exit with error and a clear message saying stock cannot be negative.
result: pass

### 5. Safety — zero staff rejection
expected: Run `ccam-sim simulate tests/fixtures/overload_scenario.yaml --seed 42`. Command should exit with error about staff_count >= 1.
result: pass

### 6. Safety — max_steps=0 rejection
expected: Run `ccam-sim simulate tests/fixtures/infinite_loop_scenario.yaml --seed 42`. Command should exit with error about max_steps > 0.
result: pass

### 7. Human-readable summary output
expected: Run with `--output human`. Should display a box-drawing table with KPI labels and values.
result: pass

### 8. JSON output to file
expected: Run with `--output /tmp/test-output.json`. File should contain valid JSON with KPIs.
result: pass

### 9. Non-existent scenario file
expected: Run `ccam-sim simulate nonexistent.yaml`. Exit code 2 with file-not-found error.
result: pass

### 10. Quiet mode
expected: Run with `--quiet`. Only JSON output on stdout, no stderr messages.
result: pass

## Summary

total: 10
passed: 10
issues: 0
pending: 0
skipped: 0

## Gaps

