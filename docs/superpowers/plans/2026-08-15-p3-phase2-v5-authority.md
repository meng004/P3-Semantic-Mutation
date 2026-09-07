# P3 Phase 2 Protocol V5 Authority Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze a two-stage Protocol V5 controller amendment: V-DESIGN
before capability code, V-FINAL after concrete manifests exist.

**Architecture:** V-DESIGN is a prospective scientific amendment
document plus schemas. It does not overwrite live `protocol.json`.
V-FINAL emits `p3-protocol-v2` only after capability registries exist
and binds those hashes. Each stage stops for an independent Sol High
verdict commit that the executor must not write.

**Tech Stack:** Python 3.12; `src/p3_v3/protocol_v5.py`;
`src/p3_v3/bridge_and_frames.py` `validate_protocol`; existing V4 file
at `data/p3_v3/protocol/protocol.json` until V-FINAL.

## Global Constraints

Every master-plan Global Constraint applies. Additional rules:

- Family→mechanism pairing, profiling execution strategies, and
  contract/predicate rules are prospective scientific protocol
  amendments. Do not call them engineering schema completion.
- Old scientific hashes are predecessor hashes only. They do not
  authorize the new semantics.
- Executor must not write `verdict=PASS`.
- No X1 before V-FINAL PASS.

---

## File map

| File | Responsibility |
|---|---|
| `src/p3_v3/protocol_v5.py` | Retain V4, emit V-DESIGN object, emit V-FINAL, preservation proof |
| `src/p3_v3/bridge_and_frames.py` | `validate_protocol` accepts `p3-protocol-v2` only as V-FINAL |
| `data/p3_v3/protocol/protocol.v4.json` | Retained V4 raw bytes after V-FINAL |
| `data/p3_v3/protocol/protocol.json` | Live V-FINAL only after Task VF1 |
| `docs/review_20260815/protocol_v5_design.md` | V-DESIGN scientific record |
| `docs/review_20260815/protocol_v5_design_packet.md` | V-DESIGN review packet |
| `docs/review_20260815/protocol_v5_design_verdict.md` | Controller-archived reviewer text |
| `docs/review_20260815/protocol_v5_final_packet.md` | V-FINAL review packet |
| `docs/review_20260815/protocol_v5_final_verdict.md` | Controller-archived reviewer text |
| `tests/p3_v3/test_protocol_v5_amendment.py` | V-DESIGN and V-FINAL tests |

---

## Scientific decisions locked by this plan

### Amendment ID

`PROTOCOL_V5_CONTROLLER_AMENDMENT_01`

### Preservation

V5 is BLOCKED if any of these differ from Phase 1 frozen bytes:

- 35 subject identities
- 460 selected `behavior_id`s and per-workload `artifact_sha256`s
- funnel 3/9/23 and the original 12 failure reasons
- 1050 `E_COMMON` rows
- `profiling_budgets`, `behavior_category_order`, `technique_order`,
  `e_common_count=30`, `e_contract_count=5`, `p12_outcome_states`,
  `p12_primary_estimand`, `infrastructure_retry_limit=3`,
  `claims_initial_status="blocked"`
- Protocol V4 raw file bytes

### Execution-row closure estimand

The confirmatory profiling denominator is 460 selected rows.

```text
N_total_rows = 460
N_bound_jobs = count(execution_plan.status == "EXECUTION_PLAN_BOUND")
N_preclosed_rows = 460 - N_bound_jobs
```

Only `N_bound_jobs` receive scientific intents. Preclosed rows remain
in the 460-row denominator as `ADAPTER_UNCERTAIN` with one of
`E_EXECUTION_BINDING_MISSING`, `E_EXECUTION_STRATEGY_UNSUPPORTED`,
`E_EXECUTION_PREREQUISITE_MISSING`, `E_SOURCE_MATERIALIZATION`,
`E_EXECUTABLE_RECIPE_ABSENT`, `E_TRACER_UNAVAILABLE`.

### Family → mechanism matrix

Governing plan §6.2 requires two slots per family and a permitted
construction mechanism per slot. It does not name the pairing. This
amendment completes that allocation using the only five permitted
mechanism IDs, each used exactly twice, assigned by frozen family
order and slot ordinal, independent of subject and profiling outcome.

```text
family_order = (INV, MONO, CONV, DYN, CMP)
mechanism_order = (CE, OS, HP, TF, SI)
mechanism(family_i, slot_ordinal) = mechanism_order[(i + slot_ordinal) % 5]
```

| family | slot 0 | slot 1 |
|---|---|---|
| INV | CE | OS |
| MONO | OS | HP |
| CONV | HP | TF |
| DYN | TF | SI |
| CMP | SI | CE |

### Profiling input role

`job_role="PROFILING"` requires `evaluation_input_class="PROFILING_WORKLOAD"`.
`E_COMMON` remains reserved for `PRIMARY_CONTROLLED` and `P12`.
The forbidden class name `PROFILING` stays forbidden.

### Tracer decision

See the profiling sub-plan. This amendment records the scientific
consequence: native strategies without a proven tracer are preclosed.
That is an estimand decision, not a later implementation hope.

### Contract / predicate decision

Predicates are family-specific static rules over frozen sites and
public-frame joins. Contracts are extracted from mounted public
documentation. If extraction cannot produce a real contract for an
applicable slot, authority status is
`PHASE2_CONTRACT_AUTHORITY_BLOCKED`. Dummy contracts are not a V5
escape hatch.

---

### Task VD1: V-DESIGN object and preservation proof

**Files:**
- Create: `src/p3_v3/protocol_v5.py`
- Create: `docs/review_20260815/protocol_v5_design.md`
- Test: `tests/p3_v3/test_protocol_v5_amendment.py`

**Interfaces:**

```python
from typing import Literal, Mapping, Sequence, TypedDict

V4_FILE_SHA256 = "240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519"
V4_ARTIFACT_SHA256 = "c4606414b3bfd3a9df10a19959dedb3e08add25b220179ef891be24bda5eb882"
AMENDMENT_ID = "PROTOCOL_V5_CONTROLLER_AMENDMENT_01"
FAMILIES = ("INV", "MONO", "CONV", "DYN", "CMP")
MECHANISMS = ("CE", "OS", "HP", "TF", "SI")


class SlotMatrixRow(TypedDict):
    family: str
    slot_ordinal: int
    mechanism: str


class ProtocolV5Design(TypedDict):
    schema_version: Literal["p3-protocol-v5-design-v1"]
    amendment_id: str
    predecessor_protocol_file_sha256: str
    predecessor_protocol_artifact_sha256: str
    predecessor_scientific_plan_sha256: str
    predecessor_evidence_design_sha256: str
    evaluation_input_class_by_role: dict[str, str]
    semantic_contract_families: list[str]
    slot_construction_matrix: list[SlotMatrixRow]
    execution_row_estimand: dict[str, object]
    claims_initial_status: Literal["blocked"]
    artifact_sha256: str


def retain_protocol_v4_bytes(source: Path, destination: Path) -> str:
    """Copy exact bytes and return file_sha256(destination)."""


def emit_protocol_v5_design(v4: Mapping[str, object]) -> ProtocolV5Design:
    """Return the design object. Do not write live protocol.json."""


def prove_phase1_selection_preserved(
    v4_path: Path,
    design: ProtocolV5Design,
    phase1_counts: Mapping[str, int],
) -> None:
    """Raise E_PROTOCOL_V5_SELECTION unless 35/460/3-9-23/1050 hold."""
```

Error codes: `E_PROTOCOL_V5_PREDECESSOR`, `E_PROTOCOL_V5_SELECTION`,
`E_PROTOCOL_HASH`.

Production caller: none in VD1. `validate-protocol` still validates V4
until VF1.

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, file_sha256, read_canonical_json
from p3_v3.protocol_v5 import (
    AMENDMENT_ID,
    V4_ARTIFACT_SHA256,
    V4_FILE_SHA256,
    emit_protocol_v5_design,
    prove_phase1_selection_preserved,
    retain_protocol_v4_bytes,
)

PHASE1_COUNTS = {
    "subject_count": 35,
    "selected_profiling_rows": 460,
    "adapter_unsupported": 3,
    "adapter_execution_failed": 9,
    "executable": 23,
    "common_input_count": 1050,
}


def test_retain_v4_bytes_match_known_digest(tmp_path: Path) -> None:
    live = Path("data/p3_v3/protocol/protocol.json")
    retained = Path("data/p3_v3/protocol/protocol.v4.json")
    source = retained if retained.is_file() else live
    destination = tmp_path / "protocol.v4.json"
    digest = retain_protocol_v4_bytes(source, destination)
    assert digest == V4_FILE_SHA256
    assert destination.read_bytes() == source.read_bytes()
    assert file_sha256(source) == V4_FILE_SHA256


def test_design_keeps_predecessor_hashes_and_does_not_write_live() -> None:
    live = Path("data/p3_v3/protocol/protocol.json")
    retained = Path("data/p3_v3/protocol/protocol.v4.json")
    v4 = read_canonical_json(retained if retained.is_file() else live)
    before = live.read_bytes()
    design = emit_protocol_v5_design(v4)
    assert live.read_bytes() == before
    assert design["amendment_id"] == AMENDMENT_ID
    assert design["predecessor_protocol_file_sha256"] == V4_FILE_SHA256
    assert design["predecessor_protocol_artifact_sha256"] == V4_ARTIFACT_SHA256
    assert design["predecessor_scientific_plan_sha256"] == v4["scientific_plan_sha256"]
    assert design["predecessor_evidence_design_sha256"] == v4["evidence_design_sha256"]
    assert design["evaluation_input_class_by_role"]["PROFILING"] == "PROFILING_WORKLOAD"
    assert design["evaluation_input_class_by_role"]["P12"] == "E_COMMON"
    assert design["claims_initial_status"] == "blocked"
    assert design["slot_construction_matrix"][0] == {
        "family": "INV",
        "slot_ordinal": 0,
        "mechanism": "CE",
    }
    assert design["execution_row_estimand"]["n_total_rows"] == 460


def test_preservation_rejects_changed_e_common_count() -> None:
    live = Path("data/p3_v3/protocol/protocol.json")
    retained = Path("data/p3_v3/protocol/protocol.v4.json")
    v4 = read_canonical_json(retained if retained.is_file() else live)
    design = emit_protocol_v5_design(v4)
    changed = dict(PHASE1_COUNTS)
    changed["common_input_count"] = 1049
    with pytest.raises(EvidenceError, match="E_PROTOCOL_V5_SELECTION"):
        prove_phase1_selection_preserved(live, design, changed)
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_protocol_v5_amendment.py -q
```

Expected: FAIL because `p3_v3.protocol_v5` is absent.

- [ ] **Step 3: Minimal implementation**

```python
from pathlib import Path
from typing import Mapping

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    validate_sha256,
)

V4_FILE_SHA256 = "240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519"
V4_ARTIFACT_SHA256 = "c4606414b3bfd3a9df10a19959dedb3e08add25b220179ef891be24bda5eb882"
AMENDMENT_ID = "PROTOCOL_V5_CONTROLLER_AMENDMENT_01"
FAMILIES = ("INV", "MONO", "CONV", "DYN", "CMP")
MECHANISMS = ("CE", "OS", "HP", "TF", "SI")


def retain_protocol_v4_bytes(source: Path, destination: Path) -> str:
    destination.write_bytes(source.read_bytes())
    digest = file_sha256(destination)
    if digest != V4_FILE_SHA256:
        raise EvidenceError("E_PROTOCOL_V5_PREDECESSOR", "V4 file digest differs")
    return digest


def emit_protocol_v5_design(v4: Mapping[str, object]) -> dict:
    matrix = [
        {
            "family": family,
            "slot_ordinal": ordinal,
            "mechanism": MECHANISMS[(index + ordinal) % 5],
        }
        for index, family in enumerate(FAMILIES)
        for ordinal in (0, 1)
    ]
    body = {
        "schema_version": "p3-protocol-v5-design-v1",
        "amendment_id": AMENDMENT_ID,
        "predecessor_protocol_file_sha256": V4_FILE_SHA256,
        "predecessor_protocol_artifact_sha256": V4_ARTIFACT_SHA256,
        "predecessor_scientific_plan_sha256": v4["scientific_plan_sha256"],
        "predecessor_evidence_design_sha256": v4["evidence_design_sha256"],
        "evaluation_input_class_by_role": {
            "PRIMARY_CONTROLLED": "E_COMMON",
            "P12": "E_COMMON",
            "CONTRACT_SENSITIVITY": "E_CONTRACT",
            "PROFILING": "PROFILING_WORKLOAD",
        },
        "semantic_contract_families": list(FAMILIES),
        "slot_construction_matrix": matrix,
        "execution_row_estimand": {
            "n_total_rows": 460,
            "bound_jobs_are_subset": True,
            "preclosed_remain_in_denominator": True,
        },
        "claims_initial_status": "blocked",
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def prove_phase1_selection_preserved(v4_path, design, phase1_counts) -> None:
    validate_sha256(design["predecessor_protocol_file_sha256"], "predecessor_file")
    retained = Path("data/p3_v3/protocol/protocol.v4.json")
    source = retained if retained.is_file() else Path(v4_path)
    if file_sha256(source) != V4_FILE_SHA256:
        raise EvidenceError("E_PROTOCOL_V5_PREDECESSOR", "V4 bytes differ")
    expected = {
        "subject_count": 35,
        "selected_profiling_rows": 460,
        "adapter_unsupported": 3,
        "adapter_execution_failed": 9,
        "executable": 23,
        "common_input_count": 1050,
    }
    if dict(phase1_counts) != expected:
        raise EvidenceError("E_PROTOCOL_V5_SELECTION", "Phase 1 selection counts differ")
    if design["claims_initial_status"] != "blocked":
        raise EvidenceError("E_PROTOCOL_V5_SELECTION", "claims are not blocked")
```

Write `docs/review_20260815/protocol_v5_design.md` with the scientific
decisions in this file, including the matrix reason and the statement
that predecessor hashes do not authorize the new semantics.

The preservation helper must compare the live-or-retained V4 file
digest to `V4_FILE_SHA256` and compare `phase1_counts` to the exact
expected mapping above. Do not read Package C or P12 reveal.

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command as Step 2. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/protocol_v5.py \
  docs/review_20260815/protocol_v5_design.md \
  tests/p3_v3/test_protocol_v5_amendment.py
rtk git commit -m "feat(p3-v3): add Protocol V5 design object" -m "Record the prospective scientific amendment without replacing live V4."
```

### Task VD2: V-DESIGN review packet and stop

**Files:**
- Create: `docs/review_20260815/protocol_v5_design_packet.md`

**Interfaces:**
- Consumes: VD1 commit and design SHA-256.
- Produces: packet only. Do not write a PASS verdict.

- [ ] **Step 1: Write the packet**

The packet must name the VD1 commit, design SHA-256, predecessor
hashes, preservation requirements, and `claims=blocked`. It must tell
the reviewer that the packet is not a verdict.

- [ ] **Step 2: Commit the packet and stop**

```bash
rtk git add docs/review_20260815/protocol_v5_design_packet.md
rtk git commit -m "docs(p3-v3): add Protocol V5 design review packet" -m "Stop for independent Sol High review. Do not emit live V5."
```

Status after this commit: `PHASE2_V5_DESIGN_REVIEW_CANDIDATE`.
Do not start capability work that depends on V-DESIGN PASS.

Controller later archives the reviewer text as
`docs/review_20260815/protocol_v5_design_verdict.md` in a separate
commit. The executor must not author that PASS.

### Task VF1: V-FINAL live protocol

**Files:**
- Modify: `src/p3_v3/protocol_v5.py` add `emit_protocol_v5_final`
- Modify: `src/p3_v3/bridge_and_frames.py` `validate_protocol`
- Modify: `src/p3_v3/run_records.py` `_ROLE_REQUIRED_INPUT_CLASS`
- Create: `data/p3_v3/protocol/protocol.v4.json`
- Modify: `data/p3_v3/protocol/protocol.json`
- Test: `tests/p3_v3/test_protocol_v5_amendment.py`

Start VF1 only after V-DESIGN verdict is PASS and capability
manifests exist.

**Interfaces:**

```python
class ProtocolV5Final(TypedDict):
    schema_version: Literal["p3-protocol-v2"]
    amendment_id: str
    predecessor_protocol_file_sha256: str
    predecessor_protocol_artifact_sha256: str
    predecessor_scientific_plan_sha256: str
    predecessor_evidence_design_sha256: str
    controller_amendment_sha256: str
    plan_package_manifest_sha256: str
    source_materialization_manifest_sha256: str
    execution_strategy_registry_sha256: str
    profiling_execution_plan_schema_sha256: str
    profiling_trace_schema_sha256: str
    profiling_runner_manifest_sha256: str
    slot_matrix_sha256: str
    applicability_predicate_registry_sha256: str
    contract_authority_schema_sha256: str
    contract_generator_registry_sha256: str
    evaluation_input_class_by_role: dict[str, str]
    claims_initial_status: Literal["blocked"]
    scientific_plan_sha256: str
    evidence_design_sha256: str
    profiling_budgets: dict[str, int]
    behavior_category_order: list[str]
    technique_order: list[str]
    e_common_count: int
    e_contract_count: int
    p12_outcome_states: list[str]
    p12_primary_estimand: str
    infrastructure_retry_limit: int
    artifact_sha256: str


def emit_protocol_v5_final(
    v4: Mapping[str, object],
    design: ProtocolV5Design,
    concrete_hashes: Mapping[str, str],
) -> ProtocolV5Final:
    """Bind every concrete manifest hash. Fail if any hash is missing."""
```

`scientific_plan_sha256` and `evidence_design_sha256` on the live
object remain the V4 values and are documented as predecessor
scientific documents. The new semantics are authorized by
`controller_amendment_sha256` plus the concrete manifest hashes, not
by those old documents.

Required `concrete_hashes` keys are exactly the `*_sha256` fields
listed above except the four predecessor fields already on `design`.

- [ ] **Step 1: Write the failing test**

```python
def test_final_requires_concrete_manifest_hashes() -> None:
    live = Path("data/p3_v3/protocol/protocol.json")
    retained = Path("data/p3_v3/protocol/protocol.v4.json")
    v4 = read_canonical_json(retained if retained.is_file() else live)
    design = emit_protocol_v5_design(v4)
    with pytest.raises(EvidenceError, match="E_PROTOCOL_V5_MANIFEST"):
        emit_protocol_v5_final(v4, design, {})


def test_final_binds_predecessor_and_concrete_hashes() -> None:
    live = Path("data/p3_v3/protocol/protocol.json")
    retained = Path("data/p3_v3/protocol/protocol.v4.json")
    v4 = read_canonical_json(retained if retained.is_file() else live)
    design = emit_protocol_v5_design(v4)
    hashes = {key: "ab" * 32 for key in FINAL_HASH_KEYS}
    final = emit_protocol_v5_final(v4, design, hashes)
    assert final["schema_version"] == "p3-protocol-v2"
    assert final["predecessor_protocol_file_sha256"] == V4_FILE_SHA256
    assert final["controller_amendment_sha256"] == hashes["controller_amendment_sha256"]
    assert final["profiling_budgets"] == v4["profiling_budgets"]
    assert final["e_common_count"] == 30
    assert final["claims_initial_status"] == "blocked"
```

`FINAL_HASH_KEYS` is the tuple of concrete hash field names declared
in this task, defined in `src/p3_v3/protocol_v5.py` and imported by
the test.

- [ ] **Step 2: Run the new tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_protocol_v5_amendment.py::test_final_requires_concrete_manifest_hashes \
  tests/p3_v3/test_protocol_v5_amendment.py::test_final_binds_predecessor_and_concrete_hashes -q
```

Expected: FAIL because `emit_protocol_v5_final` is absent.

- [ ] **Step 3: Minimal implementation**

Implement `emit_protocol_v5_final`. Copy V4 scientific count fields
unchanged. Require every concrete hash. Retain V4 bytes to
`protocol.v4.json` before replacing live `protocol.json`. Change
`_ROLE_REQUIRED_INPUT_CLASS["PROFILING"]` to `PROFILING_WORKLOAD`.
Extend `validate_protocol` to accept `p3-protocol-v2` only when
`predecessor_protocol_file_sha256 == V4_FILE_SHA256`.

- [ ] **Step 4: Re-run those tests and confirm they pass**

Same command as Step 2. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/protocol_v5.py src/p3_v3/bridge_and_frames.py \
  src/p3_v3/run_records.py data/p3_v3/protocol/protocol.v4.json \
  data/p3_v3/protocol/protocol.json \
  tests/p3_v3/test_protocol_v5_amendment.py
rtk git commit -m "feat(p3-v3): emit live Protocol V5 after concrete manifests" -m "Retain V4 bytes and bind predecessor plus capability hashes."
```

### Task VF2: V-FINAL review packet and stop

**Files:**
- Create: `docs/review_20260815/protocol_v5_final_packet.md`

- [ ] **Step 1: Write the packet**
- [ ] **Step 2: Commit and stop**

```bash
rtk git add docs/review_20260815/protocol_v5_final_packet.md
rtk git commit -m "docs(p3-v3): add Protocol V5 final review packet" -m "Stop for independent Sol High review before X1."
```

Status: `PHASE2_V5_FINAL_REVIEW_CANDIDATE`.
Controller later commits `protocol_v5_final_verdict.md`.
No X1 without that PASS.

---

## Acceptance

1. V-DESIGN object exists and does not overwrite live V4.
2. Preservation proof rejects count drift.
3. V-DESIGN packet committed; executor-authored PASS absent.
4. V-FINAL binds every listed concrete hash.
5. V4 raw bytes retained.
6. Claims remain blocked.
