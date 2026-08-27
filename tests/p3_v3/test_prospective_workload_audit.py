from __future__ import annotations

from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


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
