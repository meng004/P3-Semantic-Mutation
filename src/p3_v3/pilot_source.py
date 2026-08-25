"""Pilot-only source-preparation capability. Possession is not production authorization."""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import stat
import tarfile
import zipfile
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    read_regular_file_snapshot,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import (
    SourceSnapshot,
    SourceSnapshotEntry,
    canonical_source_tree_sha256,
)

CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH = Path(
    "docs/review_20260817/boost_math_pilot_source_preparation_sol_high_review.md"
)
SOURCE_PREPARATION_PLAN_PATH = Path(
    "docs/superpowers/plans/"
    "2026-08-17-p3-boost-math-pilot-source-preparation-only.md"
)
CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH = Path(
    "docs/review_20260817/"
    "boost_math_pilot_source_preparation_implementation_sol_high_review.md"
)
REVIEWED_PILOT_SOURCE_PATH = Path("src/p3_v3/pilot_source.py")
REVIEWED_PILOT_CLI_PATH = Path("scripts/p3_v3/pilot.py")
REVIEWED_TEST_PILOT_SOURCE_PATH = Path("tests/p3_v3/test_pilot_source.py")
REVIEWED_TEST_PILOT_PATH = Path("tests/p3_v3/test_pilot.py")
SOURCE_PREPARATION_LAUNCH_PATH = Path(
    "data/p3_v3/pilot/boost_math/source-preparation-launch.json"
)
SOURCE_PREPARATION_LAUNCH_PACKET_PATH = Path(
    "docs/review_20260817/boost_math_pilot_source_preparation_launch_packet.md"
)
SOURCE_PREPARATION_LAUNCH_VERDICT_PATH = Path(
    "docs/review_20260817/"
    "boost_math_pilot_source_preparation_launch_sol_high_review.md"
)
AUTHORIZATION_A_PATH = Path("data/p3_v3/pilot/boost_math/user-auth-preparation.txt")
AUTHORIZATION_A_BYTES = b"AUTHORIZE_BOOSTMATH_PILOT_PREPARATION\n"
AUTHORIZATION_A_SHA256 = (
    "502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6"
)
SOURCE_MANIFEST_PATH = Path("data/p3_v3/pilot/boost_math/source-manifest.json")
SOURCE_PREPARATION_RESULT_PATH = Path(
    "data/p3_v3/pilot/boost_math/source-preparation-result.json"
)

P12_ITEM_ID = "C-BOOSTMATH-001"
NEUTRAL_SNAPSHOT_ID = (
    "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886"
)
FROZEN_NORMALIZED_SOURCE_TREE_SHA256 = (
    "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8"
)
ATTEMPT2_ARCHIVE_PATH = Path("/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar")
ATTEMPT2_SOURCE_ROOT = Path("/tmp/p3-boost-math-pilot-production-source")
ATTEMPT2_SOURCE_STAGING_ROOT = Path("/tmp/p3-boost-math-pilot-production-source.staging")
ATTEMPT2_ARCHIVE_SHA256 = "6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392"
ATTEMPT2_ARCHIVE_BYTES = 99676160
ATTEMPT2_FILE_COUNT = 4396
ATTEMPT2_TOTAL_BYTES = 95635487
SOURCE_RESTORATION_SCHEMA = "p3-pilot-source-restoration-evidence-v1"
SOURCE_RESTORATION_FAILURE_REASONS = frozenset({
    "WRONG_ARCHIVE_PATH", "WRONG_SOURCE_ROOT", "ARCHIVE_UNSAFE",
    "ARCHIVE_HASH_MISMATCH", "ARCHIVE_SIZE_MISMATCH", "ARCHIVE_FORMAT_MISMATCH",
    "EXTRACTION_UNSAFE", "STAGING_EXISTS", "STAGING_SYMLINK", "ROOT_SYMLINK",
    "INVALID_RECONCILIATION_STATE", "TREE_HASH_MISMATCH", "FILE_COUNT_MISMATCH",
    "BYTE_COUNT_MISMATCH", "INVALID_PASS_PAIR",
})
SOURCE_RESTORATION_EVIDENCE_EXACT = {
    "schema_version": str, "execution_class": str, "claims": str,
    "disposition": str, "archive_sha256": str, "archive_bytes": int,
    "normalized_tree_sha256": str, "materialized_file_count": int,
    "materialized_total_bytes": int, "staging_published": bool,
    "root_published": bool, "started_at": str, "ended_at": str,
    "terminal_status": str, "failure_reason": (str, type(None)),
    "artifact_sha256": str,
}
CONTROLLED_SUBJECT_SOURCE_ID = (
    "e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7"
)
CONTROLLED_SUBJECT_ID = (
    "89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914"
)
BUILD_DESCRIPTOR_SHA256 = (
    "68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d"
)

SOURCE_PREPARATION_PLAN_VERDICT_EXACT = {
    "reviewed_plan_path": str,
    "reviewed_plan_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}
SOURCE_PREPARATION_CAPABILITY_VERDICT_EXACT = {
    "reviewed_plan_path": str,
    "reviewed_plan_sha256": str,
    "reviewed_plan_verdict_sha256": str,
    "reviewed_commit": str,
    "reviewed_pilot_source_path": str,
    "reviewed_pilot_source_sha256": str,
    "reviewed_pilot_cli_path": str,
    "reviewed_pilot_cli_sha256": str,
    "reviewed_test_pilot_source_path": str,
    "reviewed_test_pilot_source_sha256": str,
    "reviewed_test_pilot_path": str,
    "reviewed_test_pilot_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}
SOURCE_PREPARATION_LAUNCH_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "source_preparation_plan_path": str,
    "source_preparation_plan_sha256": str,
    "source_preparation_plan_verdict_path": str,
    "source_preparation_plan_verdict_sha256": str,
    "capability_implementation_verdict_path": str,
    "capability_implementation_verdict_sha256": str,
    "production_launch_packet_path": str,
    "production_launch_packet_sha256": str,
    "launch_sol_high_verdict_path": str,
    "launch_sol_high_verdict_sha256": str,
    "authorization_a_sha256": str,
    "claims": str,
    "artifact_sha256": str,
}
SOURCE_PREPARATION_LAUNCH_VERDICT_EXACT = {
    "reviewed_packet_path": str,
    "reviewed_packet_sha256": str,
    "plan_verdict_sha256": str,
    "capability_verdict_sha256": str,
    "authorization_a_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}
PILOT_SOURCE_MANIFEST_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "predecessor_sha256": list,
    "archive_sha256": str,
    "archive_bytes": int,
    "archive_format": str,
    "build_descriptor_sha256": str,
    "authorization_a_sha256": str,
    "extractor_policy_sha256": str,
    "materialized_file_count": int,
    "materialized_total_bytes": int,
    "artifact_sha256": str,
}
PILOT_SOURCE_PREPARATION_RESULT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "predecessor_sha256": list,
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "source_manifest_sha256": (str, type(None)),
    "archive_sha256": (str, type(None)),
    "archive_bytes": (int, type(None)),
    "materialized_tree_sha256": (str, type(None)),
    "artifact_sha256": str,
}

AUTHORITY_DEPENDENCY_EDGES = [
    ("source_preparation_plan", "plan_verdict"),
    ("plan_verdict", "capability_verdict"),
    ("capability_verdict", "authorization_a"),
    ("authorization_a", "launch_packet"),
    ("plan_verdict", "launch_packet"),
    ("capability_verdict", "launch_packet"),
    ("launch_packet", "launch_verdict"),
    ("plan_verdict", "launch_verdict"),
    ("capability_verdict", "launch_verdict"),
    ("authorization_a", "launch_verdict"),
    ("source_preparation_plan", "launch_authority"),
    ("plan_verdict", "launch_authority"),
    ("capability_verdict", "launch_authority"),
    ("launch_packet", "launch_authority"),
    ("launch_verdict", "launch_authority"),
    ("authorization_a", "launch_authority"),
    ("launch_authority", "source_manifest"),
    ("authorization_a", "source_manifest"),
    ("source_manifest", "pass_result"),
]
UNIQUE_AUTHORITY_ORDER = [
    "source_preparation_plan",
    "plan_verdict",
    "capability_verdict",
    "authorization_a",
    "launch_packet",
    "launch_verdict",
    "launch_authority",
    "source_manifest",
    "pass_result",
]
PROCESS_ORDER = [
    "G1_FOUNDATION_IMPLEMENTATION_PASS",
    "independent_source_preparation_plan_review",
    "formal_source_preparation_plan_verdict_archival",
    "capability_implementation",
    "independent_capability_implementation_review",
    "formal_capability_implementation_verdict_archival",
    "user_authorization_a",
    "production_launch_packet",
    "independent_launch_packet_review",
    "launch_sol_high_verdict_archival",
    "exclusive_create_source_preparation_launch",
    "production_source_preparation",
    "independent_manifest_result_review",
]
PROCESS_AUTHORITY_PROJECTION = list(UNIQUE_AUTHORITY_ORDER)

EXTRACTOR_POLICY_V1 = {
    "schema_version": "p3-pilot-extractor-policy-v1",
    "accepted_formats": ["TAR", "ZIP"],
    "strip_single_top_level_directory": True,
    "max_member_count": 100000,
    "max_member_bytes": 536870912,
    "max_total_uncompressed_bytes": 4294967296,
    "reject_absolute_paths": True,
    "reject_parent_traversal": True,
    "reject_backslash_paths": True,
    "reject_nul_paths": True,
    "reject_symlinks": True,
    "reject_hardlinks": True,
    "reject_devices": True,
    "reject_fifos": True,
    "reject_sockets": True,
    "reject_duplicate_normalized_paths": True,
    "reject_casefold_collisions": True,
    "reject_target_escape": True,
    "reject_encrypted_zip_members": True,
}
EXTRACTOR_POLICY_SHA256 = (
    "e482ea272a6836099b9dc52deab7d799e24c571c9433fdafe2cff6de48bbb229"
)
_EXTRACTOR_CHUNK = 65536
_CONTEXT_GATE = {
    "plan-verdict": "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
    "capability-verdict": "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
    "launch-verdict": "E_PILOT_SOURCE_PREPARATION_LAUNCH",
    "launch": "E_PILOT_SOURCE_PREPARATION_LAUNCH",
}
RECONCILIATION_STATES = (
    "FRESH",
    "ORPHAN_ROOT",
    "MANIFEST_ONLY",
    "MANIFEST_AND_ROOT",
    "FAILURE_TERMINAL",
    "INVALID_FAILURE_ROOT",
    "INVALID_FAILURE_MANIFEST",
    "INVALID_PASS_NO_MANIFEST",
    "INVALID_PASS_NO_ROOT",
    "ALREADY_COMPLETE",
    "INVALID_CLOSED_PAIR",
    "INVALID_DURABLE_OBJECT",
)


def read_authority_snapshot(path: Path, context: str) -> tuple[bytes, str]:
    try:
        raw, _mode = read_regular_file_snapshot(path, context)
    except EvidenceError as exc:
        if exc.code == "E_AUTHORITY_LOCK_PATH":
            raise EvidenceError(
                "E_PILOT_SOURCE_IDENTITY",
                f"{context} authority snapshot is absent or unsafe",
            ) from exc
        raise
    digest = hashlib.sha256(raw).hexdigest()
    validate_sha256(digest, f"{context}.sha256")
    return raw, digest


def parse_canonical_authority_object(raw: bytes, context: str) -> dict:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise map_gate_error(
            EvidenceError("E_PILOT_SOURCE_IDENTITY", f"{context} is not JSON"),
            _CONTEXT_GATE.get(context, "E_PILOT_SOURCE_IDENTITY"),
        ) from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise map_gate_error(
            EvidenceError(
                "E_PILOT_SOURCE_IDENTITY",
                f"{context} is not one canonical JSON object",
            ),
            _CONTEXT_GATE.get(context, "E_PILOT_SOURCE_IDENTITY"),
        )
    return value


def map_gate_error(exc: EvidenceError, gate_code: str) -> EvidenceError:
    if exc.code in {
        "E_SCHEMA_KEYS",
        "E_SCHEMA_TYPE",
        "E_SHA256",
        "E_CANONICAL_JSON",
        "E_JSON",
        "E_PILOT_SOURCE_IDENTITY",
    }:
        return EvidenceError(gate_code, str(exc))
    return exc


def validate_source_preparation_plan_verdict(
    value: object, markdown_plan_sha256: str
) -> dict:
    try:
        validated = validate_exact_object(
            value,
            SOURCE_PREPARATION_PLAN_VERDICT_EXACT,
            "source-preparation-plan-verdict",
        )
        validate_sha256(
            validated["reviewed_plan_sha256"],
            "source-preparation-plan-verdict.reviewed_plan_sha256",
        )
    except EvidenceError as exc:
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT") from exc
    if validated["reviewed_plan_path"] != SOURCE_PREPARATION_PLAN_PATH.as_posix():
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
            "reviewed plan path differs",
        )
    if validated["reviewed_plan_sha256"] != markdown_plan_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
            "reviewed plan hash differs",
        )
    if validated["verdict"] != "PASS":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
            "verdict is not PASS",
        )
    if validated["authorized_state"] != "PILOT_SOURCE_PREPARATION_PLAN_FROZEN":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
            "authorized_state is not PILOT_SOURCE_PREPARATION_PLAN_FROZEN",
        )
    if validated["claims"] != "blocked":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
            "claims are not blocked",
        )
    return validated


def validate_source_preparation_capability_verdict(
    value: object,
    markdown_plan_sha256: str,
    plan_verdict_sha256: str,
) -> dict:
    try:
        validated = validate_exact_object(
            value,
            SOURCE_PREPARATION_CAPABILITY_VERDICT_EXACT,
            "source-preparation-capability-verdict",
        )
    except EvidenceError as exc:
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT") from exc
    commit = validated["reviewed_commit"]
    if type(commit) is not str or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "reviewed_commit is not 40 lowercase hexadecimal characters",
        )
    expected_paths = {
        "reviewed_plan_path": SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_pilot_source_path": REVIEWED_PILOT_SOURCE_PATH.as_posix(),
        "reviewed_pilot_cli_path": REVIEWED_PILOT_CLI_PATH.as_posix(),
        "reviewed_test_pilot_source_path": REVIEWED_TEST_PILOT_SOURCE_PATH.as_posix(),
        "reviewed_test_pilot_path": REVIEWED_TEST_PILOT_PATH.as_posix(),
    }
    for key, required in expected_paths.items():
        if validated[key] != required:
            raise EvidenceError(
                "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
                f"{key} differs",
            )
    for key in (
        "reviewed_plan_sha256",
        "reviewed_plan_verdict_sha256",
        "reviewed_pilot_source_sha256",
        "reviewed_pilot_cli_sha256",
        "reviewed_test_pilot_source_sha256",
        "reviewed_test_pilot_sha256",
    ):
        try:
            validate_sha256(validated[key], f"capability-verdict.{key}")
        except EvidenceError as exc:
            raise map_gate_error(
                exc, "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
            ) from exc
    if validated["reviewed_plan_sha256"] != markdown_plan_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "reviewed plan hash differs",
        )
    if validated["reviewed_plan_verdict_sha256"] != plan_verdict_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "reviewed plan verdict hash differs",
        )
    if validated["verdict"] != "PASS":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "verdict is not PASS",
        )
    if validated["authorized_state"] != (
        "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS"
    ):
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "authorized_state is not PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        )
    if validated["claims"] != "blocked":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "claims are not blocked",
        )
    return validated


def verify_reviewed_production_bytes(capability_verdict: dict) -> None:
    observed_source, source_digest = read_authority_snapshot(
        REVIEWED_PILOT_SOURCE_PATH, "reviewed-pilot-source"
    )
    observed_cli, cli_digest = read_authority_snapshot(
        REVIEWED_PILOT_CLI_PATH, "reviewed-pilot-cli"
    )
    del observed_source, observed_cli
    if source_digest != capability_verdict["reviewed_pilot_source_sha256"]:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "runtime pilot_source.py bytes differ from the reviewed snapshot",
        )
    if cli_digest != capability_verdict["reviewed_pilot_cli_sha256"]:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "runtime pilot CLI bytes differ from the reviewed snapshot",
        )


def validate_source_preparation_launch(
    value: object,
    *,
    plan_sha256: str,
    plan_verdict_sha256: str,
    capability_verdict_sha256: str,
    launch_packet_sha256: str,
    launch_verdict_sha256: str,
    authorization_a_sha256: str,
) -> dict:
    try:
        validated = validate_exact_object(
            value, SOURCE_PREPARATION_LAUNCH_EXACT, "source-preparation-launch"
        )
    except EvidenceError as exc:
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_LAUNCH") from exc
    if validated["schema_version"] != "p3-pilot-source-preparation-launch-v1":
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "schema differs")
    if validated["execution_class"] != "PILOT_ONLY":
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "class differs")
    if validated["denominator"] != "PILOT_ONLY":
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "denominator differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "claims are not blocked")
    expected = {
        "source_preparation_plan_path": SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "source_preparation_plan_sha256": plan_sha256,
        "source_preparation_plan_verdict_path": (
            CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH.as_posix()
        ),
        "source_preparation_plan_verdict_sha256": plan_verdict_sha256,
        "capability_implementation_verdict_path": (
            CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH.as_posix()
        ),
        "capability_implementation_verdict_sha256": capability_verdict_sha256,
        "production_launch_packet_path": (
            SOURCE_PREPARATION_LAUNCH_PACKET_PATH.as_posix()
        ),
        "production_launch_packet_sha256": launch_packet_sha256,
        "launch_sol_high_verdict_path": (
            SOURCE_PREPARATION_LAUNCH_VERDICT_PATH.as_posix()
        ),
        "launch_sol_high_verdict_sha256": launch_verdict_sha256,
        "authorization_a_sha256": authorization_a_sha256,
    }
    try:
        for key, required in expected.items():
            if key.endswith("_sha256"):
                validate_sha256(validated[key], f"source-preparation-launch.{key}")
            if validated[key] != required:
                raise EvidenceError(
                    "E_PILOT_SOURCE_PREPARATION_LAUNCH",
                    f"{key} differs from the verified snapshot chain",
                )
        body = {key: validated[key] for key in validated if key != "artifact_sha256"}
        if validated["artifact_sha256"] != canonical_sha256(body):
            raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "self-hash differs")
    except EvidenceError as exc:
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_LAUNCH") from exc
    return validated


def validate_source_preparation_launch_verdict(
    value: object,
    *,
    packet_sha256: str,
    plan_verdict_sha256: str,
    capability_verdict_sha256: str,
    authorization_a_sha256: str,
) -> dict:
    try:
        validated = validate_exact_object(
            value,
            SOURCE_PREPARATION_LAUNCH_VERDICT_EXACT,
            "source-preparation-launch-verdict",
        )
    except EvidenceError as exc:
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_LAUNCH") from exc
    if validated["reviewed_packet_path"] != (
        SOURCE_PREPARATION_LAUNCH_PACKET_PATH.as_posix()
    ):
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "packet path differs")
    if validated["reviewed_packet_sha256"] != packet_sha256:
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "packet hash differs")
    if validated["plan_verdict_sha256"] != plan_verdict_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "plan verdict hash differs",
        )
    if validated["capability_verdict_sha256"] != capability_verdict_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "capability verdict hash differs",
        )
    if validated["authorization_a_sha256"] != authorization_a_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "authorization A hash differs",
        )
    if validated["verdict"] != "PASS":
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "verdict is not PASS")
    if validated["authorized_state"] != "PILOT_SOURCE_PREPARATION_LAUNCH_FROZEN":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "authorized_state is not PILOT_SOURCE_PREPARATION_LAUNCH_FROZEN",
        )
    if validated["claims"] != "blocked":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "claims are not blocked",
        )
    if "reviewed_launch_path" in validated or "reviewed_launch_sha256" in validated:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "launch verdict must not cite launch authority",
        )
    return validated


def verify_authorization_a(path: Path = AUTHORIZATION_A_PATH) -> tuple[bytes, str]:
    try:
        raw, digest = read_authority_snapshot(path, "authorization-a")
    except EvidenceError as exc:
        if exc.code == "E_PILOT_SOURCE_IDENTITY":
            raise EvidenceError(
                "E_PILOT_PREPARATION_AUTH_ABSENT",
                "authorization A is absent or unsafe",
            ) from exc
        raise
    if raw != AUTHORIZATION_A_BYTES or digest != AUTHORIZATION_A_SHA256:
        raise EvidenceError(
            "E_PILOT_PREPARATION_AUTH",
            "authorization A bytes or hash differ",
        )
    return raw, digest


def count_topological_authority_orders(
    edges: list[tuple[str, str]],
    limit: int = 2,
) -> int:
    nodes = {node for edge in edges for node in edge}
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    incoming = {node: 0 for node in nodes}
    for start, end in edges:
        outgoing[start].append(end)
        incoming[end] += 1
    found = 0

    def walk(indeg: dict[str, int], ready: list[str], placed: int) -> None:
        nonlocal found
        if found >= limit:
            return
        if placed == len(nodes):
            found += 1
            return
        if not ready:
            raise ValueError("authority dependency graph contains a cycle")
        for index in range(len(ready)):
            if found >= limit:
                return
            node = ready[index]
            next_ready = ready[:index] + ready[index + 1 :]
            next_indeg = dict(indeg)
            for nxt in outgoing[node]:
                next_indeg[nxt] -= 1
                if next_indeg[nxt] == 0:
                    next_ready.append(nxt)
            walk(next_indeg, next_ready, placed + 1)

    start_ready = [node for node, value in incoming.items() if value == 0]
    walk(incoming, start_ready, 0)
    return found


def require_unique_topological_authority_order(
    edges: list[tuple[str, str]],
) -> list[str]:
    nodes = {node for edge in edges for node in edge}
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    incoming = {node: 0 for node in nodes}
    for start, end in edges:
        outgoing[start].append(end)
        incoming[end] += 1
    order: list[str] = []
    remaining = set(nodes)
    while remaining:
        ready = [node for node in remaining if incoming[node] == 0]
        if not ready:
            raise ValueError("authority dependency graph contains a cycle")
        if len(ready) > 1:
            raise ValueError(
                "authority dependency graph has a non-unique topological order"
            )
        node = ready[0]
        order.append(node)
        remaining.remove(node)
        for nxt in outgoing[node]:
            incoming[nxt] -= 1
    if count_topological_authority_orders(edges, limit=2) != 1:
        raise ValueError(
            "authority dependency graph has a non-unique topological order"
        )
    if order != UNIQUE_AUTHORITY_ORDER:
        raise ValueError("unique topological order differs from the frozen sequence")
    return order


def gate_chain_predecessor_sha256(
    plan_sha256: str,
    plan_verdict_sha256: str,
    capability_verdict_sha256: str,
    launch_sha256: str,
    authorization_a_sha256: str,
) -> list[str]:
    return sorted(
        [
            plan_sha256,
            plan_verdict_sha256,
            capability_verdict_sha256,
            launch_sha256,
            authorization_a_sha256,
        ]
    )


@dataclass(frozen=True)
class ArchiveSnapshot:
    raw: bytes
    sha256: str
    size: int
    archive_format: str


def detect_archive_format(raw: bytes) -> str:
    zip_magic = raw.startswith((b"PK\x03\x04", b"PK\x05\x06"))
    tar_magic = len(raw) >= 262 and raw[257:262] == b"ustar"
    if zip_magic and tar_magic:
        raise EvidenceError(
            "E_PILOT_ARCHIVE_FORMAT",
            "archive format is ambiguous",
        )
    if zip_magic:
        return "ZIP"
    if tar_magic:
        return "TAR"
    raise EvidenceError(
        "E_PILOT_ARCHIVE_FORMAT",
        "archive format is unsupported or corrupt",
    )


def read_production_archive_bytes(archive_path: str | Path) -> ArchiveSnapshot:
    path = Path(archive_path)
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise EvidenceError("E_PILOT_ARCHIVE_UNSAFE", "archive cannot be opened") from exc
    try:
        probe = os.fstat(fd)
        if not stat.S_ISREG(probe.st_mode):
            raise EvidenceError(
                "E_PILOT_ARCHIVE_UNSAFE",
                "archive is not a regular file",
            )
        before = os.fstat(fd)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(fd)
        if (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise EvidenceError(
                "E_PILOT_ARCHIVE_UNSAFE",
                "archive identity changed during read",
            )
        raw = b"".join(chunks)
        if len(raw) != before.st_size:
            raise EvidenceError(
                "E_PILOT_ARCHIVE_UNSAFE",
                "archive size differs from st_size",
            )
        digest = hashlib.sha256(raw).hexdigest()
        archive_format = detect_archive_format(raw)
        return ArchiveSnapshot(
            raw=raw,
            sha256=digest,
            size=before.st_size,
            archive_format=archive_format,
        )
    finally:
        os.close(fd)


class StreamedLimitCounter:
    def __init__(self, policy: dict) -> None:
        self.max_member_count = policy["max_member_count"]
        self.max_member_bytes = policy["max_member_bytes"]
        self.max_total_uncompressed_bytes = policy["max_total_uncompressed_bytes"]
        self.member_count = 0
        self.total_bytes = 0
        self._open = False
        self._current_member_bytes = 0

    def begin_member(self) -> None:
        if self._open:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "member is already open")
        prospective_count = self.member_count + 1
        if prospective_count > self.max_member_count:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "member count exceeds policy")
        self.member_count = prospective_count
        self._current_member_bytes = 0
        self._open = True

    def consume_chunk(self, chunk_length: object) -> None:
        if type(chunk_length) is not int or chunk_length < 0:
            raise EvidenceError(
                "E_PILOT_EXTRACT_UNSAFE",
                "chunk length must be a nonnegative int",
            )
        if not self._open:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "no open member")
        prospective_member = self._current_member_bytes + chunk_length
        prospective_total = self.total_bytes + chunk_length
        if prospective_member > self.max_member_bytes:
            raise EvidenceError(
                "E_PILOT_EXTRACT_UNSAFE",
                "streamed member bytes exceed policy",
            )
        if prospective_total > self.max_total_uncompressed_bytes:
            raise EvidenceError(
                "E_PILOT_EXTRACT_UNSAFE",
                "streamed total bytes exceed policy",
            )
        self._current_member_bytes = prospective_member
        self.total_bytes = prospective_total

    def end_member(self) -> None:
        if not self._open:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "no open member")
        self._open = False


def shared_top_level_directory(member_names: list[str]) -> str | None:
    records: list[tuple[str, bool]] = []
    for name in member_names:
        first, separator, remainder = name.partition("/")
        del remainder
        if not first:
            return None
        is_directory_layer = bool(separator) or name.endswith("/")
        records.append((first, is_directory_layer))
    tops = {first for first, _is_directory_layer in records}
    if len(tops) != 1:
        return None
    top = next(iter(tops))
    has_directory_layer = any(
        first == top and is_directory_layer for first, is_directory_layer in records
    )
    has_file_named_top = any(
        first == top and not is_directory_layer for first, is_directory_layer in records
    )
    if has_file_named_top or not has_directory_layer:
        return None
    return top


def _reject_member_name(name: str) -> str:
    if "\x00" in name:
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "NUL in member path")
    if "\\" in name:
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "backslash in member path")
    windows_absolute = len(name) >= 2 and name[0].isalpha() and name[1] == ":"
    if name.startswith("/") or windows_absolute:
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "absolute member path")
    parts = name.split("/")
    if any(part == ".." for part in parts):
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "parent traversal")
    normalized = "/".join(part for part in parts if part not in {"", "."})
    if not normalized:
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "empty member path")
    return normalized


def _safe_staging_dest(staging: Path, relative: str) -> Path:
    dest = Path(staging, *relative.split("/"))
    root = staging.resolve()
    try:
        resolved = dest.resolve()
    except OSError as exc:
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "target escape") from exc
    if resolved != root and root not in resolved.parents:
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "target escape")
    return dest


def _write_streamed_member(
    source, dest: Path, counter: StreamedLimitCounter
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as handle:
        while True:
            chunk = source.read(_EXTRACTOR_CHUNK)
            if not chunk:
                break
            counter.consume_chunk(len(chunk))
            handle.write(chunk)


def _zip_unix_mode(info: zipfile.ZipInfo) -> int:
    return (info.external_attr >> 16) & 0o170000


def extract_archive_to_staging(snapshot: ArchiveSnapshot, staging: Path) -> Path:
    if canonical_sha256(EXTRACTOR_POLICY_V1) != EXTRACTOR_POLICY_SHA256:
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "extractor policy hash differs")
    staging = Path(staging)
    try:
        os.mkdir(staging)
    except FileExistsError as exc:
        raise EvidenceError(
            "E_PILOT_SOURCE_OUTPUT_EXISTS",
            "pre-existing staging must be preserved",
        ) from exc
    except OSError as exc:
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "staging cannot be created") from exc
    counter = StreamedLimitCounter(EXTRACTOR_POLICY_V1)
    try:
        if snapshot.archive_format == "ZIP":
            _extract_zip(snapshot.raw, staging, counter)
        elif snapshot.archive_format == "TAR":
            _extract_tar(snapshot.raw, staging, counter)
        else:
            raise EvidenceError("E_PILOT_ARCHIVE_FORMAT", "archive format is unsupported")
    except EvidenceError:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    except (zipfile.BadZipFile, tarfile.TarError) as exc:
        shutil.rmtree(staging, ignore_errors=True)
        raise EvidenceError("E_PILOT_ARCHIVE_FORMAT", "archive is corrupt") from exc
    except OSError as exc:
        shutil.rmtree(staging, ignore_errors=True)
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "staging write failed") from exc
    return staging


def _collect_and_check_names(names: list[str]) -> tuple[list[str], str | None]:
    normalized: list[str] = []
    seen: set[str] = set()
    folded: set[str] = set()
    for name in names:
        if name.endswith("/"):
            _reject_member_name(name[:-1] + "/dummy")
            continue
        norm = _reject_member_name(name)
        if norm in seen:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "duplicate normalized path")
        fold = norm.casefold()
        if fold in folded:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "casefold collision")
        seen.add(norm)
        folded.add(fold)
        normalized.append(norm)
    strip = (
        shared_top_level_directory(normalized)
        if EXTRACTOR_POLICY_V1["strip_single_top_level_directory"]
        else None
    )
    return normalized, strip


def _stripped_relative(name: str, strip: str | None) -> str:
    if strip and (name == strip or name.startswith(strip + "/")):
        inner = name[len(strip) + 1 :] if name.startswith(strip + "/") else ""
        if not inner:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "stripped path is empty")
        return inner
    return name


def _extract_zip(raw: bytes, staging: Path, counter: StreamedLimitCounter) -> None:
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile as exc:
        raise EvidenceError("E_PILOT_ARCHIVE_FORMAT", "corrupt zip") from exc
    names = [info.filename for info in archive.infolist()]
    _collect_and_check_names(names)
    file_names = [name for name in names if not name.endswith("/")]
    _normalized, strip = _collect_and_check_names(file_names)
    del _normalized
    for info in archive.infolist():
        if info.flag_bits & 0x1:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "encrypted zip member")
        mode = _zip_unix_mode(info)
        if mode == 0o120000:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "zip symlink")
        if mode in {0o060000, 0o020000, 0o010000, 0o140000}:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "zip special node")
        if info.filename.endswith("/"):
            continue
        relative = _stripped_relative(_reject_member_name(info.filename), strip)
        dest = _safe_staging_dest(staging, relative)
        counter.begin_member()
        with archive.open(info, "r") as source:
            _write_streamed_member(source, dest, counter)
        counter.end_member()


def _extract_tar(raw: bytes, staging: Path, counter: StreamedLimitCounter) -> None:
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            file_names = [
                member.name
                for member in members
                if member.isfile() or (not member.isdir() and member.size >= 0)
            ]
            _collect_and_check_names(names)
            _normalized, strip = _collect_and_check_names(
                [name for name in file_names if not name.endswith("/")]
            )
            del _normalized
            for member in members:
                if member.issym() or member.type == tarfile.SYMTYPE:
                    raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "tar symlink")
                if member.islnk() or member.type == tarfile.LNKTYPE:
                    raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "tar hardlink")
                if (
                    member.ischr()
                    or member.isblk()
                    or member.isfifo()
                    or member.type in {tarfile.CHRTYPE, tarfile.BLKTYPE, tarfile.FIFOTYPE}
                ):
                    raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "tar special node")
                if member.type not in {tarfile.REGTYPE, tarfile.AREGTYPE, tarfile.DIRTYPE}:
                    raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "tar unsupported member")
                if member.isdir():
                    continue
                relative = _stripped_relative(_reject_member_name(member.name), strip)
                dest = _safe_staging_dest(staging, relative)
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "tar member has no content")
                counter.begin_member()
                with extracted:
                    _write_streamed_member(extracted, dest, counter)
                counter.end_member()
    except tarfile.TarError as exc:
        raise EvidenceError("E_PILOT_ARCHIVE_FORMAT", "corrupt tar") from exc


def _projected_mode(mode: int) -> str:
    if mode & 0o111:
        return "100755"
    return "100644"


def capture_materialized_tree(payload_root: Path) -> SourceSnapshot:
    entries: list[SourceSnapshotEntry] = []
    for dirpath, dirnames, filenames in os.walk(payload_root, followlinks=False):
        for name in list(dirnames) + list(filenames):
            full = Path(dirpath) / name
            info = os.lstat(full)
            if stat.S_ISLNK(info.st_mode) or not (
                stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)
            ):
                raise EvidenceError(
                    "E_PILOT_EXTRACT_UNSAFE",
                    f"materialized node is not a regular file or directory: {full}",
                )
            if stat.S_ISDIR(info.st_mode):
                continue
            relative = full.relative_to(payload_root).as_posix()
            raw, raw_mode = read_regular_file_snapshot(full, "materialized-source")
            entries.append(
                SourceSnapshotEntry(
                    relative_path=relative,
                    mode=_projected_mode(raw_mode),
                    sha256=hashlib.sha256(raw).hexdigest(),
                    content=raw,
                )
            )
    entries.sort(key=lambda item: item.relative_path.encode("utf-8"))
    return SourceSnapshot(entries=tuple(entries))


def validate_materialized_tree_with_phase1(snapshot: SourceSnapshot) -> str:
    if type(snapshot) is not SourceSnapshot:
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "snapshot type differs")
    observed = canonical_source_tree_sha256(snapshot)
    if observed != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_TREE_MISMATCH",
            observed,
        )
    return observed


def classify_reconciliation(
    *,
    manifest_present: bool,
    result_present: bool,
    root_present: bool,
    manifest_valid: bool,
    result_valid: bool,
    result_status: str | None,
    closed_pair_consistent: bool,
) -> str:
    if manifest_present and not manifest_valid:
        return "INVALID_DURABLE_OBJECT"
    if result_present and not result_valid:
        return "INVALID_DURABLE_OBJECT"
    if not manifest_present and not result_present and not root_present:
        return "FRESH"
    if not manifest_present and not result_present and root_present:
        return "ORPHAN_ROOT"
    if manifest_present and not result_present and not root_present:
        return "MANIFEST_ONLY"
    if manifest_present and not result_present and root_present:
        return "MANIFEST_AND_ROOT"
    if (
        not manifest_present
        and result_present
        and result_status == "FAIL_INFRASTRUCTURE"
    ):
        if root_present:
            return "INVALID_FAILURE_ROOT"
        return "FAILURE_TERMINAL"
    if manifest_present and result_present and result_status == "FAIL_INFRASTRUCTURE":
        return "INVALID_FAILURE_MANIFEST"
    if not manifest_present and result_present and result_status == "PASS":
        return "INVALID_PASS_NO_MANIFEST"
    if (
        manifest_present
        and result_present
        and result_status == "PASS"
        and not root_present
    ):
        return "INVALID_PASS_NO_ROOT"
    if manifest_present and result_present and result_status == "PASS" and root_present:
        if closed_pair_consistent:
            return "ALREADY_COMPLETE"
        return "INVALID_CLOSED_PAIR"
    raise AssertionError("unclassified reconciliation combination")


def enumerate_reconciliation_cases() -> list[tuple]:
    cases: list[tuple] = []
    for manifest_present in (False, True):
        for result_present in (False, True):
            for root_present in (False, True):
                manifest_valids = (True,) if not manifest_present else (True, False)
                result_valids = (True,) if not result_present else (True, False)
                if not result_present:
                    result_statuses = (None,)
                else:
                    result_statuses = ("FAIL_INFRASTRUCTURE", "PASS")
                for manifest_valid in manifest_valids:
                    for result_valid in result_valids:
                        for result_status in result_statuses:
                            need_pair = (
                                manifest_present
                                and result_present
                                and root_present
                                and manifest_valid
                                and result_valid
                                and result_status == "PASS"
                            )
                            consistents = (True, False) if need_pair else (True,)
                            for closed_pair_consistent in consistents:
                                state = classify_reconciliation(
                                    manifest_present=manifest_present,
                                    result_present=result_present,
                                    root_present=root_present,
                                    manifest_valid=manifest_valid,
                                    result_valid=result_valid,
                                    result_status=result_status,
                                    closed_pair_consistent=closed_pair_consistent,
                                )
                                cases.append(
                                    (
                                        manifest_present,
                                        result_present,
                                        root_present,
                                        manifest_valid,
                                        result_valid,
                                        result_status,
                                        closed_pair_consistent,
                                        state,
                                    )
                                )
    return cases


def _require_subject_literals(value: dict, context: str) -> None:
    expected = {
        "p12_item_id": P12_ITEM_ID,
        "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
        "controlled_subject_id": CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
    }
    for key, required in expected.items():
        if value[key] != required:
            raise EvidenceError("E_PILOT_SOURCE_IDENTITY", f"{context}.{key} differs")


def validate_pilot_source_manifest(
    value: object,
    *,
    expected_predecessors: list[str] | None = None,
) -> dict:
    validated = validate_exact_object(
        value, PILOT_SOURCE_MANIFEST_EXACT, "p3-pilot-source-manifest-v1"
    )
    if validated["schema_version"] != "p3-pilot-source-manifest-v1":
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "schema differs")
    if validated["execution_class"] != "PILOT_ONLY":
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "class differs")
    if validated["denominator"] != "PILOT_ONLY":
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "denominator differs")
    _require_subject_literals(validated, "source-manifest")
    if validated["archive_format"] not in {"ZIP", "TAR"}:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "archive format differs")
    if validated["authorization_a_sha256"] != AUTHORIZATION_A_SHA256:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "authorization A hash differs")
    if validated["extractor_policy_sha256"] != EXTRACTOR_POLICY_SHA256:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "extractor policy hash differs")
    if validated["build_descriptor_sha256"] != BUILD_DESCRIPTOR_SHA256:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "build descriptor hash differs")
    for key in (
        "normalized_source_tree_sha256",
        "archive_sha256",
        "authorization_a_sha256",
        "extractor_policy_sha256",
        "build_descriptor_sha256",
        "artifact_sha256",
        "neutral_snapshot_id",
        "controlled_subject_id",
        "controlled_subject_source_id",
    ):
        validate_sha256(validated[key], f"source-manifest.{key}")
    if type(validated["archive_bytes"]) is not int or validated["archive_bytes"] <= 0:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "archive_bytes is invalid")
    if (
        type(validated["materialized_file_count"]) is not int
        or validated["materialized_file_count"] <= 0
    ):
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "file count is invalid")
    if (
        type(validated["materialized_total_bytes"]) is not int
        or validated["materialized_total_bytes"] < 0
    ):
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "total bytes are invalid")
    if type(validated["predecessor_sha256"]) is not list:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "predecessors are invalid")
    for item in validated["predecessor_sha256"]:
        validate_sha256(item, "source-manifest.predecessor_sha256")
    if expected_predecessors is not None and validated["predecessor_sha256"] != list(
        expected_predecessors
    ):
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "predecessors differ")
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "self-hash differs")
    return validated


def validate_pilot_source_preparation_result(
    value: object,
    *,
    expected_predecessors: list[str] | None = None,
) -> dict:
    validated = validate_exact_object(
        value,
        PILOT_SOURCE_PREPARATION_RESULT_EXACT,
        "p3-pilot-source-preparation-result-v1",
    )
    if validated["schema_version"] != "p3-pilot-source-preparation-result-v1":
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "schema differs")
    if validated["execution_class"] != "PILOT_ONLY":
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "class differs")
    if validated["denominator"] != "PILOT_ONLY":
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "denominator differs")
    _require_subject_literals(validated, "source-preparation-result")
    if validated["terminal_status"] not in {"PASS", "FAIL_INFRASTRUCTURE"}:
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "terminal status differs")
    for key in (
        "normalized_source_tree_sha256",
        "neutral_snapshot_id",
        "controlled_subject_id",
        "controlled_subject_source_id",
        "artifact_sha256",
    ):
        validate_sha256(validated[key], f"source-preparation-result.{key}")
    for key in (
        "source_manifest_sha256",
        "archive_sha256",
        "materialized_tree_sha256",
    ):
        if validated[key] is not None:
            validate_sha256(validated[key], f"source-preparation-result.{key}")
    if validated["archive_bytes"] is not None and type(validated["archive_bytes"]) is not int:
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "archive_bytes is invalid")
    if type(validated["predecessor_sha256"]) is not list:
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "predecessors are invalid")
    for item in validated["predecessor_sha256"]:
        validate_sha256(item, "source-preparation-result.predecessor_sha256")
    if expected_predecessors is not None and validated["predecessor_sha256"] != list(
        expected_predecessors
    ):
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "predecessors differ")
    if validated["terminal_status"] == "PASS":
        if validated["failure_reason"] is not None:
            raise EvidenceError("E_PILOT_SOURCE_RESULT", "PASS must not carry a failure")
        if validated["source_manifest_sha256"] is None:
            raise EvidenceError("E_PILOT_SOURCE_RESULT", "PASS must bind the source manifest")
        if (
            validated["archive_sha256"] is None
            or validated["archive_bytes"] is None
            or validated["materialized_tree_sha256"] is None
        ):
            raise EvidenceError("E_PILOT_SOURCE_RESULT", "PASS archive fields are incomplete")
        if validated["materialized_tree_sha256"] != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
            raise EvidenceError("E_PILOT_SOURCE_RESULT", "PASS tree hash differs")
    else:
        if not validated["failure_reason"]:
            raise EvidenceError("E_PILOT_SOURCE_RESULT", "FAIL must carry a reason")
        if validated["source_manifest_sha256"] is not None:
            raise EvidenceError("E_PILOT_SOURCE_RESULT", "FAIL must not claim a manifest")
        _validate_fail_evidence_matrix(validated)
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "self-hash differs")
    return validated


_FAIL_REASONS = {
    "ARCHIVE_UNSAFE",
    "ARCHIVE_FORMAT_UNSUPPORTED",
    "EXTRACTION_UNSAFE",
    "SOURCE_TREE_MISMATCH",
}


def _archive_pair_state(archive_sha256: object, archive_bytes: object) -> str:
    if archive_sha256 is None and archive_bytes is None:
        return "none"
    if archive_sha256 is not None and type(archive_bytes) is int:
        return "both"
    return "half"


def _validate_fail_evidence_matrix(validated: dict) -> None:
    reason = validated["failure_reason"]
    if reason not in _FAIL_REASONS:
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "unknown failure_reason")
    pair = _archive_pair_state(validated["archive_sha256"], validated["archive_bytes"])
    tree = validated["materialized_tree_sha256"]
    if reason == "ARCHIVE_UNSAFE" and (pair != "none" or tree is not None):
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "ARCHIVE_UNSAFE evidence differs")
    if reason == "ARCHIVE_FORMAT_UNSUPPORTED" and (pair == "half" or tree is not None):
        raise EvidenceError(
            "E_PILOT_SOURCE_RESULT",
            "ARCHIVE_FORMAT_UNSUPPORTED evidence differs",
        )
    if reason == "EXTRACTION_UNSAFE" and (pair != "both" or tree is not None):
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "EXTRACTION_UNSAFE evidence differs")
    if reason == "SOURCE_TREE_MISMATCH" and (pair != "both" or tree is None):
        raise EvidenceError(
            "E_PILOT_SOURCE_RESULT",
            "SOURCE_TREE_MISMATCH evidence differs",
        )


@dataclass(frozen=True)
class _GateChain:
    plan_sha256: str
    plan_verdict_sha256: str
    capability_verdict_sha256: str
    authorization_a_sha256: str
    launch_packet_sha256: str
    launch_verdict_sha256: str
    launch_sha256: str

    def predecessors(self) -> list[str]:
        return gate_chain_predecessor_sha256(
            self.plan_sha256,
            self.plan_verdict_sha256,
            self.capability_verdict_sha256,
            self.launch_sha256,
            self.authorization_a_sha256,
        )


def _snapshot_or_absent(path: Path, context: str, absent_code: str) -> tuple[bytes, str]:
    try:
        return read_authority_snapshot(path, context)
    except EvidenceError as exc:
        if exc.code == "E_PILOT_SOURCE_IDENTITY":
            raise EvidenceError(absent_code, f"{context} is absent or unsafe") from exc
        raise


def verify_production_gate_chain() -> _GateChain:
    require_unique_topological_authority_order(AUTHORITY_DEPENDENCY_EDGES)
    _plan_raw, plan_sha256 = read_authority_snapshot(
        SOURCE_PREPARATION_PLAN_PATH, "source-preparation-plan"
    )
    del _plan_raw
    plan_verdict_raw, plan_verdict_sha256 = _snapshot_or_absent(
        CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH,
        "plan-verdict",
        "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT_ABSENT",
    )
    try:
        validate_source_preparation_plan_verdict(
            parse_canonical_authority_object(plan_verdict_raw, "plan-verdict"),
            plan_sha256,
        )
    except EvidenceError as exc:
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT") from exc
    capability_raw, capability_sha256 = _snapshot_or_absent(
        CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH,
        "capability-verdict",
        "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT_ABSENT",
    )
    try:
        capability = validate_source_preparation_capability_verdict(
            parse_canonical_authority_object(capability_raw, "capability-verdict"),
            plan_sha256,
            plan_verdict_sha256,
        )
        verify_reviewed_production_bytes(capability)
    except EvidenceError as exc:
        if exc.code == "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT_ABSENT":
            raise
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT") from exc
    _auth_raw, authorization_a_sha256 = verify_authorization_a(AUTHORIZATION_A_PATH)
    del _auth_raw
    packet_raw, launch_packet_sha256 = _snapshot_or_absent(
        SOURCE_PREPARATION_LAUNCH_PACKET_PATH,
        "launch-packet",
        "E_PILOT_SOURCE_PREPARATION_LAUNCH_ABSENT",
    )
    del packet_raw
    launch_verdict_raw, launch_verdict_sha256 = _snapshot_or_absent(
        SOURCE_PREPARATION_LAUNCH_VERDICT_PATH,
        "launch-verdict",
        "E_PILOT_SOURCE_PREPARATION_LAUNCH_ABSENT",
    )
    try:
        validate_source_preparation_launch_verdict(
            parse_canonical_authority_object(launch_verdict_raw, "launch-verdict"),
            packet_sha256=launch_packet_sha256,
            plan_verdict_sha256=plan_verdict_sha256,
            capability_verdict_sha256=capability_sha256,
            authorization_a_sha256=authorization_a_sha256,
        )
    except EvidenceError as exc:
        if exc.code == "E_PILOT_SOURCE_PREPARATION_LAUNCH_ABSENT":
            raise
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_LAUNCH") from exc
    launch_raw, launch_sha256 = _snapshot_or_absent(
        SOURCE_PREPARATION_LAUNCH_PATH,
        "launch",
        "E_PILOT_SOURCE_PREPARATION_LAUNCH_ABSENT",
    )
    try:
        validate_source_preparation_launch(
            parse_canonical_authority_object(launch_raw, "launch"),
            plan_sha256=plan_sha256,
            plan_verdict_sha256=plan_verdict_sha256,
            capability_verdict_sha256=capability_sha256,
            launch_packet_sha256=launch_packet_sha256,
            launch_verdict_sha256=launch_verdict_sha256,
            authorization_a_sha256=authorization_a_sha256,
        )
    except EvidenceError as exc:
        if exc.code == "E_PILOT_SOURCE_PREPARATION_LAUNCH_ABSENT":
            raise
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_LAUNCH") from exc
    return _GateChain(
        plan_sha256=plan_sha256,
        plan_verdict_sha256=plan_verdict_sha256,
        capability_verdict_sha256=capability_sha256,
        authorization_a_sha256=authorization_a_sha256,
        launch_packet_sha256=launch_packet_sha256,
        launch_verdict_sha256=launch_verdict_sha256,
        launch_sha256=launch_sha256,
    )


@dataclass(frozen=True)
class _DurableSnapshot:
    present: bool
    valid: bool
    value: dict | None
    digest: str | None
    raw: bytes | None
    status: str | None


def _absent_durable() -> _DurableSnapshot:
    return _DurableSnapshot(
        present=False,
        valid=True,
        value=None,
        digest=None,
        raw=None,
        status=None,
    )


def _load_manifest_snapshot(chain: _GateChain) -> _DurableSnapshot:
    path = Path(SOURCE_MANIFEST_PATH)
    if not path.exists():
        return _absent_durable()
    raw, digest = read_authority_snapshot(path, "source-manifest")
    try:
        value = parse_canonical_authority_object(raw, "source-manifest")
        validated = validate_pilot_source_manifest(
            value, expected_predecessors=chain.predecessors()
        )
    except EvidenceError as exc:
        if exc.code == "E_PILOT_SOURCE_MANIFEST":
            raise
        raise EvidenceError(
            "E_PILOT_SOURCE_OUTPUT_EXISTS",
            "invalid durable source manifest",
        ) from exc
    return _DurableSnapshot(
        present=True,
        valid=True,
        value=validated,
        digest=digest,
        raw=raw,
        status=None,
    )


def _load_result_snapshot(
    chain: _GateChain, manifest: _DurableSnapshot
) -> _DurableSnapshot:
    path = Path(SOURCE_PREPARATION_RESULT_PATH)
    if not path.exists():
        return _absent_durable()
    raw, digest = read_authority_snapshot(path, "source-preparation-result")
    try:
        value = parse_canonical_authority_object(raw, "source-preparation-result")
        status = value.get("terminal_status") if isinstance(value, dict) else None
        if status == "PASS":
            if not manifest.present or manifest.digest is None:
                expected = None
            else:
                expected = sorted([*chain.predecessors(), manifest.digest])
        else:
            expected = chain.predecessors()
        validated = validate_pilot_source_preparation_result(
            value, expected_predecessors=expected
        )
    except EvidenceError as exc:
        if exc.code == "E_PILOT_SOURCE_RESULT":
            raise
        raise EvidenceError(
            "E_PILOT_SOURCE_OUTPUT_EXISTS",
            "invalid durable source-preparation result",
        ) from exc
    return _DurableSnapshot(
        present=True,
        valid=True,
        value=validated,
        digest=digest,
        raw=raw,
        status=validated["terminal_status"],
    )


def _inspect_state(
    chain: _GateChain, materialize_root: Path
) -> tuple[str, _DurableSnapshot, _DurableSnapshot]:
    manifest = _load_manifest_snapshot(chain)
    result = _load_result_snapshot(chain, manifest)
    root_present = Path(materialize_root).exists()
    closed = True
    if (
        manifest.present
        and result.present
        and root_present
        and manifest.valid
        and result.valid
        and result.status == "PASS"
        and manifest.value is not None
        and result.value is not None
    ):
        closed = result.value["source_manifest_sha256"] == manifest.digest
    state = classify_reconciliation(
        manifest_present=manifest.present,
        result_present=result.present,
        root_present=root_present,
        manifest_valid=manifest.valid,
        result_valid=result.valid,
        result_status=result.status,
        closed_pair_consistent=closed,
    )
    return state, manifest, result


def _finish_artifact(value: dict) -> dict:
    body = {key: value[key] for key in value if key != "artifact_sha256"}
    value["artifact_sha256"] = canonical_sha256(body)
    return value


def _write_fail_result(
    chain: _GateChain,
    reason: str,
    snapshot: ArchiveSnapshot | None,
    tree_hash: str | None,
) -> None:
    archive_sha256 = None
    archive_bytes = None
    if reason == "ARCHIVE_UNSAFE":
        archive_sha256 = None
        archive_bytes = None
        tree_hash = None
    elif reason == "ARCHIVE_FORMAT_UNSUPPORTED":
        if snapshot is not None:
            archive_sha256 = snapshot.sha256
            archive_bytes = snapshot.size
        tree_hash = None
    elif reason == "EXTRACTION_UNSAFE":
        if snapshot is None:
            raise EvidenceError("E_PILOT_SOURCE_RESULT", "extraction fail lacks snapshot")
        archive_sha256 = snapshot.sha256
        archive_bytes = snapshot.size
        tree_hash = None
    elif reason == "SOURCE_TREE_MISMATCH":
        if snapshot is None or tree_hash is None:
            raise EvidenceError("E_PILOT_SOURCE_RESULT", "tree mismatch lacks evidence")
        archive_sha256 = snapshot.sha256
        archive_bytes = snapshot.size
    result = _finish_artifact(
        {
            "schema_version": "p3-pilot-source-preparation-result-v1",
            "execution_class": "PILOT_ONLY",
            "denominator": "PILOT_ONLY",
            "p12_item_id": P12_ITEM_ID,
            "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
            "normalized_source_tree_sha256": FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
            "controlled_subject_id": CONTROLLED_SUBJECT_ID,
            "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
            "predecessor_sha256": chain.predecessors(),
            "terminal_status": "FAIL_INFRASTRUCTURE",
            "failure_reason": reason,
            "source_manifest_sha256": None,
            "archive_sha256": archive_sha256,
            "archive_bytes": archive_bytes,
            "materialized_tree_sha256": tree_hash,
            "artifact_sha256": "",
        }
    )
    validate_pilot_source_preparation_result(result)
    write_canonical_json(SOURCE_PREPARATION_RESULT_PATH, result, exclusive=True)


def _tree_metrics(tree: SourceSnapshot) -> tuple[int, int]:
    return len(tree.entries), sum(len(entry.content) for entry in tree.entries)


def _require_tree_matches_manifest(tree: SourceSnapshot, tree_hash: str, manifest: dict) -> None:
    file_count, total_bytes = _tree_metrics(tree)
    if tree_hash != manifest["normalized_source_tree_sha256"]:
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", tree_hash)
    if file_count != manifest["materialized_file_count"]:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "materialized file count differs")
    if total_bytes != manifest["materialized_total_bytes"]:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "materialized total bytes differ")


def _pass_result_object(
    chain: _GateChain,
    snapshot: ArchiveSnapshot,
    tree_hash: str,
    manifest_sha256: str,
) -> dict:
    predecessors = sorted([*chain.predecessors(), manifest_sha256])
    result = _finish_artifact(
        {
            "schema_version": "p3-pilot-source-preparation-result-v1",
            "execution_class": "PILOT_ONLY",
            "denominator": "PILOT_ONLY",
            "p12_item_id": P12_ITEM_ID,
            "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
            "normalized_source_tree_sha256": FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
            "controlled_subject_id": CONTROLLED_SUBJECT_ID,
            "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
            "predecessor_sha256": predecessors,
            "terminal_status": "PASS",
            "failure_reason": None,
            "source_manifest_sha256": manifest_sha256,
            "archive_sha256": snapshot.sha256,
            "archive_bytes": snapshot.size,
            "materialized_tree_sha256": tree_hash,
            "artifact_sha256": "",
        }
    )
    validate_pilot_source_preparation_result(
        result, expected_predecessors=predecessors
    )
    return result


def _publish_pass(
    chain: _GateChain,
    snapshot: ArchiveSnapshot,
    tree: SourceSnapshot,
    tree_hash: str,
    materialize_root: Path,
    staging: Path,
) -> None:
    predecessors = chain.predecessors()
    manifest = _finish_artifact(
        {
            "schema_version": "p3-pilot-source-manifest-v1",
            "execution_class": "PILOT_ONLY",
            "denominator": "PILOT_ONLY",
            "p12_item_id": P12_ITEM_ID,
            "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
            "normalized_source_tree_sha256": tree_hash,
            "controlled_subject_id": CONTROLLED_SUBJECT_ID,
            "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
            "predecessor_sha256": predecessors,
            "archive_sha256": snapshot.sha256,
            "archive_bytes": snapshot.size,
            "archive_format": snapshot.archive_format,
            "build_descriptor_sha256": BUILD_DESCRIPTOR_SHA256,
            "authorization_a_sha256": chain.authorization_a_sha256,
            "extractor_policy_sha256": EXTRACTOR_POLICY_SHA256,
            "materialized_file_count": len(tree.entries),
            "materialized_total_bytes": sum(len(entry.content) for entry in tree.entries),
            "artifact_sha256": "",
        }
    )
    validate_pilot_source_manifest(manifest, expected_predecessors=predecessors)
    manifest_bytes = canonical_json_bytes(manifest)
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    result = _pass_result_object(chain, snapshot, tree_hash, manifest_sha256)
    write_canonical_json(SOURCE_MANIFEST_PATH, manifest, exclusive=True)
    os.replace(staging, materialize_root)
    write_canonical_json(SOURCE_PREPARATION_RESULT_PATH, result, exclusive=True)


def _staging_path(materialize_root: Path) -> Path:
    return Path(str(Path(materialize_root)) + ".staging")


def _staging_lexists(staging: Path) -> bool:
    try:
        os.lstat(staging)
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "staging cannot be inspected") from exc
    return True


def _reject_preexisting_staging(staging: Path) -> None:
    if _staging_lexists(staging):
        raise EvidenceError(
            "E_PILOT_SOURCE_OUTPUT_EXISTS",
            "pre-existing staging must be preserved",
        )


def _require_safe_residue_staging(staging: Path) -> None:
    try:
        info = os.lstat(staging)
    except OSError as exc:
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "staging cannot be inspected") from exc
    if stat.S_ISLNK(info.st_mode):
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "staging is a symlink")
    if not stat.S_ISDIR(info.st_mode):
        raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "staging is not a directory")


def _fresh_prepare(archive: Path, materialize_root: Path, chain: _GateChain) -> None:
    staging = _staging_path(materialize_root)
    _reject_preexisting_staging(staging)
    snapshot: ArchiveSnapshot | None = None
    owned_staging = False
    try:
        snapshot = read_production_archive_bytes(archive)
    except EvidenceError as exc:
        if exc.code == "E_PILOT_ARCHIVE_UNSAFE":
            _write_fail_result(chain, "ARCHIVE_UNSAFE", None, None)
        elif exc.code == "E_PILOT_ARCHIVE_FORMAT":
            _write_fail_result(chain, "ARCHIVE_FORMAT_UNSUPPORTED", snapshot, None)
        raise
    try:
        extract_archive_to_staging(snapshot, staging)
        owned_staging = True
        tree = capture_materialized_tree(staging)
        try:
            tree_hash = validate_materialized_tree_with_phase1(tree)
        except EvidenceError as exc:
            if exc.code == "E_PILOT_SOURCE_TREE_MISMATCH":
                if owned_staging:
                    shutil.rmtree(staging, ignore_errors=True)
                _write_fail_result(
                    chain,
                    "SOURCE_TREE_MISMATCH",
                    snapshot,
                    str(exc)[len(exc.code) + 2 :],
                )
            raise
        _publish_pass(chain, snapshot, tree, tree_hash, Path(materialize_root), staging)
    except EvidenceError as exc:
        if exc.code == "E_PILOT_EXTRACT_UNSAFE":
            if owned_staging:
                shutil.rmtree(staging, ignore_errors=True)
            _write_fail_result(chain, "EXTRACTION_UNSAFE", snapshot, None)
        elif exc.code == "E_PILOT_ARCHIVE_FORMAT":
            if owned_staging:
                shutil.rmtree(staging, ignore_errors=True)
            _write_fail_result(chain, "ARCHIVE_FORMAT_UNSUPPORTED", snapshot, None)
        raise


def _require_matching_archive(archive: Path, manifest: dict) -> ArchiveSnapshot:
    snapshot = read_production_archive_bytes(archive)
    if (
        snapshot.sha256 != manifest["archive_sha256"]
        or snapshot.size != manifest["archive_bytes"]
        or snapshot.archive_format != manifest["archive_format"]
    ):
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "archive snapshot differs")
    return snapshot


def _recover_manifest_only(
    archive: Path,
    materialize_root: Path,
    chain: _GateChain,
    manifest_snap: _DurableSnapshot,
) -> None:
    if manifest_snap.value is None or manifest_snap.digest is None:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "manifest snapshot is absent")
    staging = _staging_path(materialize_root)
    if _staging_lexists(staging):
        _require_safe_residue_staging(staging)
        snapshot = _require_matching_archive(archive, manifest_snap.value)
        tree = capture_materialized_tree(staging)
        tree_hash = validate_materialized_tree_with_phase1(tree)
        _require_tree_matches_manifest(tree, tree_hash, manifest_snap.value)
        result = _pass_result_object(chain, snapshot, tree_hash, manifest_snap.digest)
        os.replace(staging, materialize_root)
        write_canonical_json(SOURCE_PREPARATION_RESULT_PATH, result, exclusive=True)
        return
    snapshot = _require_matching_archive(archive, manifest_snap.value)
    extract_archive_to_staging(snapshot, staging)
    try:
        tree = capture_materialized_tree(staging)
        tree_hash = validate_materialized_tree_with_phase1(tree)
        _require_tree_matches_manifest(tree, tree_hash, manifest_snap.value)
        result = _pass_result_object(chain, snapshot, tree_hash, manifest_snap.digest)
        os.replace(staging, materialize_root)
        write_canonical_json(SOURCE_PREPARATION_RESULT_PATH, result, exclusive=True)
    except EvidenceError:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def _recover_manifest_and_root(
    archive: Path,
    materialize_root: Path,
    chain: _GateChain,
    manifest_snap: _DurableSnapshot,
) -> None:
    if manifest_snap.value is None or manifest_snap.digest is None:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "manifest snapshot is absent")
    snapshot = _require_matching_archive(archive, manifest_snap.value)
    tree = capture_materialized_tree(Path(materialize_root))
    tree_hash = validate_materialized_tree_with_phase1(tree)
    _require_tree_matches_manifest(tree, tree_hash, manifest_snap.value)
    result = _pass_result_object(chain, snapshot, tree_hash, manifest_snap.digest)
    write_canonical_json(SOURCE_PREPARATION_RESULT_PATH, result, exclusive=True)


def _revalidate_already_complete(
    archive: Path,
    materialize_root: Path,
    chain: _GateChain,
    manifest_snap: _DurableSnapshot,
    result_snap: _DurableSnapshot,
) -> None:
    if manifest_snap.value is None or manifest_snap.digest is None:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "manifest snapshot is absent")
    if result_snap.value is None:
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "result snapshot is absent")
    if manifest_snap.value["predecessor_sha256"] != chain.predecessors():
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "predecessors differ")
    expected = sorted([*chain.predecessors(), manifest_snap.digest])
    if result_snap.value["predecessor_sha256"] != expected:
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "predecessors differ")
    if result_snap.value["source_manifest_sha256"] != manifest_snap.digest:
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "PASS must bind the source manifest")
    snapshot = _require_matching_archive(archive, manifest_snap.value)
    if (
        result_snap.value["archive_sha256"] != snapshot.sha256
        or result_snap.value["archive_bytes"] != snapshot.size
    ):
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "PASS archive fields differ")
    tree = capture_materialized_tree(Path(materialize_root))
    tree_hash = validate_materialized_tree_with_phase1(tree)
    _require_tree_matches_manifest(tree, tree_hash, manifest_snap.value)
    if result_snap.value["materialized_tree_sha256"] != tree_hash:
        raise EvidenceError("E_PILOT_SOURCE_RESULT", "PASS tree hash differs")


def run_validate_source(archive: Path, materialize_root: Path) -> None:
    """Run the unique authority chain, then exclusive-create manifest, root, and PASS result."""

    chain = verify_production_gate_chain()
    root = Path(materialize_root)
    state, manifest_snap, result_snap = _inspect_state(chain, root)
    staging = _staging_path(root)
    if state == "FRESH":
        _fresh_prepare(Path(archive), root, chain)
        return
    if state == "MANIFEST_ONLY":
        _recover_manifest_only(Path(archive), root, chain, manifest_snap)
        return
    if _staging_lexists(staging):
        raise EvidenceError(
            "E_PILOT_SOURCE_OUTPUT_EXISTS",
            "pre-existing staging must be preserved",
        )
    if state == "MANIFEST_AND_ROOT":
        _recover_manifest_and_root(Path(archive), root, chain, manifest_snap)
        return
    if state == "ALREADY_COMPLETE":
        _revalidate_already_complete(
            Path(archive), root, chain, manifest_snap, result_snap
        )
        return
    if state == "ORPHAN_ROOT":
        raise EvidenceError("E_PILOT_SOURCE_ORPHAN_ROOT", "materialize root is orphaned")
    raise EvidenceError("E_PILOT_SOURCE_OUTPUT_EXISTS", f"reconciliation state {state}")


def validate_source_restoration_evidence(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value, SOURCE_RESTORATION_EVIDENCE_EXACT, "source-restoration-evidence"
    )
    if validated["schema_version"] != SOURCE_RESTORATION_SCHEMA:
        raise EvidenceError("E_PILOT_SOURCE_RESTORATION", "schema differs")
    if validated["execution_class"] != "PILOT_ONLY" or validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_SOURCE_RESTORATION", "claim ceiling differs")
    if validated["disposition"] not in {"RESTORED", "REVALIDATED", "NOT_APPLIED"}:
        raise EvidenceError("E_PILOT_SOURCE_RESTORATION", "disposition differs")
    try:
        start = datetime.fromisoformat(validated["started_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(validated["ended_at"].replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise EvidenceError("E_PILOT_SOURCE_RESTORATION", "timestamps invalid") from exc
    if (
        not validated["started_at"]
        or not validated["ended_at"]
        or not validated["started_at"].endswith("Z")
        or not validated["ended_at"].endswith("Z")
        or start.utcoffset() != timezone.utc.utcoffset(start)
        or end.utcoffset() != timezone.utc.utcoffset(end)
        or start > end
    ):
        raise EvidenceError("E_PILOT_SOURCE_RESTORATION", "timestamps invalid")
    passed = validated["terminal_status"] == "PASS"
    if validated["terminal_status"] not in {"PASS", "FAIL"}:
        raise EvidenceError("E_PILOT_SOURCE_RESTORATION", "terminal status differs")
    if passed:
        expected = (ATTEMPT2_ARCHIVE_SHA256, ATTEMPT2_ARCHIVE_BYTES,
                    FROZEN_NORMALIZED_SOURCE_TREE_SHA256, ATTEMPT2_FILE_COUNT,
                    ATTEMPT2_TOTAL_BYTES)
        actual = tuple(validated[k] for k in ("archive_sha256", "archive_bytes",
            "normalized_tree_sha256", "materialized_file_count", "materialized_total_bytes"))
        flags = (validated["staging_published"], validated["root_published"])
        legal = ((validated["disposition"], flags) in {
            ("RESTORED", (True, True)), ("REVALIDATED", (False, False))})
        if actual != expected or validated["failure_reason"] is not None or not legal:
            raise EvidenceError("E_PILOT_SOURCE_RESTORATION", "invalid PASS evidence")
    elif (validated["disposition"] != "NOT_APPLIED"
          or validated["failure_reason"] not in SOURCE_RESTORATION_FAILURE_REASONS
          or validated["staging_published"] or validated["root_published"]):
        raise EvidenceError("E_PILOT_SOURCE_RESTORATION", "invalid FAIL evidence")
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_SOURCE_RESTORATION", "self-hash differs")
    return validated


def run_restore_production_source(archive: Path, materialize_root: Path) -> dict[str, Any]:
    """Restore only the frozen missing production root, or fully revalidate it."""
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    last_evidence: dict[str, Any] | None = None

    def evidence(status: str, reason: str | None = None, *, restored: bool = False,
                 snapshot: ArchiveSnapshot | None = None, tree_hash: str | None = None,
                 count: int = 0, total: int = 0) -> dict[str, Any]:
        nonlocal last_evidence
        payload = {"schema_version": SOURCE_RESTORATION_SCHEMA, "execution_class": "PILOT_ONLY",
            "claims": "blocked", "disposition": ("RESTORED" if restored else "REVALIDATED")
            if status == "PASS" else "NOT_APPLIED",
            "archive_sha256": snapshot.sha256 if snapshot else ATTEMPT2_ARCHIVE_SHA256,
            "archive_bytes": snapshot.size if snapshot else ATTEMPT2_ARCHIVE_BYTES,
            "normalized_tree_sha256": tree_hash or FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
            "materialized_file_count": count if status == "PASS" else 0,
            "materialized_total_bytes": total if status == "PASS" else 0,
            "staging_published": restored and status == "PASS",
            "root_published": restored and status == "PASS", "started_at": started,
            "ended_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "terminal_status": status, "failure_reason": reason}
        payload["artifact_sha256"] = canonical_sha256(payload)
        validated = validate_source_restoration_evidence(payload)
        last_evidence = validated
        return validated

    snapshot = None
    created_staging = False
    if Path(archive) != ATTEMPT2_ARCHIVE_PATH:
        return evidence("FAIL", "WRONG_ARCHIVE_PATH")
    if Path(materialize_root) != ATTEMPT2_SOURCE_ROOT:
        return evidence("FAIL", "WRONG_SOURCE_ROOT")
    if os.path.lexists(ATTEMPT2_SOURCE_STAGING_ROOT):
        return evidence("FAIL", "STAGING_SYMLINK" if os.path.islink(ATTEMPT2_SOURCE_STAGING_ROOT)
                        else "STAGING_EXISTS")
    if os.path.islink(ATTEMPT2_SOURCE_ROOT):
        return evidence("FAIL", "ROOT_SYMLINK")

    try:
        try:
            snapshot = read_production_archive_bytes(archive)
        except (EvidenceError, OSError) as exc:
            reason = (
                "ARCHIVE_FORMAT_MISMATCH"
                if isinstance(exc, EvidenceError) and exc.code == "E_PILOT_ARCHIVE_FORMAT"
                else "ARCHIVE_UNSAFE"
            )
            return evidence("FAIL", reason)
        if snapshot.sha256 != ATTEMPT2_ARCHIVE_SHA256:
            return evidence("FAIL", "ARCHIVE_HASH_MISMATCH", snapshot=snapshot)
        if snapshot.size != ATTEMPT2_ARCHIVE_BYTES:
            return evidence("FAIL", "ARCHIVE_SIZE_MISMATCH", snapshot=snapshot)
        if snapshot.archive_format != "TAR":
            return evidence("FAIL", "ARCHIVE_FORMAT_MISMATCH", snapshot=snapshot)
        try:
            chain = verify_production_gate_chain()
            state, manifest_snapshot, result_snapshot = _inspect_state(
                chain, ATTEMPT2_SOURCE_ROOT
            )
        except (EvidenceError, OSError):
            return evidence("FAIL", "INVALID_PASS_PAIR", snapshot=snapshot)
        if state not in {"INVALID_PASS_NO_ROOT", "ALREADY_COMPLETE"}:
            return evidence("FAIL", "INVALID_RECONCILIATION_STATE", snapshot=snapshot)
        if (
            not manifest_snapshot.present
            or not manifest_snapshot.valid
            or manifest_snapshot.value is None
            or manifest_snapshot.raw is None
            or manifest_snapshot.digest is None
            or not result_snapshot.present
            or not result_snapshot.valid
            or result_snapshot.value is None
            or result_snapshot.raw is None
            or result_snapshot.digest is None
            or result_snapshot.status != "PASS"
            or result_snapshot.value["source_manifest_sha256"]
            != manifest_snapshot.digest
        ):
            return evidence("FAIL", "INVALID_PASS_PAIR", snapshot=snapshot)

        authority_bytes = (manifest_snapshot.raw, result_snapshot.raw)
        restored = state == "INVALID_PASS_NO_ROOT"
        if restored:
            try:
                root = extract_archive_to_staging(snapshot, ATTEMPT2_SOURCE_STAGING_ROOT)
                if root != ATTEMPT2_SOURCE_STAGING_ROOT:
                    return evidence("FAIL", "EXTRACTION_UNSAFE", snapshot=snapshot)
                created_staging = True
            except EvidenceError as exc:
                reason = (
                    "ARCHIVE_FORMAT_MISMATCH"
                    if exc.code == "E_PILOT_ARCHIVE_FORMAT"
                    else "EXTRACTION_UNSAFE"
                )
                return evidence("FAIL", reason, snapshot=snapshot)
            except OSError:
                return evidence("FAIL", "EXTRACTION_UNSAFE", snapshot=snapshot)
        else:
            root = ATTEMPT2_SOURCE_ROOT
        try:
            tree = capture_materialized_tree(root)
            tree_hash = canonical_source_tree_sha256(tree)
            count, total = _tree_metrics(tree)
        except EvidenceError as exc:
            reason = (
                "TREE_HASH_MISMATCH"
                if exc.code == "E_PILOT_SOURCE_TREE_MISMATCH"
                else "EXTRACTION_UNSAFE"
            )
            return evidence("FAIL", reason, snapshot=snapshot)
        except OSError:
            return evidence("FAIL", "EXTRACTION_UNSAFE", snapshot=snapshot)
        if tree_hash != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
            return evidence("FAIL", "TREE_HASH_MISMATCH", snapshot=snapshot)
        if count != ATTEMPT2_FILE_COUNT:
            return evidence("FAIL", "FILE_COUNT_MISMATCH", snapshot=snapshot)
        if total != ATTEMPT2_TOTAL_BYTES:
            return evidence("FAIL", "BYTE_COUNT_MISMATCH", snapshot=snapshot)
        try:
            validate_materialized_tree_with_phase1(tree)
            _require_tree_matches_manifest(tree, tree_hash, manifest_snapshot.value)
        except EvidenceError as exc:
            reason = (
                "EXTRACTION_UNSAFE"
                if exc.code == "E_PILOT_EXTRACT_UNSAFE"
                else "TREE_HASH_MISMATCH"
            )
            return evidence("FAIL", reason, snapshot=snapshot)
        except OSError:
            return evidence("FAIL", "EXTRACTION_UNSAFE", snapshot=snapshot)
        boost_math = root / "include" / "boost" / "math"
        if not boost_math.is_dir() or boost_math.is_symlink():
            return evidence("FAIL", "TREE_HASH_MISMATCH", snapshot=snapshot)
        try:
            current_manifest, _ = read_authority_snapshot(
                SOURCE_MANIFEST_PATH, "source-restoration-manifest"
            )
            current_result, _ = read_authority_snapshot(
                SOURCE_PREPARATION_RESULT_PATH, "source-restoration-result"
            )
        except (EvidenceError, OSError):
            return evidence("FAIL", "INVALID_PASS_PAIR", snapshot=snapshot)
        if (current_manifest, current_result) != authority_bytes:
            return evidence("FAIL", "INVALID_PASS_PAIR", snapshot=snapshot)
        if restored:
            try:
                os.replace(ATTEMPT2_SOURCE_STAGING_ROOT, ATTEMPT2_SOURCE_ROOT)
            except OSError:
                return evidence("FAIL", "EXTRACTION_UNSAFE", snapshot=snapshot)
            created_staging = False
        return evidence("PASS", restored=restored, snapshot=snapshot,
                        tree_hash=tree_hash, count=count, total=total)
    finally:
        if created_staging and os.path.lexists(ATTEMPT2_SOURCE_STAGING_ROOT):
            cleanup_failed = False
            try:
                shutil.rmtree(ATTEMPT2_SOURCE_STAGING_ROOT)
            except OSError:
                cleanup_failed = True
            if os.path.lexists(ATTEMPT2_SOURCE_STAGING_ROOT):
                cleanup_failed = True
            if cleanup_failed and last_evidence is not None:
                pending_evidence = last_evidence
                replacement = evidence("FAIL", "EXTRACTION_UNSAFE", snapshot=snapshot)
                pending_evidence.clear()
                pending_evidence.update(replacement)


if canonical_sha256(EXTRACTOR_POLICY_V1) != EXTRACTOR_POLICY_SHA256:
    raise RuntimeError("EXTRACTOR_POLICY_SHA256 is not the canonical policy hash")
