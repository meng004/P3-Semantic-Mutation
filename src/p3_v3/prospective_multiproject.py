from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)

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
VERIFIED_BRIDGE_RELPATH = Path("data/p3_v3/p12_intake/verified_bridge.json")
_ORIGINATING_REPOSITORY_FIELDS = (
    "originating_repository_identity",
    "originating_p12_repository_identity",
    "originating_repository",
    "p12_originating_repository_identity",
)
_FORBIDDEN_PROJECT_KEY_FIELDS = frozenset({
    "neutral_snapshot_id",
    "controlled_subject_id",
    "controlled_subject_source_id",
    "source_archive_sha256",
    "build_descriptor_sha256",
    "ecosystem",
    "language_family",
    "p12_repository_identity",
})


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


def load_frozen_bridge_identity_records(
    repo_root: Path,
) -> tuple[dict[str, object], ...]:
    payload = json.loads((Path(repo_root) / VERIFIED_BRIDGE_RELPATH).read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != 35:
        raise EvidenceError("IDENTITY_CONFLICT", "verified bridge must contain 35 records")
    seen: set[str] = set()
    narrowed: list[dict[str, object]] = []
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            raise EvidenceError("IDENTITY_CONFLICT", f"bridge.records[{index}] must be an object")
        neutral = validate_sha256(
            raw.get("neutral_snapshot_id"),
            f"records[{index}].neutral_snapshot_id",
        )
        if neutral in seen:
            raise EvidenceError("IDENTITY_CONFLICT", "duplicate neutral_snapshot_id")
        seen.add(neutral)
        narrowed.append(dict(raw))
    return tuple(narrowed)


def _require_production_successor(successor: SuccessorIdentity) -> SuccessorIdentity:
    if successor.successor_ordinal == 8:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal 8 must not enter the production binder")
    for item in load_frozen_successors():
        if item == successor:
            return successor
    raise EvidenceError("IDENTITY_CONFLICT", "successor is outside frozen ordinals 9-22")


def bind_production_project_identity(
    successor: SuccessorIdentity,
    *,
    repo_root: Path,
    project_map: Mapping[object, object] | None = None,
) -> str:
    if project_map is not None:
        raise EvidenceError("IDENTITY_CONFLICT", "user project map is forbidden")
    locked = _require_production_successor(successor)
    matches = [
        row
        for row in load_frozen_bridge_identity_records(repo_root)
        if row.get("neutral_snapshot_id") == locked.neutral_snapshot_id
    ]
    if len(matches) != 1:
        raise EvidenceError("IDENTITY_CONFLICT", "frozen identity does not uniquely match successor")
    record = matches[0]
    found: list[str] = []
    for field in _ORIGINATING_REPOSITORY_FIELDS:
        if field in _FORBIDDEN_PROJECT_KEY_FIELDS:
            continue
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            found.append(value.strip())
    unique = tuple(dict.fromkeys(found))
    if len(unique) == 1:
        return unique[0]
    if len(unique) > 1:
        raise EvidenceError("IDENTITY_CONFLICT", "originating repository fields conflict")
    raise EvidenceError(
        "SLICE_B_PROCESSOR_AUTHORITY_REQUIRED",
        "frozen 35-subject identity has no originating P12 repository identity",
    )


def production_project_binder(repo_root: Path | None = None) -> ProjectIdentityBinder:
    root = Path(__file__).resolve().parents[2] if repo_root is None else Path(repo_root)

    def bind(successor: SuccessorIdentity) -> str:
        return bind_production_project_identity(successor, repo_root=root)

    return bind


PRODUCTION_PROCESSOR_STAGES = (
    "frozen_subject_identity",
    "source_identity_recovery",
    "authority_bound_applicability_closure",
    "source_authorized_contract_freeze",
    "canonical_paired_constructions",
    "controlled_paired_execution",
    "exact_overlap",
    "subject_terminal",
    "project_stopping_rule_reduction",
)


def process_production_subject(
    successor: SuccessorIdentity,
    *,
    repo_root: Path,
) -> SubjectPipelineResult:
    locked = _require_production_successor(successor)
    records = load_frozen_bridge_identity_records(repo_root)
    matches = [
        row for row in records if row.get("neutral_snapshot_id") == locked.neutral_snapshot_id
    ]
    if len(matches) != 1:
        raise EvidenceError("IDENTITY_CONFLICT", "frozen identity does not uniquely match successor")
    bind_production_project_identity(locked, repo_root=repo_root)
    raise EvidenceError(
        "SLICE_B_PROCESSOR_AUTHORITY_REQUIRED",
        "later processor stages are not authorized without originating repository identity",
    )


def production_subject_processor(repo_root: Path | None = None) -> SubjectProcessor:
    root = Path(__file__).resolve().parents[2] if repo_root is None else Path(repo_root)

    def process(successor: SuccessorIdentity) -> SubjectPipelineResult:
        return process_production_subject(successor, repo_root=root)

    return process


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
    if state.status in SCIENTIFIC_COHORT_TERMINALS and write_terminal is not None:
        if controller_source_sha256 is None:
            raise EvidenceError("IDENTITY_CONFLICT", "scientific terminal requires controller SHA")
        terminal = build_cohort_terminal(
            state=state,
            controller_source_sha256=controller_source_sha256,
        )
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


_ORDINAL8_NEUTRAL_SNAPSHOT_ID = (
    "4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b"
)
_ORDINAL8_CONTROLLED_SUBJECT_SOURCE_ID = (
    "667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0"
)
_ORDINAL8_CONTROLLED_SUBJECT_ID = (
    "0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48"
)

_TERMINAL_SCHEMA = {
    "schema_version": str,
    "slice_id": str,
    "design_commit": str,
    "design_file_sha256": str,
    "authority_artifact_sha256": str,
    "controller_source_sha256": str,
    "ordinal8_handoff_artifact_sha256": str,
    "ordinal8_overlap_artifact_sha256": str,
    "ordinal8_retained": dict,
    "terminal_status": str,
    "attempted_subjects": list,
    "completed_new_project_keys": list,
    "artifact_sha256": str,
}
_ORDINAL8_RETAINED_SCHEMA = {
    "successor_ordinal": int,
    "neutral_snapshot_id": str,
    "controlled_subject_source_id": str,
    "controlled_subject_id": str,
    "project_cluster_key": str,
    "pair_count": int,
    "semantic_pair_kills": int,
    "syntactic_pair_kills": int,
    "d_subject": float,
    "normalized_patch_overlap_numerator": int,
    "normalized_patch_overlap_denominator": int,
    "mutant_tree_overlap_numerator": int,
    "mutant_tree_overlap_denominator": int,
    "rerun_forbidden": bool,
}
_ATTEMPTED_SCHEMA = {
    "successor_ordinal": int,
    "neutral_snapshot_id": str,
    "controlled_subject_source_id": str,
    "controlled_subject_id": str,
    "project_cluster_key": str,
    "subject_terminal": str,
    "pair_count": int,
}


def _ordinal8_retained_object(ordinal8: Ordinal8RetainedObservation) -> dict[str, object]:
    return {
        "successor_ordinal": ordinal8.successor_ordinal,
        "neutral_snapshot_id": ordinal8.neutral_snapshot_id,
        "controlled_subject_source_id": ordinal8.controlled_subject_source_id,
        "controlled_subject_id": ordinal8.controlled_subject_id,
        "project_cluster_key": ordinal8.project_cluster_key,
        "pair_count": ordinal8.pair_count,
        "semantic_pair_kills": ordinal8.semantic_pair_kills,
        "syntactic_pair_kills": ordinal8.syntactic_pair_kills,
        "d_subject": ordinal8.d_subject,
        "normalized_patch_overlap_numerator": ordinal8.normalized_patch_overlap_numerator,
        "normalized_patch_overlap_denominator": ordinal8.normalized_patch_overlap_denominator,
        "mutant_tree_overlap_numerator": ordinal8.mutant_tree_overlap_numerator,
        "mutant_tree_overlap_denominator": ordinal8.mutant_tree_overlap_denominator,
        "rerun_forbidden": ordinal8.rerun_forbidden,
    }


def _attempted_object(row: AttemptedSubject) -> dict[str, object]:
    return {
        "successor_ordinal": row.successor_ordinal,
        "neutral_snapshot_id": row.neutral_snapshot_id,
        "controlled_subject_source_id": row.controlled_subject_source_id,
        "controlled_subject_id": row.controlled_subject_id,
        "project_cluster_key": row.project_cluster_key,
        "subject_terminal": row.subject_terminal.value,
        "pair_count": row.pair_count,
    }


def load_ordinal8_retained_observation(
    repo_root: Path,
    *,
    project_cluster_key: str,
) -> Ordinal8RetainedObservation:
    handoff = json.loads((repo_root / HANDOFF_RELPATH).read_text(encoding="utf-8"))
    overlap = json.loads((repo_root / OVERLAP_RELPATH).read_text(encoding="utf-8"))
    if handoff.get("artifact_sha256") != ORDINAL8_HANDOFF_ARTIFACT_SHA256:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal-8 handoff artifact SHA mismatch")
    if overlap.get("artifact_sha256") != ORDINAL8_OVERLAP_ARTIFACT_SHA256:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal-8 overlap artifact SHA mismatch")
    if overlap.get("neutral_snapshot_id") != _ORDINAL8_NEUTRAL_SNAPSHOT_ID:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal-8 snapshot identity mismatch")
    if overlap.get("controlled_subject_source_id") != _ORDINAL8_CONTROLLED_SUBJECT_SOURCE_ID:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal-8 source identity mismatch")
    if overlap.get("controlled_subject_id") != _ORDINAL8_CONTROLLED_SUBJECT_ID:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal-8 subject identity mismatch")
    return Ordinal8RetainedObservation(
        successor_ordinal=8,
        neutral_snapshot_id=_ORDINAL8_NEUTRAL_SNAPSHOT_ID,
        controlled_subject_source_id=_ORDINAL8_CONTROLLED_SUBJECT_SOURCE_ID,
        controlled_subject_id=_ORDINAL8_CONTROLLED_SUBJECT_ID,
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


def build_cohort_terminal(
    *,
    state: CohortState,
    controller_source_sha256: str,
) -> dict[str, object]:
    if state.status not in SCIENTIFIC_COHORT_TERMINALS:
        raise EvidenceError(
            state.status.value if state.status in FAILURE_TERMINALS else "IDENTITY_CONFLICT",
            "scientific terminal requires FOUND or EXHAUSTED",
        )
    validate_sha256(controller_source_sha256, "controller_source_sha256")
    body: dict[str, object] = {
        "schema_version": TERMINAL_SCHEMA_VERSION,
        "slice_id": SLICE_ID,
        "design_commit": DESIGN_COMMIT,
        "design_file_sha256": DESIGN_FILE_SHA256,
        "authority_artifact_sha256": AUTHORITY_ARTIFACT_SHA256,
        "controller_source_sha256": controller_source_sha256,
        "ordinal8_handoff_artifact_sha256": ORDINAL8_HANDOFF_ARTIFACT_SHA256,
        "ordinal8_overlap_artifact_sha256": ORDINAL8_OVERLAP_ARTIFACT_SHA256,
        "ordinal8_retained": _ordinal8_retained_object(state.ordinal8),
        "terminal_status": state.status.value,
        "attempted_subjects": [_attempted_object(row) for row in state.attempted],
        "completed_new_project_keys": list(state.completed_new_project_keys),
    }
    body["artifact_sha256"] = canonical_sha256(body)
    return body


def validate_cohort_terminal(
    terminal: Mapping[str, object],
    *,
    controller_source_sha256: str,
    successors: Sequence[SuccessorIdentity],
    ordinal8: Ordinal8RetainedObservation,
) -> dict[str, object]:
    payload = validate_exact_object(dict(terminal), _TERMINAL_SCHEMA, "cohort-terminal")
    if payload["terminal_status"] not in {
        CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND.value,
        CohortStatus.MULTIPROJECT_COHORT_EXHAUSTED.value,
    }:
        raise EvidenceError(
            "IDENTITY_CONFLICT",
            f"scientific terminal cannot use {payload['terminal_status']}",
        )
    validate_exact_object(payload["ordinal8_retained"], _ORDINAL8_RETAINED_SCHEMA, "ordinal8_retained")
    frozen = _require_frozen_successors(successors)
    attempted = payload["attempted_subjects"]
    if not attempted:
        raise EvidenceError("IDENTITY_CONFLICT", "scientific terminal has no attempted subjects")
    expected_rows = [
        {
            "successor_ordinal": successor.successor_ordinal,
            "neutral_snapshot_id": successor.neutral_snapshot_id,
            "controlled_subject_source_id": successor.controlled_subject_source_id,
            "controlled_subject_id": successor.controlled_subject_id,
        }
        for successor in frozen[: len(attempted)]
    ]
    for index, row in enumerate(attempted):
        validate_exact_object(row, _ATTEMPTED_SCHEMA, f"attempted_subjects[{index}]")
        identity = {key: row[key] for key in expected_rows[index]}
        if identity != expected_rows[index]:
            raise EvidenceError("IDENTITY_CONFLICT", "attempted subject order or identity mismatch")
    if payload["controller_source_sha256"] != controller_source_sha256:
        raise EvidenceError("IDENTITY_CONFLICT", "controller SHA mismatch")
    if payload["schema_version"] != TERMINAL_SCHEMA_VERSION:
        raise EvidenceError("IDENTITY_CONFLICT", "schema_version mismatch")
    if payload["slice_id"] != SLICE_ID:
        raise EvidenceError("IDENTITY_CONFLICT", "slice_id mismatch")
    if payload["design_commit"] != DESIGN_COMMIT:
        raise EvidenceError("IDENTITY_CONFLICT", "DESIGN_COMMIT mismatch")
    if payload["design_file_sha256"] != DESIGN_FILE_SHA256:
        raise EvidenceError("IDENTITY_CONFLICT", "design file SHA mismatch")
    if payload["authority_artifact_sha256"] != AUTHORITY_ARTIFACT_SHA256:
        raise EvidenceError("IDENTITY_CONFLICT", "authority artifact SHA mismatch")
    if payload["ordinal8_handoff_artifact_sha256"] != ORDINAL8_HANDOFF_ARTIFACT_SHA256:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal-8 handoff artifact SHA mismatch")
    if payload["ordinal8_overlap_artifact_sha256"] != ORDINAL8_OVERLAP_ARTIFACT_SHA256:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal-8 overlap artifact SHA mismatch")
    if payload["ordinal8_retained"] != _ordinal8_retained_object(ordinal8):
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal8 retained observation mismatch")
    implied_status, implied_keys = _implied_scientific_status(attempted, ordinal8)
    if payload["terminal_status"] != implied_status:
        raise EvidenceError("IDENTITY_CONFLICT", "terminal_status does not match stop rule")
    if payload["completed_new_project_keys"] != implied_keys:
        raise EvidenceError("IDENTITY_CONFLICT", "completed_new_project_keys do not match stop rule")
    body = {key: value for key, value in payload.items() if key != "artifact_sha256"}
    if payload["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("IDENTITY_CONFLICT", "terminal self-hash mismatch")
    return payload


def _implied_scientific_status(
    attempted: Sequence[Mapping[str, object]],
    ordinal8: Ordinal8RetainedObservation,
) -> tuple[str, list[str]]:
    completed: list[str] = []
    for index, row in enumerate(attempted):
        terminal = row["subject_terminal"]
        if terminal in {item.value for item in FAILURE_TERMINALS}:
            raise EvidenceError("IDENTITY_CONFLICT", "scientific terminal contains a failure subject")
        if terminal == SubjectTerminal.PAIRED_EVIDENCE_COMPLETE.value:
            pair_count = int(row["pair_count"])
            if pair_count < 1 or pair_count > MAX_PAIRS_PER_SUBJECT:
                raise EvidenceError("IDENTITY_CONFLICT", "complete pair budget mismatch")
            key = str(row["project_cluster_key"])
            if key != ordinal8.project_cluster_key and key not in completed:
                completed.append(key)
            if len(completed) >= 2:
                if index != len(attempted) - 1:
                    raise EvidenceError("IDENTITY_CONFLICT", "subjects continue after two-project stop")
                return CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND.value, completed
        elif terminal not in {item.value for item in FUNNEL_TERMINALS}:
            raise EvidenceError("IDENTITY_CONFLICT", f"unknown subject terminal {terminal}")
    if [row["successor_ordinal"] for row in attempted] != list(
        range(FIRST_SUCCESSOR_ORDINAL, LAST_SUCCESSOR_ORDINAL + 1)
    ):
        raise EvidenceError("IDENTITY_CONFLICT", "exhausted terminal must cover ordinals 9-22")
    return CohortStatus.MULTIPROJECT_COHORT_EXHAUSTED.value, completed


def _place_exclusive(staging: Path, official: Path, record: Mapping[str, object]) -> None:
    if official.exists():
        raise EvidenceError("IDENTITY_CONFLICT", f"official path already exists: {official}")
    official.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(staging, record, exclusive=True)
    try:
        os.replace(staging, official)
    except OSError as exc:
        raise EvidenceError("INFRASTRUCTURE_FAILURE", f"replace failed: {official}") from exc


def write_subject_record(
    *,
    staging_subject: Path,
    official_subject: Path,
    record: Mapping[str, object],
) -> None:
    staging_file = Path(staging_subject) / "subject-record.json"
    official_file = Path(official_subject) / "subject-record.json"
    staging_file.parent.mkdir(parents=True, exist_ok=True)
    _place_exclusive(staging_file, official_file, record)
    leftover = Path(staging_subject)
    if leftover.exists() and leftover.is_dir() and not any(leftover.iterdir()):
        leftover.rmdir()


def write_official_cohort_terminal(
    *,
    staging_terminal: Path,
    official_terminal: Path,
    terminal: Mapping[str, object],
    controller_source_sha256: str,
    successors: Sequence[SuccessorIdentity],
    ordinal8: Ordinal8RetainedObservation,
) -> None:
    validated = validate_cohort_terminal(
        terminal,
        controller_source_sha256=controller_source_sha256,
        successors=successors,
        ordinal8=ordinal8,
    )
    _place_exclusive(Path(staging_terminal), Path(official_terminal), validated)


def validate_multiproject_preflight(
    *,
    repo_root: Path,
    controller_path: Path,
) -> dict[str, object]:
    root = Path(repo_root)
    expected_controller = (root / CONTROLLER_RELPATH).resolve()
    if Path(controller_path).resolve() != expected_controller:
        raise EvidenceError("PREFLIGHT_FAIL", "controller path is not the unique controller")
    if OFFICIAL_RUN_AUTHORIZED is not False:
        raise EvidenceError("PREFLIGHT_FAIL", "official run is not authorized")
    if file_sha256(root / DESIGN_RELPATH) != DESIGN_FILE_SHA256:
        raise EvidenceError("PREFLIGHT_FAIL", "design file SHA mismatch")
    authority = json.loads((root / AUTHORITY_RELPATH).read_text(encoding="utf-8"))
    if authority.get("artifact_sha256") != AUTHORITY_ARTIFACT_SHA256:
        raise EvidenceError("PREFLIGHT_FAIL", "authority artifact SHA mismatch")
    handoff = json.loads((root / HANDOFF_RELPATH).read_text(encoding="utf-8"))
    overlap = json.loads((root / OVERLAP_RELPATH).read_text(encoding="utf-8"))
    if handoff.get("artifact_sha256") != ORDINAL8_HANDOFF_ARTIFACT_SHA256:
        raise EvidenceError("PREFLIGHT_FAIL", "handoff artifact SHA mismatch")
    if overlap.get("artifact_sha256") != ORDINAL8_OVERLAP_ARTIFACT_SHA256:
        raise EvidenceError("PREFLIGHT_FAIL", "overlap artifact SHA mismatch")
    successors = load_frozen_successors()
    if [row.successor_ordinal for row in successors] != list(
        range(FIRST_SUCCESSOR_ORDINAL, LAST_SUCCESSOR_ORDINAL + 1)
    ):
        raise EvidenceError("PREFLIGHT_FAIL", "frozen successors are not ordinals 9-22")
    if (root / OFFICIAL_RELDIR).exists() or (root / STAGING_RELDIR).exists():
        raise EvidenceError("PREFLIGHT_FAIL", "official or staging namespace already exists")
    return {
        "status": "MULTIPROJECT_PREFLIGHT_PASS",
        "slice_id": SLICE_ID,
        "successor_count": len(successors),
        "official_run_authorized": OFFICIAL_RUN_AUTHORIZED,
    }
