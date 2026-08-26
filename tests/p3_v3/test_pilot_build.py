from __future__ import annotations

import hashlib
import json
import os
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.pilot import reject_confirmatory_pilot


REQUIRED_BUILD_PREFLIGHT_TESTS = [
    "test_missing_source_preparation_pass_verdict",
    "test_source_manifest_hash_drift",
    "test_source_preparation_result_hash_drift",
    "test_source_tree_drift",
    "test_authorization_missing",
    "test_authorization_wrong_bytes",
    "test_preexisting_build_root",
    "test_preexisting_harness_root",
    "test_symlink_path_rejection",
    "test_exact_three_job_dag",
    "test_configure_failure_prevents_build_and_smoke",
    "test_build_failure_prevents_smoke",
    "test_configure_timeout",
    "test_build_timeout",
    "test_smoke_timeout",
    "test_stdout_stderr_hash_and_byte_counts",
    "test_no_shell_execution",
    "test_no_retry_on_existing_intent",
    "test_no_network_download_contract",
    "test_no_system_boost_fallback",
    "test_cuda_absence_is_non_blocking",
    "test_confirmatory_schema_leakage_rejection",
    "test_claims_denominator_rq4_invariants",
    "test_implementation_verdict_reviewed_path_commit_hash_drift",
    "test_implementation_verdict_sha_enters_intent_result_predecessor",
    "test_reviewed_production_bytes_runtime_drift",
    "test_durable_environment_snapshot_round_trip",
    "test_missing_compiler_exact_infrastructure_result",
    "test_terminal_status_exact_matrix",
    "test_result_count_conservation_and_aggregate",
    "test_configure_build_dependency_blocking",
    "test_process_group_timeout_terminates_descendants",
    "test_exception_after_intent_produces_terminal_result",
    "test_orphaned_intent_reconciliation_writes_no_new_process",
    "test_second_invocation_never_reruns",
    "test_source_drift_after_child_yields_terminal_failure",
    "test_system_boost_dependency_path_rejection",
    "test_frozen_source_dependency_closure_pass",
    "test_build_artifact_hashes_bound",
    "test_smoke_refuses_executable_hash_drift",
    "test_collect_baseline_build_evidence_pass",
    "test_collect_baseline_build_evidence_missing_frozen_include",
    "test_compile_commands_compiler_mismatch",
    "test_cmakecache_compiler_generator_root_drift",
    "test_system_boost_in_actual_depfile",
    "test_depfile_raw_and_canonical_hashes_enter_result",
    "test_configure_build_use_resolved_toolchain_argv",
    "test_producer_dead_child_live_not_orphan_terminal",
    "test_post_popen_exception_reaps_process_group",
    "test_outer_deadline_exhausted_not_missing_dependency",
    "test_validate_attempt_pair_rejects_drift",
    "test_mismatched_intent_result_is_not_result_terminal",
    "test_start_marker_exists_before_popen",
    "test_identity_publication_returns_started_job",
    "test_log_publication_returns_started_job",
    "test_normal_pass_does_not_call_killpg",
    "test_process_group_leak_is_detected_and_cleaned",
    "test_start_marker_without_identity_is_unresolved",
    "test_orphan_requires_no_start_marker",
    "test_started_post_process_failure_count_conservation",
    "test_timeout_retry_communicate_uses_final_cumulative_output_once",
    "test_timeout_falls_back_to_partial_output_when_final_collection_fails",
    "test_log_cleanup_does_not_duplicate_cumulative_stdio",
    "test_process_group_leak_cleanup_does_not_duplicate_cumulative_stdio",
]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _minimal_environment(pilot_build):
    environment = {
        "schema_version": "p3-pilot-build-preflight-environment-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "cmake_executable": "cmake",
        "cmake_executable_path": "/usr/bin/cmake",
        "cmake_version": "cmake version 3.28.0",
        "cxx_compiler_executable": "c++",
        "cxx_compiler_path": "/usr/bin/c++",
        "cxx_compiler_identity": "c++ (Debian)",
        "cxx_compiler_version": "c++ (Debian)",
        "cmake_generator": "Unix Makefiles",
        "os_name": "Linux",
        "os_release": "6.12.0",
        "python_version": "3.11.0",
        "git_version": "git version 2.43.0",
        "build_parallelism": 4,
        "nvcc_present": False,
        "native_profiling_present": False,
        "cuda_absence_blocking": False,
        "fetchcontent_fully_disconnected": True,
        "system_boost_fallback_accepted": False,
        "disconnected_environment": dict(pilot_build.DISCONNECTED_ENVIRONMENT),
        "claims": "blocked",
    }
    return pilot_build.validate_environment_snapshot(pilot_build._self_hash(environment))


def _synthetic_specs(tmp_path: Path, configure, build, smoke, timeouts=None):
    timeouts = timeouts or (900, 3600, 1800)
    return (
        {
            "job_id": "CMAKE_CONFIGURE",
            "job_kind": "CMAKE_CONFIGURE",
            "dependency_job_ids": [],
            "argv": list(configure),
            "timeout_seconds": timeouts[0],
        },
        {
            "job_id": "BASELINE_BUILD",
            "job_kind": "BASELINE_BUILD",
            "dependency_job_ids": ["CMAKE_CONFIGURE"],
            "argv": list(build),
            "timeout_seconds": timeouts[1],
        },
        {
            "job_id": "BASELINE_SMOKE",
            "job_kind": "BASELINE_SMOKE",
            "dependency_job_ids": ["BASELINE_BUILD"],
            "argv": list(smoke),
            "timeout_seconds": timeouts[2],
        },
    )


def test_required_build_preflight_names_are_frozen():
    assert REQUIRED_BUILD_PREFLIGHT_TESTS == [
        "test_missing_source_preparation_pass_verdict",
        "test_source_manifest_hash_drift",
        "test_source_preparation_result_hash_drift",
        "test_source_tree_drift",
        "test_authorization_missing",
        "test_authorization_wrong_bytes",
        "test_preexisting_build_root",
        "test_preexisting_harness_root",
        "test_symlink_path_rejection",
        "test_exact_three_job_dag",
        "test_configure_failure_prevents_build_and_smoke",
        "test_build_failure_prevents_smoke",
        "test_configure_timeout",
        "test_build_timeout",
        "test_smoke_timeout",
        "test_stdout_stderr_hash_and_byte_counts",
        "test_no_shell_execution",
        "test_no_retry_on_existing_intent",
        "test_no_network_download_contract",
        "test_no_system_boost_fallback",
        "test_cuda_absence_is_non_blocking",
        "test_confirmatory_schema_leakage_rejection",
        "test_claims_denominator_rq4_invariants",
        "test_implementation_verdict_reviewed_path_commit_hash_drift",
        "test_implementation_verdict_sha_enters_intent_result_predecessor",
        "test_reviewed_production_bytes_runtime_drift",
        "test_durable_environment_snapshot_round_trip",
        "test_missing_compiler_exact_infrastructure_result",
        "test_terminal_status_exact_matrix",
        "test_result_count_conservation_and_aggregate",
        "test_configure_build_dependency_blocking",
        "test_process_group_timeout_terminates_descendants",
        "test_exception_after_intent_produces_terminal_result",
        "test_orphaned_intent_reconciliation_writes_no_new_process",
        "test_second_invocation_never_reruns",
        "test_source_drift_after_child_yields_terminal_failure",
        "test_system_boost_dependency_path_rejection",
        "test_frozen_source_dependency_closure_pass",
        "test_build_artifact_hashes_bound",
        "test_smoke_refuses_executable_hash_drift",
        "test_collect_baseline_build_evidence_pass",
        "test_collect_baseline_build_evidence_missing_frozen_include",
        "test_compile_commands_compiler_mismatch",
        "test_cmakecache_compiler_generator_root_drift",
        "test_system_boost_in_actual_depfile",
        "test_depfile_raw_and_canonical_hashes_enter_result",
        "test_configure_build_use_resolved_toolchain_argv",
        "test_producer_dead_child_live_not_orphan_terminal",
        "test_post_popen_exception_reaps_process_group",
        "test_outer_deadline_exhausted_not_missing_dependency",
        "test_validate_attempt_pair_rejects_drift",
        "test_mismatched_intent_result_is_not_result_terminal",
        "test_start_marker_exists_before_popen",
        "test_identity_publication_returns_started_job",
        "test_log_publication_returns_started_job",
        "test_normal_pass_does_not_call_killpg",
        "test_process_group_leak_is_detected_and_cleaned",
        "test_start_marker_without_identity_is_unresolved",
        "test_orphan_requires_no_start_marker",
        "test_started_post_process_failure_count_conservation",
        "test_timeout_retry_communicate_uses_final_cumulative_output_once",
        "test_timeout_falls_back_to_partial_output_when_final_collection_fails",
        "test_log_cleanup_does_not_duplicate_cumulative_stdio",
        "test_process_group_leak_cleanup_does_not_duplicate_cumulative_stdio",
    ]


def test_missing_source_preparation_pass_verdict(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    monkeypatch.setattr(
        pilot_build,
        "SOURCE_PREPARATION_RESULT_VERDICT_PATH",
        tmp_path / "missing-source-prep-verdict.md",
    )
    monkeypatch.setattr(pilot_build, "INTENT_PATH", tmp_path / "intent.json")
    monkeypatch.setattr(pilot_build, "RESULT_PATH", tmp_path / "result.json")
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", tmp_path / "source")
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", tmp_path / "build")
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", tmp_path / "harness")
    monkeypatch.setattr(
        pilot_build,
        "AUTHORIZATION_PATH",
        tmp_path / "user-auth-build-preflight.txt",
    )
    (tmp_path / "user-auth-build-preflight.txt").write_bytes(
        pilot_build.AUTHORIZATION_BYTES
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT|E_PILOT_BUILD_IDENTITY"
    ):
        pilot_build._require_source_preparation_identities()
    assert not (tmp_path / "intent.json").exists()
    assert not (tmp_path / "result.json").exists()


def test_source_manifest_hash_drift(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    verdict = tmp_path / "source-prep-verdict.md"
    verdict.write_bytes(
        Path(
            "docs/review_20260817/"
            "boost_math_pilot_source_preparation_result_sol_high_review.md"
        ).read_bytes()
    )
    monkeypatch.setattr(
        pilot_build, "SOURCE_PREPARATION_RESULT_VERDICT_PATH", verdict
    )
    drifted = tmp_path / "source-manifest.json"
    drifted.write_bytes(b'{"drift":true}\n')
    monkeypatch.setattr(pilot_build, "SOURCE_MANIFEST_PATH", drifted)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_MANIFEST"):
        pilot_build._require_source_preparation_identities()


def test_source_preparation_result_hash_drift(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    verdict = tmp_path / "source-prep-verdict.md"
    verdict.write_bytes(
        Path(
            "docs/review_20260817/"
            "boost_math_pilot_source_preparation_result_sol_high_review.md"
        ).read_bytes()
    )
    monkeypatch.setattr(
        pilot_build, "SOURCE_PREPARATION_RESULT_VERDICT_PATH", verdict
    )
    monkeypatch.setattr(
        pilot_build,
        "SOURCE_MANIFEST_PATH",
        Path("data/p3_v3/pilot/boost_math/source-manifest.json"),
    )
    drifted = tmp_path / "source-preparation-result.json"
    drifted.write_bytes(b'{"drift":true}\n')
    monkeypatch.setattr(pilot_build, "SOURCE_PREPARATION_RESULT_PATH", drifted)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_RESULT"):
        pilot_build._require_source_preparation_identities()


def test_source_tree_drift(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    fake = tmp_path / "source"
    fake.mkdir()
    (fake / "only.txt").write_text("not the frozen tree\n", encoding="utf-8")
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", fake)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_TREE_MISMATCH"):
        pilot_build.require_frozen_source_tree(fake)


def test_authorization_missing(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    monkeypatch.setattr(
        pilot_build,
        "AUTHORIZATION_PATH",
        tmp_path / "user-auth-build-preflight.txt",
    )
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_AUTH_ABSENT"):
        pilot_build._require_authorization()


def test_authorization_wrong_bytes(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    path = tmp_path / "user-auth-build-preflight.txt"
    path.write_bytes(b"AUTHORIZE_BOOSTMATH_PILOT_PREPARATION\n")
    monkeypatch.setattr(pilot_build, "AUTHORIZATION_PATH", path)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_AUTH"):
        pilot_build._require_authorization()


def test_preexisting_build_root(tmp_path):
    import p3_v3.pilot_build as pilot_build

    root = tmp_path / "build"
    root.mkdir()
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PREEXISTING"):
        pilot_build.require_absent_path(root, "build-root")


def test_preexisting_harness_root(tmp_path):
    import p3_v3.pilot_build as pilot_build

    root = tmp_path / "harness"
    root.mkdir()
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PREEXISTING"):
        pilot_build.require_absent_path(root, "harness-root")


def test_symlink_path_rejection(tmp_path):
    import p3_v3.pilot_build as pilot_build

    real = tmp_path / "real"
    link = tmp_path / "link"
    real.mkdir()
    link.symlink_to(real)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_SYMLINK"):
        pilot_build.require_safe_directory(link, link, "source-root")


def test_exact_three_job_dag(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert [item["job_id"] for item in results] == [
        "CMAKE_CONFIGURE",
        "BASELINE_BUILD",
        "BASELINE_SMOKE",
    ]
    assert [item["terminal_status"] for item in results] == ["PASS", "PASS", "PASS"]
    assert all(item["claims"] == "blocked" for item in results)


def test_configure_failure_prevents_build_and_smoke(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "raise SystemExit(2)"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert results[0]["terminal_status"] == "FAIL"
    assert results[1]["terminal_status"] == "NOT_STARTED"
    assert results[2]["terminal_status"] == "NOT_STARTED"
    assert results[1]["failure_reason"] == "DEPENDENCY_NOT_STARTED"
    assert results[2]["failure_reason"] == "DEPENDENCY_NOT_STARTED"
    assert results[1]["exit_code"] is None
    assert results[1]["stdout_sha256"] is None


def test_build_failure_prevents_smoke(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "raise SystemExit(3)"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert results[0]["terminal_status"] == "PASS"
    assert results[1]["terminal_status"] == "FAIL"
    assert results[2]["terminal_status"] == "NOT_STARTED"
    assert results[2]["failure_reason"] == "DEPENDENCY_NOT_STARTED"


def test_configure_timeout(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "import time; time.sleep(3)"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
        timeouts=(1, 3600, 1800),
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert results[0]["terminal_status"] == "TIMEOUT"
    assert results[1]["terminal_status"] == "NOT_STARTED"
    assert results[2]["terminal_status"] == "NOT_STARTED"


def test_build_timeout(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "import time; time.sleep(3)"],
        ["python3", "-c", "print('smoke')"],
        timeouts=(900, 1, 1800),
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert results[1]["terminal_status"] == "TIMEOUT"
    assert results[2]["terminal_status"] == "NOT_STARTED"


def test_smoke_timeout(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "import time; time.sleep(3)"],
        timeouts=(900, 3600, 1),
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert results[2]["terminal_status"] == "TIMEOUT"


def test_stdout_stderr_hash_and_byte_counts(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "import sys; sys.stdout.write('OUT'); sys.stderr.write('ERR')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    job = results[0]
    assert job["stdout_sha256"] == _sha256_bytes(b"OUT")
    assert job["stderr_sha256"] == _sha256_bytes(b"ERR")
    assert job["stdout_bytes"] == 3
    assert job["stderr_bytes"] == 3


def test_no_shell_execution(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    seen = {}

    class FakeProc:
        returncode = 0
        pid = os.getpid()

        def communicate(self, timeout=None):
            return b"", b""

        def kill(self):
            return None

        def poll(self):
            return self.returncode

    def fake_popen(argv, stdout=None, stderr=None, shell=None, env=None, start_new_session=None):
        seen["argv"] = argv
        seen["shell"] = shell
        seen["start_new_session"] = start_new_session
        return FakeProc()

    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["cmake", "-S", "harness", "-B", "build"],
        "timeout_seconds": 900,
    }
    pilot_build.execute_job(
        spec, env={"PATH": "/usr/bin"}, log_root=tmp_path / "logs", popen=fake_popen
    )
    assert seen["shell"] is False
    assert seen["start_new_session"] is True
    assert seen["argv"] == ["cmake", "-S", "harness", "-B", "build"]


def test_no_retry_on_existing_intent(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    intent = tmp_path / "build-preflight-intent.json"
    intent.write_bytes(b"{}\n")
    monkeypatch.setattr(pilot_build, "INTENT_PATH", intent)
    monkeypatch.setattr(pilot_build, "RESULT_PATH", tmp_path / "result.json")
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", tmp_path / "source")
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", tmp_path / "build")
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", tmp_path / "harness")
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PREEXISTING"):
        pilot_build.run_build_preflight(tmp_path / "source", tmp_path / "build")


def test_no_network_download_contract():
    import p3_v3.pilot_build as pilot_build

    assert "-DFETCHCONTENT_FULLY_DISCONNECTED=ON" in pilot_build.CMAKE_CONFIGURE_ARGV
    assert "-DFETCHCONTENT_UPDATES_DISCONNECTED=ON" in pilot_build.CMAKE_CONFIGURE_ARGV
    assert (
        pilot_build.DISCONNECTED_ENVIRONMENT["FETCHCONTENT_FULLY_DISCONNECTED"] == "ON"
    )
    reason = pilot_build.detect_network_or_boost(
        b"Fetching Boost",
        b"",
        ["cmake"],
    )
    assert reason == "NETWORK_OR_DOWNLOAD_ATTEMPT"


def test_no_system_boost_fallback():
    import p3_v3.pilot_build as pilot_build

    with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
        # BOOST_ROOT is blocked only when the value names Boost/system Boost.
        pilot_build.reject_system_boost_environment(
            {"BOOST_ROOT": "/usr/include/boost"}
        )
    reason = pilot_build.detect_network_or_boost(
        b"",
        b"-I/usr/include/boost",
        ["c++"],
    )
    assert reason == "SYSTEM_BOOST_FALLBACK"
    assert "find_package(Boost" not in pilot_build.HARNESS_CMAKE_BYTES.decode("utf-8")
    assert b"/usr/include/boost" not in pilot_build.HARNESS_CMAKE_BYTES


def test_cuda_absence_is_non_blocking(monkeypatch):
    import p3_v3.pilot_build as pilot_build

    monkeypatch.setattr(
        pilot_build.shutil,
        "which",
        lambda name: None if name == "nvcc" else "/usr/bin/" + name,
    )
    monkeypatch.setattr(pilot_build, "probe_identity", lambda exe: None if exe is None else "probe")
    snapshot = pilot_build.make_environment_snapshot()
    assert snapshot["nvcc_present"] is False
    assert snapshot["cuda_absence_blocking"] is False
    assert snapshot["native_profiling_present"] is False
    assert snapshot["claims"] == "blocked"


def test_confirmatory_schema_leakage_rejection(tmp_path):
    from p3_v3.packages import verify_package
    from p3_v3.artifacts import canonical_sha256

    for schema in (
        "p3-pilot-build-preflight-intent-v1",
        "p3-pilot-build-preflight-job-result-v1",
        "p3-pilot-build-preflight-result-v1",
        "p3-pilot-build-preflight-environment-v1",
    ):
        value = {
            "schema_version": schema,
            "execution_class": "PILOT_ONLY",
            "denominator": "PILOT_ONLY",
            "claims": "blocked",
        }
        with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR_LEAK"):
            reject_confirmatory_pilot(value, schema)
        manifest = {
            "schema_version": schema,
            "role": "CONSTRUCTION_A",
            "parents": [],
            "files": [],
            "package_tree_sha256": canonical_sha256([]),
            "artifact_sha256": "0" * 64,
        }
        with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR_LEAK"):
            verify_package(tmp_path, manifest)
    import p3_v3.pilot_build as pilot_build

    accepted = _minimal_environment(pilot_build)
    assert accepted["execution_class"] == "PILOT_ONLY"
    assert accepted["schema_version"].startswith("p3-pilot-")


def test_claims_denominator_rq4_invariants():
    import p3_v3.pilot_build as pilot_build

    not_started = pilot_build.make_not_started_job(pilot_build.JOB_SPECS[1])
    assert not_started["claims"] == "blocked"
    assert not_started["execution_class"] == "PILOT_ONLY"
    assert not_started["denominator"] == "PILOT_ONLY"
    validated = _minimal_environment(pilot_build)
    assert validated["claims"] == "blocked"
    impl = "a" * 64
    intent = pilot_build.build_intent(validated, sorted([impl, "0" * 64]), impl)
    assert intent["claims"] == "blocked"
    assert intent["formal_denominator_membership"] is False
    assert intent["rq4_supported"] is False
    assert intent["no_retry"] is True
    assert intent["planned_count"] == 3
    assert intent["implementation_verdict_sha256"] == impl
    jobs = [
        pilot_build.make_not_started_job(spec) for spec in pilot_build.JOB_SPECS
    ]
    result = pilot_build.build_result(
        intent_sha256="1" * 64,
        environment=validated,
        jobs=jobs,
        predecessor=sorted(["1" * 64, impl]),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    assert result["claims"] == "blocked"
    assert result["formal_denominator_membership"] is False
    assert result["rq4_supported"] is False
    assert result["no_retry"] is True
    assert result["planned_count"] == 3


def test_capability_does_not_call_confirmatory_preflight():
    import p3_v3.pilot_build as pilot_build

    assert not hasattr(pilot_build, "run_preflight")
    source = Path(__file__).resolve().parents[2] / "src" / "p3_v3" / "pilot_build.py"
    text = source.read_text(encoding="utf-8")
    assert "run_preflight" not in text
    assert "erf(x)" not in text
    assert "erfc" not in text


def test_implementation_verdict_reviewed_path_commit_hash_drift():
    import p3_v3.pilot_build as pilot_build

    verdict = {
        "reviewed_plan_path": pilot_build.PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "reviewed_plan_verdict_sha256": "1" * 64,
        "reviewed_commit": "44acee8882b004f50005cd39ca732bc6f09604fa",
        "reviewed_pilot_build_path": "src/wrong.py",
        "reviewed_pilot_build_sha256": "2" * 64,
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": "3" * 64,
        "reviewed_test_pilot_build_path": "tests/p3_v3/test_pilot_build.py",
        "reviewed_test_pilot_build_sha256": "4" * 64,
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": "5" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_BUILD_PREFLIGHT_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_IMPL_VERDICT"):
        pilot_build.validate_implementation_verdict(verdict, "0" * 64, "1" * 64)
    verdict["reviewed_pilot_build_path"] = "src/p3_v3/pilot_build.py"
    verdict["reviewed_commit"] = "NOTAGITSHA"
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_IMPL_VERDICT"):
        pilot_build.validate_implementation_verdict(verdict, "0" * 64, "1" * 64)


def test_implementation_verdict_sha_enters_intent_result_predecessor():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "b" * 64
    intent = pilot_build.build_intent(env, sorted([impl, "c" * 64]), impl)
    assert intent["implementation_verdict_sha256"] == impl
    assert impl in intent["predecessor_sha256"]
    jobs = [pilot_build.make_not_started_job(spec) for spec in pilot_build.JOB_SPECS]
    result = pilot_build.build_result(
        intent_sha256="d" * 64,
        environment=env,
        jobs=jobs,
        predecessor=sorted(["d" * 64, impl]),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    assert result["implementation_verdict_sha256"] == impl
    assert impl in result["predecessor_sha256"]


def test_reviewed_production_bytes_runtime_drift(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    current = tmp_path / "src" / "p3_v3" / "pilot_build.py"
    current.parent.mkdir(parents=True)
    current.write_bytes(b"current-bytes\n")
    monkeypatch.setattr(
        pilot_build,
        "REVIEWED_IMPLEMENTATION_FILES",
        (
            (
                "reviewed_pilot_build_path",
                "reviewed_pilot_build_sha256",
                str(current),
            ),
        ),
    )
    verdict = {
        "reviewed_pilot_build_path": str(current),
        "reviewed_pilot_build_sha256": "0" * 64,
    }
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PRODUCTION_BYTES"):
        pilot_build.verify_reviewed_production_bytes(verdict)


def test_durable_environment_snapshot_round_trip():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "f" * 64
    intent = pilot_build.build_intent(env, sorted([impl]), impl)
    again = pilot_build.validate_environment_snapshot(intent["environment_snapshot"])
    assert again["artifact_sha256"] == intent["environment_snapshot_sha256"]
    assert again["cmake_executable_path"] == "/usr/bin/cmake"
    assert again["cxx_compiler_path"] == "/usr/bin/c++"
    assert again["cmake_version"] == "cmake version 3.28.0"
    assert again["cmake_generator"] == "Unix Makefiles"


def test_missing_compiler_exact_infrastructure_result(tmp_path):
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    env = dict(env)
    env["cxx_compiler_path"] = None
    env["cxx_compiler_executable"] = None
    env["cxx_compiler_identity"] = None
    env["cxx_compiler_version"] = None
    env.pop("artifact_sha256")
    env = pilot_build.validate_environment_snapshot(pilot_build._self_hash(env))
    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        environment=env,
    )
    assert results[0]["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert results[0]["failure_reason"] == "MISSING_DEPENDENCY"
    assert results[0]["process_started"] is False
    assert results[0]["infrastructure_phase"] == "PRE_PROCESS"
    assert results[1]["terminal_status"] == "NOT_STARTED"
    assert results[2]["terminal_status"] == "NOT_STARTED"


def _started_job(pilot_build, spec, **overrides):
    payload = {
        "schema_version": "p3-pilot-build-preflight-job-result-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "job_id": spec["job_id"],
        "job_kind": spec["job_kind"],
        "dependency_job_ids": list(spec["dependency_job_ids"]),
        "argv": list(spec["argv"]),
        "timeout_seconds": spec["timeout_seconds"],
        "process_started": True,
        "process_group_terminated": False,
        "infrastructure_phase": None,
        "terminal_status": "PASS",
        "failure_reason": None,
        "exit_code": 0,
        "stdout_sha256": "a" * 64,
        "stderr_sha256": "b" * 64,
        "stdout_bytes": 1,
        "stderr_bytes": 1,
        "started_at": "2026-08-18T00:00:00Z",
        "ended_at": "2026-08-18T00:00:01Z",
        "wall_seconds": 1.0,
        "cpu_seconds": 0.1,
        "peak_rss_bytes": 1024,
        "claims": "blocked",
    }
    payload.update(overrides)
    return pilot_build.validate_job_result(pilot_build._self_hash(payload))


def test_terminal_status_exact_matrix():
    import p3_v3.pilot_build as pilot_build

    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["cmake"],
        "timeout_seconds": 900,
    }
    passed = _started_job(pilot_build, spec)
    assert passed["terminal_status"] == "PASS"
    assert passed["process_started"] is True
    assert passed["failure_reason"] is None
    failed = _started_job(
        pilot_build,
        spec,
        terminal_status="FAIL",
        failure_reason="NONZERO_EXIT",
        exit_code=2,
    )
    assert failed["terminal_status"] == "FAIL"
    timed = _started_job(
        pilot_build,
        spec,
        terminal_status="TIMEOUT",
        failure_reason="TIMEOUT",
        exit_code=None,
        process_group_terminated=True,
    )
    assert timed["process_group_terminated"] is True
    not_started = pilot_build.make_not_started_job(spec)
    assert not_started["process_started"] is False
    assert not_started["failure_reason"] == "DEPENDENCY_NOT_STARTED"
    assert not_started["started_at"] is None
    pre = pilot_build.make_pre_process_infra_job(spec, "MISSING_DEPENDENCY")
    assert pre["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert pre["infrastructure_phase"] == "PRE_PROCESS"
    assert pre["process_started"] is False
    post = _started_job(
        pilot_build,
        spec,
        terminal_status="FAIL_INFRASTRUCTURE",
        failure_reason="SYSTEM_BOOST_FALLBACK",
        infrastructure_phase="POST_PROCESS",
        exit_code=1,
    )
    assert post["infrastructure_phase"] == "POST_PROCESS"
    for status in ("PASS", "FAIL", "TIMEOUT", "FAIL_INFRASTRUCTURE", "NOT_STARTED"):
        assert status in pilot_build.ALL_TERMINAL


def test_result_count_conservation_and_aggregate():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "1" * 64
    jobs = [
        pilot_build.make_pre_process_infra_job(pilot_build.JOB_SPECS[0], "MISSING_DEPENDENCY"),
        pilot_build.make_not_started_job(pilot_build.JOB_SPECS[1]),
        pilot_build.make_not_started_job(pilot_build.JOB_SPECS[2]),
    ]
    result = pilot_build.build_result(
        intent_sha256="2" * 64,
        environment=env,
        jobs=jobs,
        predecessor=sorted(["2" * 64, impl]),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    assert result["planned_count"] == 3
    assert result["terminal_count"] == 3
    assert result["started_count"] == 0
    assert result["not_started_count"] == 2
    assert result["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert result["failure_reason"] == "MISSING_DEPENDENCY"


def test_configure_build_dependency_blocking(tmp_path):
    test_configure_failure_prevents_build_and_smoke(tmp_path / "configure")
    test_build_failure_prevents_smoke(tmp_path / "build")


def test_process_group_timeout_terminates_descendants(tmp_path):
    import time
    import p3_v3.pilot_build as pilot_build

    marker = tmp_path / "desc.pid"
    partial_out = b"P3_TIMEOUT_PARTIAL_STDOUT\n"
    partial_err = b"P3_TIMEOUT_PARTIAL_STDERR\n"
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": [
            "python3",
            "-c",
            (
                "import pathlib, subprocess, sys, time\n"
                "sys.stdout.buffer.write(b'P3_TIMEOUT_PARTIAL_STDOUT\\n')\n"
                "sys.stdout.buffer.flush()\n"
                "sys.stderr.buffer.write(b'P3_TIMEOUT_PARTIAL_STDERR\\n')\n"
                "sys.stderr.buffer.flush()\n"
                "child = subprocess.Popen(['sleep', '30'])\n"
                "pathlib.Path(sys.argv[1]).write_text(str(child.pid), encoding='utf-8')\n"
                "time.sleep(30)\n"
            ),
            str(marker),
        ],
        "timeout_seconds": 900,
    }
    log_root = tmp_path / "logs"
    result = pilot_build.execute_job(
        spec,
        env=dict(os.environ),
        log_root=log_root,
        timeout_seconds=0.4,
    )
    assert result["terminal_status"] == "TIMEOUT"
    assert result["process_group_terminated"] is True
    assert result["exit_code"] is None
    raw_out = (log_root / "CMAKE_CONFIGURE.stdout").read_bytes()
    raw_err = (log_root / "CMAKE_CONFIGURE.stderr").read_bytes()
    assert raw_out == partial_out
    assert raw_err == partial_err
    assert result["stdout_sha256"] == _sha256_bytes(partial_out)
    assert result["stderr_sha256"] == _sha256_bytes(partial_err)
    assert result["stdout_bytes"] == len(partial_out)
    assert result["stderr_bytes"] == len(partial_err)
    deadline = time.monotonic() + 3
    pid = int(marker.read_text(encoding="utf-8"))
    gone = False
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            gone = True
            break
        time.sleep(0.05)
    assert gone is True


def test_exception_after_intent_produces_terminal_result(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    source = tmp_path / "source"
    build = tmp_path / "build"
    harness = tmp_path / "harness"
    intent_path = tmp_path / "intent.json"
    result_path = tmp_path / "result.json"
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", source)
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", build)
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", harness)
    monkeypatch.setattr(pilot_build, "INTENT_PATH", intent_path)
    monkeypatch.setattr(pilot_build, "RESULT_PATH", result_path)
    monkeypatch.setattr(pilot_build, "_require_authorization", lambda: "a" * 64)
    monkeypatch.setattr(pilot_build, "_require_source_preparation_identities", lambda: None)
    monkeypatch.setattr(
        pilot_build,
        "_require_plan_and_implementation_verdicts",
        lambda: ("0" * 64, "1" * 64, "2" * 64),
    )
    monkeypatch.setattr(pilot_build, "require_frozen_source_tree", lambda root: "3" * 64)
    monkeypatch.setattr(
        pilot_build,
        "make_environment_snapshot",
        lambda: _minimal_environment(pilot_build),
    )

    def boom(harness_root, cmake_bytes, cxx_bytes):
        raise EvidenceError("E_PILOT_BUILD_HARNESS", "HARNESS_PUBLICATION_FAILURE")

    monkeypatch.setattr(pilot_build, "write_harness", boom)
    written = pilot_build.run_build_preflight(source, build)
    assert intent_path.is_file()
    assert result_path.is_file()
    assert written["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert written["failure_reason"] == "HARNESS_PUBLICATION_FAILURE"
    assert written["jobs"][0]["process_started"] is False


def test_orphaned_intent_reconciliation_writes_no_new_process(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build
    from p3_v3.artifacts import write_canonical_json

    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=False,
            intent_valid=True,
            result_valid=False,
            producer_live=False,
            child_live=False,
            pair_valid=False,
        )
        == "INTENT_ONLY_ORPHAN"
    )
    env = _minimal_environment(pilot_build)
    impl = "7" * 64
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", tmp_path / "source")
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", tmp_path / "build")
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", tmp_path / "harness")
    intent = pilot_build.build_intent(env, sorted([impl]), impl)
    intent_path = tmp_path / "intent.json"
    result_path = tmp_path / "result.json"
    write_canonical_json(intent_path, intent, exclusive=True)
    original = intent_path.read_bytes()
    monkeypatch.setattr(pilot_build, "INTENT_PATH", intent_path)
    monkeypatch.setattr(pilot_build, "RESULT_PATH", result_path)
    monkeypatch.setattr(pilot_build, "attempt_is_live", lambda pid, starttime: False)
    seen = []

    def fake_popen(*args, **kwargs):
        seen.append(args)
        raise AssertionError("orphan must not start a child")

    monkeypatch.setattr(pilot_build.subprocess, "Popen", fake_popen)
    written = pilot_build.run_build_preflight(tmp_path / "source", tmp_path / "build")
    assert written["failure_reason"] == "ORPHANED_INTENT_NO_PROCESS"
    assert written["jobs"][0]["process_started"] is False
    assert seen == []
    assert intent_path.read_bytes() == original
    assert result_path.is_file()


def test_second_invocation_never_reruns(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build
    from p3_v3.artifacts import write_canonical_json

    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=True,
            intent_valid=True,
            result_valid=True,
            producer_live=False,
            child_live=False,
            pair_valid=True,
        )
        == "RESULT_TERMINAL"
    )
    env = _minimal_environment(pilot_build)
    impl = "8" * 64
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", tmp_path / "source")
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", tmp_path / "build")
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", tmp_path / "harness")
    intent = pilot_build.build_intent(env, sorted([impl]), impl)
    jobs = [
        pilot_build.make_pre_process_infra_job(
            spec, "ORPHANED_INTENT_NO_PROCESS"
        )
        if spec["job_id"] == "CMAKE_CONFIGURE"
        else pilot_build.make_not_started_job(spec)
        for spec in pilot_build.bind_job_specs(env)
    ]
    intent_path = tmp_path / "intent.json"
    result_path = tmp_path / "result.json"
    write_canonical_json(intent_path, intent, exclusive=True)
    result = pilot_build.build_result(
        intent_sha256=_sha256_bytes(intent_path.read_bytes()),
        environment=env,
        jobs=jobs,
        predecessor=sorted(
            [_sha256_bytes(intent_path.read_bytes()), *intent["predecessor_sha256"]]
        ),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    write_canonical_json(result_path, result, exclusive=True)
    before_intent = intent_path.read_bytes()
    before_result = result_path.read_bytes()
    monkeypatch.setattr(pilot_build, "INTENT_PATH", intent_path)
    monkeypatch.setattr(pilot_build, "RESULT_PATH", result_path)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PREEXISTING"):
        pilot_build.run_build_preflight(tmp_path / "source", tmp_path / "build")
    assert intent_path.read_bytes() == before_intent
    assert result_path.read_bytes() == before_result


def test_source_drift_after_child_yields_terminal_failure(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    calls = {"n": 0}

    def fake_tree(source_root):
        calls["n"] += 1
        if calls["n"] == 1:
            return "a" * 64
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "SOURCE_TREE_DRIFT")

    monkeypatch.setattr(pilot_build, "require_frozen_source_tree", fake_tree)
    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        source_root=tmp_path / "source",
    )
    assert results[0]["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert results[0]["failure_reason"] == "SOURCE_TREE_DRIFT"
    assert results[1]["terminal_status"] == "NOT_STARTED"


def test_system_boost_dependency_path_rejection():
    import p3_v3.pilot_build as pilot_build

    with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
        pilot_build.reject_nonfrozen_boost_headers(
            ["/usr/include/boost/config.hpp"]
        )


def test_frozen_source_dependency_closure_pass():
    import p3_v3.pilot_build as pilot_build

    paths = [
        "/tmp/p3-boost-math-pilot-production-source/include/boost/math/constants/constants.hpp",
        "/usr/include/c++/13/cmath",
    ]
    pilot_build.reject_nonfrozen_boost_headers(paths)
    digest = _sha256_bytes(pilot_build.canonical_dependency_list_bytes(paths))
    assert len(digest) == 64


def test_build_artifact_hashes_bound():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "4" * 64
    jobs = [_started_job(pilot_build, spec) for spec in pilot_build.JOB_SPECS]
    evidence = {
        "cmake_cache_sha256": "6" * 64,
        "compile_commands_sha256": "7" * 64,
        "compiler_depfile_sha256": "a" * 64,
        "dependency_list_sha256": "8" * 64,
        "smoke_executable_sha256": "9" * 64,
    }
    result = pilot_build.build_result(
        intent_sha256="5" * 64,
        environment=env,
        jobs=jobs,
        predecessor=sorted(["5" * 64, impl]),
        implementation_verdict_sha256=impl,
        evidence=evidence,
    )
    assert result["cmake_cache_sha256"] == "6" * 64
    assert result["compile_commands_sha256"] == "7" * 64
    assert result["compiler_depfile_sha256"] == "a" * 64
    assert result["dependency_list_sha256"] == "8" * 64
    assert result["smoke_executable_sha256"] == "9" * 64
    assert result["terminal_status"] == "PASS"
    assert result["failure_reason"] is None


def test_smoke_refuses_executable_hash_drift(tmp_path):
    import p3_v3.pilot_build as pilot_build

    exe = tmp_path / "boost_math_pilot_smoke"
    exe.write_bytes(b"old-bytes\n")
    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        [str(exe)],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        expected_smoke_sha256="0" * 64,
    )
    assert results[0]["terminal_status"] == "PASS"
    assert results[1]["terminal_status"] == "PASS"
    assert results[2]["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert results[2]["failure_reason"] == "MISSING_DEPENDENCY"
    assert results[2]["process_started"] is False


def _synthetic_build_evidence_tree(
    tmp_path: Path,
    pilot_build,
    monkeypatch,
    *,
    include_flag=True,
    compiler="/usr/bin/c++",
    generator="Unix Makefiles",
    system_boost=False,
    cache_compiler=None,
    source_dir=None,
    binary_dir=None,
):
    build = tmp_path / "build"
    harness = tmp_path / "harness"
    dep_dir = build / "CMakeFiles" / "boost_math_pilot_smoke.dir"
    dep_dir.mkdir(parents=True)
    harness.mkdir()
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", build)
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", harness)
    cache_compiler = compiler if cache_compiler is None else cache_compiler
    source_dir = harness.as_posix() if source_dir is None else source_dir
    binary_dir = build.as_posix() if binary_dir is None else binary_dir
    (build / "CMakeCache.txt").write_text(
        "\n".join(
            [
                f"CMAKE_GENERATOR:INTERNAL={generator}",
                f"CMAKE_CXX_COMPILER:FILEPATH={cache_compiler}",
                f"CMAKE_HOME_DIRECTORY:INTERNAL={source_dir}",
                f"CMAKE_BINARY_DIR:STATIC={binary_dir}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    include = pilot_build.FROZEN_INCLUDE_PREFIX if include_flag else "/tmp/other-include"
    compile_argv = [compiler, f"-I{include}", "-DBOOST_MATH_STANDALONE=1", "-c", "smoke.cpp"]
    (build / "compile_commands.json").write_text(
        __import__("json").dumps(
            [
                {
                    "directory": build.as_posix(),
                    "file": (harness / "smoke.cpp").as_posix(),
                    "arguments": compile_argv,
                }
            ]
        ),
        encoding="utf-8",
    )
    (build / "boost_math_pilot_smoke").write_bytes(b"exe\n")
    boost_header = (
        "/usr/include/boost/math/constants/constants.hpp"
        if system_boost
        else pilot_build.FROZEN_CONSTANTS_HEADER
    )
    dep_text = (
        "CMakeFiles/boost_math_pilot_smoke.dir/smoke.cpp.o: "
        f"{(harness / 'smoke.cpp').as_posix()} "
        f"{boost_header} "
        "/usr/include/c++/13/cmath\n"
    )
    (dep_dir / "smoke.cpp.o.d").write_text(dep_text, encoding="utf-8")
    env = _minimal_environment(pilot_build)
    env = dict(env)
    env["cxx_compiler_path"] = compiler
    env.pop("artifact_sha256", None)
    env = pilot_build.validate_environment_snapshot(pilot_build._self_hash(env))
    return build, env


def test_collect_baseline_build_evidence_pass(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(tmp_path, pilot_build, monkeypatch)
    evidence = pilot_build.collect_baseline_build_evidence(build, env)
    assert len(evidence["compiler_depfile_sha256"]) == 64
    assert len(evidence["dependency_list_sha256"]) == 64
    assert evidence["compiler_depfile_sha256"] != evidence["dependency_list_sha256"]


def test_attempt2_collect_baseline_build_evidence_uses_attempt2_roots(
    tmp_path, monkeypatch
):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(tmp_path, pilot_build, monkeypatch)
    attempt2_harness = tmp_path / "attempt2-harness"
    attempt2_harness.mkdir()
    original_harness = tmp_path / "harness"
    for path in (
        build / "CMakeCache.txt",
        build / "compile_commands.json",
        build / pilot_build.COMPILER_DEPFILE_RELATIVE,
    ):
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                original_harness.as_posix(), attempt2_harness.as_posix()
            ),
            encoding="utf-8",
        )
    monkeypatch.setattr(pilot_build, "ATTEMPT2_BUILD_ROOT", build)
    monkeypatch.setattr(pilot_build, "ATTEMPT2_HARNESS_ROOT", attempt2_harness)
    assert pilot_build.collect_baseline_build_evidence(build, env)[
        "smoke_executable_sha256"
    ] == hashlib.sha256((build / "boost_math_pilot_smoke").read_bytes()).hexdigest()


def test_collect_baseline_build_evidence_missing_frozen_include(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(
        tmp_path, pilot_build, monkeypatch, include_flag=False
    )
    with pytest.raises(EvidenceError, match="UNSUPPORTED_TOOLCHAIN"):
        pilot_build.collect_baseline_build_evidence(build, env)


def test_compile_commands_compiler_mismatch(tmp_path, monkeypatch):
    import json
    import p3_v3.pilot_build as pilot_build

    compiler_a = str((tmp_path / "compiler-a").resolve())
    compiler_b = str((tmp_path / "compiler-b").resolve())
    build, env = _synthetic_build_evidence_tree(
        tmp_path,
        pilot_build,
        monkeypatch,
        compiler=compiler_a,
    )
    assert env["cxx_compiler_path"] == compiler_a
    cache = (build / "CMakeCache.txt").read_text(encoding="utf-8")
    assert f"CMAKE_CXX_COMPILER:FILEPATH={compiler_a}" in cache
    commands_path = build / "compile_commands.json"
    payload = json.loads(commands_path.read_text(encoding="utf-8"))
    payload[0]["arguments"][0] = compiler_b
    commands_path.write_text(
        json.dumps(payload) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(
        EvidenceError,
        match="compile_commands compiler differs",
    ):
        pilot_build.collect_baseline_build_evidence(build, env)


def test_cmakecache_compiler_generator_root_drift(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(
        tmp_path,
        pilot_build,
        monkeypatch,
        generator="Ninja",
    )
    with pytest.raises(EvidenceError, match="CMAKE_GENERATOR differs"):
        pilot_build.collect_baseline_build_evidence(build, env)
    cache_other = tmp_path / "cache-other-cxx"
    build, env = _synthetic_build_evidence_tree(
        tmp_path / "compiler",
        pilot_build,
        monkeypatch,
        cache_compiler=str(cache_other),
    )
    with pytest.raises(
        EvidenceError,
        match="CMakeCache compiler differs",
    ):
        pilot_build.collect_baseline_build_evidence(build, env)
    build, env = _synthetic_build_evidence_tree(
        tmp_path / "root",
        pilot_build,
        monkeypatch,
        source_dir="/tmp/other-harness",
    )
    with pytest.raises(EvidenceError, match="CMake source directory differs"):
        pilot_build.collect_baseline_build_evidence(build, env)


def test_system_boost_in_actual_depfile(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(
        tmp_path, pilot_build, monkeypatch, system_boost=True
    )
    with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
        pilot_build.collect_baseline_build_evidence(build, env)


def test_depfile_raw_and_canonical_hashes_enter_result():
    test_build_artifact_hashes_bound()


def test_configure_build_use_resolved_toolchain_argv():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    configure = pilot_build.bind_configure_argv(
        env["cmake_executable_path"], env["cxx_compiler_path"]
    )
    build = pilot_build.bind_build_argv(env["cmake_executable_path"])
    assert configure[0] == env["cmake_executable_path"]
    assert build[0] == env["cmake_executable_path"]
    assert "-DCMAKE_CXX_COMPILER=" + env["cxx_compiler_path"] in configure
    intent = pilot_build.build_intent(env, sorted(["b" * 64]), "b" * 64)
    assert intent["cmake_configure_argv"] == configure
    assert intent["baseline_build_argv"] == build


def test_producer_dead_child_live_not_orphan_terminal():
    import p3_v3.pilot_build as pilot_build

    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=False,
            intent_valid=True,
            result_valid=False,
            producer_live=False,
            child_live=True,
            pair_valid=False,
        )
        == "INTENT_CHILD_LIVE"
    )
    assert "ORPHANED_INTENT_NO_PROCESS" not in {
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=False,
            intent_valid=True,
            result_valid=False,
            producer_live=False,
            child_live=True,
            pair_valid=False,
        )
    }


def test_post_popen_exception_reaps_process_group(tmp_path, monkeypatch):
    import time
    import p3_v3.pilot_build as pilot_build

    marker = tmp_path / "desc.pid"
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": [
            "python3",
            "-c",
            (
                "import pathlib, subprocess, sys, time\n"
                "child = subprocess.Popen(['sleep', '30'])\n"
                "pathlib.Path(sys.argv[1]).write_text(str(child.pid), encoding='utf-8')\n"
                "time.sleep(30)\n"
            ),
            str(marker),
        ],
        "timeout_seconds": 900,
    }

    def boom(*args, **kwargs):
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline and not marker.is_file():
            time.sleep(0.05)
        if not marker.is_file():
            raise OSError("identity publication failed before descendant pid")
        raise OSError("identity publication failed")

    monkeypatch.setattr(pilot_build, "write_process_identity", boom)
    result = pilot_build.execute_job(
        spec,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        timeout_seconds=5,
    )
    assert result["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert result["failure_reason"] == "PROCESS_IDENTITY_PUBLICATION_FAILURE"
    assert result["infrastructure_phase"] == "POST_PROCESS"
    assert result["process_started"] is True
    assert result["process_group_terminated"] is True
    deadline = time.monotonic() + 3
    pid = int(marker.read_text(encoding="utf-8"))
    gone = False
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            gone = True
            break
        time.sleep(0.05)
    assert gone is True


def test_outer_deadline_exhausted_not_missing_dependency(tmp_path):
    import time
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        outer_deadline=time.monotonic() - 1,
    )
    assert results[0]["failure_reason"] == "OUTER_DEADLINE_EXHAUSTED"
    assert results[0]["failure_reason"] != "MISSING_DEPENDENCY"
    assert results[0]["process_started"] is False
    assert results[1]["terminal_status"] == "NOT_STARTED"


def test_validate_attempt_pair_rejects_drift():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "c" * 64
    intent = pilot_build.build_intent(env, sorted([impl]), impl)
    jobs = [
        pilot_build.make_pre_process_infra_job(spec, "ORPHANED_INTENT_NO_PROCESS")
        if spec["job_id"] == "CMAKE_CONFIGURE"
        else pilot_build.make_not_started_job(spec)
        for spec in pilot_build.bind_job_specs(env)
    ]
    intent_sha = "d" * 64
    result = pilot_build.build_result(
        intent_sha256=intent_sha,
        environment=env,
        jobs=jobs,
        predecessor=sorted([intent_sha, *intent["predecessor_sha256"]]),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    drifted = dict(result)
    drifted["intent_sha256"] = "e" * 64
    drifted.pop("artifact_sha256")
    drifted = pilot_build._self_hash(drifted)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PAIR"):
        pilot_build.validate_attempt_pair(intent, intent_sha, drifted)
    other_env = dict(env)
    other_env["python_version"] = "3.12.0"
    other_env.pop("artifact_sha256", None)
    other_env = pilot_build.validate_environment_snapshot(pilot_build._self_hash(other_env))
    env_drift = dict(result)
    env_drift["environment_snapshot"] = other_env
    env_drift["environment_snapshot_sha256"] = other_env["artifact_sha256"]
    env_drift.pop("artifact_sha256")
    env_drift = pilot_build._self_hash(env_drift)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PAIR"):
        pilot_build.validate_attempt_pair(intent, intent_sha, env_drift)
    impl_drift = dict(result)
    impl_drift["implementation_verdict_sha256"] = "0" * 64
    impl_drift["predecessor_sha256"] = sorted([intent_sha, "0" * 64])
    impl_drift.pop("artifact_sha256")
    impl_drift = pilot_build._self_hash(impl_drift)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PAIR"):
        pilot_build.validate_attempt_pair(intent, intent_sha, impl_drift)
    pred_drift = dict(result)
    pred_drift["predecessor_sha256"] = sorted(list(intent["predecessor_sha256"]))
    pred_drift.pop("artifact_sha256")
    pred_drift = pilot_build._self_hash(pred_drift)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PAIR"):
        pilot_build.validate_attempt_pair(intent, intent_sha, pred_drift)
    argv_drift = dict(result)
    jobs_drift = [dict(job) for job in argv_drift["jobs"]]
    jobs_drift[0] = dict(jobs_drift[0])
    jobs_drift[0]["argv"] = ["cmake"]
    jobs_drift[0].pop("artifact_sha256", None)
    jobs_drift[0] = pilot_build._self_hash(jobs_drift[0])
    argv_drift["jobs"] = jobs_drift
    argv_drift.pop("artifact_sha256")
    argv_drift = pilot_build._self_hash(argv_drift)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PAIR"):
        pilot_build.validate_attempt_pair(intent, intent_sha, argv_drift)


def test_mismatched_intent_result_is_not_result_terminal():
    import p3_v3.pilot_build as pilot_build

    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=True,
            intent_valid=True,
            result_valid=True,
            producer_live=False,
            child_live=False,
            pair_valid=False,
        )
        == "INVALID_DURABLE"
    )


def test_start_marker_exists_before_popen(tmp_path):
    import p3_v3.pilot_build as pilot_build

    seen = {}

    class FakeProc:
        returncode = 0
        pid = os.getpid()

        def communicate(self, timeout=None):
            return b"", b""

        def poll(self):
            return 0

        def kill(self):
            return None

    def fake_popen(argv, stdout=None, stderr=None, shell=None, env=None, start_new_session=None):
        seen["marker"] = (tmp_path / "logs" / "CMAKE_CONFIGURE.start.json").is_file()
        return FakeProc()

    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["cmake", "-S", "harness", "-B", "build"],
        "timeout_seconds": 900,
    }
    result = pilot_build.execute_job(
        spec, env={"PATH": "/usr/bin"}, log_root=tmp_path / "logs", popen=fake_popen
    )
    assert seen["marker"] is True
    assert result["terminal_status"] == "PASS"
    assert (tmp_path / "logs" / "CMAKE_CONFIGURE.start.json").is_file()
    assert (tmp_path / "logs" / "CMAKE_CONFIGURE.identity.json").is_file()


def test_identity_publication_returns_started_job(tmp_path, monkeypatch):
    test_post_popen_exception_reaps_process_group(tmp_path, monkeypatch)


def test_log_publication_returns_started_job(tmp_path, monkeypatch):
    import time
    from pathlib import Path as PathType

    import p3_v3.pilot_build as pilot_build

    marker = tmp_path / "desc.pid"
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": [
            "python3",
            "-c",
            (
                "import pathlib, subprocess, sys\n"
                "child = subprocess.Popen(['sleep', '30'])\n"
                "pathlib.Path(sys.argv[1]).write_text(str(child.pid), encoding='utf-8')\n"
                "print('parent-exit')\n"
            ),
            str(marker),
        ],
        "timeout_seconds": 900,
    }
    original = PathType.write_bytes

    def boom(self, data):
        if self.name.endswith(".stdout") or self.name.endswith(".stderr"):
            raise OSError("log publication failed")
        return original(self, data)

    monkeypatch.setattr(PathType, "write_bytes", boom)
    result = pilot_build.execute_job(
        spec,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        timeout_seconds=5,
    )
    assert result["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert result["failure_reason"] == "LOG_PUBLICATION_FAILURE"
    assert result["infrastructure_phase"] == "POST_PROCESS"
    assert result["process_started"] is True
    deadline = time.monotonic() + 3
    pid = int(marker.read_text(encoding="utf-8"))
    gone = False
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            gone = True
            break
        time.sleep(0.05)
    assert gone is True


def test_normal_pass_does_not_call_killpg(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    called = []
    real = os.killpg

    def wrapped(pgid, sig):
        called.append((pgid, sig))
        return real(pgid, sig)

    monkeypatch.setattr(os, "killpg", wrapped)
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["python3", "-c", "print('ok')"],
        "timeout_seconds": 900,
    }
    result = pilot_build.execute_job(
        spec,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert result["terminal_status"] == "PASS"
    assert result["process_group_terminated"] is False
    assert called == []


def test_process_group_leak_is_detected_and_cleaned(tmp_path):
    import time
    import p3_v3.pilot_build as pilot_build

    marker = tmp_path / "desc.pid"
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": [
            "python3",
            "-c",
            (
                "import pathlib, subprocess, sys\n"
                "child = subprocess.Popen(['sleep', '30'])\n"
                "pathlib.Path(sys.argv[1]).write_text(str(child.pid), encoding='utf-8')\n"
                "print('parent-exit')\n"
            ),
            str(marker),
        ],
        "timeout_seconds": 900,
    }
    result = pilot_build.execute_job(
        spec,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert result["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert result["failure_reason"] == "PROCESS_GROUP_LEAK"
    assert result["infrastructure_phase"] == "POST_PROCESS"
    assert result["process_started"] is True
    assert result["process_group_terminated"] is True
    deadline = time.monotonic() + 3
    pid = int(marker.read_text(encoding="utf-8"))
    gone = False
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            gone = True
            break
        time.sleep(0.05)
    assert gone is True


def test_start_marker_without_identity_is_unresolved(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build
    from p3_v3.artifacts import write_canonical_json

    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=False,
            intent_valid=True,
            result_valid=False,
            producer_live=False,
            child_live=False,
            pair_valid=False,
            start_marker_present=True,
            identity_resolved=False,
        )
        == "INTENT_CHILD_STATE_UNRESOLVED"
    )
    env = _minimal_environment(pilot_build)
    impl = "7" * 64
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", tmp_path / "source")
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", tmp_path / "build")
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", tmp_path / "harness")
    intent = pilot_build.build_intent(env, sorted([impl]), impl)
    intent_path = tmp_path / "intent.json"
    result_path = tmp_path / "result.json"
    write_canonical_json(intent_path, intent, exclusive=True)
    logs = tmp_path / "build" / "logs"
    logs.mkdir(parents=True)
    write_canonical_json(
        logs / "CMAKE_CONFIGURE.start.json",
        {
            "job_id": "CMAKE_CONFIGURE",
            "argv_sha256": "a" * 64,
            "created_at": "2026-08-18T00:00:00Z",
            "state": "STARTING",
        },
        exclusive=True,
    )
    monkeypatch.setattr(pilot_build, "INTENT_PATH", intent_path)
    monkeypatch.setattr(pilot_build, "RESULT_PATH", result_path)
    monkeypatch.setattr(pilot_build, "attempt_is_live", lambda pid, starttime: False)
    seen = []

    def fake_popen(*args, **kwargs):
        seen.append(args)
        raise AssertionError("unresolved must not start a child")

    monkeypatch.setattr(pilot_build.subprocess, "Popen", fake_popen)
    with pytest.raises(EvidenceError, match="child start state is unresolved"):
        pilot_build.run_build_preflight(tmp_path / "source", tmp_path / "build")
    assert seen == []
    assert not result_path.exists()
    assert intent_path.is_file()


def test_orphan_requires_no_start_marker():
    import p3_v3.pilot_build as pilot_build

    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=False,
            intent_valid=True,
            result_valid=False,
            producer_live=False,
            child_live=False,
            pair_valid=False,
            start_marker_present=False,
            identity_resolved=True,
        )
        == "INTENT_ONLY_ORPHAN"
    )
    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=False,
            intent_valid=True,
            result_valid=False,
            producer_live=False,
            child_live=False,
            pair_valid=False,
            start_marker_present=True,
            identity_resolved=False,
        )
        != "INTENT_ONLY_ORPHAN"
    )


def test_started_post_process_failure_count_conservation():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "1" * 64
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["cmake"],
        "timeout_seconds": 900,
    }
    started = _started_job(
        pilot_build,
        spec,
        terminal_status="FAIL_INFRASTRUCTURE",
        failure_reason="PROCESS_IDENTITY_PUBLICATION_FAILURE",
        infrastructure_phase="POST_PROCESS",
        process_group_terminated=True,
        exit_code=1,
    )
    jobs = [
        started,
        pilot_build.make_not_started_job(pilot_build.JOB_SPECS[1]),
        pilot_build.make_not_started_job(pilot_build.JOB_SPECS[2]),
    ]
    result = pilot_build.build_result(
        intent_sha256="5" * 64,
        environment=env,
        jobs=jobs,
        predecessor=sorted(["5" * 64, impl]),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    assert result["planned_count"] == 3
    assert result["terminal_count"] == 3
    assert result["started_count"] == 1
    assert result["not_started_count"] == 2
    assert result["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert result["failure_reason"] == "PROCESS_IDENTITY_PUBLICATION_FAILURE"


def _patch_fake_child_identity(monkeypatch, pilot_build, pid=424242, group_live=False):
    monkeypatch.setattr(pilot_build, "read_proc_starttime", lambda value: "99")
    monkeypatch.setattr(os, "getpgid", lambda value: pid)
    monkeypatch.setattr(os, "killpg", lambda pgid, sig: None)
    monkeypatch.setattr(pilot_build, "process_group_has_members", lambda pgid: group_live)


def test_timeout_retry_communicate_uses_final_cumulative_output_once(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    expected_out = b"partial\ntail\n"
    expected_err = b"error\nmore\n"
    duplicated_out = b"partial\npartial\ntail\n"
    duplicated_err = b"error\nerror\nmore\n"

    class FakeProc:
        pid = 424242
        returncode = None
        calls = 0

        def communicate(self, timeout=None):
            self.calls += 1
            if self.calls == 1:
                raise subprocess.TimeoutExpired(
                    ["fake"],
                    0.1,
                    output=b"partial\n",
                    stderr=b"error\n",
                )
            self.returncode = -9
            return expected_out, expected_err

        def poll(self):
            return None if self.calls < 2 else -9

        def wait(self, timeout=None):
            self.returncode = -9
            return -9

    _patch_fake_child_identity(monkeypatch, pilot_build)
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["fake-timeout"],
        "timeout_seconds": 900,
    }
    result = pilot_build.execute_job(
        spec,
        env={"PATH": "/usr/bin"},
        log_root=tmp_path / "logs",
        popen=lambda *args, **kwargs: FakeProc(),
        timeout_seconds=0.1,
    )
    raw_out = (tmp_path / "logs" / "CMAKE_CONFIGURE.stdout").read_bytes()
    raw_err = (tmp_path / "logs" / "CMAKE_CONFIGURE.stderr").read_bytes()
    assert result["terminal_status"] == "TIMEOUT"
    assert result["failure_reason"] == "TIMEOUT"
    assert result["process_started"] is True
    assert result["process_group_terminated"] is True
    assert raw_out == expected_out
    assert raw_err == expected_err
    assert raw_out != duplicated_out
    assert raw_err != duplicated_err
    assert result["stdout_sha256"] == _sha256_bytes(expected_out)
    assert result["stderr_sha256"] == _sha256_bytes(expected_err)
    assert result["stdout_bytes"] == len(expected_out)
    assert result["stderr_bytes"] == len(expected_err)


def test_timeout_falls_back_to_partial_output_when_final_collection_fails(
    tmp_path, monkeypatch
):
    import p3_v3.pilot_build as pilot_build

    partial_out = b"partial\n"
    partial_err = b"error\n"

    class FakeProc:
        pid = 424242
        returncode = None
        calls = 0

        def communicate(self, timeout=None):
            self.calls += 1
            raise subprocess.TimeoutExpired(
                ["fake"],
                0.1,
                output=partial_out,
                stderr=partial_err,
            )

        def poll(self):
            return None

        def wait(self, timeout=None):
            return None

    _patch_fake_child_identity(monkeypatch, pilot_build)
    monkeypatch.setattr(
        pilot_build,
        "terminate_and_reap_process_group",
        lambda *args, **kwargs: (None, None, False),
    )
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["fake-timeout-fallback"],
        "timeout_seconds": 900,
    }
    result = pilot_build.execute_job(
        spec,
        env={"PATH": "/usr/bin"},
        log_root=tmp_path / "logs",
        popen=lambda *args, **kwargs: FakeProc(),
        timeout_seconds=0.1,
    )
    raw_out = (tmp_path / "logs" / "CMAKE_CONFIGURE.stdout").read_bytes()
    raw_err = (tmp_path / "logs" / "CMAKE_CONFIGURE.stderr").read_bytes()
    assert result["terminal_status"] == "TIMEOUT"
    assert result["failure_reason"] == "TIMEOUT"
    assert raw_out == partial_out
    assert raw_err == partial_err
    assert raw_out != partial_out + partial_out
    assert result["stdout_sha256"] == _sha256_bytes(partial_out)
    assert result["stderr_sha256"] == _sha256_bytes(partial_err)
    assert result["stdout_bytes"] == len(partial_out)
    assert result["stderr_bytes"] == len(partial_err)


def test_log_cleanup_does_not_duplicate_cumulative_stdio(tmp_path, monkeypatch):
    from pathlib import Path as PathType

    import p3_v3.pilot_build as pilot_build

    expected_out = b"once\n"
    expected_err = b"err-once\n"

    class FakeProc:
        pid = 424242
        returncode = 0
        calls = 0

        def communicate(self, timeout=None):
            self.calls += 1
            return expected_out, expected_err

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

    _patch_fake_child_identity(monkeypatch, pilot_build, group_live=False)
    original = PathType.write_bytes
    seen = {"n": 0}

    def boom(self, data):
        if self.name.endswith(".stdout") or self.name.endswith(".stderr"):
            seen["n"] += 1
            if seen["n"] == 1:
                raise OSError("log publication failed")
        return original(self, data)

    monkeypatch.setattr(PathType, "write_bytes", boom)
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["fake-log"],
        "timeout_seconds": 900,
    }
    result = pilot_build.execute_job(
        spec,
        env={"PATH": "/usr/bin"},
        log_root=tmp_path / "logs",
        popen=lambda *args, **kwargs: FakeProc(),
    )
    raw_out = (tmp_path / "logs" / "CMAKE_CONFIGURE.stdout").read_bytes()
    raw_err = (tmp_path / "logs" / "CMAKE_CONFIGURE.stderr").read_bytes()
    assert result["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert result["failure_reason"] == "LOG_PUBLICATION_FAILURE"
    assert result["process_started"] is True
    assert raw_out == expected_out
    assert raw_err == expected_err
    assert raw_out != expected_out + expected_out
    assert result["stdout_sha256"] == _sha256_bytes(expected_out)
    assert result["stderr_sha256"] == _sha256_bytes(expected_err)
    assert result["stdout_bytes"] == len(expected_out)
    assert result["stderr_bytes"] == len(expected_err)


def test_process_group_leak_cleanup_does_not_duplicate_cumulative_stdio(
    tmp_path, monkeypatch
):
    import p3_v3.pilot_build as pilot_build

    first_out = b"parent-out\n"
    first_err = b"parent-err\n"
    final_out = b"parent-out\nchild-out\n"
    final_err = b"parent-err\nchild-err\n"

    class FakeProc:
        pid = 424242
        returncode = 0
        calls = 0

        def communicate(self, timeout=None):
            self.calls += 1
            if self.calls == 1:
                return first_out, first_err
            return final_out, final_err

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

    _patch_fake_child_identity(monkeypatch, pilot_build, group_live=True)
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["fake-leak"],
        "timeout_seconds": 900,
    }
    result = pilot_build.execute_job(
        spec,
        env={"PATH": "/usr/bin"},
        log_root=tmp_path / "logs",
        popen=lambda *args, **kwargs: FakeProc(),
    )
    raw_out = (tmp_path / "logs" / "CMAKE_CONFIGURE.stdout").read_bytes()
    raw_err = (tmp_path / "logs" / "CMAKE_CONFIGURE.stderr").read_bytes()
    assert result["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert result["failure_reason"] == "PROCESS_GROUP_LEAK"
    assert result["process_started"] is True
    assert result["process_group_terminated"] is True
    assert raw_out == final_out
    assert raw_err == final_err
    assert raw_out != first_out + final_out
    assert result["stdout_sha256"] == _sha256_bytes(final_out)
    assert result["stderr_sha256"] == _sha256_bytes(final_err)
    assert result["stdout_bytes"] == len(final_out)
    assert result["stderr_bytes"] == len(final_err)


def test_verbose_child_does_not_false_timeout_when_pipe_exceeds_capacity(tmp_path):
    import p3_v3.pilot_build as pilot_build

    payload_out = b"O" * (1024 * 1024)
    payload_err = b"E" * (1024 * 1024)
    script = (
        "import sys\n"
        f"sys.stdout.buffer.write(b'O' * {len(payload_out)})\n"
        "sys.stdout.buffer.flush()\n"
        f"sys.stderr.buffer.write(b'E' * {len(payload_err)})\n"
        "sys.stderr.buffer.flush()\n"
    )
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["python3", "-c", script],
        "timeout_seconds": 5,
    }
    result = pilot_build.execute_job(
        spec,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    raw_out = (tmp_path / "logs" / "CMAKE_CONFIGURE.stdout").read_bytes()
    raw_err = (tmp_path / "logs" / "CMAKE_CONFIGURE.stderr").read_bytes()
    assert result["terminal_status"] == "PASS"
    assert result["failure_reason"] is None
    assert result["timeout_seconds"] == 5
    assert isinstance(result["timeout_seconds"], int)
    assert raw_out == payload_out
    assert raw_err == payload_err
    assert result["stdout_bytes"] == len(payload_out)
    assert result["stderr_bytes"] == len(payload_err)
    assert result["stdout_sha256"] == _sha256_bytes(payload_out)
    assert result["stderr_sha256"] == _sha256_bytes(payload_err)


def test_preexisting_canonical_start_marker_refuses_second_spawn(tmp_path):
    from p3_v3.artifacts import write_canonical_json
    import p3_v3.pilot_build as pilot_build

    log_root = tmp_path / "logs"
    log_root.mkdir()
    marker = log_root / "CMAKE_CONFIGURE.start.json"
    payload = {
        "job_id": "CMAKE_CONFIGURE",
        "argv_sha256": "0" * 64,
        "created_at": "2026-08-18T00:00:00Z",
        "state": "STARTING",
    }
    write_canonical_json(marker, payload, exclusive=True)
    before = marker.read_bytes()
    inode = marker.stat().st_ino
    calls: list[object] = []

    def fake_popen(*_args, **_kwargs):
        calls.append(1)
        raise AssertionError("Popen must not run")

    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["python3", "-c", "print('no-spawn')"],
        "timeout_seconds": 900,
    }
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        pilot_build.execute_job(
            spec,
            env=dict(os.environ),
            log_root=log_root,
            popen=fake_popen,
        )
    assert calls == []
    names = sorted(path.name for path in log_root.iterdir())
    assert names == ["CMAKE_CONFIGURE.start.json"]
    assert marker.read_bytes() == before
    assert marker.stat().st_ino == inode


def test_preexisting_canonical_identity_marker_refuses_alternate_record(tmp_path):
    from p3_v3.artifacts import write_canonical_json
    import p3_v3.pilot_build as pilot_build

    log_root = tmp_path / "logs"
    log_root.mkdir()
    marker = log_root / "CMAKE_CONFIGURE.identity.json"
    payload = {
        "job_id": "CMAKE_CONFIGURE",
        "pid": 1,
        "pgid": 1,
        "starttime": "1",
        "argv_sha256": "0" * 64,
    }
    write_canonical_json(marker, payload, exclusive=True)
    before = marker.read_bytes()
    inode = marker.stat().st_ino
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["python3", "-c", "print('identity')"],
        "timeout_seconds": 900,
    }
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        pilot_build.write_process_identity(
            log_root,
            spec,
            pid=424242,
            pgid=424242,
            starttime="99",
            argv_sha256="a" * 64,
        )
    names = sorted(path.name for path in log_root.iterdir())
    assert names == ["CMAKE_CONFIGURE.identity.json"]
    assert marker.read_bytes() == before
    assert marker.stat().st_ino == inode


def test_job_result_rejects_fractional_timeout_seconds():
    import p3_v3.pilot_build as pilot_build

    payload = dict(pilot_build.make_not_started_job(pilot_build.JOB_SPECS[0]))
    payload["timeout_seconds"] = 0.2
    payload.pop("artifact_sha256", None)
    hashed = pilot_build._self_hash(payload)
    with pytest.raises(EvidenceError, match="E_SCHEMA_TYPE"):
        pilot_build.validate_job_result(hashed)
    assert hashed["timeout_seconds"] == 0.2


def test_benign_include_environment_is_not_system_boost():
    import p3_v3.pilot_build as pilot_build

    pilot_build.reject_system_boost_environment(
        {"CPATH": "/opt/project/include"}
    )
    pilot_build.reject_system_boost_environment(
        {"CPLUS_INCLUDE_PATH": "/opt/project/include"}
    )
    with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
        pilot_build.reject_system_boost_environment(
            {"CPATH": "/usr/include/boost"}
        )
    with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
        pilot_build.reject_system_boost_environment(
            {"BOOST_ROOT": "/opt/boost"}
        )


def test_dedicated_boost_environment_is_fail_closed_without_value_marker():
    import p3_v3.pilot_build as pilot_build

    pilot_build.reject_system_boost_environment(
        {"CPATH": "/opt/project/include"}
    )
    pilot_build.reject_system_boost_environment(
        {"CPLUS_INCLUDE_PATH": "/workspace/project/include"}
    )
    for env in (
        {"BOOST_ROOT": "/opt/vendor"},
        {"BOOST_INCLUDEDIR": "/opt/vendor/include"},
        {"Boost_DIR": "/opt/vendor/cmake"},
    ):
        with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
            pilot_build.reject_system_boost_environment(env)


def test_final_none_snapshot_preserves_previous_cumulative_output(
    tmp_path, monkeypatch
):
    import p3_v3.pilot_build as pilot_build

    earlier_out = b"EARLIER_STDOUT"
    earlier_err = b"EARLIER_STDERR"

    class FakeProc:
        pid = 424242
        returncode = None
        calls = 0

        def communicate(self, timeout=None):
            self.calls += 1
            if self.calls == 1:
                raise subprocess.TimeoutExpired(
                    ["fake-none-snapshot"],
                    1,
                    output=earlier_out,
                    stderr=earlier_err,
                )
            return (None, None)

        def poll(self):
            return None

        def wait(self, timeout=None):
            return None

    _patch_fake_child_identity(monkeypatch, pilot_build)
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["fake-none-snapshot"],
        "timeout_seconds": 900,
    }
    result = pilot_build.execute_job(
        spec,
        env={"PATH": "/usr/bin"},
        log_root=tmp_path / "logs",
        popen=lambda *args, **kwargs: FakeProc(),
        timeout_seconds=1,
    )
    raw_out = (tmp_path / "logs" / "CMAKE_CONFIGURE.stdout").read_bytes()
    raw_err = (tmp_path / "logs" / "CMAKE_CONFIGURE.stderr").read_bytes()
    assert result["timeout_seconds"] == 900
    assert isinstance(result["timeout_seconds"], int)
    assert raw_out == earlier_out
    assert raw_err == earlier_err
    assert raw_out != b""
    assert raw_err != b""
    assert result["stdout_bytes"] == len(earlier_out)
    assert result["stderr_bytes"] == len(earlier_err)
    assert result["stdout_sha256"] == _sha256_bytes(earlier_out)
    assert result["stderr_sha256"] == _sha256_bytes(earlier_err)


def test_process_group_membership_uses_pgrp_not_session(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    session_only = tmp_path / "11"
    session_only.mkdir()
    (session_only / "stat").write_text(
        "11 (sleep) S 1 999 4242 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n",
        encoding="utf-8",
    )
    pgrp_member = tmp_path / "22"
    pgrp_member.mkdir()
    (pgrp_member / "stat").write_text(
        "22 (sleep) S 1 4242 777 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n",
        encoding="utf-8",
    )
    original_iterdir = Path.iterdir

    def iter_session_only(self):
        if str(self) == "/proc":
            return iter([session_only])
        return original_iterdir(self)

    monkeypatch.setattr(pilot_build.Path, "iterdir", iter_session_only)
    assert pilot_build.process_group_has_members(4242) is False

    def iter_pgrp_member(self):
        if str(self) == "/proc":
            return iter([pgrp_member])
        return original_iterdir(self)

    monkeypatch.setattr(pilot_build.Path, "iterdir", iter_pgrp_member)
    assert pilot_build.process_group_has_members(4242) is True


def test_preexisting_identity_collision_is_started_failure_and_reaped(tmp_path):
    import time
    from p3_v3.artifacts import write_canonical_json
    import p3_v3.pilot_build as pilot_build

    log_root = tmp_path / "logs"
    log_root.mkdir()
    identity = log_root / "CMAKE_CONFIGURE.identity.json"
    payload = {
        "job_id": "CMAKE_CONFIGURE",
        "pid": 1,
        "pgid": 1,
        "starttime": "1",
        "argv_sha256": "0" * 64,
    }
    write_canonical_json(identity, payload, exclusive=True)
    before = identity.read_bytes()
    inode = identity.stat().st_ino
    seen: dict[str, int] = {}

    def wrapping_popen(*args, **kwargs):
        proc = subprocess.Popen(*args, **kwargs)
        seen["pid"] = proc.pid
        seen["pgid"] = os.getpgid(proc.pid)
        return proc

    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["python3", "-c", "import time; time.sleep(30)"],
        "timeout_seconds": 900,
    }
    result = pilot_build.execute_job(
        spec,
        env=dict(os.environ),
        log_root=log_root,
        popen=wrapping_popen,
        timeout_seconds=5,
    )
    assert result["process_started"] is True
    assert result["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert result["failure_reason"] == "PROCESS_IDENTITY_PUBLICATION_FAILURE"
    assert result["infrastructure_phase"] == "POST_PROCESS"
    assert result["process_group_terminated"] is True
    identities = sorted(log_root.glob("*.identity.json"))
    assert identities == [identity]
    assert identity.read_bytes() == before
    assert identity.stat().st_ino == inode
    deadline = time.monotonic() + 3
    gone = False
    while time.monotonic() < deadline:
        try:
            os.kill(seen["pid"], 0)
        except ProcessLookupError:
            gone = True
            break
        time.sleep(0.05)
    assert gone is True
    assert pilot_build.process_group_has_members(seen["pgid"]) is False
def test_attempt2_exact_schema_and_canonical_lf():
    from p3_v3 import pilot_build

    assert set(pilot_build.ATTEMPT2_ENVIRONMENT_EXACT) == {
        "schema_version", "execution_class", "denominator", "cmake_executable",
        "cmake_executable_path", "cmake_version", "cxx_compiler_executable",
        "cxx_compiler_path", "cxx_compiler_identity", "cxx_compiler_version",
        "cmake_generator", "os_name", "os_release", "python_version", "git_version",
        "build_parallelism", "nvcc_present", "native_profiling_present",
        "cuda_absence_blocking", "fetchcontent_fully_disconnected",
        "system_boost_fallback_accepted", "disconnected_environment",
        "qualification_evidence_sha256", "verification_scope", "executor_cloud_run_id",
        "executor_build_snapshot_id", "claims", "artifact_sha256",
    }
    assert pilot_build.canonical_json_bytes({"a": 1}).endswith(b"\n")


def _write_attempt2_v5_fixture(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    q = pilot_build.qualification_contract

    root = tmp_path / "qualification"
    root.mkdir()
    stdout, stderr = b"clang version 18\n", b""
    source, executable = q.SOURCE_BYTES, b"synthetic executable"
    host = q._self_hash({
        "schema_version": q.HOST_SCHEMA, "os_name": "Linux", "os_release": "test",
        "kernel_release": "test", "machine": "x86_64", "node_name": "test",
        "python_version": "3.12", "git_version": "git version synthetic",
        "repository_commit": pilot_build.QUALIFICATION_BASE_HEAD, "repository_clean": True,
        "requested_compiler": "c++", "resolved_compiler_path": pilot_build.FROZEN_CXX_PATH,
        "resolved_compiler_realpath": pilot_build.FROZEN_CXX_REALPATH,
        "resolved_path_regular": True, "resolved_path_symlink": True,
    })
    process_base = {
        "schema_version": q.PROCESS_SCHEMA, "execution_class": q.EXECUTION_CLASS,
        "claims": q.CLAIMS, "process_role": "WORKLOAD", "process_started": True,
        "terminal_status": "PASS", "failure_reason": None, "exit_code": 0,
        "started_at": "t0", "ended_at": "t1", "wall_seconds": 0.1,
        "process_group_terminated": False, "stdout_sha256": hashlib.sha256(b"").hexdigest(),
        "stderr_sha256": hashlib.sha256(b"").hexdigest(), "stdout_bytes": 0, "stderr_bytes": 0,
    }
    compile_job = q._self_hash({**process_base, "job_id": q.JOB_COMPILE,
        "argv": [pilot_build.FROZEN_CXX_PATH, "-std=c++14", f"{root}/qualify.cpp", "-o", f"{root}/qualify"],
        "timeout_seconds": 60})
    run_job = q._self_hash({**process_base, "job_id": q.JOB_RUN,
        "argv": [f"{root}/qualify"], "timeout_seconds": 10})
    metadata = q._self_hash({**process_base, "process_role": "METADATA", "job_id": q.JOB_METADATA,
        "argv": [pilot_build.FROZEN_CXX_PATH, "--version"], "timeout_seconds": 10,
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(), "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "stdout_bytes": len(stdout), "stderr_bytes": len(stderr)})
    intent = q._self_hash({
        "schema_version": q.INTENT_SCHEMA, "execution_class": q.EXECUTION_CLASS, "claims": q.CLAIMS,
        "formal_denominator_membership": False, "attempt_2_authorized": False, "no_retry": True,
        "repository_commit": pilot_build.QUALIFICATION_BASE_HEAD, "host_snapshot": host,
        "host_snapshot_sha256": host["artifact_sha256"], "spec_path": q.SPEC_PATH.as_posix(),
        "spec_sha256": q.SPEC_SHA256, "qualification_root": str(root), "requested_compiler": "c++",
        "resolved_compiler_path": pilot_build.FROZEN_CXX_PATH,
        "resolved_compiler_realpath": pilot_build.FROZEN_CXX_REALPATH,
        "source_text": q.SOURCE_TEXT, "source_sha256": hashlib.sha256(source).hexdigest(),
        "compile_link_argv": compile_job["argv"], "binary_run_argv": run_job["argv"],
        "compile_timeout_seconds": 60, "run_timeout_seconds": 10,
        "compiler_version_timeout_seconds": 10, "relevant_environment": {"PATH": "/usr/bin"},
    })
    intent_raw = pilot_build.canonical_json_bytes(intent)
    result = q._self_hash({
        "schema_version": q.RESULT_SCHEMA, "execution_class": q.EXECUTION_CLASS, "claims": q.CLAIMS,
        "formal_denominator_membership": False, "attempt_2_authorized": False, "no_retry": True,
        "intent_sha256": hashlib.sha256(intent_raw).hexdigest(),
        "repository_commit": pilot_build.QUALIFICATION_BASE_HEAD, "host_snapshot": host,
        "host_snapshot_sha256": host["artifact_sha256"], "spec_sha256": q.SPEC_SHA256,
        "compiler_version": metadata, "jobs": [compile_job, run_job],
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "executable_sha256": hashlib.sha256(executable).hexdigest(), "executable_bytes": len(executable),
        "executable_regular": True, "executable_symlink": False,
        "terminal_status": "PASS", "failure_reason": None,
    })
    named = {
        pilot_build.QUALIFICATION_INTENT_NAME: intent_raw,
        pilot_build.QUALIFICATION_RESULT_NAME: pilot_build.canonical_json_bytes(result),
        pilot_build.QUALIFICATION_SOURCE_NAME: source,
        pilot_build.QUALIFICATION_EXECUTABLE_NAME: executable,
        pilot_build.QUALIFICATION_CXX_STDOUT_NAME: stdout,
        pilot_build.QUALIFICATION_CXX_STDERR_NAME: stderr,
        "CXX_COMPILE_LINK.stdout": b"",
        "CXX_COMPILE_LINK.stderr": b"",
        "QUALIFIED_BINARY_RUN.stdout": b"",
        "QUALIFIED_BINARY_RUN.stderr": b"",
    }
    manifest = q._self_hash({
        "schema_version": q.MANIFEST_SCHEMA, "execution_class": q.EXECUTION_CLASS, "claims": q.CLAIMS,
        "formal_denominator_membership": False, "attempt_2_authorized": False, "no_retry": True,
        "intent_sha256": hashlib.sha256(intent_raw).hexdigest(),
        "result_sha256": hashlib.sha256(named[pilot_build.QUALIFICATION_RESULT_NAME]).hexdigest(),
        "files": [{"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
                  for name, raw in sorted(named.items())],
    })
    named[pilot_build.QUALIFICATION_MANIFEST_NAME] = pilot_build.canonical_json_bytes(manifest)
    for name, raw in named.items():
        (root / name).write_bytes(raw)
    monkeypatch.setattr(pilot_build, "QUALIFICATION_FIXED_HASHES", {
        name: hashlib.sha256(named[name]).hexdigest() for name in (
            pilot_build.QUALIFICATION_INTENT_NAME, pilot_build.QUALIFICATION_RESULT_NAME,
            pilot_build.QUALIFICATION_MANIFEST_NAME, pilot_build.QUALIFICATION_SOURCE_NAME,
            pilot_build.QUALIFICATION_EXECUTABLE_NAME)})
    monkeypatch.setattr(pilot_build.os.path, "realpath", lambda path: pilot_build.FROZEN_CXX_REALPATH)
    return root, named


def _read_json_object(path: Path):
    return json.loads(path.read_bytes())


def _rewrite_v5_result_and_manifest(root, monkeypatch, mutate_result):
    """Rewrite a result and every dependent manifest/frozen hash canonically."""
    from p3_v3 import pilot_build
    q = pilot_build.qualification_contract

    result_path = root / pilot_build.QUALIFICATION_RESULT_NAME
    result = _read_json_object(result_path)
    mutate_result(result)
    result = q._self_hash(result)
    result_raw = pilot_build.canonical_json_bytes(result)
    result_path.write_bytes(result_raw)

    manifest_path = root / pilot_build.QUALIFICATION_MANIFEST_NAME
    manifest = _read_json_object(manifest_path)
    result_digest = hashlib.sha256(result_raw).hexdigest()
    manifest["result_sha256"] = result_digest
    for entry in manifest["files"]:
        if entry["path"] == pilot_build.QUALIFICATION_RESULT_NAME:
            entry["sha256"] = result_digest
            entry["bytes"] = len(result_raw)
    manifest = q._self_hash(manifest)
    manifest_raw = pilot_build.canonical_json_bytes(manifest)
    manifest_path.write_bytes(manifest_raw)
    monkeypatch.setitem(
        pilot_build.QUALIFICATION_FIXED_HASHES,
        pilot_build.QUALIFICATION_RESULT_NAME,
        result_digest,
    )
    monkeypatch.setitem(
        pilot_build.QUALIFICATION_FIXED_HASHES,
        pilot_build.QUALIFICATION_MANIFEST_NAME,
        hashlib.sha256(manifest_raw).hexdigest(),
    )


def test_attempt2_v5_adapter_complete_success_and_no_process(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    root, named = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    for forbidden in ("Popen", "run", "check_output"):
        monkeypatch.setattr(pilot_build.subprocess, forbidden, lambda *a, **k: pytest.fail("process ran"))
    monkeypatch.setattr(pilot_build.os, "system", lambda *a, **k: pytest.fail("process ran"))
    for probe_name in ("probe_identity", "make_environment_snapshot"):
        if hasattr(pilot_build, probe_name):
            monkeypatch.setattr(
                pilot_build, probe_name,
                lambda *a, **k: pytest.fail("probe or environment snapshot ran"),
            )
    evidence = pilot_build.read_v5_qualification_evidence(root)
    assert evidence["execution_class"] == "PILOT_ONLY"
    assert evidence["claims"] == "blocked"
    assert evidence["terminal_status"] == "PASS"
    assert evidence["failure_reason"] is None
    assert set(evidence) == set(pilot_build.ATTEMPT2_QUALIFICATION_EVIDENCE_EXACT)
    assert evidence["requested_compiler"] == "c++"
    assert evidence["qualification_root"] == str(root)
    assert evidence["artifact_sha256"] == pilot_build.canonical_sha256(
        {k: v for k, v in evidence.items() if k != "artifact_sha256"})


def test_attempt2_v5_adapter_undeclared_extra_root_entry_rejected(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    (root / "undeclared.log").write_bytes(b"extra")
    with pytest.raises(EvidenceError):
        pilot_build.read_v5_qualification_evidence(root)


def test_attempt2_v5_adapter_declared_workload_log_tamper_rejected(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    (root / "CXX_COMPILE_LINK.stdout").write_bytes(b"tampered")
    with pytest.raises(EvidenceError):
        pilot_build.read_v5_qualification_evidence(root)


@pytest.mark.parametrize("name", [
    "qualification-intent.json", "qualification-result.json", "qualification-manifest.json",
    "qualify.cpp", "qualify", "METADATA_CXX_VERSION.stdout", "METADATA_CXX_VERSION.stderr",
    "CXX_COMPILE_LINK.stdout", "CXX_COMPILE_LINK.stderr",
    "QUALIFIED_BINARY_RUN.stdout", "QUALIFIED_BINARY_RUN.stderr",
])
def test_attempt2_v5_adapter_each_missing_rejected(tmp_path, monkeypatch, name):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    (root / name).unlink()
    with pytest.raises(EvidenceError):
        pilot_build.read_v5_qualification_evidence(root)


def test_attempt2_v5_adapter_frozen_file_hash_mismatch_rejected(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    monkeypatch.setitem(pilot_build.QUALIFICATION_FIXED_HASHES, pilot_build.QUALIFICATION_SOURCE_NAME, "0" * 64)
    with pytest.raises(EvidenceError):
        pilot_build.read_v5_qualification_evidence(root)


def test_attempt2_v5_adapter_noncanonical_core_json_rejected(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    path = root / pilot_build.QUALIFICATION_INTENT_NAME
    noncanonical = json.dumps(_read_json_object(path), indent=2).encode() + b"\n"
    path.write_bytes(noncanonical)
    monkeypatch.setitem(
        pilot_build.QUALIFICATION_FIXED_HASHES,
        pilot_build.QUALIFICATION_INTENT_NAME,
        hashlib.sha256(noncanonical).hexdigest(),
    )
    with pytest.raises(EvidenceError, match="not one canonical JSON object"):
        pilot_build.read_v5_qualification_evidence(root)


def test_attempt2_v5_adapter_evidence_file_symlink_rejected(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    root, named = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    target = tmp_path / "outside"
    target.write_bytes(named[pilot_build.QUALIFICATION_CXX_STDERR_NAME])
    (root / pilot_build.QUALIFICATION_CXX_STDERR_NAME).unlink()
    (root / pilot_build.QUALIFICATION_CXX_STDERR_NAME).symlink_to(target)
    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_PATH.*path is not symlink-free"):
        pilot_build.read_v5_qualification_evidence(root)


def test_attempt2_v5_adapter_qualification_root_symlink_rejected(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    actual = tmp_path / "qualification-actual"
    root.rename(actual)
    root.symlink_to(actual, target_is_directory=True)
    with pytest.raises(EvidenceError, match="qualification root is unsafe"):
        pilot_build.read_v5_qualification_evidence(root)


def test_attempt2_v5_adapter_current_compiler_realpath_mismatch_rejected(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(pilot_build.os.path, "realpath", lambda path: "/different/c++")
    with pytest.raises(EvidenceError, match="current compiler differs"):
        pilot_build.read_v5_qualification_evidence(root)


def test_attempt2_v5_adapter_host_snapshot_cross_link_mismatch_rejected(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)

    def mutate(result):
        host = dict(result["host_snapshot"])
        host["node_name"] = "different-host"
        host = pilot_build.qualification_contract._self_hash(host)
        result["host_snapshot"] = host
        result["host_snapshot_sha256"] = host["artifact_sha256"]

    _rewrite_v5_result_and_manifest(root, monkeypatch, mutate)
    with pytest.raises(EvidenceError, match="host snapshot differs"):
        pilot_build.read_v5_qualification_evidence(root)


@pytest.mark.parametrize("log_name", [
    "METADATA_CXX_VERSION.stdout", "METADATA_CXX_VERSION.stderr",
])
def test_attempt2_v5_adapter_compiler_version_raw_log_mismatch_rejected(
    tmp_path, monkeypatch, log_name
):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    raw = b"different compiler metadata\n"
    (root / log_name).write_bytes(raw)
    manifest_path = root / pilot_build.QUALIFICATION_MANIFEST_NAME
    manifest = _read_json_object(manifest_path)
    for entry in manifest["files"]:
        if entry["path"] == log_name:
            entry["sha256"] = hashlib.sha256(raw).hexdigest()
            entry["bytes"] = len(raw)
    manifest = pilot_build.qualification_contract._self_hash(manifest)
    manifest_raw = pilot_build.canonical_json_bytes(manifest)
    manifest_path.write_bytes(manifest_raw)
    monkeypatch.setitem(
        pilot_build.QUALIFICATION_FIXED_HASHES,
        pilot_build.QUALIFICATION_MANIFEST_NAME,
        hashlib.sha256(manifest_raw).hexdigest(),
    )
    with pytest.raises(EvidenceError, match="compiler version output differs"):
        pilot_build.read_v5_qualification_evidence(root)


@pytest.mark.parametrize("link_name", ["intent_sha256", "result_sha256"])
def test_attempt2_v5_adapter_manifest_cross_link_mismatch_rejected(
    tmp_path, monkeypatch, link_name
):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    manifest_path = root / pilot_build.QUALIFICATION_MANIFEST_NAME
    manifest = _read_json_object(manifest_path)
    manifest[link_name] = "0" * 64
    manifest = pilot_build.qualification_contract._self_hash(manifest)
    raw = pilot_build.canonical_json_bytes(manifest)
    manifest_path.write_bytes(raw)
    monkeypatch.setitem(
        pilot_build.QUALIFICATION_FIXED_HASHES,
        pilot_build.QUALIFICATION_MANIFEST_NAME,
        hashlib.sha256(raw).hexdigest(),
    )
    with pytest.raises(EvidenceError, match="manifest cross-link differs"):
        pilot_build.read_v5_qualification_evidence(root)


def test_attempt2_v5_adapter_non_pass_result_rejected(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)

    def mutate(result):
        result["terminal_status"] = "FAIL"
        result["failure_reason"] = "SYNTHETIC_FAILURE"

    _rewrite_v5_result_and_manifest(root, monkeypatch, mutate)
    with pytest.raises(EvidenceError, match="qualification is not PASS"):
        pilot_build.read_v5_qualification_evidence(root)


def test_attempt2_v5_adapter_missing_evidence_fails_without_process(tmp_path, monkeypatch):
    from p3_v3 import pilot_build

    monkeypatch.setattr(pilot_build.subprocess, "Popen", lambda *a, **k: pytest.fail("process ran"))
    with pytest.raises(EvidenceError):
        pilot_build.read_v5_qualification_evidence(tmp_path)


def test_implementation_verdict_exact_has_seven_reviewed_blobs():
    from p3_v3 import pilot_build

    assert set(pilot_build.ATTEMPT2_IMPLEMENTATION_VERDICT_REVIEWED_BLOB_EXACT) == {
        "rejected_plan_v1", "src/p3_v3/pilot_source.py", "src/p3_v3/pilot_build.py",
        "scripts/p3_v3/pilot.py", "tests/p3_v3/test_pilot_source.py",
        "tests/p3_v3/test_pilot_build.py", "tests/p3_v3/test_pilot.py",
    }


def test_attempt2_archive_update_binds_current_design_and_plan():
    from p3_v3 import pilot_build

    expected_plan = Path(
        "docs/superpowers/plans/"
        "2026-08-26-p3-boost-math-attempt2-archive-contract-update.md"
    )
    assert pilot_build.ATTEMPT2_APPROVED_PLAN_PATH == expected_plan
    for field, (path, expected_sha256) in pilot_build.ATTEMPT2_AUTHORITY_HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha256, field


def _write_attempt2_verdict_fixture(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    authority_hashes = {}
    for index, key in enumerate(pilot_build.ATTEMPT2_AUTHORITY_HASHES):
        path = tmp_path / f"authority-{index}"
        path.write_bytes(f"authority-{key}\n".encode())
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        authority_hashes[key] = (path, digest)
    monkeypatch.setattr(pilot_build, "ATTEMPT2_AUTHORITY_HASHES", authority_hashes)
    reviewed = {}
    reviewed_hashes = {}
    for index, key in enumerate(pilot_build.ATTEMPT2_REVIEWED_FILES):
        path = tmp_path / f"reviewed-{index}"
        path.write_bytes(f"reviewed-{key}\n".encode())
        reviewed[key] = path
        reviewed_hashes[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setattr(pilot_build, "ATTEMPT2_REVIEWED_FILES", reviewed)
    monkeypatch.setattr(pilot_build, "ATTEMPT2_REJECTED_PLAN_V1_SHA256", reviewed_hashes["rejected_plan_v1"])
    payload = {
        "schema_version": pilot_build.ATTEMPT2_IMPLEMENTATION_VERDICT_SCHEMA,
        "verdict": "PASS", "reviewed_commit": "a" * 40,
        "qualification_base_head": pilot_build.QUALIFICATION_BASE_HEAD,
        **{key: digest for key, (_path, digest) in authority_hashes.items()},
        "reviewed_blob_sha256": reviewed_hashes,
        "formal_denominator_membership": False, "claims": "blocked",
        "attempt_2_authorized": False, "rq4_supported": False,
    }
    payload["artifact_sha256"] = pilot_build.canonical_sha256(payload)
    path = tmp_path / "verdict.json"
    path.write_bytes(pilot_build.canonical_json_bytes(payload))
    return path, payload


def test_attempt2_implementation_verdict_exact_success_returns_observed_hash(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    path, expected = _write_attempt2_verdict_fixture(tmp_path, monkeypatch)
    verdict, observed = pilot_build.read_attempt2_implementation_verdict(path)
    assert verdict == expected
    assert observed == hashlib.sha256(path.read_bytes()).hexdigest()
    # The Attempt-1 contract and validator remain the original independent seam.
    assert "reviewed_plan_path" in pilot_build.IMPLEMENTATION_VERDICT_EXACT
    assert callable(pilot_build.validate_implementation_verdict)


@pytest.mark.parametrize("field,value", [
    ("schema_version", "wrong"), ("verdict", "FAIL"), ("reviewed_commit", "A" * 40),
    ("qualification_base_head", "b" * 40), ("claims", "open"),
    ("formal_denominator_membership", True), ("attempt_2_authorized", True),
    ("rq4_supported", True), ("artifact_sha256", "0" * 64),
])
def test_attempt2_implementation_verdict_exact_rejects_constraints(tmp_path, monkeypatch, field, value):
    from p3_v3 import pilot_build
    _path, payload = _write_attempt2_verdict_fixture(tmp_path, monkeypatch)
    payload[field] = value
    if field != "artifact_sha256":
        payload["artifact_sha256"] = pilot_build.canonical_sha256(
            {key: item for key, item in payload.items() if key != "artifact_sha256"})
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_implementation_verdict(payload)


def test_attempt2_implementation_verdict_exact_rejects_keys(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    path, payload = _write_attempt2_verdict_fixture(tmp_path, monkeypatch)
    missing = dict(payload)
    missing.pop("claims")
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_implementation_verdict(missing)
    extra = dict(payload, invented=False)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_implementation_verdict(extra)


def test_attempt2_implementation_verdict_exact_rejects_ordinary_reviewed_file_drift(
    tmp_path, monkeypatch
):
    from p3_v3 import pilot_build
    path, _ = _write_attempt2_verdict_fixture(tmp_path, monkeypatch)
    reviewed_path = pilot_build.ATTEMPT2_REVIEWED_FILES["scripts/p3_v3/pilot.py"]
    reviewed_path.write_bytes(b"drift\n")
    with pytest.raises(EvidenceError):
        pilot_build.read_attempt2_implementation_verdict(path)


def test_attempt2_implementation_verdict_exact_rejects_authority_design_file_drift(
    tmp_path, monkeypatch
):
    from p3_v3 import pilot_build
    path, _ = _write_attempt2_verdict_fixture(tmp_path, monkeypatch)
    authority_path, _frozen_hash = pilot_build.ATTEMPT2_AUTHORITY_HASHES["v2_design_sha256"]
    authority_path.write_bytes(b"authority design drift\n")
    with pytest.raises(EvidenceError, match="v2_design_sha256 differs"):
        pilot_build.read_attempt2_implementation_verdict(path)
def test_attempt2_descriptor_dependency_and_environment():
    from p3_v3 import pilot_build

    specs = pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")
    assert [s["phase_id"] for s in specs] == [
        "METADATA_CMAKE_VERSION", "SOURCE_RESTORE", "CMAKE_CONFIGURE",
        "BASELINE_BUILD", "BASELINE_SMOKE",
    ]
    assert [s["dependency_phase_ids"] for s in specs] == [
        [], ["METADATA_CMAKE_VERSION"], ["SOURCE_RESTORE"],
        ["CMAKE_CONFIGURE"], ["BASELINE_BUILD"],
    ]
    assert all(isinstance(arg, str) for spec in specs for arg in spec["argv"])
    assert specs[1]["argv"] == [] and specs[1]["timeout_seconds"] == 0

    assert [s["timeout_seconds"] for s in specs] == [10, 0, 900, 3600, 1800]
    assert specs[0]["argv"] == ["/usr/bin/cmake", "--version"]
    assert specs[2]["argv"] == [
        "/usr/bin/cmake", "-S", str(pilot_build.ATTEMPT2_HARNESS_ROOT),
        "-B", str(pilot_build.ATTEMPT2_BUILD_ROOT), "-G", "Unix Makefiles",
        "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_CXX_STANDARD=14",
        "-DCMAKE_CXX_STANDARD_REQUIRED=ON", "-DBOOST_MATH_STANDALONE=1",
        "-DBOOST_MATH_PILOT_SOURCE_INCLUDE=/tmp/p3-boost-math-pilot-production-source/include",
        "-DCMAKE_DISABLE_SOURCE_CHANGES=ON", "-DCMAKE_DISABLE_IN_SOURCE_BUILD=ON",
        "-DFETCHCONTENT_FULLY_DISCONNECTED=ON", "-DFETCHCONTENT_UPDATES_DISCONNECTED=ON",
        "-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF",
        "-DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF",
        "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON", "-DCMAKE_CXX_COMPILER=/usr/bin/c++",
    ]
    assert specs[3]["argv"] == ["/usr/bin/cmake", "--build", str(pilot_build.ATTEMPT2_BUILD_ROOT), "--parallel", "4"]
    assert specs[4]["argv"] == [str(pilot_build.ATTEMPT2_BUILD_ROOT / "boost_math_pilot_smoke")]
    with pytest.raises(EvidenceError):
        pilot_build.attempt2_phase_descriptors("cmake")


def test_attempt2_execute_job_uses_existing_callable():
    from p3_v3 import pilot_build

    assert callable(pilot_build.execute_job)
    assert pilot_build.ATTEMPT2_LOG_ROOT == pilot_build.ATTEMPT2_BUILD_ROOT / "logs"


def test_attempt2_execute_job_metadata_processes_copied_environment(tmp_path, monkeypatch):
    from p3_v3 import pilot_build

    original = {"PRESERVED": "yes"}
    monkeypatch.setattr(pilot_build.os, "environ", original)
    calls = []
    monkeypatch.setattr(pilot_build, "reject_system_boost_environment", lambda env: env.update(SEEN_BOOST="1"))
    monkeypatch.setattr(pilot_build, "reject_unbound_toolchain", lambda env, cxx: env.update(SEEN_CXX=cxx))
    sentinel = {"sentinel": True}
    monkeypatch.setattr(pilot_build, "execute_job", lambda spec, **kwargs: calls.append((spec, kwargs)) or sentinel)
    monkeypatch.setattr(pilot_build.subprocess, "run", lambda *a, **k: pytest.fail("subprocess.run used"))
    monkeypatch.setattr(pilot_build.subprocess, "check_output", lambda *a, **k: pytest.fail("check_output used"))
    monkeypatch.setattr(pilot_build.os, "system", lambda *a, **k: pytest.fail("os.system used"))
    assert pilot_build.run_metadata_cmake_version("/opt/cmake", tmp_path) is sentinel
    assert len(calls) == 1
    spec, kwargs = calls[0]
    assert spec == {"job_id": "METADATA_CMAKE_VERSION", "job_kind": "METADATA_CMAKE_VERSION",
                    "dependency_job_ids": [], "argv": ["/opt/cmake", "--version"], "timeout_seconds": 10}
    assert kwargs["log_root"] == tmp_path
    assert "cwd" not in kwargs
    assert kwargs["env"] is not original and original == {"PRESERVED": "yes"}
    assert kwargs["env"] == {"PRESERVED": "yes", "SEEN_BOOST": "1", "SEEN_CXX": "/usr/bin/c++",
                              **pilot_build.DISCONNECTED_ENVIRONMENT}
def test_attempt2_orchestration_publication_preexisting_is_permanent(tmp_path, monkeypatch):
    from p3_v3 import pilot_build

    intent = tmp_path / "intent.json"
    intent.write_text("{}\n")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_INTENT_PATH", intent)
    monkeypatch.setattr(pilot_build, "ATTEMPT2_RESULT_PATH", tmp_path / "result.json")
    with pytest.raises(EvidenceError, match="E_PILOT_ATTEMPT2_PREEXISTING"):
        pilot_build.run_build_preflight_attempt_2(
            pilot_build.ATTEMPT2_ARCHIVE_PATH, pilot_build.ATTEMPT2_SOURCE_ROOT,
            pilot_build.ATTEMPT2_BUILD_ROOT,
        )


def test_attempt2_not_started_phase_has_no_process_evidence():
    from p3_v3 import pilot_build

    phase = pilot_build.make_attempt2_not_started(
        pilot_build.attempt2_phase_descriptors("/cmake")[-1]
    )
    assert phase["terminal_status"] == "NOT_STARTED"
    assert phase["process_started"] is False
    assert phase["exit_code"] is None and phase["started_at"] is None


def _attempt2_environment_fixture(pilot_build, cmake_version="cmake version 3.28.3"):
    value = {"schema_version": pilot_build.ATTEMPT2_ENVIRONMENT_SCHEMA,
        "execution_class": "PILOT_ONLY", "denominator": "PILOT_ONLY",
        "cmake_executable": "cmake", "cmake_executable_path": "/usr/bin/cmake",
        "cmake_version": cmake_version, "cxx_compiler_executable": "c++",
        "cxx_compiler_path": pilot_build.FROZEN_CXX_PATH,
        "cxx_compiler_identity": "clang", "cxx_compiler_version": "18.0.0",
        "cmake_generator": "Unix Makefiles", "os_name": "Linux", "os_release": "synthetic",
        "python_version": "3.11", "git_version": "git version synthetic",
        "build_parallelism": 4, "nvcc_present": False, "native_profiling_present": False,
        "cuda_absence_blocking": False, "fetchcontent_fully_disconnected": True,
        "system_boost_fallback_accepted": False,
        "disconnected_environment": dict(pilot_build.DISCONNECTED_ENVIRONMENT),
        "qualification_evidence_sha256": "1" * 64,
        "verification_scope": "ARTIFACT_HASH_AND_HOST_SNAPSHOT",
        "executor_cloud_run_id": None, "executor_build_snapshot_id": None, "claims": "blocked"}
    value["artifact_sha256"] = pilot_build.canonical_sha256(value)
    return value


def _attempt2_phase_fixture(pilot_build, descriptor, status="PASS"):
    value = {"schema_version": pilot_build.ATTEMPT2_PHASE_SCHEMA, "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY", **descriptor, "process_started": True,
        "process_group_terminated": False, "infrastructure_phase": None,
        "terminal_status": status, "failure_reason": None, "exit_code": 0,
        "stdout_sha256": "2" * 64, "stderr_sha256": "3" * 64,
        "stdout_bytes": 1, "stderr_bytes": 0, "started_at": "2026-01-01T00:00:00Z",
        "ended_at": "2026-01-01T00:00:01Z", "wall_seconds": 1.0,
        "cpu_seconds": 0.1, "peak_rss_bytes": 1, "source_restoration_evidence": None,
        "claims": "blocked"}
    if status == "NOT_STARTED":
        value.update(process_started=False, process_group_terminated=None,
            infrastructure_phase=None, failure_reason=None, exit_code=None,
            stdout_sha256=None, stderr_sha256=None, stdout_bytes=None, stderr_bytes=None,
            started_at=None, ended_at=None, wall_seconds=None, cpu_seconds=None,
            peak_rss_bytes=None, source_restoration_evidence=None)
    elif descriptor["phase_id"] == "SOURCE_RESTORE":
        from p3_v3 import pilot_source
        evidence = {"schema_version": pilot_source.SOURCE_RESTORATION_SCHEMA,
            "execution_class": "PILOT_ONLY", "claims": "blocked", "disposition": "REVALIDATED",
            "archive_sha256": pilot_source.ATTEMPT2_ARCHIVE_SHA256,
            "archive_bytes": pilot_source.ATTEMPT2_ARCHIVE_BYTES,
            "normalized_tree_sha256": pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
            "materialized_file_count": 4396,
            "materialized_total_bytes": 95635487,
            "staging_published": False, "root_published": False,
            "started_at": "2026-01-01T00:00:00Z", "ended_at": "2026-01-01T00:00:01Z",
            "terminal_status": status,
            "failure_reason": None if status == "PASS" else "TREE_HASH_MISMATCH"}
        if status == "FAIL":
            evidence.update(disposition="NOT_APPLIED", staging_published=False,
                root_published=False)
        evidence["artifact_sha256"] = pilot_build.canonical_sha256(evidence)
        value.update(process_started=False, process_group_terminated=None, exit_code=None,
            stdout_sha256=None, stderr_sha256=None, stdout_bytes=None, stderr_bytes=None,
            started_at=None, ended_at=None, wall_seconds=None, cpu_seconds=None,
            peak_rss_bytes=None, source_restoration_evidence=evidence)
        value["failure_reason"] = evidence["failure_reason"]
    elif status == "FAIL":
        value.update(failure_reason="NONZERO_EXIT", exit_code=1)
    elif status == "TIMEOUT":
        value.update(failure_reason="TIMEOUT", exit_code=None,
            process_group_terminated=True)
    elif status == "FAIL_INFRASTRUCTURE":
        value.update(process_started=False, process_group_terminated=None,
            infrastructure_phase="PRE_PROCESS", failure_reason="MISSING_DEPENDENCY",
            exit_code=None, stdout_sha256=None, stderr_sha256=None, stdout_bytes=None,
            stderr_bytes=None, started_at=None, ended_at=None, wall_seconds=None,
            cpu_seconds=None, peak_rss_bytes=None)
    value["artifact_sha256"] = pilot_build.canonical_sha256(value)
    return value


def _attempt2_result_fixture(pilot_build, statuses=None, root=(True, False)):
    statuses = statuses or ["PASS"] * 5
    descriptors = pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")
    phases = []
    for descriptor, status in zip(descriptors, statuses, strict=True):
        phases.append(pilot_build.make_attempt2_not_started(descriptor) if status == "NOT_STARTED"
                      else _attempt2_phase_fixture(pilot_build, descriptor, status))
    environment = _attempt2_environment_fixture(
        pilot_build, None if statuses[0] != "PASS" else "cmake version 3.28.3")
    fixed = {"schema_version": pilot_build.ATTEMPT2_RESULT_SCHEMA, "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY", "p12_item_id": pilot_build.P12_ITEM_ID,
        "neutral_snapshot_id": pilot_build.NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": pilot_build.FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
        "controlled_subject_id": pilot_build.CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": pilot_build.CONTROLLED_SUBJECT_SOURCE_ID,
        "build_descriptor_sha256": pilot_build.BUILD_DESCRIPTOR_SHA256,
        "source_preparation_verdict_sha256": pilot_build.SOURCE_PREPARATION_RESULT_VERDICT_SHA256,
        "source_manifest_sha256": pilot_build.SOURCE_MANIFEST_FILE_SHA256,
        "source_preparation_result_sha256": pilot_build.SOURCE_PREPARATION_RESULT_FILE_SHA256,
        "attempt1_implementation_verdict_sha256": "4" * 64,
        "attempt2_implementation_verdict_sha256": "5" * 64, "intent_sha256": "6" * 64,
        "authorization_sha256": "7" * 64, "qualification_base_head": pilot_build.QUALIFICATION_BASE_HEAD,
        "qualification_evidence_sha256": "1" * 64, "environment_snapshot": environment,
        "environment_snapshot_sha256": environment["artifact_sha256"],
        "harness_cmake_sha256": pilot_build.HARNESS_CMAKE_SHA256,
        "harness_cxx_sha256": pilot_build.HARNESS_CXX_SHA256,
        "source_root": str(pilot_build.ATTEMPT2_SOURCE_ROOT), "build_root": str(pilot_build.ATTEMPT2_BUILD_ROOT),
        "harness_root": str(pilot_build.ATTEMPT2_HARNESS_ROOT), "log_root": str(pilot_build.ATTEMPT2_LOG_ROOT),
        "archive_path": str(pilot_build.ATTEMPT2_ARCHIVE_PATH), "planned_count": 5,
        "started_count": sum(p["process_started"] for p in phases),
        "terminal_count": sum(p["terminal_status"] != "NOT_STARTED" for p in phases),
        "not_started_count": sum(p["terminal_status"] == "NOT_STARTED" for p in phases),
        "phase_order": [d["phase_id"] for d in descriptors], "phases": phases,
        "source_restoration_disposition": (phases[1]["source_restoration_evidence"]["disposition"]
            if phases[1]["terminal_status"] != "NOT_STARTED" else None),
        "terminal_status": next((p["terminal_status"] for p in phases if p["terminal_status"] != "PASS"), "PASS"),
        "failure_reason": next((p["failure_reason"] for p in phases if p["terminal_status"] != "PASS"), None),
        "build_root_exists": root[0], "build_root_is_symlink": root[1], "no_retry": True,
        "claims": "blocked", "formal_denominator_membership": False, "rq4_supported": False,
        "attempt_2_authorized": False, "verification_scope": "ARTIFACT_HASH_AND_HOST_SNAPSHOT",
        "executor_cloud_run_id": None, "executor_build_snapshot_id": None}
    fixed.update(cmake_cache_sha256="8" * 64 if statuses[3] == "PASS" else None,
        compile_commands_sha256="9" * 64 if statuses[3] == "PASS" else None,
        compiler_depfile_sha256="a" * 64 if statuses[3] == "PASS" else None,
        dependency_list_sha256="b" * 64 if statuses[3] == "PASS" else None,
        smoke_executable_sha256="c" * 64 if statuses[3] == "PASS" else None)
    required = [fixed[k] for k in ("intent_sha256", "attempt1_implementation_verdict_sha256",
        "attempt2_implementation_verdict_sha256", "authorization_sha256", "qualification_evidence_sha256",
        "source_preparation_verdict_sha256", "source_manifest_sha256",
        "source_preparation_result_sha256", "environment_snapshot_sha256")]
    fixed["predecessor_sha256"] = sorted(required)
    fixed["artifact_sha256"] = pilot_build.canonical_sha256(fixed)
    return fixed


def _attempt2_intent_fixture(pilot_build):
    """Construct the closed pre-metadata intent without consulting the host."""
    environment = _attempt2_environment_fixture(pilot_build, None)
    descriptors = pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")
    value = {"schema_version": pilot_build.ATTEMPT2_INTENT_SCHEMA,
        "execution_class": "PILOT_ONLY", "denominator": "PILOT_ONLY",
        "plan_class": "PILOT_BUILD_PREFLIGHT_ATTEMPT_2_ONLY",
        "p12_item_id": pilot_build.P12_ITEM_ID, "neutral_snapshot_id": pilot_build.NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": pilot_build.FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
        "controlled_subject_id": pilot_build.CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": pilot_build.CONTROLLED_SUBJECT_SOURCE_ID,
        "build_descriptor_sha256": pilot_build.BUILD_DESCRIPTOR_SHA256,
        "source_preparation_verdict_sha256": pilot_build.SOURCE_PREPARATION_RESULT_VERDICT_SHA256,
        "source_manifest_sha256": pilot_build.SOURCE_MANIFEST_FILE_SHA256,
        "source_preparation_result_sha256": pilot_build.SOURCE_PREPARATION_RESULT_FILE_SHA256,
        "source_preparation_reviewed_commit": pilot_build.SOURCE_PREPARATION_REVIEWED_COMMIT,
        "attempt1_implementation_verdict_sha256": "4" * 64,
        "attempt2_implementation_verdict_sha256": "5" * 64,
        "authorization_sha256": "7" * 64,
        "harness_cmake_sha256": pilot_build.HARNESS_CMAKE_SHA256,
        "harness_cxx_sha256": pilot_build.HARNESS_CXX_SHA256,
        "source_root": str(pilot_build.ATTEMPT2_SOURCE_ROOT),
        "build_root": str(pilot_build.ATTEMPT2_BUILD_ROOT),
        "harness_root": str(pilot_build.ATTEMPT2_HARNESS_ROOT),
        "log_root": str(pilot_build.ATTEMPT2_LOG_ROOT),
        "archive_path": str(pilot_build.ATTEMPT2_ARCHIVE_PATH),
        "qualification_base_head": pilot_build.QUALIFICATION_BASE_HEAD,
        "qualification_evidence_sha256": "1" * 64,
        "cmake_metadata_argv": descriptors[0]["argv"],
        "cmake_configure_argv": descriptors[2]["argv"],
        "baseline_build_argv": descriptors[3]["argv"],
        "baseline_smoke_argv": descriptors[4]["argv"],
        "cmake_version_timeout_seconds": 10, "cmake_configure_timeout_seconds": 900,
        "baseline_build_timeout_seconds": 3600, "baseline_smoke_timeout_seconds": 1800,
        "outer_timeout_seconds": 7200, "build_parallelism": 4, "planned_count": 5,
        "dependency_dag": [item["dependency_phase_ids"] for item in descriptors],
        "phase_order": [item["phase_id"] for item in descriptors],
        "environment_snapshot": environment,
        "environment_snapshot_sha256": environment["artifact_sha256"],
        "producer_pid": 17, "producer_starttime": "synthetic-starttime", "no_retry": True,
        "claims": "blocked", "formal_denominator_membership": False, "rq4_supported": False,
        "attempt_2_authorized": False, "verification_scope": "ARTIFACT_HASH_AND_HOST_SNAPSHOT",
        "executor_cloud_run_id": None, "executor_build_snapshot_id": None}
    value["predecessor_sha256"] = sorted(value[key] for key in (
        "attempt1_implementation_verdict_sha256", "attempt2_implementation_verdict_sha256",
        "authorization_sha256", "qualification_evidence_sha256",
        "source_preparation_verdict_sha256", "source_manifest_sha256",
        "source_preparation_result_sha256", "environment_snapshot_sha256"))
    return _attempt2_rehash(pilot_build, value)


def _attempt2_rebind_environment(pilot_build, value, environment):
    old = value["environment_snapshot_sha256"]
    value["environment_snapshot"] = environment
    value["environment_snapshot_sha256"] = environment["artifact_sha256"]
    value["predecessor_sha256"] = sorted(
        environment["artifact_sha256"] if item == old else item
        for item in value["predecessor_sha256"])
    return _attempt2_rehash(pilot_build, value)


def _install_attempt2_orchestration_fakes(tmp_path, monkeypatch):
    """Install only coordinator-bound synthetic seams; never run a host probe."""
    from p3_v3 import pilot_build, pilot_source

    paths = {
        "archive": tmp_path / "source.tar",
        "source": tmp_path / "source",
        "build": tmp_path / "build",
        "harness": tmp_path / "harness",
        "intent": tmp_path / "intent.json",
        "result": tmp_path / "result.json",
        "auth": tmp_path / "auth.txt",
    }
    paths["archive"].write_bytes(b"synthetic frozen tar")
    paths["auth"].write_bytes(pilot_build.ATTEMPT2_AUTHORIZATION_BYTES)
    for name, value in (
        ("ATTEMPT2_ARCHIVE_PATH", paths["archive"]),
        ("ATTEMPT2_SOURCE_ROOT", paths["source"]),
        ("ATTEMPT2_BUILD_ROOT", paths["build"]),
        ("ATTEMPT2_HARNESS_ROOT", paths["harness"]),
        ("ATTEMPT2_LOG_ROOT", paths["build"] / "logs"),
        ("ATTEMPT2_INTENT_PATH", paths["intent"]),
        ("ATTEMPT2_RESULT_PATH", paths["result"]),
        ("ATTEMPT2_AUTHORIZATION_PATH", paths["auth"]),
    ):
        monkeypatch.setattr(pilot_build, name, value)
    monkeypatch.setattr(
        pilot_build, "ATTEMPT2_AUTHORIZATION_SHA256",
        hashlib.sha256(pilot_build.ATTEMPT2_AUTHORIZATION_BYTES).hexdigest(),
    )
    events = []
    calls = []
    qualification_root, _ = _write_attempt2_v5_fixture(tmp_path, monkeypatch)
    qualification = pilot_build.read_v5_qualification_evidence(qualification_root)
    monkeypatch.setattr(
        pilot_build, "read_v5_qualification_evidence", lambda *_args: qualification
    )
    monkeypatch.setattr(
        pilot_build,
        "read_attempt2_implementation_verdict",
        lambda: (
            {
                "reviewed_commit": "a" * 40,
                "reviewed_blob_sha256": {
                    "src/p3_v3/pilot_source.py": "3" * 64,
                    "scripts/p3_v3/pilot.py": "4" * 64,
                },
            },
            "5" * 64,
        ),
    )
    monkeypatch.setattr(pilot_build, "resolve_cmake_executable_path", lambda: "/usr/bin/cmake")
    monkeypatch.setattr(pilot_build, "producer_identity", lambda: (17, "synthetic"))
    real_validate_intent = pilot_build.validate_attempt2_intent
    real_validate_result = pilot_build.validate_attempt2_result

    def validate_intent(value):
        validated = real_validate_intent(value)
        events.append("validate-intent")
        return validated

    def validate_result(value):
        validated = real_validate_result(value)
        if not paths["result"].exists():
            events.append("validate-result")
        return validated

    monkeypatch.setattr(pilot_build, "validate_attempt2_intent", validate_intent)
    monkeypatch.setattr(pilot_build, "validate_attempt2_result", validate_result)
    original_mkdir = pilot_build.os.mkdir

    def mkdir(path, *args, **kwargs):
        path = Path(path)
        if path == paths["build"]:
            events.append("build-root")
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(pilot_build.os, "mkdir", mkdir)

    def safe_logs(path):
        assert path == paths["build"] / "logs"
        events.append("logs")
        original_mkdir(path)
        return path

    monkeypatch.setattr(pilot_build, "ensure_safe_log_root", safe_logs)

    def writer(path, value, *, exclusive):
        assert exclusive is True
        events.append("intent" if path == paths["intent"] else "result")
        path.write_bytes(pilot_build.canonical_json_bytes(value))

    monkeypatch.setattr(pilot_build, "write_canonical_json", writer)
    monkeypatch.setattr(
        pilot_source,
        "_inspect_attempt2_source_entry",
        lambda *_, **__: events.append("source-entry") or "INVALID_PASS_NO_ROOT",
    )
    restoration = _attempt2_phase_fixture(
        pilot_build, pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[1]
    )["source_restoration_evidence"]
    monkeypatch.setattr(
        pilot_source,
        "run_restore_production_source",
        lambda *_, **__: events.append("source-restore") or restoration,
    )

    def harness(root, cmake_bytes, cxx_bytes):
        assert root == paths["harness"]
        assert (cmake_bytes, cxx_bytes) == (
            pilot_build.HARNESS_CMAKE_BYTES, pilot_build.HARNESS_CXX_BYTES
        )
        events.append("harness")
        original_mkdir(root)

    monkeypatch.setattr(pilot_build, "write_harness", harness)

    build_evidence = {
        "cmake_cache_sha256": "8" * 64,
        "compile_commands_sha256": "9" * 64,
        "compiler_depfile_sha256": "a" * 64,
        "dependency_list_sha256": "b" * 64,
        "smoke_executable_sha256": "c" * 64,
    }

    def collect(*args, **kwargs):
        events.append("build-evidence")
        executable = paths["build"] / "boost_math_pilot_smoke"
        executable.write_bytes(b"synthetic executable")
        build_evidence["smoke_executable_sha256"] = hashlib.sha256(
            executable.read_bytes()
        ).hexdigest()
        return dict(build_evidence)

    monkeypatch.setattr(pilot_build, "collect_baseline_build_evidence", collect)

    def execute(spec, **kwargs):
        assert "cwd" not in kwargs
        events.append(spec["job_id"])
        calls.append((spec, kwargs))
        if spec["job_id"] == "METADATA_CMAKE_VERSION":
            (kwargs["log_root"] / "METADATA_CMAKE_VERSION.stdout").write_bytes(
                b"cmake version 3.28.3\n"
            )
        descriptor = next(d for d in pilot_build.attempt2_phase_descriptors("/usr/bin/cmake") if d["phase_id"] == spec["job_id"])
        phase = _attempt2_phase_fixture(pilot_build, descriptor)
        job = {("job_id" if k == "phase_id" else "job_kind" if k == "phase_kind" else "dependency_job_ids" if k == "dependency_phase_ids" else k): v for k, v in phase.items() if k != "source_restoration_evidence"}
        job["schema_version"] = "p3-pilot-build-preflight-job-result-v1"
        job["artifact_sha256"] = pilot_build.canonical_sha256(
            {key: item for key, item in job.items() if key != "artifact_sha256"}
        )
        return job

    monkeypatch.setattr(pilot_build, "execute_job", execute)
    for forbidden in ("run", "check_output"):
        monkeypatch.setattr(subprocess, forbidden, lambda *_a, **_k: pytest.fail("real subprocess used"))
    monkeypatch.setattr(pilot_build.os, "system", lambda *_a, **_k: pytest.fail("os.system used"))
    return pilot_build, paths, events, calls


@pytest.mark.parametrize("wrong", ["archive", "source", "build"])
def test_attempt2_orchestration_wrong_cli_path_refuses_without_publication(tmp_path, monkeypatch, wrong):
    pilot_build, paths, events, calls = _install_attempt2_orchestration_fakes(tmp_path, monkeypatch)
    args = [paths["archive"], paths["source"], paths["build"]]
    args[["archive", "source", "build"].index(wrong)] = tmp_path / "wrong"
    with pytest.raises(EvidenceError, match="E_PILOT_ATTEMPT2_PATH"):
        pilot_build.run_build_preflight_attempt_2(*args)
    assert events == []


@pytest.mark.parametrize("durable", ["intent", "result"])
def test_attempt2_publication_preexisting_is_refusal_not_resume(tmp_path, monkeypatch, durable):
    pilot_build, paths, events, calls = _install_attempt2_orchestration_fakes(tmp_path, monkeypatch)
    paths[durable].write_bytes(b"preexisting\n")
    with pytest.raises(EvidenceError, match="E_PILOT_ATTEMPT2_PREEXISTING"):
        pilot_build.run_build_preflight_attempt_2(paths["archive"], paths["source"], paths["build"])
    assert events == []


def test_attempt2_missing_attempt1_result_refuses_before_publication(tmp_path, monkeypatch):
    pilot_build, paths, events, calls = _install_attempt2_orchestration_fakes(
        tmp_path, monkeypatch
    )
    monkeypatch.setattr(pilot_build, "RESULT_PATH", tmp_path / "missing-attempt1-result.json")
    with pytest.raises(EvidenceError):
        pilot_build.run_build_preflight_attempt_2(
            paths["archive"], paths["source"], paths["build"]
        )
    assert events == ["source-entry"]
    assert not paths["intent"].exists() and not paths["result"].exists()
    assert not paths["build"].exists() and not paths["harness"].exists()
    assert calls == []


def test_attempt2_orchestration_exact_one_shot_publication_order(tmp_path, monkeypatch):
    pilot_build, paths, events, calls = _install_attempt2_orchestration_fakes(tmp_path, monkeypatch)
    original_environment = dict(pilot_build.os.environ)
    result = pilot_build.run_build_preflight_attempt_2(paths["archive"], paths["source"], paths["build"])
    assert events == [
        "source-entry", "validate-intent", "intent", "build-root", "logs",
        "METADATA_CMAKE_VERSION", "source-restore", "harness",
        "CMAKE_CONFIGURE", "BASELINE_BUILD", "build-evidence",
        "BASELINE_SMOKE", "validate-result", "result",
    ]
    assert pilot_build.os.environ == original_environment
    assert [phase["phase_id"] for phase in result["phases"]] == [
        item["phase_id"]
        for item in pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")
    ]
    process_descriptors = [
        descriptor for descriptor in pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")
        if descriptor["phase_id"] != "SOURCE_RESTORE"
    ]
    assert [spec["job_id"] for spec, _ in calls] == [
        descriptor["phase_id"] for descriptor in process_descriptors
    ]
    processed_environment = calls[0][1]["env"]
    assert all(kwargs["env"] is processed_environment for _, kwargs in calls)
    assert all(kwargs["log_root"] == paths["build"] / "logs" for _, kwargs in calls)
    assert all("cwd" not in kwargs for _, kwargs in calls)
    assert [spec for spec, _ in calls] == [
        {
            "job_id": descriptor["phase_id"],
            "job_kind": descriptor["phase_kind"],
            "dependency_job_ids": descriptor["dependency_phase_ids"],
            "argv": descriptor["argv"],
            "timeout_seconds": descriptor["timeout_seconds"],
        }
        for descriptor in process_descriptors
    ]


def test_attempt2_orchestration_passes_runtime_review_to_source_gates(
    tmp_path, monkeypatch
):
    from p3_v3 import pilot_source

    pilot_build, paths, _events, _calls = _install_attempt2_orchestration_fakes(
        tmp_path, monkeypatch
    )
    reviewed = {
        "src/p3_v3/pilot_source.py": "3" * 64,
        "scripts/p3_v3/pilot.py": "4" * 64,
    }
    monkeypatch.setattr(
        pilot_build,
        "read_attempt2_implementation_verdict",
        lambda: (
            {"reviewed_commit": "a" * 40, "reviewed_blob_sha256": reviewed},
            "5" * 64,
        ),
    )
    observed = []

    def inspect(_archive, _source, *, runtime_reviewed_blob_sha256=None):
        observed.append(("entry", runtime_reviewed_blob_sha256))
        return "INVALID_PASS_NO_ROOT"

    restoration = _attempt2_phase_fixture(
        pilot_build, pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[1]
    )["source_restoration_evidence"]

    def restore(_archive, _source, *, runtime_reviewed_blob_sha256=None):
        observed.append(("restore", runtime_reviewed_blob_sha256))
        return restoration

    monkeypatch.setattr(pilot_source, "_inspect_attempt2_source_entry", inspect)
    monkeypatch.setattr(pilot_source, "run_restore_production_source", restore)

    pilot_build.run_build_preflight_attempt_2(
        paths["archive"], paths["source"], paths["build"]
    )

    assert observed == [("entry", reviewed), ("restore", reviewed)]


@pytest.mark.parametrize(
    ("phase", "status"),
    [(0, "FAIL"), (0, "TIMEOUT"), (0, "FAIL_INFRASTRUCTURE"),
     (1, "FAIL"), (2, "FAIL"), (3, "FAIL"), (4, "FAIL")],
)
def test_attempt2_not_started_after_first_terminal_failure(tmp_path, monkeypatch, phase, status):
    pilot_build, paths, events, calls = _install_attempt2_orchestration_fakes(tmp_path, monkeypatch)
    descriptors = pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")
    executed = []

    def execute(spec, **kwargs):
        index = next(i for i, d in enumerate(descriptors) if d["phase_id"] == spec["job_id"])
        executed.append(spec["job_id"])
        chosen = status if index == phase else "PASS"
        if spec["job_id"] == "METADATA_CMAKE_VERSION" and chosen == "PASS":
            (kwargs["log_root"] / "METADATA_CMAKE_VERSION.stdout").write_bytes(
                b"cmake version 3.28.3\n"
            )
        value = _attempt2_phase_fixture(pilot_build, descriptors[index], chosen)
        job = {("job_id" if k == "phase_id" else "job_kind" if k == "phase_kind" else "dependency_job_ids" if k == "dependency_phase_ids" else k): v for k, v in value.items() if k != "source_restoration_evidence"}
        job["schema_version"] = "p3-pilot-build-preflight-job-result-v1"
        job["artifact_sha256"] = pilot_build.canonical_sha256(
            {key: item for key, item in job.items() if key != "artifact_sha256"}
        )
        return job

    monkeypatch.setattr(pilot_build, "execute_job", execute)
    if phase == 1:
        from p3_v3 import pilot_source
        evidence = _attempt2_phase_fixture(pilot_build, descriptors[1], "FAIL")["source_restoration_evidence"]
        monkeypatch.setattr(
            pilot_source,
            "run_restore_production_source",
            lambda *_, **__: evidence,
        )
    result = pilot_build.run_build_preflight_attempt_2(paths["archive"], paths["source"], paths["build"])
    assert executed == [
        descriptor["phase_id"] for descriptor in descriptors[:phase + 1]
        if descriptor["phase_id"] != "SOURCE_RESTORE"
    ]
    assert [p["terminal_status"] for p in result["phases"]][phase + 1:] == ["NOT_STARTED"] * (4 - phase)
    for later in result["phases"][phase + 1:]:
        assert pilot_build.validate_attempt2_phase_result(later) == later
        assert later == pilot_build.make_attempt2_not_started(
            next(d for d in descriptors if d["phase_id"] == later["phase_id"])
        )
    assert pilot_build.validate_attempt2_result(result) == result
    assert events[-1] == "result"


def _assert_attempt2_terminal_infra(pilot_build, result, reached):
    """Assert one reached infrastructure failure and pristine blocked successors."""
    assert pilot_build.validate_attempt2_result(result) == result
    assert result["phases"][reached]["terminal_status"] == "FAIL_INFRASTRUCTURE"
    for phase in result["phases"][reached + 1:]:
        descriptor = next(
            item for item in pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")
            if item["phase_id"] == phase["phase_id"]
        )
        assert phase == pilot_build.make_attempt2_not_started(descriptor)


@pytest.mark.parametrize(
    ("failure", "reached", "forbidden"),
    [
        ("build-root", 0, {"METADATA_CMAKE_VERSION", "source-restore", "harness"}),
        ("log-root", 0, {"METADATA_CMAKE_VERSION", "source-restore", "harness"}),
        ("harness", 2, {"CMAKE_CONFIGURE", "BASELINE_BUILD", "build-evidence", "BASELINE_SMOKE"}),
        ("build-evidence", 3, {"BASELINE_SMOKE"}),
    ],
)
def test_attempt2_orchestration_publication_failure_is_terminal(
    tmp_path, monkeypatch, failure, reached, forbidden
):
    pilot_build, paths, events, calls = _install_attempt2_orchestration_fakes(
        tmp_path, monkeypatch
    )

    def fail(*_args, **_kwargs):
        raise EvidenceError("E_SYNTHETIC", f"{failure} publication failure")

    if failure == "build-root":
        original = pilot_build.os.mkdir
        monkeypatch.setattr(
            pilot_build.os, "mkdir",
            lambda path, *a, **k: fail() if Path(path) == paths["build"] else original(path, *a, **k),
        )
    elif failure == "log-root":
        monkeypatch.setattr(pilot_build, "ensure_safe_log_root", fail)
    elif failure == "harness":
        monkeypatch.setattr(pilot_build, "write_harness", fail)
    else:
        monkeypatch.setattr(pilot_build, "collect_baseline_build_evidence", fail)

    result = pilot_build.run_build_preflight_attempt_2(
        paths["archive"], paths["source"], paths["build"]
    )
    assert paths["intent"].exists()
    assert events.count("result") == 1
    assert not (set(events) & forbidden)
    _assert_attempt2_terminal_infra(pilot_build, result, reached)


def test_attempt2_outer_deadline_prevents_next_process_phase(tmp_path, monkeypatch):
    pilot_build, paths, events, calls = _install_attempt2_orchestration_fakes(
        tmp_path, monkeypatch
    )
    ticks = iter([100.0, 100.0, 100.0 + pilot_build.OUTER_TIMEOUT_SECONDS + 1])
    monkeypatch.setattr(pilot_build.time, "monotonic", lambda: next(ticks, 99999.0))
    result = pilot_build.run_build_preflight_attempt_2(
        paths["archive"], paths["source"], paths["build"]
    )
    assert paths["intent"].exists() and events.count("result") == 1
    assert [spec["job_id"] for spec, _ in calls] == ["METADATA_CMAKE_VERSION"]
    _assert_attempt2_terminal_infra(pilot_build, result, 2)


def test_attempt2_writer_intent_exception_fabricates_nothing(tmp_path, monkeypatch):
    pilot_build, paths, events, calls = _install_attempt2_orchestration_fakes(
        tmp_path, monkeypatch
    )
    publications = []

    def writer(path, _value, *, exclusive: bool):
        publications.append((path, exclusive))
        raise OSError("synthetic exclusive intent failure")

    monkeypatch.setattr(pilot_build, "write_canonical_json", writer)
    with pytest.raises(OSError, match="exclusive intent"):
        pilot_build.run_build_preflight_attempt_2(
            paths["archive"], paths["source"], paths["build"]
        )
    assert publications == [(paths["intent"], True)]
    assert not paths["intent"].exists() and not paths["result"].exists()
    assert not paths["build"].exists() and not paths["harness"].exists()
    assert calls == []


def test_attempt2_writer_result_exception_does_not_retry_or_fabricate(tmp_path, monkeypatch):
    pilot_build, paths, events, calls = _install_attempt2_orchestration_fakes(
        tmp_path, monkeypatch
    )
    original = pilot_build.write_canonical_json
    publications = []

    def writer(path, value, *, exclusive):
        publications.append((path, exclusive))
        if path == paths["result"]:
            raise OSError("synthetic exclusive result failure")
        return original(path, value, exclusive=exclusive)

    monkeypatch.setattr(pilot_build, "write_canonical_json", writer)
    with pytest.raises(OSError, match="exclusive result"):
        pilot_build.run_build_preflight_attempt_2(
            paths["archive"], paths["source"], paths["build"]
        )
    assert publications == [(paths["intent"], True), (paths["result"], True)]
    assert paths["intent"].exists() and not paths["result"].exists()


def test_attempt2_result_contract_rejects_not_started_as_first_failure():
    from p3_v3 import pilot_build
    with pytest.raises(EvidenceError, match="real terminal failure"):
        pilot_build.validate_attempt2_result(_attempt2_result_fixture(pilot_build, ["PASS", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"]))


def test_attempt2_result_contract_smoke_failure_retains_built_executable():
    from p3_v3 import pilot_build
    result = _attempt2_result_fixture(pilot_build, ["PASS", "PASS", "PASS", "PASS", "NOT_STARTED"])
    result["phases"][4] = _attempt2_phase_fixture(pilot_build, pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[4], "FAIL")
    result["phases"][4].update(failure_reason="NONZERO_EXIT", exit_code=1)
    result["phases"][4]["artifact_sha256"] = pilot_build.canonical_sha256({k: v for k, v in result["phases"][4].items() if k != "artifact_sha256"})
    result.update(started_count=sum(p["process_started"] for p in result["phases"]),
                  terminal_status="FAIL", failure_reason="NONZERO_EXIT", terminal_count=5,
                  not_started_count=0)
    result["artifact_sha256"] = pilot_build.canonical_sha256({k: v for k, v in result.items() if k != "artifact_sha256"})
    assert pilot_build.validate_attempt2_result(result)["smoke_executable_sha256"] == "c" * 64


def test_attempt2_result_contract_metadata_pre_process_failure_allows_absent_safe_root():
    from p3_v3 import pilot_build
    result = _attempt2_result_fixture(pilot_build,
        ["NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"], root=(False, False))
    first = _attempt2_phase_fixture(pilot_build,
        pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[0], "FAIL_INFRASTRUCTURE")
    result["phases"][0] = first
    result.update(started_count=0, terminal_count=1, not_started_count=4,
                  terminal_status="FAIL_INFRASTRUCTURE", failure_reason="MISSING_DEPENDENCY")
    result["artifact_sha256"] = pilot_build.canonical_sha256({k: v for k, v in result.items() if k != "artifact_sha256"})
    assert pilot_build.validate_attempt2_result(result)["build_root_exists"] is False


def test_attempt2_result_contract_cmake_version_matches_metadata_reach():
    from p3_v3 import pilot_build
    result = _attempt2_result_fixture(pilot_build)
    result["environment_snapshot"] = _attempt2_environment_fixture(pilot_build, None)
    result["environment_snapshot_sha256"] = result["environment_snapshot"]["artifact_sha256"]
    result["predecessor_sha256"] = sorted(set(result["predecessor_sha256"] + [result["environment_snapshot_sha256"]]))
    result["artifact_sha256"] = pilot_build.canonical_sha256({k: v for k, v in result.items() if k != "artifact_sha256"})
    with pytest.raises(EvidenceError, match="CMake version"):
        pilot_build.validate_attempt2_result(result)


def _attempt2_rehash(pilot_build, value):
    value["artifact_sha256"] = pilot_build.canonical_sha256(
        {key: item for key, item in value.items() if key != "artifact_sha256"}
    )
    return value


def test_attempt2_intent_contract_accepts_exact_fixture_and_extra_predecessor():
    from p3_v3 import pilot_build
    value = _attempt2_intent_fixture(pilot_build)
    assert pilot_build.validate_attempt2_intent(value) == value
    value["predecessor_sha256"] = sorted([*value["predecessor_sha256"], "e" * 64])
    _attempt2_rehash(pilot_build, value)
    assert pilot_build.validate_attempt2_intent(value) == value
    assert type(value["producer_pid"]) is int and value["producer_pid"] > 0


@pytest.mark.parametrize("validator,fixture", [
    ("validate_attempt2_intent", _attempt2_intent_fixture),
    ("validate_attempt2_result", _attempt2_result_fixture),
])
def test_attempt2_intent_contract_and_result_contract_validation_are_pure(
        monkeypatch, validator, fixture):
    from p3_v3 import pilot_build
    def forbidden(*_args, **_kwargs):
        pytest.fail("validator attempted process, probe, read, or publication")
    for name in ("execute_job", "probe_identity", "make_environment_snapshot",
                 "read_authority_snapshot", "read_json", "write_canonical_json"):
        if hasattr(pilot_build, name):
            monkeypatch.setattr(pilot_build, name, forbidden)
    assert getattr(pilot_build, validator)(fixture(pilot_build)) == fixture(pilot_build)


@pytest.mark.parametrize("group,key,replacement", [
    ("schema_version", "schema_version", "wrong"),
    ("execution_class", "execution_class", "OTHER"),
    ("denominator", "denominator", "OTHER"),
    ("no_retry", "no_retry", False),
    ("formal_denominator_membership", "formal_denominator_membership", True),
    ("rq4_supported", "rq4_supported", True),
    ("attempt_2_authorized", "attempt_2_authorized", True),
    ("plan_class", "plan_class", "OTHER"), ("planned_count", "planned_count", 4),
    ("phase_order", "phase_order", ["SMOKE"]), ("dependency_dag", "dependency_dag", [[]] * 5),
    ("p12", "p12_item_id", "OTHER"), ("snapshot", "neutral_snapshot_id", "OTHER"),
    ("tree", "normalized_source_tree_sha256", "f" * 64),
    ("subject", "controlled_subject_id", "OTHER"),
    ("subject_source", "controlled_subject_source_id", "OTHER"),
    ("descriptor", "build_descriptor_sha256", "f" * 64),
    ("source_verdict", "source_preparation_verdict_sha256", "f" * 64),
    ("manifest", "source_manifest_sha256", "f" * 64),
    ("source_result", "source_preparation_result_sha256", "f" * 64),
    ("attempt1", "attempt1_implementation_verdict_sha256", "bad"),
    ("attempt2", "attempt2_implementation_verdict_sha256", "bad"),
    ("authorization", "authorization_sha256", "bad"),
    ("qualification", "qualification_evidence_sha256", "bad"),
    ("source_root", "source_root", "/other"), ("build_root", "build_root", "/other"),
    ("harness_root", "harness_root", "/other"), ("log_root", "log_root", "/other"),
    ("archive", "archive_path", "/other"), ("base_head", "qualification_base_head", "other"),
    ("metadata_argv", "cmake_metadata_argv", ["other"]),
    ("configure_argv", "cmake_configure_argv", ["other"]),
    ("build_argv", "baseline_build_argv", ["other"]),
    ("smoke_argv", "baseline_smoke_argv", ["other"]),
    ("metadata_timeout", "cmake_version_timeout_seconds", 11),
    ("configure_timeout", "cmake_configure_timeout_seconds", 901),
    ("build_timeout", "baseline_build_timeout_seconds", 3601),
    ("smoke_timeout", "baseline_smoke_timeout_seconds", 1801),
    ("outer_timeout", "outer_timeout_seconds", 7201), ("parallelism", "build_parallelism", 3),
    ("reviewed_commit", "source_preparation_reviewed_commit", "other"),
    ("pid_bool", "producer_pid", True), ("pid_zero", "producer_pid", 0),
    ("starttime", "producer_starttime", ""), ("claims", "claims", "allowed"),
    ("scope", "verification_scope", "OTHER"), ("cloud_run", "executor_cloud_run_id", "id"),
    ("cloud_snapshot", "executor_build_snapshot_id", "id"),
])
def test_attempt2_intent_contract_rejects_semantic_drift(group, key, replacement):
    from p3_v3 import pilot_build
    value = _attempt2_intent_fixture(pilot_build)
    value[key] = replacement
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_intent(value)


@pytest.mark.parametrize("group,mutation", [
    ("environment_invalid", "claims"), ("environment_nonnull_cmake", "cmake_version"),
])
def test_attempt2_intent_contract_rejects_rehashed_environment_drift(group, mutation):
    from p3_v3 import pilot_build
    value = _attempt2_intent_fixture(pilot_build)
    environment = dict(value["environment_snapshot"])
    environment[mutation] = "allowed" if mutation == "claims" else "cmake version synthetic"
    _attempt2_rehash(pilot_build, environment)
    _attempt2_rebind_environment(pilot_build, value, environment)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_intent(value)


def test_attempt2_intent_contract_rejects_nested_hash_mismatch():
    from p3_v3 import pilot_build
    value = _attempt2_intent_fixture(pilot_build)
    value["environment_snapshot_sha256"] = "e" * 64
    value["predecessor_sha256"] = sorted(
        "e" * 64 if item == value["environment_snapshot"]["artifact_sha256"] else item
        for item in value["predecessor_sha256"])
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError, match="environment binding"):
        pilot_build.validate_attempt2_intent(value)


@pytest.mark.parametrize("group,change", [
    ("malformed", "malformed"), ("unsorted", "unsorted"), ("duplicate", "duplicate"),
    *[(f"missing_index_{index}", index) for index in range(8)],
])
def test_attempt2_intent_contract_rejects_predecessor_drift(group, change):
    from p3_v3 import pilot_build
    value = _attempt2_intent_fixture(pilot_build)
    if change == "malformed": value["predecessor_sha256"][0] = "bad"
    elif change == "unsorted": value["predecessor_sha256"].reverse()
    elif change == "duplicate": value["predecessor_sha256"].append(value["predecessor_sha256"][-1])
    else: value["predecessor_sha256"].pop(change)
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_intent(value)


@pytest.mark.parametrize("change", ["missing", "extra"])
def test_attempt2_intent_contract_rejects_exact_key_drift(change):
    from p3_v3 import pilot_build
    value = _attempt2_intent_fixture(pilot_build)
    if change == "missing": value.pop("plan_class")
    else: value["extra"] = None
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_intent(value)


def test_attempt2_intent_contract_rejects_stale_self_hash():
    from p3_v3 import pilot_build
    value = _attempt2_intent_fixture(pilot_build)
    value["planned_count"] = 4
    with pytest.raises(EvidenceError, match="self-hash"):
        pilot_build.validate_attempt2_intent(value)


@pytest.mark.parametrize("statuses,root,expected", [
    (["PASS"] * 5, (True, False), (4, 5, 0, "PASS", None)),
    (["FAIL", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"], (True, False), (1, 1, 4, "FAIL", "NONZERO_EXIT")),
    (["PASS", "FAIL", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"], (True, False), (1, 2, 3, "FAIL", "TREE_HASH_MISMATCH")),
    (["PASS", "PASS", "FAIL", "NOT_STARTED", "NOT_STARTED"], (True, False), (2, 3, 2, "FAIL", "NONZERO_EXIT")),
    (["PASS", "PASS", "PASS", "FAIL", "NOT_STARTED"], (True, False), (3, 4, 1, "FAIL", "NONZERO_EXIT")),
    (["PASS", "PASS", "PASS", "PASS", "FAIL"], (True, False), (4, 5, 0, "FAIL", "NONZERO_EXIT")),
    (["FAIL_INFRASTRUCTURE", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"], (False, False), (0, 1, 4, "FAIL_INFRASTRUCTURE", "MISSING_DEPENDENCY")),
])
def test_attempt2_result_contract_accepts_exact_terminal_states(statuses, root, expected):
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build, statuses, root)
    assert (value["started_count"], value["terminal_count"], value["not_started_count"],
            value["terminal_status"], value["failure_reason"]) == expected
    assert (value["build_root_exists"], value["build_root_is_symlink"]) == root
    assert value["environment_snapshot"]["cmake_version"] == (None if statuses[0] != "PASS" else "cmake version 3.28.3")
    assert value["source_restoration_disposition"] == (None if statuses[1] == "NOT_STARTED" else
        value["phases"][1]["source_restoration_evidence"]["disposition"])
    assert (value["cmake_cache_sha256"] is not None) == (statuses[3] == "PASS")
    assert (value["smoke_executable_sha256"] is not None) == (statuses[3] == "PASS")
    assert pilot_build.validate_attempt2_result(value) == value


@pytest.mark.parametrize("statuses,root", [
    (["PASS"] * 5, (False, False)),
    (["FAIL", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"], (False, False)),
    (["PASS"] * 5, (True, True)),
])
def test_attempt2_result_contract_rejects_invalid_root_reach(statuses, root):
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build, statuses, root)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_result(value)


def test_attempt2_result_contract_accepts_extra_predecessor():
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build)
    value["predecessor_sha256"] = sorted([*value["predecessor_sha256"], "e" * 64])
    _attempt2_rehash(pilot_build, value)
    assert pilot_build.validate_attempt2_result(value) == value


@pytest.mark.parametrize("group,key,replacement", [
    ("schema_version", "schema_version", "wrong"),
    ("execution_class", "execution_class", "OTHER"),
    ("denominator", "denominator", "OTHER"),
    ("no_retry", "no_retry", False),
    ("formal_denominator_membership", "formal_denominator_membership", True),
    ("rq4_supported", "rq4_supported", True),
    ("attempt_2_authorized", "attempt_2_authorized", True),
    ("p12", "p12_item_id", "OTHER"), ("snapshot", "neutral_snapshot_id", "OTHER"),
    ("tree", "normalized_source_tree_sha256", "f" * 64),
    ("subject", "controlled_subject_id", "OTHER"),
    ("subject_source", "controlled_subject_source_id", "OTHER"),
    ("descriptor", "build_descriptor_sha256", "f" * 64),
    ("source_verdict", "source_preparation_verdict_sha256", "f" * 64),
    ("manifest", "source_manifest_sha256", "f" * 64),
    ("source_result", "source_preparation_result_sha256", "f" * 64),
    ("attempt1", "attempt1_implementation_verdict_sha256", "bad"),
    ("attempt2", "attempt2_implementation_verdict_sha256", "bad"),
    ("intent", "intent_sha256", "bad"), ("authorization", "authorization_sha256", "bad"),
    ("qualification", "qualification_evidence_sha256", "bad"),
    ("harness_cmake", "harness_cmake_sha256", "f" * 64),
    ("harness_cxx", "harness_cxx_sha256", "f" * 64),
    ("source_root", "source_root", "/other"), ("build_root", "build_root", "/other"),
    ("harness_root", "harness_root", "/other"), ("log_root", "log_root", "/other"),
    ("archive", "archive_path", "/other"), ("base_head", "qualification_base_head", "other"),
    ("planned", "planned_count", 4), ("phase_order", "phase_order", ["SMOKE"]),
    ("started_count", "started_count", 3), ("terminal_count", "terminal_count", 4),
    ("not_started_count", "not_started_count", 1),
    ("aggregate_status", "terminal_status", "FAIL"),
    ("aggregate_failure", "failure_reason", "NONZERO_EXIT"),
    ("disposition", "source_restoration_disposition", "RESTORED"),
    ("scope", "verification_scope", "OTHER"), ("claims", "claims", "allowed"),
    ("cloud_run", "executor_cloud_run_id", "id"),
    ("cloud_snapshot", "executor_build_snapshot_id", "id"),
])
def test_attempt2_result_contract_rejects_semantic_drift(group, key, replacement):
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build)
    value[key] = replacement
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_result(value)


def test_attempt2_result_contract_rejects_nested_environment_hash_mismatch():
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build)
    old_environment_sha256 = value["environment_snapshot_sha256"]
    value["environment_snapshot_sha256"] = "e" * 64
    value["predecessor_sha256"] = sorted(
        "e" * 64 if item == old_environment_sha256 else item
        for item in value["predecessor_sha256"]
    )
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError, match="environment binding"):
        pilot_build.validate_attempt2_result(value)


@pytest.mark.parametrize("group,statuses,key,replacement", [
    ("configure_cache_absent", ["PASS"] * 5, "cmake_cache_sha256", None),
    ("configure_commands_absent", ["PASS"] * 5, "compile_commands_sha256", None),
    ("depfile_absent", ["PASS"] * 5, "compiler_depfile_sha256", None),
    ("dependency_absent", ["PASS"] * 5, "dependency_list_sha256", None),
    ("smoke_hash_absent", ["PASS"] * 5, "smoke_executable_sha256", None),
    ("configure_cache_early", ["FAIL", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"], "cmake_cache_sha256", "d" * 64),
    ("depfile_early", ["PASS", "PASS", "FAIL", "NOT_STARTED", "NOT_STARTED"], "compiler_depfile_sha256", "d" * 64),
    ("dependency_early", ["PASS", "PASS", "FAIL", "NOT_STARTED", "NOT_STARTED"], "dependency_list_sha256", "d" * 64),
    ("smoke_early", ["PASS", "PASS", "PASS", "FAIL", "NOT_STARTED"], "smoke_executable_sha256", "d" * 64),
    ("malformed_evidence", ["PASS"] * 5, "cmake_cache_sha256", "bad"),
])
def test_attempt2_result_contract_rejects_evidence_reach(group, statuses, key, replacement):
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build, statuses)
    value[key] = replacement
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_result(value)


@pytest.mark.parametrize("group,statuses,version", [
    ("pass_null", ["PASS"] * 5, None), ("pass_empty", ["PASS"] * 5, ""),
    ("failure_version", ["FAIL", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"], "cmake version synthetic"),
])
def test_attempt2_result_contract_rejects_metadata_version_drift(group, statuses, version):
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build, statuses)
    environment = _attempt2_environment_fixture(pilot_build, version)
    _attempt2_rebind_environment(pilot_build, value, environment)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_result(value)


@pytest.mark.parametrize("group,change", [
    ("malformed", "malformed"), ("unsorted", "unsorted"), ("duplicate", "duplicate"),
    *[(f"missing_{index}", index) for index in range(9)],
])
def test_attempt2_result_contract_rejects_predecessor_drift(group, change):
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build)
    if change == "malformed": value["predecessor_sha256"][0] = "bad"
    elif change == "unsorted": value["predecessor_sha256"].reverse()
    elif change == "duplicate": value["predecessor_sha256"].append(value["predecessor_sha256"][-1])
    else: value["predecessor_sha256"].pop(change)
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_result(value)


@pytest.mark.parametrize("group,change", [
    ("fewer", "fewer"), ("more", "more"), ("wrong_id", "phase_id"),
    ("wrong_kind", "phase_kind"), ("wrong_deps", "dependency_phase_ids"),
    ("wrong_argv", "argv"), ("wrong_timeout", "timeout_seconds"),
])
def test_attempt2_result_contract_rejects_phase_shape_drift(group, change):
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build)
    if change == "fewer": value["phases"].pop()
    elif change == "more": value["phases"].append(dict(value["phases"][-1]))
    else:
        value["phases"][0][change] = (["OTHER"] if change == "dependency_phase_ids" else []) if change in {"dependency_phase_ids", "argv"} else (
            11 if change == "timeout_seconds" else "OTHER")
        _attempt2_rehash(pilot_build, value["phases"][0])
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_result(value)


def test_attempt2_result_contract_rejects_reached_phase_after_failure():
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build,
        ["FAIL", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"])
    value["phases"][2] = _attempt2_phase_fixture(
        pilot_build, pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[2], "FAIL")
    value.update(started_count=2, terminal_count=2, not_started_count=3)
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError, match="phase after failure"):
        pilot_build.validate_attempt2_result(value)


@pytest.mark.parametrize("change", ["missing", "extra"])
def test_attempt2_result_contract_rejects_exact_key_drift(change):
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build)
    if change == "missing": value.pop("planned_count")
    else: value["extra"] = None
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_result(value)


def test_attempt2_result_contract_rejects_stale_self_hash():
    from p3_v3 import pilot_build
    value = _attempt2_result_fixture(pilot_build)
    value["planned_count"] = 4
    with pytest.raises(EvidenceError, match="self-hash"):
        pilot_build.validate_attempt2_result(value)


@pytest.mark.parametrize("cmake_version", [None, "cmake version synthetic"])
def test_attempt2_environment_contract_accepts_exact_before_and_after_metadata(cmake_version):
    from p3_v3 import pilot_build
    value = _attempt2_environment_fixture(pilot_build, cmake_version)
    assert pilot_build.validate_attempt2_environment(value) == value


def test_attempt2_environment_contract_validation_is_pure(monkeypatch):
    from p3_v3 import pilot_build
    def forbidden(*_args, **_kwargs):
        pytest.fail("environment validation invoked an external entry point")
    for owner, name in ((pilot_build.subprocess, "run"),
                        (pilot_build.subprocess, "check_output"),
                        (pilot_build.os, "system"), (pilot_build, "execute_job"),
                        (pilot_build, "resolve_cmake_executable_path"),
                        (pilot_build, "write_canonical_json")):
        monkeypatch.setattr(owner, name, forbidden)
    for version in (None, "cmake version synthetic"):
        value = _attempt2_environment_fixture(pilot_build, version)
        assert pilot_build.validate_attempt2_environment(value) == value


@pytest.mark.parametrize(("group", "path", "replacement"), [
    ("cmake-executable", ("cmake_executable",), "cmake3"),
    ("cmake-path-relative", ("cmake_executable_path",), "cmake"),
    ("cmake-path-empty", ("cmake_executable_path",), ""),
    ("cmake-version-empty", ("cmake_version",), ""),
    ("compiler-executable", ("cxx_compiler_executable",), "clang++"),
    ("compiler-path", ("cxx_compiler_path",), "/usr/bin/clang++"),
    ("compiler-identity-empty", ("cxx_compiler_identity",), ""),
    ("compiler-version-empty", ("cxx_compiler_version",), ""),
    ("os-name-empty", ("os_name",), ""), ("os-release-empty", ("os_release",), ""),
    ("python-version-empty", ("python_version",), ""),
    ("git-version-empty", ("git_version",), ""),
    ("generator", ("cmake_generator",), "Ninja"),
    ("parallelism", ("build_parallelism",), 3),
    ("parallelism-bool", ("build_parallelism",), True),
    ("nvcc-non-bool", ("nvcc_present",), 0),
    ("native-profiling", ("native_profiling_present",), True),
    ("cuda-blocking", ("cuda_absence_blocking",), True),
    ("disconnected-flag", ("fetchcontent_fully_disconnected",), False),
    ("system-boost", ("system_boost_fallback_accepted",), True),
    ("disconnected-changed", ("disconnected_environment", "GIT_CONFIG_NOSYSTEM"), "0"),
    ("qualification-hash", ("qualification_evidence_sha256",), "bad"),
    ("verification-scope", ("verification_scope",), "HOST_ONLY"),
    ("cloud-run-id", ("executor_cloud_run_id",), "run"),
    ("cloud-snapshot-id", ("executor_build_snapshot_id",), "snapshot"),
    ("class", ("execution_class",), "CONFIRMATORY"),
    ("denominator", ("denominator",), "FORMAL"),
    ("claims", ("claims",), "supported"),
])
def test_attempt2_environment_contract_rejects_semantic_drift(group, path, replacement):
    from p3_v3 import pilot_build
    value = _attempt2_environment_fixture(pilot_build)
    target = value
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_environment(value)


@pytest.mark.parametrize("change", ["disconnected-extra", "disconnected-missing", "missing-key", "extra-key"])
def test_attempt2_environment_contract_rejects_exact_key_drift(change):
    from p3_v3 import pilot_build
    value = _attempt2_environment_fixture(pilot_build)
    if change == "disconnected-extra": value["disconnected_environment"]["EXTRA"] = "1"
    elif change == "disconnected-missing": value["disconnected_environment"].pop(next(iter(value["disconnected_environment"])))
    elif change == "missing-key": value.pop("os_name")
    else: value["extra"] = None
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_environment(value)


def test_attempt2_environment_contract_rejects_stale_self_hash():
    from p3_v3 import pilot_build
    value = _attempt2_environment_fixture(pilot_build)
    value["os_release"] = "changed"
    with pytest.raises(EvidenceError, match="self-hash"):
        pilot_build.validate_attempt2_environment(value)


@pytest.mark.parametrize(("phase_index", "status", "post_process"), [
    (0, "PASS", False), (0, "FAIL", False), (0, "TIMEOUT", False),
    (0, "FAIL_INFRASTRUCTURE", False), (0, "FAIL_INFRASTRUCTURE", True),
    (1, "PASS", False), (1, "FAIL", False), (4, "NOT_STARTED", False),
])
def test_attempt2_phase_contract_accepts_all_legal_status_fixtures(phase_index, status, post_process):
    from p3_v3 import pilot_build
    descriptor = pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[phase_index]
    value = _attempt2_phase_fixture(pilot_build, descriptor, status)
    if post_process:
        value.update(process_started=True, process_group_terminated=False,
            infrastructure_phase="POST_PROCESS", failure_reason="SOURCE_TREE_DRIFT",
            exit_code=0, stdout_sha256="2" * 64, stderr_sha256="3" * 64,
            stdout_bytes=1, stderr_bytes=0, started_at="2026-01-01T00:00:00Z",
            ended_at="2026-01-01T00:00:01Z", wall_seconds=1.0,
            cpu_seconds=0.1, peak_rss_bytes=1)
        _attempt2_rehash(pilot_build, value)
    assert pilot_build.validate_attempt2_phase_result(value) == value


@pytest.mark.parametrize(("group", "phase_index", "field", "replacement"), [
    ("unknown-identity", 0, "phase_id", "UNKNOWN"),
    ("mismatched-identity", 0, "phase_kind", "BASELINE_BUILD"),
    ("metadata-dependencies", 0, "dependency_phase_ids", ["X"]),
    ("source-dependencies", 1, "dependency_phase_ids", []),
    ("configure-dependencies", 2, "dependency_phase_ids", []),
    ("build-dependencies", 3, "dependency_phase_ids", []),
    ("smoke-dependencies", 4, "dependency_phase_ids", []),
    ("metadata-argv", 0, "argv", ["/usr/bin/cmake", "-E"]),
    ("source-argv", 1, "argv", ["forged"]),
    ("configure-argv", 2, "argv", ["/usr/bin/cmake"]),
    ("build-argv", 3, "argv", ["/usr/bin/cmake"]),
    ("smoke-argv", 4, "argv", ["forged"]),
    ("metadata-timeout", 0, "timeout_seconds", 11),
    ("source-timeout", 1, "timeout_seconds", 1),
    ("configure-timeout", 2, "timeout_seconds", 1),
    ("build-timeout", 3, "timeout_seconds", 1),
    ("smoke-timeout", 4, "timeout_seconds", 1),
    ("argv-member", 0, "argv", ["/usr/bin/cmake", 1]),
    ("class", 0, "execution_class", "CONFIRMATORY"),
    ("denominator", 0, "denominator", "FORMAL"),
    ("claims", 0, "claims", "supported"),
    ("terminal-status", 0, "terminal_status", "CANCELLED"),
])
def test_attempt2_phase_contract_rejects_descriptor_and_identity_drift(group, phase_index, field, replacement):
    from p3_v3 import pilot_build
    value = _attempt2_phase_fixture(pilot_build,
        pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[phase_index])
    value[field] = replacement
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_phase_result(value)


@pytest.mark.parametrize(("status", "field", "replacement"), [
    ("PASS", "process_started", False), ("PASS", "exit_code", 1),
    ("PASS", "failure_reason", "NONZERO_EXIT"), ("PASS", "process_group_terminated", True),
    ("FAIL", "process_started", False), ("FAIL", "exit_code", 0),
    ("FAIL", "failure_reason", "TIMEOUT"), ("FAIL", "infrastructure_phase", "POST_PROCESS"),
    ("TIMEOUT", "process_started", False), ("TIMEOUT", "exit_code", 1),
    ("TIMEOUT", "failure_reason", "NONZERO_EXIT"), ("TIMEOUT", "process_group_terminated", False),
    ("FAIL_INFRASTRUCTURE", "process_started", True),
    ("FAIL_INFRASTRUCTURE", "infrastructure_phase", "POST_PROCESS"),
    ("FAIL_INFRASTRUCTURE", "failure_reason", "SOURCE_TREE_DRIFT"),
])
def test_attempt2_phase_contract_rejects_process_status_incoherence(status, field, replacement):
    from p3_v3 import pilot_build
    value = _attempt2_phase_fixture(pilot_build,
        pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[0], status)
    value[field] = replacement
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_phase_result(value)


@pytest.mark.parametrize(("field", "replacement"), [
    ("stdout_sha256", None), ("stderr_sha256", "bad"), ("stdout_bytes", None),
    ("started_at", None), ("ended_at", None), ("wall_seconds", None),
    ("cpu_seconds", None), ("peak_rss_bytes", None),
])
def test_attempt2_phase_contract_rejects_started_process_evidence_drift(field, replacement):
    from p3_v3 import pilot_build
    value = _attempt2_phase_fixture(pilot_build,
        pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[0])
    value[field] = replacement
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_phase_result(value)


@pytest.mark.parametrize(("group", "field", "replacement"), [
    ("source-status", "terminal_status", "FAIL"),
    ("source-failure", "failure_reason", "TREE_HASH_MISMATCH"),
    ("source-missing-evidence", "source_restoration_evidence", None),
    ("source-process", "process_started", True), ("source-log", "stdout_sha256", "2" * 64),
    ("source-resource", "peak_rss_bytes", 1),
])
def test_attempt2_phase_contract_rejects_source_evidence_disagreement(group, field, replacement):
    from p3_v3 import pilot_build
    value = _attempt2_phase_fixture(pilot_build,
        pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[1])
    value[field] = replacement
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_phase_result(value)


def test_attempt2_phase_contract_rejects_restoration_evidence_on_process_phase():
    from p3_v3 import pilot_build
    descriptors = pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")
    value = _attempt2_phase_fixture(pilot_build, descriptors[0])
    value["source_restoration_evidence"] = deepcopy(
        _attempt2_phase_fixture(pilot_build, descriptors[1])["source_restoration_evidence"])
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_phase_result(value)


@pytest.mark.parametrize(("field", "replacement"), [
    ("process_started", True), ("process_group_terminated", False),
    ("infrastructure_phase", "PRE_PROCESS"), ("failure_reason", "NONZERO_EXIT"),
    ("exit_code", 1), ("stdout_sha256", "2" * 64), ("stderr_sha256", "3" * 64),
    ("stdout_bytes", 0), ("stderr_bytes", 0), ("started_at", "2026-01-01T00:00:00Z"),
    ("ended_at", "2026-01-01T00:00:01Z"), ("wall_seconds", 0.0),
    ("cpu_seconds", 0.0), ("peak_rss_bytes", 0), ("source_restoration_evidence", {}),
])
def test_attempt2_phase_contract_rejects_forged_not_started_evidence(field, replacement):
    from p3_v3 import pilot_build
    value = _attempt2_phase_fixture(pilot_build,
        pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[4], "NOT_STARTED")
    value[field] = replacement
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_phase_result(value)


@pytest.mark.parametrize("change", ["missing-key", "extra-key"])
def test_attempt2_phase_contract_rejects_exact_key_drift(change):
    from p3_v3 import pilot_build
    value = _attempt2_phase_fixture(pilot_build,
        pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[0])
    if change == "missing-key": value.pop("claims")
    else: value["extra"] = None
    _attempt2_rehash(pilot_build, value)
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_phase_result(value)


def test_attempt2_phase_contract_rejects_stale_self_hash():
    from p3_v3 import pilot_build
    value = _attempt2_phase_fixture(pilot_build,
        pilot_build.attempt2_phase_descriptors("/usr/bin/cmake")[0])
    value["stdout_bytes"] = 2
    with pytest.raises(EvidenceError, match="self-hash"):
        pilot_build.validate_attempt2_phase_result(value)
