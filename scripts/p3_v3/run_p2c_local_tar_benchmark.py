#!/usr/bin/env python3
"""Local-tar P2-C BENCHMARK: official program-name argv only; no spawn."""

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
    "ade4089bc6d65c77e8aff681d61d4649f4edb42892292a307533513379b8f5ff"
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
JOB_ID = "p2c-20260820-011"
STREAM_LIMIT = 131072
SOURCE_REL = "benchmarks/nvector/serial/test_nvector_performance_serial.c"
PROGRAM_NAME = "nvector_serial_benchmark"
OFFICIAL_FIELDS = [
    "vector length",
    "number of vectors",
    "number of sums",
    "number of tests",
    "cache size (MB)",
    "print timing",
]
STREAM_NAMES = (
    "cmake-configure.stdout.txt",
    "cmake-configure.stderr.txt",
    "cmake-help.stdout.txt",
    "cmake-help.stderr.txt",
)
EXCLUDED_COMPONENTS = {
    "POSIX_TIMER_TEST",
    "CMakeFiles",
    "CMakeTmp",
    "CompilerIdC",
    "CompilerIdCXX",
}
HELP_EXACT = re.compile(r"^\.\.\.\s+nvector_serial_benchmark\s*$")
HELP_NAME = re.compile(r"^\.\.\.\s+(\S+)")


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
            "domain": "P3-P2C-LOCAL-TAR-BENCHMARK-ENV-v1",
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
    (attempt_dir / name).write_bytes(payload)
    return {
        "path": name,
        "nbytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _write_benchmark_streams(
    attempt_dir: Path,
    streams: dict[str, dict[str, object]],
    *,
    exclusive: bool,
) -> None:
    write_canonical_json(attempt_dir / "benchmark-streams.json", streams, exclusive=exclusive)


def _empty_streams(attempt_dir: Path) -> dict[str, dict[str, object]]:
    return {name: _persist_stream(attempt_dir, name, b"") for name in STREAM_NAMES}


def _run_captured(argv: list[str]) -> tuple[int, bytes, bytes]:
    completed = subprocess.run(argv, capture_output=True, check=False)
    return completed.returncode, completed.stdout or b"", completed.stderr or b""


def _cmake_configure(extracted_tree: Path, build_dir: Path) -> tuple[int, bytes, bytes]:
    return _run_captured(["cmake", "-S", str(extracted_tree), "-B", str(build_dir)])


def _cmake_target_help(build_dir: Path) -> tuple[int, bytes, bytes]:
    help_flag = "--target help"
    flag, name = help_flag.split()
    return _run_captured(["cmake", "--build", str(build_dir), flag, name])


def _record_pair(
    attempt_dir: Path,
    streams: dict[str, dict[str, object]],
    stdout_name: str,
    stderr_name: str,
    stdout: bytes,
    stderr: bytes,
    *,
    exclusive: bool,
) -> dict[str, dict[str, object]]:
    streams[stdout_name] = _persist_stream(attempt_dir, stdout_name, stdout)
    streams[stderr_name] = _persist_stream(attempt_dir, stderr_name, stderr)
    _write_benchmark_streams(attempt_dir, streams, exclusive=exclusive)
    return streams


def _decode(payload: bytes) -> str:
    return payload.decode("utf-8", errors="replace")


def _help_has_exact_target(help_out: bytes, help_err: bytes) -> bool:
    text = _decode(help_out) if help_out else _decode(help_err)
    names = [
        match.group(1)
        for match in (HELP_NAME.search(line) for line in text.splitlines())
        if match
    ]
    exact = any(HELP_EXACT.match(line) for line in text.splitlines())
    return PROGRAM_NAME in names and exact


def _is_excluded(relpath: str) -> bool:
    return any(part in EXCLUDED_COMPONENTS for part in relpath.split("/"))


def _source_is_regular_file(extracted_tree: Path) -> bool:
    path = extracted_tree / SOURCE_REL
    return path.is_file() and not path.is_symlink()


def _write_source_presence(attempt_dir: Path, extracted_tree: Path) -> dict[str, object]:
    body = {
        "relative_path": SOURCE_REL,
        "is_regular_file": _source_is_regular_file(extracted_tree),
    }
    write_canonical_json(attempt_dir / "source-presence.json", body, exclusive=True)
    return body


def _find_benchmark_files(extracted_tree: Path) -> list[str]:
    found: list[str] = []
    if not extracted_tree.is_dir():
        return found
    for path in extracted_tree.rglob(PROGRAM_NAME):
        if path.is_symlink() or not path.is_file() or path.name != PROGRAM_NAME:
            continue
        relpath = path.relative_to(extracted_tree).as_posix()
        if _is_excluded(relpath):
            continue
        found.append(relpath)
    return sorted(found)


def _write_benchmark_find(attempt_dir: Path, paths: list[str]) -> dict[str, object]:
    body = {"count": len(paths), "paths": paths}
    write_canonical_json(attempt_dir / "benchmark-find.json", body, exclusive=True)
    return body


def _write_argv_resolution(
    attempt_dir: Path,
    *,
    source_is_regular_file: bool,
    help_has_target: bool,
) -> dict[str, object]:
    body = {
        "schema_version": "p3-p2c-local-tar-benchmark-argv-v1",
        "packet_id": "2026-08-20-011",
        "behavior_id": PINNED_BEHAVIOR,
        "official_program_name": PROGRAM_NAME,
        "official_extra_argv_field_count": 6,
        "official_extra_argv_fields": OFFICIAL_FIELDS,
        "official_numeric_values_found": False,
        "intent_argv": [PROGRAM_NAME],
        "spawn_authorized": False,
        "help_has_target_nvector_serial_benchmark": help_has_target,
        "source_is_regular_file": source_is_regular_file,
    }
    write_canonical_json(attempt_dir / "argv-resolution.json", body, exclusive=True)
    return body


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


def _close_absent(
    attempt_dir: Path,
    extracted_tree: Path,
    help_out: bytes,
    help_err: bytes,
    presence: dict[str, object] | None,
) -> tuple[str, None, str, str, str, str, str]:
    if presence is None:
        presence = _write_source_presence(attempt_dir, extracted_tree)
    _write_benchmark_find(attempt_dir, _find_benchmark_files(extracted_tree))
    _write_argv_resolution(
        attempt_dir,
        source_is_regular_file=bool(presence["is_regular_file"]),
        help_has_target=_help_has_exact_target(help_out, help_err),
    )
    return _infra_result("E_PROFILE_BINARY_ABSENT")


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
        raise EvidenceError("E_PINNED_ROW", "invocation is not the pinned benchmark row")
    if args.job_id != JOB_ID:
        raise EvidenceError("E_JOB_ID", "job id is not the authorized packet job")

    _require_clean_baseline(root)
    workload_path = root / args.workload
    if file_sha256(workload_path) != WORKLOAD_SHA256:
        raise EvidenceError("E_WORKLOAD", "workload file digest differs")
    workload = read_canonical_json(workload_path)
    if canonical_sha256(workload["selected_behavior_ids"]) != IDS_SHA256:
        raise EvidenceError("E_WORKLOAD", "selected behavior set digest differs")
    if workload["selected_behavior_ids"][3] != PINNED_BEHAVIOR:
        raise EvidenceError("E_PINNED_ROW", "benchmark selected behavior differs")

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
        "argv": [PROGRAM_NAME],
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
        "environment_id": "p2c-local-tar-2026-08-20-011",
        "job_role": "PROFILING",
    }
    create_intent(attempt_dir, intent)

    extracted_tree = root / CWD_IDENTITY
    archive = _local_archive(root)
    help_out = b""
    help_err = b""
    if archive is None:
        streams = _empty_streams(attempt_dir)
        _write_benchmark_streams(attempt_dir, streams, exclusive=True)
        status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
            _close_absent(attempt_dir, extracted_tree, help_out, help_err, None)
        )
        status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
            _infra_result("E_ARCHIVE_FETCH_FAILED")
        )
    else:
        unsafe = _extract_archive(archive, extracted_tree)
        if unsafe is not None:
            streams = _empty_streams(attempt_dir)
            _write_benchmark_streams(attempt_dir, streams, exclusive=True)
            _close_absent(attempt_dir, extracted_tree, help_out, help_err, None)
            status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
                _infra_result(unsafe)
            )
        else:
            presence = _write_source_presence(attempt_dir, extracted_tree)
            build_dir = extracted_tree / "_p2c_build"
            streams = _empty_streams(attempt_dir)
            _write_benchmark_streams(attempt_dir, streams, exclusive=True)
            if not presence["is_regular_file"]:
                status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
                    _close_absent(attempt_dir, extracted_tree, help_out, help_err, presence)
                )
            else:
                code, out, err = _cmake_configure(extracted_tree, build_dir)
                streams = _record_pair(
                    attempt_dir,
                    streams,
                    "cmake-configure.stdout.txt",
                    "cmake-configure.stderr.txt",
                    out,
                    err,
                    exclusive=False,
                )
                if code != 0:
                    _write_benchmark_find(attempt_dir, _find_benchmark_files(extracted_tree))
                    _write_argv_resolution(
                        attempt_dir,
                        source_is_regular_file=True,
                        help_has_target=False,
                    )
                    status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
                        _infra_result("E_CMAKE_CONFIGURE")
                    )
                else:
                    help_code, help_out, help_err = _cmake_target_help(build_dir)
                    streams = _record_pair(
                        attempt_dir,
                        streams,
                        "cmake-help.stdout.txt",
                        "cmake-help.stderr.txt",
                        help_out,
                        help_err,
                        exclusive=False,
                    )
                    if help_code != 0:
                        _write_benchmark_find(attempt_dir, _find_benchmark_files(extracted_tree))
                        _write_argv_resolution(
                            attempt_dir,
                            source_is_regular_file=True,
                            help_has_target=_help_has_exact_target(help_out, help_err),
                        )
                        status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
                            _infra_result("E_CMAKE_BUILD")
                        )
                    else:
                        status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
                            _close_absent(
                                attempt_dir,
                                extracted_tree,
                                help_out,
                                help_err,
                                presence,
                            )
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
        "schema_version": "p3-p2c-local-tar-benchmark-terminal-v1",
        "packet_id": "2026-08-20-011",
        "scientific_target": "P2-C",
        "neutral_snapshot_id": SNAPSHOT_ID,
        "discovery_status": subject["discovery_status"],
        "adapter_id": subject["adapter_id"],
        "behavior_id": PINNED_BEHAVIOR,
        "process_argv": [PROGRAM_NAME],
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
