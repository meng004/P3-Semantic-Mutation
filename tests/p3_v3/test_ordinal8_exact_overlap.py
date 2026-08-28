from __future__ import annotations

import importlib.util
import hashlib
from pathlib import Path

import pytest

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    write_canonical_json,
)
from p3_v3.ordinal8_first_paired_evidence import apply_patch_text


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/p3_v3/measure_ordinal8_exact_overlap.py"
LEDGER = REPO_ROOT / "research/evidence/p3_claim_ledger_v1.3.0.yml"
FORMAL_JSON = (
    REPO_ROOT / "data/p3_v3/phase3/ordinal8-exact-overlap-v1/exact-overlap.json"
)


def _module():
    spec = importlib.util.spec_from_file_location(
        "measure_ordinal8_exact_overlap", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tiny_tree(root: Path, body: str = "value = False\n") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "target.py").write_text(body, encoding="utf-8")
    return root


def _patch(source: str, target: str, path: str = "target.py") -> dict[str, str]:
    original = "value = False\n"
    mutated = original.replace(source, target, 1)
    diff = f"--- a/{path}\n+++ b/{path}\n@@\n-{source}\n+{target}\n"
    return {
        "operator_id": "TINY_TF_DEMO_V1",
        "path": path,
        "source": source,
        "target": target,
        "unified_diff": diff,
        "patch_sha256": hashlib.sha256(diff.encode("utf-8")).hexdigest(),
        "span": "1:8-1:13",
    }


def test_four_pairs_are_unique_and_ordered():
    module = _module()
    pairs = module.discover_pairs(REPO_ROOT)
    assert [row["family_mechanism"] for row in pairs] == [
        "INV/TF",
        "INV/SI",
        "CMP/TF",
        "CMP/SI",
    ]
    slot_ids = [row["slot_id"] for row in pairs]
    site_ids = [row["site_id"] for row in pairs]
    contract_ids = [row["contract_id"] for row in pairs]
    patch_shas = [
        row["semantic_patch"]["patch_sha256"] for row in pairs
    ] + [row["syntactic_patch"]["patch_sha256"] for row in pairs]
    assert len(set(slot_ids)) == 4
    assert len(set(contract_ids)) == 4
    assert len(set(site_ids)) == 2
    assert len(set(patch_shas)) == 8
    for row in pairs:
        assert row["semantic_patch"]["patch_sha256"] != row["syntactic_patch"][
            "patch_sha256"
        ]
        assert row["semantic_patch"]["path"]
        assert row["syntactic_patch"]["path"]


def test_patch_sha_mismatch_fails_closed(tmp_path):
    module = _module()
    patch = _patch("False", "True")
    path = tmp_path / "mutant.patch"
    path.write_text("not-the-recorded-diff\n", encoding="utf-8")
    with pytest.raises(EvidenceError, match="PATCH_IDENTITY|patch SHA"):
        module.verify_patch_file(path, patch["patch_sha256"])


def test_original_tree_mismatch_fails_closed(tmp_path):
    module = _module()
    tree = _tiny_tree(tmp_path / "original")
    with pytest.raises(EvidenceError, match="SOURCE|tree"):
        module.verify_original_tree(tree, expected_sha256="0" * 64)


def test_semantic_and_syntactic_use_isolated_original_copies(tmp_path):
    module = _module()
    original = _tiny_tree(tmp_path / "original")
    semantic = _patch("False", "True")
    syntactic = _patch("False", "None")
    left = tmp_path / "semantic"
    right = tmp_path / "syntactic"
    module.copy_original_tree(original, left)
    module.copy_original_tree(original, right)
    module.apply_frozen_patch_to_tree(left, semantic)
    module.apply_frozen_patch_to_tree(right, syntactic)
    assert (original / "target.py").read_text(encoding="utf-8") == "value = False\n"
    assert (left / "target.py").read_text(encoding="utf-8") == "value = True\n"
    assert (right / "target.py").read_text(encoding="utf-8") == "value = None\n"
    assert left.resolve() != right.resolve()


def test_patch_overlap_comes_from_canonical_patch_sha():
    module = _module()
    first = _patch("False", "True")
    second = _patch("False", "True")
    third = _patch("False", "None")
    assert first["patch_sha256"] == second["patch_sha256"]
    assert module.exact_overlap(first["patch_sha256"], second["patch_sha256"]) is True
    assert module.exact_overlap(first["patch_sha256"], third["patch_sha256"]) is False


def test_tree_overlap_comes_from_full_canonical_tree_sha(tmp_path):
    module = _module()
    left = _tiny_tree(tmp_path / "left", "alpha\n")
    right = _tiny_tree(tmp_path / "right", "alpha\n")
    other = _tiny_tree(tmp_path / "other", "beta\n")
    left_sha = module.tree_sha256(left)
    right_sha = module.tree_sha256(right)
    other_sha = module.tree_sha256(other)
    assert left_sha == right_sha
    assert module.exact_overlap(left_sha, right_sha) is True
    assert module.exact_overlap(left_sha, other_sha) is False


def test_fuzzy_or_partial_patch_application_is_rejected(tmp_path):
    module = _module()
    tree = _tiny_tree(tmp_path / "tree", "value = False\nvalue = False\n")
    patch = _patch("False", "True")
    with pytest.raises(EvidenceError, match="PATCH|not unique|span"):
        module.apply_frozen_patch_to_tree(tree, patch)
    missing = _tiny_tree(tmp_path / "missing", "value = 1\n")
    with pytest.raises(EvidenceError, match="PATCH|not unique|span"):
        apply_patch_text("value = 1\n", patch)


def test_json_self_hash_and_c3_remain_blocked(tmp_path):
    module = _module()
    original = _tiny_tree(tmp_path / "original")
    original_sha = module.tree_sha256(original)
    pairs = [
        {
            "family_mechanism": "INV/TF",
            "slot_id": "a" * 64,
            "site_id": "b" * 64,
            "contract_id": "c" * 64,
            "semantic_patch": _patch("False", "True"),
            "syntactic_patch": _patch("False", "None"),
            "source_record": "fixture",
        }
    ]
    runtime = tmp_path / "runtime"
    output = tmp_path / "exact-overlap.json"
    record = module.measure_pairs(
        pairs,
        original_tree=original,
        expected_original_sha256=original_sha,
        runtime_root=runtime,
        output_path=output,
        repo_root=REPO_ROOT,
        bind_formal_identities=False,
    )
    written = read_canonical_json(output)
    body = {key: value for key, value in written.items() if key != "artifact_sha256"}
    assert written["artifact_sha256"] == canonical_sha256(body)
    assert written["artifact_sha256"] == record["artifact_sha256"]
    assert written["claim_ceiling"]["claim_id"] == (
        "C3_SEMANTIC_CONSTRUCT_DISTINCTNESS"
    )
    assert written["claim_ceiling"]["claim_status"] == "blocked"
    assert written["claim_ceiling"]["upgrade_condition_satisfied"] is False
    assert (
        written["exact_binomial_interval_status"]
        == "UNMEASURED_INTERVAL_AUTHORITY_INCOMPLETE"
    )
    assert "status: blocked" in LEDGER.read_text(encoding="utf-8")
    assert isinstance(written["pairs"][0]["normalized_patch_exact_overlap"], bool)
    assert isinstance(written["pairs"][0]["mutant_tree_exact_overlap"], bool)


def test_script_does_not_call_subject_or_paired_runners():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "run_ordinal8" not in source
    assert "run_formal_once" not in source
    assert "run_clean_replay_once" not in source
    assert "qualify_ordinal8" not in source
    assert "import numpy" not in source
    if FORMAL_JSON.is_file():
        rec = read_canonical_json(FORMAL_JSON)
        body = {key: value for key, value in rec.items() if key != "artifact_sha256"}
        assert rec["artifact_sha256"] == canonical_sha256(body)
        assert rec["claim_ceiling"]["claim_status"] == "blocked"
    assert file_sha256(SCRIPT)
