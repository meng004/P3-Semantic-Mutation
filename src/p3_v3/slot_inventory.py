from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    read_canonical_json,
    validate_exact_object,
    validate_sha256,
)

SEMANTIC_CONTRACT_FAMILIES = ("INV", "MONO", "CONV", "DYN", "CMP")
MECHANISM_ORDER = ("CE", "OS", "HP", "TF", "SI")
_IDENTITY_SCHEMA = {
    "normalized_source_tree_sha256": str,
    "build_descriptor_sha256": str,
    "public_workload_set_sha256": str,
}
_SLOT_ROW_SCHEMA = {
    "slot_id": str,
    "controlled_subject_id": str,
    "semantic_contract_family": str,
    "slot_ordinal": int,
    "permitted_construction_mechanism": str,
}


def slot_id(
    controlled_subject_id: str,
    semantic_contract_family: str,
    slot_ordinal: int,
    permitted_construction_mechanism: str,
) -> str:
    validate_sha256(controlled_subject_id, "controlled_subject_id")
    if semantic_contract_family not in SEMANTIC_CONTRACT_FAMILIES:
        raise EvidenceError("E_SLOT_INVENTORY", "unknown semantic_contract_family")
    if slot_ordinal not in (0, 1):
        raise EvidenceError("E_SLOT_INVENTORY", "slot_ordinal must be 0 or 1")
    if permitted_construction_mechanism not in MECHANISM_ORDER:
        raise EvidenceError("E_SLOT_INVENTORY", "unknown permitted_construction_mechanism")
    return canonical_sha256(
        {
            "domain": "P3-SLOT-IDENTITY-v1",
            "controlled_subject_id": controlled_subject_id,
            "semantic_contract_family": semantic_contract_family,
            "slot_ordinal": slot_ordinal,
            "permitted_construction_mechanism": permitted_construction_mechanism,
        }
    )


def project_controlled_subject_ids(
    phase1_identity_records: Sequence[Mapping[str, object]],
) -> tuple[str, ...]:
    if not isinstance(phase1_identity_records, Sequence) or isinstance(
        phase1_identity_records, (str, bytes)
    ):
        raise EvidenceError("E_SUBJECT_IDENTITY", "identity records must be a sequence")
    if len(phase1_identity_records) != 35:
        raise EvidenceError("E_SUBJECT_IDENTITY", "identity projection requires 35 records")
    ids: list[str] = []
    seen: set[str] = set()
    for index, raw in enumerate(phase1_identity_records):
        try:
            record = validate_exact_object(dict(raw), _IDENTITY_SCHEMA, f"identity[{index}]")
        except EvidenceError as exc:
            raise EvidenceError("E_SUBJECT_IDENTITY", str(exc)) from exc
        tree = validate_sha256(
            record["normalized_source_tree_sha256"], "normalized_source_tree_sha256"
        )
        build = validate_sha256(record["build_descriptor_sha256"], "build_descriptor_sha256")
        workload = validate_sha256(
            record["public_workload_set_sha256"], "public_workload_set_sha256"
        )
        subject = canonical_sha256(
            {
                "normalized_source_tree_sha256": tree,
                "build_descriptor_sha256": build,
                "public_workload_set_sha256": workload,
                "domain": "P3-SUBJECT-v1",
            }
        )
        if subject in seen:
            raise EvidenceError("E_SUBJECT_IDENTITY", "duplicate controlled_subject_id")
        seen.add(subject)
        ids.append(subject)
    return tuple(sorted(ids))


def freeze_slot_inventory(
    controlled_subject_ids: Sequence[str],
) -> dict[str, object]:
    if not isinstance(controlled_subject_ids, Sequence) or isinstance(
        controlled_subject_ids, (str, bytes)
    ):
        raise EvidenceError("E_SLOT_INVENTORY", "controlled_subject_ids must be a sequence")
    validated: list[str] = []
    seen: set[str] = set()
    for index, raw in enumerate(controlled_subject_ids):
        subject_id = validate_sha256(raw, f"controlled_subject_ids[{index}]")
        if subject_id in seen:
            raise EvidenceError("E_SLOT_INVENTORY", "duplicate controlled_subject_id")
        seen.add(subject_id)
        validated.append(subject_id)
    if len(validated) != 35:
        raise EvidenceError("E_SLOT_INVENTORY", "inventory requires 35 subject IDs")
    validated.sort()
    rows: list[dict[str, Any]] = []
    for subject_index, subject in enumerate(validated):
        for family in SEMANTIC_CONTRACT_FAMILIES:
            for ordinal in (0, 1):
                mechanism = MECHANISM_ORDER[(subject_index + ordinal) % 5]
                row = {
                    "slot_id": slot_id(subject, family, ordinal, mechanism),
                    "controlled_subject_id": subject,
                    "semantic_contract_family": family,
                    "slot_ordinal": ordinal,
                    "permitted_construction_mechanism": mechanism,
                }
                validate_exact_object(row, _SLOT_ROW_SCHEMA, "slot")
                rows.append(row)
    rows.sort(
        key=lambda row: (
            row["controlled_subject_id"],
            SEMANTIC_CONTRACT_FAMILIES.index(row["semantic_contract_family"]),
            row["slot_ordinal"],
            MECHANISM_ORDER.index(row["permitted_construction_mechanism"]),
            row["slot_id"],
        )
    )
    if len(rows) != 350:
        raise EvidenceError("E_SLOT_INVENTORY", "inventory must contain 350 rows")
    body = {"schema_version": "p3-slot-inventory-v1", "slots": rows}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def load_phase1_identity_records(
    *,
    verified_bridge_path: Path,
    workload_root: Path,
) -> tuple[dict[str, str], ...]:
    bridge = read_canonical_json(verified_bridge_path)
    records = bridge.get("records") if isinstance(bridge, Mapping) else None
    if not isinstance(records, list) or len(records) != 35:
        raise EvidenceError("E_SUBJECT_IDENTITY", "verified bridge must contain 35 records")
    narrowed: list[dict[str, str]] = []
    seen_neutrals: set[str] = set()
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            raise EvidenceError(
                "E_SUBJECT_IDENTITY", f"bridge.records[{index}] must be an object"
            )
        neutral = validate_sha256(
            raw.get("neutral_snapshot_id"), f"records[{index}].neutral_snapshot_id"
        )
        if neutral in seen_neutrals:
            raise EvidenceError("E_SUBJECT_IDENTITY", "duplicate neutral_snapshot_id")
        seen_neutrals.add(neutral)
        workload = read_canonical_json(Path(workload_root) / f"profiling-workload-{neutral}.json")
        if not isinstance(workload, Mapping):
            raise EvidenceError("E_SUBJECT_IDENTITY", "workload artifact must be an object")
        narrowed.append(
            {
                "normalized_source_tree_sha256": raw["normalized_source_tree_sha256"],
                "build_descriptor_sha256": raw["build_descriptor_sha256"],
                "public_workload_set_sha256": workload["artifact_sha256"],
            }
        )
    return tuple(narrowed)
