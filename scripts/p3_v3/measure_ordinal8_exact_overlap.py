#!/usr/bin/env python3
"""Measure ordinal-8 normalized-patch and mutant-tree exact overlap. No execution."""

from __future__ import annotations

import hashlib
import shutil
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    read_regular_file_snapshot,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import canonical_source_tree_sha256
from p3_v3.ordinal8_first_paired_evidence import apply_patch_text
from p3_v3.pilot_source import capture_materialized_tree

SCHEMA_VERSION = "p3-ordinal8-exact-overlap-v1"
TASK_ID = "P3_C3_ORDINAL8_EXACT_OVERLAP_MEASUREMENT"
ANALYSIS_HEAD = "ec9e6c949b76e7dfe5b17f397a92c497c89554b5"
PAIR_ORDER = ("INV/TF", "INV/SI", "CMP/TF", "CMP/SI")
NEUTRAL_SNAPSHOT_ID = (
    "4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b"
)
CONTROLLED_SUBJECT_SOURCE_ID = (
    "667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0"
)
CONTROLLED_SUBJECT_ID = (
    "0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48"
)
SOURCE_ARCHIVE_SHA256 = (
    "c73c0ec41ea53ba9ecb0f9903a55a19ed6c1dbfd1de00404d96b58d9c30bb3c9"
)
NORMALIZED_ORIGINAL_TREE_SHA256 = (
    "f8826c3b975f8699e136e0b6b4cd4c29bf0d7e9a3be04fe09b947eb8998e727b"
)
HANDOFF_RELATIVE = "data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json"
HANDOFF_FILE_SHA256 = (
    "ad3361f990ff0a611ece2704077780d7f097459560085eb9a996acb8b69e1b3d"
)
HANDOFF_ARTIFACT_SHA256 = (
    "a846ca2edded55ed48e0e9071a9aa218efc3dbcc9bd302a77ceb53bce9d822c5"
)
REPLAY_RELATIVE = (
    "data/p3_v3/phase3/ordinal8-first-paired-evidence-clean-replay-v1/clean-replay.json"
)
BATCH_RELATIVE = (
    "data/p3_v3/phase3/ordinal8-remaining-three-paired-batch-v1/paired-batch.json"
)
CONTRACTS_RELATIVE = "data/p3_v3/phase2/ordinal8-partial-contract-freeze/contracts.json"
ANALYSIS_SPEC_RELATIVE = "data/p3_v3/protocol/analysis_spec.md"
LEDGER_RELATIVE = "research/evidence/p3_claim_ledger_v1.3.0.yml"
ARCHIVE_RELATIVE = f"data/p3_v3/p12_intake/archives/{NEUTRAL_SNAPSHOT_ID}.tar"
EXTRACTED_RELATIVE = f"data/p3_v3/p12_intake/extracted/{NEUTRAL_SNAPSHOT_ID}"
FORMAL_OUTPUT_RELATIVE = (
    "data/p3_v3/phase3/ordinal8-exact-overlap-v1/exact-overlap.json"
)
FORMAL_RUNTIME_ROOT = Path("/tmp/p3-c3-ordinal8-exact-overlap-v1")
REPLAY_FILE_SHA256 = "5b734c2a21283d6cdb83a5827d50bdf688d69eb7e2dcd620d69b01a9875000ff"
REPLAY_ARTIFACT_SHA256 = (
    "f0ce09ff92e181fda27573c612643d3b48a8e4e24081d390f19acc4ebbd8897f"
)
BATCH_FILE_SHA256 = "ee4bcc00e1ea21d3b452eed5eb52384b27fbcc7544350dd569c38cd997fc83a0"
BATCH_ARTIFACT_SHA256 = (
    "2b14ac9e111db6189eeab890ad2f52468220233588db12e99e6790707759a5ed"
)


def verify_bound_record(
    path: str | Path,
    *,
    expected_file_sha256: str,
    expected_artifact_sha256: str,
) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file() or source.is_symlink():
        raise EvidenceError("E_EVIDENCE_IDENTITY", f"record absent: {source}")
    if file_sha256(source) != expected_file_sha256:
        raise EvidenceError("E_EVIDENCE_IDENTITY", f"file SHA-256 differs: {source}")
    record = read_canonical_json(source)
    if not isinstance(record, Mapping):
        raise EvidenceError("E_EVIDENCE_IDENTITY", f"record is not an object: {source}")
    digest = record.get("artifact_sha256")
    body = {key: value for key, value in record.items() if key != "artifact_sha256"}
    if digest != expected_artifact_sha256 or digest != canonical_sha256(body):
        raise EvidenceError(
            "E_EVIDENCE_IDENTITY", f"artifact SHA-256 differs: {source}"
        )
    return dict(record)


def _require_c3_blocked(repo_root: Path) -> dict[str, Any]:
    text = (repo_root / LEDGER_RELATIVE).read_text(encoding="utf-8")
    if "claim_id: C3_SEMANTIC_CONSTRUCT_DISTINCTNESS" not in text:
        raise EvidenceError("E_CLAIM_CEILING", "C3 claim is absent from the ledger")
    if (
        'upgrade_condition: "RQ2 paired evidence and uncertainty accounting complete"'
        not in text
    ):
        raise EvidenceError("E_CLAIM_CEILING", "C3 upgrade_condition differs")
    block = text.split("claim_id: C3_SEMANTIC_CONSTRUCT_DISTINCTNESS", 1)[1]
    block = block.split("claim_id:", 1)[0]
    if "status: blocked" not in block:
        raise EvidenceError("E_CLAIM_CEILING", "C3 is not blocked")
    return {
        "claim_id": "C3_SEMANTIC_CONSTRUCT_DISTINCTNESS",
        "claim_status": "blocked",
        "upgrade_condition": "RQ2 paired evidence and uncertainty accounting complete",
        "upgrade_condition_satisfied": False,
    }


def exact_overlap(left: str, right: str) -> bool:
    if len(left) != 64 or len(right) != 64 or left != left.lower() or right != right.lower():
        raise EvidenceError("E_OVERLAP_IDENTITY", "overlap identity is not a SHA-256")
    return left == right


def tree_sha256(tree: str | Path) -> str:
    snapshot = capture_materialized_tree(Path(tree))
    return canonical_source_tree_sha256(snapshot)


def verify_original_tree(tree: str | Path, *, expected_sha256: str) -> str:
    observed = tree_sha256(tree)
    if observed != expected_sha256:
        raise EvidenceError(
            "E_SOURCE_IDENTITY",
            f"original tree SHA-256 differs: expected {expected_sha256}, observed {observed}",
        )
    return observed


def copy_original_tree(source: str | Path, destination: str | Path) -> Path:
    src = Path(source)
    dest = Path(destination)
    if dest.exists():
        raise EvidenceError("E_RUNTIME", f"destination already exists: {dest}")
    shutil.copytree(src, dest, symlinks=False)
    return dest


def verify_patch_file(path: str | Path, expected_sha256: str) -> str:
    source = Path(path)
    if source.is_symlink() or not source.is_file():
        raise EvidenceError("E_PATCH_IDENTITY", f"PATCH_IDENTITY_CONFLICT: {source}")
    raw, _mode = read_regular_file_snapshot(source, "frozen-patch")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise EvidenceError(
            "E_PATCH_IDENTITY",
            f"PATCH_IDENTITY_CONFLICT: patch SHA-256 differs: {source}",
        )
    return digest


def apply_frozen_patch_to_tree(tree: str | Path, patch: Mapping[str, str]) -> None:
    root = Path(tree)
    relative = patch["path"]
    target = root / relative
    if target.is_symlink() or not target.is_file():
        raise EvidenceError("E_PATCH_IDENTITY", f"patch target is not a regular file: {relative}")
    text = target.read_text(encoding="utf-8")
    mutated = apply_patch_text(text, patch)
    if mutated == text:
        raise EvidenceError("E_PATCH_SPAN", "patch application produced no change")
    target.write_text(mutated, encoding="utf-8")


def _family_mechanism(contract_family: str, operator_id: str) -> str:
    prefix = f"{contract_family}_"
    if not operator_id.startswith(prefix):
        raise EvidenceError(
            "E_PAIR_IDENTITY", f"operator {operator_id} is not in family {contract_family}"
        )
    mechanism = operator_id[len(prefix) :].split("_", 1)[0]
    if mechanism not in {"TF", "SI"}:
        raise EvidenceError("E_PAIR_IDENTITY", f"mechanism is not TF or SI: {operator_id}")
    return f"{contract_family}/{mechanism}"


def _require_patch(record: Mapping[str, Any], *, slot_id: str) -> dict[str, str]:
    required = ("operator_id", "path", "source", "target", "unified_diff", "patch_sha256")
    if any(key not in record for key in required):
        raise EvidenceError("E_PATCH_IDENTITY", "frozen patch fields are incomplete")
    if "patch_sha256" not in record:
        raise EvidenceError(
            "E_NORMALIZED_PATCH_AUTHORITY", "NORMALIZED_PATCH_AUTHORITY_CONFLICT"
        )
    patch = {key: str(record[key]) for key in required}
    if slot_id and record.get("slot_id") not in {None, slot_id}:
        raise EvidenceError("E_PATCH_IDENTITY", "patch slot_id differs")
    recomputed = hashlib.sha256(patch["unified_diff"].encode("utf-8")).hexdigest()
    if recomputed != patch["patch_sha256"]:
        raise EvidenceError(
            "E_NORMALIZED_PATCH_AUTHORITY",
            "NORMALIZED_PATCH_AUTHORITY_CONFLICT: recorded patch_sha256 is not the canonical unified-diff identity",
        )
    return patch


def discover_pairs(repo_root: str | Path) -> list[dict[str, Any]]:
    root = Path(repo_root)
    replay = verify_bound_record(
        root / REPLAY_RELATIVE,
        expected_file_sha256=REPLAY_FILE_SHA256,
        expected_artifact_sha256=REPLAY_ARTIFACT_SHA256,
    )
    batch = verify_bound_record(
        root / BATCH_RELATIVE,
        expected_file_sha256=BATCH_FILE_SHA256,
        expected_artifact_sha256=BATCH_ARTIFACT_SHA256,
    )
    contracts = read_canonical_json(root / CONTRACTS_RELATIVE)
    if not isinstance(contracts, Mapping):
        raise EvidenceError("E_PAIR_IDENTITY", "contracts freeze is not an object")
    replay_slot = str(replay["slot_id"])
    if replay_slot not in contracts:
        raise EvidenceError("E_PAIR_IDENTITY", "INV/TF contract is absent")
    replay_family = contracts[replay_slot]["domain"]["semantic_contract_family"]
    semantic = _require_patch(replay["semantic_patch"], slot_id=replay_slot)
    syntactic = _require_patch(replay["syntactic_patch"], slot_id=replay_slot)
    if semantic["patch_sha256"] != replay["semantic_patch_sha256"]:
        raise EvidenceError("E_PATCH_IDENTITY", "replay semantic SHA fields differ")
    if syntactic["patch_sha256"] != replay["syntactic_patch_sha256"]:
        raise EvidenceError("E_PATCH_IDENTITY", "replay syntactic SHA fields differ")
    discovered = [
        {
            "family_mechanism": _family_mechanism(replay_family, semantic["operator_id"]),
            "slot_id": replay_slot,
            "site_id": replay["site_id"],
            "contract_id": replay["contract_id"],
            "semantic_patch": semantic,
            "syntactic_patch": syntactic,
            "source_record": "clean-replay",
        }
    ]
    batch_slots = {row["slot_id"]: row for row in batch["slots"]}
    patch_index = {
        (row["slot_id"], row["kind"]): row for row in batch["patches"]
    }
    for slot in batch["slots"]:
        slot_id = slot["slot_id"]
        identity = batch_slots[slot_id]
        if slot_id not in contracts:
            raise EvidenceError("E_PAIR_IDENTITY", f"contract missing for {slot_id}")
        family = contracts[slot_id]["domain"]["semantic_contract_family"]
        semantic = _require_patch(patch_index[(slot_id, "semantic")], slot_id=slot_id)
        syntactic = _require_patch(patch_index[(slot_id, "syntactic")], slot_id=slot_id)
        derived = _family_mechanism(family, semantic["operator_id"])
        if derived != identity["family_mechanism"]:
            raise EvidenceError("E_PAIR_IDENTITY", f"{slot_id} family_mechanism differs")
        discovered.append(
            {
                "family_mechanism": derived,
                "slot_id": slot_id,
                "site_id": identity["site_id"],
                "contract_id": identity["contract_id"],
                "semantic_patch": semantic,
                "syntactic_patch": syntactic,
                "source_record": "remaining-three-batch",
            }
        )
    ordered = []
    for family_mechanism in PAIR_ORDER:
        matches = [row for row in discovered if row["family_mechanism"] == family_mechanism]
        if len(matches) != 1:
            raise EvidenceError(
                "E_PAIR_IDENTITY", f"{family_mechanism} is not uniquely resolved"
            )
        ordered.append(matches[0])
    if len({row["slot_id"] for row in ordered}) != 4:
        raise EvidenceError("E_PAIR_IDENTITY", "pair slot_ids are not unique")
    patch_shas = [
        row[kind]["patch_sha256"]
        for row in ordered
        for kind in ("semantic_patch", "syntactic_patch")
    ]
    if len(set(patch_shas)) != 8:
        raise EvidenceError("E_PATCH_IDENTITY", "frozen patches are not uniquely located")
    return ordered


def verify_source_archive(repo_root: Path) -> dict[str, str]:
    archive = repo_root / ARCHIVE_RELATIVE
    extracted = repo_root / EXTRACTED_RELATIVE
    if archive.is_symlink() or not archive.is_file():
        raise EvidenceError(
            "E_SOURCE_IDENTITY", "SOURCE_IDENTITY_RECOVERY_REQUIRED: archive"
        )
    if file_sha256(archive) != SOURCE_ARCHIVE_SHA256:
        raise EvidenceError("E_SOURCE_IDENTITY", "archive SHA-256 differs")
    if not extracted.is_dir() or extracted.is_symlink():
        raise EvidenceError(
            "E_SOURCE_IDENTITY", "SOURCE_IDENTITY_RECOVERY_REQUIRED: extracted tree"
        )
    verify_original_tree(extracted, expected_sha256=NORMALIZED_ORIGINAL_TREE_SHA256)
    return {
        "archive_path": ARCHIVE_RELATIVE,
        "extracted_path": EXTRACTED_RELATIVE,
        "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        "normalized_original_tree_sha256": NORMALIZED_ORIGINAL_TREE_SHA256,
    }


def _materialize_patch(runtime: Path, pair: Mapping[str, Any], kind: str) -> str:
    patch = pair[f"{kind}_patch"]
    dest = runtime / "patches" / f"{pair['slot_id']}_{kind}.patch"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(patch["unified_diff"], encoding="utf-8")
    return verify_patch_file(dest, patch["patch_sha256"])


def measure_one_pair(
    pair: Mapping[str, Any],
    *,
    original_tree: Path,
    expected_original_sha256: str,
    runtime_root: Path,
) -> dict[str, Any]:
    verify_original_tree(original_tree, expected_sha256=expected_original_sha256)
    semantic_sha = _materialize_patch(runtime_root, pair, "semantic")
    syntactic_sha = _materialize_patch(runtime_root, pair, "syntactic")
    family = pair["family_mechanism"].replace("/", "_")
    semantic_tree = runtime_root / "pairs" / family / "semantic"
    syntactic_tree = runtime_root / "pairs" / family / "syntactic"
    copy_original_tree(original_tree, semantic_tree)
    copy_original_tree(original_tree, syntactic_tree)
    apply_frozen_patch_to_tree(semantic_tree, pair["semantic_patch"])
    apply_frozen_patch_to_tree(syntactic_tree, pair["syntactic_patch"])
    semantic_tree_sha = tree_sha256(semantic_tree)
    syntactic_tree_sha = tree_sha256(syntactic_tree)
    return {
        "family_mechanism": pair["family_mechanism"],
        "slot_id": pair["slot_id"],
        "site_id": pair["site_id"],
        "contract_id": pair["contract_id"],
        "source_record": pair["source_record"],
        "semantic_patch_sha256": semantic_sha,
        "syntactic_patch_sha256": syntactic_sha,
        "normalized_patch_exact_overlap": exact_overlap(semantic_sha, syntactic_sha),
        "semantic_mutant_tree_sha256": semantic_tree_sha,
        "syntactic_mutant_tree_sha256": syntactic_tree_sha,
        "mutant_tree_exact_overlap": exact_overlap(semantic_tree_sha, syntactic_tree_sha),
    }


def measure_pairs(
    pairs: Sequence[Mapping[str, Any]],
    *,
    original_tree: Path,
    expected_original_sha256: str,
    runtime_root: Path,
    output_path: Path,
    repo_root: Path,
    bind_formal_identities: bool,
) -> dict[str, Any]:
    runtime = Path(runtime_root)
    output = Path(output_path)
    if runtime.exists() or output.exists():
        raise EvidenceError("E_RUNTIME", "formal output or staging already exists")
    runtime.mkdir(parents=True, exist_ok=False)
    claim = _require_c3_blocked(repo_root)
    observations = [
        measure_one_pair(
            pair,
            original_tree=original_tree,
            expected_original_sha256=expected_original_sha256,
            runtime_root=runtime,
        )
        for pair in pairs
    ]
    patch_overlap = sum(
        1 for row in observations if row["normalized_patch_exact_overlap"]
    )
    tree_overlap = sum(1 for row in observations if row["mutant_tree_exact_overlap"])
    body: dict[str, Any] = {
        "analysis_head": ANALYSIS_HEAD,
        "analysis_spec": {
            "path": ANALYSIS_SPEC_RELATIVE,
            "file_sha256": file_sha256(repo_root / ANALYSIS_SPEC_RELATIVE),
        },
        "claim_ceiling": claim,
        "controlled_subject_id": CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
        "exact_binomial_interval_status": "UNMEASURED_INTERVAL_AUTHORITY_INCOMPLETE",
        "exact_binomial_interval_reason": (
            "The frozen analysis spec requires exact binomial intervals for overlap "
            "counts but does not freeze the confidence level or exact method. This "
            "measurement therefore keeps the observed numerator/denominator and does "
            "not select 95%, Clopper-Pearson, or any other interval."
        ),
        "limitations": [
            "n_subjects = 1",
            "n_projects = 1",
            "exact-binomial interval authority is incomplete",
            "project-clustered uncertainty remains unidentifiable",
            "overlap measurement does not upgrade C3",
            "this task does not rerun ordinal-8 mutants or inventory a new project",
        ],
        "measurement_implementation_sha256": file_sha256(Path(__file__).resolve()),
        "mutant_tree_overlap_count": tree_overlap,
        "mutant_tree_pair_count": len(observations),
        "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
        "normalized_original_tree_sha256": expected_original_sha256,
        "normalized_patch_overlap_count": patch_overlap,
        "normalized_patch_pair_count": len(observations),
        "pairs": observations,
        "rq2_handoff": {
            "path": HANDOFF_RELATIVE,
            "file_sha256": HANDOFF_FILE_SHA256,
            "artifact_sha256": HANDOFF_ARTIFACT_SHA256,
        },
        "schema_version": SCHEMA_VERSION,
        "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        "task_id": TASK_ID,
    }
    if bind_formal_identities:
        handoff = verify_bound_record(
            repo_root / HANDOFF_RELATIVE,
            expected_file_sha256=HANDOFF_FILE_SHA256,
            expected_artifact_sha256=HANDOFF_ARTIFACT_SHA256,
        )
        if handoff["claim_ceiling"]["claim_status"] != "blocked":
            raise EvidenceError("E_CLAIM_CEILING", "handoff C3 is not blocked")
        body["rq2_handoff"]["file_sha256"] = file_sha256(repo_root / HANDOFF_RELATIVE)
        body["source_identities"] = verify_source_archive(repo_root)
    else:
        body["source_identities"] = {
            "normalized_original_tree_sha256": expected_original_sha256,
            "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        }
    record = {**body, "artifact_sha256": canonical_sha256(body)}
    output.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(output, record, exclusive=True)
    return record


def measure_formal(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    identities = verify_source_archive(root)
    pairs = discover_pairs(root)
    if [row["family_mechanism"] for row in pairs] != list(PAIR_ORDER):
        raise EvidenceError("E_PAIR_IDENTITY", "pair order differs")
    runtime = FORMAL_RUNTIME_ROOT
    if runtime.exists() or (root / FORMAL_OUTPUT_RELATIVE).exists():
        raise EvidenceError("E_RUNTIME", "formal output or staging already exists")
    runtime.mkdir(parents=True, exist_ok=False)
    original = runtime / "original"
    copy_original_tree(root / EXTRACTED_RELATIVE, original)
    verify_original_tree(
        original, expected_sha256=identities["normalized_original_tree_sha256"]
    )
    # measure_pairs also refuses a pre-existing runtime; use the prepared original.
    output = root / FORMAL_OUTPUT_RELATIVE
    claim = _require_c3_blocked(root)
    verify_bound_record(
        root / HANDOFF_RELATIVE,
        expected_file_sha256=HANDOFF_FILE_SHA256,
        expected_artifact_sha256=HANDOFF_ARTIFACT_SHA256,
    )
    observations = [
        measure_one_pair(
            pair,
            original_tree=original,
            expected_original_sha256=NORMALIZED_ORIGINAL_TREE_SHA256,
            runtime_root=runtime,
        )
        for pair in pairs
    ]
    patch_overlap = sum(
        1 for row in observations if row["normalized_patch_exact_overlap"]
    )
    tree_overlap = sum(1 for row in observations if row["mutant_tree_exact_overlap"])
    body = {
        "analysis_head": ANALYSIS_HEAD,
        "analysis_spec": {
            "path": ANALYSIS_SPEC_RELATIVE,
            "file_sha256": file_sha256(root / ANALYSIS_SPEC_RELATIVE),
        },
        "claim_ceiling": claim,
        "controlled_subject_id": CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
        "exact_binomial_interval_status": "UNMEASURED_INTERVAL_AUTHORITY_INCOMPLETE",
        "exact_binomial_interval_reason": (
            "The frozen analysis spec requires exact binomial intervals for overlap "
            "counts but does not freeze the confidence level or exact method. This "
            "measurement therefore keeps the observed numerator/denominator and does "
            "not select 95%, Clopper-Pearson, or any other interval."
        ),
        "limitations": [
            "n_subjects = 1",
            "n_projects = 1",
            "exact-binomial interval authority is incomplete",
            "project-clustered uncertainty remains unidentifiable",
            "overlap measurement does not upgrade C3",
            "this task does not rerun ordinal-8 mutants or inventory a new project",
        ],
        "measurement_implementation_sha256": file_sha256(Path(__file__).resolve()),
        "mutant_tree_overlap_count": tree_overlap,
        "mutant_tree_pair_count": 4,
        "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
        "normalized_original_tree_sha256": NORMALIZED_ORIGINAL_TREE_SHA256,
        "normalized_patch_overlap_count": patch_overlap,
        "normalized_patch_pair_count": 4,
        "pairs": observations,
        "rq2_handoff": {
            "path": HANDOFF_RELATIVE,
            "file_sha256": HANDOFF_FILE_SHA256,
            "artifact_sha256": HANDOFF_ARTIFACT_SHA256,
        },
        "schema_version": SCHEMA_VERSION,
        "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        "source_identities": identities,
        "task_id": TASK_ID,
    }
    record = {**body, "artifact_sha256": canonical_sha256(body)}
    output.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(output, record, exclusive=True)
    return record


def main(argv: Sequence[str] | None = None) -> int:
    if argv:
        raise EvidenceError("E_MEASUREMENT_SELECTOR", "measurement arguments are rejected")
    measure_formal(Path.cwd())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
