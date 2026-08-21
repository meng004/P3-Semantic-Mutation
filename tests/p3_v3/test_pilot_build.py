from __future__ import annotations

import hashlib
import os
import subprocess
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
    build, env = _synthetic_build_evidence_tree(
        tmp_path / "compiler",
        pilot_build,
        monkeypatch,
        cache_compiler="/usr/bin/g++",
    )
    with pytest.raises(EvidenceError, match="CMakeCache compiler differs"):
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
