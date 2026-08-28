from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

import pytest

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    write_canonical_json,
)
from p3_v3.ordinal8_remaining_three_paired_batch_v1 import (
    BATCH_VERSION,
    CELL_TIMEOUT_SEC,
    CMP_SI_INPUT_IDS,
    CMP_SI_SLOT_ID,
    CMP_TF_INPUT_IDS,
    CMP_TF_SLOT_ID,
    C3_STATUS,
    EXCLUDED_INV_TF_SEMANTIC_PATCH_SHA256,
    EXCLUDED_INV_TF_SYNTACTIC_PATCH_SHA256,
    FORMAL_OUTPUT_ROOT_RELATIVE,
    FORMAL_RUNTIME_ROOT,
    INV_SI_INPUT_IDS,
    INV_SI_SLOT_ID,
    INV_TF_SLOT_ID,
    MONO_SLOT_IDS,
    PREREGISTRATION_COMMIT,
    PREREGISTRATION_FILE_SHA256,
    PRIOR_INV_TF_ARTIFACT_SHA256,
    PRIOR_INV_TF_COMMIT,
    PRIOR_INV_TF_FILE_SHA256,
    QUALIFICATION_ARTIFACT_SHA256,
    QUALIFICATION_COMMIT,
    QUALIFICATION_FILE_SHA256,
    SLOT_ORDER,
    VARIANTS,
    apply_named_patch,
    bind_remaining_three_slots,
    certify_remaining_patches,
    generate_slot_patches,
    main,
    prepare_batch_roots,
    reduce_batch_mutant,
    run_isolated_cell,
    run_remaining_three_paired_batch_once,
    verify_prior_inv_tf_evidence,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "research/evidence/p3_claim_ledger_v1.3.0.yml"
MODULE_PATH = REPO_ROOT / "src/p3_v3/ordinal8_remaining_three_paired_batch_v1.py"
DESIGN_PATH = (
    REPO_ROOT
    / "docs/superpowers/specs/2026-08-28-p3-c3-ordinal8-remaining-three-paired-evidence-batch-design.md"
)
QUAL_RECORD = (
    REPO_ROOT
    / "data/p3_v3/phase3/ordinal8-controlled-numpy-runtime/qualification.json"
)
PRIOR_RECORD = (
    REPO_ROOT
    / "data/p3_v3/phase3/ordinal8-first-paired-evidence-clean-replay-v1/clean-replay.json"
)
FIRST_PAIRED_MODULE = REPO_ROOT / "src/p3_v3/ordinal8_first_paired_evidence.py"
CLEAN_REPLAY_MODULE = (
    REPO_ROOT / "src/p3_v3/ordinal8_controlled_numpy_clean_replay_v1.py"
)


def _cli():
    path = (
        REPO_ROOT / "scripts/p3_v3/run_ordinal8_remaining_three_paired_batch_v1.py"
    )
    spec = importlib.util.spec_from_file_location(
        "run_ordinal8_remaining_three_paired_batch_v1", path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ok_probe(_executable: str) -> dict[str, object]:
    record = read_canonical_json(QUAL_RECORD)
    controlled = record["qualification"]["controlled"]
    site = Path(controlled["numpy_file"]).parent
    return {
        "executable": controlled["executable"],
        "prefix": controlled["prefix"],
        "version": controlled["version"],
        "modules": {
            "numpy": {"file": controlled["numpy_file"]},
            "numpy.array_api": {"file": controlled["array_api_file"]},
            "numpy.array_api._array_object": {
                "file": str(site / "array_api/_array_object.py")
            },
            "numpy.array_api._dtypes": {"file": str(site / "array_api/_dtypes.py")},
            "numpy.array_api._elementwise_functions": {
                "file": str(site / "array_api/_elementwise_functions.py")
            },
        },
    }


def _stub_executor(calls: list[tuple[str, str, str]]):
    allowed = {
        INV_SI_SLOT_ID: set(INV_SI_INPUT_IDS),
        CMP_TF_SLOT_ID: set(CMP_TF_INPUT_IDS),
        CMP_SI_SLOT_ID: set(CMP_SI_INPUT_IDS),
    }

    def executor(
        slot_id: str, variant: str, input_id: str, payload: object
    ) -> dict[str, object]:
        assert slot_id in allowed
        assert variant in VARIANTS
        assert input_id in allowed[slot_id]
        assert payload is not None
        calls.append((slot_id, variant, input_id))
        return {
            "observation_class": "STUB_NOT_EXECUTED",
            "status": "STUB_NOT_EXECUTED",
            "verdict": "UNOBSERVED",
            "scientific_result": None,
            "failure_code": None,
            "controlled_numpy_version": "2.0.0.dev0",
            "controlled_numpy_file": (
                "/tmp/p3-c3-ordinal8-controlled-numpy-runtime/venv/"
                "lib/python3.12/site-packages/numpy/__init__.py"
            ),
        }

    return executor


def _stubbed_run(tmp_path: Path, **overrides):
    calls: list[tuple[str, str, str]] = []
    kwargs = {
        "repo_root": REPO_ROOT,
        "runtime_root": tmp_path / "runtime",
        "output_root": tmp_path / "output",
        "executor": _stub_executor(calls),
        "import_probe": _ok_probe,
    }
    kwargs.update(overrides)
    if "executor" in overrides:
        return run_remaining_three_paired_batch_once(**kwargs), calls
    record = run_remaining_three_paired_batch_once(**kwargs)
    return record, calls


def test_three_slots_fixed_order_and_complete():
    bound = bind_remaining_three_slots(REPO_ROOT)
    assert [row["slot_id"] for row in bound] == list(SLOT_ORDER)
    assert SLOT_ORDER == (INV_SI_SLOT_ID, CMP_TF_SLOT_ID, CMP_SI_SLOT_ID)
    assert bound[0]["family_mechanism"] == "INV/SI"
    assert bound[1]["family_mechanism"] == "CMP/TF"
    assert bound[2]["family_mechanism"] == "CMP/SI"
    assert bound[0]["contract_id"].startswith("bf302808")
    assert bound[1]["contract_id"].startswith("52e6e033")
    assert bound[2]["contract_id"].startswith("607a987a")
    assert bound[0]["qualified_name"] == "numpy.array_api.linalg:cholesky"
    assert bound[1]["qualified_name"] == "numpy.typing.tests.test_typing:get_test_cases"
    assert bound[2]["qualified_name"] == "numpy.typing.tests.test_typing:get_test_cases"


def test_fifteen_frozen_input_ids_exact():
    bound = bind_remaining_three_slots(REPO_ROOT)
    assert bound[0]["input_ids"] == list(INV_SI_INPUT_IDS)
    assert bound[1]["input_ids"] == list(CMP_TF_INPUT_IDS)
    assert bound[2]["input_ids"] == list(CMP_SI_INPUT_IDS)
    observed = [input_id for row in bound for input_id in row["input_ids"]]
    assert len(observed) == 15
    assert len(set(observed)) == 15
    assert set(INV_SI_INPUT_IDS).isdisjoint(CMP_TF_INPUT_IDS)
    assert set(INV_SI_INPUT_IDS).isdisjoint(CMP_SI_INPUT_IDS)
    assert set(CMP_TF_INPUT_IDS).isdisjoint(CMP_SI_INPUT_IDS)
    for row in bound:
        assert len(row["rows"]) == 5
        assert {item["status"] for item in row["rows"]} == {"CONTRACT_INPUT_GENERATED"}


def test_mono_and_inv_tf_never_enter():
    bound = bind_remaining_three_slots(REPO_ROOT)
    selected = {row["slot_id"] for row in bound}
    assert INV_TF_SLOT_ID not in selected
    assert selected.isdisjoint(MONO_SLOT_IDS)
    with pytest.raises(EvidenceError, match="MONO|slot"):
        bind_remaining_three_slots(REPO_ROOT, slot_id=next(iter(MONO_SLOT_IDS)))
    with pytest.raises(EvidenceError, match="slot|INV/TF|replacement"):
        bind_remaining_three_slots(REPO_ROOT, slot_id=INV_TF_SLOT_ID)


def test_six_patches_are_pairwise_distinct_and_exclude_inv_tf():
    bound = bind_remaining_three_slots(REPO_ROOT)
    patches = generate_slot_patches(REPO_ROOT, bound)
    identities = []
    for slot_id in SLOT_ORDER:
        pair = patches[slot_id]
        identities.append(
            (
                pair["semantic"]["patch_sha256"],
                pair["semantic"]["operator_id"],
                pair["semantic"]["path"],
                pair["semantic"]["source"],
                pair["semantic"]["target"],
            )
        )
        identities.append(
            (
                pair["syntactic"]["patch_sha256"],
                pair["syntactic"]["operator_id"],
                pair["syntactic"]["path"],
                pair["syntactic"]["source"],
                pair["syntactic"]["target"],
            )
        )
    assert len(identities) == 6
    assert len({row[0] for row in identities}) == 6
    assert len({row[1] for row in identities}) == 6
    assert {row[0] for row in identities}.isdisjoint(
        {
            EXCLUDED_INV_TF_SEMANTIC_PATCH_SHA256,
            EXCLUDED_INV_TF_SYNTACTIC_PATCH_SHA256,
        }
    )
    sources_targets = {(row[3], row[4]) for row in identities}
    assert len(sources_targets) == 6
    assert (
        "    return Array._new(2 * L)\n",
    ) not in {(row[4],) for row in identities}
    assert all("2 * L" not in row[4] for row in identities)


def test_tf_and_si_do_not_share_semantic_patches():
    bound = bind_remaining_three_slots(REPO_ROOT)
    patches = generate_slot_patches(REPO_ROOT, bound)
    inv_si = patches[INV_SI_SLOT_ID]["semantic"]
    cmp_tf = patches[CMP_TF_SLOT_ID]["semantic"]
    cmp_si = patches[CMP_SI_SLOT_ID]["semantic"]
    assert inv_si["operator_id"] == "INV_SI_TRANSPOSE_CHOLESKY_FACTOR_V1"
    assert cmp_tf["operator_id"] == "CMP_TF_EXTEND_ACCEPTED_SUFFIX_SET_V1"
    assert cmp_si["operator_id"] == "CMP_SI_INDEX_EXTENSION_FIELD_V1"
    assert inv_si["target"] == "    return Array._new(L.T)\n"
    assert "2 * L" not in inv_si["target"]
    assert cmp_tf["patch_sha256"] != cmp_si["patch_sha256"]
    assert cmp_tf["source"] != cmp_si["source"] or cmp_tf["target"] != cmp_si["target"]
    assert ".txt" in cmp_tf["target"]
    assert "short_fname" in cmp_si["target"]
    assert ".txt" not in cmp_si["target"]
    assert "short_fname" not in cmp_tf["target"]


def test_patch_path_span_source_target_fail_closed():
    bound = bind_remaining_three_slots(REPO_ROOT)
    patches = generate_slot_patches(REPO_ROOT, bound)
    certify_remaining_patches(bound, patches)
    semantic = dict(patches[INV_SI_SLOT_ID]["semantic"])
    semantic["source"] = "this source span is absent\n"
    broken = {
        slot_id: {
            "semantic": semantic if slot_id == INV_SI_SLOT_ID else pair["semantic"],
            "syntactic": pair["syntactic"],
        }
        for slot_id, pair in patches.items()
    }
    with pytest.raises(EvidenceError, match="PATCH|SPAN|source"):
        certify_remaining_patches(bound, broken)
    escaped = {
        slot_id: {
            "semantic": (
                {**pair["semantic"], "span": "1:0-1:1"}
                if slot_id == INV_SI_SLOT_ID
                else pair["semantic"]
            ),
            "syntactic": pair["syntactic"],
        }
        for slot_id, pair in patches.items()
    }
    with pytest.raises(EvidenceError, match="PATCH|SPAN|span"):
        certify_remaining_patches(bound, escaped)
    wrong_path = {
        slot_id: {
            "semantic": (
                {**pair["semantic"], "path": "numpy/wrong.py"}
                if slot_id == INV_SI_SLOT_ID
                else pair["semantic"]
            ),
            "syntactic": pair["syntactic"],
        }
        for slot_id, pair in patches.items()
    }
    with pytest.raises(EvidenceError, match="PATCH|path"):
        certify_remaining_patches(bound, wrong_path)
    with pytest.raises(EvidenceError, match="PATCH|source"):
        apply_named_patch("abc", {"source": "missing", "target": "x"})


def test_qualification_runtime_and_prior_evidence_identity(tmp_path):
    verify_prior_inv_tf_evidence(PRIOR_RECORD)
    record, _calls = _stubbed_run(tmp_path)
    assert record["qualification_commit"] == QUALIFICATION_COMMIT
    assert record["qualification_file_sha256"] == QUALIFICATION_FILE_SHA256
    assert record["qualification_artifact_sha256"] == QUALIFICATION_ARTIFACT_SHA256
    assert record["prior_inv_tf_commit"] == PRIOR_INV_TF_COMMIT
    assert record["prior_inv_tf_file_sha256"] == PRIOR_INV_TF_FILE_SHA256
    assert record["prior_inv_tf_artifact_sha256"] == PRIOR_INV_TF_ARTIFACT_SHA256
    assert record["prior_result_disclosed"] is True
    assert record["not_prior_runner_retry"] is True
    assert file_sha256(QUAL_RECORD) == QUALIFICATION_FILE_SHA256
    assert file_sha256(PRIOR_RECORD) == PRIOR_INV_TF_FILE_SHA256
    mutated = read_canonical_json(PRIOR_RECORD)
    mutated["artifact_sha256"] = "1" * 64
    target = tmp_path / "clean-replay.json"
    write_canonical_json(target, mutated, exclusive=True)
    with pytest.raises(EvidenceError, match="PRIOR|INV/TF|evidence"):
        verify_prior_inv_tf_evidence(target)
    with pytest.raises(EvidenceError, match="CONTROLLED_RUNTIME|runtime"):
        run_remaining_three_paired_batch_once(
            repo_root=REPO_ROOT,
            runtime_root=tmp_path / "runtime-missing",
            output_root=tmp_path / "output-missing",
            qualification_runtime=tmp_path / "absent-runtime",
            executor=_stub_executor([]),
            import_probe=_ok_probe,
        )


def test_ambient_numpy_import_leak_is_rejected(tmp_path):
    def probe(_executable: str) -> dict[str, object]:
        payload = _ok_probe(_executable)
        modules = dict(payload["modules"])
        modules["numpy"] = {
            "file": "/usr/local/lib/python3.12/dist-packages/numpy/__init__.py"
        }
        payload["modules"] = modules
        return payload

    with pytest.raises(EvidenceError, match="AMBIENT|ambient"):
        _stubbed_run(tmp_path, import_probe=probe)


def test_schedule_is_exactly_forty_five_cells_in_frozen_order(tmp_path):
    record, calls = _stubbed_run(tmp_path)
    expected = [
        (slot_id, variant, input_id)
        for slot_id, input_ids in (
            (INV_SI_SLOT_ID, INV_SI_INPUT_IDS),
            (CMP_TF_SLOT_ID, CMP_TF_INPUT_IDS),
            (CMP_SI_SLOT_ID, CMP_SI_INPUT_IDS),
        )
        for variant in VARIANTS
        for input_id in input_ids
    ]
    assert calls == expected
    assert len(calls) == 45
    assert record["cell_count"] == 45
    per_slot = record["per_slot"]
    assert list(per_slot) == list(SLOT_ORDER)
    for slot_id, input_ids in (
        (INV_SI_SLOT_ID, INV_SI_INPUT_IDS),
        (CMP_TF_SLOT_ID, CMP_TF_INPUT_IDS),
        (CMP_SI_SLOT_ID, CMP_SI_INPUT_IDS),
    ):
        terminals = per_slot[slot_id]["per_input_terminals"]
        assert list(terminals) == list(VARIANTS)
        for variant in VARIANTS:
            assert list(terminals[variant]) == list(input_ids)


def test_cell_timeout_is_sixty_seconds():
    assert CELL_TIMEOUT_SEC == 60
    captured: dict[str, object] = {}

    def runner(command, **kwargs):
        captured["command"] = list(command)
        captured["timeout"] = kwargs["timeout"]
        captured["env"] = dict(kwargs["env"])
        completed = type("R", (), {})()
        completed.returncode = 0
        completed.stdout = json.dumps(
            {
                "status": "PASS",
                "verdict": "SURVIVE",
                "scientific_result": "SURVIVE",
                "failure_code": None,
                "controlled_numpy_version": "2.0.0.dev0",
                "controlled_numpy_file": "/tmp/rt/numpy/__init__.py",
            }
        )
        completed.stderr = ""
        return completed

    observation = run_isolated_cell(
        interpreter="/tmp/rt/venv/bin/python",
        runtime_root="/tmp/rt",
        source_text="def get_test_cases(directory):\n    yield None\n",
        input_id=CMP_TF_INPUT_IDS[0],
        payload={"entries": ["a.py", "b.txt"]},
        variant="original",
        family_mechanism="CMP/TF",
        runner=runner,
    )
    assert captured["timeout"] == 60
    assert captured["command"][1] == "-I"
    assert "PYTHONPATH" not in captured["env"]
    assert captured["env"]["PYTHONNOUSERSITE"] == "1"
    assert observation["status"] == "PASS"


def test_per_mutant_reducer_is_independent():
    survive = {
        input_id: {
            "status": "PASS",
            "verdict": "SURVIVE",
            "scientific_result": "SURVIVE",
            "observation_class": "REAL_SCIENTIFIC",
        }
        for input_id in INV_SI_INPUT_IDS
    }
    assert reduce_batch_mutant(survive) == "SURVIVE"
    killed = dict(survive)
    killed[INV_SI_INPUT_IDS[0]] = {
        "status": "PASS",
        "verdict": "KILL",
        "scientific_result": "KILL",
        "observation_class": "REAL_SCIENTIFIC",
    }
    assert reduce_batch_mutant(killed) == "KILL"
    timeout = dict(survive)
    timeout[INV_SI_INPUT_IDS[1]] = {
        "status": "TIMEOUT",
        "verdict": "TIMEOUT",
        "scientific_result": "TIMEOUT",
        "observation_class": "REAL_SCIENTIFIC",
    }
    assert reduce_batch_mutant(timeout) == "TIMEOUT"
    infra = dict(survive)
    infra[INV_SI_INPUT_IDS[2]] = {
        "status": "FAIL_INFRASTRUCTURE",
        "verdict": "UNOBSERVED",
        "scientific_result": None,
        "observation_class": "REAL_SCIENTIFIC",
    }
    assert reduce_batch_mutant(infra) == "UNOBSERVED"
    stub = {
        input_id: {
            "status": "STUB_NOT_EXECUTED",
            "verdict": "UNOBSERVED",
            "scientific_result": None,
            "observation_class": "STUB_NOT_EXECUTED",
        }
        for input_id in INV_SI_INPUT_IDS
    }
    assert reduce_batch_mutant(stub) is None


def test_existing_runtime_output_or_staging_is_rejected(tmp_path):
    prepare_batch_roots(tmp_path / "runtime", tmp_path / "output")
    with pytest.raises(EvidenceError, match="already exists"):
        prepare_batch_roots(tmp_path / "runtime", tmp_path / "output-2")
    (tmp_path / "output-3").mkdir()
    with pytest.raises(EvidenceError, match="already exists"):
        prepare_batch_roots(tmp_path / "runtime-3", tmp_path / "output-3")
    (tmp_path / "output-4.staging").mkdir()
    with pytest.raises(EvidenceError, match="already exists"):
        prepare_batch_roots(tmp_path / "runtime-4", tmp_path / "output-4")
    with pytest.raises(EvidenceError, match="already exists"):
        _stubbed_run(tmp_path, runtime_root=tmp_path / "runtime")


def test_cli_rejects_every_selection_argument():
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--retry"])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--resume"])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--skip"])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--slot", INV_SI_SLOT_ID])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--mutant", "semantic"])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--input", INV_SI_INPUT_IDS[0]])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--order", "cmp"])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["unexpected"])


def test_atomic_write_and_record_bindings(tmp_path):
    record, _calls = _stubbed_run(tmp_path)
    output = tmp_path / "output" / "paired-batch.json"
    assert output.is_file()
    assert not (tmp_path / "output.staging").exists()
    written = read_canonical_json(output)
    body = {key: value for key, value in written.items() if key != "artifact_sha256"}
    assert written["artifact_sha256"] == canonical_sha256(body)
    assert written["artifact_sha256"] == record["artifact_sha256"]
    assert written["batch_version"] == BATCH_VERSION
    assert written["c3_status"] == C3_STATUS
    assert written["preregistration_commit"] == PREREGISTRATION_COMMIT
    assert written["preregistration_file_sha256"] == PREREGISTRATION_FILE_SHA256
    assert written["batch_runner_sha256"] == file_sha256(MODULE_PATH)
    assert len(written["implementation_commit"]) == 40
    assert written["prior_result_disclosed"] is True
    assert written["not_prior_runner_retry"] is True
    assert written["qualification_artifact_sha256"] == QUALIFICATION_ARTIFACT_SHA256
    assert written["prior_inv_tf_artifact_sha256"] == PRIOR_INV_TF_ARTIFACT_SHA256
    assert file_sha256(DESIGN_PATH) == PREREGISTRATION_FILE_SHA256
    assert len(written["patches"]) == 6
    assert len({row["patch_sha256"] for row in written["patches"]}) == 6
    cell = written["per_slot"][INV_SI_SLOT_ID]["per_input_terminals"]["original"][
        INV_SI_INPUT_IDS[0]
    ]
    for key in (
        "status",
        "verdict",
        "scientific_result",
        "failure_code",
        "controlled_numpy_version",
        "controlled_numpy_file",
        "variant",
        "input_id",
    ):
        assert key in cell


def test_stubbed_run_does_not_execute_subject_or_emit_scientific_evidence(tmp_path):
    record, calls = _stubbed_run(tmp_path)
    assert len(calls) == 45
    for slot in record["per_slot"].values():
        for variant_cells in slot["per_input_terminals"].values():
            for cell in variant_cells.values():
                assert cell["observation_class"] == "STUB_NOT_EXECUTED"
                assert cell["scientific_result"] is None
                assert cell["verdict"] != "KILL"
                assert cell["verdict"] != "SURVIVE"
        assert slot["per_mutant"]["semantic"]["scientific_result"] is None
        assert slot["per_mutant"]["syntactic"]["scientific_result"] is None
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    called: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            called.add(node.func.id)
    assert "numpy" not in imported
    assert "exec" not in called
    assert "eval" not in called


def test_module_does_not_call_prior_runners(tmp_path, monkeypatch):
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imported_names: set[str] = set()
    called: set[str] = set()
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
            imported.add(node.module)
            imported_names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            called.add(node.func.id)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            called.add(node.func.attr)
    assert "numpy" not in imported
    for name in (
        "run_formal_once",
        "run_controlled_pair",
        "run_clean_replay_once",
        "bind_frozen_first_slot",
    ):
        assert name not in imported_names
        assert name not in called

    def boom(*_args, **_kwargs):
        raise AssertionError("prior runner was invoked")

    monkeypatch.setattr("p3_v3.ordinal8_first_paired_evidence.main", boom)
    monkeypatch.setattr("p3_v3.ordinal8_first_paired_evidence.run_formal_once", boom)
    monkeypatch.setattr("p3_v3.ordinal8_first_paired_evidence.run_controlled_pair", boom)
    monkeypatch.setattr(
        "p3_v3.ordinal8_controlled_numpy_clean_replay_v1.main", boom
    )
    monkeypatch.setattr(
        "p3_v3.ordinal8_controlled_numpy_clean_replay_v1.run_clean_replay_once",
        boom,
    )
    record, calls = _stubbed_run(tmp_path)
    assert len(calls) == 45
    assert record["not_prior_runner_retry"] is True
    assert FIRST_PAIRED_MODULE.is_file()
    assert CLEAN_REPLAY_MODULE.is_file()


def test_formal_roots_remain_absent_and_c3_blocked():
    cli = _cli()
    assert Path(cli.FORMAL_RUNTIME_ROOT) == FORMAL_RUNTIME_ROOT
    assert cli.FORMAL_OUTPUT_ROOT_RELATIVE == FORMAL_OUTPUT_ROOT_RELATIVE
    assert FORMAL_RUNTIME_ROOT == Path(
        "/tmp/p3-c3-ordinal8-remaining-three-paired-batch-v1"
    )
    assert FORMAL_OUTPUT_ROOT_RELATIVE == (
        "data/p3_v3/phase3/ordinal8-remaining-three-paired-batch-v1"
    )
    assert not FORMAL_RUNTIME_ROOT.exists()
    official = REPO_ROOT / FORMAL_OUTPUT_ROOT_RELATIVE
    assert not official.exists()
    assert not official.with_name(official.name + ".staging").exists()
    assert C3_STATUS == "blocked"
    assert BATCH_VERSION == "ordinal8-remaining-three-paired-batch-v1"
    assert LEDGER.is_file()
    assert "status: blocked" in LEDGER.read_text(encoding="utf-8")
    assert PREREGISTRATION_COMMIT.startswith("0d567ab1")
