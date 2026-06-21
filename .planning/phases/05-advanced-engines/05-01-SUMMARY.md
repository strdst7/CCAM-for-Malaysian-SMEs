---
phase: 05-advanced-engines
plan: 01
type: execute
subsystem: engines
tags: [parser, menu-engineering, nlp, milp, ortools, onnx, safety]
dependency-graph:
  requires: []
  provides: [ENG-01, ENG-02]
  affects: [backend engine integration, future plans 05-02 through 05-04]
tech-stack:
  added:
    - ccam-parser: hatchling, onnxruntime, numpy, regex
    - ccam-menu: hatchling, ortools, numpy
  patterns:
    - Standalone Python packages under engines/ with src/ layout
    - Regex-first + ML fallback pipeline with confidence scoring
    - OR-Tools CP-SAT MILP with hard safety constraints
key-files:
  created:
    - engines/parser/pyproject.toml
    - engines/parser/src/ccam_parser/__init__.py
    - engines/parser/src/ccam_parser/models.py
    - engines/parser/src/ccam_parser/regex_engine.py
    - engines/parser/src/ccam_parser/ner_engine.py
    - engines/parser/src/ccam_parser/pipeline.py
    - engines/parser/src/ccam_parser/exceptions.py
    - engines/menu/pyproject.toml
    - engines/menu/src/ccam_menu/__init__.py
    - engines/menu/src/ccam_menu/models.py
    - engines/menu/src/ccam_menu/safety.py
    - engines/menu/src/ccam_menu/solver.py
    - engines/menu/src/ccam_menu/engine.py
    - engines/menu/src/ccam_menu/exceptions.py
  modified: []
decisions:
  - "Regex patterns use comma-separated item detection (not just before-price/EOS lookahead)"
  - "OR-Tools CP-SAT uses conditional profit variables (OnlyEnforceIf) instead of multiplication (unsupported)"
  - "Solver time limit set to 10 seconds per T-05-03 threat mitigation"
metrics:
  duration: ~20 minutes
  completed_date: 2026-06-21
  task_count: 2
  commit_count: 2
  file_count: 14
  test_count: 0 (manual verification via python -c)
---

# Phase 05 Plan 01: Parser Engine + Menu Engineering Engine Summary

**Build the Parser Engine (ENG-01) and Menu Engineering Engine (ENG-02) as standalone Python packages under `engines/`.**

The parser engine extracts structured orders from Malaysian F&B WhatsApp messages using a regex-first approach with DistilBERT NER fallback via ONNX Runtime. The menu engineering engine recommends optimized menu configurations via Google OR-Tools MILP solver with 6 hard-coded safety constraints.

## Implementation

### Parser Engine (`engines/parser/`)

- **RegexEngine**: 4 item patterns covering quantity-prefixed, x-notation, parenthesized-quantity, and standalone item names. 3 price patterns (RM prefix, decimal standalone, total/jumlah keyword), 3 time patterns (Malay/English time keywords, standalone HH:MM), and 2 customer patterns (nama/name/atas nama, dari).
- **NEREngine**: ONNX Runtime wrapper for DistilBERT with lazy loading, CPUExecutionProvider, configurable model path (env var `CCAM_PARSER_MODEL_PATH`, default `models/parser/distilbert-ner.onnx`), and graceful fallback when model is absent (confidence=0.2).
- **ParserPipeline**: Orchestrates regex first → NER fallback. Uses confidence threshold (default 0.6). Returns regex result if confidence >= threshold. Falls back to NER if regex confidence is low and NER improves.
- **Confidence scoring**: Per-field confidence (items, customer_name, pickup_time, total_price) + overall confidence (0.0-1.0). Regex baseline: items alone = 0.5, with price +0.2, time +0.15, customer +0.15.
- **Non-food keyword filter**: Filters out RM, total, jumlah, nama, catatan, pukul, etc. from being captured as food items.

### Menu Engineering Engine (`engines/menu/`)

- **MenuSolver**: OR-Tools CP-SAT formulation with decision variables (keep/remove binary, price delta integer bounded by ±30%/+50%), constraints (price bounds, margin floor ≥20% of cost, category min/max, total size cap ≤80 items), and weighted objective (profit 50%, variety 20%, price stability 20%, simplicity 10%).
- **MenuSafetyConstraints**: 6 non-overridable hard rules — no negative margin, no price below cost, keep at least 1 low-cost item (<RM8), no increase >50%, no decrease >30%, at least 1 item per category.
- **MenuEngine**: Safety-gated orchestrator running input validation → MILP solver → post-optimization validation. Supports strict mode (raises SafetyViolationError) and soft mode (filters unsafe changes).
- **Solver time limit**: 10 seconds max (T-05-03 DoS threat mitigation).

## Verification Results

Both packages install cleanly via `pip install -e .` and pass all verification checks:

**Parser checks:**
- ✅ Multi-item comma-separated message: "2 Nasi Lemak Ayam, 1 Teh Tarik, RM15.50" → 2 items, confidence 0.70, regex source
- ✅ Empty message returns empty order
- ✅ Single item: "Nasi Lemak" → 1 item, implicit qty=1
- ✅ All confidence scores in 0.0-1.0 range
- ✅ Malay time: "pukul 2 petang" → "2:00"
- ✅ Customer: "nama: Ali" → "Ali"
- ✅ Total price: "total RM15" → 1500 cents
- ✅ x-notation: "Nasi Lemak x2" → quantity 2
- ✅ Parenthesized: "Nasi Lemak (2)" → quantity 2
- ✅ Non-food keywords filtered (RM not captured as item)
- ✅ NER gracefully degrades without model (confidence=0.2)
- ✅ Per-field confidence reported

**Menu engine checks:**
- ✅ 5 items pass input validation
- ✅ Solver returns optimal status, score=100
- ✅ 5 price changes, 0 removals
- ✅ All price changes within ±50%/+30% bounds
- ✅ Recommendation passes all 6 safety rules
- ✅ Safety correctly rejects item with price below cost
- ✅ Infeasible constraint (min_items_per_category > available) correctly detected
- ✅ Solver time limit enforced (10s)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Functionality] Regex item patterns don't handle comma-separated lists**
- **Found during:** Task 1 verification
- **Issue:** The first ITEM_PATTERN's lookahead `(?=\s*(?:RM|\d+\.\d{2}|$))` required items to be followed by price or end-of-string. Most real messages use comma separation ("2 Nasi Lemak, 1 Teh Tarik"), which failed to match.
- **Fix:** Added `[,;]` to the lookahead: `(?=\s*(?:RM|\d+\.\d{2}|[,;]|$))`
- **Files modified:** `engines/parser/src/ccam_parser/regex_engine.py`
- **Commit:** `214acb3`

**2. [Rule 2 - Missing Functionality] No pattern for standalone item names**
- **Found during:** Task 1 verification
- **Issue:** Item patterns required a quantity prefix or suffix, but simple messages like "Nasi Lemak" (implicit qty=1) should be parsed.
- **Fix:** Added 4th ITEM_PATTERN `(?:^|[,;]\s*)(?P<item>[A-Za-z][A-Za-z\s/]+?)(?=\s*(?:RM|\d+\.\d{2}|[,;]|$))` and updated `_extract_items` to use `groupdict().get("qty")` for optional quantity groups. Added non-food keyword filter.
- **Files modified:** `engines/parser/src/ccam_parser/regex_engine.py`
- **Commit:** `214acb3`

**3. [Rule 2 - Missing Functionality] OR-Tools multiplication of variables not supported**
- **Found during:** Task 2 verification
- **Issue:** The objective used `weight * profit * self._keep_vars[item.id]` which multiplies a LinearExpr by a BoolVar — unsupported in OR-Tools CP-SAT API. Caused `TypeError: __mul__(): incompatible function arguments`.
- **Fix:** Refactored to use conditional profit variables with `OnlyEnforceIf` for both profit contribution and variety bonus terms instead of direct multiplication.
- **Files modified:** `engines/menu/src/ccam_menu/solver.py`
- **Commit:** `4d1f40d`

**4. [Rule 2 - Missing Functionality] No solver time limit**
- **Found during:** Task 2 verification
- **Issue:** Threat model T-05-03 specifies "OR-Tools CP-SAT has built-in time limits" as DoS mitigation, but no time limit was set.
- **Fix:** Added `self._solver.parameters.max_time_in_seconds = 10` per threat mitigation.
- **Files modified:** `engines/menu/src/ccam_menu/solver.py`
- **Commit:** `4d1f40d`

## Known Gaps

- DistilBERT ONNX model file (~50MB) not included — downloaded separately. NER engine gracefully falls back when model is absent.
- Simplified character-level tokenization for NER input. Full tokenization requires `tokenizers` / `huggingface` libraries.
- GPU inference not supported — CPUExecutionProvider only (D-05).
- Simulator validation pass (D-09) not implemented — deferred to Plan 04 backend wiring.
- Historical sales data integration not included — uses `avg_daily_orders` from existing data.
- Menu item addition recommendations (`items_to_add`) intentionally left empty — requires business input.
- No test suite yet — verification done via inline python scripts. Tests deferred to a follow-up plan.

## Testing

No formal test suite yet. Manual verification performed via:
- `uv run python3 -c "..."` for parser engine (10 test cases)
- `uv run python3 -c "..."` for menu engine (6 test cases)

All test cases pass.

## Self-Check: PASSED

All 14 files verified to exist:
- engines/parser/pyproject.toml ✓
- engines/parser/src/ccam_parser/__init__.py ✓
- engines/parser/src/ccam_parser/models.py ✓
- engines/parser/src/ccam_parser/regex_engine.py ✓
- engines/parser/src/ccam_parser/ner_engine.py ✓
- engines/parser/src/ccam_parser/pipeline.py ✓
- engines/parser/src/ccam_parser/exceptions.py ✓
- engines/menu/pyproject.toml ✓
- engines/menu/src/ccam_menu/__init__.py ✓
- engines/menu/src/ccam_menu/models.py ✓
- engines/menu/src/ccam_menu/safety.py ✓
- engines/menu/src/ccam_menu/solver.py ✓
- engines/menu/src/ccam_menu/engine.py ✓
- engines/menu/src/ccam_menu/exceptions.py ✓

All commits verified:
- `214acb3`: feat(05-advanced-engines): create ccam-parser package
- `4d1f40d`: feat(05-advanced-engines): create ccam-menu package

Both packages import independently without backend dependencies.
