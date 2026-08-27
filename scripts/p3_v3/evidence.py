#!/usr/bin/env python3
"""Thin CLI for the P3 v3 minimum evidence foundation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.applicability_predicates import load_applicability_authority  # noqa: E402
from p3_v3.artifacts import (  # noqa: E402
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    read_canonical_regular_bytes,
    read_canonical_regular_json,
    read_canonical_json,
    read_regular_file_snapshot,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import (  # noqa: E402
    SourceSnapshot,
    SourceSnapshotEntry,
    build_contract_inputs,
    build_common_inputs,
    build_public_behavior_frame,
    build_subject_frames,
    close_slot,
    derive_subject_material,
    derive_source_scale,
    rebuild_indexed_subject,
    run_adapter_discovery,
    select_profiling_workload,
    validate_adapter_registry,
    validate_contract_generator_registry,
    validate_input_generator_registry,
    validate_mr_inventory,
    validate_protocol,
    verify_pinned_bridge,
    verify_slot_chronology,
)
from p3_v3.packages import (  # noqa: E402
    PACKAGE_B_PRIMARY_CLASSES,
    PACKAGE_B_SENSITIVITY_CLASSES,
    build_package,
    verify_common_input_evidence,
    verify_materialized_package,
    verify_package,
)
from p3_v3.preflight import run_preflight  # noqa: E402
from p3_v3.pilot import reject_confirmatory_pilot  # noqa: E402
from p3_v3.run_records import (  # noqa: E402
    _verify_locked_execution_snapshot,
    close_phase,
    intent_template_sha256,
    recompute_p12_summary,
    validate_claim_ledger,
    verify_ledger,
    verify_phase_receipt,
)


def reject_confirmatory_artifact(value, context: str) -> None:
    reject_confirmatory_pilot(value, context)

SCIENTIFIC_PLAN_SHA256 = (
    "fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830"
)
EVIDENCE_DESIGN_SHA256 = (
    "7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9"
)

_AUTHORITY_LOCK_SCHEMA = {
    "schema_version": str,
    "task_id": str,
    "controller_repository": dict,
    "subjects": list,
    "governing_materials": dict,
    "protocol": dict,
    "registries": dict,
    "preflight": dict,
    "jobs": list,
    "claim_policy": dict,
}
_CONTROLLER_AUTHORITY_SCHEMA = {
    "normalized_repository_identity": str,
    "base_commit": str,
    "base_tree": str,
    "tracked_source_manifest_sha256": str,
}
_SUBJECT_AUTHORITY_SCHEMA = {
    "subject_id": str,
    "repository_role": str,
    "normalized_repository_identity": str,
    "base_commit": str,
    "base_tree": str,
    "tracked_source_manifest_sha256": str,
    "build_descriptor_sha256": str,
    "adapter_id": str,
}
_GOVERNING_AUTHORITY_SCHEMA = {
    "scientific_plan_sha256": str,
    "evidence_design_sha256": str,
    "authority_lock_design_sha256": str,
    "implementation_plan_sha256": str,
    "controller_implementation_manifest_sha256": str,
}
_PROTOCOL_AUTHORITY_SCHEMA = {
    "protocol_sha256": str,
    "rq_spec_sha256": str,
    "claim_ceiling_sha256": str,
    "p12_contract_sha256": str,
    "operator_catalogue_sha256": str,
    "mr_policy_sha256": str,
    "site_policy_sha256": str,
    "analysis_spec_sha256": str,
    "package_policy_sha256": str,
    "environment_lock_sha256": str,
    "job_derivation_policy_sha256": str,
}
_REGISTRY_AUTHORITY_SCHEMA = {
    "adapter_registry_sha256": str,
    "input_generator_registry_sha256": str,
}
_PREFLIGHT_AUTHORITY_SCHEMA = {
    "normalized_repository_identity": str,
    "base_commit": str,
    "base_tree": str,
    "dependency_lock_sha256": str,
    "environment_policy_sha256": str,
    "required_capabilities": list,
    "forbidden_credential_fields": list,
}
_JOB_AUTHORITY_SCHEMA = {
    "job_id": str,
    "phase": str,
    "job_role": str,
    "object_identity": str,
    "input_identity_sha256": str,
    "intent_template_sha256": str,
    "maximum_attempts": int,
    "retry_trigger": str,
    "execution_class": str,
    "p12_access_class": str,
}
_CLAIM_POLICY_AUTHORITY_SCHEMA = {
    "claim_ceiling_sha256": str,
    "required_status": str,
    "rq_ids": list,
}
_GIT_OBJECT_RE = re.compile(r"[0-9a-f]{40}")
_CREDENTIAL_FIELD_NAMES = frozenset(
    {"authorization", "credential", "password", "token"}
)
_SAFE_CREDENTIAL_POLICY_FIELDS = frozenset({"forbidden_credential_fields"})
_CREDENTIAL_METADATA_COMPONENTS = _CREDENTIAL_FIELD_NAMES | frozenset(
    {"key", "secret"}
)
_NON_CREDENTIAL_KEY_FIELDS = frozenset(
    {
        "provenance_span_or_key",
        "schema_provenance_span_or_key",
        "schema_selection_key",
    }
)
_BEARER_VALUE_RE = re.compile(r"(?i)(?<![^\W_])bearer[ \t]+[^\s]+")
_USERINFO_VALUE_RE = re.compile(
    r"(?i)\b[a-z][a-z0-9+.-]*://[^/\s@]+@"
)
_REQUIRED_RQ_IDS = ("RQ1", "RQ2", "RQ3", "RQ4")
_REQUIRED_CLAIM_ASSOCIATIONS = (
    (
        "C1_ARTIFACT_FIRST_SEMANTIC_MUTANT_PROTOCOL",
        ("RQ1", "RQ2", "RQ3", "RQ4"),
    ),
    ("C2_CERTIFIED_MUTANTS_ACROSS_SCALES_TECHNIQUES", ("RQ1",)),
    ("C3_SEMANTIC_CONSTRUCT_DISTINCTNESS", ("RQ2",)),
    ("C4_FAMILY_AWARE_SMS_RESIDUAL_EXPLANATION", ("RQ3",)),
    ("C5_P12_CRITERION_INCREMENTAL_VALUE", ("RQ4",)),
    ("C6_UNIVERSAL_SUPERIORITY_CEILING", ("RQ3", "RQ4")),
    ("C7_LANGUAGE_INDEPENDENT_AUTOMATION_CEILING", ("RQ1",)),
    ("C8_PROFILING_REPRESENTATIVENESS_CEILING", ("RQ1",)),
)
_EXECUTION_CLASSES = frozenset(
    {"SYNTHETIC_INFRASTRUCTURE", "NON_SCIENTIFIC_CONTROL", "REAL_SCIENTIFIC"}
)
_P12_ACCESS_CLASSES = frozenset({"FORBIDDEN", "PERMITTED", "REQUIRED"})
_PREPARED_OBJECT_SOURCES = frozenset(
    {"SUBJECT", "SUBJECT_BEHAVIOR", "SUBJECT_COMMON_INPUT", "SYNTHETIC_P12_CASE"}
)
_PREPARED_FORBIDDEN_FIELDS = frozenset(
    {
        "base_intents",
        "jobs",
        "intent",
        "result",
        "completion",
        "execution_scope",
        "execution_class",
        "p12_access_class",
        "classes",
        "completed_intent",
    }
)
_PREPARED_AUTHORITY_SCHEMA = {
    "controller_repository": dict,
    "controller_manifest": dict,
    "subjects": list,
    "governing_materials": dict,
    "governing_artifacts": dict,
    "protocol": dict,
    "protocol_artifacts": dict,
    "registries": dict,
    "registry_artifacts": dict,
    "preflight": dict,
    "claim_policy": dict,
    "objects": list,
    "environments": list,
    "job_derivation_policy": dict,
}
_PREPARED_SUBJECT_SCHEMA = {
    "authority_row": dict,
    "source_manifest": dict,
    "build_descriptor": dict,
    "adapter_discovery": dict,
    "public_behavior_frame": dict,
    "profiling_workload": dict,
    "common_inputs": dict,
}
_PREPARED_OBJECT_SCHEMA = {
    "object_source": str,
    "inventory_id": str,
    "subject_id": str,
    "object_type": str,
    "object_id": str,
    "mr_id": str,
    "evaluation_input_class": str,
    "evaluation_input_id": str,
    "inputs": list,
}
_PREPARED_INPUT_SCHEMA = {"role": str, "sha256": str}
_PREPARED_ENVIRONMENT_SCHEMA = {
    "environment_role": str,
    "environment_id": str,
    "environment_sha256": str,
}
_JOB_DERIVATION_POLICY_SCHEMA = {
    "schema_version": str,
    "maximum_attempts": int,
    "retry_trigger": str,
    "templates": list,
}
_JOB_DERIVATION_TEMPLATE_SCHEMA = {
    "template_id": str,
    "phase": str,
    "job_role": str,
    "object_source": str,
    "argv_template": list,
    "cwd_role": str,
    "environment_role": str,
    "input_roles": list,
    "seed_rule": str,
    "timeout_seconds": int,
    "repetition_ids": list,
    "execution_class": str,
    "p12_access_class": str,
}
_ARGV_PLACEHOLDERS = frozenset(
    {
        "${protocol_sha256}",
        "${subject_id}",
        "${object_id}",
        "${evaluation_input_id}",
        "${environment_id}",
        "${repetition_id}",
    }
)
_CONTROLLER_ROLE_ROOTS = (
    "src/p3_v3",
    "scripts/p3_v3",
    "requirements-frozen.txt",
)
_TRACKED_SOURCE_MANIFEST_SCHEMA = {
    "schema_version": str,
    "role": str,
    "files": list,
}
_TRACKED_SOURCE_FILE_SCHEMA = {
    "relative_path": str,
    "mode": str,
    "sha256": str,
}
_LOCKED_REGISTRIES_SCHEMA = {
    "adapter_registry": dict,
    "input_generator_registry": dict,
}
_TRANSIENT_SOURCE_NAMES = frozenset(
    {
        ".mypy_cache",
        ".nox",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
)
_FIXED_GIT_BINARY_BY_PLATFORM = {
    "darwin": Path("/usr/bin/git"),
    "linux": Path("/usr/bin/git"),
}
_AUTHORITY_INPUTS_SCHEMA = {
    "schema_version": str,
    "task_id": str,
    "subjects": list,
    "governing_material_paths": dict,
    "protocol_artifact_paths": dict,
    "registry_artifact_paths": dict,
}
_AUTHORITY_INPUT_SUBJECT_SCHEMA = {
    "subject_id": str,
    "repository_role": str,
    "root": str,
    "build_descriptor_path": str,
    "adapter_id": str,
}
_GOVERNING_PATH_SCHEMA = {
    "scientific_plan": str,
    "evidence_design": str,
    "authority_lock_design": str,
    "implementation_plan": str,
}
_PROTOCOL_PATH_SCHEMA = {
    "protocol": str,
    "rq_spec": str,
    "claim_ceiling": str,
    "p12_contract": str,
    "operator_catalogue": str,
    "mr_policy": str,
    "site_policy": str,
    "analysis_spec": str,
    "package_policy": str,
    "environment_lock": str,
    "job_derivation_policy": str,
}
_REGISTRY_PATH_SCHEMA = {
    "adapter_registry": str,
    "input_generator_registry": str,
}
_RAW_AUTHORITY_BYTES_SCHEMA = {
    "schema_version": str,
    "relative_path": str,
    "sha256": str,
    "bytes_hex": str,
}
_ENVIRONMENT_LOCK_SCHEMA = {
    "schema_version": str,
    "required_capabilities": list,
    "forbidden_credential_fields": list,
    "environments": list,
}
_P12_CONTRACT_SCHEMA = {"schema_version": str, "synthetic_cases": list}
_SYNTHETIC_CASE_SCHEMA = {
    "inventory_id": str,
    "object_type": str,
    "object_id": str,
    "mr_id": str,
    "evaluation_input_class": str,
    "evaluation_input_id": str,
    "inputs": list,
}


def _authority_failure(detail: str) -> None:
    raise EvidenceError("E_AUTHORITY_LOCK_SCHEMA", detail)


def _require_authority(condition: bool, detail: str) -> None:
    if not condition:
        _authority_failure(detail)


def _validate_authority_text(value: str, field: str) -> str:
    _require_authority(bool(value) and not any(ord(char) < 32 for char in value), f"{field} is invalid")
    return value


def _validate_git_object(value: str, field: str) -> str:
    _require_authority(_GIT_OBJECT_RE.fullmatch(value) is not None, f"{field} is invalid")
    return value


def _validate_repository_identity(value: str, field: str) -> str:
    _validate_authority_text(value, field)
    unsafe = (
        "://" in value
        or "@" in value
        or "?" in value
        or "#" in value
        or "\\" in value
        or value.startswith("/")
    )
    if unsafe:
        raise EvidenceError(
            "E_CREDENTIAL_METADATA", f"{field} is not a normalized repository identity"
        )
    parts = value.split("/")
    _require_authority(
        len(parts) >= 2 and all(part not in {"", ".", ".."} for part in parts),
        f"{field} is invalid",
    )
    return value


def _reject_credential_metadata(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if isinstance(key, str):
                expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
                components = frozenset(
                    re.findall(r"[a-z0-9]+", expanded.casefold())
                )
                if (
                    key.casefold() not in _SAFE_CREDENTIAL_POLICY_FIELDS
                    and key.casefold() not in _NON_CREDENTIAL_KEY_FIELDS
                    and components & _CREDENTIAL_METADATA_COMPONENTS
                ):
                    raise EvidenceError(
                        "E_CREDENTIAL_METADATA",
                        "credential-bearing metadata field is forbidden",
                    )
            _reject_credential_metadata(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_credential_metadata(nested)
    elif isinstance(value, str) and (
        _BEARER_VALUE_RE.search(value) is not None
        or _USERINFO_VALUE_RE.search(value) is not None
    ):
        raise EvidenceError(
            "E_CREDENTIAL_METADATA", "credential-shaped metadata value is forbidden"
        )


def _lstat_directory_components(root: Path) -> Path:
    absolute = root if root.is_absolute() else Path.cwd() / root
    parts = absolute.parts
    current = Path(parts[0])
    try:
        for part in parts[1:]:
            current /= part
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_MANIFEST", "manifest root is not a safe directory"
                )
    except EvidenceError:
        raise
    except OSError as exc:
        raise EvidenceError(
            "E_AUTHORITY_MANIFEST", "manifest root is unavailable"
        ) from exc
    return absolute


def _project_git_mode(mode: int) -> str:
    return "100755" if mode & stat.S_IXUSR else "100644"


def _snapshot_from_captured_files(
    captured: Mapping[str, tuple[bytes, str]], paths: Sequence[str] | None = None
) -> SourceSnapshot:
    selected = list(captured) if paths is None else list(paths)
    entries = []
    for relative in sorted(selected, key=lambda value: value.encode("utf-8")):
        raw, mode = captured[relative]
        entries.append(
            SourceSnapshotEntry(
                relative_path=relative,
                mode=mode,
                sha256=hashlib.sha256(raw).hexdigest(),
                content=raw,
            )
        )
    return SourceSnapshot(entries=tuple(entries))


def _capture_declared_source_snapshot(
    root: Path, paths: Sequence[str], context: str
) -> SourceSnapshot:
    entries = []
    ordered = sorted(set(paths), key=lambda value: value.encode("utf-8"))
    for relative in ordered:
        safe_relative_path(relative)
        try:
            raw, mode = read_regular_file_snapshot(
                root / relative, f"{context} {relative}"
            )
        except EvidenceError as exc:
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", f"{context} cannot be captured safely"
            ) from exc
        entries.append(
            SourceSnapshotEntry(
                relative_path=relative,
                mode=_project_git_mode(mode),
                sha256=hashlib.sha256(raw).hexdigest(),
                content=raw,
            )
        )
    return SourceSnapshot(entries=tuple(entries))


def _validate_role_root_components(base: Path, relative: Path) -> None:
    current = base
    try:
        for index, part in enumerate(relative.parts):
            current /= part
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_MANIFEST", "manifest role root contains a symlink"
                )
            if index < len(relative.parts) - 1 and not stat.S_ISDIR(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_MANIFEST",
                    "manifest role root parent is not a directory",
                )
    except EvidenceError:
        raise
    except OSError as exc:
        raise EvidenceError(
            "E_AUTHORITY_MANIFEST", "manifest role root is unavailable"
        ) from exc


def _capture_tracked_source_manifest(
    root: Path, role_roots: Sequence[str], role: str
) -> tuple[dict[str, Any], SourceSnapshot]:
    """Inventory and capture every safe regular file below exact role roots."""

    base = _lstat_directory_components(Path(root))
    if not isinstance(role, str) or not role:
        raise EvidenceError("E_AUTHORITY_MANIFEST", "manifest role is invalid")
    if isinstance(role_roots, (str, bytes)) or not isinstance(role_roots, Sequence):
        raise EvidenceError("E_AUTHORITY_MANIFEST", "manifest role roots are invalid")
    root_names = list(role_roots)
    if not root_names or any(type(item) is not str for item in root_names):
        raise EvidenceError("E_AUTHORITY_MANIFEST", "manifest role roots are invalid")
    if role == "subject-source" and root_names != ["."]:
        raise EvidenceError(
            "E_AUTHORITY_MANIFEST", "subject manifest must cover the complete root"
        )
    if role == "controller-source" and tuple(root_names) != _CONTROLLER_ROLE_ROOTS:
        raise EvidenceError(
            "E_AUTHORITY_MANIFEST", "controller manifest role roots differ"
        )

    normalized = []
    for name in root_names:
        if name == ".":
            normalized.append(Path("."))
        else:
            try:
                normalized.append(Path(safe_relative_path(name).as_posix()))
            except EvidenceError as exc:
                raise EvidenceError(
                    "E_AUTHORITY_MANIFEST", "manifest role root is unsafe"
                ) from exc
    part_sets = [item.parts for item in normalized]
    if len(set(part_sets)) != len(part_sets):
        raise EvidenceError("E_AUTHORITY_MANIFEST", "manifest role roots overlap")
    for index, left in enumerate(part_sets):
        for right in part_sets[index + 1 :]:
            shorter = min(len(left), len(right))
            if left[:shorter] == right[:shorter]:
                raise EvidenceError("E_AUTHORITY_MANIFEST", "manifest role roots overlap")

    rows: list[dict[str, Any]] = []
    snapshot_entries: list[SourceSnapshotEntry] = []

    def visit(path: Path, relative: Path) -> None:
        try:
            info = path.lstat()
        except OSError as exc:
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "manifest node is unavailable"
            ) from exc
        if stat.S_ISLNK(info.st_mode):
            raise EvidenceError("E_AUTHORITY_MANIFEST", "manifest contains a symlink")
        if relative.name == ".git":
            if (
                role == "subject-source"
                and relative == Path(".git")
                and stat.S_ISDIR(info.st_mode)
            ):
                return
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "manifest contains forbidden .git metadata"
            )
        if any(part in _TRANSIENT_SOURCE_NAMES for part in relative.parts):
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "manifest contains a transient path"
            )
        if stat.S_ISDIR(info.st_mode):
            try:
                entries = sorted(os.scandir(path), key=lambda item: item.name.encode("utf-8"))
            except OSError as exc:
                raise EvidenceError(
                    "E_AUTHORITY_MANIFEST", "manifest directory could not be inventoried"
                ) from exc
            for entry in entries:
                child_relative = relative / entry.name if relative != Path(".") else Path(entry.name)
                visit(Path(entry.path), child_relative)
            return
        if not stat.S_ISREG(info.st_mode):
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "manifest contains a special node"
            )
        try:
            raw, opened_mode = read_regular_file_snapshot(
                path, f"manifest file {relative.as_posix()}"
            )
        except EvidenceError as exc:
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "manifest file could not be read safely"
            ) from exc
        mode = _project_git_mode(opened_mode)
        digest = hashlib.sha256(raw).hexdigest()
        rows.append(
            {
                "relative_path": relative.as_posix(),
                "mode": mode,
                "sha256": digest,
            }
        )
        snapshot_entries.append(
            SourceSnapshotEntry(
                relative_path=relative.as_posix(),
                mode=mode,
                sha256=digest,
                content=raw,
            )
        )

    for relative_root in normalized:
        _validate_role_root_components(base, relative_root)
        visit(base / relative_root, relative_root)
    rows.sort(key=lambda row: row["relative_path"].encode("utf-8"))
    if not rows:
        raise EvidenceError("E_AUTHORITY_MANIFEST", "manifest contains no source files")
    if len({row["relative_path"] for row in rows}) != len(rows):
        raise EvidenceError("E_AUTHORITY_MANIFEST", "manifest contains duplicate files")
    manifest = {
        "schema_version": "P3_V3_TRACKED_SOURCE_MANIFEST_V1",
        "role": role,
        "files": rows,
    }
    snapshot_entries.sort(key=lambda entry: entry.relative_path.encode("utf-8"))
    return manifest, SourceSnapshot(entries=tuple(snapshot_entries))


def build_tracked_source_manifest(
    root: Path, role_roots: Sequence[str], role: str
) -> dict[str, Any]:
    """Inventory every safe regular file below the exact roots for one role."""

    manifest, _snapshot = _capture_tracked_source_manifest(root, role_roots, role)
    return manifest


def verify_running_controller(
    lock: Mapping[str, Any],
    controller_manifest: Mapping[str, Any],
    locked_registries: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind installed verifier and registry bytes to the external lock."""

    try:
        _reject_credential_metadata(locked_registries)
        validated_lock = validate_authority_lock(lock)
        manifest = validate_exact_object(
            dict(controller_manifest),
            _TRACKED_SOURCE_MANIFEST_SCHEMA,
            "controller manifest",
        )
        if (
            manifest["schema_version"]
            != "P3_V3_TRACKED_SOURCE_MANIFEST_V1"
            or manifest["role"] != "controller-source"
            or canonical_sha256(manifest)
            != validated_lock["controller_repository"][
                "tracked_source_manifest_sha256"
            ]
        ):
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "controller manifest authority differs"
            )
        rows = [
            validate_exact_object(
                candidate,
                _TRACKED_SOURCE_FILE_SCHEMA,
                f"controller manifest files[{index}]",
            )
            for index, candidate in enumerate(manifest["files"])
        ]
        relative_paths = [row["relative_path"] for row in rows]
        if (
            not rows
            or relative_paths
            != sorted(relative_paths, key=lambda value: value.encode("utf-8"))
            or len(relative_paths) != len(set(relative_paths))
        ):
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "controller manifest rows differ"
            )
        installed_root = Path(__file__).resolve().parents[2]
        for row in rows:
            relative = safe_relative_path(row["relative_path"])
            if not any(
                relative.as_posix() == role_root
                or relative.as_posix().startswith(f"{role_root}/")
                for role_root in _CONTROLLER_ROLE_ROOTS
            ):
                raise EvidenceError(
                    "E_AUTHORITY_MANIFEST", "controller manifest path is not installed"
                )
            cursor = installed_root
            for part in relative.parts:
                cursor /= part
                try:
                    installed_node = cursor.lstat()
                except OSError as exc:
                    raise EvidenceError(
                        "E_AUTHORITY_MANIFEST",
                        "installed controller path is unavailable",
                    ) from exc
                if stat.S_ISLNK(installed_node.st_mode):
                    raise EvidenceError(
                        "E_AUTHORITY_MANIFEST", "installed controller path is unsafe"
                    )
            try:
                raw, mode = read_regular_file_snapshot(
                    cursor, f"installed controller {row['relative_path']}"
                )
            except EvidenceError as exc:
                raise EvidenceError(
                    "E_AUTHORITY_MANIFEST", "installed controller path is unsafe"
                ) from exc
            validate_sha256(row["sha256"], "controller manifest file digest")
            installed_mode = _project_git_mode(mode)
            if (
                hashlib.sha256(raw).hexdigest() != row["sha256"]
                or installed_mode != row["mode"]
            ):
                raise EvidenceError(
                    "E_AUTHORITY_MANIFEST", "installed controller bytes differ"
                )
        registries = validate_exact_object(
            dict(locked_registries),
            _LOCKED_REGISTRIES_SCHEMA,
            "locked registries",
        )
        if (
            canonical_sha256(registries["adapter_registry"])
            != validated_lock["registries"]["adapter_registry_sha256"]
            or canonical_sha256(registries["input_generator_registry"])
            != validated_lock["registries"]["input_generator_registry_sha256"]
        ):
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "locked registry bytes differ"
            )
        implementation_paths = [
            entry["implementation_path"]
            for registry_name, entries_field in (
                ("adapter_registry", "adapters"),
                ("input_generator_registry", "generators"),
            )
            for entry in registries[registry_name][entries_field]
        ]
        implementation_snapshot = _capture_declared_source_snapshot(
            installed_root,
            implementation_paths,
            "installed registry implementation",
        )
        return {
            "adapter_registry": validate_adapter_registry(
                registries["adapter_registry"], implementation_snapshot
            ),
            "input_generator_registry": validate_input_generator_registry(
                registries["input_generator_registry"], implementation_snapshot
            ),
        }
    except EvidenceError as exc:
        if exc.code in {"E_AUTHORITY_MANIFEST", "E_CREDENTIAL_METADATA"}:
            raise
        raise EvidenceError(
            "E_AUTHORITY_MANIFEST", "running controller authority is invalid"
        ) from exc


def _verify_running_controller_for_evidence(
    lock: Mapping[str, Any],
    controller_manifest: Mapping[str, Any],
    locked_registries: Mapping[str, Any],
    evidence_root: str | Path,
) -> dict[str, Any]:
    """Reject evidence-root implementations before invoking the public verifier."""

    try:
        _reject_credential_metadata(locked_registries)
        registries = validate_exact_object(
            dict(locked_registries),
            _LOCKED_REGISTRIES_SCHEMA,
            "locked registries",
        )
        installed_root = Path(__file__).resolve().parents[2]
        resolved_evidence_root = Path(evidence_root).resolve(strict=True)
        for registry_name, entries_field in (
            ("adapter_registry", "adapters"),
            ("input_generator_registry", "generators"),
        ):
            entries = registries[registry_name].get(entries_field)
            if type(entries) is not list:
                raise EvidenceError(
                    "E_AUTHORITY_MANIFEST", "locked registry entries are malformed"
                )
            for entry in entries:
                if not isinstance(entry, Mapping):
                    raise EvidenceError(
                        "E_AUTHORITY_MANIFEST", "locked registry entry is malformed"
                    )
                relative = safe_relative_path(entry.get("implementation_path"))
                resolved_implementation = (installed_root / relative).resolve(
                    strict=True
                )
                if resolved_implementation == resolved_evidence_root or (
                    resolved_implementation.is_relative_to(resolved_evidence_root)
                ):
                    raise EvidenceError(
                        "E_AUTHORITY_MANIFEST",
                        "registry implementation overlaps the evidence root",
                    )
    except EvidenceError as exc:
        if exc.code in {"E_AUTHORITY_MANIFEST", "E_CREDENTIAL_METADATA"}:
            raise
        raise EvidenceError(
            "E_AUTHORITY_MANIFEST", "registry implementation identity is invalid"
        ) from exc
    except OSError as exc:
        raise EvidenceError(
            "E_AUTHORITY_MANIFEST", "registry implementation identity is unavailable"
        ) from exc
    return verify_running_controller(lock, controller_manifest, registries)


def validate_authority_inputs(
    authority_inputs: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the non-authoritative, exact-schema freezer declaration."""

    _reject_credential_metadata(authority_inputs)
    try:
        snapshot = json.loads(canonical_json_bytes(authority_inputs).decode("utf-8"))
        value = validate_exact_object(
            snapshot, _AUTHORITY_INPUTS_SCHEMA, "authority inputs"
        )
        if value["schema_version"] != "P3_V3_AUTHORITY_INPUTS_V1":
            raise EvidenceError("E_AUTHORITY_INPUTS", "schema version differs")
        _validate_authority_text(value["task_id"], "authority inputs task_id")

        subjects: list[dict[str, Any]] = []
        for index, candidate in enumerate(value["subjects"]):
            subject = validate_exact_object(
                candidate,
                _AUTHORITY_INPUT_SUBJECT_SCHEMA,
                f"authority inputs subjects[{index}]",
            )
            for field in ("subject_id", "repository_role", "adapter_id"):
                _validate_authority_text(
                    subject[field], f"authority inputs subjects[{index}].{field}"
                )
            raw_root = subject["root"]
            if (
                not raw_root
                or "\\" in raw_root
                or "\x00" in raw_root
                or Path(raw_root).as_posix() != raw_root
                or any(part in {".", ".."} for part in Path(raw_root).parts)
            ):
                raise EvidenceError("E_AUTHORITY_INPUTS", "subject root is unsafe")
            safe_relative_path(subject["build_descriptor_path"])
            subjects.append(subject)
        subject_ids = [row["subject_id"] for row in subjects]
        repository_roles = [row["repository_role"] for row in subjects]
        if (
            not subjects
            or subject_ids != sorted(subject_ids)
            or len(subject_ids) != len(set(subject_ids))
            or len(repository_roles) != len(set(repository_roles))
        ):
            raise EvidenceError(
                "E_AUTHORITY_INPUTS", "subjects must be sorted and unique"
            )

        all_artifact_paths: list[str] = []
        for field, schema in (
            ("governing_material_paths", _GOVERNING_PATH_SCHEMA),
            ("protocol_artifact_paths", _PROTOCOL_PATH_SCHEMA),
            ("registry_artifact_paths", _REGISTRY_PATH_SCHEMA),
        ):
            paths = validate_exact_object(value[field], schema, f"authority inputs {field}")
            for path in paths.values():
                safe_relative_path(path)
                all_artifact_paths.append(path)
            if len(set(paths.values())) != len(paths):
                raise EvidenceError(
                    "E_AUTHORITY_INPUTS", f"{field} paths must be unique"
                )
        if len(all_artifact_paths) != len(set(all_artifact_paths)):
            raise EvidenceError(
                "E_AUTHORITY_INPUTS", "authority artifact paths must be globally unique"
            )
    except EvidenceError as exc:
        if exc.code == "E_AUTHORITY_INPUTS":
            raise
        raise EvidenceError(
            "E_AUTHORITY_INPUTS", "authority inputs schema differs"
        ) from exc
    return value


def _validated_fixed_git_binary() -> Path:
    candidate = _FIXED_GIT_BINARY_BY_PLATFORM.get(sys.platform)
    if candidate is None or not candidate.is_absolute():
        raise EvidenceError(
            "E_AUTHORITY_GIT", "platform has no fixed trusted Git binary"
        )
    current = Path(candidate.anchor)
    try:
        for index, part in enumerate(candidate.parts):
            if index:
                current /= part
            info = current.lstat()
            is_final = index == len(candidate.parts) - 1
            if stat.S_ISLNK(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "fixed Git binary path contains a symlink"
                )
            if info.st_uid != 0 or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "fixed Git binary path is caller-writable"
                )
            if is_final:
                if not stat.S_ISREG(info.st_mode) or not info.st_mode & (
                    stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                ):
                    raise EvidenceError(
                        "E_AUTHORITY_GIT", "fixed Git binary is not executable"
                    )
            elif not stat.S_ISDIR(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "fixed Git binary path is not a directory"
                )
        if current.resolve(strict=True) != candidate:
            raise EvidenceError(
                "E_AUTHORITY_GIT", "fixed Git binary path is not stable"
            )
    except EvidenceError:
        raise
    except (OSError, ValueError) as exc:
        raise EvidenceError(
            "E_AUTHORITY_GIT", "fixed trusted Git binary is unavailable"
        ) from exc
    return candidate


def _reject_executable_filter_config(raw: bytes) -> None:
    in_filter_section = False
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line or line.startswith((b"#", b";")):
            continue
        if line.startswith(b"["):
            closing = line.find(b"]")
            if closing < 0:
                in_filter_section = False
                continue
            section = line[1:closing].strip().split(None, 1)[0]
            normalized_section = section.lower()
            in_filter_section = normalized_section == b"filter" or (
                normalized_section.startswith(b"filter.")
            )
            continue
        if in_filter_section and re.match(
            rb"(?i)^(?:clean|process)(?:\s|=|$)", line
        ):
            raise EvidenceError(
                "E_AUTHORITY_GIT", "executable Git filters are forbidden"
            )


def _validated_local_git_metadata(root: Path) -> Path:
    metadata = root / ".git"
    try:
        metadata_info = metadata.lstat()
        if stat.S_ISLNK(metadata_info.st_mode) or not stat.S_ISDIR(
            metadata_info.st_mode
        ):
            raise EvidenceError(
                "E_AUTHORITY_GIT", "Git metadata must be an in-root directory"
            )
        metadata.resolve(strict=True).relative_to(root.resolve(strict=True))
        for current, directory_names, file_names in os.walk(
            metadata, followlinks=False
        ):
            for name in [*directory_names, *file_names]:
                candidate = Path(current) / name
                candidate_info = candidate.lstat()
                if stat.S_ISLNK(candidate_info.st_mode) or not (
                    stat.S_ISDIR(candidate_info.st_mode)
                    or stat.S_ISREG(candidate_info.st_mode)
                ):
                    raise EvidenceError(
                        "E_AUTHORITY_GIT", "Git metadata contains an unsafe node"
                    )
        for forbidden in (
            metadata / "commondir",
            metadata / "objects/info/alternates",
        ):
            try:
                forbidden.lstat()
            except FileNotFoundError:
                continue
            raise EvidenceError(
                "E_AUTHORITY_GIT", "external Git metadata indirection is forbidden"
            )

        for config in (metadata / "config", metadata / "config.worktree"):
            try:
                config_info = config.lstat()
            except FileNotFoundError:
                continue
            if stat.S_ISLNK(config_info.st_mode) or not stat.S_ISREG(
                config_info.st_mode
            ):
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "Git configuration metadata is unsafe"
                )
            raw, _mode = read_regular_file_snapshot(config, "local Git configuration")
            if re.search(
                rb"(?im)^\s*\[\s*include(?:if\b[^]]*)?\s*]", raw
            ) is not None:
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "Git configuration includes are forbidden"
                )
            _reject_executable_filter_config(raw)
    except EvidenceError:
        raise
    except (OSError, ValueError) as exc:
        raise EvidenceError(
            "E_AUTHORITY_GIT", "Git metadata boundary is unavailable"
        ) from exc
    return metadata


def _run_fixed_git_queries(root: Path) -> dict[str, Any]:
    git_binary = _validated_fixed_git_binary()
    metadata = _validated_local_git_metadata(root)
    outputs: dict[tuple[str, ...], bytes] = {}
    fixed_config = (
        "core.fsmonitor=false",
        f"core.hooksPath={os.devnull}",
        "core.pager=",
        "credential.helper=",
        "credential.interactive=never",
        "core.useReplaceRefs=false",
        "protocol.allow=never",
    )
    fixed_config_argv = [
        item
        for setting in fixed_config
        for item in ("-c", setting)
    ]
    git_env = {
        "LANG": "C",
        "LC_ALL": "C",
        "TMPDIR": "/tmp",
        "GIT_ATTR_NOSYSTEM": "1",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_DIR": str(metadata),
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "",
        "PAGER": "",
    }

    def run_query(query: tuple[str, ...]) -> bytes:
        try:
            result = subprocess.run(
                [str(git_binary), "-C", str(root), *fixed_config_argv, *query],
                capture_output=True,
                check=False,
                env=git_env,
            )
        except (OSError, ValueError) as exc:
            raise EvidenceError(
                "E_AUTHORITY_GIT", "fixed read-only Git query failed"
            ) from exc
        if (
            result.returncode != 0
            or not isinstance(result.stdout, bytes)
            or result.stderr != b""
        ):
            raise EvidenceError(
                "E_AUTHORITY_GIT", "fixed read-only Git query failed"
            )
        outputs[query] = result.stdout
        return result.stdout

    def object_id(raw: bytes) -> str:
        try:
            value = raw[:-1].decode("ascii") if raw.endswith(b"\n") else ""
        except UnicodeDecodeError as exc:
            raise EvidenceError("E_AUTHORITY_GIT", "Git object output is malformed") from exc
        if len(raw) != 41 or _GIT_OBJECT_RE.fullmatch(value) is None:
            raise EvidenceError("E_AUTHORITY_GIT", "Git object output is malformed")
        return value

    head_query = ("rev-parse", "HEAD")
    base_commit = object_id(run_query(head_query))
    tree_query = ("rev-parse", f"{base_commit}^{{tree}}")
    base_tree = object_id(run_query(tree_query))
    for query in (
        ("remote", "get-url", "origin"),
        ("ls-files", "--stage", "-z"),
    ):
        run_query(query)

    origin_raw = outputs[("remote", "get-url", "origin")]
    if not origin_raw.endswith(b"\n") or origin_raw.count(b"\n") != 1:
        raise EvidenceError("E_AUTHORITY_GIT", "Git origin output is malformed")
    try:
        origin = origin_raw[:-1].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceError("E_AUTHORITY_GIT", "Git origin output is malformed") from exc
    tracked_raw = outputs[("ls-files", "--stage", "-z")]
    if tracked_raw and not tracked_raw.endswith(b"\0"):
        raise EvidenceError("E_AUTHORITY_GIT", "Git tracked inventory is malformed")
    tracked_entries: list[dict[str, Any]] = []
    try:
        for raw_record in tracked_raw.split(b"\0"):
            if not raw_record:
                continue
            header, separator, raw_path = raw_record.partition(b"\t")
            fields = header.split(b" ")
            if not separator or len(fields) != 3:
                raise ValueError("stage row shape differs")
            raw_mode, raw_oid, raw_stage = fields
            mode = raw_mode.decode("ascii")
            blob_oid = raw_oid.decode("ascii")
            stage_text = raw_stage.decode("ascii")
            path = raw_path.decode("utf-8")
            if (
                mode not in {"100644", "100755"}
                or _GIT_OBJECT_RE.fullmatch(blob_oid) is None
                or stage_text != "0"
                or safe_relative_path(path).as_posix() != path
            ):
                raise ValueError("stage row value differs")
            tracked_entries.append(
                {
                    "mode": mode,
                    "blob_oid": blob_oid,
                    "stage": 0,
                    "path": path,
                }
            )
    except (UnicodeDecodeError, ValueError, EvidenceError) as exc:
        raise EvidenceError(
            "E_AUTHORITY_GIT", "Git tracked inventory is malformed"
        ) from exc
    tracked = [entry["path"] for entry in tracked_entries]
    if (
        tracked != sorted(tracked, key=lambda value: value.encode("utf-8"))
        or len(tracked) != len(set(tracked))
        or any(
            not item
            or "\\" in item
            or "\x00" in item
            or Path(item).is_absolute()
            or any(part in {"", ".", ".."} for part in item.split("/"))
            for item in tracked
        )
    ):
        raise EvidenceError("E_AUTHORITY_GIT", "Git tracked inventory is malformed")
    if not tracked_entries or _git_tree_oid(tracked_entries) != base_tree:
        raise EvidenceError(
            "E_AUTHORITY_GIT", "Git staged inventory differs from fixed HEAD tree"
        )
    return {
        "base_commit": base_commit,
        "base_tree": base_tree,
        "origin": origin,
        "tracked": tracked,
        "tracked_entries": tracked_entries,
    }


def _git_blob_oid(raw: bytes) -> str:
    payload = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    return hashlib.sha1(payload, usedforsecurity=False).hexdigest()


def _git_tree_oid(entries: Sequence[Mapping[str, Any]]) -> str:
    root: dict[str, Any] = {}
    for entry in entries:
        components = entry["path"].split("/")
        node = root
        for component in components[:-1]:
            child = node.setdefault(component, {})
            if not isinstance(child, dict):
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "Git inventory has a file/directory collision"
                )
            node = child
        leaf = components[-1]
        if leaf in node:
            raise EvidenceError(
                "E_AUTHORITY_GIT", "Git inventory has a duplicate tree entry"
            )
        node[leaf] = (entry["mode"], entry["blob_oid"])

    def tree_oid(node: Mapping[str, Any]) -> str:
        encoded: list[tuple[bytes, bytes]] = []
        for name, value in node.items():
            raw_name = name.encode("utf-8")
            if isinstance(value, dict):
                mode = b"40000"
                oid = tree_oid(value)
                sort_key = raw_name + b"/"
            else:
                mode = value[0].encode("ascii")
                oid = value[1]
                sort_key = raw_name
            row = mode + b" " + raw_name + b"\0" + bytes.fromhex(oid)
            encoded.append((sort_key, row))
        body = b"".join(row for _key, row in sorted(encoded))
        payload = b"tree " + str(len(body)).encode("ascii") + b"\0" + body
        return hashlib.sha1(payload, usedforsecurity=False).hexdigest()

    return tree_oid(root)


def _read_checkout_file_snapshot(
    directory_fd: int, name: str, relative_path: str
) -> tuple[bytes, int]:
    fd: int | None = None
    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        fd = os.open(name, flags, dir_fd=directory_fd)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise EvidenceError(
                "E_AUTHORITY_GIT", "checkout file is not regular"
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                return b"".join(chunks), os.fstat(fd).st_mode
            chunks.append(chunk)
    except EvidenceError:
        raise
    except OSError as exc:
        raise EvidenceError(
            "E_AUTHORITY_GIT",
            f"checkout file {relative_path!r} could not be snapshotted",
        ) from exc
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


def _open_checkout_root(root: Path, directory_flags: int) -> int:
    absolute = root if root.is_absolute() else Path.cwd() / root
    components = absolute.parts[1:]
    if any(
        component in {"", ".", ".."} or "\x00" in component
        for component in components
    ):
        raise EvidenceError("E_AUTHORITY_GIT", "checkout root is unsafe")
    current_fd: int | None = None
    try:
        current_fd = os.open(absolute.parts[0], directory_flags)
        for component in components:
            next_fd = os.open(component, directory_flags, dir_fd=current_fd)
            previous_fd = current_fd
            current_fd = next_fd
            os.close(previous_fd)
        return current_fd
    except OSError as exc:
        if current_fd is not None:
            try:
                os.close(current_fd)
            except OSError:
                pass
        raise EvidenceError(
            "E_AUTHORITY_GIT", "checkout root could not be anchored"
        ) from exc


def _capture_git_checkout_snapshot(
    root: Path,
    entries: Sequence[Mapping[str, Any]],
    separate_checkout_roots: Sequence[str] = (),
) -> dict[str, tuple[bytes, str]]:
    expected = {entry["path"]: entry for entry in entries}
    try:
        separate = frozenset(
            safe_relative_path(value).as_posix()
            for value in separate_checkout_roots
        )
    except EvidenceError as exc:
        raise EvidenceError(
            "E_AUTHORITY_GIT", "separate checkout root is unsafe"
        ) from exc
    if any(
        path == checkout or path.startswith(f"{checkout}/")
        for path in expected
        for checkout in separate
    ):
        raise EvidenceError(
            "E_AUTHORITY_GIT", "separate checkout overlaps fixed HEAD"
        )
    expected_directories = frozenset(
        "/".join(path.split("/")[:depth])
        for path in expected
        for depth in range(1, len(path.split("/")))
    )
    captured: dict[str, tuple[bytes, str]] = {}
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )

    def visit(directory_fd: int, relative: Path) -> None:
        try:
            with os.scandir(directory_fd) as iterator:
                children = sorted(
                    (child.name for child in iterator),
                    key=lambda name: name.encode("utf-8"),
                )
        except (OSError, UnicodeError) as exc:
            raise EvidenceError(
                "E_AUTHORITY_GIT", "checkout directory could not be inventoried"
            ) from exc
        for name in children:
            child_relative = (
                Path(name) if relative == Path(".") else relative / name
            )
            try:
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except OSError as exc:
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "checkout node is unavailable"
                ) from exc
            if child_relative == Path(".git"):
                if stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode):
                    continue
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "checkout .git node is unsafe"
                )
            if child_relative.name == ".git":
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "nested checkout .git metadata is forbidden"
                )
            if stat.S_ISLNK(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "checkout contains a symlink"
                )
            relative_text = child_relative.as_posix()
            if relative_text in separate:
                if not stat.S_ISDIR(info.st_mode):
                    raise EvidenceError(
                        "E_AUTHORITY_GIT",
                        "separate checkout root is not a directory",
                    )
                continue
            if any(
                part in _TRANSIENT_SOURCE_NAMES for part in child_relative.parts
            ):
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "checkout contains a transient path"
                )
            if stat.S_ISDIR(info.st_mode):
                if not (
                    relative_text in expected_directories
                    or any(
                        checkout.startswith(f"{relative_text}/")
                        for checkout in separate
                    )
                ):
                    raise EvidenceError(
                        "E_AUTHORITY_GIT",
                        "checkout contains an undeclared directory",
                    )
                child_fd: int | None = None
                try:
                    child_fd = os.open(
                        name, directory_flags, dir_fd=directory_fd
                    )
                    if not stat.S_ISDIR(os.fstat(child_fd).st_mode):
                        raise EvidenceError(
                            "E_AUTHORITY_GIT",
                            "checkout directory is unavailable",
                        )
                    visit(child_fd, child_relative)
                except EvidenceError:
                    raise
                except OSError as exc:
                    raise EvidenceError(
                        "E_AUTHORITY_GIT",
                        "checkout directory could not be anchored",
                    ) from exc
                finally:
                    if child_fd is not None:
                        try:
                            os.close(child_fd)
                        except OSError:
                            pass
                continue
            if not stat.S_ISREG(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "checkout contains a special node"
                )
            try:
                safe_relative_path(relative_text)
                raw, opened_mode = _read_checkout_file_snapshot(
                    directory_fd, name, relative_text
                )
            except EvidenceError as exc:
                raise EvidenceError(
                    "E_AUTHORITY_GIT", "checkout file could not be snapshotted"
                ) from exc
            captured[relative_text] = (raw, _project_git_mode(opened_mode))

    root_fd: int | None = None
    try:
        root_fd = _open_checkout_root(root, directory_flags)
        if not stat.S_ISDIR(os.fstat(root_fd).st_mode):
            raise EvidenceError(
                "E_AUTHORITY_GIT", "checkout root is not a directory"
            )
        visit(root_fd, Path("."))
    except EvidenceError:
        raise
    except OSError as exc:
        raise EvidenceError(
            "E_AUTHORITY_GIT", "checkout root could not be anchored"
        ) from exc
    finally:
        if root_fd is not None:
            try:
                os.close(root_fd)
            except OSError:
                pass
    if set(captured) != set(expected):
        raise EvidenceError(
            "E_AUTHORITY_GIT", "checkout inventory differs from fixed HEAD"
        )
    for path, entry in expected.items():
        raw, mode = captured[path]
        if mode != entry["mode"] or _git_blob_oid(raw) != entry["blob_oid"]:
            raise EvidenceError(
                "E_AUTHORITY_GIT", "live tracked bytes differ from fixed HEAD"
            )
    return {path: captured[path] for path in expected}


def _capture_complete_controller_source_manifest(root: Path) -> dict[str, Any]:
    """Capture the complete controller-source tree and admit only fixed role roots."""

    role_roots = tuple(Path(value).as_posix() for value in _CONTROLLER_ROLE_ROOTS)
    captured: dict[str, tuple[bytes, str]] = {}
    directories: set[str] = set()
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )

    def related_to_role_root(relative: str) -> bool:
        return any(
            relative == role_root
            or relative.startswith(f"{role_root}/")
            or role_root.startswith(f"{relative}/")
            for role_root in role_roots
        )

    def manifest_failure(detail: str, exc: BaseException | None = None) -> None:
        error = EvidenceError("E_AUTHORITY_MANIFEST", detail)
        if exc is None:
            raise error
        raise error from exc

    def visit(directory_fd: int, relative: Path) -> None:
        try:
            with os.scandir(directory_fd) as iterator:
                children = sorted(
                    (child.name for child in iterator),
                    key=lambda name: name.encode("utf-8"),
                )
        except (OSError, UnicodeError) as exc:
            manifest_failure("controller source directory could not be inventoried", exc)
        for name in children:
            child_relative = (
                Path(name) if relative == Path(".") else relative / name
            )
            relative_text = child_relative.as_posix()
            try:
                safe_relative_path(relative_text)
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except (EvidenceError, OSError) as exc:
                manifest_failure("controller source node is unavailable", exc)
            if child_relative.name == ".git":
                manifest_failure("controller source contains forbidden .git metadata")
            if any(part in _TRANSIENT_SOURCE_NAMES for part in child_relative.parts):
                manifest_failure("controller source contains a transient path")
            if stat.S_ISLNK(info.st_mode):
                manifest_failure("controller source contains a symlink")
            if stat.S_ISDIR(info.st_mode):
                if not related_to_role_root(relative_text):
                    manifest_failure("controller source contains an undeclared directory")
                directories.add(relative_text)
                child_fd: int | None = None
                try:
                    child_fd = os.open(
                        name, directory_flags, dir_fd=directory_fd
                    )
                    if not stat.S_ISDIR(os.fstat(child_fd).st_mode):
                        manifest_failure("controller source directory is unavailable")
                    visit(child_fd, child_relative)
                except EvidenceError:
                    raise
                except OSError as exc:
                    manifest_failure(
                        "controller source directory could not be anchored", exc
                    )
                finally:
                    if child_fd is not None:
                        try:
                            os.close(child_fd)
                        except OSError:
                            pass
                continue
            if not stat.S_ISREG(info.st_mode):
                manifest_failure("controller source contains a special node")
            if not any(
                relative_text == role_root
                or relative_text.startswith(f"{role_root}/")
                for role_root in role_roots
            ):
                manifest_failure("controller source contains an undeclared file")
            try:
                raw, opened_mode = _read_checkout_file_snapshot(
                    directory_fd, name, relative_text
                )
            except EvidenceError as exc:
                manifest_failure("controller source file could not be snapshotted", exc)
            captured[relative_text] = (raw, _project_git_mode(opened_mode))

    root_fd: int | None = None
    try:
        root_fd = _open_checkout_root(root, directory_flags)
        if not stat.S_ISDIR(os.fstat(root_fd).st_mode):
            manifest_failure("controller source root is not a directory")
        visit(root_fd, Path("."))
    except EvidenceError as exc:
        if exc.code == "E_AUTHORITY_MANIFEST":
            raise
        manifest_failure("controller source root could not be anchored", exc)
    except OSError as exc:
        manifest_failure("controller source root could not be anchored", exc)
    finally:
        if root_fd is not None:
            try:
                os.close(root_fd)
            except OSError:
                pass

    if any(role_root not in captured and role_root not in directories for role_root in role_roots):
        manifest_failure("controller source role root is unavailable")
    expected_directories = {
        "/".join(path.split("/")[:depth])
        for path in (*captured, *role_roots)
        for depth in range(1, len(path.split("/")))
    }
    expected_directories.update(
        role_root for role_root in role_roots if role_root in directories
    )
    if directories != expected_directories:
        manifest_failure("controller source directory inventory differs")
    ordered = sorted(captured, key=lambda value: value.encode("utf-8"))
    if not ordered:
        manifest_failure("controller source manifest contains no files")
    return {
        "schema_version": "P3_V3_TRACKED_SOURCE_MANIFEST_V1",
        "role": "controller-source",
        "files": [
            {
                "relative_path": path,
                "mode": captured[path][1],
                "sha256": hashlib.sha256(captured[path][0]).hexdigest(),
            }
            for path in ordered
        ],
    }


def _manifest_from_git_snapshot(
    snapshot: Mapping[str, tuple[bytes, str]],
    tracked_paths: Sequence[str],
    role: str,
) -> dict[str, Any]:
    return {
        "schema_version": "P3_V3_TRACKED_SOURCE_MANIFEST_V1",
        "role": role,
        "files": [
            {
                "relative_path": path,
                "mode": snapshot[path][1],
                "sha256": hashlib.sha256(snapshot[path][0]).hexdigest(),
            }
            for path in tracked_paths
        ],
    }


def _snapshot_canonical_json(
    snapshot: SourceSnapshot, path: str, context: str
) -> dict[str, Any]:
    try:
        raw = snapshot.read_bytes(path)
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
        if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
            raise ValueError("canonical object differs")
        return value
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError(
            "E_AUTHORITY_GIT", f"{context} is not a tracked canonical snapshot"
        ) from exc


def _normalize_git_origin(origin: str) -> str:
    try:
        if "://" in origin:
            parsed = urlsplit(origin)
            host = parsed.hostname
            path = unquote(parsed.path)
        else:
            remote, separator, path = origin.partition(":")
            if not separator:
                raise ValueError("origin has no host/path separator")
            host = remote.rsplit("@", 1)[-1]
        if not host:
            raise ValueError("origin host is absent")
        path = path.strip("/")
        if path.endswith(".git"):
            path = path[:-4]
        identity = f"{host.casefold()}/{path}"
        return _validate_repository_identity(identity, "normalized Git origin")
    except (EvidenceError, UnicodeError, ValueError) as exc:
        raise EvidenceError(
            "E_AUTHORITY_GIT", "Git origin cannot be normalized safely"
        ) from exc


def _checkout_authority(
    root: Path,
    role_roots: Sequence[str],
    role: str,
    separate_checkout_roots: Sequence[str] = (),
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    tuple[str, ...],
    SourceSnapshot,
]:
    safe_root = _lstat_directory_components(root)
    git = _run_fixed_git_queries(safe_root)
    captured = _capture_git_checkout_snapshot(
        safe_root,
        git["tracked_entries"],
        separate_checkout_roots,
    )
    if role == "controller-source":
        tracked = [
            item
            for item in git["tracked"]
            if any(item == root_name or item.startswith(f"{root_name}/") for root_name in role_roots)
        ]
    else:
        tracked = git["tracked"]
    manifest = _manifest_from_git_snapshot(captured, tracked, role)
    snapshot = _snapshot_from_captured_files(captured)
    return (
        {
            "normalized_repository_identity": _normalize_git_origin(git["origin"]),
            "base_commit": git["base_commit"],
            "base_tree": git["base_tree"],
            "tracked_source_manifest_sha256": canonical_sha256(manifest),
        },
        manifest,
        tuple(git["tracked"]),
        snapshot,
    )


def _require_tracked_paths(
    tracked: Sequence[str], required: Sequence[str], context: str
) -> None:
    tracked_set = set(tracked)
    if any(path not in tracked_set for path in required):
        raise EvidenceError(
            "E_AUTHORITY_GIT", f"{context} contains untracked authority bytes"
        )


def _registered_implementation_paths(
    registry_relative_path: str, entries: Any
) -> list[str]:
    safe_relative_path(registry_relative_path)
    if type(entries) is not list:
        raise EvidenceError(
            "E_AUTHORITY_GIT", "registry implementation declarations are malformed"
        )
    paths = []
    for entry in entries:
        if not isinstance(entry, Mapping) or type(entry.get("implementation_path")) is not str:
            raise EvidenceError(
                "E_AUTHORITY_GIT", "registry implementation declaration is malformed"
            )
        implementation = safe_relative_path(entry.get("implementation_path"))
        paths.append(implementation.as_posix())
    return paths


def _raw_authority_envelope(
    controller_root: Path,
    relative_path: str,
    context: str,
    *,
    raw: bytes | None = None,
) -> tuple[dict[str, Any], str]:
    if raw is None:
        raw = read_canonical_regular_bytes(controller_root / relative_path, context)
    digest = hashlib.sha256(raw).hexdigest()
    return (
        {
            "schema_version": "P3_V3_RAW_AUTHORITY_BYTES_V1",
            "relative_path": relative_path,
            "sha256": digest,
            "bytes_hex": raw.hex(),
        },
        digest,
    )


def _rq_ids_from_spec_bytes(raw: bytes) -> list[str]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceError("E_CLAIM_SET", "RQ authority is not UTF-8 Markdown") from exc
    rq_ids = re.findall(
        r"^### (RQ[0-9]+)(?:：|[ \t]+[—-][ \t]+)",
        text,
        flags=re.MULTILINE,
    )
    if not rq_ids:
        raise EvidenceError("E_CLAIM_SET", "RQ authority has no research questions")
    if rq_ids != list(_REQUIRED_RQ_IDS):
        raise EvidenceError(
            "E_CLAIM_SET",
            "RQ authority headings must exactly enumerate RQ1 through RQ4 in order",
        )
    return rq_ids


def _validate_environment_lock(artifact: Mapping[str, Any]) -> dict[str, Any]:
    value = validate_exact_object(
        dict(artifact), _ENVIRONMENT_LOCK_SCHEMA, "environment lock"
    )
    if value["schema_version"] != "P3_V3_ENVIRONMENT_LOCK_V1":
        _authority_failure("environment lock schema version differs")
    for field in ("required_capabilities", "forbidden_credential_fields"):
        items = value[field]
        _require_authority(
            bool(items)
            and all(type(item) is str and bool(item) for item in items)
            and items == sorted(items)
            and len(items) == len(set(items)),
            f"environment lock {field} differs",
        )
    _require_authority(
        value["forbidden_credential_fields"] == sorted(_CREDENTIAL_FIELD_NAMES),
        "environment lock forbidden credential fields differ",
    )
    environments = []
    for index, candidate in enumerate(value["environments"]):
        row = validate_exact_object(
            candidate,
            _PREPARED_ENVIRONMENT_SCHEMA,
            f"environment lock environments[{index}]",
        )
        for field in ("environment_role", "environment_id"):
            _validate_authority_text(row[field], f"environment lock {field}")
        validate_sha256(row["environment_sha256"], "environment lock digest")
        environments.append(row)
    roles = [row["environment_role"] for row in environments]
    _require_authority(
        bool(environments)
        and roles == sorted(roles)
        and len(roles) == len(set(roles)),
        "environment lock environments are not sorted and unique",
    )
    return value


def _synthetic_objects(artifact: Mapping[str, Any]) -> list[dict[str, Any]]:
    value = validate_exact_object(dict(artifact), _P12_CONTRACT_SCHEMA, "P12 contract")
    _require_authority(
        value["schema_version"] == "P3_V3_P12_CONTRACT_V1",
        "P12 contract schema version differs",
    )
    objects = []
    for index, candidate in enumerate(value["synthetic_cases"]):
        case = validate_exact_object(
            candidate, _SYNTHETIC_CASE_SCHEMA, f"P12 synthetic_cases[{index}]"
        )
        inputs = []
        for input_index, candidate_input in enumerate(case["inputs"]):
            input_row = validate_exact_object(
                candidate_input,
                _PREPARED_INPUT_SCHEMA,
                f"P12 synthetic_cases[{index}].inputs[{input_index}]",
            )
            _validate_authority_text(input_row["role"], "P12 synthetic input role")
            validate_sha256(input_row["sha256"], "P12 synthetic input digest")
            inputs.append(input_row)
        roles = [row["role"] for row in inputs]
        _require_authority(
            bool(inputs)
            and roles == sorted(roles)
            and len(roles) == len(set(roles)),
            "P12 synthetic inputs are not sorted and unique",
        )
        for field in _SYNTHETIC_CASE_SCHEMA:
            if field != "inputs":
                _validate_authority_text(case[field], f"P12 synthetic case {field}")
        objects.append(
            {
                "object_source": "SYNTHETIC_P12_CASE",
                "subject_id": "",
                **case,
                "inputs": inputs,
            }
        )
    inventory_ids = [row["inventory_id"] for row in objects]
    _require_authority(
        inventory_ids == sorted(inventory_ids)
        and len(inventory_ids) == len(set(inventory_ids)),
        "P12 synthetic cases are not sorted and unique",
    )
    return objects


def _validate_claim_ceiling_authority(
    artifact: Mapping[str, Any],
) -> dict[str, Any]:
    value = validate_exact_object(
        dict(artifact), _CLAIM_CEILING_SCHEMA, "claim_ceiling_authority"
    )
    if value["schema_version"] != "p3-claim-ceiling-authority-v1":
        raise EvidenceError("E_CLAIM_SET", "claim ceiling authority version differs")
    body = {key: nested for key, nested in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_CLAIM_SET", "claim ceiling authority hash differs")
    claims = [
        validate_exact_object(
            candidate,
            _CLAIM_AUTHORITY_ROW_SCHEMA,
            f"claim_ceiling_authority.claims[{index}]",
        )
        for index, candidate in enumerate(value["claims"])
    ]
    claim_ids = [claim["claim_id"] for claim in claims]
    if (
        not claim_ids
        or claim_ids != list(dict.fromkeys(claim_ids))
        or any(
            claim["initial_status"] != "blocked"
            or not claim["rqs"]
            or claim["rqs"] != sorted(set(claim["rqs"]))
            or any(type(rq) is not str or not rq for rq in claim["rqs"])
            for claim in claims
        )
    ):
        raise EvidenceError("E_CLAIM_SET", "claim ceiling authority differs")
    return value


def _validate_rq_claim_authority(
    rq_spec_raw: bytes,
    claim_ceiling: Mapping[str, Any],
    *,
    scientific_plan_raw: bytes | None = None,
) -> list[str]:
    rq_ids = _rq_ids_from_spec_bytes(rq_spec_raw)
    required_rqs = list(_REQUIRED_RQ_IDS)
    if rq_ids != required_rqs:
        raise EvidenceError(
            "E_CLAIM_SET", "RQ authority must exactly enumerate RQ1 through RQ4"
        )
    if (
        scientific_plan_raw is not None
        and _rq_ids_from_spec_bytes(scientific_plan_raw) != required_rqs
    ):
        raise EvidenceError(
            "E_CLAIM_SET",
            "scientific plan and RQ authority do not exactly enumerate RQ1 through RQ4",
        )
    authority = _validate_claim_ceiling_authority(claim_ceiling)
    observed = tuple(
        (claim["claim_id"], tuple(claim["rqs"])) for claim in authority["claims"]
    )
    if observed != _REQUIRED_CLAIM_ASSOCIATIONS:
        raise EvidenceError(
            "E_CLAIM_SET", "claim authority differs from the governing claim table"
        )
    return rq_ids


def _subject_objects(
    subject: Mapping[str, Any], registries: Mapping[str, str]
) -> list[dict[str, Any]]:
    authority = subject["authority_row"]
    subject_id = authority["subject_id"]
    shared = [
        {
            "role": "ADAPTER_REGISTRY",
            "sha256": registries["adapter_registry_sha256"],
        },
        {"role": "BUILD_DESCRIPTOR", "sha256": authority["build_descriptor_sha256"]},
        {
            "role": "COMMON_INPUT_INVENTORY",
            "sha256": canonical_sha256(subject["common_inputs"]),
        },
        {
            "role": "INPUT_GENERATOR_REGISTRY",
            "sha256": registries["input_generator_registry_sha256"],
        },
        {
            "role": "PUBLIC_BEHAVIOR_FRAME",
            "sha256": canonical_sha256(subject["public_behavior_frame"]),
        },
        {
            "role": "SOURCE_MANIFEST",
            "sha256": authority["tracked_source_manifest_sha256"],
        },
    ]
    objects = [
        {
            "object_source": "SUBJECT",
            "inventory_id": subject_id,
            "subject_id": subject_id,
            "object_type": "CONTROLLED_SUBJECT",
            "object_id": subject_id,
            "mr_id": "NOT_APPLICABLE",
            "evaluation_input_class": "E_COMMON",
            "evaluation_input_id": subject_id,
            "inputs": shared,
        }
    ]
    for row in subject["public_behavior_frame"]["rows"]:
        behavior_id = row["behavior_id"]
        objects.append(
            {
                "object_source": "SUBJECT_BEHAVIOR",
                "inventory_id": f"{subject_id}:{behavior_id}",
                "subject_id": subject_id,
                "object_type": "PUBLIC_BEHAVIOR",
                "object_id": behavior_id,
                "mr_id": "NOT_APPLICABLE",
                "evaluation_input_class": "PUBLIC_BEHAVIOR",
                "evaluation_input_id": behavior_id,
                "inputs": [
                    {
                        "role": "ADAPTER_REGISTRY",
                        "sha256": registries["adapter_registry_sha256"],
                    },
                    {"role": "BEHAVIOR", "sha256": canonical_sha256(row)},
                    {
                        "role": "INPUT_GENERATOR_REGISTRY",
                        "sha256": registries["input_generator_registry_sha256"],
                    },
                    {
                        "role": "SOURCE_MANIFEST",
                        "sha256": authority["tracked_source_manifest_sha256"],
                    },
                ],
            }
        )
    for row in subject["common_inputs"]["rows"]:
        input_id = row["input_id"]
        objects.append(
            {
                "object_source": "SUBJECT_COMMON_INPUT",
                "inventory_id": f"{subject_id}:{input_id}",
                "subject_id": subject_id,
                "object_type": "COMMON_INPUT",
                "object_id": input_id,
                "mr_id": "NOT_APPLICABLE",
                "evaluation_input_class": "E_COMMON",
                "evaluation_input_id": input_id,
                "inputs": [
                    {
                        "role": "ADAPTER_REGISTRY",
                        "sha256": registries["adapter_registry_sha256"],
                    },
                    {"role": "COMMON_INPUT", "sha256": canonical_sha256(row)},
                    {
                        "role": "INPUT_GENERATOR_REGISTRY",
                        "sha256": registries["input_generator_registry_sha256"],
                    },
                    {
                        "role": "SOURCE_MANIFEST",
                        "sha256": authority["tracked_source_manifest_sha256"],
                    },
                ],
            }
        )
    return objects


def prepare_authority(
    controller_root: Path, authority_inputs: Mapping[str, Any]
) -> dict[str, Any]:
    """Mechanically prepare byte-bound authority from declared paths."""

    inputs = validate_authority_inputs(authority_inputs)
    controller_root = _lstat_directory_components(Path(controller_root))
    subject_roots: list[Path] = []
    for subject in inputs["subjects"]:
        raw_root = Path(subject["root"])
        subject_roots.append(
            raw_root if raw_root.is_absolute() else controller_root / raw_root
        )
    nested_subject_roots: list[str] = []
    for subject_root in subject_roots:
        try:
            nested_subject_roots.append(
                subject_root.relative_to(controller_root).as_posix()
            )
        except ValueError:
            continue
    (
        controller_repository,
        controller_manifest,
        controller_tracked,
        controller_snapshot,
    ) = _checkout_authority(
        controller_root,
        _CONTROLLER_ROLE_ROOTS,
        "controller-source",
        nested_subject_roots,
    )
    declared_authority_paths = [
        path
        for field in (
            "governing_material_paths",
            "protocol_artifact_paths",
            "registry_artifact_paths",
        )
        for path in inputs[field].values()
    ]
    _require_tracked_paths(
        controller_tracked, declared_authority_paths, "controller authority"
    )

    governing_materials: dict[str, str] = {}
    governing_artifacts: dict[str, dict[str, Any]] = {}
    governing_raw: dict[str, bytes] = {}
    for role, relative_path in inputs["governing_material_paths"].items():
        raw = controller_snapshot.read_bytes(relative_path)
        envelope, digest = _raw_authority_envelope(
            controller_root,
            relative_path,
            f"governing material {role}",
            raw=raw,
        )
        governing_materials[f"{role}_sha256"] = digest
        governing_artifacts[f"{role}_sha256"] = envelope
        governing_raw[role] = raw
    governing_materials["controller_implementation_manifest_sha256"] = (
        controller_repository["tracked_source_manifest_sha256"]
    )
    governing_artifacts["controller_implementation_manifest_sha256"] = (
        controller_manifest
    )

    protocol_artifacts: dict[str, dict[str, Any]] = {}
    for role, relative_path in inputs["protocol_artifact_paths"].items():
        if role == "rq_spec":
            artifact, _digest = _raw_authority_envelope(
                controller_root,
                relative_path,
                "protocol artifact rq_spec",
                raw=controller_snapshot.read_bytes(relative_path),
            )
            _rq_ids_from_spec_bytes(bytes.fromhex(artifact["bytes_hex"]))
        else:
            artifact = _snapshot_canonical_json(
                controller_snapshot, relative_path, f"protocol artifact {role}"
            )
            _reject_credential_metadata(artifact)
        protocol_artifacts[f"{role}_sha256"] = artifact
    protocol_artifact = validate_protocol(
        protocol_artifacts["protocol_sha256"],
        SCIENTIFIC_PLAN_SHA256,
        EVIDENCE_DESIGN_SHA256,
    )
    protocol = {
        field: (
            protocol_artifacts[field]["sha256"]
            if field == "rq_spec_sha256"
            else canonical_sha256(protocol_artifacts[field])
        )
        for field in _PROTOCOL_AUTHORITY_SCHEMA
    }
    for field in _PROTOCOL_AUTHORITY_SCHEMA:
        if field not in {"protocol_sha256", "job_derivation_policy_sha256"}:
            _require_authority(
                protocol_artifact[field] == protocol[field],
                f"protocol artifact binding differs for {field}",
            )
    _require_authority(
        protocol_artifact["scientific_plan_sha256"]
        == governing_materials["scientific_plan_sha256"]
        and protocol_artifact["evidence_design_sha256"]
        == governing_materials["evidence_design_sha256"],
        "protocol governing-material binding differs",
    )
    job_derivation_policy = protocol_artifacts["job_derivation_policy_sha256"]
    rq_ids = _validate_rq_claim_authority(
        bytes.fromhex(protocol_artifacts["rq_spec_sha256"]["bytes_hex"]),
        protocol_artifacts["claim_ceiling_sha256"],
        scientific_plan_raw=governing_raw["scientific_plan"],
    )
    environment_lock = _validate_environment_lock(
        protocol_artifacts["environment_lock_sha256"]
    )
    synthetic_objects = _synthetic_objects(
        protocol_artifacts["p12_contract_sha256"]
    )

    adapter_relative = inputs["registry_artifact_paths"]["adapter_registry"]
    generator_relative = inputs["registry_artifact_paths"][
        "input_generator_registry"
    ]
    adapter_artifact = _snapshot_canonical_json(
        controller_snapshot, adapter_relative, "adapter registry"
    )
    _reject_credential_metadata(adapter_artifact)
    generator_artifact = _snapshot_canonical_json(
        controller_snapshot, generator_relative, "input generator registry"
    )
    _reject_credential_metadata(generator_artifact)
    implementation_paths = [
        *_registered_implementation_paths(
            adapter_relative,
            adapter_artifact.get("adapters", []),
        ),
        *_registered_implementation_paths(
            generator_relative,
            generator_artifact.get("generators", []),
        ),
    ]
    _require_tracked_paths(
        controller_tracked, implementation_paths, "registry implementations"
    )
    adapter_registry = validate_adapter_registry(
        adapter_artifact,
        controller_snapshot,
    )
    generator_registry = validate_input_generator_registry(
        generator_artifact,
        controller_snapshot,
    )
    registry_artifacts = {
        "adapter_registry_sha256": adapter_artifact,
        "input_generator_registry_sha256": generator_artifact,
    }
    registries = {
        field: canonical_sha256(registry_artifacts[field])
        for field in _REGISTRY_AUTHORITY_SCHEMA
    }
    for field in _REGISTRY_AUTHORITY_SCHEMA:
        _require_authority(
            protocol_artifact[field] == registries[field],
            f"protocol registry binding differs for {field}",
        )

    subjects = []
    for subject_input, subject_root in zip(
        inputs["subjects"], subject_roots, strict=True
    ):
        (
            repository,
            source_manifest,
            _subject_tracked,
            subject_snapshot,
        ) = _checkout_authority(subject_root, ["."], "subject-source")
        _require_tracked_paths(
            _subject_tracked,
            [subject_input["build_descriptor_path"]],
            f"subject {subject_input['subject_id']} build descriptor",
        )
        build_descriptor = _snapshot_canonical_json(
            subject_snapshot,
            subject_input["build_descriptor_path"],
            f"subject {subject_input['subject_id']} build descriptor",
        )
        entries = {
            row["adapter_id"]: row for row in adapter_registry["adapters"]
        }
        adapter_entry = entries.get(subject_input["adapter_id"])
        _require_authority(
            adapter_entry is not None
            and build_descriptor.get("ecosystem") == adapter_entry["ecosystem"],
            "subject adapter and build descriptor differ",
        )
        source_record = {
            "normalized_source_tree_sha256": repository[
                "tracked_source_manifest_sha256"
            ],
            "build_descriptor_sha256": canonical_sha256(build_descriptor),
        }
        adapter_discovery = run_adapter_discovery(
            subject_snapshot,
            build_descriptor,
            adapter_registry,
            subject_input["adapter_id"],
        )
        public_behavior_frame = build_public_behavior_frame(
            source_record, adapter_discovery
        )
        scale = derive_source_scale(subject_snapshot, adapter_discovery)
        profiling_workload = select_profiling_workload(
            public_behavior_frame, scale["scale_class"]
        )
        common_inputs = build_common_inputs(
            source_record, public_behavior_frame, generator_registry
        )
        authority_row = {
            "subject_id": subject_input["subject_id"],
            "repository_role": subject_input["repository_role"],
            **repository,
            "build_descriptor_sha256": canonical_sha256(build_descriptor),
            "adapter_id": subject_input["adapter_id"],
        }
        subjects.append(
            {
                "authority_row": authority_row,
                "source_manifest": source_manifest,
                "build_descriptor": build_descriptor,
                "adapter_discovery": adapter_discovery,
                "public_behavior_frame": public_behavior_frame,
                "profiling_workload": profiling_workload,
                "common_inputs": common_inputs,
            }
        )

    objects = [
        *synthetic_objects,
        *(
            item
            for subject in subjects
            for item in _subject_objects(subject, registries)
        ),
    ]
    objects.sort(key=lambda row: (row["object_source"], row["inventory_id"]))
    dependency_lock = controller_snapshot.read_bytes("requirements-frozen.txt")
    prepared = {
        "controller_repository": controller_repository,
        "controller_manifest": controller_manifest,
        "subjects": subjects,
        "governing_materials": governing_materials,
        "governing_artifacts": governing_artifacts,
        "protocol": protocol,
        "protocol_artifacts": protocol_artifacts,
        "registries": registries,
        "registry_artifacts": registry_artifacts,
        "preflight": {
            "normalized_repository_identity": controller_repository[
                "normalized_repository_identity"
            ],
            "base_commit": controller_repository["base_commit"],
            "base_tree": controller_repository["base_tree"],
            "dependency_lock_sha256": hashlib.sha256(dependency_lock).hexdigest(),
            "environment_policy_sha256": protocol["environment_lock_sha256"],
            "required_capabilities": environment_lock["required_capabilities"],
            "forbidden_credential_fields": environment_lock[
                "forbidden_credential_fields"
            ],
        },
        "claim_policy": {
            "claim_ceiling_sha256": protocol["claim_ceiling_sha256"],
            "required_status": "blocked",
            "rq_ids": rq_ids,
        },
        "objects": objects,
        "environments": environment_lock["environments"],
        "job_derivation_policy": job_derivation_policy,
    }
    snapshot = _snapshot_prepared_authority(prepared)
    _validate_derivation_inputs(snapshot, snapshot["job_derivation_policy"])
    return snapshot


def build_authority_lock(
    controller_root: Path, authority_inputs: Mapping[str, Any]
) -> dict[str, Any]:
    inputs = validate_authority_inputs(authority_inputs)
    prepared = prepare_authority(controller_root, inputs)
    jobs = derive_locked_jobs(prepared, prepared["job_derivation_policy"])
    return validate_authority_lock(
        {
            "schema_version": "P3_V3_AUTHORITY_LOCK_V1",
            "task_id": inputs["task_id"],
            "controller_repository": prepared["controller_repository"],
            "subjects": [row["authority_row"] for row in prepared["subjects"]],
            "governing_materials": prepared["governing_materials"],
            "protocol": prepared["protocol"],
            "registries": prepared["registries"],
            "preflight": prepared["preflight"],
            "jobs": jobs,
            "claim_policy": prepared["claim_policy"],
        }
    )


def freeze_authority_lock(
    controller_root: Path, authority_inputs_path: Path, output_path: Path
) -> dict[str, Any]:
    declared_inputs_path = Path(authority_inputs_path)
    if any(part in {".", ".."} for part in declared_inputs_path.parts):
        raise EvidenceError("E_AUTHORITY_INPUTS", "authority inputs path is unsafe")
    inputs_path = (
        declared_inputs_path
        if declared_inputs_path.is_absolute()
        else Path.cwd() / declared_inputs_path
    )
    inputs = read_canonical_regular_json(inputs_path, "authority inputs")
    inputs = validate_authority_inputs(inputs)
    resolved = json.loads(canonical_json_bytes(inputs).decode("utf-8"))
    for subject in resolved["subjects"]:
        root = Path(subject["root"])
        if not root.is_absolute():
            subject["root"] = str(inputs_path.parent / root)
    lock = build_authority_lock(controller_root, resolved)
    write_canonical_json(output_path, lock, exclusive=True)
    return lock


def validate_authority_lock(lock: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the exact structural and cross-field Authority Lock contract."""

    if not isinstance(lock, Mapping):
        raise EvidenceError("E_SCHEMA_TYPE", "authority lock must be an object")
    _reject_credential_metadata(lock)
    value = validate_exact_object(dict(lock), _AUTHORITY_LOCK_SCHEMA, "authority lock")
    _require_authority(
        value["schema_version"] == "P3_V3_AUTHORITY_LOCK_V1",
        "authority lock schema version differs",
    )
    _validate_authority_text(value["task_id"], "authority lock task_id")

    controller = validate_exact_object(
        value["controller_repository"],
        _CONTROLLER_AUTHORITY_SCHEMA,
        "authority lock controller_repository",
    )
    _validate_repository_identity(
        controller["normalized_repository_identity"],
        "authority lock controller repository identity",
    )
    for field in ("base_commit", "base_tree"):
        _validate_git_object(controller[field], f"controller_repository.{field}")
    validate_sha256(
        controller["tracked_source_manifest_sha256"],
        "controller_repository.tracked_source_manifest_sha256",
    )

    _require_authority(bool(value["subjects"]), "authority lock subjects are empty")
    subjects = []
    for index, candidate in enumerate(value["subjects"]):
        subject = validate_exact_object(
            candidate, _SUBJECT_AUTHORITY_SCHEMA, f"authority lock subjects[{index}]"
        )
        for field in ("subject_id", "repository_role", "adapter_id"):
            _validate_authority_text(subject[field], f"subjects[{index}].{field}")
        _validate_repository_identity(
            subject["normalized_repository_identity"],
            f"subjects[{index}].normalized_repository_identity",
        )
        for field in ("base_commit", "base_tree"):
            _validate_git_object(subject[field], f"subjects[{index}].{field}")
        for field in ("tracked_source_manifest_sha256", "build_descriptor_sha256"):
            validate_sha256(subject[field], f"subjects[{index}].{field}")
        subjects.append(subject)
    subject_ids = [item["subject_id"] for item in subjects]
    _require_authority(
        subject_ids == sorted(subject_ids) and len(subject_ids) == len(set(subject_ids)),
        "authority lock subjects are not sorted and unique",
    )
    for field in ("repository_role", "tracked_source_manifest_sha256"):
        observed = [item[field] for item in subjects]
        _require_authority(
            len(observed) == len(set(observed)),
            f"authority lock subjects have duplicate {field}",
        )
    _require_authority(
        controller["tracked_source_manifest_sha256"]
        not in {item["tracked_source_manifest_sha256"] for item in subjects},
        "controller and subject manifests are not independent",
    )

    governing = validate_exact_object(
        value["governing_materials"],
        _GOVERNING_AUTHORITY_SCHEMA,
        "authority lock governing_materials",
    )
    for field, digest in governing.items():
        validate_sha256(digest, f"governing_materials.{field}")
    _require_authority(
        governing["controller_implementation_manifest_sha256"]
        == controller["tracked_source_manifest_sha256"],
        "controller implementation manifest differs",
    )

    protocol = validate_exact_object(
        value["protocol"], _PROTOCOL_AUTHORITY_SCHEMA, "authority lock protocol"
    )
    for field, digest in protocol.items():
        validate_sha256(digest, f"protocol.{field}")

    registries = validate_exact_object(
        value["registries"], _REGISTRY_AUTHORITY_SCHEMA, "authority lock registries"
    )
    for field, digest in registries.items():
        validate_sha256(digest, f"registries.{field}")

    preflight = validate_exact_object(
        value["preflight"], _PREFLIGHT_AUTHORITY_SCHEMA, "authority lock preflight"
    )
    _validate_repository_identity(
        preflight["normalized_repository_identity"],
        "authority lock preflight repository identity",
    )
    for field in ("base_commit", "base_tree"):
        _validate_git_object(preflight[field], f"preflight.{field}")
    for field in ("dependency_lock_sha256", "environment_policy_sha256"):
        validate_sha256(preflight[field], f"preflight.{field}")
    for field in ("required_capabilities", "forbidden_credential_fields"):
        items = preflight[field]
        _require_authority(
            bool(items)
            and all(type(item) is str and bool(item) for item in items)
            and items == sorted(items)
            and len(items) == len(set(items)),
            f"preflight.{field} must be a sorted unique nonempty string list",
        )
    _require_authority(
        preflight["forbidden_credential_fields"] == sorted(_CREDENTIAL_FIELD_NAMES),
        "preflight forbidden credential fields differ",
    )
    for field in ("normalized_repository_identity", "base_commit", "base_tree"):
        _require_authority(
            preflight[field] == controller[field],
            f"preflight.{field} differs from controller authority",
        )
    _require_authority(
        preflight["environment_policy_sha256"] == protocol["environment_lock_sha256"],
        "preflight environment policy differs from protocol authority",
    )

    _require_authority(bool(value["jobs"]), "authority lock jobs are empty")
    jobs = []
    for index, candidate in enumerate(value["jobs"]):
        job = validate_exact_object(
            candidate, _JOB_AUTHORITY_SCHEMA, f"authority lock jobs[{index}]"
        )
        for field in ("job_id", "input_identity_sha256", "intent_template_sha256"):
            validate_sha256(job[field], f"jobs[{index}].{field}")
        for field in ("phase", "job_role", "object_identity"):
            _validate_authority_text(job[field], f"jobs[{index}].{field}")
        _require_authority(
            job["maximum_attempts"] == 3,
            "authority lock job maximum_attempts differs",
        )
        _require_authority(
            job["retry_trigger"] == "FAIL_INFRASTRUCTURE",
            "authority lock job retry_trigger differs",
        )
        _require_authority(
            job["execution_class"] in _EXECUTION_CLASSES,
            "authority lock job execution_class is invalid",
        )
        _require_authority(
            job["p12_access_class"] in _P12_ACCESS_CLASSES,
            "authority lock job p12_access_class is invalid",
        )
        jobs.append(job)
    job_ids = [item["job_id"] for item in jobs]
    _require_authority(
        job_ids == sorted(job_ids) and len(job_ids) == len(set(job_ids)),
        "authority lock jobs are not sorted and unique",
    )
    intent_templates = [item["intent_template_sha256"] for item in jobs]
    _require_authority(
        len(intent_templates) == len(set(intent_templates)),
        "authority lock jobs have duplicate intent templates",
    )

    claim_policy = validate_exact_object(
        value["claim_policy"],
        _CLAIM_POLICY_AUTHORITY_SCHEMA,
        "authority lock claim_policy",
    )
    validate_sha256(claim_policy["claim_ceiling_sha256"], "claim_policy.claim_ceiling_sha256")
    _require_authority(
        claim_policy["claim_ceiling_sha256"] == protocol["claim_ceiling_sha256"],
        "claim ceiling differs from protocol authority",
    )
    _require_authority(
        claim_policy["required_status"] == "blocked",
        "authority lock claim status differs",
    )
    if claim_policy["rq_ids"] != list(_REQUIRED_RQ_IDS):
        raise EvidenceError(
            "E_CLAIM_SET", "authority lock RQ coverage differs from RQ1 through RQ4"
        )
    return value


def load_authority_lock(lock_path: Path, expected_sha256: str) -> dict[str, Any]:
    """Load one canonical Authority Lock only under its external byte digest."""

    try:
        validate_sha256(expected_sha256, "authority_lock_sha256")
    except EvidenceError as exc:
        if exc.code == "E_SHA256":
            raise EvidenceError(
                "E_AUTHORITY_LOCK_DIGEST",
                "authority lock digest is malformed",
            ) from exc
        raise
    raw = read_canonical_regular_bytes(lock_path, "authority lock")
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise EvidenceError(
            "E_AUTHORITY_LOCK_DIGEST", "authority lock digest differs"
        )
    try:
        value = json.loads(raw.decode("utf-8"))
        is_canonical = canonical_json_bytes(value) == raw
    except (UnicodeDecodeError, json.JSONDecodeError, EvidenceError) as exc:
        raise EvidenceError(
            "E_AUTHORITY_LOCK_SCHEMA", "authority lock is noncanonical"
        ) from exc
    if not is_canonical:
        raise EvidenceError(
            "E_AUTHORITY_LOCK_SCHEMA", "authority lock is noncanonical"
        )
    if isinstance(value, Mapping):
        reject_confirmatory_artifact(value, "authority-lock")
    return validate_authority_lock(value)


_PREFLIGHT_EVENT_SCHEMA = {
    "schema_version": str,
    "normalized_repository_identity": str,
    "base_commit": str,
    "base_tree": str,
    "dependency_lock_sha256": str,
    "environment_policy_sha256": str,
    "capability_results": list,
    "event_sha256": str,
}
_CAPABILITY_RESULT_SCHEMA = {
    "capability": str,
    "status": str,
    "observation_sha256": str,
}


def reconstruct_origin_receipt(
    lock_preflight: Mapping[str, Any], preflight_event: Mapping[str, Any]
) -> dict[str, Any]:
    """Rebuild the canonical Phase 0 origin receipt from locked authority."""

    _reject_credential_metadata(preflight_event)
    try:
        locked = validate_exact_object(
            dict(lock_preflight), _PREFLIGHT_AUTHORITY_SCHEMA, "lock preflight"
        )
        event = validate_exact_object(
            dict(preflight_event), _PREFLIGHT_EVENT_SCHEMA, "preflight event"
        )
        if event["schema_version"] != "P3_V3_PREFLIGHT_EVENT_V1":
            raise EvidenceError("E_AUTHORITY_ORIGIN", "preflight event version differs")
        event_body = {key: value for key, value in event.items() if key != "event_sha256"}
        validate_sha256(event["event_sha256"], "preflight event digest")
        if event["event_sha256"] != canonical_sha256(event_body):
            raise EvidenceError("E_AUTHORITY_ORIGIN", "preflight event hash differs")
        stable_fields = (
            "normalized_repository_identity",
            "base_commit",
            "base_tree",
            "dependency_lock_sha256",
            "environment_policy_sha256",
        )
        if any(event[field] != locked[field] for field in stable_fields):
            raise EvidenceError("E_AUTHORITY_ORIGIN", "preflight authority differs")
        results = [
            validate_exact_object(
                candidate,
                _CAPABILITY_RESULT_SCHEMA,
                f"preflight event capability_results[{index}]",
            )
            for index, candidate in enumerate(event["capability_results"])
        ]
        for index, result in enumerate(results):
            _validate_authority_text(
                result["capability"], f"capability_results[{index}].capability"
            )
            if result["status"] not in {"PASS", "FAIL"}:
                raise EvidenceError(
                    "E_AUTHORITY_ORIGIN", "preflight capability status is invalid"
                )
            validate_sha256(
                result["observation_sha256"],
                f"capability_results[{index}].observation_sha256",
            )
        capability_names = [result["capability"] for result in results]
        if capability_names != sorted(capability_names) or len(capability_names) != len(
            set(capability_names)
        ):
            raise EvidenceError(
                "E_AUTHORITY_ORIGIN", "preflight capabilities are not sorted and unique"
            )
        by_capability = {result["capability"]: result for result in results}
        required_results = []
        for capability in locked["required_capabilities"]:
            result = by_capability.get(capability)
            if result is None or result["status"] != "PASS":
                raise EvidenceError(
                    "E_AUTHORITY_ORIGIN", "required preflight capability did not pass"
                )
            required_results.append(result)
        receipt_body = {
            "schema_version": "P3_V3_ORIGIN_RECEIPT_V1",
            **{field: locked[field] for field in stable_fields},
            "required_capability_results": required_results,
            "preflight_event_sha256": event["event_sha256"],
        }
        return {**receipt_body, "artifact_sha256": canonical_sha256(receipt_body)}
    except EvidenceError as exc:
        if exc.code == "E_AUTHORITY_ORIGIN":
            raise
        raise EvidenceError(
            "E_AUTHORITY_ORIGIN", "preflight origin receipt is invalid"
        ) from exc


def _authority_intent_failure(detail: str) -> None:
    raise EvidenceError("E_AUTHORITY_INTENT", detail)


def _snapshot_prepared_authority(
    prepared_authority: Mapping[str, Any],
) -> dict[str, Any]:
    """Copy and cross-validate the complete internal authority value."""

    try:
        snapshot = json.loads(canonical_json_bytes(prepared_authority).decode("utf-8"))
        value = validate_exact_object(
            snapshot, _PREPARED_AUTHORITY_SCHEMA, "prepared authority"
        )
    except (TypeError, ValueError, json.JSONDecodeError, EvidenceError) as exc:
        raise EvidenceError(
            "E_AUTHORITY_INPUTS", "prepared authority schema differs"
        ) from exc

    try:
        controller = validate_exact_object(
            value["controller_repository"],
            _CONTROLLER_AUTHORITY_SCHEMA,
            "prepared controller_repository",
        )
        validate_sha256(
            controller["tracked_source_manifest_sha256"],
            "prepared controller manifest digest",
        )
        if canonical_sha256(value["controller_manifest"]) != controller[
            "tracked_source_manifest_sha256"
        ]:
            _authority_intent_failure("prepared controller manifest binding differs")

        subjects: list[dict[str, Any]] = []
        subject_ids: list[str] = []
        for index, candidate in enumerate(value["subjects"]):
            subject = validate_exact_object(
                candidate, _PREPARED_SUBJECT_SCHEMA, f"prepared subjects[{index}]"
            )
            authority_row = validate_exact_object(
                subject["authority_row"],
                _SUBJECT_AUTHORITY_SCHEMA,
                f"prepared subjects[{index}].authority_row",
            )
            for field in (
                "tracked_source_manifest_sha256",
                "build_descriptor_sha256",
            ):
                validate_sha256(authority_row[field], f"prepared subject {field}")
            if canonical_sha256(subject["source_manifest"]) != authority_row[
                "tracked_source_manifest_sha256"
            ]:
                _authority_intent_failure("prepared subject manifest binding differs")
            if canonical_sha256(subject["build_descriptor"]) != authority_row[
                "build_descriptor_sha256"
            ]:
                _authority_intent_failure(
                    "prepared subject build-descriptor binding differs"
                )
            subject_ids.append(authority_row["subject_id"])
            subjects.append(subject)
        if (
            not subjects
            or subject_ids != sorted(subject_ids)
            or len(subject_ids) != len(set(subject_ids))
        ):
            _authority_intent_failure("prepared subjects are not sorted and unique")

        governing = validate_exact_object(
            value["governing_materials"],
            _GOVERNING_AUTHORITY_SCHEMA,
            "prepared governing_materials",
        )
        governing_artifacts = validate_exact_object(
            value["governing_artifacts"],
            {field: dict for field in _GOVERNING_AUTHORITY_SCHEMA},
            "prepared governing_artifacts",
        )
        for field, digest in governing.items():
            validate_sha256(digest, f"prepared governing_materials.{field}")
            artifact = governing_artifacts[field]
            if field == "controller_implementation_manifest_sha256":
                observed_digest = canonical_sha256(artifact)
            else:
                envelope = validate_exact_object(
                    artifact,
                    _RAW_AUTHORITY_BYTES_SCHEMA,
                    f"prepared governing_artifacts.{field}",
                )
                if envelope["schema_version"] != "P3_V3_RAW_AUTHORITY_BYTES_V1":
                    _authority_intent_failure(
                        "prepared governing artifact envelope differs"
                    )
                safe_relative_path(envelope["relative_path"])
                validate_sha256(envelope["sha256"], "governing bytes digest")
                try:
                    raw = bytes.fromhex(envelope["bytes_hex"])
                except ValueError as exc:
                    raise EvidenceError(
                        "E_AUTHORITY_INTENT", "prepared governing bytes are invalid"
                    ) from exc
                if raw.hex() != envelope["bytes_hex"]:
                    _authority_intent_failure(
                        "prepared governing bytes encoding differs"
                    )
                observed_digest = hashlib.sha256(raw).hexdigest()
                if observed_digest != envelope["sha256"]:
                    _authority_intent_failure(
                        "prepared governing byte binding differs"
                    )
            if observed_digest != digest:
                _authority_intent_failure("prepared governing artifact binding differs")

        protocol = validate_exact_object(
            value["protocol"], _PROTOCOL_AUTHORITY_SCHEMA, "prepared protocol"
        )
        protocol_artifacts = validate_exact_object(
            value["protocol_artifacts"],
            {field: dict for field in _PROTOCOL_AUTHORITY_SCHEMA},
            "prepared protocol_artifacts",
        )
        for field, digest in protocol.items():
            validate_sha256(digest, f"prepared protocol.{field}")
            observed_digest = (
                protocol_artifacts[field].get("sha256")
                if field == "rq_spec_sha256"
                else canonical_sha256(protocol_artifacts[field])
            )
            if observed_digest != digest:
                _authority_intent_failure("prepared protocol artifact binding differs")
            if field == "rq_spec_sha256":
                envelope = validate_exact_object(
                    protocol_artifacts[field],
                    _RAW_AUTHORITY_BYTES_SCHEMA,
                    "prepared protocol_artifacts.rq_spec_sha256",
                )
                if envelope["schema_version"] != "P3_V3_RAW_AUTHORITY_BYTES_V1":
                    _authority_intent_failure(
                        "prepared rq_spec authority envelope differs"
                    )
                safe_relative_path(envelope["relative_path"])
                validate_sha256(envelope["sha256"], "prepared rq_spec bytes digest")
                try:
                    raw = bytes.fromhex(envelope["bytes_hex"])
                except ValueError as exc:
                    raise EvidenceError(
                        "E_AUTHORITY_INTENT", "prepared rq_spec bytes are invalid"
                    ) from exc
                _rq_ids_from_spec_bytes(raw)
                if (
                    raw.hex() != envelope["bytes_hex"]
                    or hashlib.sha256(raw).hexdigest() != digest
                ):
                    _authority_intent_failure(
                        "prepared rq_spec byte binding differs"
                    )

        registries = validate_exact_object(
            value["registries"], _REGISTRY_AUTHORITY_SCHEMA, "prepared registries"
        )
        registry_artifacts = validate_exact_object(
            value["registry_artifacts"],
            {field: dict for field in _REGISTRY_AUTHORITY_SCHEMA},
            "prepared registry_artifacts",
        )
        for field, digest in registries.items():
            validate_sha256(digest, f"prepared registries.{field}")
            if canonical_sha256(registry_artifacts[field]) != digest:
                _authority_intent_failure("prepared registry artifact binding differs")

        preflight = validate_exact_object(
            value["preflight"], _PREFLIGHT_AUTHORITY_SCHEMA, "prepared preflight"
        )
        claim_policy = validate_exact_object(
            value["claim_policy"],
            _CLAIM_POLICY_AUTHORITY_SCHEMA,
            "prepared claim_policy",
        )
        rq_ids = _validate_rq_claim_authority(
            bytes.fromhex(protocol_artifacts["rq_spec_sha256"]["bytes_hex"]),
            protocol_artifacts["claim_ceiling_sha256"],
            scientific_plan_raw=bytes.fromhex(
                governing_artifacts["scientific_plan_sha256"]["bytes_hex"]
            ),
        )
        if (
            preflight["normalized_repository_identity"]
            != controller["normalized_repository_identity"]
            or preflight["base_commit"] != controller["base_commit"]
            or preflight["base_tree"] != controller["base_tree"]
            or preflight["environment_policy_sha256"]
            != protocol["environment_lock_sha256"]
            or claim_policy["claim_ceiling_sha256"]
            != protocol["claim_ceiling_sha256"]
            or claim_policy["required_status"] != "blocked"
            or claim_policy["rq_ids"] != rq_ids
        ):
            _authority_intent_failure("prepared cross-authority binding differs")
    except EvidenceError as exc:
        if str(exc).startswith("E_AUTHORITY_INTENT"):
            raise
        raise EvidenceError(
            "E_AUTHORITY_INTENT", "prepared authority validation failed"
        ) from exc
    return value


def _policy_class_projection(policy: Mapping[str, Any]) -> list[tuple[Any, Any, Any]]:
    templates = policy.get("templates")
    if not isinstance(templates, list):
        return []
    return [
        (
            template.get("template_id"),
            template.get("execution_class"),
            template.get("p12_access_class"),
        )
        for template in templates
        if isinstance(template, Mapping)
    ]


def _validate_derivation_inputs(
    prepared_authority: Mapping[str, Any],
    job_derivation_policy: Mapping[str, Any],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
]:
    if not isinstance(prepared_authority, Mapping):
        raise EvidenceError("E_AUTHORITY_INPUTS", "prepared authority must be an object")
    forbidden = _PREPARED_FORBIDDEN_FIELDS.intersection(prepared_authority)
    unexpected = set(prepared_authority).difference(_PREPARED_AUTHORITY_SCHEMA)
    if forbidden or unexpected:
        raise EvidenceError(
            "E_AUTHORITY_INPUTS",
            "caller-supplied execution authority is forbidden",
        )
    prepared = _snapshot_prepared_authority(prepared_authority)
    protocol = prepared["protocol"]
    objects_value = prepared["objects"]
    environments_value = prepared["environments"]
    policy_sha256 = protocol["job_derivation_policy_sha256"]
    if not isinstance(job_derivation_policy, Mapping):
        _authority_intent_failure("job derivation policy must be an object")
    try:
        supplied_policy_snapshot = json.loads(
            canonical_json_bytes(job_derivation_policy).decode("utf-8")
        )
        supplied_policy = validate_exact_object(
            supplied_policy_snapshot,
            _JOB_DERIVATION_POLICY_SCHEMA,
            "job_derivation_policy",
        )
    except (TypeError, ValueError, EvidenceError) as exc:
        raise EvidenceError(
            "E_AUTHORITY_INTENT", "job derivation policy schema differs"
        ) from exc
    prepared_policy = prepared["job_derivation_policy"]
    if supplied_policy != prepared_policy:
        if _policy_class_projection(supplied_policy) != _policy_class_projection(
            prepared_policy
        ):
            raise EvidenceError(
                "E_AUTHORITY_EXECUTION_CLASS",
                "supplied execution classes differ from prepared authority",
            )
        _authority_intent_failure("supplied derivation policy differs from prepared authority")
    policy = supplied_policy
    if canonical_sha256(prepared_policy) != policy_sha256:
        _authority_intent_failure("job derivation policy bytes differ from protocol")
    if (
        policy["schema_version"] != "P3_V3_JOB_DERIVATION_POLICY_V1"
        or policy["maximum_attempts"] != 3
        or policy["retry_trigger"] != "FAIL_INFRASTRUCTURE"
        or not policy["templates"]
    ):
        _authority_intent_failure("job derivation policy contract differs")

    objects: list[dict[str, Any]] = []
    for index, candidate in enumerate(objects_value):
        try:
            item = validate_exact_object(
                candidate, _PREPARED_OBJECT_SCHEMA, f"prepared objects[{index}]"
            )
        except (TypeError, ValueError, EvidenceError) as exc:
            raise EvidenceError(
                "E_AUTHORITY_INTENT", "prepared object inventory differs"
            ) from exc
        if (
            item["object_source"] not in _PREPARED_OBJECT_SOURCES
            or not all(
                item[field]
                for field in (
                    "inventory_id",
                    "object_type",
                    "object_id",
                    "mr_id",
                    "evaluation_input_class",
                    "evaluation_input_id",
                )
            )
            or not item["inputs"]
        ):
            _authority_intent_failure("prepared object inventory is invalid")
        inputs = []
        for input_index, candidate_input in enumerate(item["inputs"]):
            try:
                prepared_input = validate_exact_object(
                    candidate_input,
                    _PREPARED_INPUT_SCHEMA,
                    f"prepared objects[{index}].inputs[{input_index}]",
                )
                validate_sha256(
                    prepared_input["sha256"],
                    f"prepared objects[{index}].inputs[{input_index}].sha256",
                )
            except (TypeError, ValueError, EvidenceError) as exc:
                raise EvidenceError(
                    "E_AUTHORITY_INTENT", "prepared object input differs"
                ) from exc
            if not prepared_input["role"]:
                _authority_intent_failure("prepared object input role is empty")
            inputs.append(prepared_input)
        roles = [item["role"] for item in inputs]
        if roles != sorted(roles) or len(roles) != len(set(roles)):
            _authority_intent_failure("prepared object inputs are not sorted and unique")
        objects.append({**item, "inputs": inputs})
    object_keys = [(item["object_source"], item["inventory_id"]) for item in objects]
    if (
        not objects
        or object_keys != sorted(object_keys)
        or len(object_keys) != len(set(object_keys))
    ):
        _authority_intent_failure("prepared objects are not sorted and unique")
    input_roles_by_source: dict[str, list[str]] = {}
    for item in objects:
        input_roles = [prepared_input["role"] for prepared_input in item["inputs"]]
        expected_roles = input_roles_by_source.setdefault(
            item["object_source"], input_roles
        )
        if input_roles != expected_roles:
            _authority_intent_failure(
                "prepared objects from one source have inconsistent input roles"
            )

    environments: list[dict[str, Any]] = []
    for index, candidate in enumerate(environments_value):
        try:
            environment = validate_exact_object(
                candidate,
                _PREPARED_ENVIRONMENT_SCHEMA,
                f"prepared environments[{index}]",
            )
            validate_sha256(
                environment["environment_sha256"],
                f"prepared environments[{index}].environment_sha256",
            )
        except (TypeError, ValueError, EvidenceError) as exc:
            raise EvidenceError(
                "E_AUTHORITY_INTENT", "prepared environment inventory differs"
            ) from exc
        if not environment["environment_role"] or not environment["environment_id"]:
            _authority_intent_failure("prepared environment identity is empty")
        environments.append(environment)
    environment_roles = [item["environment_role"] for item in environments]
    if (
        not environments
        or environment_roles != sorted(environment_roles)
        or len(environment_roles) != len(set(environment_roles))
    ):
        _authority_intent_failure("prepared environments are not sorted and unique")
    subject_ids = {
        item["authority_row"]["subject_id"] for item in prepared["subjects"]
    }
    for item in objects:
        if item["object_source"].startswith("SUBJECT") and item["subject_id"] not in subject_ids:
            _authority_intent_failure("prepared object names an unavailable subject")
    return objects, environments, policy, protocol


def _expand_base_intents(
    prepared_authority: Mapping[str, Any],
    job_derivation_policy: Mapping[str, Any],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    objects, environments, policy, protocol = _validate_derivation_inputs(
        prepared_authority, job_derivation_policy
    )
    protocol_sha256 = protocol["protocol_sha256"]
    environment_by_role = {
        item["environment_role"]: item for item in environments
    }
    templates: list[dict[str, Any]] = []
    for index, candidate in enumerate(policy["templates"]):
        try:
            template = validate_exact_object(
                candidate,
                _JOB_DERIVATION_TEMPLATE_SCHEMA,
                f"job_derivation_policy.templates[{index}]",
            )
        except (TypeError, ValueError, EvidenceError) as exc:
            raise EvidenceError(
                "E_AUTHORITY_INTENT", "job derivation template schema differs"
            ) from exc
        if (
            not template["template_id"]
            or template["phase"] not in {f"PHASE_{number}" for number in range(8)}
            or template["object_source"] not in _PREPARED_OBJECT_SOURCES
            or template["cwd_role"] not in {"CONTROLLER_ROOT", "SUBJECT_ROOT"}
            or template["seed_rule"] not in {"NONE", "REPETITION_ID"}
            or template["execution_class"] not in _EXECUTION_CLASSES
            or template["p12_access_class"] not in _P12_ACCESS_CLASSES
            or type(template["timeout_seconds"]) is bool
            or template["timeout_seconds"] < 1
        ):
            _authority_intent_failure("job derivation template value is invalid")
        argv = template["argv_template"]
        if (
            not argv
            or any(
                type(token) is not str
                or not token
                or ("$" in token and token not in _ARGV_PLACEHOLDERS)
                for token in argv
            )
        ):
            _authority_intent_failure("argv template contains an unsafe token")
        input_roles = template["input_roles"]
        repetitions = template["repetition_ids"]
        if (
            not input_roles
            or any(type(role) is not str or not role for role in input_roles)
            or input_roles != sorted(input_roles)
            or len(input_roles) != len(set(input_roles))
            or not repetitions
            or any(type(item) is not int or item < 1 for item in repetitions)
            or repetitions != sorted(repetitions)
            or len(repetitions) != len(set(repetitions))
        ):
            _authority_intent_failure("template expansion dimensions are invalid")
        templates.append(template)
    template_ids = [item["template_id"] for item in templates]
    if template_ids != sorted(template_ids) or len(template_ids) != len(set(template_ids)):
        _authority_intent_failure("job derivation templates are not sorted and unique")

    expanded: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for template in templates:
        selected = [
            item
            for item in objects
            if item["object_source"] == template["object_source"]
        ]
        environment = environment_by_role.get(template["environment_role"])
        if not selected or environment is None:
            _authority_intent_failure("template names an unavailable inventory role")
        complete_input_roles = [
            value["role"] for value in selected[0]["inputs"]
        ]
        if template["input_roles"] != complete_input_roles:
            _authority_intent_failure(
                "template input roles do not exactly cover selected objects"
            )
        for item in selected:
            input_sha256 = sorted(value["sha256"] for value in item["inputs"])
            if template["cwd_role"] == "SUBJECT_ROOT" and not item["subject_id"]:
                _authority_intent_failure("subject cwd role has no subject identity")
            cwd_identity = (
                "controller"
                if template["cwd_role"] == "CONTROLLER_ROOT"
                else f'subject:{item["subject_id"]}'
            )
            for repetition_id in template["repetition_ids"]:
                substitutions = {
                    "${protocol_sha256}": protocol_sha256,
                    "${subject_id}": item["subject_id"],
                    "${object_id}": item["object_id"],
                    "${evaluation_input_id}": item["evaluation_input_id"],
                    "${environment_id}": environment["environment_id"],
                    "${repetition_id}": str(repetition_id),
                }
                intent = {
                    "job_id": canonical_sha256(
                        {
                            "template_id": template["template_id"],
                            "object_source": item["object_source"],
                            "inventory_id": item["inventory_id"],
                            "repetition_id": repetition_id,
                        }
                    ),
                    "protocol_sha256": protocol_sha256,
                    "phase": template["phase"],
                    "argv": [substitutions.get(token, token) for token in template["argv_template"]],
                    "cwd_identity": cwd_identity,
                    "environment_sha256": environment["environment_sha256"],
                    "input_sha256": input_sha256,
                    "seed": repetition_id if template["seed_rule"] == "REPETITION_ID" else None,
                    "timeout_seconds": template["timeout_seconds"],
                    "attempt": 1,
                    "object_type": item["object_type"],
                    "object_id": item["object_id"],
                    "mr_id": item["mr_id"],
                    "evaluation_input_class": item["evaluation_input_class"],
                    "evaluation_input_id": item["evaluation_input_id"],
                    "repetition_id": repetition_id,
                    "environment_id": environment["environment_id"],
                    "job_role": template["job_role"],
                }
                try:
                    intent_template_sha256(intent)
                except EvidenceError as exc:
                    raise EvidenceError(
                        "E_AUTHORITY_INTENT", "derived intent is invalid"
                    ) from exc
                expanded.append(
                    (
                        intent,
                        {
                            **template,
                            "_maximum_attempts": policy["maximum_attempts"],
                            "_retry_trigger": policy["retry_trigger"],
                        },
                    )
                )
    expanded.sort(key=lambda pair: pair[0]["job_id"])
    job_ids = [pair[0]["job_id"] for pair in expanded]
    if len(job_ids) != len(set(job_ids)):
        _authority_intent_failure("job derivation produced duplicate expansions")
    return expanded


def derive_base_intents(
    prepared_authority: Mapping[str, Any],
    job_derivation_policy: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Mechanically expand base intents from byte-bound prepared inventories."""

    return [intent for intent, _template in _expand_base_intents(
        prepared_authority, job_derivation_policy
    )]


def derive_locked_jobs(
    prepared_authority: Mapping[str, Any],
    job_derivation_policy: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Derive the exact external job-authority rows from frozen templates."""

    expanded = _expand_base_intents(prepared_authority, job_derivation_policy)
    return [
        {
            "job_id": intent["job_id"],
            "phase": intent["phase"],
            "job_role": intent["job_role"],
            "object_identity": f'{intent["object_type"]}:{intent["object_id"]}',
            "input_identity_sha256": canonical_sha256(intent["input_sha256"]),
            "intent_template_sha256": intent_template_sha256(intent),
            "maximum_attempts": template["_maximum_attempts"],
            "retry_trigger": template["_retry_trigger"],
            "execution_class": template["execution_class"],
            "p12_access_class": template["p12_access_class"],
        }
        for intent, template in expanded
    ]


def _write(payload: dict) -> None:
    sys.stdout.buffer.write(canonical_json_bytes(payload))


def _write_output(path: str | None, payload: dict) -> None:
    if path:
        write_canonical_json(path, payload, exclusive=True)


def _write_under(output_root: Path, name: str, payload: Any) -> None:
    target = output_root / name
    if target.resolve().parent != output_root.resolve():
        raise EvidenceError(
            "E_OUTPUT_ROOT", f"refusing to write outside output-root: {name}"
        )
    write_canonical_json(target, payload, exclusive=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("freeze-authority-lock")
    command.add_argument("--controller-root", required=True)
    command.add_argument("--authority-inputs", required=True)
    command.add_argument("--output", required=True)
    command = sub.add_parser("validate-protocol")
    command.add_argument("--protocol", required=True)
    command = sub.add_parser("verify-bridge")
    command.add_argument("--repo-root", required=True)
    command.add_argument("--lock", required=True)
    command.add_argument("--output")
    command = sub.add_parser("build-frames")
    command.add_argument("--bridge", required=True)
    command.add_argument("--subject-specs", required=True)
    command.add_argument("--adapter-root", required=True)
    command.add_argument("--generator-root", required=True)
    command.add_argument("--slots", required=True)
    command.add_argument("--contracts", required=True)
    command.add_argument("--applicability-map", required=True)
    command.add_argument("--output-root", required=True)
    command.add_argument("--contract-generator-registry")
    command.add_argument("--contract-generator-root")
    command = sub.add_parser("verify-mr-inventory")
    command.add_argument("--candidate-frame", required=True)
    command.add_argument("--custodian-receipt", required=True)
    command.add_argument("--final-inventory", required=True)
    command.add_argument("--portfolios", required=True)
    command = sub.add_parser("build-package")
    command.add_argument("--role", required=True)
    command.add_argument("--root", required=True)
    command.add_argument("--specs", required=True)
    command.add_argument("--parents", required=True)
    command.add_argument("--output", required=True)
    command.add_argument("--allowed-classes")
    command = sub.add_parser("verify-package")
    command.add_argument("--root", required=True)
    command.add_argument("--manifest", required=True)
    command = sub.add_parser("run-preflight")
    command.add_argument("--root", required=True)
    command.add_argument("--spec", required=True)
    command.add_argument("--output")
    command = sub.add_parser("verify-run-records")
    command.add_argument("--ledger", required=True)
    command = sub.add_parser("close-phase")
    command.add_argument("--phase-id", required=True)
    command.add_argument("--protocol-sha256", required=True)
    command.add_argument("--expected-jobs", required=True)
    command.add_argument("--ledger", required=True)
    command.add_argument("--output-manifest-sha256", required=True)
    command.add_argument("--output", required=True)
    command = sub.add_parser("verify-evidence")
    command.add_argument("--index", required=True)
    command.add_argument("--authority-lock", required=True)
    command.add_argument("--authority-lock-sha256", required=True)
    command = sub.add_parser("validate-applicability-authority")
    command.add_argument("--manifest", required=True)
    command.add_argument("--registry", required=True)
    command.add_argument("--inventory", required=True)
    command.add_argument("--slot-implementation", required=True)
    command.add_argument("--predicate-implementation", required=True)
    return parser


_SUBJECT_SPEC_SCHEMA = {
    "neutral_snapshot_id": str,
    "source_root": str,
    "source_record": dict,
    "build_descriptor": dict,
    "adapter_registry": dict,
    "input_generator_registry": dict,
    "profiling_results": dict,
}


def _subject_specs_by_neutral(
    bridge: Mapping[str, Any], subject_specs: Any
) -> list[tuple[dict[str, Any], Mapping[str, Any]]]:
    records = bridge.get("records") if isinstance(bridge, Mapping) else None
    if not isinstance(records, list):
        raise EvidenceError("E_BRIDGE_RECORDS", "verified bridge records are absent")
    records_by_neutral: dict[str, Mapping[str, Any]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise EvidenceError(
                "E_BRIDGE_RECORDS", f"records[{index}] must be an object"
            )
        neutral = validate_sha256(
            record.get("neutral_snapshot_id"), f"records[{index}].neutral_snapshot_id"
        )
        if neutral in records_by_neutral:
            raise EvidenceError("E_BRIDGE_RECORDS", "duplicate bridge neutral ID")
        records_by_neutral[neutral] = record
    if not isinstance(subject_specs, list):
        raise EvidenceError("E_SUBJECT_SPEC", "subject-specs must be a list")
    specs_by_neutral: dict[str, dict[str, Any]] = {}
    for index, candidate in enumerate(subject_specs):
        if not isinstance(candidate, Mapping):
            raise EvidenceError(
                "E_SUBJECT_SPEC", f"subject_specs[{index}] must be an object"
            )
        spec = validate_exact_object(
            dict(candidate), _SUBJECT_SPEC_SCHEMA, f"subject_specs[{index}]"
        )
        neutral = validate_sha256(
            spec["neutral_snapshot_id"], f"subject_specs[{index}].neutral_snapshot_id"
        )
        if neutral in specs_by_neutral:
            raise EvidenceError(
                "E_SUBJECT_SPEC_COVERAGE", f"duplicate subject specification: {neutral}"
            )
        specs_by_neutral[neutral] = spec
    if set(specs_by_neutral) != set(records_by_neutral):
        raise EvidenceError(
            "E_SUBJECT_SPEC_COVERAGE",
            "subject specifications do not cover bridge exactly",
        )
    return [
        (specs_by_neutral[neutral], records_by_neutral[neutral])
        for neutral in sorted(records_by_neutral)
    ]


def _dispatch_build_frames(args: argparse.Namespace) -> dict:
    slots = read_canonical_json(args.slots)
    contracts = read_canonical_json(args.contracts)
    applicability_map = read_canonical_json(args.applicability_map)
    if not isinstance(slots, list):
        raise EvidenceError("E_SLOTS", "slots must be a list")
    if not isinstance(contracts, Mapping):
        raise EvidenceError("E_CONTRACTS", "contracts must be an object")
    if not isinstance(applicability_map, Mapping):
        raise EvidenceError("E_APPLICABILITY", "applicability-map must be an object")
    if applicability_map:
        raise EvidenceError(
            "E_APPLICABILITY",
            "handwritten applicability-map is forbidden; validate frozen authority",
        )
    if slots:
        raise EvidenceError(
            "E_SLOTS",
            "build-frames does not close confirmatory slots; use validate-applicability-authority",
        )
    bridge = read_canonical_json(args.bridge)
    indexed_specs = _subject_specs_by_neutral(
        bridge, read_canonical_json(args.subject_specs)
    )
    derived_subjects = []
    for spec, record in indexed_specs:
        _manifest, source_snapshot = _capture_tracked_source_manifest(
            Path(spec["source_root"]), ["."], "subject-source"
        )
        _reject_credential_metadata(spec["adapter_registry"])
        _reject_credential_metadata(spec["input_generator_registry"])
        adapter_paths = [
            entry["implementation_path"]
            for entry in spec["adapter_registry"]["adapters"]
        ]
        generator_paths = [
            entry["implementation_path"]
            for entry in spec["input_generator_registry"]["generators"]
        ]
        prepared = {
            **{key: value for key, value in spec.items() if key != "source_root"},
            "source_snapshot": source_snapshot,
            "adapter_registry": validate_adapter_registry(
                spec["adapter_registry"],
                _capture_declared_source_snapshot(
                    Path(args.adapter_root), adapter_paths, "adapter implementation"
                ),
            ),
            "input_generator_registry": validate_input_generator_registry(
                spec["input_generator_registry"],
                _capture_declared_source_snapshot(
                    Path(args.generator_root),
                    generator_paths,
                    "input generator implementation",
                ),
            ),
        }
        derived_subjects.append(derive_subject_material(prepared, record))
    subject_frames = build_subject_frames(bridge, derived_subjects)

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    written = []
    artifact_names = {
        "adapter_discovery": "adapter-discovery",
        "source_scale": "source-scale",
        "public_behavior_frame": "public-behavior-frame",
        "profiling_workload": "profiling-workload",
        "common_inputs": "evaluation-inputs-common",
        "profiling_results": "profiling-results",
        "technique_profile": "technique-profile",
    }
    for material in derived_subjects:
        neutral = material["neutral_snapshot_id"]
        for field, stem in artifact_names.items():
            name = f"{stem}-{neutral}.json"
            _write_under(output_root, name, material[field])
            written.append(name)
        name = f"derived-subject-{neutral}.json"
        _write_under(output_root, name, material)
        written.append(name)
    _write_under(output_root, "subject-frames.json", subject_frames)
    written.append("subject-frames.json")

    subjects_by_id = {
        subject["controlled_subject_id"]: subject
        for subject in subject_frames["subjects"]
    }
    contract_registry = None
    for index, slot in enumerate(slots):
        if not isinstance(slot, Mapping):
            raise EvidenceError("E_SLOTS", f"slots[{index}] must be an object")
        subject = subjects_by_id.get(slot.get("controlled_subject_id"))
        if subject is None:
            raise EvidenceError(
                "E_SLOTS",
                f"slots[{index}] controlled_subject_id is not in subject frames",
            )
        sites = subject["sites"]

        def predicate(site: Mapping[str, Any], _map=applicability_map) -> bool:
            value = _map.get(site["site_id"], False)
            if type(value) is not bool:
                raise EvidenceError(
                    "E_APPLICABILITY",
                    f"applicability for {site['site_id']} must be bool",
                )
            return value

        closure = close_slot(slot, sites, predicate)
        slot_name = f"slot-closure-{closure['slot_id']}.json"
        _write_under(output_root, slot_name, closure)
        written.append(slot_name)
        if closure["path"] != "APPLICABLE":
            continue
        contract = contracts.get(closure["slot_id"])
        if contract is None:
            continue
        if contract_registry is None:
            if not args.contract_generator_registry or not args.contract_generator_root:
                raise EvidenceError(
                    "E_CONTRACT_GENERATOR",
                    "applicable slot contracts require --contract-generator-registry/root",
                )
            contract_registry_artifact = read_canonical_json(
                args.contract_generator_registry
            )
            _reject_credential_metadata(contract_registry_artifact)
            contract_registry = validate_contract_generator_registry(
                contract_registry_artifact,
                args.contract_generator_root,
            )
        inventory = build_contract_inputs(closure, contract, contract_registry)
        contract_name = f"evaluation-inputs-contract-{closure['slot_id']}.json"
        _write_under(output_root, contract_name, inventory)
        written.append(contract_name)
    return {
        "status": "PASS",
        "output_root": str(output_root),
        "artifacts": sorted(written),
        "common_input_count": sum(
            len(material["common_inputs"]["rows"]) for material in derived_subjects
        ),
        "subject_count": len(subject_frames["subjects"]),
    }


_INDEX_SCHEMA = {
    "schema_version": str,
    "phase_coverage": list,
    "controller_source": dict,
    "subject_sources": list,
    "protocol": dict,
    "protocol_artifacts": dict,
    "adapter_registries": list,
    "input_generator_registries": list,
    "subjects": list,
    "packages": list,
    "mr_chain": dict,
    "job_root": str,
    "ledger": dict,
    "phase_receipts": list,
    "preflight_event": dict,
    "origin_receipt": dict,
    "p12": dict,
    "claims": dict,
    "artifact_sha256": str,
}
_PROTOCOL_ARTIFACT_FIELDS = (
    "rq_spec_sha256",
    "claim_ceiling_sha256",
    "p12_contract_sha256",
    "operator_catalogue_sha256",
    "mr_policy_sha256",
    "site_policy_sha256",
    "analysis_spec_sha256",
    "package_policy_sha256",
    "environment_lock_sha256",
    "job_derivation_policy_sha256",
)
_PROTOCOL_ARTIFACT_SCHEMA = {field: dict for field in _PROTOCOL_ARTIFACT_FIELDS}
_CLAIM_CEILING_SCHEMA = {
    "schema_version": str,
    "claims": list,
    "artifact_sha256": str,
}
_CLAIM_AUTHORITY_ROW_SCHEMA = {
    "claim_id": str,
    "rqs": list,
    "initial_status": str,
}
_REFERENCE_SCHEMA = {"path": str, "sha256": str}
_CONTROLLER_SOURCE_INDEX_SCHEMA = {"root": str, "manifest": dict}
_SUBJECT_SOURCE_INDEX_SCHEMA = {
    "subject_id": str,
    "root": str,
    "manifest": dict,
}
_ORIGIN_RECEIPT_SCHEMA = {
    "schema_version": str,
    "normalized_repository_identity": str,
    "base_commit": str,
    "base_tree": str,
    "dependency_lock_sha256": str,
    "environment_policy_sha256": str,
    "required_capability_results": list,
    "preflight_event_sha256": str,
    "artifact_sha256": str,
}
_SUBJECT_INDEX_SCHEMA = {
    "subject_id": str,
    "phase": str,
    "controlled_subject_source_id": str,
    "controlled_subject_id": str,
    "bridge_record": dict,
    "source_root": str,
    "source_record": dict,
    "build_descriptor": dict,
    "adapter_registry_sha256": str,
    "input_generator_registry_sha256": str,
    "adapter_discovery": dict,
    "source_scale": dict,
    "public_frame": dict,
    "profiling_workload": dict,
    "profiling_results": dict,
    "profiling_traces": list,
    "common_inputs": dict,
    "common_input_validity": dict,
    "technique_profile": dict,
    "sites": dict,
    "subject": dict,
    "slot_artifacts": list,
}
_PROFILE_TRACE_INDEX_SCHEMA = {
    "job_id": str,
    "attempt": int,
    "behavior_id": str,
    "artifact": dict,
}
_SLOT_INDEX_SCHEMA = {
    "slot_id": str,
    "controlled_subject_id": str,
    "artifact": dict,
}
_PACKAGE_INDEX_SCHEMA = {
    "phase": str,
    "input_role": str,
    "root": str,
    "manifest": dict,
}
_RECEIPT_INDEX_SCHEMA = {
    "phase": str,
    "receipt": dict,
    "expected_jobs": dict,
    "output_manifest": dict,
}
_MR_CHAIN_INDEX_SCHEMA = {
    "candidate_frame": dict,
    "custodian_receipt": dict,
    "final_inventory": dict,
    "portfolios": dict,
}
_P12_INDEX_SCHEMA = {"denominator": dict, "result_rows": dict, "summary": dict}
_PHASES = tuple(f"PHASE_{number}" for number in range(8))


def _indexed_directory(root: Path, relative: Any, seen: set[str], context: str) -> Path:
    normalized = safe_relative_path(relative).as_posix()
    if normalized in seen:
        raise EvidenceError(
            "E_INDEX_DUPLICATE", f"duplicate indexed path: {normalized}"
        )
    seen.add(normalized)
    path = _safe_index_node(root, normalized, context)
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError(
            "E_INDEX_PATH", f"missing indexed directory: {normalized}"
        ) from exc
    if path.is_symlink() or not stat.S_ISDIR(info.st_mode):
        raise EvidenceError(
            "E_INDEX_PATH", f"indexed directory is unsafe: {normalized}"
        )
    return path


def _safe_index_node(root: Path, relative: str, context: str) -> Path:
    """Resolve an indexed node without traversing any symlink component."""

    try:
        declared_root = root.resolve(strict=True)
    except OSError as exc:
        raise EvidenceError(
            "E_INDEX_PATH", "evidence index root is unavailable"
        ) from exc
    cursor = root
    for part in safe_relative_path(relative).parts:
        cursor = cursor / part
        try:
            info = cursor.lstat()
        except FileNotFoundError as exc:
            raise EvidenceError(
                "E_INDEX_PATH", f"missing indexed path component: {relative}"
            ) from exc
        if stat.S_ISLNK(info.st_mode):
            raise EvidenceError(
                "E_INDEX_PATH", f"indexed path contains a symlink: {relative}"
            )
    try:
        cursor.resolve(strict=True).relative_to(declared_root)
    except (OSError, ValueError) as exc:
        raise EvidenceError(
            "E_INDEX_PATH", f"indexed path escapes declared root: {relative}"
        ) from exc
    return cursor


def _indexed_file(
    root: Path,
    candidate: Any,
    seen: set[str],
    loaded: dict[str, Any],
    context: str,
    *,
    canonical: bool = True,
) -> tuple[Path, Any]:
    reference = validate_exact_object(candidate, _REFERENCE_SCHEMA, context)
    relative = safe_relative_path(reference["path"]).as_posix()
    validate_sha256(reference["sha256"], f"{context}.sha256")
    if relative in seen:
        raise EvidenceError("E_INDEX_DUPLICATE", f"duplicate indexed path: {relative}")
    seen.add(relative)
    path = _safe_index_node(root, relative, context)
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError(
            "E_INDEX_PATH", f"missing indexed file: {relative}"
        ) from exc
    if path.is_symlink() or not stat.S_ISREG(info.st_mode):
        raise EvidenceError("E_INDEX_PATH", f"indexed file is unsafe: {relative}")
    try:
        raw = read_canonical_regular_bytes(path, context)
    except EvidenceError as exc:
        if exc.code == "E_AUTHORITY_LOCK_PATH":
            raise EvidenceError(
                "E_INDEX_PATH", f"indexed file is unsafe: {relative}"
            ) from exc
        raise
    if hashlib.sha256(raw).hexdigest() != reference["sha256"]:
        raise EvidenceError("E_INDEX_FILE_HASH", f"indexed bytes differ: {relative}")
    if canonical:
        try:
            value = json.loads(
                raw.decode("utf-8"),
                parse_constant=lambda token: (_ for _ in ()).throw(
                    ValueError(token)
                ),
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise EvidenceError("E_JSON", f"invalid indexed JSON: {relative}") from exc
        if canonical_json_bytes(value) != raw:
            raise EvidenceError(
                "E_NONCANONICAL_JSON", f"noncanonical indexed JSON: {relative}"
            )
        if isinstance(value, Mapping):
            reject_confirmatory_artifact(value, context)
    else:
        value = raw
    loaded[relative] = raw
    return path, value


def _canonical_index_snapshot(raw: bytes, context: str) -> Any:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError("E_JSON", f"invalid indexed JSON: {context}") from exc
    if canonical_json_bytes(value) != raw:
        raise EvidenceError(
            "E_NONCANONICAL_JSON", f"noncanonical indexed JSON: {context}"
        )
    if isinstance(value, Mapping):
        reject_confirmatory_artifact(value, context)
    return value


def _phase(value: Any, coverage: list[str], context: str) -> str:
    if type(value) is not str or value not in _PHASES or value not in coverage:
        raise EvidenceError("E_INDEX_PHASE", f"{context} has an unknown phase")
    return value


def _load_evidence_index(
    index_path: str | Path,
    validated_lock: Mapping[str, Any],
    authority_lock_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    source = Path(index_path)
    try:
        raw = read_canonical_regular_bytes(source, "evidence index")
    except EvidenceError as exc:
        if exc.code == "E_AUTHORITY_LOCK_PATH":
            raise EvidenceError(
                "E_INDEX_PATH", "declared evidence index path is unsafe"
            ) from exc
        raise
    try:
        parsed = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError("E_JSON", "invalid evidence index JSON") from exc
    if canonical_json_bytes(parsed) != raw:
        raise EvidenceError(
            "E_NONCANONICAL_JSON", "evidence index bytes are noncanonical"
        )
    if isinstance(parsed, Mapping):
        reject_confirmatory_artifact(parsed, "evidence_index")
    _reject_credential_metadata(parsed)
    value = validate_exact_object(parsed, _INDEX_SCHEMA, "evidence_index")
    index_sha256 = hashlib.sha256(raw).hexdigest()
    if value["schema_version"] != "P3_V3_EVIDENCE_INDEX_V3":
        raise EvidenceError("E_INDEX_SCHEMA", "evidence index schema version differs")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    validate_sha256(value["artifact_sha256"], "evidence_index.artifact_sha256")
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_INDEX_HASH", "evidence index self-hash differs")
    coverage = value["phase_coverage"]
    if any(type(item) is not str or item not in _PHASES for item in coverage):
        raise EvidenceError("E_INDEX_PHASE", "phase coverage contains an unknown phase")
    if coverage != sorted(set(coverage), key=_PHASES.index):
        raise EvidenceError("E_INDEX_PHASE", "phase coverage is not sorted and unique")

    root = source.parent
    seen: set[str] = set()
    loaded: dict[str, Any] = {}
    controller_index = validate_exact_object(
        value["controller_source"],
        _CONTROLLER_SOURCE_INDEX_SCHEMA,
        "controller_source",
    )
    controller_root = _indexed_directory(
        root, controller_index["root"], seen, "controller_source.root"
    )
    _, controller_manifest = _indexed_file(
        root,
        controller_index["manifest"],
        seen,
        loaded,
        "controller_source.manifest",
    )
    rebuilt_controller_manifest = _capture_complete_controller_source_manifest(
        controller_root
    )
    if (
        canonical_json_bytes(controller_manifest)
        != canonical_json_bytes(rebuilt_controller_manifest)
        or canonical_sha256(controller_manifest)
        != validated_lock["controller_repository"][
            "tracked_source_manifest_sha256"
        ]
    ):
        raise EvidenceError(
            "E_AUTHORITY_MANIFEST", "controller source manifest differs"
        )

    if len(value["adapter_registries"]) != 1 or len(
        value["input_generator_registries"]
    ) != 1:
        raise EvidenceError(
            "E_PROTOCOL_BINDING",
            "exactly one adapter and input-generator registry is required",
        )
    adapter_registries: list[dict[str, Any]] = []
    adapter_registry_file_sha256: list[str] = []
    for index, reference in enumerate(value["adapter_registries"]):
        locked_reference = validate_exact_object(
            reference, _REFERENCE_SCHEMA, f"adapter_registries[{index}]"
        )
        validate_sha256(
            locked_reference["sha256"], f"adapter_registries[{index}].sha256"
        )
        if locked_reference["sha256"] != validated_lock["registries"][
            "adapter_registry_sha256"
        ]:
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "adapter registry bytes differ from lock"
            )
        _, registry = _indexed_file(
            root, reference, seen, loaded, f"adapter_registries[{index}]"
        )
        _reject_credential_metadata(registry)
        adapter_registries.append(registry)
        adapter_registry_file_sha256.append(locked_reference["sha256"])
    generator_registries: list[dict[str, Any]] = []
    generator_registry_file_sha256: list[str] = []
    for index, reference in enumerate(value["input_generator_registries"]):
        locked_reference = validate_exact_object(
            reference,
            _REFERENCE_SCHEMA,
            f"input_generator_registries[{index}]",
        )
        validate_sha256(
            locked_reference["sha256"],
            f"input_generator_registries[{index}].sha256",
        )
        if locked_reference["sha256"] != validated_lock["registries"][
            "input_generator_registry_sha256"
        ]:
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "generator registry bytes differ from lock"
            )
        _, registry = _indexed_file(
            root,
            reference,
            seen,
            loaded,
            f"input_generator_registries[{index}]",
        )
        _reject_credential_metadata(registry)
        generator_registries.append(registry)
        generator_registry_file_sha256.append(locked_reference["sha256"])

    subject_authority = {
        subject["subject_id"]: subject for subject in validated_lock["subjects"]
    }
    subject_source_ids = [
        candidate.get("subject_id")
        for candidate in value["subject_sources"]
        if isinstance(candidate, Mapping)
    ]
    if subject_source_ids != list(subject_authority):
        raise EvidenceError(
            "E_AUTHORITY_MANIFEST", "subject source identities differ"
        )
    subject_sources = []
    for index, candidate in enumerate(value["subject_sources"]):
        entry = validate_exact_object(
            candidate,
            _SUBJECT_SOURCE_INDEX_SCHEMA,
            f"subject_sources[{index}]",
        )
        subject_root = _indexed_directory(
            root,
            entry["root"],
            seen,
            f"subject_sources[{index}].root",
        )
        try:
            (subject_root / ".git").lstat()
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "subject Git metadata is unsafe"
            ) from exc
        else:
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "subject Git metadata is forbidden"
            )
        _, declared_manifest = _indexed_file(
            root,
            entry["manifest"],
            seen,
            loaded,
            f"subject_sources[{index}].manifest",
        )
        rebuilt_manifest, source_snapshot = _capture_tracked_source_manifest(
            subject_root, ["."], "subject-source"
        )
        if (
            canonical_json_bytes(declared_manifest)
            != canonical_json_bytes(rebuilt_manifest)
            or canonical_sha256(declared_manifest)
            != subject_authority[entry["subject_id"]][
                "tracked_source_manifest_sha256"
            ]
        ):
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "subject source manifest differs"
            )
        subject_sources.append(
            {
                **entry,
                "root": subject_root,
                "manifest": declared_manifest,
                "source_snapshot": source_snapshot,
            }
        )
    subject_sources_by_id = {
        entry["subject_id"]: entry for entry in subject_sources
    }

    _protocol_path, protocol = _indexed_file(
        root, value["protocol"], seen, loaded, "protocol"
    )
    if value["protocol"]["sha256"] != validated_lock["protocol"]["protocol_sha256"]:
        raise EvidenceError("E_AUTHORITY_PROTOCOL", "protocol bytes differ from lock")
    protocol_artifact_index = validate_exact_object(
        value["protocol_artifacts"],
        _PROTOCOL_ARTIFACT_SCHEMA,
        "protocol_artifacts",
    )
    protocol_artifacts: dict[str, Any] = {}
    protocol_artifact_bytes: dict[str, bytes] = {}
    for field in _PROTOCOL_ARTIFACT_FIELDS:
        _artifact_path, artifact = _indexed_file(
            root,
            protocol_artifact_index[field],
            seen,
            loaded,
            f"protocol_artifacts.{field}",
            canonical=False,
        )
        protocol_digest = (
            protocol[field]
            if field in protocol
            else validated_lock["protocol"][field]
        )
        if (
            protocol_digest != protocol_artifact_index[field]["sha256"]
            or protocol_artifact_index[field]["sha256"]
            != validated_lock["protocol"][field]
        ):
            raise EvidenceError(
                "E_PROTOCOL_BINDING", f"protocol byte binding differs: {field}"
            )
        protocol_artifacts[field] = artifact
        protocol_artifact_bytes[field] = loaded[
            protocol_artifact_index[field]["path"]
        ]
    authority_rq_ids = _validate_rq_claim_authority(
        protocol_artifact_bytes["rq_spec_sha256"],
        _canonical_index_snapshot(
            protocol_artifact_bytes["claim_ceiling_sha256"],
            "claim ceiling authority",
        ),
    )
    if authority_rq_ids != validated_lock["claim_policy"]["rq_ids"]:
        raise EvidenceError(
            "E_CLAIM_SET", "indexed RQ authority differs from Authority Lock"
        )
    ledger_path, ledger_raw = _indexed_file(
        root, value["ledger"], seen, loaded, "ledger", canonical=False
    )
    _claims_path, claims_raw = _indexed_file(
        root, value["claims"], seen, loaded, "claims", canonical=False
    )
    job_root = _indexed_directory(root, value["job_root"], seen, "job_root")

    _, preflight_event = _indexed_file(
        root, value["preflight_event"], seen, loaded, "preflight_event"
    )
    _, origin_receipt = _indexed_file(
        root, value["origin_receipt"], seen, loaded, "origin_receipt"
    )
    validate_exact_object(origin_receipt, _ORIGIN_RECEIPT_SCHEMA, "origin_receipt")

    if (
        protocol["adapter_registry_sha256"]
        != value["adapter_registries"][0].get("sha256")
        or protocol["input_generator_registry_sha256"]
        != value["input_generator_registries"][0].get("sha256")
    ):
        raise EvidenceError(
            "E_PROTOCOL_BINDING", "protocol registry byte binding differs"
        )

    subjects: list[dict[str, Any]] = []
    for index, candidate in enumerate(value["subjects"]):
        subject = validate_exact_object(
            candidate, _SUBJECT_INDEX_SCHEMA, f"subjects[{index}]"
        )
        _phase(subject["phase"], coverage, f"subjects[{index}]")
        validate_sha256(
            subject["controlled_subject_source_id"],
            f"subjects[{index}].controlled_subject_source_id",
        )
        validate_sha256(
            subject["controlled_subject_id"], f"subjects[{index}].controlled_subject_id"
        )
        material = dict(subject)
        for field in (
            "bridge_record",
            "source_record",
            "build_descriptor",
            "adapter_discovery",
            "source_scale",
            "technique_profile",
            "sites",
            "subject",
        ):
            _, material[field] = _indexed_file(
                root, subject[field], seen, loaded, f"subjects[{index}].{field}"
            )
        source_authority = subject_sources_by_id.get(subject["subject_id"])
        if (
            source_authority is None
            or subject["source_root"]
            != value["subject_sources"][subject_source_ids.index(subject["subject_id"])][
                "root"
            ]
        ):
            raise EvidenceError(
                "E_AUTHORITY_MANIFEST", "indexed subject source authority differs"
            )
        material["source_snapshot"] = source_authority["source_snapshot"]
        validate_sha256(
            subject["adapter_registry_sha256"],
            f"subjects[{index}].adapter_registry_sha256",
        )
        validate_sha256(
            subject["input_generator_registry_sha256"],
            f"subjects[{index}].input_generator_registry_sha256",
        )
        for field in (
            "public_frame",
            "profiling_workload",
            "profiling_results",
            "common_inputs",
            "common_input_validity",
        ):
            _, material[field] = _indexed_file(
                root, subject[field], seen, loaded, f"subjects[{index}].{field}"
            )
        traces = []
        for trace_index, candidate_trace in enumerate(subject["profiling_traces"]):
            trace_entry = validate_exact_object(
                candidate_trace,
                _PROFILE_TRACE_INDEX_SCHEMA,
                f"subjects[{index}].profiling_traces[{trace_index}]",
            )
            if (
                not trace_entry["job_id"]
                or "/" in trace_entry["job_id"]
                or type(trace_entry["attempt"]) is bool
                or trace_entry["attempt"] < 1
                or not trace_entry["behavior_id"]
            ):
                raise EvidenceError(
                    "E_PROFILE_ATTEMPT_BINDING", "profiling trace identity is invalid"
                )
            _trace_path, trace = _indexed_file(
                root,
                trace_entry["artifact"],
                seen,
                loaded,
                f"subjects[{index}].profiling_traces[{trace_index}]",
            )
            traces.append(
                {
                    **trace_entry,
                    "artifact": trace,
                    "artifact_sha256": trace_entry["artifact"]["sha256"],
                }
            )
        material["profiling_traces"] = traces
        slots = []
        for slot_index, candidate_slot in enumerate(subject["slot_artifacts"]):
            slot_entry = validate_exact_object(
                candidate_slot,
                _SLOT_INDEX_SCHEMA,
                f"subjects[{index}].slot_artifacts[{slot_index}]",
            )
            validate_sha256(
                slot_entry["slot_id"],
                f"subjects[{index}].slot_artifacts[{slot_index}].slot_id",
            )
            if slot_entry["controlled_subject_id"] != subject["controlled_subject_id"]:
                raise EvidenceError(
                    "E_SLOT_COORDINATE", "slot controlled-subject coordinate differs"
                )
            _, slot = _indexed_file(
                root,
                slot_entry["artifact"],
                seen,
                loaded,
                f"subjects[{index}].slot_artifacts[{slot_index}]",
            )
            slots.append({**slot_entry, "artifact": slot})
        material["slot_artifacts"] = slots
        subjects.append(material)
    if "PHASE_1" in coverage and [
        subject["subject_id"] for subject in subjects
    ] != list(subject_authority):
        raise EvidenceError(
            "E_AUTHORITY_MANIFEST",
            "indexed subject identities do not exactly cover authority lock",
        )

    packages: list[dict[str, Any]] = []
    for index, candidate in enumerate(value["packages"]):
        entry = validate_exact_object(
            candidate, _PACKAGE_INDEX_SCHEMA, f"packages[{index}]"
        )
        _phase(entry["phase"], coverage, f"packages[{index}]")
        if entry["input_role"] not in {"A", "B_PRIMARY", "B_SENSITIVITY", "C"}:
            raise EvidenceError("E_PACKAGE_INPUT_ROLE", "package input role is unknown")
        package_root = _indexed_directory(
            root, entry["root"], seen, f"packages[{index}].root"
        )
        _, manifest = _indexed_file(
            root, entry["manifest"], seen, loaded, f"packages[{index}].manifest"
        )
        packages.append({**entry, "root": package_root, "manifest": manifest})

    receipts: list[dict[str, Any]] = []
    for index, candidate in enumerate(value["phase_receipts"]):
        entry = validate_exact_object(
            candidate, _RECEIPT_INDEX_SCHEMA, f"phase_receipts[{index}]"
        )
        _phase(entry["phase"], coverage, f"phase_receipts[{index}]")
        material = dict(entry)
        for field in ("receipt", "expected_jobs", "output_manifest"):
            _, material[field] = _indexed_file(
                root, entry[field], seen, loaded, f"phase_receipts[{index}].{field}"
            )
        receipts.append(material)

    mr_chain: dict[str, Any] = {}
    if value["mr_chain"]:
        chain = validate_exact_object(
            value["mr_chain"], _MR_CHAIN_INDEX_SCHEMA, "mr_chain"
        )
        for field, reference in chain.items():
            _, mr_chain[field] = _indexed_file(
                root, reference, seen, loaded, f"mr_chain.{field}"
            )
    p12: dict[str, Any] = {}
    if value["p12"]:
        p12_index = validate_exact_object(value["p12"], _P12_INDEX_SCHEMA, "p12")
        for field, reference in p12_index.items():
            _, p12[field] = _indexed_file(root, reference, seen, loaded, f"p12.{field}")

    indexed_directories = [
        value["controller_source"]["root"],
        *[entry["root"] for entry in value["subject_sources"]],
        value["job_root"],
        *[entry["root"] for entry in value["packages"]],
        *[entry["source_root"] for entry in value["subjects"]],
    ]
    indexed_paths = set(seen) | {source.name}
    try:
        indexed_paths.add(authority_lock_path.relative_to(root).as_posix())
    except ValueError:
        pass
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        inside_indexed_directory = any(
            relative == directory or relative.startswith(f"{directory}/")
            for directory in indexed_directories
        )
        parent_of_indexed_path = any(
            indexed.startswith(f"{relative}/") for indexed in indexed_paths
        )
        if (
            relative in indexed_paths
            or inside_indexed_directory
            or parent_of_indexed_path
        ):
            continue
        raise EvidenceError("E_INDEX_UNINDEXED", f"unindexed path: {relative}")

    if not coverage:
        raise EvidenceError("E_INDEX_COVERAGE", "phase coverage must be nonempty")
    receipt_phases = [entry["phase"] for entry in receipts]
    if len(receipt_phases) != len(set(receipt_phases)) or set(receipt_phases) != set(
        coverage
    ):
        raise EvidenceError(
            "E_INDEX_COVERAGE",
            "phase receipts must uniquely and exactly cover phase_coverage",
        )
    if "PHASE_1" in coverage and (
        not value["adapter_registries"]
        or not value["input_generator_registries"]
        or not any(subject["phase"] == "PHASE_1" for subject in subjects)
    ):
        raise EvidenceError(
            "E_INDEX_COVERAGE", "subject evidence coverage is incomplete"
        )
    if any(phase in coverage for phase in ("PHASE_2", "PHASE_3")) and not any(
        subject["slot_artifacts"] for subject in subjects
    ):
        raise EvidenceError("E_INDEX_COVERAGE", "slot evidence coverage is incomplete")
    if "PHASE_4" in coverage and not mr_chain:
        raise EvidenceError("E_INDEX_COVERAGE", "MR chain coverage is incomplete")
    if "PHASE_5" in coverage:
        phase_5_root = job_root / "PHASE_5"
        try:
            phase_5_info = phase_5_root.lstat()
        except FileNotFoundError as exc:
            raise EvidenceError(
                "E_INDEX_COVERAGE", "Phase 5 job coverage is absent"
            ) from exc
        if (
            stat.S_ISLNK(phase_5_info.st_mode)
            or not stat.S_ISDIR(phase_5_info.st_mode)
            or not any(phase_5_root.iterdir())
            or ledger_path.stat().st_size == 0
        ):
            raise EvidenceError("E_INDEX_COVERAGE", "job/ledger coverage is incomplete")
    if "PHASE_6" in coverage and not any(
        package["phase"] == "PHASE_6" for package in packages
    ):
        raise EvidenceError("E_INDEX_COVERAGE", "package coverage is incomplete")
    if "PHASE_7" in coverage and not p12:
        raise EvidenceError("E_INDEX_COVERAGE", "P12 coverage is incomplete")
    return value, {
        "root": root,
        "evidence_index_sha256": index_sha256,
        "controller_manifest": controller_manifest,
        "controller_source": controller_root,
        "subject_sources": subject_sources,
        "preflight_event": preflight_event,
        "origin_receipt": origin_receipt,
        "protocol_sha256": value["protocol"]["sha256"],
        "protocol": protocol,
        "protocol_artifacts": protocol_artifacts,
        "protocol_artifact_bytes": protocol_artifact_bytes,
        "authority_rq_ids": authority_rq_ids,
        "ledger_path": ledger_path,
        "ledger_raw": ledger_raw,
        "claims_raw": claims_raw,
        "indexed_paths": frozenset(seen),
        "job_root": job_root,
        "subjects": subjects,
        "adapter_registries": adapter_registries,
        "adapter_registry_file_sha256": adapter_registry_file_sha256,
        "generator_registries": generator_registries,
        "generator_registry_file_sha256": generator_registry_file_sha256,
        "packages": packages,
        "receipts": receipts,
        "mr_chain": mr_chain,
        "p12": p12,
    }


def _verify_claim_reconstruction(material: Mapping[str, Any]) -> dict[str, Any]:
    claims = validate_claim_ledger(
        _canonical_index_snapshot(material["claims_raw"], "claims")
    )
    indexed_claim_paths = material["indexed_paths"]
    for claim in claims["claims"]:
        if any(
            reference not in indexed_claim_paths
            for reference in claim["evidence_references"]
        ):
            raise EvidenceError(
                "E_CLAIM_EVIDENCE", "claim names evidence absent from the index"
            )

    claim_ceiling = _canonical_index_snapshot(
        material["protocol_artifact_bytes"]["claim_ceiling_sha256"],
        "claim ceiling authority",
    )
    authoritative_rqs = _validate_rq_claim_authority(
        material["protocol_artifact_bytes"]["rq_spec_sha256"],
        claim_ceiling,
    )
    authoritative_claims = [
        validate_exact_object(
            candidate,
            _CLAIM_AUTHORITY_ROW_SCHEMA,
            f"claim_ceiling_authority.claims[{index}]",
        )
        for index, candidate in enumerate(claim_ceiling["claims"])
    ]
    authoritative_claim_ids = [claim["claim_id"] for claim in authoritative_claims]
    authoritative_associations = {
        claim["claim_id"]: claim["rqs"] for claim in authoritative_claims
    }
    protocol = material["protocol"]
    if (
        not authoritative_claim_ids
        or authoritative_claim_ids != list(dict.fromkeys(authoritative_claim_ids))
        or any(
            claim["initial_status"] != "blocked"
            or not claim["rqs"]
            or claim["rqs"] != sorted(set(claim["rqs"]))
            or not set(claim["rqs"]) <= set(authoritative_rqs)
            for claim in authoritative_claims
        )
        or not authoritative_rqs
        or authoritative_rqs != material["authority_rq_ids"]
        or claims["claim_authority_sha256"]
        != protocol["claim_ceiling_sha256"]
        or claims["rq_authority_sha256"] != protocol["rq_spec_sha256"]
        or [claim["claim_id"] for claim in claims["claims"]]
        != authoritative_claim_ids
        or {
            claim["claim_id"]: claim["rqs"] for claim in claims["claims"]
        }
        != authoritative_associations
    ):
        raise EvidenceError(
            "E_CLAIM_SET", "claim ledger differs from byte-verified frozen authority"
        )
    return claims


def _dispatch_verify_evidence(args: argparse.Namespace) -> dict:
    validated_lock = load_authority_lock(
        Path(args.authority_lock), args.authority_lock_sha256
    )
    _index, material = _load_evidence_index(
        args.index, validated_lock, Path(args.authority_lock)
    )
    installed_registries = _verify_running_controller_for_evidence(
        validated_lock,
        material["controller_manifest"],
        {
            "adapter_registry": material["adapter_registries"][0],
            "input_generator_registry": material["generator_registries"][0],
        },
        material["root"],
    )
    material["adapter_registries"] = [
        installed_registries["adapter_registry"]
    ]
    material["generator_registries"] = [
        installed_registries["input_generator_registry"]
    ]
    rebuilt_origin = reconstruct_origin_receipt(
        validated_lock["preflight"], material["preflight_event"]
    )
    if canonical_json_bytes(rebuilt_origin) != canonical_json_bytes(
        material["origin_receipt"]
    ):
        raise EvidenceError("E_AUTHORITY_ORIGIN", "origin receipt bytes differ")
    execution_snapshot = _verify_locked_execution_snapshot(
        validated_lock["jobs"], material["job_root"], material["ledger_raw"]
    )
    completion = execution_snapshot.completion_counts()
    attempt_records = execution_snapshot.attempt_records()
    events = execution_snapshot.ledger_events()
    validate_protocol(
        material["protocol"], SCIENTIFIC_PLAN_SHA256, EVIDENCE_DESIGN_SHA256
    )
    if material["protocol"]["adapter_registry_sha256"] != material[
        "adapter_registry_file_sha256"
    ][0]:
        raise EvidenceError(
            "E_PROTOCOL_BINDING", "protocol adapter-registry binding differs"
        )
    if material["protocol"]["input_generator_registry_sha256"] != material[
        "generator_registry_file_sha256"
    ][0]:
        raise EvidenceError(
            "E_PROTOCOL_BINDING", "protocol input-generator binding differs"
        )
    manifests = []
    for package in material["packages"]:
        manifest = verify_materialized_package(package["root"], package["manifest"])
        classes = {record["class"] for record in manifest["files"]}
        role = package["input_role"]
        if role == "A" and manifest["role"] != "CONSTRUCTION_A":
            raise EvidenceError(
                "E_PACKAGE_INPUT_ROLE", "A package has a non-A manifest"
            )
        if (
            role in {"B_PRIMARY", "B_SENSITIVITY"}
            and manifest["role"] != "CONTROLLED_B"
        ):
            raise EvidenceError(
                "E_PACKAGE_INPUT_ROLE", "B package has a non-B manifest"
            )
        if role == "B_PRIMARY" and not classes <= PACKAGE_B_PRIMARY_CLASSES:
            raise EvidenceError(
                "E_PACKAGE_INPUT_ROLE", "primary B package contains sensitivity input"
            )
        if role == "B_SENSITIVITY" and not classes <= PACKAGE_B_SENSITIVITY_CLASSES:
            raise EvidenceError(
                "E_PACKAGE_INPUT_ROLE", "sensitivity B package contains primary input"
            )
        if role == "C" and manifest["role"] != "REAL_HOLDOUT_C":
            raise EvidenceError(
                "E_PACKAGE_INPUT_ROLE", "C package has a non-C manifest"
            )
        manifests.append(manifest)

    if material["p12"]:
        terminal_by_job: dict[str, dict[str, Any]] = {}
        for pair in attempt_records:
            intent = pair["intent"]
            result = pair["result"]
            if (
                result is None
                or intent["phase"] != "PHASE_7"
                or intent["job_role"] != "P12"
            ):
                continue
            terminal_by_job[intent["job_id"]] = {"intent": intent, "result": result}
        terminal_results = [terminal_by_job[job_id] for job_id in sorted(terminal_by_job)]
        rebuilt_summary = recompute_p12_summary(
            material["p12"]["denominator"], terminal_results
        )
        rebuilt_rows = [
            {
                "job_id": pair["intent"]["job_id"],
                "scientific_outcome": pair["result"]["scientific_outcome"],
            }
            for pair in terminal_results
        ]
        if canonical_json_bytes(material["p12"]["result_rows"]) != canonical_json_bytes(
            rebuilt_rows
        ):
            raise EvidenceError(
                "E_P12_RESULT_ROWS", "declared P12 results differ from terminal attempts"
            )
        if canonical_json_bytes(material["p12"]["summary"]) != canonical_json_bytes(
            rebuilt_summary
        ):
            raise EvidenceError(
                "E_P12_SUMMARY", "declared P12 summary differs from terminal attempts"
            )
    protocol_sha256 = material["protocol_sha256"]
    attempt_common_ids: set[str] = set()
    common_consumer_intents: dict[str, list[dict[str, Any]]] = {}
    for pair in attempt_records:
        intent = pair["intent"]
        if intent.get("protocol_sha256") != protocol_sha256:
            raise EvidenceError(
                "E_PROTOCOL_BINDING", "attempt intent is bound to another protocol"
            )
        if (
            intent.get("evaluation_input_class") == "E_COMMON"
            and intent.get("phase") != "PHASE_0"
            and intent.get("job_role") != "PROFILING"
        ):
            attempt_common_ids.add(intent["evaluation_input_id"])
            common_consumer_intents.setdefault(
                intent["evaluation_input_id"], []
            ).append(intent)
    locked_phase_jobs: dict[str, list[str]] = {}
    for locked_job in validated_lock["jobs"]:
        locked_phase_jobs.setdefault(locked_job["phase"], []).append(
            locked_job["job_id"]
        )
    for entry in material["receipts"]:
        receipt = entry["receipt"]
        if receipt.get("protocol_sha256") != protocol_sha256:
            raise EvidenceError(
                "E_PROTOCOL_BINDING", "phase receipt is bound to another protocol"
            )
        phase_events = [event for event in events if event["phase"] == entry["phase"]]
        expected_jobs = locked_phase_jobs.get(entry["phase"], [])
        if entry["expected_jobs"] != expected_jobs:
            raise EvidenceError(
                "E_PHASE_RECEIPT",
                "indexed expected jobs differ from the locked phase inventory",
            )
        verify_phase_receipt(
            receipt,
            phase_events,
            expected_jobs,
            entry["output_manifest"],
        )
        if receipt["phase_id"] != entry["phase"]:
            raise EvidenceError("E_PHASE_RECEIPT", "indexed phase differs from receipt")

    if material["mr_chain"]:
        validate_mr_inventory(
            material["mr_chain"]["candidate_frame"],
            material["mr_chain"]["custodian_receipt"],
            material["mr_chain"]["final_inventory"],
            material["mr_chain"]["portfolios"],
        )

    slot_count = 0
    slot_ids: set[str] = set()
    unassigned_attempt_ids = set(attempt_common_ids) if material["subjects"] else set()
    for subject in material["subjects"]:
        adapters = {
            registry["artifact_sha256"]: registry
            for registry in material["adapter_registries"]
        }
        generators = {
            registry["artifact_sha256"]: registry
            for registry in material["generator_registries"]
        }
        adapter_registry = adapters.get(subject["adapter_registry_sha256"])
        generator_registry = generators.get(
            subject["input_generator_registry_sha256"]
        )
        if adapter_registry is None or generator_registry is None:
            raise EvidenceError(
                "E_INDEXED_SUBJECT_REDERIVATION",
                "subject names an unverified generator or adapter registry",
            )
        rebuilt = rebuild_indexed_subject(
            {
                "source_snapshot": subject["source_snapshot"],
                "source_record": subject["source_record"],
                "build_descriptor": subject["build_descriptor"],
                "adapter_registry": adapter_registry,
                "input_generator_registry": generator_registry,
                "profiling_results": subject["profiling_results"],
                "adapter_discovery": subject["adapter_discovery"],
                "source_scale": subject["source_scale"],
                "public_frame": subject["public_frame"],
                "profiling_workload": subject["profiling_workload"],
                "common_inputs": subject["common_inputs"],
                "technique_profile": subject["technique_profile"],
                "sites": subject["sites"],
                "subject": subject["subject"],
            },
            subject["bridge_record"],
        )
        if (
            rebuilt["controlled_subject_source_id"]
            != subject["controlled_subject_source_id"]
            or rebuilt["subject"]["controlled_subject_id"]
            != subject["controlled_subject_id"]
        ):
            raise EvidenceError(
                "E_INDEXED_SUBJECT_REDERIVATION", "indexed subject identity differs"
            )

        terminal_attempts: dict[tuple[str, int], tuple[dict[str, Any], dict[str, Any]]] = {}
        for pair in attempt_records:
            intent = pair["intent"]
            result = pair["result"]
            if result is None or intent["phase"] != "PHASE_1":
                continue
            coordinate = (intent["job_id"], intent["attempt"])
            terminal_attempts[coordinate] = (intent, result)
        traces_by_behavior: dict[str, dict[str, Any]] = {}
        for trace in subject["profiling_traces"]:
            if trace["behavior_id"] in traces_by_behavior:
                raise EvidenceError(
                    "E_PROFILE_ATTEMPT_BINDING", "duplicate profiling trace behavior"
                )
            traces_by_behavior[trace["behavior_id"]] = trace
        receipt_rows = subject["profiling_results"]["results"]
        if set(traces_by_behavior) != {row["behavior_id"] for row in receipt_rows}:
            raise EvidenceError(
                "E_PROFILE_ATTEMPT_BINDING",
                "profiling trace coverage differs from profiling receipt",
            )
        used_attempts: set[tuple[str, int]] = set()
        for row in receipt_rows:
            trace = traces_by_behavior[row["behavior_id"]]
            coordinate = (trace["job_id"], trace["attempt"])
            pair = terminal_attempts.get(coordinate)
            if pair is None or coordinate in used_attempts:
                raise EvidenceError(
                    "E_PROFILE_ATTEMPT_BINDING",
                    "profiling result lacks a unique authenticated terminal attempt",
                )
            used_attempts.add(coordinate)
            intent, result = pair
            expected_trace_identity = canonical_sha256(
                {
                    "job_id": trace["job_id"],
                    "attempt": trace["attempt"],
                    "behavior_id": trace["behavior_id"],
                    "call_trace_sha256": trace["artifact_sha256"],
                    "domain": "P3-PROFILING-TRACE-v1",
                }
            )
            if (
                subject["phase"] != "PHASE_1"
                or intent["phase"] != "PHASE_1"
                or intent["job_id"] != trace["job_id"]
                or intent["attempt"] != trace["attempt"]
                or intent["job_role"] != "PROFILING"
                or intent["object_type"] != "PROFILING_BEHAVIOR"
                or intent["object_id"] != trace["behavior_id"]
                or intent["cwd_identity"] != f"subject:{subject['subject_id']}"
                or intent["argv"] != row["argv"]
                or intent["input_sha256"] != row["input_sha256"]
                or intent["environment_sha256"] != row["environment_sha256"]
                or result["exit_code"] != row["exit_code"]
                or result["stdout_sha256"] != row["stdout_sha256"]
                or result["stderr_sha256"] != row["stderr_sha256"]
                or result["failure_code"] != row["failure_code"]
                or result["call_trace_sha256"] != trace["artifact_sha256"]
                or result["call_trace_sha256"] != row["call_trace_sha256"]
                or result["call_trace_identity"] != expected_trace_identity
                or canonical_json_bytes(trace["artifact"])
                != canonical_json_bytes(row["call_trace"])
            ):
                raise EvidenceError(
                    "E_PROFILE_ATTEMPT_BINDING",
                    "profiling receipt differs from authenticated attempt and trace bytes",
                )
        subject_consumed_ids: set[str] = set()
        inventory_ids = {
            row.get("input_id") for row in subject["common_inputs"].get("rows", [])
        }
        subject_attempt_ids = unassigned_attempt_ids & inventory_ids
        subject_consumed_ids.update(subject_attempt_ids)
        unassigned_attempt_ids -= subject_attempt_ids
        for slot_entry in subject["slot_artifacts"]:
            slot = slot_entry["artifact"]
            verify_slot_chronology(slot)
            slot_id = validate_sha256(slot.get("slot_id"), "slot.slot_id")
            if slot_id != slot_entry["slot_id"]:
                raise EvidenceError(
                    "E_SLOT_COORDINATE", "slot artifact coordinate differs"
                )
            coordinate = f"{slot_entry['controlled_subject_id']}:{slot_id}"
            if coordinate in slot_ids:
                raise EvidenceError("E_SLOT_COORDINATE", "duplicate slot identity")
            slot_ids.add(coordinate)
            common_ids = slot["e_common_input_ids"]
            contract_ids = slot["e_contract_input_ids"]
            if (
                any(
                    type(input_id) is not str
                    for input_id in [*common_ids, *contract_ids]
                )
                or common_ids != list(dict.fromkeys(common_ids))
                or contract_ids != list(dict.fromkeys(contract_ids))
                or not set(common_ids) <= inventory_ids
            ):
                raise EvidenceError(
                    "E_SLOT_INPUT_ROLE", "slot input role inventories are not canonical"
                )
            contract_inventory = slot.get("e_contract")
            if contract_inventory is None:
                contract_row_ids: list[str] = []
            elif not isinstance(contract_inventory, Mapping) or not isinstance(
                contract_inventory.get("rows"), list
            ):
                raise EvidenceError(
                    "E_SLOT_INPUT_ROLE", "slot contract inventory is absent"
                )
            else:
                contract_row_ids = []
                for row in contract_inventory["rows"]:
                    if (
                        not isinstance(row, Mapping)
                        or type(row.get("input_id")) is not str
                    ):
                        raise EvidenceError(
                            "E_SLOT_INPUT_ROLE", "slot contract row identity is invalid"
                        )
                    contract_row_ids.append(row["input_id"])
            if contract_ids != contract_row_ids:
                raise EvidenceError(
                    "E_SLOT_INPUT_ROLE",
                    "declared contract IDs differ from contract rows",
                )
            if set(common_ids) & (set(contract_ids) | set(contract_row_ids)) or (
                inventory_ids & set(contract_row_ids)
            ):
                raise EvidenceError("E_SLOT_INPUT_ROLE", "slot A/B input roles overlap")
            subject_consumed_ids.update(common_ids)
            slot_count += 1
        verify_common_input_evidence(
            subject["common_inputs"],
            subject["common_input_validity"],
            controlled_subject_source_id=subject["controlled_subject_source_id"],
            public_frame=subject["public_frame"],
            profiling_workload=subject["profiling_workload"],
            consumer_input_ids=sorted(subject_consumed_ids),
            generator_registries=material["generator_registries"],
            consumer_intents=[
                intent
                for input_id in subject_attempt_ids
                for intent in common_consumer_intents[input_id]
            ],
        )
    if unassigned_attempt_ids:
        raise EvidenceError(
            "E_COMMON_CHRONOLOGY", "attempt consumed an unknown common input"
        )
    _verify_claim_reconstruction(material)
    return {
        "status": "PASS",
        "authority_lock_sha256": args.authority_lock_sha256,
        "evidence_index_sha256": material["evidence_index_sha256"],
        "subject_count": len(validated_lock["subjects"]),
        "authorized_real_p12_job_count": completion[
            "authorized_real_p12_job_count"
        ],
        "recorded_real_scientific_terminal_count": completion[
            "recorded_real_scientific_terminal_count"
        ],
        "claims_status": "blocked",
    }


def dispatch(args: argparse.Namespace) -> dict:
    if args.command == "freeze-authority-lock":
        lock = freeze_authority_lock(
            Path(args.controller_root),
            Path(args.authority_inputs),
            Path(args.output),
        )
        return {
            "authority_lock_sha256": canonical_sha256(lock),
            "controller_manifest_sha256": lock["controller_repository"][
                "tracked_source_manifest_sha256"
            ],
            "subject_count": len(lock["subjects"]),
        }
    if args.command == "validate-protocol":
        validate_protocol(
            read_canonical_json(args.protocol),
            SCIENTIFIC_PLAN_SHA256,
            EVIDENCE_DESIGN_SHA256,
        )
        return {"status": "PASS", "protocol_sha256": file_sha256(args.protocol)}
    if args.command == "verify-bridge":
        bridge = verify_pinned_bridge(args.repo_root, read_canonical_json(args.lock))
        _write_output(args.output, bridge)
        return {"status": "PASS", "bridge_sha256": canonical_sha256(bridge)}
    if args.command == "build-frames":
        return _dispatch_build_frames(args)
    if args.command == "verify-mr-inventory":
        value = validate_mr_inventory(
            read_canonical_json(args.candidate_frame),
            read_canonical_json(args.custodian_receipt),
            read_canonical_json(args.final_inventory),
            read_canonical_json(args.portfolios),
        )
        return {
            "status": "PASS",
            "inventory_sha256": value["final_inventory"]["artifact_sha256"],
        }
    if args.command == "build-package":
        allowed = None
        if args.allowed_classes:
            allowed = read_canonical_json(args.allowed_classes)
            if not isinstance(allowed, list):
                raise EvidenceError(
                    "E_PACKAGE_ALLOWED_CLASSES", "allowed-classes must be a list"
                )
        manifest = build_package(
            args.role,
            args.root,
            read_canonical_json(args.specs),
            read_canonical_json(args.parents),
            allowed_classes=allowed,
        )
        _write_output(args.output, manifest)
        return {"status": "PASS", "manifest_sha256": canonical_sha256(manifest)}
    if args.command == "verify-package":
        manifest = read_canonical_json(args.manifest)
        reject_confirmatory_artifact(manifest, "verify-package")
        verify_package(args.root, manifest)
        return {"status": "PASS", "manifest_sha256": file_sha256(args.manifest)}
    if args.command == "run-preflight":
        result = run_preflight(args.root, read_canonical_json(args.spec))
        _write_output(args.output, result)
        return result
    if args.command == "verify-run-records":
        events = verify_ledger(args.ledger)
        return {
            "status": "PASS",
            "event_count": len(events),
            "ledger_sha256": file_sha256(args.ledger),
        }
    if args.command == "close-phase":
        receipt = close_phase(
            args.phase_id,
            args.protocol_sha256,
            read_canonical_json(args.expected_jobs),
            args.ledger,
            args.output_manifest_sha256,
        )
        _write_output(args.output, receipt)
        return {"status": "PASS", "receipt_sha256": canonical_sha256(receipt)}
    if args.command == "verify-evidence":
        return _dispatch_verify_evidence(args)
    if args.command == "validate-applicability-authority":
        loaded = load_applicability_authority(
            manifest_path=Path(args.manifest),
            registry_path=Path(args.registry),
            inventory_path=Path(args.inventory),
            slot_implementation_path=Path(args.slot_implementation),
            predicate_implementation_path=Path(args.predicate_implementation),
        )
        return {
            "status": "PASS",
            "authority_id": loaded["manifest"]["authority_id"],
            "subject_count": len(loaded["controlled_subject_ids"]),
            "slot_count": len(loaded["inventory"]["slots"]),
            "manifest_sha256": loaded["manifest"]["artifact_sha256"],
        }
    raise EvidenceError("E_CLI_COMMAND", f"unsupported command: {args.command}")


def main() -> int:
    try:
        payload = dispatch(build_parser().parse_args())
    except EvidenceError as exc:
        sys.stderr.buffer.write(
            canonical_json_bytes({"status": "FAIL", "code": exc.code})
        )
        return 2
    _write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
