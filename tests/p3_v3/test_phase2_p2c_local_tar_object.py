"""Machine-check P2-C packet 2026-08-20-009 criteria 1-9.

Reads this packet's artifacts and frozen Phase 1 inputs. Does not invoke
cmake or ctest and does not import qualification or pilot-build modules.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from p3_v3.artifacts import canonical_sha256, file_sha256, read_canonical_json

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "p3_v3" / "run_p2c_local_tar_object.py"
ATTEMPT = (
    REPO
    / "data"
    / "p3_v3"
    / "phase2_profiling"
    / "jobs"
    / "p2c-20260820-009"
    / "1"
)
INTENT_PATH = ATTEMPT / "intent.json"
RESULT_PATH = ATTEMPT / "result.json"
TRACE_PATH = ATTEMPT / "call_trace.json"
STREAMS_PATH = ATTEMPT / "object-streams.json"
HELP_STDOUT = ATTEMPT / "cmake-help.stdout.txt"
HELP_STDERR = ATTEMPT / "cmake-help.stderr.txt"
CTEST_STDOUT = ATTEMPT / "ctest-list.stdout.txt"
CTEST_STDERR = ATTEMPT / "ctest-list.stderr.txt"
FIND_PATH = ATTEMPT / "ltest-find.json"
RESOLUTION_PATH = ATTEMPT / "object-resolution.json"
TERMINAL_PATH = (
    REPO / "data" / "p3_v3" / "phase2_profiling" / "local-tar-object-terminal.json"
)
ARCHIVE_REL = (
    "data/p3_v3/p12_intake/archives/"
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar"
)
WORKLOAD_REL = (
    "data/p3_v3/phase1_frames/out/"
    "profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json"
)
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
ARCHIVE_SHA256 = (
    "c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c"
)
BEHAVIOR_ID = (
    "13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45"
)
SNAPSHOT_ID = (
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72"
)
EMPTY_TRACE_SHA256 = (
    "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"
)
PLACEHOLDER_ENV = (
    "396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007"
)
EVAL_INPUT_ID = (
    "60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8"
)
JOB_ID = "p2c-20260820-009"
CWD_IDENTITY = (
    "data/p3_v3/p12_intake/extracted/"
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72"
)
EXCLUDED_COMPONENTS = {
    "POSIX_TIMER_TEST",
    "CMakeFiles",
    "CMakeTmp",
    "CompilerIdC",
    "CompilerIdCXX",
}
SPAWN_EVENT = {
    "sequence": 1,
    "module": "target:ltest",
    "symbol": "ltest",
    "call_kind": "PROCESS_SPAWN",
    "argument_types": [],
    "keyword_names": [],
}
ALLOWED_INFRA = {
    "E_ARCHIVE_FETCH_FAILED",
    "E_ARCHIVE_UNSAFE",
    "E_CMAKE_CONFIGURE",
    "E_CMAKE_BUILD",
    "E_PROFILE_BINARY_ABSENT",
}
INTENT_KEYS = {
    "job_id",
    "protocol_sha256",
    "phase",
    "argv",
    "cwd_identity",
    "environment_sha256",
    "input_sha256",
    "seed",
    "timeout_seconds",
    "attempt",
    "object_type",
    "object_id",
    "mr_id",
    "evaluation_input_class",
    "evaluation_input_id",
    "repetition_id",
    "environment_id",
    "job_role",
}
RESULT_KEYS = {
    "job_id",
    "attempt",
    "status",
    "exit_code",
    "stdout_sha256",
    "stderr_sha256",
    "duration_seconds",
    "failure_code",
    "scientific_outcome",
    "call_trace_sha256",
    "call_trace_identity",
}
TERMINAL_KEYS = {
    "schema_version",
    "packet_id",
    "scientific_target",
    "neutral_snapshot_id",
    "discovery_status",
    "adapter_id",
    "behavior_id",
    "process_argv",
    "denominator",
    "formal_denominator_membership",
    "claims",
    "result_status",
    "result_failure_code",
    "workload_file_sha256",
    "selected_behavior_ids_sha256",
    "artifact_sha256",
}
RESOLUTION_KEYS = {
    "schema_version",
    "packet_id",
    "filename_hits_all",
    "filename_hits_excluded",
    "filename_hits_kept",
    "help_has_target_ltest",
    "ctest_names",
    "ctest_names_named_ltest",
    "ctest_total_tests",
    "prior_008_pass_is_pinned_cli",
}
STREAM_NAMES = (
    "cmake-configure.stdout.txt",
    "cmake-configure.stderr.txt",
    "cmake-help.stdout.txt",
    "cmake-help.stderr.txt",
    "ctest-list.stdout.txt",
    "ctest-list.stderr.txt",
)
SCRIPT_FORBIDDEN = (
    "--target ltest",
    "git clone",
    "--filter=blob:none",
    "P12-Defect4MR",
    "qualify_cxx" + "_link",
    "boost" + "_math",
    "p3-phase1-" + "unexecuted",
    "PHASE1_PROFILING_" + "NOT_EXECUTED",
    "shutil.which",
)
HELP_NAME = re.compile(r"^\.\.\.\s+(\S+)")
CTEST_NAME = re.compile(r"^\s*Test\s+#(\d+):\s+(\S+)")
TOTAL_TESTS = re.compile(r"Total Tests:\s+(\d+)")


def _body_without_artifact(value: dict) -> dict:
    return {key: item for key, item in value.items() if key != "artifact_sha256"}


def _is_excluded(relpath: str) -> bool:
    return any(part in EXCLUDED_COMPONENTS for part in relpath.split("/"))


def test_packet_test_does_not_import_qualification_or_invoke_cmake_or_ctest():
    loaded = set(sys.modules)
    assert "p3_v3.toolchain_qualification" not in loaded
    assert "p3_v3.pilot_build" not in loaded
    argv0 = Path(sys.argv[0]).name
    assert "cmake" not in argv0
    assert "ctest" not in argv0


def test_script_reuses_run_records_and_pins_local_tar_object():
    source = SCRIPT.read_text(encoding="utf-8")
    assert SCRIPT.is_file()
    assert "from p3_v3.run_records import create_intent, write_result" in source
    assert "file_sha256" in source
    assert ARCHIVE_SHA256 in source
    assert SNAPSHOT_ID in source
    assert "cmake" in source
    assert "--target help" in source
    assert "ctest --test-dir" in source or '"ctest"' in source
    assert "object-streams.json" in source
    assert "object-resolution.json" in source
    assert "ltest-find.json" in source
    assert "STREAM_LIMIT" in source
    limit = int(re.search(r"STREAM_LIMIT\s*=\s*(\d+)", source).group(1))
    assert limit >= 131072
    spawn = (
        'subprocess.run(["ltest"], cwd=extracted_tree, timeout=60, '
        "capture_output=True, executable=str(binary))"
    )
    assert spawn in source
    assert "verified_bridge" not in source
    lowered = source.lower()
    for token in SCRIPT_FORBIDDEN:
        assert token not in source
        assert token.lower() not in lowered
    archive = REPO / ARCHIVE_REL
    if archive.is_file() and not archive.is_symlink():
        assert file_sha256(archive) == ARCHIVE_SHA256


def test_intent_matches_frozen_local_tar_object_contract():
    intent = read_canonical_json(INTENT_PATH)
    workload = read_canonical_json(REPO / WORKLOAD_REL)
    assert set(intent) == INTENT_KEYS
    assert len(intent) == 18
    assert intent["job_id"] == JOB_ID
    assert intent["protocol_sha256"] == PROTOCOL_SHA256
    assert intent["phase"] == "PHASE_1"
    assert intent["argv"] == ["ltest"]
    assert intent["cwd_identity"] == CWD_IDENTITY
    assert intent["input_sha256"] == sorted(
        {PROTOCOL_SHA256, RECEIPTS_SHA256, WORKLOAD_SHA256}
    )
    assert intent["seed"] is None
    assert intent["timeout_seconds"] == 60
    assert intent["attempt"] == 1
    assert intent["object_type"] == "PROFILING_BEHAVIOR"
    assert intent["object_id"] == BEHAVIOR_ID
    assert intent["object_id"] == workload["selected_behavior_ids"][1]
    assert canonical_sha256(workload["selected_behavior_ids"]) == IDS_SHA256
    assert intent["mr_id"] == "not-applicable"
    assert intent["evaluation_input_class"] == "E_COMMON"
    assert intent["evaluation_input_id"] == EVAL_INPUT_ID
    assert intent["repetition_id"] == 1
    assert intent["environment_id"] == "p2c-local-tar-2026-08-20-009"
    assert intent["job_role"] == "PROFILING"
    assert len(intent["environment_sha256"]) == 64
    assert intent["environment_sha256"] != PLACEHOLDER_ENV


def test_result_is_one_of_the_authorized_local_tar_object_terminals():
    intent = read_canonical_json(INTENT_PATH)
    result = read_canonical_json(RESULT_PATH)
    find = read_canonical_json(FIND_PATH)
    resolution = read_canonical_json(RESOLUTION_PATH)
    assert set(result) == RESULT_KEYS
    assert len(result) == 11
    assert result["job_id"] == JOB_ID
    assert result["attempt"] == 1
    assert result["scientific_outcome"] is None
    assert result["failure_code"] != "PHASE1_PROFILING_" + "NOT_EXECUTED"
    assert result["failure_code"] != "E_SOURCE_TREE_ABSENT"
    assert result["duration_seconds"] >= 0
    assert len(result["stdout_sha256"]) == 64
    assert len(result["stderr_sha256"]) == 64
    assert result["call_trace_identity"] == canonical_sha256(
        {
            "job_id": intent["job_id"],
            "attempt": 1,
            "behavior_id": intent["object_id"],
            "call_trace_sha256": result["call_trace_sha256"],
            "domain": "P3-PROFILING-TRACE-v1",
        }
    )
    assert set(find) == {"count", "paths"}
    assert find["count"] == len(find["paths"])
    assert find["paths"] == sorted(find["paths"])
    kept = [path for path in find["paths"] if not _is_excluded(path)]
    excluded = [path for path in find["paths"] if _is_excluded(path)]
    assert resolution["filename_hits_all"] == find["paths"]
    assert resolution["filename_hits_kept"] == kept
    assert resolution["filename_hits_excluded"] == excluded
    assert resolution["prior_008_pass_is_pinned_cli"] is False
    if result["failure_code"] in ALLOWED_INFRA:
        assert result["status"] == "FAIL_INFRASTRUCTURE"
        assert result["exit_code"] is None
        assert result["call_trace_sha256"] == EMPTY_TRACE_SHA256
        assert result["call_trace_sha256"] == canonical_sha256([])
        assert not TRACE_PATH.exists()
        if result["failure_code"] == "E_PROFILE_BINARY_ABSENT":
            assert len(kept) != 1
        return
    assert len(kept) == 1
    assert not _is_excluded(kept[0])
    trace = read_canonical_json(TRACE_PATH)
    assert trace == [SPAWN_EVENT]
    assert result["call_trace_sha256"] == canonical_sha256([SPAWN_EVENT])
    if result["status"] == "PASS":
        assert result["exit_code"] == 0
        assert result["failure_code"] == ""
        return
    if result["status"] == "INCONCLUSIVE":
        assert result["failure_code"] == "E_PROFILE_TIMEOUT"
        return
    assert result["status"] == "FAIL_SCIENTIFIC"
    assert result["failure_code"] == "E_PROFILE_NONZERO_EXIT"


def test_object_streams_listings_and_resolution_are_persisted():
    assert STREAMS_PATH.is_file()
    assert HELP_STDOUT.is_file() or HELP_STDERR.is_file()
    assert CTEST_STDOUT.is_file() or CTEST_STDERR.is_file()
    assert FIND_PATH.is_file()
    assert RESOLUTION_PATH.is_file()
    streams = json.loads(STREAMS_PATH.read_text(encoding="utf-8"))
    assert isinstance(streams, dict)
    listing_rows = []
    for name in STREAM_NAMES:
        if name not in streams:
            continue
        row = streams[name]
        assert set(row) >= {"path", "nbytes", "sha256"}
        assert row["path"] == name
        assert isinstance(row["nbytes"], int)
        assert row["nbytes"] >= 0
        assert len(row["sha256"]) == 64
        on_disk = ATTEMPT / name
        if on_disk.is_file() and row["nbytes"] <= 131072:
            raw = on_disk.read_bytes()
            assert len(raw) == row["nbytes"]
            assert hashlib.sha256(raw).hexdigest() == row["sha256"]
        if name.startswith("cmake-help.") or name.startswith("ctest-list."):
            listing_rows.append(row)
    assert listing_rows
    resolution = json.loads(RESOLUTION_PATH.read_text(encoding="utf-8"))
    assert set(resolution) == RESOLUTION_KEYS
    assert resolution["schema_version"] == "p3-p2c-local-tar-object-v1"
    assert resolution["packet_id"] == "2026-08-20-009"
    assert isinstance(resolution["help_has_target_ltest"], bool)
    assert isinstance(resolution["filename_hits_all"], list)
    assert isinstance(resolution["filename_hits_excluded"], list)
    assert isinstance(resolution["filename_hits_kept"], list)
    assert isinstance(resolution["ctest_names"], list)
    assert isinstance(resolution["ctest_names_named_ltest"], list)
    assert resolution["ctest_names_named_ltest"] == [
        name for name in resolution["ctest_names"] if name == "ltest"
    ]
    assert resolution["prior_008_pass_is_pinned_cli"] is False
    if CTEST_STDOUT.is_file():
        text = CTEST_STDOUT.read_text(encoding="utf-8", errors="replace")
        parsed = [
            (int(match.group(1)), match.group(2))
            for match in (
                CTEST_NAME.search(line) for line in text.splitlines()
            )
            if match
        ]
        parsed.sort(key=lambda item: item[0])
        assert resolution["ctest_names"] == [name for _, name in parsed]
        totals = TOTAL_TESTS.findall(text)
        if totals:
            assert resolution["ctest_total_tests"] == int(totals[-1])
        else:
            assert resolution["ctest_total_tests"] is None
    if HELP_STDOUT.is_file():
        help_text = HELP_STDOUT.read_text(encoding="utf-8", errors="replace")
        names = [
            match.group(1)
            for match in (
                HELP_NAME.search(line) for line in help_text.splitlines()
            )
            if match
        ]
        assert resolution["help_has_target_ltest"] is ("ltest" in names)


def test_local_tar_object_terminal_is_one_row_and_blocked():
    result = read_canonical_json(RESULT_PATH)
    terminal = read_canonical_json(TERMINAL_PATH)
    assert set(terminal) == TERMINAL_KEYS
    assert terminal["schema_version"] == "p3-p2c-local-tar-object-terminal-v1"
    assert terminal["packet_id"] == "2026-08-20-009"
    assert terminal["scientific_target"] == "P2-C"
    assert terminal["neutral_snapshot_id"] == SNAPSHOT_ID
    assert terminal["discovery_status"] == "EXECUTABLE"
    assert terminal["adapter_id"] == "CMAKE_CTEST_V1"
    assert terminal["behavior_id"] == BEHAVIOR_ID
    assert terminal["process_argv"] == ["ltest"]
    assert terminal["denominator"] == "PROFILING_ONE_ROW"
    assert terminal["formal_denominator_membership"] is False
    assert terminal["claims"] == "blocked"
    assert terminal["result_status"] == result["status"]
    assert terminal["result_failure_code"] == result["failure_code"]
    assert terminal["workload_file_sha256"] == WORKLOAD_SHA256
    assert hashlib.sha256((REPO / WORKLOAD_REL).read_bytes()).hexdigest() == (
        WORKLOAD_SHA256
    )
    assert terminal["selected_behavior_ids_sha256"] == IDS_SHA256
    assert terminal["artifact_sha256"] == canonical_sha256(
        _body_without_artifact(terminal)
    )
