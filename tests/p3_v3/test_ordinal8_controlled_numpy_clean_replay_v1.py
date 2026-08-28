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
from p3_v3.ordinal8_controlled_numpy_clean_replay_v1 import (
    CELL_TIMEOUT_SEC,
    CONTROLLED_IMPORT_NAMES,
    C3_STATUS,
    FORMAL_OUTPUT_ROOT_RELATIVE,
    FORMAL_RUNTIME_ROOT,
    FROZEN_INPUT_IDS,
    NUMPY_IDENTITY_COMMIT,
    PRIOR_ARTIFACT_SHA256,
    PRIOR_FAILURE_COMMIT,
    PRIOR_FILE_SHA256,
    QUALIFICATION_ARTIFACT_SHA256,
    QUALIFICATION_COMMIT,
    QUALIFICATION_FILE_SHA256,
    REPLAY_VERSION,
    SEMANTIC_PATCH_SHA256,
    SLOT_ID,
    SYNTACTIC_PATCH_SHA256,
    VARIANTS,
    bind_frozen_selection_preserving_prior,
    main,
    prepare_clean_replay_roots,
    qualification_record_path,
    reduce_scientific_result,
    run_clean_replay_once,
    run_isolated_cell,
    sanitize_replay_env,
    verify_controlled_import_closure,
    verify_prior_failure,
    verify_qualification_record,
    verify_unchanged_scientific_inputs,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "research/evidence/p3_claim_ledger_v1.3.0.yml"
MODULE_PATH = REPO_ROOT / "src/p3_v3/ordinal8_controlled_numpy_clean_replay_v1.py"
OLD_RUNNER = REPO_ROOT / "src/p3_v3/ordinal8_first_paired_evidence.py"
QUAL_RECORD = (
    REPO_ROOT
    / "data/p3_v3/phase3/ordinal8-controlled-numpy-runtime/qualification.json"
)
PRIOR_RECORD = (
    REPO_ROOT
    / "data/p3_v3/phase3/ordinal8-first-paired-evidence/paired-evidence.json"
)


def _cli():
    path = REPO_ROOT / "scripts/p3_v3/run_ordinal8_controlled_numpy_clean_replay_v1.py"
    spec = importlib.util.spec_from_file_location(
        "run_ordinal8_controlled_numpy_clean_replay_v1", path
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


def _stub_executor(calls: list[tuple[str, str]]):
    def executor(variant: str, input_id: str, payload: object) -> dict[str, object]:
        assert variant in VARIANTS
        assert input_id in FROZEN_INPUT_IDS
        assert payload is not None
        calls.append((variant, input_id))
        return {
            "observation_class": "STUB_NOT_EXECUTED",
            "status": "PASS",
            "verdict": "SURVIVE",
            "scientific_result": "SURVIVE",
            "failure_code": None,
            "controlled_numpy_version": "2.0.0.dev0",
            "controlled_numpy_file": (
                "/tmp/p3-c3-ordinal8-controlled-numpy-runtime/venv/"
                "lib/python3.12/site-packages/numpy/__init__.py"
            ),
        }

    return executor


def _stubbed_run(tmp_path: Path, **overrides):
    calls: list[tuple[str, str]] = []
    kwargs = {
        "repo_root": REPO_ROOT,
        "runtime_root": tmp_path / "runtime",
        "output_root": tmp_path / "output",
        "executor": _stub_executor(calls),
        "import_probe": _ok_probe,
    }
    kwargs.update(overrides)
    if "executor" in overrides:
        return run_clean_replay_once(**kwargs), calls
    record = run_clean_replay_once(**kwargs)
    return record, calls


def test_qualification_artifact_tamper_fails(tmp_path):
    record = read_canonical_json(QUAL_RECORD)
    record["artifact_sha256"] = "0" * 64
    target = tmp_path / "qualification.json"
    write_canonical_json(target, record, exclusive=True)
    with pytest.raises(EvidenceError, match="QUALIFICATION"):
        verify_qualification_record(target, repo_root=REPO_ROOT)


def test_qualification_commit_mismatch_fails():
    with pytest.raises(EvidenceError, match="QUALIFICATION|commit"):
        verify_qualification_record(
            QUAL_RECORD,
            repo_root=REPO_ROOT,
            expected_commit="0" * 40,
        )


def test_controlled_runtime_missing_fails(tmp_path):
    with pytest.raises(EvidenceError, match="CONTROLLED_RUNTIME|runtime"):
        run_clean_replay_once(
            REPO_ROOT,
            runtime_root=tmp_path / "runtime",
            output_root=tmp_path / "output",
            qualification_runtime=tmp_path / "missing-runtime",
            executor=_stub_executor([]),
            import_probe=_ok_probe,
        )


def test_controlled_import_path_escape_fails(tmp_path):
    def probe(_executable: str) -> dict[str, object]:
        payload = _ok_probe(_executable)
        modules = dict(payload["modules"])
        modules["numpy.array_api"] = {"file": "/tmp/escaped/array_api/__init__.py"}
        payload["modules"] = modules
        return payload

    with pytest.raises(EvidenceError, match="CONTROLLED_IMPORT|import"):
        _stubbed_run(tmp_path, import_probe=probe)


def test_ambient_numpy_is_rejected(tmp_path):
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


def test_old_failure_evidence_missing_or_changed_fails(tmp_path):
    with pytest.raises(EvidenceError, match="PRIOR|preserved|failure"):
        verify_prior_failure(tmp_path / "missing.json")
    mutated = read_canonical_json(PRIOR_RECORD)
    mutated["artifact_sha256"] = "1" * 64
    target = tmp_path / "paired-evidence.json"
    write_canonical_json(target, mutated, exclusive=True)
    with pytest.raises(EvidenceError, match="PRIOR|preserved|failure"):
        verify_prior_failure(target)


def test_slot_contract_input_or_patch_change_fails():
    selection = bind_frozen_selection_preserving_prior(REPO_ROOT)
    semantic = {"patch_sha256": SEMANTIC_PATCH_SHA256}
    syntactic = {"patch_sha256": SYNTACTIC_PATCH_SHA256}
    verify_unchanged_scientific_inputs(selection, semantic, syntactic)
    changed = dict(selection)
    changed["slot_id"] = "0" * 64
    with pytest.raises(EvidenceError, match="UNCHANGED|slot"):
        verify_unchanged_scientific_inputs(changed, semantic, syntactic)
    changed = dict(selection)
    changed["contract_id"] = "1" * 64
    with pytest.raises(EvidenceError, match="UNCHANGED|contract"):
        verify_unchanged_scientific_inputs(changed, semantic, syntactic)
    changed = dict(selection)
    changed["input_ids"] = list(reversed(selection["input_ids"]))
    with pytest.raises(EvidenceError, match="UNCHANGED|input"):
        verify_unchanged_scientific_inputs(changed, semantic, syntactic)
    with pytest.raises(EvidenceError, match="UNCHANGED|patch"):
        verify_unchanged_scientific_inputs(
            selection, {"patch_sha256": "2" * 64}, syntactic
        )


def test_original_runner_is_not_called(tmp_path, monkeypatch):
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
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
    assert "run_formal_once" not in imported_names
    assert "run_formal_once" not in called
    assert "run_controlled_pair" not in imported_names
    assert "run_controlled_pair" not in called

    def boom(*_args, **_kwargs):
        raise AssertionError("original runner was invoked")

    monkeypatch.setattr(
        "p3_v3.ordinal8_first_paired_evidence.main", boom
    )
    monkeypatch.setattr(
        "p3_v3.ordinal8_first_paired_evidence.run_formal_once", boom
    )
    monkeypatch.setattr(
        "p3_v3.ordinal8_first_paired_evidence.run_controlled_pair", boom
    )
    record, calls = _stubbed_run(tmp_path)
    assert len(calls) == 15
    assert record["not_original_runner_retry"] is True
    assert record["replay_version"] == REPLAY_VERSION


def test_schedule_is_exactly_three_by_five_in_frozen_order(tmp_path):
    record, calls = _stubbed_run(tmp_path)
    assert [variant for variant, _input_id in calls] == [
        variant for variant in VARIANTS for _ in FROZEN_INPUT_IDS
    ]
    assert [input_id for _variant, input_id in calls[:5]] == list(FROZEN_INPUT_IDS)
    assert [input_id for _variant, input_id in calls[5:10]] == list(FROZEN_INPUT_IDS)
    assert [input_id for _variant, input_id in calls[10:15]] == list(FROZEN_INPUT_IDS)
    assert len(calls) == 15
    terminals = record["per_input_terminals"]
    assert list(terminals) == list(VARIANTS)
    for variant in VARIANTS:
        assert list(terminals[variant]) == list(FROZEN_INPUT_IDS)


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
        source_text="def cholesky(x, /, *, upper=False):\n    return x\n",
        input_id=FROZEN_INPUT_IDS[0],
        payload={"matrix": [[1.0]]},
        variant="original",
        runner=runner,
    )
    assert captured["timeout"] == 60
    assert captured["command"][1] == "-I"
    assert "PYTHONPATH" not in captured["env"]
    assert captured["env"]["PYTHONNOUSERSITE"] == "1"
    assert observation["status"] == "PASS"


def test_scientific_result_reducer():
    survive = {
        input_id: {
            "status": "PASS",
            "verdict": "SURVIVE",
            "scientific_result": "SURVIVE",
        }
        for input_id in FROZEN_INPUT_IDS
    }
    assert reduce_scientific_result(survive) == "SURVIVE"
    killed = dict(survive)
    killed[FROZEN_INPUT_IDS[0]] = {
        "status": "PASS",
        "verdict": "KILL",
        "scientific_result": "KILL",
    }
    assert reduce_scientific_result(killed) == "KILL"
    timeout = dict(survive)
    timeout[FROZEN_INPUT_IDS[1]] = {
        "status": "TIMEOUT",
        "verdict": "TIMEOUT",
        "scientific_result": "TIMEOUT",
    }
    assert reduce_scientific_result(timeout) == "TIMEOUT"
    infra = dict(survive)
    infra[FROZEN_INPUT_IDS[2]] = {
        "status": "FAIL_INFRASTRUCTURE",
        "verdict": "UNOBSERVED",
        "scientific_result": None,
    }
    assert reduce_scientific_result(infra) == "UNOBSERVED"
    mixed = dict(survive)
    mixed[FROZEN_INPUT_IDS[3]] = {
        "status": "FAIL",
        "verdict": "FAIL",
        "scientific_result": "FAIL",
    }
    assert reduce_scientific_result(mixed) == "INCONCLUSIVE"


def test_existing_runtime_output_or_staging_is_rejected(tmp_path):
    prepare_clean_replay_roots(tmp_path / "runtime", tmp_path / "output")
    with pytest.raises(EvidenceError, match="already exists"):
        prepare_clean_replay_roots(tmp_path / "runtime", tmp_path / "output-2")
    (tmp_path / "output-3").mkdir()
    with pytest.raises(EvidenceError, match="already exists"):
        prepare_clean_replay_roots(tmp_path / "runtime-3", tmp_path / "output-3")
    (tmp_path / "output-4.staging").mkdir()
    with pytest.raises(EvidenceError, match="already exists"):
        prepare_clean_replay_roots(tmp_path / "runtime-4", tmp_path / "output-4")
    with pytest.raises(EvidenceError, match="already exists"):
        _stubbed_run(tmp_path, runtime_root=tmp_path / "runtime")


def test_cli_rejects_every_argument():
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--retry"])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--resume"])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--skip"])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--slot", SLOT_ID])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--mutant", "semantic"])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--input", FROZEN_INPUT_IDS[0]])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["unexpected"])


def test_atomic_write_and_record_bindings(tmp_path):
    record, _calls = _stubbed_run(tmp_path)
    output = tmp_path / "output" / "clean-replay.json"
    assert output.is_file()
    assert not (tmp_path / "output.staging").exists()
    written = read_canonical_json(output)
    body = {key: value for key, value in written.items() if key != "artifact_sha256"}
    assert written["artifact_sha256"] == canonical_sha256(body)
    assert written["artifact_sha256"] == record["artifact_sha256"]
    assert written["prior_failure_commit"] == PRIOR_FAILURE_COMMIT
    assert written["prior_failure_file_sha256"] == PRIOR_FILE_SHA256
    assert written["prior_failure_artifact_sha256"] == PRIOR_ARTIFACT_SHA256
    assert written["qualification_commit"] == QUALIFICATION_COMMIT
    assert written["qualification_file_sha256"] == QUALIFICATION_FILE_SHA256
    assert written["qualification_artifact_sha256"] == QUALIFICATION_ARTIFACT_SHA256
    assert written["clean_replay_runner_sha256"] == file_sha256(MODULE_PATH)
    assert written["replay_version"] == REPLAY_VERSION
    assert written["not_original_runner_retry"] is True
    assert written["c3_status"] == C3_STATUS
    assert written["slot_id"] == SLOT_ID
    assert written["semantic_patch_sha256"] == SEMANTIC_PATCH_SHA256
    assert written["syntactic_patch_sha256"] == SYNTACTIC_PATCH_SHA256
    assert written["input_ids"] == list(FROZEN_INPUT_IDS)
    identity = written["controlled_runtime"]["recovered_gitlink_identity"]
    assert identity["commit"] == NUMPY_IDENTITY_COMMIT
    assert {row["commit"] for row in identity["submodules"]} == {
        "4e370ca8ab73c07f7b84abe8a4b937caace050a4",
        "1b21e453f6b1ba6a6aca392b1d810d9d41576123",
        "978731d047eb07d7f1b61c9407e7a8f48a377ccc",
        "ba0900a4957b929390ab73827235557959234fea",
    }
    cell = written["per_input_terminals"]["original"][FROZEN_INPUT_IDS[0]]
    assert cell["variant"] == "original"
    assert cell["input_id"] == FROZEN_INPUT_IDS[0]
    assert "status" in cell
    assert "verdict" in cell
    assert "scientific_result" in cell
    assert "failure_code" in cell
    assert "controlled_numpy_version" in cell
    assert "controlled_numpy_file" in cell


def test_stub_executor_tests_do_not_import_numpy_or_run_cholesky():
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "numpy" not in imported
    calls = [
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    assert "exec" not in calls
    assert "eval" not in calls


def test_formal_roots_and_identity_constants():
    cli = _cli()
    assert Path(cli.FORMAL_RUNTIME_ROOT) == FORMAL_RUNTIME_ROOT
    assert cli.FORMAL_OUTPUT_ROOT_RELATIVE == FORMAL_OUTPUT_ROOT_RELATIVE
    assert FORMAL_RUNTIME_ROOT == Path(
        "/tmp/p3-c3-ordinal8-controlled-numpy-clean-replay-v1"
    )
    assert FORMAL_OUTPUT_ROOT_RELATIVE == (
        "data/p3_v3/phase3/ordinal8-first-paired-evidence-clean-replay-v1"
    )
    assert not FORMAL_RUNTIME_ROOT.exists()
    official_output = REPO_ROOT / FORMAL_OUTPUT_ROOT_RELATIVE
    assert not official_output.exists()
    assert not official_output.with_name(official_output.name + ".staging").exists()
    assert QUALIFICATION_COMMIT.startswith("256305eb")
    assert file_sha256(QUAL_RECORD) == QUALIFICATION_FILE_SHA256
    assert (
        read_canonical_json(QUAL_RECORD)["artifact_sha256"]
        == QUALIFICATION_ARTIFACT_SHA256
    )
    assert file_sha256(PRIOR_RECORD) == PRIOR_FILE_SHA256
    assert C3_STATUS == "blocked"
    assert LEDGER.is_file()
    assert "status: blocked" in LEDGER.read_text(encoding="utf-8")
    assert set(CONTROLLED_IMPORT_NAMES) == {
        "numpy",
        "numpy.array_api",
        "numpy.array_api._array_object",
        "numpy.array_api._dtypes",
        "numpy.array_api._elementwise_functions",
    }
    env = sanitize_replay_env({"PYTHONPATH": "/ambient", "PATH": "/bin"})
    assert "PYTHONPATH" not in env
    assert env["PYTHONNOUSERSITE"] == "1"
    assert qualification_record_path(REPO_ROOT) == QUAL_RECORD


def test_import_closure_helper_rejects_ambient_and_escape():
    runtime = Path("/tmp/p3-c3-ordinal8-controlled-numpy-runtime")
    ok = _ok_probe("unused")
    verify_controlled_import_closure(
        ok,
        runtime,
        ambient_numpy_file="/usr/local/lib/python3.12/dist-packages/numpy/__init__.py",
    )
    leaked = dict(ok)
    leaked["modules"] = dict(ok["modules"])
    leaked["modules"]["numpy"] = {
        "file": "/usr/local/lib/python3.12/dist-packages/numpy/__init__.py"
    }
    with pytest.raises(EvidenceError, match="AMBIENT|ambient"):
        verify_controlled_import_closure(
            leaked,
            runtime,
            ambient_numpy_file="/usr/local/lib/python3.12/dist-packages/numpy/__init__.py",
        )
    escaped = dict(ok)
    escaped["modules"] = dict(ok["modules"])
    escaped["modules"]["numpy.array_api._dtypes"] = {
        "file": "/tmp/other/_dtypes.py"
    }
    with pytest.raises(EvidenceError, match="CONTROLLED_IMPORT|import"):
        verify_controlled_import_closure(escaped, runtime)


def test_old_runner_file_is_untouched():
    assert file_sha256(OLD_RUNNER)
    text = OLD_RUNNER.read_text(encoding="utf-8")
    assert "def run_formal_once" in text
    assert "def main" in text
