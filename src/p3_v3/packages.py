"""Content-addressed, role-separated phase packages."""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from .artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
)


ALLOWED_CLASSES = {
    "CONSTRUCTION_A": {
        "SOURCE",
        "BUILD",
        "PUBLIC_DOC",
        "CONTRACT",
        "PROPOSAL_INPUT",
    },
    "CONTROLLED_B": {
        "SOURCE",
        "SEMANTIC_MUTANT",
        "SYNTACTIC_MUTANT",
        "MR",
        "JOB_INPUT",
    },
    "REAL_HOLDOUT_C": {
        "P12_IDENTITY",
        "P12_BUGGY",
        "P12_REVEAL",
        "REAL_JOB_INPUT",
    },
}
_SPEC_SCHEMA = {"path": str, "class": str}
_FILE_SCHEMA = {"path": str, "class": str, "mode": int, "size": int, "sha256": str}
_MANIFEST_SCHEMA = {
    "schema_version": str,
    "role": str,
    "parents": list,
    "files": list,
    "package_tree_sha256": str,
    "artifact_sha256": str,
}


def _regular_file(root: Path, relative: str) -> Path:
    path = root / safe_relative_path(relative)
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError("E_PACKAGE_MISSING", f"declared file is absent: {relative}") from exc
    if not stat.S_ISREG(info.st_mode) or path.is_symlink():
        raise EvidenceError("E_PACKAGE_FILE_TYPE", f"not a regular file: {relative}")
    return path


def _validate_role(role: Any) -> str:
    if not isinstance(role, str) or role not in ALLOWED_CLASSES:
        raise EvidenceError("E_PACKAGE_ROLE", f"unsupported package role: {role!r}")
    return role


def build_package(
    role: str,
    source_root: str | Path,
    file_specs: Sequence[Mapping[str, Any]],
    parents: Sequence[str],
) -> dict[str, Any]:
    role = _validate_role(role)
    root = Path(source_root)
    for index, parent in enumerate(parents):
        validate_sha256(parent, f"parents[{index}]")
    if list(parents) != sorted(set(parents)):
        raise EvidenceError("E_PACKAGE_PARENTS", "parent hashes must be sorted and unique")
    files: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, candidate in enumerate(file_specs):
        spec = validate_exact_object(dict(candidate), _SPEC_SCHEMA, f"file_specs[{index}]")
        relative = safe_relative_path(spec["path"]).as_posix()
        if relative in seen:
            raise EvidenceError("E_PACKAGE_DUPLICATE", f"duplicate path: {relative}")
        seen.add(relative)
        if spec["class"] not in ALLOWED_CLASSES[role]:
            raise EvidenceError(
                "E_PACKAGE_CONTENT_CLASS",
                f"{spec['class']} is forbidden in {role}",
            )
        path = _regular_file(root, relative)
        info = path.stat()
        files.append(
            {
                "path": relative,
                "class": spec["class"],
                "mode": stat.S_IMODE(info.st_mode),
                "size": info.st_size,
                "sha256": file_sha256(path),
            }
        )
    files.sort(key=lambda item: item["path"])
    body = {
        "schema_version": "p3-package-manifest-v1",
        "role": role,
        "parents": list(parents),
        "files": files,
        "package_tree_sha256": canonical_sha256(files),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _validate_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    value = validate_exact_object(dict(manifest), _MANIFEST_SCHEMA, "manifest")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PACKAGE_MANIFEST_HASH", "manifest self-hash differs")
    if value["schema_version"] != "p3-package-manifest-v1":
        raise EvidenceError("E_PACKAGE_VERSION", "unsupported package manifest")
    role = _validate_role(value["role"])
    if value["parents"] != sorted(set(value["parents"])):
        raise EvidenceError("E_PACKAGE_PARENTS", "parent hashes are not canonical")
    for index, parent in enumerate(value["parents"]):
        validate_sha256(parent, f"manifest.parents[{index}]")
    paths: list[str] = []
    for index, candidate in enumerate(value["files"]):
        record = validate_exact_object(candidate, _FILE_SCHEMA, f"manifest.files[{index}]")
        relative = safe_relative_path(record["path"]).as_posix()
        paths.append(relative)
        if record["class"] not in ALLOWED_CLASSES[role]:
            raise EvidenceError("E_PACKAGE_CONTENT_CLASS", "manifest contains forbidden class")
        if type(record["mode"]) is not int or not 0 <= record["mode"] <= 0o7777:
            raise EvidenceError("E_PACKAGE_MODE", f"invalid mode: {relative}")
        if type(record["size"]) is not int or record["size"] < 0:
            raise EvidenceError("E_PACKAGE_SIZE", f"invalid size: {relative}")
        validate_sha256(record["sha256"], f"manifest.files[{index}].sha256")
    if paths != sorted(set(paths)):
        raise EvidenceError("E_PACKAGE_DUPLICATE", "manifest paths are not sorted and unique")
    if value["package_tree_sha256"] != canonical_sha256(value["files"]):
        raise EvidenceError("E_PACKAGE_TREE", "package tree hash differs")
    return value


def verify_package(source_root: str | Path, manifest: Mapping[str, Any]) -> None:
    root = Path(source_root)
    value = _validate_manifest(manifest)
    declared = {item["path"] for item in value["files"]}
    observed: set[str] = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise EvidenceError("E_PACKAGE_FILE_TYPE", f"symlink present: {relative}")
        if path.is_file():
            observed.add(relative)
    if observed != declared:
        raise EvidenceError(
            "E_PACKAGE_FILE_SET",
            f"file set differs: missing={sorted(declared - observed)}, extra={sorted(observed - declared)}",
        )
    for record in value["files"]:
        path = _regular_file(root, record["path"])
        info = path.stat()
        if stat.S_IMODE(info.st_mode) != record["mode"]:
            raise EvidenceError("E_PACKAGE_MODE", f"mode differs: {record['path']}")
        if info.st_size != record["size"]:
            raise EvidenceError("E_PACKAGE_SIZE", f"size differs: {record['path']}")
        if file_sha256(path) != record["sha256"]:
            raise EvidenceError("E_PACKAGE_SHA256", f"bytes differ: {record['path']}")


def materialize_package(
    source_root: str | Path,
    target_root: str | Path,
    manifest: Mapping[str, Any],
) -> None:
    source = Path(source_root)
    target = Path(target_root)
    verify_package(source, manifest)
    if target.exists():
        raise EvidenceError("E_PACKAGE_TARGET_EXISTS", f"target exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{target.name}.", dir=target.parent))
    try:
        for record in manifest["files"]:
            destination = temporary / safe_relative_path(record["path"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            with (source / record["path"]).open("rb") as reader, destination.open("xb") as writer:
                shutil.copyfileobj(reader, writer)
                writer.flush()
                os.fsync(writer.fileno())
            os.chmod(destination, record["mode"])
        verify_package(temporary, manifest)
        temporary.rename(target)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
