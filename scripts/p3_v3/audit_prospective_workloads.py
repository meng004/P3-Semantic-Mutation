#!/usr/bin/env python3
"""Outcome-blind audit of frozen P3 prospective profiling workloads."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping
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
