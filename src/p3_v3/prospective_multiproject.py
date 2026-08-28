from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from p3_v3.artifacts import EvidenceError

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


def _canonical_v2_rows() -> tuple[Mapping[str, object], ...]:
    from scripts.p3_v3.prospective_applicability_search_v2 import FROZEN_SUCCESSOR_ROWS

    return FROZEN_SUCCESSOR_ROWS


def _identity_from_row(row: Mapping[str, object]) -> SuccessorIdentity:
    return SuccessorIdentity(
        successor_ordinal=int(row["successor_ordinal"]),
        neutral_snapshot_id=str(row["neutral_snapshot_id"]),
        controlled_subject_source_id=str(row["controlled_subject_source_id"]),
        controlled_subject_id=str(row["controlled_subject_id"]),
    )


def _frozen_successor_identities(
    rows: Sequence[Mapping[str, object]],
) -> tuple[SuccessorIdentity, ...]:
    selected = [_identity_from_row(row) for row in rows[8:22]]
    ordinals = tuple(item.successor_ordinal for item in selected)
    if ordinals != tuple(range(FIRST_SUCCESSOR_ORDINAL, LAST_SUCCESSOR_ORDINAL + 1)):
        raise EvidenceError("IDENTITY_CONFLICT", "frozen successors must be ordinals 9-22")
    if len(selected) != MAXIMUM_ATTEMPTS:
        raise EvidenceError("IDENTITY_CONFLICT", "frozen successor count must be 14")
    return tuple(selected)


def load_frozen_successors(
    *,
    v2_rows: Sequence[Mapping[str, object]] | None = None,
) -> tuple[SuccessorIdentity, ...]:
    canonical = _canonical_v2_rows()
    rows = canonical if v2_rows is None else v2_rows
    if tuple(dict(row) for row in rows) != tuple(dict(row) for row in canonical):
        raise EvidenceError("IDENTITY_CONFLICT", "v2 successor rows were reordered or replaced")
    return _frozen_successor_identities(canonical)


def _require_frozen_successors(
    successors: Sequence[SuccessorIdentity],
) -> tuple[SuccessorIdentity, ...]:
    frozen = load_frozen_successors()
    observed = tuple(successors)
    if observed != frozen:
        raise EvidenceError("IDENTITY_CONFLICT", "successor sequence is not frozen ordinals 9-22")
    return frozen


def initial_cohort_state(
    successors: Sequence[SuccessorIdentity],
    ordinal8: Ordinal8RetainedObservation,
) -> CohortState:
    frozen = _require_frozen_successors(successors)
    if ordinal8.successor_ordinal != 8 or not ordinal8.rerun_forbidden:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal 8 must remain a readonly observation")
    return CohortState(
        successors=frozen,
        ordinal8=ordinal8,
        attempted=(),
        status=CohortStatus.IN_PROGRESS,
        completed_new_project_keys=(),
    )


def advance_multiproject_state(
    state: CohortState,
    result: SubjectPipelineResult,
) -> CohortState:
    if state.status is not CohortStatus.IN_PROGRESS:
        raise EvidenceError("IDENTITY_CONFLICT", "stopped cohort cannot advance")
    if len(state.attempted) >= MAXIMUM_ATTEMPTS:
        raise EvidenceError("IDENTITY_CONFLICT", "attempt budget already exhausted")
    expected = state.successors[len(state.attempted)]
    if result.successor_ordinal != expected.successor_ordinal:
        raise EvidenceError(
            "IDENTITY_CONFLICT",
            f"expected ordinal {expected.successor_ordinal}, got {result.successor_ordinal}",
        )
    if result.pair_count > MAX_PAIRS_PER_SUBJECT:
        raise EvidenceError("IDENTITY_CONFLICT", "pair_count exceeds 4")
    if (
        result.subject_terminal is SubjectTerminal.PAIRED_EVIDENCE_COMPLETE
        and result.pair_count < 1
    ):
        raise EvidenceError("IDENTITY_CONFLICT", "complete subject requires 1-4 pairs")

    attempted = AttemptedSubject(
        successor_ordinal=expected.successor_ordinal,
        neutral_snapshot_id=expected.neutral_snapshot_id,
        controlled_subject_source_id=expected.controlled_subject_source_id,
        controlled_subject_id=expected.controlled_subject_id,
        project_cluster_key=result.project_cluster_key,
        subject_terminal=result.subject_terminal,
        pair_count=result.pair_count,
    )
    next_attempted = state.attempted + (attempted,)

    if result.subject_terminal in FAILURE_TERMINALS:
        return CohortState(
            successors=state.successors,
            ordinal8=state.ordinal8,
            attempted=next_attempted,
            status=CohortStatus(result.subject_terminal.value),
            completed_new_project_keys=state.completed_new_project_keys,
        )

    completed = state.completed_new_project_keys
    if result.subject_terminal is SubjectTerminal.PAIRED_EVIDENCE_COMPLETE:
        key = result.project_cluster_key
        if key != state.ordinal8.project_cluster_key and key not in completed:
            completed = completed + (key,)
        if len(completed) >= 2:
            return CohortState(
                successors=state.successors,
                ordinal8=state.ordinal8,
                attempted=next_attempted,
                status=CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND,
                completed_new_project_keys=completed,
            )

    status = (
        CohortStatus.MULTIPROJECT_COHORT_EXHAUSTED
        if len(next_attempted) == len(state.successors)
        else CohortStatus.IN_PROGRESS
    )
    return CohortState(
        successors=state.successors,
        ordinal8=state.ordinal8,
        attempted=next_attempted,
        status=status,
        completed_new_project_keys=completed,
    )


def run_multiproject_search(
    *,
    process_subject: SubjectProcessor,
    bind_project: ProjectIdentityBinder,
    ordinal8: Ordinal8RetainedObservation,
    successors: Sequence[SuccessorIdentity] | None = None,
    write_subject: SubjectWriter | None = None,
    write_terminal: TerminalWriter | None = None,
    controller_source_sha256: str | None = None,
) -> SearchResult:
    frozen = (
        load_frozen_successors()
        if successors is None
        else _require_frozen_successors(successors)
    )
    state = initial_cohort_state(frozen, ordinal8)
    opened: list[int] = []
    for successor in frozen:
        if state.status is not CohortStatus.IN_PROGRESS:
            break
        bind_project(successor)
        result = process_subject(successor)
        opened.append(successor.successor_ordinal)
        state = advance_multiproject_state(state, result)
        if write_subject is not None and result.subject_terminal not in FAILURE_TERMINALS:
            write_subject(state.attempted[-1])

    terminal = None
    official_terminal_written = False
    if (
        state.status in SCIENTIFIC_COHORT_TERMINALS
        and write_terminal is not None
        and controller_source_sha256 is not None
    ):
        terminal = {
            "terminal_status": state.status.value,
            "attempted_subjects": [
                {
                    "successor_ordinal": row.successor_ordinal,
                    "neutral_snapshot_id": row.neutral_snapshot_id,
                    "controlled_subject_source_id": row.controlled_subject_source_id,
                    "controlled_subject_id": row.controlled_subject_id,
                    "project_cluster_key": row.project_cluster_key,
                    "subject_terminal": row.subject_terminal.value,
                    "pair_count": row.pair_count,
                }
                for row in state.attempted
            ],
            "completed_new_project_keys": list(state.completed_new_project_keys),
        }
        write_terminal(terminal)
        official_terminal_written = True

    return SearchResult(
        status=state.status,
        attempted=state.attempted,
        completed_new_project_keys=state.completed_new_project_keys,
        official_terminal_written=official_terminal_written,
        terminal=terminal,
        opened_ordinals=tuple(opened),
    )
