"""Machine-check P2-C packet 2026-08-19-005 criteria 1-5.

Reads this packet's artifacts and frozen Phase 1 inputs. Does not invoke
cmake and does not import qualification or pilot-build modules.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from p3_v3.artifacts import canonical_sha256, read_canonical_json

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "p3_v3" / "run_p2c_one_archive_spawn.py"
ATTEMPT = (
    REPO
    / "data"
    / "p3_v3"
    / "phase2_profiling"
    / "jobs"
    / "p2c-20260819-005"
    / "1"
)
INTENT_PATH = ATTEMPT / "intent.json"
RESULT_PATH = ATTEMPT / "result.json"
TRACE_PATH = ATTEMPT / "call_trace.json"
TERMINAL_PATH = (
    REPO / "data" / "p3_v3" / "phase2_profiling" / "one-archive-terminal.json"
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
JOB_ID = "p2c-20260819-005"
CWD_IDENTITY = (
    "data/p3_v3/p12_intake/extracted/"
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72"
)
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
SCRIPT_FORBIDDEN = (
    "qualify_cxx" + "_link",
    "boost" + "_math",
    "p3-phase1-" + "unexecuted",
    "PHASE1_PROFILING_" + "NOT_EXECUTED",
)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _body_without_artifact(value: dict) -> dict:
    return {key: item for key, item in value.items() if key != "artifact_sha256"}


def test_packet_test_does_not_import_qualification_or_invoke_cmake():
    loaded = set(sys.modules)
    assert "p3_v3.toolchain_qualification" not in loaded
    assert "p3_v3.pilot_build" not in loaded
    assert "cmake" not in Path(sys.argv[0]).name


def test_script_reuses_run_records_and_pins_one_archive_cmake_spawn():
    source = SCRIPT.read_text(encoding="utf-8")
    assert SCRIPT.is_file()
    assert "from p3_v3.run_records import create_intent, write_result" in source
    assert "--filter=blob:none" in source
    assert SNAPSHOT_ID in source
    assert "cmake" in source
    assert "--target ltest" in source
    spawn = 'subprocess.run(["ltest"], cwd=extracted_tree, timeout=60, capture_output=True, executable=str(binary))'
    assert spawn in source
    assert "shutil.which" not in source
    assert "verified_bridge" not in source
    lowered = source.lower()
    for token in SCRIPT_FORBIDDEN:
        assert token not in source
        assert token.lower() not in lowered


def test_intent_matches_frozen_one_archive_contract():
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
    assert intent["environment_id"] == "p2c-one-archive-2026-08-19-005"
    assert intent["job_role"] == "PROFILING"
    assert len(intent["environment_sha256"]) == 64
    assert intent["environment_sha256"] != PLACEHOLDER_ENV


def test_result_is_one_of_the_authorized_one_archive_terminals():
    intent = read_canonical_json(INTENT_PATH)
    result = read_canonical_json(RESULT_PATH)
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
    if result["failure_code"] in ALLOWED_INFRA:
        assert result["status"] == "FAIL_INFRASTRUCTURE"
        assert result["exit_code"] is None
        assert result["call_trace_sha256"] == EMPTY_TRACE_SHA256
        assert result["call_trace_sha256"] == canonical_sha256([])
        assert not TRACE_PATH.exists()
        return
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


def test_one_archive_terminal_is_one_row_and_blocked():
    result = read_canonical_json(RESULT_PATH)
    terminal = read_canonical_json(TERMINAL_PATH)
    assert set(terminal) == TERMINAL_KEYS
    assert terminal["schema_version"] == "p3-p2c-one-archive-terminal-v1"
    assert terminal["packet_id"] == "2026-08-19-005"
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
    assert _file_sha256(REPO / WORKLOAD_REL) == WORKLOAD_SHA256
    assert terminal["selected_behavior_ids_sha256"] == IDS_SHA256
    assert terminal["artifact_sha256"] == canonical_sha256(
        _body_without_artifact(terminal)
    )
