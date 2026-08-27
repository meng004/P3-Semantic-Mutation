from __future__ import annotations

import hashlib
import inspect
from collections import Counter
from collections.abc import Mapping

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256, validate_sha256
from p3_v3.slot_inventory import (
    MECHANISM_ORDER,
    SEMANTIC_CONTRACT_FAMILIES,
    freeze_slot_inventory,
    project_controlled_subject_ids,
    slot_id,
)

FORBIDDEN_SLOT_FIELDS = {
    "site",
    "site_id",
    "path",
    "symbol",
    "applicability",
    "profiling",
    "profiling_results",
    "contract",
    "patch",
    "outcome",
    "technique",
    "project",
}


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _identity_records(count: int = 35) -> list[dict[str, str]]:
    return [
        {
            "normalized_source_tree_sha256": _digest(f"tree-{index}"),
            "build_descriptor_sha256": _digest(f"build-{index}"),
            "public_workload_set_sha256": _digest(f"work-{index}"),
        }
        for index in range(count)
    ]


def test_project_controlled_subject_ids_sorts_35_unique_sha256():
    records = list(reversed(_identity_records()))
    ids = project_controlled_subject_ids(records)
    assert len(ids) == 35
    assert len(set(ids)) == 35
    assert ids == tuple(sorted(ids))
    assert ids == project_controlled_subject_ids(_identity_records())
    for item in ids:
        validate_sha256(item, "controlled_subject_id")
        assert item == item.lower()


def test_project_controlled_subject_ids_rejects_extra_or_missing_fields():
    extra = {**_identity_records()[0], "scale_class": "S"}
    with pytest.raises(EvidenceError, match="E_SUBJECT_IDENTITY"):
        project_controlled_subject_ids([extra, *_identity_records()[1:]])
    missing = {
        "normalized_source_tree_sha256": _digest("tree"),
        "build_descriptor_sha256": _digest("build"),
    }
    with pytest.raises(EvidenceError, match="E_SUBJECT_IDENTITY"):
        project_controlled_subject_ids([missing, *_identity_records()[1:]])


def test_project_controlled_subject_ids_rejects_duplicate_missing_or_illegal_count():
    records = _identity_records()
    with pytest.raises(EvidenceError, match="E_SUBJECT_IDENTITY"):
        project_controlled_subject_ids(records + [records[0]])
    with pytest.raises(EvidenceError, match="E_SUBJECT_IDENTITY"):
        project_controlled_subject_ids(records[:34])
    bad = {**records[0], "public_workload_set_sha256": "not-a-sha"}
    with pytest.raises(EvidenceError, match="E_SHA256"):
        project_controlled_subject_ids([bad, *records[1:]])


def test_freeze_slot_inventory_counts_and_rebuildable_ids():
    ids = project_controlled_subject_ids(_identity_records())
    inventory = freeze_slot_inventory(ids)
    slots = inventory["slots"]
    assert inventory["schema_version"] == "p3-slot-inventory-v1"
    assert inventory["artifact_sha256"] == canonical_sha256(
        {key: value for key, value in inventory.items() if key != "artifact_sha256"}
    )
    assert len(slots) == 350
    assert {row["controlled_subject_id"] for row in slots} == set(ids)
    per_subject = Counter(row["controlled_subject_id"] for row in slots)
    assert set(per_subject.values()) == {10}
    per_family = Counter(row["semantic_contract_family"] for row in slots)
    assert per_family == {family: 70 for family in SEMANTIC_CONTRACT_FAMILIES}
    per_cell = Counter(
        (row["semantic_contract_family"], row["permitted_construction_mechanism"])
        for row in slots
    )
    assert len(per_cell) == 25
    assert set(per_cell.values()) == {14}
    rebuilt = {
        slot_id(
            row["controlled_subject_id"],
            row["semantic_contract_family"],
            row["slot_ordinal"],
            row["permitted_construction_mechanism"],
        )
        for row in slots
    }
    assert rebuilt == {row["slot_id"] for row in slots}
    assert len(rebuilt) == 350


def test_freeze_slot_inventory_ignores_input_order_and_omits_outcome_fields():
    ids = project_controlled_subject_ids(_identity_records())
    left = freeze_slot_inventory(ids)
    right = freeze_slot_inventory(list(reversed(ids)))
    assert left == right
    for row in left["slots"]:
        assert set(row) == {
            "slot_id",
            "controlled_subject_id",
            "semantic_contract_family",
            "slot_ordinal",
            "permitted_construction_mechanism",
        }
        assert FORBIDDEN_SLOT_FIELDS.isdisjoint(row)
    ordered = left["slots"]
    assert ordered == sorted(
        ordered,
        key=lambda row: (
            row["controlled_subject_id"],
            SEMANTIC_CONTRACT_FAMILIES.index(row["semantic_contract_family"]),
            row["slot_ordinal"],
            MECHANISM_ORDER.index(row["permitted_construction_mechanism"]),
            row["slot_id"],
        ),
    )


def test_freeze_slot_inventory_rejects_illegal_subject_ids():
    ids = list(project_controlled_subject_ids(_identity_records()))
    with pytest.raises(EvidenceError, match="E_SLOT_INVENTORY"):
        freeze_slot_inventory(ids + [ids[0]])
    with pytest.raises(EvidenceError, match="E_SHA256"):
        freeze_slot_inventory(["not-a-sha", *ids[1:]])
    with pytest.raises(EvidenceError, match="E_SLOT_INVENTORY"):
        freeze_slot_inventory(ids[:10])


def test_mechanism_formula_is_index_plus_ordinal_mod_five():
    ids = project_controlled_subject_ids(_identity_records())
    slots = freeze_slot_inventory(ids)["slots"]
    by_subject = {subject_id: [] for subject_id in ids}
    for row in slots:
        by_subject[row["controlled_subject_id"]].append(row)
    for subject_index, subject_id in enumerate(ids):
        rows = by_subject[subject_id]
        assert len(rows) == 10
        for row in rows:
            expected = MECHANISM_ORDER[(subject_index + row["slot_ordinal"]) % 5]
            assert row["permitted_construction_mechanism"] == expected
