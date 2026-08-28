from __future__ import annotations

import ast
import importlib.util
import os
from pathlib import Path
from shutil import copy2

import pytest

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
)
from p3_v3.ordinal8_controlled_numpy_runtime import (
    ADAPTER_ID,
    BUILD_DESCRIPTOR,
    BUILD_DESCRIPTOR_SHA256,
    C3_STATUS,
    CLEAN_REPLAY_AUTHORIZED,
    CONTRACT_ID,
    EXPECTED_NUMPY_VERSION,
    FORBIDDEN_CONSUMED_CLI,
    FORBIDDEN_IMPORT_ROOTS,
    FORMAL_OUTPUT_ROOT_RELATIVE,
    FORMAL_PAIRED_EVIDENCE_RETRY_FORBIDDEN,
    FORMAL_RUNTIME_ROOT,
    FROZEN_INPUT_IDS,
    PRESERVED_ARTIFACT_SHA256,
    PRESERVED_FILE_SHA256,
    PRESERVED_OUTPUT_ROOT_RELATIVE,
    PRESERVED_PAIRED_EVIDENCE_COMMIT,
    PRESERVED_RUNTIME_ROOT,
    SEMANTIC_OPERATOR_ID,
    SEMANTIC_PATCH_SHA256,
    SITE_ID,
    SLOT_ID,
    SOURCE_FILE_SHA256,
    SOURCE_RELATIVE,
    SYNTACTIC_OPERATOR_ID,
    SYNTACTIC_PATCH_SHA256,
    TASK_ID,
    VENDORED_MESON_COMMIT,
    VENDORED_MESON_URL,
    bind_frozen_identities,
    descriptor_path,
    extracted_source_root,
    isolated_build_env,
    interpret_qualification,
    main,
    prepare_qualification_roots,
    preserved_output_path,
    recover_vendored_meson,
    run_qualification_once,
    sanitize_build_env,
    unchanged_selection,
    vendored_meson_path,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "research/evidence/p3_claim_ledger_v1.3.0.yml"


def _cli():
    path = REPO_ROOT / "scripts/p3_v3/qualify_ordinal8_controlled_numpy_runtime.py"
    spec = importlib.util.spec_from_file_location(
        "qualify_ordinal8_controlled_numpy_runtime", path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _linalg_copy(directory: Path) -> Path:
    source = extracted_source_root(REPO_ROOT) / SOURCE_RELATIVE
    target = directory / "linalg.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    copy2(source, target)
    return target


def _probe(*, version, numpy_file, array_api_file, linalg_path, importable=True):
    return {
        "array_api": {
            "error": None if importable else "missing",
            "file": array_api_file,
            "importable": importable,
        },
        "executable": "/tmp/probe-python",
        "linalg": {
            "error": None if importable else "missing",
            "file": linalg_path,
            "importable": importable,
        },
        "linalg_path": linalg_path,
        "numpy": {
            "error": None,
            "file": numpy_file,
            "importable": True,
        },
        "prefix": "/tmp/prefix",
        "version": version,
    }


def test_preserves_paired_terminal_and_unchanged_selection():
    bound = bind_frozen_identities(REPO_ROOT)
    assert bound["preserved_commit"] == PRESERVED_PAIRED_EVIDENCE_COMMIT
    assert bound["preserved_artifact_sha256"] == PRESERVED_ARTIFACT_SHA256
    assert bound["preserved_file_sha256"] == PRESERVED_FILE_SHA256
    assert file_sha256(preserved_output_path(REPO_ROOT)) == PRESERVED_FILE_SHA256
    assert PRESERVED_RUNTIME_ROOT.exists()
    selection = bound["unchanged_selection"]
    assert selection["slot_id"] == SLOT_ID
    assert selection["site_id"] == SITE_ID
    assert selection["contract_id"] == CONTRACT_ID
    assert selection["input_ids"] == list(FROZEN_INPUT_IDS)
    assert selection["semantic_operator_id"] == SEMANTIC_OPERATOR_ID
    assert selection["syntactic_operator_id"] == SYNTACTIC_OPERATOR_ID
    assert selection["semantic_patch_sha256"] == SEMANTIC_PATCH_SHA256
    assert selection["syntactic_patch_sha256"] == SYNTACTIC_PATCH_SHA256
    assert selection == unchanged_selection()


def test_build_descriptor_and_source_identity():
    bound = bind_frozen_identities(REPO_ROOT)
    assert bound["build_descriptor"] == BUILD_DESCRIPTOR
    assert bound["build_descriptor_sha256"] == BUILD_DESCRIPTOR_SHA256
    assert canonical_sha256(read_canonical_json(descriptor_path(REPO_ROOT))) == (
        BUILD_DESCRIPTOR_SHA256
    )
    assert bound["adapter_id"] == ADAPTER_ID
    source = extracted_source_root(REPO_ROOT)
    assert (source / "meson.build").is_file()
    assert file_sha256(source / SOURCE_RELATIVE) == SOURCE_FILE_SHA256
    assert bound["source_file_sha256"] == SOURCE_FILE_SHA256


def test_new_roots_differ_from_preserved_roots():
    assert FORMAL_RUNTIME_ROOT != PRESERVED_RUNTIME_ROOT
    assert FORMAL_OUTPUT_ROOT_RELATIVE != PRESERVED_OUTPUT_ROOT_RELATIVE
    assert FORBIDDEN_CONSUMED_CLI.endswith(
        "run_ordinal8_first_paired_evidence.py"
    )
    assert FORMAL_PAIRED_EVIDENCE_RETRY_FORBIDDEN is True
    assert CLEAN_REPLAY_AUTHORIZED is False


def test_prepare_rejects_existing_and_preserved_paths(tmp_path):
    runtime = tmp_path / "runtime"
    output = tmp_path / "output"
    prepare_qualification_roots(
        runtime,
        output,
        preserved_runtime=PRESERVED_RUNTIME_ROOT,
        preserved_output=tmp_path / "preserved-output",
    )
    with pytest.raises(EvidenceError, match="already exists"):
        prepare_qualification_roots(
            runtime,
            tmp_path / "output-2",
            preserved_runtime=PRESERVED_RUNTIME_ROOT,
            preserved_output=tmp_path / "preserved-output",
        )
    with pytest.raises(EvidenceError, match="preserved runtime"):
        prepare_qualification_roots(
            PRESERVED_RUNTIME_ROOT,
            tmp_path / "output-3",
            preserved_runtime=PRESERVED_RUNTIME_ROOT,
            preserved_output=tmp_path / "preserved-output",
        )
    preserved_output = tmp_path / "preserved-output"
    preserved_output.mkdir()
    with pytest.raises(EvidenceError, match="preserved output"):
        prepare_qualification_roots(
            tmp_path / "runtime-4",
            preserved_output,
            preserved_runtime=PRESERVED_RUNTIME_ROOT,
            preserved_output=preserved_output,
        )


def test_cli_rejects_selectors_and_old_retry():
    with pytest.raises(EvidenceError, match="selector"):
        main(["--retry"])
    with pytest.raises(EvidenceError, match="selector"):
        main(["--resume"])
    with pytest.raises(EvidenceError, match="selector"):
        main(["--mutant", "semantic"])
    with pytest.raises(EvidenceError, match="selector"):
        main(["--slot", SLOT_ID])
    with pytest.raises(EvidenceError, match="selector|arguments"):
        main(["--contract", CONTRACT_ID])


def test_module_does_not_import_numpy_or_call_old_runner():
    module_path = REPO_ROOT / "src/p3_v3/ordinal8_controlled_numpy_runtime.py"
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    imported_names: set[str] = set()
    called: set[str] = set()
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
    for forbidden in FORBIDDEN_IMPORT_ROOTS:
        assert forbidden not in imported
    assert "numpy" not in imported
    assert "run_formal_once" not in imported_names
    assert "run_controlled_pair" not in imported_names
    assert "run_formal_once" not in called
    assert "run_controlled_pair" not in called
    assert "p3_claim_ledger" not in source


def test_interpret_accepts_controlled_array_api(tmp_path):
    runtime = tmp_path / "runtime"
    site = runtime / "venv/lib/python3.12/site-packages/numpy"
    linalg = _linalg_copy(site / "array_api")
    identities = bind_frozen_identities(REPO_ROOT)
    result = interpret_qualification(
        identities=identities,
        runtime_root=runtime,
        build={
            "allow_noblas": True,
            "build_dir": str(runtime / "meson-build"),
            "command": ["pip"],
            "meson_executable": str(runtime / "venv/bin/meson"),
            "prefix": str(runtime / "venv"),
            "returncode": 0,
            "source_copy": str(runtime / "source"),
            "status": "PASS",
            "vendored_meson_commit": None,
            "vendored_meson_present": False,
            "vendored_meson_recovered": False,
            "venv_python": str(runtime / "venv/bin/python"),
        },
        controlled=_probe(
            version=EXPECTED_NUMPY_VERSION,
            numpy_file=str(site / "__init__.py"),
            array_api_file=str(site / "array_api/__init__.py"),
            linalg_path=str(linalg),
        ),
        ambient=_probe(
            version="2.4.4",
            numpy_file="/usr/local/lib/python3.12/dist-packages/numpy/__init__.py",
            array_api_file=None,
            linalg_path=None,
            importable=False,
        ),
    )
    assert result["qualification_status"] == "PASS"
    assert result["array_api_origin"] == "controlled_build"
    assert result["controlled"]["linalg_sha256"] == SOURCE_FILE_SHA256
    assert result["controlled"]["version"] == EXPECTED_NUMPY_VERSION


def test_interpret_rejects_ambient_path_or_version(tmp_path):
    identities = bind_frozen_identities(REPO_ROOT)
    result = interpret_qualification(
        identities=identities,
        runtime_root=tmp_path / "runtime",
        build={
            "allow_noblas": True,
            "build_dir": "x",
            "command": ["pip"],
            "meson_executable": "x/bin/meson",
            "prefix": "x",
            "returncode": 0,
            "source_copy": "x",
            "status": "PASS",
            "vendored_meson_commit": None,
            "vendored_meson_present": False,
            "vendored_meson_recovered": False,
            "venv_python": "x",
        },
        controlled=_probe(
            version="2.4.4",
            numpy_file="/usr/local/lib/python3.12/dist-packages/numpy/__init__.py",
            array_api_file="/usr/local/lib/python3.12/dist-packages/numpy/array_api/__init__.py",
            linalg_path="/usr/local/lib/python3.12/dist-packages/numpy/array_api/linalg.py",
        ),
        ambient=_probe(
            version="2.4.4",
            numpy_file="/usr/local/lib/python3.12/dist-packages/numpy/__init__.py",
            array_api_file=None,
            linalg_path=None,
            importable=False,
        ),
    )
    assert result["qualification_status"] == "FAIL_INFRASTRUCTURE"
    assert result["array_api_origin"] == "unqualified"
    assert result["failure_codes"]


def test_stubbed_qualification_is_not_paired_evidence(tmp_path):
    runtime = tmp_path / "runtime"
    created: dict[str, Path] = {}

    def builder(_identities, root: Path):
        assert root == runtime
        site = root / "venv/lib/python3.12/site-packages/numpy"
        created["linalg"] = _linalg_copy(site / "array_api")
        created["numpy"] = site / "__init__.py"
        created["array_api"] = site / "array_api/__init__.py"
        created["numpy"].write_text("", encoding="utf-8")
        created["array_api"].write_text("", encoding="utf-8")
        return {
            "allow_noblas": True,
            "build_dir": str(root / "meson-build"),
            "command": ["stub-build"],
            "meson_executable": str(root / "venv/bin/meson"),
            "prefix": str(root / "venv"),
            "returncode": 0,
            "source_copy": str(root / "source"),
            "status": "PASS",
            "vendored_meson_commit": VENDORED_MESON_COMMIT,
            "vendored_meson_present": True,
            "vendored_meson_recovered": True,
            "venv_python": str(root / "venv/bin/python"),
        }

    def controlled_probe(executable: str):
        assert executable.endswith("venv/bin/python")
        return _probe(
            version=EXPECTED_NUMPY_VERSION,
            numpy_file=str(created["numpy"]),
            array_api_file=str(created["array_api"]),
            linalg_path=str(created["linalg"]),
        )

    def ambient_probe(_executable: str):
        return _probe(
            version="2.4.4",
            numpy_file="/usr/local/lib/python3.12/dist-packages/numpy/__init__.py",
            array_api_file=None,
            linalg_path=None,
            importable=False,
        )

    record = run_qualification_once(
        REPO_ROOT,
        runtime_root=runtime,
        output_root=tmp_path / "output",
        builder=builder,
        controlled_probe=controlled_probe,
        ambient_probe=ambient_probe,
    )
    assert record["task_id"] == TASK_ID
    assert record["not_paired_evidence"] is True
    assert record["not_original_runner_retry"] is True
    assert record["paired_evidence_admissible"] is False
    assert record["scientific_result"] is None
    assert record["kill_survival"] == "UNOBSERVED"
    assert record["c3_status"] == C3_STATUS
    assert record["formal_paired_evidence_retry_forbidden"] is True
    assert record["clean_replay_authorized"] is False
    assert "per_input_terminals" not in record
    assert "per_mutant" not in record
    assert record["qualification"]["qualification_status"] == "PASS"
    written = read_canonical_json(tmp_path / "output" / "qualification.json")
    assert written["artifact_sha256"] == record["artifact_sha256"]
    assert file_sha256(preserved_output_path(REPO_ROOT)) == PRESERVED_FILE_SHA256


def test_formal_paths_and_c3_remain_blocked():
    cli = _cli()
    assert Path(cli.FORMAL_RUNTIME_ROOT) == FORMAL_RUNTIME_ROOT
    assert cli.FORMAL_OUTPUT_ROOT_RELATIVE == FORMAL_OUTPUT_ROOT_RELATIVE
    assert C3_STATUS == "blocked"
    assert LEDGER.is_file()
    text = LEDGER.read_text(encoding="utf-8")
    assert "claim_id: C3_SEMANTIC_CONSTRUCT_DISTINCTNESS" in text
    assert "status: blocked" in text


def test_sanitize_build_env_drops_git_identity():
    env = sanitize_build_env(
        {
            "PATH": "/bin",
            "GIT_DIR": "/tmp/p3-c3-applicability-authority/.git",
            "GIT_WORK_TREE": "/tmp/p3-c3-applicability-authority",
        }
    )
    assert env["PATH"] == "/bin"
    assert env["GIT_DIR"] == os.devnull
    assert "GIT_WORK_TREE" not in env


def test_isolated_meson_overrides_missing_vendored_meson():
    source = extracted_source_root(REPO_ROOT)
    assert not vendored_meson_path(source).is_file()
    gitmodules = (source / ".gitmodules").read_text(encoding="utf-8")
    assert VENDORED_MESON_URL in gitmodules
    env = isolated_build_env(Path("/tmp/isolated-prefix"))
    assert env["MESON"] == "/tmp/isolated-prefix/bin/meson"
    assert env["NINJA"] == "/tmp/isolated-prefix/bin/ninja"
    assert env["CYTHON"] == "/tmp/isolated-prefix/bin/cython"
    assert env["PATH"].startswith("/tmp/isolated-prefix/bin" + os.pathsep)
    assert env["GIT_DIR"] == os.devnull


def test_recover_vendored_meson_checkouts_frozen_pin(tmp_path):
    source_copy = tmp_path / "source"
    source_copy.mkdir()
    calls: list[list[str]] = []

    def runner(command, **_kwargs):
        calls.append(list(command))
        dest = source_copy / "vendored-meson" / "meson"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "meson.py").write_text("print('meson')\n", encoding="utf-8")
        features = dest / "mesonbuild" / "modules" / "features"
        features.mkdir(parents=True, exist_ok=True)
        (features / "__init__.py").write_text("", encoding="utf-8")
        completed = type("R", (), {})()
        completed.returncode = 0
        completed.stdout = ""
        completed.stderr = ""
        return completed

    recovered = recover_vendored_meson(source_copy, runner=runner)
    assert recovered["recovered"] is True
    assert recovered["commit"] == VENDORED_MESON_COMMIT
    assert any(VENDORED_MESON_COMMIT in command for command in calls)
    assert vendored_meson_path(source_copy).is_file()
