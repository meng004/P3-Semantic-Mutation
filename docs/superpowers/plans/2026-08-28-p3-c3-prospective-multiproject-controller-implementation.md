# P3 C3 Prospective Multiproject Controller Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement and validate the deterministic controller for the approved ordinal 9–22 prospective multiproject paired slice without opening successor sites or running the scientific slice.

**Spec:** `docs/superpowers/specs/2026-08-28-p3-c3-prospective-multiproject-paired-slice-design.md`

**Architecture:** One pure state-machine module owns successor identity, per-subject terminals, equal subject/project weighting rules, and the two-new-project stop. Tests drive it with a synthetic subject processor and an injected project-identity binder. A thin no-argument CLI runs preflight and then fail-closes before any official write. Atomic writers exist only for later Slice B and are proven against temporary roots.

**Tech Stack:** Python 3, existing `p3_v3` canonical artifact helpers, pytest, Git.

---

## 0. Authorization boundary

```text
STOP_AFTER_CONTROLLER_IMPLEMENTATION=true
FORMAL_MULTIPROJECT_RUN_NOT_AUTHORIZED=true
```

| Slice | Content | Authorized now | Success terminal |
|---|---|---|---|
| A | Controller, state machine, writer, CLI, synthetic/focused tests | Yes, after this plan | `MULTIPROJECT_CONTROLLER_IMPLEMENTATION_PASS` |
| B | Official ordinal 9→22 source/applicability search | **No** | later scientific terminals |

Completing Tasks 1–4 must not invoke the official zero-argument command against the real worktree namespaces. Implementation pass does not start Slice B.

C3 remains `blocked`. This plan does not modify the claim ledger or `analysis_spec.md`.

Cursor Cloud commands use `python3`, `/workspace/.venv/bin/python`, `git`, and `sha256sum`. Do not use `rtk`. Do not install packages.

---

## 1. Frozen baseline

Worktree: `/tmp/p3-c3-applicability-authority`

Branch: `cursor/ordinal8-remaining-three-paired-evidence-batch-v1-b65d`

Implementation start HEAD: `de3e7c85f3bebd7bd3efa5b30d87bddd813abc55`

Approved design SHA-256:

`fbf1291b5a0df59b6ca68af772a21491099b0a46901aa7f97c749c6ebc85439c`

Before Task 1:

```bash
cd /tmp/p3-c3-applicability-authority
git rev-parse HEAD
git status --porcelain=v1 --untracked-files=all
sha256sum docs/superpowers/specs/2026-08-28-p3-c3-prospective-multiproject-paired-slice-design.md
```

Required: HEAD equals `de3e7c85f3bebd7bd3efa5b30d87bddd813abc55` plus only this plan file until Task 1 starts. Porcelain otherwise empty. Design SHA unchanged. Otherwise stop: `WORKSPACE_CONFLICT` or `DESIGN_IDENTITY_CONFLICT`.

---

## 2. File map

Slice A may only create:

- `src/p3_v3/prospective_multiproject.py`
- `scripts/p3_v3/run_prospective_multiproject_paired_slice.py`
- `tests/p3_v3/test_prospective_multiproject.py`

Do not modify v2 controller, predicates, inventory, authority JSON, analysis spec, claim ledger, ordinal-8 artifacts, or the approved design.

Do not create a JSON Schema file, manifest, second ledger, subject closure, contract, mutant, or official/staging directory under `data/p3_v3/phase3/prospective-multiproject-paired-slice-v1/`.

If implementation needs a fourth production file or a frozen-module edit, stop: `SCIENTIFIC_DESIGN_CONFLICT`.

Reuse only:

- `EvidenceError`, `canonical_json_bytes`, `canonical_sha256`, `file_sha256`, `validate_exact_object`, `validate_sha256`, `write_canonical_json` from `src/p3_v3/artifacts.py`
- identity rows `FROZEN_SUCCESSOR_ROWS[8:22]` from `scripts/p3_v3/prospective_applicability_search_v2.py` (ordinals 9–22). Importing that module does not open a PBF.

Do not call, even from tests:

- `close_slot_with_authority`
- `run_restore_production_source`
- `build_ordinal8_contracts` / `freeze_ordinal8_package`
- `run_formal_once` / `run_controlled_pair`
- `measure_formal` / `measure_pairs`
- `read_successor_pbf`

---

## 3. Locked production interfaces

Write these types and signatures exactly. Do not add optional scientific parameters.

```python
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal

class SubjectTerminal(str, Enum):
    ALL_SLOTS_NOT_APPLICABLE = "ALL_SLOTS_NOT_APPLICABLE"
    SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT = "SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT"
    PAIR_CONSTRUCTION_UNAVAILABLE = "PAIR_CONSTRUCTION_UNAVAILABLE"
    PAIRED_EVIDENCE_COMPLETE = "PAIRED_EVIDENCE_COMPLETE"
    INFRASTRUCTURE_FAILURE = "INFRASTRUCTURE_FAILURE"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"

class CohortStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    MULTIPROJECT_TWO_NEW_PROJECTS_FOUND = "MULTIPROJECT_TWO_NEW_PROJECTS_FOUND"
    MULTIPROJECT_COHORT_EXHAUSTED = "MULTIPROJECT_COHORT_EXHAUSTED"
    INFRASTRUCTURE_FAILURE = "INFRASTRUCTURE_FAILURE"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"

FUNNEL_TERMINALS = frozenset({
    SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE,
    SubjectTerminal.SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT,
    SubjectTerminal.PAIR_CONSTRUCTION_UNAVAILABLE,
})
FAILURE_TERMINALS = frozenset({
    SubjectTerminal.INFRASTRUCTURE_FAILURE,
    SubjectTerminal.IDENTITY_CONFLICT,
})
SCIENTIFIC_COHORT_TERMINALS = frozenset({
    CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND,
    CohortStatus.MULTIPROJECT_COHORT_EXHAUSTED,
})

@dataclass(frozen=True)
class SuccessorIdentity:
    successor_ordinal: int
    neutral_snapshot_id: str
    controlled_subject_source_id: str
    controlled_subject_id: str

@dataclass(frozen=True)
class Ordinal8RetainedObservation:
    successor_ordinal: int
    neutral_snapshot_id: str
    controlled_subject_source_id: str
    controlled_subject_id: str
    project_cluster_key: str
    pair_count: int
    semantic_pair_kills: int
    syntactic_pair_kills: int
    d_subject: float
    normalized_patch_overlap_numerator: int
    normalized_patch_overlap_denominator: int
    mutant_tree_overlap_numerator: int
    mutant_tree_overlap_denominator: int
    rerun_forbidden: bool

@dataclass(frozen=True)
class SubjectPipelineResult:
    successor_ordinal: int
    project_cluster_key: str
    subject_terminal: SubjectTerminal
    pair_count: int

@dataclass(frozen=True)
class AttemptedSubject:
    successor_ordinal: int
    neutral_snapshot_id: str
    controlled_subject_source_id: str
    controlled_subject_id: str
    project_cluster_key: str
    subject_terminal: SubjectTerminal
    pair_count: int

@dataclass(frozen=True)
class CohortState:
    successors: tuple[SuccessorIdentity, ...]
    ordinal8: Ordinal8RetainedObservation
    attempted: tuple[AttemptedSubject, ...]
    status: CohortStatus
    completed_new_project_keys: tuple[str, ...]

@dataclass(frozen=True)
class SearchResult:
    status: CohortStatus
    attempted: tuple[AttemptedSubject, ...]
    completed_new_project_keys: tuple[str, ...]
    official_terminal_written: bool
    terminal: dict[str, object] | None
    opened_ordinals: tuple[int, ...]

ProjectIdentityBinder = Callable[[SuccessorIdentity], str]
SubjectProcessor = Callable[[SuccessorIdentity], SubjectPipelineResult]
SubjectWriter = Callable[[AttemptedSubject], None]
TerminalWriter = Callable[[Mapping[str, object]], None]

def load_frozen_successors(
    *,
    v2_rows: Sequence[Mapping[str, object]] | None = None,
) -> tuple[SuccessorIdentity, ...]: ...

def load_ordinal8_retained_observation(
    repo_root: Path,
    *,
    project_cluster_key: str,
) -> Ordinal8RetainedObservation: ...

def initial_cohort_state(
    successors: Sequence[SuccessorIdentity],
    ordinal8: Ordinal8RetainedObservation,
) -> CohortState: ...

def advance_multiproject_state(
    state: CohortState,
    result: SubjectPipelineResult,
) -> CohortState: ...

def run_multiproject_search(
    *,
    process_subject: SubjectProcessor,
    bind_project: ProjectIdentityBinder,
    ordinal8: Ordinal8RetainedObservation,
    successors: Sequence[SuccessorIdentity] | None = None,
    write_subject: SubjectWriter | None = None,
    write_terminal: TerminalWriter | None = None,
    controller_source_sha256: str | None = None,
) -> SearchResult: ...

def build_cohort_terminal(
    *,
    state: CohortState,
    controller_source_sha256: str,
) -> dict[str, object]: ...

def validate_cohort_terminal(
    terminal: Mapping[str, object],
    *,
    controller_source_sha256: str,
    successors: Sequence[SuccessorIdentity],
    ordinal8: Ordinal8RetainedObservation,
) -> dict[str, object]: ...

def write_subject_record(
    *,
    staging_subject: Path,
    official_subject: Path,
    record: Mapping[str, object],
) -> None: ...

def write_official_cohort_terminal(
    *,
    staging_terminal: Path,
    official_terminal: Path,
    terminal: Mapping[str, object],
    controller_source_sha256: str,
    successors: Sequence[SuccessorIdentity],
    ordinal8: Ordinal8RetainedObservation,
) -> None: ...

def validate_multiproject_preflight(
    *,
    repo_root: Path,
    controller_path: Path,
) -> dict[str, object]: ...

def main() -> int: ...
```

`main()` lives in `scripts/p3_v3/run_prospective_multiproject_paired_slice.py` and re-exports the module functions. It accepts no argv.

`load_frozen_successors` must not accept order, max attempts, replacement, subject ID, or project. If `v2_rows` is omitted, it imports `FROZEN_SUCCESSOR_ROWS` from the existing v2 controller and keeps ordinals 9–22 in that order. A mismatch is `IDENTITY_CONFLICT`.

`run_multiproject_search(..., successors=None)` loads the frozen 14-row table. Tests may pass an already-loaded frozen tuple. They must not pass a reordered, truncated, or extra-ordinal table; the function rejects any such tuple with `IDENTITY_CONFLICT`.

---

## 4. Locked constants and exact objects

```python
SLICE_ID = "p3-c3-prospective-multiproject-paired-slice-v1"
DESIGN_COMMIT = "de3e7c85f3bebd7bd3efa5b30d87bddd813abc55"
DESIGN_FILE_SHA256 = "fbf1291b5a0df59b6ca68af772a21491099b0a46901aa7f97c749c6ebc85439c"
AUTHORITY_ARTIFACT_SHA256 = "30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214"
ORDINAL8_HANDOFF_ARTIFACT_SHA256 = (
    "a846ca2edded55ed48e0e9071a9aa218efc3dbcc9bd302a77ceb53bce9d822c5"
)
ORDINAL8_OVERLAP_ARTIFACT_SHA256 = (
    "f4ca00694f4a3a0a63df151bf7cce96a66ae957d0d11d85ca056cb0e6b438071"
)
MAXIMUM_ATTEMPTS = 14
MAX_PAIRS_PER_SUBJECT = 4
FIRST_SUCCESSOR_ORDINAL = 9
LAST_SUCCESSOR_ORDINAL = 22
OFFICIAL_RUN_AUTHORIZED = False
C3_STATUS = "blocked"
C3_UPGRADE_CONDITION = "RQ2 paired evidence and uncertainty accounting complete"
TERMINAL_SCHEMA_VERSION = "p3-c3-prospective-multiproject-paired-slice-v1-terminal-v1"
OFFICIAL_RELDIR = Path("data/p3_v3/phase3/prospective-multiproject-paired-slice-v1")
STAGING_RELDIR = Path("data/p3_v3/phase3/prospective-multiproject-paired-slice-v1.staging")
DESIGN_RELPATH = Path(
    "docs/superpowers/specs/2026-08-28-p3-c3-prospective-multiproject-paired-slice-design.md"
)
AUTHORITY_RELPATH = Path("data/p3_v3/phase2/applicability-authority.json")
HANDOFF_RELPATH = Path("data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json")
OVERLAP_RELPATH = Path("data/p3_v3/phase3/ordinal8-exact-overlap-v1/exact-overlap.json")
CONTROLLER_RELPATH = Path("src/p3_v3/prospective_multiproject.py")
CLI_RELPATH = Path("scripts/p3_v3/run_prospective_multiproject_paired_slice.py")
```

Official future paths, recorded only; do not create them in Slice A production runs:

```text
data/p3_v3/phase3/prospective-multiproject-paired-slice-v1/
data/p3_v3/phase3/prospective-multiproject-paired-slice-v1/cohort-terminal.json
data/p3_v3/phase3/prospective-multiproject-paired-slice-v1/subjects/<neutral_snapshot_id>/subject-record.json
data/p3_v3/phase3/prospective-multiproject-paired-slice-v1.staging/
```

Cohort terminal exact keys, no extras, `artifact_sha256 = canonical_sha256(body without artifact_sha256)`:

```text
schema_version
slice_id
design_commit
design_file_sha256
authority_artifact_sha256
controller_source_sha256
ordinal8_handoff_artifact_sha256
ordinal8_overlap_artifact_sha256
ordinal8_retained
terminal_status
attempted_subjects
completed_new_project_keys
artifact_sha256
```

`terminal_status` is exactly `MULTIPROJECT_TWO_NEW_PROJECTS_FOUND` or `MULTIPROJECT_COHORT_EXHAUSTED`. `INFRASTRUCTURE_FAILURE` and `IDENTITY_CONFLICT` must not appear in an official terminal.

`ordinal8_retained` exact keys:

```text
successor_ordinal = 8
neutral_snapshot_id = 4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b
controlled_subject_source_id = 667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0
controlled_subject_id = 0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48
project_cluster_key
pair_count = 4
semantic_pair_kills = 4
syntactic_pair_kills = 3
d_subject = 0.25
normalized_patch_overlap_numerator = 0
normalized_patch_overlap_denominator = 4
mutant_tree_overlap_numerator = 0
mutant_tree_overlap_denominator = 4
rerun_forbidden = true
```

`project_cluster_key` is supplied by the binder for that frozen snapshot. Tests use an opaque synthetic string. The controller must not invent a production repository URL table.

Each `attempted_subjects` row exact keys:

```text
successor_ordinal, neutral_snapshot_id, controlled_subject_source_id,
controlled_subject_id, project_cluster_key, subject_terminal, pair_count
```

Stop rule, mechanical:

1. Start with ordinal 8 retained. Its project key is never a new project.
2. Process ordinals 9→22 in order, at most 14 times.
3. Funnel terminals stay in `attempted` and continue.
4. `PAIRED_EVIDENCE_COMPLETE` requires `1 <= pair_count <= 4`. Its project key, if different from ordinal 8 and from already completed new keys, is appended to `completed_new_project_keys`.
5. A second distinct non-NumPy project key stops immediately as `MULTIPROJECT_TWO_NEW_PROJECTS_FOUND`.
6. Two complete subjects with the same key count as one project.
7. After ordinal 22 with fewer than two new keys: `MULTIPROJECT_COHORT_EXHAUSTED`.
8. `INFRASTRUCTURE_FAILURE` or `IDENTITY_CONFLICT` stops the slice, keeps staging residue, and writes no official terminal.
9. Pair count is not chosen from kill, overlap, or success rate. `pair_count > 4` or `PAIRED_EVIDENCE_COMPLETE` with `pair_count < 1` is `IDENTITY_CONFLICT`.

Project-identity binder: Slice A binds the key as a required injected function. Production CLI must not accept a user map. Official reconstruction of originating P12 repository identity is Slice B work. Slice A official `main()` must not open the P12 inventory, a PBF, or a successor archive.

No design gap: the approved design plus this plan's mandated paths and bindings uniquely determine the terminal object. This plan does not add a scientific rule.

---

## 5. Slice A / Slice B isolation

Slice A may import frozen identity rows and hash regular files. It may not parse successor PBF `sites`, restore source, close a real slot, freeze a contract, build a mutant, or write the official multiproject namespace.

`OFFICIAL_RUN_AUTHORIZED` is `False`. `main()` runs preflight, then returns status `MULTIPROJECT_OFFICIAL_RUN_NOT_AUTHORIZED` without calling `process_subject` on ordinals 9–22 and without writing `cohort-terminal.json`.

Focused verification is only:

```text
tests/p3_v3/test_prospective_multiproject.py
tests/p3_v3/test_prospective_applicability_search_v2.py::test_main_rejects_help_and_extra_arguments
tests/p3_v3/test_applicability_authority.py::test_project_controlled_subject_ids_sorts_35_unique_sha256
```

Do not run full pytest, compilers, subjects, profiling, paired runners, source recovery, or a package manager.

Later model split:

- state machine, writer, CLI, focused tests: `gpt-5.6-terra` / medium
- official Slice B run: `gpt-5.6-luna` / low
- post-run multi-project interpretation: `gpt-5.6-sol` / high

---

## 6. Test runtime

```text
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest <args>
```

If that interpreter cannot import pytest:

```text
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=src python3 -m pytest <args>
```

If both fail: `TEST_RUNTIME_UNAVAILABLE`. Do not install dependencies.

---

### Task 1: Freeze successors and the pure state machine

**Creates:** `src/p3_v3/prospective_multiproject.py`, `tests/p3_v3/test_prospective_multiproject.py`

**Modifies:** nothing else

**Tests:** `tests/p3_v3/test_prospective_multiproject.py`

**Consumes:** approved design table; v2 `FROZEN_SUCCESSOR_ROWS` ordinals 9–22; `EvidenceError`

**Produces:** types in §3; `load_frozen_successors`; `initial_cohort_state`; `advance_multiproject_state`; `run_multiproject_search` without writers

- [ ] **Step 1: Write the failing state-machine tests**

Create `tests/p3_v3/test_prospective_multiproject.py` with this exact body.

```python
from __future__ import annotations

import hashlib
from collections.abc import Mapping

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.prospective_multiproject import (
    FIRST_SUCCESSOR_ORDINAL,
    LAST_SUCCESSOR_ORDINAL,
    MAX_PAIRS_PER_SUBJECT,
    MAXIMUM_ATTEMPTS,
    CohortStatus,
    Ordinal8RetainedObservation,
    SubjectPipelineResult,
    SubjectTerminal,
    SuccessorIdentity,
    advance_multiproject_state,
    initial_cohort_state,
    load_frozen_successors,
    run_multiproject_search,
)


def _key(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _ordinal8(project_cluster_key: str = "numpy-readonly") -> Ordinal8RetainedObservation:
    return Ordinal8RetainedObservation(
        successor_ordinal=8,
        neutral_snapshot_id="4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b",
        controlled_subject_source_id="667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0",
        controlled_subject_id="0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48",
        project_cluster_key=project_cluster_key,
        pair_count=4,
        semantic_pair_kills=4,
        syntactic_pair_kills=3,
        d_subject=0.25,
        normalized_patch_overlap_numerator=0,
        normalized_patch_overlap_denominator=4,
        mutant_tree_overlap_numerator=0,
        mutant_tree_overlap_denominator=4,
        rerun_forbidden=True,
    )


def _result(
    ordinal: int,
    terminal: SubjectTerminal,
    project: str,
    pair_count: int = 0,
) -> SubjectPipelineResult:
    if terminal is SubjectTerminal.PAIRED_EVIDENCE_COMPLETE and pair_count == 0:
        pair_count = 1
    return SubjectPipelineResult(
        successor_ordinal=ordinal,
        project_cluster_key=project,
        subject_terminal=terminal,
        pair_count=pair_count,
    )


def _binder(table: Mapping[int, str]):
    def bind(successor: SuccessorIdentity) -> str:
        return table[successor.successor_ordinal]

    return bind


def _processor(table: Mapping[int, SubjectPipelineResult], seen: list[int]):
    def process(successor: SuccessorIdentity) -> SubjectPipelineResult:
        seen.append(successor.successor_ordinal)
        return table[successor.successor_ordinal]

    return process


def test_load_frozen_successors_is_ordinals_9_through_22_in_v2_order():
    rows = load_frozen_successors()
    assert [row.successor_ordinal for row in rows] == list(range(9, 23))
    assert len(rows) == MAXIMUM_ATTEMPTS == 14
    assert rows[0].successor_ordinal == FIRST_SUCCESSOR_ORDINAL
    assert rows[-1].successor_ordinal == LAST_SUCCESSOR_ORDINAL
    assert rows[0].neutral_snapshot_id == (
        "24ab4a18534a3125f49060cc83fca0ea4c66646f701eb5e4091097a7ae1f9d8b"
    )
    assert rows[-1].neutral_snapshot_id == (
        "494c35cb94f9fd4db2559ad0c7da45f54ca17ac5b3a8ab8d481142b1349280de"
    )


def test_load_frozen_successors_rejects_reordered_or_replaced_v2_rows():
    from scripts.p3_v3.prospective_applicability_search_v2 import FROZEN_SUCCESSOR_ROWS

    swapped = list(FROZEN_SUCCESSOR_ROWS)
    swapped[8], swapped[9] = swapped[9], swapped[8]
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        load_frozen_successors(v2_rows=swapped)


def test_funnel_terminals_continue_and_keep_the_subject():
    successors = load_frozen_successors()
    state = initial_cohort_state(successors, _ordinal8())
    for terminal in (
        SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE,
        SubjectTerminal.SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT,
        SubjectTerminal.PAIR_CONSTRUCTION_UNAVAILABLE,
    ):
        state = advance_multiproject_state(
            state, _result(state.successors[len(state.attempted)].successor_ordinal, terminal, "p-a")
        )
        assert state.status is CohortStatus.IN_PROGRESS
    assert [row.subject_terminal for row in state.attempted] == [
        SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE,
        SubjectTerminal.SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT,
        SubjectTerminal.PAIR_CONSTRUCTION_UNAVAILABLE,
    ]


def test_first_complete_project_does_not_stop():
    successors = load_frozen_successors()
    state = initial_cohort_state(successors, _ordinal8())
    state = advance_multiproject_state(
        state, _result(9, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "proj-a", 2)
    )
    assert state.status is CohortStatus.IN_PROGRESS
    assert state.completed_new_project_keys == ("proj-a",)


def test_second_distinct_non_numpy_project_stops_immediately():
    successors = load_frozen_successors()
    state = initial_cohort_state(successors, _ordinal8("numpy-readonly"))
    state = advance_multiproject_state(
        state, _result(9, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "proj-a", 1)
    )
    state = advance_multiproject_state(
        state, _result(10, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "proj-b", 3)
    )
    assert state.status is CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND
    assert state.completed_new_project_keys == ("proj-a", "proj-b")


def test_same_repository_is_not_a_second_project():
    successors = load_frozen_successors()
    state = initial_cohort_state(successors, _ordinal8())
    state = advance_multiproject_state(
        state, _result(9, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "same-repo", 1)
    )
    state = advance_multiproject_state(
        state, _result(10, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "same-repo", 4)
    )
    assert state.status is CohortStatus.IN_PROGRESS
    assert state.completed_new_project_keys == ("same-repo",)


def test_numpy_project_is_not_a_new_project():
    successors = load_frozen_successors()
    numpy_key = "numpy-readonly"
    state = initial_cohort_state(successors, _ordinal8(numpy_key))
    state = advance_multiproject_state(
        state, _result(9, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, numpy_key, 2)
    )
    assert state.status is CohortStatus.IN_PROGRESS
    assert state.completed_new_project_keys == ()


def test_infrastructure_and_identity_failure_stop_without_scientific_status():
    successors = load_frozen_successors()
    infra = advance_multiproject_state(
        initial_cohort_state(successors, _ordinal8()),
        _result(9, SubjectTerminal.INFRASTRUCTURE_FAILURE, "p-a"),
    )
    conflict = advance_multiproject_state(
        initial_cohort_state(successors, _ordinal8()),
        _result(9, SubjectTerminal.IDENTITY_CONFLICT, "p-a"),
    )
    assert infra.status is CohortStatus.INFRASTRUCTURE_FAILURE
    assert conflict.status is CohortStatus.IDENTITY_CONFLICT


def test_pair_budget_rejects_more_than_four_or_complete_with_zero():
    successors = load_frozen_successors()
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        advance_multiproject_state(
            initial_cohort_state(successors, _ordinal8()),
            _result(9, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "p-a", MAX_PAIRS_PER_SUBJECT + 1),
        )
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        advance_multiproject_state(
            initial_cohort_state(successors, _ordinal8()),
            SubjectPipelineResult(
                successor_ordinal=9,
                project_cluster_key="p-a",
                subject_terminal=SubjectTerminal.PAIRED_EVIDENCE_COMPLETE,
                pair_count=0,
            ),
        )


def test_run_search_uses_9_to_22_stops_on_second_project_and_never_opens_23():
    seen: list[int] = []
    table = {
        ordinal: _result(ordinal, SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE, f"p-{ordinal}")
        for ordinal in range(9, 23)
    }
    table[12] = _result(12, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "proj-a", 1)
    table[15] = _result(15, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "proj-b", 2)
    result = run_multiproject_search(
        process_subject=_processor(table, seen),
        bind_project=_binder({ordinal: f"p-{ordinal}" for ordinal in range(9, 23)}),
        ordinal8=_ordinal8(),
    )
    assert seen == list(range(9, 16))
    assert 23 not in seen
    assert 8 not in seen
    assert result.status is CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND
    assert result.official_terminal_written is False
    assert result.opened_ordinals == tuple(range(9, 16))


def test_run_search_exhausts_exactly_9_through_22():
    seen: list[int] = []
    table = {
        ordinal: _result(ordinal, SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE, f"p-{ordinal}")
        for ordinal in range(9, 23)
    }
    result = run_multiproject_search(
        process_subject=_processor(table, seen),
        bind_project=_binder({ordinal: f"p-{ordinal}" for ordinal in range(9, 23)}),
        ordinal8=_ordinal8(),
    )
    assert seen == list(range(9, 23))
    assert result.status is CohortStatus.MULTIPROJECT_COHORT_EXHAUSTED
    assert [row.successor_ordinal for row in result.attempted] == list(range(9, 23))


def test_run_search_failure_does_not_continue_or_write_terminal():
    seen: list[int] = []
    table = {
        9: _result(9, SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE, "p-9"),
        10: _result(10, SubjectTerminal.INFRASTRUCTURE_FAILURE, "p-10"),
        11: _result(11, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "proj-a", 1),
    }
    result = run_multiproject_search(
        process_subject=_processor(table, seen),
        bind_project=_binder({9: "p-9", 10: "p-10", 11: "p-11"}),
        ordinal8=_ordinal8(),
    )
    assert seen == [9, 10]
    assert result.status is CohortStatus.INFRASTRUCTURE_FAILURE
    assert result.terminal is None
    assert result.official_terminal_written is False
```

- [ ] **Step 2: Run RED**

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest -q \
  tests/p3_v3/test_prospective_multiproject.py
```

Expected: collection or import fails with `ModuleNotFoundError: No module named 'p3_v3.prospective_multiproject'`, or every listed test fails with `AttributeError` / `ImportError`. Do not create a passing stub.

- [ ] **Step 3: Minimal GREEN implementation**

Implement only the Task 1 functions in `src/p3_v3/prospective_multiproject.py`. Keep `build_cohort_terminal`, writers, preflight, and `main` unimplemented or absent until later tasks. `run_multiproject_search` must loop frozen successors, call `bind_project` then `process_subject`, call `advance_multiproject_state`, stop on scientific FOUND/EXHAUSTED or execution failure, and leave `official_terminal_written=False`.

Hard rules inside the loop:

- reject a result whose ordinal is not the next unused frozen ordinal
- reject user-supplied successor sequences that are not exactly ordinals 9–22
- do not call the processor after stop
- do not reread or rewrite ordinal 8

- [ ] **Step 4: Run GREEN**

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest -q \
  tests/p3_v3/test_prospective_multiproject.py
```

Expected: the Task 1 tests pass.

- [ ] **Step 5: Commit**

Files: `src/p3_v3/prospective_multiproject.py`, `tests/p3_v3/test_prospective_multiproject.py`

```text
feat(p3-v3): add multiproject paired-slice state machine
```

---

### Task 2: Atomic writer and terminal validator

**Creates:** functions in the existing `src/p3_v3/prospective_multiproject.py`

**Modifies:** `src/p3_v3/prospective_multiproject.py`, `tests/p3_v3/test_prospective_multiproject.py`

**Tests:** add the functions below to the same test file

**Consumes:** `canonical_sha256`, `validate_exact_object`, `write_canonical_json(..., exclusive=True)`, `os.replace`

**Produces:** `build_cohort_terminal`, `validate_cohort_terminal`, `write_subject_record`, `write_official_cohort_terminal`, `load_ordinal8_retained_observation`

- [ ] **Step 1: Write the failing writer/validator tests**

Append:

```python
import json
from pathlib import Path

from p3_v3.artifacts import canonical_sha256, file_sha256
from p3_v3.prospective_multiproject import (
    AUTHORITY_ARTIFACT_SHA256,
    DESIGN_COMMIT,
    DESIGN_FILE_SHA256,
    ORDINAL8_HANDOFF_ARTIFACT_SHA256,
    ORDINAL8_OVERLAP_ARTIFACT_SHA256,
    build_cohort_terminal,
    load_ordinal8_retained_observation,
    validate_cohort_terminal,
    write_official_cohort_terminal,
    write_subject_record,
)


def _complete_state(status: CohortStatus) -> tuple:
    successors = load_frozen_successors()
    ordinal8 = _ordinal8("numpy-readonly")
    state = initial_cohort_state(successors, ordinal8)
    if status is CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND:
        state = advance_multiproject_state(
            state, _result(9, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "proj-a", 1)
        )
        state = advance_multiproject_state(
            state, _result(10, SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, "proj-b", 2)
        )
    else:
        for ordinal in range(9, 23):
            state = advance_multiproject_state(
                state, _result(ordinal, SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE, f"p-{ordinal}")
            )
    return state, successors, ordinal8


def test_build_and_validate_found_and_exhausted_terminals():
    controller = "a" * 64
    for status in (
        CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND,
        CohortStatus.MULTIPROJECT_COHORT_EXHAUSTED,
    ):
        state, successors, ordinal8 = _complete_state(status)
        terminal = build_cohort_terminal(state=state, controller_source_sha256=controller)
        validated = validate_cohort_terminal(
            terminal,
            controller_source_sha256=controller,
            successors=successors,
            ordinal8=ordinal8,
        )
        body = {key: value for key, value in validated.items() if key != "artifact_sha256"}
        assert validated["artifact_sha256"] == canonical_sha256(body)
        assert validated["terminal_status"] == status.value
        assert validated["design_commit"] == DESIGN_COMMIT
        assert validated["design_file_sha256"] == DESIGN_FILE_SHA256
        assert validated["authority_artifact_sha256"] == AUTHORITY_ARTIFACT_SHA256
        assert validated["ordinal8_handoff_artifact_sha256"] == ORDINAL8_HANDOFF_ARTIFACT_SHA256
        assert validated["ordinal8_overlap_artifact_sha256"] == ORDINAL8_OVERLAP_ARTIFACT_SHA256
        assert validated["ordinal8_retained"]["rerun_forbidden"] is True
        assert validated["ordinal8_retained"]["pair_count"] == 4


def test_validate_rejects_failure_status_and_hash_or_order_tamper():
    controller = "b" * 64
    state, successors, ordinal8 = _complete_state(
        CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND
    )
    terminal = build_cohort_terminal(state=state, controller_source_sha256=controller)
    bad_status = dict(terminal)
    bad_status["terminal_status"] = "INFRASTRUCTURE_FAILURE"
    body = {key: value for key, value in bad_status.items() if key != "artifact_sha256"}
    bad_status["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="INFRASTRUCTURE_FAILURE|IDENTITY_CONFLICT|E_"):
        validate_cohort_terminal(
            bad_status,
            controller_source_sha256=controller,
            successors=successors,
            ordinal8=ordinal8,
        )
    bad_hash = dict(terminal)
    bad_hash["controller_source_sha256"] = "c" * 64
    with pytest.raises(EvidenceError):
        validate_cohort_terminal(
            bad_hash,
            controller_source_sha256=controller,
            successors=successors,
            ordinal8=ordinal8,
        )
    bad_order = dict(terminal)
    attempted = list(bad_order["attempted_subjects"])
    attempted[0], attempted[1] = attempted[1], attempted[0]
    bad_order["attempted_subjects"] = attempted
    with pytest.raises(EvidenceError):
        validate_cohort_terminal(
            bad_order,
            controller_source_sha256=controller,
            successors=successors,
            ordinal8=ordinal8,
        )


def test_atomic_write_and_fail_closed_existing_output(tmp_path: Path):
    controller = "d" * 64
    state, successors, ordinal8 = _complete_state(
        CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND
    )
    terminal = build_cohort_terminal(state=state, controller_source_sha256=controller)
    staging_root = tmp_path / "staging"
    official_root = tmp_path / "official"
    subject = state.attempted[0]
    write_subject_record(
        staging_subject=staging_root / subject.neutral_snapshot_id,
        official_subject=official_root / "subjects" / subject.neutral_snapshot_id,
        record={
            "successor_ordinal": subject.successor_ordinal,
            "neutral_snapshot_id": subject.neutral_snapshot_id,
            "controlled_subject_source_id": subject.controlled_subject_source_id,
            "controlled_subject_id": subject.controlled_subject_id,
            "project_cluster_key": subject.project_cluster_key,
            "subject_terminal": subject.subject_terminal.value,
            "pair_count": subject.pair_count,
        },
    )
    assert (official_root / "subjects" / subject.neutral_snapshot_id / "subject-record.json").is_file()
    assert not (staging_root / subject.neutral_snapshot_id).exists()
    write_official_cohort_terminal(
        staging_terminal=staging_root / "cohort-terminal.json",
        official_terminal=official_root / "cohort-terminal.json",
        terminal=terminal,
        controller_source_sha256=controller,
        successors=successors,
        ordinal8=ordinal8,
    )
    assert (official_root / "cohort-terminal.json").is_file()
    assert not (staging_root / "cohort-terminal.json").exists()
    with pytest.raises(EvidenceError):
        write_official_cohort_terminal(
            staging_terminal=staging_root / "cohort-terminal.json",
            official_terminal=official_root / "cohort-terminal.json",
            terminal=terminal,
            controller_source_sha256=controller,
            successors=successors,
            ordinal8=ordinal8,
        )


def test_staging_failure_keeps_residue(tmp_path: Path, monkeypatch):
    controller = "e" * 64
    state, successors, ordinal8 = _complete_state(
        CohortStatus.MULTIPROJECT_COHORT_EXHAUSTED
    )
    terminal = build_cohort_terminal(state=state, controller_source_sha256=controller)
    staging = tmp_path / "staging" / "cohort-terminal.json"
    official = tmp_path / "official" / "cohort-terminal.json"

    def boom(*args, **kwargs):
        raise OSError("replace failed")

    monkeypatch.setattr("os.replace", boom)
    with pytest.raises(EvidenceError):
        write_official_cohort_terminal(
            staging_terminal=staging,
            official_terminal=official,
            terminal=terminal,
            controller_source_sha256=controller,
            successors=successors,
            ordinal8=ordinal8,
        )
    assert staging.is_file()
    assert not official.exists()


def test_load_ordinal8_is_readonly_and_matches_frozen_artifacts():
    root = Path("/tmp/p3-c3-applicability-authority")
    observed = load_ordinal8_retained_observation(root, project_cluster_key="numpy-readonly")
    assert observed.rerun_forbidden is True
    assert observed.pair_count == 4
    assert observed.semantic_pair_kills == 4
    assert observed.syntactic_pair_kills == 3
    assert observed.d_subject == 0.25
    assert file_sha256(root / "data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json") == (
        "ad3361f990ff0a611ece2704077780d7f097459560085eb9a996acb8b69e1b3d"
    )
    assert file_sha256(root / "data/p3_v3/phase3/ordinal8-exact-overlap-v1/exact-overlap.json") == (
        "d64872250399ac0230d55d2e7fa2883fed783110061188d3fe6597272f571074"
    )
```

- [ ] **Step 2: Run RED**

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest -q \
  tests/p3_v3/test_prospective_multiproject.py
```

Expected: Task 1 tests still pass; the new Task 2 tests fail with `ImportError` or `AttributeError` for the missing writer/validator names.

- [ ] **Step 3: Minimal GREEN implementation**

Implement the five functions. Writers must:

1. write exclusive canonical JSON into staging
2. refuse to overwrite an existing official path
3. `os.replace` staging onto official
4. on replace failure, keep the staging file and raise `EvidenceError("INFRASTRUCTURE_FAILURE", ...)`
5. call `validate_cohort_terminal` before placing the official terminal
6. refuse to build a terminal unless `state.status` is a scientific cohort terminal

`load_ordinal8_retained_observation` reads the two frozen artifacts, checks their inner `artifact_sha256` fields, and returns the readonly dataclass. It must not execute a mutant or reread source.

Wire optional writers into `run_multiproject_search`: write each funnel/success subject after it is accepted; write the official terminal only after FOUND or EXHAUSTED. Failures must not call `write_terminal`.

- [ ] **Step 4: Run GREEN**

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest -q \
  tests/p3_v3/test_prospective_multiproject.py
```

Expected: all tests in that file pass.

- [ ] **Step 5: Commit**

Files: `src/p3_v3/prospective_multiproject.py`, `tests/p3_v3/test_prospective_multiproject.py`

```text
feat(p3-v3): add multiproject terminal writer and validator
```

---

### Task 3: CLI / controller seam

**Creates:** `scripts/p3_v3/run_prospective_multiproject_paired_slice.py`

**Modifies:** `src/p3_v3/prospective_multiproject.py` only to add `validate_multiproject_preflight`; `tests/p3_v3/test_prospective_multiproject.py`

**Tests:** CLI tests in the same file

**Consumes:** Task 1–2 functions; design/authority/handoff/overlap file hashes

**Produces:** no-argument `main()`; preflight; injection seam used only by tests

Forbidden argv tokens, each `PREFLIGHT_FAIL`: `--help`, `--order`, `--max-attempts`, `--applicability-map`, `--subject`, `--project`, `--skip`, `--retry`, `--resume`, `--pair-count`, `--output`, `--runtime`, or any extra token.

- [ ] **Step 1: Write the failing CLI tests**

Append:

```python
import sys

from p3_v3.artifacts import canonical_json_bytes
from p3_v3.prospective_multiproject import (
    AUTHORITY_RELPATH,
    CONTROLLER_RELPATH,
    DESIGN_RELPATH,
    HANDOFF_RELPATH,
    OFFICIAL_RELDIR,
    OFFICIAL_RUN_AUTHORIZED,
    OVERLAP_RELPATH,
    STAGING_RELDIR,
    validate_multiproject_preflight,
)
from scripts.p3_v3.run_prospective_multiproject_paired_slice import main


def _copy_frozen_identity_tree(real_root: Path, dest_root: Path) -> None:
    for rel in (
        DESIGN_RELPATH,
        AUTHORITY_RELPATH,
        HANDOFF_RELPATH,
        OVERLAP_RELPATH,
        CONTROLLER_RELPATH,
    ):
        dest = dest_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((real_root / rel).read_bytes())


def test_preflight_passes_frozen_identities_without_opening_successor_sites(monkeypatch):
    opened: list[str] = []
    real_open = open

    def guarded_open(path, *args, **kwargs):
        text = str(path)
        if "public-behavior-frame-" in text and "4e7e9556" not in text:
            opened.append(text)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", guarded_open)
    root = Path("/tmp/p3-c3-applicability-authority")
    payload = validate_multiproject_preflight(
        repo_root=root,
        controller_path=root / "src/p3_v3/prospective_multiproject.py",
    )
    assert payload["status"] == "MULTIPROJECT_PREFLIGHT_PASS"
    assert payload["successor_count"] == 14
    assert opened == []
    assert OFFICIAL_RUN_AUTHORIZED is False


def test_preflight_rejects_existing_official_namespace(tmp_path: Path):
    real_root = Path("/tmp/p3-c3-applicability-authority")
    _copy_frozen_identity_tree(real_root, tmp_path)
    payload = validate_multiproject_preflight(
        repo_root=tmp_path,
        controller_path=tmp_path / CONTROLLER_RELPATH,
    )
    assert payload["status"] == "MULTIPROJECT_PREFLIGHT_PASS"

    official = tmp_path / OFFICIAL_RELDIR
    official.mkdir(parents=True)
    with pytest.raises(EvidenceError, match="PREFLIGHT_FAIL"):
        validate_multiproject_preflight(
            repo_root=tmp_path,
            controller_path=tmp_path / CONTROLLER_RELPATH,
        )

    official.rmdir()
    staging = tmp_path / STAGING_RELDIR
    staging.mkdir(parents=True)
    with pytest.raises(EvidenceError, match="PREFLIGHT_FAIL"):
        validate_multiproject_preflight(
            repo_root=tmp_path,
            controller_path=tmp_path / CONTROLLER_RELPATH,
        )


def test_main_rejects_every_selector_and_does_not_run_search(monkeypatch):
    called = []
    monkeypatch.setattr(
        "scripts.p3_v3.run_prospective_multiproject_paired_slice.run_multiproject_search",
        lambda **kwargs: called.append(kwargs) or {},
    )
    for argv in (
        ["--help"],
        ["--max-attempts", "14"],
        ["--order", "9"],
        ["--subject", "x"],
        ["--project", "y"],
        ["--skip"],
        ["--retry"],
        ["--resume"],
        ["--pair-count", "4"],
        ["--output", "/tmp"],
        ["--runtime", "/tmp"],
    ):
        monkeypatch.setattr(sys, "argv", ["run_prospective_multiproject_paired_slice.py", *argv])
        assert main() == 2
    assert called == []


def test_main_zero_args_is_preflight_only_and_does_not_write_official_terminal(
    monkeypatch, capsys
):
    root = Path("/tmp/p3-c3-applicability-authority")
    official = root / "data/p3_v3/phase3/prospective-multiproject-paired-slice-v1/cohort-terminal.json"
    monkeypatch.setattr(sys, "argv", ["run_prospective_multiproject_paired_slice.py"])
    code = main()
    assert code == 2
    stdout = capsys.readouterr().out
    payload = json.loads(stdout)
    assert payload["status"] == "MULTIPROJECT_OFFICIAL_RUN_NOT_AUTHORIZED"
    assert payload["official_terminal_written"] is False
    assert official.exists() is False
```

- [ ] **Step 2: Run RED**

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest -q \
  tests/p3_v3/test_prospective_multiproject.py
```

Expected: Task 1–2 tests pass; new CLI tests fail with `ModuleNotFoundError` for the script or `AttributeError` for `validate_multiproject_preflight` / `main`.

- [ ] **Step 3: Minimal GREEN implementation**

CLI `main()`:

```python
def main() -> int:
    if len(sys.argv) != 1:
        sys.stdout.buffer.write(canonical_json_bytes({
            "status": "PREFLIGHT_FAIL",
            "slice_id": SLICE_ID,
            "official_terminal_written": False,
        }))
        return 2
    root = Path(__file__).resolve().parents[2]
    validate_multiproject_preflight(
        repo_root=root,
        controller_path=root / CONTROLLER_RELPATH,
    )
    sys.stdout.buffer.write(canonical_json_bytes({
        "status": "MULTIPROJECT_OFFICIAL_RUN_NOT_AUTHORIZED",
        "slice_id": SLICE_ID,
        "design_commit": DESIGN_COMMIT,
        "official_terminal_written": False,
        "successor_count": MAXIMUM_ATTEMPTS,
    }))
    return 2
```

Preflight must verify, without opening successor PBF site arrays:

1. design file SHA equals `DESIGN_FILE_SHA256`
2. authority manifest `artifact_sha256` equals `AUTHORITY_ARTIFACT_SHA256`
3. handoff and overlap artifact SHAs equal the frozen constants
4. `load_frozen_successors()` returns ordinals 9–22
5. official and staging namespaces are absent
6. controller path is the unique `CONTROLLER_RELPATH`
7. `OFFICIAL_RUN_AUTHORIZED is False`

The official/staging absence check is independent of missing identity files. A fixture that copies only the frozen identity files and then creates `OFFICIAL_RELDIR` or `STAGING_RELDIR` must raise `PREFLIGHT_FAIL`. An empty `tmp_path` is not a sufficient RED for this rule.

Do not parse PBF `sites`. Do not restore source.

- [ ] **Step 4: Run GREEN**

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest -q \
  tests/p3_v3/test_prospective_multiproject.py
```

Expected: all tests in that file pass.

- [ ] **Step 5: Commit**

Files: `src/p3_v3/prospective_multiproject.py`, `scripts/p3_v3/run_prospective_multiproject_paired_slice.py`, `tests/p3_v3/test_prospective_multiproject.py`

```text
feat(p3-v3): add fail-closed multiproject controller CLI
```

---

### Task 4: Focused integration verification

**Creates:** no new production file

**Modifies:** `tests/p3_v3/test_prospective_multiproject.py` only if a listed scenario is still missing after Tasks 1–3

**Tests:** the commands below

**Consumes:** the three production/test files

**Produces:** the Slice A success terminal, not an official scientific terminal

- [ ] **Step 1: Confirm the checklist is covered by named tests**

| Scenario | Test |
|---|---|
| ordinal 9→22 order | `test_load_frozen_successors_is_ordinals_9_through_22_in_v2_order` |
| max 14 | same |
| all-not-applicable continues | `test_funnel_terminals_continue_and_keep_the_subject` |
| no-contract / no-pair continues | same |
| first complete project does not stop | `test_first_complete_project_does_not_stop` |
| second distinct non-NumPy project stops | `test_second_distinct_non_numpy_project_stops_immediately` |
| same repository is not a second project | `test_same_repository_is_not_a_second_project` |
| NumPy is not a new project | `test_numpy_project_is_not_a_new_project` |
| infrastructure failure stops, no scientific terminal | `test_run_search_failure_does_not_continue_or_write_terminal` |
| identity conflict stops, no scientific terminal | `test_infrastructure_and_identity_failure_stop_without_scientific_status` |
| exhausted covers exactly 9–22 | `test_run_search_exhausts_exactly_9_through_22` |
| ordinal 23 / extra subject never opened | `test_run_search_uses_9_to_22_stops_on_second_project_and_never_opens_23` |
| pair budget ≤ 4 | `test_pair_budget_rejects_more_than_four_or_complete_with_zero` |
| ordinal 8 readonly, not rerun | `test_load_ordinal8_is_readonly_and_matches_frozen_artifacts` |
| terminal self-hash | `test_build_and_validate_found_and_exhausted_terminals` |
| staging failure keeps residue | `test_staging_failure_keeps_residue` |
| existing output fail-closed | `test_atomic_write_and_fail_closed_existing_output` |
| official/staging namespace fail-closed after identity PASS | `test_preflight_rejects_existing_official_namespace` |

If any row lacks a passing test, add only that missing test to the same file. Do not add a second test module.

- [ ] **Step 2: Run focused GREEN plus the two regression tests**

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest -q \
  tests/p3_v3/test_prospective_multiproject.py \
  tests/p3_v3/test_prospective_applicability_search_v2.py::test_main_rejects_help_and_extra_arguments \
  tests/p3_v3/test_applicability_authority.py::test_project_controlled_subject_ids_sorts_35_unique_sha256
git diff --check
git status --porcelain=v1 --untracked-files=all
test ! -e data/p3_v3/phase3/prospective-multiproject-paired-slice-v1
test ! -e data/p3_v3/phase3/prospective-multiproject-paired-slice-v1.staging
```

Expected: focused tests pass; `git diff --check` silent; no official/staging namespace; C3 ledger file still SHA-256 `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68`.

- [ ] **Step 3: Commit only if Task 4 added a missing test**

```text
test(p3-v3): close multiproject controller focused checklist
```

If no file changed, do not create an empty commit.

Success of Tasks 1–4 is `MULTIPROJECT_CONTROLLER_IMPLEMENTATION_PASS`. It is not a Slice B authorization.

---

## 7. Self-audit

1. Design rules map to Tasks: successor freeze/stop/funnel → Task 1; atomic terminal → Task 2; CLI/preflight isolation → Task 3; checklist → Task 4.
2. No TODO/TBD/placeholder remains.
3. Types and signatures are the same in §3 and every Task.
4. Ordinal 8 is a readonly retained observation; processors never receive ordinal 8.
5. Slice A tests use a synthetic processor; preflight must not open successor PBF site arrays.
6. Funnel terminals continue; infrastructure/identity failures stop and cannot be scientific terminals.
7. The second distinct non-NumPy project stops immediately.
8. No schema, manifest, or ledger file is added.
9. `OFFICIAL_RUN_AUTHORIZED = False`; `main()` cannot write the official terminal.
10. C3 remains `blocked`; ledger is not edited.
11. Official/staging fail-closed is isolated: the RED first proves identity-complete preflight PASS, then creates only `OFFICIAL_RELDIR` / `STAGING_RELDIR`.

---

## 8. Unique next task

`P3_C3_PROSPECTIVE_MULTIPROJECT_CONTROLLER_IMPLEMENTATION`

That later task executes this plan, Tasks 1–4 only. It must not open ordinal 9, recover source, or write the official multiproject namespace.
