# P3 Phase 2 Profiling Capability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the frozen 460-row Profiling Workload into bound jobs
and preclosed rows, execute only bound Python recipes under CPython
`sys.setprofile`, and reduce every selected `behavior_id` into a
`p3-profiling-results-v1` receipt.

**Architecture:** Execution plans consume a `SourceArchiveBinding` plus
the public-frame row behind each selected `behavior_id`. Native
strategies are registered and fail closed because no native tracer is
available in the authorized environment. The reducer, not Task D,
constructs the profiling receipt.

**Tech Stack:** Python 3.12 stdlib only for the tracer; no extra
packages; no root; no network.

## Global Constraints

Master-plan Global Constraints apply. Additional rules:

```text
N_total_rows = 460
N_bound_jobs = count(status == EXECUTION_PLAN_BOUND)
N_preclosed_rows = 460 - N_bound_jobs
```

Only `N_bound_jobs` receive scientific intents. Do not execute a
no-op, create a fake intent, or replace a preclosed row.

---

## File map

| File | Responsibility |
|---|---|
| `src/p3_v3/profiling_execution_plan.py` | 460-row compiler |
| `src/p3_v3/profiling_strategies.py` | strategy registry |
| `src/p3_v3/profiling_trace.py` | CPython `sys.setprofile` tracer |
| `src/p3_v3/profiling_streams.py` | stdout/stderr hashing |
| `src/p3_v3/profiling_terminals.py` | job terminal mapping |
| `src/p3_v3/profiling_runner.py` | intent-then-exec |
| `src/p3_v3/profiling_runner_manifest.py` | four-file manifest |
| `src/p3_v3/profiling_receipt.py` | attempt → receipt reducer |
| `src/p3_v3/phase2_cohorts.py` | rebind and C_CRITERION |
| `src/p3_v3/run_records.py` | `PROFILING_WORKLOAD` role class |
| `tests/p3_v3/test_phase2_execution_plan.py` | C0 |
| `tests/p3_v3/test_phase2_profiling_runner.py` | C1 |
| `tests/p3_v3/test_phase2_cross_role_inputs.py` | C1 |
| `tests/p3_v3/test_phase2_receipt.py` | reducer |
| `tests/p3_v3/test_phase2_reducer.py` | rebind |
| `tests/p3_v3/test_phase2_cohorts.py` | cohorts |

---

## Tracer decision

This is a decision, not a later choice.

### Defined tracer: `P3_CPYTHON_SETPROFILE_V1`

| Field | Value |
|---|---|
| Tool | CPython `sys.setprofile` |
| Implementation | `src/p3_v3/profiling_trace.py` |
| Version | the preflight `expected_python` string, currently 3.12 |
| Offline | yes, stdlib |
| Root / entitlement / network | no |
| Exact command | in-process: `sys.setprofile(hook)` around the bound Python callable or `runpy` invocation |
| Supported OS | any OS that already runs the Phase 2 preflight CPython |
| Build-flag effect | none |
| Raw output | canonical JSON bytes of `list[ProfilingTraceEvent]` |
| Timeout | the job `timeout_seconds` |
| Parser | identity; events are already normalized |
| Failure codes | `E_TRACE_PROFILE_HOOK`, `E_TRACE_RAW_BYTES` |
| Reproducibility | event sequence is recorded without timestamps; same argv and source tree must reproduce the same event identities after normalization |

```python
from typing import Literal, TypedDict

class ProfilingTraceEvent(TypedDict):
    sequence: int
    module: str
    symbol: str
    call_kind: Literal[
        "PYTHON_CALL",
        "FUNCTION_CALL",
        "METHOD_CALL",
        "NATIVE_CALL",
        "FFI_CALL",
        "PROCESS_SPAWN",
    ]
    argument_types: list[str]
    keyword_names: list[str]
```

`call_trace.raw` is `canonical_json_bytes(events)`.
`file_sha256(call_trace.raw)` must equal receipt `call_trace_sha256`.

`observed_site_ids` come only from exact
`(event.module, event.symbol) == (site.path_as_module, site.symbol)`
or exact `(event.symbol, event.module) == (site.symbol, site.path)`.
No fuzzy match. If no exact pair exists, the list stays empty.

### Strategies that fail closed: tracer unavailable

These strategies are registered so the compiler can name them. They
must not execute and must not assume a future native tracer.

| strategy_id | accepted adapter | reason |
|---|---|---|
| `CMAKE_CTEST_NAME_V1` | `CMAKE_CTEST_V1` | exact `ctest:` name exists, but no proven native tracer |
| `CMAKE_TARGET_V1` | `CMAKE_CTEST_V1` | target name is not a CTest name and no native tracer |
| `MESON_TEST_NAME_V1` | `MESON_TEST_V1` | Meson test name exists, no native tracer |
| `AUTOTOOLS_MAKECHECK_NAME_V1` | `AUTOTOOLS_MAKECHECK_V1` | TESTS target exists, no native tracer |
| `HEADER_SURFACE_V1` | cmake/meson/autotools | `header:` rows have no executable recipe |
| `SOURCE_PATH_V1` | cmake/meson/autotools | `example:` / `benchmark:` / `project_test:` path rows have no executable recipe |

Fail-closed code for those rows: `E_TRACER_UNAVAILABLE` or
`E_EXECUTABLE_RECIPE_ABSENT`.

Observed frozen prefix counts imply most of the 460 rows preclose.
That is the estimand, not a defect to paper over.

---

## Strategy registry entry

```python
class ExecutionStrategy(TypedDict):
    strategy_id: str
    accepted_adapter: str
    accepted_invocation_kinds: list[str]
    required_frozen_fields: list[str]
    argv_algorithm_id: str
    cwd_algorithm_id: str
    build_prerequisites: list[str]
    input_binding_rule: str
    timeout_policy: str
    tracer_id: str
    implementation_path: str
    implementation_source_sha256: str
    fail_closed_codes: list[str]
```

Bindable Python strategies:

| strategy_id | required frozen fields | argv algorithm |
|---|---|---|
| `PYTHON_PUBLIC_API_V1` | `entrypoint` matching `module:qualname`, adapter Python or meson-python | in-process call of that qualname under `sys.setprofile` |
| `PYTHON_CLI_V1` | `normalized_entrypoint` starting `cli:`, frozen console-script name | `python -c` console-script replica from `[project.scripts]` recipe stored on the frame row `declared_inputs.argv_tokens` after join |
| `PYTHON_FILE_V1` | provenance path ending `.py` plus frozen input recipe | `python <path>` plus frozen tokens |

Join rule: selected row `behavior_id` → public-frame row with the same
`behavior_id`. The selected row itself has no argv. Do not guess a
CTest name from a header or source path.

`build_profiling_execution_plan` signature:

```python
def build_profiling_execution_plan(
    selected_row: Mapping[str, object],
    workload: Mapping[str, object],
    derived_subject: Mapping[str, object],
    adapter_registry: Mapping[str, object],
    source_binding: SourceArchiveBinding,
    public_frame_row: Mapping[str, object],
    strategy_registry: Mapping[str, ExecutionStrategy],
) -> dict:
    """Bind one row or write a prescribed preclosure."""
```

---

### Task C0: Execution-plan compiler

**Files:**
- Create: `src/p3_v3/profiling_execution_plan.py`
- Create: `src/p3_v3/profiling_strategies.py`
- Test: `tests/p3_v3/test_phase2_execution_plan.py`

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256
from p3_v3.profiling_execution_plan import build_profiling_execution_plan
from p3_v3.profiling_strategies import STRATEGY_REGISTRY


def source_binding() -> dict:
    return {
        "neutral_snapshot_id": "aa" * 32,
        "controlled_subject_source_id": "bb" * 32,
        "archive_relative_path": "archives/00.tar",
        "archive_sha256": "cc" * 32,
        "descriptor_relative_path": "archives/00.descriptor.json",
        "descriptor_sha256": "dd" * 32,
        "normalized_source_tree_sha256": "ee" * 32,
        "build_descriptor_sha256": "ff" * 32,
        "extraction_policy_id": "P3-SAFE-TAR-V1",
        "materialized_root_identity": "11" * 32,
    }


def cmake_header_row() -> dict:
    return {
        "behavior_id": "22" * 32,
        "category": "PUBLIC_API",
        "declared_input_schema_sha256": "33" * 32,
        "diversity_signature_sha256": "44" * 32,
        "entrypoint": "include/demo.h",
        "normalized_entrypoint": "header:include/demo.h",
        "provenance_path": "include/demo.h",
        "provenance_span_or_key": "path",
        "static_dependency_tags": [],
    }


def cmake_header_frame_row() -> dict:
    row = cmake_header_row()
    return {
        **row,
        "declared_inputs": {"header": "include/demo.h"},
        "adapter_id": "CMAKE_CTEST_V1",
        "prerequisites": [],
    }


def python_api_row() -> dict:
    return {
        "behavior_id": "55" * 32,
        "category": "PUBLIC_API",
        "declared_input_schema_sha256": "66" * 32,
        "diversity_signature_sha256": "77" * 32,
        "entrypoint": "pkg.mod:func",
        "normalized_entrypoint": "pkg.mod:func",
        "provenance_path": "src/pkg/mod.py",
        "provenance_span_or_key": "L1",
        "static_dependency_tags": [],
    }


def python_api_frame_row() -> dict:
    row = python_api_row()
    return {
        **row,
        "declared_inputs": {"argv_tokens": []},
        "adapter_id": "PYTHON_PEP517_V1",
        "prerequisites": [],
    }


def workload_for(row: dict) -> dict:
    body = {
        "schema_version": "p3-profiling-workload-v1",
        "controlled_subject_source_id": "bb" * 32,
        "scale_class": "L",
        "budget": 20,
        "category_order": ["PUBLIC_API"],
        "selected_rows": [row],
        "selected_behavior_ids": [row["behavior_id"]],
        "selected_category_counts": {"PUBLIC_API": 1},
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def test_cmake_header_row_is_preclosed() -> None:
    plan = build_profiling_execution_plan(
        cmake_header_row(),
        workload_for(cmake_header_row()),
        {"adapter_discovery": {"adapter_id": "CMAKE_CTEST_V1"}},
        {"adapters": []},
        source_binding(),
        cmake_header_frame_row(),
        STRATEGY_REGISTRY,
    )
    assert plan["status"] != "EXECUTION_PLAN_BOUND"
    assert plan["argv"] == []
    assert plan["failure_code"] in {
        "E_EXECUTABLE_RECIPE_ABSENT",
        "E_TRACER_UNAVAILABLE",
    }


def test_python_public_api_can_bind() -> None:
    plan = build_profiling_execution_plan(
        python_api_row(),
        workload_for(python_api_row()),
        {"adapter_discovery": {"adapter_id": "PYTHON_PEP517_V1"}},
        {"adapters": []},
        source_binding(),
        python_api_frame_row(),
        STRATEGY_REGISTRY,
    )
    assert plan["status"] == "EXECUTION_PLAN_BOUND"
    assert plan["tracer_id"] == "P3_CPYTHON_SETPROFILE_V1"
    assert "/usr/bin/true" not in plan["argv"]


def cmake_source_path_row() -> dict:
    return {
        "behavior_id": "88" * 32,
        "category": "EXAMPLE",
        "declared_input_schema_sha256": "99" * 32,
        "diversity_signature_sha256": "aa" * 32,
        "entrypoint": "examples/demo.cpp",
        "normalized_entrypoint": "example:examples/demo.cpp",
        "provenance_path": "examples/demo.cpp",
        "provenance_span_or_key": "path",
        "static_dependency_tags": [],
    }


def cmake_source_path_frame_row() -> dict:
    row = cmake_source_path_row()
    return {
        **row,
        "declared_inputs": {"source_path": "examples/demo.cpp"},
        "adapter_id": "CMAKE_CTEST_V1",
        "prerequisites": [],
    }


def test_cmake_source_path_row_is_preclosed() -> None:
    plan = build_profiling_execution_plan(
        cmake_source_path_row(),
        workload_for(cmake_source_path_row()),
        {"adapter_discovery": {"adapter_id": "CMAKE_CTEST_V1"}},
        {"adapters": []},
        source_binding(),
        cmake_source_path_frame_row(),
        STRATEGY_REGISTRY,
    )
    assert plan["status"] != "EXECUTION_PLAN_BOUND"
    assert plan["argv"] == []
    assert plan["failure_code"] in {
        "E_EXECUTABLE_RECIPE_ABSENT",
        "E_TRACER_UNAVAILABLE",
    }
```

The CMake header and `source_path` fixtures are frozen row shapes.
Do not test only synthetic Python.

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_execution_plan.py -q
```

Expected: FAIL because the compiler is absent.

- [ ] **Step 3: Minimal implementation**

Classify the joined frame row:

1. `normalized_entrypoint` starts with `header:` → preclose
   `E_EXECUTABLE_RECIPE_ABSENT`.
2. `declared_inputs` has `source_path` and no argv recipe → preclose
   `E_EXECUTABLE_RECIPE_ABSENT`.
3. `normalized_entrypoint` starts with `ctest:`, `target:`,
   `meson-test:`, or autotools TESTS → preclose `E_TRACER_UNAVAILABLE`.
4. `entrypoint` matches `module:qualname` and adapter is Python or
   meson-python → bind `PYTHON_PUBLIC_API_V1`.
5. `normalized_entrypoint` starts with `cli:` → bind `PYTHON_CLI_V1`
   using frozen `declared_inputs.argv_tokens`.
6. Otherwise preclose `E_EXECUTION_STRATEGY_UNSUPPORTED`.

Reject `/usr/bin/true` and `/usr/bin/false` in production argv.

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/profiling_execution_plan.py \
  src/p3_v3/profiling_strategies.py \
  tests/p3_v3/test_phase2_execution_plan.py
rtk git commit -m "feat(p3-v3): compile bound and preclosed profiling rows" -m "Fail-close header, source-path, and native rows. Bind only Python recipes."
```

### Task C1: Runner, identity, and traces

**Files:**
- Create: `src/p3_v3/profiling_runner.py`
- Create: `src/p3_v3/profiling_trace.py`
- Create: `src/p3_v3/profiling_streams.py`
- Create: `src/p3_v3/profiling_terminals.py`
- Create: `src/p3_v3/profiling_runner_manifest.py`
- Modify: `src/p3_v3/run_records.py`
- Test: `tests/p3_v3/test_phase2_profiling_runner.py`
- Test: `tests/p3_v3/test_phase2_cross_role_inputs.py`

**Interfaces:**

```python
from subprocess import CompletedProcess
from typing import Protocol


class ProfilingExecutor(Protocol):
    def __call__(
        self,
        argv: list[str],
        cwd: str,
        timeout: int,
    ) -> CompletedProcess[bytes]:
        raise NotImplementedError("ProfilingExecutor protocol")


def execute_profiling_attempt(
    attempt_dir: Path,
    intent: Mapping[str, object],
    plan: Mapping[str, object],
    executor: ProfilingExecutor,
) -> dict:
    """Write intent, fsync, exec, persist call_trace.raw, write result."""
```

Intent fields: `phase="PHASE_1"`, `job_role="PROFILING"`,
`object_type="PROFILING_BEHAVIOR"`, `object_id=behavior_id`,
`evaluation_input_class="PROFILING_WORKLOAD"`,
`evaluation_input_id=workload_row_sha256`, `mr_id="PROFILING_NO_MR"`.

`/usr/bin/true` is legal only when
`intent["environment_id"]=="P3-TERMINAL-MAP-TEST-v1"`.

- [ ] **Step 1: Write the failing tests**

```python
import subprocess
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.profiling_runner import execute_profiling_attempt
from p3_v3.profiling_runner_manifest import build_profiling_runner_manifest
from p3_v3.run_records import _validate_intent


def literal_profiling_intent(job_id: str = "job-1") -> dict:
    return {
        "job_id": job_id,
        "protocol_sha256": "aa" * 32,
        "phase": "PHASE_1",
        "argv": ["/opt/anaconda3/bin/python", "-c", "print(1)"],
        "cwd_identity": "fixture",
        "environment_sha256": "bb" * 32,
        "input_sha256": ["cc" * 32],
        "seed": None,
        "timeout_seconds": 5,
        "attempt": 1,
        "object_type": "PROFILING_BEHAVIOR",
        "object_id": "55" * 32,
        "mr_id": "PROFILING_NO_MR",
        "evaluation_input_class": "PROFILING_WORKLOAD",
        "evaluation_input_id": "66" * 32,
        "repetition_id": 1,
        "environment_id": "env-1",
        "job_role": "PROFILING",
    }


def bound_plan() -> dict:
    return {
        "status": "EXECUTION_PLAN_BOUND",
        "argv": ["/opt/anaconda3/bin/python", "-c", "print(1)"],
        "tracer_id": "P3_CPYTHON_SETPROFILE_V1",
        "behavior_id": "55" * 32,
    }


def test_runner_writes_intent_before_side_effect(tmp_path: Path) -> None:
    seen = []

    def executor(argv, cwd, timeout):
        seen.append((tmp_path / "jobs/job-1/1/intent.json").exists())
        return subprocess.CompletedProcess(argv, 0, b"1\n", b"")

    execute_profiling_attempt(
        tmp_path / "jobs/job-1/1",
        literal_profiling_intent(),
        bound_plan(),
        executor,
    )
    assert seen == [True]
    assert (tmp_path / "jobs/job-1/1/call_trace.raw").is_file()


def test_profiling_intent_rejects_e_common() -> None:
    intent = literal_profiling_intent()
    intent["evaluation_input_class"] = "E_COMMON"
    with pytest.raises(EvidenceError, match="E_JOB_ROLE_INPUT"):
        _validate_intent(intent)


def test_p12_intent_rejects_profiling_workload() -> None:
    intent = literal_profiling_intent()
    intent["job_role"] = "P12"
    intent["phase"] = "PHASE_7"
    intent["evaluation_input_class"] = "PROFILING_WORKLOAD"
    intent["object_type"] = "SEMANTIC_MUTANT"
    intent["mr_id"] = "mr-1"
    with pytest.raises(EvidenceError, match="E_JOB_ROLE_INPUT"):
        _validate_intent(intent)


def test_runner_manifest_excludes_bridge_helper() -> None:
    manifest = build_profiling_runner_manifest(Path("."))
    paths = {entry["path"] for entry in manifest["files"]}
    assert paths == {
        "src/p3_v3/profiling_runner.py",
        "src/p3_v3/profiling_trace.py",
        "src/p3_v3/profiling_streams.py",
        "src/p3_v3/profiling_terminals.py",
    }
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_profiling_runner.py \
  tests/p3_v3/test_phase2_cross_role_inputs.py -q
```

Expected: FAIL because the runner or the role class is absent.

- [ ] **Step 3: Minimal implementation**

Install `sys.setprofile` in `profiling_trace.py`. Persist canonical
JSON events. Change `_ROLE_REQUIRED_INPUT_CLASS["PROFILING"]` to
`PROFILING_WORKLOAD` if V-FINAL has not already done so. Update
existing tests that still expect `file_sha256(bridge_and_frames.py)`
as the runner digest.

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/profiling_runner.py src/p3_v3/profiling_trace.py \
  src/p3_v3/profiling_streams.py src/p3_v3/profiling_terminals.py \
  src/p3_v3/profiling_runner_manifest.py src/p3_v3/run_records.py \
  tests/p3_v3/test_phase2_profiling_runner.py \
  tests/p3_v3/test_phase2_cross_role_inputs.py
rtk git commit -m "feat(p3-v3): execute bound profiling jobs under sys.setprofile" -m "Persist canonical trace bytes and reject E_COMMON on profiling intents."
```

### Task R1: Attempt → profiling receipt reducer

**Files:**
- Create: `src/p3_v3/profiling_receipt.py`
- Test: `tests/p3_v3/test_phase2_receipt.py`

**Interfaces:**

```python
def build_profiling_receipt_from_attempts(
    workload: Mapping[str, object],
    execution_inventory: Mapping[str, object],
    terminal_attempts: Sequence[Mapping[str, object]],
    preclosed_rows: Sequence[Mapping[str, object]],
    raw_trace_root: Path,
    runner_manifest: Mapping[str, object],
    frozen_sites: Sequence[Mapping[str, object]],
) -> dict:
    """Cover every selected behavior_id exactly once."""
```

Terminal mapping:

| attempt / plan | receipt status |
|---|---|
| bound PASS + valid nonempty trace | `SUCCESS` |
| timeout | `TIMEOUT` |
| PASS but trace absent or hash mismatch | `MISSING_TRACE` |
| `FAIL_SCIENTIFIC` | `FAILURE` |
| exhausted `FAIL_INFRASTRUCTURE` | `ADAPTER_UNCERTAIN` |
| `INCONCLUSIVE` | `ADAPTER_UNCERTAIN` |
| `MISSING_WITH_REASON` | `ADAPTER_UNCERTAIN` |
| preclosed execution binding | `ADAPTER_UNCERTAIN` |

Unsuccessful rows have `call_trace=[]`. Raw attempt bytes stay in the
attempt ledger.

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_json_bytes, canonical_sha256
from p3_v3.profiling_receipt import build_profiling_receipt_from_attempts


def _workload(behavior_ids: list[str]) -> dict:
    rows = [{"behavior_id": item, "category": "PUBLIC_API"} for item in behavior_ids]
    body = {
        "schema_version": "p3-profiling-workload-v1",
        "controlled_subject_source_id": "bb" * 32,
        "selected_rows": rows,
        "selected_behavior_ids": behavior_ids,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def test_reducer_rejects_missing_behavior(tmp_path: Path) -> None:
    ids = [f"{index:064x}" for index in range(460)]
    workload = _workload(ids)
    with pytest.raises(EvidenceError, match="E_PROFILE_RECEIPT"):
        build_profiling_receipt_from_attempts(
            workload,
            {"plans": []},
            [],
            [],
            tmp_path,
            {"artifact_sha256": "aa" * 32},
            [],
        )


def test_reducer_maps_preclosed_to_uncertain(tmp_path: Path) -> None:
    behavior_id = "22" * 32
    workload = _workload([behavior_id])
    receipt = build_profiling_receipt_from_attempts(
        workload,
        {"plans": [{"behavior_id": behavior_id, "status": "EXECUTION_PLAN_FAIL_CLOSED"}]},
        [],
        [{
            "behavior_id": behavior_id,
            "status": "ADAPTER_UNCERTAIN",
            "failure_code": "E_EXECUTABLE_RECIPE_ABSENT",
        }],
        tmp_path,
        {"artifact_sha256": "aa" * 32},
        [],
    )
    assert receipt["results"][0]["behavior_id"] == behavior_id
    assert receipt["results"][0]["status"] == "ADAPTER_UNCERTAIN"
    assert receipt["results"][0]["call_trace"] == []


def test_reducer_covers_exactly_460_preclosed_ids(tmp_path: Path) -> None:
    ids = [f"{index:064x}" for index in range(460)]
    workload = _workload(ids)
    preclosed = [
        {
            "behavior_id": item,
            "status": "ADAPTER_UNCERTAIN",
            "failure_code": "E_EXECUTABLE_RECIPE_ABSENT",
        }
        for item in ids
    ]
    receipt = build_profiling_receipt_from_attempts(
        workload,
        {"plans": [{"behavior_id": item, "status": "EXECUTION_PLAN_FAIL_CLOSED"} for item in ids]},
        [],
        preclosed,
        tmp_path,
        {"artifact_sha256": "aa" * 32},
        [],
    )
    observed = [row["behavior_id"] for row in receipt["results"]]
    assert observed == ids
    assert all(row["status"] == "ADAPTER_UNCERTAIN" for row in receipt["results"])
    assert all(row["call_trace"] == [] for row in receipt["results"])


def test_reducer_rejects_duplicate_or_extra_row(tmp_path: Path) -> None:
    behavior_id = "22" * 32
    extra = "33" * 32
    workload = _workload([behavior_id])
    with pytest.raises(EvidenceError, match="E_PROFILE_RECEIPT"):
        build_profiling_receipt_from_attempts(
            workload,
            {"plans": []},
            [],
            [
                {"behavior_id": behavior_id, "status": "ADAPTER_UNCERTAIN", "failure_code": "E_EXECUTABLE_RECIPE_ABSENT"},
                {"behavior_id": behavior_id, "status": "ADAPTER_UNCERTAIN", "failure_code": "E_EXECUTABLE_RECIPE_ABSENT"},
            ],
            tmp_path,
            {"artifact_sha256": "aa" * 32},
            [],
        )
    with pytest.raises(EvidenceError, match="E_PROFILE_RECEIPT"):
        build_profiling_receipt_from_attempts(
            workload,
            {"plans": []},
            [],
            [
                {"behavior_id": behavior_id, "status": "ADAPTER_UNCERTAIN", "failure_code": "E_EXECUTABLE_RECIPE_ABSENT"},
                {"behavior_id": extra, "status": "ADAPTER_UNCERTAIN", "failure_code": "E_EXECUTABLE_RECIPE_ABSENT"},
            ],
            tmp_path,
            {"artifact_sha256": "aa" * 32},
            [],
        )


def test_reducer_rejects_raw_hash_mismatch(tmp_path: Path) -> None:
    behavior_id = "22" * 32
    workload = _workload([behavior_id])
    raw = tmp_path / behavior_id / "call_trace.raw"
    raw.parent.mkdir(parents=True)
    events = [{
        "sequence": 0,
        "module": "pkg.mod",
        "symbol": "func",
        "call_kind": "PYTHON_CALL",
        "argument_types": ["int"],
        "keyword_names": [],
    }]
    raw.write_bytes(canonical_json_bytes(events))
    with pytest.raises(EvidenceError, match="E_PROFILE_RECEIPT"):
        build_profiling_receipt_from_attempts(
            workload,
            {"plans": [{"behavior_id": behavior_id, "status": "EXECUTION_PLAN_BOUND"}]},
            [{
                "behavior_id": behavior_id,
                "status": "PASS",
                "call_trace_sha256": "00" * 32,
                "attempt": 1,
            }],
            [],
            tmp_path,
            {"artifact_sha256": "aa" * 32},
            [],
        )


def test_reducer_rejects_runner_manifest_mismatch(tmp_path: Path) -> None:
    behavior_id = "22" * 32
    workload = _workload([behavior_id])
    with pytest.raises(EvidenceError, match="E_PROFILE_RECEIPT"):
        build_profiling_receipt_from_attempts(
            workload,
            {
                "plans": [{"behavior_id": behavior_id, "status": "EXECUTION_PLAN_FAIL_CLOSED"}],
                "runner_manifest_sha256": "ff" * 32,
            },
            [],
            [{
                "behavior_id": behavior_id,
                "status": "ADAPTER_UNCERTAIN",
                "failure_code": "E_EXECUTABLE_RECIPE_ABSENT",
            }],
            tmp_path,
            {"artifact_sha256": "aa" * 32},
            [],
        )


def test_reducer_maps_exhausted_infrastructure_to_uncertain(tmp_path: Path) -> None:
    behavior_id = "22" * 32
    workload = _workload([behavior_id])
    receipt = build_profiling_receipt_from_attempts(
        workload,
        {"plans": [{"behavior_id": behavior_id, "status": "EXECUTION_PLAN_BOUND"}]},
        [{
            "behavior_id": behavior_id,
            "status": "FAIL_INFRASTRUCTURE",
            "attempt": 3,
            "exhausted": True,
        }],
        [],
        tmp_path,
        {"artifact_sha256": "aa" * 32},
        [],
    )
    assert receipt["results"][0]["status"] == "ADAPTER_UNCERTAIN"
    assert receipt["results"][0]["call_trace"] == []


def test_reducer_maps_sites_by_exact_pair_only(tmp_path: Path) -> None:
    behavior_id = "22" * 32
    workload = _workload([behavior_id])
    events = [{
        "sequence": 0,
        "module": "pkg.mod",
        "symbol": "func",
        "call_kind": "PYTHON_CALL",
        "argument_types": ["int"],
        "keyword_names": [],
    }]
    raw = tmp_path / behavior_id / "call_trace.raw"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(canonical_json_bytes(events))
    digest = canonical_sha256(events)
    sites = [
        {"site_id": "11" * 32, "path": "pkg/mod.py", "symbol": "func", "path_as_module": "pkg.mod"},
        {"site_id": "33" * 32, "path": "pkg/other.py", "symbol": "nearby", "path_as_module": "pkg.other"},
    ]
    receipt = build_profiling_receipt_from_attempts(
        workload,
        {"plans": [{"behavior_id": behavior_id, "status": "EXECUTION_PLAN_BOUND"}]},
        [{
            "behavior_id": behavior_id,
            "status": "PASS",
            "call_trace_sha256": digest,
            "attempt": 1,
        }],
        [],
        tmp_path,
        {"artifact_sha256": "aa" * 32},
        sites,
    )
    assert receipt["results"][0]["status"] == "SUCCESS"
    assert receipt["results"][0]["observed_site_ids"] == ["11" * 32]


def test_two_reductions_are_byte_identical(tmp_path: Path) -> None:
    ids = [f"{index:064x}" for index in range(4)]
    workload = _workload(ids)
    preclosed = [
        {
            "behavior_id": item,
            "status": "ADAPTER_UNCERTAIN",
            "failure_code": "E_EXECUTABLE_RECIPE_ABSENT",
        }
        for item in ids
    ]
    inventory = {"plans": [{"behavior_id": item, "status": "EXECUTION_PLAN_FAIL_CLOSED"} for item in ids]}
    first = build_profiling_receipt_from_attempts(
        workload, inventory, [], preclosed, tmp_path, {"artifact_sha256": "aa" * 32}, []
    )
    second = build_profiling_receipt_from_attempts(
        workload, inventory, [], preclosed, tmp_path, {"artifact_sha256": "aa" * 32}, []
    )
    assert canonical_json_bytes(first) == canonical_json_bytes(second)


def test_success_only_receipt_is_rejected_by_classify_technique() -> None:
    from p3_v3.bridge_and_frames import classify_technique

    success_id = "22" * 32
    missing_id = "33" * 32
    workload = _workload([success_id, missing_id])
    receipt = {
        "schema_version": "p3-profiling-results-v1",
        "results": [{
            "behavior_id": success_id,
            "status": "SUCCESS",
            "call_trace": [],
            "call_trace_sha256": "44" * 32,
        }],
        "runner_implementation_source_sha256": "aa" * 32,
    }
    with pytest.raises(EvidenceError, match="E_PROFILE_RESULTS"):
        classify_technique(workload, receipt)
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_receipt.py -q
```

Expected: FAIL because the reducer is absent.

- [ ] **Step 3: Minimal implementation**

Index selected `behavior_id`s. Require a partition of bound terminal
attempts and preclosed rows. Map statuses with the table above. Read
`call_trace.raw` only for SUCCESS. Compute `observed_site_ids` by
exact pair match.

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/profiling_receipt.py tests/p3_v3/test_phase2_receipt.py
rtk git commit -m "feat(p3-v3): reduce attempts and preclosures into profiling receipts" -m "Cover every selected behavior_id once and keep failed raw bytes."
```

### Task D: Rebind after receipts

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py`
- Test: `tests/p3_v3/test_phase2_reducer.py`

```python
def rebind_derived_subject_after_profiling(
    frozen_derived: Mapping[str, object],
    profiling_receipt: Mapping[str, object],
) -> dict:
    """Replace only profiling_results and technique_profile."""
```

- [ ] **Step 1: Write the failing tests**

```python
from p3_v3.bridge_and_frames import classify_technique, rebind_derived_subject_after_profiling


def reducer_fixtures() -> tuple[dict, dict, dict]:
    workload_body = {
        "schema_version": "p3-profiling-workload-v1",
        "controlled_subject_source_id": "bb" * 32,
        "selected_rows": [{"behavior_id": "22" * 32, "category": "PUBLIC_API"}],
        "selected_behavior_ids": ["22" * 32],
    }
    from p3_v3.artifacts import canonical_sha256

    workload = {**workload_body, "artifact_sha256": canonical_sha256(workload_body)}
    frozen = {
        "adapter_discovery": {"adapter_id": "PYTHON_PEP517_V1"},
        "profiling_workload": workload,
        "common_inputs": {"rows": []},
        "source_scale": {"scale_class": "L"},
        "public_behavior_frame": {"rows": []},
    }
    receipt = {
        "schema_version": "p3-profiling-results-v1",
        "neutral_snapshot_id": "aa" * 32,
        "controlled_subject_source_id": "bb" * 32,
        "normalized_source_tree_sha256": "cc" * 32,
        "build_descriptor_sha256": "dd" * 32,
        "profiling_workload_sha256": workload["artifact_sha256"],
        "adapter_implementation_source_sha256": None,
        "runner_implementation_source_sha256": "ee" * 32,
        "results": [{
            "behavior_id": "22" * 32,
            "status": "TIMEOUT",
            "argv": ["/opt/anaconda3/bin/python", "-c", "pass"],
            "input_sha256": ["11" * 32],
            "environment_sha256": "22" * 32,
            "runner_version": "p3-profiling-runner-v1",
            "exit_code": None,
            "stdout_sha256": "33" * 32,
            "stderr_sha256": "44" * 32,
            "call_trace": [],
            "call_trace_sha256": "55" * 32,
            "timed_out": True,
            "failure_code": "E_TIMEOUT",
            "observed_site_ids": [],
        }],
        "artifact_sha256": "66" * 32,
    }
    return frozen, receipt, workload


def test_rebind_does_not_call_discovery(monkeypatch) -> None:
    frozen, receipt, _workload = reducer_fixtures()
    monkeypatch.setattr(
        "p3_v3.bridge_and_frames.discover_subject_or_fail_closed",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("rediscovery")),
    )
    updated = rebind_derived_subject_after_profiling(frozen, receipt)
    assert updated["adapter_discovery"] == frozen["adapter_discovery"]
    assert updated["profiling_workload"] == frozen["profiling_workload"]
    assert updated["common_inputs"] == frozen["common_inputs"]
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_reducer.py -q
```

Expected: FAIL because `rebind_derived_subject_after_profiling` is
absent.

- [ ] **Step 3: Minimal implementation**

Copy the frozen derived subject, attach the receipt, run
`classify_technique` on the full selected denominator, and rebind
hashes. Runner digest is the four-file manifest hash.

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/bridge_and_frames.py tests/p3_v3/test_phase2_reducer.py
rtk git commit -m "feat(p3-v3): rebind frozen subjects after profiling receipts" -m "Keep discovery and E_COMMON bytes immutable."
```

### Task E: Cohorts

**Files:**
- Create: `src/p3_v3/phase2_cohorts.py`
- Modify: `scripts/p3_v3/evidence.py`
- Test: `tests/p3_v3/test_phase2_cohorts.py`

```python
def unique_eligible_criterion_ids(verified_bridge: Mapping[str, object]) -> list[str]:
    """Exact sorted unique controlled_subject_id with eligible_for_criterion."""


def rebuild_frames_from_derived(
    verified_bridge: Mapping[str, object],
    derived_subjects: Sequence[Mapping[str, object]],
) -> dict:
    """Call only build_subject_frames."""
```

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

from p3_v3.phase2_cohorts import rebuild_frames_from_derived, unique_eligible_criterion_ids


def test_rebuild_frames_from_derived_does_not_import_discover() -> None:
    source = Path("scripts/p3_v3/evidence.py").read_text(encoding="utf-8")
    dispatch = source.split("def _dispatch_rebuild_frames_from_derived")[1].split("def ")[0]
    assert "derive_subject_material" not in dispatch
    assert "discover_subject_or_fail_closed" not in dispatch


def test_criterion_equals_all_unique_eligible_ids() -> None:
    bridge = {
        "records": [
            {
                "controlled_subject_id": "11" * 32,
                "eligible_for_criterion": True,
            },
            {
                "controlled_subject_id": "11" * 32,
                "eligible_for_criterion": True,
            },
            {
                "controlled_subject_id": "22" * 32,
                "eligible_for_criterion": False,
            },
            {
                "controlled_subject_id": "33" * 32,
                "eligible_for_criterion": True,
            },
        ]
    }
    expected = ["11" * 32, "33" * 32]
    assert unique_eligible_criterion_ids(bridge) == expected
```

`rebuild_frames_from_derived` is checked by the dispatch-source test
above: it may call only `build_subject_frames`. The criterion
assertion is the exact unique eligible ID list, with no `A or B`.

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_cohorts.py -q
```

Expected: FAIL because `phase2_cohorts` is absent.

- [ ] **Step 3: Minimal implementation**

`unique_eligible_criterion_ids` reads bridge records. 
`rebuild_frames_from_derived` calls `build_subject_frames` only.

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/phase2_cohorts.py scripts/p3_v3/evidence.py \
  tests/p3_v3/test_phase2_cohorts.py
rtk git commit -m "feat(p3-v3): rebuild cohorts from frozen derived subjects" -m "Keep C_CRITERION equal to the exact unique eligible IDs."
```