# P3 C3 Contract Authority Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ordinal 8's six frozen slots ready for one separately authorized contract and `E_CONTRACT` freeze.

**Architecture:** Reuse the existing contract registry validator and `build_contract_inputs()` seam. Add five hash-bound generator implementations, one deep ordinal-8 authority module, and one exclusive-write command; do not add a schema, manifest, ledger, or gate.

**Tech Stack:** Python 3.11, canonical JSON artifacts, pytest.

## Global Constraints

- Baseline commit is `19fbb31559f3d83677b664cac09d424e6a807e66`.
- Formal prospective-v2 execution is never retried.
- No outcome, patch, reveal, profiling result, or MR material is consumed.
- This implementation does not write formal contracts or `E_CONTRACT` artifacts.
- Focused tests only; no full suite or subject execution.

---

### Task 1: Production contract generators

**Files:**
- Create: `src/p3_v3/contract_generators/*.py`
- Create: `data/p3_v3/protocol/contract-generator-registry.json`
- Test: `tests/p3_v3/test_contract_authority.py`

**Interfaces:**
- Consumes: existing `generate(schema_bytes: bytes, seed: int) -> dict` loader contract.
- Produces: five registered implementations for the exact existing allowlist.

- [ ] Write tests for deterministic enum, numeric, array, sequence, and relation-pair payloads and invalid-domain failure codes.
- [ ] Run the focused test and observe import/registry failure.
- [ ] Implement the five minimal standalone generators.
- [ ] Materialize the single existing-format registry with implementation SHA-256 values.
- [ ] Run the generator tests and existing registry tests.

### Task 2: Ordinal 8 authority module

**Files:**
- Create: `src/p3_v3/contract_authority.py`
- Modify: `tests/p3_v3/test_contract_authority.py`

**Interfaces:**
- Consumes: the ten formal closures and validated generator registry.
- Produces: `build_ordinal8_contracts()` and `freeze_ordinal8_package()`.

- [ ] Write tests for six exact contracts, four excluded closures, three semantic domains, recomputable IDs, and 30 generated rows.
- [ ] Run the focused test and observe missing module failure.
- [ ] Implement exact identity checks and the three outcome-blind contract templates.
- [ ] Delegate row generation only to `build_contract_inputs()`.
- [ ] Run focused tests and the existing chronology regression.

### Task 3: Exclusive formal-freeze command

**Files:**
- Create: `scripts/p3_v3/freeze_ordinal8_contracts.py`
- Modify: `tests/p3_v3/test_contract_authority.py`

**Interfaces:**
- Consumes: closure root, registry path/root, and an empty output root.
- Produces later, under separate authorization: one contracts JSON and six `E_CONTRACT` inventories.

- [ ] Write CLI tests for in-memory validation, refusal of existing output, and no partial writes on invalid identity.
- [ ] Run the focused test and observe missing command failure.
- [ ] Implement preflight-first exclusive writes with no retry/resume options.
- [ ] Run CLI and bridge/chronology focused regressions.

### Task 4: Freeze engineering baseline

**Files:**
- Modify only files listed above plus this design and plan.

- [ ] Run all focused contract-authority tests.
- [ ] Run existing contract-registry, contract-input, and chronology tests.
- [ ] Run `git diff --check`.
- [ ] Verify no formal contract/E_CONTRACT output exists.
- [ ] Commit the implementation without running the formal command.
