from __future__ import annotations

import os
import re
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.prospective_multiproject import load_frozen_successors

STAGE1_SLICE_ID = "p3-c3-prospective-multiproject-applicability-stage1-v2"
STAGE1_SCHEMA_VERSION = "p3-c3-prospective-multiproject-applicability-stage1-v2-terminal-v1"
STAGE1_TERMINAL_STATUS = "STAGE1_APPLICABILITY_CENSUS_COMPLETE"
STAGE1_DESIGN_COMMIT = "270025608be7db631484b77ffda181438100d785"
STAGE1_DESIGN_FILE_SHA256 = (
    "a8828022ee2095b4209261c26d0ecbab66141e59b2c9f18ce3df2045f6dd79c5"
)
STAGE1_APPLICABILITY_AUTHORITY_ARTIFACT_SHA256 = (
    "30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214"
)
STAGE1_SLOT_INVENTORY_ARTIFACT_SHA256 = (
    "5c7f2dae8b0b7fd72926e2569354dbf6e878186f69d512e259e6034026dd0e27"
)
STAGE1_PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256 = (
    "802ec9a8db866c1c1d79b29e03d4e5dc0f55d4961a3f415a2486dd562fbf810e"
)
STAGE1_ORDINALS = (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22)
STAGE1_SUBJECT_COUNT = 14
STAGE1_CLOSURES_PER_SUBJECT = 10
STAGE1_CLOSURE_COUNT = 140
STAGE1_OFFICIAL_RELDIR = Path(
    "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2"
)
STAGE1_STAGING_RELDIR = Path(
    "data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2.staging"
)
STAGE1_TERMINAL_FILENAME = "cohort-terminal.json"
STAGE1_DESIGN_RELPATH = Path(
    "docs/superpowers/specs/2026-08-28-p3-c3-two-stage-prospective-paired-slice-design.md"
)
STAGE1_CONTROLLER_RELPATH = Path(
    "src/p3_v3/prospective_applicability_census_stage1.py"
)
STAGE1_CLI_RELPATH = Path(
    "scripts/p3_v3/run_prospective_multiproject_applicability_stage1_v2.py"
)
STAGE1_AUTHORITY_RELPATH = Path("data/p3_v3/phase2/applicability-authority.json")
STAGE1_INVENTORY_RELPATH = Path("data/p3_v3/phase2/slot-inventory.json")
STAGE1_PROJECT_CLUSTER_AUTHORITY_RELPATH = Path(
    "data/p3_v3/phase3/inputs/project-cluster-authority-v1.json"
)
STAGE1_PREDICATE_REGISTRY_RELPATH = Path(
    "data/p3_v3/protocol/applicability-predicate-registry.json"
)
STAGE1_SLOT_IMPLEMENTATION_RELPATH = Path("src/p3_v3/slot_inventory.py")
STAGE1_PREDICATE_IMPLEMENTATION_RELPATH = Path(
    "src/p3_v3/applicability_predicates.py"
)
OLD_V1_OFFICIAL_RELDIR = Path(
    "data/p3_v3/phase3/prospective-multiproject-paired-slice-v1"
)
OLD_V1_STAGING_RELDIR = Path(
    "data/p3_v3/phase3/prospective-multiproject-paired-slice-v1.staging"
)
OFFICIAL_RUN_AUTHORIZED = False
ALLOWED_CLOSURE_STATES = frozenset({
    "SITE_FROZEN",
    "APPLICABILITY_CLOSED_NOT_APPLICABLE",
})
INVENTORY_FAMILY_ORDER = ("INV", "MONO", "CONV", "DYN", "CMP")
_GIT_SHA1_RE = re.compile(r"[0-9a-f]{40}")
FORBIDDEN_TERMINAL_FIELDS = frozenset({
    "timestamp",
    "created_at",
    "hostname",
    "host",
    "random",
    "nonce",
    "contract_id",
    "pair_count",
    "kill_count",
    "survival",
    "overlap",
    "eligibility",
    "PAIRED_EVIDENCE_COMPLETE",
    "SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT",
    "PAIR_CONSTRUCTION_UNAVAILABLE",
    "MULTIPROJECT_COHORT_EXHAUSTED",
    "d_subject",
    "semantic_pair_kills",
    "syntactic_pair_kills",
})
STAGE1_TERMINAL_SCHEMA = {
    "schema_version": str,
    "slice_id": str,
    "design_commit": str,
    "design_file_sha256": str,
    "applicability_authority_artifact_sha256": str,
    "slot_inventory_artifact_sha256": str,
    "project_cluster_authority_artifact_sha256": str,
    "controller_source_sha256": str,
    "terminal_status": str,
    "subjects": list,
    "artifact_sha256": str,
}
STAGE1_SUBJECT_SCHEMA = {
    "successor_ordinal": int,
    "neutral_snapshot_id": str,
    "controlled_subject_source_id": str,
    "controlled_subject_id": str,
    "project_cluster_key": str,
    "closure_artifact_sha256s": list,
    "site_frozen_count": int,
    "not_applicable_count": int,
}

def validate_git_sha1(value: Any, field: str) -> str:
    if not isinstance(value, str) or _GIT_SHA1_RE.fullmatch(value) is None:
        raise EvidenceError("E_STAGE1_IDENTITY", f"{field} must be a 40-character git SHA")
    return value

def sort_stage1_inventory_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    indexed = list(INVENTORY_FAMILY_ORDER)
    return sorted(
        (dict(row) for row in rows),
        key=lambda row: (indexed.index(str(row["semantic_contract_family"])), int(row["slot_ordinal"])),
    )

def inventory_slot_ids_for_subject(
    inventory: Mapping[str, Any],
    controlled_subject_id: str,
) -> tuple[str, ...]:
    from p3_v3.multiproject_production_processor import _subject_inventory_rows

    rows = sort_stage1_inventory_rows(
        _subject_inventory_rows(inventory, controlled_subject_id)
    )
    return tuple(str(row["slot_id"]) for row in rows)

def make_stage1_closure(
    *,
    slot_id: str,
    controlled_subject_id: str,
    state: str,
    site_id: str | None,
) -> dict[str, Any]:
    if state not in ALLOWED_CLOSURE_STATES:
        raise EvidenceError("E_STAGE1_TERMINAL", f"illegal closure state {state}")
    if state == "SITE_FROZEN":
        path = "APPLICABLE"
        if not isinstance(site_id, str):
            raise EvidenceError("E_STAGE1_TERMINAL", "SITE_FROZEN requires site_id")
        validate_sha256(site_id, "site_id")
    else:
        path = "APPLICABILITY_CLOSED_NOT_APPLICABLE"
        if site_id is not None:
            raise EvidenceError("E_STAGE1_TERMINAL", "NOT_APPLICABLE forbids site_id")
    body = {
        "schema_version": "p3-slot-closure-v1",
        "slot_id": validate_sha256(slot_id, "slot_id"),
        "controlled_subject_id": validate_sha256(
            controlled_subject_id, "controlled_subject_id"
        ),
        "site_id": site_id,
        "state": state,
        "path": path,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}

def rebuild_stage1_counts(
    closures: Sequence[Mapping[str, Any]],
) -> tuple[int, int]:
    site_frozen = 0
    not_applicable = 0
    for closure in closures:
        state = closure["state"]
        if state == "SITE_FROZEN":
            site_frozen += 1
        elif state == "APPLICABILITY_CLOSED_NOT_APPLICABLE":
            not_applicable += 1
        else:
            raise EvidenceError("E_STAGE1_TERMINAL", f"illegal closure state {state}")
    if site_frozen + not_applicable != STAGE1_CLOSURES_PER_SUBJECT:
        raise EvidenceError("E_STAGE1_TERMINAL", "closure counts must sum to 10")
    return site_frozen, not_applicable

def build_stage1_terminal(
    *,
    design_commit: str,
    design_file_sha256: str,
    controller_source_sha256: str,
    applicability_authority_artifact_sha256: str,
    slot_inventory_artifact_sha256: str,
    project_cluster_authority_artifact_sha256: str,
    subjects: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for raw in subjects:
        closures = list(raw["closures"])
        site_frozen, not_applicable = rebuild_stage1_counts(closures)
        rows.append({
            "successor_ordinal": int(raw["successor_ordinal"]),
            "neutral_snapshot_id": str(raw["neutral_snapshot_id"]),
            "controlled_subject_source_id": str(raw["controlled_subject_source_id"]),
            "controlled_subject_id": str(raw["controlled_subject_id"]),
            "project_cluster_key": str(raw["project_cluster_key"]),
            "closure_artifact_sha256s": [str(item["artifact_sha256"]) for item in closures],
            "site_frozen_count": site_frozen,
            "not_applicable_count": not_applicable,
        })
    body = {
        "schema_version": STAGE1_SCHEMA_VERSION,
        "slice_id": STAGE1_SLICE_ID,
        "design_commit": design_commit,
        "design_file_sha256": design_file_sha256,
        "applicability_authority_artifact_sha256": applicability_authority_artifact_sha256,
        "slot_inventory_artifact_sha256": slot_inventory_artifact_sha256,
        "project_cluster_authority_artifact_sha256": project_cluster_authority_artifact_sha256,
        "controller_source_sha256": controller_source_sha256,
        "terminal_status": STAGE1_TERMINAL_STATUS,
        "subjects": rows,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}

def validate_stage1_terminal(
    terminal: Mapping[str, Any],
    *,
    expected_design_commit: str,
    expected_design_file_sha256: str,
    expected_controller_source_sha256: str,
    expected_applicability_authority_artifact_sha256: str,
    expected_slot_inventory_artifact_sha256: str,
    expected_project_cluster_authority_artifact_sha256: str,
    subject_closures: Sequence[Sequence[Mapping[str, Any]]],
    inventory: Mapping[str, Any],
) -> dict[str, Any]:
    if FORBIDDEN_TERMINAL_FIELDS.intersection(terminal):
        raise EvidenceError("E_STAGE1_TERMINAL", "forbidden terminal field present")
    payload = validate_exact_object(dict(terminal), STAGE1_TERMINAL_SCHEMA, "stage1-terminal")
    if payload["schema_version"] != STAGE1_SCHEMA_VERSION:
        raise EvidenceError("E_STAGE1_TERMINAL", "illegal schema_version")
    if payload["slice_id"] != STAGE1_SLICE_ID:
        raise EvidenceError("E_STAGE1_TERMINAL", "illegal slice_id")
    if payload["terminal_status"] != STAGE1_TERMINAL_STATUS:
        raise EvidenceError("E_STAGE1_TERMINAL", "illegal terminal_status")
    if payload["design_commit"] != expected_design_commit:
        raise EvidenceError("E_STAGE1_IDENTITY", "design_commit mismatch")
    validate_git_sha1(payload["design_commit"], "design_commit")
    if payload["design_file_sha256"] != expected_design_file_sha256:
        raise EvidenceError("E_STAGE1_IDENTITY", "design_file_sha256 mismatch")
    if payload["controller_source_sha256"] != expected_controller_source_sha256:
        raise EvidenceError("E_STAGE1_IDENTITY", "controller_source_sha256 mismatch")
    if (
        payload["applicability_authority_artifact_sha256"]
        != expected_applicability_authority_artifact_sha256
    ):
        raise EvidenceError("E_STAGE1_IDENTITY", "authority artifact mismatch")
    if payload["slot_inventory_artifact_sha256"] != expected_slot_inventory_artifact_sha256:
        raise EvidenceError("E_STAGE1_IDENTITY", "inventory artifact mismatch")
    if (
        payload["project_cluster_authority_artifact_sha256"]
        != expected_project_cluster_authority_artifact_sha256
    ):
        raise EvidenceError("E_STAGE1_IDENTITY", "project-cluster artifact mismatch")
    validate_sha256(payload["design_file_sha256"], "design_file_sha256")
    validate_sha256(payload["controller_source_sha256"], "controller_source_sha256")
    validate_sha256(
        payload["applicability_authority_artifact_sha256"],
        "applicability_authority_artifact_sha256",
    )
    validate_sha256(
        payload["slot_inventory_artifact_sha256"],
        "slot_inventory_artifact_sha256",
    )
    validate_sha256(
        payload["project_cluster_authority_artifact_sha256"],
        "project_cluster_authority_artifact_sha256",
    )
    subjects = payload["subjects"]
    if len(subjects) != STAGE1_SUBJECT_COUNT:
        raise EvidenceError("E_STAGE1_TERMINAL", "subject count must be 14")
    if len(subject_closures) != STAGE1_SUBJECT_COUNT:
        raise EvidenceError("E_STAGE1_TERMINAL", "subject_closures count must be 14")
    ordinals: list[int] = []
    closure_count = 0
    for index, raw in enumerate(subjects):
        row = validate_exact_object(dict(raw), STAGE1_SUBJECT_SCHEMA, f"subjects[{index}]")
        if FORBIDDEN_TERMINAL_FIELDS.intersection(row):
            raise EvidenceError("E_STAGE1_TERMINAL", "forbidden subject field present")
        ordinals.append(int(row["successor_ordinal"]))
        closures = list(subject_closures[index])
        if len(closures) != STAGE1_CLOSURES_PER_SUBJECT:
            raise EvidenceError("E_STAGE1_TERMINAL", "each subject must have 10 closures")
        if len(row["closure_artifact_sha256s"]) != STAGE1_CLOSURES_PER_SUBJECT:
            raise EvidenceError("E_STAGE1_TERMINAL", "each subject must have 10 closure hashes")
        site_frozen, not_applicable = rebuild_stage1_counts(closures)
        if row["site_frozen_count"] != site_frozen:
            raise EvidenceError("E_STAGE1_TERMINAL", "site_frozen_count does not rebuild")
        if row["not_applicable_count"] != not_applicable:
            raise EvidenceError("E_STAGE1_TERMINAL", "not_applicable_count does not rebuild")
        expected_slot_ids = inventory_slot_ids_for_subject(
            inventory, str(row["controlled_subject_id"])
        )
        observed_slot_ids = tuple(str(item["slot_id"]) for item in closures)
        if observed_slot_ids != expected_slot_ids:
            raise EvidenceError("E_STAGE1_TERMINAL", "closure order does not match inventory")
        observed_hashes = [str(item["artifact_sha256"]) for item in closures]
        if observed_hashes != list(row["closure_artifact_sha256s"]):
            raise EvidenceError("E_STAGE1_TERMINAL", "closure hashes do not match written objects")
        closure_count += len(closures)
    if ordinals != list(STAGE1_ORDINALS):
        raise EvidenceError("E_STAGE1_TERMINAL", "ordinals must be exactly 9-22 in order")
    if 8 in ordinals:
        raise EvidenceError("E_STAGE1_TERMINAL", "ordinal 8 is forbidden")
    if closure_count != STAGE1_CLOSURE_COUNT:
        raise EvidenceError("E_STAGE1_TERMINAL", "closure count must be 140")
    body = {key: value for key, value in payload.items() if key != "artifact_sha256"}
    if payload["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_STAGE1_IDENTITY", "terminal self-hash mismatch")
    return {
        "valid": True,
        "terminal_status": STAGE1_TERMINAL_STATUS,
        "subject_count": STAGE1_SUBJECT_COUNT,
        "closure_count": STAGE1_CLOSURE_COUNT,
        "artifact_sha256": payload["artifact_sha256"],
    }

def stage1_subject_directory(root: Path, ordinal: int, controlled_subject_id: str) -> Path:
    return Path(root) / "subjects" / f"{ordinal:02d}-{controlled_subject_id}"


def write_stage1_closure(
    path: Path,
    closure: Mapping[str, Any],
    write_log: list[Path],
) -> None:
    write_canonical_json(path, closure, exclusive=True)
    write_log.append(Path(path))


def publish_stage1_official(*, staging_root: Path, output_root: Path) -> None:
    if Path(output_root).exists():
        raise EvidenceError("E_STAGE1_FAIL_CLOSED", f"official path already exists: {output_root}")
    os.replace(Path(staging_root), Path(output_root))


def _controller_source_sha256(repo_root: Path) -> str:
    candidate = Path(repo_root) / STAGE1_CONTROLLER_RELPATH
    if candidate.is_file():
        return file_sha256(candidate)
    return file_sha256(STAGE1_CONTROLLER_RELPATH)


def _inventory_from_subject_rows(subject_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    slots: list[dict[str, Any]] = []
    families = [family for family in INVENTORY_FAMILY_ORDER for _slot in (0, 1)]
    ordinals = [0, 1] * 5
    for produced in subject_rows:
        closures = list(produced["closures"])
        for closure, family, slot_ordinal in zip(closures, families, ordinals, strict=True):
            slots.append({
                "controlled_subject_id": produced["controlled_subject_id"],
                "permitted_construction_mechanism": "CE",
                "semantic_contract_family": family,
                "slot_id": closure["slot_id"],
                "slot_ordinal": slot_ordinal,
            })
    return {"slots": slots}


def run_stage1_census(
    *,
    repo_root: Path,
    output_root: Path,
    staging_root: Path,
    subject_processor: Callable[..., Mapping[str, Any]],
) -> dict[str, Any]:
    official = Path(output_root)
    staging = Path(staging_root)
    if official.exists() or staging.exists():
        raise EvidenceError("E_STAGE1_FAIL_CLOSED", "official or staging path already exists")
    successors = load_frozen_successors()
    ordinals = [item.successor_ordinal for item in successors]
    if 8 in ordinals:
        raise EvidenceError("E_STAGE1_IDENTITY", "ordinal 8 is excluded from Stage I")
    if ordinals != list(STAGE1_ORDINALS):
        raise EvidenceError("E_STAGE1_IDENTITY", "frozen successors must be ordinals 9-22")
    staging.mkdir(parents=True)
    write_log: list[Path] = []
    subject_rows: list[dict[str, Any]] = []
    all_closures: list[list[dict[str, Any]]] = []
    try:
        for successor in successors:
            if successor.successor_ordinal == 8:
                raise EvidenceError("E_STAGE1_IDENTITY", "ordinal 8 is excluded from Stage I")
            produced = dict(subject_processor(successor, repo_root=Path(repo_root)))
            closures = [dict(item) for item in produced["closures"]]
            if len(closures) != STAGE1_CLOSURES_PER_SUBJECT:
                raise EvidenceError("E_STAGE1_TERMINAL", "each subject must have 10 closures")
            produced["closures"] = closures
            directory = stage1_subject_directory(
                staging,
                int(successor.successor_ordinal),
                str(successor.controlled_subject_id),
            )
            directory.mkdir(parents=True)
            for closure in closures:
                target = directory / f"{closure['slot_id']}.json"
                write_stage1_closure(target, closure, write_log)
            subject_rows.append(produced)
            all_closures.append(closures)
        if len(subject_rows) != STAGE1_SUBJECT_COUNT:
            raise EvidenceError("E_STAGE1_TERMINAL", "subject count must be 14")
        inventory = _inventory_from_subject_rows(subject_rows)
        controller_sha = _controller_source_sha256(Path(repo_root))
        terminal = build_stage1_terminal(
            design_commit=STAGE1_DESIGN_COMMIT,
            design_file_sha256=STAGE1_DESIGN_FILE_SHA256,
            controller_source_sha256=controller_sha,
            applicability_authority_artifact_sha256=STAGE1_APPLICABILITY_AUTHORITY_ARTIFACT_SHA256,
            slot_inventory_artifact_sha256=STAGE1_SLOT_INVENTORY_ARTIFACT_SHA256,
            project_cluster_authority_artifact_sha256=STAGE1_PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256,
            subjects=subject_rows,
        )
        validate_stage1_terminal(
            terminal,
            expected_design_commit=STAGE1_DESIGN_COMMIT,
            expected_design_file_sha256=STAGE1_DESIGN_FILE_SHA256,
            expected_controller_source_sha256=controller_sha,
            expected_applicability_authority_artifact_sha256=STAGE1_APPLICABILITY_AUTHORITY_ARTIFACT_SHA256,
            expected_slot_inventory_artifact_sha256=STAGE1_SLOT_INVENTORY_ARTIFACT_SHA256,
            expected_project_cluster_authority_artifact_sha256=STAGE1_PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256,
            subject_closures=all_closures,
            inventory=inventory,
        )
        terminal_path = staging / STAGE1_TERMINAL_FILENAME
        write_canonical_json(terminal_path, terminal, exclusive=True)
        write_log.append(terminal_path)
        if write_log[-1].name != STAGE1_TERMINAL_FILENAME:
            raise EvidenceError("E_STAGE1_TERMINAL", "terminal must be the last written file")
        if len(write_log) != STAGE1_CLOSURE_COUNT + 1:
            raise EvidenceError("E_STAGE1_TERMINAL", "staging must contain 140 closures and 1 terminal")
        publish_stage1_official(staging_root=staging, output_root=official)
    except Exception:
        if official.exists():
            raise EvidenceError("E_STAGE1_FAIL_CLOSED", "official namespace written after failure")
        raise
    if staging.exists():
        raise EvidenceError("E_STAGE1_FAIL_CLOSED", "staging sibling remained after publication")
    return {
        "status": STAGE1_TERMINAL_STATUS,
        "official_root": str(official),
        "subject_count": STAGE1_SUBJECT_COUNT,
        "closure_count": STAGE1_CLOSURE_COUNT,
        "write_order": [str(path) for path in write_log],
        "terminal": terminal,
    }


def process_stage1_subject(successor: Any, *, repo_root: Path) -> dict[str, Any]:
    import json

    from p3_v3.applicability_predicates import (
        close_slot_with_authority,
        load_applicability_authority,
    )
    from p3_v3.multiproject_production_processor import (
        _pbf_path,
        _subject_inventory_rows,
        canonicalize_production_sites,
        freeze_subject_identity,
        inspect_regular_identity_file,
        recover_production_source,
    )

    if successor.successor_ordinal == 8:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal 8 is excluded from Stage I")
    root = Path(repo_root)
    binding = freeze_subject_identity(successor, root)
    recover_production_source(binding, root)
    authority = load_applicability_authority(
        manifest_path=root / STAGE1_AUTHORITY_RELPATH,
        registry_path=root / STAGE1_PREDICATE_REGISTRY_RELPATH,
        inventory_path=root / STAGE1_INVENTORY_RELPATH,
        slot_implementation_path=root / STAGE1_SLOT_IMPLEMENTATION_RELPATH,
        predicate_implementation_path=root / STAGE1_PREDICATE_IMPLEMENTATION_RELPATH,
    )
    rows = sort_stage1_inventory_rows(
        _subject_inventory_rows(authority["inventory"], successor.controlled_subject_id)
    )
    pbf_path = _pbf_path(root, successor.neutral_snapshot_id)
    inspect_regular_identity_file(pbf_path)
    frame = json.loads(pbf_path.read_text(encoding="utf-8"))
    canonical_sites = canonicalize_production_sites(
        successor.controlled_subject_id,
        frame["sites"],
        frozen_controlled_subject_id=successor.controlled_subject_id,
    )
    closures = [
        close_slot_with_authority(authority, row, canonical_sites, frame) for row in rows
    ]
    return {
        "successor_ordinal": successor.successor_ordinal,
        "neutral_snapshot_id": successor.neutral_snapshot_id,
        "controlled_subject_source_id": successor.controlled_subject_source_id,
        "controlled_subject_id": successor.controlled_subject_id,
        "project_cluster_key": binding.project_cluster_key,
        "closures": closures,
    }
