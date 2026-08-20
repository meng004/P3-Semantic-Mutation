#!/usr/bin/env python3
"""Local-tar P2-C PUBLIC_API header: official empty subject process argv."""

from __future__ import annotations

import argparse
import hashlib
import platform
import struct
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
    "ab27acfcaaf2f1dbdbd965d57f645c4f948520bd4998f62c3cc8ccdfb3ccd320"
)
SNAPSHOT_ID = (
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72"
)
EVAL_INPUT_ID = (
    "60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8"
)
RECEIPTS_REL = "data/p3_v3/phase1_frames/receipts.json"
PROTOCOL_REL = "data/p3_v3/protocol/protocol.json"
WORKLOAD_REL = (
    "data/p3_v3/phase1_frames/out/"
    "profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json"
)
CWD_IDENTITY = f"data/p3_v3/p12_intake/extracted/{SNAPSHOT_ID}"
ARCHIVE_REL = f"data/p3_v3/p12_intake/archives/{SNAPSHOT_ID}.tar"
JOB_ID = "p2c-20260820-013"
SOURCE_REL = "include/nvector/nvector_serial.h"
REJECTED_OTHER = ["test_nvector_serial", "1000", "0"]
INTENT_ARGV = [
    "python3",
    "scripts/p3_v3/run_p2c_local_tar_header_serial.py",
    "--root",
    ".",
    "--workload",
    WORKLOAD_REL,
    "--behavior-id",
    PINNED_BEHAVIOR,
    "--jobs-root",
    "data/p3_v3/phase2_profiling/jobs",
    "--job-id",
    JOB_ID,
    "--terminal-output",
    "data/p3_v3/phase2_profiling/local-tar-header-serial-terminal.json",
]


def _git_dir(root: Path) -> Path:
    marker = root / ".git"
    if marker.is_dir():
        return marker
    if marker.is_file():
        prefix = "gitdir:"
        for line in marker.read_text(encoding="utf-8").splitlines():
            if line.startswith(prefix):
                return Path(line[len(prefix) :].strip())
    raise EvidenceError("E_PREFLIGHT_DIR", "repository metadata missing")


def _head_commit(root: Path) -> str:
    directory = _git_dir(root)
    head = (directory / "HEAD").read_text(encoding="utf-8").strip()
    prefix = "ref:"
    if not head.startswith(prefix):
        return head
    ref = head[len(prefix) :].strip()
    loose = directory / ref
    if loose.is_file():
        return loose.read_text(encoding="utf-8").strip()
    packed = directory / "packed-refs"
    if packed.is_file():
        for line in packed.read_text(encoding="utf-8").splitlines():
            if not line or line[0] in {"#", "^"}:
                continue
            parts = line.split()
            if len(parts) == 2 and parts[1] == ref:
                return parts[0]
    raise EvidenceError("E_PREFLIGHT_COMMIT", "HEAD differs from expected commit")


def _parse_index(data: bytes) -> list[tuple[str, int, bytes]]:
    if data[:4] != b"DIRC":
        raise EvidenceError("E_PREFLIGHT_DIRTY", "tracked worktree is dirty")
    version, count = struct.unpack_from(">II", data, 4)
    if version not in {2, 3, 4}:
        raise EvidenceError("E_PREFLIGHT_DIRTY", "tracked worktree is dirty")
    offset = 12
    rows: list[tuple[str, int, bytes]] = []
    for _ in range(count):
        start = offset
        size = struct.unpack_from(">I", data, start + 36)[0]
        digest = data[start + 40 : start + 60]
        flags = struct.unpack_from(">H", data, start + 60)[0]
        offset = start + 62
        if flags & 0x4000:
            offset += 2
        end = data.index(b"\x00", offset)
        name = data[offset:end].decode("utf-8", "surrogateescape")
        offset = end + 1
        offset = start + ((offset - start + 7) & ~7)
        rows.append((name, size, digest))
    return rows


def _tracked_dirty(root: Path) -> bool:
    index = _git_dir(root) / "index"
    if not index.is_file():
        return True
    for name, size, digest in _parse_index(index.read_bytes()):
        path = root / name
        if not path.is_file() or path.is_symlink():
            return True
        raw = path.read_bytes()
        if len(raw) != size:
            return True
        blob = hashlib.sha1(
            f"blob {len(raw)}\0".encode("ascii") + raw, usedforsecurity=False
        ).digest()
        if blob != digest:
            return True
    return False


def _require_clean_baseline(root: Path) -> None:
    if _head_commit(root) != EXPECTED_COMMIT:
        raise EvidenceError("E_PREFLIGHT_COMMIT", "HEAD differs from expected commit")
    if _tracked_dirty(root):
        raise EvidenceError("E_PREFLIGHT_DIRTY", "tracked worktree is dirty")


def _environment_sha256() -> str:
    digest = canonical_sha256(
        {
            "dependency_lock_sha256": LOCK_SHA256,
            "domain": "P3-P2C-LOCAL-TAR-HEADER-SERIAL-ENV-v1",
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


def _header_is_regular(extracted_tree: Path) -> bool:
    header = extracted_tree / SOURCE_REL
    return header.is_file() and not header.is_symlink()


def _subject_row(receipts: dict) -> dict:
    for row in receipts["subjects"]:
        if row["neutral_snapshot_id"] == SNAPSHOT_ID:
            return row
    raise EvidenceError("E_SUBJECT", "pinned snapshot absent from receipts")


def _decide_outcome(
    *,
    archive: Path | None,
    extracted_tree: Path,
) -> tuple[str, str, bool]:
    header_regular = extracted_tree.is_dir() and _header_is_regular(extracted_tree)
    if archive is None:
        return "FAIL_INFRASTRUCTURE", "E_ARCHIVE_FETCH_FAILED", header_regular
    if not extracted_tree.is_dir():
        unsafe = _extract_archive(archive, extracted_tree)
        if unsafe is not None:
            return "FAIL_INFRASTRUCTURE", unsafe, False
        if not extracted_tree.is_dir():
            return "MISSING_WITH_REASON", "E_SOURCE_TREE_ABSENT", False
        header_regular = _header_is_regular(extracted_tree)
    if header_regular:
        return "MISSING_WITH_REASON", "E_PROFILE_NO_PROCESS_ARGV", True
    if extracted_tree.is_dir():
        return "MISSING_WITH_REASON", "E_SOURCE_FILE_ABSENT", False
    return "MISSING_WITH_REASON", "E_SOURCE_TREE_ABSENT", False


def _write_sidecar(attempt_dir: Path, header_regular: bool) -> None:
    write_canonical_json(
        attempt_dir / "source-presence.json",
        {"relative_path": SOURCE_REL, "is_regular_file": header_regular},
        exclusive=True,
    )
    write_canonical_json(
        attempt_dir / "argv-resolution.json",
        {
            "schema_version": "p3-p2c-local-tar-header-serial-argv-v1",
            "packet_id": "2026-08-20-013",
            "behavior_id": PINNED_BEHAVIOR,
            "official_process_argv": [],
            "official_program_name": "",
            "rejected_other_object_argv": REJECTED_OTHER,
            "intent_argv": INTENT_ARGV,
            "source_is_regular_file": header_regular,
            "subject_process_spawn_authorized": False,
        },
        exclusive=True,
    )


def _write_terminal(
    path: Path,
    *,
    subject: dict,
    status: str,
    failure_code: str,
) -> None:
    body = {
        "schema_version": "p3-p2c-local-tar-header-serial-terminal-v1",
        "packet_id": "2026-08-20-013",
        "scientific_target": "P2-C",
        "neutral_snapshot_id": SNAPSHOT_ID,
        "discovery_status": subject["discovery_status"],
        "adapter_id": subject["adapter_id"],
        "behavior_id": PINNED_BEHAVIOR,
        "process_argv": [],
        "denominator": "PROFILING_ONE_ROW",
        "formal_denominator_membership": False,
        "claims": "blocked",
        "result_status": status,
        "result_failure_code": failure_code,
        "workload_file_sha256": WORKLOAD_SHA256,
        "selected_behavior_ids_sha256": IDS_SHA256,
    }
    write_canonical_json(
        path,
        {**body, "artifact_sha256": canonical_sha256(body)},
        exclusive=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--workload", default=WORKLOAD_REL)
    parser.add_argument("--behavior-id", default=PINNED_BEHAVIOR)
    parser.add_argument("--jobs-root", default="data/p3_v3/phase2_profiling/jobs")
    parser.add_argument("--job-id", default=JOB_ID)
    parser.add_argument(
        "--terminal-output",
        default="data/p3_v3/phase2_profiling/local-tar-header-serial-terminal.json",
    )
    args = parser.parse_args(argv)
    if args.job_id != JOB_ID or args.behavior_id != PINNED_BEHAVIOR:
        raise EvidenceError("E_JOB_ID", "pinned job identity differs")
    root = Path(args.root).resolve()
    _require_clean_baseline(root)
    if file_sha256(root / PROTOCOL_REL) != PROTOCOL_SHA256:
        raise EvidenceError("E_PROTOCOL", "protocol digest differs")
    if file_sha256(root / RECEIPTS_REL) != RECEIPTS_SHA256:
        raise EvidenceError("E_RECEIPTS", "receipts digest differs")
    workload_path = root / args.workload
    if file_sha256(workload_path) != WORKLOAD_SHA256:
        raise EvidenceError("E_WORKLOAD", "workload digest differs")
    workload = read_canonical_json(workload_path)
    if canonical_sha256(workload["selected_behavior_ids"]) != IDS_SHA256:
        raise EvidenceError("E_WORKLOAD", "selected behavior digest differs")
    if workload["selected_behavior_ids"][5] != PINNED_BEHAVIOR:
        raise EvidenceError("E_WORKLOAD", "pinned behavior is not workload[5]")
    receipts = read_canonical_json(root / RECEIPTS_REL)
    subject = _subject_row(receipts)
    started = time.perf_counter()
    archive = _local_archive(root)
    extracted_tree = root / CWD_IDENTITY
    status, failure_code, header_regular = _decide_outcome(
        archive=archive,
        extracted_tree=extracted_tree,
    )
    duration = time.perf_counter() - started
    attempt_dir = root / args.jobs_root / JOB_ID / "1"
    attempt_dir.mkdir(parents=True, exist_ok=True)
    create_intent(
        attempt_dir,
        {
            "job_id": JOB_ID,
            "protocol_sha256": PROTOCOL_SHA256,
            "phase": "PHASE_1",
            "argv": INTENT_ARGV,
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
            "environment_id": "p2c-local-tar-2026-08-20-013",
            "job_role": "PROFILING",
        },
    )
    _write_sidecar(attempt_dir, header_regular)
    write_result(
        attempt_dir,
        {
            "job_id": JOB_ID,
            "attempt": 1,
            "status": status,
            "exit_code": None,
            "stdout_sha256": EMPTY_STREAM,
            "stderr_sha256": EMPTY_STREAM,
            "duration_seconds": duration,
            "failure_code": failure_code,
            "scientific_outcome": None,
            "call_trace_sha256": EMPTY_TRACE,
            "call_trace_identity": _empty_trace_identity(),
        },
    )
    _write_terminal(
        root / args.terminal_output,
        subject=subject,
        status=status,
        failure_code=failure_code,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
