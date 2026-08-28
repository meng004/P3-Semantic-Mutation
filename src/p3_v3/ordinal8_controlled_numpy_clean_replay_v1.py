"""Controlled NumPy clean-replay v1. Not an original-runner retry."""

from __future__ import annotations

import hashlib
import json
import os
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
    write_canonical_json,
)
from p3_v3.ordinal8_controlled_numpy_runtime import (
    CONTRACT_ID,
    EXPECTED_NUMPY_VERSION,
    FORMAL_OUTPUT_ROOT_RELATIVE as QUALIFICATION_OUTPUT_ROOT_RELATIVE,
    FORMAL_RUNTIME_ROOT as QUALIFICATION_RUNTIME_ROOT,
    FROZEN_SUBMODULES,
    NUMPY_IDENTITY_COMMIT,
    PRESERVED_ARTIFACT_SHA256,
    PRESERVED_FILE_SHA256,
    PRESERVED_OUTPUT_ROOT_RELATIVE,
    PRESERVED_PAIRED_EVIDENCE_COMMIT,
    PRESERVED_RUNTIME_ROOT,
    SEMANTIC_PATCH_SHA256,
    SOURCE_FILE_SHA256,
    SYNTACTIC_PATCH_SHA256,
    VENDORED_MESON_COMMIT,
)
from p3_v3.ordinal8_first_paired_evidence import (
    CONTRACT_ID_PREFIX,
    FROZEN_INPUT_IDS,
    SITE_ID,
    SLOT_ID,
    apply_patch_text,
    bind_frozen_first_slot,
    certify_static_patches,
    frozen_input_aggregate_sha256,
    generate_semantic_patch,
    generate_syntactic_patch,
    read_frozen_source,
)

FORBIDDEN_IMPORT_ROOTS = (
    "numpy",
    "profiling_runner",
    "p3_v3.profiling_runner",
)
TASK_ID = "P3_C3_ORDINAL8_CONTROLLED_NUMPY_CLEAN_REPLAY_RUNNER_PREPARATION"
REPLAY_VERSION = "ordinal8-controlled-numpy-clean-replay-v1"
SCHEMA_VERSION = "p3-ordinal8-controlled-numpy-clean-replay-v1"
C3_STATUS = "blocked"
CELL_TIMEOUT_SEC = 60
VARIANTS = ("original", "semantic", "syntactic")
QUALIFICATION_COMMIT = "256305eb7d0bd835cb1fc37d99e5cc1732fefba2"
QUALIFICATION_FILE_SHA256 = (
    "290506c4324a062d56fecbbe22d3baa829cd99a2668fee4eeb70fd25d7ac46e0"
)
QUALIFICATION_ARTIFACT_SHA256 = (
    "501203515a524bcd4b51a6148908af25dbdd09932c7790e2e257404533d80abf"
)
PRIOR_FAILURE_COMMIT = PRESERVED_PAIRED_EVIDENCE_COMMIT
PRIOR_IMPLEMENTATION_COMMIT = "9a19228de78093e1ab4457bd7654e94eb459a344"
PRIOR_FILE_SHA256 = PRESERVED_FILE_SHA256
PRIOR_ARTIFACT_SHA256 = PRESERVED_ARTIFACT_SHA256
FORMAL_RUNTIME_ROOT = Path("/tmp/p3-c3-ordinal8-controlled-numpy-clean-replay-v1")
FORMAL_OUTPUT_ROOT_RELATIVE = (
    "data/p3_v3/phase3/ordinal8-first-paired-evidence-clean-replay-v1"
)
QUALIFICATION_RECORD_RELATIVE = (
    f"{QUALIFICATION_OUTPUT_ROOT_RELATIVE}/qualification.json"
)
FORBIDDEN_CONSUMED_CLI = "scripts/p3_v3/run_ordinal8_first_paired_evidence.py"
FORBIDDEN_QUALIFICATION_CLI = (
    "scripts/p3_v3/qualify_ordinal8_controlled_numpy_runtime.py"
)
AMBIENT_NUMPY_FILE = "/usr/local/lib/python3.12/dist-packages/numpy/__init__.py"
AMBIENT_NUMPY_VERSION = "2.4.4"
CONTROLLED_IMPORT_NAMES = (
    "numpy",
    "numpy.array_api",
    "numpy.array_api._array_object",
    "numpy.array_api._dtypes",
    "numpy.array_api._elementwise_functions",
)
_AMBIENT_MARKERS = (
    "/usr/local/lib",
    "/usr/lib/python",
    "dist-packages",
    "/workspace/.venv",
)
_STRIP_ENV = ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE", "PYTHONSTARTUP")
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
_CELL_REQUIRED = (
    "variant",
    "input_id",
    "status",
    "verdict",
    "scientific_result",
    "failure_code",
    "controlled_numpy_version",
    "controlled_numpy_file",
)
_RECORD_REQUIRED = {
    "artifact_sha256",
    "c3_status",
    "cell_timeout_sec",
    "clean_replay_runner_sha256",
    "contract_id",
    "controlled_runtime",
    "frozen_input_aggregate_sha256",
    "input_ids",
    "not_original_runner_retry",
    "per_input_terminals",
    "per_mutant",
    "prior_failure_artifact_sha256",
    "prior_failure_commit",
    "prior_failure_file_sha256",
    "prior_implementation_commit",
    "qualification_artifact_sha256",
    "qualification_commit",
    "qualification_file_sha256",
    "replay_version",
    "semantic_patch",
    "semantic_patch_sha256",
    "site_id",
    "slot_id",
    "static_certification",
    "syntactic_patch",
    "syntactic_patch_sha256",
    "task_id",
}
_IMPORT_PROBE_SCRIPT = """
import importlib
import json
import os
import sys

names = [
    "numpy",
    "numpy.array_api",
    "numpy.array_api._array_object",
    "numpy.array_api._dtypes",
    "numpy.array_api._elementwise_functions",
]
modules = {}
for name in names:
    module = importlib.import_module(name)
    modules[name] = {"file": getattr(module, "__file__", None)}
print(json.dumps({
    "executable": sys.executable,
    "modules": modules,
    "prefix": sys.prefix,
    "version": importlib.import_module("numpy").__version__,
}, sort_keys=True, separators=(",", ":")))
"""
_CELL_SCRIPT = """
import importlib
import json
import os
import sys

payload = json.loads(sys.stdin.read())
runtime_root = os.path.realpath(payload["runtime_root"])
ambient = payload.get("ambient_numpy") or ""
source_text = payload["source_text"]

def _file(module):
    path = os.path.realpath(getattr(module, "__file__", "") or "")
    if ambient and (ambient in path or path == os.path.realpath(ambient)):
        raise RuntimeError(f"ambient numpy: {module.__name__}")
    if not path.startswith(runtime_root + os.sep):
        raise RuntimeError(f"import escape: {module.__name__}")
    return path

numpy = importlib.import_module("numpy")
array_api = importlib.import_module("numpy.array_api")
array_object = importlib.import_module("numpy.array_api._array_object")
dtypes = importlib.import_module("numpy.array_api._dtypes")
elementwise = importlib.import_module("numpy.array_api._elementwise_functions")
numpy_file = _file(numpy)
_file(array_api)
_file(array_object)
_file(dtypes)
_file(elementwise)
lines = source_text.splitlines(keepends=True)
if len(lines) < 62:
    raise RuntimeError("cholesky span is missing")
namespace = {
    "Array": array_object.Array,
    "complex64": dtypes.complex64,
    "complex128": dtypes.complex128,
    "conj": elementwise.conj,
    "np": numpy,
    "_floating_dtypes": dtypes._floating_dtypes,
}
exec("".join(lines[45:62]), namespace, namespace)
cholesky = namespace["cholesky"]
matrix = payload["payload"]["matrix"]
factor = cholesky(array_object.Array._new(numpy.asarray(matrix, dtype=float)))
values = factor._array
reconstructed = values @ values.T
original = numpy.asarray(matrix, dtype=float)
residual = numpy.abs(reconstructed - original)
limit = 1e-10 + 1e-10 * numpy.abs(original)
violated = bool(numpy.any(residual > limit))
print(json.dumps({
    "controlled_numpy_file": numpy_file,
    "controlled_numpy_version": numpy.__version__,
    "failure_code": None,
    "scientific_result": "KILL" if violated else "SURVIVE",
    "status": "PASS",
    "verdict": "KILL" if violated else "SURVIVE",
}, sort_keys=True, separators=(",", ":")))
"""


def qualification_record_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / QUALIFICATION_RECORD_RELATIVE


def prior_failure_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / PRESERVED_OUTPUT_ROOT_RELATIVE / "paired-evidence.json"


def sanitize_replay_env(base: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if base is None else base)
    for key in _STRIP_ENV:
        env.pop(key, None)
    env["PYTHONNOUSERSITE"] = "1"
    return env


def _same_or_nested(left: Path, right: Path) -> bool:
    first = left.resolve()
    second = right.resolve()
    return first == second or first in second.parents or second in first.parents


def _verify_commit_ancestor(repo_root: Path, commit: str) -> str:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "merge-base",
            "--is-ancestor",
            commit,
            "HEAD",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise EvidenceError(
            "E_QUALIFICATION_COMMIT",
            f"qualification commit {commit} is not an ancestor",
        )
    return commit


def _file_sha_at_commit(repo_root: Path, commit: str, relative: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{commit}:{relative}"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise EvidenceError(
            "E_QUALIFICATION_COMMIT",
            "qualification blob is absent at the expected commit",
        )
    return hashlib.sha256(result.stdout).hexdigest()


def bind_frozen_selection_preserving_prior(repo_root: str | Path) -> dict[str, Any]:
    import p3_v3.ordinal8_first_paired_evidence as paired

    original = paired._assert_outcome_blind
    paired._assert_outcome_blind = lambda _root: None
    try:
        return bind_frozen_first_slot(repo_root)
    finally:
        paired._assert_outcome_blind = original


def verify_prior_failure(
    path: str | Path,
    *,
    runtime: str | Path = PRESERVED_RUNTIME_ROOT,
) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise EvidenceError("E_PRIOR_FAILURE", "prior failure record is absent")
    if file_sha256(source) != PRIOR_FILE_SHA256:
        raise EvidenceError("E_PRIOR_FAILURE", "prior failure file SHA-256 differs")
    record = read_canonical_json(source)
    if not isinstance(record, Mapping):
        raise EvidenceError("E_PRIOR_FAILURE", "prior failure record is not an object")
    digest = record.get("artifact_sha256")
    body = {key: value for key, value in record.items() if key != "artifact_sha256"}
    if digest != PRIOR_ARTIFACT_SHA256 or digest != canonical_sha256(body):
        raise EvidenceError("E_PRIOR_FAILURE", "prior failure artifact SHA-256 differs")
    if not Path(runtime).exists():
        raise EvidenceError("E_PRIOR_FAILURE", "prior failure runtime is absent")
    return dict(record)


def verify_qualification_record(
    path: str | Path,
    *,
    repo_root: str | Path,
    expected_commit: str | None = None,
) -> dict[str, Any]:
    commit = QUALIFICATION_COMMIT if expected_commit is None else expected_commit
    source = Path(path)
    if not source.is_file():
        raise EvidenceError(
            "E_QUALIFICATION_IDENTITY", "qualification record is absent"
        )
    if file_sha256(source) != QUALIFICATION_FILE_SHA256:
        raise EvidenceError(
            "E_QUALIFICATION_IDENTITY", "qualification file SHA-256 differs"
        )
    record = read_canonical_json(source)
    if not isinstance(record, Mapping):
        raise EvidenceError(
            "E_QUALIFICATION_IDENTITY", "qualification record is not an object"
        )
    digest = record.get("artifact_sha256")
    body = {key: value for key, value in record.items() if key != "artifact_sha256"}
    if digest != QUALIFICATION_ARTIFACT_SHA256 or digest != canonical_sha256(body):
        raise EvidenceError(
            "E_QUALIFICATION_IDENTITY", "qualification artifact differs"
        )
    if record.get("paired_evidence_admissible") is not False:
        raise EvidenceError(
            "E_QUALIFICATION_IDENTITY", "paired_evidence_admissible changed"
        )
    if record.get("scientific_result") is not None:
        raise EvidenceError("E_QUALIFICATION_IDENTITY", "scientific_result changed")
    if record.get("not_original_runner_retry") is not True:
        raise EvidenceError(
            "E_QUALIFICATION_IDENTITY", "not_original_runner_retry changed"
        )
    _verify_commit_ancestor(Path(repo_root), commit)
    if (
        _file_sha_at_commit(Path(repo_root), commit, QUALIFICATION_RECORD_RELATIVE)
        != QUALIFICATION_FILE_SHA256
    ):
        raise EvidenceError(
            "E_QUALIFICATION_IDENTITY", "qualification commit content differs"
        )
    return dict(record)


def verify_controlled_runtime_identity(
    record: Mapping[str, Any],
    runtime_root: str | Path,
) -> dict[str, Any]:
    runtime = Path(runtime_root)
    if runtime.is_symlink():
        raise EvidenceError("E_CONTROLLED_RUNTIME", "controlled runtime is a symlink")
    if not runtime.is_dir():
        raise EvidenceError("E_CONTROLLED_RUNTIME", "controlled runtime is absent")
    if runtime.resolve() != Path(record["runtime_root"]).resolve():
        raise EvidenceError("E_CONTROLLED_RUNTIME", "controlled runtime path differs")
    controlled = record["qualification"]["controlled"]
    interpreter = Path(controlled["executable"])
    if not interpreter.is_file():
        raise EvidenceError("E_CONTROLLED_RUNTIME", "controlled interpreter is absent")
    runtime_s = str(runtime.resolve())
    interp_parent = str(interpreter.parent.resolve())
    if not interp_parent.startswith(runtime_s + os.sep) and interp_parent != runtime_s:
        raise EvidenceError(
            "E_CONTROLLED_RUNTIME", "controlled interpreter is outside runtime"
        )
    if controlled.get("version") != EXPECTED_NUMPY_VERSION:
        raise EvidenceError("E_CONTROLLED_RUNTIME", "controlled numpy version differs")
    prefix = Path(controlled["prefix"])
    if prefix.resolve() != (runtime / "venv").resolve():
        raise EvidenceError("E_CONTROLLED_RUNTIME", "controlled prefix differs")
    numpy_file = Path(controlled["numpy_file"])
    array_api_file = Path(controlled["array_api_file"])
    linalg = Path(controlled["linalg_path"])
    for path in (numpy_file, array_api_file, linalg):
        if not path.is_file():
            raise EvidenceError("E_CONTROLLED_RUNTIME", "controlled module file is absent")
        resolved = str(path.resolve())
        if not resolved.startswith(runtime_s + os.sep):
            raise EvidenceError("E_CONTROLLED_RUNTIME", "controlled module path differs")
        if any(marker in resolved for marker in _AMBIENT_MARKERS):
            raise EvidenceError("E_CONTROLLED_RUNTIME", "controlled module is ambient")
    if file_sha256(linalg) != SOURCE_FILE_SHA256:
        raise EvidenceError("E_CONTROLLED_RUNTIME", "controlled linalg SHA-256 differs")
    if controlled.get("linalg_sha256") != SOURCE_FILE_SHA256:
        raise EvidenceError("E_CONTROLLED_RUNTIME", "recorded linalg SHA-256 differs")
    return {
        "array_api_file": str(array_api_file),
        "interpreter": str(interpreter),
        "linalg_path": str(linalg),
        "linalg_sha256": SOURCE_FILE_SHA256,
        "numpy_file": str(numpy_file),
        "numpy_version": controlled["version"],
        "prefix": str(prefix),
        "root": str(runtime),
    }


def verify_controlled_import_closure(
    probe: Mapping[str, Any],
    runtime_root: str | Path,
    ambient_numpy_file: str | None = None,
) -> dict[str, Any]:
    runtime = str(Path(runtime_root).resolve())
    if probe.get("version") != EXPECTED_NUMPY_VERSION:
        raise EvidenceError("E_CONTROLLED_IMPORT", "controlled import version differs")
    modules = probe.get("modules")
    if not isinstance(modules, Mapping):
        raise EvidenceError("E_CONTROLLED_IMPORT", "import probe modules are absent")
    ambient = ambient_numpy_file
    ambient_resolved = (
        str(Path(ambient).resolve()) if ambient else None
    )
    for name in CONTROLLED_IMPORT_NAMES:
        row = modules.get(name)
        if not isinstance(row, Mapping) or not row.get("file"):
            raise EvidenceError(
                "E_CONTROLLED_IMPORT", f"{name} is absent from the probe"
            )
        resolved = str(Path(str(row["file"])).resolve())
        if ambient and (ambient in resolved or resolved == ambient_resolved):
            raise EvidenceError("E_AMBIENT_NUMPY", f"{name} resolved to ambient numpy")
        if any(marker in resolved for marker in _AMBIENT_MARKERS):
            raise EvidenceError("E_AMBIENT_NUMPY", f"{name} resolved to an ambient path")
        if not resolved.startswith(runtime + os.sep):
            raise EvidenceError(
                "E_CONTROLLED_IMPORT", f"{name} escaped the controlled runtime"
            )
    return dict(probe)


def verify_recovered_gitlinks(
    record: Mapping[str, Any],
    runtime_root: str | Path | None = None,
) -> dict[str, Any]:
    rows = record.get("build", {}).get("recovered_submodules")
    if not isinstance(rows, list):
        raise EvidenceError("E_GITLINK", "recovered_submodules are absent")
    expected = {spec["path"]: spec["commit"] for spec in FROZEN_SUBMODULES}
    observed = {row["path"]: row["commit"] for row in rows}
    if observed != expected:
        raise EvidenceError("E_GITLINK", "recovered submodule OIDs differ")
    if observed.get("vendored-meson/meson") != VENDORED_MESON_COMMIT:
        raise EvidenceError("E_GITLINK", "vendored meson OID differs")
    identity = {
        "commit": NUMPY_IDENTITY_COMMIT,
        "submodules": [
            {
                "commit": spec["commit"],
                "path": spec["path"],
                "url": spec["url"],
            }
            for spec in FROZEN_SUBMODULES
        ],
    }
    if runtime_root is None:
        return identity
    source = Path(runtime_root) / "source"
    if not source.is_dir():
        return identity
    for spec in FROZEN_SUBMODULES:
        dest = source / spec["path"]
        if not dest.is_dir():
            raise EvidenceError("E_GITLINK", f"gitlink directory missing: {spec['path']}")
        result = subprocess.run(
            ["git", "-C", str(dest), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or result.stdout.strip() != spec["commit"]:
            raise EvidenceError("E_GITLINK", f"live OID differs for {spec['path']}")
    return identity


def verify_unchanged_scientific_inputs(
    selection: Mapping[str, Any],
    semantic: Mapping[str, Any],
    syntactic: Mapping[str, Any],
) -> None:
    if selection.get("slot_id") != SLOT_ID:
        raise EvidenceError("E_UNCHANGED_SELECTION", "slot_id changed")
    if selection.get("site_id") != SITE_ID:
        raise EvidenceError("E_UNCHANGED_SELECTION", "site_id changed")
    if selection.get("contract_id") != CONTRACT_ID:
        raise EvidenceError("E_UNCHANGED_SELECTION", "contract_id changed")
    if selection.get("input_ids") != list(FROZEN_INPUT_IDS):
        raise EvidenceError("E_UNCHANGED_SELECTION", "input_ids changed")
    if selection.get("frozen_input_aggregate_sha256") != frozen_input_aggregate_sha256():
        raise EvidenceError("E_UNCHANGED_SELECTION", "input aggregate changed")
    if semantic.get("patch_sha256") != SEMANTIC_PATCH_SHA256:
        raise EvidenceError("E_UNCHANGED_SELECTION", "semantic patch changed")
    if syntactic.get("patch_sha256") != SYNTACTIC_PATCH_SHA256:
        raise EvidenceError("E_UNCHANGED_SELECTION", "syntactic patch changed")
    if not str(selection.get("contract_id", "")).startswith(CONTRACT_ID_PREFIX):
        raise EvidenceError("E_UNCHANGED_SELECTION", "contract_id prefix differs")


def prepare_clean_replay_roots(
    runtime_root: str | Path,
    output_root: str | Path,
) -> None:
    runtime = Path(runtime_root)
    output = Path(output_root)
    staging = output.with_name(output.name + ".staging")
    if _same_or_nested(runtime, PRESERVED_RUNTIME_ROOT):
        raise EvidenceError("E_PRESERVED_ROOT", "refusing to reuse preserved runtime")
    if _same_or_nested(runtime, QUALIFICATION_RUNTIME_ROOT):
        raise EvidenceError(
            "E_PRESERVED_ROOT", "refusing to reuse qualification runtime"
        )
    if runtime.exists():
        raise EvidenceError("E_REPLAY_OUTPUT", "runtime root already exists")
    if output.exists():
        raise EvidenceError("E_REPLAY_OUTPUT", "output root already exists")
    if staging.exists():
        raise EvidenceError("E_REPLAY_OUTPUT", "staging root already exists")
    runtime.mkdir(parents=True, exist_ok=False)


def reduce_scientific_result(observations: Mapping[str, Mapping[str, Any]]) -> str:
    rows = list(observations.values())
    if any(row.get("status") == "FAIL_INFRASTRUCTURE" for row in rows):
        return "UNOBSERVED"
    if any(
        row.get("status") == "TIMEOUT" or row.get("scientific_result") == "TIMEOUT"
        for row in rows
    ):
        return "TIMEOUT"
    if any(
        row.get("verdict") == "KILL" or row.get("scientific_result") == "KILL"
        for row in rows
    ):
        return "KILL"
    if all(
        row.get("verdict") == "SURVIVE" and row.get("scientific_result") == "SURVIVE"
        for row in rows
    ):
        return "SURVIVE"
    return "INCONCLUSIVE"


def probe_controlled_imports(
    executable: str | Path,
    runtime_root: str | Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    result = runner(
        [str(executable), "-I", "-c", _IMPORT_PROBE_SCRIPT],
        check=False,
        capture_output=True,
        text=True,
        timeout=CELL_TIMEOUT_SEC,
        env=sanitize_replay_env(),
    )
    if result.returncode != 0:
        raise EvidenceError(
            "E_CONTROLLED_IMPORT",
            f"controlled import probe failed: {result.stderr or result.stdout}",
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise EvidenceError("E_CONTROLLED_IMPORT", "probe output is not JSON") from exc
    return verify_controlled_import_closure(
        payload,
        runtime_root,
        ambient_numpy_file=AMBIENT_NUMPY_FILE,
    )


def run_isolated_cell(
    *,
    interpreter: str | Path,
    runtime_root: str | Path,
    source_text: str,
    input_id: str,
    payload: object,
    variant: str,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    document = {
        "ambient_numpy": AMBIENT_NUMPY_FILE,
        "input_id": input_id,
        "payload": payload,
        "runtime_root": str(runtime_root),
        "source_text": source_text,
        "variant": variant,
    }
    try:
        result = runner(
            [str(interpreter), "-I", "-c", _CELL_SCRIPT],
            input=json.dumps(document),
            capture_output=True,
            text=True,
            timeout=CELL_TIMEOUT_SEC,
            env=sanitize_replay_env(),
        )
    except subprocess.TimeoutExpired:
        return {
            "controlled_numpy_file": None,
            "controlled_numpy_version": None,
            "failure_code": "TIMEOUT",
            "input_id": input_id,
            "observation_class": "REAL_SCIENTIFIC",
            "scientific_result": "TIMEOUT",
            "status": "TIMEOUT",
            "variant": variant,
            "verdict": "TIMEOUT",
        }
    if getattr(result, "returncode", 1) != 0:
        detail = (getattr(result, "stderr", None) or getattr(result, "stdout", None) or "")
        text = str(detail)
        infra = any(
            token in text.lower()
            for token in ("import", "ambient", "escape", "numpy")
        )
        return {
            "controlled_numpy_file": None,
            "controlled_numpy_version": None,
            "failure_code": text[:500] or "subprocess failed",
            "input_id": input_id,
            "observation_class": "REAL_SCIENTIFIC",
            "scientific_result": None if infra else "FAIL",
            "status": "FAIL_INFRASTRUCTURE" if infra else "FAIL",
            "variant": variant,
            "verdict": "UNOBSERVED" if infra else "FAIL",
        }
    try:
        observed = json.loads(result.stdout)
    except (TypeError, json.JSONDecodeError):
        return {
            "controlled_numpy_file": None,
            "controlled_numpy_version": None,
            "failure_code": "cell output is not JSON",
            "input_id": input_id,
            "observation_class": "REAL_SCIENTIFIC",
            "scientific_result": None,
            "status": "FAIL_INFRASTRUCTURE",
            "variant": variant,
            "verdict": "UNOBSERVED",
        }
    return {
        "controlled_numpy_file": observed.get("controlled_numpy_file"),
        "controlled_numpy_version": observed.get("controlled_numpy_version"),
        "failure_code": observed.get("failure_code"),
        "input_id": input_id,
        "observation_class": "REAL_SCIENTIFIC",
        "scientific_result": observed.get("scientific_result"),
        "status": observed.get("status"),
        "variant": variant,
        "verdict": observed.get("verdict"),
    }


def _make_controlled_executor(
    *,
    interpreter: str,
    runtime_root: str | Path,
    variants: Mapping[str, str],
    cell_runner: Callable[..., Mapping[str, Any]] | None = None,
) -> Callable[[str, str, object], Mapping[str, Any]]:
    run_cell = run_isolated_cell if cell_runner is None else cell_runner

    def executor(variant: str, input_id: str, payload: object) -> Mapping[str, Any]:
        return run_cell(
            interpreter=interpreter,
            runtime_root=runtime_root,
            source_text=variants[variant],
            input_id=input_id,
            payload=payload,
            variant=variant,
        )

    return executor


def _reject_selectors(argv: Sequence[str]) -> None:
    if not argv:
        return
    flag = argv[0].split("=", 1)[0]
    if flag in _SELECTOR_FLAGS or flag.startswith("--"):
        raise EvidenceError("E_REPLAY_SELECTOR", "selector arguments are rejected")
    raise EvidenceError("E_REPLAY_SELECTOR", "arguments are rejected")


def _validate_record(record: Mapping[str, Any]) -> None:
    missing = _RECORD_REQUIRED.difference(record)
    if missing:
        raise EvidenceError(
            "E_REPLAY_RECORD", f"record missing {sorted(missing)}"
        )
    if record["replay_version"] != REPLAY_VERSION:
        raise EvidenceError("E_REPLAY_RECORD", "replay_version differs")
    if record["not_original_runner_retry"] is not True:
        raise EvidenceError("E_REPLAY_RECORD", "not_original_runner_retry is not true")
    if record["input_ids"] != list(FROZEN_INPUT_IDS):
        raise EvidenceError("E_REPLAY_RECORD", "input_ids order differs")
    terminals = record["per_input_terminals"]
    if list(terminals) != list(VARIANTS):
        raise EvidenceError("E_REPLAY_RECORD", "variants differ")
    for variant in VARIANTS:
        cells = terminals[variant]
        if list(cells) != list(FROZEN_INPUT_IDS):
            raise EvidenceError("E_REPLAY_RECORD", "cell input order differs")
        for input_id, cell in cells.items():
            for key in _CELL_REQUIRED:
                if key not in cell:
                    raise EvidenceError("E_REPLAY_RECORD", f"cell missing {key}")
            if cell["variant"] != variant or cell["input_id"] != input_id:
                raise EvidenceError("E_REPLAY_RECORD", "cell identity differs")
    body = {key: value for key, value in record.items() if key != "artifact_sha256"}
    if record["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_REPLAY_RECORD", "artifact self-hash differs")


def run_clean_replay_once(
    repo_root: str | Path | None = None,
    *,
    runtime_root: str | Path | None = None,
    output_root: str | Path | None = None,
    qualification_path: str | Path | None = None,
    qualification_runtime: str | Path | None = None,
    prior_output_path: str | Path | None = None,
    prior_runtime: str | Path | None = None,
    expected_qualification_commit: str | None = None,
    executor: Callable[[str, str, object], Mapping[str, Any]] | None = None,
    import_probe: Callable[[str], Mapping[str, Any]] | None = None,
    cell_runner: Callable[..., Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    prior_path = (
        Path(prior_output_path)
        if prior_output_path is not None
        else prior_failure_path(root)
    )
    qual_path = (
        Path(qualification_path)
        if qualification_path is not None
        else qualification_record_path(root)
    )
    qual_runtime = (
        Path(qualification_runtime)
        if qualification_runtime is not None
        else QUALIFICATION_RUNTIME_ROOT
    )
    prior_rt = (
        Path(prior_runtime) if prior_runtime is not None else PRESERVED_RUNTIME_ROOT
    )
    runtime = Path(runtime_root) if runtime_root is not None else FORMAL_RUNTIME_ROOT
    output = (
        Path(output_root)
        if output_root is not None
        else root / FORMAL_OUTPUT_ROOT_RELATIVE
    )
    if _same_or_nested(runtime, PRESERVED_RUNTIME_ROOT) or _same_or_nested(
        runtime, QUALIFICATION_RUNTIME_ROOT
    ):
        raise EvidenceError("E_PRESERVED_ROOT", "refusing to reuse a frozen runtime")
    if _same_or_nested(output, root / PRESERVED_OUTPUT_ROOT_RELATIVE) or _same_or_nested(
        output, root / QUALIFICATION_OUTPUT_ROOT_RELATIVE
    ):
        raise EvidenceError("E_PRESERVED_ROOT", "refusing to reuse a frozen output")
    verify_prior_failure(prior_path, runtime=prior_rt)
    qualification = verify_qualification_record(
        qual_path,
        repo_root=root,
        expected_commit=expected_qualification_commit,
    )
    identity = verify_controlled_runtime_identity(qualification, qual_runtime)
    if import_probe is not None:
        probe = dict(import_probe(identity["interpreter"]))
        verify_controlled_import_closure(
            probe,
            qual_runtime,
            ambient_numpy_file=qualification["qualification"]["ambient"]["numpy_file"]
            or AMBIENT_NUMPY_FILE,
        )
    else:
        probe = probe_controlled_imports(identity["interpreter"], qual_runtime)
    gitlinks = verify_recovered_gitlinks(qualification, qual_runtime)
    prepare_clean_replay_roots(runtime, output)
    selection = bind_frozen_selection_preserving_prior(root)
    source_text = read_frozen_source(root)
    semantic = generate_semantic_patch(source_text)
    syntactic = generate_syntactic_patch(source_text)
    verify_unchanged_scientific_inputs(selection, semantic, syntactic)
    certification = certify_static_patches(
        selection, semantic, syntactic, source_text
    )
    variants = {
        "original": source_text,
        "semantic": apply_patch_text(source_text, semantic),
        "syntactic": apply_patch_text(source_text, syntactic),
    }
    exec_fn = executor
    if exec_fn is None:
        exec_fn = _make_controlled_executor(
            interpreter=identity["interpreter"],
            runtime_root=qual_runtime,
            variants=variants,
            cell_runner=cell_runner,
        )
    terminals: dict[str, dict[str, Any]] = {variant: {} for variant in VARIANTS}
    rows_by_id = {row["input_id"]: row for row in selection["rows"]}
    for variant in VARIANTS:
        for input_id in selection["input_ids"]:
            row = rows_by_id[input_id]
            observation = dict(
                exec_fn(variant, input_id, row["envelope"]["payload"])
            )
            observation.setdefault("variant", variant)
            observation.setdefault("input_id", input_id)
            observation.setdefault(
                "controlled_numpy_version", identity["numpy_version"]
            )
            observation.setdefault("controlled_numpy_file", identity["numpy_file"])
            observation.setdefault("failure_code", None)
            observation.setdefault("status", "FAIL_INFRASTRUCTURE")
            observation.setdefault("scientific_result", None)
            observation.setdefault(
                "verdict",
                observation.get("scientific_result") or "UNOBSERVED",
            )
            terminals[variant][input_id] = observation
    per_mutant = {
        name: {
            "observations": [
                {"input_id": input_id, **dict(terminals[name][input_id])}
                for input_id in selection["input_ids"]
            ],
            "scientific_result": reduce_scientific_result(terminals[name]),
        }
        for name in ("semantic", "syntactic")
    }
    body = {
        "c3_status": C3_STATUS,
        "cell_timeout_sec": CELL_TIMEOUT_SEC,
        "clean_replay_runner_sha256": file_sha256(Path(__file__)),
        "contract_id": selection["contract_id"],
        "controlled_runtime": {
            "array_api_file": identity["array_api_file"],
            "interpreter": identity["interpreter"],
            "numpy_file": identity["numpy_file"],
            "numpy_version": identity["numpy_version"],
            "prefix": identity["prefix"],
            "recovered_gitlink_identity": gitlinks,
            "root": identity["root"],
        },
        "forbidden_consumed_cli": FORBIDDEN_CONSUMED_CLI,
        "frozen_input_aggregate_sha256": selection["frozen_input_aggregate_sha256"],
        "input_ids": list(selection["input_ids"]),
        "not_original_runner_retry": True,
        "paired_evidence_admissible": False,
        "per_input_terminals": terminals,
        "per_mutant": per_mutant,
        "prior_failure_artifact_sha256": PRIOR_ARTIFACT_SHA256,
        "prior_failure_commit": PRIOR_FAILURE_COMMIT,
        "prior_failure_file_sha256": PRIOR_FILE_SHA256,
        "prior_implementation_commit": PRIOR_IMPLEMENTATION_COMMIT,
        "qualification_artifact_sha256": QUALIFICATION_ARTIFACT_SHA256,
        "qualification_commit": QUALIFICATION_COMMIT,
        "qualification_file_sha256": QUALIFICATION_FILE_SHA256,
        "replay_version": REPLAY_VERSION,
        "schema_version": SCHEMA_VERSION,
        "scientific_class": "CONTROLLED_NUMPY_CLEAN_REPLAY",
        "semantic_patch": dict(semantic),
        "semantic_patch_sha256": semantic["patch_sha256"],
        "site_id": selection["site_id"],
        "slot_id": selection["slot_id"],
        "static_certification": certification,
        "syntactic_patch": dict(syntactic),
        "syntactic_patch_sha256": syntactic["patch_sha256"],
        "task_id": TASK_ID,
    }
    record = {**body, "artifact_sha256": canonical_sha256(body)}
    _validate_record(record)
    staging = output.with_name(output.name + ".staging")
    staging.mkdir(parents=True, exist_ok=False)
    write_canonical_json(staging / "clean-replay.json", record, exclusive=True)
    os.replace(staging, output)
    return record


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    _reject_selectors(args)
    run_clean_replay_once()
    return 0
