from __future__ import annotations

import importlib.util
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
