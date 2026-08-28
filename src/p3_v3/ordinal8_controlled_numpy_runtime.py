"""Isolated NumPy runtime qualification. Not a paired-evidence retry."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    validate_exact_object,
    write_canonical_json,
)
from p3_v3.contract_authority import ORDINAL8_SUBJECT_ID
from p3_v3.ordinal8_first_paired_evidence import (
    CONTRACT_ID_PREFIX,
    CONTROLLED_SUBJECT_SOURCE_ID,
    FORMAL_OUTPUT_ROOT_RELATIVE as PRESERVED_OUTPUT_ROOT_RELATIVE,
    FORMAL_RUNTIME_ROOT as PRESERVED_RUNTIME_ROOT,
    FROZEN_INPUT_IDS,
    FROZEN_INVENTORY_ARTIFACT_SHA256,
    GENERATOR_ID,
    NEUTRAL_SNAPSHOT_ID,
    QUALIFIED_NAME,
    SEMANTIC_OPERATOR_ID,
    SITE_ID,
    SLOT_ID,
    SOURCE_FILE_SHA256,
    SOURCE_RELATIVE,
    SYNTACTIC_OPERATOR_ID,
)

FORBIDDEN_IMPORT_ROOTS = (
    "numpy",
    "profiling_runner",
    "p3_v3.profiling_runner",
)
TASK_ID = "P3_C3_ORDINAL8_CONTROLLED_NUMPY_RUNTIME_RECOVERY"
SCHEMA_VERSION = "p3-ordinal8-controlled-numpy-runtime-qualification-v1"
C3_STATUS = "blocked"
FORMAL_PAIRED_EVIDENCE_RETRY_FORBIDDEN = True
CLEAN_REPLAY_AUTHORIZED = False
PRESERVED_PAIRED_EVIDENCE_COMMIT = "2a698e74ab49a6a73b98d3de9f21478156600f09"
PRESERVED_ARTIFACT_SHA256 = (
    "3f317d80c163114d9b5f5ee8373cec044c8f90fb04934a7ae63f0625114aee8f"
)
PRESERVED_FILE_SHA256 = (
    "8e0de660deba8b4bc00d5994dd180bfefb7aca9673583dcdef426ba27673855f"
)
FORBIDDEN_CONSUMED_CLI = "scripts/p3_v3/run_ordinal8_first_paired_evidence.py"
FORMAL_RUNTIME_ROOT = Path("/tmp/p3-c3-ordinal8-controlled-numpy-runtime")
FORMAL_OUTPUT_ROOT_RELATIVE = "data/p3_v3/phase3/ordinal8-controlled-numpy-runtime"
BUILD_DESCRIPTOR = {"ecosystem": "meson", "language_family": "python"}
BUILD_DESCRIPTOR_SHA256 = (
    "c6efda5c841b1900a51b69dc3982168098752015351a7e7fa07f201e70f99836"
)
NORMALIZED_SOURCE_TREE_SHA256 = (
    "f8826c3b975f8699e136e0b6b4cd4c29bf0d7e9a3be04fe09b947eb8998e727b"
)
ADAPTER_ID = "MESON_TEST_V1"
EXPECTED_NUMPY_VERSION = "2.0.0.dev0"
VENDORED_MESON_URL = "https://github.com/numpy/meson.git"
VENDORED_MESON_COMMIT = "4e370ca8ab73c07f7b84abe8a4b937caace050a4"
NUMPY_IDENTITY_COMMIT = "61f97f07b73f64c0dce92cb8158739d6d92ceb82"
CONTRACT_ID = "449bc0e7eba8f2947047d72817b36ebd966aa4759bc0ae25a570907414c035ae"
SEMANTIC_PATCH_SHA256 = (
    "9f0bfbb4d14bb944bf13cfdb97e135590f71208b62eabeb8b3d78937f6cfcda6"
)
SYNTACTIC_PATCH_SHA256 = (
    "234be58e515729e102dbb255564960e3767e939301d37e30a72a9fc333867f82"
)
BUILD_TIMEOUT_SEC = 5400
PROBE_TIMEOUT_SEC = 120
_GIT_ENV_KEYS = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_PREFIX",
)
_SELECTOR_FLAGS = frozenset(
    {
        "--retry",
        "--resume",
        "--skip",
        "--mutant",
        "--slot",
        "--contract",
        "--input",
        "--inputs",
        "--count",
        "--runs",
        "--patch",
    }
)
_AMBIENT_MARKERS = (
    "/usr/local/lib",
    "/usr/lib/python",
    "dist-packages",
    "/workspace/.venv",
)
_PROBE_SCRIPT = """
import importlib
import json
import pathlib
import sys

def _try_import(name):
    try:
        module = importlib.import_module(name)
        path = getattr(module, "__file__", None)
        return {"error": None, "file": path, "importable": True}
    except Exception as exc:
        return {
            "error": f"{type(exc).__name__}: {exc}",
            "file": None,
            "importable": False,
        }

numpy_info = _try_import("numpy")
array_api_info = _try_import("numpy.array_api")
linalg_info = _try_import("numpy.array_api.linalg")
version = None
if numpy_info["importable"]:
    version = importlib.import_module("numpy").__version__
linalg_path = None
if array_api_info["importable"] and array_api_info["file"]:
    candidate = pathlib.Path(array_api_info["file"]).resolve().parent / "linalg.py"
    if candidate.is_file():
        linalg_path = str(candidate)
print(json.dumps({
    "array_api": array_api_info,
    "executable": sys.executable,
    "linalg": linalg_info,
    "linalg_path": linalg_path,
    "numpy": numpy_info,
    "prefix": sys.prefix,
    "version": version,
}, sort_keys=True, separators=(",", ":")))
"""
_BUILD_RECEIPT_SCHEMA = {
    "allow_noblas": bool,
    "build_dir": str,
    "command": list,
    "meson_executable": str,
    "prefix": str,
    "returncode": int,
    "source_copy": str,
    "status": str,
    "vendored_meson_commit": (str, type(None)),
    "vendored_meson_present": bool,
    "vendored_meson_recovered": bool,
    "venv_python": str,
}
_PROBE_SCHEMA = {
    "array_api": dict,
    "executable": str,
    "linalg": dict,
    "linalg_path": (str, type(None)),
    "numpy": dict,
    "prefix": str,
    "version": (str, type(None)),
}


def extracted_source_root(repo_root: str | Path) -> Path:
    return (
        Path(repo_root)
        / "data/p3_v3/p12_intake/extracted"
        / NEUTRAL_SNAPSHOT_ID
    )


def descriptor_path(repo_root: str | Path) -> Path:
    return (
        Path(repo_root)
        / "data/p3_v3/p12_intake/descriptors"
        / f"{NEUTRAL_SNAPSHOT_ID}.json"
    )


def preserved_output_path(repo_root: str | Path) -> Path:
    return (
        Path(repo_root)
        / PRESERVED_OUTPUT_ROOT_RELATIVE
        / "paired-evidence.json"
    )


def unchanged_selection() -> dict[str, Any]:
    return {
        "contract_id": CONTRACT_ID,
        "generator_id": GENERATOR_ID,
        "input_ids": list(FROZEN_INPUT_IDS),
        "inventory_artifact_sha256": FROZEN_INVENTORY_ARTIFACT_SHA256,
        "qualified_name": QUALIFIED_NAME,
        "semantic_operator_id": SEMANTIC_OPERATOR_ID,
        "semantic_patch_sha256": SEMANTIC_PATCH_SHA256,
        "site_id": SITE_ID,
        "slot_id": SLOT_ID,
        "source_relative": SOURCE_RELATIVE,
        "syntactic_operator_id": SYNTACTIC_OPERATOR_ID,
        "syntactic_patch_sha256": SYNTACTIC_PATCH_SHA256,
    }


def sanitize_build_env(base: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if base is None else base)
    for key in _GIT_ENV_KEYS:
        env.pop(key, None)
    env["GIT_DIR"] = os.devnull
    return env


def isolated_build_env(venv_dir: str | Path) -> dict[str, str]:
    env = sanitize_build_env()
    prefix = Path(venv_dir)
    bindir = prefix / "bin"
    meson = bindir / "meson"
    ninja = bindir / "ninja"
    cython = bindir / "cython"
    env["MESON"] = str(meson)
    env["NINJA"] = str(ninja)
    env["CYTHON"] = str(cython)
    env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
    return env


def vendored_meson_path(source_root: str | Path) -> Path:
    return Path(source_root) / "vendored-meson" / "meson" / "meson.py"


def recover_vendored_meson(
    source_copy: str | Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    dest = Path(source_copy) / "vendored-meson" / "meson"
    meson_py = dest / "meson.py"
    if meson_py.is_file():
        return {
            "commit": None,
            "destination": str(dest),
            "present": True,
            "recovered": False,
        }
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise EvidenceError("E_VENDORED_MESON", "incomplete vendored-meson directory")
    run = runner if runner is not None else subprocess.run
    clone = run(
        [
            "git",
            "clone",
            "--filter=blob:none",
            "--no-checkout",
            VENDORED_MESON_URL,
            str(dest),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if clone.returncode != 0:
        raise EvidenceError(
            "E_VENDORED_MESON",
            f"git clone of vendored meson failed: {clone.stderr or clone.stdout}",
        )
    fetch = run(
        [
            "git",
            "-C",
            str(dest),
            "fetch",
            "--depth",
            "1",
            "origin",
            VENDORED_MESON_COMMIT,
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if fetch.returncode != 0:
        raise EvidenceError(
            "E_VENDORED_MESON",
            f"git fetch of vendored meson failed: {fetch.stderr or fetch.stdout}",
        )
    checkout = run(
        [
            "git",
            "-C",
            str(dest),
            "checkout",
            "--detach",
            VENDORED_MESON_COMMIT,
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if checkout.returncode != 0 or not meson_py.is_file():
        raise EvidenceError(
            "E_VENDORED_MESON",
            "vendored meson checkout did not produce meson.py",
        )
    if not (dest / "mesonbuild" / "modules" / "features" / "__init__.py").is_file():
        raise EvidenceError("E_VENDORED_MESON", "features module is absent")
    return {
        "commit": VENDORED_MESON_COMMIT,
        "destination": str(dest),
        "present": True,
        "recovered": True,
    }


def _verify_preserved_commit(repo_root: Path) -> str:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "merge-base",
            "--is-ancestor",
            PRESERVED_PAIRED_EVIDENCE_COMMIT,
            "HEAD",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise EvidenceError(
            "E_PRESERVED_COMMIT",
            f"preserved commit {PRESERVED_PAIRED_EVIDENCE_COMMIT} is not an ancestor",
        )
    return PRESERVED_PAIRED_EVIDENCE_COMMIT


def _same_or_nested(left: Path, right: Path) -> bool:
    first = left.resolve()
    second = right.resolve()
    return first == second or first in second.parents or second in first.parents


def bind_frozen_identities(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    preserved_commit = _verify_preserved_commit(root)
    descriptor = read_canonical_json(descriptor_path(root))
    if descriptor != BUILD_DESCRIPTOR:
        raise EvidenceError("E_BUILD_DESCRIPTOR", "build descriptor object differs")
    if canonical_sha256(descriptor) != BUILD_DESCRIPTOR_SHA256:
        raise EvidenceError("E_BUILD_DESCRIPTOR", "build descriptor SHA-256 differs")
    source_root = extracted_source_root(root)
    if not source_root.is_dir() or source_root.is_symlink():
        raise EvidenceError("E_SOURCE_IDENTITY", "extracted source tree is absent")
    if not (source_root / "meson.build").is_file():
        raise EvidenceError("E_SOURCE_IDENTITY", "root meson.build is absent")
    linalg = source_root / SOURCE_RELATIVE
    if not linalg.is_file() or linalg.is_symlink():
        raise EvidenceError("E_SOURCE_IDENTITY", "SOURCE_IDENTITY_REQUIRED")
    if file_sha256(linalg) != SOURCE_FILE_SHA256:
        raise EvidenceError("E_SOURCE_IDENTITY", "source file SHA-256 differs")
    pyproject = (source_root / "pyproject.toml").read_text(encoding="utf-8")
    if 'name = "numpy"' not in pyproject or EXPECTED_NUMPY_VERSION not in pyproject:
        raise EvidenceError("E_SOURCE_IDENTITY", "pyproject identity differs")
    if "mesonpy" not in pyproject:
        raise EvidenceError("E_BUILD_DESCRIPTOR", "mesonpy backend is absent")
    gitmodules = (source_root / ".gitmodules").read_text(encoding="utf-8")
    if VENDORED_MESON_URL not in gitmodules:
        raise EvidenceError("E_VENDORED_MESON", "frozen .gitmodules URL differs")
    preserved = preserved_output_path(root)
    if not preserved.is_file():
        raise EvidenceError("E_PRESERVED_OUTPUT", "preserved paired-evidence.json is absent")
    if file_sha256(preserved) != PRESERVED_FILE_SHA256:
        raise EvidenceError("E_PRESERVED_OUTPUT", "preserved file SHA-256 differs")
    record = read_canonical_json(preserved)
    if not isinstance(record, Mapping):
        raise EvidenceError("E_PRESERVED_OUTPUT", "preserved record is not an object")
    if record.get("artifact_sha256") != PRESERVED_ARTIFACT_SHA256:
        raise EvidenceError("E_PRESERVED_OUTPUT", "preserved artifact SHA-256 differs")
    if record.get("slot_id") != SLOT_ID:
        raise EvidenceError("E_UNCHANGED_SELECTION", "slot_id changed")
    if record.get("site_id") != SITE_ID:
        raise EvidenceError("E_UNCHANGED_SELECTION", "site_id changed")
    if record.get("contract_id") != CONTRACT_ID:
        raise EvidenceError("E_UNCHANGED_SELECTION", "contract_id changed")
    if record.get("input_ids") != list(FROZEN_INPUT_IDS):
        raise EvidenceError("E_UNCHANGED_SELECTION", "input_ids changed")
    semantic = record.get("semantic_patch")
    syntactic = record.get("syntactic_patch")
    if not isinstance(semantic, Mapping) or not isinstance(syntactic, Mapping):
        raise EvidenceError("E_UNCHANGED_SELECTION", "patches are absent")
    if semantic.get("patch_sha256") != SEMANTIC_PATCH_SHA256:
        raise EvidenceError("E_UNCHANGED_SELECTION", "semantic patch changed")
    if syntactic.get("patch_sha256") != SYNTACTIC_PATCH_SHA256:
        raise EvidenceError("E_UNCHANGED_SELECTION", "syntactic patch changed")
    if semantic.get("operator_id") != SEMANTIC_OPERATOR_ID:
        raise EvidenceError("E_UNCHANGED_SELECTION", "semantic operator changed")
    if syntactic.get("operator_id") != SYNTACTIC_OPERATOR_ID:
        raise EvidenceError("E_UNCHANGED_SELECTION", "syntactic operator changed")
    if not CONTRACT_ID.startswith(CONTRACT_ID_PREFIX):
        raise EvidenceError("E_UNCHANGED_SELECTION", "contract_id prefix differs")
    if not PRESERVED_RUNTIME_ROOT.exists():
        raise EvidenceError("E_PRESERVED_RUNTIME", "preserved runtime root is absent")
    if record.get("controlled_subject_id") != ORDINAL8_SUBJECT_ID:
        raise EvidenceError("E_SOURCE_IDENTITY", "controlled_subject_id differs")
    return {
        "adapter_id": ADAPTER_ID,
        "build_descriptor": dict(BUILD_DESCRIPTOR),
        "build_descriptor_sha256": BUILD_DESCRIPTOR_SHA256,
        "c3_status": C3_STATUS,
        "controlled_subject_id": ORDINAL8_SUBJECT_ID,
        "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
        "extracted_source_root": str(source_root),
        "linalg_path": str(linalg),
        "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": NORMALIZED_SOURCE_TREE_SHA256,
        "preserved_artifact_sha256": PRESERVED_ARTIFACT_SHA256,
        "preserved_commit": preserved_commit,
        "preserved_file_sha256": PRESERVED_FILE_SHA256,
        "preserved_output": str(preserved),
        "preserved_runtime": str(PRESERVED_RUNTIME_ROOT),
        "source_file_sha256": SOURCE_FILE_SHA256,
        "unchanged_selection": unchanged_selection(),
    }


def prepare_qualification_roots(
    runtime_root: str | Path,
    output_root: str | Path,
    *,
    preserved_runtime: str | Path = PRESERVED_RUNTIME_ROOT,
    preserved_output: str | Path | None = None,
) -> None:
    runtime = Path(runtime_root)
    output = Path(output_root)
    staging = output.with_name(output.name + ".staging")
    preserved_out = (
        Path(preserved_output)
        if preserved_output is not None
        else Path(PRESERVED_OUTPUT_ROOT_RELATIVE)
    )
    if _same_or_nested(runtime, Path(preserved_runtime)):
        raise EvidenceError("E_PRESERVED_ROOT", "refusing to reuse preserved runtime")
    if _same_or_nested(output, preserved_out):
        raise EvidenceError("E_PRESERVED_ROOT", "refusing to reuse preserved output")
    if runtime.exists():
        raise EvidenceError("E_QUAL_OUTPUT", "runtime root already exists")
    if output.exists():
        raise EvidenceError("E_QUAL_OUTPUT", "output root already exists")
    if staging.exists():
        raise EvidenceError("E_QUAL_OUTPUT", "staging root already exists")
    runtime.mkdir(parents=True, exist_ok=False)


def _run_checked(
    command: Sequence[str],
    *,
    cwd: Path | None,
    env: Mapping[str, str],
    timeout: int,
    log_path: Path,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        check=False,
        cwd=None if cwd is None else str(cwd),
        env=dict(env),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "$ "
        + " ".join(command)
        + "\n"
        + (result.stdout or "")
        + (result.stderr or ""),
        encoding="utf-8",
    )
    return result


def build_isolated_runtime(
    identities: Mapping[str, Any],
    runtime_root: str | Path,
    *,
    builder: Callable[[Mapping[str, Any], Path], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    runtime = Path(runtime_root)
    if builder is not None:
        return dict(builder(identities, runtime))
    source_src = Path(identities["extracted_source_root"])
    source_copy = runtime / "source"
    build_dir = runtime / "meson-build"
    venv_dir = runtime / "venv"
    meson_exe = venv_dir / "bin" / "meson"
    vendored_in_snapshot = vendored_meson_path(source_src).is_file()
    if source_copy.exists():
        raise EvidenceError("E_RUNTIME_BUILD", "source copy already exists")
    shutil.copytree(source_src, source_copy, symlinks=False)
    copied_linalg = source_copy / SOURCE_RELATIVE
    if file_sha256(copied_linalg) != SOURCE_FILE_SHA256:
        raise EvidenceError("E_SOURCE_IDENTITY", "copied linalg.py SHA-256 differs")
    if file_sha256(source_src / SOURCE_RELATIVE) != SOURCE_FILE_SHA256:
        raise EvidenceError("E_SOURCE_IDENTITY", "extracted linalg.py SHA-256 differs")
    try:
        recovered = recover_vendored_meson(source_copy)
    except EvidenceError as exc:
        recovered = {
            "commit": None,
            "destination": str(source_copy / "vendored-meson" / "meson"),
            "error": str(exc),
            "present": False,
            "recovered": False,
        }
    vendored = bool(recovered["present"])
    meson_for_build = (
        str(vendored_meson_path(source_copy))
        if vendored
        else str(meson_exe)
    )
    env = sanitize_build_env()
    venv_python = venv_dir / "bin" / "python"

    def _receipt(command: list[str], returncode: int, status: str) -> dict[str, Any]:
        return {
            "allow_noblas": True,
            "build_dir": str(build_dir),
            "command": command,
            "meson_executable": meson_for_build,
            "prefix": str(venv_dir),
            "returncode": int(returncode),
            "source_copy": str(source_copy),
            "status": status,
            "vendored_meson_commit": recovered.get("commit"),
            "vendored_meson_present": vendored or vendored_in_snapshot,
            "vendored_meson_recovered": bool(recovered.get("recovered")),
            "venv_python": str(venv_python),
        }

    if not recovered.get("present"):
        return _receipt(
            ["git", "clone", VENDORED_MESON_URL],
            1,
            "FAIL_INFRASTRUCTURE",
        )

    create = _run_checked(
        [sys.executable, "-m", "venv", str(venv_dir)],
        cwd=runtime,
        env=env,
        timeout=120,
        log_path=runtime / "venv-create.log",
    )
    if create.returncode != 0 or not venv_python.is_file():
        return _receipt(
            [sys.executable, "-m", "venv", str(venv_dir)],
            create.returncode,
            "FAIL_INFRASTRUCTURE",
        )
    bootstrap = [
        str(venv_python),
        "-m",
        "pip",
        "install",
        "-U",
        "pip",
        "meson-python>=0.15.0",
        "meson>=1.2.99",
        "Cython>=3.0.6",
        "ninja",
    ]
    deps = _run_checked(
        bootstrap,
        cwd=runtime,
        env=env,
        timeout=600,
        log_path=runtime / "pip-build-deps.log",
    )
    if deps.returncode != 0:
        return _receipt(bootstrap, deps.returncode, "FAIL_INFRASTRUCTURE")
    if not meson_exe.is_file():
        return _receipt(bootstrap, 1, "FAIL_INFRASTRUCTURE")
    install_env = isolated_build_env(venv_dir)
    if vendored_meson_path(source_copy).is_file():
        install_env.pop("MESON", None)
    install = [
        str(venv_python),
        "-m",
        "pip",
        "install",
        "--no-deps",
        "--no-build-isolation",
        "--config-settings=build-dir=" + str(build_dir),
        "--config-settings=setup-args=-Dallow-noblas=true",
        str(source_copy),
    ]
    built = _run_checked(
        install,
        cwd=runtime,
        env=install_env,
        timeout=BUILD_TIMEOUT_SEC,
        log_path=runtime / "pip-install-numpy.log",
    )
    return _receipt(
        install,
        built.returncode,
        "PASS" if built.returncode == 0 else "FAIL_INFRASTRUCTURE",
    )


def probe_interpreter(
    executable: str | Path,
    *,
    timeout: int = PROBE_TIMEOUT_SEC,
) -> dict[str, Any]:
    result = subprocess.run(
        [str(executable), "-I", "-c", _PROBE_SCRIPT],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=sanitize_build_env(),
    )
    if result.returncode != 0:
        raise EvidenceError(
            "E_RUNTIME_PROBE",
            f"probe failed: {result.stderr or result.stdout or result.returncode}",
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise EvidenceError("E_RUNTIME_PROBE", "probe output is not JSON") from exc
    return validate_exact_object(payload, _PROBE_SCHEMA, "probe")


def interpret_qualification(
    *,
    identities: Mapping[str, Any],
    runtime_root: str | Path,
    build: Mapping[str, Any],
    controlled: Mapping[str, Any],
    ambient: Mapping[str, Any],
) -> dict[str, Any]:
    runtime = Path(runtime_root).resolve()
    failures: list[str] = []
    if build.get("status") != "PASS":
        failures.append("isolated Meson/PEP 517 build did not succeed")
    controlled_file = None
    array_api_file = None
    if not controlled.get("numpy", {}).get("importable"):
        failures.append("controlled numpy import failed")
    else:
        controlled_file = controlled["numpy"].get("file")
        if not isinstance(controlled_file, str):
            failures.append("controlled numpy.__file__ is absent")
        else:
            resolved = str(Path(controlled_file).resolve())
            if not resolved.startswith(str(runtime) + os.sep):
                failures.append("controlled numpy is outside the isolated runtime")
            if any(marker in resolved for marker in _AMBIENT_MARKERS):
                failures.append("controlled numpy resolved to an ambient path")
    if controlled.get("version") != EXPECTED_NUMPY_VERSION:
        failures.append(
            f"controlled numpy version is {controlled.get('version')!r}"
        )
    if not controlled.get("array_api", {}).get("importable"):
        failures.append("controlled numpy.array_api import failed")
    else:
        array_api_file = controlled["array_api"].get("file")
        if not isinstance(array_api_file, str):
            failures.append("controlled numpy.array_api.__file__ is absent")
        else:
            resolved = str(Path(array_api_file).resolve())
            if not resolved.startswith(str(runtime) + os.sep):
                failures.append("controlled array_api is outside the isolated runtime")
            if any(marker in resolved for marker in _AMBIENT_MARKERS):
                failures.append("controlled array_api resolved to an ambient path")
    linalg_sha = None
    linalg_path = controlled.get("linalg_path")
    if not isinstance(linalg_path, str):
        failures.append("controlled linalg.py path is absent")
    else:
        linalg = Path(linalg_path)
        if not linalg.is_file():
            failures.append("controlled linalg.py is unreadable")
        else:
            linalg_sha = file_sha256(linalg)
            if linalg_sha != SOURCE_FILE_SHA256:
                failures.append("controlled linalg.py SHA-256 differs")
            if not str(linalg.resolve()).startswith(str(runtime) + os.sep):
                failures.append("controlled linalg.py is outside the isolated runtime")
    if ambient.get("array_api", {}).get("importable"):
        failures.append("ambient numpy.array_api unexpectedly importable")
    if ambient.get("version") == EXPECTED_NUMPY_VERSION:
        failures.append("ambient version unexpectedly matches the frozen tree")
    status = "PASS" if not failures else "FAIL_INFRASTRUCTURE"
    return {
        "ambient": {
            "array_api_file": ambient.get("array_api", {}).get("file"),
            "array_api_importable": bool(
                ambient.get("array_api", {}).get("importable")
            ),
            "executable": ambient.get("executable"),
            "numpy_file": ambient.get("numpy", {}).get("file"),
            "numpy_importable": bool(ambient.get("numpy", {}).get("importable")),
            "version": ambient.get("version"),
        },
        "array_api_origin": (
            "controlled_build" if status == "PASS" else "unqualified"
        ),
        "controlled": {
            "array_api_file": array_api_file,
            "array_api_importable": bool(
                controlled.get("array_api", {}).get("importable")
            ),
            "executable": controlled.get("executable"),
            "linalg_path": linalg_path,
            "linalg_sha256": linalg_sha,
            "numpy_file": controlled_file,
            "numpy_importable": bool(controlled.get("numpy", {}).get("importable")),
            "prefix": controlled.get("prefix"),
            "version": controlled.get("version"),
        },
        "failure_codes": failures,
        "identities": dict(identities),
        "qualification_kind": "IMPORT_PATH_VERSION",
        "qualification_status": status,
    }


def write_qualification_record(
    *,
    identities: Mapping[str, Any],
    runtime_root: str | Path,
    output_root: str | Path,
    build: Mapping[str, Any],
    qualification: Mapping[str, Any],
) -> dict[str, Any]:
    validate_exact_object(dict(build), _BUILD_RECEIPT_SCHEMA, "build")
    output = Path(output_root)
    staging = output.with_name(output.name + ".staging")
    body = {
        "adapter_id": ADAPTER_ID,
        "build": dict(build),
        "build_descriptor": dict(BUILD_DESCRIPTOR),
        "build_descriptor_sha256": BUILD_DESCRIPTOR_SHA256,
        "c3_status": C3_STATUS,
        "clean_replay_authorized": CLEAN_REPLAY_AUTHORIZED,
        "controlled_subject_id": identities["controlled_subject_id"],
        "controlled_subject_source_id": identities["controlled_subject_source_id"],
        "formal_paired_evidence_retry_forbidden": (
            FORMAL_PAIRED_EVIDENCE_RETRY_FORBIDDEN
        ),
        "forbidden_consumed_cli": FORBIDDEN_CONSUMED_CLI,
        "kill_survival": "UNOBSERVED",
        "neutral_snapshot_id": identities["neutral_snapshot_id"],
        "normalized_source_tree_sha256": NORMALIZED_SOURCE_TREE_SHA256,
        "not_original_runner_retry": True,
        "not_paired_evidence": True,
        "output_root": str(output),
        "paired_evidence_admissible": False,
        "preserved_artifact_sha256": PRESERVED_ARTIFACT_SHA256,
        "preserved_commit": PRESERVED_PAIRED_EVIDENCE_COMMIT,
        "preserved_file_sha256": PRESERVED_FILE_SHA256,
        "qualification": dict(qualification),
        "runtime_root": str(Path(runtime_root)),
        "schema_version": SCHEMA_VERSION,
        "scientific_class": "RUNTIME_QUALIFICATION",
        "scientific_result": None,
        "task_id": TASK_ID,
        "unchanged_selection": dict(identities["unchanged_selection"]),
    }
    record = {**body, "artifact_sha256": canonical_sha256(body)}
    staging.mkdir(parents=True, exist_ok=False)
    write_canonical_json(staging / "qualification.json", record, exclusive=True)
    os.replace(staging, output)
    return record


def run_qualification_once(
    repo_root: str | Path | None = None,
    *,
    runtime_root: str | Path | None = None,
    output_root: str | Path | None = None,
    builder: Callable[[Mapping[str, Any], Path], Mapping[str, Any]] | None = None,
    controlled_probe: Callable[[str], Mapping[str, Any]] | None = None,
    ambient_probe: Callable[[str], Mapping[str, Any]] | None = None,
    ambient_executable: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    identities = bind_frozen_identities(root)
    runtime = Path(runtime_root) if runtime_root is not None else FORMAL_RUNTIME_ROOT
    output = (
        Path(output_root)
        if output_root is not None
        else root / FORMAL_OUTPUT_ROOT_RELATIVE
    )
    prepare_qualification_roots(
        runtime,
        output,
        preserved_runtime=PRESERVED_RUNTIME_ROOT,
        preserved_output=root / PRESERVED_OUTPUT_ROOT_RELATIVE,
    )
    build = build_isolated_runtime(identities, runtime, builder=builder)
    probe = controlled_probe if controlled_probe is not None else probe_interpreter
    ambient_fn = ambient_probe if ambient_probe is not None else probe_interpreter
    ambient_exe = (
        str(ambient_executable) if ambient_executable is not None else sys.executable
    )
    if build.get("status") == "PASS":
        try:
            controlled = dict(probe(str(build["venv_python"])))
        except (EvidenceError, OSError, subprocess.SubprocessError) as exc:
            controlled = {
                "array_api": {
                    "error": str(exc),
                    "file": None,
                    "importable": False,
                },
                "executable": str(build["venv_python"]),
                "linalg": {"error": str(exc), "file": None, "importable": False},
                "linalg_path": None,
                "numpy": {"error": str(exc), "file": None, "importable": False},
                "prefix": str(build["prefix"]),
                "version": None,
            }
    else:
        controlled = {
            "array_api": {
                "error": "build did not succeed",
                "file": None,
                "importable": False,
            },
            "executable": str(build.get("venv_python")),
            "linalg": {
                "error": "build did not succeed",
                "file": None,
                "importable": False,
            },
            "linalg_path": None,
            "numpy": {
                "error": "build did not succeed",
                "file": None,
                "importable": False,
            },
            "prefix": str(build.get("prefix")),
            "version": None,
        }
    ambient = dict(ambient_fn(ambient_exe))
    qualification = interpret_qualification(
        identities=identities,
        runtime_root=runtime,
        build=build,
        controlled=controlled,
        ambient=ambient,
    )
    return write_qualification_record(
        identities=identities,
        runtime_root=runtime,
        output_root=output,
        build=build,
        qualification=qualification,
    )


def _reject_selectors(argv: Sequence[str]) -> None:
    if not argv:
        return
    flag = argv[0].split("=", 1)[0]
    if flag in _SELECTOR_FLAGS or flag.startswith("--"):
        raise EvidenceError("E_QUAL_SELECTOR", "selector arguments are rejected")
    raise EvidenceError("E_QUAL_SELECTOR", "arguments are rejected")


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    _reject_selectors(args)
    run_qualification_once()
    return 0
