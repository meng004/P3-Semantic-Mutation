"""Outcome-blind first ordinal-8 paired mutant preparation. No formal run."""

from __future__ import annotations

import difflib
import hashlib
import importlib
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
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import APPLICABLE_SLOT_CHRONOLOGY, verify_slot_chronology
from p3_v3.contract_authority import ORDINAL8_SUBJECT_ID

FORBIDDEN_IMPORT_ROOTS = (
    "numpy",
    "profiling_runner",
    "p3_v3.profiling_runner",
)
FROZEN_EVIDENCE_COMMIT = "3f81139d2c620136a20fd16a16d057bd2698f1cd"
FROZEN_PARENT_COMMIT = "f969d3354fef85ffef338b5d5b19980659c7ea96"
FROZEN_CONTRACTS_SHA256 = (
    "f89e979b4c2392ed440e37a92f9742ff68618c2961926f70bfe6096f99958457"
)
FROZEN_INVENTORY_ARTIFACT_SHA256 = (
    "a2f7cf47fc0ddb3db5f1a3268fa319debf8388061b2157b88c633ab0f4ed0c5c"
)
SLOT_ID = "a2f7a2164e7968cb5a6edf0aafa9bb406b8ba089df79cccdc565bdd9164cd913"
SITE_ID = "f37fc591deeeadf562c46130a6cc598ca142c552bbadd1d66b0d5b0d143e2fd3"
CONTRACT_ID_PREFIX = "449bc0e7"
GENERATOR_ID = "CONTRACT_ARRAY_DOMAIN_V1"
QUALIFIED_NAME = "numpy.array_api.linalg:cholesky"
SOURCE_RELATIVE = "numpy/array_api/linalg.py"
SOURCE_FILE_SHA256 = (
    "b64e5f8c46b457c94a96f74da90bff368f409f9f77f27519f0c84e9517803b00"
)
NEUTRAL_SNAPSHOT_ID = (
    "4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b"
)
CONTROLLED_SUBJECT_SOURCE_ID = (
    "667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0"
)
SITE_SPAN = "46:0-62:24"
FROZEN_INPUT_IDS = (
    "82261a722a9730fd1e03c3b138f24bc7ecac9de710de9fd9ac7ae38e04a3c2b2",
    "cbd30153ac94b040e5fee28d8c559db619ec4f7342c9fb2c2b881ed02a2d21b2",
    "3ae9ca4d6efa478cff35e7ffb5d5be8f6dd9dea8443c43018933a206fceae2f7",
    "499142be0698116e670bfbead9881e25ed54e3be9ff3e157c23b73e5c0d6d102",
    "a3faf1a42deb3e155b457d1d7278b0388672895dba880b89b3c653a8484182b7",
)
MONO_SLOT_IDS = frozenset(
    {
        "77f69dc9343febceb4f3f5163d6da260dbb08ed3e1a08bd30828bec11d9ca40a",
        "07546603ddbc9fca6e73bc7f7e551fa52f9dfd94c648c19e7b96cb12bcb0aac0",
    }
)
FREEZE_RELATIVE = "data/p3_v3/phase2/ordinal8-partial-contract-freeze"
FORMAL_RUNTIME_ROOT = Path("/tmp/p3-c3-ordinal8-first-paired-evidence")
FORMAL_OUTPUT_ROOT_RELATIVE = "data/p3_v3/phase3/ordinal8-first-paired-evidence"
SEMANTIC_OPERATOR_ID = "INV_TF_SCALE_CHOLESKY_FACTOR_V1"
SEMANTIC_OLD = "    return Array._new(L)\n"
SEMANTIC_NEW = "    return Array._new(2 * L)\n"
SEMANTIC_SPAN = "62:4-62:24"
SYNTACTIC_OPERATOR_ID = "FIRST_ORDER_BOOLEAN_LITERAL_FLIP_V1"
SYNTACTIC_OLD = "def cholesky(x: Array, /, *, upper: bool = False) -> Array:\n"
SYNTACTIC_NEW = "def cholesky(x: Array, /, *, upper: bool = True) -> Array:\n"
SYNTACTIC_SPAN = "46:43-46:48"
_CONTRACT_SCHEMA = {
    "contract_id": str,
    "generator_id": str,
    "domain": dict,
    "site_id": str,
}
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
_VARIANTS = ("original", "semantic", "syntactic")


def selected_inventory_path(freeze_root: str | Path) -> Path:
    return Path(freeze_root) / f"evaluation-inputs-contract-{SLOT_ID}.json"


def _freeze_root(repo_root: Path) -> Path:
    return Path(repo_root) / FREEZE_RELATIVE


def _reject_user_slot(slot_id: str | None) -> None:
    if slot_id is None:
        return
    validate_sha256(slot_id, "slot_id")
    if slot_id in MONO_SLOT_IDS:
        raise EvidenceError("E_PAIRED_SLOT", "MONO slots are never selectable")
    raise EvidenceError("E_PAIRED_SLOT", "slot replacement is rejected")


def _verify_evidence_commit(repo_root: Path) -> str:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "merge-base",
            "--is-ancestor",
            FROZEN_EVIDENCE_COMMIT,
            "HEAD",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise EvidenceError(
            "E_PAIRED_COMMIT",
            f"frozen evidence commit {FROZEN_EVIDENCE_COMMIT} is not an ancestor",
        )
    return FROZEN_EVIDENCE_COMMIT


def _assert_outcome_blind(repo_root: Path) -> None:
    official = Path(repo_root) / FORMAL_OUTPUT_ROOT_RELATIVE
    if official.exists():
        raise EvidenceError(
            "E_OUTCOME_BLINDNESS",
            "OUTCOME_BLINDNESS_CONFLICT: mutation outcome already present",
        )
    if FORMAL_RUNTIME_ROOT.exists():
        raise EvidenceError(
            "E_OUTCOME_BLINDNESS",
            "OUTCOME_BLINDNESS_CONFLICT: formal runtime already present",
        )


def frozen_input_aggregate_sha256() -> str:
    return canonical_sha256(
        {
            "domain": "P3-E-CONTRACT-INPUT-SET-v1",
            "input_ids": list(FROZEN_INPUT_IDS),
            "inventory_artifact_sha256": FROZEN_INVENTORY_ARTIFACT_SHA256,
            "slot_id": SLOT_ID,
        }
    )


def bind_frozen_first_slot(
    repo_root: str | Path, slot_id: str | None = None
) -> dict[str, Any]:
    _reject_user_slot(slot_id)
    root = Path(repo_root)
    _assert_outcome_blind(root)
    evidence_commit = _verify_evidence_commit(root)
    freeze = _freeze_root(root)
    contracts_path = freeze / "contracts.json"
    if file_sha256(contracts_path) != FROZEN_CONTRACTS_SHA256:
        raise EvidenceError("E_PAIRED_IDENTITY", "contracts.json SHA-256 differs")
    contracts = read_canonical_json(contracts_path)
    if not isinstance(contracts, Mapping):
        raise EvidenceError("E_PAIRED_IDENTITY", "contracts.json is not an object")
    if MONO_SLOT_IDS.intersection(contracts):
        raise EvidenceError("E_PAIRED_SLOT", "MONO slots entered the contract map")
    if SLOT_ID not in contracts:
        raise EvidenceError("E_PAIRED_SLOT", "frozen first slot is absent")
    contract = validate_exact_object(
        dict(contracts[SLOT_ID]), _CONTRACT_SCHEMA, "contract"
    )
    contract_id = validate_sha256(contract["contract_id"], "contract_id")
    if not contract_id.startswith(CONTRACT_ID_PREFIX):
        raise EvidenceError("E_PAIRED_IDENTITY", "contract_id prefix differs")
    if contract["site_id"] != SITE_ID:
        raise EvidenceError("E_PAIRED_IDENTITY", "site_id differs")
    if contract["generator_id"] != GENERATOR_ID:
        raise EvidenceError("E_PAIRED_IDENTITY", "generator_id differs")
    inventory_path = selected_inventory_path(freeze)
    inventory = read_canonical_json(inventory_path)
    if not isinstance(inventory, Mapping):
        raise EvidenceError("E_PAIRED_IDENTITY", "inventory is not an object")
    inventory_body = {
        key: value for key, value in inventory.items() if key != "artifact_sha256"
    }
    digest = validate_sha256(
        inventory.get("artifact_sha256"), "inventory.artifact_sha256"
    )
    if (
        digest != FROZEN_INVENTORY_ARTIFACT_SHA256
        or digest != canonical_sha256(inventory_body)
    ):
        raise EvidenceError("E_PAIRED_IDENTITY", "inventory artifact differs")
    if (
        inventory.get("slot_id") != SLOT_ID
        or inventory.get("site_id") != SITE_ID
        or inventory.get("contract_id") != contract_id
        or inventory.get("controlled_subject_id") != ORDINAL8_SUBJECT_ID
    ):
        raise EvidenceError("E_PAIRED_IDENTITY", "inventory identity differs")
    rows = inventory.get("rows")
    if not isinstance(rows, list) or len(rows) != 5:
        raise EvidenceError("E_PAIRED_IDENTITY", "frozen inventory must have five rows")
    input_ids = [row["input_id"] for row in rows]
    if input_ids != list(FROZEN_INPUT_IDS):
        raise EvidenceError("E_PAIRED_IDENTITY", "frozen input IDs differ")
    if {row["status"] for row in rows} != {"CONTRACT_INPUT_GENERATED"}:
        raise EvidenceError("E_PAIRED_IDENTITY", "frozen row status differs")
    return {
        "evidence_commit": evidence_commit,
        "parent_commit": FROZEN_PARENT_COMMIT,
        "slot_id": SLOT_ID,
        "site_id": SITE_ID,
        "site_span": SITE_SPAN,
        "qualified_name": QUALIFIED_NAME,
        "source_path": SOURCE_RELATIVE,
        "controlled_subject_id": ORDINAL8_SUBJECT_ID,
        "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
        "contract_id": contract_id,
        "generator_id": GENERATOR_ID,
        "contract": contract,
        "inventory": dict(inventory),
        "rows": list(rows),
        "input_ids": input_ids,
        "inventory_artifact_sha256": digest,
        "frozen_input_aggregate_sha256": frozen_input_aggregate_sha256(),
    }


def _unified_diff(path: str, original: str, mutated: str) -> str:
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            mutated.splitlines(keepends=True),
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
            n=3,
        )
    )


def _patch_record(
    *,
    operator_id: str,
    span: str,
    source: str,
    target: str,
    original_text: str,
) -> dict[str, str]:
    if original_text.count(source) != 1:
        raise EvidenceError("E_PATCH_SPAN", f"{operator_id} source span is not unique")
    mutated = original_text.replace(source, target, 1)
    diff = _unified_diff(SOURCE_RELATIVE, original_text, mutated)
    return {
        "operator_id": operator_id,
        "path": SOURCE_RELATIVE,
        "span": span,
        "source": source,
        "target": target,
        "unified_diff": diff,
        "patch_sha256": hashlib.sha256(diff.encode("utf-8")).hexdigest(),
    }


def generate_semantic_patch(source_text: str) -> dict[str, str]:
    if SEMANTIC_OLD not in source_text:
        raise EvidenceError("E_SEMANTIC_MUTANT", "SEMANTIC_MUTANT source span missing")
    return _patch_record(
        operator_id=SEMANTIC_OPERATOR_ID,
        span=SEMANTIC_SPAN,
        source=SEMANTIC_OLD,
        target=SEMANTIC_NEW,
        original_text=source_text,
    )


def first_order_baseline_token(source_text: str) -> tuple[str, str, str]:
    lines = source_text.splitlines(keepends=True)
    if len(lines) < 62:
        raise EvidenceError(
            "E_SYNTACTIC_BASELINE", "SYNTACTIC_BASELINE span is missing"
        )
    for lineno in range(46, 62):
        line = lines[lineno - 1]
        for token, flipped in (("False", "True"), ("True", "False")):
            column = line.find(token)
            if column < 0:
                continue
            span = f"{lineno}:{column}-{lineno}:{column + len(token)}"
            return token, flipped, span
        for left, right in (
            (" not in ", " in "),
            (" in ", " not in "),
            ("!=", "=="),
            ("==", "!="),
            ("<=", ">"),
            (">=", "<"),
            ("<", ">="),
            (">", "<="),
        ):
            column = line.find(left)
            if column < 0:
                continue
            span = f"{lineno}:{column}-{lineno}:{column + len(left)}"
            return left.strip(), right.strip(), span
    raise EvidenceError(
        "E_SYNTACTIC_BASELINE", "SYNTACTIC_BASELINE unique token is not applicable"
    )


def generate_syntactic_patch(source_text: str) -> dict[str, str]:
    token, flipped, span = first_order_baseline_token(source_text)
    if (token, flipped, span) != ("False", "True", SYNTACTIC_SPAN):
        raise EvidenceError(
            "E_SYNTACTIC_BASELINE",
            "SYNTACTIC_BASELINE unique preregistered token is not applicable",
        )
    if SYNTACTIC_OLD not in source_text:
        raise EvidenceError(
            "E_SYNTACTIC_BASELINE", "SYNTACTIC_BASELINE source span missing"
        )
    return _patch_record(
        operator_id=SYNTACTIC_OPERATOR_ID,
        span=SYNTACTIC_SPAN,
        source=SYNTACTIC_OLD,
        target=SYNTACTIC_NEW,
        original_text=source_text,
    )


def apply_patch_text(source_text: str, patch: Mapping[str, str]) -> str:
    old = patch["source"]
    new = patch["target"]
    if source_text.count(old) != 1:
        raise EvidenceError("E_PATCH_SPAN", "patch source is not unique")
    return source_text.replace(old, new, 1)


def _changed_lines(original: str, mutated: str) -> list[int]:
    left = original.splitlines()
    right = mutated.splitlines()
    changed = [
        index
        for index, (old, new) in enumerate(zip(left, right), start=1)
        if old != new
    ]
    if len(left) != len(right):
        longer = max(len(left), len(right))
        changed.extend(range(min(len(left), len(right)) + 1, longer + 1))
    return changed


def _span_line(span: str) -> int:
    return int(span.split(":")[0])


def _static_scope_pass(source_text: str, patch: Mapping[str, str]) -> bool:
    mutated = apply_patch_text(source_text, patch)
    changed = _changed_lines(source_text, mutated)
    return changed == [_span_line(patch["span"])]


def _witness(patch: Mapping[str, str]) -> dict[str, str]:
    return {
        "witness_id": canonical_sha256(
            {
                "domain": "P3-CERTIFICATION-WITNESS-v1",
                "operator_id": patch["operator_id"],
                "patch_sha256": patch["patch_sha256"],
                "span": patch["span"],
            }
        )
    }


def certify_static_patches(
    selection: Mapping[str, Any],
    semantic: Mapping[str, str],
    syntactic: Mapping[str, str],
    source_text: str,
) -> dict[str, Any]:
    if semantic["patch_sha256"] == syntactic["patch_sha256"]:
        raise EvidenceError("E_PATCH_IDENTITY", "semantic and syntactic patches match")
    if semantic["span"] == syntactic["span"]:
        raise EvidenceError("E_PATCH_IDENTITY", "semantic and syntactic spans match")
    certified: dict[str, Any] = {"uniqueness": True}
    for name, patch in (("semantic", semantic), ("syntactic", syntactic)):
        if not _static_scope_pass(source_text, patch):
            raise EvidenceError("E_PATCH_SPAN", f"{name} patch escapes preregistered span")
        verify_slot_chronology(
            {
                "slot_id": selection["slot_id"],
                "chronology": list(APPLICABLE_SLOT_CHRONOLOGY),
                "contract": selection["contract"],
                "e_contract": selection["inventory"],
                "patch": {
                    "path": patch["path"],
                    "span": patch["span"],
                    "source": patch["source"],
                    "target": patch["target"],
                },
                "certification_witness": _witness(patch),
                "e_common_input_ids": [],
                "e_contract_input_ids": list(selection["input_ids"]),
            }
        )
        certified[name] = {
            "PATCH_SCOPE_PASS": True,
            "UNIQUENESS_PASS": True,
            "witness_id": _witness(patch)["witness_id"],
        }
    return certified


def prepare_controlled_roots(runtime_root: str | Path, output_root: str | Path) -> None:
    runtime = Path(runtime_root)
    output = Path(output_root)
    staging = output.with_name(output.name + ".staging")
    if runtime.exists():
        raise EvidenceError("E_PAIRED_OUTPUT", "runtime root already exists")
    if output.exists():
        raise EvidenceError("E_PAIRED_OUTPUT", "output root already exists")
    if staging.exists():
        raise EvidenceError("E_PAIRED_OUTPUT", "staging root already exists")
    runtime.mkdir(parents=True, exist_ok=False)


def _reject_selectors(argv: Sequence[str]) -> None:
    if not argv:
        return
    flag = argv[0].split("=", 1)[0]
    if flag in _SELECTOR_FLAGS or flag.startswith("--"):
        raise EvidenceError("E_PAIRED_SELECTOR", "selector arguments are rejected")
    raise EvidenceError("E_PAIRED_SELECTOR", "arguments are rejected")


def run_controlled_pair(
    *,
    selection: Mapping[str, Any],
    source_text: str,
    semantic: Mapping[str, str],
    syntactic: Mapping[str, str],
    runtime_root: str | Path,
    output_root: str | Path,
    executor: Callable[[str, str, object], Mapping[str, Any]],
) -> dict[str, Any]:
    if executor is None:
        raise EvidenceError("E_PAIRED_EXECUTOR", "an executor is required")
    prepare_controlled_roots(runtime_root, output_root)
    certification = certify_static_patches(
        selection, semantic, syntactic, source_text
    )
    terminals: dict[str, dict[str, Any]] = {variant: {} for variant in _VARIANTS}
    for variant in _VARIANTS:
        for row in selection["rows"]:
            observation = dict(
                executor(variant, row["input_id"], row["envelope"]["payload"])
            )
            terminals[variant][row["input_id"]] = observation
    per_mutant = {
        name: {
            "scientific_result": None
            if any(
                row.get("observation_class") == "SYNTHETIC_INFRASTRUCTURE"
                or row.get("scientific_result") is None
                for row in terminals[name].values()
            )
            else _reduce_mutant(terminals[name]),
            "observations": [
                {
                    "input_id": input_id,
                    **dict(terminals[name][input_id]),
                }
                for input_id in selection["input_ids"]
            ],
        }
        for name in ("semantic", "syntactic")
    }
    output = Path(output_root)
    staging = output.with_name(output.name + ".staging")
    body = {
        "controlled_subject_id": selection["controlled_subject_id"],
        "contract_id": selection["contract_id"],
        "evidence_commit": selection["evidence_commit"],
        "frozen_input_aggregate_sha256": selection["frozen_input_aggregate_sha256"],
        "input_ids": list(selection["input_ids"]),
        "inventory_artifact_sha256": selection["inventory_artifact_sha256"],
        "per_input_terminals": terminals,
        "per_mutant": per_mutant,
        "semantic_patch": dict(semantic),
        "site_id": selection["site_id"],
        "slot_id": selection["slot_id"],
        "static_certification": certification,
        "syntactic_patch": dict(syntactic),
    }
    record = {**body, "artifact_sha256": canonical_sha256(body)}
    staging.mkdir(parents=True, exist_ok=False)
    write_canonical_json(staging / "paired-evidence.json", record, exclusive=True)
    os.replace(staging, output)
    return record


def _reduce_mutant(observations: Mapping[str, Mapping[str, Any]]) -> str:
    states = [row.get("status") for row in observations.values()]
    if any(state == "TIMEOUT" for state in states):
        return "TIMEOUT"
    if any(state in {"FAIL", "ERROR", "FAIL_INFRASTRUCTURE"} for state in states):
        return "FAIL"
    if any(row.get("verdict") == "KILL" for row in observations.values()):
        return "KILL"
    if all(row.get("verdict") == "SURVIVE" for row in observations.values()):
        return "SURVIVE"
    return "INCONCLUSIVE"


def frozen_source_path(repo_root: str | Path) -> Path:
    return (
        Path(repo_root)
        / "data/p3_v3/p12_intake/extracted"
        / NEUTRAL_SNAPSHOT_ID
        / SOURCE_RELATIVE
    )


def read_frozen_source(repo_root: str | Path) -> str:
    path = frozen_source_path(repo_root)
    if not path.is_file() or path.is_symlink():
        raise EvidenceError("E_SOURCE_IDENTITY", "SOURCE_IDENTITY_REQUIRED")
    if file_sha256(path) != SOURCE_FILE_SHA256:
        raise EvidenceError("E_SOURCE_IDENTITY", "source file SHA-256 differs")
    text = path.read_text(encoding="utf-8")
    if SEMANTIC_OLD not in text or SYNTACTIC_OLD not in text:
        raise EvidenceError("E_SOURCE_IDENTITY", "preregistered spans missing")
    return text


def _make_real_executor(
    source_text: str,
    semantic: Mapping[str, str],
    syntactic: Mapping[str, str],
) -> Callable[[str, str, object], Mapping[str, Any]]:
    variants = {
        "original": source_text,
        "semantic": apply_patch_text(source_text, semantic),
        "syntactic": apply_patch_text(source_text, syntactic),
    }

    def executor(
        variant: str, input_id: str, payload: object
    ) -> dict[str, Any]:
        return _observe_real_subject(variants[variant], input_id, payload)

    return executor


def _cholesky_function_text(source_text: str) -> str:
    lines = source_text.splitlines(keepends=True)
    if len(lines) < 62:
        raise EvidenceError("E_SOURCE_IDENTITY", "cholesky span is missing")
    return "".join(lines[45:62])


def _observe_real_subject(
    source_text: str, input_id: str, payload: object
) -> dict[str, Any]:
    try:
        numpy = importlib.import_module("numpy")
        array_object = importlib.import_module("numpy.array_api._array_object")
        dtypes = importlib.import_module("numpy.array_api._dtypes")
        elementwise = importlib.import_module("numpy.array_api._elementwise_functions")
    except ImportError as exc:
        return {
            "observation_class": "REAL_SCIENTIFIC",
            "status": "FAIL_INFRASTRUCTURE",
            "scientific_result": None,
            "failure_code": f"numpy import failed: {exc}",
            "input_id": input_id,
        }
    if not isinstance(payload, Mapping) or "matrix" not in payload:
        return {
            "observation_class": "REAL_SCIENTIFIC",
            "status": "FAIL",
            "scientific_result": None,
            "failure_code": "payload.matrix missing",
            "input_id": input_id,
        }
    namespace = {
        "Array": array_object.Array,
        "complex64": dtypes.complex64,
        "complex128": dtypes.complex128,
        "conj": elementwise.conj,
        "np": numpy,
        "_floating_dtypes": dtypes._floating_dtypes,
    }
    try:
        exec(_cholesky_function_text(source_text), namespace, namespace)
        cholesky = namespace["cholesky"]
        matrix = payload["matrix"]
        factor = cholesky(array_object.Array._new(numpy.asarray(matrix, dtype=float)))
        values = factor._array
        reconstructed = values @ values.T
        original = numpy.asarray(matrix, dtype=float)
        residual = numpy.abs(reconstructed - original)
        limit = 1e-10 + 1e-10 * numpy.abs(original)
        violated = bool(numpy.any(residual > limit))
        return {
            "observation_class": "REAL_SCIENTIFIC",
            "status": "PASS",
            "scientific_result": (
                "KILL" if violated else "SURVIVE"
            ),
            "verdict": "KILL" if violated else "SURVIVE",
            "expected_violation_direction": "reconstruction_error_exceeds_tolerance",
            "input_id": input_id,
        }
    except TimeoutError:
        return {
            "observation_class": "REAL_SCIENTIFIC",
            "status": "TIMEOUT",
            "scientific_result": "TIMEOUT",
            "verdict": "TIMEOUT",
            "input_id": input_id,
        }
    except Exception as exc:  # noqa: BLE001 - retain formal failure
        return {
            "observation_class": "REAL_SCIENTIFIC",
            "status": "FAIL",
            "scientific_result": "FAIL",
            "verdict": "FAIL",
            "failure_code": type(exc).__name__,
            "input_id": input_id,
        }


def run_formal_once(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    selection = bind_frozen_first_slot(root)
    source_text = read_frozen_source(root)
    semantic = generate_semantic_patch(source_text)
    syntactic = generate_syntactic_patch(source_text)
    return run_controlled_pair(
        selection=selection,
        source_text=source_text,
        semantic=semantic,
        syntactic=syntactic,
        runtime_root=FORMAL_RUNTIME_ROOT,
        output_root=root / FORMAL_OUTPUT_ROOT_RELATIVE,
        executor=_make_real_executor(source_text, semantic, syntactic),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    _reject_selectors(args)
    run_formal_once()
    return 0
