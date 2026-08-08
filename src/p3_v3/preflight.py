"""Repeatable, non-scientific preflight for one phase environment."""

from __future__ import annotations

import hashlib
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
)


_SPEC_SCHEMA = {
    "schema_version": str,
    "repository_identity": str,
    "expected_commit": str,
    "dependency_lock_path": str,
    "dependency_lock_sha256": str,
    "phase_inputs": list,
    "smoke_commands": list,
    "timeout_seconds": int,
}
_INPUT_SCHEMA = {"path": str, "sha256": str}
_GIT_OID_RE = re.compile(r"[0-9a-f]{40}")


def normalize_repository_identity(raw: str) -> str:
    patterns = (
        r"https://github.com/([^/]+/[^/]+?)(?:\.git)?$",
        r"git@github.com:([^/]+/[^/]+?)(?:\.git)?$",
        r"ssh://git@github.com/([^/]+/[^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, raw)
        if match:
            return match.group(1)
    raise EvidenceError("E_REPOSITORY_IDENTITY", f"unsupported repository origin: {raw!r}")


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    if result.returncode != 0:
        raise EvidenceError("E_PREFLIGHT_GIT", f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _stream_sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def run_preflight(
    repo_root: str | Path,
    specification: Mapping[str, Any],
    executor=subprocess.run,
) -> dict[str, Any]:
    root = Path(repo_root)
    spec = validate_exact_object(dict(specification), _SPEC_SCHEMA, "preflight")
    if spec["schema_version"] != "p3-preflight-v1":
        raise EvidenceError("E_PREFLIGHT_VERSION", "unsupported preflight schema")
    if not _GIT_OID_RE.fullmatch(spec["expected_commit"]):
        raise EvidenceError("E_PREFLIGHT_COMMIT", "expected commit is not a Git SHA-1")
    if type(spec["timeout_seconds"]) is not int or spec["timeout_seconds"] < 1:
        raise EvidenceError("E_PREFLIGHT_TIMEOUT", "timeout must be a positive integer")
    raw_origin = _git(root, "remote", "get-url", "origin")
    identity = normalize_repository_identity(raw_origin)
    if identity != spec["repository_identity"]:
        raise EvidenceError("E_PREFLIGHT_REPOSITORY", "normalized repository identity differs")
    head = _git(root, "rev-parse", "HEAD")
    if head != spec["expected_commit"]:
        raise EvidenceError("E_PREFLIGHT_COMMIT", "HEAD differs from expected commit")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=no"):
        raise EvidenceError("E_PREFLIGHT_DIRTY", "tracked worktree is dirty")

    lock_path = root / safe_relative_path(spec["dependency_lock_path"])
    validate_sha256(spec["dependency_lock_sha256"], "dependency_lock_sha256")
    if not lock_path.is_file() or file_sha256(lock_path) != spec["dependency_lock_sha256"]:
        raise EvidenceError("E_PREFLIGHT_DEPENDENCY_LOCK", "dependency lock differs")
    inputs: list[dict[str, str]] = []
    for index, candidate in enumerate(spec["phase_inputs"]):
        item = validate_exact_object(candidate, _INPUT_SCHEMA, f"phase_inputs[{index}]")
        path = safe_relative_path(item["path"]).as_posix()
        validate_sha256(item["sha256"], f"phase_inputs[{index}].sha256")
        absolute = root / path
        if not absolute.is_file() or absolute.is_symlink() or file_sha256(absolute) != item["sha256"]:
            raise EvidenceError("E_PREFLIGHT_INPUT", f"phase input differs: {path}")
        inputs.append({"path": path, "sha256": item["sha256"]})
    if [item["path"] for item in inputs] != sorted({item["path"] for item in inputs}):
        raise EvidenceError("E_PREFLIGHT_INPUT_ORDER", "phase inputs are not sorted and unique")

    smoke: list[dict[str, Any]] = []
    failure_code = ""
    for index, argv in enumerate(spec["smoke_commands"]):
        if not isinstance(argv, list) or not argv or any(type(arg) is not str or not arg for arg in argv):
            raise EvidenceError("E_PREFLIGHT_ARGV", f"smoke command {index} is invalid")
        try:
            result = executor(
                argv,
                cwd=root,
                capture_output=True,
                shell=False,
                timeout=spec["timeout_seconds"],
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or b""
            stderr = exc.stderr or b""
            smoke.append(
                {
                    "argv": argv,
                    "exit_code": None,
                    "stdout_sha256": _stream_sha(stdout),
                    "stderr_sha256": _stream_sha(stderr),
                    "status": "TIMEOUT",
                }
            )
            failure_code = "E_PREFLIGHT_TIMEOUT"
            break
        smoke.append(
            {
                "argv": argv,
                "exit_code": result.returncode,
                "stdout_sha256": _stream_sha(result.stdout),
                "stderr_sha256": _stream_sha(result.stderr),
                "status": "PASS" if result.returncode == 0 else "FAIL",
            }
        )
        if result.returncode != 0:
            failure_code = "E_PREFLIGHT_SMOKE"
            break
    disk = shutil.disk_usage(root)
    body = {
        "schema_version": "p3-preflight-result-v1",
        "status": "FAIL" if failure_code else "PASS",
        "failure_code": failure_code,
        "repository_identity": identity,
        "raw_origin": raw_origin,
        "commit": head,
        "platform": platform.system(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "disk_free_bytes": disk.free,
        "phase_inputs": inputs,
        "smoke": smoke,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}
