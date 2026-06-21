---
phase: 1
slug: 01-simulator-core
status: verified
threats_open: 0
asvs_level: 1
created: 2026-06-21
---

# Phase 1 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| User → CLI | Untrusted YAML file loaded from filesystem at user request | Scenario YAML with menu, stock, station config |
| CLI → Safety Layer | Safety must be called before simulation begins and every tick | SimState mutations |
| Engine pipeline ↔ SimState | Data integrity — engines mutate shared state; order of operations determines correctness | Events, KPI data |
| Pipeline → Safety Gate 2 | Safety depends on per-tick check running after stock mutations | Stock levels, step count |
| Test fixtures ↔ Source code | Tests consume production source; test corruption could mask bugs | Source imports |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T1-01 | Tampering | loader.py | mitigate | `yaml.safe_load()` exclusively at `loader.py:37`. PyYAML 6.0.3 pinned in `pyproject.toml`. | closed |
| T1-02 | Tampering | loader.py | mitigate | `click.Path(exists=True, dir_okay=False)` validates file exists and is readable before loader runs at `cli.py:24`. | closed |
| T1-03 | Repudiation | rand.py | accept | CLI is local single-user; no audit trail needed for RNG seed choice. Phase 2 adds audit logging. | closed |
| T2-01 | Tampering | loader.py | mitigate | Same as T1-01 — `yaml.safe_load()` at `loader.py:37`. | closed |
| T2-02 | Tampering | cli.py | mitigate | `click.Path(exists=True)` file validation at `cli.py:24`. Scenario validated via `validate_scenario()` before pipeline at `cli.py:41`. | closed |
| T2-03 | Denial of Service | safety.py | mitigate | `max_steps` guard at `safety.py:50-56` (Gate 1 `_check_max_steps`) and `pipeline.py:51` (while-loop `state.step < max_steps`). Per-tick check at `safety.py:83-89`. | closed |
| T2-04 | Tampering | safety.py | mitigate | Gate 1 at `cli.py:41` (`validate_scenario`). Gate 2 at `pipeline.py:58` (`check_per_tick` each tick). Both must pass. | closed |
| T3-01 | Tampering | pipeline.py | mitigate | Strict engine ordering at `pipeline.py:44-62`: demand → order → [tick: kitchen → stock → safety] → kpi. No engine can skip others. | closed |
| T3-02 | Denial of Service | pipeline.py | mitigate | `max_steps` read from scenario and enforced in loop condition at `pipeline.py:40,51` + per-tick safety check. | closed |
| T3-03 | Information Disclosure | engines/kpi.py | accept | In-memory event log only. No external data access in Phase 1. | closed |
| T3-04 | Tampering | engines/stock.py | mitigate | Gate 2 enforces no-negative-stock per tick via `safety.py:73-79` (`_check_stock_non_negative`) called at `pipeline.py:58` after `stock_engine()`. | closed |
| T4-01 | Tampering | tests/ | mitigate | Tests import production code directly at `test_determinism.py:9` — any source change that breaks determinism is caught. | closed |
| T4-02 | Repudiation | test_determinism.py | mitigate | 7 deterministic replay tests serve as acceptance gate (SIM-08). | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R1-01 | T1-03 | CLI is local single-user; RNG seed audit trail not needed. Phase 2 adds server-side audit logging. | Design decision | 2026-06-21 |
| R1-02 | T3-03 | KPI engine uses in-memory event log only. No external data accessed in Phase 1. | Design decision | 2026-06-21 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-06-21 | 13 | 13 | 0 | gsd-security-auditor |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-06-21
