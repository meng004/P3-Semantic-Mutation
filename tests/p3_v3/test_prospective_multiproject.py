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
