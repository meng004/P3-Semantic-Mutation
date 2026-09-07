# P3 Phase 2 Authorized Execution Runbook

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.
>
> This file is not itself a user authorization. X1 starts only after
> production-preparation authorization. X4 starts only after scientific
> profiling authorization.

**Goal:** Encode the two user-authorization gates and the twelve Lane X
nodes so later authorized execution cannot start early, skip a hash,
or create a confirmatory intent before X4 is allowed.

**Architecture:** Gate checkers are ordinary Python functions with
fail-closed tests. X1–X3 consume those gates and write only preflight,
pilot, and inventory artifacts. X4–X12 consume the second gate and
execute `N_bound_jobs` only. Checkpoint files refuse duplicate starts.

**Tech Stack:** Python 3.12; `src/p3_v3/phase2_authorization.py`;
`scripts/p3_v3/evidence.py` Phase 2 commands.

## Global Constraints

Master-plan Global Constraints apply. Additional rules:

- Boxes 5–8 of the old single launch gate are produced by X1–X3. They
  are not prerequisites of X1.
- X1–X3 must not call `create_intent`.
- X4 expected job count is `N_bound_jobs`, never the literal 460.
- Claims stay `blocked`.
- No node may start if its checkpoint file already exists with
  `status=STARTED` or `status=CLOSED`.

---

## File map

| File | Responsibility |
|---|---|
| `src/p3_v3/phase2_authorization.py` | two gates, node checkpoint, resume, duplicate-start |
| `scripts/p3_v3/evidence.py` | Phase 2 X-node commands |
| `tests/p3_v3/test_phase2_authorization.py` | gate and checkpoint tests |
| `data/p3_v3/phase2/checkpoints/<node>.json` | per-node checkpoint |

---

## Shared interfaces

```python
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, TypedDict


class AuthorizationRecord(TypedDict):
    schema_version: Literal["p3-phase2-authorization-v1"]
    kind: Literal["PRODUCTION_PREPARATION", "SCIENTIFIC_PROFILING"]
    user_sentence: str
    plan_package_manifest_sha256: str
    v_design_verdict_sha256: str
    v_final_verdict_sha256: str
    implementation_verdict_sha256: str
    claims_status: Literal["blocked"]
    package_c_absent: Literal[True]
    artifact_sha256: str


class NodeCheckpoint(TypedDict):
    schema_version: Literal["p3-phase2-node-checkpoint-v1"]
    node_id: str
    status: Literal["STARTED", "CLOSED", "FAILED"]
    input_sha256: dict[str, str]
    counts: dict[str, int]
    command: list[str]
    exit_code: int
    artifact_sha256: str


def require_production_preparation(record: AuthorizationRecord) -> None:
    """Raise E_PHASE2_AUTH unless kind is PRODUCTION_PREPARATION and claims are blocked."""


def require_scientific_profiling(
    record: AuthorizationRecord,
    x1_receipt: Mapping[str, object],
    x2_receipt: Mapping[str, object],
    x3_inventory: Mapping[str, object],
) -> None:
    """Raise E_PHASE2_AUTH unless X1–X3 counts and the second user sentence hold."""


def start_node(path: Path, node_id: str, command: list[str], input_sha256: dict[str, str]) -> NodeCheckpoint:
    """Refuse if the checkpoint already exists."""


def close_node(path: Path, started: NodeCheckpoint, counts: dict[str, int], exit_code: int) -> NodeCheckpoint:
    """Write CLOSED only when exit_code==0."""


def resume_node(path: Path) -> NodeCheckpoint:
    """Return FAILED checkpoints only. STARTED and CLOSED raise E_PHASE2_DUPLICATE_START."""
```

X3 inventory required counts:

```text
total_rows = 460
bound_job_count = N_bound_jobs
preclosed_row_count = N_preclosed_rows
empty_subject_receipt_count = 12
replacement_count = 0
hand_selected_argv_count = 0
synthetic_production_argv_count = 0
N_bound_jobs + N_preclosed_rows = 460
```

---

### Task AUTH1: Production-preparation gate

**Files:**
- Create: `src/p3_v3/phase2_authorization.py`
- Test: `tests/p3_v3/test_phase2_authorization.py`

- [ ] **Step 1: Write the failing tests**

```python
import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256
from p3_v3.phase2_authorization import require_production_preparation


def production_record() -> dict:
    body = {
        "schema_version": "p3-phase2-authorization-v1",
        "kind": "PRODUCTION_PREPARATION",
        "user_sentence": "I authorize Phase 2 production preparation for X1 through X3.",
        "plan_package_manifest_sha256": "11" * 32,
        "v_design_verdict_sha256": "22" * 32,
        "v_final_verdict_sha256": "33" * 32,
        "implementation_verdict_sha256": "44" * 32,
        "claims_status": "blocked",
        "package_c_absent": True,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def test_production_gate_accepts_complete_record() -> None:
    require_production_preparation(production_record())


def test_production_gate_rejects_scientific_kind() -> None:
    record = production_record()
    record["kind"] = "SCIENTIFIC_PROFILING"
    with pytest.raises(EvidenceError, match="E_PHASE2_AUTH"):
        require_production_preparation(record)


def test_production_gate_rejects_unblocked_claims() -> None:
    record = production_record()
    record["claims_status"] = "open"
    with pytest.raises(EvidenceError, match="E_PHASE2_AUTH"):
        require_production_preparation(record)
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_production_gate_accepts_complete_record \
  tests/p3_v3/test_phase2_authorization.py::test_production_gate_rejects_scientific_kind \
  tests/p3_v3/test_phase2_authorization.py::test_production_gate_rejects_unblocked_claims -q
```

Expected: FAIL because `phase2_authorization` is absent.

- [ ] **Step 3: Minimal implementation**

```python
from p3_v3.artifacts import EvidenceError, canonical_sha256, validate_exact_object

_AUTH_SCHEMA = {
    "schema_version": str,
    "kind": str,
    "user_sentence": str,
    "plan_package_manifest_sha256": str,
    "v_design_verdict_sha256": str,
    "v_final_verdict_sha256": str,
    "implementation_verdict_sha256": str,
    "claims_status": str,
    "package_c_absent": bool,
    "artifact_sha256": str,
}


def require_production_preparation(record):
    value = validate_exact_object(dict(record), _AUTH_SCHEMA, "authorization")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PHASE2_AUTH", "authorization self-hash differs")
    if value["kind"] != "PRODUCTION_PREPARATION":
        raise EvidenceError("E_PHASE2_AUTH", "production preparation kind required")
    if value["claims_status"] != "blocked":
        raise EvidenceError("E_PHASE2_AUTH", "claims must stay blocked")
    if value["package_c_absent"] is not True:
        raise EvidenceError("E_PHASE2_AUTH", "Package C must be absent")
    if "I authorize Phase 2 production preparation" not in value["user_sentence"]:
        raise EvidenceError("E_PHASE2_AUTH", "user sentence is absent")
```

- [ ] **Step 4: Re-run those tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/phase2_authorization.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): add production-preparation authorization gate" -m "Refuse X1 until the user sentence, verdicts, and blocked claims are present."
```

### Task AUTH2: Scientific profiling gate and checkpoints

**Files:**
- Modify: `src/p3_v3/phase2_authorization.py`
- Test: `tests/p3_v3/test_phase2_authorization.py`

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256
from p3_v3.phase2_authorization import (
    close_node,
    require_scientific_profiling,
    resume_node,
    start_node,
)


def scientific_record() -> dict:
    body = {
        "schema_version": "p3-phase2-authorization-v1",
        "kind": "SCIENTIFIC_PROFILING",
        "user_sentence": "I authorize Phase 2 scientific profiling for X4 through X12.",
        "plan_package_manifest_sha256": "11" * 32,
        "v_design_verdict_sha256": "22" * 32,
        "v_final_verdict_sha256": "33" * 32,
        "implementation_verdict_sha256": "44" * 32,
        "claims_status": "blocked",
        "package_c_absent": True,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def x3_inventory(bound: int, preclosed: int) -> dict:
    return {
        "total_rows": 460,
        "bound_job_count": bound,
        "preclosed_row_count": preclosed,
        "empty_subject_receipt_count": 12,
        "replacement_count": 0,
        "hand_selected_argv_count": 0,
        "synthetic_production_argv_count": 0,
    }


def test_scientific_gate_requires_x3_partition() -> None:
    require_scientific_profiling(
        scientific_record(),
        {"status": "PASS"},
        {"status": "PASS", "denominator": "PILOT_ONLY"},
        x3_inventory(8, 452),
    )


def test_scientific_gate_rejects_non_partition() -> None:
    with pytest.raises(EvidenceError, match="E_PHASE2_AUTH"):
        require_scientific_profiling(
            scientific_record(),
            {"status": "PASS"},
            {"status": "PASS", "denominator": "PILOT_ONLY"},
            x3_inventory(8, 451),
        )


def test_checkpoint_refuses_duplicate_start(tmp_path: Path) -> None:
    path = tmp_path / "X4.json"
    start_node(path, "X4", ["evidence.py", "execute-bound-profiling"], {"inventory": "aa" * 32})
    with pytest.raises(EvidenceError, match="E_PHASE2_DUPLICATE_START"):
        start_node(path, "X4", ["evidence.py", "execute-bound-profiling"], {"inventory": "aa" * 32})


def test_resume_allows_failed_only(tmp_path: Path) -> None:
    path = tmp_path / "X4.json"
    started = start_node(path, "X4", ["evidence.py", "execute-bound-profiling"], {"inventory": "aa" * 32})
    close_node(path, started, {"bound_job_count": 0}, exit_code=1)
    resumed = resume_node(path)
    assert resumed["status"] == "FAILED"
    closed = start_node(tmp_path / "X5.json", "X5", ["evidence.py", "validate-profiling-ledger"], {})
    close_node(tmp_path / "X5.json", closed, {}, exit_code=0)
    with pytest.raises(EvidenceError, match="E_PHASE2_DUPLICATE_START"):
        resume_node(tmp_path / "X5.json")
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py -q
```

Expected: FAIL because `require_scientific_profiling` or `start_node`
is absent.

- [ ] **Step 3: Minimal implementation**

`require_scientific_profiling` checks kind, the scientific user
sentence, X1/X2 PASS, `x3["total_rows"]==460`,
`bound + preclosed == 460`, empty receipts 12, and the three zero
replacement counts. `start_node` writes exclusive JSON. `resume_node`
reads FAILED only.

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/phase2_authorization.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): add scientific profiling gate and node checkpoints" -m "Refuse X4 until X1-X3 counts partition 460 and the user authorizes profiling."
```

### Task X1: Real preflight

**Files:**
- Modify: `scripts/p3_v3/evidence.py` add `run-phase2-preflight`

This task is executed only after production-preparation authorization.
It is not a capability-unit-test task.

Exact command after capability exists:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  run-phase2-preflight \
  --repo-root . \
  --spec data/p3_v3/phase2/preflight-spec.json \
  --authorization data/p3_v3/phase2/production-preparation.json \
  --checkpoint data/p3_v3/phase2/checkpoints/X1.json
```

| Field | Rule |
|---|---|
| Inputs | production-preparation record; source-materialization manifest SHA-256; Protocol V-FINAL SHA-256 |
| Counts | `subject_count=35`, `smoke_executed_count=23`, `smoke_retained_count=12` |
| Exit 0 | all three counts hold and Package C checks pass |
| Exit 2 | `E_SOURCE_MATERIALIZATION` or Package C class/field/path |
| Checkpoint | `X1.json` STARTED then CLOSED |
| Resume | only from FAILED; do not rerun a CLOSED X1 |
| Duplicate start | `E_PHASE2_DUPLICATE_START` |
| Forbidden | `create_intent`, Package C, recapture |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
from pathlib import Path

import scripts.p3_v3.evidence as evidence_module


def test_run_phase2_preflight_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "run-phase2-preflight" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_run_phase2_preflight_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register the command. The handler calls
`require_production_preparation`, `start_node`, `run_phase2_preflight`,
then `close_node`. It must not import `create_intent`.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): register authorized Phase 2 preflight command" -m "X1 stays behind the production-preparation gate and writes no scientific intent."
```

### Task X2: Actual PILOT_ONLY

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  pilot-only \
  --root data/p3_v3/phase2/pilot \
  --spec data/p3_v3/phase2/pilot-spec.json \
  --authorization data/p3_v3/phase2/production-preparation.json \
  --checkpoint data/p3_v3/phase2/checkpoints/X2.json
```

| Field | Rule |
|---|---|
| Inputs | X1 CLOSED hash; production-preparation record; frozen 7-role spec |
| Counts | 7 pilot subjects; independent ledger events only |
| Exit 0 | five terminals plus two slot paths observed |
| Exit 2 | confirmatory ledger write attempted or P12 ID present |
| Checkpoint | `X2.json` |
| Resume / duplicate | same as X1 |
| Forbidden | `create_intent`, scientific `_INTENT_SCHEMA` |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
import scripts.p3_v3.evidence as evidence_module


def test_pilot_only_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "pilot-only" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_pilot_only_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register `pilot-only`. Handler calls `require_production_preparation`
and `run_pilot_only`. Write only `pilot-ledger.jsonl`.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): register authorized PILOT_ONLY command" -m "Keep the independent pilot ledger out of confirmatory run records."
```

### Task X3: Freeze profiling execution inventory

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  freeze-profiling-inventory \
  --workload-root data/p3_v3/derived \
  --materialization data/p3_v3/phase2/source-materialization.json \
  --authorization data/p3_v3/phase2/production-preparation.json \
  --checkpoint data/p3_v3/phase2/checkpoints/X3.json \
  --output data/p3_v3/phase2/profiling-execution-inventory.json
```

| Field | Rule |
|---|---|
| Inputs | X2 CLOSED; 35 source bindings; 35 frozen workloads |
| Counts | `total_rows=460`; `bound_job_count + preclosed_row_count = 460`; `empty_subject_receipt_count=12`; three replacement counts = 0 |
| Exit 0 | those counts hold |
| Exit 2 | any replacement, guessed argv, or missing binding |
| Checkpoint | `X3.json` stores `N_bound_jobs` |
| Forbidden | scientific intent; hard-coded 460 jobs |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
import scripts.p3_v3.evidence as evidence_module


def test_freeze_profiling_inventory_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "freeze-profiling-inventory" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_freeze_profiling_inventory_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register the command. The handler compiles 460 rows through
`build_profiling_execution_plan` and writes the inventory. It does not
call `create_intent`.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): register profiling inventory freeze command" -m "Report bound and preclosed counts that partition 460. Write no confirmatory intent."
```

### Task X4: Execute N_bound_jobs

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  execute-bound-profiling \
  --inventory data/p3_v3/phase2/profiling-execution-inventory.json \
  --authorization data/p3_v3/phase2/scientific-profiling.json \
  --checkpoint data/p3_v3/phase2/checkpoints/X4.json \
  --ledger data/p3_v3/phase2/profiling-ledger.jsonl
```

| Field | Rule |
|---|---|
| Inputs | scientific-profiling record; X3 inventory SHA-256 |
| Counts | `expected_job_count == inventory["bound_job_count"]`; never 460 unless that happens to equal `N_bound_jobs` |
| Exit 0 | every bound job has a terminal result |
| Exit 2 | preclosed row executed, fake intent, or expected jobs hard-coded to 460 when `N_bound_jobs != 460` |
| Checkpoint | `X4.json` |
| Resume | FAILED bound jobs only; do not recreate CLOSED jobs |
| Forbidden | executing preclosed rows; `/usr/bin/true` production argv |

This is the first node allowed to call `create_intent`, and only for
bound jobs.

- [ ] **Step 1: Write the failing expected-count test**

```python
import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.phase2_authorization import expected_bound_job_count


def test_expected_jobs_follow_bound_count_not_460() -> None:
    assert expected_bound_job_count({"bound_job_count": 8, "total_rows": 460}) == 8
    with pytest.raises(EvidenceError, match="E_PHASE2_AUTH"):
        expected_bound_job_count({"bound_job_count": 460, "total_rows": 459})
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_expected_jobs_follow_bound_count_not_460 -q
```

Expected: FAIL because `expected_bound_job_count` is absent.

- [ ] **Step 3: Minimal implementation**

```python
def expected_bound_job_count(inventory):
    bound = inventory["bound_job_count"]
    total = inventory["total_rows"]
    preclosed = inventory["preclosed_row_count"]
    if total != 460 or bound + preclosed != 460:
        raise EvidenceError("E_PHASE2_AUTH", "inventory does not partition 460")
    return bound
```

Register `execute-bound-profiling`. The handler calls
`require_scientific_profiling` then `create_intent` once per bound
job.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/phase2_authorization.py scripts/p3_v3/evidence.py \
  tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): execute only bound profiling jobs" -m "X4 expected count is N_bound_jobs. Preclosed rows stay unexecuted."
```

### Task X5: Ledger validation

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  validate-profiling-ledger \
  --ledger data/p3_v3/phase2/profiling-ledger.jsonl \
  --inventory data/p3_v3/phase2/profiling-execution-inventory.json \
  --checkpoint data/p3_v3/phase2/checkpoints/X5.json
```

| Field | Rule |
|---|---|
| Inputs | X4 CLOSED; ledger SHA-256; inventory SHA-256 |
| Counts | intent/result pairs == `N_bound_jobs` terminal jobs; attempt count may be larger |
| Exit 0 | `verify_ledger` succeeds and job IDs match bound jobs |
| Exit 2 | extra, missing, or preclosed job ID |
| Checkpoint | `X5.json` |
| Resume / duplicate | same as X1 |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
import scripts.p3_v3.evidence as evidence_module


def test_validate_profiling_ledger_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "validate-profiling-ledger" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_validate_profiling_ledger_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register the command. Call `verify_ledger` and compare job IDs to
`inventory["bound_job_ids"]`.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): validate the bound profiling ledger" -m "Keep attempt counts separate from the bound job inventory."
```

### Task X6: Receipt reduction

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  reduce-profiling-receipts \
  --inventory data/p3_v3/phase2/profiling-execution-inventory.json \
  --ledger data/p3_v3/phase2/profiling-ledger.jsonl \
  --trace-root data/p3_v3/phase2/traces \
  --checkpoint data/p3_v3/phase2/checkpoints/X6.json \
  --output data/p3_v3/phase2/profiling-receipts
```

| Field | Rule |
|---|---|
| Inputs | X5 CLOSED; runner manifest SHA-256; frozen sites |
| Counts | one receipt row per selected `behavior_id`; 460 IDs across 35 subjects |
| Exit 0 | reducer covers every selected ID once |
| Exit 2 | success-only subset, hash mismatch, extra ID |
| Checkpoint | `X6.json` |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
import scripts.p3_v3.evidence as evidence_module


def test_reduce_profiling_receipts_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "reduce-profiling-receipts" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_reduce_profiling_receipts_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register the command. Call `build_profiling_receipt_from_attempts`.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): reduce profiling attempts into receipts" -m "Cover every selected behavior_id once, including preclosed rows."
```

### Task X7: 35-subject rebind

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  rebind-derived-subjects \
  --derived-root data/p3_v3/derived \
  --receipt-root data/p3_v3/phase2/profiling-receipts \
  --checkpoint data/p3_v3/phase2/checkpoints/X7.json
```

| Field | Rule |
|---|---|
| Inputs | X6 receipts; frozen derived subjects |
| Counts | 35 rebound subjects; 12 empty workload receipts retained |
| Exit 0 | no rediscovery; workload bytes unchanged |
| Exit 2 | discovery import or workload mutation |
| Checkpoint | `X7.json` |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
import scripts.p3_v3.evidence as evidence_module


def test_rebind_derived_subjects_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "rebind-derived-subjects" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_rebind_derived_subjects_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register the command. Call `rebind_derived_subject_after_profiling`
once per subject.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): rebind derived subjects from profiling receipts" -m "Replace only profiling_results and technique_profile."
```

### Task X8: Cohorts

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  rebuild-frames-from-derived \
  --bridge data/p3_v3/bridge/bridge.json \
  --derived-root data/p3_v3/derived \
  --checkpoint data/p3_v3/phase2/checkpoints/X8.json \
  --output data/p3_v3/frames/subject-frames.json
```

| Field | Rule |
|---|---|
| Inputs | X7 rebound derived subjects; frozen bridge |
| Counts | `C_CONSTRUCT` and `C_CRITERION` keep separate denominators |
| Exit 0 | `c_criterion` equals unique eligible IDs |
| Exit 2 | `A or B` union or rediscovery |
| Checkpoint | `X8.json` |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
import scripts.p3_v3.evidence as evidence_module


def test_rebuild_frames_from_derived_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "rebuild-frames-from-derived" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_rebuild_frames_from_derived_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register the command. Call `rebuild_frames_from_derived`.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): rebuild subject frames from rebound derived subjects" -m "Keep C_CRITERION equal to the unique eligible IDs."
```

### Task X9: 350 slot and contract close

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  close-phase2-slots \
  --frames data/p3_v3/frames/subject-frames.json \
  --sites-root data/p3_v3/sites \
  --docs-root data/p3_v3/phase2/materialized \
  --checkpoint data/p3_v3/phase2/checkpoints/X9.json \
  --output data/p3_v3/phase2/slots
```

| Field | Rule |
|---|---|
| Inputs | X8 frames; frozen sites; mounted public docs |
| Counts | 350 slots; contracts only for applicable slots |
| Exit 0 | every slot closed; contracts extracted |
| Exit 2 | `PHASE2_CONTRACT_AUTHORITY_BLOCKED` or dummy contract |
| Checkpoint | `X9.json` |
| Note | current in-repo materials lack the 35 archives, so production X9 is expected to BLOCK until mount and extraction succeed |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
import scripts.p3_v3.evidence as evidence_module


def test_close_phase2_slots_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "close-phase2-slots" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_close_phase2_slots_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register the command. Call `build_contract_authority` and
`close_subject_slots`. Propagate
`PHASE2_CONTRACT_AUTHORITY_BLOCKED` as exit 2.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): close 350 slots from contract authority" -m "Stop on PHASE2_CONTRACT_AUTHORITY_BLOCKED. Do not invent dummy contracts."
```

### Task X10: Package A

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  build-phase2-package-a \
  --source-root data/p3_v3/phase2/package-a-src \
  --checkpoint data/p3_v3/phase2/checkpoints/X10.json \
  --output data/p3_v3/phase2/package-a
```

| Field | Rule |
|---|---|
| Inputs | X9 slot/contract artifacts; public frames |
| Counts | proposer view leak count = 0 |
| Exit 0 | `collect_package_leaks == []` |
| Exit 2 | `E_PACKAGE_LEAK` |
| Checkpoint | `X10.json` |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
import scripts.p3_v3.evidence as evidence_module


def test_build_phase2_package_a_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "build-phase2-package-a" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_build_phase2_package_a_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register the command. Call `build_phase2_package_a` and
`materialize_package` with `PROPOSER_ALLOWED_CLASSES`.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): build Phase 2 Package A" -m "Reject proposer leaks with E_PACKAGE_LEAK."
```

### Task X11: Shuffle

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  shuffle-phase2-package-a \
  --first-root data/p3_v3/phase2/package-a \
  --second-root data/p3_v3/phase2/package-a-shuffle \
  --checkpoint data/p3_v3/phase2/checkpoints/X11.json
```

| Field | Rule |
|---|---|
| Inputs | two output trees, not one `output_files` map |
| Counts | file-to-file SHA-256 identity |
| Exit 0 | `shuffle_byte_identical is True` |
| Exit 2 | directory hashed as a file, or trees differ |
| Checkpoint | `X11.json` |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
import scripts.p3_v3.evidence as evidence_module


def test_shuffle_phase2_package_a_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "shuffle-phase2-package-a" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_shuffle_phase2_package_a_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register the command. Rebuild Package A into `second-root` and compare
file trees.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py
rtk git commit -m "feat(p3-v3): prove Package A shuffle identity on two trees" -m "Hash files only. Do not treat a directory as a file digest."
```

### Task X12: Close and independent final review packet

Exact command:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  close-phase2-production \
  --phase PHASE_1 \
  --ledger data/p3_v3/phase2/profiling-ledger.jsonl \
  --first-root data/p3_v3/phase2/package-a \
  --second-root data/p3_v3/phase2/package-a-shuffle \
  --checkpoint data/p3_v3/phase2/checkpoints/X12.json \
  --output data/p3_v3/phase2/phase2-close.json
```

| Field | Rule |
|---|---|
| Inputs | X11 trees; X4 ledger; protocol SHA-256 |
| Counts | `expected_job_count == N_bound_jobs`; `attempt_count` may be larger; `terminal_result_count` is distinct terminal jobs |
| Exit 0 | shuffle identity and counts hold |
| Exit 2 | `"pending"` manifest hash or job/attempt confusion |
| Checkpoint | `X12.json` |
| After close | write `docs/review_20260815/phase2_final_packet.md`, commit, stop as `PHASE2_FINAL_REVIEW_CANDIDATE`. Executor must not write PASS. |

- [ ] **Step 1: Write the failing CLI wiring test**

```python
import scripts.p3_v3.evidence as evidence_module


def test_close_phase2_production_command_is_registered() -> None:
    parser = evidence_module.build_parser()
    action = parser._subparsers._group_actions[0]
    assert "close-phase2-production" in action.choices
```

- [ ] **Step 2: Run the test and confirm it fails**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_authorization.py::test_close_phase2_production_command_is_registered -q
```

Expected: FAIL because the command is absent.

- [ ] **Step 3: Minimal implementation**

Register the command. Call `close_phase2_production`. Write the final
review packet. Do not write a verdict.

- [ ] **Step 4: Re-run the test and confirm it passes**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_phase2_authorization.py \
  docs/review_20260815/phase2_final_packet.md
rtk git commit -m "feat(p3-v3): close Phase 2 production and emit final review packet" -m "Stop for independent Sol High review. Do not author PASS."
```

Need `build_parser` to exist. If `evidence.py` currently builds the
parser inside `main`, add:

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evidence")
    sub = parser.add_subparsers(dest="command", required=True)
    # existing add_parser calls move here
    return parser
```

and keep current commands. New Phase 2 commands are added in the
tasks above.

---

## Acceptance

1. Production-preparation and scientific-profiling are different
   records and different user sentences.
2. X1–X3 cannot create confirmatory intents.
3. X4 expected jobs equal `N_bound_jobs`.
4. Checkpoints refuse duplicate starts and resume FAILED only.
5. X9 may legally stop as `PHASE2_CONTRACT_AUTHORITY_BLOCKED`.
6. Final review packet is not a PASS verdict.
