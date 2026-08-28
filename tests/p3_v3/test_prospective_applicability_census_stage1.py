from __future__ import annotations

import importlib.util
import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256
from p3_v3.prospective_multiproject import load_frozen_successors
from p3_v3.slot_inventory import SEMANTIC_CONTRACT_FAMILIES


MODULE_PATH = Path(__file__).resolve().parents[2] / "src/p3_v3/prospective_applicability_census_stage1.py"
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
    return f"{FAKE_SLOT_PREFIX}{index:02x}" + ("d" * 60)


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


import hashlib

FROZEN_CONTROLLER_SHA256 = (
    "5ab44c9840f44468c556a94b93a7a294858549688c11ca282e660adb5f71c341"
)
STAGE1_AUTH_RELPATH = Path(
    "data/p3_v3/phase3/inputs/"
    "user-auth-prospective-multiproject-applicability-stage1-v2.txt"
)
STAGE1_AUTH_BYTES = (
    b"P3_C3_STAGE1_APPLICABILITY_CENSUS_AUTHORIZED=true\n"
    b"implementation_commit=ee12a75b6dbd3905dcc6acc967beb638ddcc4410\n"
    b"controller_source_sha256="
    b"5ab44c9840f44468c556a94b93a7a294858549688c11ca282e660adb5f71c341\n"
    b"design_file_sha256="
    b"a8828022ee2095b4209261c26d0ecbab66141e59b2c9f18ce3df2045f6dd79c5\n"
)
STAGE1_AUTH_SHA256 = (
    "cde781bbe0bd25514b117c55563ac2b88720574da274bf98d3f3f0a56308d60d"
)


def _cli_module():
    from scripts.p3_v3 import run_prospective_multiproject_applicability_stage1_v2 as cli

    return cli


def _unauthorized_payload() -> dict[str, object]:
    return {
        "status": "STAGE1_OFFICIAL_RUN_NOT_AUTHORIZED",
        "slice_id": "p3-c3-prospective-multiproject-applicability-stage1-v2",
        "design_commit": "270025608be7db631484b77ffda181438100d785",
        "official_run_authorized": False,
        "official_terminal_written": False,
        "successor_count": 14,
    }


def _install_auth(cli, monkeypatch, tmp_path: Path, data: bytes, *, kind: str = "file") -> Path:
    target = tmp_path / "stage1-auth.txt"
    if kind == "dir":
        target.mkdir()
    elif kind == "symlink":
        real = tmp_path / "real-auth.txt"
        real.write_bytes(data)
        target.symlink_to(real)
    else:
        target.write_bytes(data)
    monkeypatch.setattr(cli, "STAGE1_AUTHORIZATION_PATH", target)
    return target


def test_cli_authorized_path_uses_synthetic_processor_only(tmp_path: Path, monkeypatch):
    from p3_v3.prospective_applicability_census_stage1 import run_stage1_census
    from scripts.p3_v3 import run_prospective_multiproject_applicability_stage1_v2 as cli

    assert hasattr(cli, "require_stage1_authorization")
    processor, inventory, subjects, closures = _synthetic_processor_factory()
    captured: list[object] = []

    def redirected_census(*, repo_root, output_root, staging_root, subject_processor):
        del repo_root, output_root, staging_root
        captured.append(subject_processor)
        if subject_processor is not processor:
            raise AssertionError("authorized CLI test must inject the synthetic processor")
        return run_stage1_census(
            repo_root=tmp_path,
            output_root=tmp_path / "official",
            staging_root=tmp_path / "staging",
            subject_processor=processor,
        )

    _install_auth(cli, monkeypatch, tmp_path, STAGE1_AUTH_BYTES)
    monkeypatch.setattr(cli, "process_stage1_subject", processor)
    monkeypatch.setattr(cli, "run_stage1_census", redirected_census)
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 0
    assert captured == [processor]
    assert (tmp_path / "official" / "cohort-terminal.json").is_file()
    assert (
        _repo_root()
        / "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2"
    ).exists() is False
    assert (_repo_root() / STAGE1_AUTH_RELPATH).exists() is False


def test_cli_does_not_flip_authorization_for_real_processor():
    from p3_v3.artifacts import file_sha256
    from p3_v3.prospective_applicability_census_stage1 import OFFICIAL_RUN_AUTHORIZED

    source = (
        _repo_root() / "src/p3_v3/prospective_applicability_census_stage1.py"
    ).read_text(encoding="utf-8")
    cli_source = (
        _repo_root()
        / "scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py"
    ).read_text(encoding="utf-8")
    assert "OFFICIAL_RUN_AUTHORIZED = False" in source
    assert "OFFICIAL_RUN_AUTHORIZED = True" not in source
    assert "OFFICIAL_RUN_AUTHORIZED = True" not in cli_source
    assert "OFFICIAL_RUN_AUTHORIZED = False" not in cli_source
    assert OFFICIAL_RUN_AUTHORIZED is False
    assert file_sha256(
        _repo_root() / "src/p3_v3/prospective_applicability_census_stage1.py"
    ) == FROZEN_CONTROLLER_SHA256
    assert (_repo_root() / STAGE1_AUTH_RELPATH).exists() is False
    assert (_repo_root() / STAGE1_AUTH_RELPATH).is_symlink() is False


def test_stage1_authorization_constants_are_exact_bytes():
    cli = _cli_module()
    assert hasattr(cli, "STAGE1_AUTHORIZATION_PATH")
    assert hasattr(cli, "STAGE1_AUTHORIZATION_BYTES")
    assert hasattr(cli, "STAGE1_AUTHORIZATION_SHA256")
    assert hasattr(cli, "require_stage1_authorization")
    assert cli.STAGE1_AUTHORIZATION_PATH == _repo_root() / STAGE1_AUTH_RELPATH
    assert cli.STAGE1_AUTHORIZATION_BYTES == STAGE1_AUTH_BYTES
    assert len(cli.STAGE1_AUTHORIZATION_BYTES) == 287
    assert hashlib.sha256(cli.STAGE1_AUTHORIZATION_BYTES).hexdigest() == STAGE1_AUTH_SHA256
    assert cli.STAGE1_AUTHORIZATION_SHA256 == STAGE1_AUTH_SHA256
    assert "read_authority_snapshot" in (
        _repo_root()
        / "scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py"
    ).read_text(encoding="utf-8")


def test_cli_missing_authorization_file_is_stable_and_does_not_call_census(
    monkeypatch, capsys
):
    cli = _cli_module()
    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 2
    assert json.loads(capsys.readouterr().out) == _unauthorized_payload()
    assert called == []
    assert (_repo_root() / STAGE1_AUTH_RELPATH).exists() is False
    assert (
        _repo_root()
        / "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2"
    ).exists() is False
    assert (
        _repo_root()
        / "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2.staging"
    ).exists() is False


def test_cli_wrong_authorization_bytes_do_not_call_controller(
    tmp_path: Path, monkeypatch, capsys
):
    cli = _cli_module()
    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    _install_auth(cli, monkeypatch, tmp_path, STAGE1_AUTH_BYTES[:-1] + b"X")
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 2
    assert json.loads(capsys.readouterr().out) == _unauthorized_payload()
    assert called == []


def test_cli_authorization_missing_final_newline_is_rejected(
    tmp_path: Path, monkeypatch, capsys
):
    cli = _cli_module()
    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    _install_auth(cli, monkeypatch, tmp_path, STAGE1_AUTH_BYTES[:-1])
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 2
    assert json.loads(capsys.readouterr().out)["status"] == "STAGE1_OFFICIAL_RUN_NOT_AUTHORIZED"
    assert called == []


def test_cli_authorization_crlf_is_rejected(tmp_path: Path, monkeypatch, capsys):
    cli = _cli_module()
    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    _install_auth(cli, monkeypatch, tmp_path, STAGE1_AUTH_BYTES.replace(b"\n", b"\r\n"))
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 2
    assert json.loads(capsys.readouterr().out)["status"] == "STAGE1_OFFICIAL_RUN_NOT_AUTHORIZED"
    assert called == []


def test_cli_authorization_extra_space_or_line_is_rejected(
    tmp_path: Path, monkeypatch, capsys
):
    cli = _cli_module()
    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    for data in (STAGE1_AUTH_BYTES + b" ", STAGE1_AUTH_BYTES + b"extra\n"):
        _install_auth(cli, monkeypatch, tmp_path, data)
        assert main() == 2
        assert called == []
    assert json.loads(capsys.readouterr().out.splitlines()[-1])["status"] == (
        "STAGE1_OFFICIAL_RUN_NOT_AUTHORIZED"
    )


def test_cli_authorization_symlink_is_rejected(tmp_path: Path, monkeypatch, capsys):
    cli = _cli_module()
    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    _install_auth(cli, monkeypatch, tmp_path, STAGE1_AUTH_BYTES, kind="symlink")
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 2
    assert json.loads(capsys.readouterr().out)["status"] == "STAGE1_OFFICIAL_RUN_NOT_AUTHORIZED"
    assert called == []


def test_cli_authorization_directory_is_rejected(tmp_path: Path, monkeypatch, capsys):
    cli = _cli_module()
    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    _install_auth(cli, monkeypatch, tmp_path, STAGE1_AUTH_BYTES, kind="dir")
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 2
    assert json.loads(capsys.readouterr().out)["status"] == "STAGE1_OFFICIAL_RUN_NOT_AUTHORIZED"
    assert called == []


def test_cli_exact_authorization_digest_and_synthetic_census_once(
    tmp_path: Path, monkeypatch
):
    cli = _cli_module()
    assert len(STAGE1_AUTH_BYTES) == 287
    assert hashlib.sha256(STAGE1_AUTH_BYTES).hexdigest() == STAGE1_AUTH_SHA256
    assert cli.require_stage1_authorization.__name__ == "require_stage1_authorization"
    _install_auth(cli, monkeypatch, tmp_path, STAGE1_AUTH_BYTES)
    assert cli.require_stage1_authorization() == STAGE1_AUTH_SHA256
    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 0
    assert len(called) == 1
    assert called[0]["subject_processor"] is cli.process_stage1_subject
    assert called[0]["output_root"] == _repo_root() / (
        "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2"
    )
    assert called[0]["staging_root"] == _repo_root() / (
        "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2.staging"
    )
    assert (
        _repo_root()
        / "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2"
    ).exists() is False


def test_cli_extra_args_fail_even_with_exact_authorization(
    tmp_path: Path, monkeypatch, capsys
):
    cli = _cli_module()
    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    _install_auth(cli, monkeypatch, tmp_path, STAGE1_AUTH_BYTES)
    monkeypatch.setattr(sys, "argv", ["run_stage1.py", "--resume"])
    assert main() == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PREFLIGHT_FAIL"
    assert payload["official_terminal_written"] is False
    assert called == []


def test_cli_env_and_stdin_cannot_bypass_missing_authorization(
    monkeypatch, capsys
):
    import io

    cli = _cli_module()
    called = []
    monkeypatch.setattr(cli, "run_stage1_census", lambda **kwargs: called.append(kwargs))
    monkeypatch.setenv("OFFICIAL_RUN_AUTHORIZED", "true")
    monkeypatch.setenv("STAGE1_AUTHORIZATION_SHA256", STAGE1_AUTH_SHA256)
    monkeypatch.setattr(sys, "stdin", io.BytesIO(STAGE1_AUTH_BYTES))
    monkeypatch.setattr(sys, "argv", ["run_stage1.py"])
    assert main() == 2
    assert json.loads(capsys.readouterr().out) == _unauthorized_payload()
    assert called == []
    assert (_repo_root() / STAGE1_AUTH_RELPATH).exists() is False


def test_controller_sha_and_official_authorization_file_remain_frozen():
    from p3_v3.artifacts import file_sha256

    assert file_sha256(
        _repo_root() / "src/p3_v3/prospective_applicability_census_stage1.py"
    ) == FROZEN_CONTROLLER_SHA256
    assert (_repo_root() / STAGE1_AUTH_RELPATH).exists() is False


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
