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


def test_validate_rejects_frozen_identity_and_stop_rule_tamper():
    controller = "f" * 64
    state, successors, ordinal8 = _complete_state(
        CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND
    )
    terminal = build_cohort_terminal(state=state, controller_source_sha256=controller)
    for field, value in (
        ("schema_version", "tampered-schema"),
        ("slice_id", "tampered-slice"),
        ("design_file_sha256", "0" * 64),
        ("authority_artifact_sha256", "1" * 64),
        ("ordinal8_handoff_artifact_sha256", "2" * 64),
        ("ordinal8_overlap_artifact_sha256", "3" * 64),
    ):
        tampered = dict(terminal)
        tampered[field] = value
        body = {key: item for key, item in tampered.items() if key != "artifact_sha256"}
        tampered["artifact_sha256"] = canonical_sha256(body)
        with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
            validate_cohort_terminal(
                tampered,
                controller_source_sha256=controller,
                successors=successors,
                ordinal8=ordinal8,
            )

    relabeled = dict(terminal)
    relabeled["terminal_status"] = CohortStatus.MULTIPROJECT_COHORT_EXHAUSTED.value
    body = {key: item for key, item in relabeled.items() if key != "artifact_sha256"}
    relabeled["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        validate_cohort_terminal(
            relabeled,
            controller_source_sha256=controller,
            successors=successors,
            ordinal8=ordinal8,
        )

    exhausted_state, exhausted_successors, exhausted_ordinal8 = _complete_state(
        CohortStatus.MULTIPROJECT_COHORT_EXHAUSTED
    )
    exhausted = build_cohort_terminal(
        state=exhausted_state, controller_source_sha256=controller
    )
    fake_found = dict(exhausted)
    fake_found["terminal_status"] = CohortStatus.MULTIPROJECT_TWO_NEW_PROJECTS_FOUND.value
    fake_found["completed_new_project_keys"] = ["proj-a", "proj-b"]
    body = {key: item for key, item in fake_found.items() if key != "artifact_sha256"}
    fake_found["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        validate_cohort_terminal(
            fake_found,
            controller_source_sha256=controller,
            successors=exhausted_successors,
            ordinal8=exhausted_ordinal8,
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
