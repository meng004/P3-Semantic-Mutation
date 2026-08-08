from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.bridge_and_frames import (
    build_subject_frames,
    select_construct_subjects,
    select_first_applicable_site,
    validate_bridge_document,
    verify_pinned_bridge,
    verify_reveal,
)


def _bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode() + b"\n"


def _sha(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def _run(root: Path, *argv: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *argv], capture_output=True, check=True, text=True
    )
    return result.stdout.strip()


@dataclass
class SyntheticRelease:
    root: Path
    lock: dict
    bridge: dict
    fixed_oid: str
    nonce_hex: str


@pytest.fixture
def synthetic_release(tmp_path) -> SyntheticRelease:
    root = tmp_path / "p12"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "P12 Fixture")
    _run(root, "config", "user.email", "p12@example.invalid")
    contract_path = "release/p3-contract.json"
    bridge_path = "release/p3-bridge.json"
    (root / "release").mkdir()
    contract = {"schema_version": "p12-p3-contract-v2", "claim": "fixture"}
    (root / contract_path).write_bytes(_bytes(contract))
    contract_blob = _run(root, "hash-object", contract_path)

    package_root = "1" * 64
    source_sha = "2" * 64
    archive_sha = "3" * 64
    build_sha = "4" * 64
    fixed_oid = "5" * 40
    nonce = bytes.fromhex("6" * 64)
    commitment = hashlib.sha256(
        b"P3-FIXED-TREE-v1"
        + package_root.encode()
        + fixed_oid.encode()
        + nonce
    ).hexdigest()
    neutral = _sha(
        {
            "p12_package_root_sha256": package_root,
            "normalized_source_tree_sha256": source_sha,
            "source_archive_sha256": archive_sha,
            "domain": "P3-NEUTRAL-SNAPSHOT-v1",
        }
    )
    records = [
        {
            "neutral_snapshot_id": neutral,
            "fixed_tree_commitment": commitment,
            "normalized_source_tree_sha256": source_sha,
            "source_archive_sha256": archive_sha,
            "build_descriptor_sha256": build_sha,
            "eligibility_reason": "synthetic complete record",
            "eligible_for_construct": True,
            "eligible_for_criterion": True,
        }
    ]
    body = {
        "schema_version": "p3-p12-bridge-v1",
        "p12_release_id": "p12-synthetic-v2",
        "p12_repository_identity": "example/P12-Defect4MR",
        "p12_contract_path": contract_path,
        "p12_contract_blob_sha": contract_blob,
        "p12_package_root_sha256": package_root,
        "p12_contract_sha256": hashlib.sha256(_bytes(contract)).hexdigest(),
        "eligible_inventory_root_sha256": _sha(records),
        "eligible_item_count": 1,
        "records": records,
        "trust_mode": "PINNED_GIT_RELEASE",
    }
    bridge = {**body, "artifact_sha256": _sha(body)}
    (root / bridge_path).write_bytes(_bytes(bridge))
    _run(root, "add", "release")
    _run(root, "commit", "-m", "release fixture")
    release_commit = _run(root, "rev-parse", "HEAD")
    bridge_blob = _run(root, "rev-parse", f"{release_commit}:{bridge_path}")
    contract_blob = _run(root, "rev-parse", f"{release_commit}:{contract_path}")
    lock = {
        "repository_identity": "example/P12-Defect4MR",
        "release_commit_sha": release_commit,
        "bridge_path": bridge_path,
        "bridge_blob_sha": bridge_blob,
        "contract_path": contract_path,
        "contract_blob_sha": contract_blob,
        "package_root_sha256": package_root,
    }
    return SyntheticRelease(root, lock, bridge, fixed_oid, nonce.hex())


def test_bridge_is_read_from_exact_pinned_git_release(synthetic_release):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    assert verified["trust_mode"] == "PINNED_GIT_RELEASE"
    assert verified["eligible_item_count"] == 1


def test_bridge_rejects_wrong_external_blob_pin(synthetic_release):
    lock = {**synthetic_release.lock, "bridge_blob_sha": "0" * 40}
    with pytest.raises(EvidenceError, match="E_PINNED_BRIDGE_BLOB"):
        verify_pinned_bridge(synthetic_release.root, lock)


def test_visible_bridge_rejects_fixed_tree_oid_even_when_rehashed(synthetic_release):
    bridge = json.loads(json.dumps(synthetic_release.bridge))
    bridge["records"][0]["fixed_git_tree_oid"] = synthetic_release.fixed_oid
    body = {key: value for key, value in bridge.items() if key != "artifact_sha256"}
    bridge["artifact_sha256"] = _sha(body)
    with pytest.raises(EvidenceError, match="E_BRIDGE_RECORD_KEYS"):
        validate_bridge_document(bridge, synthetic_release.lock)


def _features(neutral_id: str):
    return [
        {
            "neutral_snapshot_id": neutral_id,
            "public_workload_set_sha256": "7" * 64,
            "scale_class": "S",
            "primary_technique": "ARRAY_NUMERICAL",
            "technique_vector": ["ARRAY_NUMERICAL", "SCALAR_CONTROL"],
            "sites": [
                {
                    "path": "src/a.py",
                    "symbol": "solve",
                    "start_line": 10,
                    "start_col": 4,
                    "end_line": 10,
                    "end_col": 20,
                }
            ],
        }
    ]


def test_subject_frames_are_input_order_invariant_and_use_subject_id(synthetic_release):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    features = _features(verified["records"][0]["neutral_snapshot_id"])
    first = build_subject_frames(verified, features)
    second = build_subject_frames(
        {**verified, "records": list(reversed(verified["records"]))},
        list(reversed(features)),
    )
    assert first == second
    subject = first["subjects"][0]
    assert len(subject["controlled_subject_id"]) == 64
    assert len(subject["sites"][0]["site_id"]) == 64
    assert first["c_criterion"] == [subject["controlled_subject_id"]]
    assert len(first["empty_construct_cells"]) == 20
    assert {
        "scale_class": "S",
        "primary_technique": "SCALAR_CONTROL",
        "status": "EMPTY_FRAME",
    } in first["empty_construct_cells"]


def test_subject_frame_rejects_missing_feature_record(synthetic_release):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    with pytest.raises(EvidenceError, match="E_FEATURE_COVERAGE"):
        build_subject_frames(verified, [])


def _subject(subject_id: str, technique: str) -> dict:
    return {
        "controlled_subject_id": subject_id,
        "scale_class": "S",
        "primary_technique": technique,
        "technique_vector": [technique],
    }


def test_construct_selection_continues_strict_round_robin_by_cell():
    subjects = [
        _subject("1" * 64, "ARRAY_NUMERICAL"),
        _subject("2" * 64, "ARRAY_NUMERICAL"),
        _subject("3" * 64, "SCALAR_CONTROL"),
        _subject("4" * 64, "SCALAR_CONTROL"),
    ]
    selected = select_construct_subjects(
        subjects, {item["controlled_subject_id"] for item in subjects}, limit=4
    )
    cell_by_id = {
        item["controlled_subject_id"]: item["primary_technique"] for item in subjects
    }
    assert [cell_by_id[item] for item in selected] == [
        "ARRAY_NUMERICAL",
        "SCALAR_CONTROL",
        "ARRAY_NUMERICAL",
        "SCALAR_CONTROL",
    ]


def test_slot_selects_first_applicable_canonical_site_or_none():
    sites = [
        {
            "path": "a.py",
            "symbol": "f",
            "start_line": 1,
            "start_col": 0,
            "end_line": 1,
            "end_col": 1,
            "site_id": "1" * 64,
        },
        {
            "path": "b.py",
            "symbol": "g",
            "start_line": 2,
            "start_col": 0,
            "end_line": 2,
            "end_col": 1,
            "site_id": "2" * 64,
        },
    ]
    assert select_first_applicable_site(sites, lambda site: site["symbol"] in {"f", "g"}) == "1" * 64
    assert select_first_applicable_site(sites, lambda _site: False) is None


def test_reveal_binds_nonce_oid_commitment_and_normalized_source(synthetic_release):
    record = synthetic_release.bridge["records"][0]
    reveal = {
        "neutral_snapshot_id": record["neutral_snapshot_id"],
        "fixed_git_tree_oid": synthetic_release.fixed_oid,
        "reveal_nonce": synthetic_release.nonce_hex,
        "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
    }
    verify_reveal(
        record,
        reveal,
        synthetic_release.bridge["p12_package_root_sha256"],
        observed_tree_oid=synthetic_release.fixed_oid,
        observed_normalized_sha256=record["normalized_source_tree_sha256"],
    )
    bad = {**reveal, "reveal_nonce": "0" * 64}
    with pytest.raises(EvidenceError, match="E_REVEAL_COMMITMENT"):
        verify_reveal(
            record,
            bad,
            synthetic_release.bridge["p12_package_root_sha256"],
            observed_tree_oid=synthetic_release.fixed_oid,
            observed_normalized_sha256=record["normalized_source_tree_sha256"],
        )
