from __future__ import annotations

import hashlib
import os
import subprocess
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
    PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256,
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
        assert (
            validated["project_cluster_authority_artifact_sha256"]
            == PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256
        )
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
        ("project_cluster_authority_artifact_sha256", "4" * 64),
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
    root = _repo_root_from_test_file()
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
    PROJECT_CLUSTER_AUTHORITY_RELPATH,
    STAGING_RELDIR,
    VERIFIED_BRIDGE_RELPATH,
    validate_multiproject_preflight,
)
from scripts.p3_v3.run_prospective_multiproject_paired_slice import main

_OLD_FIXED_WORKTREE = "/tmp/" + "p3-c3-applicability-authority"
_FOCUSED_TEST_RELPATHS = (
    Path("tests/p3_v3/test_prospective_multiproject.py"),
    Path("tests/p3_v3/test_prospective_applicability_search_v2.py"),
    Path("tests/p3_v3/test_applicability_authority.py"),
)


def _repo_root_from_test_file() -> Path:
    return Path(__file__).resolve().parents[2]


def test_focused_tests_run_from_any_checkout_without_fixed_tmp_worktree():
    root = _repo_root_from_test_file()
    assert (root / "src/p3_v3/prospective_multiproject.py").is_file()
    assert (root / "scripts/p3_v3/run_prospective_multiproject_paired_slice.py").is_file()
    for relpath in _FOCUSED_TEST_RELPATHS:
        text = (root / relpath).read_text(encoding="utf-8")
        assert _OLD_FIXED_WORKTREE not in text


def _copy_frozen_identity_tree(real_root: Path, dest_root: Path) -> None:
    for rel in (
        DESIGN_RELPATH,
        AUTHORITY_RELPATH,
        PROJECT_CLUSTER_AUTHORITY_RELPATH,
        VERIFIED_BRIDGE_RELPATH,
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
    root = _repo_root_from_test_file()
    payload = validate_multiproject_preflight(
        repo_root=root,
        controller_path=root / "src/p3_v3/prospective_multiproject.py",
    )
    assert payload["status"] == "MULTIPROJECT_PREFLIGHT_PASS"
    assert payload["successor_count"] == 14
    assert opened == []
    assert OFFICIAL_RUN_AUTHORIZED is False


def test_preflight_rejects_existing_official_namespace(tmp_path: Path):
    real_root = _repo_root_from_test_file()
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
    root = _repo_root_from_test_file()
    official = root / "data/p3_v3/phase3/prospective-multiproject-paired-slice-v1/cohort-terminal.json"
    monkeypatch.setattr(sys, "argv", ["run_prospective_multiproject_paired_slice.py"])
    code = main()
    assert code == 2
    stdout = capsys.readouterr().out
    payload = json.loads(stdout)
    assert payload["status"] == "MULTIPROJECT_OFFICIAL_RUN_NOT_AUTHORIZED"
    assert payload["official_terminal_written"] is False
    assert official.exists() is False


def test_cli_constructs_unique_production_seams_without_opening_ordinal_9(monkeypatch, capsys):
    import scripts.p3_v3.run_prospective_multiproject_paired_slice as cli

    constructed: list[str] = []
    opened_ordinals: list[object] = []

    def fake_binder(repo_root=None):
        constructed.append("binder")

        def bind(successor):
            opened_ordinals.append(successor.successor_ordinal)
            raise AssertionError("production binder invoked")

        return bind

    def fake_processor(repo_root=None):
        constructed.append("processor")

        def process(successor):
            opened_ordinals.append(successor.successor_ordinal)
            raise AssertionError("production processor invoked")

        return process

    monkeypatch.setattr(cli, "production_project_binder", fake_binder)
    monkeypatch.setattr(cli, "production_subject_processor", fake_processor)
    monkeypatch.setattr(
        cli,
        "run_multiproject_search",
        lambda **kwargs: opened_ordinals.append("search"),
    )
    monkeypatch.setattr(sys, "argv", ["run_prospective_multiproject_paired_slice.py"])
    assert main() == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "MULTIPROJECT_OFFICIAL_RUN_NOT_AUTHORIZED"
    assert payload["official_terminal_written"] is False
    assert constructed == ["binder", "processor"]
    assert opened_ordinals == []
    assert OFFICIAL_RUN_AUTHORIZED is False
    assert not (_repo_root_from_test_file() / OFFICIAL_RELDIR).exists()
    assert not (_repo_root_from_test_file() / STAGING_RELDIR).exists()


def test_direct_cli_process_returns_unauthorized_before_ordinal_9():
    root = _repo_root_from_test_file()
    completed = subprocess.run(
        [sys.executable, str(root / "scripts/p3_v3/run_prospective_multiproject_paired_slice.py")],
        cwd=str(root),
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout.decode("utf-8"))
    assert payload["status"] == "MULTIPROJECT_OFFICIAL_RUN_NOT_AUTHORIZED"
    assert payload["official_terminal_written"] is False
    combined = (completed.stdout + completed.stderr).decode("utf-8")
    assert "ModuleNotFoundError" not in combined
    assert "public-behavior-frame-" not in combined


from p3_v3.prospective_multiproject import (
    FAILURE_TERMINALS,
    FUNNEL_TERMINALS,
    PRODUCTION_PROCESSOR_STAGES,
    VERIFIED_BRIDGE_RELPATH,
    bind_production_project_identity,
    load_frozen_bridge_identity_records,
    process_production_subject,
    production_project_binder,
    production_subject_processor,
)

_FORBIDDEN_PROJECT_KEY_FIELDS = frozenset({
    "neutral_snapshot_id",
    "controlled_subject_id",
    "source_archive_sha256",
    "build_descriptor_sha256",
    "ecosystem",
    "language_family",
    "p12_repository_identity",
})


def _ordinal8_successor() -> SuccessorIdentity:
    return SuccessorIdentity(
        successor_ordinal=8,
        neutral_snapshot_id="4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b",
        controlled_subject_source_id="667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0",
        controlled_subject_id="0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48",
    )


def test_frozen_35_subject_identity_uniquely_matches_successors_9_to_22():
    root = _repo_root_from_test_file()
    records = load_frozen_bridge_identity_records(root)
    assert len(records) == 35
    neutrals = [row["neutral_snapshot_id"] for row in records]
    assert len(set(neutrals)) == 35
    successors = load_frozen_successors()
    assert [row.successor_ordinal for row in successors] == list(range(9, 23))
    for successor in successors:
        matches = [
            row for row in records if row["neutral_snapshot_id"] == successor.neutral_snapshot_id
        ]
        assert len(matches) == 1
        assert _FORBIDDEN_PROJECT_KEY_FIELDS.isdisjoint(
            {
                key
                for key in matches[0]
                if key in {
                    "originating_repository_identity",
                    "originating_p12_repository_identity",
                    "originating_repository",
                }
            }
        )
        assert "originating_repository_identity" not in matches[0]
        assert "originating_repository" not in matches[0]


def test_production_binder_rejects_user_map_ordinal_8_and_covers_ordinals_9_to_22():
    root = _repo_root_from_test_file()
    successors = load_frozen_successors()
    first = successors[0]
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        bind_production_project_identity(
            first,
            repo_root=root,
            project_map={first.successor_ordinal: "github.com/example/user-map"},
        )
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        bind_production_project_identity(_ordinal8_successor(), repo_root=root)
    binder = production_project_binder(repo_root=root)
    keys = []
    for successor in successors:
        key = binder(successor)
        keys.append(key)
        assert "/" in key
        assert successor.neutral_snapshot_id not in key
    assert [row.successor_ordinal for row in successors] == list(range(9, 23))
    assert len(keys) == 14
    assert 8 not in [row.successor_ordinal for row in successors]


def test_production_binder_does_not_use_forbidden_identity_fields_as_project_key():
    root = _repo_root_from_test_file()
    records = load_frozen_bridge_identity_records(root)
    successors = load_frozen_successors()
    shared = {}
    for successor in successors:
        record = next(
            row for row in records if row["neutral_snapshot_id"] == successor.neutral_snapshot_id
        )
        shared.setdefault(record["build_descriptor_sha256"], []).append(successor.successor_ordinal)
    assert any(len(ordinals) > 1 for ordinals in shared.values())
    binder = production_project_binder(repo_root=root)
    keys = []
    for successor in successors:
        key = binder(successor)
        keys.append(key)
        record = next(
            row for row in records if row["neutral_snapshot_id"] == successor.neutral_snapshot_id
        )
        assert key not in {
            successor.neutral_snapshot_id,
            record["source_archive_sha256"],
            record["build_descriptor_sha256"],
        }
    assert keys
    assert all(key.count("/") == 2 for key in keys)
    bridge = json.loads((root / VERIFIED_BRIDGE_RELPATH).read_text(encoding="utf-8"))
    inventory_repo = bridge["p12_repository_identity"]
    assert inventory_repo == "github.com/meng004/P12-Defect4MR"
    assert inventory_repo not in keys


def test_production_processor_stages_and_selector_rejection():
    assert PRODUCTION_PROCESSOR_STAGES == (
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
    root = _repo_root_from_test_file()
    first = load_frozen_successors()[0]
    with pytest.raises(TypeError):
        process_production_subject(first, repo_root=root, skip=True)
    with pytest.raises(TypeError):
        process_production_subject(first, repo_root=root, retry=True)
    with pytest.raises(TypeError):
        process_production_subject(first, repo_root=root, resume=True)
    with pytest.raises(TypeError):
        process_production_subject(first, repo_root=root, order=(9, 10))
    with pytest.raises(TypeError):
        process_production_subject(first, repo_root=root, pair_count=4)
    with pytest.raises(TypeError):
        process_production_subject(first, repo_root=root, site="x")
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        process_production_subject(_ordinal8_successor(), repo_root=root)
    assert MAX_PAIRS_PER_SUBJECT == 4
    assert FUNNEL_TERMINALS.isdisjoint(FAILURE_TERMINALS)
    assert SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE in FUNNEL_TERMINALS
    assert SubjectTerminal.SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT in FUNNEL_TERMINALS
    assert SubjectTerminal.PAIR_CONSTRUCTION_UNAVAILABLE in FUNNEL_TERMINALS
    assert SubjectTerminal.INFRASTRUCTURE_FAILURE in FAILURE_TERMINALS
    assert SubjectTerminal.IDENTITY_CONFLICT in FAILURE_TERMINALS


def test_production_processor_does_not_open_ordinal_9_or_call_forbidden_seams(monkeypatch):
    root = _repo_root_from_test_file()
    opened: list[str] = []
    called: list[str] = []
    real_open = open

    def guarded_open(path, *args, **kwargs):
        text = str(path)
        if "public-behavior-frame-" in text or ".pbf" in text.lower():
            opened.append(text)
        return real_open(path, *args, **kwargs)

    def forbidden(*args, **kwargs):
        called.append("forbidden")
        raise AssertionError("forbidden production seam was called")

    monkeypatch.setattr("builtins.open", guarded_open)
    monkeypatch.setattr(
        "p3_v3.applicability_predicates.close_slot_with_authority", forbidden, raising=False
    )
    monkeypatch.setattr("p3_v3.pilot_source.run_restore_production_source", forbidden, raising=False)
    monkeypatch.setattr("p3_v3.contract_authority.build_ordinal8_contracts", forbidden, raising=False)
    monkeypatch.setattr("p3_v3.contract_authority.freeze_ordinal8_package", forbidden, raising=False)
    processor = production_subject_processor(repo_root=root)
    first = load_frozen_successors()[0]
    assert first.successor_ordinal == 9
    with pytest.raises(EvidenceError) as excinfo:
        processor(first)
    assert excinfo.value.code == "SLICE_B_PROCESSOR_AUTHORITY_REQUIRED"
    assert opened == []
    assert called == []
    assert first.successor_ordinal == 9


_FROZEN_BRIDGE_RECORD_KEYS = frozenset({
    "neutral_snapshot_id",
    "fixed_tree_commitment",
    "normalized_source_tree_sha256",
    "source_archive_sha256",
    "build_descriptor_sha256",
    "eligibility_reason",
    "eligible_for_construct",
    "eligible_for_criterion",
})


def test_frozen_bridge_has_no_legal_seam_for_originating_repository_identity():
    from p3_v3.artifacts import canonical_sha256, validate_exact_object
    from p3_v3.bridge_and_frames import _RECORD_SCHEMA

    root = _repo_root_from_test_file()
    bridge = json.loads((root / VERIFIED_BRIDGE_RELPATH).read_text(encoding="utf-8"))
    assert len(bridge["records"]) == 35
    for record in bridge["records"]:
        assert set(record) == _FROZEN_BRIDGE_RECORD_KEYS
        assert "originating_repository_identity" not in record
    mutated = dict(bridge["records"][0])
    mutated["originating_repository_identity"] = "github.com/example/demo"
    with pytest.raises(EvidenceError, match="keys differ"):
        validate_exact_object(mutated, _RECORD_SCHEMA, "bridge.records[0]")
    rewritten = [dict(row) for row in bridge["records"]]
    rewritten[0] = mutated
    assert canonical_sha256(rewritten) != bridge["eligible_inventory_root_sha256"]


_CONTENT_JOINED = {
    "09d68a08265580090b8f294221b1c98c91ba95d9c3d357219341569bc6ed0fef": "github.com/scipy/scipy",
    "0e5083ae446a47f6baf389a1b395454da59dea57586e3e2a8d143e8bc63b1b32": "github.com/scipy/scipy",
    "4bd7cd8976f2ced7956c2cbd9b1c0644f5ecd51b020008cc867dc1cf3e4692af": "github.com/scipy/scipy",
    "6dbda0ca35433b15550b35780460f4cbedc21ed4afc34a5c17bae8da9f3d2300": "github.com/sciml/ordinarydiffeq.jl",
    "748ce0fa24a32b11d2f8096f9b6803943a9b5998ab9fa600b0cc781607836bb1": "github.com/amrex-astro/castro",
    "76adbf4193d953c4fdc0933a30495976ffa128585255db9621573d2090670e02": "github.com/lammps/lammps",
    "78d4f9c45640bac958bdd85ea4597432c3e956e3aea084c58c99a39b7bb18a0a": "github.com/sciml/ordinarydiffeq.jl",
    "8fc2d3296ad1245742455682fe2e6b98489cb8776553bea9acf10c599bbd15c8": "github.com/vislearn/freia",
    "95e5fd62f2fa59f819fe6583d1fc7b9ce5755f9024f482592cc4aff6b677dc42": "github.com/drtimothyaldendavis/suitesparse",
    "a15c7019d4627aa01064874a3414923571e6dadec35ddd13a1551cd8c762883a": "github.com/mreineck/pocketfft",
    "f91f803b4cf9f187a4718fe96a5ad03c00cebe1e4b1b4f2eceef9f377956ef2f": "github.com/sciml/datainterpolations.jl",
}


def test_local_project_cluster_authority_has_35_ids_and_19_repositories():
    from p3_v3.prospective_multiproject import (
        PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256,
        load_project_cluster_authority,
    )

    root = _repo_root_from_test_file()
    mapping = load_project_cluster_authority(
        authority_path=root / PROJECT_CLUSTER_AUTHORITY_RELPATH,
        verified_bridge_path=root / VERIFIED_BRIDGE_RELPATH,
    )
    bridge = json.loads((root / VERIFIED_BRIDGE_RELPATH).read_text(encoding="utf-8"))
    authority = json.loads((root / PROJECT_CLUSTER_AUTHORITY_RELPATH).read_text(encoding="utf-8"))
    assert set(mapping) == {row["neutral_snapshot_id"] for row in bridge["records"]}
    assert len(mapping) == 35
    assert len(set(mapping.values())) == 19
    assert [row["neutral_snapshot_id"] for row in authority["records"]] == sorted(mapping)
    assert authority["artifact_sha256"] == PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256
    body = {key: value for key, value in authority.items() if key != "artifact_sha256"}
    assert authority["artifact_sha256"] == canonical_sha256(body)
    for snapshot, repository in _CONTENT_JOINED.items():
        assert mapping[snapshot] == repository


def test_authority_self_hash_and_user_map_remain_fail_closed(tmp_path: Path):
    from p3_v3.prospective_multiproject import load_project_cluster_authority

    root = _repo_root_from_test_file()
    authority = json.loads((root / PROJECT_CLUSTER_AUTHORITY_RELPATH).read_text(encoding="utf-8"))
    authority["artifact_sha256"] = "0" * 64
    bad = tmp_path / "bad-authority.json"
    bad.write_text(json.dumps(authority), encoding="utf-8")
    with pytest.raises(EvidenceError, match="self-hash"):
        load_project_cluster_authority(
            authority_path=bad,
            verified_bridge_path=root / VERIFIED_BRIDGE_RELPATH,
        )
    first = load_frozen_successors()[0]
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        bind_production_project_identity(
            first,
            repo_root=root,
            project_map={"github.com/example/user-map": first.neutral_snapshot_id},
        )


def test_placed_content_joined_archives_match_frozen_bridge_hashes():
    root = _repo_root_from_test_file()
    bridge = {
        row["neutral_snapshot_id"]: row
        for row in json.loads((root / VERIFIED_BRIDGE_RELPATH).read_text(encoding="utf-8"))["records"]
    }
    checked = 0
    for snapshot in _CONTENT_JOINED:
        archive = root / "data/p3_v3/p12_intake/archives" / f"{snapshot}.tar"
        if not archive.is_file():
            continue
        assert file_sha256(archive) == bridge[snapshot]["source_archive_sha256"]
        checked += 1
    assert checked == 11


def test_ordinal_8_still_excluded_from_processor_after_local_authority():
    root = _repo_root_from_test_file()
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        process_production_subject(_ordinal8_successor(), repo_root=root)
    first = load_frozen_successors()[0]
    with pytest.raises(EvidenceError) as excinfo:
        process_production_subject(first, repo_root=root)
    assert excinfo.value.code == "SLICE_B_PROCESSOR_AUTHORITY_REQUIRED"
    assert first.successor_ordinal == 9
