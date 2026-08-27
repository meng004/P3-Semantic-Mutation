from __future__ import annotations

import hashlib
import io
import tarfile
from collections import Counter
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.bridge_and_frames import canonical_source_tree_sha256
import scripts.p3_v3.build_phase1_frames as driver_module
import scripts.p3_v3.evidence as evidence_cli


REPO_ROOT = Path(__file__).resolve().parents[2]
NUMPY_UNDERSPECIFIED = {
    "8c1ab7821c4d7371f050b1e6f44ce4ea66b9118fe8f5f5962eddf4c3b4fb12da",
    "8d7480faf827795019e7fee407efd497df03f0903c97eb4c1d499a04a08d6714",
    "b5887a06a0a85403947b377f59e49b72f510ee101ecd4476d83db9eb713913db",
}


def test_audit_module_exposes_narrow_cli():
    import scripts.p3_v3.audit_prospective_workloads as audit

    parser = audit.build_parser()
    parsed = parser.parse_args(
        [
            "--consumer-lock", "lock.json",
            "--verified-bridge", "bridge.json",
            "--phase1-root", "phase1",
            "--descriptor-root", "descriptors",
            "--archive-root", "archives",
            "--runtime-root", "runtime",
            "--output", "audit.md",
        ]
    )
    assert parsed.consumer_lock == "lock.json"
    assert parsed.verified_bridge == "bridge.json"
    assert parsed.phase1_root == "phase1"
    assert parsed.descriptor_root == "descriptors"
    assert parsed.archive_root == "archives"
    assert parsed.runtime_root == "runtime"
    assert parsed.output == "audit.md"


def test_audit_parser_does_not_accept_outcome_inputs():
    import scripts.p3_v3.audit_prospective_workloads as audit

    option_strings = {
        option
        for action in audit.build_parser()._actions
        for option in action.option_strings
    }
    assert "--profiling-results" not in option_strings
    assert "--technique-profile" not in option_strings
    assert "--claim-ledger" not in option_strings


def _load_real_population(audit):
    return audit.load_population(
        consumer_lock_path=REPO_ROOT / "data/p3_v3/p12_intake/consumer_lock.json",
        verified_bridge_path=REPO_ROOT / "data/p3_v3/p12_intake/verified_bridge.json",
        phase1_root=REPO_ROOT / "data/p3_v3/phase1_frames/out",
        descriptor_root=REPO_ROOT / "data/p3_v3/p12_intake/descriptors",
    )


def test_real_population_is_exactly_the_frozen_35():
    import scripts.p3_v3.audit_prospective_workloads as audit

    subjects = _load_real_population(audit)
    assert len(subjects) == 35
    assert [row.neutral_snapshot_id for row in subjects] == sorted(
        row.neutral_snapshot_id for row in subjects
    )
    counts = Counter(
        len(row.profiling_workload["selected_rows"]) for row in subjects
    )
    assert counts == {0: 12, 20: 23}


def test_argv_tokens_are_a_unique_invocation():
    import scripts.p3_v3.audit_prospective_workloads as audit

    decision = audit.classify_row_invocation(
        language_family="c",
        entrypoint="target:example",
        declared_inputs={"argv_tokens": ["example", "--fixed"]},
        exact_boost_header_runner=False,
    )
    assert decision == audit.RowDecision("ARGV", True, None)


def test_python_parameters_require_a_python_callable():
    import scripts.p3_v3.audit_prospective_workloads as audit

    assert audit.classify_row_invocation(
        language_family="python",
        entrypoint="numpy.matlib:ones",
        declared_inputs={"parameters": {"shape": [2, 2]}},
        exact_boost_header_runner=False,
    ) == audit.RowDecision("PYTHON_CALLABLE", True, None)


@pytest.mark.parametrize("declared_inputs", [
    {"source_path": "examples/example.c"},
    {"header": "include/example.h"},
])
def test_path_or_header_without_a_frozen_harness_is_underspecified(declared_inputs):
    import scripts.p3_v3.audit_prospective_workloads as audit

    decision = audit.classify_row_invocation(
        language_family="c",
        entrypoint=next(iter(declared_inputs.values())),
        declared_inputs=declared_inputs,
        exact_boost_header_runner=False,
    )
    assert decision.unique is False
    assert decision.failure_code == "NO_UNIQUE_EXECUTION_ACTION"


def test_real_population_preserves_boost_and_numpy_terminals():
    import scripts.p3_v3.audit_prospective_workloads as audit

    results = audit.audit_invocations_for_population(_load_real_population(audit))
    by_id = {row.neutral_snapshot_id: row for row in results}
    assert by_id[audit.BOOST_MATH_ID].terminal == "TERMINAL_RETRY_FORBIDDEN"
    numpy = by_id[audit.NUMPY_ID]
    assert numpy.terminal == "WORKLOAD_EXECUTION_UNDERSPECIFIED"
    observed = {
        behavior_id
        for behavior_id, decision in numpy.row_decisions
        if not decision.unique
    }
    assert observed == NUMPY_UNDERSPECIFIED


def test_real_invocation_audit_matches_preregistered_terminals():
    import scripts.p3_v3.audit_prospective_workloads as audit

    results = audit.audit_invocations_for_population(_load_real_population(audit))
    assert all(
        row.row_count != 20 or len(row.row_decisions) == 20 for row in results
    )
    counts = Counter(row.terminal for row in results)
    assert counts["NO_FROZEN_WORKLOAD"] == 12
    assert counts["TERMINAL_RETRY_FORBIDDEN"] == 1
    assert counts["WORKLOAD_EXECUTION_UNDERSPECIFIED"] == 22
    assert counts.get("INVOCATION_COMPLETE", 0) == 0
    assert sum(counts.values()) == 35


def _eligible_subject(neutral_snapshot_id, trace, dependency_count):
    import scripts.p3_v3.audit_prospective_workloads as audit

    decisions = tuple(
        (f"{index:064x}", audit.RowDecision("ARGV", True, None))
        for index in range(20)
    )
    return audit.SubjectAudit(
        neutral_snapshot_id=neutral_snapshot_id,
        language_family="c",
        ecosystem="cmake",
        row_count=20,
        row_decisions=decisions,
        terminal="PROSPECTIVE_EXECUTABLE",
        trace_strategy=trace,
        dependency_count=dependency_count,
        source_status="SOURCE_IDENTITY_PASS",
    )


def test_trace_strategy_is_language_and_build_specific():
    import scripts.p3_v3.audit_prospective_workloads as audit

    assert audit.trace_strategy("python", "meson", {"ARGV", "PYTHON_CALLABLE"}) == (
        "PYTHON_CALL_TRACE_V1", 1
    )
    assert audit.trace_strategy("c", "cmake", {"ARGV"}) == (
        "CMAKE_NATIVE_CALL_TRACE_V1", 2
    )
    assert audit.trace_strategy("fortran", "autotools", {"ARGV"}) == (
        "AUTOTOOLS_NATIVE_CALL_TRACE_V1", 3
    )
    assert audit.trace_strategy("c", "cmake", {"ARGV", "CXX_HEADER_COMPILE"}) is None


def test_selection_is_order_independent_and_freezes_one_candidate():
    import scripts.p3_v3.audit_prospective_workloads as audit

    python = _eligible_subject("b" * 64, "PYTHON_CALL_TRACE_V1", 1)
    cmake = _eligible_subject("a" * 64, "CMAKE_NATIVE_CALL_TRACE_V1", 2)
    assert audit.select_candidate([cmake, python]) == python
    assert audit.select_candidate([python, cmake]) == python


def test_same_runner_and_dependency_prefers_lexicographically_smaller_id():
    import scripts.p3_v3.audit_prospective_workloads as audit

    later = _eligible_subject("b" * 64, "CMAKE_NATIVE_CALL_TRACE_V1", 2)
    earlier = _eligible_subject("a" * 64, "CMAKE_NATIVE_CALL_TRACE_V1", 2)
    assert audit.select_candidate([later, earlier]) == earlier
    assert audit.select_candidate([earlier, later]) == earlier


def test_select_candidate_returns_none_when_no_subject_is_eligible():
    import scripts.p3_v3.audit_prospective_workloads as audit

    blocked = _eligible_subject("a" * 64, "CMAKE_NATIVE_CALL_TRACE_V1", 2)
    blocked = audit.SubjectAudit(
        **{
            **blocked.__dict__,
            "terminal": "WORKLOAD_EXECUTION_UNDERSPECIFIED",
            "source_status": None,
            "trace_strategy": None,
        }
    )
    assert audit.select_candidate([blocked]) is None
    assert audit.select_candidate([]) is None


def _write_tar(path, member: tarfile.TarInfo, payload: bytes = b"") -> str:
    with tarfile.open(path, "w") as archive:
        archive.addfile(member, io.BytesIO(payload) if payload else None)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tiny_archive(tmp_path, payload: bytes = b"int main(void) { return 0; }\n"):
    archive_path = tmp_path / "subject.tar"
    member = tarfile.TarInfo("main.c")
    member.size = len(payload)
    member.mode = 0o644
    archive_sha256 = _write_tar(archive_path, member, payload)
    return archive_path, archive_sha256, payload


def _captured_tree_sha256(destination: Path) -> str:
    _manifest, snapshot = evidence_cli._capture_tracked_source_manifest(
        destination, ["."], "subject-source"
    )
    return canonical_source_tree_sha256(snapshot)


def _source_subject(audit, snapshot_id: str, archive_sha256: str, tree_sha256: str):
    return audit.SubjectInputs(
        neutral_snapshot_id=snapshot_id,
        bridge_record={
            "source_archive_sha256": archive_sha256,
            "normalized_source_tree_sha256": tree_sha256,
        },
        descriptor={"language_family": "c", "ecosystem": "cmake"},
        adapter_discovery={},
        public_behavior_frame={},
        profiling_workload={"selected_rows": []},
    )


def test_verify_candidate_source_accepts_tiny_normalized_tree(tmp_path):
    import scripts.p3_v3.audit_prospective_workloads as audit

    archive_path, archive_sha256, _payload = _tiny_archive(tmp_path)
    extracted = tmp_path / "pre"
    driver_module.extract_archive(archive_path, extracted, archive_sha256)
    tree_sha256 = _captured_tree_sha256(extracted)
    snapshot_id = "ab" * 32
    archive_root = tmp_path / "archives"
    archive_root.mkdir()
    (archive_root / f"{snapshot_id}.tar").write_bytes(archive_path.read_bytes())
    subject = _source_subject(audit, snapshot_id, archive_sha256, tree_sha256)
    runtime_root = tmp_path / "runtime"
    assert (
        audit.verify_candidate_source(
            subject,
            archive_root=archive_root,
            runtime_root=runtime_root,
        )
        == "SOURCE_IDENTITY_PASS"
    )
    assert (runtime_root / snapshot_id / "main.c").is_file()


def test_verify_candidate_source_maps_archive_failures(tmp_path):
    import scripts.p3_v3.audit_prospective_workloads as audit

    archive_path, archive_sha256, _payload = _tiny_archive(tmp_path)
    extracted = tmp_path / "pre"
    driver_module.extract_archive(archive_path, extracted, archive_sha256)
    tree_sha256 = _captured_tree_sha256(extracted)
    snapshot_id = "cd" * 32
    archive_root = tmp_path / "archives"
    archive_root.mkdir()
    runtime_root = tmp_path / "runtime"
    missing = _source_subject(audit, snapshot_id, archive_sha256, tree_sha256)
    assert (
        audit.verify_candidate_source(
            missing,
            archive_root=archive_root,
            runtime_root=runtime_root,
        )
        == "SOURCE_UNAVAILABLE"
    )
    (archive_root / f"{snapshot_id}.tar").write_bytes(b"not-the-archive\n")
    assert (
        audit.verify_candidate_source(
            missing,
            archive_root=archive_root,
            runtime_root=runtime_root,
        )
        == "SOURCE_IDENTITY_FAIL"
    )
    with pytest.raises(EvidenceError, match="EVIDENCE_CONFLICT"):
        audit.verify_candidate_source(
            _source_subject(audit, snapshot_id, "0" * 16, tree_sha256),
            archive_root=archive_root,
            runtime_root=runtime_root,
        )
