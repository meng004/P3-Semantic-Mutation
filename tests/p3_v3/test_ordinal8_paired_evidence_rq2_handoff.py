from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    write_canonical_json,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "research/evidence/p3_claim_ledger_v1.3.0.yml"
SCRIPT = REPO_ROOT / "scripts/p3_v3/build_ordinal8_paired_evidence_rq2_handoff.py"
FORMAL_JSON = (
    REPO_ROOT / "data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json"
)
FORMAL_MD = (
    REPO_ROOT
    / "docs/review_20260828/p3_c3_ordinal8_paired_evidence_rq2_handoff.md"
)
INFRA = (
    REPO_ROOT / "data/p3_v3/phase3/ordinal8-first-paired-evidence/paired-evidence.json"
)
REPLAY = (
    REPO_ROOT
    / "data/p3_v3/phase3/ordinal8-first-paired-evidence-clean-replay-v1/clean-replay.json"
)
BATCH = (
    REPO_ROOT
    / "data/p3_v3/phase3/ordinal8-remaining-three-paired-batch-v1/paired-batch.json"
)


def _builder():
    spec = importlib.util.spec_from_file_location(
        "build_ordinal8_paired_evidence_rq2_handoff", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_four_pair_reductions_are_rebuilt_from_cells():
    module = _builder()
    handoff = module.build_handoff(REPO_ROOT)
    pairs = handoff["pairs"]
    assert len(pairs) == 4
    assert [row["family_mechanism"] for row in pairs] == [
        "INV/TF",
        "INV/SI",
        "CMP/TF",
        "CMP/SI",
    ]
    expected = {
        "INV/TF": ("KILL", "KILL"),
        "INV/SI": ("KILL", "SURVIVE"),
        "CMP/TF": ("KILL", "KILL"),
        "CMP/SI": ("KILL", "KILL"),
    }
    for row in pairs:
        assert (row["semantic_pair_result"], row["syntactic_pair_result"]) == expected[
            row["family_mechanism"]
        ]
        assert row["frozen_input_count"] == 5
        assert row["original_cell_survive"] == 5
        assert row["semantic_cell_kill"] == 5
        assert row["valid_cells"] == 15
    assert handoff["reductions"]["semantic_pair_kill"] == "4/4"
    assert handoff["reductions"]["syntactic_pair_kill"] == "3/4"
    assert handoff["reductions"]["original_cell_survive"] == "20/20"
    assert handoff["reductions"]["semantic_cell_kill"] == "20/20"
    assert handoff["reductions"]["syntactic_cell_kill"] == "15/20"
    assert handoff["paired_contingency"]["both_killed"] == 3
    assert handoff["paired_contingency"]["semantic_only"] == 1
    assert handoff["paired_contingency"]["syntactic_only"] == 0
    assert handoff["paired_contingency"]["neither"] == 0
    assert handoff["paired_contingency"]["descriptive_pair_kill_rate_difference"] == 0.25


def test_input_cells_are_not_independent_pairs():
    module = _builder()
    handoff = module.build_handoff(REPO_ROOT)
    structure = handoff["analysis_units"]
    assert structure["primary_descriptive_unit"] == "frozen_semantic_syntactic_pair"
    assert structure["n_pairs"] == 4
    assert structure["valid_cells"] == 60
    assert structure["valid_cells"] != structure["n_pairs"]
    assert structure["n_pairs"] * 5 * 3 == 60
    assert handoff["reductions"]["independent_pair_denominator"] == 4
    assert structure["input_cells_are_independent_pairs"] is False
    assert structure["input_cells_are_independent_experimental_units"] is False
    assert any(
        "20 valid input cells are 20 independent experimental units" in claim
        for claim in handoff["blocked_claims"]
    )


def test_single_project_bootstrap_is_unidentifiable():
    module = _builder()
    handoff = module.build_handoff(REPO_ROOT)
    uncertainty = handoff["uncertainty"]
    assert uncertainty["project_cluster_count"] == 1
    assert uncertainty["project_clustered_bootstrap_status"] == "UNIDENTIFIABLE"
    assert uncertainty["substitute_bootstrap_used"] is False
    assert handoff["rq2_coverage"]["project-clustered bootstrap interval"] == (
        "UNIDENTIFIABLE"
    )
    assert uncertainty["exact_binomial_status"] == "UNMEASURED"
    assert (
        uncertainty["normalized_patch_exact_overlap"]
        == "UNMEASURED_MISSING_FROZEN_INPUT"
    )
    assert (
        uncertainty["mutant_tree_exact_overlap"] == "UNMEASURED_MISSING_FROZEN_INPUT"
    )


def test_infrastructure_failure_is_retained_outside_kill_estimates():
    module = _builder()
    handoff = module.build_handoff(REPO_ROOT)
    funnel = handoff["execution_funnel"]
    assert funnel["infrastructure_failure_cells"] == 15
    assert funnel["infrastructure_failure_scientific_result_observed"] is False
    assert funnel["prior_infrastructure_record"]["artifact_sha256"] == (
        "3f317d80c163114d9b5f5ee8373cec044c8f90fb04934a7ae63f0625114aee8f"
    )
    assert funnel["prior_infrastructure_deleted"] is False
    assert handoff["reductions"]["valid_cells"] == 60
    assert 15 not in {
        handoff["reductions"]["semantic_cell_kill_count"],
        handoff["paired_contingency"]["both_killed"],
    }


def test_identity_mismatch_fails_closed(tmp_path):
    module = _builder()
    mutated = read_canonical_json(REPLAY)
    mutated["artifact_sha256"] = "1" * 64
    target = tmp_path / "clean-replay.json"
    write_canonical_json(target, mutated, exclusive=True)
    with pytest.raises(EvidenceError, match="IDENTITY|artifact|SHA"):
        module.verify_bound_record(
            target,
            expected_file_sha256=(
                "5b734c2a21283d6cdb83a5827d50bdf688d69eb7e2dcd620d69b01a9875000ff"
            ),
            expected_artifact_sha256=(
                "f0ce09ff92e181fda27573c612643d3b48a8e4e24081d390f19acc4ebbd8897f"
            ),
        )


def test_handoff_self_hash_and_c3_remain_blocked(tmp_path):
    module = _builder()
    output_json = tmp_path / "handoff.json"
    output_md = tmp_path / "handoff.md"
    record = module.write_handoff(
        REPO_ROOT, json_path=output_json, markdown_path=output_md
    )
    written = read_canonical_json(output_json)
    body = {key: value for key, value in written.items() if key != "artifact_sha256"}
    assert written["artifact_sha256"] == canonical_sha256(body)
    assert written["artifact_sha256"] == record["artifact_sha256"]
    assert written["claim_ceiling"]["claim_id"] == (
        "C3_SEMANTIC_CONSTRUCT_DISTINCTNESS"
    )
    assert written["claim_ceiling"]["claim_status"] == "blocked"
    assert written["claim_ceiling"]["upgrade_condition_satisfied"] is False
    assert "status: blocked" in LEDGER.read_text(encoding="utf-8")
    assert file_sha256(LEDGER)
    text = output_md.read_text(encoding="utf-8")
    assert text.startswith("在一个受控 NumPy subject")
    assert "4/4 KILL" in text
    assert "3/4 KILL" in text
    assert "C3 仍为 blocked" in text
    assert re.search(r"n_subjects\s*=\s*1", text)
    assert re.search(r"n_projects\s*=\s*1", text)
    assert re.search(r"n_sites\s*=\s*2", text)
    assert re.search(r"n_pairs\s*=\s*4", text)
    assert "20/20" in text
    assert written["analysis_units"]["valid_cells"] == 60


def test_formal_paths_and_no_ledger_or_runner_imports():
    module = _builder()
    assert module.FORMAL_JSON_RELATIVE == (
        "data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json"
    )
    source = SCRIPT.read_text(encoding="utf-8")
    assert "run_ordinal8" not in source
    assert "run_formal_once" not in source
    assert "run_clean_replay_once" not in source
    assert "p3_claim_ledger_v1.3.0.yml" in source
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "C3_SEMANTIC_CONSTRUCT_DISTINCTNESS" in ledger
    assert "status: blocked" in ledger
    if FORMAL_JSON.is_file():
        rec = read_canonical_json(FORMAL_JSON)
        body = {key: value for key, value in rec.items() if key != "artifact_sha256"}
        assert rec["artifact_sha256"] == canonical_sha256(body)
        assert rec["claim_ceiling"]["claim_status"] == "blocked"
    if FORMAL_MD.is_file():
        assert FORMAL_MD.read_text(encoding="utf-8").startswith("在一个受控 NumPy subject")
    assert INFRA.is_file()
    assert REPLAY.is_file()
    assert BATCH.is_file()
