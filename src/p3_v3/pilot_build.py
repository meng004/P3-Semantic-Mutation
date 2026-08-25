"""Pilot-only Boost.Math consumer-harness build-preflight capability."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shlex
import resource
import shutil
import signal
import stat
import subprocess
import time
from pathlib import Path
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    read_regular_file_snapshot,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.pilot_source import (
    ATTEMPT2_ARCHIVE_PATH,
    ATTEMPT2_SOURCE_ROOT,
    capture_materialized_tree,
    validate_materialized_tree_with_phase1,
)
from p3_v3 import toolchain_qualification as qualification_contract

PILOT_EXECUTION_CLASS = "PILOT_ONLY"
PILOT_DENOMINATOR = "PILOT_ONLY"
QUALIFICATION_BASE_HEAD = "0e51252f23dc3be4f82eb99e4f493c103f38c620"
QUALIFICATION_ROOT = Path("/tmp/p3-cxx-link-qualification")
QUALIFICATION_INTENT_NAME = "qualification-intent.json"
QUALIFICATION_RESULT_NAME = "qualification-result.json"
QUALIFICATION_MANIFEST_NAME = "qualification-manifest.json"
QUALIFICATION_SOURCE_NAME = "qualify.cpp"
QUALIFICATION_EXECUTABLE_NAME = "qualify"
QUALIFICATION_CXX_STDOUT_NAME = "METADATA_CXX_VERSION.stdout"
QUALIFICATION_CXX_STDERR_NAME = "METADATA_CXX_VERSION.stderr"
QUALIFICATION_INTENT_SHA256 = "0a13766c565e89e32a21bc69ba0f449dc8a79c48a66a7bcace54c63faa224860"
QUALIFICATION_RESULT_SHA256 = "68aaac07c2d5ad4f834f114e1a0ac011052176f2a20ea63793f483357c31f6c2"
QUALIFICATION_MANIFEST_SHA256 = "5ef4c89e9601303b9e40e3fcda07c68055664cf53fb578d6efb1d39fc5f27c9a"
QUALIFICATION_SOURCE_SHA256 = "91193433e324b0a1e525cfecac51f43ca0f6bd882e1c34292510c9740115bf5c"
QUALIFICATION_EXECUTABLE_SHA256 = "9d24d5298272942e95333acf18b05052b4c9d701aeaf92f7252a4d9666228b3b"
QUALIFICATION_FIXED_HASHES = {
    QUALIFICATION_INTENT_NAME: QUALIFICATION_INTENT_SHA256,
    QUALIFICATION_RESULT_NAME: QUALIFICATION_RESULT_SHA256,
    QUALIFICATION_MANIFEST_NAME: QUALIFICATION_MANIFEST_SHA256,
    QUALIFICATION_SOURCE_NAME: QUALIFICATION_SOURCE_SHA256,
    QUALIFICATION_EXECUTABLE_NAME: QUALIFICATION_EXECUTABLE_SHA256,
}
FROZEN_CXX_PATH = "/usr/bin/c++"
FROZEN_CXX_REALPATH = "/usr/lib/llvm-18/bin/clang"
ATTEMPT2_BUILD_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2")
ATTEMPT2_LOG_ROOT = ATTEMPT2_BUILD_ROOT / "logs"
ATTEMPT2_HARNESS_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2-harness")
ATTEMPT2_INTENT_PATH = Path("data/p3_v3/pilot/boost_math/build-preflight-attempt-2-intent.json")
ATTEMPT2_RESULT_PATH = Path("data/p3_v3/pilot/boost_math/build-preflight-attempt-2-result.json")
ATTEMPT2_AUTHORIZATION_PATH = Path("data/p3_v3/pilot/boost_math/user-auth-build-preflight-attempt-2.txt")
ATTEMPT2_AUTHORIZATION_BYTES = b"P3_BUILD_PREFLIGHT_ATTEMPT_2_AUTHORIZED=true\n"
ATTEMPT2_AUTHORIZATION_SHA256 = "fdb55d342c8e132a7377e4dcde1be16c3a2f736e76fe3edfc0cdc85bcfc79201"

ATTEMPT2_ENVIRONMENT_SCHEMA = "p3-pilot-build-preflight-attempt-2-environment-v1"
ATTEMPT2_PHASE_SCHEMA = "p3-pilot-build-preflight-attempt-2-phase-v1"
ATTEMPT2_INTENT_SCHEMA = "p3-pilot-build-preflight-attempt-2-intent-v1"
ATTEMPT2_RESULT_SCHEMA = "p3-pilot-build-preflight-attempt-2-result-v1"
ATTEMPT2_ENVIRONMENT_EXACT = {
 "schema_version": str, "execution_class": str, "denominator": str,
 "cmake_executable": str, "cmake_executable_path": str, "cmake_version": (str, type(None)),
 "cxx_compiler_executable": (str, type(None)), "cxx_compiler_path": (str, type(None)),
 "cxx_compiler_identity": (str, type(None)), "cxx_compiler_version": (str, type(None)),
 "cmake_generator": str, "os_name": str, "os_release": str, "python_version": str,
 "git_version": (str, type(None)), "build_parallelism": int, "nvcc_present": bool,
 "native_profiling_present": bool, "cuda_absence_blocking": bool,
 "fetchcontent_fully_disconnected": bool, "system_boost_fallback_accepted": bool,
 "disconnected_environment": dict, "qualification_evidence_sha256": str,
 "verification_scope": str, "executor_cloud_run_id": (str, type(None)),
 "executor_build_snapshot_id": (str, type(None)), "claims": str, "artifact_sha256": str,
}
ATTEMPT2_PHASE_EXACT = {
 "schema_version": str, "execution_class": str, "denominator": str, "phase_id": str,
 "phase_kind": str, "dependency_phase_ids": list, "argv": list, "timeout_seconds": int,
 "process_started": bool, "process_group_terminated": (bool, type(None)),
 "infrastructure_phase": (str, type(None)), "terminal_status": str,
 "failure_reason": (str, type(None)), "exit_code": (int, type(None)),
 "stdout_sha256": (str, type(None)), "stderr_sha256": (str, type(None)),
 "stdout_bytes": (int, type(None)), "stderr_bytes": (int, type(None)),
 "started_at": (str, type(None)), "ended_at": (str, type(None)),
 "wall_seconds": (float, type(None)), "cpu_seconds": (float, type(None)),
 "peak_rss_bytes": (int, type(None)), "source_restoration_evidence": (dict, type(None)),
 "claims": str, "artifact_sha256": str,
}
ATTEMPT2_INTENT_EXACT = {
 "schema_version": str, "execution_class": str, "denominator": str, "plan_class": str,
 "p12_item_id": str, "neutral_snapshot_id": str, "normalized_source_tree_sha256": str,
 "controlled_subject_id": str, "controlled_subject_source_id": str, "build_descriptor_sha256": str,
 "source_preparation_verdict_sha256": str, "source_manifest_sha256": str,
 "source_preparation_result_sha256": str, "source_preparation_reviewed_commit": str,
 "attempt1_implementation_verdict_sha256": str, "attempt2_implementation_verdict_sha256": str,
 "authorization_sha256": str, "harness_cmake_sha256": str, "harness_cxx_sha256": str,
 "source_root": str, "build_root": str, "harness_root": str, "log_root": str, "archive_path": str,
 "qualification_base_head": str, "qualification_evidence_sha256": str,
 "cmake_metadata_argv": list, "cmake_configure_argv": list, "baseline_build_argv": list,
 "baseline_smoke_argv": list, "cmake_version_timeout_seconds": int,
 "cmake_configure_timeout_seconds": int, "baseline_build_timeout_seconds": int,
 "baseline_smoke_timeout_seconds": int, "outer_timeout_seconds": int, "build_parallelism": int,
 "planned_count": int, "dependency_dag": list, "phase_order": list,
 "environment_snapshot": dict, "environment_snapshot_sha256": str, "producer_pid": int,
 "producer_starttime": str, "predecessor_sha256": list, "no_retry": bool, "claims": str,
 "formal_denominator_membership": bool, "rq4_supported": bool, "attempt_2_authorized": bool,
 "verification_scope": str, "executor_cloud_run_id": (str, type(None)),
 "executor_build_snapshot_id": (str, type(None)), "artifact_sha256": str,
}
ATTEMPT2_RESULT_EXACT = {
 "schema_version": str, "execution_class": str, "denominator": str, "p12_item_id": str,
 "neutral_snapshot_id": str, "normalized_source_tree_sha256": str, "controlled_subject_id": str,
 "controlled_subject_source_id": str, "build_descriptor_sha256": str,
 "source_preparation_verdict_sha256": str, "source_manifest_sha256": str,
 "source_preparation_result_sha256": str, "attempt1_implementation_verdict_sha256": str,
 "attempt2_implementation_verdict_sha256": str, "intent_sha256": str, "authorization_sha256": str,
 "qualification_base_head": str, "qualification_evidence_sha256": str,
 "environment_snapshot": dict, "environment_snapshot_sha256": str,
 "harness_cmake_sha256": str, "harness_cxx_sha256": str,
 "cmake_cache_sha256": (str, type(None)), "compile_commands_sha256": (str, type(None)),
 "compiler_depfile_sha256": (str, type(None)), "dependency_list_sha256": (str, type(None)),
 "smoke_executable_sha256": (str, type(None)), "source_root": str, "build_root": str,
 "harness_root": str, "log_root": str, "archive_path": str, "planned_count": int,
 "started_count": int, "terminal_count": int, "not_started_count": int, "phase_order": list,
 "phases": list, "source_restoration_disposition": (str, type(None)), "terminal_status": str,
 "failure_reason": (str, type(None)), "build_root_exists": bool, "build_root_is_symlink": bool,
 "no_retry": bool, "claims": str, "formal_denominator_membership": bool, "rq4_supported": bool,
 "attempt_2_authorized": bool, "verification_scope": str,
 "executor_cloud_run_id": (str, type(None)), "executor_build_snapshot_id": (str, type(None)),
 "predecessor_sha256": list, "artifact_sha256": str,
}
ATTEMPT2_IMPLEMENTATION_VERDICT_SCHEMA = "p3-pilot-attempt2-recovery-implementation-verdict-v1"
ATTEMPT2_IMPLEMENTATION_VERDICT_PATH = Path(
    "docs/review_20260824/boost_math_attempt_2_recovery_implementation_sol_high_review.md"
)
ATTEMPT2_QUALIFICATION_EVIDENCE_SCHEMA = "p3-pilot-attempt-2-qualification-evidence-v1"
ATTEMPT2_QUALIFICATION_EVIDENCE_EXACT = {
 "schema_version": str, "execution_class": str, "claims": str,
 "qualification_root": str, "qualification_base_head": str,
 "intent_sha256": str, "result_sha256": str, "manifest_sha256": str,
 "source_sha256": str, "executable_sha256": str,
 "compiler_version_stdout_sha256": str, "compiler_version_stderr_sha256": str,
 "compiler_version_stdout": str, "compiler_version_stderr": str,
 "requested_compiler": str, "resolved_compiler_path": str,
 "resolved_compiler_realpath": str, "current_cxx_realpath": str,
 "host_git_version": str, "host_snapshot_sha256": str,
 "terminal_status": str, "failure_reason": (str, type(None)),
 "verification_scope": str, "artifact_sha256": str,
}
ATTEMPT2_IMPLEMENTATION_VERDICT_EXACT = {
 "schema_version": str, "verdict": str, "reviewed_commit": str,
 "qualification_base_head": str, "v1_design_sha256": str, "v2_design_sha256": str,
 "v3_design_sha256": str, "approved_implementation_plan_sha256": str,
 "reviewed_blob_sha256": dict, "formal_denominator_membership": bool, "claims": str,
 "attempt_2_authorized": bool, "rq4_supported": bool, "artifact_sha256": str,
}
ATTEMPT2_IMPLEMENTATION_VERDICT_REVIEWED_BLOB_EXACT = {
 "rejected_plan_v1": str, "src/p3_v3/pilot_source.py": str,
 "src/p3_v3/pilot_build.py": str, "scripts/p3_v3/pilot.py": str,
 "tests/p3_v3/test_pilot_source.py": str, "tests/p3_v3/test_pilot_build.py": str,
 "tests/p3_v3/test_pilot.py": str,
}
ATTEMPT2_V1_DESIGN_PATH = Path("docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design.md")
ATTEMPT2_V2_DESIGN_PATH = Path("docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design-amendment-v2.md")
ATTEMPT2_V3_DESIGN_PATH = Path("docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design-amendment-v3.md")
ATTEMPT2_APPROVED_PLAN_PATH = Path("docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation-v2.md")
ATTEMPT2_REJECTED_PLAN_V1_PATH = Path("docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation.md")
ATTEMPT2_AUTHORITY_HASHES = {
    "v1_design_sha256": (ATTEMPT2_V1_DESIGN_PATH, "a441fd68321e28f769447f19315c4b3bd82943888600126fe91bc66f3aec923b"),
    "v2_design_sha256": (ATTEMPT2_V2_DESIGN_PATH, "a75cc3a3fecaafc26b59d32bb79fceac93f1a511f65a206b47ab497eacc2912f"),
    "v3_design_sha256": (ATTEMPT2_V3_DESIGN_PATH, "b99c72f89704f582692dffdad8478efca56b4f75d17b0b7541b84cb0f311f3e3"),
    "approved_implementation_plan_sha256": (ATTEMPT2_APPROVED_PLAN_PATH, "c004284bc7c5c101a6af999481af79ae34aa7fa1d9e61386326248b2b13bb98e"),
}
ATTEMPT2_REJECTED_PLAN_V1_SHA256 = "9d5192b78b103fb0213ed2947c15b3e207aec022241b6cac9520e07da73c3e8c"
ATTEMPT2_REVIEWED_FILES = {
    "rejected_plan_v1": ATTEMPT2_REJECTED_PLAN_V1_PATH,
    "src/p3_v3/pilot_source.py": Path("src/p3_v3/pilot_source.py"),
    "src/p3_v3/pilot_build.py": Path("src/p3_v3/pilot_build.py"),
    "scripts/p3_v3/pilot.py": Path("scripts/p3_v3/pilot.py"),
    "tests/p3_v3/test_pilot_source.py": Path("tests/p3_v3/test_pilot_source.py"),
    "tests/p3_v3/test_pilot_build.py": Path("tests/p3_v3/test_pilot_build.py"),
    "tests/p3_v3/test_pilot.py": Path("tests/p3_v3/test_pilot.py"),
}
P12_ITEM_ID = "C-BOOSTMATH-001"
NEUTRAL_SNAPSHOT_ID = (
    "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886"
)
FROZEN_NORMALIZED_SOURCE_TREE_SHA256 = (
    "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8"
)
CONTROLLED_SUBJECT_ID = (
    "89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914"
)
CONTROLLED_SUBJECT_SOURCE_ID = (
    "e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7"
)
BUILD_DESCRIPTOR_SHA256 = (
    "68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d"
)
SOURCE_PREPARATION_RESULT_VERDICT_SHA256 = (
    "43cedfd21621496f61feec1418b2ec4d9e02b51096c477b0d221067d1e1ed7f2"
)
SOURCE_MANIFEST_FILE_SHA256 = (
    "d774143f6a0dc6cf24a9ddda8b4e9760b3d547e03cbd21e16d84220f826073c5"
)
SOURCE_PREPARATION_RESULT_FILE_SHA256 = (
    "6a525ff074f5ab67f4a58af0a4f7f2264f3888757513a8fc80fb6760c8b577b9"
)
SOURCE_PREPARATION_REVIEWED_COMMIT = "44acee8882b004f50005cd39ca732bc6f09604fa"

FROZEN_SOURCE_ROOT = Path("/tmp/p3-boost-math-pilot-production-source")
FROZEN_BUILD_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight")
FROZEN_HARNESS_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight-harness")
INTENT_PATH = Path("data/p3_v3/pilot/boost_math/build-preflight-intent.json")
RESULT_PATH = Path("data/p3_v3/pilot/boost_math/build-preflight-result.json")
AUTHORIZATION_PATH = Path(
    "data/p3_v3/pilot/boost_math/user-auth-build-preflight.txt"
)
SOURCE_MANIFEST_PATH = Path("data/p3_v3/pilot/boost_math/source-manifest.json")
SOURCE_PREPARATION_RESULT_PATH = Path(
    "data/p3_v3/pilot/boost_math/source-preparation-result.json"
)
SOURCE_PREPARATION_RESULT_VERDICT_PATH = Path(
    "docs/review_20260817/"
    "boost_math_pilot_source_preparation_result_sol_high_review.md"
)
PLAN_PATH = Path(
    "docs/superpowers/plans/"
    "2026-08-17-p3-boost-math-pilot-build-preflight-only.md"
)
PLAN_VERDICT_PATH = Path(
    "docs/review_20260817/"
    "boost_math_pilot_build_preflight_plan_sol_high_review.md"
)
IMPLEMENTATION_VERDICT_PATH = Path(
    "docs/review_20260817/"
    "boost_math_pilot_build_preflight_implementation_sol_high_review.md"
)

AUTHORIZATION_BYTES = b"AUTHORIZE_BOOSTMATH_PILOT_BUILD_PREFLIGHT\n"
AUTHORIZATION_SHA256 = (
    "2265145a6b73a16e1ae06b3c5b12baa2a842ad7d700e60ed0de67393746cfb15"
)

HARNESS_CMAKE_BYTES = (
    b"cmake_minimum_required(VERSION 3.5)\n"
    b"project(boost_math_pilot_build_preflight_harness LANGUAGES CXX)\n"
    b"\n"
    b"set(BOOST_MATH_PILOT_SOURCE_INCLUDE\n"
    b'    "/tmp/p3-boost-math-pilot-production-source/include"\n'
    b"    CACHE PATH\n"
    b'    "Frozen Boost.Math public include root")\n'
    b"\n"
    b"if(NOT BOOST_MATH_PILOT_SOURCE_INCLUDE STREQUAL\n"
    b'    "/tmp/p3-boost-math-pilot-production-source/include")\n'
    b"  message(FATAL_ERROR\n"
    b'    "BOOST_MATH_PILOT_SOURCE_INCLUDE is not the frozen include path")\n'
    b"endif()\n"
    b"\n"
    b"if(DEFINED BOOST_ROOT OR DEFINED BOOST_INCLUDEDIR OR DEFINED Boost_INCLUDE_DIR\n"
    b"    OR DEFINED Boost_DIR)\n"
    b'  message(FATAL_ERROR "unbound Boost search variables are forbidden")\n'
    b"endif()\n"
    b"\n"
    b"add_executable(boost_math_pilot_smoke smoke.cpp)\n"
    b"target_include_directories(\n"
    b"    boost_math_pilot_smoke\n"
    b"    PRIVATE\n"
    b'    "${BOOST_MATH_PILOT_SOURCE_INCLUDE}")\n'
    b"target_compile_definitions(\n"
    b"    boost_math_pilot_smoke\n"
    b"    PRIVATE\n"
    b"    BOOST_MATH_STANDALONE=1)\n"
    b"target_compile_features(boost_math_pilot_smoke PRIVATE cxx_std_14)\n"
    b"set_target_properties(\n"
    b"    boost_math_pilot_smoke\n"
    b"    PROPERTIES\n"
    b'    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")\n'
)
HARNESS_CXX_BYTES = (
    b"#include <boost/math/constants/constants.hpp>\n"
    b"\n"
    b"int main()\n"
    b"{\n"
    b"    const double pi = boost::math::constants::pi<double>();\n"
    b"    if (pi > 3.14 && pi < 3.15)\n"
    b"    {\n"
    b"        return 0;\n"
    b"    }\n"
    b"    return 1;\n"
    b"}\n"
)
HARNESS_CMAKE_SHA256 = hashlib.sha256(HARNESS_CMAKE_BYTES).hexdigest()
HARNESS_CXX_SHA256 = hashlib.sha256(HARNESS_CXX_BYTES).hexdigest()

CMAKE_CONFIGURE_TIMEOUT_SECONDS = 900
BASELINE_BUILD_TIMEOUT_SECONDS = 3600
BASELINE_SMOKE_TIMEOUT_SECONDS = 1800
OUTER_TIMEOUT_SECONDS = 7200
SHELL_WATCHDOG = "2h5m"
BUILD_PARALLELISM = 4
PLANNED_COUNT = 3
COMPILER_DEPFILE_RELATIVE = (
    "CMakeFiles/boost_math_pilot_smoke.dir/smoke.cpp.o.d"
)
FROZEN_CONSTANTS_HEADER = (
    "/tmp/p3-boost-math-pilot-production-source/include/"
    "boost/math/constants/constants.hpp"
)
FROZEN_SMOKE_CXX = "/tmp/p3-boost-math-pilot-build-preflight-harness/smoke.cpp"
FORBIDDEN_TOOLCHAIN_ENV = (
    "CXX",
    "CC",
    "CMAKE_CXX_COMPILER",
    "CMAKE_C_COMPILER",
)

CMAKE_CONFIGURE_ARGV = [
    "cmake",
    "-S",
    "/tmp/p3-boost-math-pilot-build-preflight-harness",
    "-B",
    "/tmp/p3-boost-math-pilot-build-preflight",
    "-G",
    "Unix Makefiles",
    "-DCMAKE_BUILD_TYPE=Release",
    "-DCMAKE_CXX_STANDARD=14",
    "-DCMAKE_CXX_STANDARD_REQUIRED=ON",
    "-DBOOST_MATH_STANDALONE=1",
    "-DBOOST_MATH_PILOT_SOURCE_INCLUDE=/tmp/p3-boost-math-pilot-production-source/include",
    "-DCMAKE_DISABLE_SOURCE_CHANGES=ON",
    "-DCMAKE_DISABLE_IN_SOURCE_BUILD=ON",
    "-DFETCHCONTENT_FULLY_DISCONNECTED=ON",
    "-DFETCHCONTENT_UPDATES_DISCONNECTED=ON",
    "-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF",
    "-DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF",
    "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
]
BASELINE_BUILD_ARGV = [
    "cmake",
    "--build",
    "/tmp/p3-boost-math-pilot-build-preflight",
    "--parallel",
    "4",
]
BASELINE_SMOKE_ARGV = [
    "/tmp/p3-boost-math-pilot-build-preflight/boost_math_pilot_smoke"
]
DEPENDENCY_DAG = [
    ["CMAKE_CONFIGURE", "BASELINE_BUILD"],
    ["BASELINE_BUILD", "BASELINE_SMOKE"],
]
JOB_SPECS = (
    {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": CMAKE_CONFIGURE_ARGV,
        "timeout_seconds": CMAKE_CONFIGURE_TIMEOUT_SECONDS,
    },
    {
        "job_id": "BASELINE_BUILD",
        "job_kind": "BASELINE_BUILD",
        "dependency_job_ids": ["CMAKE_CONFIGURE"],
        "argv": BASELINE_BUILD_ARGV,
        "timeout_seconds": BASELINE_BUILD_TIMEOUT_SECONDS,
    },
    {
        "job_id": "BASELINE_SMOKE",
        "job_kind": "BASELINE_SMOKE",
        "dependency_job_ids": ["BASELINE_BUILD"],
        "argv": BASELINE_SMOKE_ARGV,
        "timeout_seconds": BASELINE_SMOKE_TIMEOUT_SECONDS,
    },
)

DISCONNECTED_ENVIRONMENT = {
    "FETCHCONTENT_FULLY_DISCONNECTED": "ON",
    "FETCHCONTENT_UPDATES_DISCONNECTED": "ON",
}
DEDICATED_BOOST_ENV = (
    "BOOST_ROOT",
    "BOOST_INCLUDEDIR",
    "Boost_DIR",
)
AGGREGATE_PATH_ENV = (
    "CMAKE_PREFIX_PATH",
    "CMAKE_INCLUDE_PATH",
    "CPATH",
    "CPLUS_INCLUDE_PATH",
)
FORBIDDEN_BOOST_ENV = DEDICATED_BOOST_ENV + AGGREGATE_PATH_ENV
NETWORK_MARKERS = (
    b"Downloading ",
    b"Cloning into",
    b"Fetching ",
    b"file(DOWNLOAD",
    b"-- Fetching",
    b"Resolving deltas",
    b"github.com",
    b"gitlab.com",
    b"bitbucket.org",
    b"FetchContent_Declare",
    b"ExternalProject_Add",
)
SYSTEM_BOOST_MARKERS = (
    "/usr/include/boost",
    "/usr/local/include/boost",
)
FROZEN_INCLUDE_PREFIX = "/tmp/p3-boost-math-pilot-production-source/include"
FROZEN_CMAKE_GENERATOR = "Unix Makefiles"
GIT_OID_RE = re.compile(r"^[0-9a-f]{40}$")
REVIEWED_IMPLEMENTATION_FILES = (
    (
        "reviewed_pilot_build_path",
        "reviewed_pilot_build_sha256",
        "src/p3_v3/pilot_build.py",
    ),
    (
        "reviewed_pilot_cli_path",
        "reviewed_pilot_cli_sha256",
        "scripts/p3_v3/pilot.py",
    ),
    (
        "reviewed_test_pilot_build_path",
        "reviewed_test_pilot_build_sha256",
        "tests/p3_v3/test_pilot_build.py",
    ),
    (
        "reviewed_test_pilot_path",
        "reviewed_test_pilot_sha256",
        "tests/p3_v3/test_pilot.py",
    ),
)
FAIL_REASONS = frozenset({"NONZERO_EXIT", "CRASH"})
INFRA_REASONS_PRE_PROCESS = frozenset(
    {
        "MISSING_DEPENDENCY",
        "SYSTEM_BOOST_FALLBACK",
        "UNSUPPORTED_TOOLCHAIN",
        "ORPHANED_INTENT_NO_PROCESS",
        "HARNESS_PUBLICATION_FAILURE",
        "RESULT_PUBLICATION_FAILURE",
        "OUTER_DEADLINE_EXHAUSTED",
    }
)
INFRA_REASONS_POST_PROCESS = frozenset(
    {
        "NETWORK_OR_DOWNLOAD_ATTEMPT",
        "SYSTEM_BOOST_FALLBACK",
        "MISSING_DEPENDENCY",
        "UNSUPPORTED_TOOLCHAIN",
        "SOURCE_TREE_DRIFT",
        "LOG_PUBLICATION_FAILURE",
        "PROCESS_IDENTITY_PUBLICATION_FAILURE",
        "PROCESS_CONTROL_FAILURE",
        "PROCESS_GROUP_LEAK",
    }
)
POST_SPAWN_CLEANUP_REASONS = frozenset(
    {
        "PROCESS_IDENTITY_PUBLICATION_FAILURE",
        "LOG_PUBLICATION_FAILURE",
        "PROCESS_CONTROL_FAILURE",
        "PROCESS_GROUP_LEAK",
    }
)
RECONCILIATION_STATES = frozenset(
    {
        "FRESH",
        "INTENT_PRODUCER_LIVE",
        "INTENT_CHILD_LIVE",
        "INTENT_CHILD_STATE_UNRESOLVED",
        "INTENT_ONLY_ORPHAN",
        "RESULT_TERMINAL",
        "RESULT_WITHOUT_INTENT",
        "INVALID_DURABLE",
    }
)

PLAN_VERDICT_EXACT = {
    "reviewed_plan_path": str,
    "reviewed_plan_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}
IMPLEMENTATION_VERDICT_EXACT = {
    "reviewed_plan_path": str,
    "reviewed_plan_sha256": str,
    "reviewed_plan_verdict_sha256": str,
    "reviewed_commit": str,
    "reviewed_pilot_build_path": str,
    "reviewed_pilot_build_sha256": str,
    "reviewed_pilot_cli_path": str,
    "reviewed_pilot_cli_sha256": str,
    "reviewed_test_pilot_build_path": str,
    "reviewed_test_pilot_build_sha256": str,
    "reviewed_test_pilot_path": str,
    "reviewed_test_pilot_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}
SOURCE_PREPARATION_RESULT_VERDICT_EXACT = {
    "authorized_state": str,
    "claims": str,
    "materialized_tree_sha256": str,
    "reviewed_commit": str,
    "reviewed_source_manifest_path": str,
    "reviewed_source_manifest_sha256": str,
    "reviewed_source_preparation_result_path": str,
    "reviewed_source_preparation_result_sha256": str,
    "verdict": str,
}
BUILD_PREFLIGHT_ENVIRONMENT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "cmake_executable": str,
    "cmake_executable_path": str,
    "cmake_version": str,
    "cxx_compiler_executable": (str, type(None)),
    "cxx_compiler_path": (str, type(None)),
    "cxx_compiler_identity": (str, type(None)),
    "cxx_compiler_version": (str, type(None)),
    "cmake_generator": str,
    "os_name": str,
    "os_release": str,
    "python_version": str,
    "git_version": (str, type(None)),
    "build_parallelism": int,
    "nvcc_present": bool,
    "native_profiling_present": bool,
    "cuda_absence_blocking": bool,
    "fetchcontent_fully_disconnected": bool,
    "system_boost_fallback_accepted": bool,
    "disconnected_environment": dict,
    "claims": str,
    "artifact_sha256": str,
}
BUILD_PREFLIGHT_INTENT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "plan_class": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "build_descriptor_sha256": str,
    "source_preparation_verdict_sha256": str,
    "source_manifest_sha256": str,
    "source_preparation_result_sha256": str,
    "source_preparation_reviewed_commit": str,
    "implementation_verdict_sha256": str,
    "authorization_sha256": str,
    "harness_cmake_sha256": str,
    "harness_cxx_sha256": str,
    "source_root": str,
    "build_root": str,
    "harness_root": str,
    "cmake_configure_argv": list,
    "baseline_build_argv": list,
    "baseline_smoke_argv": list,
    "cmake_configure_timeout_seconds": int,
    "baseline_build_timeout_seconds": int,
    "baseline_smoke_timeout_seconds": int,
    "outer_timeout_seconds": int,
    "build_parallelism": int,
    "planned_count": int,
    "dependency_dag": list,
    "environment_snapshot": dict,
    "environment_snapshot_sha256": str,
    "producer_pid": int,
    "producer_starttime": str,
    "predecessor_sha256": list,
    "no_retry": bool,
    "claims": str,
    "formal_denominator_membership": bool,
    "rq4_supported": bool,
    "artifact_sha256": str,
}
BUILD_PREFLIGHT_JOB_RESULT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "job_id": str,
    "job_kind": str,
    "dependency_job_ids": list,
    "argv": list,
    "timeout_seconds": int,
    "process_started": bool,
    "process_group_terminated": (bool, type(None)),
    "infrastructure_phase": (str, type(None)),
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "exit_code": (int, type(None)),
    "stdout_sha256": (str, type(None)),
    "stderr_sha256": (str, type(None)),
    "stdout_bytes": (int, type(None)),
    "stderr_bytes": (int, type(None)),
    "started_at": (str, type(None)),
    "ended_at": (str, type(None)),
    "wall_seconds": (float, type(None)),
    "cpu_seconds": (float, type(None)),
    "peak_rss_bytes": (int, type(None)),
    "claims": str,
    "artifact_sha256": str,
}
BUILD_PREFLIGHT_RESULT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "build_descriptor_sha256": str,
    "source_preparation_verdict_sha256": str,
    "source_manifest_sha256": str,
    "source_preparation_result_sha256": str,
    "implementation_verdict_sha256": str,
    "intent_sha256": str,
    "authorization_sha256": str,
    "environment_snapshot": dict,
    "environment_snapshot_sha256": str,
    "harness_cmake_sha256": str,
    "harness_cxx_sha256": str,
    "cmake_cache_sha256": (str, type(None)),
    "compile_commands_sha256": (str, type(None)),
    "compiler_depfile_sha256": (str, type(None)),
    "dependency_list_sha256": (str, type(None)),
    "smoke_executable_sha256": (str, type(None)),
    "source_root": str,
    "build_root": str,
    "harness_root": str,
    "planned_count": int,
    "started_count": int,
    "terminal_count": int,
    "not_started_count": int,
    "jobs": list,
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "build_root_exists": bool,
    "build_root_is_symlink": bool,
    "no_retry": bool,
    "claims": str,
    "formal_denominator_membership": bool,
    "rq4_supported": bool,
    "predecessor_sha256": list,
    "artifact_sha256": str,
}

STARTED_TERMINAL = {"PASS", "FAIL", "TIMEOUT", "FAIL_INFRASTRUCTURE"}
ALL_TERMINAL = STARTED_TERMINAL | {"NOT_STARTED"}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _self_hash(payload: dict[str, Any]) -> dict[str, Any]:
    body = {key: payload[key] for key in payload if key != "artifact_sha256"}
    return {**payload, "artifact_sha256": canonical_sha256(body)}


def read_authority_snapshot(path: Path, context: str) -> tuple[bytes, str]:
    try:
        raw, _mode = read_regular_file_snapshot(path, context)
    except EvidenceError as exc:
        if exc.code == "E_AUTHORITY_LOCK_PATH":
            raise EvidenceError(
                "E_PILOT_BUILD_IDENTITY",
                f"{context} authority snapshot is absent or unsafe",
            ) from exc
        raise
    digest = _sha256_bytes(raw)
    validate_sha256(digest, f"{context}.sha256")
    return raw, digest


def parse_canonical_json_object(raw: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError("E_PILOT_BUILD_IDENTITY", f"{context} is not JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise EvidenceError(
            "E_PILOT_BUILD_IDENTITY",
            f"{context} is not one canonical JSON object",
        )
    return value


def read_v5_qualification_evidence(
    qualification_root: Path = QUALIFICATION_ROOT,
) -> dict[str, Any]:
    """Adapt frozen V5 files without rerunning any qualification or metadata tool."""
    root = Path(qualification_root)
    try:
        root_info = root.lstat()
    except OSError as exc:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "qualification root is unavailable") from exc
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "qualification root is unsafe")
    required = {
        *QUALIFICATION_FIXED_HASHES,
        QUALIFICATION_CXX_STDOUT_NAME,
        QUALIFICATION_CXX_STDERR_NAME,
    }
    try:
        observed_names = {entry.name for entry in root.iterdir()}
    except OSError as exc:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "qualification inventory is unavailable") from exc
    if not required.issubset(observed_names):
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "qualification core evidence is absent")
    records: dict[str, bytes] = {}
    digests: dict[str, str] = {}
    for name in (*QUALIFICATION_FIXED_HASHES,
                 QUALIFICATION_CXX_STDOUT_NAME, QUALIFICATION_CXX_STDERR_NAME):
        raw, _mode = read_regular_file_snapshot(root / name, f"qualification-{name}")
        records[name] = raw
        digests[name] = _sha256_bytes(raw)
        expected = QUALIFICATION_FIXED_HASHES.get(name)
        if expected is not None and digests[name] != expected:
            raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", f"{name} hash differs")
    intent = qualification_contract.validate_intent(
        parse_canonical_json_object(records[QUALIFICATION_INTENT_NAME], "qualification-intent")
    )
    result = qualification_contract.validate_result(
        parse_canonical_json_object(records[QUALIFICATION_RESULT_NAME], "qualification-result")
    )
    manifest = qualification_contract.validate_manifest(
        parse_canonical_json_object(records[QUALIFICATION_MANIFEST_NAME], "qualification-manifest")
    )
    qualification_contract.validate_attempt_pair(intent, digests[QUALIFICATION_INTENT_NAME], result)
    manifest_names = {entry["path"] for entry in manifest["files"]}
    if (observed_names != manifest_names | {QUALIFICATION_MANIFEST_NAME}
            or QUALIFICATION_MANIFEST_NAME in manifest_names):
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "qualification inventory differs")
    manifest_inventory = {
        entry["path"]: {"sha256": entry["sha256"], "bytes": entry["bytes"]}
        for entry in manifest["files"]
    }
    for name in manifest_names:
        if name not in records:
            raw, _mode = read_regular_file_snapshot(root / name, f"qualification-{name}")
            records[name] = raw
            digests[name] = _sha256_bytes(raw)
        if (digests[name] != manifest_inventory[name]["sha256"]
                or len(records[name]) != manifest_inventory[name]["bytes"]):
            raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", f"{name} manifest evidence differs")
    if result.get("terminal_status") != "PASS" or result.get("failure_reason") is not None:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "qualification is not PASS")
    if os.path.realpath(FROZEN_CXX_PATH) != FROZEN_CXX_REALPATH:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "current compiler differs")
    stdout = records[QUALIFICATION_CXX_STDOUT_NAME]
    stderr = records[QUALIFICATION_CXX_STDERR_NAME]
    if intent["repository_commit"] != QUALIFICATION_BASE_HEAD:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "qualification base differs")
    if intent["requested_compiler"] != "c++":
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "requested compiler differs")
    if intent["resolved_compiler_path"] != FROZEN_CXX_PATH:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "compiler path differs")
    if intent["resolved_compiler_realpath"] != FROZEN_CXX_REALPATH:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "compiler realpath differs")
    host = intent["host_snapshot"]
    if host != result["host_snapshot"] or host["repository_commit"] != QUALIFICATION_BASE_HEAD:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "host snapshot differs")
    host_git = host["git_version"]
    host_snapshot = intent["host_snapshot_sha256"]
    version = result["compiler_version"]
    if version is None:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "compiler version evidence is absent")
    if (version["stdout_sha256"] != _sha256_bytes(stdout)
            or version["stderr_sha256"] != _sha256_bytes(stderr)
            or version["stdout_bytes"] != len(stdout)
            or version["stderr_bytes"] != len(stderr)):
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "compiler version output differs")
    if (manifest["intent_sha256"] != digests[QUALIFICATION_INTENT_NAME]
            or manifest["result_sha256"] != digests[QUALIFICATION_RESULT_NAME]
            or result["source_sha256"] != digests[QUALIFICATION_SOURCE_NAME]
            or result["executable_sha256"] != digests[QUALIFICATION_EXECUTABLE_NAME]
            or result["executable_bytes"] != len(records[QUALIFICATION_EXECUTABLE_NAME])):
        raise EvidenceError("E_PILOT_ATTEMPT2_QUALIFICATION", "manifest cross-link differs")
    payload = {
        "schema_version": ATTEMPT2_QUALIFICATION_EVIDENCE_SCHEMA,
        "execution_class": "PILOT_ONLY", "claims": "blocked",
        "qualification_root": root.as_posix(),
        "qualification_base_head": QUALIFICATION_BASE_HEAD,
        "intent_sha256": digests[QUALIFICATION_INTENT_NAME],
        "result_sha256": digests[QUALIFICATION_RESULT_NAME],
        "manifest_sha256": digests[QUALIFICATION_MANIFEST_NAME],
        "source_sha256": digests[QUALIFICATION_SOURCE_NAME],
        "executable_sha256": digests[QUALIFICATION_EXECUTABLE_NAME],
        "compiler_version_stdout_sha256": _sha256_bytes(stdout),
        "compiler_version_stderr_sha256": _sha256_bytes(stderr),
        "compiler_version_stdout": stdout.decode("utf-8"),
        "compiler_version_stderr": stderr.decode("utf-8"),
        "requested_compiler": "c++",
        "resolved_compiler_path": FROZEN_CXX_PATH,
        "resolved_compiler_realpath": FROZEN_CXX_REALPATH,
        "current_cxx_realpath": os.path.realpath(FROZEN_CXX_PATH),
        "host_git_version": host_git, "host_snapshot_sha256": host_snapshot,
        "terminal_status": "PASS", "failure_reason": None,
        "verification_scope": "ARTIFACT_HASH_AND_HOST_SNAPSHOT",
    }
    payload["artifact_sha256"] = canonical_sha256(payload)
    return validate_exact_object(payload, ATTEMPT2_QUALIFICATION_EVIDENCE_EXACT, "attempt2-qualification-evidence")


def validate_attempt2_implementation_verdict(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value, ATTEMPT2_IMPLEMENTATION_VERDICT_EXACT, "attempt2-implementation-verdict"
    )
    if validated["schema_version"] != ATTEMPT2_IMPLEMENTATION_VERDICT_SCHEMA:
        raise EvidenceError("E_PILOT_ATTEMPT2_IMPL_VERDICT", "schema differs")
    if validated["verdict"] != "PASS":
        raise EvidenceError("E_PILOT_ATTEMPT2_IMPL_VERDICT", "verdict is not PASS")
    if GIT_OID_RE.fullmatch(validated["reviewed_commit"]) is None:
        raise EvidenceError("E_PILOT_ATTEMPT2_IMPL_VERDICT", "reviewed commit is invalid")
    if validated["qualification_base_head"] != QUALIFICATION_BASE_HEAD:
        raise EvidenceError("E_PILOT_ATTEMPT2_IMPL_VERDICT", "qualification base differs")
    if (validated["formal_denominator_membership"] is not False
            or validated["claims"] != "blocked"
            or validated["attempt_2_authorized"] is not False
            or validated["rq4_supported"] is not False):
        raise EvidenceError("E_PILOT_ATTEMPT2_IMPL_VERDICT", "claim ceiling differs")
    blobs = validate_exact_object(
        validated["reviewed_blob_sha256"],
        ATTEMPT2_IMPLEMENTATION_VERDICT_REVIEWED_BLOB_EXACT,
        "attempt2-implementation-verdict.reviewed_blob_sha256",
    )
    for key, value_hash in validated.items():
        if key.endswith("_sha256") and key != "reviewed_blob_sha256":
            validate_sha256(value_hash, f"attempt2-implementation-verdict.{key}")
    for key, value_hash in blobs.items():
        validate_sha256(value_hash, f"attempt2-implementation-verdict.reviewed_blob_sha256.{key}")
    body = {key: item for key, item in validated.items() if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_ATTEMPT2_IMPL_VERDICT", "self hash differs")
    validated["reviewed_blob_sha256"] = blobs
    return validated


def read_attempt2_implementation_verdict(
    verdict_path: Path = ATTEMPT2_IMPLEMENTATION_VERDICT_PATH,
) -> tuple[dict[str, Any], str]:
    raw, verdict_sha256 = read_authority_snapshot(verdict_path, "attempt2-implementation-verdict")
    verdict = validate_attempt2_implementation_verdict(
        parse_canonical_json_object(raw, "attempt2-implementation-verdict")
    )
    for key, (path, frozen_hash) in ATTEMPT2_AUTHORITY_HASHES.items():
        _raw, observed = read_authority_snapshot(path, key)
        if observed != frozen_hash or verdict[key] != frozen_hash:
            raise EvidenceError("E_PILOT_ATTEMPT2_IMPL_VERDICT", f"{key} differs")
    for key, path in ATTEMPT2_REVIEWED_FILES.items():
        _raw, observed = read_authority_snapshot(path, f"reviewed-blob-{key}")
        expected = ATTEMPT2_REJECTED_PLAN_V1_SHA256 if key == "rejected_plan_v1" else observed
        if observed != expected or verdict["reviewed_blob_sha256"][key] != expected:
            raise EvidenceError("E_PILOT_ATTEMPT2_IMPL_VERDICT", f"reviewed blob {key} differs")
    return verdict, verdict_sha256


def require_safe_directory(path: Path, expected: Path, context: str) -> Path:
    if path != expected:
        raise EvidenceError(
            "E_PILOT_BUILD_PATH",
            f"{context} must equal the frozen path",
        )
    if path.as_posix() != expected.as_posix():
        raise EvidenceError("E_PILOT_BUILD_PATH", f"{context} is not canonical")
    if not str(path).startswith("/tmp/"):
        raise EvidenceError("E_PILOT_BUILD_PATH", f"{context} escaped /tmp")
    try:
        info = path.lstat()
    except OSError as exc:
        raise EvidenceError(
            "E_PILOT_BUILD_PATH",
            f"{context} is unavailable",
        ) from exc
    if stat.S_ISLNK(info.st_mode):
        raise EvidenceError("E_PILOT_BUILD_SYMLINK", f"{context} is a symlink")
    if not stat.S_ISDIR(info.st_mode):
        raise EvidenceError("E_PILOT_BUILD_PATH", f"{context} is not a directory")
    return path


def require_absent_path(path: Path, context: str) -> None:
    if os.path.lexists(path):
        raise EvidenceError(
            "E_PILOT_BUILD_PREEXISTING",
            f"{context} already exists",
        )


def require_frozen_source_tree(source_root: Path) -> str:
    require_safe_directory(source_root, FROZEN_SOURCE_ROOT, "source-root")
    snapshot = capture_materialized_tree(source_root)
    observed = validate_materialized_tree_with_phase1(snapshot)
    if observed != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", observed)
    if len(snapshot.entries) != 4396:
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "file count differs")
    total = sum(len(entry.content) for entry in snapshot.entries)
    if total != 95635487:
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "total bytes differ")
    return observed


def reject_system_boost_environment(env: dict[str, str]) -> None:
    for key in DEDICATED_BOOST_ENV:
        if env.get(key):
            raise EvidenceError(
                "E_PILOT_SYSTEM_BOOST",
                "SYSTEM_BOOST_FALLBACK",
            )
    for key in AGGREGATE_PATH_ENV:
        value = env.get(key)
        if not value:
            continue
        lowered = value.lower()
        if "boost" in lowered or any(
            marker in value for marker in SYSTEM_BOOST_MARKERS
        ):
            raise EvidenceError(
                "E_PILOT_SYSTEM_BOOST",
                "SYSTEM_BOOST_FALLBACK",
            )


def detect_network_or_boost(stdout: bytes, stderr: bytes, argv: list[str]) -> str | None:
    joined = b"\0".join(item.encode("utf-8") for item in argv)
    haystack = stdout + b"\n" + stderr + b"\n" + joined
    for marker in SYSTEM_BOOST_MARKERS:
        if marker.encode("utf-8") in haystack:
            return "SYSTEM_BOOST_FALLBACK"
    for marker in NETWORK_MARKERS:
        if marker in haystack:
            return "NETWORK_OR_DOWNLOAD_ATTEMPT"
    return None


def validate_plan_verdict(value: object, plan_sha256: str) -> dict[str, Any]:
    validated = validate_exact_object(
        value, PLAN_VERDICT_EXACT, "build-preflight-plan-verdict"
    )
    validate_sha256(validated["reviewed_plan_sha256"], "plan-verdict.reviewed_plan_sha256")
    if validated["reviewed_plan_path"] != PLAN_PATH.as_posix():
        raise EvidenceError("E_PILOT_BUILD_PLAN_VERDICT", "reviewed plan path differs")
    if validated["reviewed_plan_sha256"] != plan_sha256:
        raise EvidenceError("E_PILOT_BUILD_PLAN_VERDICT", "reviewed plan hash differs")
    if validated["verdict"] != "PASS":
        raise EvidenceError("E_PILOT_BUILD_PLAN_VERDICT", "verdict is not PASS")
    if validated["authorized_state"] != "PILOT_BUILD_PREFLIGHT_PLAN_FROZEN":
        raise EvidenceError("E_PILOT_BUILD_PLAN_VERDICT", "authorized_state differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_PLAN_VERDICT", "claims are not blocked")
    return validated


def validate_source_preparation_result_verdict(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value,
        SOURCE_PREPARATION_RESULT_VERDICT_EXACT,
        "source-preparation-result-verdict",
    )
    if validated["verdict"] != "PASS":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "source-preparation verdict is not PASS",
        )
    if validated["authorized_state"] != "PILOT_SOURCE_PREPARATION_PASS":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "authorized_state differs",
        )
    if validated["claims"] != "blocked":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "claims are not blocked",
        )
    if validated["reviewed_source_manifest_sha256"] != SOURCE_MANIFEST_FILE_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "source manifest hash differs",
        )
    if (
        validated["reviewed_source_preparation_result_sha256"]
        != SOURCE_PREPARATION_RESULT_FILE_SHA256
    ):
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "source-preparation result hash differs",
        )
    if validated["materialized_tree_sha256"] != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "tree hash differs",
        )
    if validated["reviewed_commit"] != SOURCE_PREPARATION_REVIEWED_COMMIT:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "reviewed commit differs",
        )
    return validated


def producer_identity() -> tuple[int, str]:
    pid = os.getpid()
    stat_text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    rparen = stat_text.rfind(")")
    fields = stat_text[rparen + 2 :].split()
    return pid, fields[19]


def attempt_is_live(pid: int, starttime: str) -> bool:
    path = Path(f"/proc/{pid}/stat")
    if not path.is_file():
        return False
    stat_text = path.read_text(encoding="utf-8")
    rparen = stat_text.rfind(")")
    fields = stat_text[rparen + 2 :].split()
    return fields[19] == starttime


def read_proc_starttime(pid: int) -> str:
    stat_text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    rparen = stat_text.rfind(")")
    fields = stat_text[rparen + 2 :].split()
    return fields[19]


def process_group_has_members(pgid: int) -> bool:
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat_text = (entry / "stat").read_text(encoding="utf-8")
        except OSError:
            continue
        rparen = stat_text.rfind(")")
        fields = stat_text[rparen + 2 :].split()
        if len(fields) > 2 and fields[2] == str(pgid):
            return True
    return False


def classify_reconciliation(
    *,
    intent_present: bool,
    result_present: bool,
    intent_valid: bool,
    result_valid: bool,
    producer_live: bool,
    child_live: bool,
    pair_valid: bool,
    start_marker_present: bool = False,
    identity_resolved: bool = True,
) -> str:
    if not intent_present and not result_present:
        return "FRESH"
    if not intent_present and result_present:
        return "RESULT_WITHOUT_INTENT"
    if intent_present and result_present:
        if intent_valid and result_valid and pair_valid:
            return "RESULT_TERMINAL"
        return "INVALID_DURABLE"
    if intent_present and not result_present and intent_valid:
        if producer_live:
            return "INTENT_PRODUCER_LIVE"
        if child_live:
            return "INTENT_CHILD_LIVE"
        if start_marker_present or not identity_resolved:
            return "INTENT_CHILD_STATE_UNRESOLVED"
        return "INTENT_ONLY_ORPHAN"
    return "INVALID_DURABLE"


def probe_identity(executable: str | None) -> str | None:
    if executable is None:
        return None
    try:
        completed = subprocess.run(
            [executable, "--version"],
            check=False,
            capture_output=True,
            timeout=5,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    blob = (completed.stdout or b"") + (completed.stderr or b"")
    text = blob.decode("utf-8", "replace").strip()
    if not text:
        return None
    return text.splitlines()[0]


def parse_dependency_paths(dep_text: str) -> list[str]:
    stripped = dep_text.replace("\\\n", " ")
    if ":" in stripped:
        stripped = stripped.split(":", 1)[1]
    paths = [item.strip() for item in stripped.split() if item.strip()]
    return sorted(dict.fromkeys(paths))


def reject_nonfrozen_boost_headers(paths: list[str]) -> None:
    for path in paths:
        posix = path.replace("\\", "/")
        lowered = posix.lower()
        if "/boost/" not in lowered and not lowered.endswith("/boost"):
            continue
        if not posix.startswith(FROZEN_INCLUDE_PREFIX + "/"):
            raise EvidenceError("E_PILOT_SYSTEM_BOOST", "SYSTEM_BOOST_FALLBACK")


def canonical_dependency_list_bytes(paths: list[str]) -> bytes:
    return ("".join(f"{item}\n" for item in sorted(paths))).encode("utf-8")


def bind_configure_argv(cmake_path: str, cxx_path: str | None) -> list[str]:
    argv = [cmake_path, *CMAKE_CONFIGURE_ARGV[1:]]
    if cxx_path is not None:
        argv.append("-DCMAKE_CXX_COMPILER=" + cxx_path)
    return argv


def bind_build_argv(cmake_path: str) -> list[str]:
    return [cmake_path, *BASELINE_BUILD_ARGV[1:]]


def bind_job_specs(environment: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    cmake_path = environment["cmake_executable_path"]
    cxx_path = environment["cxx_compiler_path"]
    argvs = (
        bind_configure_argv(cmake_path, cxx_path),
        bind_build_argv(cmake_path),
        list(BASELINE_SMOKE_ARGV),
    )
    bound = []
    for spec, argv in zip(JOB_SPECS, argvs, strict=True):
        item = dict(spec)
        item["argv"] = list(argv)
        bound.append(item)
    return tuple(bound)


def attempt2_phase_descriptors(cmake_path: str) -> list[dict[str, Any]]:
    if type(cmake_path) is not str or not cmake_path or not os.path.isabs(cmake_path):
        raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "CMake path must be absolute")
    configure = [cmake_path, "-S", ATTEMPT2_HARNESS_ROOT.as_posix(), "-B",
        ATTEMPT2_BUILD_ROOT.as_posix(), "-G", "Unix Makefiles", "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_CXX_STANDARD=14", "-DCMAKE_CXX_STANDARD_REQUIRED=ON",
        "-DBOOST_MATH_STANDALONE=1",
        "-DBOOST_MATH_PILOT_SOURCE_INCLUDE=/tmp/p3-boost-math-pilot-production-source/include",
        "-DCMAKE_DISABLE_SOURCE_CHANGES=ON", "-DCMAKE_DISABLE_IN_SOURCE_BUILD=ON",
        "-DFETCHCONTENT_FULLY_DISCONNECTED=ON", "-DFETCHCONTENT_UPDATES_DISCONNECTED=ON",
        "-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF", "-DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF",
        "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON", "-DCMAKE_CXX_COMPILER=/usr/bin/c++"]
    rows = [
        ("METADATA_CMAKE_VERSION", [], [cmake_path, "--version"], 10),
        ("SOURCE_RESTORE", ["METADATA_CMAKE_VERSION"], [], 0),
        ("CMAKE_CONFIGURE", ["SOURCE_RESTORE"], configure, 900),
        ("BASELINE_BUILD", ["CMAKE_CONFIGURE"], [cmake_path, "--build",
         ATTEMPT2_BUILD_ROOT.as_posix(), "--parallel", "4"], 3600),
        ("BASELINE_SMOKE", ["BASELINE_BUILD"],
         [(ATTEMPT2_BUILD_ROOT / "boost_math_pilot_smoke").as_posix()], 1800),
    ]
    return [{"phase_id": phase, "phase_kind": phase,
             "dependency_phase_ids": deps, "argv": argv,
             "timeout_seconds": timeout} for phase, deps, argv, timeout in rows]


def make_attempt2_not_started(spec: dict[str, Any]) -> dict[str, Any]:
    payload = {"schema_version": ATTEMPT2_PHASE_SCHEMA, "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY", **spec, "process_started": False,
        "process_group_terminated": None, "infrastructure_phase": None,
        "terminal_status": "NOT_STARTED", "failure_reason": None, "exit_code": None,
        "stdout_sha256": None, "stderr_sha256": None, "stdout_bytes": None,
        "stderr_bytes": None, "started_at": None, "ended_at": None,
        "wall_seconds": None, "cpu_seconds": None, "peak_rss_bytes": None,
        "source_restoration_evidence": None, "claims": "blocked"}
    payload["artifact_sha256"] = canonical_sha256(payload)
    return validate_attempt2_phase_result(payload)


def validate_attempt2_phase_result(value: object) -> dict[str, Any]:
    validated = validate_exact_object(value, ATTEMPT2_PHASE_EXACT, "attempt2-phase")
    if validated["schema_version"] != ATTEMPT2_PHASE_SCHEMA or validated["phase_id"] != validated["phase_kind"]:
        raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "phase identity differs")
    if validated["execution_class"] != "PILOT_ONLY" or validated["denominator"] != "PILOT_ONLY" or validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "claim ceiling differs")
    if validated["terminal_status"] not in {"PASS", "FAIL", "TIMEOUT", "FAIL_INFRASTRUCTURE", "NOT_STARTED"}:
        raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "status differs")
    cmake_path = (validated["argv"][0] if validated["phase_id"] in
                  {"METADATA_CMAKE_VERSION", "CMAKE_CONFIGURE", "BASELINE_BUILD"}
                  and validated["argv"] else "/cmake")
    descriptors = {item["phase_id"]: item for item in attempt2_phase_descriptors(cmake_path)}
    expected = descriptors.get(validated["phase_id"])
    if expected is None or any(validated[key] != expected[key] for key in
                               ("phase_kind", "dependency_phase_ids", "argv", "timeout_seconds")):
        raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "phase descriptor differs")
    if validated["terminal_status"] == "NOT_STARTED":
        forbidden = ("process_group_terminated", "infrastructure_phase", "failure_reason",
                     "exit_code", "stdout_sha256", "stderr_sha256", "stdout_bytes",
                     "stderr_bytes", "started_at", "ended_at", "wall_seconds",
                     "cpu_seconds", "peak_rss_bytes", "source_restoration_evidence")
        if validated["process_started"] is not False or any(validated[key] is not None for key in forbidden):
            raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "NOT_STARTED carries evidence")
    elif validated["phase_id"] == "SOURCE_RESTORE":
        from p3_v3.pilot_source import validate_source_restoration_evidence
        forbidden = ("process_group_terminated", "infrastructure_phase", "exit_code",
                     "stdout_sha256", "stderr_sha256", "stdout_bytes", "stderr_bytes",
                     "started_at", "ended_at", "wall_seconds", "cpu_seconds", "peak_rss_bytes")
        if validated["process_started"] is not False or any(validated[k] is not None for k in forbidden):
            raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "source restoration forged process evidence")
        evidence = validate_source_restoration_evidence(validated["source_restoration_evidence"])
        if (validated["terminal_status"] != evidence["terminal_status"]
                or validated["terminal_status"] not in {"PASS", "FAIL"}
                or validated["failure_reason"] != evidence["failure_reason"]):
            raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "restoration status differs")
    else:
        if validated["source_restoration_evidence"] is not None:
            raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "process phase carries restoration")
        job = dict(validated)
        job.pop("source_restoration_evidence")
        job.update(schema_version="p3-pilot-build-preflight-job-result-v1",
                   job_id=job.pop("phase_id"), job_kind=job.pop("phase_kind"),
                   dependency_job_ids=job.pop("dependency_phase_ids"))
        job["artifact_sha256"] = canonical_sha256({k: v for k, v in job.items() if k != "artifact_sha256"})
        validate_job_result(job)
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "self-hash differs")
    return validated


def validate_attempt2_environment(value: object) -> dict[str, Any]:
    validated = validate_exact_object(value, ATTEMPT2_ENVIRONMENT_EXACT, "attempt2-environment")
    if (validated["schema_version"] != ATTEMPT2_ENVIRONMENT_SCHEMA
            or validated["execution_class"] != "PILOT_ONLY"
            or validated["denominator"] != "PILOT_ONLY" or validated["claims"] != "blocked"):
        raise EvidenceError("E_PILOT_ATTEMPT2_ENVIRONMENT", "identity or ceiling differs")
    path = validated["cmake_executable_path"]
    nonempty = ("cxx_compiler_identity", "cxx_compiler_version", "os_name", "os_release",
                "python_version", "git_version")
    if (validated["cmake_executable"] != "cmake" or type(path) is not str or not path
            or not os.path.isabs(path) or validated["cmake_version"] == ""
            or validated["cxx_compiler_executable"] != "c++"
            or validated["cxx_compiler_path"] != FROZEN_CXX_PATH
            or any(type(validated[k]) is not str or not validated[k] for k in nonempty)
            or validated["cmake_generator"] != "Unix Makefiles"
            or type(validated["build_parallelism"]) is not int
            or validated["build_parallelism"] != 4 or type(validated["nvcc_present"]) is not bool
            or validated["native_profiling_present"] is not False
            or validated["cuda_absence_blocking"] is not False
            or validated["fetchcontent_fully_disconnected"] is not True
            or validated["system_boost_fallback_accepted"] is not False
            or validated["disconnected_environment"] != DISCONNECTED_ENVIRONMENT
            or validated["verification_scope"] != "ARTIFACT_HASH_AND_HOST_SNAPSHOT"
            or validated["executor_cloud_run_id"] is not None
            or validated["executor_build_snapshot_id"] is not None):
        raise EvidenceError("E_PILOT_ATTEMPT2_ENVIRONMENT", "frozen environment differs")
    validate_sha256(validated["qualification_evidence_sha256"], "qualification_evidence_sha256")
    if validated["artifact_sha256"] != canonical_sha256({k: v for k, v in validated.items() if k != "artifact_sha256"}):
        raise EvidenceError("E_PILOT_ATTEMPT2_ENVIRONMENT", "self-hash differs")
    return validated


def resolve_cmake_executable_path() -> str:
    path = shutil.which("cmake")
    if path is None:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
    if not os.path.isabs(path):
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY") from exc
    if stat.S_ISLNK(info.st_mode):
        target = os.path.realpath(path)
        try:
            target_info = os.lstat(target)
        except OSError as exc:
            raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY") from exc
        if not stat.S_ISREG(target_info.st_mode) or not os.path.isabs(target):
            raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
        return target
    if not stat.S_ISREG(info.st_mode):
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
    return path


def run_metadata_cmake_version(cmake_path: str, log_root: Path) -> dict[str, Any]:
    descriptor = attempt2_phase_descriptors(cmake_path)[0]
    spec = {"job_id": descriptor["phase_id"], "job_kind": descriptor["phase_kind"],
            "dependency_job_ids": descriptor["dependency_phase_ids"],
            "argv": descriptor["argv"], "timeout_seconds": descriptor["timeout_seconds"]}
    env = dict(os.environ)
    reject_system_boost_environment(env)
    env.update(DISCONNECTED_ENVIRONMENT)
    reject_unbound_toolchain(env, FROZEN_CXX_PATH)
    return execute_job(spec, env=env, log_root=log_root)


def reject_unbound_toolchain(env: dict[str, str], resolved_cxx: str | None) -> None:
    for key in FORBIDDEN_TOOLCHAIN_ENV:
        value = env.get(key)
        if not value:
            continue
        if resolved_cxx is None or os.path.realpath(value) != os.path.realpath(resolved_cxx):
            raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")


def parse_cmake_cache(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        if ":" not in line or "=" not in line:
            continue
        key = line.split(":", 1)[0]
        value = line.split("=", 1)[1]
        values[key] = value
    return values


def smoke_compile_argv(compile_db: list[object]) -> list[str]:
    matches = []
    for entry in compile_db:
        if not isinstance(entry, dict):
            continue
        file_name = str(entry.get("file", ""))
        if Path(file_name).name != "smoke.cpp":
            continue
        matches.append(entry)
    if len(matches) != 1:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    entry = matches[0]
    if isinstance(entry.get("arguments"), list):
        return [str(item) for item in entry["arguments"]]
    command = entry.get("command")
    if not isinstance(command, str):
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    return shlex.split(command)


def ensure_safe_log_root(log_root: Path) -> Path:
    if os.path.lexists(log_root) and log_root.is_symlink():
        raise EvidenceError("E_PILOT_BUILD_SYMLINK", "log-root is a symlink")
    log_root.mkdir(parents=True, exist_ok=True)
    if log_root.is_symlink() or not log_root.is_dir():
        raise EvidenceError("E_PILOT_BUILD_PATH", "log-root is unsafe")
    return log_root


def argv_digest(argv: list[str]) -> str:
    return _sha256_bytes("\0".join(argv).encode("utf-8"))


def write_job_start_marker(log_root: Path, spec: dict[str, Any]) -> str:
    digest = argv_digest(list(spec["argv"]))
    payload = {
        "job_id": spec["job_id"],
        "argv_sha256": digest,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "state": "STARTING",
    }
    write_canonical_json(
        log_root / f"{spec['job_id']}.start.json",
        payload,
        exclusive=True,
    )
    return digest


def write_process_identity(
    log_root: Path,
    spec: dict[str, Any],
    pid: int,
    pgid: int,
    starttime: str,
    argv_sha256: str,
) -> None:
    payload = {
        "job_id": spec["job_id"],
        "pid": pid,
        "pgid": pgid,
        "starttime": starttime,
        "argv_sha256": argv_sha256,
    }
    write_canonical_json(
        log_root / f"{spec['job_id']}.identity.json",
        payload,
        exclusive=True,
    )


def load_process_identities(log_root: Path) -> list[dict[str, Any]]:
    if not log_root.is_dir():
        return []
    records = []
    for path in sorted(log_root.glob("*.identity.json")):
        raw, _digest = read_authority_snapshot(path, "process-identity")
        records.append(parse_canonical_json_object(raw, "process-identity"))
    return records


def load_job_start_markers(log_root: Path) -> list[dict[str, Any]]:
    if not log_root.is_dir():
        return []
    records = []
    for path in sorted(log_root.glob("*.start.json")):
        raw, _digest = read_authority_snapshot(path, "job-start-marker")
        records.append(parse_canonical_json_object(raw, "job-start-marker"))
    return records


def _is_controller_process_group(pgid: int | None, proc: Any) -> bool:
    if pgid is None or proc is None:
        return False
    try:
        return pgid == os.getpgrp() and int(proc.pid) == os.getpid()
    except (TypeError, ValueError, OSError):
        return False


def _pgid_still_matches_identity(
    pgid: int | None, pid: int | None, starttime: str | None
) -> bool:
    if pgid is None or pid is None or starttime is None:
        return False
    path = Path(f"/proc/{pid}/stat")
    if not path.is_file():
        return True
    return attempt_is_live(pid, starttime)


def child_records_are_live(records: list[dict[str, Any]]) -> bool:
    for record in records:
        if attempt_is_live(int(record["pid"]), str(record["starttime"])):
            return True
        if process_group_has_members(int(record["pgid"])):
            return True
    return False


def select_cumulative_output(
    previous: bytes,
    final_snapshot: bytes | None,
) -> bytes:
    if final_snapshot is None:
        return previous
    return final_snapshot


def terminate_and_reap_process_group(
    pgid: int | None,
    proc: Any,
    pid: int | None = None,
    starttime: str | None = None,
    *,
    force: bool = True,
) -> tuple[bytes | None, bytes | None, bool]:
    final_stdout_snapshot: bytes | None = None
    final_stderr_snapshot: bytes | None = None
    if _is_controller_process_group(pgid, proc):
        return None, None, False
    still_running = False
    if proc is not None and hasattr(proc, "poll"):
        still_running = proc.poll() is None
    identity_ok = _pgid_still_matches_identity(pgid, pid, starttime)
    if force and still_running and pgid is not None and identity_ok:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if proc is not None:
        try:
            received_out, received_err = proc.communicate(timeout=5)
            final_stdout_snapshot = received_out
            final_stderr_snapshot = received_err
        except Exception:
            final_stdout_snapshot = None
            final_stderr_snapshot = None
            try:
                proc.wait(timeout=5)
            except Exception:
                pass
    leaked = False
    if pgid is not None and _pgid_still_matches_identity(pgid, pid, starttime):
        if process_group_has_members(pgid):
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline and process_group_has_members(pgid):
                time.sleep(0.05)
        leaked = process_group_has_members(pgid)
    return final_stdout_snapshot, final_stderr_snapshot, leaked


def validate_implementation_verdict(
    value: object, plan_sha256: str, plan_verdict_sha256: str
) -> dict[str, Any]:
    validated = validate_exact_object(
        value,
        IMPLEMENTATION_VERDICT_EXACT,
        "build-preflight-implementation-verdict",
    )
    for key in (
        "reviewed_plan_sha256",
        "reviewed_plan_verdict_sha256",
        "reviewed_pilot_build_sha256",
        "reviewed_pilot_cli_sha256",
        "reviewed_test_pilot_build_sha256",
        "reviewed_test_pilot_sha256",
    ):
        validate_sha256(validated[key], f"implementation-verdict.{key}")
    if GIT_OID_RE.fullmatch(validated["reviewed_commit"]) is None:
        raise EvidenceError(
            "E_PILOT_BUILD_IMPL_VERDICT",
            "reviewed_commit is not 40 lowercase hexadecimal characters",
        )
    if validated["reviewed_plan_path"] != PLAN_PATH.as_posix():
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "reviewed plan path differs")
    if validated["reviewed_plan_sha256"] != plan_sha256:
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "reviewed plan hash differs")
    if validated["reviewed_plan_verdict_sha256"] != plan_verdict_sha256:
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "plan verdict hash differs")
    for path_key, _sha_key, expected in REVIEWED_IMPLEMENTATION_FILES:
        if validated[path_key] != expected:
            raise EvidenceError(
                "E_PILOT_BUILD_IMPL_VERDICT",
                f"{path_key} differs",
            )
    if validated["verdict"] != "PASS":
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "verdict is not PASS")
    if validated["authorized_state"] != "PILOT_BUILD_PREFLIGHT_IMPLEMENTATION_PASS":
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "authorized_state differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "claims are not blocked")
    return validated


def verify_reviewed_production_bytes(verdict: dict[str, Any]) -> None:
    for path_key, sha_key, expected in REVIEWED_IMPLEMENTATION_FILES:
        if verdict[path_key] != expected:
            raise EvidenceError("E_PILOT_BUILD_PRODUCTION_BYTES", f"{path_key} differs")
        raw, digest = read_authority_snapshot(Path(expected), path_key)
        if digest != verdict[sha_key]:
            raise EvidenceError(
                "E_PILOT_BUILD_PRODUCTION_BYTES",
                f"{expected} drifted from the implementation verdict",
            )
        if _sha256_bytes(raw) != digest:
            raise EvidenceError("E_PILOT_BUILD_PRODUCTION_BYTES", "snapshot hash drifted")


def validate_environment_snapshot(value: object) -> dict[str, Any]:
    # Pilot producer accepts p3-pilot / PILOT_ONLY objects. Do not call
    # reject_confirmatory_pilot here: that helper is the confirmatory
    # consumer gate and would reject this node's legal inputs.
    validated = validate_exact_object(
        value,
        BUILD_PREFLIGHT_ENVIRONMENT_EXACT,
        "p3-pilot-build-preflight-environment-v1",
    )
    if validated["schema_version"] != "p3-pilot-build-preflight-environment-v1":
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "schema differs")
    if validated["execution_class"] != PILOT_EXECUTION_CLASS:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "class differs")
    if validated["denominator"] != PILOT_DENOMINATOR:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "denominator differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "claims are not blocked")
    if validated["system_boost_fallback_accepted"] is not False:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "system Boost fallback accepted")
    if validated["fetchcontent_fully_disconnected"] is not True:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "FetchContent is not disconnected")
    if validated["cuda_absence_blocking"] is not False:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CUDA absence must be non-blocking")
    if validated["native_profiling_present"] is not False:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "profiling is not a prerequisite")
    if validated["disconnected_environment"] != DISCONNECTED_ENVIRONMENT:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "disconnected environment differs")
    if validated["cmake_generator"] != FROZEN_CMAKE_GENERATOR:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "generator differs")
    if validated["build_parallelism"] != BUILD_PARALLELISM:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "parallelism differs")
    if not validated["cmake_executable_path"] or not validated["cmake_version"]:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "cmake identity is incomplete")
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "self-hash differs")
    return validated


def _require_stdio(validated: dict[str, Any]) -> None:
    if validated["stdout_sha256"] is None or validated["stderr_sha256"] is None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "started job must hash stdio")
    validate_sha256(validated["stdout_sha256"], "job.stdout_sha256")
    validate_sha256(validated["stderr_sha256"], "job.stderr_sha256")
    if type(validated["stdout_bytes"]) is not int or validated["stdout_bytes"] < 0:
        raise EvidenceError("E_PILOT_BUILD_JOB", "stdout_bytes is invalid")
    if type(validated["stderr_bytes"]) is not int or validated["stderr_bytes"] < 0:
        raise EvidenceError("E_PILOT_BUILD_JOB", "stderr_bytes is invalid")
    if validated["started_at"] is None or validated["ended_at"] is None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "started job must have timestamps")
    if validated["wall_seconds"] is None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "started job must have wall time")
    if validated["cpu_seconds"] is None or validated["peak_rss_bytes"] is None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "started job must have rusage")


def _require_no_process_evidence(validated: dict[str, Any]) -> None:
    if validated["exit_code"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not have exit_code")
    if validated["stdout_sha256"] is not None or validated["stderr_sha256"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not forge hashes")
    if validated["stdout_bytes"] is not None or validated["stderr_bytes"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not forge byte counts")
    if validated["wall_seconds"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not have wall time")
    if validated["cpu_seconds"] is not None or validated["peak_rss_bytes"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not have rusage")
    if validated["process_group_terminated"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not claim a process group")


def validate_job_result(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value,
        BUILD_PREFLIGHT_JOB_RESULT_EXACT,
        "p3-pilot-build-preflight-job-result-v1",
    )
    if validated["schema_version"] != "p3-pilot-build-preflight-job-result-v1":
        raise EvidenceError("E_PILOT_BUILD_JOB", "schema differs")
    if validated["execution_class"] != PILOT_EXECUTION_CLASS:
        raise EvidenceError("E_PILOT_BUILD_JOB", "class differs")
    if validated["denominator"] != PILOT_DENOMINATOR:
        raise EvidenceError("E_PILOT_BUILD_JOB", "denominator differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_JOB", "claims are not blocked")
    if validated["terminal_status"] not in ALL_TERMINAL:
        raise EvidenceError("E_PILOT_BUILD_JOB", "terminal status differs")
    if type(validated["argv"]) is not list or any(
        type(item) is not str for item in validated["argv"]
    ):
        raise EvidenceError("E_PILOT_BUILD_JOB", "argv is invalid")
    if type(validated["dependency_job_ids"]) is not list or any(
        type(item) is not str for item in validated["dependency_job_ids"]
    ):
        raise EvidenceError("E_PILOT_BUILD_JOB", "dependency_job_ids are invalid")
    status = validated["terminal_status"]
    if status == "PASS":
        if validated["process_started"] is not True:
            raise EvidenceError("E_PILOT_BUILD_JOB", "PASS must start a process")
        if validated["exit_code"] != 0:
            raise EvidenceError("E_PILOT_BUILD_JOB", "PASS must have exit_code 0")
        if validated["failure_reason"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "PASS must not carry a failure")
        if validated["infrastructure_phase"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "PASS must not set infrastructure_phase")
        if validated["process_group_terminated"] is not False:
            raise EvidenceError("E_PILOT_BUILD_JOB", "PASS must not kill the process group")
        _require_stdio(validated)
    elif status == "FAIL":
        if validated["process_started"] is not True:
            raise EvidenceError("E_PILOT_BUILD_JOB", "FAIL must start a process")
        if validated["failure_reason"] not in FAIL_REASONS:
            raise EvidenceError("E_PILOT_BUILD_JOB", "FAIL reason is not frozen")
        if validated["failure_reason"] == "NONZERO_EXIT" and (
            validated["exit_code"] is None or validated["exit_code"] == 0
        ):
            raise EvidenceError("E_PILOT_BUILD_JOB", "NONZERO_EXIT must have a nonzero exit")
        if validated["failure_reason"] == "CRASH" and validated["exit_code"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "CRASH must not invent exit_code")
        if validated["infrastructure_phase"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "FAIL must not set infrastructure_phase")
        _require_stdio(validated)
    elif status == "TIMEOUT":
        if validated["process_started"] is not True:
            raise EvidenceError("E_PILOT_BUILD_JOB", "TIMEOUT must start a process")
        if validated["exit_code"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "TIMEOUT must have null exit_code")
        if validated["failure_reason"] != "TIMEOUT":
            raise EvidenceError("E_PILOT_BUILD_JOB", "TIMEOUT reason differs")
        if validated["process_group_terminated"] is not True:
            raise EvidenceError("E_PILOT_BUILD_JOB", "TIMEOUT must terminate the process group")
        if validated["infrastructure_phase"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "TIMEOUT must not set infrastructure_phase")
        _require_stdio(validated)
    elif status == "FAIL_INFRASTRUCTURE":
        if validated["infrastructure_phase"] not in {"PRE_PROCESS", "POST_PROCESS"}:
            raise EvidenceError("E_PILOT_BUILD_JOB", "infrastructure_phase differs")
        if validated["infrastructure_phase"] == "PRE_PROCESS":
            if validated["process_started"] is not False:
                raise EvidenceError("E_PILOT_BUILD_JOB", "PRE_PROCESS must not start")
            if validated["failure_reason"] not in INFRA_REASONS_PRE_PROCESS:
                raise EvidenceError("E_PILOT_BUILD_JOB", "PRE_PROCESS reason is not frozen")
            _require_no_process_evidence(validated)
        else:
            if validated["process_started"] is not True:
                raise EvidenceError("E_PILOT_BUILD_JOB", "POST_PROCESS must start")
            if validated["failure_reason"] not in INFRA_REASONS_POST_PROCESS:
                raise EvidenceError("E_PILOT_BUILD_JOB", "POST_PROCESS reason is not frozen")
            if (
                validated["failure_reason"] in POST_SPAWN_CLEANUP_REASONS
                and validated["process_group_terminated"] is not True
            ):
                raise EvidenceError(
                    "E_PILOT_BUILD_JOB",
                    "post-spawn infrastructure failure must terminate the process group",
                )
            _require_stdio(validated)
    elif status == "NOT_STARTED":
        if validated["process_started"] is not False:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not start")
        if validated["failure_reason"] != "DEPENDENCY_NOT_STARTED":
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED reason differs")
        if validated["infrastructure_phase"] is not None:
            raise EvidenceError(
                "E_PILOT_BUILD_JOB",
                "NOT_STARTED must not set infrastructure_phase",
            )
        if validated["started_at"] is not None or validated["ended_at"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not have timestamps")
        _require_no_process_evidence(validated)
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_BUILD_JOB", "self-hash differs")
    return validated


def validate_intent(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value, BUILD_PREFLIGHT_INTENT_EXACT, "p3-pilot-build-preflight-intent-v1"
    )
    if validated["schema_version"] != "p3-pilot-build-preflight-intent-v1":
        raise EvidenceError("E_PILOT_BUILD_INTENT", "schema differs")
    if validated["execution_class"] != PILOT_EXECUTION_CLASS:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "class differs")
    if validated["denominator"] != PILOT_DENOMINATOR:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "denominator differs")
    if validated["plan_class"] != "PILOT_BUILD_PREFLIGHT_ONLY":
        raise EvidenceError("E_PILOT_BUILD_INTENT", "plan class differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_INTENT", "claims are not blocked")
    if validated["formal_denominator_membership"] is not False:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "denominator membership must be false")
    if validated["rq4_supported"] is not False:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "rq4_supported must be false")
    if validated["no_retry"] is not True:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "no_retry must be true")
    if validated["planned_count"] != PLANNED_COUNT:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "planned_count must be 3")
    if validated["build_parallelism"] != BUILD_PARALLELISM:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "parallelism must be 4")
    if validated["cmake_configure_timeout_seconds"] != CMAKE_CONFIGURE_TIMEOUT_SECONDS:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "configure timeout differs")
    if validated["baseline_build_timeout_seconds"] != BASELINE_BUILD_TIMEOUT_SECONDS:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "build timeout differs")
    if validated["baseline_smoke_timeout_seconds"] != BASELINE_SMOKE_TIMEOUT_SECONDS:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "smoke timeout differs")
    if validated["outer_timeout_seconds"] != OUTER_TIMEOUT_SECONDS:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "outer timeout differs")
    snapshot = validate_environment_snapshot(validated["environment_snapshot"])
    if snapshot["artifact_sha256"] != validated["environment_snapshot_sha256"]:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "environment snapshot hash differs")
    if validated["cmake_configure_argv"] != bind_configure_argv(
        snapshot["cmake_executable_path"], snapshot["cxx_compiler_path"]
    ):
        raise EvidenceError("E_PILOT_BUILD_INTENT", "configure argv differs")
    if validated["baseline_build_argv"] != bind_build_argv(snapshot["cmake_executable_path"]):
        raise EvidenceError("E_PILOT_BUILD_INTENT", "build argv differs")
    if validated["baseline_smoke_argv"] != BASELINE_SMOKE_ARGV:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "smoke argv differs")
    if validated["dependency_dag"] != DEPENDENCY_DAG:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "dependency dag differs")
    if validated["source_root"] != FROZEN_SOURCE_ROOT.as_posix():
        raise EvidenceError("E_PILOT_BUILD_INTENT", "source root differs")
    if validated["build_root"] != FROZEN_BUILD_ROOT.as_posix():
        raise EvidenceError("E_PILOT_BUILD_INTENT", "build root differs")
    if validated["harness_root"] != FROZEN_HARNESS_ROOT.as_posix():
        raise EvidenceError("E_PILOT_BUILD_INTENT", "harness root differs")
    if validated["authorization_sha256"] != AUTHORIZATION_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "authorization hash differs")
    if validated["harness_cmake_sha256"] != HARNESS_CMAKE_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "harness cmake hash differs")
    if validated["harness_cxx_sha256"] != HARNESS_CXX_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "harness cxx hash differs")
    if validated["normalized_source_tree_sha256"] != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "tree hash differs")
    if (
        validated["source_preparation_verdict_sha256"]
        != SOURCE_PREPARATION_RESULT_VERDICT_SHA256
    ):
        raise EvidenceError("E_PILOT_BUILD_INTENT", "source-preparation verdict differs")
    if validated["source_manifest_sha256"] != SOURCE_MANIFEST_FILE_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "source manifest hash differs")
    if validated["source_preparation_result_sha256"] != SOURCE_PREPARATION_RESULT_FILE_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "source-preparation result differs")
    validate_sha256(
        validated["implementation_verdict_sha256"],
        "intent.implementation_verdict_sha256",
    )
    if validated["implementation_verdict_sha256"] not in validated["predecessor_sha256"]:
        raise EvidenceError(
            "E_PILOT_BUILD_INTENT",
            "predecessor_sha256 must contain implementation_verdict_sha256",
        )
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_BUILD_INTENT", "self-hash differs")
    return validated


def validate_result(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value, BUILD_PREFLIGHT_RESULT_EXACT, "p3-pilot-build-preflight-result-v1"
    )
    if validated["schema_version"] != "p3-pilot-build-preflight-result-v1":
        raise EvidenceError("E_PILOT_BUILD_RESULT", "schema differs")
    if validated["execution_class"] != PILOT_EXECUTION_CLASS:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "class differs")
    if validated["denominator"] != PILOT_DENOMINATOR:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "denominator differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_RESULT", "claims are not blocked")
    if validated["formal_denominator_membership"] is not False:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "denominator membership must be false")
    if validated["rq4_supported"] is not False:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "rq4_supported must be false")
    if validated["no_retry"] is not True:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "no_retry must be true")
    if validated["planned_count"] != PLANNED_COUNT:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "planned_count must be 3")
    if validated["terminal_count"] != PLANNED_COUNT:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "terminal_count must be 3")
    if type(validated["jobs"]) is not list or len(validated["jobs"]) != 3:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "jobs must be exactly 3")
    jobs = [validate_job_result(item) for item in validated["jobs"]]
    order = [item["job_id"] for item in jobs]
    if order != ["CMAKE_CONFIGURE", "BASELINE_BUILD", "BASELINE_SMOKE"]:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "job order differs")
    started = sum(1 for item in jobs if item["process_started"] is True)
    not_started = sum(1 for item in jobs if item["terminal_status"] == "NOT_STARTED")
    if validated["started_count"] != started:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "started_count is not conserved")
    if validated["not_started_count"] != not_started:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "not_started_count is not conserved")
    for job, spec in zip(jobs, JOB_SPECS, strict=True):
        if job["job_id"] != spec["job_id"] or job["job_kind"] != spec["job_kind"]:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "job identity differs")
        if job["dependency_job_ids"] != list(spec["dependency_job_ids"]):
            raise EvidenceError("E_PILOT_BUILD_RESULT", "job dependencies differ")
        if job["timeout_seconds"] != spec["timeout_seconds"]:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "job timeout differs")
    if jobs[0]["terminal_status"] != "PASS":
        first_blocked = jobs[1]["terminal_status"] != "NOT_STARTED"
        second_blocked = jobs[2]["terminal_status"] != "NOT_STARTED"
        if first_blocked or second_blocked:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "configure failure must block dependents")
    elif jobs[1]["terminal_status"] != "PASS":
        if jobs[2]["terminal_status"] != "NOT_STARTED":
            raise EvidenceError("E_PILOT_BUILD_RESULT", "build failure must block smoke")
    first_bad = next((item for item in jobs if item["terminal_status"] != "PASS"), None)
    if first_bad is None:
        if validated["terminal_status"] != "PASS" or validated["failure_reason"] is not None:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "all-PASS aggregate differs")
    else:
        if validated["terminal_status"] != first_bad["terminal_status"]:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "aggregate status differs")
        if validated["failure_reason"] != first_bad["failure_reason"]:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "aggregate failure_reason differs")
    if jobs[1]["terminal_status"] == "PASS":
        for key in (
            "cmake_cache_sha256",
            "compile_commands_sha256",
            "compiler_depfile_sha256",
            "dependency_list_sha256",
            "smoke_executable_sha256",
        ):
            validate_sha256(validated[key], f"result.{key}")
    elif first_bad is not None and jobs[1]["terminal_status"] != "PASS":
        for key in (
            "cmake_cache_sha256",
            "compile_commands_sha256",
            "compiler_depfile_sha256",
            "dependency_list_sha256",
            "smoke_executable_sha256",
        ):
            if validated[key] is not None:
                raise EvidenceError("E_PILOT_BUILD_RESULT", f"{key} must be null")
    snapshot = validate_environment_snapshot(validated["environment_snapshot"])
    if snapshot["artifact_sha256"] != validated["environment_snapshot_sha256"]:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "environment snapshot hash differs")
    validate_sha256(
        validated["implementation_verdict_sha256"],
        "result.implementation_verdict_sha256",
    )
    if validated["implementation_verdict_sha256"] not in validated["predecessor_sha256"]:
        raise EvidenceError(
            "E_PILOT_BUILD_RESULT",
            "predecessor_sha256 must contain implementation_verdict_sha256",
        )
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_BUILD_RESULT", "self-hash differs")
    return validated


def validate_attempt_pair(
    intent: object, intent_file_sha256: str, result: object
) -> tuple[dict[str, Any], dict[str, Any]]:
    validated_intent = validate_intent(intent)
    validated_result = validate_result(result)
    validate_sha256(intent_file_sha256, "attempt.intent_file_sha256")
    if validated_result["intent_sha256"] != intent_file_sha256:
        raise EvidenceError("E_PILOT_BUILD_PAIR", "intent file SHA differs")
    if validated_result["environment_snapshot"] != validated_intent["environment_snapshot"]:
        raise EvidenceError("E_PILOT_BUILD_PAIR", "environment snapshot differs")
    if (
        validated_result["environment_snapshot_sha256"]
        != validated_intent["environment_snapshot_sha256"]
    ):
        raise EvidenceError("E_PILOT_BUILD_PAIR", "environment snapshot hash differs")
    if (
        validated_result["implementation_verdict_sha256"]
        != validated_intent["implementation_verdict_sha256"]
    ):
        raise EvidenceError("E_PILOT_BUILD_PAIR", "implementation verdict SHA differs")
    for key in (
        "source_preparation_verdict_sha256",
        "source_manifest_sha256",
        "source_preparation_result_sha256",
        "normalized_source_tree_sha256",
        "controlled_subject_id",
        "controlled_subject_source_id",
        "build_descriptor_sha256",
        "authorization_sha256",
        "harness_cmake_sha256",
        "harness_cxx_sha256",
        "source_root",
        "build_root",
        "harness_root",
    ):
        if validated_result[key] != validated_intent[key]:
            raise EvidenceError("E_PILOT_BUILD_PAIR", f"{key} differs")
    expected_predecessor = sorted(
        [intent_file_sha256, *validated_intent["predecessor_sha256"]]
    )
    if validated_result["predecessor_sha256"] != expected_predecessor:
        raise EvidenceError("E_PILOT_BUILD_PAIR", "predecessor set differs")
    expected_argvs = [
        validated_intent["cmake_configure_argv"],
        validated_intent["baseline_build_argv"],
        validated_intent["baseline_smoke_argv"],
    ]
    expected_timeouts = [
        validated_intent["cmake_configure_timeout_seconds"],
        validated_intent["baseline_build_timeout_seconds"],
        validated_intent["baseline_smoke_timeout_seconds"],
    ]
    for job, argv, timeout, spec in zip(
        validated_result["jobs"], expected_argvs, expected_timeouts, JOB_SPECS, strict=True
    ):
        if job["argv"] != argv:
            raise EvidenceError("E_PILOT_BUILD_PAIR", "job argv differs from intent")
        if job["timeout_seconds"] != timeout:
            raise EvidenceError("E_PILOT_BUILD_PAIR", "job timeout differs from intent")
        if job["dependency_job_ids"] != list(spec["dependency_job_ids"]):
            raise EvidenceError("E_PILOT_BUILD_PAIR", "job DAG differs from intent")
    return validated_intent, validated_result


def make_not_started_job(spec: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema_version": "p3-pilot-build-preflight-job-result-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "job_id": spec["job_id"],
        "job_kind": spec["job_kind"],
        "dependency_job_ids": list(spec["dependency_job_ids"]),
        "argv": list(spec["argv"]),
        "timeout_seconds": spec["timeout_seconds"],
        "process_started": False,
        "process_group_terminated": None,
        "infrastructure_phase": None,
        "terminal_status": "NOT_STARTED",
        "failure_reason": "DEPENDENCY_NOT_STARTED",
        "exit_code": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "stdout_bytes": None,
        "stderr_bytes": None,
        "started_at": None,
        "ended_at": None,
        "wall_seconds": None,
        "cpu_seconds": None,
        "peak_rss_bytes": None,
        "claims": "blocked",
    }
    return validate_job_result(_self_hash(payload))


def make_pre_process_infra_job(spec: dict[str, Any], reason: str) -> dict[str, Any]:
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = {
        "schema_version": "p3-pilot-build-preflight-job-result-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "job_id": spec["job_id"],
        "job_kind": spec["job_kind"],
        "dependency_job_ids": list(spec["dependency_job_ids"]),
        "argv": list(spec["argv"]),
        "timeout_seconds": spec["timeout_seconds"],
        "process_started": False,
        "process_group_terminated": None,
        "infrastructure_phase": "PRE_PROCESS",
        "terminal_status": "FAIL_INFRASTRUCTURE",
        "failure_reason": reason,
        "exit_code": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "stdout_bytes": None,
        "stderr_bytes": None,
        "started_at": now,
        "ended_at": now,
        "wall_seconds": None,
        "cpu_seconds": None,
        "peak_rss_bytes": None,
        "claims": "blocked",
    }
    return validate_job_result(_self_hash(payload))


def make_environment_snapshot() -> dict[str, Any]:
    cmake_path = shutil.which("cmake")
    cxx_path = shutil.which("c++") or shutil.which("g++")
    if cmake_path is None:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
    cmake_version = probe_identity(cmake_path)
    if cmake_version is None:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
    cxx_identity = probe_identity(cxx_path)
    payload = {
        "schema_version": "p3-pilot-build-preflight-environment-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "cmake_executable": "cmake",
        "cmake_executable_path": cmake_path,
        "cmake_version": cmake_version,
        "cxx_compiler_executable": None if cxx_path is None else Path(cxx_path).name,
        "cxx_compiler_path": cxx_path,
        "cxx_compiler_identity": cxx_identity,
        "cxx_compiler_version": cxx_identity,
        "cmake_generator": FROZEN_CMAKE_GENERATOR,
        "os_name": platform.system(),
        "os_release": platform.release(),
        "python_version": platform.python_version(),
        "git_version": probe_identity(shutil.which("git")),
        "build_parallelism": BUILD_PARALLELISM,
        "nvcc_present": shutil.which("nvcc") is not None,
        "native_profiling_present": False,
        "cuda_absence_blocking": False,
        "fetchcontent_fully_disconnected": True,
        "system_boost_fallback_accepted": False,
        "disconnected_environment": dict(DISCONNECTED_ENVIRONMENT),
        "claims": "blocked",
    }
    return validate_environment_snapshot(_self_hash(payload))


def collect_baseline_build_evidence(
    build_root: Path,
    environment: dict[str, Any],
) -> dict[str, str]:
    cache = build_root / "CMakeCache.txt"
    commands = build_root / "compile_commands.json"
    executable = build_root / "boost_math_pilot_smoke"
    dep_file = build_root / COMPILER_DEPFILE_RELATIVE
    for path in (cache, commands, executable, dep_file):
        if path.is_symlink() or not path.is_file():
            raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
        raw, _mode = read_regular_file_snapshot(path, path.name)
        if path == dep_file:
            dep_raw = raw
    cache_text = cache.read_text(encoding="utf-8")
    values = parse_cmake_cache(cache_text)
    if values.get("CMAKE_GENERATOR") != FROZEN_CMAKE_GENERATOR:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CMAKE_GENERATOR differs")
    compiler = environment["cxx_compiler_path"]
    if compiler is None:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
    cache_compiler = values.get("CMAKE_CXX_COMPILER")
    if cache_compiler is None or os.path.realpath(cache_compiler) != os.path.realpath(compiler):
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CMakeCache compiler differs")
    source_dir = values.get("CMAKE_HOME_DIRECTORY") or values.get("CMAKE_SOURCE_DIR")
    binary_dir = values.get("CMAKE_BINARY_DIR") or values.get("CMAKE_CACHEFILE_DIR")
    if source_dir != FROZEN_HARNESS_ROOT.as_posix():
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CMake source directory differs")
    if binary_dir != FROZEN_BUILD_ROOT.as_posix():
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CMake build directory differs")
    try:
        compile_db = json.loads(commands.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN") from exc
    if not isinstance(compile_db, list):
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    compile_argv = smoke_compile_argv(compile_db)
    if os.path.realpath(compile_argv[0]) != os.path.realpath(compiler):
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "compile_commands compiler differs")
    joined = " ".join(compile_argv)
    if FROZEN_INCLUDE_PREFIX not in joined:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    if "BOOST_MATH_STANDALONE=1" not in joined:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    for marker in SYSTEM_BOOST_MARKERS:
        if marker in joined:
            raise EvidenceError("E_PILOT_SYSTEM_BOOST", "SYSTEM_BOOST_FALLBACK")
    dep_text = dep_raw.decode("utf-8")
    paths = parse_dependency_paths(dep_text)
    reject_nonfrozen_boost_headers(paths)
    smoke_path = (FROZEN_HARNESS_ROOT / "smoke.cpp").as_posix()
    if smoke_path not in paths and "smoke.cpp" not in dep_text:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    if FROZEN_CONSTANTS_HEADER not in paths and FROZEN_CONSTANTS_HEADER not in dep_text:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    return {
        "cmake_cache_sha256": _sha256_bytes(cache.read_bytes()),
        "compile_commands_sha256": _sha256_bytes(commands.read_bytes()),
        "compiler_depfile_sha256": _sha256_bytes(dep_raw),
        "dependency_list_sha256": _sha256_bytes(canonical_dependency_list_bytes(paths)),
        "smoke_executable_sha256": _sha256_bytes(executable.read_bytes()),
    }


def write_harness(harness_root: Path, cmake_bytes: bytes, cxx_bytes: bytes) -> None:
    require_absent_path(harness_root, "harness-root")
    try:
        os.mkdir(harness_root)
        cmake_path = harness_root / "CMakeLists.txt"
        cxx_path = harness_root / "smoke.cpp"
        cmake_path.write_bytes(cmake_bytes)
        cxx_path.write_bytes(cxx_bytes)
    except OSError as exc:
        raise EvidenceError("E_PILOT_BUILD_HARNESS", "HARNESS_PUBLICATION_FAILURE") from exc
    if _sha256_bytes(cmake_path.read_bytes()) != _sha256_bytes(cmake_bytes):
        raise EvidenceError("E_PILOT_BUILD_HARNESS", "HARNESS_PUBLICATION_FAILURE")
    if _sha256_bytes(cxx_path.read_bytes()) != _sha256_bytes(cxx_bytes):
        raise EvidenceError("E_PILOT_BUILD_HARNESS", "HARNESS_PUBLICATION_FAILURE")


def execute_job(
    spec: dict[str, Any],
    *,
    env: dict[str, str],
    log_root: Path,
    popen=subprocess.Popen,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    reject_system_boost_environment(env)
    argv = list(spec["argv"])
    if any(not isinstance(item, str) for item in argv):
        raise EvidenceError("E_PILOT_BUILD_ARGV", "argv items must be strings")
    ensure_safe_log_root(log_root)
    argv_sha256 = write_job_start_marker(log_root, spec)
    start_marker = log_root / f"{spec['job_id']}.start.json"
    if not start_marker.is_file():
        raise EvidenceError(
            "E_PILOT_BUILD_START_MARKER",
            "STARTING start.json missing before Popen",
        )
    started_at = time.time()
    effective_timeout = spec["timeout_seconds"] if timeout_seconds is None else timeout_seconds
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    proc = None
    pgid = None
    pid = None
    starttime = None
    stdout = b""
    stderr = b""
    timed_out = False
    force_group_cleanup = False
    process_group_terminated = False
    post_spawn_reason = None
    identity_written = False
    try:
        proc = popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env=env,
            start_new_session=True,
        )
    except FileNotFoundError:
        return make_pre_process_infra_job(spec, "MISSING_DEPENDENCY")
    try:
        try:
            pgid = os.getpgid(proc.pid)
        except ProcessLookupError:
            pgid = proc.pid
        pid = proc.pid
        starttime = read_proc_starttime(proc.pid)
        write_process_identity(log_root, spec, proc.pid, pgid, starttime, argv_sha256)
        identity_written = True
        # communicate() is the only waiter so PIPE-backed children cannot
        # fill the buffer and deadlock. Slices let a parent-exit with live
        # descendants become PROCESS_GROUP_LEAK instead of a false TIMEOUT.
        if isinstance(proc, subprocess.Popen):
            deadline = time.monotonic() + float(effective_timeout)
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    force_group_cleanup = True
                    break
                try:
                    received = proc.communicate(timeout=min(0.2, remaining))
                    stdout = received[0] or b""
                    stderr = received[1] or b""
                    break
                except subprocess.TimeoutExpired as exc:
                    stdout = exc.stdout if exc.stdout is not None else stdout
                    stderr = exc.stderr if exc.stderr is not None else stderr
                    if proc.poll() is not None:
                        break
        else:
            received = proc.communicate(timeout=effective_timeout)
            stdout = received[0] or b""
            stderr = received[1] or b""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        force_group_cleanup = True
        stdout = exc.stdout if exc.stdout is not None else stdout
        stderr = exc.stderr if exc.stderr is not None else stderr
    except Exception:
        force_group_cleanup = True
        if not identity_written:
            post_spawn_reason = "PROCESS_IDENTITY_PUBLICATION_FAILURE"
        else:
            post_spawn_reason = "PROCESS_CONTROL_FAILURE"
    finally:
        final_stdout_snapshot = None
        final_stderr_snapshot = None
        leaked = False
        if force_group_cleanup:
            process_group_terminated = True
            if (
                pgid is not None
                and not _is_controller_process_group(pgid, proc)
                and _pgid_still_matches_identity(pgid, pid, starttime)
            ):
                try:
                    os.killpg(pgid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            (
                final_stdout_snapshot,
                final_stderr_snapshot,
                leaked,
            ) = terminate_and_reap_process_group(
                pgid, proc, pid, starttime, force=True
            )
            stdout = select_cumulative_output(stdout or b"", final_stdout_snapshot)
            stderr = select_cumulative_output(stderr or b"", final_stderr_snapshot)
            if leaked:
                post_spawn_reason = "PROCESS_CONTROL_FAILURE"
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    stdout = stdout or b""
    stderr = stderr or b""
    try:
        (log_root / f"{spec['job_id']}.stdout").write_bytes(stdout)
        (log_root / f"{spec['job_id']}.stderr").write_bytes(stderr)
    except OSError:
        post_spawn_reason = "LOG_PUBLICATION_FAILURE"
        process_group_terminated = True
        (
            final_stdout_snapshot,
            final_stderr_snapshot,
            leaked,
        ) = terminate_and_reap_process_group(
            pgid, proc, pid, starttime, force=True
        )
        stdout = select_cumulative_output(stdout, final_stdout_snapshot)
        stderr = select_cumulative_output(stderr, final_stderr_snapshot)
        try:
            (log_root / f"{spec['job_id']}.stdout").write_bytes(stdout)
            (log_root / f"{spec['job_id']}.stderr").write_bytes(stderr)
        except OSError:
            pass
    if not force_group_cleanup and post_spawn_reason is None:
        if _is_controller_process_group(pgid, proc):
            process_group_terminated = False
        elif (
            pgid is not None
            and process_group_has_members(pgid)
            and _pgid_still_matches_identity(pgid, pid, starttime)
        ):
            process_group_terminated = True
            post_spawn_reason = "PROCESS_GROUP_LEAK"
            (
                final_stdout_snapshot,
                final_stderr_snapshot,
                leaked,
            ) = terminate_and_reap_process_group(
                pgid, proc, pid, starttime, force=True
            )
            stdout = select_cumulative_output(stdout, final_stdout_snapshot)
            stderr = select_cumulative_output(stderr, final_stderr_snapshot)
            try:
                (log_root / f"{spec['job_id']}.stdout").write_bytes(stdout)
                (log_root / f"{spec['job_id']}.stderr").write_bytes(stderr)
            except OSError:
                post_spawn_reason = "LOG_PUBLICATION_FAILURE"
            if leaked:
                post_spawn_reason = "PROCESS_GROUP_LEAK"
        else:
            process_group_terminated = False
    ended_at = time.time()
    detected = detect_network_or_boost(stdout, stderr, argv)
    exit_code = None if proc is None else proc.returncode
    cpu_seconds = float(
        (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
    )
    peak_rss_bytes = int(after.ru_maxrss) * 1024
    if post_spawn_reason is not None:
        terminal_status = "FAIL_INFRASTRUCTURE"
        failure_reason = post_spawn_reason
        recorded_exit = None if timed_out else exit_code
        infrastructure_phase = "POST_PROCESS"
        process_group_terminated = True
    elif timed_out:
        terminal_status = "TIMEOUT"
        failure_reason = "TIMEOUT"
        recorded_exit = None
        infrastructure_phase = None
        process_group_terminated = True
    elif detected == "NETWORK_OR_DOWNLOAD_ATTEMPT":
        terminal_status = "FAIL_INFRASTRUCTURE"
        failure_reason = "NETWORK_OR_DOWNLOAD_ATTEMPT"
        recorded_exit = exit_code
        infrastructure_phase = "POST_PROCESS"
    elif detected == "SYSTEM_BOOST_FALLBACK":
        terminal_status = "FAIL_INFRASTRUCTURE"
        failure_reason = "SYSTEM_BOOST_FALLBACK"
        recorded_exit = exit_code
        infrastructure_phase = "POST_PROCESS"
    elif exit_code == 0:
        terminal_status = "PASS"
        failure_reason = None
        recorded_exit = 0
        infrastructure_phase = None
    elif exit_code is None or exit_code < 0:
        terminal_status = "FAIL"
        failure_reason = "CRASH"
        recorded_exit = None
        infrastructure_phase = None
    else:
        terminal_status = "FAIL"
        failure_reason = "NONZERO_EXIT"
        recorded_exit = exit_code
        infrastructure_phase = None
    payload = {
        "schema_version": "p3-pilot-build-preflight-job-result-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "job_id": spec["job_id"],
        "job_kind": spec["job_kind"],
        "dependency_job_ids": list(spec["dependency_job_ids"]),
        "argv": argv,
        "timeout_seconds": spec["timeout_seconds"],
        "process_started": True,
        "process_group_terminated": process_group_terminated,
        "infrastructure_phase": infrastructure_phase,
        "terminal_status": terminal_status,
        "failure_reason": failure_reason,
        "exit_code": recorded_exit,
        "stdout_sha256": _sha256_bytes(stdout),
        "stderr_sha256": _sha256_bytes(stderr),
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_at)),
        "ended_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ended_at)),
        "wall_seconds": float(ended_at - started_at),
        "cpu_seconds": cpu_seconds,
        "peak_rss_bytes": peak_rss_bytes,
        "claims": "blocked",
    }
    return validate_job_result(_self_hash(payload))


def run_three_jobs(
    specs: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    *,
    env: dict[str, str],
    log_root: Path,
    popen=subprocess.Popen,
    source_root: Path | None = None,
    environment: dict[str, Any] | None = None,
    outer_deadline: float | None = None,
    expected_smoke_sha256: str | None = None,
    collect_evidence=None,
) -> tuple[list[dict[str, Any]], dict[str, str] | None]:
    if len(specs) != 3:
        raise EvidenceError("E_PILOT_BUILD_DAG", "planned_count must be 3")
    ids = [spec["job_id"] for spec in specs]
    if ids != ["CMAKE_CONFIGURE", "BASELINE_BUILD", "BASELINE_SMOKE"]:
        raise EvidenceError("E_PILOT_BUILD_DAG", "job order differs")
    results: list[dict[str, Any]] = []
    prior_pass = True
    tree_before = None
    evidence = None
    if source_root is not None:
        tree_before = require_frozen_source_tree(source_root)
    if environment is not None and environment["cxx_compiler_path"] is None:
        results.append(make_pre_process_infra_job(specs[0], "MISSING_DEPENDENCY"))
        results.append(make_not_started_job(specs[1]))
        results.append(make_not_started_job(specs[2]))
        return results, None
    for spec in specs:
        if not prior_pass:
            results.append(make_not_started_job(spec))
            continue
        remaining = None
        if outer_deadline is not None:
            remaining = outer_deadline - time.monotonic()
            if remaining <= 0:
                results.append(make_pre_process_infra_job(spec, "OUTER_DEADLINE_EXHAUSTED"))
                prior_pass = False
                continue
        timeout_seconds = spec["timeout_seconds"]
        if remaining is not None:
            timeout_seconds = min(timeout_seconds, max(1, int(remaining)))
        if spec["job_id"] == "BASELINE_SMOKE" and expected_smoke_sha256 is not None:
            executable = Path(spec["argv"][0])
            if (
                not executable.is_file()
                or _sha256_bytes(executable.read_bytes()) != expected_smoke_sha256
            ):
                results.append(make_pre_process_infra_job(spec, "MISSING_DEPENDENCY"))
                prior_pass = False
                continue
        result = execute_job(
            spec,
            env=env,
            log_root=log_root,
            popen=popen,
            timeout_seconds=timeout_seconds,
        )
        if source_root is not None:
            try:
                tree_after = require_frozen_source_tree(source_root)
                if tree_after != tree_before:
                    raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "SOURCE_TREE_DRIFT")
            except EvidenceError:
                overlay = dict(result)
                overlay["terminal_status"] = "FAIL_INFRASTRUCTURE"
                overlay["failure_reason"] = "SOURCE_TREE_DRIFT"
                overlay["infrastructure_phase"] = "POST_PROCESS"
                overlay.pop("artifact_sha256", None)
                result = validate_job_result(_self_hash(overlay))
        if (
            spec["job_id"] == "BASELINE_BUILD"
            and result["terminal_status"] == "PASS"
            and collect_evidence is not None
            and environment is not None
        ):
            try:
                evidence = collect_evidence(FROZEN_BUILD_ROOT, environment)
                expected_smoke_sha256 = evidence["smoke_executable_sha256"]
            except EvidenceError as exc:
                reason = str(exc).split(":", 1)[-1].strip()
                if reason not in INFRA_REASONS_POST_PROCESS:
                    reason = "UNSUPPORTED_TOOLCHAIN"
                overlay = dict(result)
                overlay["terminal_status"] = "FAIL_INFRASTRUCTURE"
                overlay["failure_reason"] = reason
                overlay["infrastructure_phase"] = "POST_PROCESS"
                overlay.pop("artifact_sha256", None)
                result = validate_job_result(_self_hash(overlay))
        results.append(result)
        prior_pass = result["terminal_status"] == "PASS"
    return results, evidence


def _require_authorization() -> str:
    if not os.path.lexists(AUTHORIZATION_PATH):
        raise EvidenceError("E_PILOT_BUILD_AUTH_ABSENT", "authorization is absent")
    raw, digest = read_authority_snapshot(AUTHORIZATION_PATH, "build-preflight-auth")
    if raw != AUTHORIZATION_BYTES or digest != AUTHORIZATION_SHA256:
        raise EvidenceError("E_PILOT_BUILD_AUTH", "authorization bytes differ")
    return digest


def _require_source_preparation_identities() -> None:
    raw, digest = read_authority_snapshot(
        SOURCE_PREPARATION_RESULT_VERDICT_PATH,
        "source-preparation-result-verdict",
    )
    if digest != SOURCE_PREPARATION_RESULT_VERDICT_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "source-preparation verdict hash differs",
        )
    validate_source_preparation_result_verdict(parse_canonical_json_object(raw, "verdict"))
    _manifest_raw, manifest_digest = read_authority_snapshot(
        SOURCE_MANIFEST_PATH, "source-manifest"
    )
    if manifest_digest != SOURCE_MANIFEST_FILE_SHA256:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "source manifest hash differs")
    _result_raw, result_digest = read_authority_snapshot(
        SOURCE_PREPARATION_RESULT_PATH, "source-preparation-result"
    )
    if result_digest != SOURCE_PREPARATION_RESULT_FILE_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_RESULT",
            "source-preparation result hash differs",
        )


def _require_plan_and_implementation_verdicts() -> tuple[str, str, str]:
    plan_raw, plan_digest = read_authority_snapshot(PLAN_PATH, "build-preflight-plan")
    verdict_raw, verdict_digest = read_authority_snapshot(
        PLAN_VERDICT_PATH, "build-preflight-plan-verdict"
    )
    validate_plan_verdict(parse_canonical_json_object(verdict_raw, "plan-verdict"), plan_digest)
    impl_raw, impl_digest = read_authority_snapshot(
        IMPLEMENTATION_VERDICT_PATH, "build-preflight-implementation-verdict"
    )
    impl_verdict = validate_implementation_verdict(
        parse_canonical_json_object(impl_raw, "implementation-verdict"),
        plan_digest,
        verdict_digest,
    )
    verify_reviewed_production_bytes(impl_verdict)
    return plan_digest, verdict_digest, impl_digest


def build_intent(
    environment: dict[str, Any],
    predecessor: list[str],
    implementation_verdict_sha256: str,
) -> dict[str, Any]:
    pid, starttime = producer_identity()
    payload = {
        "schema_version": "p3-pilot-build-preflight-intent-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "plan_class": "PILOT_BUILD_PREFLIGHT_ONLY",
        "p12_item_id": P12_ITEM_ID,
        "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
        "controlled_subject_id": CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
        "build_descriptor_sha256": BUILD_DESCRIPTOR_SHA256,
        "source_preparation_verdict_sha256": SOURCE_PREPARATION_RESULT_VERDICT_SHA256,
        "source_manifest_sha256": SOURCE_MANIFEST_FILE_SHA256,
        "source_preparation_result_sha256": SOURCE_PREPARATION_RESULT_FILE_SHA256,
        "source_preparation_reviewed_commit": SOURCE_PREPARATION_REVIEWED_COMMIT,
        "implementation_verdict_sha256": implementation_verdict_sha256,
        "authorization_sha256": AUTHORIZATION_SHA256,
        "harness_cmake_sha256": HARNESS_CMAKE_SHA256,
        "harness_cxx_sha256": HARNESS_CXX_SHA256,
        "source_root": FROZEN_SOURCE_ROOT.as_posix(),
        "build_root": FROZEN_BUILD_ROOT.as_posix(),
        "harness_root": FROZEN_HARNESS_ROOT.as_posix(),
        "cmake_configure_argv": bind_configure_argv(
            environment["cmake_executable_path"], environment["cxx_compiler_path"]
        ),
        "baseline_build_argv": bind_build_argv(environment["cmake_executable_path"]),
        "baseline_smoke_argv": list(BASELINE_SMOKE_ARGV),
        "cmake_configure_timeout_seconds": CMAKE_CONFIGURE_TIMEOUT_SECONDS,
        "baseline_build_timeout_seconds": BASELINE_BUILD_TIMEOUT_SECONDS,
        "baseline_smoke_timeout_seconds": BASELINE_SMOKE_TIMEOUT_SECONDS,
        "outer_timeout_seconds": OUTER_TIMEOUT_SECONDS,
        "build_parallelism": BUILD_PARALLELISM,
        "planned_count": PLANNED_COUNT,
        "dependency_dag": [list(edge) for edge in DEPENDENCY_DAG],
        "environment_snapshot": environment,
        "environment_snapshot_sha256": environment["artifact_sha256"],
        "producer_pid": pid,
        "producer_starttime": starttime,
        "predecessor_sha256": list(predecessor),
        "no_retry": True,
        "claims": "blocked",
        "formal_denominator_membership": False,
        "rq4_supported": False,
    }
    return validate_intent(_self_hash(payload))


def build_result(
    *,
    intent_sha256: str,
    environment: dict[str, Any],
    jobs: list[dict[str, Any]],
    predecessor: list[str],
    implementation_verdict_sha256: str,
    evidence: dict[str, str] | None,
) -> dict[str, Any]:
    started = [job for job in jobs if job["process_started"] is True]
    not_started = [job for job in jobs if job["terminal_status"] == "NOT_STARTED"]
    first_bad = next((job for job in jobs if job["terminal_status"] != "PASS"), None)
    if first_bad is None:
        terminal_status = "PASS"
        failure_reason = None
        if evidence is None:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "PASS must bind build artifacts")
        cache_sha = evidence["cmake_cache_sha256"]
        commands_sha = evidence["compile_commands_sha256"]
        depfile_sha = evidence["compiler_depfile_sha256"]
        dep_sha = evidence["dependency_list_sha256"]
        smoke_sha = evidence["smoke_executable_sha256"]
    else:
        terminal_status = first_bad["terminal_status"]
        failure_reason = first_bad["failure_reason"]
        cache_sha = None if evidence is None else evidence.get("cmake_cache_sha256")
        commands_sha = None if evidence is None else evidence.get("compile_commands_sha256")
        depfile_sha = None if evidence is None else evidence.get("compiler_depfile_sha256")
        dep_sha = None if evidence is None else evidence.get("dependency_list_sha256")
        smoke_sha = None if evidence is None else evidence.get("smoke_executable_sha256")
    payload = {
        "schema_version": "p3-pilot-build-preflight-result-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "p12_item_id": P12_ITEM_ID,
        "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
        "controlled_subject_id": CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
        "build_descriptor_sha256": BUILD_DESCRIPTOR_SHA256,
        "source_preparation_verdict_sha256": SOURCE_PREPARATION_RESULT_VERDICT_SHA256,
        "source_manifest_sha256": SOURCE_MANIFEST_FILE_SHA256,
        "source_preparation_result_sha256": SOURCE_PREPARATION_RESULT_FILE_SHA256,
        "implementation_verdict_sha256": implementation_verdict_sha256,
        "intent_sha256": intent_sha256,
        "authorization_sha256": AUTHORIZATION_SHA256,
        "environment_snapshot": environment,
        "environment_snapshot_sha256": environment["artifact_sha256"],
        "harness_cmake_sha256": HARNESS_CMAKE_SHA256,
        "harness_cxx_sha256": HARNESS_CXX_SHA256,
        "cmake_cache_sha256": cache_sha,
        "compile_commands_sha256": commands_sha,
        "compiler_depfile_sha256": depfile_sha,
        "dependency_list_sha256": dep_sha,
        "smoke_executable_sha256": smoke_sha,
        "source_root": FROZEN_SOURCE_ROOT.as_posix(),
        "build_root": FROZEN_BUILD_ROOT.as_posix(),
        "harness_root": FROZEN_HARNESS_ROOT.as_posix(),
        "planned_count": PLANNED_COUNT,
        "started_count": len(started),
        "terminal_count": len(jobs),
        "not_started_count": len(not_started),
        "jobs": jobs,
        "terminal_status": terminal_status,
        "failure_reason": failure_reason,
        "build_root_exists": os.path.lexists(FROZEN_BUILD_ROOT),
        "build_root_is_symlink": os.path.islink(FROZEN_BUILD_ROOT),
        "no_retry": True,
        "claims": "blocked",
        "formal_denominator_membership": False,
        "rq4_supported": False,
        "predecessor_sha256": list(predecessor),
    }
    return validate_result(_self_hash(payload))


def _write_terminal_result(
    *,
    intent_sha256: str,
    environment: dict[str, Any],
    jobs: list[dict[str, Any]],
    predecessor: list[str],
    implementation_verdict_sha256: str,
    evidence: dict[str, str] | None,
) -> dict[str, Any]:
    if os.path.lexists(RESULT_PATH):
        raise EvidenceError("E_PILOT_BUILD_PREEXISTING", "result already exists")
    result = build_result(
        intent_sha256=intent_sha256,
        environment=environment,
        jobs=jobs,
        predecessor=predecessor,
        implementation_verdict_sha256=implementation_verdict_sha256,
        evidence=evidence,
    )
    write_canonical_json(RESULT_PATH, result, exclusive=True)
    return result


def run_build_preflight(source_root: Path, build_root: Path) -> dict[str, Any]:
    if source_root != FROZEN_SOURCE_ROOT or build_root != FROZEN_BUILD_ROOT:
        raise EvidenceError("E_PILOT_BUILD_PATH", "CLI paths must equal frozen paths")
    intent_exists = os.path.lexists(INTENT_PATH)
    result_exists = os.path.lexists(RESULT_PATH)
    intent_obj = None
    result_obj = None
    intent_digest = None
    intent_valid = False
    result_valid = False
    producer_live = False
    child_live = False
    pair_valid = False
    start_marker_present = False
    identity_resolved = True
    if intent_exists:
        try:
            raw, intent_digest = read_authority_snapshot(INTENT_PATH, "existing-intent")
            intent_obj = validate_intent(parse_canonical_json_object(raw, "existing-intent"))
            intent_valid = True
            producer_live = attempt_is_live(
                intent_obj["producer_pid"],
                intent_obj["producer_starttime"],
            )
            log_root = FROZEN_BUILD_ROOT / "logs"
            start_markers = load_job_start_markers(log_root)
            identities = load_process_identities(log_root)
            start_marker_present = bool(start_markers)
            child_live = child_records_are_live(identities)
            identity_by_job = {item.get("job_id"): item for item in identities}
            identity_resolved = True
            if start_markers:
                identity_resolved = all(
                    marker.get("job_id") in identity_by_job for marker in start_markers
                )
        except EvidenceError:
            intent_valid = False
    if result_exists:
        try:
            raw, _digest = read_authority_snapshot(RESULT_PATH, "existing-result")
            result_obj = validate_result(parse_canonical_json_object(raw, "existing-result"))
            result_valid = True
        except EvidenceError:
            result_valid = False
    if intent_valid and result_valid and intent_obj is not None and result_obj is not None:
        try:
            validate_attempt_pair(intent_obj, intent_digest or "", result_obj)
            pair_valid = True
        except EvidenceError:
            pair_valid = False
    state = classify_reconciliation(
        intent_present=intent_exists,
        result_present=result_exists,
        intent_valid=intent_valid,
        result_valid=result_valid,
        producer_live=producer_live,
        child_live=child_live,
        pair_valid=pair_valid,
        start_marker_present=start_marker_present,
        identity_resolved=identity_resolved,
    )
    if state == "RESULT_TERMINAL":
        raise EvidenceError("E_PILOT_BUILD_PREEXISTING", "result already exists")
    if state in {"INTENT_PRODUCER_LIVE", "INTENT_CHILD_LIVE"}:
        raise EvidenceError("E_PILOT_BUILD_PREEXISTING", "original attempt is still live")
    if state == "INTENT_CHILD_STATE_UNRESOLVED":
        raise EvidenceError("E_PILOT_BUILD_PREEXISTING", "child start state is unresolved")
    if state == "RESULT_WITHOUT_INTENT" or state == "INVALID_DURABLE":
        raise EvidenceError("E_PILOT_BUILD_PREEXISTING", "durable objects are inconsistent")
    if state == "INTENT_ONLY_ORPHAN":
        environment = intent_obj["environment_snapshot"]
        specs = bind_job_specs(environment)
        jobs = [
            make_pre_process_infra_job(specs[0], "ORPHANED_INTENT_NO_PROCESS"),
            make_not_started_job(specs[1]),
            make_not_started_job(specs[2]),
        ]
        return _write_terminal_result(
            intent_sha256=_sha256_bytes(INTENT_PATH.read_bytes()),
            environment=environment,
            jobs=jobs,
            predecessor=sorted(
                [_sha256_bytes(INTENT_PATH.read_bytes()), *intent_obj["predecessor_sha256"]]
            ),
            implementation_verdict_sha256=intent_obj["implementation_verdict_sha256"],
            evidence=None,
        )
    require_absent_path(FROZEN_BUILD_ROOT, "build-root")
    require_absent_path(FROZEN_HARNESS_ROOT, "harness-root")
    env = dict(os.environ)
    reject_system_boost_environment(env)
    env.update(DISCONNECTED_ENVIRONMENT)
    _require_authorization()
    _require_source_preparation_identities()
    plan_digest, verdict_digest, impl_digest = _require_plan_and_implementation_verdicts()
    require_frozen_source_tree(FROZEN_SOURCE_ROOT)
    environment = make_environment_snapshot()
    reject_unbound_toolchain(env, environment["cxx_compiler_path"])
    specs = bind_job_specs(environment)
    predecessor = sorted(
        [
            plan_digest,
            verdict_digest,
            impl_digest,
            SOURCE_PREPARATION_RESULT_VERDICT_SHA256,
            SOURCE_MANIFEST_FILE_SHA256,
            SOURCE_PREPARATION_RESULT_FILE_SHA256,
            AUTHORIZATION_SHA256,
            environment["artifact_sha256"],
        ]
    )
    intent = build_intent(environment, predecessor, impl_digest)
    write_canonical_json(INTENT_PATH, intent, exclusive=True)
    intent_sha256 = _sha256_bytes(INTENT_PATH.read_bytes())
    outer_deadline = time.monotonic() + OUTER_TIMEOUT_SECONDS
    jobs = [make_not_started_job(spec) for spec in specs]
    evidence = None
    try:
        write_harness(FROZEN_HARNESS_ROOT, HARNESS_CMAKE_BYTES, HARNESS_CXX_BYTES)
        os.mkdir(FROZEN_BUILD_ROOT)
        ensure_safe_log_root(FROZEN_BUILD_ROOT / "logs")
        jobs, evidence = run_three_jobs(
            specs,
            env=env,
            log_root=FROZEN_BUILD_ROOT / "logs",
            source_root=FROZEN_SOURCE_ROOT,
            environment=environment,
            outer_deadline=outer_deadline,
            expected_smoke_sha256=None,
            collect_evidence=collect_baseline_build_evidence,
        )
    except EvidenceError as exc:
        detail = str(exc)
        reason = "RESULT_PUBLICATION_FAILURE"
        if "SOURCE_TREE" in detail or "SOURCE_TREE_DRIFT" in detail:
            reason = "SOURCE_TREE_DRIFT"
        elif "HARNESS" in detail:
            reason = "HARNESS_PUBLICATION_FAILURE"
        elif "LOG_PUBLICATION" in detail:
            reason = "LOG_PUBLICATION_FAILURE"
        elif "SYSTEM_BOOST" in detail:
            reason = "SYSTEM_BOOST_FALLBACK"
        while len(jobs) < 3:
            jobs.append(make_not_started_job(specs[len(jobs)]))
        if all(job["terminal_status"] == "NOT_STARTED" for job in jobs):
            jobs = [
                make_pre_process_infra_job(specs[0], reason),
                make_not_started_job(specs[1]),
                make_not_started_job(specs[2]),
            ]
        return _write_terminal_result(
            intent_sha256=intent_sha256,
            environment=environment,
            jobs=jobs,
            predecessor=sorted([intent_sha256, *predecessor]),
            implementation_verdict_sha256=impl_digest,
            evidence=evidence,
        )
    except Exception:
        jobs = [
            make_pre_process_infra_job(specs[0], "RESULT_PUBLICATION_FAILURE"),
            make_not_started_job(specs[1]),
            make_not_started_job(specs[2]),
        ]
        return _write_terminal_result(
            intent_sha256=intent_sha256,
            environment=environment,
            jobs=jobs,
            predecessor=sorted([intent_sha256, *predecessor]),
            implementation_verdict_sha256=impl_digest,
            evidence=None,
        )
    return _write_terminal_result(
        intent_sha256=intent_sha256,
        environment=environment,
        jobs=jobs,
        predecessor=sorted([intent_sha256, *predecessor]),
        implementation_verdict_sha256=impl_digest,
        evidence=evidence,
    )


def _validate_attempt2_common(value: object, schema: str, context: str,
                              exact: dict[str, object]) -> dict[str, Any]:
    validated = validate_exact_object(value, exact, context)
    if (validated.get("schema_version") != schema
            or validated.get("execution_class") != "PILOT_ONLY"
            or validated.get("denominator") != "PILOT_ONLY"
            or validated.get("claims") != "blocked"
            or validated.get("no_retry") is not True
            or validated.get("formal_denominator_membership") is not False
            or validated.get("rq4_supported") is not False
            or validated.get("attempt_2_authorized") is not False):
        raise EvidenceError(context, "identity or claim ceiling differs")
    digest = validated.get("artifact_sha256")
    if digest != canonical_sha256({k: v for k, v in validated.items() if k != "artifact_sha256"}):
        raise EvidenceError(context, "self-hash differs")
    return validated


def _require_attempt2_bindings(value: dict[str, Any], context: str) -> None:
    fixed = {
        "p12_item_id": P12_ITEM_ID, "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
        "controlled_subject_id": CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
        "build_descriptor_sha256": BUILD_DESCRIPTOR_SHA256,
        "source_preparation_verdict_sha256": SOURCE_PREPARATION_RESULT_VERDICT_SHA256,
        "source_manifest_sha256": SOURCE_MANIFEST_FILE_SHA256,
        "source_preparation_result_sha256": SOURCE_PREPARATION_RESULT_FILE_SHA256,
        "harness_cmake_sha256": HARNESS_CMAKE_SHA256, "harness_cxx_sha256": HARNESS_CXX_SHA256,
        "source_root": str(ATTEMPT2_SOURCE_ROOT), "build_root": str(ATTEMPT2_BUILD_ROOT),
        "harness_root": str(ATTEMPT2_HARNESS_ROOT), "log_root": str(ATTEMPT2_LOG_ROOT),
        "archive_path": str(ATTEMPT2_ARCHIVE_PATH), "qualification_base_head": QUALIFICATION_BASE_HEAD,
        "verification_scope": "ARTIFACT_HASH_AND_HOST_SNAPSHOT",
        "executor_cloud_run_id": None, "executor_build_snapshot_id": None,
    }
    if any(value.get(k) != expected for k, expected in fixed.items()):
        raise EvidenceError(context, "frozen binding differs")
    for key in ("attempt1_implementation_verdict_sha256", "attempt2_implementation_verdict_sha256",
                "authorization_sha256", "qualification_evidence_sha256"):
        validate_sha256(value[key], key)


def _require_predecessors(value: dict[str, Any], required: list[str], context: str) -> None:
    predecessor = value["predecessor_sha256"]
    if (type(predecessor) is not list or predecessor != sorted(predecessor)
            or len(predecessor) != len(set(predecessor))):
        raise EvidenceError(context, "predecessors must be sorted and unique")
    for digest in predecessor:
        validate_sha256(digest, "predecessor_sha256")
    if not set(required).issubset(predecessor):
        raise EvidenceError(context, "direct predecessor missing")


def validate_attempt2_intent(value: object) -> dict[str, Any]:
    validated = _validate_attempt2_common(value, ATTEMPT2_INTENT_SCHEMA,
                                          "E_PILOT_ATTEMPT2_INTENT", ATTEMPT2_INTENT_EXACT)
    environment = validate_attempt2_environment(validated["environment_snapshot"])
    if validated["environment_snapshot_sha256"] != environment["artifact_sha256"]:
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "environment binding differs")
    _require_attempt2_bindings(validated, "E_PILOT_ATTEMPT2_INTENT")
    descriptors = attempt2_phase_descriptors(environment["cmake_executable_path"])
    expected = {
        "plan_class": "PILOT_BUILD_PREFLIGHT_ATTEMPT_2_ONLY", "planned_count": 5,
        "phase_order": [d["phase_id"] for d in descriptors],
        "dependency_dag": [d["dependency_phase_ids"] for d in descriptors],
        "cmake_metadata_argv": descriptors[0]["argv"], "cmake_configure_argv": descriptors[2]["argv"],
        "baseline_build_argv": descriptors[3]["argv"], "baseline_smoke_argv": descriptors[4]["argv"],
        "cmake_version_timeout_seconds": 10, "cmake_configure_timeout_seconds": 900,
        "baseline_build_timeout_seconds": 3600, "baseline_smoke_timeout_seconds": 1800,
        "outer_timeout_seconds": 7200, "build_parallelism": 4,
        "source_preparation_reviewed_commit": SOURCE_PREPARATION_REVIEWED_COMMIT,
    }
    if any(validated[k] != expected for k, expected in expected.items()):
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "intent plan differs")
    if (environment["cmake_version"] is not None or type(validated["producer_pid"]) is not int
            or validated["producer_pid"] <= 0 or not validated["producer_starttime"]):
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "producer or metadata state differs")
    required = [validated[k] for k in ("attempt1_implementation_verdict_sha256",
        "attempt2_implementation_verdict_sha256", "authorization_sha256",
        "qualification_evidence_sha256", "source_preparation_verdict_sha256",
        "source_manifest_sha256", "source_preparation_result_sha256", "environment_snapshot_sha256")]
    _require_predecessors(validated, required, "E_PILOT_ATTEMPT2_INTENT")
    return validated


def validate_attempt2_result(value: object) -> dict[str, Any]:
    validated = _validate_attempt2_common(value, ATTEMPT2_RESULT_SCHEMA,
                                          "E_PILOT_ATTEMPT2_RESULT", ATTEMPT2_RESULT_EXACT)
    environment = validate_attempt2_environment(validated["environment_snapshot"])
    if validated["environment_snapshot_sha256"] != environment["artifact_sha256"]:
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "environment binding differs")
    _require_attempt2_bindings(validated, "E_PILOT_ATTEMPT2_RESULT")
    validate_sha256(validated["intent_sha256"], "intent_sha256")
    phases = validated.get("phases")
    if not isinstance(phases, list) or len(phases) != 5:
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "five phases required")
    checked = [validate_attempt2_phase_result(phase) for phase in phases]
    descriptors = attempt2_phase_descriptors(environment["cmake_executable_path"])
    if (validated["planned_count"] != 5 or validated["phase_order"] != [d["phase_id"] for d in descriptors]
            or any(any(p[k] != d[k] for k in ("phase_id", "phase_kind", "dependency_phase_ids",
                                               "argv", "timeout_seconds"))
                   for p, d in zip(checked, descriptors, strict=True))):
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "phase order differs")
    if validated["started_count"] != sum(p["process_started"] for p in checked):
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "started count differs")
    if validated["terminal_count"] != sum(p["terminal_status"] != "NOT_STARTED" for p in checked):
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "terminal count differs")
    if validated["not_started_count"] != sum(p["terminal_status"] == "NOT_STARTED" for p in checked):
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "not-started count differs")
    failed = False
    for phase in checked:
        if failed and phase["terminal_status"] != "NOT_STARTED":
            raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "phase after failure was started")
        if phase["terminal_status"] == "NOT_STARTED" and not failed:
            raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "NOT_STARTED requires a prior real terminal failure")
        failed |= phase["terminal_status"] in {"FAIL", "TIMEOUT", "FAIL_INFRASTRUCTURE"}
    first = next((p for p in checked if p["terminal_status"] != "PASS"), None)
    aggregate_status = "PASS" if first is None else first["terminal_status"]
    aggregate_failure = None if first is None else first["failure_reason"]
    if validated["terminal_status"] != aggregate_status or validated["failure_reason"] != aggregate_failure:
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "aggregate differs")
    source = checked[1]
    disposition = (None if source["terminal_status"] == "NOT_STARTED" else
                   source["source_restoration_evidence"]["disposition"])
    if validated["source_restoration_disposition"] != disposition:
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "restoration disposition differs")
    evidence_requirements = (("cmake_cache_sha256", 2), ("compile_commands_sha256", 2),
                             ("compiler_depfile_sha256", 3), ("dependency_list_sha256", 3),
                             ("smoke_executable_sha256", 3))
    for key, index in evidence_requirements:
        digest = validated[key]
        if digest is not None:
            validate_sha256(digest, key)
        if (checked[index]["terminal_status"] == "PASS") != (digest is not None):
            raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "build evidence reach differs")
    absent_root_before_process = (
        checked[0]["terminal_status"] == "FAIL_INFRASTRUCTURE"
        and checked[0]["infrastructure_phase"] == "PRE_PROCESS"
        and checked[0]["process_started"] is False
        and all(p["terminal_status"] == "NOT_STARTED" for p in checked[1:])
    )
    if (validated["build_root_is_symlink"] is not False
            or validated["build_root_exists"] is False and not absent_root_before_process):
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "unsafe build root")
    metadata_passed = checked[0]["terminal_status"] == "PASS"
    cmake_version = environment["cmake_version"]
    if (metadata_passed and (type(cmake_version) is not str or not cmake_version)
            or not metadata_passed and cmake_version is not None):
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "CMake version does not match metadata reach")
    required = [validated[k] for k in ("intent_sha256", "attempt1_implementation_verdict_sha256",
        "attempt2_implementation_verdict_sha256", "authorization_sha256",
        "qualification_evidence_sha256", "source_preparation_verdict_sha256",
        "source_manifest_sha256", "source_preparation_result_sha256", "environment_snapshot_sha256")]
    _require_predecessors(validated, required, "E_PILOT_ATTEMPT2_RESULT")
    return validated


def run_build_preflight_attempt_2(
    archive: Path, source_root: Path, build_root: Path,
) -> dict[str, Any]:
    """Execute the frozen one-shot Attempt-2 adapter; durable preexistence is final."""
    if (Path(archive), Path(source_root), Path(build_root)) != (
            ATTEMPT2_ARCHIVE_PATH, ATTEMPT2_SOURCE_ROOT, ATTEMPT2_BUILD_ROOT):
        raise EvidenceError("E_PILOT_ATTEMPT2_PATH", "CLI paths must equal frozen paths")
    if os.path.lexists(ATTEMPT2_INTENT_PATH) or os.path.lexists(ATTEMPT2_RESULT_PATH):
        raise EvidenceError("E_PILOT_ATTEMPT2_PREEXISTING", "intent or result already exists")
    for path in (ATTEMPT2_BUILD_ROOT, ATTEMPT2_HARNESS_ROOT):
        require_absent_path(path, "attempt2-runtime-root")
    auth, auth_digest = read_authority_snapshot(ATTEMPT2_AUTHORIZATION_PATH, "attempt2-auth")
    if auth != ATTEMPT2_AUTHORIZATION_BYTES or auth_digest != ATTEMPT2_AUTHORIZATION_SHA256:
        raise EvidenceError("E_PILOT_ATTEMPT2_AUTH", "authorization bytes differ")
    qualification = read_v5_qualification_evidence()
    cmake_path = resolve_cmake_executable_path()
    env = dict(os.environ)
    reject_system_boost_environment(env)
    env.update(DISCONNECTED_ENVIRONMENT)
    reject_unbound_toolchain(env, FROZEN_CXX_PATH)
    descriptors = attempt2_phase_descriptors(cmake_path)
    pid, starttime = producer_identity()
    intent = {"schema_version": ATTEMPT2_INTENT_SCHEMA, "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY", "plan_class": "PILOT_BUILD_PREFLIGHT_ATTEMPT_2_ONLY",
        "archive_path": archive.as_posix(), "source_root": source_root.as_posix(),
        "build_root": build_root.as_posix(), "harness_root": ATTEMPT2_HARNESS_ROOT.as_posix(),
        "log_root": ATTEMPT2_LOG_ROOT.as_posix(), "planned_count": 5,
        "phase_order": [item["phase_id"] for item in descriptors],
        "dependency_dag": [item["dependency_phase_ids"] for item in descriptors],
        "qualification_evidence_sha256": qualification["artifact_sha256"],
        "authorization_sha256": auth_digest, "producer_pid": pid,
        "producer_starttime": starttime, "no_retry": True, "claims": "blocked",
        "formal_denominator_membership": False, "rq4_supported": False,
        "attempt_2_authorized": False}
    intent["artifact_sha256"] = canonical_sha256(intent)
    validate_attempt2_intent(intent)
    write_canonical_json(ATTEMPT2_INTENT_PATH, intent, exclusive=True)
    # Runtime publication begins only after the durable intent.
    os.mkdir(ATTEMPT2_BUILD_ROOT)
    ensure_safe_log_root(ATTEMPT2_LOG_ROOT)
    from p3_v3.pilot_source import run_restore_production_source
    phases: list[dict[str, Any]] = []
    prior_pass = True
    for descriptor in descriptors:
        if not prior_pass:
            phases.append(make_attempt2_not_started(descriptor))
            continue
        if descriptor["phase_id"] == "SOURCE_RESTORE":
            restoration = run_restore_production_source(archive, source_root)
            phase = make_attempt2_not_started(descriptor)
            phase.update({"terminal_status": "PASS", "source_restoration_evidence": restoration})
            phase["artifact_sha256"] = canonical_sha256({k: v for k, v in phase.items() if k != "artifact_sha256"})
            phase = validate_attempt2_phase_result(phase)
        else:
            spec = {"job_id": descriptor["phase_id"], "job_kind": descriptor["phase_kind"],
                "dependency_job_ids": descriptor["dependency_phase_ids"], "argv": descriptor["argv"],
                "timeout_seconds": descriptor["timeout_seconds"]}
            job = execute_job(spec, env=env, log_root=ATTEMPT2_LOG_ROOT)
            phase = {("phase_id" if k == "job_id" else "phase_kind" if k == "job_kind"
                      else "dependency_phase_ids" if k == "dependency_job_ids" else k): v
                     for k, v in job.items()}
            phase["schema_version"] = ATTEMPT2_PHASE_SCHEMA
            phase["source_restoration_evidence"] = None
            phase["artifact_sha256"] = canonical_sha256({k: v for k, v in phase.items() if k != "artifact_sha256"})
            phase = validate_attempt2_phase_result(phase)
        phases.append(phase)
        prior_pass = phase["terminal_status"] == "PASS"
    result = {"schema_version": ATTEMPT2_RESULT_SCHEMA, "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY", "phases": phases, "planned_count": 5,
        "started_count": sum(p["process_started"] for p in phases), "terminal_count": 5,
        "not_started_count": sum(p["terminal_status"] == "NOT_STARTED" for p in phases),
        "terminal_status": next((p["terminal_status"] for p in phases if p["terminal_status"] != "PASS"), "PASS"),
        "no_retry": True, "claims": "blocked", "formal_denominator_membership": False,
        "rq4_supported": False, "attempt_2_authorized": False}
    result["artifact_sha256"] = canonical_sha256(result)
    validate_attempt2_result(result)
    write_canonical_json(ATTEMPT2_RESULT_PATH, result, exclusive=True)
    return result
