# P3 C3 Stage I Applicability Census Implementation Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and validate the Stage I ordinal 9–22 applicability census
without executing it.

**Architecture:** A dedicated Stage I module processes the frozen 14-subject
universe through existing identity, source-recovery and applicability seams,
writes 140 existing p3-slot-closure-v1 objects into a staging namespace, and
atomically publishes a single validated cohort terminal only after 14/14 and
140/140 completion. It never calls contract, pair, mutant, runner or overlap
code.

**Tech Stack:** Python 3, existing p3_v3 canonical artifact helpers, pytest.

**Spec:** docs/superpowers/specs/2026-08-28-p3-c3-two-stage-prospective-paired-slice-design.md

---

## 0. Authorization boundary

```text
SLICE_A_IMPLEMENTATION_AUTHORIZED=true
SLICE_B_OFFICIAL_STAGE1_RUN_AUTHORIZED=false
OFFICIAL_RUN_AUTHORIZED=false
```

| Slice | Content | Authorized now | Success terminal |
|---|---|---|---|
| A | Stage I controller, validator, CLI, synthetic/focused tests | Yes, after this plan | `STAGE1_IMPLEMENTATION_PASS` after Tasks 1–3 |
| B | One official Stage I census | **No** | later `STAGE1_APPLICABILITY_CENSUS_COMPLETE` |

Completing Tasks 1–3 must not invoke the official zero-argument command against
the real worktree namespaces. Task 3 GREEN must not set the production
`OFFICIAL_RUN_AUTHORIZED` constant to `True`. Slice A pass does not start
Slice B. Stage II is outside this plan.

C3 remains `blocked`. `n_projects` remains 1. This plan does not modify the
claim ledger, analysis spec, design, or ordinal-8 evidence.

Cursor Cloud commands use `python3`, `git`, and `sha256sum`. Do not use `rtk`.
Do not install packages. Do not run full-suite pytest.

Worktree: `/tmp/p3-c3-ordinal9-22-source-recovery`

Branch: `cursor/content-addressed-source-join-b65d`

Implementation start HEAD after this plan lands is the commit that adds this
file. Before Task 1 starts, porcelain must be empty except the files of the
current task.

Approved design SHA-256:

`a8828022ee2095b4209261c26d0ecbab66141e59b2c9f18ce3df2045f6dd79c5`

Claim ledger SHA-256:

`bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68`

---

## 1. File map

Create only:

- `src/p3_v3/prospective_applicability_census_stage1.py`
- `scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py`
- `tests/p3_v3/test_prospective_applicability_census_stage1.py`

Do not modify these files unless a compile or import blocker appears. The
default is no modification:

- `src/p3_v3/multiproject_production_processor.py`
- `tests/p3_v3/test_multiproject_production_processor.py`

Do not modify:

- `src/p3_v3/prospective_multiproject.py`
- `scripts/p3_v3/run_prospective_multiproject_paired_slice.py`
- contract registry or generators
- pair, mutant, runner, or overlap modules
- applicability authority JSON, predicate registry, or inventory JSON
- project-cluster authority
- the two-stage design
- the claim ledger
- ordinal-8 handoff or overlap artifacts

Do not create a JSON Schema file, manifest, second ledger, Stage II module,
authorization file, or any official/staging directory under:

```text
data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2
data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2.staging
data/p3_v3/phase3/prospective-multiproject-paired-stage2-v2
data/p3_v3/phase3/prospective-multiproject-paired-stage2-v2.staging
data/p3_v3/phase3/prospective-multiproject-paired-slice-v1
data/p3_v3/phase3/prospective-multiproject-paired-slice-v1.staging
```

Reuse only:

- `EvidenceError`, `canonical_sha256`, `file_sha256`, `validate_exact_object`,
  `validate_sha256`, `write_canonical_json` from `src/p3_v3/artifacts.py`
- `SuccessorIdentity`, `load_frozen_successors`,
  `bind_production_project_identity`, `load_frozen_bridge_identity_records`
  from `src/p3_v3/prospective_multiproject.py`
- `freeze_subject_identity`, `recover_production_source`,
  `canonicalize_production_sites`, `_subject_inventory_rows`
  from `src/p3_v3/multiproject_production_processor.py`
- `load_applicability_authority`, `close_slot_with_authority`
  from `src/p3_v3/applicability_predicates.py`
- `close_slot` from `src/p3_v3/bridge_and_frames.py`
- `SEMANTIC_CONTRACT_FAMILIES` from `src/p3_v3/slot_inventory.py`

Do not call, even from Slice A tests against a real successor:

- `process_production_subject`
- `run_production_subject_pipeline`
- `freeze_production_contracts`
- any contract `generate()`
- `construct_production_pairs`
- any mutant constructor
- `execute_production_pairs`
- `measure_production_overlap`
- subject build, test, or oracle
- any ordinal-8 runner
- `close_slot_with_authority` on a real Public Behavior Frame
- `evaluate_predicate` on a real site

---

## 2. Locked production interfaces

Write these names and signatures exactly. They are shared by Tasks 1–3.

```python
from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from p3_v3.artifacts import EvidenceError, canonical_sha256, validate_exact_object, validate_sha256

STAGE1_SLICE_ID = "p3-c3-prospective-multiproject-applicability-stage1-v2"
STAGE1_SCHEMA_VERSION = "p3-c3-prospective-multiproject-applicability-stage1-v2-terminal-v1"
STAGE1_TERMINAL_STATUS = "STAGE1_APPLICABILITY_CENSUS_COMPLETE"
STAGE1_DESIGN_COMMIT = "270025608be7db631484b77ffda181438100d785"
STAGE1_DESIGN_FILE_SHA256 = (
    "a8828022ee2095b4209261c26d0ecbab66141e59b2c9f18ce3df2045f6dd79c5"
)
STAGE1_APPLICABILITY_AUTHORITY_ARTIFACT_SHA256 = (
    "30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214"
)
STAGE1_SLOT_INVENTORY_ARTIFACT_SHA256 = (
    "5c7f2dae8b0b7fd72926e2569354dbf6e878186f69d512e259e6034026dd0e27"
)
STAGE1_PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256 = (
    "802ec9a8db866c1c1d79b29e03d4e5dc0f55d4961a3f415a2486dd562fbf810e"
)
STAGE1_ORDINALS = (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22)
STAGE1_SUBJECT_COUNT = 14
STAGE1_CLOSURES_PER_SUBJECT = 10
STAGE1_CLOSURE_COUNT = 140
STAGE1_OFFICIAL_RELDIR = Path(
    "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2"
)
STAGE1_STAGING_RELDIR = Path(
    "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2.staging"
)
STAGE1_TERMINAL_FILENAME = "cohort-terminal.json"
STAGE1_DESIGN_RELPATH = Path(
    "docs/superpowers/specs/2026-08-28-p3-c3-two-stage-prospective-paired-slice-design.md"
)
STAGE1_CONTROLLER_RELPATH = Path(
    "src/p3_v3/prospective_applicability_census_stage1.py"
)
STAGE1_CLI_RELPATH = Path(
    "scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py"
)
STAGE1_AUTHORITY_RELPATH = Path("data/p3_v3/phase2/applicability-authority.json")
STAGE1_INVENTORY_RELPATH = Path("data/p3_v3/phase2/slot-inventory.json")
STAGE1_PROJECT_CLUSTER_AUTHORITY_RELPATH = Path(
    "data/p3_v3/phase3/inputs/project-cluster-authority-v1.json"
)
STAGE1_PREDICATE_REGISTRY_RELPATH = Path(
    "data/p3_v3/protocol/applicability-predicate-registry.json"
)
STAGE1_SLOT_IMPLEMENTATION_RELPATH = Path("src/p3_v3/slot_inventory.py")
STAGE1_PREDICATE_IMPLEMENTATION_RELPATH = Path(
    "src/p3_v3/applicability_predicates.py"
)
OLD_V1_OFFICIAL_RELDIR = Path(
    "data/p3_v3/phase3/prospective-multiproject-paired-slice-v1"
)
OLD_V1_STAGING_RELDIR = Path(
    "data/p3_v3/phase3/prospective-multiproject-paired-slice-v1.staging"
)
OFFICIAL_RUN_AUTHORIZED = False
ALLOWED_CLOSURE_STATES = frozenset({
    "SITE_FROZEN",
    "APPLICABILITY_CLOSED_NOT_APPLICABLE",
})
INVENTORY_FAMILY_ORDER = ("INV", "MONO", "CONV", "DYN", "CMP")
_GIT_SHA1_RE = re.compile(r"[0-9a-f]{40}")
FORBIDDEN_TERMINAL_FIELDS = frozenset({
    "timestamp",
    "created_at",
    "hostname",
    "host",
    "random",
    "nonce",
    "contract_id",
    "pair_count",
    "kill_count",
    "survival",
    "overlap",
    "eligibility",
    "PAIRED_EVIDENCE_COMPLETE",
    "SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT",
    "PAIR_CONSTRUCTION_UNAVAILABLE",
    "MULTIPROJECT_COHORT_EXHAUSTED",
    "d_subject",
    "semantic_pair_kills",
    "syntactic_pair_kills",
})
STAGE1_TERMINAL_SCHEMA = {
    "schema_version": str,
    "slice_id": str,
    "design_commit": str,
    "design_file_sha256": str,
    "applicability_authority_artifact_sha256": str,
    "slot_inventory_artifact_sha256": str,
    "project_cluster_authority_artifact_sha256": str,
    "controller_source_sha256": str,
    "terminal_status": str,
    "subjects": list,
    "artifact_sha256": str,
}
STAGE1_SUBJECT_SCHEMA = {
    "successor_ordinal": int,
    "neutral_snapshot_id": str,
    "controlled_subject_source_id": str,
    "controlled_subject_id": str,
    "project_cluster_key": str,
    "closure_artifact_sha256s": list,
    "site_frozen_count": int,
    "not_applicable_count": int,
}

def validate_git_sha1(value: Any, field: str) -> str:
    if not isinstance(value, str) or _GIT_SHA1_RE.fullmatch(value) is None:
        raise EvidenceError("E_STAGE1_IDENTITY", f"{field} must be a 40-character git SHA")
    return value

def sort_stage1_inventory_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    indexed = list(INVENTORY_FAMILY_ORDER)
    return sorted(
        (dict(row) for row in rows),
        key=lambda row: (indexed.index(str(row["semantic_contract_family"])), int(row["slot_ordinal"])),
    )

def inventory_slot_ids_for_subject(
    inventory: Mapping[str, Any],
    controlled_subject_id: str,
) -> tuple[str, ...]:
    from p3_v3.multiproject_production_processor import _subject_inventory_rows

    rows = sort_stage1_inventory_rows(
        _subject_inventory_rows(inventory, controlled_subject_id)
    )
    return tuple(str(row["slot_id"]) for row in rows)

def make_stage1_closure(
    *,
    slot_id: str,
    controlled_subject_id: str,
    state: str,
    site_id: str | None,
) -> dict[str, Any]:
    if state not in ALLOWED_CLOSURE_STATES:
        raise EvidenceError("E_STAGE1_TERMINAL", f"illegal closure state {state}")
    if state == "SITE_FROZEN":
        path = "APPLICABLE"
        if not isinstance(site_id, str):
            raise EvidenceError("E_STAGE1_TERMINAL", "SITE_FROZEN requires site_id")
        validate_sha256(site_id, "site_id")
    else:
        path = "APPLICABILITY_CLOSED_NOT_APPLICABLE"
        if site_id is not None:
            raise EvidenceError("E_STAGE1_TERMINAL", "NOT_APPLICABLE forbids site_id")
    body = {
        "schema_version": "p3-slot-closure-v1",
        "slot_id": validate_sha256(slot_id, "slot_id"),
        "controlled_subject_id": validate_sha256(
            controlled_subject_id, "controlled_subject_id"
        ),
        "site_id": site_id,
        "state": state,
        "path": path,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}

def rebuild_stage1_counts(
    closures: Sequence[Mapping[str, Any]],
) -> tuple[int, int]:
    site_frozen = 0
    not_applicable = 0
    for closure in closures:
        state = closure["state"]
        if state == "SITE_FROZEN":
            site_frozen += 1
        elif state == "APPLICABILITY_CLOSED_NOT_APPLICABLE":
            not_applicable += 1
        else:
            raise EvidenceError("E_STAGE1_TERMINAL", f"illegal closure state {state}")
    if site_frozen + not_applicable != STAGE1_CLOSURES_PER_SUBJECT:
        raise EvidenceError("E_STAGE1_TERMINAL", "closure counts must sum to 10")
    return site_frozen, not_applicable

def build_stage1_terminal(
    *,
    design_commit: str,
    design_file_sha256: str,
    controller_source_sha256: str,
    applicability_authority_artifact_sha256: str,
    slot_inventory_artifact_sha256: str,
    project_cluster_authority_artifact_sha256: str,
    subjects: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for raw in subjects:
        closures = list(raw["closures"])
        site_frozen, not_applicable = rebuild_stage1_counts(closures)
        rows.append({
            "successor_ordinal": int(raw["successor_ordinal"]),
            "neutral_snapshot_id": str(raw["neutral_snapshot_id"]),
            "controlled_subject_source_id": str(raw["controlled_subject_source_id"]),
            "controlled_subject_id": str(raw["controlled_subject_id"]),
            "project_cluster_key": str(raw["project_cluster_key"]),
            "closure_artifact_sha256s": [str(item["artifact_sha256"]) for item in closures],
            "site_frozen_count": site_frozen,
            "not_applicable_count": not_applicable,
        })
    body = {
        "schema_version": STAGE1_SCHEMA_VERSION,
        "slice_id": STAGE1_SLICE_ID,
        "design_commit": design_commit,
        "design_file_sha256": design_file_sha256,
        "applicability_authority_artifact_sha256": applicability_authority_artifact_sha256,
        "slot_inventory_artifact_sha256": slot_inventory_artifact_sha256,
        "project_cluster_authority_artifact_sha256": project_cluster_authority_artifact_sha256,
        "controller_source_sha256": controller_source_sha256,
        "terminal_status": STAGE1_TERMINAL_STATUS,
        "subjects": rows,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}

def validate_stage1_terminal(
    terminal: Mapping[str, Any],
    *,
    expected_design_commit: str,
    expected_design_file_sha256: str,
    expected_controller_source_sha256: str,
    expected_applicability_authority_artifact_sha256: str,
    expected_slot_inventory_artifact_sha256: str,
    expected_project_cluster_authority_artifact_sha256: str,
    subject_closures: Sequence[Sequence[Mapping[str, Any]]],
    inventory: Mapping[str, Any],
) -> dict[str, Any]:
    if FORBIDDEN_TERMINAL_FIELDS.intersection(terminal):
        raise EvidenceError("E_STAGE1_TERMINAL", "forbidden terminal field present")
    payload = validate_exact_object(dict(terminal), STAGE1_TERMINAL_SCHEMA, "stage1-terminal")
    if payload["schema_version"] != STAGE1_SCHEMA_VERSION:
        raise EvidenceError("E_STAGE1_TERMINAL", "illegal schema_version")
    if payload["slice_id"] != STAGE1_SLICE_ID:
        raise EvidenceError("E_STAGE1_TERMINAL", "illegal slice_id")
    if payload["terminal_status"] != STAGE1_TERMINAL_STATUS:
        raise EvidenceError("E_STAGE1_TERMINAL", "illegal terminal_status")
    if payload["design_commit"] != expected_design_commit:
        raise EvidenceError("E_STAGE1_IDENTITY", "design_commit mismatch")
    validate_git_sha1(payload["design_commit"], "design_commit")
    if payload["design_file_sha256"] != expected_design_file_sha256:
        raise EvidenceError("E_STAGE1_IDENTITY", "design_file_sha256 mismatch")
    if payload["controller_source_sha256"] != expected_controller_source_sha256:
        raise EvidenceError("E_STAGE1_IDENTITY", "controller_source_sha256 mismatch")
    if (
        payload["applicability_authority_artifact_sha256"]
        != expected_applicability_authority_artifact_sha256
    ):
        raise EvidenceError("E_STAGE1_IDENTITY", "authority artifact mismatch")
    if payload["slot_inventory_artifact_sha256"] != expected_slot_inventory_artifact_sha256:
        raise EvidenceError("E_STAGE1_IDENTITY", "inventory artifact mismatch")
    if (
        payload["project_cluster_authority_artifact_sha256"]
        != expected_project_cluster_authority_artifact_sha256
    ):
        raise EvidenceError("E_STAGE1_IDENTITY", "project-cluster artifact mismatch")
    validate_sha256(payload["design_file_sha256"], "design_file_sha256")
    validate_sha256(payload["controller_source_sha256"], "controller_source_sha256")
    validate_sha256(
        payload["applicability_authority_artifact_sha256"],
        "applicability_authority_artifact_sha256",
    )
    validate_sha256(
        payload["slot_inventory_artifact_sha256"],
        "slot_inventory_artifact_sha256",
    )
    validate_sha256(
        payload["project_cluster_authority_artifact_sha256"],
        "project_cluster_authority_artifact_sha256",
    )
    subjects = payload["subjects"]
    if len(subjects) != STAGE1_SUBJECT_COUNT:
        raise EvidenceError("E_STAGE1_TERMINAL", "subject count must be 14")
    if len(subject_closures) != STAGE1_SUBJECT_COUNT:
        raise EvidenceError("E_STAGE1_TERMINAL", "subject_closures count must be 14")
    ordinals: list[int] = []
    closure_count = 0
    for index, raw in enumerate(subjects):
        row = validate_exact_object(dict(raw), STAGE1_SUBJECT_SCHEMA, f"subjects[{index}]")
        if FORBIDDEN_TERMINAL_FIELDS.intersection(row):
            raise EvidenceError("E_STAGE1_TERMINAL", "forbidden subject field present")
        ordinals.append(int(row["successor_ordinal"]))
        closures = list(subject_closures[index])
        if len(closures) != STAGE1_CLOSURES_PER_SUBJECT:
            raise EvidenceError("E_STAGE1_TERMINAL", "each subject must have 10 closures")
        if len(row["closure_artifact_sha256s"]) != STAGE1_CLOSURES_PER_SUBJECT:
            raise EvidenceError("E_STAGE1_TERMINAL", "each subject must have 10 closure hashes")
        site_frozen, not_applicable = rebuild_stage1_counts(closures)
        if row["site_frozen_count"] != site_frozen:
            raise EvidenceError("E_STAGE1_TERMINAL", "site_frozen_count does not rebuild")
        if row["not_applicable_count"] != not_applicable:
            raise EvidenceError("E_STAGE1_TERMINAL", "not_applicable_count does not rebuild")
        expected_slot_ids = inventory_slot_ids_for_subject(
            inventory, str(row["controlled_subject_id"])
        )
        observed_slot_ids = tuple(str(item["slot_id"]) for item in closures)
        if observed_slot_ids != expected_slot_ids:
            raise EvidenceError("E_STAGE1_TERMINAL", "closure order does not match inventory")
        observed_hashes = [str(item["artifact_sha256"]) for item in closures]
        if observed_hashes != list(row["closure_artifact_sha256s"]):
            raise EvidenceError("E_STAGE1_TERMINAL", "closure hashes do not match written objects")
        closure_count += len(closures)
    if ordinals != list(STAGE1_ORDINALS):
        raise EvidenceError("E_STAGE1_TERMINAL", "ordinals must be exactly 9-22 in order")
    if 8 in ordinals:
        raise EvidenceError("E_STAGE1_TERMINAL", "ordinal 8 is forbidden")
    if closure_count != STAGE1_CLOSURE_COUNT:
        raise EvidenceError("E_STAGE1_TERMINAL", "closure count must be 140")
    body = {key: value for key, value in payload.items() if key != "artifact_sha256"}
    if payload["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_STAGE1_IDENTITY", "terminal self-hash mismatch")
    return {
        "valid": True,
        "terminal_status": STAGE1_TERMINAL_STATUS,
        "subject_count": STAGE1_SUBJECT_COUNT,
        "closure_count": STAGE1_CLOSURE_COUNT,
        "artifact_sha256": payload["artifact_sha256"],
    }

def run_stage1_census(
    *,
    repo_root: Path,
    output_root: Path,
    staging_root: Path,
    subject_processor: Callable[..., Mapping[str, Any]],
) -> dict[str, Any]:
    raise EvidenceError("E_STAGE1_FAIL_CLOSED", "implemented in Task 2")

def process_stage1_subject(
    successor: Any,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    raise EvidenceError("E_STAGE1_FAIL_CLOSED", "implemented in Task 2")
```

`design_commit` is the 40-character git SHA of the approved two-stage design
commit `270025608be7db631484b77ffda181438100d785`. The implementation bytes are
bound separately by `controller_source_sha256` via `file_sha256` of
`STAGE1_CONTROLLER_RELPATH`. Do not call `validate_sha256` on `design_commit`.

`run_stage1_census` accepts only the four keyword arguments above. It must not
accept `order`, `max_attempts`, `project_map`, `resume`, `retry`, or `skip`.

`process_stage1_subject` is the unique production processor. Slice A tests must
not call it against real ordinal 9–22 Public Behavior Frames. Task 2 tests
inject a synthetic `subject_processor` into `run_stage1_census`.

---

## 3. Task 1: Stage I domain, terminal builder, and validator

**Files:**

| Role | Path |
|---|---|
| Create | `src/p3_v3/prospective_applicability_census_stage1.py` |
| Create | `tests/p3_v3/test_prospective_applicability_census_stage1.py` |
| Modify | none |

**Consumes:**

- `EvidenceError`, `canonical_sha256`, `validate_exact_object`, `validate_sha256`
- `load_frozen_successors` identities only (no site open)
- `_subject_inventory_rows` plus `INVENTORY_FAMILY_ORDER` for slot order
- a synthetic inventory object built in the test file

**Produces:**

- `STAGE1_*` constants listed in §2
- `validate_git_sha1`
- `sort_stage1_inventory_rows`
- `inventory_slot_ids_for_subject`
- `make_stage1_closure`
- `rebuild_stage1_counts`
- `build_stage1_terminal`
- `validate_stage1_terminal`

`run_stage1_census` and `process_stage1_subject` may be absent in Task 1. Do
not implement atomic publication in Task 1.

- [ ] Write the Task 1 test file exactly as specified
- [ ] Run the Task 1 RED command and keep the failing exit
- [ ] Implement the Task 1 module functions from §2
- [ ] Run the Task 1 GREEN command and require 12 passed
- [ ] Commit and push only the Task 1 files

### 3.1 Task 1 test helpers and test functions

Write the complete test file below. Do not open a Public Behavior Frame or
extracted source tree.

```python
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256
from p3_v3.prospective_multiproject import load_frozen_successors
from p3_v3.slot_inventory import SEMANTIC_CONTRACT_FAMILIES


MODULE_PATH = Path("src/p3_v3/prospective_applicability_census_stage1.py")
FAKE_CONTROLLER_SHA = "aa" * 32
FAKE_SITE_SHA = "bb" * 32
FAKE_SLOT_PREFIX = "cc"


def _require_module():
    if importlib.util.find_spec("p3_v3.prospective_applicability_census_stage1") is None:
        raise AssertionError("stage1 module is absent")
    from p3_v3.prospective_applicability_census_stage1 import (
        STAGE1_APPLICABILITY_AUTHORITY_ARTIFACT_SHA256,
        STAGE1_DESIGN_COMMIT,
        STAGE1_DESIGN_FILE_SHA256,
        STAGE1_PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256,
        STAGE1_SLICE_ID,
        STAGE1_SLOT_INVENTORY_ARTIFACT_SHA256,
        STAGE1_TERMINAL_STATUS,
        build_stage1_terminal,
        make_stage1_closure,
        validate_stage1_terminal,
    )

    return {
        "build": build_stage1_terminal,
        "closure": make_stage1_closure,
        "validate": validate_stage1_terminal,
        "slice_id": STAGE1_SLICE_ID,
        "status": STAGE1_TERMINAL_STATUS,
        "design_commit": STAGE1_DESIGN_COMMIT,
        "design_file": STAGE1_DESIGN_FILE_SHA256,
        "authority": STAGE1_APPLICABILITY_AUTHORITY_ARTIFACT_SHA256,
        "inventory_sha": STAGE1_SLOT_INVENTORY_ARTIFACT_SHA256,
        "cluster": STAGE1_PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256,
    }


def _slot_id(index: int) -> str:
    return f"{FAKE_SLOT_PREFIX}{index:02d}" + ("d" * 60)


def _synthetic_inventory_and_subjects(mixed: bool = True):
    successors = load_frozen_successors()
    inventory_slots = []
    subjects = []
    closures_by_subject = []
    for offset, successor in enumerate(successors):
        closures = []
        for slot_index, family in enumerate(SEMANTIC_CONTRACT_FAMILIES):
            for slot_ordinal in (0, 1):
                linear = slot_index * 2 + slot_ordinal
                slot_id = _slot_id(offset * 10 + linear)
                if mixed and linear < (offset % 4):
                    state = "SITE_FROZEN"
                    site_id = FAKE_SITE_SHA
                else:
                    state = "APPLICABILITY_CLOSED_NOT_APPLICABLE"
                    site_id = None
                inventory_slots.append({
                    "controlled_subject_id": successor.controlled_subject_id,
                    "permitted_construction_mechanism": "CE",
                    "semantic_contract_family": family,
                    "slot_id": slot_id,
                    "slot_ordinal": slot_ordinal,
                })
                closures.append(
                    _require_module()["closure"](
                        slot_id=slot_id,
                        controlled_subject_id=successor.controlled_subject_id,
                        state=state,
                        site_id=site_id,
                    )
                )
        subjects.append({
            "successor_ordinal": successor.successor_ordinal,
            "neutral_snapshot_id": successor.neutral_snapshot_id,
            "controlled_subject_source_id": successor.controlled_subject_source_id,
            "controlled_subject_id": successor.controlled_subject_id,
            "project_cluster_key": f"synthetic.project.{successor.successor_ordinal}",
            "closures": closures,
        })
        closures_by_subject.append(closures)
    inventory = {
        "artifact_sha256": "ee" * 32,
        "schema_version": "p3-slot-inventory-v1",
        "slots": inventory_slots,
    }
    return inventory, subjects, closures_by_subject


def _expected(mod):
    return {
        "expected_design_commit": mod["design_commit"],
        "expected_design_file_sha256": mod["design_file"],
        "expected_controller_source_sha256": FAKE_CONTROLLER_SHA,
        "expected_applicability_authority_artifact_sha256": mod["authority"],
        "expected_slot_inventory_artifact_sha256": mod["inventory_sha"],
        "expected_project_cluster_authority_artifact_sha256": mod["cluster"],
    }


def test_stage1_module_and_interfaces_exist():
    assert MODULE_PATH.is_file()
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=subjects,
    )
    report = mod["validate"](
        terminal,
        subject_closures=closures,
        inventory=inventory,
        **_expected(mod),
    )
    assert report["valid"] is True
    assert report["subject_count"] == 14
    assert report["closure_count"] == 140


def test_build_stage1_terminal_exact_keys_slice_status_and_self_hash():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=subjects,
    )
    assert set(terminal) == {
        "schema_version",
        "slice_id",
        "design_commit",
        "design_file_sha256",
        "applicability_authority_artifact_sha256",
        "slot_inventory_artifact_sha256",
        "project_cluster_authority_artifact_sha256",
        "controller_source_sha256",
        "terminal_status",
        "subjects",
        "artifact_sha256",
    }
    assert terminal["slice_id"] == mod["slice_id"]
    assert terminal["terminal_status"] == mod["status"]
    assert [row["successor_ordinal"] for row in terminal["subjects"]] == list(range(9, 23))
    body = {key: value for key, value in terminal.items() if key != "artifact_sha256"}
    assert terminal["artifact_sha256"] == canonical_sha256(body)
    assert len(terminal["subjects"]) == 14
    assert sum(len(row["closure_artifact_sha256s"]) for row in terminal["subjects"]) == 140
    mod["validate"](terminal, subject_closures=closures, inventory=inventory, **_expected(mod))


def test_validate_rejects_identity_field_tamper():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=subjects,
    )
    terminal["design_file_sha256"] = "ff" * 32
    terminal["artifact_sha256"] = canonical_sha256(
        {key: value for key, value in terminal.items() if key != "artifact_sha256"}
    )
    with pytest.raises(EvidenceError, match="design_file_sha256 mismatch"):
        mod["validate"](terminal, subject_closures=closures, inventory=inventory, **_expected(mod))


def test_validate_rejects_missing_duplicate_and_reordered_ordinals():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    missing = subjects[1:]
    built = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=missing,
    )
    with pytest.raises(EvidenceError, match="subject count must be 14"):
        mod["validate"](
            built,
            subject_closures=closures[1:],
            inventory=inventory,
            **_expected(mod),
        )
    swapped = list(subjects)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    swapped_closures = list(closures)
    swapped_closures[0], swapped_closures[1] = swapped_closures[1], swapped_closures[0]
    reordered = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=swapped,
    )
    with pytest.raises(EvidenceError, match="ordinals must be exactly 9-22"):
        mod["validate"](
            reordered,
            subject_closures=swapped_closures,
            inventory=inventory,
            **_expected(mod),
        )
    duplicated = list(subjects)
    duplicated[1] = dict(subjects[0])
    duplicated[1]["closures"] = list(subjects[0]["closures"])
    dup_closures = list(closures)
    dup_closures[1] = list(closures[0])
    duplicated_terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=duplicated,
    )
    with pytest.raises(EvidenceError, match="ordinals must be exactly 9-22"):
        mod["validate"](
            duplicated_terminal,
            subject_closures=dup_closures,
            inventory=inventory,
            **_expected(mod),
        )


def test_validate_rejects_subject_without_exactly_ten_closures():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    subjects[0]["closures"] = subjects[0]["closures"][:9]
    closures[0] = closures[0][:9]
    with pytest.raises(EvidenceError, match="closure counts must sum to 10"):
        mod["build"](
            design_commit=mod["design_commit"],
            design_file_sha256=mod["design_file"],
            controller_source_sha256=FAKE_CONTROLLER_SHA,
            applicability_authority_artifact_sha256=mod["authority"],
            slot_inventory_artifact_sha256=mod["inventory_sha"],
            project_cluster_authority_artifact_sha256=mod["cluster"],
            subjects=subjects,
        )


def test_validate_rejects_total_closure_count_not_140():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=subjects,
    )
    with pytest.raises(EvidenceError, match="subject_closures count must be 14"):
        mod["validate"](
            terminal,
            subject_closures=closures[:13],
            inventory=inventory,
            **_expected(mod),
        )


def test_validate_rejects_closure_order_not_matching_inventory():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    closures[0] = list(reversed(closures[0]))
    subjects[0]["closures"] = closures[0]
    terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=subjects,
    )
    with pytest.raises(EvidenceError, match="closure order does not match inventory"):
        mod["validate"](terminal, subject_closures=closures, inventory=inventory, **_expected(mod))


def test_validate_rejects_counts_that_do_not_rebuild_from_closures():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=subjects,
    )
    terminal["subjects"][0]["site_frozen_count"] = 10
    terminal["subjects"][0]["not_applicable_count"] = 0
    terminal["artifact_sha256"] = canonical_sha256(
        {key: value for key, value in terminal.items() if key != "artifact_sha256"}
    )
    with pytest.raises(EvidenceError, match="site_frozen_count does not rebuild"):
        mod["validate"](terminal, subject_closures=closures, inventory=inventory, **_expected(mod))


def test_validate_rejects_illegal_terminal_status_and_slice_id():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=subjects,
    )
    terminal["terminal_status"] = "PAIRED_EVIDENCE_COMPLETE"
    terminal["artifact_sha256"] = canonical_sha256(
        {key: value for key, value in terminal.items() if key != "artifact_sha256"}
    )
    with pytest.raises(EvidenceError, match="illegal terminal_status"):
        mod["validate"](terminal, subject_closures=closures, inventory=inventory, **_expected(mod))
    terminal["terminal_status"] = mod["status"]
    terminal["slice_id"] = "p3-c3-prospective-multiproject-paired-slice-v1"
    terminal["artifact_sha256"] = canonical_sha256(
        {key: value for key, value in terminal.items() if key != "artifact_sha256"}
    )
    with pytest.raises(EvidenceError, match="illegal slice_id"):
        mod["validate"](terminal, subject_closures=closures, inventory=inventory, **_expected(mod))


def test_validate_rejects_self_hash_then_frozen_identity_tamper():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=subjects,
    )
    terminal["subjects"][0]["controlled_subject_id"] = load_frozen_successors()[1].controlled_subject_id
    terminal["artifact_sha256"] = canonical_sha256(
        {key: value for key, value in terminal.items() if key != "artifact_sha256"}
    )
    with pytest.raises(EvidenceError):
        mod["validate"](terminal, subject_closures=closures, inventory=inventory, **_expected(mod))


def test_validate_rejects_forbidden_contract_pair_kill_fields():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects()
    terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=subjects,
    )
    terminal["pair_count"] = 4
    with pytest.raises(EvidenceError, match="forbidden terminal field present"):
        mod["validate"](terminal, subject_closures=closures, inventory=inventory, **_expected(mod))


def test_validate_accepts_mixed_site_frozen_and_not_applicable_counts():
    mod = _require_module()
    inventory, subjects, closures = _synthetic_inventory_and_subjects(mixed=True)
    terminal = mod["build"](
        design_commit=mod["design_commit"],
        design_file_sha256=mod["design_file"],
        controller_source_sha256=FAKE_CONTROLLER_SHA,
        applicability_authority_artifact_sha256=mod["authority"],
        slot_inventory_artifact_sha256=mod["inventory_sha"],
        project_cluster_authority_artifact_sha256=mod["cluster"],
        subjects=subjects,
    )
    report = mod["validate"](
        terminal,
        subject_closures=closures,
        inventory=inventory,
        **_expected(mod),
    )
    rebuilt = [
        row["site_frozen_count"] + row["not_applicable_count"]
        for row in terminal["subjects"]
    ]
    assert rebuilt == [10] * 14
    assert report["closure_count"] == 140
```

### 3.2 RED

```bash
cd /tmp/p3-c3-ordinal9-22-source-recovery
PYTHONPATH=src python3 -m pytest -q tests/p3_v3/test_prospective_applicability_census_stage1.py
```

Expected failure: `AssertionError: stage1 module is absent` or
`ModuleNotFoundError: No module named 'p3_v3.prospective_applicability_census_stage1'`.
Exit code: `1` or `2`.

Do not create the production module before this RED command.

### 3.3 Minimal implementation

Create `src/p3_v3/prospective_applicability_census_stage1.py` with the Task 1
functions and constants from §2. Omit the bodies of `run_stage1_census` and
`process_stage1_subject` or leave them raising `EvidenceError` with
`E_STAGE1_FAIL_CLOSED`. Do not write official or staging directories.

### 3.4 GREEN

```bash
cd /tmp/p3-c3-ordinal9-22-source-recovery
PYTHONPATH=src python3 -m pytest -q tests/p3_v3/test_prospective_applicability_census_stage1.py
git diff --check
```

Expected: `12 passed`. Exit code `0`. `git diff --check` is silent.

### 3.5 Task 1 commit

```bash
git add \
  src/p3_v3/prospective_applicability_census_stage1.py \
  tests/p3_v3/test_prospective_applicability_census_stage1.py
git diff --cached --check
git commit -m "$(cat <<'EOF'
feat(p3-v3): add Stage I terminal builder and validator

Implement the Stage I cohort terminal object, inventory-order helper,
and fail-closed validator for the frozen 14-subject census without
running applicability predicates or writing official namespaces.
EOF
)"
git push -u origin cursor/content-addressed-source-join-b65d
```

---

## 4. Task 2: Stage I controller and atomic publication

**Files:**

| Role | Path |
|---|---|
| Modify | `src/p3_v3/prospective_applicability_census_stage1.py` |
| Modify | `tests/p3_v3/test_prospective_applicability_census_stage1.py` |
| Create | none |

**Consumes:**

- Task 1 builder and validator
- `load_frozen_successors`
- `write_canonical_json(path, value, exclusive=True)`
- injected synthetic `subject_processor`

**Produces:**

- `run_stage1_census`
- `process_stage1_subject`
- `stage1_subject_directory`
- `write_stage1_closure`
- `publish_stage1_official`

`process_stage1_subject` is implemented in this task so the production
composition is present, but Task 2 tests must not call it. Tests pass a
synthetic processor.

Production composition of `process_stage1_subject`, used only after a later
Slice B authorization:

1. reject `successor_ordinal == 8`
2. `freeze_subject_identity(successor, repo_root)`
3. `recover_production_source(binding, repo_root)`
4. `load_applicability_authority` with the Stage I frozen paths
5. `_subject_inventory_rows` then `sort_stage1_inventory_rows`
6. read that ordinal's Public Behavior Frame only through the existing closer
7. `canonicalize_production_sites`
8. `close_slot_with_authority` once per sorted inventory row
9. return the subject mapping with ten full `p3-slot-closure-v1` objects

`run_stage1_census` execution order:

1. Fail closed if `output_root` or `staging_root` exists.
2. Create the unique `staging_root`.
3. Load `load_frozen_successors()` and require ordinals `STAGE1_ORDINALS`.
4. Process ordinals 9 through 22 in that order. Do not accept another order.
5. For each subject, require exactly 10 closures and write each as
   `staging_root/subjects/<ordinal-two-digit>-<controlled_subject_id>/<slot_id>.json`
   with `write_canonical_json(path, value, exclusive=True)`.
6. After each closure write, retain the bytes; do not delete them on later
   success of the same subject.
7. On any failure: do not write `cohort-terminal.json`, do not rename staging
   to official, retain `staging_root` as partial, and do not retry, resume, or
   continue.
8. After 14/14 subjects and 140/140 closures, call `build_stage1_terminal` and
   `validate_stage1_terminal`.
9. Write `staging_root/cohort-terminal.json` as the last file.
10. Recheck the staging file set: 140 closures + 1 terminal, identities match.
11. Publish with one `os.replace(staging_root, output_root)`.
12. After success, the staging sibling path must not exist.

Return value of `run_stage1_census` after success:

```python
{
    "status": STAGE1_TERMINAL_STATUS,
    "official_root": str(output_root),
    "subject_count": 14,
    "closure_count": 140,
    "write_order": [str(path) for path in write_log],
    "terminal": terminal,
}
```

### 4.1 Task 2 additional tests

Append these functions to the Task 1 test file.

```python
import inspect
import os

from p3_v3.artifacts import write_canonical_json


def _synthetic_processor_factory(fail_ordinal: int | None = None):
    inventory, subjects, closures = _synthetic_inventory_and_subjects(mixed=True)
    by_ordinal = {int(row["successor_ordinal"]): row for row in subjects}

    def processor(successor, *, repo_root):
        del repo_root
        if successor.successor_ordinal == 8:
            raise EvidenceError("IDENTITY_CONFLICT", "ordinal 8 is excluded from Stage I")
        if fail_ordinal is not None and successor.successor_ordinal == fail_ordinal:
            raise EvidenceError("INFRASTRUCTURE_FAILURE", f"synthetic failure at {fail_ordinal}")
        return by_ordinal[int(successor.successor_ordinal)]

    return processor, inventory, subjects, closures


def test_run_stage1_census_fixed_order_9_to_22(tmp_path: Path):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census

    seen: list[int] = []
    processor, inventory, subjects, closures = _synthetic_processor_factory()

    def wrapped(successor, *, repo_root):
        seen.append(successor.successor_ordinal)
        return processor(successor, repo_root=repo_root)

    output = tmp_path / "official"
    staging = tmp_path / "staging"
    result = run_stage1_census(
        repo_root=tmp_path,
        output_root=output,
        staging_root=staging,
        subject_processor=wrapped,
    )
    assert seen == list(range(9, 23))
    assert result["subject_count"] == 14
    assert result["closure_count"] == 140
    assert result["status"] == "STAGE1_APPLICABILITY_CENSUS_COMPLETE"


def test_run_stage1_census_rejects_ordinal_8(tmp_path: Path, monkeypatch):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census
    from p3_v3.prospective_multiproject import SuccessorIdentity, load_frozen_successors

    processor, inventory, subjects, closures = _synthetic_processor_factory()
    frozen = load_frozen_successors()
    fake = SuccessorIdentity(
        successor_ordinal=8,
        neutral_snapshot_id=frozen[0].neutral_snapshot_id,
        controlled_subject_source_id=frozen[0].controlled_subject_source_id,
        controlled_subject_id=frozen[0].controlled_subject_id,
    )
    monkeypatch.setattr(
        "p3_v3.prospective_applicability_census_stage1.load_frozen_successors",
        lambda: (fake, *frozen[1:]),
    )
    with pytest.raises(EvidenceError, match="ordinal 8"):
        run_stage1_census(
            repo_root=tmp_path,
            output_root=tmp_path / "official",
            staging_root=tmp_path / "staging",
            subject_processor=processor,
        )
    assert not (tmp_path / "official").exists()


def test_run_stage1_census_writes_fourteen_by_ten(tmp_path: Path):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census

    processor, inventory, subjects, closures = _synthetic_processor_factory()
    output = tmp_path / "official"
    run_stage1_census(
        repo_root=tmp_path,
        output_root=output,
        staging_root=tmp_path / "staging",
        subject_processor=processor,
    )
    subject_dirs = sorted((output / "subjects").iterdir())
    assert len(subject_dirs) == 14
    closure_files = list(output.glob("subjects/*/*.json"))
    assert len(closure_files) == 140
    assert (output / "cohort-terminal.json").is_file()


def test_run_stage1_census_does_not_stop_early_on_site_frozen(tmp_path: Path):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census

    seen: list[int] = []
    processor, inventory, subjects, closures = _synthetic_processor_factory()

    def wrapped(successor, *, repo_root):
        seen.append(successor.successor_ordinal)
        return processor(successor, repo_root=repo_root)

    run_stage1_census(
        repo_root=tmp_path,
        output_root=tmp_path / "official",
        staging_root=tmp_path / "staging",
        subject_processor=wrapped,
    )
    assert seen == list(range(9, 23))


def test_run_stage1_census_signature_forbids_order_max_attempts_and_map():
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census

    names = set(inspect.signature(run_stage1_census).parameters)
    assert names == {"repo_root", "output_root", "staging_root", "subject_processor"}
    with pytest.raises(TypeError):
        run_stage1_census(
            repo_root=Path("."),
            output_root=Path("o"),
            staging_root=Path("s"),
            subject_processor=lambda successor, repo_root=None: {},
            order=(9, 10),
        )
    with pytest.raises(TypeError):
        run_stage1_census(
            repo_root=Path("."),
            output_root=Path("o"),
            staging_root=Path("s"),
            subject_processor=lambda successor, repo_root=None: {},
            max_attempts=3,
        )
    with pytest.raises(TypeError):
        run_stage1_census(
            repo_root=Path("."),
            output_root=Path("o"),
            staging_root=Path("s"),
            subject_processor=lambda successor, repo_root=None: {},
            project_map={"x": "y"},
        )


def test_run_stage1_census_writes_mixed_synthetic_states(tmp_path: Path):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census
    from p3_v3.artifacts import read_canonical_json

    processor, inventory, subjects, closures = _synthetic_processor_factory()
    output = tmp_path / "official"
    result = run_stage1_census(
        repo_root=tmp_path,
        output_root=output,
        staging_root=tmp_path / "staging",
        subject_processor=processor,
    )
    states = set()
    for path in output.glob("subjects/*/*.json"):
        states.add(read_canonical_json(path)["state"])
    assert states == {"SITE_FROZEN", "APPLICABILITY_CLOSED_NOT_APPLICABLE"}
    assert result["closure_count"] == 140


def test_nth_subject_failure_keeps_partial_staging_without_official(tmp_path: Path):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census

    processor, inventory, subjects, closures = _synthetic_processor_factory(fail_ordinal=12)
    output = tmp_path / "official"
    staging = tmp_path / "staging"
    with pytest.raises(EvidenceError, match="synthetic failure at 12"):
        run_stage1_census(
            repo_root=tmp_path,
            output_root=output,
            staging_root=staging,
            subject_processor=processor,
        )
    assert output.exists() is False
    assert staging.exists() is True
    written = list(staging.glob("subjects/*/*.json"))
    assert 0 < len(written) < 140
    assert (staging / "cohort-terminal.json").exists() is False


def test_partial_failure_writes_no_complete_terminal(tmp_path: Path):
    from p3_v3.prospective_applicability_census_stage1 import (
        STAGE1_TERMINAL_STATUS,
        run_stage1_census,
    )

    processor, inventory, subjects, closures = _synthetic_processor_factory(fail_ordinal=15)
    staging = tmp_path / "staging"
    with pytest.raises(EvidenceError):
        run_stage1_census(
            repo_root=tmp_path,
            output_root=tmp_path / "official",
            staging_root=staging,
            subject_processor=processor,
        )
    assert list(staging.glob("**/cohort-terminal.json")) == []
    combined = "\n".join(path.read_text(encoding="utf-8") for path in staging.rglob("*.json"))
    assert STAGE1_TERMINAL_STATUS not in combined


def test_existing_output_or_staging_fail_closed(tmp_path: Path):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census

    processor, inventory, subjects, closures = _synthetic_processor_factory()
    output = tmp_path / "official"
    staging = tmp_path / "staging"
    output.mkdir()
    with pytest.raises(EvidenceError, match="already exists"):
        run_stage1_census(
            repo_root=tmp_path,
            output_root=output,
            staging_root=staging,
            subject_processor=processor,
        )
    output.rmdir()
    staging.mkdir()
    with pytest.raises(EvidenceError, match="already exists"):
        run_stage1_census(
            repo_root=tmp_path,
            output_root=output,
            staging_root=staging,
            subject_processor=processor,
        )
    assert output.exists() is False


def test_cohort_terminal_is_last_written_file(tmp_path: Path):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census

    processor, inventory, subjects, closures = _synthetic_processor_factory()
    result = run_stage1_census(
        repo_root=tmp_path,
        output_root=tmp_path / "official",
        staging_root=tmp_path / "staging",
        subject_processor=processor,
    )
    assert result["write_order"][-1].endswith("cohort-terminal.json")
    assert len(result["write_order"]) == 141


def test_success_atomically_publishes_and_removes_staging(tmp_path: Path):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census

    processor, inventory, subjects, closures = _synthetic_processor_factory()
    output = tmp_path / "official"
    staging = tmp_path / "staging"
    run_stage1_census(
        repo_root=tmp_path,
        output_root=output,
        staging_root=staging,
        subject_processor=processor,
    )
    assert output.is_dir()
    assert staging.exists() is False
    assert (output / "cohort-terminal.json").is_file()


def test_forbidden_contract_pair_runner_seams_are_never_called(tmp_path: Path, monkeypatch):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census

    called: list[str] = []

    def fail(name):
        def inner(*args, **kwargs):
            called.append(name)
            raise AssertionError(name)

        return inner

    monkeypatch.setattr(
        "p3_v3.prospective_multiproject.process_production_subject",
        fail("process_production_subject"),
    )
    monkeypatch.setattr(
        "p3_v3.multiproject_production_processor.run_production_subject_pipeline",
        fail("run_production_subject_pipeline"),
    )
    monkeypatch.setattr(
        "p3_v3.multiproject_production_processor.freeze_production_contracts",
        fail("freeze_production_contracts"),
    )
    monkeypatch.setattr(
        "p3_v3.multiproject_production_processor.construct_production_pairs",
        fail("construct_production_pairs"),
    )
    monkeypatch.setattr(
        "p3_v3.multiproject_production_processor.execute_production_pairs",
        fail("execute_production_pairs"),
    )
    monkeypatch.setattr(
        "p3_v3.multiproject_production_processor.measure_production_overlap",
        fail("measure_production_overlap"),
    )
    processor, inventory, subjects, closures = _synthetic_processor_factory()
    run_stage1_census(
        repo_root=tmp_path,
        output_root=tmp_path / "official",
        staging_root=tmp_path / "staging",
        subject_processor=processor,
    )
    assert called == []


def test_old_v1_official_namespace_is_untouched(tmp_path: Path):
    from p3_v3.prospective_applicability_census_stage1 import (
        OLD_V1_OFFICIAL_RELDIR,
        OLD_V1_STAGING_RELDIR,
        run_stage1_census,
    )

    processor, inventory, subjects, closures = _synthetic_processor_factory()
    run_stage1_census(
        repo_root=tmp_path,
        output_root=tmp_path / "official",
        staging_root=tmp_path / "staging",
        subject_processor=processor,
    )
    assert (tmp_path / OLD_V1_OFFICIAL_RELDIR).exists() is False
    assert (tmp_path / OLD_V1_STAGING_RELDIR).exists() is False
```

### 4.2 Task 2 controller implementation

Add these functions to the Stage I module.

```python
import os

from p3_v3.artifacts import file_sha256, write_canonical_json
from p3_v3.prospective_multiproject import load_frozen_successors


def stage1_subject_directory(root: Path, ordinal: int, controlled_subject_id: str) -> Path:
    return Path(root) / "subjects" / f"{ordinal:02d}-{controlled_subject_id}"


def write_stage1_closure(
    path: Path,
    closure: Mapping[str, Any],
    write_log: list[Path],
) -> None:
    write_canonical_json(path, closure, exclusive=True)
    write_log.append(Path(path))


def publish_stage1_official(*, staging_root: Path, output_root: Path) -> None:
    if Path(output_root).exists():
        raise EvidenceError("E_STAGE1_FAIL_CLOSED", f"official path already exists: {output_root}")
    os.replace(Path(staging_root), Path(output_root))


def run_stage1_census(
    *,
    repo_root: Path,
    output_root: Path,
    staging_root: Path,
    subject_processor: Callable[..., Mapping[str, Any]],
) -> dict[str, Any]:
    official = Path(output_root)
    staging = Path(staging_root)
    if official.exists() or staging.exists():
        raise EvidenceError("E_STAGE1_FAIL_CLOSED", "official or staging path already exists")
    successors = load_frozen_successors()
    ordinals = [item.successor_ordinal for item in successors]
    if ordinals != list(STAGE1_ORDINALS):
        raise EvidenceError("E_STAGE1_IDENTITY", "frozen successors must be ordinals 9-22")
    if 8 in ordinals:
        raise EvidenceError("E_STAGE1_IDENTITY", "ordinal 8 is excluded from Stage I")
    staging.mkdir(parents=True)
    write_log: list[Path] = []
    subject_rows: list[dict[str, Any]] = []
    all_closures: list[list[dict[str, Any]]] = []
    try:
        for successor in successors:
            if successor.successor_ordinal == 8:
                raise EvidenceError("E_STAGE1_IDENTITY", "ordinal 8 is excluded from Stage I")
            produced = subject_processor(successor, repo_root=Path(repo_root))
            closures = [dict(item) for item in produced["closures"]]
            if len(closures) != STAGE1_CLOSURES_PER_SUBJECT:
                raise EvidenceError("E_STAGE1_TERMINAL", "each subject must have 10 closures")
            directory = stage1_subject_directory(
                staging,
                int(successor.successor_ordinal),
                str(successor.controlled_subject_id),
            )
            directory.mkdir(parents=True)
            for closure in closures:
                target = directory / f"{closure['slot_id']}.json"
                write_stage1_closure(target, closure, write_log)
            subject_rows.append(produced)
            all_closures.append(closures)
        if len(subject_rows) != STAGE1_SUBJECT_COUNT:
            raise EvidenceError("E_STAGE1_TERMINAL", "subject count must be 14")
        inventory = {"slots": []}
        for produced in subject_rows:
            for closure, family, slot_ordinal in zip(
                produced["closures"],
                [family for family in INVENTORY_FAMILY_ORDER for _slot in (0, 1)],
                [0, 1] * 5,
                strict=True,
            ):
                inventory["slots"].append({
                    "controlled_subject_id": produced["controlled_subject_id"],
                    "permitted_construction_mechanism": "CE",
                    "semantic_contract_family": family,
                    "slot_id": closure["slot_id"],
                    "slot_ordinal": slot_ordinal,
                })
        terminal = build_stage1_terminal(
            design_commit=STAGE1_DESIGN_COMMIT,
            design_file_sha256=STAGE1_DESIGN_FILE_SHA256,
            controller_source_sha256=file_sha256(Path(repo_root) / STAGE1_CONTROLLER_RELPATH)
            if (Path(repo_root) / STAGE1_CONTROLLER_RELPATH).is_file()
            else file_sha256(STAGE1_CONTROLLER_RELPATH),
            applicability_authority_artifact_sha256=STAGE1_APPLICABILITY_AUTHORITY_ARTIFACT_SHA256,
            slot_inventory_artifact_sha256=STAGE1_SLOT_INVENTORY_ARTIFACT_SHA256,
            project_cluster_authority_artifact_sha256=STAGE1_PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256,
            subjects=subject_rows,
        )
        validate_stage1_terminal(
            terminal,
            expected_design_commit=STAGE1_DESIGN_COMMIT,
            expected_design_file_sha256=STAGE1_DESIGN_FILE_SHA256,
            expected_controller_source_sha256=terminal["controller_source_sha256"],
            expected_applicability_authority_artifact_sha256=STAGE1_APPLICABILITY_AUTHORITY_ARTIFACT_SHA256,
            expected_slot_inventory_artifact_sha256=STAGE1_SLOT_INVENTORY_ARTIFACT_SHA256,
            expected_project_cluster_authority_artifact_sha256=STAGE1_PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256,
            subject_closures=all_closures,
            inventory=inventory,
        )
        terminal_path = staging / STAGE1_TERMINAL_FILENAME
        write_canonical_json(terminal_path, terminal, exclusive=True)
        write_log.append(terminal_path)
        if write_log[-1].name != STAGE1_TERMINAL_FILENAME:
            raise EvidenceError("E_STAGE1_TERMINAL", "terminal must be the last written file")
        if len(write_log) != STAGE1_CLOSURE_COUNT + 1:
            raise EvidenceError("E_STAGE1_TERMINAL", "staging must contain 140 closures and 1 terminal")
        publish_stage1_official(staging_root=staging, output_root=official)
    except Exception:
        if official.exists():
            raise EvidenceError("E_STAGE1_FAIL_CLOSED", "official namespace written after failure")
        raise
    if staging.exists():
        raise EvidenceError("E_STAGE1_FAIL_CLOSED", "staging sibling remained after publication")
    return {
        "status": STAGE1_TERMINAL_STATUS,
        "official_root": str(official),
        "subject_count": STAGE1_SUBJECT_COUNT,
        "closure_count": STAGE1_CLOSURE_COUNT,
        "write_order": [str(path) for path in write_log],
        "terminal": terminal,
    }
```

`process_stage1_subject` must compose only the allowed seams listed in §1.
Copy this exact body:

```python
def process_stage1_subject(successor, *, repo_root: Path) -> dict[str, Any]:
    import json

    from p3_v3.applicability_predicates import (
        close_slot_with_authority,
        load_applicability_authority,
    )
    from p3_v3.multiproject_production_processor import (
        _pbf_path,
        _subject_inventory_rows,
        canonicalize_production_sites,
        freeze_subject_identity,
        inspect_regular_identity_file,
        recover_production_source,
    )

    if successor.successor_ordinal == 8:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal 8 is excluded from Stage I")
    root = Path(repo_root)
    binding = freeze_subject_identity(successor, root)
    recover_production_source(binding, root)
    authority = load_applicability_authority(
        manifest_path=root / STAGE1_AUTHORITY_RELPATH,
        registry_path=root / STAGE1_PREDICATE_REGISTRY_RELPATH,
        inventory_path=root / STAGE1_INVENTORY_RELPATH,
        slot_implementation_path=root / STAGE1_SLOT_IMPLEMENTATION_RELPATH,
        predicate_implementation_path=root / STAGE1_PREDICATE_IMPLEMENTATION_RELPATH,
    )
    rows = sort_stage1_inventory_rows(
        _subject_inventory_rows(authority["inventory"], successor.controlled_subject_id)
    )
    pbf_path = _pbf_path(root, successor.neutral_snapshot_id)
    inspect_regular_identity_file(pbf_path)
    frame = json.loads(pbf_path.read_text(encoding="utf-8"))
    canonical_sites = canonicalize_production_sites(
        successor.controlled_subject_id,
        frame["sites"],
        frozen_controlled_subject_id=successor.controlled_subject_id,
    )
    closures = [
        close_slot_with_authority(authority, row, canonical_sites, frame) for row in rows
    ]
    return {
        "successor_ordinal": successor.successor_ordinal,
        "neutral_snapshot_id": successor.neutral_snapshot_id,
        "controlled_subject_source_id": successor.controlled_subject_source_id,
        "controlled_subject_id": successor.controlled_subject_id,
        "project_cluster_key": binding.project_cluster_key,
        "closures": closures,
    }
```

If `_pbf_path` cannot be imported because it is private and missing from the
module export surface, import the same helper from
`p3_v3.multiproject_production_processor` by name; do not copy PBF reading
into a new schema. Do not modify the processor module unless that import is
impossible.

Controller-source SHA in tests: `run_stage1_census` may hash the already
created Stage I module file. Tests must not require a real worktree official
namespace.

The inventory rebuilt inside `run_stage1_census` is derived from the synthetic
processor's own slot ids and the frozen family × ordinal zipper. That keeps
Task 2 tests independent of real site predicates while still exercising the
validator's order check.

- [ ] Append the Task 2 tests to the Stage I test file
- [ ] Run the Task 2 RED command and keep the failing exit
- [ ] Implement `run_stage1_census` and `process_stage1_subject`
- [ ] Run the Task 2 GREEN command and require 25 passed
- [ ] Commit and push only the Task 2 files

### 4.3 RED

```bash
cd /tmp/p3-c3-ordinal9-22-source-recovery
PYTHONPATH=src python3 -m pytest -q \
  tests/p3_v3/test_prospective_applicability_census_stage1.py::test_run_stage1_census_fixed_order_9_to_22 \
  tests/p3_v3/test_prospective_applicability_census_stage1.py::test_nth_subject_failure_keeps_partial_staging_without_official \
  tests/p3_v3/test_prospective_applicability_census_stage1.py::test_success_atomically_publishes_and_removes_staging
```

Expected failure: `ImportError` for `run_stage1_census` or `EvidenceError:
E_STAGE1_FAIL_CLOSED`. Exit code `1`.

### 4.4 GREEN

```bash
cd /tmp/p3-c3-ordinal9-22-source-recovery
PYTHONPATH=src python3 -m pytest -q tests/p3_v3/test_prospective_applicability_census_stage1.py
git diff --check
```

Expected: `25 passed`. Exit code `0`. `git diff --check` is silent.

### 4.5 Task 2 commit

```bash
git add \
  src/p3_v3/prospective_applicability_census_stage1.py \
  tests/p3_v3/test_prospective_applicability_census_stage1.py
git diff --cached --check
git commit -m "$(cat <<'EOF'
feat(p3-v3): add Stage I census controller and atomic publish

Write 140 synthetic-validated closures into an exclusive staging
namespace and publish one Stage I terminal only after 14/14 completion.
Official Stage I execution remains unauthorized.
EOF
)"
git push -u origin cursor/content-addressed-source-join-b65d
```

---

## 5. Task 3: Zero-argument CLI, focused regression, and Slice B boundary

**Files:**

| Role | Path |
|---|---|
| Create | `scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py` |
| Modify | `tests/p3_v3/test_prospective_applicability_census_stage1.py` |
| Modify | none of the old v1 controller or processor files |

**Consumes:**

- Task 2 `run_stage1_census`
- Task 2 `process_stage1_subject` as the unique production seam name
- frozen constants from §2

**Produces:**

- `unauthorized_stage1_status`
- `main`

### 5.1 CLI implementation

Create `scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py`
with this complete file:

```python
#!/usr/bin/env python3
"""Fail-closed Stage I CLI. Official execution remains unauthorized."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _path in (_REPO_ROOT, _REPO_ROOT / "src"):
    _text = str(_path)
    if _text not in sys.path:
        sys.path.insert(0, _text)

from p3_v3.artifacts import canonical_json_bytes
from p3_v3.prospective_applicability_census_stage1 import (
    OFFICIAL_RUN_AUTHORIZED,
    STAGE1_DESIGN_COMMIT,
    STAGE1_OFFICIAL_RELDIR,
    STAGE1_SLICE_ID,
    STAGE1_STAGING_RELDIR,
    STAGE1_SUBJECT_COUNT,
    process_stage1_subject,
    run_stage1_census,
)


def unauthorized_stage1_status() -> dict[str, object]:
    return {
        "status": "STAGE1_OFFICIAL_RUN_NOT_AUTHORIZED",
        "slice_id": STAGE1_SLICE_ID,
        "design_commit": STAGE1_DESIGN_COMMIT,
        "official_run_authorized": False,
        "official_terminal_written": False,
        "successor_count": STAGE1_SUBJECT_COUNT,
    }


def main() -> int:
    if len(sys.argv) != 1:
        sys.stdout.buffer.write(canonical_json_bytes({
            "status": "PREFLIGHT_FAIL",
            "slice_id": STAGE1_SLICE_ID,
            "official_terminal_written": False,
        }))
        return 2
    if OFFICIAL_RUN_AUTHORIZED is not True:
        sys.stdout.buffer.write(canonical_json_bytes(unauthorized_stage1_status()))
        return 2
    root = Path(__file__).resolve().parents[2]
    run_stage1_census(
        repo_root=root,
        output_root=root / STAGE1_OFFICIAL_RELDIR,
        staging_root=root / STAGE1_STAGING_RELDIR,
        subject_processor=process_stage1_subject,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The unique future official command, recorded here and not executed by Slice A:

```bash
PYTHONPATH=src python3 \
  scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py
```

### 5.2 Task 3 additional tests

Append these functions to the Stage I test file.

```python
import json
import subprocess
import sys

from scripts.p3_v3.run_prospective_multiproject_applicability_stage1_v2 import main


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_cli_rejects_user_arguments(monkeypatch, capsys):
    from scripts.p3_v3 import run_prospective_multiproject_applicability_stage1_v2 as cli

    called = []
    monkeypatch.setattr(
        cli,
        "run_stage1_census",
        lambda **kwargs: called.append(kwargs),
    )
    for argv in (
        ["--help"],
        ["--order", "9"],
        ["--max-attempts", "14"],
        ["--output", "/tmp"],
        ["--resume"],
        ["--retry"],
    ):
        monkeypatch.setattr(sys, "argv", ["run_stage1.py", *argv])
        assert main() == 2
    assert called == []
    payload = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert payload["status"] == "PREFLIGHT_FAIL"
    assert payload["official_terminal_written"] is False


def test_cli_unauthorized_zero_args_stable_json(monkeypatch, capsys):
    from p3_v3.prospective_applicability_census_stage1 import OFFICIAL_RUN_AUTHORIZED
    from scripts.p3_v3 import run_prospective_multiproject_applicability_stage1_v2 as cli

    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "status": "STAGE1_OFFICIAL_RUN_NOT_AUTHORIZED",
        "slice_id": "p3-c3-prospective-multiproject-applicability-stage1-v2",
        "design_commit": "270025608be7db631484b77ffda181438100d785",
        "official_run_authorized": False,
        "official_terminal_written": False,
        "successor_count": 14,
    }
    assert called == []
    assert OFFICIAL_RUN_AUTHORIZED is False


def test_cli_unauthorized_does_not_create_output_or_staging():
    root = _repo_root()
    official = root / "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2"
    staging = root / "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2.staging"
    completed = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py"),
        ],
        cwd=str(root),
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout.decode("utf-8"))
    assert payload["status"] == "STAGE1_OFFICIAL_RUN_NOT_AUTHORIZED"
    assert official.exists() is False
    assert staging.exists() is False
    assert (
        root / "data/p3_v3/phase3/prospective-multiproject-paired-slice-v1"
    ).exists() is False


def test_cli_unauthorized_does_not_open_successor_site(monkeypatch, capsys):
    from scripts.p3_v3 import run_prospective_multiproject_applicability_stage1_v2 as cli

    opened: list[str] = []
    real_open = open

    def guarded_open(path, *args, **kwargs):
        text = str(path)
        if "public-behavior-frame-" in text:
            opened.append(text)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", guarded_open)
    monkeypatch.setattr(cli, "process_stage1_subject", lambda *a, **k: opened.append("processor"))
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: opened.append("census"))
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["official_terminal_written"] is False
    assert opened == []


def test_cli_authorized_path_uses_synthetic_processor_only(tmp_path: Path, monkeypatch):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census
    from scripts.p3_v3 import run_prospective_multiproject_applicability_stage1_v2 as cli

    processor, inventory, subjects, closures = _synthetic_processor_factory()
    captured: dict[str, object] = {}

    def redirected_census(*, repo_root, output_root, staging_root, subject_processor):
        del repo_root, output_root, staging_root
        captured["subject_processor"] = subject_processor
        if subject_processor is not processor:
            raise AssertionError("authorized CLI test must inject the synthetic processor")
        return run_stage1_census(
            repo_root=tmp_path,
            output_root=tmp_path / "official",
            staging_root=tmp_path / "staging",
            subject_processor=processor,
        )

    monkeypatch.setattr(cli, "OFFICIAL_RUN_AUTHORIZED", True)
    monkeypatch.setattr(cli, "process_stage1_subject", processor)
    monkeypatch.setattr(cli, "run_stage1_census", redirected_census)
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 0
    assert captured["subject_processor"] is processor
    assert (tmp_path / "official" / "cohort-terminal.json").is_file()
    assert (
        _repo_root()
        / "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2"
    ).exists() is False


def test_cli_does_not_flip_authorization_for_real_processor():
    from p3_v3.prospective_applicability_census_stage1 import OFFICIAL_RUN_AUTHORIZED
    from scripts.p3_v3.run_prospective_multiproject_applicability_stage1_v2 import (
        OFFICIAL_RUN_AUTHORIZED as CLI_FLAG,
    )

    source = (
        _repo_root() / "src/p3_v3/prospective_applicability_census_stage1.py"
    ).read_text(encoding="utf-8")
    cli_source = (
        _repo_root()
        / "scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py"
    ).read_text(encoding="utf-8")
    assert "OFFICIAL_RUN_AUTHORIZED = False" in source
    assert "OFFICIAL_RUN_AUTHORIZED = False" in cli_source
    assert "OFFICIAL_RUN_AUTHORIZED = True" not in source
    assert "OFFICIAL_RUN_AUTHORIZED = True" not in cli_source
    assert OFFICIAL_RUN_AUTHORIZED is False
    assert CLI_FLAG is False


def test_stage1_constants_match_frozen_design_identities():
    from p3_v3.prospective_applicability_census_stage1 import (
        STAGE1_APPLICABILITY_AUTHORITY_ARTIFACT_SHA256,
        STAGE1_DESIGN_COMMIT,
        STAGE1_DESIGN_FILE_SHA256,
        STAGE1_OFFICIAL_RELDIR,
        STAGE1_ORDINALS,
        STAGE1_PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256,
        STAGE1_SLICE_ID,
        STAGE1_SLOT_INVENTORY_ARTIFACT_SHA256,
        STAGE1_STAGING_RELDIR,
        STAGE1_TERMINAL_STATUS,
    )

    assert STAGE1_SLICE_ID == "p3-c3-prospective-multiproject-applicability-stage1-v2"
    assert STAGE1_TERMINAL_STATUS == "STAGE1_APPLICABILITY_CENSUS_COMPLETE"
    assert STAGE1_DESIGN_COMMIT == "270025608be7db631484b77ffda181438100d785"
    assert STAGE1_DESIGN_FILE_SHA256 == (
        "a8828022ee2095b4209261c26d0ecbab66141e59b2c9f18ce3df2045f6dd79c5"
    )
    assert STAGE1_APPLICABILITY_AUTHORITY_ARTIFACT_SHA256 == (
        "30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214"
    )
    assert STAGE1_SLOT_INVENTORY_ARTIFACT_SHA256 == (
        "5c7f2dae8b0b7fd72926e2569354dbf6e878186f69d512e259e6034026dd0e27"
    )
    assert STAGE1_PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256 == (
        "802ec9a8db866c1c1d79b29e03d4e5dc0f55d4961a3f415a2486dd562fbf810e"
    )
    assert STAGE1_ORDINALS == tuple(range(9, 23))
    assert str(STAGE1_OFFICIAL_RELDIR) == (
        "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2"
    )
    assert str(STAGE1_STAGING_RELDIR) == (
        "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2.staging"
    )
```

The authorized CLI test may monkeypatch `OFFICIAL_RUN_AUTHORIZED` only on the
CLI module object. It must replace `process_stage1_subject` with the synthetic
processor before `main()` can reach `run_stage1_census`. It must not import the
real processor under `True` and must not write into the real worktree
namespaces.

- [ ] Create the zero-argument Stage I CLI
- [ ] Append the Task 3 CLI and constant tests
- [ ] Run the Task 3 RED command and keep the failing exit
- [ ] Run the Task 3 focused GREEN command and require 39 passed
- [ ] Commit and push the CLI plus updated tests
- [ ] Record Slice A HEAD and controller SHA; stop before Slice B

### 5.3 RED

```bash
cd /tmp/p3-c3-ordinal9-22-source-recovery
PYTHONPATH=src python3 -m pytest -q \
  tests/p3_v3/test_prospective_applicability_census_stage1.py::test_cli_unauthorized_zero_args_stable_json \
  tests/p3_v3/test_prospective_applicability_census_stage1.py::test_cli_unauthorized_does_not_create_output_or_staging
```

Expected failure: `ModuleNotFoundError` for the CLI script or
`ImportError: cannot import name 'main'`. Exit code `1` or `2`.

Do not execute the official command against the real worktree.

### 5.4 GREEN

```bash
cd /tmp/p3-c3-ordinal9-22-source-recovery
PYTHONPATH=src python3 -m pytest -q \
  tests/p3_v3/test_prospective_applicability_census_stage1.py \
  tests/p3_v3/test_multiproject_production_processor.py::test_raw_pbf_sites_canonicalize_through_existing_p3_site_v1_seam \
  tests/p3_v3/test_multiproject_production_processor.py::test_malformed_raw_site_maps_to_identity_conflict_and_does_not_leak \
  tests/p3_v3/test_prospective_multiproject.py::test_load_frozen_successors_is_ordinals_9_through_22_in_v2_order \
  tests/p3_v3/test_prospective_multiproject.py::test_production_binder_rejects_user_map_ordinal_8_and_covers_ordinals_9_to_22 \
  tests/p3_v3/test_prospective_multiproject.py::test_direct_cli_process_returns_unauthorized_before_ordinal_9 \
  tests/p3_v3/test_prospective_multiproject.py::test_main_zero_args_is_preflight_only_and_does_not_write_official_terminal \
  tests/p3_v3/test_multiproject_production_processor.py::test_official_staging_absent_and_frozen_bytes_unchanged
git diff --check
```

Expected: `39 passed` (32 new Stage I tests + 7 focused regressions).
Exit code `0`. `git diff --check` is silent.

Do not run `python3 -m pytest tests/` or any other full suite.

### 5.5 Task 3 commit and push

```bash
git add \
  scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py \
  tests/p3_v3/test_prospective_applicability_census_stage1.py
git diff --cached --check
git commit -m "$(cat <<'EOF'
feat(p3-v3): add unauthorized Stage I census CLI

Add the zero-argument Stage I entry point that fail-closes before any
successor site is opened and before official or staging namespaces are
created. Official Stage I execution remains a separate Slice B.
EOF
)"
git push -u origin cursor/content-addressed-source-join-b65d
```

After Task 3, record:

```text
SLICE_A_IMPLEMENTATION_COMMIT=<git rev-parse HEAD>
STAGE1_CONTROLLER_SOURCE_SHA256=<sha256sum src/p3_v3/prospective_applicability_census_stage1.py>
```

Those two values are Slice B preflight inputs. Do not start Slice B.

---

## 6. Slice B authorization boundary

This section is not a Slice A execution step. Slice A completion must not
start it. A later human authorization is required.

1. Fix the Slice A implementation commit from Task 3 HEAD.
2. Fix the controller source SHA-256 of
   `src/p3_v3/prospective_applicability_census_stage1.py` at that commit.
3. Read-only verify 14/14 recovered archives and extracted trees, the
   applicability authority artifact, the slot inventory artifact, and the
   project-cluster binder.
4. Confirm Stage I official and staging namespaces do not exist.
5. Re-run the Task 3 focused GREEN command and require `39 passed`.
6. Independently set the Stage I `OFFICIAL_RUN_AUTHORIZED` constant to `True`
   in a separate authorization commit. Do not reuse the old v1 flag as
   authorization for Stage I.
7. Run the official command exactly once:

```bash
PYTHONPATH=src python3 \
  scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py
```

8. On FAIL or partial staging, keep the bytes as written. Do not retry,
   resume, or continue.
9. On success, verify 14 subjects, 140 `p3-slot-closure-v1` files, and exactly
   one `cohort-terminal.json` with `STAGE1_APPLICABILITY_CENSUS_COMPLETE`.
10. Commit the Stage I observation before any scientific review of counts or
    family/mechanism reconstruction.
11. Do not start Stage II, do not write Stage II namespaces, and do not change
    C3 or `n_projects`.

---

## 7. Design coverage self-audit

| Approved design requirement | Task |
|---|---|
| Slice identity `p3-c3-prospective-multiproject-applicability-stage1-v2` | Task 1 constants |
| Terminal status `STAGE1_APPLICABILITY_CENSUS_COMPLETE` | Task 1 builder/validator |
| Exact terminal keys and no extras | Task 1 |
| Ordinals exactly 9–22, 14 subjects, 10 closures, 140 total | Task 1 and Task 2 |
| Identity fields match `load_frozen_successors()` | Task 1 and Task 2 |
| Closure order is inventory family then `slot_ordinal` | Task 1 `sort_stage1_inventory_rows` |
| Closure states only `SITE_FROZEN` / `APPLICABILITY_CLOSED_NOT_APPLICABLE` | Task 1 `make_stage1_closure` |
| Counts rebuild from closures and sum to 10 | Task 1 validator |
| Self-hash uses existing `canonical_sha256` | Task 1 |
| No contract, pair, kill, eligibility, timestamp, hostname, or random fields | Task 1 |
| Fail closed if official or staging exists | Task 2 |
| Unique staging, ordinal 9→22, no early stop | Task 2 |
| Partial failure keeps staging, writes no complete terminal, no retry | Task 2 |
| Terminal is the last staging file; one `os.replace` | Task 2 |
| Staging sibling gone after success | Task 2 |
| No call to contract, pair, runner, overlap, or old v1 pipeline | Task 2 monkeypatch |
| Old v1 official namespace untouched | Task 2 and Task 3 |
| Zero-argument CLI, frozen paths, `OFFICIAL_RUN_AUTHORIZED = False` | Task 3 |
| Unauthorized CLI does not open sites or create namespaces | Task 3 |
| Slice A tests do not authorize the real processor | Task 3 |
| No Stage II implementation | all tasks |
| No new schema, manifest, or ledger | all tasks |
| No full-suite pytest | all GREEN commands |
| Next scientific progress is an official Stage I observation | §6 Slice B |

Gap-token scan required before the plan commit. Scan only §0 through §6 so the
audit list itself cannot match:

```bash
python3 - <<'PY'
from pathlib import Path
text = Path("docs/superpowers/plans/2026-08-28-p3-c3-stage1-applicability-census-implementation.md").read_text()
body = text.split("## 7. Design coverage self-audit")[0]
needles = ["TODO", "TBD", "FIXME", "添加适当测试", "实现错误处理", "类似 Task"]
hits = [item for item in needles if item in body]
print("gap_hits", hits)
print("task_headings", body.count("## 3. Task 1") + body.count("## 4. Task 2") + body.count("## 5. Task 3"))
PY
```

Required result: `gap_hits []` and `task_headings 3`.

---

## 8. Plan-only closeout

This planning task adds only this file. It does not implement Tasks 1–3.

```bash
cd /tmp/p3-c3-ordinal9-22-source-recovery
git add docs/superpowers/plans/2026-08-28-p3-c3-stage1-applicability-census-implementation.md
git diff --cached --check
git commit -m "$(cat <<'EOF'
docs(p3-v3): plan Stage I applicability census implementation

Write the executable TDD plan for the Stage I ordinal 9-22
applicability census controller. Slice A remains unauthorized to run
the official census; Stage II is out of scope.
EOF
)"
git push -u origin cursor/content-addressed-source-join-b65d
git status --porcelain=v1 --untracked-files=all
```

Unique next task after this plan is committed:

`P3_C3_STAGE1_APPLICABILITY_CENSUS_CONTROLLER_IMPLEMENTATION`

Do not write another design. Do not schedule an independent plan review.
Do not run Stage I.
