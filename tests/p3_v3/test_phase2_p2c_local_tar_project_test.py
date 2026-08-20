"""Machine-check P2-C packet 2026-08-20-012 criteria 1-10.

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
SCRIPT = REPO / "scripts" / "p3_v3" / "run_p2c_local_tar_project_test.py"
ATTEMPT = (
    REPO
    / "data"
    / "p3_v3"
    / "phase2_profiling"
    / "jobs"
    / "p2c-20260820-012"
    / "1"
)
INTENT_PATH = ATTEMPT / "intent.json"
RESULT_PATH = ATTEMPT / "result.json"
TRACE_PATH = ATTEMPT / "call_trace.json"
STREAMS_PATH = ATTEMPT / "project-test-streams.json"
HELP_STDOUT = ATTEMPT / "cmake-help.stdout.txt"
HELP_STDERR = ATTEMPT / "cmake-help.stderr.txt"
CTEST_STDOUT = ATTEMPT / "ctest-list.stdout.txt"
CTEST_STDOUT_HEAD = ATTEMPT / "ctest-list.stdout.head.txt"
CTEST_STDOUT_TAIL = ATTEMPT / "ctest-list.stdout.tail.txt"
SOURCE_PRESENCE_PATH = ATTEMPT / "source-presence.json"
FIND_PATH = ATTEMPT / "project-test-find.json"
ARGV_PATH = ATTEMPT / "argv-resolution.json"
TERMINAL_PATH = (
    REPO
    / "data"
    / "p3_v3"
    / "phase2_profiling"
    / "local-tar-project-test-terminal.json"
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
    "04321f42383ae60108c6113034b91f1bda7e03a21090fe400895e58f70e2f69d"
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
JOB_ID = "p2c-20260820-012"
CWD_IDENTITY = (
    "data/p3_v3/p12_intake/extracted/"
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72"
)
SOURCE_REL = "test/unit_tests/kinsol/C_serial/kin_test_getuserdata.c"
PROGRAM_NAME = "kin_test_getuserdata"
REJECTED_UNEXPANDED = ["ctest", "-R", "^NAME$"]
SPAWN_EVENT = {
    "sequence": 1,
    "module": "target:kin_test_getuserdata",
    "symbol": "kin_test_getuserdata",
    "call_kind": "PROCESS_SPAWN",
    "argument_types": [],
    "keyword_names": [],
}
EXCLUDED_COMPONENTS = {
    "POSIX_TIMER_TEST",
    "CMakeFiles",
    "CMakeTmp",
    "CompilerIdC",
    "CompilerIdCXX",
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
ARGV_KEYS = {
    "schema_version",
    "packet_id",
    "behavior_id",
    "official_program_name",
    "official_ctest_name",
    "rejected_unexpanded_argv",
    "official_extra_argv",
    "intent_argv",
    "help_has_target_kin_test_getuserdata",
    "ctest_has_name_kin_test_getuserdata",
    "source_is_regular_file",
}
STREAM_NAMES = (
    "cmake-configure.stdout.txt",
    "cmake-configure.stderr.txt",
    "cmake-help.stdout.txt",
    "cmake-help.stderr.txt",
    "ctest-list.stdout.txt",
    "ctest-list.stderr.txt",
    "cmake-build.stdout.txt",
    "cmake-build.stderr.txt",
)
SCRIPT_FORBIDDEN = (
    "--target ltest",
    "--target cvDiurnal_kry_bp",
    "--target nvector_serial_benchmark",
    "SUNDIALS_" + "TEST_UNITTESTS",
    "SUNDIALS_" + "TEST_ENABLE_UNIT_TESTS",
    "SUNDIALS_" + "TEST_DEVTESTS",
    "ENABLE_" + "XBRAID",
    "ENABLE_" + "LAPACK",
    "BUILD" + "_BENCHMARKS",
    "SUNDIALS_ENABLE_" + "BENCHMARKS",
    "git clone",
    "--filter=blob:none",
    "P12-Defect4MR",
    "qualify_cxx" + "_link",
    "boost" + "_math",
    "p3-phase1-" + "unexecuted",
    "PHASE1_PROFILING_" + "NOT_EXECUTED",
    "shutil.which",
    "verified_bridge",
)
HELP_EXACT = re.compile(r"^\.\.\.\s+kin_test_getuserdata\s*$")
HELP_NAME = re.compile(r"^\.\.\.\s+(\S+)")
CTEST_NAME = re.compile(r"^\s*Test\s+#(\d+):\s+(\S+)")


def _body_without_artifact(value: dict) -> dict:
    return {key: item for key, item in value.items() if key != "artifact_sha256"}


def _is_excluded(relpath: str) -> bool:
    return any(part in EXCLUDED_COMPONENTS for part in relpath.split("/"))


def _help_text() -> str:
    if HELP_STDOUT.is_file():
        return HELP_STDOUT.read_text(encoding="utf-8", errors="replace")
    if HELP_STDERR.is_file():
        return HELP_STDERR.read_text(encoding="utf-8", errors="replace")
    return ""


def _help_has_exact_target() -> bool:
    text = _help_text()
    names = [
        match.group(1)
        for match in (HELP_NAME.search(line) for line in text.splitlines())
        if match
    ]
    return PROGRAM_NAME in names and any(
        HELP_EXACT.match(line) for line in text.splitlines()
    )


def _ctest_list_text() -> str:
    if CTEST_STDOUT.is_file():
        return CTEST_STDOUT.read_text(encoding="utf-8", errors="replace")
    return ""


def _ctest_has_exact_name() -> bool:
    names = [
        match.group(2)
        for match in (CTEST_NAME.search(line) for line in _ctest_list_text().splitlines())
        if match
    ]
    return PROGRAM_NAME in names


def test_packet_test_does_not_import_qualification_or_invoke_cmake_or_ctest():
    loaded = set(sys.modules)
    assert "p3_v3.toolchain_qualification" not in loaded
    assert "p3_v3.pilot_build" not in loaded
    argv0 = Path(sys.argv[0]).name
    assert "cmake" not in argv0
    assert "ctest" not in argv0


def test_script_reuses_run_records_and_pins_local_tar_project_test():
    source = SCRIPT.read_text(encoding="utf-8")
    assert SCRIPT.is_file()
    assert "from p3_v3.run_records import create_intent, write_result" in source
    assert "file_sha256" in source
    assert ARCHIVE_SHA256 in source
    assert SNAPSHOT_ID in source
    assert "cmake" in source
    assert "--target help" in source or '"--target", "help"' in source
    assert "--test-dir" in source
    assert '"-N"' in source
    assert "project-test-streams.json" in source
    assert "source-presence.json" in source
    assert "project-test-find.json" in source
    assert "argv-resolution.json" in source
    assert "rejected_unexpanded_argv" in source
    assert "STREAM_LIMIT" in source
    limit = int(re.search(r"STREAM_LIMIT\s*=\s*(\d+)", source).group(1))
    assert limit >= 131072
    spawn = (
        'subprocess.run(["kin_test_getuserdata"], cwd=extracted_tree, timeout=60, '
        "capture_output=True, executable=str(binary))"
    )
    assert spawn in source
    assert 'subprocess.run(["ctest"' not in source
    assert "ctest -R" not in source
    lowered = source.lower()
    for token in SCRIPT_FORBIDDEN:
        assert token not in source
        assert token.lower() not in lowered
    archive = REPO / ARCHIVE_REL
    if archive.is_file() and not archive.is_symlink():
        assert file_sha256(archive) == ARCHIVE_SHA256


def test_intent_matches_frozen_local_tar_project_test_contract():
    intent = read_canonical_json(INTENT_PATH)
    workload = read_canonical_json(REPO / WORKLOAD_REL)
    assert set(intent) == INTENT_KEYS
    assert len(intent) == 18
    assert intent["job_id"] == JOB_ID
    assert intent["protocol_sha256"] == PROTOCOL_SHA256
    assert intent["phase"] == "PHASE_1"
    assert intent["argv"] == [PROGRAM_NAME]
    assert intent["argv"] != REJECTED_UNEXPANDED
    assert intent["cwd_identity"] == CWD_IDENTITY
    assert intent["input_sha256"] == sorted(
        {PROTOCOL_SHA256, RECEIPTS_SHA256, WORKLOAD_SHA256}
    )
    assert intent["seed"] is None
    assert intent["timeout_seconds"] == 60
    assert intent["attempt"] == 1
    assert intent["object_type"] == "PROFILING_BEHAVIOR"
    assert intent["object_id"] == BEHAVIOR_ID
    assert intent["object_id"] == workload["selected_behavior_ids"][4]
    assert canonical_sha256(workload["selected_behavior_ids"]) == IDS_SHA256
    assert intent["mr_id"] == "not-applicable"
    assert intent["evaluation_input_class"] == "E_COMMON"
    assert intent["evaluation_input_id"] == EVAL_INPUT_ID
    assert intent["repetition_id"] == 1
    assert intent["environment_id"] == "p2c-local-tar-2026-08-20-012"
    assert intent["job_role"] == "PROFILING"
    assert len(intent["environment_sha256"]) == 64
    assert intent["environment_sha256"] != PLACEHOLDER_ENV


def test_result_is_one_of_the_authorized_local_tar_project_test_terminals():
    intent = read_canonical_json(INTENT_PATH)
    result = read_canonical_json(RESULT_PATH)
    presence = read_canonical_json(SOURCE_PRESENCE_PATH)
    find = read_canonical_json(FIND_PATH)
    argv_resolution = read_canonical_json(ARGV_PATH)
    assert set(result) == RESULT_KEYS
    assert len(result) == 11
    assert result["job_id"] == JOB_ID
    assert result["attempt"] == 1
    assert result["scientific_outcome"] is None
    assert result["failure_code"] != "PHASE1_PROFILING_" + "NOT_EXECUTED"
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
    assert set(presence) == {"relative_path", "is_regular_file"}
    assert presence["relative_path"] == SOURCE_REL
    assert isinstance(presence["is_regular_file"], bool)
    assert set(find) == {"count", "paths"}
    assert find["count"] == len(find["paths"])
    assert find["paths"] == sorted(find["paths"])
    kept = [
        path
        for path in find["paths"]
        if Path(path).name == PROGRAM_NAME and not _is_excluded(path)
    ]
    assert find["paths"] == kept
    assert set(argv_resolution) == ARGV_KEYS
    assert argv_resolution["intent_argv"] == [PROGRAM_NAME]
    assert argv_resolution["rejected_unexpanded_argv"] == REJECTED_UNEXPANDED
    assert argv_resolution["official_extra_argv"] == []
    if result["failure_code"] in ALLOWED_INFRA:
        assert result["status"] == "FAIL_INFRASTRUCTURE"
        assert result["exit_code"] is None
        assert result["call_trace_sha256"] == EMPTY_TRACE_SHA256
        assert result["call_trace_sha256"] == canonical_sha256([])
        assert not TRACE_PATH.exists()
        if result["failure_code"] == "E_PROFILE_BINARY_ABSENT":
            assert (
                not presence["is_regular_file"]
                or not argv_resolution["help_has_target_kin_test_getuserdata"]
                or find["count"] != 1
            )
        return
    assert presence["is_regular_file"] is True
    assert argv_resolution["help_has_target_kin_test_getuserdata"] is True
    assert find["count"] == 1
    assert not _is_excluded(find["paths"][0])
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


def test_project_test_streams_source_presence_find_and_argv_are_persisted():
    assert STREAMS_PATH.is_file()
    assert HELP_STDOUT.is_file() or HELP_STDERR.is_file()
    assert CTEST_STDOUT.is_file() or (
        CTEST_STDOUT_HEAD.is_file() and CTEST_STDOUT_TAIL.is_file()
    )
    assert SOURCE_PRESENCE_PATH.is_file()
    assert FIND_PATH.is_file()
    assert ARGV_PATH.is_file()
    streams = json.loads(STREAMS_PATH.read_text(encoding="utf-8"))
    assert isinstance(streams, dict)
    listing_rows = []
    ctest_rows = []
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
        if name.startswith("cmake-help."):
            listing_rows.append(row)
        if name.startswith("ctest-list."):
            ctest_rows.append(row)
    assert listing_rows
    assert ctest_rows
    if "ctest-list.stdout.txt" in streams:
        assert streams["ctest-list.stdout.txt"]["nbytes"] == len(
            _ctest_list_text().encode("utf-8")
        ) or CTEST_STDOUT.is_file()
    presence = json.loads(SOURCE_PRESENCE_PATH.read_text(encoding="utf-8"))
    assert presence["relative_path"] == SOURCE_REL
    find = json.loads(FIND_PATH.read_text(encoding="utf-8"))
    for path in find["paths"]:
        assert Path(path).name == PROGRAM_NAME
        assert not _is_excluded(path)
    argv_resolution = json.loads(ARGV_PATH.read_text(encoding="utf-8"))
    assert set(argv_resolution) == ARGV_KEYS
    assert argv_resolution["schema_version"] == "p3-p2c-local-tar-project-test-argv-v1"
    assert argv_resolution["packet_id"] == "2026-08-20-012"
    assert argv_resolution["behavior_id"] == BEHAVIOR_ID
    assert argv_resolution["official_program_name"] == PROGRAM_NAME
    assert argv_resolution["official_ctest_name"] == PROGRAM_NAME
    assert argv_resolution["rejected_unexpanded_argv"] == REJECTED_UNEXPANDED
    assert argv_resolution["official_extra_argv"] == []
    assert argv_resolution["intent_argv"] == [PROGRAM_NAME]
    assert isinstance(argv_resolution["help_has_target_kin_test_getuserdata"], bool)
    assert isinstance(argv_resolution["ctest_has_name_kin_test_getuserdata"], bool)
    assert isinstance(argv_resolution["source_is_regular_file"], bool)
    assert argv_resolution["source_is_regular_file"] is presence["is_regular_file"]
    assert argv_resolution["help_has_target_kin_test_getuserdata"] is (
        _help_has_exact_target()
    )
    assert argv_resolution["ctest_has_name_kin_test_getuserdata"] is (
        _ctest_has_exact_name()
    )


def test_local_tar_project_test_terminal_is_one_row_and_blocked():
    result = read_canonical_json(RESULT_PATH)
    terminal = read_canonical_json(TERMINAL_PATH)
    assert set(terminal) == TERMINAL_KEYS
    assert terminal["schema_version"] == "p3-p2c-local-tar-project-test-terminal-v1"
    assert terminal["packet_id"] == "2026-08-20-012"
    assert terminal["scientific_target"] == "P2-C"
    assert terminal["neutral_snapshot_id"] == SNAPSHOT_ID
    assert terminal["discovery_status"] == "EXECUTABLE"
    assert terminal["adapter_id"] == "CMAKE_CTEST_V1"
    assert terminal["behavior_id"] == BEHAVIOR_ID
    assert terminal["process_argv"] == [PROGRAM_NAME]
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
