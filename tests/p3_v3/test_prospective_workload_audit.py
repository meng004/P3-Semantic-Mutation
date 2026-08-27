from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest


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
