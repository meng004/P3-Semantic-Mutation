"""Outcome-blind remaining-three ordinal-8 paired batch. No formal run."""

from __future__ import annotations

import difflib
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
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.contract_authority import ORDINAL8_SUBJECT_ID
from p3_v3.ordinal8_controlled_numpy_clean_replay_v1 import (
    AMBIENT_NUMPY_FILE,
    probe_controlled_imports,
    reduce_scientific_result,
    sanitize_replay_env,
    verify_controlled_import_closure,
    verify_controlled_runtime_identity,
    verify_qualification_record,
    verify_recovered_gitlinks,
)
from p3_v3.ordinal8_controlled_numpy_runtime import (
    FORMAL_RUNTIME_ROOT as QUALIFICATION_RUNTIME_ROOT,
)
from p3_v3.ordinal8_first_paired_evidence import (
    FREEZE_RELATIVE,
    FROZEN_CONTRACTS_SHA256,
    NEUTRAL_SNAPSHOT_ID,
    apply_patch_text,
    certify_static_patches,
)

FORBIDDEN_IMPORT_ROOTS = (
    "numpy",
    "profiling_runner",
    "p3_v3.profiling_runner",
)
TASK_ID = "P3_C3_ORDINAL8_REMAINING_THREE_PAIRED_EVIDENCE_BATCH_PREPARATION"
BATCH_VERSION = "ordinal8-remaining-three-paired-batch-v1"
SCHEMA_VERSION = "p3-ordinal8-remaining-three-paired-batch-v1"
C3_STATUS = "blocked"
CELL_TIMEOUT_SEC = 60
VARIANTS = ("original", "semantic", "syntactic")
PREREGISTRATION_COMMIT = "0d567ab19954ac99354f82fd61ab98668c19b1db"
PREREGISTRATION_RELATIVE = (
    "docs/superpowers/specs/"
    "2026-08-28-p3-c3-ordinal8-remaining-three-paired-evidence-batch-design.md"
)
PREREGISTRATION_FILE_SHA256 = (
    "bc2d89d081a7279ef4181d97afb12a49418dd121157dc656c959f43ddf6a73f8"
)
EVIDENCE_COMMIT = "1b945f1bf3238c03c9ad4dc7170dc69e6bb744c1"
PRIOR_INV_TF_COMMIT = EVIDENCE_COMMIT
PRIOR_INV_TF_FILE_SHA256 = (
    "5b734c2a21283d6cdb83a5827d50bdf688d69eb7e2dcd620d69b01a9875000ff"
)
PRIOR_INV_TF_ARTIFACT_SHA256 = (
    "f0ce09ff92e181fda27573c612643d3b48a8e4e24081d390f19acc4ebbd8897f"
)
PRIOR_INV_TF_RECORD_RELATIVE = (
    "data/p3_v3/phase3/ordinal8-first-paired-evidence-clean-replay-v1/clean-replay.json"
)
QUALIFICATION_COMMIT = "256305eb7d0bd835cb1fc37d99e5cc1732fefba2"
QUALIFICATION_FILE_SHA256 = (
    "290506c4324a062d56fecbbe22d3baa829cd99a2668fee4eeb70fd25d7ac46e0"
)
QUALIFICATION_ARTIFACT_SHA256 = (
    "501203515a524bcd4b51a6148908af25dbdd09932c7790e2e257404533d80abf"
)
EXCLUDED_INV_TF_SEMANTIC_PATCH_SHA256 = (
    "9f0bfbb4d14bb944bf13cfdb97e135590f71208b62eabeb8b3d78937f6cfcda6"
)
EXCLUDED_INV_TF_SYNTACTIC_PATCH_SHA256 = (
    "234be58e515729e102dbb255564960e3767e939301d37e30a72a9fc333867f82"
)
FORMAL_RUNTIME_ROOT = Path("/tmp/p3-c3-ordinal8-remaining-three-paired-batch-v1")
FORMAL_OUTPUT_ROOT_RELATIVE = (
    "data/p3_v3/phase3/ordinal8-remaining-three-paired-batch-v1"
)
FORBIDDEN_CONSUMED_CLIS = (
    "scripts/p3_v3/run_ordinal8_first_paired_evidence.py",
    "scripts/p3_v3/run_ordinal8_controlled_numpy_clean_replay_v1.py",
)
INV_TF_SLOT_ID = "a2f7a2164e7968cb5a6edf0aafa9bb406b8ba089df79cccdc565bdd9164cd913"
INV_SI_SLOT_ID = "e8fd94d60c42ed7357d8e00ebc1135b55b44dbde4978f887ab54abe94b261c6c"
CMP_TF_SLOT_ID = "e0b42ce7f2c60d9b3d0feae5ce3280d1619ec78b75c22c3e41fc6c936c3485e6"
CMP_SI_SLOT_ID = "06556e4b744f26766ef8593fc4ae727103082944ae6b26c6179fc947c3a2f1f5"
SLOT_ORDER = (INV_SI_SLOT_ID, CMP_TF_SLOT_ID, CMP_SI_SLOT_ID)
MONO_SLOT_IDS = frozenset(
    {
        "77f69dc9343febceb4f3f5163d6da260dbb08ed3e1a08bd30828bec11d9ca40a",
        "07546603ddbc9fca6e73bc7f7e551fa52f9dfd94c648c19e7b96cb12bcb0aac0",
    }
)
INV_SI_INPUT_IDS = (
    "bafc971271795518178a0c595c4c64092bc9abb44a37a93b24a404e98e54d078",
    "cde5b4777711071dfadb51c74bad4544c76788150d753468f51711ee3678d7a1",
    "40373f5853a5b8cd82760ac4c3af62b85b830317d165a2c8c6a4ff290614a65d",
    "6c2a8c10a883a22695336af7300527a25e996dc5a55bbe6f9dda7a41c0beaa72",
    "76e75bf0a2eba34f5b91748bcd24646429275a48cda10d2bc0365f10b20834fd",
)
CMP_TF_INPUT_IDS = (
    "177271477e557055b0eae40ad55409bedcd6336173054e1f248b3c8a008e71db",
    "d731142f32f15bf44e7475ba6c41a41d14583d07649a0e22ed767a41376270cf",
    "1673ef30f59ebbe02deca678d04a2113906186a0bef91677f8f15a781858a9b5",
    "8e9857f5b13c86a9b69ad9b401bcaa3ff21e9732895da9f21bd2dd446fc055ec",
    "25b89d6a90b9bd027618b73d41dad4a7accc1fe629523c875ac3ee8f50d642a4",
)
CMP_SI_INPUT_IDS = (
    "edc0788958caebf8732955e946ec93ee7f67bde0de2b28243d6309651f4e0c57",
    "c7b46a0acaac520220aa9ccc4fb005bb2811a9837cac4c48018cbb4782d587be",
    "5bf881af9f49c5f53df0c21918161bc87fb68d76aaa1c149aeb5942b395ae1dd",
    "899e1cf136f1fadd1e224e6687a784b747b6137251d2a8ea74d17a77e17dbe1f",
    "4f9f97b4d159437b242e2f5f8716599364138480c53a683af357fdd7f3a462f7",
)
CHOLESKY_RELATIVE = "numpy/array_api/linalg.py"
TYPING_RELATIVE = "numpy/typing/tests/test_typing.py"
CHOLESKY_FILE_SHA256 = (
    "b64e5f8c46b457c94a96f74da90bff368f409f9f77f27519f0c84e9517803b00"
)
TYPING_FILE_SHA256 = (
    "79058ab5ef500e34fde14babf0c5535b5613ba125371c12577a879b304c37c6c"
)
_STUB_CLASSES = frozenset({"STUB_NOT_EXECUTED", "SYNTHETIC_INFRASTRUCTURE"})
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
        "--order",
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
    "batch_runner_sha256",
    "batch_version",
    "c3_status",
    "cell_count",
    "cell_timeout_sec",
    "implementation_commit",
    "not_prior_runner_retry",
    "patches",
    "per_slot",
    "preregistration_commit",
    "preregistration_file_sha256",
    "prior_inv_tf_artifact_sha256",
    "prior_inv_tf_commit",
    "prior_inv_tf_file_sha256",
    "prior_result_disclosed",
    "qualification_artifact_sha256",
    "qualification_commit",
    "qualification_file_sha256",
    "slots",
    "static_certification",
    "task_id",
}
_SLOT_SPECS = (
    {
        "slot_id": INV_SI_SLOT_ID,
        "family_mechanism": "INV/SI",
        "site_id": "f37fc591deeeadf562c46130a6cc598ca142c552bbadd1d66b0d5b0d143e2fd3",
        "contract_id": "bf30280854c72200869c82aec832543c94e50db14d918e40646c05ff8659ed10",
        "contract_prefix": "bf302808",
        "generator_id": "CONTRACT_ARRAY_DOMAIN_V1",
        "qualified_name": "numpy.array_api.linalg:cholesky",
        "source_path": CHOLESKY_RELATIVE,
        "source_sha256": CHOLESKY_FILE_SHA256,
        "site_span": "46:0-62:24",
        "inventory_artifact_sha256": (
            "4294c1a9c2f781c819e69d30c8e49826ef8320363e91224d8504f86bc859abad"
        ),
        "frozen_input_aggregate_sha256": (
            "477ddc91a3606bb19ca68d0f18c8b1744a865e1d547f5c14017c82ed74b16246"
        ),
        "input_ids": INV_SI_INPUT_IDS,
    },
    {
        "slot_id": CMP_TF_SLOT_ID,
        "family_mechanism": "CMP/TF",
        "site_id": "c7ca9add6d16308fcbc02989173ca8e786eab212724104feb6250ebf1a333c35",
        "contract_id": "52e6e0336c207d7c3a38284907890fca9a750ff454e7851b2062f4d9d6b10570",
        "contract_prefix": "52e6e033",
        "generator_id": "CONTRACT_SEQUENCE_DOMAIN_V1",
        "qualified_name": "numpy.typing.tests.test_typing:get_test_cases",
        "source_path": TYPING_RELATIVE,
        "source_sha256": TYPING_FILE_SHA256,
        "site_span": "123:0-129:60",
        "inventory_artifact_sha256": (
            "6465e0425d36515ebd966a6361932ac5a3f162c9a3141e9a72080faa0e357421"
        ),
        "frozen_input_aggregate_sha256": (
            "74259d06afd257f2d9a8d0854bdcfdca5546f9b3ec44daed9b27b4df08256b8b"
        ),
        "input_ids": CMP_TF_INPUT_IDS,
    },
    {
        "slot_id": CMP_SI_SLOT_ID,
        "family_mechanism": "CMP/SI",
        "site_id": "c7ca9add6d16308fcbc02989173ca8e786eab212724104feb6250ebf1a333c35",
        "contract_id": "607a987a8ed4d868903e2ba322d02e2bc2038ab97c6df94951ec37f2d16d850f",
        "contract_prefix": "607a987a",
        "generator_id": "CONTRACT_SEQUENCE_DOMAIN_V1",
        "qualified_name": "numpy.typing.tests.test_typing:get_test_cases",
        "source_path": TYPING_RELATIVE,
        "source_sha256": TYPING_FILE_SHA256,
        "site_span": "123:0-129:60",
        "inventory_artifact_sha256": (
            "db5943676f7d969f021735d375bcfd4768fe0a09a986f510e8d84b838bf71b66"
        ),
        "frozen_input_aggregate_sha256": (
            "9288075930671af56e298a0a44383739786ac13e762cfe3c447c77635b415361"
        ),
        "input_ids": CMP_SI_INPUT_IDS,
    },
)
_PATCH_SPECS = {
    INV_SI_SLOT_ID: {
        "semantic": {
            "operator_id": "INV_SI_TRANSPOSE_CHOLESKY_FACTOR_V1",
            "path": CHOLESKY_RELATIVE,
            "span": "62:4-62:24",
            "source": "    return Array._new(L)\n",
            "target": "    return Array._new(L.T)\n",
            "patch_sha256": (
                "880e678e69a48664af113042ea1828cc1fe3db7d75f2f98a9c2f5d7d0c9909c4"
            ),
        },
        "syntactic": {
            "operator_id": "FIRST_ORDER_MEMBERSHIP_FLIP_CHOLESKY_COMPLEX_V1",
            "path": CHOLESKY_RELATIVE,
            "span": "59:19-59:21",
            "source": "        if U.dtype in [complex64, complex128]:\n",
            "target": "        if U.dtype not in [complex64, complex128]:\n",
            "patch_sha256": (
                "0e36dff5212a1db0978b5caa2a7077c6ded2b3630e83446f2e4fd523b7c5e42b"
            ),
        },
    },
    CMP_TF_SLOT_ID: {
        "semantic": {
            "operator_id": "CMP_TF_EXTEND_ACCEPTED_SUFFIX_SET_V1",
            "path": TYPING_RELATIVE,
            "span": "127:22-127:37",
            "source": '(".pyi", ".py")',
            "target": '(".pyi", ".py", ".txt")',
            "patch_sha256": (
                "bc9f5b151d48cae4a76e46e3276d75e04b018b09c5764e3ab844e113c943b29a"
            ),
        },
        "syntactic": {
            "operator_id": "FIRST_ORDER_MEMBERSHIP_FLIP_GET_TEST_CASES_V1",
            "path": TYPING_RELATIVE,
            "span": "127:19-127:21",
            "source": '            if ext in (".pyi", ".py"):\n',
            "target": '            if ext not in (".pyi", ".py"):\n',
            "patch_sha256": (
                "ded9d61b450522e708287648175236fb31ff48e5584a8c0e6303d5e200c362a2"
            ),
        },
    },
    CMP_SI_SLOT_ID: {
        "semantic": {
            "operator_id": "CMP_SI_INDEX_EXTENSION_FIELD_V1",
            "path": TYPING_RELATIVE,
            "span": "127:15-127:18",
            "source": "if ext in",
            "target": "if short_fname in",
            "patch_sha256": (
                "0693d22901aaff058f78a08ec5f341b80a59be065048e81b5f780d129ef6d7f7"
            ),
        },
        "syntactic": {
            "operator_id": "FIRST_ORDER_CONSTANT_REPLACE_PY_SUFFIX_V1",
            "path": TYPING_RELATIVE,
            "span": "127:31-127:36",
            "source": '".py"',
            "target": '".pyc"',
            "patch_sha256": (
                "ca203bbc8b9be344a54cf4b8f93e57bc4e46725c961bc0e472ea7d6cc6e99a93"
            ),
        },
    },
}
_INV_CELL_SCRIPT = """
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
array_object = importlib.import_module("numpy.array_api._array_object")
dtypes = importlib.import_module("numpy.array_api._dtypes")
elementwise = importlib.import_module("numpy.array_api._elementwise_functions")
numpy_file = _file(numpy)
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
_CMP_CELL_SCRIPT = """
import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

payload = json.loads(sys.stdin.read())
runtime_root = os.path.realpath(payload["runtime_root"])
ambient = payload.get("ambient_numpy") or ""
source_text = payload["source_text"]
entries = payload["payload"]["entries"]

def _file(module):
    path = os.path.realpath(getattr(module, "__file__", "") or "")
    if ambient and (ambient in path or path == os.path.realpath(ambient)):
        raise RuntimeError(f"ambient numpy: {module.__name__}")
    if not path.startswith(runtime_root + os.sep):
        raise RuntimeError(f"import escape: {module.__name__}")
    return path

numpy = importlib.import_module("numpy")
numpy_file = _file(numpy)

class _Param:
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id")

class _Pytest:
    @staticmethod
    def param(*args, **kwargs):
        return _Param(*args, **kwargs)

lines = source_text.splitlines(keepends=True)
start = None
for index, line in enumerate(lines):
    if line.startswith("def get_test_cases"):
        start = index
        break
if start is None:
    raise RuntimeError("get_test_cases missing")
end = start + 1
while end < len(lines) and not (
    lines[end].startswith("def ") or lines[end].startswith("@")
):
    end += 1
func_src = "".join(lines[start:end]).replace(
    "def get_test_cases(directory: str) -> Iterator[ParameterSet]:",
    "def get_test_cases(directory):",
)
namespace = {"os": os, "pytest": _Pytest()}
exec(func_src, namespace, namespace)
get_test_cases = namespace["get_test_cases"]
with tempfile.TemporaryDirectory() as tmp:
    for name in entries:
        Path(tmp, name).write_text("", encoding="utf-8")
    yielded = {item.id for item in get_test_cases(tmp)}
expected = {
    Path(name).stem for name in entries if Path(name).suffix in {".py", ".pyi"}
}
violated = yielded != expected
print(json.dumps({
    "controlled_numpy_file": numpy_file,
    "controlled_numpy_version": numpy.__version__,
    "failure_code": None,
    "scientific_result": "KILL" if violated else "SURVIVE",
    "status": "PASS",
    "verdict": "KILL" if violated else "SURVIVE",
}, sort_keys=True, separators=(",", ":")))
"""


def _freeze_root(repo_root: Path) -> Path:
    return Path(repo_root) / FREEZE_RELATIVE


def _extracted_source(repo_root: Path, relative: str) -> Path:
    return (
        Path(repo_root)
        / "data/p3_v3/p12_intake/extracted"
        / NEUTRAL_SNAPSHOT_ID
        / relative
    )


def _same_or_nested(left: Path, right: Path) -> bool:
    first = left.resolve()
    second = right.resolve()
    return first == second or first in second.parents or second in first.parents


def _verify_commit_ancestor(repo_root: Path, commit: str, code: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", commit, "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise EvidenceError(code, f"{commit} is not an ancestor of HEAD")
    return commit


def _head_commit(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise EvidenceError("E_IMPLEMENTATION_COMMIT", "HEAD commit is unavailable")
    return result.stdout.strip()


def _reject_user_slot(slot_id: str | None) -> None:
    if slot_id is None:
        return
    validate_sha256(slot_id, "slot_id")
    if slot_id in MONO_SLOT_IDS:
        raise EvidenceError("E_BATCH_SLOT", "MONO slots are never selectable")
    if slot_id == INV_TF_SLOT_ID:
        raise EvidenceError("E_BATCH_SLOT", "INV/TF slot replacement is rejected")
    raise EvidenceError("E_BATCH_SLOT", "slot replacement is rejected")


def _unified_diff(path: str, original: str, mutated: str) -> str:
    name = Path(path).name
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            mutated.splitlines(keepends=True),
            fromfile=f"a/{name}",
            tofile=f"b/{name}",
            n=3,
        )
    )


def _patch_record(
    *,
    operator_id: str,
    path: str,
    span: str,
    source: str,
    target: str,
    original_text: str,
    expected_sha256: str,
) -> dict[str, str]:
    if original_text.count(source) != 1:
        raise EvidenceError("E_PATCH_SPAN", f"{operator_id} source span is not unique")
    mutated = original_text.replace(source, target, 1)
    diff = _unified_diff(path, original_text, mutated)
    digest = hashlib.sha256(diff.encode("utf-8")).hexdigest()
    if digest != expected_sha256:
        raise EvidenceError("E_PATCH_IDENTITY", f"{operator_id} patch SHA-256 differs")
    return {
        "operator_id": operator_id,
        "path": path,
        "span": span,
        "source": source,
        "target": target,
        "unified_diff": diff,
        "patch_sha256": digest,
    }


def apply_named_patch(source_text: str, patch: Mapping[str, str]) -> str:
    return apply_patch_text(source_text, patch)


def read_frozen_source(repo_root: str | Path, relative: str, expected_sha256: str) -> str:
    path = _extracted_source(Path(repo_root), relative)
    if not path.is_file() or path.is_symlink():
        raise EvidenceError("E_SOURCE_IDENTITY", "SOURCE_IDENTITY_REQUIRED")
    if file_sha256(path) != expected_sha256:
        raise EvidenceError("E_SOURCE_IDENTITY", "source file SHA-256 differs")
    return path.read_text(encoding="utf-8")


def frozen_input_aggregate_sha256(
    slot_id: str, input_ids: Sequence[str], inventory_artifact_sha256: str
) -> str:
    return canonical_sha256(
        {
            "domain": "P3-E-CONTRACT-INPUT-SET-v1",
            "input_ids": list(input_ids),
            "inventory_artifact_sha256": inventory_artifact_sha256,
            "slot_id": slot_id,
        }
    )


def prior_inv_tf_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / PRIOR_INV_TF_RECORD_RELATIVE


def verify_prior_inv_tf_evidence(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise EvidenceError("E_PRIOR_INV_TF", "prior INV/TF evidence is absent")
    if file_sha256(source) != PRIOR_INV_TF_FILE_SHA256:
        raise EvidenceError("E_PRIOR_INV_TF", "prior INV/TF file SHA-256 differs")
    record = read_canonical_json(source)
    if not isinstance(record, Mapping):
        raise EvidenceError("E_PRIOR_INV_TF", "prior INV/TF record is not an object")
    digest = record.get("artifact_sha256")
    body = {key: value for key, value in record.items() if key != "artifact_sha256"}
    if digest != PRIOR_INV_TF_ARTIFACT_SHA256 or digest != canonical_sha256(body):
        raise EvidenceError("E_PRIOR_INV_TF", "prior INV/TF artifact SHA-256 differs")
    return dict(record)


def bind_remaining_three_slots(
    repo_root: str | Path, slot_id: str | None = None
) -> list[dict[str, Any]]:
    _reject_user_slot(slot_id)
    root = Path(repo_root)
    freeze = _freeze_root(root)
    contracts_path = freeze / "contracts.json"
    if file_sha256(contracts_path) != FROZEN_CONTRACTS_SHA256:
        raise EvidenceError("E_BATCH_IDENTITY", "contracts.json SHA-256 differs")
    contracts = read_canonical_json(contracts_path)
    if not isinstance(contracts, Mapping):
        raise EvidenceError("E_BATCH_IDENTITY", "contracts.json is not an object")
    if MONO_SLOT_IDS.intersection(contracts):
        raise EvidenceError("E_BATCH_SLOT", "MONO slots entered the contract map")
    bound: list[dict[str, Any]] = []
    for spec in _SLOT_SPECS:
        if spec["slot_id"] not in contracts:
            raise EvidenceError("E_BATCH_SLOT", f"{spec['family_mechanism']} slot is absent")
        contract = validate_exact_object(
            dict(contracts[spec["slot_id"]]), _CONTRACT_SCHEMA, "contract"
        )
        contract_id = validate_sha256(contract["contract_id"], "contract_id")
        if contract_id != spec["contract_id"]:
            raise EvidenceError("E_BATCH_IDENTITY", "contract_id differs")
        if not contract_id.startswith(spec["contract_prefix"]):
            raise EvidenceError("E_BATCH_IDENTITY", "contract_id prefix differs")
        if contract["site_id"] != spec["site_id"]:
            raise EvidenceError("E_BATCH_IDENTITY", "site_id differs")
        if contract["generator_id"] != spec["generator_id"]:
            raise EvidenceError("E_BATCH_IDENTITY", "generator_id differs")
        inventory_path = freeze / f"evaluation-inputs-contract-{spec['slot_id']}.json"
        inventory = read_canonical_json(inventory_path)
        if not isinstance(inventory, Mapping):
            raise EvidenceError("E_BATCH_IDENTITY", "inventory is not an object")
        inventory_body = {
            key: value for key, value in inventory.items() if key != "artifact_sha256"
        }
        digest = validate_sha256(
            inventory.get("artifact_sha256"), "inventory.artifact_sha256"
        )
        if (
            digest != spec["inventory_artifact_sha256"]
            or digest != canonical_sha256(inventory_body)
        ):
            raise EvidenceError("E_BATCH_IDENTITY", "inventory artifact differs")
        if (
            inventory.get("slot_id") != spec["slot_id"]
            or inventory.get("site_id") != spec["site_id"]
            or inventory.get("contract_id") != contract_id
            or inventory.get("controlled_subject_id") != ORDINAL8_SUBJECT_ID
        ):
            raise EvidenceError("E_BATCH_IDENTITY", "inventory identity differs")
        rows = inventory.get("rows")
        if not isinstance(rows, list) or len(rows) != 5:
            raise EvidenceError("E_BATCH_IDENTITY", "frozen inventory must have five rows")
        input_ids = [row["input_id"] for row in rows]
        if input_ids != list(spec["input_ids"]):
            raise EvidenceError("E_BATCH_IDENTITY", "frozen input IDs differ")
        if {row["status"] for row in rows} != {"CONTRACT_INPUT_GENERATED"}:
            raise EvidenceError("E_BATCH_IDENTITY", "frozen row status differs")
        aggregate = frozen_input_aggregate_sha256(
            spec["slot_id"], input_ids, digest
        )
        if aggregate != spec["frozen_input_aggregate_sha256"]:
            raise EvidenceError("E_BATCH_IDENTITY", "input aggregate differs")
        bound.append(
            {
                "slot_id": spec["slot_id"],
                "family_mechanism": spec["family_mechanism"],
                "site_id": spec["site_id"],
                "site_span": spec["site_span"],
                "qualified_name": spec["qualified_name"],
                "source_path": spec["source_path"],
                "source_sha256": spec["source_sha256"],
                "controlled_subject_id": ORDINAL8_SUBJECT_ID,
                "contract_id": contract_id,
                "generator_id": spec["generator_id"],
                "contract": contract,
                "inventory": dict(inventory),
                "rows": list(rows),
                "input_ids": input_ids,
                "inventory_artifact_sha256": digest,
                "frozen_input_aggregate_sha256": aggregate,
                "repo_root": str(root),
            }
        )
    selected = [row["slot_id"] for row in bound]
    if selected != list(SLOT_ORDER):
        raise EvidenceError("E_BATCH_SLOT", "remaining slot order differs")
    if INV_TF_SLOT_ID in selected or MONO_SLOT_IDS.intersection(selected):
        raise EvidenceError("E_BATCH_SLOT", "excluded slot entered the batch")
    return bound


def generate_slot_patches(
    repo_root: str | Path, selections: Sequence[Mapping[str, Any]]
) -> dict[str, dict[str, dict[str, str]]]:
    sources = {
        CHOLESKY_RELATIVE: read_frozen_source(
            repo_root, CHOLESKY_RELATIVE, CHOLESKY_FILE_SHA256
        ),
        TYPING_RELATIVE: read_frozen_source(
            repo_root, TYPING_RELATIVE, TYPING_FILE_SHA256
        ),
    }
    generated: dict[str, dict[str, dict[str, str]]] = {}
    for selection in selections:
        slot_id = selection["slot_id"]
        pair: dict[str, dict[str, str]] = {}
        for kind, spec in _PATCH_SPECS[slot_id].items():
            if spec["path"] != selection["source_path"]:
                raise EvidenceError("E_PATCH_PATH", f"{slot_id} {kind} path differs")
            pair[kind] = _patch_record(
                operator_id=spec["operator_id"],
                path=spec["path"],
                span=spec["span"],
                source=spec["source"],
                target=spec["target"],
                original_text=sources[spec["path"]],
                expected_sha256=spec["patch_sha256"],
            )
        generated[slot_id] = pair
    return generated


def certify_remaining_patches(
    selections: Sequence[Mapping[str, Any]],
    patches: Mapping[str, Mapping[str, Mapping[str, str]]],
) -> dict[str, Any]:
    certified_slots: dict[str, Any] = {}
    identities: list[tuple[str, str, str, str, str]] = []
    for selection in selections:
        slot_id = selection["slot_id"]
        pair = patches[slot_id]
        for kind, patch in pair.items():
            if patch.get("path") != selection["source_path"]:
                raise EvidenceError("E_PATCH_PATH", f"{kind} patch path differs")
            identities.append(
                (
                    patch["patch_sha256"],
                    patch["operator_id"],
                    patch["path"],
                    patch["source"],
                    patch["target"],
                )
            )
        certified_slots[slot_id] = certify_static_patches(
            selection,
            pair["semantic"],
            pair["syntactic"],
            _source_text_for_certify(selection),
        )
    hashes = [row[0] for row in identities]
    if len(set(hashes)) != 6:
        raise EvidenceError("E_PATCH_IDENTITY", "six remaining patches are not unique")
    excluded = {
        EXCLUDED_INV_TF_SEMANTIC_PATCH_SHA256,
        EXCLUDED_INV_TF_SYNTACTIC_PATCH_SHA256,
    }
    if excluded.intersection(hashes):
        raise EvidenceError("E_PATCH_IDENTITY", "INV/TF patch was reused")
    if patches[INV_SI_SLOT_ID]["semantic"]["target"] != "    return Array._new(L.T)\n":
        raise EvidenceError("E_PATCH_IDENTITY", "INV/SI semantic is not the SI transpose")
    if (
        patches[CMP_TF_SLOT_ID]["semantic"]["patch_sha256"]
        == patches[CMP_SI_SLOT_ID]["semantic"]["patch_sha256"]
    ):
        raise EvidenceError("E_PATCH_IDENTITY", "CMP/TF and CMP/SI share a semantic patch")
    return {"uniqueness": True, "slots": certified_slots}


def _source_text_for_certify(selection: Mapping[str, Any]) -> str:
    stored = selection.get("source_text")
    if isinstance(stored, str) and stored:
        return stored
    repo_root = selection.get("repo_root") or Path.cwd()
    return read_frozen_source(
        repo_root, selection["source_path"], selection["source_sha256"]
    )


def prepare_batch_roots(runtime_root: str | Path, output_root: str | Path) -> None:
    runtime = Path(runtime_root)
    output = Path(output_root)
    staging = output.with_name(output.name + ".staging")
    if _same_or_nested(runtime, QUALIFICATION_RUNTIME_ROOT):
        raise EvidenceError("E_PRESERVED_ROOT", "refusing to reuse qualification runtime")
    if runtime.exists():
        raise EvidenceError("E_BATCH_OUTPUT", "runtime root already exists")
    if output.exists():
        raise EvidenceError("E_BATCH_OUTPUT", "output root already exists")
    if staging.exists():
        raise EvidenceError("E_BATCH_OUTPUT", "staging root already exists")
    runtime.mkdir(parents=True, exist_ok=False)


def reduce_batch_mutant(observations: Mapping[str, Mapping[str, Any]]) -> str | None:
    rows = list(observations.values())
    if any(row.get("observation_class") in _STUB_CLASSES for row in rows):
        return None
    return reduce_scientific_result(observations)


def run_isolated_cell(
    *,
    interpreter: str | Path,
    runtime_root: str | Path,
    source_text: str,
    input_id: str,
    payload: object,
    variant: str,
    family_mechanism: str,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    script = _CMP_CELL_SCRIPT if family_mechanism.startswith("CMP/") else _INV_CELL_SCRIPT
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
            [str(interpreter), "-I", "-c", script],
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
        detail = getattr(result, "stderr", None) or getattr(result, "stdout", None) or ""
        text = str(detail)
        infra = any(
            token in text.lower() for token in ("import", "ambient", "escape", "numpy")
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
    variants: Mapping[str, Mapping[str, str]],
    families: Mapping[str, str],
    cell_runner: Callable[..., Mapping[str, Any]] | None = None,
) -> Callable[[str, str, str, object], Mapping[str, Any]]:
    run_cell = run_isolated_cell if cell_runner is None else cell_runner

    def executor(
        slot_id: str, variant: str, input_id: str, payload: object
    ) -> Mapping[str, Any]:
        return run_cell(
            interpreter=interpreter,
            runtime_root=runtime_root,
            source_text=variants[slot_id][variant],
            input_id=input_id,
            payload=payload,
            variant=variant,
            family_mechanism=families[slot_id],
        )

    return executor


def _reject_selectors(argv: Sequence[str]) -> None:
    if not argv:
        return
    flag = argv[0].split("=", 1)[0]
    if flag in _SELECTOR_FLAGS or flag.startswith("--"):
        raise EvidenceError("E_BATCH_SELECTOR", "selector arguments are rejected")
    raise EvidenceError("E_BATCH_SELECTOR", "arguments are rejected")


def _validate_record(record: Mapping[str, Any]) -> None:
    missing = _RECORD_REQUIRED.difference(record)
    if missing:
        raise EvidenceError("E_BATCH_RECORD", f"record missing {sorted(missing)}")
    if record["batch_version"] != BATCH_VERSION:
        raise EvidenceError("E_BATCH_RECORD", "batch_version differs")
    if record["not_prior_runner_retry"] is not True:
        raise EvidenceError("E_BATCH_RECORD", "not_prior_runner_retry is not true")
    if record["prior_result_disclosed"] is not True:
        raise EvidenceError("E_BATCH_RECORD", "prior_result_disclosed is not true")
    if record["cell_count"] != 45:
        raise EvidenceError("E_BATCH_RECORD", "cell_count is not 45")
    if record["cell_timeout_sec"] != CELL_TIMEOUT_SEC:
        raise EvidenceError("E_BATCH_RECORD", "cell_timeout_sec differs")
    if list(record["per_slot"]) != list(SLOT_ORDER):
        raise EvidenceError("E_BATCH_RECORD", "slot order differs")
    if len(record["patches"]) != 6:
        raise EvidenceError("E_BATCH_RECORD", "patch count differs")
    spec_by_slot = {spec["slot_id"]: spec for spec in _SLOT_SPECS}
    for slot_id, slot_record in record["per_slot"].items():
        terminals = slot_record["per_input_terminals"]
        if list(terminals) != list(VARIANTS):
            raise EvidenceError("E_BATCH_RECORD", "variants differ")
        expected_inputs = list(spec_by_slot[slot_id]["input_ids"])
        for variant in VARIANTS:
            cells = terminals[variant]
            if list(cells) != expected_inputs:
                raise EvidenceError("E_BATCH_RECORD", "cell input order differs")
            for input_id, cell in cells.items():
                for key in _CELL_REQUIRED:
                    if key not in cell:
                        raise EvidenceError("E_BATCH_RECORD", f"cell missing {key}")
                if cell["variant"] != variant or cell["input_id"] != input_id:
                    raise EvidenceError("E_BATCH_RECORD", "cell identity differs")
    body = {key: value for key, value in record.items() if key != "artifact_sha256"}
    if record["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_BATCH_RECORD", "artifact self-hash differs")


def run_remaining_three_paired_batch_once(
    repo_root: str | Path | None = None,
    *,
    runtime_root: str | Path | None = None,
    output_root: str | Path | None = None,
    qualification_path: str | Path | None = None,
    qualification_runtime: str | Path | None = None,
    prior_output_path: str | Path | None = None,
    expected_qualification_commit: str | None = None,
    executor: Callable[[str, str, str, object], Mapping[str, Any]] | None = None,
    import_probe: Callable[[str], Mapping[str, Any]] | None = None,
    cell_runner: Callable[..., Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    prior_path = (
        Path(prior_output_path)
        if prior_output_path is not None
        else prior_inv_tf_path(root)
    )
    qual_path = (
        Path(qualification_path)
        if qualification_path is not None
        else root / "data/p3_v3/phase3/ordinal8-controlled-numpy-runtime/qualification.json"
    )
    qual_runtime = (
        Path(qualification_runtime)
        if qualification_runtime is not None
        else QUALIFICATION_RUNTIME_ROOT
    )
    runtime = Path(runtime_root) if runtime_root is not None else FORMAL_RUNTIME_ROOT
    output = (
        Path(output_root)
        if output_root is not None
        else root / FORMAL_OUTPUT_ROOT_RELATIVE
    )
    if _same_or_nested(runtime, QUALIFICATION_RUNTIME_ROOT):
        raise EvidenceError("E_PRESERVED_ROOT", "refusing to reuse a frozen runtime")
    design = root / PREREGISTRATION_RELATIVE
    if file_sha256(design) != PREREGISTRATION_FILE_SHA256:
        raise EvidenceError("E_PREREGISTRATION", "preregistration file SHA-256 differs")
    _verify_commit_ancestor(root, EVIDENCE_COMMIT, "E_EVIDENCE_COMMIT")
    _verify_commit_ancestor(root, PREREGISTRATION_COMMIT, "E_PREREGISTRATION")
    verify_prior_inv_tf_evidence(prior_path)
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
        probe_controlled_imports(identity["interpreter"], qual_runtime)
    gitlinks = verify_recovered_gitlinks(qualification, qual_runtime)
    prepare_batch_roots(runtime, output)
    selections = bind_remaining_three_slots(root)
    for selection in selections:
        selection["repo_root"] = str(root)
        selection["source_text"] = read_frozen_source(
            root, selection["source_path"], selection["source_sha256"]
        )
    patches = generate_slot_patches(root, selections)
    certification = certify_remaining_patches(selections, patches)
    variants = {
        selection["slot_id"]: {
            "original": selection["source_text"],
            "semantic": apply_named_patch(
                selection["source_text"], patches[selection["slot_id"]]["semantic"]
            ),
            "syntactic": apply_named_patch(
                selection["source_text"], patches[selection["slot_id"]]["syntactic"]
            ),
        }
        for selection in selections
    }
    families = {
        selection["slot_id"]: selection["family_mechanism"] for selection in selections
    }
    exec_fn = executor
    if exec_fn is None:
        exec_fn = _make_controlled_executor(
            interpreter=identity["interpreter"],
            runtime_root=qual_runtime,
            variants=variants,
            families=families,
            cell_runner=cell_runner,
        )
    per_slot: dict[str, Any] = {}
    cell_count = 0
    for selection in selections:
        slot_id = selection["slot_id"]
        terminals: dict[str, dict[str, Any]] = {variant: {} for variant in VARIANTS}
        rows_by_id = {row["input_id"]: row for row in selection["rows"]}
        for variant in VARIANTS:
            for input_id in selection["input_ids"]:
                row = rows_by_id[input_id]
                observation = dict(
                    exec_fn(slot_id, variant, input_id, row["envelope"]["payload"])
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
                observation.setdefault("observation_class", "REAL_SCIENTIFIC")
                terminals[variant][input_id] = observation
                cell_count += 1
        per_slot[slot_id] = {
            "contract_id": selection["contract_id"],
            "family_mechanism": selection["family_mechanism"],
            "frozen_input_aggregate_sha256": selection["frozen_input_aggregate_sha256"],
            "input_ids": list(selection["input_ids"]),
            "inventory_artifact_sha256": selection["inventory_artifact_sha256"],
            "per_input_terminals": terminals,
            "per_mutant": {
                name: {
                    "observations": [
                        {"input_id": input_id, **dict(terminals[name][input_id])}
                        for input_id in selection["input_ids"]
                    ],
                    "scientific_result": reduce_batch_mutant(terminals[name]),
                }
                for name in ("semantic", "syntactic")
            },
            "site_id": selection["site_id"],
            "slot_id": slot_id,
        }
    patch_rows = []
    for selection in selections:
        slot_id = selection["slot_id"]
        for kind in ("semantic", "syntactic"):
            patch_rows.append(
                {
                    "kind": kind,
                    "slot_id": slot_id,
                    **dict(patches[slot_id][kind]),
                }
            )
    body = {
        "batch_runner_sha256": file_sha256(Path(__file__)),
        "batch_version": BATCH_VERSION,
        "c3_status": C3_STATUS,
        "cell_count": cell_count,
        "cell_timeout_sec": CELL_TIMEOUT_SEC,
        "controlled_runtime": {
            "array_api_file": identity["array_api_file"],
            "interpreter": identity["interpreter"],
            "numpy_file": identity["numpy_file"],
            "numpy_version": identity["numpy_version"],
            "prefix": identity["prefix"],
            "recovered_gitlink_identity": gitlinks,
            "root": identity["root"],
        },
        "evidence_commit": EVIDENCE_COMMIT,
        "forbidden_consumed_clis": list(FORBIDDEN_CONSUMED_CLIS),
        "implementation_commit": _head_commit(root),
        "not_prior_runner_retry": True,
        "patches": patch_rows,
        "per_slot": per_slot,
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "preregistration_file_sha256": PREREGISTRATION_FILE_SHA256,
        "prior_inv_tf_artifact_sha256": PRIOR_INV_TF_ARTIFACT_SHA256,
        "prior_inv_tf_commit": PRIOR_INV_TF_COMMIT,
        "prior_inv_tf_disclosure": {
            "binary_kill_rate_difference": 0,
            "not_used_to_revise_remaining_design": True,
            "original": "5/5 SURVIVE",
            "semantic": "5/5 KILL",
            "syntactic": "5/5 KILL",
        },
        "prior_inv_tf_file_sha256": PRIOR_INV_TF_FILE_SHA256,
        "prior_result_disclosed": True,
        "qualification_artifact_sha256": QUALIFICATION_ARTIFACT_SHA256,
        "qualification_commit": QUALIFICATION_COMMIT,
        "qualification_file_sha256": QUALIFICATION_FILE_SHA256,
        "schema_version": SCHEMA_VERSION,
        "slots": [
            {
                "contract_id": selection["contract_id"],
                "family_mechanism": selection["family_mechanism"],
                "frozen_input_aggregate_sha256": selection[
                    "frozen_input_aggregate_sha256"
                ],
                "input_ids": list(selection["input_ids"]),
                "inventory_artifact_sha256": selection["inventory_artifact_sha256"],
                "qualified_name": selection["qualified_name"],
                "site_id": selection["site_id"],
                "site_span": selection["site_span"],
                "slot_id": selection["slot_id"],
                "source_path": selection["source_path"],
            }
            for selection in selections
        ],
        "static_certification": certification,
        "task_id": TASK_ID,
    }
    record = {**body, "artifact_sha256": canonical_sha256(body)}
    _validate_record(record)
    staging = output.with_name(output.name + ".staging")
    staging.mkdir(parents=True, exist_ok=False)
    write_canonical_json(staging / "paired-batch.json", record, exclusive=True)
    os.replace(staging, output)
    return record


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    _reject_selectors(args)
    run_remaining_three_paired_batch_once()
    return 0
