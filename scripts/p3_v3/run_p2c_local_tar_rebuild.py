#!/usr/bin/env python3
"""Local-tar P2-C rebuild: persist cmake streams, then ltest and spawn."""

from __future__ import annotations

import argparse
import hashlib
import platform
import re
import subprocess
import sys
import tarfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import (  # noqa: E402
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    write_canonical_json,
)
from p3_v3.run_records import create_intent, write_result  # noqa: E402

EXPECTED_COMMIT = "4444061dde0159a5edd62753fe3cef2d881a308c"
PROTOCOL_SHA256 = (
    "240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519"
)
RECEIPTS_SHA256 = (
    "8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440"
)
WORKLOAD_SHA256 = (
    "db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d"
)
IDS_SHA256 = (
    "e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6"
)
LOCK_SHA256 = (
    "7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f"
)
ARCHIVE_SHA256 = (
    "c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c"
)
PLACEHOLDER_ENV = (
    "396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007"
)
EMPTY_STREAM = hashlib.sha256(b"").hexdigest()
EMPTY_TRACE = "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"
PINNED_BEHAVIOR = (
    "13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45"
)
SNAPSHOT_ID = (
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72"
)
EVAL_INPUT_ID = (
    "60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8"
)
RECEIPTS_REL = "data/p3_v3/phase1_frames/receipts.json"
WORKLOAD_REL = (
    "data/p3_v3/phase1_frames/out/"
    "profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json"
)
CWD_IDENTITY = f"data/p3_v3/p12_intake/extracted/{SNAPSHOT_ID}"
ARCHIVE_REL = f"data/p3_v3/p12_intake/archives/{SNAPSHOT_ID}.tar"
JOB_ID = "p2c-20260820-007"
STREAM_LIMIT = 65536
STREAM_NAMES = (
    "cmake-configure.stdout.txt",
    "cmake-configure.stderr.txt",
    "cmake-build.stdout.txt",
    "cmake-build.stderr.txt",
)
SPAWN_EVENT = {
    "sequence": 1,
    "module": "target:ltest",
    "symbol": "ltest",
    "call_kind": "PROCESS_SPAWN",
    "argument_types": [],
    "keyword_names": [],
}


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


def _require_clean_baseline(root: Path) -> None:
    head = _git(root, "rev-parse", "HEAD")
    if head != EXPECTED_COMMIT:
        raise EvidenceError("E_PREFLIGHT_COMMIT", "HEAD differs from expected commit")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=no"):
        raise EvidenceError("E_PREFLIGHT_DIRTY", "tracked worktree is dirty")


def _first_executable_subject(receipts: dict) -> dict:
    for row in receipts["subjects"]:
        if row["discovery_status"] == "EXECUTABLE":
            return row
    raise EvidenceError("E_SUBJECT", "no EXECUTABLE subject in receipts")


def _environment_sha256() -> str:
    digest = canonical_sha256(
        {
            "dependency_lock_sha256": LOCK_SHA256,
            "domain": "P3-P2C-LOCAL-TAR-REBUILD-ENV-v1",
            "platform": platform.system(),
            "python": platform.python_version(),
        }
    )
    if digest == PLACEHOLDER_ENV:
        raise EvidenceError("E_ENV", "environment digest collided with placeholder")
    return digest


def _empty_trace_identity() -> str:
    return canonical_sha256(
        {
            "job_id": JOB_ID,
            "attempt": 1,
            "behavior_id": PINNED_BEHAVIOR,
            "call_trace_sha256": EMPTY_TRACE,
            "domain": "P3-PROFILING-TRACE-v1",
        }
    )


def _local_archive(root: Path) -> Path | None:
    archive = root / ARCHIVE_REL
    if archive.is_file() and not archive.is_symlink() and file_sha256(archive) == ARCHIVE_SHA256:
        return archive
    return None


def _extract_archive(archive: Path, extracted_tree: Path) -> str | None:
    extracted_tree.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r") as handle:
        for member in handle.getmembers():
            if member.issym() or member.islnk():
                return "E_ARCHIVE_UNSAFE"
        handle.extractall(extracted_tree)
    return None


def _persist_stream(attempt_dir: Path, name: str, payload: bytes) -> dict[str, object]:
    visible = payload if len(payload) <= STREAM_LIMIT else payload[-STREAM_LIMIT:]
    (attempt_dir / name).write_bytes(visible)
    return {
        "path": name,
        "nbytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _write_cmake_streams(
    attempt_dir: Path,
    streams: dict[str, dict[str, object]],
    *,
    exclusive: bool,
) -> None:
    write_canonical_json(attempt_dir / "cmake-streams.json", streams, exclusive=exclusive)


def _empty_streams(attempt_dir: Path) -> dict[str, dict[str, object]]:
    return {name: _persist_stream(attempt_dir, name, b"") for name in STREAM_NAMES}


def _named_packages_from_captured(text: str) -> list[str]:
    names: list[str] = []
    for match in re.finditer(r"Could NOT find ([A-Za-z0-9_+.-]+)", text):
        names.append(match.group(1).lower())
    for match in re.finditer(r"package ['\"]([A-Za-z0-9.+-]+)['\"]", text, flags=re.I):
        names.append(match.group(1))
    allowed = []
    for name in names:
        if name in {"cmake", "ninja", "make", "gfortran", "g++", "gcc"}:
            allowed.append(name)
        elif name.startswith("lib") and name.replace("-", "").replace("+", "").isalnum():
            allowed.append(name)
    return list(dict.fromkeys(allowed))[:3]


def _captured_text(attempt_dir: Path) -> str:
    parts: list[str] = []
    for name in STREAM_NAMES:
        path = attempt_dir / name
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "".join(parts)


def _install_named(packages: list[str]) -> None:
    if not packages:
        return
    installer = ["brew", "install", *packages] if platform.system() == "Darwin" else [
        "apt-get",
        "install",
        "-y",
        *packages,
    ]
    subprocess.run(installer, capture_output=True, text=True, check=False)


def _run_cmake(argv: list[str]) -> tuple[int, bytes, bytes]:
    completed = subprocess.run(argv, capture_output=True, check=False)
    return completed.returncode, completed.stdout or b"", completed.stderr or b""


def _cmake_configure(extracted_tree: Path, build_dir: Path) -> tuple[int, bytes, bytes]:
    return _run_cmake(["cmake", "-S", str(extracted_tree), "-B", str(build_dir)])


def _cmake_build_ltest(build_dir: Path) -> tuple[int, bytes, bytes]:
    target_flag = "--target ltest"
    flag, name = target_flag.split()
    return _run_cmake(["cmake", "--build", str(build_dir), flag, name])


def _record_configure(
    attempt_dir: Path,
    streams: dict[str, dict[str, object]],
    stdout: bytes,
    stderr: bytes,
    *,
    exclusive: bool,
) -> dict[str, dict[str, object]]:
    streams["cmake-configure.stdout.txt"] = _persist_stream(
        attempt_dir, "cmake-configure.stdout.txt", stdout
    )
    streams["cmake-configure.stderr.txt"] = _persist_stream(
        attempt_dir, "cmake-configure.stderr.txt", stderr
    )
    _write_cmake_streams(attempt_dir, streams, exclusive=exclusive)
    return streams


def _record_build(
    attempt_dir: Path,
    streams: dict[str, dict[str, object]],
    stdout: bytes,
    stderr: bytes,
) -> dict[str, dict[str, object]]:
    streams["cmake-build.stdout.txt"] = _persist_stream(
        attempt_dir, "cmake-build.stdout.txt", stdout
    )
    streams["cmake-build.stderr.txt"] = _persist_stream(
        attempt_dir, "cmake-build.stderr.txt", stderr
    )
    _write_cmake_streams(attempt_dir, streams, exclusive=False)
    return streams


def _one_repair_from_logs(attempt_dir: Path) -> bool:
    streams_path = attempt_dir / "cmake-streams.json"
    if not streams_path.is_file():
        return False
    packages = _named_packages_from_captured(_captured_text(attempt_dir))
    if not packages:
        return False
    _install_named(packages)
    return True


def _tree_binary(extracted_tree: Path) -> Path | None:
    build_dir = extracted_tree / "_p2c_build"
    for root in (build_dir, extracted_tree):
        if not root.is_dir() or root.is_symlink():
            continue
        for path in root.rglob("ltest"):
            if path.is_symlink() or not path.is_file() or path.name != "ltest":
                continue
            resolved = path.resolve()
            if resolved.is_file() and not resolved.is_symlink():
                return resolved
    return None


def _spawn(extracted_tree: Path, binary: Path) -> tuple[str, int | None, str, str, str]:
    try:
        completed = subprocess.run(["ltest"], cwd=extracted_tree, timeout=60, capture_output=True, executable=str(binary))
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
        return (
            "INCONCLUSIVE",
            None,
            "E_PROFILE_TIMEOUT",
            hashlib.sha256(stdout).hexdigest(),
            hashlib.sha256(stderr).hexdigest(),
        )
    stdout_sha = hashlib.sha256(completed.stdout).hexdigest()
    stderr_sha = hashlib.sha256(completed.stderr).hexdigest()
    if completed.returncode == 0:
        return "PASS", 0, "", stdout_sha, stderr_sha
    return (
        "FAIL_SCIENTIFIC",
        completed.returncode,
        "E_PROFILE_NONZERO_EXIT",
        stdout_sha,
        stderr_sha,
    )


def _infra_result(failure_code: str) -> tuple[str, None, str, str, str, str, str]:
    return (
        "FAIL_INFRASTRUCTURE",
        None,
        failure_code,
        EMPTY_STREAM,
        EMPTY_STREAM,
        EMPTY_TRACE,
        _empty_trace_identity(),
    )


def main(argv: list[str] | None = None) -> int:
    started = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--workload", required=True)
    parser.add_argument("--behavior-id", required=True)
    parser.add_argument("--jobs-root", required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--terminal-output", required=True)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.workload != WORKLOAD_REL or args.behavior_id != PINNED_BEHAVIOR:
        raise EvidenceError("E_PINNED_ROW", "invocation is not the pinned process row")
    if args.job_id != JOB_ID:
        raise EvidenceError("E_JOB_ID", "job id is not the authorized packet job")

    _require_clean_baseline(root)
    workload_path = root / args.workload
    if file_sha256(workload_path) != WORKLOAD_SHA256:
        raise EvidenceError("E_WORKLOAD", "workload file digest differs")
    workload = read_canonical_json(workload_path)
    if canonical_sha256(workload["selected_behavior_ids"]) != IDS_SHA256:
        raise EvidenceError("E_WORKLOAD", "selected behavior set digest differs")
    if workload["selected_behavior_ids"][1] != PINNED_BEHAVIOR:
        raise EvidenceError("E_PINNED_ROW", "process-capable selected behavior differs")

    receipts_path = root / RECEIPTS_REL
    if file_sha256(receipts_path) != RECEIPTS_SHA256:
        raise EvidenceError("E_RECEIPTS", "receipts digest differs")
    subject = _first_executable_subject(read_canonical_json(receipts_path))
    if subject["neutral_snapshot_id"] != SNAPSHOT_ID:
        raise EvidenceError("E_SUBJECT", "first EXECUTABLE subject differs")

    attempt_dir = root / args.jobs_root / args.job_id / "1"
    intent = {
        "job_id": JOB_ID,
        "protocol_sha256": PROTOCOL_SHA256,
        "phase": "PHASE_1",
        "argv": ["ltest"],
        "cwd_identity": CWD_IDENTITY,
        "environment_sha256": _environment_sha256(),
        "input_sha256": sorted(
            {PROTOCOL_SHA256, RECEIPTS_SHA256, WORKLOAD_SHA256}
        ),
        "seed": None,
        "timeout_seconds": 60,
        "attempt": 1,
        "object_type": "PROFILING_BEHAVIOR",
        "object_id": PINNED_BEHAVIOR,
        "mr_id": "not-applicable",
        "evaluation_input_class": "E_COMMON",
        "evaluation_input_id": EVAL_INPUT_ID,
        "repetition_id": 1,
        "environment_id": "p2c-local-tar-2026-08-20-007",
        "job_role": "PROFILING",
    }
    create_intent(attempt_dir, intent)

    extracted_tree = root / CWD_IDENTITY
    archive = _local_archive(root)
    if archive is None:
        status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
            _infra_result("E_ARCHIVE_FETCH_FAILED")
        )
    else:
        unsafe = _extract_archive(archive, extracted_tree)
        if unsafe is not None:
            status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
                _infra_result(unsafe)
            )
        else:
            build_dir = extracted_tree / "_p2c_build"
            streams = _empty_streams(attempt_dir)
            _write_cmake_streams(attempt_dir, streams, exclusive=True)
            code, out, err = _cmake_configure(extracted_tree, build_dir)
            streams = _record_configure(attempt_dir, streams, out, err, exclusive=False)
            repaired = False
            if code != 0:
                repaired = _one_repair_from_logs(attempt_dir)
                if repaired:
                    code, out, err = _cmake_configure(extracted_tree, build_dir)
                    streams = _record_configure(
                        attempt_dir, streams, out, err, exclusive=False
                    )
            if code != 0:
                status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
                    _infra_result("E_CMAKE_CONFIGURE")
                )
            else:
                code, out, err = _cmake_build_ltest(build_dir)
                streams = _record_build(attempt_dir, streams, out, err)
                if code != 0 and not repaired:
                    repaired = _one_repair_from_logs(attempt_dir)
                    if repaired:
                        code, out, err = _cmake_configure(extracted_tree, build_dir)
                        streams = _record_configure(
                            attempt_dir, streams, out, err, exclusive=False
                        )
                        if code == 0:
                            code, out, err = _cmake_build_ltest(build_dir)
                            streams = _record_build(attempt_dir, streams, out, err)
                if code != 0:
                    status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
                        _infra_result("E_CMAKE_BUILD")
                    )
                else:
                    binary = _tree_binary(extracted_tree)
                    if binary is None:
                        status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
                            _infra_result("E_PROFILE_BINARY_ABSENT")
                        )
                    else:
                        status, exit_code, failure_code, stdout_sha, stderr_sha = _spawn(
                            extracted_tree, binary
                        )
                        write_canonical_json(
                            attempt_dir / "call_trace.json", [SPAWN_EVENT], exclusive=True
                        )
                        trace_sha = canonical_sha256([SPAWN_EVENT])
                        trace_identity = canonical_sha256(
                            {
                                "job_id": JOB_ID,
                                "attempt": 1,
                                "behavior_id": PINNED_BEHAVIOR,
                                "call_trace_sha256": trace_sha,
                                "domain": "P3-PROFILING-TRACE-v1",
                            }
                        )

    result = {
        "job_id": JOB_ID,
        "attempt": 1,
        "status": status,
        "exit_code": exit_code,
        "stdout_sha256": stdout_sha,
        "stderr_sha256": stderr_sha,
        "duration_seconds": time.monotonic() - started,
        "failure_code": failure_code,
        "scientific_outcome": None,
        "call_trace_sha256": trace_sha,
        "call_trace_identity": trace_identity,
    }
    write_result(attempt_dir, result)

    terminal_body = {
        "schema_version": "p3-p2c-local-tar-rebuild-terminal-v1",
        "packet_id": "2026-08-20-007",
        "scientific_target": "P2-C",
        "neutral_snapshot_id": SNAPSHOT_ID,
        "discovery_status": subject["discovery_status"],
        "adapter_id": subject["adapter_id"],
        "behavior_id": PINNED_BEHAVIOR,
        "process_argv": ["ltest"],
        "denominator": "PROFILING_ONE_ROW",
        "formal_denominator_membership": False,
        "claims": "blocked",
        "result_status": result["status"],
        "result_failure_code": result["failure_code"],
        "workload_file_sha256": WORKLOAD_SHA256,
        "selected_behavior_ids_sha256": IDS_SHA256,
    }
    terminal_body["artifact_sha256"] = canonical_sha256(terminal_body)
    terminal_path = Path(args.terminal_output)
    if not terminal_path.is_absolute():
        terminal_path = root / terminal_path
    write_canonical_json(terminal_path, terminal_body, exclusive=True)
    sys.stdout.buffer.write(
        (
            '{"status":"%s","failure_code":"%s","artifact_sha256":"%s"}\n'
            % (
                result["status"],
                result["failure_code"],
                terminal_body["artifact_sha256"],
            )
        ).encode("utf-8")
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvidenceError as exc:
        sys.stderr.write(f"{exc}\n")
        raise SystemExit(2)
