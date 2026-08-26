from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest

from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    write_canonical_json,
)

REQUIRED_SOURCE_PREPARATION_TESTS = [
    "test_authorization_absent_writes_no_output",
    "test_authorization_wrong_bytes_writes_no_output",
    "test_implementation_verdict_hash_mismatch_fails_closed",
    "test_machine_plan_hash_mismatch_fails_closed",
    "test_capability_verdict_absent_writes_no_output",
    "test_launch_authority_absent_writes_no_output",
    "test_runtime_production_bytes_drift_writes_no_output",
    "test_authority_snapshot_binds_validated_bytes_on_replacement_race",
    "test_capability_verdict_requires_reviewed_commit",
    "test_capability_verdict_binds_implementation_files",
    "test_authority_dependency_graph_has_exactly_one_topological_order",
    "test_reconciliation_classifier_is_total_and_exclusive",
    "test_streamed_chunk_exceeds_member_limit_before_write",
    "test_streamed_chunks_exceed_total_limit",
    "test_overlimit_chunk_is_not_written",
    "test_streamed_chunk_length_rejects_bool_and_negative",
    "test_member_count_checked_before_content",
    "test_plan_verdict_rejects_noncanonical",
    "test_plan_verdict_rejects_extra_key",
    "test_plan_verdict_rejects_wrong_type",
    "test_plan_verdict_rejects_bad_sha",
    "test_capability_verdict_rejects_noncanonical",
    "test_capability_verdict_rejects_extra_key",
    "test_capability_verdict_rejects_wrong_type",
    "test_capability_verdict_rejects_bad_sha",
    "test_launch_verdict_rejects_noncanonical",
    "test_launch_verdict_rejects_extra_key",
    "test_launch_verdict_rejects_wrong_type",
    "test_launch_verdict_rejects_bad_sha",
    "test_launch_authority_rejects_noncanonical",
    "test_launch_authority_rejects_extra_key",
    "test_launch_authority_rejects_wrong_type",
    "test_launch_authority_rejects_bad_sha",
    "test_archive_snapshot_rejects_symlink",
    "test_archive_snapshot_rejects_non_regular_file",
    "test_archive_snapshot_hashes_same_fd_bytes",
    "test_archive_snapshot_rejects_identity_change",
    "test_archive_format_uses_bytes_not_suffix",
    "test_zip_rejects_parent_traversal",
    "test_zip_rejects_symlink",
    "test_zip_rejects_encrypted_member",
    "test_tar_rejects_parent_traversal",
    "test_tar_rejects_symlink",
    "test_tar_rejects_hardlink",
    "test_extractor_rejects_casefold_collision",
    "test_extractor_rejects_duplicate_normalized_path",
    "test_extractor_rejects_member_limit",
    "test_extractor_rejects_total_bytes_limit",
    "test_streamed_member_bytes_cannot_exceed_declared_policy_limit",
    "test_single_top_level_selection_is_order_invariant",
    "test_single_top_level_file_is_not_stripped",
    "test_materialized_tree_uses_phase1_canonical_hash",
    "test_phase1_tree_hash_function_is_called_by_production_seam",
    "test_wrong_materialized_tree_writes_failure_result",
    "test_source_manifest_exact_keys",
    "test_source_manifest_predecessors_are_exact",
    "test_source_manifest_cannot_validate_as_pilot_plan",
    "test_pass_result_binds_source_manifest",
    "test_outputs_are_exclusive",
    "test_crash_after_manifest_publication",
    "test_crash_after_materialize_root_rename",
    "test_manifest_only_recovery",
    "test_manifest_and_root_recovery",
    "test_tampered_manifest_refuses_recovery",
    "test_orphan_root_without_manifest_refuses_recovery",
    "test_result_is_always_the_final_pass_commit_point",
    "test_tree_mismatch_leaves_materialize_root_and_manifest_absent",
    "test_validate_source_cli_has_no_authority_overrides",
    "test_capability_implementation_creates_no_production_artifact",
]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _patch_outputs(monkeypatch, module, tmp_path: Path) -> None:
    monkeypatch.setattr(module, "SOURCE_MANIFEST_PATH", tmp_path / "source-manifest.json")
    monkeypatch.setattr(
        module, "SOURCE_PREPARATION_RESULT_PATH", tmp_path / "source-preparation-result.json"
    )


def _write_zip(path: Path, members: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return path


def _write_tar(path: Path, members: dict[str, bytes]) -> Path:
    with tarfile.open(path, "w") as archive:
        for name, payload in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
    return path


def test_required_names_are_defined():
    defined = {name for name, value in globals().items() if callable(value)}
    missing = set(REQUIRED_SOURCE_PREPARATION_TESTS) - defined
    assert missing == set()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _install_capability_verdict(monkeypatch, tmp_path: Path) -> Path:
    from p3_v3 import pilot_source

    plan_sha256 = _file_sha256(pilot_source.SOURCE_PREPARATION_PLAN_PATH)
    plan_verdict_sha256 = _file_sha256(
        pilot_source.CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH
    )
    verdict = {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": plan_sha256,
        "reviewed_plan_verdict_sha256": plan_verdict_sha256,
        "reviewed_commit": "1cdf2a1d5b4f43c5565f2b773103a971784468e1",
        "reviewed_pilot_source_path": "src/p3_v3/pilot_source.py",
        "reviewed_pilot_source_sha256": _file_sha256(Path("src/p3_v3/pilot_source.py")),
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": _file_sha256(Path("scripts/p3_v3/pilot.py")),
        "reviewed_test_pilot_source_path": "tests/p3_v3/test_pilot_source.py",
        "reviewed_test_pilot_source_sha256": _file_sha256(
            Path("tests/p3_v3/test_pilot_source.py")
        ),
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": _file_sha256(Path("tests/p3_v3/test_pilot.py")),
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }
    path = tmp_path / "capability-verdict.md"
    write_canonical_json(path, verdict, exclusive=True)
    monkeypatch.setattr(
        pilot_source, "CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH", path
    )
    return path


def _install_launch_predecessors(monkeypatch, tmp_path: Path) -> None:
    from p3_v3 import pilot_source

    _install_capability_verdict(monkeypatch, tmp_path)
    auth = tmp_path / "user-auth-preparation.txt"
    auth.write_bytes(pilot_source.AUTHORIZATION_A_BYTES)
    monkeypatch.setattr(pilot_source, "AUTHORIZATION_A_PATH", auth)
    packet = tmp_path / "launch-packet.md"
    packet.write_bytes(b"synthetic launch packet\n")
    monkeypatch.setattr(pilot_source, "SOURCE_PREPARATION_LAUNCH_PACKET_PATH", packet)
    launch_verdict = {
        "reviewed_packet_path": packet.as_posix(),
        "reviewed_packet_sha256": _file_sha256(packet),
        "plan_verdict_sha256": _file_sha256(
            Path("docs/review_20260817/boost_math_pilot_source_preparation_sol_high_review.md")
        ),
        "capability_verdict_sha256": _file_sha256(
            tmp_path / "capability-verdict.md"
        ),
        "authorization_a_sha256": pilot_source.AUTHORIZATION_A_SHA256,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_LAUNCH_FROZEN",
        "claims": "blocked",
    }
    verdict_path = tmp_path / "launch-verdict.md"
    write_canonical_json(verdict_path, launch_verdict, exclusive=True)
    monkeypatch.setattr(
        pilot_source, "SOURCE_PREPARATION_LAUNCH_VERDICT_PATH", verdict_path
    )


def _install_full_authority_chain(monkeypatch, tmp_path: Path) -> dict:
    from p3_v3 import pilot_source

    _install_launch_predecessors(monkeypatch, tmp_path)
    _patch_outputs(monkeypatch, pilot_source, tmp_path)
    plan_sha256 = _file_sha256(pilot_source.SOURCE_PREPARATION_PLAN_PATH)
    plan_verdict_sha256 = _file_sha256(
        pilot_source.CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH
    )
    capability_sha256 = _file_sha256(
        pilot_source.CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH
    )
    packet_sha256 = _file_sha256(pilot_source.SOURCE_PREPARATION_LAUNCH_PACKET_PATH)
    launch_verdict_sha256 = _file_sha256(
        pilot_source.SOURCE_PREPARATION_LAUNCH_VERDICT_PATH
    )
    body = {
        "schema_version": "p3-pilot-source-preparation-launch-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "source_preparation_plan_path": (
            pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix()
        ),
        "source_preparation_plan_sha256": plan_sha256,
        "source_preparation_plan_verdict_path": (
            pilot_source.CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH.as_posix()
        ),
        "source_preparation_plan_verdict_sha256": plan_verdict_sha256,
        "capability_implementation_verdict_path": (
            pilot_source.CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH.as_posix()
        ),
        "capability_implementation_verdict_sha256": capability_sha256,
        "production_launch_packet_path": (
            pilot_source.SOURCE_PREPARATION_LAUNCH_PACKET_PATH.as_posix()
        ),
        "production_launch_packet_sha256": packet_sha256,
        "launch_sol_high_verdict_path": (
            pilot_source.SOURCE_PREPARATION_LAUNCH_VERDICT_PATH.as_posix()
        ),
        "launch_sol_high_verdict_sha256": launch_verdict_sha256,
        "authorization_a_sha256": pilot_source.AUTHORIZATION_A_SHA256,
        "claims": "blocked",
    }
    body["artifact_sha256"] = canonical_sha256(body)
    launch_path = tmp_path / "source-preparation-launch.json"
    write_canonical_json(launch_path, body, exclusive=True)
    monkeypatch.setattr(pilot_source, "SOURCE_PREPARATION_LAUNCH_PATH", launch_path)
    predecessors = pilot_source.gate_chain_predecessor_sha256(
        plan_sha256,
        plan_verdict_sha256,
        capability_sha256,
        _file_sha256(launch_path),
        pilot_source.AUTHORIZATION_A_SHA256,
    )
    return {"predecessors": predecessors}


def _force_frozen_tree_hash(monkeypatch) -> None:
    from p3_v3 import pilot_source

    monkeypatch.setattr(
        pilot_source,
        "canonical_source_tree_sha256",
        lambda snapshot: pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
    )


def _canonical_manifest(
    *,
    predecessors: list[str],
    archive_sha256: str,
    archive_bytes: int,
    archive_format: str,
    file_count: int,
    total_bytes: int,
) -> dict:
    from p3_v3 import pilot_source

    value = {
        "schema_version": "p3-pilot-source-manifest-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "p12_item_id": pilot_source.P12_ITEM_ID,
        "neutral_snapshot_id": pilot_source.NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": (
            pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256
        ),
        "controlled_subject_id": pilot_source.CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": pilot_source.CONTROLLED_SUBJECT_SOURCE_ID,
        "predecessor_sha256": list(predecessors),
        "archive_sha256": archive_sha256,
        "archive_bytes": archive_bytes,
        "archive_format": archive_format,
        "build_descriptor_sha256": pilot_source.BUILD_DESCRIPTOR_SHA256,
        "authorization_a_sha256": pilot_source.AUTHORIZATION_A_SHA256,
        "extractor_policy_sha256": pilot_source.EXTRACTOR_POLICY_SHA256,
        "materialized_file_count": file_count,
        "materialized_total_bytes": total_bytes,
        "artifact_sha256": "",
    }
    value["artifact_sha256"] = canonical_sha256(
        {key: value[key] for key in value if key != "artifact_sha256"}
    )
    return value


def _canonical_result(
    *,
    predecessors: list[str],
    terminal_status: str,
    failure_reason: str | None,
    source_manifest_sha256: str | None,
    archive_sha256: str | None,
    archive_bytes: int | None,
    materialized_tree_sha256: str | None,
) -> dict:
    from p3_v3 import pilot_source

    value = {
        "schema_version": "p3-pilot-source-preparation-result-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "p12_item_id": pilot_source.P12_ITEM_ID,
        "neutral_snapshot_id": pilot_source.NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": (
            pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256
        ),
        "controlled_subject_id": pilot_source.CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": pilot_source.CONTROLLED_SUBJECT_SOURCE_ID,
        "predecessor_sha256": list(predecessors),
        "terminal_status": terminal_status,
        "failure_reason": failure_reason,
        "source_manifest_sha256": source_manifest_sha256,
        "archive_sha256": archive_sha256,
        "archive_bytes": archive_bytes,
        "materialized_tree_sha256": materialized_tree_sha256,
        "artifact_sha256": "",
    }
    value["artifact_sha256"] = canonical_sha256(
        {key: value[key] for key in value if key != "artifact_sha256"}
    )
    return value


def _synthetic_tree_metrics(tmp_path: Path, members: dict[str, bytes]) -> tuple:
    from p3_v3 import pilot_source

    archive = _write_zip(tmp_path / "synthetic-source.zip", members)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    probe = tmp_path / "probe-tree"
    pilot_source.extract_archive_to_staging(snapshot, probe)
    tree = pilot_source.capture_materialized_tree(probe)
    return (
        archive,
        snapshot,
        tree,
        len(tree.entries),
        sum(len(entry.content) for entry in tree.entries),
    )


def test_authorization_absent_writes_no_output(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _install_capability_verdict(monkeypatch, tmp_path)
    monkeypatch.setattr(
        pilot_source,
        "AUTHORIZATION_A_PATH",
        tmp_path / "user-auth-preparation.txt",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(EvidenceError, match="E_PILOT_PREPARATION_AUTH_ABSENT"):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()
    assert not (tmp_path / "materialize").exists()


def test_authorization_wrong_bytes_writes_no_output(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _install_capability_verdict(monkeypatch, tmp_path)
    auth = tmp_path / "user-auth-preparation.txt"
    auth.write_bytes(b"WRONG_AUTHORIZATION\n")
    monkeypatch.setattr(pilot_source, "AUTHORIZATION_A_PATH", auth)
    _patch_outputs(monkeypatch, pilot_source, tmp_path)
    with pytest.raises(EvidenceError, match="E_PILOT_PREPARATION_AUTH"):
        pilot_source.run_validate_source(tmp_path / "missing.zip", tmp_path / "materialize")
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_implementation_verdict_hash_mismatch_fails_closed(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    verdict = {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "reviewed_plan_verdict_sha256": "1" * 64,
        "reviewed_commit": "a" * 40,
        "reviewed_pilot_source_path": "src/p3_v3/pilot_source.py",
        "reviewed_pilot_source_sha256": "2" * 64,
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": "3" * 64,
        "reviewed_test_pilot_source_path": "tests/p3_v3/test_pilot_source.py",
        "reviewed_test_pilot_source_sha256": "4" * 64,
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": "5" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
    ):
        pilot_source.validate_source_preparation_capability_verdict(
            verdict, "6" * 64, "7" * 64
        )


def test_machine_plan_hash_mismatch_fails_closed():
    from p3_v3 import pilot_source

    verdict = {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_PLAN_FROZEN",
        "claims": "blocked",
    }
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT"):
        pilot_source.validate_source_preparation_plan_verdict(verdict, "1" * 64)


def test_capability_verdict_absent_writes_no_output(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    monkeypatch.setattr(
        pilot_source,
        "CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH",
        tmp_path / "missing-capability-verdict.md",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT_ABSENT"
    ):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_launch_authority_absent_writes_no_output(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _install_launch_predecessors(monkeypatch, tmp_path)
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_LAUNCH_PATH",
        tmp_path / "missing-launch.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH_ABSENT"
    ):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_runtime_production_bytes_drift_writes_no_output(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _install_capability_verdict(monkeypatch, tmp_path)
    monkeypatch.setattr(
        pilot_source,
        "REVIEWED_PILOT_SOURCE_PATH",
        tmp_path / "drifted-pilot-source.py",
    )
    (tmp_path / "drifted-pilot-source.py").write_text("drifted\n", encoding="utf-8")
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
    ):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_authority_snapshot_binds_validated_bytes_on_replacement_race(tmp_path):
    from p3_v3 import pilot_source

    path = tmp_path / "authority.json"
    first = {"schema_version": "race-v1", "value": "before"}
    path.write_bytes(canonical_json_bytes(first))
    raw, digest = pilot_source.read_authority_snapshot(path, "race")
    path.write_bytes(canonical_json_bytes({"schema_version": "race-v1", "value": "after"}))
    assert raw == canonical_json_bytes(first)
    assert digest == _sha256_bytes(raw)
    assert digest != _sha256_bytes(path.read_bytes())


def test_capability_verdict_requires_reviewed_commit():
    from p3_v3 import pilot_source

    verdict = {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "reviewed_plan_verdict_sha256": "1" * 64,
        "reviewed_commit": "NOT-A-COMMIT",
        "reviewed_pilot_source_path": "src/p3_v3/pilot_source.py",
        "reviewed_pilot_source_sha256": "2" * 64,
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": "3" * 64,
        "reviewed_test_pilot_source_path": "tests/p3_v3/test_pilot_source.py",
        "reviewed_test_pilot_source_sha256": "4" * 64,
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": "5" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
    ):
        pilot_source.validate_source_preparation_capability_verdict(
            verdict, "0" * 64, "1" * 64
        )


def test_capability_verdict_binds_implementation_files():
    from p3_v3 import pilot_source

    verdict = {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "reviewed_plan_verdict_sha256": "1" * 64,
        "reviewed_commit": "a" * 40,
        "reviewed_pilot_source_path": "src/wrong.py",
        "reviewed_pilot_source_sha256": "2" * 64,
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": "3" * 64,
        "reviewed_test_pilot_source_path": "tests/p3_v3/test_pilot_source.py",
        "reviewed_test_pilot_source_sha256": "4" * 64,
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": "5" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
    ):
        pilot_source.validate_source_preparation_capability_verdict(
            verdict, "0" * 64, "1" * 64
        )


def test_authority_dependency_graph_has_exactly_one_topological_order():
    from p3_v3.pilot_source import (
        AUTHORITY_DEPENDENCY_EDGES,
        UNIQUE_AUTHORITY_ORDER,
        count_topological_authority_orders,
        require_unique_topological_authority_order,
    )

    order = require_unique_topological_authority_order(AUTHORITY_DEPENDENCY_EDGES)
    assert count_topological_authority_orders(AUTHORITY_DEPENDENCY_EDGES) == 1
    assert order == UNIQUE_AUTHORITY_ORDER
    missing_capability_to_auth = [
        edge
        for edge in AUTHORITY_DEPENDENCY_EDGES
        if edge != ("capability_verdict", "authorization_a")
    ]
    with pytest.raises(ValueError, match="non-unique topological order"):
        require_unique_topological_authority_order(missing_capability_to_auth)
    assert count_topological_authority_orders(missing_capability_to_auth) != 1
    missing_auth_to_packet = [
        edge
        for edge in AUTHORITY_DEPENDENCY_EDGES
        if edge != ("authorization_a", "launch_packet")
    ]
    with pytest.raises(ValueError, match="non-unique topological order"):
        require_unique_topological_authority_order(missing_auth_to_packet)
    assert count_topological_authority_orders(missing_auth_to_packet) != 1


def test_reconciliation_classifier_is_total_and_exclusive():
    from p3_v3.pilot_source import (
        RECONCILIATION_STATES,
        classify_reconciliation,
        enumerate_reconciliation_cases,
    )

    cases = enumerate_reconciliation_cases()
    observed = {case[-1] for case in cases}
    assert observed == set(RECONCILIATION_STATES)
    assert len(cases) == 31
    assert len(RECONCILIATION_STATES) == 12
    for case in cases:
        again = classify_reconciliation(
            manifest_present=case[0],
            result_present=case[1],
            root_present=case[2],
            manifest_valid=case[3],
            result_valid=case[4],
            result_status=case[5],
            closed_pair_consistent=case[6],
        )
        assert again == case[-1]


def test_streamed_chunk_exceeds_member_limit_before_write():
    from p3_v3.pilot_source import StreamedLimitCounter

    written: list[bytes] = []
    counter = StreamedLimitCounter(
        {"max_member_count": 2, "max_member_bytes": 4, "max_total_uncompressed_bytes": 100}
    )
    counter.begin_member()
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(5)
        written.append(b"12345")
    assert written == []


def test_streamed_chunks_exceed_total_limit():
    from p3_v3.pilot_source import StreamedLimitCounter

    counter = StreamedLimitCounter(
        {"max_member_count": 3, "max_member_bytes": 100, "max_total_uncompressed_bytes": 10}
    )
    counter.begin_member()
    counter.consume_chunk(6)
    counter.end_member()
    counter.begin_member()
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(5)


def test_overlimit_chunk_is_not_written():
    from p3_v3.pilot_source import StreamedLimitCounter

    staging: list[bytes] = []
    counter = StreamedLimitCounter(
        {"max_member_count": 1, "max_member_bytes": 3, "max_total_uncompressed_bytes": 3}
    )
    counter.begin_member()
    counter.consume_chunk(2)
    staging.append(b"ab")
    chunk = b"cd"
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(len(chunk))
        staging.append(chunk)
    assert staging == [b"ab"]


def test_streamed_chunk_length_rejects_bool_and_negative():
    from p3_v3.pilot_source import EXTRACTOR_POLICY_V1, StreamedLimitCounter

    counter = StreamedLimitCounter(EXTRACTOR_POLICY_V1)
    counter.begin_member()
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(True)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(-1)


def test_member_count_checked_before_content():
    from p3_v3.pilot_source import EXTRACTOR_POLICY_V1, StreamedLimitCounter

    policy = dict(EXTRACTOR_POLICY_V1)
    policy["max_member_count"] = 1
    counter = StreamedLimitCounter(policy)
    counter.begin_member()
    counter.end_member()
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.begin_member()


def _plan_verdict_valid():
    from p3_v3 import pilot_source

    return {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_PLAN_FROZEN",
        "claims": "blocked",
    }


def test_plan_verdict_rejects_noncanonical():
    from p3_v3 import pilot_source

    raw = b'{"authorized_state":"PILOT_SOURCE_PREPARATION_PLAN_FROZEN","claims":"blocked","reviewed_plan_path":"docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-source-preparation-only.md","reviewed_plan_sha256":"' + b"0" * 64 + b'","verdict":"PASS"} \n'
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT"):
        parsed = pilot_source.parse_canonical_authority_object(raw, "plan-verdict")
        pilot_source.validate_source_preparation_plan_verdict(parsed, "0" * 64)


def test_plan_verdict_rejects_extra_key():
    from p3_v3 import pilot_source

    value = dict(_plan_verdict_valid())
    value["extra"] = "no"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT"):
        pilot_source.validate_source_preparation_plan_verdict(value, "0" * 64)


def test_plan_verdict_rejects_wrong_type():
    from p3_v3 import pilot_source

    value = dict(_plan_verdict_valid())
    value["claims"] = False
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT"):
        pilot_source.validate_source_preparation_plan_verdict(value, "0" * 64)


def test_plan_verdict_rejects_bad_sha():
    from p3_v3 import pilot_source

    value = dict(_plan_verdict_valid())
    value["reviewed_plan_sha256"] = "not-a-sha"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT"):
        pilot_source.validate_source_preparation_plan_verdict(value, "0" * 64)


def _capability_verdict_valid():
    return {
        "reviewed_plan_path": "docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-source-preparation-only.md",
        "reviewed_plan_sha256": "0" * 64,
        "reviewed_plan_verdict_sha256": "1" * 64,
        "reviewed_commit": "a" * 40,
        "reviewed_pilot_source_path": "src/p3_v3/pilot_source.py",
        "reviewed_pilot_source_sha256": "2" * 64,
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": "3" * 64,
        "reviewed_test_pilot_source_path": "tests/p3_v3/test_pilot_source.py",
        "reviewed_test_pilot_source_sha256": "4" * 64,
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": "5" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }


def test_capability_verdict_rejects_noncanonical():
    from p3_v3 import pilot_source

    raw = canonical_json_bytes(_capability_verdict_valid())[:-1] + b" \n"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"):
        parsed = pilot_source.parse_canonical_authority_object(raw, "capability-verdict")
        pilot_source.validate_source_preparation_capability_verdict(
            parsed, "0" * 64, "1" * 64
        )


def test_capability_verdict_rejects_extra_key():
    from p3_v3 import pilot_source

    value = dict(_capability_verdict_valid())
    value["extra"] = "no"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"):
        pilot_source.validate_source_preparation_capability_verdict(
            value, "0" * 64, "1" * 64
        )


def test_capability_verdict_rejects_wrong_type():
    from p3_v3 import pilot_source

    value = dict(_capability_verdict_valid())
    value["claims"] = 1
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"):
        pilot_source.validate_source_preparation_capability_verdict(
            value, "0" * 64, "1" * 64
        )


def test_capability_verdict_rejects_bad_sha():
    from p3_v3 import pilot_source

    value = dict(_capability_verdict_valid())
    value["reviewed_plan_sha256"] = "zz"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"):
        pilot_source.validate_source_preparation_capability_verdict(
            value, "0" * 64, "1" * 64
        )


def _launch_verdict_valid():
    return {
        "reviewed_packet_path": "docs/review_20260817/boost_math_pilot_source_preparation_launch_packet.md",
        "reviewed_packet_sha256": "0" * 64,
        "plan_verdict_sha256": "1" * 64,
        "capability_verdict_sha256": "2" * 64,
        "authorization_a_sha256": "3" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_LAUNCH_FROZEN",
        "claims": "blocked",
    }


def test_launch_verdict_rejects_noncanonical():
    from p3_v3 import pilot_source

    raw = canonical_json_bytes(_launch_verdict_valid())[:-1] + b" \n"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        parsed = pilot_source.parse_canonical_authority_object(raw, "launch-verdict")
        pilot_source.validate_source_preparation_launch_verdict(
            parsed,
            packet_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            authorization_a_sha256="3" * 64,
        )


def test_launch_verdict_rejects_extra_key():
    from p3_v3 import pilot_source

    value = dict(_launch_verdict_valid())
    value["extra"] = "no"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch_verdict(
            value,
            packet_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            authorization_a_sha256="3" * 64,
        )


def test_launch_verdict_rejects_wrong_type():
    from p3_v3 import pilot_source

    value = dict(_launch_verdict_valid())
    value["verdict"] = True
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch_verdict(
            value,
            packet_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            authorization_a_sha256="3" * 64,
        )


def test_launch_verdict_rejects_bad_sha():
    from p3_v3 import pilot_source

    value = dict(_launch_verdict_valid())
    value["reviewed_packet_sha256"] = "bad"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch_verdict(
            value,
            packet_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            authorization_a_sha256="3" * 64,
        )


def _launch_authority_valid():
    return {
        "schema_version": "p3-pilot-source-preparation-launch-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "source_preparation_plan_path": "docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-source-preparation-only.md",
        "source_preparation_plan_sha256": "0" * 64,
        "source_preparation_plan_verdict_path": "docs/review_20260817/boost_math_pilot_source_preparation_sol_high_review.md",
        "source_preparation_plan_verdict_sha256": "1" * 64,
        "capability_implementation_verdict_path": "docs/review_20260817/boost_math_pilot_source_preparation_implementation_sol_high_review.md",
        "capability_implementation_verdict_sha256": "2" * 64,
        "production_launch_packet_path": "docs/review_20260817/boost_math_pilot_source_preparation_launch_packet.md",
        "production_launch_packet_sha256": "3" * 64,
        "launch_sol_high_verdict_path": "docs/review_20260817/boost_math_pilot_source_preparation_launch_sol_high_review.md",
        "launch_sol_high_verdict_sha256": "4" * 64,
        "authorization_a_sha256": "5" * 64,
        "claims": "blocked",
        "artifact_sha256": "6" * 64,
    }


def test_launch_authority_rejects_noncanonical():
    from p3_v3 import pilot_source

    raw = canonical_json_bytes(_launch_authority_valid())[:-1] + b" \n"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        parsed = pilot_source.parse_canonical_authority_object(raw, "launch")
        pilot_source.validate_source_preparation_launch(
            parsed,
            plan_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            launch_packet_sha256="3" * 64,
            launch_verdict_sha256="4" * 64,
            authorization_a_sha256="5" * 64,
        )


def test_launch_authority_rejects_extra_key():
    from p3_v3 import pilot_source

    value = dict(_launch_authority_valid())
    value["extra"] = "no"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch(
            value,
            plan_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            launch_packet_sha256="3" * 64,
            launch_verdict_sha256="4" * 64,
            authorization_a_sha256="5" * 64,
        )


def test_launch_authority_rejects_wrong_type():
    from p3_v3 import pilot_source

    value = dict(_launch_authority_valid())
    value["claims"] = 0
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch(
            value,
            plan_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            launch_packet_sha256="3" * 64,
            launch_verdict_sha256="4" * 64,
            authorization_a_sha256="5" * 64,
        )


def test_launch_authority_rejects_bad_sha():
    from p3_v3 import pilot_source

    value = dict(_launch_authority_valid())
    value["source_preparation_plan_sha256"] = "bad"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch(
            value,
            plan_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            launch_packet_sha256="3" * 64,
            launch_verdict_sha256="4" * 64,
            authorization_a_sha256="5" * 64,
        )


def test_archive_snapshot_rejects_symlink(tmp_path):
    from p3_v3.pilot_source import read_production_archive_bytes

    target = tmp_path / "real.zip"
    target.write_bytes(b"PK\x03\x04" + b"x")
    link = tmp_path / "link.zip"
    link.symlink_to(target)
    with pytest.raises(EvidenceError, match="E_PILOT_ARCHIVE_UNSAFE"):
        read_production_archive_bytes(link)


def test_archive_snapshot_rejects_non_regular_file(tmp_path):
    from p3_v3.pilot_source import read_production_archive_bytes

    directory = tmp_path / "not-a-file"
    directory.mkdir()
    with pytest.raises(EvidenceError, match="E_PILOT_ARCHIVE_UNSAFE"):
        read_production_archive_bytes(directory)


def test_archive_snapshot_hashes_same_fd_bytes(tmp_path):
    from p3_v3.pilot_source import read_production_archive_bytes

    archive = tmp_path / "fixture.zip"
    archive.write_bytes(b"PK\x03\x04" + b"synthetic-zip-bytes")
    snapshot = read_production_archive_bytes(archive)
    assert snapshot.sha256 == __import__("hashlib").sha256(snapshot.raw).hexdigest()
    assert snapshot.size == len(snapshot.raw)
    assert snapshot.archive_format == "ZIP"


def test_archive_snapshot_rejects_identity_change(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    archive = tmp_path / "fixture.zip"
    archive.write_bytes(b"PK\x03\x04" + b"synthetic-zip-bytes")
    original = os.fstat
    calls = {"n": 0}

    def flaky(fd):
        info = original(fd)
        calls["n"] += 1
        if calls["n"] >= 3:
            return os.stat_result(
                (
                    info.st_mode,
                    info.st_ino + 1,
                    info.st_dev,
                    info.st_nlink,
                    info.st_uid,
                    info.st_gid,
                    info.st_size,
                    info.st_atime,
                    info.st_mtime,
                    info.st_ctime,
                )
            )
        return info

    monkeypatch.setattr(pilot_source.os, "fstat", flaky)
    with pytest.raises(EvidenceError, match="E_PILOT_ARCHIVE_UNSAFE"):
        pilot_source.read_production_archive_bytes(archive)


def test_archive_format_uses_bytes_not_suffix(tmp_path):
    from p3_v3.pilot_source import read_production_archive_bytes

    archive = tmp_path / "named-as.tar"
    archive.write_bytes(b"PK\x03\x04" + b"synthetic-zip-bytes")
    snapshot = read_production_archive_bytes(archive)
    assert snapshot.archive_format == "ZIP"


def test_zip_rejects_parent_traversal(tmp_path):
    from p3_v3 import pilot_source

    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("../escape.txt", b"x")
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_zip_rejects_symlink(tmp_path):
    from p3_v3 import pilot_source

    archive = tmp_path / "link.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = 0o120777 << 16
        handle.writestr(info, b"target")
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_zip_rejects_encrypted_member(tmp_path):
    from p3_v3 import pilot_source

    archive = tmp_path / "enc.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.setpassword(b"secret")
        handle.writestr("secret.txt", b"hidden")
        info = handle.getinfo("secret.txt")
        info.flag_bits |= 0x1
    data = bytearray(archive.read_bytes())
    index = 0
    while True:
        index = data.find(b"PK\x03\x04", index)
        if index < 0:
            break
        data[index + 6] |= 0x1
        index += 4
    index = 0
    while True:
        index = data.find(b"PK\x01\x02", index)
        if index < 0:
            break
        data[index + 8] |= 0x1
        index += 4
    archive.write_bytes(data)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_tar_rejects_parent_traversal(tmp_path):
    from p3_v3 import pilot_source

    archive = tmp_path / "bad.tar"
    with tarfile.open(archive, "w") as handle:
        info = tarfile.TarInfo("../escape.txt")
        payload = b"x"
        info.size = len(payload)
        handle.addfile(info, io.BytesIO(payload))
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_tar_rejects_symlink(tmp_path):
    from p3_v3 import pilot_source

    archive = tmp_path / "link.tar"
    with tarfile.open(archive, "w") as handle:
        info = tarfile.TarInfo("link")
        info.type = tarfile.SYMTYPE
        info.linkname = "target"
        handle.addfile(info)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_tar_rejects_hardlink(tmp_path):
    from p3_v3 import pilot_source

    archive = tmp_path / "hard.tar"
    with tarfile.open(archive, "w") as handle:
        payload = b"x"
        regular = tarfile.TarInfo("a.txt")
        regular.size = len(payload)
        handle.addfile(regular, io.BytesIO(payload))
        link = tarfile.TarInfo("b.txt")
        link.type = tarfile.LNKTYPE
        link.linkname = "a.txt"
        handle.addfile(link)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_extractor_rejects_casefold_collision(tmp_path):
    from p3_v3 import pilot_source

    archive = tmp_path / "case.zip"
    _write_zip(archive, {"Foo.txt": b"a", "foo.txt": b"b"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_extractor_rejects_duplicate_normalized_path(tmp_path):
    from p3_v3 import pilot_source

    archive = tmp_path / "dup.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("pkg/a.txt", b"one")
        handle.writestr("pkg//a.txt", b"two")
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_extractor_rejects_member_limit(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    policy = dict(pilot_source.EXTRACTOR_POLICY_V1)
    policy["max_member_count"] = 1
    monkeypatch.setattr(pilot_source, "EXTRACTOR_POLICY_V1", policy)
    archive = tmp_path / "many.zip"
    _write_zip(archive, {"a.txt": b"a", "b.txt": b"b"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_extractor_rejects_total_bytes_limit(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    policy = dict(pilot_source.EXTRACTOR_POLICY_V1)
    policy["max_total_uncompressed_bytes"] = 3
    monkeypatch.setattr(pilot_source, "EXTRACTOR_POLICY_V1", policy)
    archive = tmp_path / "big.zip"
    _write_zip(archive, {"a.txt": b"abcd"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_streamed_member_bytes_cannot_exceed_declared_policy_limit(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    policy = dict(pilot_source.EXTRACTOR_POLICY_V1)
    policy["max_member_bytes"] = 2
    monkeypatch.setattr(pilot_source, "EXTRACTOR_POLICY_V1", policy)
    archive = tmp_path / "member.zip"
    _write_zip(archive, {"a.txt": b"abcd"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_single_top_level_selection_is_order_invariant():
    from p3_v3.pilot_source import shared_top_level_directory

    assert shared_top_level_directory(["pkg/b", "pkg/a"]) == "pkg"
    assert shared_top_level_directory(["pkg/a", "pkg/b"]) == "pkg"


def test_single_top_level_file_is_not_stripped():
    from p3_v3.pilot_source import shared_top_level_directory

    assert shared_top_level_directory(["readme.txt"]) is None
    assert shared_top_level_directory(["pkg/a", "pkg/b"]) == "pkg"
    assert shared_top_level_directory(["pkg/b", "pkg/a"]) == "pkg"


def test_materialized_tree_uses_phase1_canonical_hash(tmp_path, monkeypatch):
    from p3_v3 import pilot_source
    from p3_v3.bridge_and_frames import canonical_source_tree_sha256 as phase1

    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "readme.txt").write_bytes(b"synthetic\n")
    snapshot = pilot_source.capture_materialized_tree(payload)
    seen: list[str] = []

    def spy(value):
        digest = phase1(value)
        seen.append(digest)
        return digest

    monkeypatch.setattr(pilot_source, "canonical_source_tree_sha256", spy)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_TREE_MISMATCH"):
        pilot_source.validate_materialized_tree_with_phase1(snapshot)
    assert seen == [phase1(snapshot)]
    assert seen[0] != pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256


def test_phase1_tree_hash_function_is_called_by_production_seam(tmp_path, monkeypatch):
    from p3_v3 import pilot_source
    from p3_v3.bridge_and_frames import SourceSnapshot

    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "readme.txt").write_bytes(b"synthetic\n")
    snapshot = pilot_source.capture_materialized_tree(payload)
    calls: list[object] = []

    def spy(value):
        calls.append(value)
        return pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256

    monkeypatch.setattr(pilot_source, "canonical_source_tree_sha256", spy)
    observed = pilot_source.validate_materialized_tree_with_phase1(snapshot)
    assert calls == [snapshot]
    assert type(calls[0]) is SourceSnapshot
    assert observed == pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256


def _install_minimal_fail_closed_chain(monkeypatch, tmp_path: Path) -> None:
    from p3_v3 import pilot_source

    _patch_outputs(monkeypatch, pilot_source, tmp_path)
    monkeypatch.setattr(pilot_source, "AUTHORIZATION_A_PATH", tmp_path / "missing-auth.txt")
    monkeypatch.setattr(
        pilot_source,
        "CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH",
        tmp_path / "missing-capability.md",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_LAUNCH_PATH",
        tmp_path / "missing-launch.json",
    )


def test_wrong_materialized_tree_writes_failure_result(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _install_full_authority_chain(monkeypatch, tmp_path)
    archive, snapshot, tree, _count, _total = _synthetic_tree_metrics(
        tmp_path, {"pkg/readme.txt": b"synthetic-mismatch\n"}
    )
    observed = __import__(
        "p3_v3.bridge_and_frames", fromlist=["canonical_source_tree_sha256"]
    ).canonical_source_tree_sha256(tree)
    materialize = tmp_path / "materialize"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_TREE_MISMATCH"):
        pilot_source.run_validate_source(archive, materialize)
    result_path = tmp_path / "source-preparation-result.json"
    assert result_path.is_file()
    result = __import__("json").loads(result_path.read_text(encoding="utf-8"))
    assert result["failure_reason"] == "SOURCE_TREE_MISMATCH"
    assert result["archive_sha256"] == snapshot.sha256
    assert result["archive_bytes"] == snapshot.size
    assert result["materialized_tree_sha256"] == observed
    assert result["source_manifest_sha256"] is None
    assert not (tmp_path / "source-manifest.json").exists()
    assert not materialize.exists()


def test_source_manifest_exact_keys():
    from p3_v3 import pilot_source

    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        pilot_source.validate_pilot_source_manifest({"schema_version": "x"})


def test_source_manifest_predecessors_are_exact():
    from p3_v3 import pilot_source

    expected = pilot_source.gate_chain_predecessor_sha256(
        "0" * 64, "1" * 64, "2" * 64, "3" * 64, "4" * 64
    )
    assert expected == sorted(["0" * 64, "1" * 64, "2" * 64, "3" * 64, "4" * 64])


def test_source_manifest_cannot_validate_as_pilot_plan():
    from p3_v3.pilot import validate_pilot_plan

    forged = {
        "schema_version": "p3-pilot-source-manifest-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "archive_sha256": "0" * 64,
        "archive_bytes": 1,
    }
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        validate_pilot_plan(forged)


def test_pass_result_binds_source_manifest():
    from p3_v3 import pilot_source

    with pytest.raises(EvidenceError):
        pilot_source.validate_pilot_source_preparation_result(
            {
                "schema_version": "p3-pilot-source-preparation-result-v1",
                "execution_class": "PILOT_ONLY",
                "denominator": "PILOT_ONLY",
                "p12_item_id": "C-BOOSTMATH-001",
                "neutral_snapshot_id": "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886",
                "normalized_source_tree_sha256": "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8",
                "controlled_subject_id": "89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914",
                "controlled_subject_source_id": "e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7",
                "predecessor_sha256": [],
                "terminal_status": "PASS",
                "failure_reason": None,
                "source_manifest_sha256": None,
                "archive_sha256": "0" * 64,
                "archive_bytes": 1,
                "materialized_tree_sha256": "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8",
                "artifact_sha256": "1" * 64,
            }
        )


def test_outputs_are_exclusive(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _install_full_authority_chain(monkeypatch, tmp_path)
    manifest = tmp_path / "source-manifest.json"
    result = tmp_path / "source-preparation-result.json"
    write_canonical_json(manifest, {"marker": "one"}, exclusive=True)
    write_canonical_json(result, {"marker": "result"}, exclusive=True)
    before_manifest = manifest.read_bytes()
    before_result = result.read_bytes()
    archive = tmp_path / "synthetic.zip"
    archive.write_bytes(b"PK\x03\x04" + b"unused")
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_OUTPUT_EXISTS"):
        pilot_source.run_validate_source(archive, tmp_path / "materialize")
    assert manifest.read_bytes() == before_manifest
    assert result.read_bytes() == before_result


def test_crash_after_manifest_publication():
    from p3_v3 import pilot_source

    state = pilot_source.classify_reconciliation(
        manifest_present=True,
        result_present=False,
        root_present=False,
        manifest_valid=True,
        result_valid=True,
        result_status=None,
        closed_pair_consistent=True,
    )
    assert state == "MANIFEST_ONLY"


def test_crash_after_materialize_root_rename():
    from p3_v3 import pilot_source

    state = pilot_source.classify_reconciliation(
        manifest_present=True,
        result_present=False,
        root_present=True,
        manifest_valid=True,
        result_valid=True,
        result_status=None,
        closed_pair_consistent=True,
    )
    assert state == "MANIFEST_AND_ROOT"


def test_manifest_only_recovery():
    from p3_v3 import pilot_source

    assert (
        pilot_source.classify_reconciliation(
            manifest_present=True,
            result_present=False,
            root_present=False,
            manifest_valid=True,
            result_valid=True,
            result_status=None,
            closed_pair_consistent=True,
        )
        == "MANIFEST_ONLY"
    )


def test_manifest_and_root_recovery():
    from p3_v3 import pilot_source

    assert (
        pilot_source.classify_reconciliation(
            manifest_present=True,
            result_present=False,
            root_present=True,
            manifest_valid=True,
            result_valid=True,
            result_status=None,
            closed_pair_consistent=True,
        )
        == "MANIFEST_AND_ROOT"
    )


def test_tampered_manifest_refuses_recovery():
    from p3_v3 import pilot_source

    assert (
        pilot_source.classify_reconciliation(
            manifest_present=True,
            result_present=False,
            root_present=False,
            manifest_valid=False,
            result_valid=True,
            result_status=None,
            closed_pair_consistent=True,
        )
        == "INVALID_DURABLE_OBJECT"
    )


def test_orphan_root_without_manifest_refuses_recovery():
    from p3_v3 import pilot_source

    assert (
        pilot_source.classify_reconciliation(
            manifest_present=False,
            result_present=False,
            root_present=True,
            manifest_valid=True,
            result_valid=True,
            result_status=None,
            closed_pair_consistent=True,
        )
        == "ORPHAN_ROOT"
    )


def test_result_is_always_the_final_pass_commit_point():
    from p3_v3 import pilot_source

    assert (
        pilot_source.classify_reconciliation(
            manifest_present=True,
            result_present=True,
            root_present=True,
            manifest_valid=True,
            result_valid=True,
            result_status="PASS",
            closed_pair_consistent=True,
        )
        == "ALREADY_COMPLETE"
    )


def test_tree_mismatch_leaves_materialize_root_and_manifest_absent(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _install_minimal_fail_closed_chain(monkeypatch, tmp_path)
    with pytest.raises(EvidenceError):
        pilot_source.run_validate_source(tmp_path / "missing.zip", tmp_path / "materialize")
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "materialize").exists()


def test_validate_source_cli_has_no_authority_overrides():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    forbidden = [
        "--authorization",
        "--output",
        "--expected-archive-hash",
        "--expected-tree-hash",
        "--expected-build-descriptor-hash",
        "--implementation-verdict",
        "--machine-plan",
        "--extractor-policy",
        "--launch-authority",
        "--plan-verdict",
        "--capability-verdict",
    ]
    for flag in forbidden:
        with pytest.raises(SystemExit):
            parser.parse_args(
                [
                    "validate-source",
                    "--archive",
                    "synthetic.zip",
                    "--materialize-root",
                    "synthetic-root",
                    flag,
                    "forged",
                ]
            )


def test_capability_implementation_creates_no_production_artifact():
    implementation_base = "1cdf2a1d5b4f43c5565f2b773103a971784468e1"
    verdict_path = Path(
        "docs/review_20260817/"
        "boost_math_pilot_source_preparation_implementation_sol_high_review.md"
    )
    verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    reviewed_commit = verdict["reviewed_commit"]

    assert reviewed_commit == "e5a92499b2b3495ecd0013b2279438147b203f25"

    env = dict(os.environ)
    env.update(
        {
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_COUNT": "0",
        }
    )
    completed = subprocess.run(
        [
            "git",
            "diff",
            "--name-status",
            f"{implementation_base}..{reviewed_commit}",
            "--",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    changed = completed.stdout.splitlines()
    assert changed == [
        "M\tscripts/p3_v3/pilot.py",
        "A\tsrc/p3_v3/pilot_source.py",
        "M\ttests/p3_v3/test_pilot.py",
        "A\ttests/p3_v3/test_pilot_source.py",
    ]

    changed_paths = {line.split("\t", 1)[1] for line in changed}
    production_paths = {
        "data/p3_v3/pilot/boost_math/user-auth-preparation.txt",
        "data/p3_v3/pilot/boost_math/source-manifest.json",
        "data/p3_v3/pilot/boost_math/source-preparation-result.json",
        "data/p3_v3/pilot/boost_math/source-preparation-launch.json",
        (
            "docs/review_20260817/"
            "boost_math_pilot_source_preparation_implementation_sol_high_review.md"
        ),
        (
            "docs/review_20260817/"
            "boost_math_pilot_source_preparation_launch_packet.md"
        ),
        (
            "docs/review_20260817/"
            "boost_math_pilot_source_preparation_launch_sol_high_review.md"
        ),
    }
    assert changed_paths.isdisjoint(production_paths)


def test_preexisting_staging_is_preserved_and_attempt_fails_closed(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _install_full_authority_chain(monkeypatch, tmp_path)
    materialize = tmp_path / "materialize"
    staging = Path(str(materialize) + ".staging")
    staging.mkdir()
    sentinel = staging / "sentinel"
    sentinel.write_bytes(b"keep-staging\n")
    calls: list[str] = []

    def forbidden(path):
        calls.append(str(path))
        raise AssertionError("archive snapshot started")

    monkeypatch.setattr(pilot_source, "read_production_archive_bytes", forbidden)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_OUTPUT_EXISTS"):
        pilot_source.run_validate_source(tmp_path / "unused.zip", materialize)
    assert sentinel.is_file()
    assert sentinel.read_bytes() == b"keep-staging\n"
    assert staging.is_dir()
    assert calls == []
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_manifest_only_recovery_replays_same_archive_and_finishes_pass(
    tmp_path, monkeypatch
):
    from p3_v3 import pilot_source

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    _force_frozen_tree_hash(monkeypatch)
    archive, snapshot, _tree, file_count, total_bytes = _synthetic_tree_metrics(
        tmp_path, {"pkg/a.txt": b"hello\n"}
    )
    manifest = _canonical_manifest(
        predecessors=chain["predecessors"],
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        archive_format=snapshot.archive_format,
        file_count=file_count,
        total_bytes=total_bytes,
    )
    manifest_path = tmp_path / "source-manifest.json"
    write_canonical_json(manifest_path, manifest, exclusive=True)
    before = manifest_path.read_bytes()
    materialize = tmp_path / "materialize"
    pilot_source.run_validate_source(archive, materialize)
    assert manifest_path.read_bytes() == before
    assert materialize.is_dir()
    assert (materialize / "a.txt").read_bytes() == b"hello\n"
    result_path = tmp_path / "source-preparation-result.json"
    result = __import__("json").loads(result_path.read_text(encoding="utf-8"))
    assert result["terminal_status"] == "PASS"
    assert result["source_manifest_sha256"] == _sha256_bytes(before)
    assert result["predecessor_sha256"] == sorted(
        [*chain["predecessors"], _sha256_bytes(before)]
    )


def test_manifest_and_root_recovery_verifies_root_and_finishes_without_rename(
    tmp_path, monkeypatch
):
    from p3_v3 import pilot_source

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    _force_frozen_tree_hash(monkeypatch)
    archive, snapshot, _tree, file_count, total_bytes = _synthetic_tree_metrics(
        tmp_path, {"pkg/a.txt": b"hello\n"}
    )
    manifest = _canonical_manifest(
        predecessors=chain["predecessors"],
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        archive_format=snapshot.archive_format,
        file_count=file_count,
        total_bytes=total_bytes,
    )
    write_canonical_json(tmp_path / "source-manifest.json", manifest, exclusive=True)
    materialize = tmp_path / "materialize"
    materialize.mkdir()
    (materialize / "a.txt").write_bytes(b"hello\n")
    inode = materialize.stat().st_ino
    payload = (materialize / "a.txt").read_bytes()
    archive_calls: list[str] = []
    original = pilot_source.extract_archive_to_staging

    def no_extract(snapshot_obj, staging):
        archive_calls.append(str(staging))
        return original(snapshot_obj, staging)

    monkeypatch.setattr(pilot_source, "extract_archive_to_staging", no_extract)
    pilot_source.run_validate_source(archive, materialize)
    assert materialize.stat().st_ino == inode
    assert (materialize / "a.txt").read_bytes() == payload
    assert archive_calls == []
    result = __import__("json").loads(
        (tmp_path / "source-preparation-result.json").read_text(encoding="utf-8")
    )
    assert result["terminal_status"] == "PASS"
    assert not Path(str(materialize) + ".staging").exists()


def test_manifest_and_root_recovery_rejects_root_mismatch(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    _force_frozen_tree_hash(monkeypatch)
    archive, snapshot, _tree, file_count, total_bytes = _synthetic_tree_metrics(
        tmp_path, {"pkg/a.txt": b"hello\n"}
    )
    manifest = _canonical_manifest(
        predecessors=chain["predecessors"],
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        archive_format=snapshot.archive_format,
        file_count=file_count,
        total_bytes=total_bytes,
    )
    manifest_path = tmp_path / "source-manifest.json"
    write_canonical_json(manifest_path, manifest, exclusive=True)
    before = manifest_path.read_bytes()
    materialize = tmp_path / "materialize"
    materialize.mkdir()
    (materialize / "a.txt").write_bytes(b"DIFFERENT\n")
    inode = materialize.stat().st_ino
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_TREE_MISMATCH|E_PILOT_SOURCE_MANIFEST"):
        pilot_source.run_validate_source(archive, materialize)
    assert manifest_path.read_bytes() == before
    assert materialize.stat().st_ino == inode
    assert (materialize / "a.txt").read_bytes() == b"DIFFERENT\n"
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_already_complete_revalidates_root(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    _force_frozen_tree_hash(monkeypatch)
    archive, snapshot, _tree, file_count, total_bytes = _synthetic_tree_metrics(
        tmp_path, {"pkg/a.txt": b"hello\n"}
    )
    manifest = _canonical_manifest(
        predecessors=chain["predecessors"],
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        archive_format=snapshot.archive_format,
        file_count=file_count,
        total_bytes=total_bytes,
    )
    manifest_path = tmp_path / "source-manifest.json"
    write_canonical_json(manifest_path, manifest, exclusive=True)
    manifest_bytes = manifest_path.read_bytes()
    materialize = tmp_path / "materialize"
    materialize.mkdir()
    (materialize / "a.txt").write_bytes(b"hello\n")
    (materialize / "extra.txt").write_bytes(b"tamper\n")
    result = _canonical_result(
        predecessors=sorted([*chain["predecessors"], _sha256_bytes(manifest_bytes)]),
        terminal_status="PASS",
        failure_reason=None,
        source_manifest_sha256=_sha256_bytes(manifest_bytes),
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        materialized_tree_sha256=pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
    )
    result_path = tmp_path / "source-preparation-result.json"
    write_canonical_json(result_path, result, exclusive=True)
    before_result = result_path.read_bytes()
    with pytest.raises(EvidenceError):
        pilot_source.run_validate_source(archive, materialize)
    assert manifest_path.read_bytes() == manifest_bytes
    assert result_path.read_bytes() == before_result
    assert (materialize / "extra.txt").is_file()


def test_durable_manifest_predecessor_drift_is_invalid(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    drifted = ["a" * 64, "b" * 64, "c" * 64, "d" * 64, "e" * 64]
    assert drifted != chain["predecessors"]
    archive, snapshot, _tree, file_count, total_bytes = _synthetic_tree_metrics(
        tmp_path, {"pkg/a.txt": b"hello\n"}
    )
    manifest = _canonical_manifest(
        predecessors=drifted,
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        archive_format=snapshot.archive_format,
        file_count=file_count,
        total_bytes=total_bytes,
    )
    pilot_source.validate_pilot_source_manifest(manifest)
    manifest_path = tmp_path / "source-manifest.json"
    write_canonical_json(manifest_path, manifest, exclusive=True)
    before = manifest_path.read_bytes()
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_MANIFEST"):
        pilot_source.run_validate_source(archive, tmp_path / "materialize")
    assert manifest_path.read_bytes() == before
    assert not (tmp_path / "source-preparation-result.json").exists()
    assert not (tmp_path / "materialize").exists()


def test_durable_result_predecessor_drift_is_invalid(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    drifted = ["1" * 64]
    fail = _canonical_result(
        predecessors=drifted,
        terminal_status="FAIL_INFRASTRUCTURE",
        failure_reason="ARCHIVE_UNSAFE",
        source_manifest_sha256=None,
        archive_sha256=None,
        archive_bytes=None,
        materialized_tree_sha256=None,
    )
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_RESULT"):
        pilot_source.validate_pilot_source_preparation_result(
            fail, expected_predecessors=chain["predecessors"]
        )
    pass_result = _canonical_result(
        predecessors=drifted,
        terminal_status="PASS",
        failure_reason=None,
        source_manifest_sha256="2" * 64,
        archive_sha256="3" * 64,
        archive_bytes=1,
        materialized_tree_sha256=pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
    )
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_RESULT"):
        pilot_source.validate_pilot_source_preparation_result(
            pass_result,
            expected_predecessors=sorted([*chain["predecessors"], "2" * 64]),
        )
    result_path = tmp_path / "source-preparation-result.json"
    write_canonical_json(result_path, fail, exclusive=True)
    before = result_path.read_bytes()
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_RESULT"):
        pilot_source.run_validate_source(tmp_path / "unused.zip", tmp_path / "materialize")
    assert result_path.read_bytes() == before


@pytest.mark.parametrize(
    ("reason", "archive_sha256", "archive_bytes", "tree_hash", "allowed"),
    [
        ("ARCHIVE_UNSAFE", None, None, None, True),
        ("ARCHIVE_UNSAFE", "0" * 64, 1, None, False),
        ("ARCHIVE_FORMAT_UNSUPPORTED", None, None, None, True),
        ("ARCHIVE_FORMAT_UNSUPPORTED", "0" * 64, 4, None, True),
        ("ARCHIVE_FORMAT_UNSUPPORTED", "0" * 64, None, None, False),
        ("ARCHIVE_FORMAT_UNSUPPORTED", None, 4, None, False),
        ("EXTRACTION_UNSAFE", "0" * 64, 4, None, True),
        ("EXTRACTION_UNSAFE", None, None, None, False),
        ("EXTRACTION_UNSAFE", "0" * 64, 4, "1" * 64, False),
        ("SOURCE_TREE_MISMATCH", "0" * 64, 4, "2" * 64, True),
        ("SOURCE_TREE_MISMATCH", None, None, "2" * 64, False),
        ("SOURCE_TREE_MISMATCH", "0" * 64, 4, None, False),
        ("NOT_A_REASON", None, None, None, False),
    ],
)
def test_fail_result_evidence_matrix_is_exact(
    reason, archive_sha256, archive_bytes, tree_hash, allowed
):
    from p3_v3 import pilot_source

    predecessors = ["a" * 64, "b" * 64, "c" * 64, "d" * 64, "e" * 64]
    value = _canonical_result(
        predecessors=predecessors,
        terminal_status="FAIL_INFRASTRUCTURE",
        failure_reason=reason,
        source_manifest_sha256=None,
        archive_sha256=archive_sha256,
        archive_bytes=archive_bytes,
        materialized_tree_sha256=tree_hash,
    )
    if allowed:
        validated = pilot_source.validate_pilot_source_preparation_result(
            value, expected_predecessors=predecessors
        )
        assert validated["failure_reason"] == reason
    else:
        with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_RESULT"):
            pilot_source.validate_pilot_source_preparation_result(
                value, expected_predecessors=predecessors
            )
    claimed = _canonical_result(
        predecessors=predecessors,
        terminal_status="FAIL_INFRASTRUCTURE",
        failure_reason="ARCHIVE_UNSAFE",
        source_manifest_sha256="f" * 64,
        archive_sha256=None,
        archive_bytes=None,
        materialized_tree_sha256=None,
    )
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_RESULT"):
        pilot_source.validate_pilot_source_preparation_result(
            claimed, expected_predecessors=predecessors
        )


def test_manifest_digest_uses_validated_snapshot_bytes(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    _force_frozen_tree_hash(monkeypatch)
    archive, snapshot, _tree, file_count, total_bytes = _synthetic_tree_metrics(
        tmp_path, {"pkg/a.txt": b"hello\n"}
    )
    manifest = _canonical_manifest(
        predecessors=chain["predecessors"],
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        archive_format=snapshot.archive_format,
        file_count=file_count,
        total_bytes=total_bytes,
    )
    manifest_path = tmp_path / "source-manifest.json"
    write_canonical_json(manifest_path, manifest, exclusive=True)
    original = manifest_path.read_bytes()
    materialize = tmp_path / "materialize"
    materialize.mkdir()
    (materialize / "a.txt").write_bytes(b"hello\n")
    result = _canonical_result(
        predecessors=sorted([*chain["predecessors"], _sha256_bytes(original)]),
        terminal_status="PASS",
        failure_reason=None,
        source_manifest_sha256=_sha256_bytes(original),
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        materialized_tree_sha256=pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
    )
    write_canonical_json(tmp_path / "source-preparation-result.json", result, exclusive=True)
    original_read = pilot_source.read_authority_snapshot

    def replace_after_snapshot(path, context):
        raw, digest = original_read(path, context)
        if Path(path) == manifest_path:
            Path(path).write_bytes(b"replaced-manifest-bytes\n")
        return raw, digest

    monkeypatch.setattr(pilot_source, "read_authority_snapshot", replace_after_snapshot)
    pilot_source.run_validate_source(archive, materialize)
    assert manifest_path.read_bytes() == b"replaced-manifest-bytes\n"
    result_after = __import__("json").loads(
        (tmp_path / "source-preparation-result.json").read_text(encoding="utf-8")
    )
    assert result_after["source_manifest_sha256"] == _sha256_bytes(original)


def test_corrupt_archive_cleans_only_attempt_owned_staging(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _install_full_authority_chain(monkeypatch, tmp_path)
    preexisting = tmp_path / "preexisting-keep"
    preexisting.mkdir()
    keep = preexisting / "keep.txt"
    keep.write_bytes(b"retain\n")
    archive = tmp_path / "corrupt.zip"
    archive.write_bytes(b"PK\x03\x04" + b"not-a-valid-zip-body")
    materialize = tmp_path / "materialize"
    with pytest.raises(EvidenceError, match="E_PILOT_ARCHIVE_FORMAT|E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.run_validate_source(archive, materialize)
    assert keep.is_file()
    assert keep.read_bytes() == b"retain\n"
    assert not Path(str(materialize) + ".staging").exists()
    assert not materialize.exists()
    assert not (tmp_path / "source-manifest.json").exists()


def test_corrupt_magic_archive_writes_exact_format_failure_result(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    raw = b"PK\x03\x04not-a-valid-zip-body"
    archive = tmp_path / "corrupt-magic.zip"
    archive.write_bytes(raw)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    assert snapshot.raw == raw
    materialize = tmp_path / "materialize"
    with pytest.raises(EvidenceError, match="E_PILOT_ARCHIVE_FORMAT"):
        pilot_source.run_validate_source(archive, materialize)
    result_path = tmp_path / "source-preparation-result.json"
    assert result_path.is_file()
    result = __import__("json").loads(result_path.read_text(encoding="utf-8"))
    expected = _canonical_result(
        predecessors=chain["predecessors"],
        terminal_status="FAIL_INFRASTRUCTURE",
        failure_reason="ARCHIVE_FORMAT_UNSUPPORTED",
        source_manifest_sha256=None,
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        materialized_tree_sha256=None,
    )
    assert result == expected
    assert result["archive_sha256"] == snapshot.sha256
    assert result["archive_bytes"] == snapshot.size
    assert result["materialized_tree_sha256"] is None
    assert result["source_manifest_sha256"] is None
    assert not (tmp_path / "source-manifest.json").exists()
    assert not materialize.exists()
    assert not Path(str(materialize) + ".staging").exists()


def test_staging_write_oserror_is_extraction_failure_not_archive_format(
    tmp_path, monkeypatch
):
    from p3_v3 import pilot_source

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    archive, snapshot, _tree, _count, _total = _synthetic_tree_metrics(
        tmp_path, {"pkg/a.txt": b"hello\n"}
    )

    def boom(*_args, **_kwargs):
        raise OSError("injected staging write failure")

    monkeypatch.setattr(pilot_source, "_write_streamed_member", boom)
    materialize = tmp_path / "materialize"
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.run_validate_source(archive, materialize)
    result_path = tmp_path / "source-preparation-result.json"
    assert result_path.is_file()
    result = __import__("json").loads(result_path.read_text(encoding="utf-8"))
    expected = _canonical_result(
        predecessors=chain["predecessors"],
        terminal_status="FAIL_INFRASTRUCTURE",
        failure_reason="EXTRACTION_UNSAFE",
        source_manifest_sha256=None,
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        materialized_tree_sha256=None,
    )
    assert result == expected
    assert not (tmp_path / "source-manifest.json").exists()
    assert not materialize.exists()
    assert not Path(str(materialize) + ".staging").exists()


def test_manifest_publication_crash_with_staging_recovers_on_retry(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    class PublicationCrash(BaseException):
        """Crash after exclusive manifest create and before root rename."""

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    _force_frozen_tree_hash(monkeypatch)
    archive, snapshot, _tree, _count, _total = _synthetic_tree_metrics(
        tmp_path, {"pkg/a.txt": b"hello\n"}
    )
    materialize = tmp_path / "materialize"
    staging = Path(str(materialize) + ".staging")
    manifest_path = tmp_path / "source-manifest.json"
    result_path = tmp_path / "source-preparation-result.json"
    real_replace = pilot_source.os.replace

    def crash_replace(src, dst, *args, **kwargs):
        if Path(src) == staging and Path(dst) == materialize:
            raise PublicationCrash("injected after manifest publication")
        return real_replace(src, dst, *args, **kwargs)

    monkeypatch.setattr(pilot_source.os, "replace", crash_replace)
    with pytest.raises(PublicationCrash):
        pilot_source.run_validate_source(archive, materialize)
    assert manifest_path.is_file()
    assert staging.is_dir()
    assert (staging / "a.txt").read_bytes() == b"hello\n"
    assert not materialize.exists()
    assert not result_path.exists()
    manifest_bytes = manifest_path.read_bytes()
    staging_inode = staging.stat().st_ino
    monkeypatch.setattr(pilot_source.os, "replace", real_replace)
    extract_calls: list[str] = []
    original_extract = pilot_source.extract_archive_to_staging

    def spy_extract(snapshot_obj, staging_path):
        extract_calls.append(str(staging_path))
        return original_extract(snapshot_obj, staging_path)

    monkeypatch.setattr(pilot_source, "extract_archive_to_staging", spy_extract)
    pilot_source.run_validate_source(archive, materialize)
    assert extract_calls == []
    assert manifest_path.read_bytes() == manifest_bytes
    assert materialize.is_dir()
    assert materialize.stat().st_ino == staging_inode
    assert (materialize / "a.txt").read_bytes() == b"hello\n"
    assert not staging.exists()
    result = __import__("json").loads(result_path.read_text(encoding="utf-8"))
    assert result["terminal_status"] == "PASS"
    assert result["source_manifest_sha256"] == _sha256_bytes(manifest_bytes)
    assert result["archive_sha256"] == snapshot.sha256
    assert result["archive_bytes"] == snapshot.size
    assert result["predecessor_sha256"] == sorted(
        [*chain["predecessors"], _sha256_bytes(manifest_bytes)]
    )


def test_manifest_only_mismatched_staging_is_preserved_and_rejected(
    tmp_path, monkeypatch
):
    from p3_v3 import pilot_source

    chain = _install_full_authority_chain(monkeypatch, tmp_path)
    archive, snapshot, _tree, file_count, total_bytes = _synthetic_tree_metrics(
        tmp_path, {"pkg/a.txt": b"hello\n"}
    )
    manifest = _canonical_manifest(
        predecessors=chain["predecessors"],
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        archive_format=snapshot.archive_format,
        file_count=file_count,
        total_bytes=total_bytes,
    )
    write_canonical_json(tmp_path / "source-manifest.json", manifest, exclusive=True)
    materialize = tmp_path / "materialize"
    staging = Path(str(materialize) + ".staging")
    staging.mkdir()
    wrong = staging / "wrong.txt"
    wrong.write_bytes(b"mismatch-bytes\n")
    staging_inode = staging.stat().st_ino
    file_inode = wrong.stat().st_ino
    extract_calls: list[str] = []

    def forbidden_extract(snapshot_obj, staging_path):
        extract_calls.append(str(staging_path))
        raise AssertionError("extractor must not run for mismatched residue")

    monkeypatch.setattr(pilot_source, "extract_archive_to_staging", forbidden_extract)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_TREE_MISMATCH"):
        pilot_source.run_validate_source(archive, materialize)
    assert staging.stat().st_ino == staging_inode
    assert wrong.stat().st_ino == file_inode
    assert wrong.read_bytes() == b"mismatch-bytes\n"
    assert list(staging.iterdir()) == [wrong]
    assert extract_calls == []
    assert not materialize.exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_dangling_staging_symlink_is_rejected_before_archive_snapshot(
    tmp_path, monkeypatch
):
    from p3_v3 import pilot_source

    _install_full_authority_chain(monkeypatch, tmp_path)
    materialize = tmp_path / "materialize"
    staging = Path(str(materialize) + ".staging")
    missing_target = tmp_path / "absent-staging-target"
    staging.symlink_to(missing_target, target_is_directory=True)
    before_stat = os.lstat(staging)
    before_target = os.readlink(staging)
    archive_calls: list[str] = []
    original_read = pilot_source.read_production_archive_bytes

    def spy_read(path):
        archive_calls.append(str(path))
        return original_read(path)

    monkeypatch.setattr(pilot_source, "read_production_archive_bytes", spy_read)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_OUTPUT_EXISTS"):
        pilot_source.run_validate_source(tmp_path / "unused.zip", materialize)
    assert archive_calls == []
    after_stat = os.lstat(staging)
    assert staging.is_symlink()
    assert after_stat.st_ino == before_stat.st_ino
    assert os.readlink(staging) == before_target
    assert not materialize.exists()
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()
def _attempt2_fixture(tmp_path, monkeypatch, members=None):
    from p3_v3 import pilot_source

    members = members or {"pkg/include/boost/math/a.hpp": b"math\n", "pkg/x.txt": b"x\n"}
    archive = _write_tar(tmp_path / "source.tar", members)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    extracted = tmp_path / "expected"
    pilot_source.extract_archive_to_staging(snapshot, extracted)
    tree = pilot_source.capture_materialized_tree(extracted)
    tree_hash = pilot_source.canonical_source_tree_sha256(tree)
    count, total = pilot_source._tree_metrics(tree)
    root = tmp_path / "production"
    staging = tmp_path / "production.staging"
    manifest_path = tmp_path / "source-manifest.json"
    result_path = tmp_path / "source-result.json"
    monkeypatch.setattr(pilot_source, "ATTEMPT2_ARCHIVE_PATH", archive)
    monkeypatch.setattr(pilot_source, "ATTEMPT2_SOURCE_ROOT", root)
    monkeypatch.setattr(pilot_source, "ATTEMPT2_SOURCE_STAGING_ROOT", staging)
    monkeypatch.setattr(pilot_source, "ATTEMPT2_ARCHIVE_SHA256", snapshot.sha256)
    monkeypatch.setattr(pilot_source, "ATTEMPT2_ARCHIVE_BYTES", snapshot.size)
    monkeypatch.setattr(pilot_source, "FROZEN_NORMALIZED_SOURCE_TREE_SHA256", tree_hash)
    monkeypatch.setattr(pilot_source, "ATTEMPT2_FILE_COUNT", count)
    monkeypatch.setattr(pilot_source, "ATTEMPT2_TOTAL_BYTES", total)
    monkeypatch.setattr(pilot_source, "SOURCE_MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(pilot_source, "SOURCE_PREPARATION_RESULT_PATH", result_path)
    chain = pilot_source._GateChain(*("1" * 64, "2" * 64, "3" * 64,
                                      "4" * 64, "5" * 64, "6" * 64,
                                      "7" * 64))
    monkeypatch.setattr(pilot_source, "verify_production_gate_chain", lambda: chain)
    manifest = _canonical_manifest(
        predecessors=chain.predecessors(), archive_sha256=snapshot.sha256, archive_bytes=snapshot.size,
        archive_format="TAR", file_count=count, total_bytes=total,
    )
    manifest["normalized_source_tree_sha256"] = tree_hash
    manifest["artifact_sha256"] = canonical_sha256(
        {k: v for k, v in manifest.items() if k != "artifact_sha256"}
    )
    manifest_digest = hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
    result = _canonical_result(
        predecessors=sorted([*chain.predecessors(), manifest_digest]), terminal_status="PASS", failure_reason=None,
        source_manifest_sha256=manifest_digest, archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size, materialized_tree_sha256=tree_hash,
    )
    write_canonical_json(manifest_path, manifest, exclusive=True)
    write_canonical_json(result_path, result, exclusive=True)
    shutil.rmtree(extracted)
    return pilot_source, archive, root, staging, manifest_path, result_path


def test_source_restoration_evidence_rejects_missing_extra_type_value_timestamp_and_hash(monkeypatch):
    from p3_v3.artifacts import canonical_sha256
    from p3_v3 import pilot_source

    value = {
        "schema_version": "p3-pilot-source-restoration-evidence-v1",
        "execution_class": "PILOT_ONLY", "claims": "blocked",
        "disposition": "REVALIDATED", "archive_sha256": "6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392",
        "archive_bytes": 99676160, "normalized_tree_sha256": pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
        "materialized_file_count": 4396, "materialized_total_bytes": 95635487,
        "staging_published": False, "root_published": False,
        "started_at": "2026-08-25T00:00:00Z", "ended_at": "2026-08-25T00:00:01Z",
        "terminal_status": "PASS", "failure_reason": None,
    }
    value["artifact_sha256"] = canonical_sha256(value)
    assert pilot_source.validate_source_restoration_evidence(value) == value
    mutations = [
        lambda x: x.pop("claims"), lambda x: x.update(extra=True),
        lambda x: x.update(archive_bytes=True), lambda x: x.update(disposition="OTHER"),
        lambda x: x.update(started_at="not-a-time"),
        lambda x: x.update(started_at="2026-08-25T00:00:02Z"),
        lambda x: x.update(artifact_sha256="0" * 64),
    ]
    for mutate in mutations:
        bad = dict(value)
        mutate(bad)
        with pytest.raises(EvidenceError):
            pilot_source.validate_source_restoration_evidence(bad)


def test_attempt2_restore_wrong_archive_and_root_return_failure_evidence(tmp_path, monkeypatch):
    from p3_v3 import pilot_source
    archive = tmp_path / "frozen.tar"
    root = tmp_path / "frozen-root"
    monkeypatch.setattr(pilot_source, "ATTEMPT2_ARCHIVE_PATH", archive)
    monkeypatch.setattr(pilot_source, "ATTEMPT2_SOURCE_ROOT", root)
    monkeypatch.setattr(pilot_source, "ATTEMPT2_SOURCE_STAGING_ROOT", tmp_path / "stage")
    for actual_archive, actual_root, reason in [
        (tmp_path / "wrong", root, "WRONG_ARCHIVE_PATH"),
        (archive, tmp_path / "wrong-root", "WRONG_SOURCE_ROOT"),
    ]:
        evidence = pilot_source.run_restore_production_source(actual_archive, actual_root)
        assert (evidence["terminal_status"], evidence["disposition"], evidence["failure_reason"]) == ("FAIL", "NOT_APPLIED", reason)


def test_attempt2_restore_invalid_pass_no_root_success(tmp_path, monkeypatch):
    ps, archive, root, staging, manifest, result = _attempt2_fixture(tmp_path, monkeypatch)
    before = (manifest.read_bytes(), result.read_bytes())
    evidence = ps.run_restore_production_source(archive, root)
    assert (evidence["disposition"], evidence["terminal_status"]) == ("RESTORED", "PASS")
    assert root.is_dir() and (root / "include/boost/math/a.hpp").is_file()
    assert not os.path.lexists(staging)
    assert before == (manifest.read_bytes(), result.read_bytes())


def test_attempt2_restore_already_complete_revalidates_without_mutation(tmp_path, monkeypatch):
    ps, archive, root, staging, manifest, result = _attempt2_fixture(tmp_path, monkeypatch)
    snap = ps.read_production_archive_bytes(archive)
    ps.extract_archive_to_staging(snap, root)
    before = (root.stat().st_ino, manifest.read_bytes(), result.read_bytes())
    evidence = ps.run_restore_production_source(archive, root)
    assert evidence["disposition"] == "REVALIDATED"
    assert before == (root.stat().st_ino, manifest.read_bytes(), result.read_bytes())


def test_attempt2_restore_rejects_archive_symlink_hash_size_and_format(tmp_path, monkeypatch):
    ps, archive, root, staging, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    link = tmp_path / "link.tar"; link.symlink_to(archive)
    monkeypatch.setattr(ps, "ATTEMPT2_ARCHIVE_PATH", link)
    assert ps.run_restore_production_source(link, root)["failure_reason"] == "ARCHIVE_UNSAFE"
    monkeypatch.setattr(ps, "ATTEMPT2_ARCHIVE_PATH", archive)
    monkeypatch.setattr(ps, "ATTEMPT2_ARCHIVE_SHA256", "0" * 64)
    assert ps.run_restore_production_source(archive, root)["failure_reason"] == "ARCHIVE_HASH_MISMATCH"
    monkeypatch.setattr(ps, "ATTEMPT2_ARCHIVE_SHA256", _file_sha256(archive))
    monkeypatch.setattr(ps, "ATTEMPT2_ARCHIVE_BYTES", archive.stat().st_size + 1)
    assert ps.run_restore_production_source(archive, root)["failure_reason"] == "ARCHIVE_SIZE_MISMATCH"
    monkeypatch.setattr(ps, "ATTEMPT2_ARCHIVE_BYTES", archive.stat().st_size)
    monkeypatch.setattr(ps, "detect_archive_format", lambda raw: "ZIP")
    assert ps.run_restore_production_source(archive, root)["failure_reason"] == "ARCHIVE_FORMAT_MISMATCH"


def test_attempt2_restore_rejects_unsafe_extraction(tmp_path, monkeypatch):
    ps, archive, root, staging, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(ps, "extract_archive_to_staging", lambda *_: (_ for _ in ()).throw(EvidenceError("E_PILOT_EXTRACT_UNSAFE", "bad")))
    assert ps.run_restore_production_source(archive, root)["failure_reason"] == "EXTRACTION_UNSAFE"
    assert not os.path.lexists(root)


def test_attempt2_restore_rejects_staging_collision_and_symlink(tmp_path, monkeypatch):
    for symlink in (False, True):
        case = tmp_path / str(symlink); case.mkdir()
        ps, archive, root, staging, *_ = _attempt2_fixture(case, monkeypatch)
        staging.symlink_to(case / "missing") if symlink else staging.mkdir()
        expected = "STAGING_SYMLINK" if symlink else "STAGING_EXISTS"
        assert ps.run_restore_production_source(archive, root)["failure_reason"] == expected


def test_attempt2_restore_rejects_partial_orphan_and_root_symlink(tmp_path, monkeypatch):
    ps, archive, root, staging, manifest, result = _attempt2_fixture(tmp_path, monkeypatch)
    result.unlink(); root.mkdir()
    assert ps.run_restore_production_source(archive, root)["failure_reason"] == "INVALID_RECONCILIATION_STATE"
    root.rmdir(); root.symlink_to(tmp_path / "missing")
    assert ps.run_restore_production_source(archive, root)["failure_reason"] == "ROOT_SYMLINK"


def test_attempt2_restore_distinguishes_tree_hash_count_and_byte_failures(tmp_path, monkeypatch):
    ps, archive, root, staging, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    original_hash = ps.canonical_source_tree_sha256
    original_metrics = ps._tree_metrics
    with monkeypatch.context() as patch:
        patch.setattr(ps, "canonical_source_tree_sha256", lambda tree: "0" * 64)
        assert ps.run_restore_production_source(archive, root)["failure_reason"] == "TREE_HASH_MISMATCH"
    with monkeypatch.context() as patch:
        patch.setattr(ps, "_tree_metrics", lambda tree: (99, original_metrics(tree)[1]))
        assert ps.run_restore_production_source(archive, root)["failure_reason"] == "FILE_COUNT_MISMATCH"
    with monkeypatch.context() as patch:
        patch.setattr(ps, "_tree_metrics", lambda tree: (original_metrics(tree)[0], 99))
        assert ps.run_restore_production_source(archive, root)["failure_reason"] == "BYTE_COUNT_MISMATCH"
    assert ps.canonical_source_tree_sha256 is original_hash


def test_attempt2_restore_rejects_invalid_or_crossed_pass_pair(tmp_path, monkeypatch):
    ps, archive, root, staging, manifest, result = _attempt2_fixture(tmp_path, monkeypatch)
    raw = json.loads(result.read_text()); raw["source_manifest_sha256"] = "0" * 64
    raw["artifact_sha256"] = canonical_sha256({k:v for k,v in raw.items() if k != "artifact_sha256"})
    result.write_bytes(canonical_json_bytes(raw))
    assert ps.run_restore_production_source(archive, root)["failure_reason"] == "INVALID_PASS_PAIR"


def test_attempt2_restore_never_starts_subprocess(tmp_path, monkeypatch):
    ps, archive, root, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    def forbidden(*args, **kwargs): raise AssertionError("subprocess forbidden")
    monkeypatch.setattr(subprocess, "run", forbidden); monkeypatch.setattr(subprocess, "Popen", forbidden)
    assert ps.run_restore_production_source(archive, root)["terminal_status"] == "PASS"


def test_attempt2_restore_reuses_verified_chain_for_state_inspection(tmp_path, monkeypatch):
    ps, archive, root, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    chain = ps.verify_production_gate_chain()
    calls = []
    original_inspect = ps._inspect_state
    monkeypatch.setattr(ps, "verify_production_gate_chain",
                        lambda: calls.append(("verify", chain)) or chain)

    def inspect(actual_chain, actual_root):
        calls.append(("inspect", actual_chain, actual_root))
        return original_inspect(actual_chain, actual_root)

    monkeypatch.setattr(ps, "_inspect_state", inspect)
    assert ps.run_restore_production_source(archive, root)["terminal_status"] == "PASS"
    assert calls == [("verify", chain), ("inspect", chain, root)]
    assert not hasattr(ps, "_read_restoration_pass_pair")


def test_attempt2_restore_rejects_forged_predecessor_chain_before_mutation(tmp_path, monkeypatch):
    ps, archive, root, staging, manifest, result = _attempt2_fixture(tmp_path, monkeypatch)
    before = (manifest.read_bytes(), result.read_bytes())
    wrong_chain = ps._GateChain(*("a" * 64, "b" * 64, "c" * 64, "d" * 64,
                                  "e" * 64, "f" * 64, "0" * 64))
    monkeypatch.setattr(ps, "verify_production_gate_chain", lambda: wrong_chain)
    evidence = ps.run_restore_production_source(archive, root)
    assert evidence["failure_reason"] == "INVALID_PASS_PAIR"
    assert not os.path.lexists(staging) and not os.path.lexists(root)
    assert before == (manifest.read_bytes(), result.read_bytes())


def test_attempt2_restore_uses_inspected_state_not_hard_coded_flags(tmp_path, monkeypatch):
    ps, archive, root, staging, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    chain = ps.verify_production_gate_chain()
    _, manifest, result = ps._inspect_state(chain, root)
    monkeypatch.setattr(ps, "_inspect_state",
                        lambda actual_chain, actual_root: ("CROSSED_PAIR", manifest, result))
    evidence = ps.run_restore_production_source(archive, root)
    assert evidence["failure_reason"] == "INVALID_RECONCILIATION_STATE"
    assert not os.path.lexists(staging) and not os.path.lexists(root)


def test_attempt2_restore_maps_error_code_without_message_token_search(tmp_path, monkeypatch):
    ps, archive, root, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(
        ps, "_require_tree_matches_manifest",
        lambda *_: (_ for _ in ()).throw(EvidenceError(
            "E_PILOT_SOURCE_TREE_MISMATCH",
            "ARCHIVE_UNSAFE FILE_COUNT_MISMATCH EXTRACTION_UNSAFE",
        )),
    )
    assert ps.run_restore_production_source(archive, root)["failure_reason"] == "TREE_HASH_MISMATCH"


@pytest.mark.parametrize(
    ("operation", "expected"),
    [("read_production_archive_bytes", "ARCHIVE_UNSAFE"),
     ("capture_materialized_tree", "EXTRACTION_UNSAFE"),
     ("replace", "EXTRACTION_UNSAFE")],
)
def test_attempt2_restore_maps_operation_local_oserror(tmp_path, monkeypatch, operation, expected):
    ps, archive, root, staging, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    if operation == "replace":
        monkeypatch.setattr(ps.os, operation, lambda *_: (_ for _ in ()).throw(OSError("boom")))
    else:
        monkeypatch.setattr(ps, operation, lambda *_: (_ for _ in ()).throw(OSError("boom")))
    assert ps.run_restore_production_source(archive, root)["failure_reason"] == expected
    assert not os.path.lexists(root)


def test_attempt2_restore_owned_cleanup_failure_returns_failure_evidence(tmp_path, monkeypatch):
    ps, archive, root, staging, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(
        ps,
        "capture_materialized_tree",
        lambda *_: (_ for _ in ()).throw(EvidenceError("E_PILOT_EXTRACT_UNSAFE", "stop")),
    )
    monkeypatch.setattr(ps.shutil, "rmtree",
                        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("cleanup")))
    evidence = ps.run_restore_production_source(archive, root)
    assert ps.validate_source_restoration_evidence(evidence) == evidence
    assert (
        evidence["terminal_status"], evidence["disposition"], evidence["failure_reason"]
    ) == ("FAIL", "NOT_APPLIED", "EXTRACTION_UNSAFE")
    assert (evidence["staging_published"], evidence["root_published"]) == (False, False)
    assert os.path.lexists(staging)


def test_attempt2_restore_extractor_race_preserves_foreign_staging(tmp_path, monkeypatch):
    ps, archive, root, staging, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    foreign_inode = None

    def collide(_snapshot, destination):
        nonlocal foreign_inode
        destination.mkdir()
        (destination / "foreign").write_text("unchanged")
        foreign_inode = destination.stat().st_ino
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "exclusive mkdir collision")

    monkeypatch.setattr(ps, "extract_archive_to_staging", collide)
    evidence = ps.run_restore_production_source(archive, root)
    assert evidence["failure_reason"] == "EXTRACTION_UNSAFE"
    assert staging.stat().st_ino == foreign_inode
    assert (staging / "foreign").read_text() == "unchanged"
    assert not os.path.lexists(root)


def test_attempt2_restore_authority_drift_precedes_publication(tmp_path, monkeypatch):
    ps, archive, root, staging, manifest, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    original_read = ps.read_authority_snapshot
    reads = 0

    def drift_on_reread(path, label):
        nonlocal reads
        reads += 1
        if reads == 1:
            manifest.write_bytes(manifest.read_bytes() + b" ")
        return original_read(path, label)

    monkeypatch.setattr(ps, "read_authority_snapshot", drift_on_reread)
    evidence = ps.run_restore_production_source(archive, root)
    assert evidence["failure_reason"] == "INVALID_PASS_PAIR"
    assert not os.path.lexists(root)
    assert not os.path.lexists(staging)


def test_attempt2_restore_rereads_authority_before_atomic_replace(tmp_path, monkeypatch):
    ps, archive, root, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    original_read = ps.read_authority_snapshot
    original_replace = ps.os.replace
    calls = []

    def ordered_read(path, label):
        calls.append(("read", label))
        return original_read(path, label)

    def ordered_replace(source, destination):
        calls.append(("replace", source, destination))
        return original_replace(source, destination)

    monkeypatch.setattr(ps, "read_authority_snapshot", ordered_read)
    monkeypatch.setattr(ps.os, "replace", ordered_replace)
    assert ps.run_restore_production_source(archive, root)["terminal_status"] == "PASS"
    boundary_calls = [
        call for call in calls
        if call[0] == "replace" or call[1].startswith("source-restoration-")
    ]
    assert boundary_calls == [
        ("read", "source-restoration-manifest"),
        ("read", "source-restoration-result"),
        ("replace", ps.ATTEMPT2_SOURCE_STAGING_ROOT, ps.ATTEMPT2_SOURCE_ROOT),
    ]


def test_attempt2_restore_preserves_preexisting_staging_when_cleanup_not_owned(tmp_path, monkeypatch):
    ps, archive, root, staging, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    staging.mkdir()
    inode = staging.stat().st_ino
    assert ps.run_restore_production_source(archive, root)["failure_reason"] == "STAGING_EXISTS"
    assert staging.stat().st_ino == inode


def _attempt2_source_entry_snapshot(paths):
    """Recursive inode/content snapshot which never follows a symlink."""
    snapshot = {}
    def observe(path):
        if not os.path.lexists(path):
            snapshot[path] = None
            return
        stat = os.lstat(path)
        is_link = path.is_symlink()
        snapshot[path] = (
            stat.st_mode,
            stat.st_ino,
            os.readlink(path) if is_link else path.read_bytes() if path.is_file() else None,
        )
        if path.is_dir() and not is_link:
            for child in sorted(path.iterdir(), key=lambda item: item.name):
                observe(child)

    for path in paths:
        observe(path)
    return snapshot


@pytest.mark.parametrize("state", ["INVALID_PASS_NO_ROOT", "ALREADY_COMPLETE"])
def test_attempt2_source_entry_accepts_only_legal_read_only_states(
    tmp_path, monkeypatch, state
):
    ps, archive, root, staging, manifest, result = _attempt2_fixture(
        tmp_path, monkeypatch
    )
    if state == "ALREADY_COMPLETE":
        snapshot = ps.read_production_archive_bytes(archive)
        ps.extract_archive_to_staging(snapshot, root)
    chain = ps.verify_production_gate_chain()
    original_inspect = ps._inspect_state
    monkeypatch.setattr(
        ps, "_inspect_state", lambda actual_chain, actual_root: (
            (state, *original_inspect(chain, root)[1:])
        )
    )
    watched = [archive, root, staging, manifest, result]
    before = _attempt2_source_entry_snapshot(watched)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("read-only source entry attempted publication")

    for owner, name in (
        (ps.os, "mkdir"), (ps.os, "replace"), (ps.os, "rename"),
        (ps, "write_canonical_json"), (ps, "extract_archive_to_staging"),
    ):
        monkeypatch.setattr(owner, name, forbidden)

    assert ps._inspect_attempt2_source_entry(archive, root) == state
    assert _attempt2_source_entry_snapshot(watched) == before


def test_attempt2_source_entry_rejects_complete_but_drifted_tree_before_intent(
    tmp_path, monkeypatch
):
    ps, archive, root, staging, manifest, result = _attempt2_fixture(
        tmp_path, monkeypatch
    )
    snapshot = ps.read_production_archive_bytes(archive)
    ps.extract_archive_to_staging(snapshot, root)
    changed = root / "x.txt"
    changed.write_bytes(b"drift\n")
    watched = [archive, root, staging, manifest, result]
    before = _attempt2_source_entry_snapshot(watched)
    with pytest.raises(EvidenceError, match="source tree differs"):
        ps._inspect_attempt2_source_entry(archive, root)
    assert _attempt2_source_entry_snapshot(watched) == before


@pytest.mark.parametrize(
    "state",
    [
        "ABSENT", "PASS_NO_ROOT", "PARTIAL_ROOT", "CROSSED_PAIR",
        "ROOT_MISMATCH", "STAGING_PRESENT", "INVALID_PASS_WITH_ROOT",
    ],
)
def test_attempt2_source_entry_rejects_every_other_reconciliation_state(
    tmp_path, monkeypatch, state
):
    ps, archive, root, staging, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    chain = ps.verify_production_gate_chain()
    _, manifest, result = ps._inspect_state(chain, root)
    monkeypatch.setattr(ps, "_inspect_state", lambda *_: (state, manifest, result))
    before = _attempt2_source_entry_snapshot([archive, root, staging])
    with pytest.raises(EvidenceError):
        ps._inspect_attempt2_source_entry(archive, root)
    assert _attempt2_source_entry_snapshot([archive, root, staging]) == before


@pytest.mark.parametrize("drift", ["archive-path", "root-path", "archive-symlink", "staging", "root-symlink", "authority"])
def test_attempt2_source_entry_rejects_path_safety_and_authority_drift(
    tmp_path, monkeypatch, drift
):
    ps, archive, root, staging, *_ = _attempt2_fixture(tmp_path, monkeypatch)
    actual_archive, actual_root = archive, root
    if drift == "archive-path":
        actual_archive = tmp_path / "wrong.tar"
    elif drift == "root-path":
        actual_root = tmp_path / "wrong-root"
    elif drift == "archive-symlink":
        link = tmp_path / "archive-link.tar"
        link.symlink_to(archive)
        monkeypatch.setattr(ps, "ATTEMPT2_ARCHIVE_PATH", link)
        actual_archive = link
    elif drift == "staging":
        staging.mkdir()
    elif drift == "root-symlink":
        root.symlink_to(tmp_path / "missing", target_is_directory=True)
    else:
        monkeypatch.setattr(
            ps, "verify_production_gate_chain",
            lambda: (_ for _ in ()).throw(EvidenceError("E_SYNTHETIC", "bad chain")),
        )
    before = _attempt2_source_entry_snapshot([archive, root, staging])
    with pytest.raises(EvidenceError):
        ps._inspect_attempt2_source_entry(actual_archive, actual_root)
    assert _attempt2_source_entry_snapshot([archive, root, staging]) == before
