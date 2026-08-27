from __future__ import annotations

import hashlib
import os
import signal
import stat
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    write_canonical_json,
)

RUNNER_VERSION = "p3-cxx-header-compile-profiler-v1"
COMPILE_TIMEOUT_SECONDS = 120


def header_include(entrypoint: str) -> str:
    if type(entrypoint) is not str or "\\" in entrypoint:
        raise EvidenceError("E_PROFILE_HEADER_ENTRYPOINT", "entrypoint is invalid")
    path = PurePosixPath(entrypoint)
    parts = entrypoint.split("/")
    if (
        path.is_absolute()
        or path.as_posix() != entrypoint
        or any(part in {"", ".", ".."} for part in parts)
        or parts[:2] != ["include", "boost"]
    ):
        raise EvidenceError("E_PROFILE_HEADER_ENTRYPOINT", "entrypoint escaped include/boost")
    return PurePosixPath(*parts[1:]).as_posix()


def translation_unit_bytes(entrypoint: str) -> bytes:
    include = header_include(entrypoint)
    return f"#include <{include}>\nint main() {{ return 0; }}\n".encode("utf-8")


def compile_argv(
    compiler: Path,
    include_root: Path,
    source: Path,
    object_path: Path,
    depfile: Path,
) -> list[str]:
    return [
        compiler.as_posix(), "-std=c++14", "-DBOOST_MATH_STANDALONE=1",
        "-I", include_root.as_posix(), "-MD", "-MF", depfile.as_posix(),
        "-MT", object_path.as_posix(), "-c", source.as_posix(),
        "-o", object_path.as_posix(),
    ]


def _depfile_dependency_tokens(depfile_bytes: bytes) -> list[str]:
    text = depfile_bytes.decode("utf-8")
    text = text.replace("\\\r\n", " ").replace("\\\n", " ")
    colon = None
    escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == ":":
            colon = index
            break
    if colon is None:
        raise EvidenceError("E_PROFILE_DEPFILE", "depfile target is absent")
    tokens: list[str] = []
    current: list[str] = []
    escaped = False
    for char in text[colon + 1 :]:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char.isspace():
            if current:
                tokens.append("".join(current))
                current = []
            continue
        current.append(char)
    if current:
        tokens.append("".join(current))
    return tokens


def validate_depfile_containment(
    depfile_bytes: bytes,
    include_root: Path,
    requested_header: str,
) -> None:
    if type(depfile_bytes) is not bytes:
        raise EvidenceError("E_PROFILE_DEPFILE", "depfile bytes are invalid")
    include_resolved = include_root.resolve()
    requested_resolved = (include_root / requested_header).resolve()
    found_requested = False
    for token in _depfile_dependency_tokens(depfile_bytes):
        resolved = Path(token).resolve()
        if resolved == requested_resolved:
            found_requested = True
        if "boost" in resolved.parts and not resolved.is_relative_to(include_resolved):
            raise EvidenceError(
                "E_PROFILE_DEPFILE",
                "SYSTEM_BOOST_FALLBACK",
            )
    if not found_requested:
        raise EvidenceError("E_PROFILE_DEPFILE", "requested controlled header is absent")


FROZEN_NEUTRAL_SNAPSHOT_ID = (
    "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886"
)
FROZEN_CONTROLLED_SUBJECT_SOURCE_ID = (
    "e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7"
)
FROZEN_NORMALIZED_SOURCE_TREE_SHA256 = (
    "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8"
)
FROZEN_BUILD_DESCRIPTOR_SHA256 = (
    "68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d"
)
FROZEN_PROFILING_WORKLOAD_SHA256 = (
    "982375e1fedb6ff26aa25e39cb1d65e45ff14474d4d34fca634c95ef352b036e"
)
FROZEN_ADAPTER_IMPLEMENTATION_SOURCE_SHA256 = (
    "18a7f223ef2482cd8a4a099f531ca17d4f961a8047b8d682a2e644d66aea2208"
)
PROBE_ENVIRONMENT = {"PATH": "/usr/bin"}


@dataclass(frozen=True)
class CompileProbe:
    exit_code: int | None
    stdout: bytes
    stderr: bytes
    timed_out: bool


def _require_absent(path: Path, context: str) -> Path:
    if path.exists() or path.is_symlink():
        raise EvidenceError("E_PROFILE_OUTPUT", f"{context} already exists")
    return path


def _require_real_directory(path: Path, context: str) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise EvidenceError("E_PROFILE_SOURCE", f"{context} must be a real directory")
    return path


def _require_real_compiler(path: Path) -> Path:
    resolved = path.resolve()
    try:
        info = resolved.stat()
    except OSError as exc:
        raise EvidenceError("E_PROFILE_COMPILER", "compiler is not usable") from exc
    if not stat.S_ISREG(info.st_mode):
        raise EvidenceError("E_PROFILE_COMPILER", "compiler is not a regular file")
    return path


def _exclusive_write(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(path, flags, 0o644)
    except FileExistsError as exc:
        raise EvidenceError("E_PROFILE_OUTPUT", f"{path} already exists") from exc
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


def run_compile_probe(
    argv: list[str],
    *,
    env: dict[str, str],
    timeout_seconds: int,
    popen: Callable,
) -> CompileProbe:
    try:
        proc = popen(
            argv,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            env=env,
        )
    except OSError:
        raise
    try:
        stdout, stderr = proc.communicate(timeout=timeout_seconds)
        return CompileProbe(proc.returncode, stdout, stderr, False)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError as exc:
            raise EvidenceError("E_PROFILE_PROCESS", "process control failed") from exc
        try:
            stdout, stderr = proc.communicate()
        except Exception as exc:
            raise EvidenceError("E_PROFILE_PROCESS", "process control failed") from exc
        return CompileProbe(None, stdout or b"", stderr or b"", True)
    except Exception as exc:
        raise EvidenceError("E_PROFILE_PROCESS", "process control failed") from exc


def _environment_sha256(compiler: Path, include_root: Path) -> str:
    return canonical_sha256(
        {
            "compiler_path": compiler.as_posix(),
            "compiler_realpath": compiler.resolve().as_posix(),
            "cxx_standard": "c++14",
            "include_root": include_root.as_posix(),
            "os_name": os.uname().sysname,
            "os_release": os.uname().release,
        }
    )


def _row_result(
    *,
    behavior_id: str,
    argv: list[str],
    source_bytes: bytes,
    environment_sha256: str,
    probe: CompileProbe | None,
    status: str,
    failure_code: str,
    start_error: bool = False,
) -> dict[str, Any]:
    stdout = b"" if probe is None else probe.stdout
    stderr = b"" if probe is None else probe.stderr
    return {
        "behavior_id": behavior_id,
        "status": status,
        "argv": argv,
        "input_sha256": [hashlib.sha256(source_bytes).hexdigest()],
        "environment_sha256": environment_sha256,
        "runner_version": RUNNER_VERSION,
        "exit_code": None if start_error or (probe is not None and probe.timed_out) else (
            None if probe is None else probe.exit_code
        ),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "call_trace": [],
        "call_trace_sha256": canonical_sha256([]),
        "timed_out": False if probe is None else probe.timed_out,
        "failure_code": failure_code,
        "observed_site_ids": [],
    }


def run_cxx_header_workload(
    workload: Mapping[str, Any],
    *,
    source_root: Path,
    compiler: Path,
    runtime_root: Path,
    receipt_path: Path,
    popen: Callable = subprocess.Popen,
) -> dict[str, Any]:
    if not isinstance(workload, Mapping):
        raise EvidenceError("E_WORKLOAD", "profiling workload must be an object")
    selected_rows = workload.get("selected_rows")
    selected_ids = workload.get("selected_behavior_ids")
    if (
        workload.get("artifact_sha256") != FROZEN_PROFILING_WORKLOAD_SHA256
        or not isinstance(selected_rows, list)
        or not isinstance(selected_ids, list)
        or len(selected_rows) != 20
        or len(selected_ids) != 20
    ):
        raise EvidenceError("E_PROFILE_WORKLOAD_BINDING", "workload is not the frozen 20-row artifact")
    source_root = Path(source_root)
    compiler = Path(compiler)
    runtime_root = Path(runtime_root)
    receipt_path = Path(receipt_path)
    _require_real_directory(source_root, "source root")
    include_root = _require_real_directory(source_root / "include", "include root")
    _require_real_compiler(compiler)
    _require_absent(runtime_root, "runtime root")
    _require_absent(receipt_path, "receipt")
    try:
        os.mkdir(runtime_root)
    except OSError as exc:
        raise EvidenceError("E_PROFILE_OUTPUT", "runtime root cannot be created") from exc
    environment_sha256 = _environment_sha256(compiler, include_root)
    ordered = sorted(selected_rows, key=lambda row: row["behavior_id"])
    results: list[dict[str, Any]] = []
    for row in ordered:
        behavior_id = row["behavior_id"]
        entrypoint = row["entrypoint"]
        requested = header_include(entrypoint)
        source_bytes = translation_unit_bytes(entrypoint)
        row_dir = runtime_root / behavior_id
        os.mkdir(row_dir)
        source_path = row_dir / "probe.cpp"
        object_path = row_dir / "probe.o"
        depfile_path = row_dir / "probe.d"
        stdout_path = row_dir / "stdout"
        stderr_path = row_dir / "stderr"
        _exclusive_write(source_path, source_bytes)
        argv = compile_argv(compiler, include_root, source_path, object_path, depfile_path)
        try:
            probe = run_compile_probe(
                argv,
                env=dict(PROBE_ENVIRONMENT),
                timeout_seconds=COMPILE_TIMEOUT_SECONDS,
                popen=popen,
            )
        except OSError:
            _exclusive_write(stdout_path, b"")
            _exclusive_write(stderr_path, b"")
            results.append(
                _row_result(
                    behavior_id=behavior_id,
                    argv=argv,
                    source_bytes=source_bytes,
                    environment_sha256=environment_sha256,
                    probe=None,
                    status="FAILURE",
                    failure_code="COMPILER_START_ERROR",
                    start_error=True,
                )
            )
            continue
        _exclusive_write(stdout_path, probe.stdout)
        _exclusive_write(stderr_path, probe.stderr)
        if probe.timed_out:
            results.append(
                _row_result(
                    behavior_id=behavior_id,
                    argv=argv,
                    source_bytes=source_bytes,
                    environment_sha256=environment_sha256,
                    probe=probe,
                    status="TIMEOUT",
                    failure_code="COMPILE_TIMEOUT",
                )
            )
            continue
        if probe.exit_code != 0:
            results.append(
                _row_result(
                    behavior_id=behavior_id,
                    argv=argv,
                    source_bytes=source_bytes,
                    environment_sha256=environment_sha256,
                    probe=probe,
                    status="FAILURE",
                    failure_code="COMPILE_NONZERO_EXIT",
                )
            )
            continue
        try:
            validate_depfile_containment(
                depfile_path.read_bytes(), include_root, requested
            )
        except EvidenceError as exc:
            if exc.code == "E_PROFILE_DEPFILE" and "SYSTEM_BOOST_FALLBACK" in str(exc):
                results.append(
                    _row_result(
                        behavior_id=behavior_id,
                        argv=argv,
                        source_bytes=source_bytes,
                        environment_sha256=environment_sha256,
                        probe=probe,
                        status="FAILURE",
                        failure_code="SYSTEM_BOOST_FALLBACK",
                    )
                )
                continue
            raise
        results.append(
            _row_result(
                behavior_id=behavior_id,
                argv=argv,
                source_bytes=source_bytes,
                environment_sha256=environment_sha256,
                probe=probe,
                status="MISSING_TRACE",
                failure_code="NO_SUBJECT_CALL_TRACE",
            )
        )
    body = {
        "schema_version": "p3-profiling-results-v1",
        "neutral_snapshot_id": FROZEN_NEUTRAL_SNAPSHOT_ID,
        "controlled_subject_source_id": FROZEN_CONTROLLED_SUBJECT_SOURCE_ID,
        "normalized_source_tree_sha256": FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
        "build_descriptor_sha256": FROZEN_BUILD_DESCRIPTOR_SHA256,
        "profiling_workload_sha256": FROZEN_PROFILING_WORKLOAD_SHA256,
        "adapter_implementation_source_sha256": FROZEN_ADAPTER_IMPLEMENTATION_SOURCE_SHA256,
        "runner_implementation_source_sha256": file_sha256(Path(__file__)),
        "results": results,
    }
    receipt = {**body, "artifact_sha256": canonical_sha256(body)}
    write_canonical_json(receipt_path, receipt, exclusive=True)
    return receipt
