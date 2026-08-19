#!/usr/bin/env python3
"""One-archive P2-C attempt: sparse fetch, cmake --target ltest, spawn."""

from __future__ import annotations

import argparse
import hashlib
import os
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
PINNED_GIT = "d57fa8119e47baf88c5bcff2d67346864cf3672d"
P12_URL = "https://github.com/meng004/P12-Defect4MR.git"
CLONE_DIR = Path("/tmp/p12-one-archive-005")
RECEIPTS_REL = "data/p3_v3/phase1_frames/receipts.json"
WORKLOAD_REL = (
    "data/p3_v3/phase1_frames/out/"
    "profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json"
)
CWD_IDENTITY = f"data/p3_v3/p12_intake/extracted/{SNAPSHOT_ID}"
ARCHIVE_REL = f"data/p3_v3/p12_intake/archives/{SNAPSHOT_ID}.tar"
JOB_ID = "p2c-20260819-005"
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
            "domain": "P3-P2C-ONE-ARCHIVE-ENV-v1",
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


def _git_no_prompt(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "true"
    return subprocess.run(
        args,
        cwd=None if cwd is None else str(cwd),
        capture_output=True,
        text=True,
        shell=False,
        check=False,
        timeout=180,
        env=env,
    )


def _local_archive(root: Path) -> Path | None:
    archive = root / ARCHIVE_REL
    if archive.is_file() and not archive.is_symlink() and file_sha256(archive) == ARCHIVE_SHA256:
        return archive
    return None


def _fetch_one_archive(root: Path) -> Path | None:
    existing = _local_archive(root)
    if existing is not None:
        return existing
    if CLONE_DIR.exists():
        subprocess.run(["rm", "-rf", str(CLONE_DIR)], check=False)
    clone = _git_no_prompt(
        [
            "git",
            "clone",
            "--filter=blob:none",
            "--no-checkout",
            P12_URL,
            str(CLONE_DIR),
        ]
    )
    if clone.returncode != 0:
        return None
    fetched = _git_no_prompt(
        ["git", "-C", str(CLONE_DIR), "fetch", "--depth", "1", "origin", PINNED_GIT]
    )
    if fetched.returncode != 0:
        return None
    parsed = _git_no_prompt(["git", "-C", str(CLONE_DIR), "rev-parse", "FETCH_HEAD"])
    if parsed.returncode != 0 or parsed.stdout.strip() != PINNED_GIT:
        return None
    listed = _git_no_prompt(
        ["git", "-C", str(CLONE_DIR), "ls-tree", "-r", "--name-only", "FETCH_HEAD"]
    )
    if listed.returncode != 0:
        return None
    matches = [
        path
        for path in listed.stdout.splitlines()
        if SNAPSHOT_ID in path and path.endswith(".tar")
    ]
    if not matches:
        candidate = f"release/p3-bridge-v1-package/archives/{SNAPSHOT_ID}.tar"
        matches = [candidate]
    if len(matches) != 1:
        return None
    tar_git_path = matches[0]
    sparse_init = _git_no_prompt(
        ["git", "-C", str(CLONE_DIR), "sparse-checkout", "init", "--no-cone"]
    )
    if sparse_init.returncode != 0:
        return None
    sparse_set = _git_no_prompt(
        ["git", "-C", str(CLONE_DIR), "sparse-checkout", "set", "--no-cone", tar_git_path]
    )
    if sparse_set.returncode != 0:
        return None
    checked = _git_no_prompt(["git", "-C", str(CLONE_DIR), "checkout", PINNED_GIT])
    if checked.returncode != 0:
        return None
    found_tars = [
        path
        for path in CLONE_DIR.rglob("*.tar")
        if path.is_file() and not path.is_symlink()
    ]
    if len(found_tars) != 1:
        return None
    dest = root / ARCHIVE_REL
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(found_tars[0].read_bytes())
    if file_sha256(dest) != ARCHIVE_SHA256:
        dest.unlink(missing_ok=True)
        return None
    return dest


def _extract_archive(archive: Path, extracted_tree: Path) -> str | None:
    extracted_tree.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r") as handle:
        for member in handle.getmembers():
            if member.issym() or member.islnk():
                return "E_ARCHIVE_UNSAFE"
        handle.extractall(extracted_tree)
    return None


def _named_packages(log: str) -> list[str]:
    names: list[str] = []
    for match in re.finditer(r"Could NOT find ([A-Za-z0-9_+.-]+)", log):
        names.append(match.group(1).lower())
    for match in re.finditer(r"package ['\"]([A-Za-z0-9.+-]+)['\"]", log, flags=re.I):
        names.append(match.group(1))
    allowed = []
    for name in names:
        if name in {"cmake", "ninja", "make", "gfortran", "g++", "gcc"}:
            allowed.append(name)
        elif name.startswith("lib") and name.replace("-", "").replace("+", "").isalnum():
            allowed.append(name)
    return list(dict.fromkeys(allowed))[:3]


def _cmake_configure(extracted_tree: Path, build_dir: Path) -> bool:
    configure = subprocess.run(
        ["cmake", "-S", str(extracted_tree), "-B", str(build_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    if configure.returncode == 0:
        return True
    packages = _named_packages((configure.stdout or "") + (configure.stderr or ""))
    if packages:
        subprocess.run(
            ["apt-get", "install", "-y", *packages],
            capture_output=True,
            text=True,
            check=False,
        )
        retry = subprocess.run(
            ["cmake", "-S", str(extracted_tree), "-B", str(build_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        return retry.returncode == 0
    return False


def _cmake_build_ltest(build_dir: Path) -> bool:
    # Authorized build: cmake --build <dir> --target ltest
    target_flag = "--target ltest"
    flag, name = target_flag.split()
    built = subprocess.run(
        ["cmake", "--build", str(build_dir), flag, name],
        capture_output=True,
        text=True,
        check=False,
    )
    return built.returncode == 0


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
        "environment_id": "p2c-one-archive-2026-08-19-005",
        "job_role": "PROFILING",
    }
    create_intent(attempt_dir, intent)

    extracted_tree = root / CWD_IDENTITY
    archive = _fetch_one_archive(root)
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
            if not _cmake_configure(extracted_tree, build_dir):
                status, exit_code, failure_code, stdout_sha, stderr_sha, trace_sha, trace_identity = (
                    _infra_result("E_CMAKE_CONFIGURE")
                )
            elif not _cmake_build_ltest(build_dir):
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
        "schema_version": "p3-p2c-one-archive-terminal-v1",
        "packet_id": "2026-08-19-005",
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
