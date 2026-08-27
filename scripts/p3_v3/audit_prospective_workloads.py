#!/usr/bin/env python3
"""Outcome-blind audit of frozen P3 prospective profiling workloads."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import (  # noqa: E402
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    validate_sha256,
)
from p3_v3.bridge_and_frames import validate_bridge_document  # noqa: E402

EXPECTED_SUBJECT_COUNT = 35
BOOST_MATH_ID = "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886"
NUMPY_ID = "4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b"


@dataclass(frozen=True)
class SubjectInputs:
    neutral_snapshot_id: str
    bridge_record: Mapping[str, Any]
    descriptor: Mapping[str, Any]
    adapter_discovery: Mapping[str, Any]
    public_behavior_frame: Mapping[str, Any]
    profiling_workload: Mapping[str, Any]


@dataclass(frozen=True)
class RowDecision:
    invocation_kind: str | None
    unique: bool
    failure_code: str | None


@dataclass(frozen=True)
class SubjectAudit:
    neutral_snapshot_id: str
    language_family: str
    ecosystem: str
    row_count: int
    row_decisions: tuple[tuple[str, RowDecision], ...]
    terminal: str
    trace_strategy: str | None
    dependency_count: int | None
    source_status: str | None


_UNDERSPECIFIED = RowDecision(None, False, "NO_UNIQUE_EXECUTION_ACTION")
_JOIN_FIELDS = (
    "category",
    "entrypoint",
    "declared_input_schema_sha256",
    "diversity_signature_sha256",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="audit-prospective-workloads")
    parser.add_argument("--consumer-lock", required=True)
    parser.add_argument("--verified-bridge", required=True)
    parser.add_argument("--phase1-root", required=True)
    parser.add_argument("--descriptor-root", required=True)
    parser.add_argument("--archive-root", required=True)
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--output", required=True)
    return parser


def read_self_hashed_object(path: Path, context: str) -> dict[str, Any]:
    value = read_canonical_json(path)
    if not isinstance(value, dict):
        raise EvidenceError("E_AUDIT_ARTIFACT", f"{context} must be an object")
    artifact = validate_sha256(value.get("artifact_sha256"), f"{context}.artifact_sha256")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if artifact != canonical_sha256(body):
        raise EvidenceError("E_AUDIT_ARTIFACT_HASH", f"{context} self-hash differs")
    return value


def load_population(
    *,
    consumer_lock_path: Path,
    verified_bridge_path: Path,
    phase1_root: Path,
    descriptor_root: Path,
) -> tuple[SubjectInputs, ...]:
    consumer_lock = read_canonical_json(consumer_lock_path)
    if not isinstance(consumer_lock, dict):
        raise EvidenceError("E_AUDIT_ARTIFACT", "consumer lock must be an object")
    bridge = read_canonical_json(verified_bridge_path)
    if not isinstance(bridge, dict):
        raise EvidenceError("E_AUDIT_ARTIFACT", "verified bridge must be an object")
    validated = validate_bridge_document(bridge, consumer_lock)
    records = list(validated["records"])
    if (
        validated["eligible_item_count"] != EXPECTED_SUBJECT_COUNT
        or len(records) != EXPECTED_SUBJECT_COUNT
    ):
        raise EvidenceError(
            "E_AUDIT_POPULATION",
            "eligible item count must be exactly 35",
        )
    records.sort(key=lambda record: record["neutral_snapshot_id"])
    expected_ids = [record["neutral_snapshot_id"] for record in records]
    if len(set(expected_ids)) != EXPECTED_SUBJECT_COUNT:
        raise EvidenceError("E_AUDIT_POPULATION", "neutral snapshot IDs are not unique")

    subjects: list[SubjectInputs] = []
    workload_ids: list[str] = []
    for record in records:
        snapshot_id = record["neutral_snapshot_id"]
        descriptor_path = Path(descriptor_root) / f"{snapshot_id}.json"
        adapter_path = Path(phase1_root) / f"adapter-discovery-{snapshot_id}.json"
        frame_path = Path(phase1_root) / f"public-behavior-frame-{snapshot_id}.json"
        workload_path = Path(phase1_root) / f"profiling-workload-{snapshot_id}.json"
        if file_sha256(descriptor_path) != record["build_descriptor_sha256"]:
            raise EvidenceError(
                "E_AUDIT_DESCRIPTOR",
                f"{snapshot_id} descriptor hash differs from the bridge",
            )
        descriptor = read_canonical_json(descriptor_path)
        if not isinstance(descriptor, dict):
            raise EvidenceError("E_AUDIT_ARTIFACT", f"{snapshot_id} descriptor must be an object")
        adapter_discovery = read_self_hashed_object(
            adapter_path, f"{snapshot_id} adapter-discovery"
        )
        public_behavior_frame = read_self_hashed_object(
            frame_path, f"{snapshot_id} public-behavior-frame"
        )
        profiling_workload = read_self_hashed_object(
            workload_path, f"{snapshot_id} profiling-workload"
        )
        workload_ids.append(snapshot_id)
        subjects.append(
            SubjectInputs(
                neutral_snapshot_id=snapshot_id,
                bridge_record=record,
                descriptor=descriptor,
                adapter_discovery=adapter_discovery,
                public_behavior_frame=public_behavior_frame,
                profiling_workload=profiling_workload,
            )
        )
    if sorted(workload_ids) != sorted(expected_ids):
        raise EvidenceError(
            "E_AUDIT_POPULATION",
            "workload filenames do not match the bridge ID set",
        )
    return tuple(subjects)


def classify_row_invocation(
    *,
    language_family: str,
    entrypoint: str,
    declared_inputs: Mapping[str, Any] | None,
    exact_boost_header_runner: bool,
) -> RowDecision:
    if not isinstance(declared_inputs, Mapping):
        return _UNDERSPECIFIED
    keys = set(declared_inputs)
    if keys == {"argv_tokens"}:
        tokens = declared_inputs["argv_tokens"]
        if (
            isinstance(tokens, list)
            and tokens
            and all(isinstance(token, str) for token in tokens)
        ):
            return RowDecision("ARGV", True, None)
        return _UNDERSPECIFIED
    if keys == {"parameters"}:
        if language_family == "python" and _python_callable_entrypoint(entrypoint):
            return RowDecision("PYTHON_CALLABLE", True, None)
        return _UNDERSPECIFIED
    if keys == {"header"} and exact_boost_header_runner:
        return RowDecision("CXX_HEADER_COMPILE", True, None)
    return _UNDERSPECIFIED


def _python_callable_entrypoint(entrypoint: object) -> bool:
    if not isinstance(entrypoint, str) or ":" not in entrypoint:
        return False
    module, symbol = entrypoint.rsplit(":", 1)
    return bool(module) and bool(symbol)


def _selected_rows(workload: Mapping[str, Any], snapshot_id: str) -> list[dict[str, Any]]:
    rows = workload.get("selected_rows")
    if rows is None:
        return []
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise EvidenceError("E_AUDIT_WORKLOAD", f"{snapshot_id} selected_rows must be objects")
    return rows


def _behavior_frame_index(
    frame: Mapping[str, Any],
    snapshot_id: str,
) -> dict[str, dict[str, Any]]:
    rows = frame.get("rows")
    if not isinstance(rows, list):
        raise EvidenceError(
            "E_AUDIT_JOIN",
            f"{snapshot_id} public behavior frame rows must be a list",
        )
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise EvidenceError("E_AUDIT_JOIN", f"{snapshot_id} behavior row must be an object")
        behavior_id = row.get("behavior_id")
        if not isinstance(behavior_id, str) or not behavior_id:
            raise EvidenceError("E_AUDIT_JOIN", f"{snapshot_id} behavior_id is missing")
        if behavior_id in index:
            raise EvidenceError(
                "E_AUDIT_JOIN",
                f"{snapshot_id} duplicate public behavior {behavior_id}",
            )
        index[behavior_id] = row
    return index


def _join_selected_row(
    selected: Mapping[str, Any],
    frame_row: Mapping[str, Any],
    snapshot_id: str,
    behavior_id: str,
) -> None:
    for field in _JOIN_FIELDS:
        if selected.get(field) != frame_row.get(field):
            raise EvidenceError(
                "E_AUDIT_JOIN",
                f"{snapshot_id} {behavior_id} {field} differs from the public behavior frame",
            )


def audit_invocations(subject: SubjectInputs) -> SubjectAudit:
    language_family = str(subject.descriptor.get("language_family") or "")
    ecosystem = str(subject.descriptor.get("ecosystem") or "")
    selected_rows = _selected_rows(subject.profiling_workload, subject.neutral_snapshot_id)
    row_count = len(selected_rows)
    if row_count not in {0, 20}:
        raise EvidenceError(
            "E_AUDIT_ROW_COUNT",
            f"{subject.neutral_snapshot_id} selected_rows must be 0 or 20",
        )
    if row_count == 0:
        return SubjectAudit(
            neutral_snapshot_id=subject.neutral_snapshot_id,
            language_family=language_family,
            ecosystem=ecosystem,
            row_count=0,
            row_decisions=(),
            terminal="NO_FROZEN_WORKLOAD",
            trace_strategy=None,
            dependency_count=None,
            source_status=None,
        )
    behavior_ids = [row.get("behavior_id") for row in selected_rows]
    if any(not isinstance(item, str) or not item for item in behavior_ids):
        raise EvidenceError(
            "E_AUDIT_WORKLOAD",
            f"{subject.neutral_snapshot_id} selected rows require behavior_id",
        )
    if len(set(behavior_ids)) != 20:
        raise EvidenceError(
            "E_AUDIT_WORKLOAD",
            f"{subject.neutral_snapshot_id} must have exactly 20 distinct behavior IDs",
        )
    frame_index = _behavior_frame_index(
        subject.public_behavior_frame,
        subject.neutral_snapshot_id,
    )
    exact_boost = subject.neutral_snapshot_id == BOOST_MATH_ID
    decisions: list[tuple[str, RowDecision]] = []
    for selected in selected_rows:
        behavior_id = str(selected["behavior_id"])
        frame_row = frame_index.get(behavior_id)
        if frame_row is None:
            raise EvidenceError(
                "E_AUDIT_JOIN",
                f"{subject.neutral_snapshot_id} missing public behavior {behavior_id}",
            )
        _join_selected_row(selected, frame_row, subject.neutral_snapshot_id, behavior_id)
        decisions.append(
            (
                behavior_id,
                classify_row_invocation(
                    language_family=language_family,
                    entrypoint=str(selected.get("entrypoint") or ""),
                    declared_inputs=frame_row.get("declared_inputs"),
                    exact_boost_header_runner=exact_boost,
                ),
            )
        )
    decisions.sort(key=lambda item: item[0])
    if exact_boost:
        terminal = "TERMINAL_RETRY_FORBIDDEN"
    elif any(not decision.unique for _, decision in decisions):
        terminal = "WORKLOAD_EXECUTION_UNDERSPECIFIED"
    else:
        terminal = "INVOCATION_COMPLETE"
    return SubjectAudit(
        neutral_snapshot_id=subject.neutral_snapshot_id,
        language_family=language_family,
        ecosystem=ecosystem,
        row_count=20,
        row_decisions=tuple(decisions),
        terminal=terminal,
        trace_strategy=None,
        dependency_count=None,
        source_status=None,
    )


def audit_invocations_for_population(
    subjects: Sequence[SubjectInputs],
) -> tuple[SubjectAudit, ...]:
    return tuple(audit_invocations(subject) for subject in subjects)
