"""Machine-check P2-C packet 2026-08-20-013 criteria 1-9.

Reads this packet's artifacts and frozen Phase 1 inputs. Does not invoke
a compiler and does not import qualification or pilot-build modules.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from p3_v3.artifacts import canonical_sha256, file_sha256, read_canonical_json

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "p3_v3" / "run_p2c_local_tar_header_serial.py"
ATTEMPT = (
    REPO
    / "data"
    / "p3_v3"
    / "phase2_profiling"
    / "jobs"
    / "p2c-20260820-013"
    / "1"
)
INTENT_PATH = ATTEMPT / "intent.json"
RESULT_PATH = ATTEMPT / "result.json"
TRACE_PATH = ATTEMPT / "call_trace.json"
SOURCE_PRESENCE_PATH = ATTEMPT / "source-presence.json"
ARGV_PATH = ATTEMPT / "argv-resolution.json"
TERMINAL_PATH = (
    REPO
    / "data"
    / "p3_v3"
    / "phase2_profiling"
    / "local-tar-header-serial-terminal.json"
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
    "ab27acfcaaf2f1dbdbd965d57f645c4f948520bd4998f62c3cc8ccdfb3ccd320"
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
JOB_ID = "p2c-20260820-013"
CWD_IDENTITY = (
    "data/p3_v3/p12_intake/extracted/"
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72"
)
SOURCE_REL = "include/nvector/nvector_serial.h"
INTENT_ARGV = [
    "python3",
    "scripts/p3_v3/run_p2c_local_tar_header_serial.py",
    "--root",
    ".",
    "--workload",
    (
        "data/p3_v3/phase1_frames/out/"
        "profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json"
    ),
    "--behavior-id",
    BEHAVIOR_ID,
    "--jobs-root",
    "data/p3_v3/phase2_profiling/jobs",
    "--job-id",
    JOB_ID,
    "--terminal-output",
    "data/p3_v3/phase2_profiling/local-tar-header-serial-terminal.json",
]
REJECTED_OTHER = ["test_nvector_serial", "1000", "0"]
FORBIDDEN_FAILURE = {
    "E_PROFILE_BINARY_ABSENT",
    "E_PROFILE_TIMEOUT",
    "E_PROFILE_NONZERO_EXIT",
}
ALLOWED_TERMINALS = {
    ("FAIL_INFRASTRUCTURE", "E_ARCHIVE_FETCH_FAILED"),
    ("FAIL_INFRASTRUCTURE", "E_ARCHIVE_UNSAFE"),
    ("MISSING_WITH_REASON", "E_SOURCE_TREE_ABSENT"),
    ("MISSING_WITH_REASON", "E_SOURCE_FILE_ABSENT"),
    ("MISSING_WITH_REASON", "E_PROFILE_NO_PROCESS_ARGV"),
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
    "official_process_argv",
    "official_program_name",
    "rejected_other_object_argv",
    "intent_argv",
    "source_is_regular_file",
    "subject_process_spawn_authorized",
}
SCRIPT_FORBIDDEN = (
    "cmake",
    "ctest",
    "meson",
    "autotools",
    "--target ltest",
    "--target test_nvector_serial",
    "ENABLE_" + "XBRAID",
    "BUILD" + "_BENCHMARKS",
    "SUNDIALS_" + "TEST_UNITTESTS",
    "git clone",
    "--filter=blob:none",
    "P12-Defect4MR",
    "qualify_cxx" + "_link",
    "boost" + "_math",
    "p3-phase1-" + "unexecuted",
    "PHASE1_PROFILING_" + "NOT_EXECUTED",
    "shutil.which",
    "subprocess",
)


def _body_without_artifact(value: dict) -> dict:
    return {key: item for key, item in value.items() if key != "artifact_sha256"}


def test_packet_test_does_not_import_qualification_or_invoke_compiler():
    loaded = set(sys.modules)
    assert "p3_v3.toolchain_qualification" not in loaded
    assert "p3_v3.pilot_build" not in loaded
    argv0 = Path(sys.argv[0]).name
    assert "cc" != argv0
    assert "c++" != argv0


def test_script_reuses_run_records_and_pins_local_tar_header_serial():
    source = SCRIPT.read_text(encoding="utf-8")
    assert SCRIPT.is_file()
    assert "from p3_v3.run_records import create_intent, write_result" in source
    assert "file_sha256" in source
    assert ARCHIVE_SHA256 in source
    assert SNAPSHOT_ID in source
    assert "source-presence.json" in source
    assert "argv-resolution.json" in source
    assert "official_process_argv" in source
    assert "rejected_other_object_argv" in source
    assert "subject_process_spawn_authorized" in source
    lowered = source.lower()
    for token in SCRIPT_FORBIDDEN:
        assert token not in source
        assert token.lower() not in lowered
    archive = REPO / ARCHIVE_REL
    if archive.is_file() and not archive.is_symlink():
        assert file_sha256(archive) == ARCHIVE_SHA256


def test_intent_matches_frozen_local_tar_header_serial_contract():
    intent = read_canonical_json(INTENT_PATH)
    workload = read_canonical_json(REPO / WORKLOAD_REL)
    assert set(intent) == INTENT_KEYS
    assert len(intent) == 18
    assert intent["job_id"] == JOB_ID
    assert intent["protocol_sha256"] == PROTOCOL_SHA256
    assert intent["phase"] == "PHASE_1"
    assert intent["argv"] == INTENT_ARGV
    assert len(intent["argv"]) == 14
    assert intent["argv"] != []
    assert intent["argv"] != ["nvector_serial"]
    assert intent["argv"] != ["test_nvector_serial"]
    assert intent["argv"] != REJECTED_OTHER
    assert intent["cwd_identity"] == CWD_IDENTITY
    assert intent["input_sha256"] == sorted(
        {PROTOCOL_SHA256, RECEIPTS_SHA256, WORKLOAD_SHA256}
    )
    assert intent["seed"] is None
    assert intent["timeout_seconds"] == 60
    assert intent["attempt"] == 1
    assert intent["object_type"] == "PROFILING_BEHAVIOR"
    assert intent["object_id"] == BEHAVIOR_ID
    assert intent["object_id"] == workload["selected_behavior_ids"][5]
    assert canonical_sha256(workload["selected_behavior_ids"]) == IDS_SHA256
    assert intent["mr_id"] == "not-applicable"
    assert intent["evaluation_input_class"] == "E_COMMON"
    assert intent["evaluation_input_id"] == EVAL_INPUT_ID
    assert intent["repetition_id"] == 1
    assert intent["environment_id"] == "p2c-local-tar-2026-08-20-013"
    assert intent["job_role"] == "PROFILING"
    assert len(intent["environment_sha256"]) == 64
    assert intent["environment_sha256"] != PLACEHOLDER_ENV


def test_result_is_one_of_the_authorized_local_tar_header_serial_terminals():
    intent = read_canonical_json(INTENT_PATH)
    result = read_canonical_json(RESULT_PATH)
    presence = read_canonical_json(SOURCE_PRESENCE_PATH)
    argv_resolution = read_canonical_json(ARGV_PATH)
    assert set(result) == RESULT_KEYS
    assert len(result) == 11
    assert result["job_id"] == JOB_ID
    assert result["attempt"] == 1
    assert result["scientific_outcome"] is None
    assert result["failure_code"] != "PHASE1_PROFILING_" + "NOT_EXECUTED"
    assert result["failure_code"] not in FORBIDDEN_FAILURE
    assert result["status"] != "PASS"
    assert result["duration_seconds"] >= 0
    assert len(result["stdout_sha256"]) == 64
    assert len(result["stderr_sha256"]) == 64
    assert result["call_trace_sha256"] == EMPTY_TRACE_SHA256
    assert result["call_trace_sha256"] == canonical_sha256([])
    assert result["call_trace_identity"] == canonical_sha256(
        {
            "job_id": intent["job_id"],
            "attempt": 1,
            "behavior_id": intent["object_id"],
            "call_trace_sha256": result["call_trace_sha256"],
            "domain": "P3-PROFILING-TRACE-v1",
        }
    )
    assert not TRACE_PATH.exists()
    assert set(presence) == {"relative_path", "is_regular_file"}
    assert presence["relative_path"] == SOURCE_REL
    assert isinstance(presence["is_regular_file"], bool)
    assert set(argv_resolution) == ARGV_KEYS
    assert argv_resolution["official_process_argv"] == []
    assert argv_resolution["official_program_name"] == ""
    assert argv_resolution["rejected_other_object_argv"] == REJECTED_OTHER
    assert argv_resolution["intent_argv"] == INTENT_ARGV
    assert argv_resolution["subject_process_spawn_authorized"] is False
    assert (result["status"], result["failure_code"]) in ALLOWED_TERMINALS
    if result["failure_code"] == "E_PROFILE_NO_PROCESS_ARGV":
        assert result["status"] == "MISSING_WITH_REASON"
        assert presence["is_regular_file"] is True
        return
    if result["failure_code"] == "E_SOURCE_FILE_ABSENT":
        assert result["status"] == "MISSING_WITH_REASON"
        assert presence["is_regular_file"] is False
        return
    if result["failure_code"] == "E_SOURCE_TREE_ABSENT":
        assert result["status"] == "MISSING_WITH_REASON"
        return
    assert result["status"] == "FAIL_INFRASTRUCTURE"


def test_source_presence_and_argv_resolution_are_persisted():
    assert SOURCE_PRESENCE_PATH.is_file()
    assert ARGV_PATH.is_file()
    presence = read_canonical_json(SOURCE_PRESENCE_PATH)
    argv_resolution = read_canonical_json(ARGV_PATH)
    assert presence["relative_path"] == SOURCE_REL
    assert set(argv_resolution) == ARGV_KEYS
    assert argv_resolution["schema_version"] == "p3-p2c-local-tar-header-serial-argv-v1"
    assert argv_resolution["packet_id"] == "2026-08-20-013"
    assert argv_resolution["behavior_id"] == BEHAVIOR_ID
    assert argv_resolution["official_process_argv"] == []
    assert argv_resolution["official_program_name"] == ""
    assert argv_resolution["rejected_other_object_argv"] == REJECTED_OTHER
    assert argv_resolution["intent_argv"] == INTENT_ARGV
    assert isinstance(argv_resolution["source_is_regular_file"], bool)
    assert argv_resolution["source_is_regular_file"] is presence["is_regular_file"]
    assert argv_resolution["subject_process_spawn_authorized"] is False


def test_local_tar_header_serial_terminal_is_one_row_and_blocked():
    result = read_canonical_json(RESULT_PATH)
    terminal = read_canonical_json(TERMINAL_PATH)
    assert set(terminal) == TERMINAL_KEYS
    assert terminal["schema_version"] == "p3-p2c-local-tar-header-serial-terminal-v1"
    assert terminal["packet_id"] == "2026-08-20-013"
    assert terminal["scientific_target"] == "P2-C"
    assert terminal["neutral_snapshot_id"] == SNAPSHOT_ID
    assert terminal["discovery_status"] == "EXECUTABLE"
    assert terminal["adapter_id"] == "CMA" + "KE_CTEST_V1"
    assert terminal["behavior_id"] == BEHAVIOR_ID
    assert terminal["process_argv"] == []
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
