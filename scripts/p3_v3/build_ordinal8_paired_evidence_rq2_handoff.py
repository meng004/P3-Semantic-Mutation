#!/usr/bin/env python3
"""Deterministic RQ2 handoff from frozen ordinal-8 paired evidence. No experiment."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    write_canonical_json,
)

SCHEMA_VERSION = "p3-ordinal8-paired-evidence-rq2-handoff-v1"
TASK_ID = "P3_C3_ORDINAL8_PAIRED_EVIDENCE_ANALYSIS_AND_RQ2_HANDOFF"
ANALYSIS_HEAD = "181fea50bdcf04aa5c40824368d02215cfd4265e"
SUBJECT_ID = "0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48"
LEDGER_RELATIVE = "research/evidence/p3_claim_ledger_v1.3.0.yml"
ANALYSIS_SPEC_RELATIVE = "data/p3_v3/protocol/analysis_spec.md"
FORMAL_JSON_RELATIVE = "data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json"
FORMAL_MD_RELATIVE = (
    "docs/review_20260828/p3_c3_ordinal8_paired_evidence_rq2_handoff.md"
)
QUALIFICATION_RELATIVE = (
    "data/p3_v3/phase3/ordinal8-controlled-numpy-runtime/qualification.json"
)
INFRA_RELATIVE = "data/p3_v3/phase3/ordinal8-first-paired-evidence/paired-evidence.json"
REPLAY_RELATIVE = (
    "data/p3_v3/phase3/ordinal8-first-paired-evidence-clean-replay-v1/clean-replay.json"
)
BATCH_RELATIVE = (
    "data/p3_v3/phase3/ordinal8-remaining-three-paired-batch-v1/paired-batch.json"
)
CONTRACTS_RELATIVE = "data/p3_v3/phase2/ordinal8-partial-contract-freeze/contracts.json"
SLOT_INVENTORY_RELATIVE = "data/p3_v3/phase2/slot-inventory.json"
CLOSURE_ROOT_RELATIVE = (
    "data/p3_v3/phase2/prospective-applicability-search-v2/subjects/"
    "4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b"
)
VARIANTS = ("original", "semantic", "syntactic")

INFRA_COMMIT = "2a698e74ab49a6a73b98d3de9f21478156600f09"
INFRA_FILE_SHA256 = "8e0de660deba8b4bc00d5994dd180bfefb7aca9673583dcdef426ba27673855f"
INFRA_ARTIFACT_SHA256 = (
    "3f317d80c163114d9b5f5ee8373cec044c8f90fb04934a7ae63f0625114aee8f"
)
REPLAY_COMMIT = "1b945f1bf3238c03c9ad4dc7170dc69e6bb744c1"
REPLAY_FILE_SHA256 = "5b734c2a21283d6cdb83a5827d50bdf688d69eb7e2dcd620d69b01a9875000ff"
REPLAY_ARTIFACT_SHA256 = (
    "f0ce09ff92e181fda27573c612643d3b48a8e4e24081d390f19acc4ebbd8897f"
)
BATCH_COMMIT = "181fea50bdcf04aa5c40824368d02215cfd4265e"
BATCH_FILE_SHA256 = "ee4bcc00e1ea21d3b452eed5eb52384b27fbcc7544350dd569c38cd997fc83a0"
BATCH_ARTIFACT_SHA256 = (
    "2b14ac9e111db6189eeab890ad2f52468220233588db12e99e6790707759a5ed"
)
QUALIFICATION_COMMIT = "256305eb7d0bd835cb1fc37d99e5cc1732fefba2"
QUALIFICATION_FILE_SHA256 = (
    "290506c4324a062d56fecbbe22d3baa829cd99a2668fee4eeb70fd25d7ac46e0"
)
QUALIFICATION_ARTIFACT_SHA256 = (
    "501203515a524bcd4b51a6148908af25dbdd09932c7790e2e257404533d80abf"
)


def verify_bound_record(
    path: str | Path,
    *,
    expected_file_sha256: str,
    expected_artifact_sha256: str,
) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise EvidenceError("E_EVIDENCE_IDENTITY", f"record absent: {source}")
    if file_sha256(source) != expected_file_sha256:
        raise EvidenceError("E_EVIDENCE_IDENTITY", f"file SHA-256 differs: {source}")
    record = read_canonical_json(source)
    if not isinstance(record, Mapping):
        raise EvidenceError("E_EVIDENCE_IDENTITY", f"record is not an object: {source}")
    digest = record.get("artifact_sha256")
    body = {key: value for key, value in record.items() if key != "artifact_sha256"}
    if digest != expected_artifact_sha256 or digest != canonical_sha256(body):
        raise EvidenceError(
            "E_EVIDENCE_IDENTITY", f"artifact SHA-256 differs: {source}"
        )
    return dict(record)


def _verify_ancestor(repo_root: Path, commit: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", commit, "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise EvidenceError("E_EVIDENCE_IDENTITY", f"{commit} is not an ancestor")


def _require_c3_blocked(repo_root: Path) -> dict[str, str]:
    text = (repo_root / LEDGER_RELATIVE).read_text(encoding="utf-8")
    if "claim_id: C3_SEMANTIC_CONSTRUCT_DISTINCTNESS" not in text:
        raise EvidenceError("E_CLAIM_CEILING", "C3 claim is absent from the ledger")
    if "upgrade_condition: \"RQ2 paired evidence and uncertainty accounting complete\"" not in text:
        raise EvidenceError("E_CLAIM_CEILING", "C3 upgrade_condition differs")
    block = text.split("claim_id: C3_SEMANTIC_CONSTRUCT_DISTINCTNESS", 1)[1]
    block = block.split("claim_id:", 1)[0]
    if "status: blocked" not in block:
        raise EvidenceError("E_CLAIM_CEILING", "C3 is not blocked")
    return {
        "claim_id": "C3_SEMANTIC_CONSTRUCT_DISTINCTNESS",
        "claim_status": "blocked",
        "upgrade_condition": "RQ2 paired evidence and uncertainty accounting complete",
        "upgrade_condition_satisfied": False,
    }


def _reduce_cells(results: Sequence[str]) -> str:
    if any(item == "KILL" for item in results):
        return "KILL"
    if results and all(item == "SURVIVE" for item in results):
        return "SURVIVE"
    raise EvidenceError("E_PAIR_REDUCER", f"unreducible cell results: {results}")


def _cell_result(cell: Mapping[str, Any]) -> str:
    result = cell.get("scientific_result") or cell.get("verdict")
    if result not in {"KILL", "SURVIVE"}:
        raise EvidenceError("E_PAIR_REDUCER", f"valid cell is not kill/survival: {cell}")
    if cell.get("status") != "PASS":
        raise EvidenceError("E_PAIR_REDUCER", "valid cell status is not PASS")
    return str(result)


def _ordered_cells(
    terminals: Mapping[str, Any], input_ids: Sequence[str], variant: str
) -> list[dict[str, Any]]:
    if variant not in terminals:
        raise EvidenceError("E_PAIR_REDUCER", f"variant {variant} is absent")
    cells = terminals[variant]
    if not isinstance(cells, Mapping):
        raise EvidenceError("E_PAIR_REDUCER", f"{variant} terminals are not an object")
    if set(cells) != set(input_ids):
        raise EvidenceError("E_PAIR_REDUCER", f"{variant} input IDs differ")
    return [dict(cells[input_id]) for input_id in input_ids]


def _count(results: Sequence[str], value: str) -> int:
    return sum(1 for item in results if item == value)


def _scan_overlap_fields(record: Mapping[str, Any]) -> None:
    blob = repr(record).lower()
    for token in (
        "normalized-patch",
        "normalized_patch",
        "mutant-tree",
        "mutant_tree",
        "exact_overlap",
    ):
        if token in blob:
            raise EvidenceError(
                "E_ANALYSIS_SPEC",
                f"overlap field {token} is present but unparsed",
            )


def _rebuild_pair(
    *,
    family_mechanism: str,
    slot_id: str,
    site_id: str,
    contract_id: str,
    input_ids: Sequence[str],
    terminals: Mapping[str, Any],
    recorded_semantic: str | None,
    recorded_syntactic: str | None,
    semantic_patch_sha256: str,
    syntactic_patch_sha256: str,
    source_record: str,
) -> dict[str, Any]:
    if len(input_ids) != 5 or len(set(input_ids)) != 5:
        raise EvidenceError("E_PAIR_REDUCER", f"{family_mechanism} inputs are not five unique IDs")
    original = [_cell_result(cell) for cell in _ordered_cells(terminals, input_ids, "original")]
    semantic = [_cell_result(cell) for cell in _ordered_cells(terminals, input_ids, "semantic")]
    syntactic = [_cell_result(cell) for cell in _ordered_cells(terminals, input_ids, "syntactic")]
    semantic_pair = _reduce_cells(semantic)
    syntactic_pair = _reduce_cells(syntactic)
    if recorded_semantic not in {None, semantic_pair}:
        raise EvidenceError("E_PAIR_REDUCER", f"{family_mechanism} semantic reducer differs")
    if recorded_syntactic not in {None, syntactic_pair}:
        raise EvidenceError("E_PAIR_REDUCER", f"{family_mechanism} syntactic reducer differs")
    if _reduce_cells(original) != "SURVIVE" or _count(original, "SURVIVE") != 5:
        raise EvidenceError("E_PAIR_REDUCER", f"{family_mechanism} original is not 5/5 SURVIVE")
    return {
        "family_mechanism": family_mechanism,
        "slot_id": slot_id,
        "site_id": site_id,
        "contract_id": contract_id,
        "source_record": source_record,
        "input_ids": list(input_ids),
        "frozen_input_count": 5,
        "valid_cells": 15,
        "original_cell_survive": _count(original, "SURVIVE"),
        "semantic_cell_kill": _count(semantic, "KILL"),
        "syntactic_cell_kill": _count(syntactic, "KILL"),
        "semantic_pair_result": semantic_pair,
        "syntactic_pair_result": syntactic_pair,
        "semantic_patch_sha256": semantic_patch_sha256,
        "syntactic_patch_sha256": syntactic_patch_sha256,
        "paired_class": (
            "both_killed"
            if semantic_pair == "KILL" and syntactic_pair == "KILL"
            else "semantic_only"
            if semantic_pair == "KILL" and syntactic_pair == "SURVIVE"
            else "syntactic_only"
            if semantic_pair == "SURVIVE" and syntactic_pair == "KILL"
            else "neither"
        ),
    }


def _infra_funnel(record: Mapping[str, Any]) -> dict[str, Any]:
    input_ids = list(record["input_ids"])
    if len(input_ids) != 5:
        raise EvidenceError("E_FUNNEL", "infrastructure inventory is not five inputs")
    count = 0
    for variant in VARIANTS:
        cells = _ordered_cells(record["per_input_terminals"], input_ids, variant)
        for cell in cells:
            count += 1
            if cell.get("status") != "FAIL_INFRASTRUCTURE":
                raise EvidenceError("E_FUNNEL", "infrastructure cell status changed")
            if cell.get("scientific_result") not in {None, "UNOBSERVED"}:
                raise EvidenceError("E_FUNNEL", "infrastructure cell has a kill/survival result")
    if count != 15:
        raise EvidenceError("E_FUNNEL", "infrastructure funnel is not 15 cells")
    return {
        "infrastructure_failure_cells": 15,
        "infrastructure_failure_scientific_result_observed": False,
        "prior_infrastructure_deleted": False,
        "failure_code": "numpy.array_api import failed",
        "slot_id": record["slot_id"],
        "site_id": record["site_id"],
        "controlled_subject_id": record["controlled_subject_id"],
        "counts_toward_kill_survival_estimates": False,
        "prior_infrastructure_record": {
            "commit": INFRA_COMMIT,
            "path": INFRA_RELATIVE,
            "file_sha256": INFRA_FILE_SHA256,
            "artifact_sha256": INFRA_ARTIFACT_SHA256,
        },
    }


def _contract_coverage(repo_root: Path) -> dict[str, Any]:
    contracts = read_canonical_json(repo_root / CONTRACTS_RELATIVE)
    inventory = read_canonical_json(repo_root / SLOT_INVENTORY_RELATIVE)
    if not isinstance(contracts, Mapping) or not isinstance(inventory, Mapping):
        raise EvidenceError("E_COVERAGE", "freeze artifacts are not objects")
    subject_slots = [
        row
        for row in inventory["slots"]
        if row.get("controlled_subject_id") == SUBJECT_ID
    ]
    if len(subject_slots) != 10:
        raise EvidenceError("E_COVERAGE", "ordinal-8 slot inventory is not ten rows")
    closures: dict[str, dict[str, Any]] = {}
    for path in (repo_root / CLOSURE_ROOT_RELATIVE).glob("slot-closure-*.json"):
        row = read_canonical_json(path)
        closures[row["slot_id"]] = row
    families_with_contract = sorted(
        {
            next(
                item["semantic_contract_family"]
                for item in subject_slots
                if item["slot_id"] == slot_id
            )
            for slot_id in contracts
        }
    )
    mechanisms = sorted(
        {
            next(
                item["permitted_construction_mechanism"]
                for item in subject_slots
                if item["slot_id"] == slot_id
            )
            for slot_id in contracts
        }
    )
    mono = [
        row
        for row in subject_slots
        if row["semantic_contract_family"] == "MONO"
    ]
    if any(row["slot_id"] in contracts for row in mono):
        raise EvidenceError("E_COVERAGE", "MONO entered the contract freeze")
    if any(closures[row["slot_id"]].get("state") != "SITE_FROZEN" for row in mono):
        raise EvidenceError("E_COVERAGE", "MONO SITE_FROZEN state differs")
    for family in ("CONV", "DYN"):
        rows = [row for row in subject_slots if row["semantic_contract_family"] == family]
        for row in rows:
            state = closures[row["slot_id"]].get("state")
            site_id = closures[row["slot_id"]].get("site_id")
            if state == "SITE_FROZEN" or site_id:
                raise EvidenceError("E_COVERAGE", f"{family} unexpectedly has SITE_FROZEN")
            if state != "APPLICABILITY_CLOSED_NOT_APPLICABLE":
                raise EvidenceError("E_COVERAGE", f"{family} closure state differs")
    return {
        "represented_families": families_with_contract,
        "represented_mechanisms": mechanisms,
        "successful_frozen_pairs": 4,
        "target_families": ["INV", "MONO", "CONV", "DYN", "CMP"],
        "mono": "SITE_FROZEN_WITHOUT_CONTRACT",
        "conv": "NO_SITE_FROZEN",
        "dyn": "NO_SITE_FROZEN",
        "unrepresented_families_are_not_kill_failures": True,
    }


def build_handoff(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    _verify_ancestor(root, ANALYSIS_HEAD)
    _verify_ancestor(root, INFRA_COMMIT)
    _verify_ancestor(root, REPLAY_COMMIT)
    _verify_ancestor(root, BATCH_COMMIT)
    _verify_ancestor(root, QUALIFICATION_COMMIT)
    claim = _require_c3_blocked(root)
    infra = verify_bound_record(
        root / INFRA_RELATIVE,
        expected_file_sha256=INFRA_FILE_SHA256,
        expected_artifact_sha256=INFRA_ARTIFACT_SHA256,
    )
    replay = verify_bound_record(
        root / REPLAY_RELATIVE,
        expected_file_sha256=REPLAY_FILE_SHA256,
        expected_artifact_sha256=REPLAY_ARTIFACT_SHA256,
    )
    batch = verify_bound_record(
        root / BATCH_RELATIVE,
        expected_file_sha256=BATCH_FILE_SHA256,
        expected_artifact_sha256=BATCH_ARTIFACT_SHA256,
    )
    qualification = verify_bound_record(
        root / QUALIFICATION_RELATIVE,
        expected_file_sha256=QUALIFICATION_FILE_SHA256,
        expected_artifact_sha256=QUALIFICATION_ARTIFACT_SHA256,
    )
    for record in (infra, replay, batch):
        _scan_overlap_fields(record)
    if infra.get("controlled_subject_id") != SUBJECT_ID:
        raise EvidenceError("E_EVIDENCE_IDENTITY", "infrastructure subject differs")
    if replay.get("slot_id") != infra.get("slot_id"):
        raise EvidenceError("E_EVIDENCE_IDENTITY", "clean-replay slot differs")
    if qualification.get("qualification", {}).get("controlled", {}).get("version") != "2.0.0.dev0":
        raise EvidenceError("E_EVIDENCE_IDENTITY", "controlled NumPy version differs")

    inv_tf = _rebuild_pair(
        family_mechanism="INV/TF",
        slot_id=replay["slot_id"],
        site_id=replay["site_id"],
        contract_id=replay["contract_id"],
        input_ids=list(replay["input_ids"]),
        terminals=replay["per_input_terminals"],
        recorded_semantic=replay["per_mutant"]["semantic"]["scientific_result"],
        recorded_syntactic=replay["per_mutant"]["syntactic"]["scientific_result"],
        semantic_patch_sha256=replay["semantic_patch_sha256"],
        syntactic_patch_sha256=replay["syntactic_patch_sha256"],
        source_record="clean-replay",
    )
    remaining = []
    batch_slots = {row["slot_id"]: row for row in batch["slots"]}
    expected_remaining = (
        (
            "INV/SI",
            "e8fd94d60c42ed7357d8e00ebc1135b55b44dbde4978f887ab54abe94b261c6c",
        ),
        (
            "CMP/TF",
            "e0b42ce7f2c60d9b3d0feae5ce3280d1619ec78b75c22c3e41fc6c936c3485e6",
        ),
        (
            "CMP/SI",
            "06556e4b744f26766ef8593fc4ae727103082944ae6b26c6179fc947c3a2f1f5",
        ),
    )
    patch_index = {
        (row["slot_id"], row["kind"]): row["patch_sha256"] for row in batch["patches"]
    }
    for family_mechanism, slot_id in expected_remaining:
        slot = batch["per_slot"][slot_id]
        identity = batch_slots[slot_id]
        remaining.append(
            _rebuild_pair(
                family_mechanism=family_mechanism,
                slot_id=slot_id,
                site_id=identity["site_id"],
                contract_id=identity["contract_id"],
                input_ids=list(identity["input_ids"]),
                terminals=slot["per_input_terminals"],
                recorded_semantic=slot["per_mutant"]["semantic"]["scientific_result"],
                recorded_syntactic=slot["per_mutant"]["syntactic"]["scientific_result"],
                semantic_patch_sha256=patch_index[(slot_id, "semantic")],
                syntactic_patch_sha256=patch_index[(slot_id, "syntactic")],
                source_record="remaining-three-batch",
            )
        )
    pairs = [inv_tf, *remaining]
    if len(pairs) != 4:
        raise EvidenceError("E_PAIR_REDUCER", "pair count differs")
    input_ids = [input_id for pair in pairs for input_id in pair["input_ids"]]
    if len(input_ids) != 20 or len(set(input_ids)) != 20:
        raise EvidenceError("E_PAIR_REDUCER", "valid input IDs are not twenty unique values")
    sites = sorted({pair["site_id"] for pair in pairs})
    if len(sites) != 2:
        raise EvidenceError("E_PAIR_REDUCER", "distinct site count differs")
    both = sum(pair["paired_class"] == "both_killed" for pair in pairs)
    semantic_only = sum(pair["paired_class"] == "semantic_only" for pair in pairs)
    syntactic_only = sum(pair["paired_class"] == "syntactic_only" for pair in pairs)
    neither = sum(pair["paired_class"] == "neither" for pair in pairs)
    semantic_pair_kills = sum(pair["semantic_pair_result"] == "KILL" for pair in pairs)
    syntactic_pair_kills = sum(pair["syntactic_pair_result"] == "KILL" for pair in pairs)
    semantic_cell_kills = sum(pair["semantic_cell_kill"] for pair in pairs)
    syntactic_cell_kills = sum(pair["syntactic_cell_kill"] for pair in pairs)
    original_survives = sum(pair["original_cell_survive"] for pair in pairs)
    if (semantic_pair_kills, syntactic_pair_kills, both, semantic_only) != (4, 3, 3, 1):
        raise EvidenceError("E_PAIR_REDUCER", "frozen pair contingency differs")
    if (semantic_cell_kills, syntactic_cell_kills, original_survives) != (20, 15, 20):
        raise EvidenceError("E_PAIR_REDUCER", "frozen cell totals differ")
    coverage = _contract_coverage(root)
    funnel = _infra_funnel(infra)
    funnel.update(
        {
            "valid_cells": 60,
            "valid_pass_cells": 60,
            "clean_replay_valid_cells": 15,
            "remaining_three_valid_cells": 45,
            "qualification_artifact_sha256": QUALIFICATION_ARTIFACT_SHA256,
            "controlled_numpy_version": "2.0.0.dev0",
            "clean_runtime_removed_array_api_block": True,
        }
    )
    body = {
        "analysis_head": ANALYSIS_HEAD,
        "analysis_spec": ANALYSIS_SPEC_RELATIVE,
        "analysis_units": {
            "primary_descriptive_unit": "frozen_semantic_syntactic_pair",
            "n_subjects": 1,
            "n_projects": 1,
            "n_sites": 2,
            "n_pairs": 4,
            "semantic_mutants": 4,
            "syntactic_baselines": 4,
            "frozen_inputs_per_pair": 5,
            "valid_cells": 60,
            "infrastructure_failure_cells": 15,
            "input_cells_are_independent_pairs": False,
            "input_cells_are_independent_experimental_units": False,
            "n_repositories": 1,
            "site_ids": sites,
            "controlled_subject_id": SUBJECT_ID,
        },
        "blocked_claims": [
            "semantic mutants are generally superior to syntactic mutants",
            "semantic mutation is construct-distinct as a completed C3 result",
            "a NumPy or Python population effect",
            "effects outside INV and CMP",
            "cross-subject, cross-repository, or cross-project inference",
            "C3 upgrade_condition is satisfied",
            "the 20 valid input cells are 20 independent experimental units",
            "the 3/4 versus 4/4 contrast is statistically significant",
        ],
        "claim_ceiling": claim,
        "contract_category_coverage": coverage,
        "descriptive_pair_difference_statement": (
            "在该单一受控 subject 的四个冻结 paired mutants 中，semantic mutant "
            "的观察 kill 比例比 syntactic baseline 高 25 个百分点。"
        ),
        "evidence_bindings": {
            "infrastructure_failure": {
                "commit": INFRA_COMMIT,
                "path": INFRA_RELATIVE,
                "file_sha256": INFRA_FILE_SHA256,
                "artifact_sha256": INFRA_ARTIFACT_SHA256,
            },
            "clean_replay": {
                "commit": REPLAY_COMMIT,
                "path": REPLAY_RELATIVE,
                "file_sha256": REPLAY_FILE_SHA256,
                "artifact_sha256": REPLAY_ARTIFACT_SHA256,
            },
            "remaining_three_batch": {
                "commit": BATCH_COMMIT,
                "path": BATCH_RELATIVE,
                "file_sha256": BATCH_FILE_SHA256,
                "artifact_sha256": BATCH_ARTIFACT_SHA256,
            },
            "qualification": {
                "commit": QUALIFICATION_COMMIT,
                "path": QUALIFICATION_RELATIVE,
                "file_sha256": QUALIFICATION_FILE_SHA256,
                "artifact_sha256": QUALIFICATION_ARTIFACT_SHA256,
            },
        },
        "execution_funnel": funnel,
        "limitations": [
            "n_subjects = 1",
            "n_projects = 1",
            "n_sites = 2",
            "n_pairs = 4",
            "project-clustered uncertainty is unidentifiable",
            "family coverage is INV and CMP only",
            "this is a local result from the first eligible subject after prospective-v2 eligibility search",
            "the first infrastructure failure is retained; clean replay is a disclosed new controlled run, not a deletion of that failure",
        ],
        "methodology_audit": {
            "Simpson’s paradox": (
                "RISK_ADDRESSED: primary unit is the frozen pair, not a site-pooled "
                "cell rate; both sites are disclosed."
            ),
            "ecological fallacy": (
                "RISK_ADDRESSED: pair-level 0.25 is not transported to mutants, "
                "inputs, subjects, or projects."
            ),
            "Berkson’s paradox": (
                "NOT_APPLICABLE: inclusion is eligibility-frozen, not conditioning "
                "on both arms being killed."
            ),
            "collider bias": (
                "RISK: first eligible completed subject after prospective search; "
                "disclosed, not treated as a random project draw."
            ),
            "base-rate neglect": (
                "NOT_APPLICABLE: no prevalence claim; original 20/20 SURVIVE is "
                "the local oracle base, not a population rate."
            ),
            "regression to the mean": (
                "NO_EVIDENCE: each pair has one frozen scientific execution; clean "
                "replay followed unobserved infrastructure failure, not a prior kill."
            ),
            "survivorship bias": (
                "RISK_ADDRESSED: CONV/DYN closed-not-applicable and MONO-without-contract "
                "remain in the funnel and are not coded as KILL failures."
            ),
            "look-elsewhere effect": (
                "RISK_ADDRESSED: contrasts are the four frozen pairs and the frozen RQ2 list; "
                "no post-hoc family or statistic shopping."
            ),
            "garden of forking paths": (
                "RISK_ADDRESSED: no McNemar, Fisher, Wald, Wilson, Bayesian, or substitute "
                "bootstrap was added after seeing the 3/4 versus 4/4 split."
            ),
            "correlation/causation confusion": (
                "RISK_ADDRESSED: paired executions are not a causal proof that semantic "
                "operators produce kills."
            ),
            "reverse causality": (
                "NOT_APPLICABLE: mutants and inputs were frozen before valid kill/survival "
                "observation; remaining-three designs were not rewritten from INV/TF outcomes."
            ),
            "pseudo_replication": (
                "RISK_ADDRESSED: 20 input cells and 60 valid cells are repeated measures "
                "inside four pairs, not 20 or 60 independent experiments."
            ),
            "single_project_extrapolation": (
                "RISK_ADDRESSED: project-clustered bootstrap is UNIDENTIFIABLE; no transport."
            ),
            "outcome_disclosed_clean_replay": (
                "RISK_ADDRESSED: the 15-cell infrastructure failure remains in the funnel; "
                "clean replay is a new controlled run after that disclosure."
            ),
        },
        "observed_allowed": [
            "On this NumPy ordinal-8 subject, two frozen sites, four frozen pairs, and five frozen inputs per pair, all four semantic mutants were killed.",
            "Three syntactic baselines were killed and one survived.",
            "The only discordant pair is semantic KILL / syntactic SURVIVE.",
            "The original baseline survived on all 20 valid inputs.",
            "The clean controlled runtime removed the prior numpy.array_api infrastructure block.",
            "The present results are local paired execution evidence.",
        ],
        "pairs": pairs,
        "paired_contingency": {
            "both_killed": both,
            "semantic_only": semantic_only,
            "syntactic_only": syntactic_only,
            "neither": neither,
            "tied_pairs": both + neither,
            "descriptive_pair_kill_rate_difference": 0.25,
        },
        "reductions": {
            "independent_pair_denominator": 4,
            "original_cell_survive": "20/20",
            "original_cell_survive_count": original_survives,
            "semantic_pair_kill": "4/4",
            "semantic_pair_kill_count": semantic_pair_kills,
            "semantic_cell_kill": "20/20",
            "semantic_cell_kill_count": semantic_cell_kills,
            "syntactic_pair_kill": "3/4",
            "syntactic_pair_kill_count": syntactic_pair_kills,
            "syntactic_cell_kill": "15/20",
            "syntactic_cell_kill_count": syntactic_cell_kills,
            "valid_cells": 60,
        },
        "rq2_coverage": {
            "paired semantic/syntactic execution observations": "OBSERVED",
            "complete execution funnel": "OBSERVED",
            "normalized-patch exact overlap": "UNMEASURED",
            "mutant-tree exact overlap": "UNMEASURED",
            "exact binomial uncertainty": "UNMEASURED",
            "contract-category coverage": "OBSERVED",
            "paired subject-level difference": "OBSERVED",
            "project-clustered bootstrap interval": "UNIDENTIFIABLE",
            "multi-subject coverage": "UNIDENTIFIABLE",
            "multi-project coverage": "UNIDENTIFIABLE",
        },
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "uncertainty": {
            "project_cluster_count": 1,
            "project_clustered_bootstrap_status": "UNIDENTIFIABLE",
            "project_clustered_bootstrap_reason": (
                "A single project cannot identify cross-project sampling uncertainty. "
                "Cell, pair, or site bootstrap is not a substitute for the frozen "
                "project-clustered bootstrap."
            ),
            "substitute_bootstrap_used": False,
            "normalized_patch_exact_overlap": "UNMEASURED_MISSING_FROZEN_INPUT",
            "mutant_tree_exact_overlap": "UNMEASURED_MISSING_FROZEN_INPUT",
            "exact_binomial_status": "UNMEASURED",
            "exact_binomial_reason": (
                "RQ2 exact binomial intervals attach to independent normalized-patch "
                "and mutant-tree exact-overlap trials. Those fields are absent from "
                "the frozen execution records and are not inferred from patch text."
            ),
            "subject_level_pair_difference": 0.25,
            "subject_level_is_population_interval": False,
        },
    }
    return body


def render_markdown(handoff: Mapping[str, Any]) -> str:
    pairs = handoff["pairs"]
    pair_lines = []
    for pair in pairs:
        pair_lines.append(
            f"- `{pair['family_mechanism']}` site `{pair['site_id'][:8]}…`, "
            f"slot `{pair['slot_id'][:8]}…`: original 5/5 SURVIVE; "
            f"semantic {pair['semantic_cell_kill']}/5 {pair['semantic_pair_result']}; "
            f"syntactic {pair['syntactic_cell_kill']}/5 {pair['syntactic_pair_result']} "
            f"({pair['paired_class']})."
        )
    coverage_lines = [
        f"- `{key}`: `{value}`"
        for key, value in handoff["rq2_coverage"].items()
    ]
    audit_lines = [
        f"- **{key}**: {value}"
        for key, value in handoff["methodology_audit"].items()
    ]
    allowed = "\n".join(f"- {item}" for item in handoff["observed_allowed"])
    blocked = "\n".join(f"- {item}" for item in handoff["blocked_claims"])
    limits = "\n".join(f"- {item}" for item in handoff["limitations"])
    families = ", ".join(handoff["contract_category_coverage"]["represented_families"])
    mechanisms = ", ".join(
        handoff["contract_category_coverage"]["represented_mechanisms"]
    )
    return (
        "在一个受控 NumPy subject 的四个冻结 semantic–syntactic pairs 上，"
        "semantic mutants 为 4/4 KILL，syntactic baselines 为 3/4 KILL；"
        "唯一 discordant pair 的方向是 semantic-only kill。"
        "该结果是局部、有效的 paired execution evidence，但单一 project 无法支持"
        "冻结规格要求的 project-clustered uncertainty，因此 C3 仍为 blocked。\n\n"
        "## Observed results\n\n"
        f"- subject / project / sites / pairs / valid cells: "
        f"n_subjects = 1, n_projects = 1, n_sites = 2, n_pairs = 4, "
        f"{handoff['reductions']['valid_cells']} valid PASS cells.\n"
        f"- original baseline: {handoff['reductions']['original_cell_survive']} SURVIVE.\n"
        f"- semantic: pair-level {handoff['reductions']['semantic_pair_kill']} KILL; "
        f"cell-level {handoff['reductions']['semantic_cell_kill']} KILL.\n"
        f"- syntactic: pair-level {handoff['reductions']['syntactic_pair_kill']} KILL; "
        f"cell-level {handoff['reductions']['syntactic_cell_kill']} KILL.\n"
        + "\n".join(pair_lines)
        + "\n\n## Execution funnel including prior infrastructure failure\n\n"
        "- Historical INV/TF attempt: 15/15 `FAIL_INFRASTRUCTURE` "
        "(`numpy.array_api` import failure). Kill/survival was not observed. "
        "That record remains provenance and is excluded from kill/survival estimates.\n"
        "- Qualification of the controlled NumPy `2.0.0.dev0` runtime is identity "
        "and provenance only; it is not a scientific kill observation and was not rerun.\n"
        "- Clean replay then produced 15 valid INV/TF cells. Remaining-three batch "
        "produced 45 valid cells. Combined valid evidence is 60 cells, all PASS.\n"
        "- Clean replay is a disclosed new controlled run after the infrastructure "
        "failure. It does not delete or replace that failure.\n\n"
        "## Paired comparison\n\n"
        f"- both killed: {handoff['paired_contingency']['both_killed']}\n"
        f"- semantic only: {handoff['paired_contingency']['semantic_only']}\n"
        f"- syntactic only: {handoff['paired_contingency']['syntactic_only']}\n"
        f"- neither: {handoff['paired_contingency']['neither']}\n"
        f"- tied pairs: {handoff['paired_contingency']['tied_pairs']}\n"
        f"- {handoff['descriptive_pair_difference_statement']}\n"
        "- This 0.25 figure is not a population effect, mean improvement, "
        "significant advantage, or general superiority.\n"
        "- Primary descriptive unit is the frozen pair (4), not the 20 input cells "
        "and not the 60 valid cells.\n\n"
        "## Contract-category coverage\n\n"
        f"- represented families: {families}\n"
        f"- represented mechanisms: {mechanisms}\n"
        f"- successful frozen pairs: {handoff['contract_category_coverage']['successful_frozen_pairs']}\n"
        "- MONO: SITE_FROZEN but no contract; not a KILL failure and not construct absence.\n"
        "- CONV and DYN: no SITE_FROZEN (`APPLICABILITY_CLOSED_NOT_APPLICABLE`).\n"
        "- Unrepresented families are not written as kill failures.\n\n"
        "## Uncertainty accounting\n\n"
        f"- project_cluster_count = {handoff['uncertainty']['project_cluster_count']}\n"
        f"- project_clustered_bootstrap_status = {handoff['uncertainty']['project_clustered_bootstrap_status']}\n"
        f"- {handoff['uncertainty']['project_clustered_bootstrap_reason']}\n"
        f"- normalized-patch exact overlap: `{handoff['uncertainty']['normalized_patch_exact_overlap']}`\n"
        f"- mutant-tree exact overlap: `{handoff['uncertainty']['mutant_tree_exact_overlap']}`\n"
        f"- exact binomial: `{handoff['uncertainty']['exact_binomial_status']}`; "
        f"{handoff['uncertainty']['exact_binomial_reason']}\n"
        "- No McNemar, Fisher, Wald, Wilson, Bayesian posterior, cell bootstrap, "
        "pair bootstrap, or site bootstrap was computed.\n\n"
        "## RQ2 coverage gaps\n\n"
        + "\n".join(coverage_lines)
        + "\n\nThe observed local paired executions do not complete RQ2 uncertainty "
        "accounting. C3 therefore remains blocked.\n\n"
        "## Allowed and blocked claims\n\n"
        "Allowed observed statements:\n"
        f"{allowed}\n\n"
        "Blocked statements:\n"
        f"{blocked}\n\n"
        "Limits:\n"
        f"{limits}\n\n"
        "## Methodology audit\n\n"
        + "\n".join(audit_lines)
        + "\n\n## Next scientific gap\n\n"
        "The next scientific gap is project-clustered uncertainty accounting and the "
        "missing frozen overlap measurements, not another mutant, input, or rerun on "
        "this subject. This handoff does not start that task. "
        "`FORMAL_V2_RUN_RETRY_FORBIDDEN=true` remains in force.\n"
    )


def write_handoff(
    repo_root: str | Path,
    *,
    json_path: str | Path | None = None,
    markdown_path: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    body = build_handoff(root)
    record = {**body, "artifact_sha256": canonical_sha256(body)}
    json_out = Path(json_path) if json_path is not None else root / FORMAL_JSON_RELATIVE
    md_out = (
        Path(markdown_path) if markdown_path is not None else root / FORMAL_MD_RELATIVE
    )
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(json_out, record, exclusive=True)
    md_out.write_text(render_markdown(record), encoding="utf-8")
    return record


def main(argv: Sequence[str] | None = None) -> int:
    if argv:
        raise EvidenceError("E_HANDOFF_SELECTOR", "builder arguments are rejected")
    write_handoff(Path.cwd())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
