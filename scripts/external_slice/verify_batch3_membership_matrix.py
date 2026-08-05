#!/usr/bin/env python3
"""Verify Batch 3 membership byte-identity and A1d-r3 semantic binding."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_IDS = [
    "EXT-numpy-01",
    "EXT-scipy-01",
    "EXT-scikit-learn-01",
    "EXT-statsmodels-01",
    "EXT-statsmodels-02",
    "EXT-statsmodels-03",
]
FORMAL_SEEDS = [0, 1, 2, 3, 4]
SMOKE_SEEDS = [0]
SHEET_SHA256 = (
    "77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a"
)


def _load_helpers():
    path = Path(__file__).resolve().parent / "batch3_a1d_r1.py"
    spec = importlib.util.spec_from_file_location("batch3_a1d_r1", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _expected_counts(case_results: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "batch_size": len(case_results),
        "proposed_PASS": sum(1 for c in case_results if c.get("proposed") == "PASS"),
        "proposed_REPRO_FAILED": sum(
            1 for c in case_results if c.get("proposed") == "REPRO_FAILED"
        ),
    }


def verify_batch3_state(
    *,
    membership_path: Path | None = None,
    matrix_path: Path | None = None,
    readiness_path: Path | None = None,
    handoff_path: Path | None = None,
    sheet_path: Path | None = None,
    candidate_path: Path | None = None,
    repro_root: Path | None = None,
) -> int:
    """Semantically bind membership/matrix/readiness/handoff/artifacts.

    Raises AssertionError on any mismatch. Returns 0 on success.
    """
    helpers = _load_helpers()
    membership_path = membership_path or (
        ROOT / "data/external_slice/BATCH3_MEMBERSHIP.json"
    )
    matrix_path = matrix_path or (
        ROOT / "data/external_slice/BATCH3_EXECUTION_MATRIX.json"
    )
    readiness_path = readiness_path or (
        ROOT / "data/external_slice/readiness_batch3.json"
    )
    handoff_path = handoff_path or (
        ROOT / "data/external_slice/HANDOFF_REPRO_BATCH3.json"
    )
    sheet_path = sheet_path or (ROOT / "data/external_slice/admission_sheet.csv")
    candidate_path = candidate_path or (
        ROOT / "data/external_slice/admission_sheet.cursor_candidate.csv"
    )
    repro_root = repro_root or (ROOT / "data/external_slice/reproduction")

    membership = json.loads(membership_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))

    ids = [row["neutral_id"] for row in membership["members"]]
    assert ids == matrix["members"] == EXPECTED_IDS
    mem_sha = hashlib.sha256(membership_path.read_bytes()).hexdigest()
    assert mem_sha == matrix["membership_sha256_expected"]
    assert mem_sha == readiness["frozen_membership_sha256"]
    assert matrix["smoke"]["seeds"] == SMOKE_SEEDS
    assert matrix["formal_repetitions"]["seeds"] == FORMAL_SEEDS
    assert readiness["smoke_seeds"] == SMOKE_SEEDS
    assert readiness["formal_seeds"] == FORMAL_SEEDS

    readiness_ids = [case["neutral_id"] for case in readiness["cases"]]
    handoff_ids = [case["neutral_id"] for case in handoff["case_results"]]
    assert readiness_ids == ids
    assert handoff_ids == ids, (
        f"handoff case ID/order mismatch: {handoff_ids} != {ids}"
    )
    assert handoff["batch"].get("formal_seeds") == FORMAL_SEEDS
    assert handoff["batch"].get("smoke_seeds") == SMOKE_SEEDS
    assert handoff["inputs"].get("formal_seeds") == FORMAL_SEEDS

    reconstructed_verdicts: list[str] = []
    for idx, case in enumerate(readiness["cases"]):
        nid = case["neutral_id"]
        hcase = handoff["case_results"][idx]
        assert hcase["neutral_id"] == nid
        case_dir = repro_root / nid

        reconstructed = helpers.reconstruct_formal_per_seed_from_artifacts(
            case_dir, formal_seeds=FORMAL_SEEDS
        )
        assert set(reconstructed) == set(FORMAL_SEEDS), (
            f"{nid}: reconstructed seeds {sorted(reconstructed)} "
            f"!= {FORMAL_SEEDS}"
        )
        aggregation = helpers.aggregate_formal_verdict(
            reconstructed, formal_seeds=FORMAL_SEEDS
        )
        verdict = aggregation["proposed_crit_dual_arm_repro"]
        reconstructed_verdicts.append(verdict)

        for seed in FORMAL_SEEDS:
            row = next(r for r in aggregation["seed_rows"] if r["seed"] == seed)
            if verdict == "PASS":
                assert row["seed_ok"] is True
                assert row["input_parity_ok"] is True
                assert row["buggy_property_holds"] is False
                assert row["fixed_property_holds"] is True
                assert row["buggy_raw_return_code"] == 1
                assert row["fixed_raw_return_code"] == 0

        reported = case.get("formal_aggregation") or {}
        assert reported.get("formal_seeds", FORMAL_SEEDS) == FORMAL_SEEDS
        assert case.get("proposed_crit_dual_arm_repro") == verdict
        assert reported.get("proposed_crit_dual_arm_repro") == verdict
        assert reported.get("failing_seeds") == aggregation["failing_seeds"]
        if verdict == "PASS":
            assert aggregation.get("all_seeds_contrasted") is True
            assert reported.get("all_seeds_contrasted") is True

        matrix_payload = json.loads(
            (case_dir / "REPETITION_MATRIX.json").read_text(encoding="utf-8")
        )
        matrix_agg = matrix_payload.get("aggregation") or {}
        assert matrix_agg.get("proposed_crit_dual_arm_repro") == verdict
        assert matrix_agg.get("failing_seeds") == aggregation["failing_seeds"]
        assert matrix_payload.get("formal_seeds") == FORMAL_SEEDS

        # Bind handoff case row to reconstructed + readiness surfaces.
        assert hcase.get("proposed") == verdict == case.get(
            "proposed_crit_dual_arm_repro"
        )
        assert hcase.get("formal_seeds") == FORMAL_SEEDS
        assert hcase.get("smoke_seeds") == SMOKE_SEEDS
        seed0 = reconstructed[0]
        expected_rcs = {
            "buggy": seed0["buggy_raw_return_code"],
            "fixed": seed0["fixed_raw_return_code"],
        }
        assert case.get("trigger_exit_codes") == expected_rcs
        assert hcase.get("trigger_exit_codes") == expected_rcs
        per_case_exit = (
            handoff.get("exit_codes", {}).get("per_case_trigger", {}).get(nid)
        )
        assert per_case_exit == expected_rcs

        assert hcase.get("failure_stage") == case.get("failure_stage")
        if "failure_detail" in hcase:
            assert hcase.get("failure_detail") == case.get("failure_detail")
        if verdict == "PASS":
            assert hcase.get("failure_stage") is None
            assert case.get("failure_stage") is None
        else:
            assert hcase.get("failure_stage") is not None
            assert case.get("failure_stage") is not None

    # Recalculate and bind handoff counts / failures from reconstructed verdicts.
    expected_case_results = []
    for idx, nid in enumerate(ids):
        case = readiness["cases"][idx]
        expected_case_results.append(
            {
                "neutral_id": nid,
                "proposed": reconstructed_verdicts[idx],
                "trigger_exit_codes": case.get("trigger_exit_codes"),
                "failure_stage": case.get("failure_stage"),
                "failure_detail": case.get("failure_detail"),
                "formal_seeds": FORMAL_SEEDS,
                "smoke_seeds": SMOKE_SEEDS,
            }
        )
    expected_counts = {
        "batch_size": len(ids),
        "proposed_PASS": sum(1 for v in reconstructed_verdicts if v == "PASS"),
        "proposed_REPRO_FAILED": sum(
            1 for v in reconstructed_verdicts if v == "REPRO_FAILED"
        ),
    }
    assert readiness["counts"] == expected_counts
    assert handoff["counts"] == expected_counts
    assert handoff["counts"] == _expected_counts(
        [
            {"proposed": row["proposed"]}
            for row in handoff["case_results"]
        ]
    )

    expected_failures = [
        row
        for row in handoff["case_results"]
        if row.get("proposed") == "REPRO_FAILED"
    ]
    assert handoff.get("failures") == expected_failures
    assert [row["neutral_id"] for row in expected_failures] == [
        ids[i]
        for i, verdict in enumerate(reconstructed_verdicts)
        if verdict == "REPRO_FAILED"
    ]
    for fail in handoff.get("failures", []):
        assert fail.get("proposed") == "REPRO_FAILED"
        assert fail.get("failure_stage") is not None

    sheet_sha = hashlib.sha256(sheet_path.read_bytes()).hexdigest()
    assert sheet_sha == SHEET_SHA256
    rows = list(csv.DictReader(sheet_path.open(encoding="utf-8")))
    assert all(
        row["crit_dual_arm_repro"] == "PENDING"
        for row in rows
        if row["neutral_id"] in set(ids)
    )
    candidates = list(csv.DictReader(candidate_path.open(encoding="utf-8")))
    assert all(row["crit_dual_arm_repro"] == "PENDING" for row in candidates)
    print("membership_matrix_ok", len(ids))
    return 0


def main() -> int:
    return verify_batch3_state()


if __name__ == "__main__":
    raise SystemExit(main())
