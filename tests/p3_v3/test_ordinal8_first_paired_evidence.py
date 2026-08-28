from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, file_sha256, read_canonical_json
from p3_v3.ordinal8_first_paired_evidence import (
    FORBIDDEN_IMPORT_ROOTS,
    FORMAL_OUTPUT_ROOT_RELATIVE,
    FORMAL_RUNTIME_ROOT,
    FROZEN_CONTRACTS_SHA256,
    FROZEN_EVIDENCE_COMMIT,
    FROZEN_INPUT_IDS,
    FROZEN_INVENTORY_ARTIFACT_SHA256,
    MONO_SLOT_IDS,
    SEMANTIC_NEW,
    SEMANTIC_OLD,
    SEMANTIC_OPERATOR_ID,
    SEMANTIC_SPAN,
    SITE_ID,
    SLOT_ID,
    SOURCE_RELATIVE,
    SYNTACTIC_NEW,
    SYNTACTIC_OLD,
    SYNTACTIC_OPERATOR_ID,
    SYNTACTIC_SPAN,
    apply_patch_text,
    bind_frozen_first_slot,
    certify_static_patches,
    first_order_baseline_token,
    generate_semantic_patch,
    generate_syntactic_patch,
    main,
    prepare_controlled_roots,
    run_controlled_pair,
    selected_inventory_path,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FREEZE_ROOT = REPO_ROOT / "data/p3_v3/phase2/ordinal8-partial-contract-freeze"
OTHER_INVENTORY_MARKERS = (
    "e8fd94d60c42ed7357d8e00ebc1135b55b44dbde4978f887ab54abe94b261c6c",
    "e0b42ce7f2c60d9b3d0feae5ce3280d1619ec78b75c22c3e41fc6c936c3485e6",
    "06556e4b744f26766ef8593fc4ae727103082944ae6b26c6179fc947c3a2f1f5",
)


def _cholesky_source() -> str:
    return ("\n" * 45) + (
        "def cholesky(x: Array, /, *, upper: bool = False) -> Array:\n"
        '    """\n'
        "    Array API compatible wrapper for :py:func:`np.linalg.cholesky <numpy.linalg.cholesky>`.\n"
        "\n"
        "    See its docstring for more information.\n"
        '    """\n'
        "    # Note: the restriction to floating-point dtypes only is different from\n"
        "    # np.linalg.cholesky.\n"
        "    if x.dtype not in _floating_dtypes:\n"
        "        raise TypeError('Only floating-point dtypes are allowed in cholesky')\n"
        "    L = np.linalg.cholesky(x._array)\n"
        "    if upper:\n"
        "        U = Array._new(L).mT\n"
        "        if U.dtype in [complex64, complex128]:\n"
        "            U = conj(U)\n"
        "        return U\n"
        "    return Array._new(L)\n"
    )


def _cli():
    path = REPO_ROOT / "scripts/p3_v3/run_ordinal8_first_paired_evidence.py"
    spec = importlib.util.spec_from_file_location(
        "run_ordinal8_first_paired_evidence", path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixed_selection_is_first_canonical_slot():
    bound = bind_frozen_first_slot(REPO_ROOT)
    assert bound["slot_id"] == SLOT_ID
    assert bound["slot_id"].startswith("a2f7a216")
    assert bound["site_id"] == SITE_ID
    assert bound["contract_id"].startswith("449bc0e7")
    assert bound["generator_id"] == "CONTRACT_ARRAY_DOMAIN_V1"
    assert bound["qualified_name"] == "numpy.array_api.linalg:cholesky"


def test_bind_reads_only_the_five_frozen_rows_of_the_selected_slot(monkeypatch):
    seen: list[str] = []
    real = read_canonical_json

    def wrapper(path):
        seen.append(Path(path).name)
        return real(path)

    monkeypatch.setattr(
        "p3_v3.ordinal8_first_paired_evidence.read_canonical_json", wrapper
    )
    bound = bind_frozen_first_slot(REPO_ROOT)
    assert bound["input_ids"] == list(FROZEN_INPUT_IDS)
    assert len(bound["input_ids"]) == 5
    assert selected_inventory_path(FREEZE_ROOT).name.endswith(f"{SLOT_ID}.json")
    assert any(name.startswith("evaluation-inputs-contract-a2f7a216") for name in seen)
    assert not any(marker in name for name in seen for marker in OTHER_INVENTORY_MARKERS)
    assert bound["inventory_artifact_sha256"] == FROZEN_INVENTORY_ARTIFACT_SHA256


def test_mono_slots_never_enter_selection_or_inventories():
    bound = bind_frozen_first_slot(REPO_ROOT)
    assert bound["slot_id"] not in MONO_SLOT_IDS
    contracts = read_canonical_json(FREEZE_ROOT / "contracts.json")
    assert MONO_SLOT_IDS.isdisjoint(contracts)
    with pytest.raises(EvidenceError, match="MONO"):
        bind_frozen_first_slot(REPO_ROOT, slot_id=next(iter(MONO_SLOT_IDS)))


def test_semantic_patch_is_exact_and_rebuildable():
    source = _cholesky_source()
    first = generate_semantic_patch(source)
    second = generate_semantic_patch(source)
    assert first == second
    assert first["operator_id"] == SEMANTIC_OPERATOR_ID
    assert first["path"] == SOURCE_RELATIVE
    assert first["span"] == SEMANTIC_SPAN
    assert first["source"] == SEMANTIC_OLD
    assert first["target"] == SEMANTIC_NEW
    rebuilt = apply_patch_text(source, first)
    assert SEMANTIC_NEW in rebuilt
    assert rebuilt.count(SEMANTIC_NEW) == 1
    assert "np.linalg.cholesky(x._array)" in rebuilt
    assert first["patch_sha256"] == second["patch_sha256"]
    assert len(first["patch_sha256"]) == 64


def test_syntactic_baseline_is_the_preregistered_first_order_edit():
    source = _cholesky_source()
    token = first_order_baseline_token(source)
    assert token == ("False", "True", SYNTACTIC_SPAN)
    patch = generate_syntactic_patch(source)
    assert patch["operator_id"] == SYNTACTIC_OPERATOR_ID
    assert patch["path"] == SOURCE_RELATIVE
    assert patch["span"] == SYNTACTIC_SPAN
    assert patch["source"] == SYNTACTIC_OLD
    assert patch["target"] == SYNTACTIC_NEW
    rebuilt = apply_patch_text(source, patch)
    assert SYNTACTIC_NEW in rebuilt
    assert rebuilt.count("= True") == 1
    assert rebuilt.count("= False") == 0
    assert patch["unified_diff"].count("\n-") == 1 or patch["unified_diff"].count(
        "\n-"
    ) >= 1
    hunk_changes = [
        line
        for line in patch["unified_diff"].splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    assert len(hunk_changes) == 2


def test_semantic_and_syntactic_patch_identities_differ():
    source = _cholesky_source()
    semantic = generate_semantic_patch(source)
    syntactic = generate_syntactic_patch(source)
    assert semantic["patch_sha256"] != syntactic["patch_sha256"]
    assert semantic["span"] != syntactic["span"]
    assert semantic["operator_id"] != syntactic["operator_id"]
    certified = certify_static_patches(
        bind_frozen_first_slot(REPO_ROOT), semantic, syntactic, source
    )
    assert certified["semantic"]["PATCH_SCOPE_PASS"] is True
    assert certified["syntactic"]["PATCH_SCOPE_PASS"] is True
    assert certified["uniqueness"] is True


def test_unique_syntactic_baseline_failure_is_retained():
    source = _cholesky_source().replace(SYNTACTIC_OLD, "def cholesky(x):\n", 1)
    with pytest.raises(EvidenceError, match="SYNTACTIC_BASELINE"):
        generate_syntactic_patch(source)


def test_outcome_and_import_firewall():
    module_path = (
        REPO_ROOT / "src/p3_v3/ordinal8_first_paired_evidence.py"
    )
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
            imported.add(node.module)
    for forbidden in FORBIDDEN_IMPORT_ROOTS:
        assert forbidden not in imported
    assert "numpy" not in imported
    assert "profiling_runner" not in imported


def test_frozen_commit_source_site_contract_and_input_identity():
    bound = bind_frozen_first_slot(REPO_ROOT)
    assert bound["evidence_commit"] == FROZEN_EVIDENCE_COMMIT
    assert file_sha256(FREEZE_ROOT / "contracts.json") == FROZEN_CONTRACTS_SHA256
    assert bound["contract_id"] == bound["contract"]["contract_id"]
    assert bound["contract"]["site_id"] == SITE_ID
    assert bound["input_ids"] == [
        "82261a722a9730fd1e03c3b138f24bc7ecac9de710de9fd9ac7ae38e04a3c2b2",
        "cbd30153ac94b040e5fee28d8c559db619ec4f7342c9fb2c2b881ed02a2d21b2",
        "3ae9ca4d6efa478cff35e7ffb5d5be8f6dd9dea8443c43018933a206fceae2f7",
        "499142be0698116e670bfbead9881e25ed54e3be9ff3e157c23b73e5c0d6d102",
        "a3faf1a42deb3e155b457d1d7278b0388672895dba880b89b3c653a8484182b7",
    ]
    assert bound["source_path"] == SOURCE_RELATIVE
    assert "frozen_input_aggregate_sha256" in bound


def test_prepare_roots_rejects_existing_runtime_output_or_staging(tmp_path):
    runtime = tmp_path / "runtime"
    output = tmp_path / "output"
    prepare_controlled_roots(runtime, output)
    runtime_two = tmp_path / "runtime-2"
    output_two = tmp_path / "output-2"
    output_two.mkdir()
    with pytest.raises(EvidenceError, match="output root already exists"):
        prepare_controlled_roots(runtime_two, output_two)
    runtime_three = tmp_path / "runtime-3"
    runtime_three.mkdir()
    with pytest.raises(EvidenceError, match="runtime root already exists"):
        prepare_controlled_roots(runtime_three, tmp_path / "output-3")
    staging = (tmp_path / "output-4").with_name("output-4.staging")
    staging.mkdir()
    with pytest.raises(EvidenceError, match="staging root already exists"):
        prepare_controlled_roots(tmp_path / "runtime-4", tmp_path / "output-4")


def test_cli_and_bind_reject_replacement_selectors():
    with pytest.raises(EvidenceError, match="selector"):
        main(["--slot", SLOT_ID])
    with pytest.raises(EvidenceError, match="selector"):
        main(["--mutant", "semantic"])
    with pytest.raises(EvidenceError, match="selector"):
        main(["--retry"])
    with pytest.raises(EvidenceError, match="selector"):
        main(["--resume"])
    with pytest.raises(EvidenceError, match="selector"):
        main(["--skip"])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--contract", "x"])
    with pytest.raises(EvidenceError, match="MONO|slot"):
        bind_frozen_first_slot(REPO_ROOT, slot_id=SLOT_ID[:-1] + "0")


def test_runner_records_stubbed_terminals_without_numpy(tmp_path):
    source = _cholesky_source()
    semantic = generate_semantic_patch(source)
    syntactic = generate_syntactic_patch(source)
    bound = bind_frozen_first_slot(REPO_ROOT)
    calls: list[tuple[str, str]] = []

    def executor(variant: str, input_id: str, payload: object) -> dict[str, object]:
        assert variant in {"original", "semantic", "syntactic"}
        assert input_id in FROZEN_INPUT_IDS
        calls.append((variant, input_id))
        return {
            "observation_class": "SYNTHETIC_INFRASTRUCTURE",
            "status": "STUB_NOT_EXECUTED",
            "scientific_result": None,
        }

    record = run_controlled_pair(
        selection=bound,
        source_text=source,
        semantic=semantic,
        syntactic=syntactic,
        runtime_root=tmp_path / "runtime",
        output_root=tmp_path / "output",
        executor=executor,
    )
    assert len(calls) == 15
    assert {variant for variant, _input_id in calls} == {
        "original",
        "semantic",
        "syntactic",
    }
    assert [input_id for _variant, input_id in calls[:5]] == list(FROZEN_INPUT_IDS)
    terminals = record["per_input_terminals"]
    assert set(terminals) == {"original", "semantic", "syntactic"}
    for variant in terminals:
        assert list(terminals[variant]) == list(FROZEN_INPUT_IDS)
        assert all(
            row["observation_class"] == "SYNTHETIC_INFRASTRUCTURE"
            and row["scientific_result"] is None
            for row in terminals[variant].values()
        )
    assert record["per_mutant"]["semantic"]["scientific_result"] is None
    assert record["per_mutant"]["syntactic"]["scientific_result"] is None
    assert (tmp_path / "output" / "paired-evidence.json").is_file()
    assert not (tmp_path / "output.staging").exists()


def test_formal_roots_are_frozen_and_cli_is_argument_free():
    cli = _cli()
    assert Path(cli.FORMAL_RUNTIME_ROOT) == FORMAL_RUNTIME_ROOT
    assert cli.FORMAL_OUTPUT_ROOT_RELATIVE == FORMAL_OUTPUT_ROOT_RELATIVE
    assert FORMAL_RUNTIME_ROOT == Path("/tmp/p3-c3-ordinal8-first-paired-evidence")
    assert (
        FORMAL_OUTPUT_ROOT_RELATIVE
        == "data/p3_v3/phase3/ordinal8-first-paired-evidence"
    )


def test_controlled_b_still_admits_mutant_content_classes():
    from p3_v3.packages import ALLOWED_CLASSES

    assert "SEMANTIC_MUTANT" in ALLOWED_CLASSES["CONTROLLED_B"]
    assert "SYNTACTIC_MUTANT" in ALLOWED_CLASSES["CONTROLLED_B"]
