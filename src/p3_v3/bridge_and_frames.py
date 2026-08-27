"""Pinned P12 bridge verification and deterministic P3 subject frames."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import io
import json
import re
import socket
import subprocess
import sys
import threading
import uuid
from collections.abc import Callable, Mapping, Sequence
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any

from .artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    read_canonical_regular_bytes,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
)

_GIT_OID_RE = re.compile(r"[0-9a-f]{40}")
_SCALE_ORDER = ("S", "M", "L")
_TECHNIQUE_ORDER = (
    "HYBRID_NATIVE",
    "TENSOR_AUTODIFF",
    "PROBABILISTIC_SURROGATE",
    "ITERATIVE_STOCHASTIC",
    "ARRAY_NUMERICAL",
    "SCALAR_CONTROL",
    "TECH_UNCERTAIN",
)
_SCALES = set(_SCALE_ORDER)
_TECHNIQUES = set(_TECHNIQUE_ORDER)


@dataclass(frozen=True)
class _VerifiedImplementationSnapshot:
    logical_filename: str
    source_sha256: str
    source_bytes: bytes


@dataclass(frozen=True)
class SourceSnapshotEntry:
    """One explicit regular-file value captured by an authority boundary."""

    relative_path: str
    mode: str
    sha256: str
    content: bytes


@dataclass(frozen=True)
class SourceSnapshot:
    """Immutable source values; possession does not itself confer authority."""

    entries: tuple[SourceSnapshotEntry, ...]

    def read_bytes(self, relative_path: str) -> bytes:
        entries = _validate_source_snapshot(self)
        try:
            return entries[safe_relative_path(relative_path).as_posix()].content
        except (KeyError, EvidenceError) as exc:
            raise EvidenceError(
                "E_SOURCE_SNAPSHOT", f"source snapshot path is absent: {relative_path}"
            ) from exc

    def read_text(self, relative_path: str) -> str:
        try:
            return self.read_bytes(relative_path).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise EvidenceError(
                "E_SOURCE_SNAPSHOT", f"source snapshot path is not UTF-8: {relative_path}"
            ) from exc


def _validate_source_snapshot(
    snapshot: SourceSnapshot,
) -> dict[str, SourceSnapshotEntry]:
    """Revalidate every explicit value at each source-consuming seam."""

    if type(snapshot) is not SourceSnapshot or type(snapshot.entries) is not tuple:
        raise EvidenceError("E_SOURCE_SNAPSHOT", "source snapshot schema differs")
    validated: dict[str, SourceSnapshotEntry] = {}
    ordered_paths: list[str] = []
    for index, entry in enumerate(snapshot.entries):
        if type(entry) is not SourceSnapshotEntry:
            raise EvidenceError(
                "E_SOURCE_SNAPSHOT", f"source snapshot entry {index} schema differs"
            )
        if type(entry.relative_path) is not str:
            raise EvidenceError(
                "E_SOURCE_SNAPSHOT", f"source snapshot entry {index} value differs"
            )
        try:
            canonical_path = safe_relative_path(entry.relative_path).as_posix()
            validate_sha256(entry.sha256, f"source snapshot entry {index} sha256")
        except EvidenceError as exc:
            raise EvidenceError(
                "E_SOURCE_SNAPSHOT", f"source snapshot entry {index} value differs"
            ) from exc
        if (
            canonical_path != entry.relative_path
            or type(entry.mode) is not str
            or entry.mode not in {"100644", "100755"}
            or type(entry.sha256) is not str
            or type(entry.content) is not bytes
        ):
            raise EvidenceError(
                "E_SOURCE_SNAPSHOT", f"source snapshot entry {index} value differs"
            )
        if hashlib.sha256(entry.content).hexdigest() != entry.sha256:
            raise EvidenceError(
                "E_SOURCE_SNAPSHOT", f"source snapshot entry {index} digest differs"
            )
        if entry.relative_path in validated:
            raise EvidenceError("E_SOURCE_SNAPSHOT", "source snapshot paths duplicate")
        validated[entry.relative_path] = entry
        ordered_paths.append(entry.relative_path)
    if ordered_paths != sorted(
        ordered_paths, key=lambda value: value.encode("utf-8")
    ):
        raise EvidenceError(
            "E_SOURCE_SNAPSHOT", "source snapshot paths are not sorted"
        )
    return validated


_VERIFIED_EXECUTION_LOCK = threading.RLock()
_BLOCKED_SOCKET_ATTRIBUTES = (
    "create_connection",
    "getaddrinfo",
    "getfqdn",
    "gethostbyaddr",
    "gethostbyname",
    "gethostbyname_ex",
    "getnameinfo",
    "socket",
    "socketpair",
)

PROFILING_BUDGETS = {"S": 10, "M": 15, "L": 20}
BEHAVIOR_CATEGORY_ORDER = [
    "PUBLIC_API",
    "CLI",
    "EXAMPLE",
    "BENCHMARK",
    "PROJECT_TEST",
]
CONFIRMATORY_ADAPTERS = {
    "PYTHON_PEP517_V1",
    "CMAKE_CTEST_V1",
    "MESON_TEST_V1",
    "AUTOTOOLS_MAKECHECK_V1",
}
_ADAPTER_ECOSYSTEMS = {
    "PYTHON_PEP517_V1": "python",
    "CMAKE_CTEST_V1": "cmake",
    "MESON_TEST_V1": "meson",
    "AUTOTOOLS_MAKECHECK_V1": "autotools",
}
_BEHAVIOR_CATEGORIES = set(BEHAVIOR_CATEGORY_ORDER)
_PROFILE_TECHNIQUES = tuple(
    technique for technique in _TECHNIQUE_ORDER if technique != "TECH_UNCERTAIN"
)
_UNRESOLVED_STATUSES = frozenset(
    {"FAILURE", "TIMEOUT", "MISSING_TRACE", "ADAPTER_UNCERTAIN"}
)
PHASE1_UNEXECUTED_RUNNER_SHA256 = (
    "978fa53c66ae15f9c51b5fa73dc03afdb2d23448f7714d752bccf92c09503ad0"
)
_TRACE_CALL_KINDS = frozenset(
    {
        "PYTHON_CALL",
        "FUNCTION_CALL",
        "METHOD_CALL",
        "NATIVE_CALL",
        "FFI_CALL",
        "PROCESS_SPAWN",
    }
)
_NATIVE_CALL_KINDS = frozenset({"NATIVE_CALL", "FFI_CALL", "PROCESS_SPAWN"})
_TENSOR_MODULE_PREFIXES = ("torch", "tensorflow", "jax", "autograd")
_PROBABILISTIC_MODULE_PREFIXES = (
    "pymc",
    "pyro",
    "sklearn.gaussian_process",
    "scipy.stats",
    "statsmodels",
)
_ITERATIVE_MODULE_PREFIXES = ("scipy.optimize", "scipy.integrate", "emcee")
_ARRAY_MODULE_PREFIXES = ("numpy", "scipy.linalg", "scipy.sparse", "cupy")
_TENSOR_SYMBOL_TOKENS = frozenset(
    {"autodiff", "backprop", "backward", "gradient", "tensor"}
)
_PROBABILISTIC_SYMBOL_TOKENS = frozenset(
    {
        "bayes",
        "distribution",
        "gaussian",
        "inference",
        "logprob",
        "posterior",
        "predict",
    }
)
_ITERATIVE_SYMBOL_TOKENS = frozenset(
    {"iterate", "minimize", "optimize", "sample", "simulate", "step", "trajectory"}
)
_ARRAY_SYMBOL_TOKENS = frozenset(
    {"array", "dot", "linalg", "matmul", "matrix", "solve", "sparse", "vector"}
)
P12_OUTCOME_STATES = [
    "MR_VIOLATION",
    "MR_SATISFIED",
    "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
    "SCIENTIFIC_INCONCLUSIVE",
    "INFRASTRUCTURE_UNRESOLVED",
]
P12_PRIMARY_ESTIMAND = "INTENTION_TO_EVALUATE_LOWER_BOUND"
INFRASTRUCTURE_RETRY_LIMIT = 3
E_COMMON_COUNT = 30
E_CONTRACT_COUNT = 5
E_COMMON_GENERATOR_IDS = (
    "JSON_SCHEMA_DRAFT2020_12_V1",
    "CLI_TOKEN_GRAMMAR_V1",
    "NUMERIC_ARRAY_DOMAIN_V1",
    "TEXT_IO_SCHEMA_V1",
    "BINARY_RECORD_SCHEMA_V1",
)
E_CONTRACT_GENERATOR_IDS = (
    "CONTRACT_ENUM_DOMAIN_V1",
    "CONTRACT_NUMERIC_DOMAIN_V1",
    "CONTRACT_ARRAY_DOMAIN_V1",
    "CONTRACT_SEQUENCE_DOMAIN_V1",
    "CONTRACT_RELATION_PAIR_DOMAIN_V1",
)
_E_COMMON_GENERATOR_ID_SET = set(E_COMMON_GENERATOR_IDS)
_E_CONTRACT_GENERATOR_ID_SET = set(E_CONTRACT_GENERATOR_IDS)
APPLICABLE_SLOT_CHRONOLOGY = (
    "SITE_FROZEN",
    "CONTRACT_FROZEN",
    "E_CONTRACT_FROZEN",
    "PATCH_FROZEN",
    "CERTIFICATION_WITNESS_SELECTED",
    "TERMINAL_STATE",
)
NOT_APPLICABLE_SLOT_CHRONOLOGY = ("APPLICABILITY_CLOSED_NOT_APPLICABLE",)
UNAVAILABLE_NOT_CLAIMED = "UNAVAILABLE_NOT_CLAIMED"
_PROPOSAL_SCHEMA = {
    "schema_version": str,
    "provider_model": str,
    "prompt_sha256": str,
    "context_sha256": str,
    "response_sha256": str,
    "timestamp_utc": str,
    "exposed_generation_metadata": dict,
    "temperature": str,
    "seed": str,
    "top_p": str,
}
_PROPOSAL_UNAVAILABLE_FIELDS = ("temperature", "seed", "top_p")
_SCHEMA_ALIAS_KEYS = frozenset(
    {"subject_alias", "project_alias", "controlled_subject_source_id"}
)
_FORBIDDEN_GENERATOR_INPUT_KEYS = frozenset(
    {
        "project_test_body",
        "project_test_bodies",
        "project_test_fixture",
        "project_test_fixtures",
        "fixture_body",
        "test_fixture",
        "test_fixtures",
        "contract",
        "contracts",
        "site",
        "sites",
        "profiling_result",
        "profiling_results",
        "patch",
        "patches",
        "mr",
        "mrs",
        "evaluated_mr",
        "evaluated_mrs",
        "p12",
        "p12_identity",
        "p12_identities",
        "p12_fault_id",
        "outcome",
        "outcomes",
        "mr_outcome",
        "kill_outcome",
        "execution_outcome",
    }
)

_PROTOCOL_SCHEMA = {
    "schema_version": str,
    "scientific_plan_sha256": str,
    "evidence_design_sha256": str,
    "claims_initial_status": str,
    "rq_spec_sha256": str,
    "claim_ceiling_sha256": str,
    "p12_contract_sha256": str,
    "operator_catalogue_sha256": str,
    "adapter_registry_sha256": str,
    "input_generator_registry_sha256": str,
    "mr_policy_sha256": str,
    "site_policy_sha256": str,
    "analysis_spec_sha256": str,
    "package_policy_sha256": str,
    "environment_lock_sha256": str,
    "profiling_budgets": dict,
    "behavior_category_order": list,
    "technique_order": list,
    "e_common_count": int,
    "e_contract_count": int,
    "p12_outcome_states": list,
    "p12_primary_estimand": str,
    "infrastructure_retry_limit": int,
    "artifact_sha256": str,
}
_PROTOCOL_HASH_FIELDS = (
    "scientific_plan_sha256",
    "evidence_design_sha256",
    "rq_spec_sha256",
    "claim_ceiling_sha256",
    "p12_contract_sha256",
    "operator_catalogue_sha256",
    "adapter_registry_sha256",
    "input_generator_registry_sha256",
    "mr_policy_sha256",
    "site_policy_sha256",
    "analysis_spec_sha256",
    "package_policy_sha256",
    "environment_lock_sha256",
)
_MR_CANDIDATE_FRAME_SCHEMA = {
    "schema_version": str,
    "artifact_type": str,
    "candidate_mr_ids": list,
    "artifact_sha256": str,
}
_MR_CUSTODIAN_RECEIPT_SCHEMA = {
    "schema_version": str,
    "artifact_type": str,
    "candidate_frame_sha256": str,
    "receipt_state": str,
    "admitted_mr_ids": list,
    "excluded_mr_ids": list,
    "artifact_sha256": str,
}
_MR_FINAL_INVENTORY_SCHEMA = {
    "schema_version": str,
    "artifact_type": str,
    "custodian_receipt_sha256": str,
    "mr_ids": list,
    "artifact_sha256": str,
}
_MR_PORTFOLIOS_SCHEMA = {
    "schema_version": str,
    "artifact_type": str,
    "final_inventory_sha256": str,
    "portfolios": list,
    "artifact_sha256": str,
}
_MR_PORTFOLIO_SCHEMA = {
    "portfolio_id": str,
    "mr_ids": list,
}

_LOCK_SCHEMA = {
    "repository_identity": str,
    "release_commit_sha": str,
    "bridge_path": str,
    "bridge_blob_sha": str,
    "contract_path": str,
    "contract_blob_sha": str,
    "package_root_sha256": str,
}
_BRIDGE_SCHEMA = {
    "schema_version": str,
    "p12_release_id": str,
    "p12_repository_identity": str,
    "p12_contract_path": str,
    "p12_contract_blob_sha": str,
    "p12_package_root_sha256": str,
    "p12_contract_sha256": str,
    "eligible_inventory_root_sha256": str,
    "eligible_item_count": int,
    "records": list,
    "trust_mode": str,
    "artifact_sha256": str,
}
_RECORD_SCHEMA = {
    "neutral_snapshot_id": str,
    "fixed_tree_commitment": str,
    "normalized_source_tree_sha256": str,
    "source_archive_sha256": str,
    "build_descriptor_sha256": str,
    "eligibility_reason": str,
    "eligible_for_construct": bool,
    "eligible_for_criterion": bool,
}
_SUBJECT_SPEC_SCHEMA = {
    "neutral_snapshot_id": str,
    "source_snapshot": SourceSnapshot,
    "source_record": dict,
    "build_descriptor": dict,
    "adapter_registry": dict,
    "input_generator_registry": dict,
    "profiling_results": dict,
}
_SUBJECT_PROFILE_SCHEMA = {
    "controlled_subject_id": str,
    "normalized_source_tree_sha256": str,
    "build_descriptor_sha256": str,
    "public_workload_set_sha256": str,
    "scale_class": str,
    "primary_technique": str,
    "technique_vector": list,
    "sites": list,
    "neutral_snapshot_ids": list,
}
_DERIVED_SUBJECT_SCHEMA = {
    "neutral_snapshot_id": str,
    "controlled_subject_source_id": str,
    "adapter_discovery": dict,
    "adapter_discovery_sha256": str,
    "source_scale": dict,
    "source_scale_sha256": str,
    "public_behavior_frame": dict,
    "public_behavior_frame_sha256": str,
    "profiling_workload": dict,
    "profiling_workload_sha256": str,
    "common_inputs": dict,
    "common_inputs_sha256": str,
    "profiling_results": dict,
    "profiling_results_sha256": str,
    "technique_profile": dict,
    "technique_profile_sha256": str,
    "subject": dict,
    "artifact_sha256": str,
}
_INDEXED_SUBJECT_REBUILD_SCHEMA = {
    "source_snapshot": SourceSnapshot,
    "source_record": dict,
    "build_descriptor": dict,
    "adapter_registry": dict,
    "input_generator_registry": dict,
    "profiling_results": dict,
    "adapter_discovery": dict,
    "source_scale": dict,
    "public_frame": dict,
    "profiling_workload": dict,
    "common_inputs": dict,
    "technique_profile": dict,
    "sites": list,
    "subject": dict,
}
_SITE_SCHEMA = {
    "path": str,
    "symbol": str,
    "start_line": int,
    "start_col": int,
    "end_line": int,
    "end_col": int,
}
_CANONICAL_SITE_SCHEMA = {**_SITE_SCHEMA, "site_id": str}
_REVEAL_SCHEMA = {
    "neutral_snapshot_id": str,
    "fixed_git_tree_oid": str,
    "reveal_nonce": str,
    "normalized_source_tree_sha256": str,
}
_ADAPTER_ENTRY_SCHEMA = {
    "adapter_id": str,
    "ecosystem": str,
    "implementation_path": str,
    "source_sha256": str,
}
_ADAPTER_REGISTRY_SCHEMA = {
    "schema_version": str,
    "adapters": list,
    "artifact_sha256": str,
}
_ADAPTER_RESULT_SCHEMA = {
    "adapter_id": str,
    "ecosystem": str,
    "source_files": list,
    "declarations": list,
    "public_schemas": list,
    "sites": list,
}
_ADAPTER_DISCOVERY_SCHEMA = {
    "schema_version": str,
    "adapter_id": (str, type(None)),
    "ecosystem": str,
    "discovery_status": str,
    "implementation_source_sha256": (str, type(None)),
    "source_files": list,
    "declarations": list,
    "public_schemas": list,
    "sites": list,
    "unsupported_or_exclusion_reason": str,
    "artifact_sha256": str,
}
_SOURCE_RECORD_SCHEMA = {
    "normalized_source_tree_sha256": str,
    "build_descriptor_sha256": str,
}
_PROFILING_RESULT_SCHEMA = {
    "behavior_id": str,
    "status": str,
    "argv": list,
    "input_sha256": list,
    "environment_sha256": str,
    "runner_version": str,
    "exit_code": (int, type(None)),
    "stdout_sha256": str,
    "stderr_sha256": str,
    "call_trace": list,
    "call_trace_sha256": str,
    "timed_out": bool,
    "failure_code": str,
    "observed_site_ids": list,
}
_CALL_TRACE_EVENT_SCHEMA = {
    "sequence": int,
    "module": str,
    "symbol": str,
    "call_kind": str,
    "argument_types": list,
    "keyword_names": list,
}
_PROFILING_RECEIPT_SCHEMA = {
    "schema_version": str,
    "neutral_snapshot_id": str,
    "controlled_subject_source_id": str,
    "normalized_source_tree_sha256": str,
    "build_descriptor_sha256": str,
    "profiling_workload_sha256": str,
    "adapter_implementation_source_sha256": (str, type(None)),
    "runner_implementation_source_sha256": str,
    "results": list,
    "artifact_sha256": str,
}
_GENERATOR_ENTRY_SCHEMA = {
    "generator_id": str,
    "schema_kind": str,
    "implementation_path": str,
    "source_sha256": str,
    "output_schema": dict,
    "failure_code": str,
}
_GENERATOR_REGISTRY_SCHEMA = {
    "schema_version": str,
    "generators": list,
    "artifact_sha256": str,
}
_SLOT_SCHEMA = {
    "slot_id": str,
    "controlled_subject_id": str,
}
_CONTRACT_SCHEMA = {
    "contract_id": str,
    "generator_id": str,
    "domain": dict,
    "site_id": str,
}
_SLOT_ARTIFACTS_SCHEMA = {
    "slot_id": str,
    "chronology": list,
    "contract": (dict, type(None)),
    "e_contract": (dict, type(None)),
    "patch": (dict, type(None)),
    "certification_witness": (dict, type(None)),
    "e_common_input_ids": list,
    "e_contract_input_ids": list,
}


def validate_protocol(
    protocol: Mapping[str, Any],
    expected_plan_sha256: str,
    expected_design_sha256: str,
) -> dict[str, Any]:
    value = validate_exact_object(dict(protocol), _PROTOCOL_SCHEMA, "protocol")
    if value["schema_version"] != "p3-protocol-v1":
        raise EvidenceError("E_PROTOCOL", "protocol version differs")
    if value["claims_initial_status"] != "blocked":
        raise EvidenceError("E_PROTOCOL", "claims_initial_status must be blocked")
    for field in _PROTOCOL_HASH_FIELDS:
        validate_sha256(value[field], field)
    validate_sha256(value["artifact_sha256"], "artifact_sha256")
    validate_sha256(expected_plan_sha256, "expected_plan_sha256")
    validate_sha256(expected_design_sha256, "expected_design_sha256")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PROTOCOL_HASH", "protocol canonical self-hash differs")
    if (
        value["scientific_plan_sha256"] != expected_plan_sha256
        or value["evidence_design_sha256"] != expected_design_sha256
    ):
        raise EvidenceError("E_PROTOCOL_AUTHORITY", "protocol authority hashes differ")
    if value["profiling_budgets"] != PROFILING_BUDGETS:
        raise EvidenceError("E_PROTOCOL", "profiling_budgets differ")
    if value["behavior_category_order"] != BEHAVIOR_CATEGORY_ORDER:
        raise EvidenceError("E_PROTOCOL", "behavior_category_order differs")
    if value["technique_order"] != list(_TECHNIQUE_ORDER):
        raise EvidenceError("E_PROTOCOL", "technique_order differs")
    if value["e_common_count"] != E_COMMON_COUNT or value["e_contract_count"] != E_CONTRACT_COUNT:
        raise EvidenceError("E_PROTOCOL_COUNTS", "evaluation input counts differ")
    if value["p12_outcome_states"] != P12_OUTCOME_STATES:
        raise EvidenceError("E_PROTOCOL_OUTCOMES", "p12_outcome_states order differs")
    if value["p12_primary_estimand"] != P12_PRIMARY_ESTIMAND:
        raise EvidenceError("E_PROTOCOL", "p12_primary_estimand differs")
    if value["infrastructure_retry_limit"] != INFRASTRUCTURE_RETRY_LIMIT:
        raise EvidenceError("E_PROTOCOL_RETRY", "infrastructure_retry_limit differs")
    return value


def _validate_mr_artifact(
    artifact: Mapping[str, Any],
    schema: Mapping[str, Any],
    context: str,
    expected_schema_version: str,
    expected_artifact_type: str,
) -> dict[str, Any]:
    value = validate_exact_object(dict(artifact), schema, context)
    if value["schema_version"] != expected_schema_version:
        raise EvidenceError(
            "E_MR_SCHEMA_VERSION",
            f"{context} schema version differs",
        )
    if value["artifact_type"] != expected_artifact_type:
        raise EvidenceError(
            "E_MR_ARTIFACT_TYPE",
            f"{context} artifact type differs",
        )
    validate_sha256(value["artifact_sha256"], f"{context}.artifact_sha256")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError(
            "E_MR_ARTIFACT_HASH",
            f"{context} canonical self-hash differs",
        )
    return value


def _validate_mr_ids(value: list[Any], context: str) -> list[str]:
    if any(type(item) is not str or not item for item in value):
        raise EvidenceError("E_MR_MEMBERSHIP", f"{context} contains an invalid MR ID")
    if value != sorted(set(value)):
        raise EvidenceError(
            "E_MR_MEMBERSHIP",
            f"{context} must be sorted and unique",
        )
    return value


def validate_mr_inventory(
    candidate: Mapping[str, Any],
    receipt: Mapping[str, Any],
    final_inventory: Mapping[str, Any],
    portfolios: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    candidate_value = _validate_mr_artifact(
        candidate,
        _MR_CANDIDATE_FRAME_SCHEMA,
        "mr_candidate_frame",
        "p3-mr-candidate-frame-v1",
        "MR_CANDIDATE_FRAME",
    )
    receipt_value = _validate_mr_artifact(
        receipt,
        _MR_CUSTODIAN_RECEIPT_SCHEMA,
        "mr_custodian_receipt",
        "p3-mr-custodian-receipt-v1",
        "MR_CUSTODIAN_RECEIPT",
    )
    inventory_value = _validate_mr_artifact(
        final_inventory,
        _MR_FINAL_INVENTORY_SCHEMA,
        "mr_final_inventory",
        "p3-mr-final-inventory-v1",
        "MR_FINAL_INVENTORY",
    )
    portfolios_value = _validate_mr_artifact(
        portfolios,
        _MR_PORTFOLIOS_SCHEMA,
        "mr_portfolios",
        "p3-mr-portfolios-v1",
        "MR_PORTFOLIOS",
    )

    candidate_ids = _validate_mr_ids(
        candidate_value["candidate_mr_ids"],
        "mr_candidate_frame.candidate_mr_ids",
    )
    admitted_ids = _validate_mr_ids(
        receipt_value["admitted_mr_ids"],
        "mr_custodian_receipt.admitted_mr_ids",
    )
    excluded_ids = _validate_mr_ids(
        receipt_value["excluded_mr_ids"],
        "mr_custodian_receipt.excluded_mr_ids",
    )
    if receipt_value["receipt_state"] != "CLOSED":
        raise EvidenceError(
            "E_MR_RECEIPT_STATE",
            "custodian receipt must fail closed before inventory freeze",
        )
    if (
        set(admitted_ids) & set(excluded_ids)
        or sorted(admitted_ids + excluded_ids) != candidate_ids
    ):
        raise EvidenceError(
            "E_MR_RECEIPT_MEMBERSHIP",
            "custodian receipt must partition every candidate exactly once",
        )

    inventory_ids = _validate_mr_ids(
        inventory_value["mr_ids"],
        "mr_final_inventory.mr_ids",
    )
    if inventory_ids != admitted_ids:
        raise EvidenceError(
            "E_MR_INVENTORY_MEMBERSHIP",
            "final inventory must contain exactly the admitted MR IDs",
        )

    portfolio_rows: list[dict[str, Any]] = []
    for index, row in enumerate(portfolios_value["portfolios"]):
        portfolio = validate_exact_object(
            row,
            _MR_PORTFOLIO_SCHEMA,
            f"mr_portfolios.portfolios[{index}]",
        )
        if not portfolio["portfolio_id"]:
            raise EvidenceError("E_MR_PORTFOLIO", "portfolio ID must be nonempty")
        _validate_mr_ids(
            portfolio["mr_ids"],
            f"mr_portfolios.portfolios[{index}].mr_ids",
        )
        if not set(portfolio["mr_ids"]).issubset(inventory_ids):
            raise EvidenceError(
                "E_MR_PORTFOLIO_MEMBERSHIP",
                "every portfolio MR must belong to the final inventory",
            )
        portfolio_rows.append(portfolio)
    portfolio_ids = [row["portfolio_id"] for row in portfolio_rows]
    if portfolio_ids != sorted(set(portfolio_ids)):
        raise EvidenceError(
            "E_MR_PORTFOLIO",
            "portfolio IDs must be sorted and unique",
        )

    parent_links = (
        (
            receipt_value["candidate_frame_sha256"],
            candidate_value["artifact_sha256"],
        ),
        (
            inventory_value["custodian_receipt_sha256"],
            receipt_value["artifact_sha256"],
        ),
        (
            portfolios_value["final_inventory_sha256"],
            inventory_value["artifact_sha256"],
        ),
    )
    for child_parent, expected_parent in parent_links:
        validate_sha256(child_parent, "mr parent reference")
        if child_parent != expected_parent:
            raise EvidenceError("E_MR_PARENT", "MR artifact parent hash differs")

    return {
        "candidate": candidate_value,
        "receipt": receipt_value,
        "final_inventory": inventory_value,
        "portfolios": portfolios_value,
    }


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        shell=False,
        check=False,
    )
    if result.returncode != 0:
        raise EvidenceError("E_PINNED_GIT", f"git {' '.join(args)} failed")
    return result.stdout


def _git_oid(value: Any, field: str) -> str:
    if not isinstance(value, str) or _GIT_OID_RE.fullmatch(value) is None:
        raise EvidenceError("E_GIT_OID", f"{field} must be 40 lowercase hexadecimal characters")
    return value


def _canonical_document(raw: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("E_BRIDGE_JSON", f"{context} is not valid JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise EvidenceError("E_BRIDGE_CANONICAL", f"{context} is not canonical JSON")
    return value


def _neutral_snapshot_id(record: Mapping[str, Any], package_root: str) -> str:
    return canonical_sha256(
        {
            "p12_package_root_sha256": package_root,
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "source_archive_sha256": record["source_archive_sha256"],
            "domain": "P3-NEUTRAL-SNAPSHOT-v1",
        }
    )


def validate_bridge_document(bridge: dict[str, Any], consumer_lock: Mapping[str, Any]) -> dict:
    lock = validate_exact_object(dict(consumer_lock), _LOCK_SCHEMA, "consumer_lock")
    _git_oid(lock["release_commit_sha"], "consumer_lock.release_commit_sha")
    _git_oid(lock["bridge_blob_sha"], "consumer_lock.bridge_blob_sha")
    _git_oid(lock["contract_blob_sha"], "consumer_lock.contract_blob_sha")
    safe_relative_path(lock["bridge_path"])
    safe_relative_path(lock["contract_path"])
    validate_sha256(lock["package_root_sha256"], "consumer_lock.package_root_sha256")

    validate_exact_object(bridge, _BRIDGE_SCHEMA, "bridge")
    if bridge["schema_version"] != "p3-p12-bridge-v1":
        raise EvidenceError("E_BRIDGE_VERSION", "unsupported bridge schema")
    if bridge["trust_mode"] != "PINNED_GIT_RELEASE":
        raise EvidenceError("E_BRIDGE_TRUST", "bridge trust mode is not pinned Git")
    body = {key: value for key, value in bridge.items() if key != "artifact_sha256"}
    if bridge["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_BRIDGE_HASH", "bridge canonical self-hash differs")
    if (
        bridge["p12_repository_identity"] != lock["repository_identity"]
        or bridge["p12_contract_path"] != lock["contract_path"]
        or bridge["p12_contract_blob_sha"] != lock["contract_blob_sha"]
        or bridge["p12_package_root_sha256"] != lock["package_root_sha256"]
    ):
        raise EvidenceError("E_BRIDGE_LOCK", "bridge identity differs from consumer lock")
    validate_sha256(bridge["p12_contract_sha256"], "bridge.p12_contract_sha256")
    validate_sha256(
        bridge["eligible_inventory_root_sha256"], "bridge.eligible_inventory_root_sha256"
    )
    records: list[dict[str, Any]] = []
    for index, record in enumerate(bridge["records"]):
        try:
            validate_exact_object(record, _RECORD_SCHEMA, f"bridge.records[{index}]")
        except EvidenceError as exc:
            if exc.code == "E_SCHEMA_KEYS":
                raise EvidenceError("E_BRIDGE_RECORD_KEYS", str(exc)) from exc
            raise
        for field in (
            "neutral_snapshot_id",
            "fixed_tree_commitment",
            "normalized_source_tree_sha256",
            "source_archive_sha256",
            "build_descriptor_sha256",
        ):
            validate_sha256(record[field], f"bridge.records[{index}].{field}")
        if record["neutral_snapshot_id"] != _neutral_snapshot_id(
            record, bridge["p12_package_root_sha256"]
        ):
            raise EvidenceError("E_NEUTRAL_ID", f"record {index} neutral ID differs")
        records.append(record)
    if bridge["eligible_item_count"] != len(records):
        raise EvidenceError("E_BRIDGE_COUNT", "eligible item count differs")
    if bridge["eligible_inventory_root_sha256"] != canonical_sha256(records):
        raise EvidenceError("E_BRIDGE_INVENTORY", "eligible inventory root differs")
    if len({record["fixed_tree_commitment"] for record in records}) != len(records):
        raise EvidenceError("E_BRIDGE_COMMITMENT_DUPLICATE", "duplicate tree commitment")
    return bridge


def verify_pinned_bridge(repo_root: str | Path, consumer_lock: Mapping[str, Any]) -> dict:
    root = Path(repo_root)
    lock = validate_exact_object(dict(consumer_lock), _LOCK_SCHEMA, "consumer_lock")
    commit = _git_oid(lock["release_commit_sha"], "consumer_lock.release_commit_sha")
    observed_commit = _git(root, "rev-parse", commit).decode().strip()
    if observed_commit != commit:
        raise EvidenceError("E_PINNED_COMMIT", "release commit does not resolve exactly")
    bridge_path = safe_relative_path(lock["bridge_path"]).as_posix()
    contract_path = safe_relative_path(lock["contract_path"]).as_posix()
    bridge_blob = _git(root, "rev-parse", f"{commit}:{bridge_path}").decode().strip()
    if bridge_blob != lock["bridge_blob_sha"]:
        raise EvidenceError("E_PINNED_BRIDGE_BLOB", "bridge Git blob differs")
    contract_blob = _git(root, "rev-parse", f"{commit}:{contract_path}").decode().strip()
    if contract_blob != lock["contract_blob_sha"]:
        raise EvidenceError("E_PINNED_CONTRACT_BLOB", "contract Git blob differs")
    bridge_raw = _git(root, "show", f"{commit}:{bridge_path}")
    contract_raw = _git(root, "show", f"{commit}:{contract_path}")
    bridge = validate_bridge_document(_canonical_document(bridge_raw, "bridge"), lock)
    if hashlib.sha256(contract_raw).hexdigest() != bridge["p12_contract_sha256"]:
        raise EvidenceError("E_CONTRACT_SHA256", "contract raw SHA-256 differs")
    return bridge


def _controlled_subject_id(record: Mapping[str, Any], feature: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
            "public_workload_set_sha256": feature["public_workload_set_sha256"],
            "domain": "P3-SUBJECT-v1",
        }
    )


def _sites(subject_id: str, values: Sequence[Any]) -> list[dict[str, Any]]:
    sites: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        site = validate_exact_object(value, _SITE_SCHEMA, f"site[{index}]")
        safe_relative_path(site["path"])
        if any(type(site[field]) is not int or site[field] < 0 for field in _SITE_SCHEMA if field.endswith(("line", "col"))):
            raise EvidenceError("E_SITE_SPAN", f"site {index} has invalid span")
        body = {"controlled_subject_id": subject_id, **site, "domain": "P3-SITE-v1"}
        sites.append({**site, "site_id": canonical_sha256(body)})
    sites.sort(
        key=lambda item: (
            item["path"],
            item["symbol"],
            item["start_line"],
            item["start_col"],
            item["end_line"],
            item["end_col"],
            item["site_id"],
        )
    )
    if len({item["site_id"] for item in sites}) != len(sites):
        raise EvidenceError("E_SITE_DUPLICATE", "duplicate canonical site")
    return sites


def select_first_applicable_site(
    sites: Sequence[Mapping[str, Any]],
    predicate: Callable[[Mapping[str, Any]], bool],
) -> str | None:
    """Select the first applicable canonical site without transferring the slot."""

    canonical: list[dict[str, Any]] = []
    for index, candidate in enumerate(sites):
        site = validate_exact_object(
            dict(candidate), _CANONICAL_SITE_SCHEMA, f"canonical_sites[{index}]"
        )
        safe_relative_path(site["path"])
        validate_sha256(site["site_id"], f"canonical_sites[{index}].site_id")
        canonical.append(site)
    def order(item: Mapping[str, Any]) -> tuple[Any, ...]:
        return (
            item["path"],
            item["symbol"],
            item["start_line"],
            item["start_col"],
            item["end_line"],
            item["end_col"],
            item["site_id"],
        )
    if canonical != sorted(canonical, key=order):
        raise EvidenceError("E_SITE_ORDER", "sites are not in canonical order")
    for site in canonical:
        applicable = predicate(site)
        if type(applicable) is not bool:
            raise EvidenceError("E_APPLICABILITY_RESULT", "predicate must return bool")
        if applicable:
            return site["site_id"]
    return None


def tag_site_reachability(
    sites: Sequence[Mapping[str, Any]],
    profiling_results: Sequence[Mapping[str, Any]],
    applicability_predicate: Callable[[Mapping[str, Any]], bool],
) -> list[dict[str, str]]:
    """Tag static sites with reachability and independent applicability.

    Reachability is derived only from observed profiling site IDs. Applicability
    is derived only from the frozen static semantic predicate. An unexecuted
    site is always ``UNPROFILED`` and is never reported as ``NOT_APPLICABLE``
    through the reachability channel.
    """

    canonical: list[dict[str, Any]] = []
    for index, candidate in enumerate(sites):
        site = validate_exact_object(
            dict(candidate), _CANONICAL_SITE_SCHEMA, f"canonical_sites[{index}]"
        )
        safe_relative_path(site["path"])
        validate_sha256(site["site_id"], f"canonical_sites[{index}].site_id")
        canonical.append(site)
    def order(item: Mapping[str, Any]) -> tuple[Any, ...]:
        return (
            item["path"],
            item["symbol"],
            item["start_line"],
            item["start_col"],
            item["end_line"],
            item["end_col"],
            item["site_id"],
        )
    if canonical != sorted(canonical, key=order):
        raise EvidenceError("E_SITE_ORDER", "sites are not in canonical order")
    if not isinstance(profiling_results, Sequence) or isinstance(
        profiling_results, (str, bytes)
    ):
        raise EvidenceError("E_PROFILE_RESULTS", "profiling_results must be a sequence")
    observed: set[str] = set()
    for index, candidate in enumerate(profiling_results):
        if not isinstance(candidate, Mapping):
            raise EvidenceError(
                "E_PROFILE_RESULTS", f"profiling_results[{index}] must be an object"
            )
        site_ids = candidate.get("observed_site_ids", [])
        if site_ids is None:
            site_ids = []
        if not isinstance(site_ids, list):
            raise EvidenceError(
                "E_PROFILE_RESULTS",
                f"profiling_results[{index}].observed_site_ids must be a list",
            )
        for site_index, site_id in enumerate(site_ids):
            observed.add(
                validate_sha256(
                    site_id,
                    f"profiling_results[{index}].observed_site_ids[{site_index}]",
                )
            )
    tagged: list[dict[str, str]] = []
    for site in canonical:
        applicable = applicability_predicate(site)
        if type(applicable) is not bool:
            raise EvidenceError("E_APPLICABILITY_RESULT", "predicate must return bool")
        reachability = (
            "OBSERVED_REACHABLE" if site["site_id"] in observed else "UNPROFILED"
        )
        applicability = "APPLICABLE" if applicable else "NOT_APPLICABLE"
        if reachability == "NOT_APPLICABLE":
            raise EvidenceError(
                "E_SITE_REACHABILITY",
                "reachability channel cannot emit NOT_APPLICABLE",
            )
        tagged.append(
            {
                "site_id": site["site_id"],
                "reachability": reachability,
                "applicability": applicability,
            }
        )
    return tagged


def validate_proposal_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate proposal provenance; reject missing hashes and fabricated params."""

    if not isinstance(record, Mapping):
        raise EvidenceError("E_PROPOSAL", "proposal record must be an object")
    for field in ("prompt_sha256", "context_sha256", "response_sha256"):
        if field not in record:
            raise EvidenceError("E_PROPOSAL", f"proposal record missing {field}")
    for field in _PROPOSAL_UNAVAILABLE_FIELDS:
        if field in record and record[field] != UNAVAILABLE_NOT_CLAIMED:
            raise EvidenceError(
                "E_PROPOSAL_UNAVAILABLE",
                f"{field} must be the literal {UNAVAILABLE_NOT_CLAIMED}",
            )
    value = validate_exact_object(dict(record), _PROPOSAL_SCHEMA, "proposal_record")
    if value["schema_version"] != "p3-proposal-record-v1":
        raise EvidenceError("E_PROPOSAL", "unsupported proposal record schema")
    if not value["provider_model"]:
        raise EvidenceError("E_PROPOSAL", "provider_model must be nonempty")
    if not value["timestamp_utc"]:
        raise EvidenceError("E_PROPOSAL", "timestamp_utc must be nonempty")
    validate_sha256(value["prompt_sha256"], "prompt_sha256")
    validate_sha256(value["context_sha256"], "context_sha256")
    validate_sha256(value["response_sha256"], "response_sha256")
    body = dict(value)
    return {**body, "artifact_sha256": canonical_sha256(body)}


def select_construct_subjects(
    subjects: Sequence[Mapping[str, Any]],
    eligible_subject_ids: set[str],
    *,
    limit: int = 18,
) -> list[str]:
    """Apply the frozen cell order and strict round-robin construction sampling."""

    if type(limit) is not int or limit < 1:
        raise EvidenceError("E_CONSTRUCT_LIMIT", "construct limit must be positive")
    buckets: dict[tuple[str, str], list[tuple[str, str]]] = {}
    observed: set[str] = set()
    for subject in subjects:
        subject_id = validate_sha256(
            subject.get("controlled_subject_id"), "subject.controlled_subject_id"
        )
        if subject_id in observed:
            raise EvidenceError("E_SUBJECT_DUPLICATE", "duplicate controlled subject")
        observed.add(subject_id)
        if subject_id not in eligible_subject_ids:
            continue
        scale = subject.get("scale_class")
        technique = subject.get("primary_technique")
        vector = subject.get("technique_vector")
        if scale not in _SCALES or technique not in _TECHNIQUES or not isinstance(vector, list):
            raise EvidenceError("E_SUBJECT_PROFILE", "subject sampling profile is invalid")
        selection_key = canonical_sha256(
            {
                "controlled_subject_id": subject_id,
                "scale_class": scale,
                "technique_vector": vector,
                "domain": "P3-C1",
            }
        )
        buckets.setdefault((scale, technique), []).append((selection_key, subject_id))
    for bucket in buckets.values():
        bucket.sort()
    selected: list[str] = []
    scale_rank = {value: index for index, value in enumerate(_SCALE_ORDER)}
    technique_rank = {value: index for index, value in enumerate(_TECHNIQUE_ORDER)}
    cells = sorted(
        buckets, key=lambda cell: (scale_rank[cell[0]], technique_rank[cell[1]])
    )
    round_index = 0
    while len(selected) < limit:
        progressed = False
        for cell in cells:
            bucket = buckets[cell]
            if round_index < len(bucket):
                selected.append(bucket[round_index][1])
                progressed = True
                if len(selected) == limit:
                    break
        if not progressed:
            break
        round_index += 1
    return selected


def build_subject_frames(
    verified_bridge: Mapping[str, Any],
    derived_subjects: Sequence[Mapping[str, Any]],
    construct_limit: int = 18,
) -> dict[str, Any]:
    if type(construct_limit) is not int or construct_limit < 1:
        raise EvidenceError("E_CONSTRUCT_LIMIT", "construct limit must be positive")
    records = verified_bridge.get("records")
    if not isinstance(records, list):
        raise EvidenceError("E_BRIDGE_RECORDS", "verified bridge records are absent")
    records_by_neutral: dict[str, Mapping[str, Any]] = {}
    for record in records:
        neutral = validate_sha256(
            record.get("neutral_snapshot_id"), "bridge_record.neutral_snapshot_id"
        )
        if neutral in records_by_neutral:
            raise EvidenceError("E_BRIDGE_RECORDS", "duplicate bridge neutral ID")
        records_by_neutral[neutral] = record

    materials: dict[str, dict[str, Any]] = {}
    for index, candidate in enumerate(derived_subjects):
        if not isinstance(candidate, Mapping):
            raise EvidenceError(
                "E_DERIVED_SUBJECT", f"derived_subjects[{index}] must be an object"
            )
        material = validate_exact_object(
            dict(candidate), _DERIVED_SUBJECT_SCHEMA, f"derived_subjects[{index}]"
        )
        neutral = validate_sha256(
            material["neutral_snapshot_id"],
            f"derived_subjects[{index}].neutral_snapshot_id",
        )
        body = {key: value for key, value in material.items() if key != "artifact_sha256"}
        if material["artifact_sha256"] != canonical_sha256(body):
            raise EvidenceError("E_DERIVED_SUBJECT_HASH", "derived subject self-hash differs")
        source_id = validate_sha256(
            material["controlled_subject_source_id"],
            f"derived_subjects[{index}].controlled_subject_source_id",
        )
        artifact_fields = (
            "adapter_discovery",
            "source_scale",
            "public_behavior_frame",
            "profiling_workload",
            "common_inputs",
            "profiling_results",
            "technique_profile",
        )
        for field in artifact_fields:
            artifact = material[field]
            if not isinstance(artifact, Mapping):
                raise EvidenceError(
                    "E_DERIVED_SUBJECT_BINDING", f"{field} must be an object"
                )
            artifact_body = {
                key: value
                for key, value in artifact.items()
                if key != "artifact_sha256"
            }
            observed_sha256 = artifact.get("artifact_sha256")
            if (
                material[f"{field}_sha256"] != observed_sha256
                or observed_sha256 != canonical_sha256(artifact_body)
            ):
                raise EvidenceError(
                    "E_DERIVED_SUBJECT_BINDING", f"{field} artifact binding differs"
                )
        record = records_by_neutral.get(neutral)
        if record is not None:
            expected_source_id = _controlled_subject_source_id(record)
            discovery = material["adapter_discovery"]
            scale = material["source_scale"]
            frame = material["public_behavior_frame"]
            workload = material["profiling_workload"]
            common = material["common_inputs"]
            receipt = material["profiling_results"]
            technique = material["technique_profile"]
            if source_id != expected_source_id or any(
                artifact.get("controlled_subject_source_id") != source_id
                for artifact in (discovery, scale, frame, workload, common, receipt, technique)
            ):
                raise EvidenceError(
                    "E_DERIVED_SUBJECT_BINDING", "controlled source binding differs"
                )
            if (
                discovery.get("neutral_snapshot_id") != neutral
                or discovery.get("normalized_source_tree_sha256")
                != record["normalized_source_tree_sha256"]
                or discovery.get("build_descriptor_sha256")
                != record["build_descriptor_sha256"]
                or scale.get("neutral_snapshot_id") != neutral
                or scale.get("normalized_source_tree_sha256")
                != record["normalized_source_tree_sha256"]
                or scale.get("build_descriptor_sha256")
                != record["build_descriptor_sha256"]
                or receipt.get("neutral_snapshot_id") != neutral
                or receipt.get("normalized_source_tree_sha256")
                != record["normalized_source_tree_sha256"]
                or receipt.get("build_descriptor_sha256")
                != record["build_descriptor_sha256"]
                or technique.get("neutral_snapshot_id") != neutral
                or technique.get("normalized_source_tree_sha256")
                != record["normalized_source_tree_sha256"]
                or technique.get("build_descriptor_sha256")
                != record["build_descriptor_sha256"]
            ):
                raise EvidenceError(
                    "E_DERIVED_SUBJECT_BINDING", "subject identity binding differs"
                )
            if (
                scale.get("discovery_sha256")
                != material["adapter_discovery_sha256"]
                or frame.get("adapter_discovery_sha256")
                != material["adapter_discovery_sha256"]
                or receipt.get("profiling_workload_sha256")
                != material["profiling_workload_sha256"]
                or receipt.get("adapter_implementation_source_sha256")
                != discovery.get("implementation_source_sha256")
                or technique.get("adapter_discovery_sha256")
                != material["adapter_discovery_sha256"]
                or technique.get("profiling_workload_sha256")
                != material["profiling_workload_sha256"]
                or technique.get("profiling_results_sha256")
                != material["profiling_results_sha256"]
            ):
                raise EvidenceError(
                    "E_DERIVED_SUBJECT_BINDING", "direct parent binding differs"
                )
            try:
                discovery_bindings = {
                    "neutral_snapshot_id": neutral,
                    "controlled_subject_source_id": source_id,
                    "normalized_source_tree_sha256": record[
                        "normalized_source_tree_sha256"
                    ],
                    "build_descriptor_sha256": record["build_descriptor_sha256"],
                    "adapter_registry_sha256": validate_sha256(
                        discovery.get("adapter_registry_sha256"),
                        "adapter_discovery.adapter_registry_sha256",
                    ),
                }
                expected_discovery_keys = set(_ADAPTER_DISCOVERY_SCHEMA) | set(
                    discovery_bindings
                )
                if set(discovery) != expected_discovery_keys:
                    raise EvidenceError(
                        "E_DERIVED_SUBJECT_BINDING",
                        "bound adapter discovery keys differ",
                    )
                raw_discovery_body = {
                    key: discovery[key]
                    for key in _ADAPTER_DISCOVERY_SCHEMA
                    if key != "artifact_sha256"
                }
                raw_discovery = {
                    **raw_discovery_body,
                    "artifact_sha256": canonical_sha256(raw_discovery_body),
                }
                raw_discovery = _validate_discovery(raw_discovery)
                expected_discovery = _bind_artifact(
                    raw_discovery, discovery_bindings
                )
                if discovery != expected_discovery:
                    raise EvidenceError(
                        "E_DERIVED_SUBJECT_BINDING",
                        "adapter discovery does not reconstruct from nested evidence",
                    )
                source_record = {
                    "normalized_source_tree_sha256": record[
                        "normalized_source_tree_sha256"
                    ],
                    "build_descriptor_sha256": record["build_descriptor_sha256"],
                }
                expected_frame = _bind_artifact(
                    build_public_behavior_frame(source_record, raw_discovery),
                    {"adapter_discovery_sha256": discovery["artifact_sha256"]},
                )
                if frame != expected_frame:
                    raise EvidenceError(
                        "E_DERIVED_SUBJECT_BINDING",
                        "public behavior frame does not reconstruct from discovery",
                    )

                per_file = scale.get("per_file_effective_lines")
                if not isinstance(per_file, list):
                    raise EvidenceError(
                        "E_DERIVED_SUBJECT_BINDING", "source scale rows are absent"
                    )
                expected_paths = raw_discovery["source_files"]
                observed_paths = [
                    row.get("path")
                    for row in per_file
                    if isinstance(row, Mapping)
                ]
                if observed_paths != expected_paths:
                    raise EvidenceError(
                        "E_DERIVED_SUBJECT_BINDING",
                        "source scale paths differ from adapter discovery",
                    )
                if any(
                    not isinstance(row, Mapping)
                    or set(row) != {"path", "effective_lines"}
                    or type(row["effective_lines"]) is not int
                    or row["effective_lines"] < 0
                    for row in per_file
                ):
                    raise EvidenceError(
                        "E_DERIVED_SUBJECT_BINDING", "source scale rows are invalid"
                    )
                total_lines = sum(row["effective_lines"] for row in per_file)
                expected_scale_class = (
                    "S"
                    if total_lines < 10_000
                    else "M"
                    if total_lines < 100_000
                    else "L"
                )
                expected_scale = _bind_artifact(
                    {
                        "schema_version": "p3-source-scale-v1",
                        "adapter_id": raw_discovery["adapter_id"],
                        "ecosystem": raw_discovery["ecosystem"],
                        "implementation_source_sha256": raw_discovery[
                            "implementation_source_sha256"
                        ],
                        "discovery_sha256": raw_discovery["artifact_sha256"],
                        "per_file_effective_lines": per_file,
                        "total_effective_lines": total_lines,
                        "scale_class": expected_scale_class,
                    },
                    {
                        "neutral_snapshot_id": neutral,
                        "controlled_subject_source_id": source_id,
                        "normalized_source_tree_sha256": record[
                            "normalized_source_tree_sha256"
                        ],
                        "build_descriptor_sha256": record[
                            "build_descriptor_sha256"
                        ],
                        "discovery_sha256": discovery["artifact_sha256"],
                    },
                )
                if scale != expected_scale:
                    raise EvidenceError(
                        "E_DERIVED_SUBJECT_BINDING",
                        "source scale does not reconstruct from nested evidence",
                    )

                expected_workload = select_profiling_workload(
                    expected_frame, expected_scale_class
                )
                if workload != expected_workload:
                    raise EvidenceError(
                        "E_DERIVED_SUBJECT_BINDING",
                        "profiling workload does not reconstruct from frame and scale",
                    )
                expected_technique_body = classify_technique(
                    expected_workload, receipt
                )
                expected_technique = _bind_artifact(
                    expected_technique_body,
                    {
                        "neutral_snapshot_id": neutral,
                        "controlled_subject_source_id": source_id,
                        "normalized_source_tree_sha256": record[
                            "normalized_source_tree_sha256"
                        ],
                        "build_descriptor_sha256": record[
                            "build_descriptor_sha256"
                        ],
                        "adapter_discovery_sha256": discovery["artifact_sha256"],
                        "profiling_workload_sha256": expected_workload[
                            "artifact_sha256"
                        ],
                        "profiling_results_sha256": receipt["artifact_sha256"],
                    },
                )
                if technique != expected_technique:
                    raise EvidenceError(
                        "E_DERIVED_SUBJECT_BINDING",
                        "technique profile does not reconstruct from profiling receipt",
                    )

                expected_subject_id = _controlled_subject_id(
                    record,
                    {
                        "public_workload_set_sha256": expected_workload[
                            "artifact_sha256"
                        ]
                    },
                )
                expected_vector = sorted(
                    set(expected_technique["confirmed_tags"])
                    | {expected_technique["primary_technique"]}
                )
                expected_subject = {
                    "controlled_subject_id": expected_subject_id,
                    "normalized_source_tree_sha256": record[
                        "normalized_source_tree_sha256"
                    ],
                    "build_descriptor_sha256": record["build_descriptor_sha256"],
                    "public_workload_set_sha256": expected_workload[
                        "artifact_sha256"
                    ],
                    "scale_class": expected_scale_class,
                    "primary_technique": expected_technique["primary_technique"],
                    "technique_vector": expected_vector,
                    "sites": _sites(expected_subject_id, raw_discovery["sites"]),
                    "neutral_snapshot_ids": [neutral],
                }
                if material["subject"] != expected_subject:
                    raise EvidenceError(
                        "E_DERIVED_SUBJECT_BINDING",
                        "derived subject does not reconstruct from nested evidence",
                    )
            except EvidenceError as exc:
                if exc.code == "E_DERIVED_SUBJECT_BINDING":
                    raise
                raise EvidenceError(
                    "E_DERIVED_SUBJECT_BINDING",
                    f"nested subject derivation is invalid: {exc.code}",
                ) from exc
        if neutral in materials:
            raise EvidenceError(
                "E_SUBJECT_SPEC_COVERAGE", f"duplicate derived subject: {neutral}"
            )
        profile = validate_exact_object(
            material["subject"], _SUBJECT_PROFILE_SCHEMA, f"derived_subjects[{index}].subject"
        )
        if profile["neutral_snapshot_ids"] != [neutral]:
            raise EvidenceError("E_DERIVED_SUBJECT", "derived subject neutral binding differs")
        if profile["scale_class"] not in _SCALES:
            raise EvidenceError("E_SCALE", f"invalid scale: {profile['scale_class']}")
        if profile["primary_technique"] not in _TECHNIQUES:
            raise EvidenceError("E_TECHNIQUE", "invalid primary technique")
        vector = profile["technique_vector"]
        if (
            not vector
            or any(item not in _TECHNIQUES for item in vector)
            or vector != sorted(set(vector))
            or profile["primary_technique"] not in vector
        ):
            raise EvidenceError("E_TECHNIQUE", "technique vector is not canonical")
        materials[neutral] = material
    if set(materials) != set(records_by_neutral):
        raise EvidenceError(
            "E_SUBJECT_SPEC_COVERAGE", "derived subjects do not cover bridge exactly"
        )

    profiles: dict[str, dict[str, Any]] = {}
    eligibility: dict[str, dict[str, bool]] = {}
    for neutral in sorted(records_by_neutral):
        record = records_by_neutral[neutral]
        profile = {
            **materials[neutral]["subject"],
            "neutral_snapshot_ids": list(
                materials[neutral]["subject"]["neutral_snapshot_ids"]
            ),
        }
        if (
            profile["normalized_source_tree_sha256"]
            != record["normalized_source_tree_sha256"]
            or profile["build_descriptor_sha256"]
            != record["build_descriptor_sha256"]
        ):
            raise EvidenceError("E_DERIVED_SUBJECT", "derived subject source binding differs")
        subject_id = validate_sha256(
            profile["controlled_subject_id"], "subject.controlled_subject_id"
        )
        existing = profiles.get(subject_id)
        if existing is not None:
            comparable = {**existing, "neutral_snapshot_ids": [neutral]}
            if comparable != profile:
                raise EvidenceError("E_SUBJECT_ALIAS_CONFLICT", "subject aliases conflict")
            existing["neutral_snapshot_ids"].append(neutral)
            existing["neutral_snapshot_ids"].sort()
        else:
            profiles[subject_id] = profile
        state = eligibility.setdefault(subject_id, {"construct": False, "criterion": False})
        state["construct"] = state["construct"] or record["eligible_for_construct"]
        state["criterion"] = state["criterion"] or record["eligible_for_criterion"]

    subjects = [profiles[key] for key in sorted(profiles)]
    selected = select_construct_subjects(
        subjects,
        {subject_id for subject_id, state in eligibility.items() if state["construct"]},
        limit=construct_limit,
    )
    criterion = sorted(
        subject_id for subject_id, state in eligibility.items() if state["criterion"]
    )
    construct_cells = {
        (subject["scale_class"], subject["primary_technique"])
        for subject in subjects
        if eligibility[subject["controlled_subject_id"]]["construct"]
    }
    empty_construct_cells = [
        {
            "scale_class": scale,
            "primary_technique": technique,
            "status": "EMPTY_FRAME",
        }
        for scale in _SCALE_ORDER
        for technique in _TECHNIQUE_ORDER
        if (scale, technique) not in construct_cells
    ]
    body = {
        "schema_version": "p3-subject-frames-v1",
        "subjects": subjects,
        "c_construct": selected,
        "c_criterion": criterion,
        "empty_construct_cells": empty_construct_cells,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def verify_reveal(
    bridge_record: Mapping[str, Any],
    reveal_record: Mapping[str, Any],
    package_root: str,
    *,
    observed_tree_oid: str,
    observed_normalized_sha256: str,
) -> None:
    validate_exact_object(dict(bridge_record), _RECORD_SCHEMA, "bridge_record")
    reveal = validate_exact_object(dict(reveal_record), _REVEAL_SCHEMA, "reveal_record")
    validate_sha256(package_root, "package_root")
    fixed_oid = _git_oid(reveal["fixed_git_tree_oid"], "reveal.fixed_git_tree_oid")
    if not isinstance(reveal["reveal_nonce"], str) or re.fullmatch(
        r"[0-9a-f]{64}", reveal["reveal_nonce"]
    ) is None:
        raise EvidenceError("E_REVEAL_NONCE", "reveal nonce must encode 32 bytes")
    validate_sha256(reveal["normalized_source_tree_sha256"], "reveal.normalized_source")
    commitment = hashlib.sha256(
        b"P3-FIXED-TREE-v1"
        + package_root.encode("ascii")
        + fixed_oid.encode("ascii")
        + bytes.fromhex(reveal["reveal_nonce"])
    ).hexdigest()
    if commitment != bridge_record["fixed_tree_commitment"]:
        raise EvidenceError("E_REVEAL_COMMITMENT", "fixed-tree commitment does not open")
    if reveal["neutral_snapshot_id"] != bridge_record["neutral_snapshot_id"]:
        raise EvidenceError("E_REVEAL_ID", "neutral snapshot ID differs")
    if observed_tree_oid != fixed_oid:
        raise EvidenceError("E_REVEAL_TREE", "observed Git tree differs")
    if (
        reveal["normalized_source_tree_sha256"]
        != bridge_record["normalized_source_tree_sha256"]
        or observed_normalized_sha256 != bridge_record["normalized_source_tree_sha256"]
    ):
        raise EvidenceError("E_REVEAL_SOURCE", "normalized source differs")


def _validate_adapter_registry_structure(
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    value = validate_exact_object(dict(registry), _ADAPTER_REGISTRY_SCHEMA, "adapter_registry")
    if value["schema_version"] != "p3-adapter-registry-v1":
        raise EvidenceError("E_ADAPTER_REGISTRY", "adapter registry version differs")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_ADAPTER_REGISTRY_HASH", "adapter registry self-hash differs")
    adapters = value["adapters"]
    if not isinstance(adapters, list) or len(adapters) != len(CONFIRMATORY_ADAPTERS):
        raise EvidenceError("E_ADAPTER_ALLOWLIST", "adapter registry must list confirmatory adapters exactly")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, candidate in enumerate(adapters):
        entry = validate_exact_object(candidate, _ADAPTER_ENTRY_SCHEMA, f"adapters[{index}]")
        adapter_id = entry["adapter_id"]
        if adapter_id not in CONFIRMATORY_ADAPTERS:
            raise EvidenceError("E_ADAPTER_ALLOWLIST", f"adapter not confirmatory: {adapter_id}")
        if adapter_id in seen:
            raise EvidenceError("E_ADAPTER_DUPLICATE", f"duplicate adapter: {adapter_id}")
        seen.add(adapter_id)
        if entry["ecosystem"] != _ADAPTER_ECOSYSTEMS[adapter_id]:
            raise EvidenceError("E_ADAPTER_ECOSYSTEM", f"ecosystem differs for {adapter_id}")
        safe_relative_path(entry["implementation_path"])
        validate_sha256(entry["source_sha256"], f"adapters[{index}].source_sha256")
        normalized.append(entry)
    if seen != CONFIRMATORY_ADAPTERS:
        raise EvidenceError("E_ADAPTER_ALLOWLIST", "confirmatory adapter set differs")
    return {
        "schema_version": value["schema_version"],
        "adapters": normalized,
        "artifact_sha256": value["artifact_sha256"],
    }


def _implementation_snapshot(
    source_snapshot: SourceSnapshot,
    entry: Mapping[str, Any],
    implementation_id: str,
    kind: str,
) -> _VerifiedImplementationSnapshot:
    relative = safe_relative_path(entry["implementation_path"])
    source_bytes = source_snapshot.read_bytes(relative.as_posix())
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != entry["source_sha256"]:
        code = "E_ADAPTER_SOURCE_HASH" if kind == "adapter" else "E_GENERATOR_SOURCE_HASH"
        raise EvidenceError(code, f"{kind} source hash differs: {implementation_id}")
    return _VerifiedImplementationSnapshot(
        logical_filename=relative.as_posix(),
        source_sha256=digest,
        source_bytes=source_bytes,
    )


def _path_implementation_snapshot(
    root: Path,
    entry: Mapping[str, Any],
    implementation_id: str,
    kind: str,
) -> _VerifiedImplementationSnapshot:
    relative = safe_relative_path(entry["implementation_path"])
    absolute = root / relative.as_posix()
    source_bytes = read_canonical_regular_bytes(
        absolute, f"{kind} implementation {implementation_id}"
    )
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != entry["source_sha256"]:
        code = "E_ADAPTER_SOURCE_HASH" if kind == "adapter" else "E_GENERATOR_SOURCE_HASH"
        raise EvidenceError(code, f"{kind} source hash differs: {implementation_id}")
    return _VerifiedImplementationSnapshot(
        logical_filename=relative.as_posix(),
        source_sha256=digest,
        source_bytes=source_bytes,
    )


def _validated_snapshot_map(
    registry: Mapping[str, Any],
    entries: Sequence[Mapping[str, Any]],
    id_field: str,
    code: str,
) -> dict[str, _VerifiedImplementationSnapshot]:
    raw = registry.get("_implementation_snapshots")
    expected_ids = {entry[id_field] for entry in entries}
    if not isinstance(raw, Mapping) or set(raw) != expected_ids:
        raise EvidenceError(code, "verified implementation snapshots are absent")
    captured: dict[str, _VerifiedImplementationSnapshot] = {}
    for entry in entries:
        implementation_id = entry[id_field]
        snapshot = raw.get(implementation_id)
        if type(snapshot) is not _VerifiedImplementationSnapshot:
            raise EvidenceError(code, "verified implementation snapshot differs")
        logical_filename = snapshot.logical_filename
        source_sha256 = snapshot.source_sha256
        source_bytes = snapshot.source_bytes
        if (
            type(logical_filename) is not str
            or type(source_sha256) is not str
            or type(source_bytes) is not bytes
        ):
            raise EvidenceError(code, "verified implementation snapshot differs")
        try:
            logical_filename = safe_relative_path(logical_filename).as_posix()
            validate_sha256(
                source_sha256,
                f"verified implementation {implementation_id} digest",
            )
        except EvidenceError as exc:
            raise EvidenceError(
                code, "verified implementation snapshot differs"
            ) from exc
        if (
            logical_filename != entry["implementation_path"]
            or source_sha256 != entry["source_sha256"]
            or hashlib.sha256(source_bytes).hexdigest() != source_sha256
        ):
            raise EvidenceError(code, "verified implementation snapshot differs")
        captured[implementation_id] = _VerifiedImplementationSnapshot(
            logical_filename=logical_filename,
            source_sha256=source_sha256,
            source_bytes=bytes(memoryview(source_bytes)),
        )
    return captured


def _consume_verified_registry(
    registry: Mapping[str, Any], *, registry_kind: str
) -> dict[str, Any]:
    """Project a verified registry to revalidated in-memory implementation bytes."""

    if not isinstance(registry, Mapping):
        raise EvidenceError("E_ADAPTER_REGISTRY", "verified registry is absent")
    if registry_kind == "adapter":
        public_keys = ("schema_version", "adapters", "artifact_sha256")
        validated = _validate_adapter_registry_structure(
            {key: registry.get(key) for key in public_keys}
        )
        entries = validated["adapters"]
        id_field = "adapter_id"
        code = "E_ADAPTER_REGISTRY"
    elif registry_kind == "input_generator":
        public_keys = ("schema_version", "generators", "artifact_sha256")
        validated = _validate_input_generator_registry_structure(
            {key: registry.get(key) for key in public_keys}
        )
        entries = validated["generators"]
        id_field = "generator_id"
        code = "E_GENERATOR_REGISTRY"
    else:
        raise EvidenceError(
            "E_GENERATOR_REGISTRY", "verified registry kind is unsupported"
        )
    snapshots = _validated_snapshot_map(registry, entries, id_field, code)
    return {
        **validated,
        "_implementation_snapshots": snapshots,
    }


def validate_adapter_registry(
    registry: Mapping[str, Any], implementation_source: SourceSnapshot
) -> dict[str, Any]:
    value = _validate_adapter_registry_structure(registry)
    _validate_source_snapshot(implementation_source)
    snapshots = {
        entry["adapter_id"]: _implementation_snapshot(
            implementation_source, entry, entry["adapter_id"], "adapter"
        )
        for entry in value["adapters"]
    }
    return {
        **value,
        "_implementation_source": implementation_source,
        "_implementation_snapshots": snapshots,
    }


_CALLER_DISCOVERY_KEYS = frozenset(
    {
        "source_files",
        "declarations",
        "public_schemas",
        "sites",
        "discovery",
        "scale_class",
        "source_scale",
        "hand_command",
        "manual_fallback",
    }
)
_EXCLUDED_SOURCE_PARTS = frozenset(
    {
        ".bzr",
        ".git",
        ".hg",
        ".svn",
        ".tox",
        ".venv",
        "_build",
        "__pycache__",
        "build",
        "cmakefiles",
        "debug",
        "dist",
        "env",
        "external",
        "fixture",
        "fixtures",
        "generated",
        "node_modules",
        "out",
        "release",
        "relwithdebinfo",
        "minsizerel",
        "site-packages",
        "target",
        "testdata",
        "third-party",
        "third_party",
        "vendor",
        "vendored",
        "vendors",
        "venv",
    }
)
_EXCLUDED_SOURCE_NAMES = frozenset(
    {
        ".ninja_deps",
        ".ninja_log",
        "build.ninja",
        "cmakecache.txt",
        "compile_commands.json",
    }
)
_VCS_METADATA_PARTS = frozenset({".bzr", ".git", ".hg", ".svn"})
_TRANSIENT_SOURCE_PARTS = frozenset(
    {
        ".tox",
        ".venv",
        "_build",
        "__pycache__",
        "build",
        "cmakefiles",
        "debug",
        "dist",
        "env",
        "node_modules",
        "out",
        "release",
        "relwithdebinfo",
        "minsizerel",
        "site-packages",
        "target",
        "venv",
    }
)
_TRANSIENT_SOURCE_NAMES = _EXCLUDED_SOURCE_NAMES
_PYTHON_SOURCE_SUFFIXES = frozenset({".py", ".pyi", ".pyx", ".pxd"})
_CPP_SOURCE_SUFFIXES = frozenset(
    {".c", ".cc", ".cpp", ".cu", ".cuh", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl"}
)
_FORTRAN_SOURCE_SUFFIXES = frozenset(
    {".f", ".for", ".f77", ".f90", ".f95", ".f03", ".f08"}
)
_FORTRAN_FIXED_FORM_SUFFIXES = frozenset({".f", ".for", ".f77"})


def _reject_caller_discovery(value: Mapping[str, Any]) -> None:
    forbidden = sorted(set(value) & _CALLER_DISCOVERY_KEYS)
    if forbidden:
        raise EvidenceError(
            "E_ADAPTER_AUTHORITY",
            f"build descriptor contains caller-controlled discovery fields: {forbidden}",
        )


def _execute_verified_python(operation: Callable[[], Any]) -> Any:
    stdout = io.StringIO()
    stderr = io.StringIO()
    network_attempts: list[str] = []

    def block_network(*_args: Any, **_kwargs: Any) -> None:
        network_attempts.append("blocked")
        raise OSError("verified implementation network access is forbidden")

    with _VERIFIED_EXECUTION_LOCK:
        originals = {
            name: getattr(socket, name) for name in _BLOCKED_SOCKET_ATTRIBUTES
        }
        previous_dont_write_bytecode = sys.dont_write_bytecode
        result: Any = None
        failure: BaseException | None = None
        try:
            for name in _BLOCKED_SOCKET_ATTRIBUTES:
                setattr(socket, name, block_network)
            sys.dont_write_bytecode = True
            with redirect_stdout(stdout), redirect_stderr(stderr):
                try:
                    result = operation()
                except BaseException as exc:  # noqa: BLE001 - restore before propagation
                    failure = exc
        finally:
            sys.dont_write_bytecode = previous_dont_write_bytecode
            for name, original in originals.items():
                setattr(socket, name, original)

    if network_attempts:
        raise EvidenceError(
            "E_VERIFIED_EXECUTION_NETWORK",
            "verified implementation attempted network access",
        )
    if stdout.getvalue() or stderr.getvalue():
        raise EvidenceError(
            "E_VERIFIED_EXECUTION_OUTPUT",
            "verified implementation emitted Python output",
        )
    if failure is not None:
        if isinstance(failure, Exception):
            raise failure
        raise EvidenceError(
            "E_VERIFIED_EXECUTION", "verified implementation aborted execution"
        ) from failure
    return result


def _load_adapter_discover(
    logical_filename: str, adapter_id: str, source_bytes: bytes
) -> Callable[..., Any]:
    module_name = f"_p3_v3_adapter_{adapter_id.lower()}_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_loader(
        module_name, loader=None, origin=logical_filename
    )
    if spec is None:
        raise EvidenceError("E_ADAPTER_LOAD", f"unable to load adapter: {adapter_id}")
    module = importlib.util.module_from_spec(spec)
    module.__file__ = logical_filename
    try:
        exec(compile(source_bytes, logical_filename, "exec"), module.__dict__)
    except Exception as exc:
        raise EvidenceError("E_ADAPTER_LOAD", f"unable to load adapter: {adapter_id}") from exc
    discover = getattr(module, "discover", None)
    if not callable(discover):
        raise EvidenceError("E_ADAPTER_SIGNATURE", f"adapter lacks discover(): {adapter_id}")
    parameters = list(inspect.signature(discover).parameters.values())
    if (
        [parameter.name for parameter in parameters]
        != ["source_snapshot", "build_descriptor"]
        or any(
            parameter.kind is not inspect.Parameter.POSITIONAL_OR_KEYWORD
            or parameter.default is not inspect.Parameter.empty
            for parameter in parameters
        )
    ):
        raise EvidenceError(
            "E_ADAPTER_SIGNATURE",
            "discover must accept exactly source_snapshot and build_descriptor",
        )
    return discover


def _canonical_collection(values: list[Any], context: str) -> list[Any]:
    for index, item in enumerate(values):
        if not isinstance(item, Mapping):
            raise EvidenceError("E_ADAPTER_RESULT", f"{context}[{index}] must be an object")
    return sorted((dict(item) for item in values), key=canonical_json_bytes)


def _normalize_adapter_result(
    result: Any,
    *,
    source_snapshot: SourceSnapshot,
    adapter_id: str,
    ecosystem: str,
) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise EvidenceError("E_ADAPTER_RESULT", "adapter result must be an exact object")
    try:
        value = validate_exact_object(result, _ADAPTER_RESULT_SCHEMA, "adapter_result")
    except EvidenceError as exc:
        raise EvidenceError("E_ADAPTER_RESULT", str(exc)) from exc
    if value["adapter_id"] != adapter_id:
        raise EvidenceError("E_ADAPTER_ID", "adapter returned a different adapter_id")
    if value["ecosystem"] != ecosystem:
        raise EvidenceError("E_ADAPTER_ECOSYSTEM", "adapter returned a different ecosystem")

    source_files: list[str] = []
    seen_sources: set[str] = set()
    for index, raw in enumerate(value["source_files"]):
        if not isinstance(raw, str):
            raise EvidenceError(
                "E_ADAPTER_SOURCE_PATH", f"source_files[{index}] must be a string"
            )
        try:
            safe_relative_path(raw)
        except EvidenceError as exc:
            raise EvidenceError("E_ADAPTER_SOURCE_PATH", str(exc)) from exc
        if raw in seen_sources:
            raise EvidenceError("E_ADAPTER_SOURCE_PATH", f"duplicate source path: {raw}")
        seen_sources.add(raw)
        if _excluded_scale_path(raw):
            raise EvidenceError(
                "E_ADAPTER_SOURCE_PATH", f"source path is excluded: {raw}"
            )
        try:
            source_snapshot.read_bytes(raw)
        except EvidenceError as exc:
            raise EvidenceError("E_ADAPTER_SOURCE_PATH", str(exc)) from exc
        source_files.append(raw)

    declarations = _canonical_collection(value["declarations"], "declarations")
    for declaration in declarations:
        for field in ("static_dependency_tags", "prerequisites"):
            collection = declaration.get(field)
            if type(collection) is not list or any(
                type(item) is not str for item in collection
            ):
                raise EvidenceError(
                    "E_ADAPTER_RESULT",
                    f"declaration {field} must be an exact string list",
                )
            declaration[field] = sorted(set(collection))

    public_schemas = _canonical_collection(value["public_schemas"], "public_schemas")
    for index, schema in enumerate(public_schemas):
        _reject_forbidden_generator_inputs(schema, f"public_schemas[{index}]")
        provenance = schema.get("provenance_path")
        if not isinstance(provenance, str):
            raise EvidenceError(
                "E_PUBLIC_SCHEMAS", f"public_schemas[{index}] lacks provenance_path"
            )
        safe_relative_path(provenance)
        span = schema.get("provenance_span_or_key")
        if not isinstance(span, str) or not span:
            raise EvidenceError(
                "E_PUBLIC_SCHEMAS",
                f"public_schemas[{index}] lacks provenance_span_or_key",
            )

    sites: list[dict[str, Any]] = []
    for index, raw in enumerate(value["sites"]):
        if not isinstance(raw, Mapping):
            raise EvidenceError(
                "E_ADAPTER_RESULT", f"sites[{index}] must be an object"
            )
        try:
            site = validate_exact_object(dict(raw), _SITE_SCHEMA, f"sites[{index}]")
        except (TypeError, ValueError, EvidenceError) as exc:
            raise EvidenceError("E_ADAPTER_RESULT", f"sites[{index}] is invalid") from exc
        safe_relative_path(site["path"])
        if not site["symbol"] or any(
            type(site[field]) is not int or site[field] < 0
            for field in _SITE_SCHEMA
            if field.endswith(("line", "col"))
        ):
            raise EvidenceError("E_SITE_SPAN", f"sites[{index}] has an invalid span")
        sites.append(site)
    sites.sort(
        key=lambda site: (
            site["path"],
            site["symbol"],
            site["start_line"],
            site["start_col"],
            site["end_line"],
            site["end_col"],
        )
    )
    if len({canonical_sha256(site) for site in sites}) != len(sites):
        raise EvidenceError("E_SITE_DUPLICATE", "adapter returned a duplicate site")
    declarations.sort(key=canonical_json_bytes)
    public_schemas.sort(key=canonical_json_bytes)
    return {
        "source_files": sorted(source_files),
        "declarations": declarations,
        "public_schemas": public_schemas,
        "sites": sites,
    }


def run_adapter_discovery(
    source_snapshot: SourceSnapshot,
    build_descriptor: Mapping[str, Any],
    registry: Mapping[str, Any],
    adapter_id: str | None,
) -> dict[str, Any]:
    """Execute only a source-hash-verified adapter and normalize its discovery."""

    if not isinstance(build_descriptor, Mapping):
        raise EvidenceError("E_BUILD_DESCRIPTOR", "build_descriptor must be an object")
    _reject_caller_discovery(build_descriptor)
    if not isinstance(registry, Mapping):
        raise EvidenceError("E_ADAPTER_REGISTRY", "adapter registry is not verified")
    public_registry = {
        key: registry.get(key)
        for key in ("schema_version", "adapters", "artifact_sha256")
    }
    verified_registry = _validate_adapter_registry_structure(public_registry)
    snapshots = _validated_snapshot_map(
        registry,
        verified_registry["adapters"],
        "adapter_id",
        "E_ADAPTER_REGISTRY",
    )
    _validate_source_snapshot(source_snapshot)

    if adapter_id is None:
        ecosystem = build_descriptor.get("ecosystem")
        if not isinstance(ecosystem, str) or not ecosystem:
            raise EvidenceError(
                "E_ADAPTER_UNSUPPORTED", "unsupported discovery requires ecosystem"
            )
        body = {
            "schema_version": "p3-adapter-discovery-v1",
            "adapter_id": None,
            "ecosystem": ecosystem,
            "discovery_status": "ADAPTER_UNSUPPORTED",
            "implementation_source_sha256": None,
            "source_files": [],
            "declarations": [],
            "public_schemas": [],
            "sites": [],
            "unsupported_or_exclusion_reason": (
                "ecosystem has no confirmatory adapter; hand-selected commands are forbidden"
            ),
        }
        return {**body, "artifact_sha256": canonical_sha256(body)}

    entries = {
        entry.get("adapter_id"): entry
        for entry in verified_registry["adapters"]
        if isinstance(entry, Mapping)
    }
    entry = entries.get(adapter_id)
    if entry is None:
        raise EvidenceError("E_ADAPTER_UNREGISTERED", f"adapter is not registered: {adapter_id}")
    snapshot = snapshots[adapter_id]

    def invoke_adapter() -> Any:
        discover = _load_adapter_discover(
            snapshot.logical_filename, adapter_id, snapshot.source_bytes
        )
        return discover(source_snapshot, dict(build_descriptor))

    try:
        raw_result = _execute_verified_python(invoke_adapter)
    except EvidenceError:
        raise
    except Exception as exc:
        raise EvidenceError("E_ADAPTER_EXECUTION", f"adapter failed: {adapter_id}") from exc
    normalized = _normalize_adapter_result(
        raw_result,
        source_snapshot=source_snapshot,
        adapter_id=adapter_id,
        ecosystem=entry["ecosystem"],
    )
    body = {
        "schema_version": "p3-adapter-discovery-v1",
        "adapter_id": adapter_id,
        "ecosystem": entry["ecosystem"],
        "discovery_status": "EXECUTABLE",
        "implementation_source_sha256": entry["source_sha256"],
        **normalized,
        "unsupported_or_exclusion_reason": "",
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def discover_subject_or_fail_closed(
    source_snapshot: SourceSnapshot,
    build_descriptor: Mapping[str, Any],
    registry: Mapping[str, Any],
    adapter_id: str | None,
) -> dict[str, Any]:
    """Run discovery; keep adapter execution failure visible in the ITT funnel."""

    try:
        return run_adapter_discovery(
            source_snapshot, build_descriptor, registry, adapter_id
        )
    except EvidenceError as exc:
        if exc.code != "E_ADAPTER_EXECUTION" or not adapter_id:
            raise
        entries = {
            entry.get("adapter_id"): entry
            for entry in registry["adapters"]
            if isinstance(entry, Mapping)
        }
        entry = entries.get(adapter_id)
        if not isinstance(entry, Mapping):
            raise
        cause = exc.__cause__
        reason = str(cause) if cause is not None else str(exc)
        ecosystem = entry.get("ecosystem")
        if not isinstance(ecosystem, str) or not ecosystem:
            ecosystem = (
                build_descriptor.get("ecosystem")
                if isinstance(build_descriptor, Mapping)
                and isinstance(build_descriptor.get("ecosystem"), str)
                else ""
            )
        body = {
            "schema_version": "p3-adapter-discovery-v1",
            "adapter_id": adapter_id,
            "ecosystem": ecosystem,
            "discovery_status": "ADAPTER_EXECUTION_FAILED",
            "implementation_source_sha256": entry["source_sha256"],
            "source_files": [],
            "declarations": [],
            "public_schemas": [],
            "sites": [],
            "unsupported_or_exclusion_reason": reason,
        }
        return {**body, "artifact_sha256": canonical_sha256(body)}


def _validate_discovery(
    discovery: Mapping[str, Any],
    *,
    source_path_error_code: str = "E_ADAPTER_SOURCE_PATH",
) -> dict[str, Any]:
    value = validate_exact_object(
        dict(discovery), _ADAPTER_DISCOVERY_SCHEMA, "adapter_discovery"
    )
    if value["schema_version"] != "p3-adapter-discovery-v1":
        raise EvidenceError("E_ADAPTER_DISCOVERY", "discovery version differs")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_ADAPTER_DISCOVERY_HASH", "discovery self-hash differs")
    source_files: list[str] = []
    for index, relative in enumerate(value["source_files"]):
        if not isinstance(relative, str):
            raise EvidenceError(
                source_path_error_code, f"source_files[{index}] must be a string"
            )
        try:
            safe_relative_path(relative)
        except EvidenceError as exc:
            raise EvidenceError(source_path_error_code, str(exc)) from exc
        if _excluded_scale_path(relative):
            raise EvidenceError(
                source_path_error_code, f"source path is excluded: {relative}"
            )
        source_files.append(relative)
    if source_files != sorted(set(source_files)):
        raise EvidenceError(
            source_path_error_code, "source files must be sorted and unique"
        )

    declarations = value["declarations"]
    if any(not isinstance(item, Mapping) for item in declarations):
        raise EvidenceError("E_ADAPTER_RESULT", "declarations must contain objects")
    for declaration in declarations:
        for field in ("static_dependency_tags", "prerequisites"):
            collection = declaration.get(field)
            if type(collection) is not list or any(
                type(item) is not str for item in collection
            ):
                raise EvidenceError(
                    "E_ADAPTER_RESULT",
                    f"declaration {field} must be an exact string list",
                )
            if collection != sorted(set(collection)):
                raise EvidenceError(
                    "E_ADAPTER_RESULT", f"declaration {field} is not normalized"
                )
    if declarations != sorted(declarations, key=canonical_json_bytes):
        raise EvidenceError("E_ADAPTER_RESULT", "declarations are not normalized")

    public_schemas = value["public_schemas"]
    if any(not isinstance(item, Mapping) for item in public_schemas):
        raise EvidenceError("E_PUBLIC_SCHEMAS", "public schemas must contain objects")
    for index, schema in enumerate(public_schemas):
        _reject_forbidden_generator_inputs(schema, f"public_schemas[{index}]")
        provenance = schema.get("provenance_path")
        if not isinstance(provenance, str):
            raise EvidenceError(
                "E_PUBLIC_SCHEMAS", f"public_schemas[{index}] lacks provenance_path"
            )
        safe_relative_path(provenance)
        span = schema.get("provenance_span_or_key")
        if not isinstance(span, str) or not span or "raw_schema" not in schema:
            raise EvidenceError(
                "E_PUBLIC_SCHEMAS", f"public_schemas[{index}] is incomplete"
            )
    if public_schemas != sorted(public_schemas, key=canonical_json_bytes):
        raise EvidenceError("E_PUBLIC_SCHEMAS", "public schemas are not normalized")

    sites: list[dict[str, Any]] = []
    for index, candidate in enumerate(value["sites"]):
        if not isinstance(candidate, Mapping):
            raise EvidenceError(
                "E_ADAPTER_RESULT", f"sites[{index}] must be an object"
            )
        try:
            site = validate_exact_object(dict(candidate), _SITE_SCHEMA, f"sites[{index}]")
        except (TypeError, ValueError, EvidenceError) as exc:
            raise EvidenceError("E_ADAPTER_RESULT", f"sites[{index}] is invalid") from exc
        safe_relative_path(site["path"])
        if not site["symbol"] or any(
            site[field] < 0
            for field in _SITE_SCHEMA
            if field.endswith(("line", "col"))
        ):
            raise EvidenceError("E_SITE_SPAN", f"sites[{index}] has an invalid span")
        sites.append(site)
    def site_order(site: Mapping[str, Any]) -> tuple[Any, ...]:
        return (
            site["path"],
            site["symbol"],
            site["start_line"],
            site["start_col"],
            site["end_line"],
            site["end_col"],
        )
    if sites != sorted(sites, key=site_order):
        raise EvidenceError("E_ADAPTER_RESULT", "sites are not normalized")
    if len({canonical_sha256(site) for site in sites}) != len(sites):
        raise EvidenceError("E_SITE_DUPLICATE", "discovery contains duplicate sites")
    status = value["discovery_status"]
    if status == "EXECUTABLE":
        if value["adapter_id"] not in CONFIRMATORY_ADAPTERS:
            raise EvidenceError("E_ADAPTER_ID", "executable discovery adapter is invalid")
        validate_sha256(
            value["implementation_source_sha256"], "implementation_source_sha256"
        )
        if value["ecosystem"] != _ADAPTER_ECOSYSTEMS[value["adapter_id"]]:
            raise EvidenceError("E_ADAPTER_ECOSYSTEM", "discovery ecosystem differs")
    elif status == "ADAPTER_UNSUPPORTED":
        if (
            value["adapter_id"] is not None
            or value["implementation_source_sha256"] is not None
            or any(
                value[field]
                for field in ("source_files", "declarations", "public_schemas", "sites")
            )
        ):
            raise EvidenceError(
                "E_ADAPTER_UNSUPPORTED", "unsupported discovery must contain no fallback data"
            )
    elif status == "ADAPTER_EXECUTION_FAILED":
        if value["adapter_id"] not in CONFIRMATORY_ADAPTERS:
            raise EvidenceError("E_ADAPTER_ID", "failed discovery adapter is invalid")
        validate_sha256(
            value["implementation_source_sha256"], "implementation_source_sha256"
        )
        if value["ecosystem"] != _ADAPTER_ECOSYSTEMS[value["adapter_id"]]:
            raise EvidenceError("E_ADAPTER_ECOSYSTEM", "discovery ecosystem differs")
        if any(
            value[field]
            for field in ("source_files", "declarations", "public_schemas", "sites")
        ):
            raise EvidenceError(
                "E_ADAPTER_EXECUTION",
                "failed discovery must contain no fallback data",
            )
    else:
        raise EvidenceError("E_ADAPTER_DISCOVERY", "discovery status is invalid")
    return value


def _excluded_scale_path(relative: str) -> bool:
    parts = [part.casefold() for part in safe_relative_path(relative).parts]
    return any(
        part in _EXCLUDED_SOURCE_PARTS
        or part in _EXCLUDED_SOURCE_NAMES
        or part.startswith("cmake-build-")
        or part.startswith("build-")
        for part in parts
    )


def canonical_source_tree_sha256(source_snapshot: SourceSnapshot) -> str:
    """Hash the canonical regular-file manifest from explicit captured values."""

    entries = _validate_source_snapshot(source_snapshot)
    files: list[dict[str, str]] = []
    for relative, entry in entries.items():
        parts = tuple(part.casefold() for part in safe_relative_path(relative).parts)
        if any(part in _VCS_METADATA_PARTS for part in parts):
            continue
        if any(
            part in _TRANSIENT_SOURCE_PARTS
            or part.startswith("cmake-build-")
            or part.startswith("build-")
            for part in parts
        ) or Path(relative).name.casefold() in _TRANSIENT_SOURCE_NAMES:
            raise EvidenceError(
                "E_SOURCE_TREE_PATH",
                f"source snapshot contains transient output: {relative}",
            )
        files.append({"path": relative, "byte_sha256": entry.sha256})
    return canonical_sha256(
        {
            "domain": "P3-NORMALIZED-SOURCE-TREE-v1",
            "files": files,
        }
    )


def _source_language(relative_path: str) -> str:
    path = Path(relative_path)
    suffix = path.suffix.casefold()
    if path.name.casefold() == "cmakelists.txt" or suffix == ".cmake":
        return "cmake"
    if suffix in _PYTHON_SOURCE_SUFFIXES:
        return "python"
    if suffix in _CPP_SOURCE_SUFFIXES:
        return "cpp"
    if suffix in _FORTRAN_SOURCE_SUFFIXES:
        return "fortran"
    raise EvidenceError(
        "E_SCALE_SOURCE_LANGUAGE", f"unsupported source language: {path.name}"
    )


def _effective_line_count(relative_path: str, raw: bytes) -> int:
    language = _source_language(relative_path)
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise EvidenceError(
            "E_SCALE_SOURCE", f"source file is not UTF-8 text: {relative_path}"
        ) from exc
    if language == "fortran":
        fixed_form = Path(relative_path).suffix.casefold() in _FORTRAN_FIXED_FORM_SUFFIXES
        return sum(
            1
            for line in lines
            if line.strip()
            and not line.lstrip().startswith("!")
            and (not fixed_form or line[0] not in {"c", "C", "*", "d", "D"})
        )
    if language in {"python", "cmake"}:
        return sum(
            1 for line in lines if line.strip() and not line.lstrip().startswith("#")
        )
    count = 0
    in_block = False
    for line in lines:
        has_code = False
        index = 0
        while index < len(line):
            if in_block:
                end = line.find("*/", index)
                if end < 0:
                    index = len(line)
                else:
                    in_block = False
                    index = end + 2
                continue
            if line.startswith("//", index):
                break
            if line.startswith("/*", index):
                in_block = True
                index += 2
                continue
            character = line[index]
            if character in {'"', "'"}:
                has_code = True
                quote = character
                index += 1
                while index < len(line):
                    if line[index] == "\\":
                        index += 2
                    elif line[index] == quote:
                        index += 1
                        break
                    else:
                        index += 1
                continue
            if not character.isspace():
                has_code = True
            index += 1
        count += int(has_code)
    return count


def derive_source_scale(
    source_snapshot: SourceSnapshot, discovery: Mapping[str, Any]
) -> dict[str, Any]:
    """Derive scale solely from validated adapter-enumerated source files."""

    value = _validate_discovery(
        discovery, source_path_error_code="E_SCALE_SOURCE_PATH"
    )
    entries = _validate_source_snapshot(source_snapshot)
    counts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for relative in value["source_files"]:
        if not isinstance(relative, str) or relative in seen or _excluded_scale_path(relative):
            raise EvidenceError("E_SCALE_SOURCE_PATH", f"source path is excluded: {relative}")
        seen.add(relative)
        entry = entries.get(relative)
        if entry is None:
            raise EvidenceError(
                "E_SCALE_SOURCE_PATH", f"source path is absent: {relative}"
            )
        counts.append(
            {
                "path": relative,
                "effective_lines": _effective_line_count(relative, entry.content),
            }
        )
    counts.sort(key=lambda item: item["path"])
    total = sum(item["effective_lines"] for item in counts)
    scale_class = "S" if total < 10_000 else "M" if total < 100_000 else "L"
    body = {
        "schema_version": "p3-source-scale-v1",
        "adapter_id": value["adapter_id"],
        "ecosystem": value["ecosystem"],
        "implementation_source_sha256": value["implementation_source_sha256"],
        "discovery_sha256": value["artifact_sha256"],
        "per_file_effective_lines": counts,
        "total_effective_lines": total,
        "scale_class": scale_class,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _controlled_subject_source_id(source_record: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {
            "normalized_source_tree_sha256": source_record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": source_record["build_descriptor_sha256"],
            "domain": "P3-SOURCE-v1",
        }
    )


def _ecosystem_to_adapter(registry: Mapping[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for entry in registry["adapters"]:
        mapping[entry["ecosystem"]] = entry["adapter_id"]
    return mapping


def _declaration_is_structurally_valid(declaration: Mapping[str, Any]) -> tuple[bool, str]:
    category = declaration.get("category")
    if category not in _BEHAVIOR_CATEGORIES:
        return False, "category is not a frozen behavior category"
    entrypoint = declaration.get("entrypoint")
    normalized = declaration.get("normalized_entrypoint")
    if not isinstance(entrypoint, str) or not entrypoint:
        return False, "entrypoint is empty"
    if not isinstance(normalized, str) or not normalized:
        return False, "normalized_entrypoint is empty"
    try:
        validate_sha256(
            declaration.get("declared_input_schema_sha256"),
            "declared_input_schema_sha256",
        )
    except EvidenceError:
        return False, "declared_input_schema_sha256 is invalid"
    tags = declaration.get("static_dependency_tags")
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        return False, "static_dependency_tags must be a string list"
    prerequisites = declaration.get("prerequisites")
    if not isinstance(prerequisites, list) or any(not isinstance(item, str) for item in prerequisites):
        return False, "prerequisites must be a string list"
    if "declared_inputs" not in declaration:
        return False, "declared_inputs missing"
    span = declaration.get("provenance_span_or_key")
    if not isinstance(span, str) or not span:
        return False, "provenance_span_or_key missing"
    return True, ""


def _diversity_signature(row: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {
            "category": row["category"],
            "normalized_entrypoint": row["normalized_entrypoint"],
            "sorted_static_dependency_tags": sorted(set(row["static_dependency_tags"])),
            "declared_input_schema_sha256": row["declared_input_schema_sha256"],
            "domain": "P3-PROFILE-DIVERSITY-v1",
        }
    )


def _behavior_id(source_id: str, row: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {
            "controlled_subject_source_id": source_id,
            "category": row["category"],
            "provenance_path": row["provenance_path"],
            "provenance_span_or_key": row["provenance_span_or_key"],
            "normalized_entrypoint": row["normalized_entrypoint"],
            "domain": "P3-BEHAVIOR-v1",
        }
    )


def build_public_behavior_frame(
    source_record: Mapping[str, Any],
    discovery: Mapping[str, Any],
) -> dict[str, Any]:
    source = validate_exact_object(dict(source_record), _SOURCE_RECORD_SCHEMA, "source_record")
    validate_sha256(source["normalized_source_tree_sha256"], "normalized_source_tree_sha256")
    validate_sha256(source["build_descriptor_sha256"], "build_descriptor_sha256")
    adapter_discovery = _validate_discovery(discovery)
    declarations = adapter_discovery["declarations"]
    source_id = _controlled_subject_source_id(source)
    rows: list[dict[str, Any]] = []
    for index, raw in enumerate(declarations):
        if not isinstance(raw, Mapping):
            raise EvidenceError("E_DECLARATION", f"declarations[{index}] must be an object")
        declaration = dict(raw)
        provenance_path = declaration.get("provenance_path")
        if not isinstance(provenance_path, str) or not provenance_path.strip():
            raise EvidenceError("E_PROVENANCE", f"declarations[{index}] lacks public provenance")
        safe_relative_path(provenance_path)
        provenance_span = declaration.get("provenance_span_or_key")
        if not isinstance(provenance_span, str):
            provenance_span = ""
        ecosystem = adapter_discovery["ecosystem"]
        valid, reason = _declaration_is_structurally_valid(declaration)
        adapter_id = adapter_discovery["adapter_id"]
        if adapter_id is None:
            discovery_status = "ADAPTER_UNSUPPORTED"
            exclusion = "ecosystem has no confirmatory adapter; hand-selected commands are forbidden"
            diversity = None
            behavior_fields = {
                "category": declaration.get("category")
                if declaration.get("category") in _BEHAVIOR_CATEGORIES
                else "PUBLIC_API",
                "entrypoint": declaration.get("entrypoint")
                if isinstance(declaration.get("entrypoint"), str)
                else "",
                "normalized_entrypoint": declaration.get("normalized_entrypoint")
                if isinstance(declaration.get("normalized_entrypoint"), str)
                else "",
                "declared_inputs": declaration.get("declared_inputs", {}),
                "declared_input_schema_sha256": declaration.get("declared_input_schema_sha256")
                if isinstance(declaration.get("declared_input_schema_sha256"), str)
                else "0" * 64,
                "static_dependency_tags": list(declaration.get("static_dependency_tags") or []),
                "prerequisites": list(declaration.get("prerequisites") or []),
            }
            if behavior_fields["category"] not in _BEHAVIOR_CATEGORIES:
                behavior_fields["category"] = "PUBLIC_API"
        elif not valid:
            discovery_status = "INVALID_DECLARATION"
            exclusion = reason or "declaration is invalid"
            diversity = None
            behavior_fields = {
                "category": declaration["category"]
                if declaration.get("category") in _BEHAVIOR_CATEGORIES
                else "PUBLIC_API",
                "entrypoint": declaration.get("entrypoint")
                if isinstance(declaration.get("entrypoint"), str)
                else "",
                "normalized_entrypoint": declaration.get("normalized_entrypoint")
                if isinstance(declaration.get("normalized_entrypoint"), str)
                else "",
                "declared_inputs": declaration.get("declared_inputs", {}),
                "declared_input_schema_sha256": declaration.get("declared_input_schema_sha256")
                if isinstance(declaration.get("declared_input_schema_sha256"), str)
                and len(str(declaration.get("declared_input_schema_sha256"))) == 64
                else "0" * 64,
                "static_dependency_tags": [
                    tag
                    for tag in list(declaration.get("static_dependency_tags") or [])
                    if isinstance(tag, str)
                ],
                "prerequisites": [
                    item
                    for item in list(declaration.get("prerequisites") or [])
                    if isinstance(item, str)
                ],
            }
        else:
            discovery_status = "EXECUTABLE"
            exclusion = ""
            behavior_fields = {
                "category": declaration["category"],
                "entrypoint": declaration["entrypoint"],
                "normalized_entrypoint": declaration["normalized_entrypoint"],
                "declared_inputs": declaration["declared_inputs"],
                "declared_input_schema_sha256": validate_sha256(
                    declaration["declared_input_schema_sha256"],
                    "declared_input_schema_sha256",
                ),
                "static_dependency_tags": list(declaration["static_dependency_tags"]),
                "prerequisites": list(declaration["prerequisites"]),
            }
            diversity = _diversity_signature(behavior_fields)
        row_body = {
            "controlled_subject_source_id": source_id,
            "category": behavior_fields["category"],
            "provenance_path": provenance_path,
            "provenance_span_or_key": provenance_span,
            "entrypoint": behavior_fields["entrypoint"],
            "normalized_entrypoint": behavior_fields["normalized_entrypoint"],
            "declared_inputs": behavior_fields["declared_inputs"],
            "declared_input_schema_sha256": behavior_fields["declared_input_schema_sha256"],
            "static_dependency_tags": sorted(set(behavior_fields["static_dependency_tags"]))
            if discovery_status == "EXECUTABLE"
            else list(behavior_fields["static_dependency_tags"]),
            "prerequisites": list(behavior_fields["prerequisites"]),
            "ecosystem": ecosystem,
            "adapter_id": adapter_id,
            "discovery_status": discovery_status,
            "unsupported_or_exclusion_reason": exclusion,
            "diversity_signature_sha256": diversity,
        }
        behavior_id = _behavior_id(source_id, row_body)
        row = {**row_body, "behavior_id": behavior_id}
        row_hash_body = {key: value for key, value in row.items()}
        rows.append({**row, "artifact_sha256": canonical_sha256(row_hash_body)})

    rows.sort(
        key=lambda item: (
            BEHAVIOR_CATEGORY_ORDER.index(item["category"])
            if item["category"] in _BEHAVIOR_CATEGORIES
            else len(BEHAVIOR_CATEGORY_ORDER),
            item["provenance_path"],
            item["provenance_span_or_key"],
            item["normalized_entrypoint"],
            item["behavior_id"],
        )
    )
    accounting = []
    for category in BEHAVIOR_CATEGORY_ORDER:
        category_rows = [row for row in rows if row["category"] == category]
        accounting.append(
            {
                "category": category,
                "discovered_count": len(category_rows),
                "executable_count": sum(
                    1 for row in category_rows if row["discovery_status"] == "EXECUTABLE"
                ),
                "adapter_unsupported_count": sum(
                    1
                    for row in category_rows
                    if row["discovery_status"] == "ADAPTER_UNSUPPORTED"
                ),
                "invalid_count": sum(
                    1
                    for row in category_rows
                    if row["discovery_status"] == "INVALID_DECLARATION"
                ),
            }
        )
    body = {
        "schema_version": "p3-public-behavior-frame-v1",
        "controlled_subject_source_id": source_id,
        "discovery_status": adapter_discovery["discovery_status"],
        "adapter_discovery_sha256": adapter_discovery["artifact_sha256"],
        "category_accounting": accounting,
        "rows": rows,
        "public_schemas": list(adapter_discovery["public_schemas"]),
        "sites": list(adapter_discovery["sites"]),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def select_profiling_workload(frame: Mapping[str, Any], scale_class: str) -> dict[str, Any]:
    if scale_class not in PROFILING_BUDGETS:
        raise EvidenceError("E_SCALE", f"invalid scale_class: {scale_class}")
    if not isinstance(frame, Mapping) or "rows" not in frame:
        raise EvidenceError("E_FRAME", "public behavior frame rows are absent")
    budget = PROFILING_BUDGETS[scale_class]
    source_id = frame.get("controlled_subject_source_id")
    validate_sha256(source_id, "controlled_subject_source_id")
    buckets: dict[str, list[dict[str, Any]]] = {category: [] for category in BEHAVIOR_CATEGORY_ORDER}
    for index, candidate in enumerate(frame["rows"]):
        if not isinstance(candidate, Mapping):
            raise EvidenceError("E_FRAME_ROW", f"rows[{index}] must be an object")
        if candidate.get("discovery_status") != "EXECUTABLE":
            continue
        category = candidate.get("category")
        if category not in _BEHAVIOR_CATEGORIES:
            raise EvidenceError("E_FRAME_ROW", f"rows[{index}] category is invalid")
        behavior_id = validate_sha256(candidate.get("behavior_id"), f"rows[{index}].behavior_id")
        diversity = candidate.get("diversity_signature_sha256")
        if not isinstance(diversity, str):
            diversity = _diversity_signature(candidate)
        else:
            validate_sha256(diversity, f"rows[{index}].diversity_signature_sha256")
        buckets[category].append(
            {
                "behavior_id": behavior_id,
                "category": category,
                "diversity_signature_sha256": diversity,
                "normalized_entrypoint": candidate.get("normalized_entrypoint"),
                "declared_input_schema_sha256": candidate.get("declared_input_schema_sha256"),
                "static_dependency_tags": list(candidate.get("static_dependency_tags") or []),
                "provenance_path": candidate.get("provenance_path"),
                "provenance_span_or_key": candidate.get("provenance_span_or_key"),
                "entrypoint": candidate.get("entrypoint"),
            }
        )
    for category, items in buckets.items():
        items.sort(key=lambda item: (item["diversity_signature_sha256"], item["behavior_id"]))
    selected: list[dict[str, Any]] = []
    selected_ids: list[str] = []
    selected_set: set[str] = set()
    seen_diversity: set[str] = set()
    # First pass: one lowest row from each nonempty executable category.
    for category in BEHAVIOR_CATEGORY_ORDER:
        if len(selected) >= budget:
            break
        bucket = buckets[category]
        if not bucket:
            continue
        choice = bucket[0]
        selected.append(choice)
        selected_ids.append(choice["behavior_id"])
        selected_set.add(choice["behavior_id"])
        seen_diversity.add(choice["diversity_signature_sha256"])
    # Subsequent passes: prefer unseen diversity signatures, then lowest behavior_id.
    while len(selected) < budget:
        progressed = False
        for category in BEHAVIOR_CATEGORY_ORDER:
            if len(selected) >= budget:
                break
            remaining = [
                item for item in buckets[category] if item["behavior_id"] not in selected_set
            ]
            if not remaining:
                continue
            unseen = [
                item
                for item in remaining
                if item["diversity_signature_sha256"] not in seen_diversity
            ]
            if unseen:
                pool = sorted(
                    unseen,
                    key=lambda item: (
                        item["diversity_signature_sha256"],
                        item["behavior_id"],
                    ),
                )
            else:
                pool = sorted(remaining, key=lambda item: item["behavior_id"])
            choice = pool[0]
            selected.append(choice)
            selected_ids.append(choice["behavior_id"])
            selected_set.add(choice["behavior_id"])
            seen_diversity.add(choice["diversity_signature_sha256"])
            progressed = True
        if not progressed:
            break
    counts = {
        category: sum(1 for item in selected if item["category"] == category)
        for category in BEHAVIOR_CATEGORY_ORDER
        if any(item["category"] == category for item in selected)
    }
    body = {
        "schema_version": "p3-profiling-workload-v1",
        "controlled_subject_source_id": source_id,
        "scale_class": scale_class,
        "budget": budget,
        "category_order": list(BEHAVIOR_CATEGORY_ORDER),
        "selected_rows": selected,
        "selected_behavior_ids": selected_ids,
        "selected_category_counts": counts,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def build_phase1_unresolved_profiling_receipt(
    workload: Mapping[str, Any],
    source_record: Mapping[str, Any],
    *,
    neutral_snapshot_id: str,
    adapter_implementation_source_sha256: str | None,
) -> dict[str, Any]:
    """Bind selected Phase 1 rows without claiming profiling execution."""

    if not isinstance(workload, Mapping):
        raise EvidenceError("E_WORKLOAD", "profiling workload must be an object")
    selected_rows = workload.get("selected_rows")
    if not isinstance(selected_rows, list):
        raise EvidenceError("E_WORKLOAD", "selected_rows are absent")
    workload_sha256 = validate_sha256(
        workload.get("artifact_sha256"), "profiling_workload.artifact_sha256"
    )
    workload_body = {
        key: value for key, value in workload.items() if key != "artifact_sha256"
    }
    if workload_sha256 != canonical_sha256(workload_body):
        raise EvidenceError("E_WORKLOAD_HASH", "profiling workload self-hash differs")

    if not isinstance(source_record, Mapping):
        raise EvidenceError("E_SOURCE_RECORD", "source_record must be an object")
    source = validate_exact_object(
        dict(source_record), _SOURCE_RECORD_SCHEMA, "source_record"
    )
    for field in ("normalized_source_tree_sha256", "build_descriptor_sha256"):
        validate_sha256(source[field], f"source_record.{field}")
    source_id = validate_sha256(
        workload.get("controlled_subject_source_id"),
        "profiling_workload.controlled_subject_source_id",
    )
    if source_id != _controlled_subject_source_id(source):
        raise EvidenceError(
            "E_PROFILE_SOURCE_BINDING", "profiling workload source binding differs"
        )

    neutral = validate_sha256(neutral_snapshot_id, "neutral_snapshot_id")
    if adapter_implementation_source_sha256 is not None:
        validate_sha256(
            adapter_implementation_source_sha256,
            "adapter_implementation_source_sha256",
        )

    empty_bytes_sha256 = hashlib.sha256(b"").hexdigest()
    results: list[dict[str, Any]] = []
    seen_behavior_ids: set[str] = set()
    for index, candidate in enumerate(selected_rows):
        if not isinstance(candidate, Mapping):
            raise EvidenceError(
                "E_WORKLOAD_ROW", f"selected_rows[{index}] must be an object"
            )
        behavior_id = validate_sha256(
            candidate.get("behavior_id"), f"selected_rows[{index}].behavior_id"
        )
        if behavior_id in seen_behavior_ids:
            raise EvidenceError(
                "E_WORKLOAD_ROW", f"duplicate selected behavior: {behavior_id}"
            )
        seen_behavior_ids.add(behavior_id)
        results.append(
            {
                "behavior_id": behavior_id,
                "status": "ADAPTER_UNCERTAIN",
                "argv": ["p3-phase1-unexecuted", behavior_id],
                "input_sha256": [
                    canonical_sha256(
                        {
                            "behavior_id": behavior_id,
                            "domain": "P3-PHASE1-UNEXECUTED-INPUT-v1",
                        }
                    )
                ],
                "environment_sha256": canonical_sha256(
                    {"domain": "P3-PHASE1-UNEXECUTED-ENV-v1"}
                ),
                "runner_version": "p3-phase1-unexecuted-v1",
                "exit_code": None,
                "stdout_sha256": empty_bytes_sha256,
                "stderr_sha256": empty_bytes_sha256,
                "call_trace": [],
                "call_trace_sha256": canonical_sha256([]),
                "timed_out": False,
                "failure_code": "PHASE1_PROFILING_NOT_EXECUTED",
                "observed_site_ids": [],
            }
        )
    results.sort(key=lambda row: row["behavior_id"])
    body = {
        "schema_version": "p3-profiling-results-v1",
        "neutral_snapshot_id": neutral,
        "controlled_subject_source_id": source_id,
        "normalized_source_tree_sha256": source[
            "normalized_source_tree_sha256"
        ],
        "build_descriptor_sha256": source["build_descriptor_sha256"],
        "profiling_workload_sha256": workload_sha256,
        "adapter_implementation_source_sha256": (
            adapter_implementation_source_sha256
        ),
        "runner_implementation_source_sha256": PHASE1_UNEXECUTED_RUNNER_SHA256,
        "results": results,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _serialize_fraction(value: Fraction) -> str:
    text = format(Decimal(value.numerator) / Decimal(value.denominator), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _module_matches(module: str, prefixes: tuple[str, ...]) -> bool:
    normalized = module.casefold()
    return any(
        normalized == prefix or normalized.startswith(f"{prefix}.")
        for prefix in prefixes
    )


def _techniques_from_call_trace(call_trace: list[Any]) -> list[str]:
    techniques: set[str] = set()
    for index, candidate in enumerate(call_trace):
        if not isinstance(candidate, Mapping):
            raise EvidenceError(
                "E_PROFILE_TRACE", f"call_trace[{index}] must be an object"
            )
        event = validate_exact_object(
            dict(candidate), _CALL_TRACE_EVENT_SCHEMA, f"call_trace[{index}]"
        )
        if event["sequence"] != index + 1:
            raise EvidenceError(
                "E_PROFILE_TRACE", "call trace sequence must be contiguous and ordered"
            )
        if not event["module"] or not event["symbol"]:
            raise EvidenceError(
                "E_PROFILE_TRACE", "call trace module and symbol must be nonempty"
            )
        if event["call_kind"] not in _TRACE_CALL_KINDS:
            raise EvidenceError("E_PROFILE_TRACE", "call trace kind is not frozen")
        argument_types = event["argument_types"]
        keyword_names = event["keyword_names"]
        if any(type(item) is not str or not item for item in argument_types):
            raise EvidenceError("E_PROFILE_TRACE", "call argument types are invalid")
        if (
            any(type(item) is not str or not item for item in keyword_names)
            or keyword_names != sorted(set(keyword_names))
        ):
            raise EvidenceError("E_PROFILE_TRACE", "call keyword names are not canonical")

        module = event["module"]
        symbol_tokens = frozenset(
            re.findall(r"[a-z0-9]+", event["symbol"].casefold())
        )
        if event["call_kind"] in _NATIVE_CALL_KINDS:
            techniques.add("HYBRID_NATIVE")
        if _module_matches(module, _TENSOR_MODULE_PREFIXES) or (
            symbol_tokens & _TENSOR_SYMBOL_TOKENS
        ):
            techniques.add("TENSOR_AUTODIFF")
        if _module_matches(module, _PROBABILISTIC_MODULE_PREFIXES) or (
            symbol_tokens & _PROBABILISTIC_SYMBOL_TOKENS
        ):
            techniques.add("PROBABILISTIC_SURROGATE")
        if _module_matches(module, _ITERATIVE_MODULE_PREFIXES) or (
            symbol_tokens & _ITERATIVE_SYMBOL_TOKENS
        ):
            techniques.add("ITERATIVE_STOCHASTIC")
        if _module_matches(module, _ARRAY_MODULE_PREFIXES) or (
            symbol_tokens & _ARRAY_SYMBOL_TOKENS
        ):
            techniques.add("ARRAY_NUMERICAL")
    if call_trace and not techniques:
        techniques.add("SCALAR_CONTROL")
    return sorted(techniques)


def _expected_profiling_runner_sha256(results: list[Mapping[str, Any]]) -> str:
    versions = {row.get("runner_version") for row in results}
    if not results:
        return PHASE1_UNEXECUTED_RUNNER_SHA256
    if versions == {"p3-phase1-unexecuted-v1"}:
        return PHASE1_UNEXECUTED_RUNNER_SHA256
    if versions == {"p3-cxx-header-compile-profiler-v1"}:
        from p3_v3 import profiling_runner

        return file_sha256(Path(profiling_runner.__file__))
    raise EvidenceError("E_PROFILE_RUNNER_BINDING", "runner version is unknown or mixed")


def _validated_profiling_rows(
    workload: Mapping[str, Any], profiling_receipt: Mapping[str, Any]
) -> list[dict[str, Any]]:
    if not isinstance(profiling_receipt, Mapping):
        raise EvidenceError("E_PROFILE_RECEIPT", "profiling receipt must be an object")
    receipt = validate_exact_object(
        dict(profiling_receipt), _PROFILING_RECEIPT_SCHEMA, "profiling_receipt"
    )
    if receipt["schema_version"] != "p3-profiling-results-v1":
        raise EvidenceError("E_PROFILE_RECEIPT", "profiling receipt version differs")
    body = {key: value for key, value in receipt.items() if key != "artifact_sha256"}
    if receipt["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PROFILE_RECEIPT_HASH", "profiling receipt self-hash differs")
    for field in (
        "neutral_snapshot_id",
        "controlled_subject_source_id",
        "normalized_source_tree_sha256",
        "build_descriptor_sha256",
        "profiling_workload_sha256",
        "runner_implementation_source_sha256",
        "artifact_sha256",
    ):
        validate_sha256(receipt[field], f"profiling_receipt.{field}")
    adapter_source = receipt["adapter_implementation_source_sha256"]
    if adapter_source is not None:
        validate_sha256(
            adapter_source,
            "profiling_receipt.adapter_implementation_source_sha256",
        )
    expected_source_id = _controlled_subject_source_id(
        {
            "normalized_source_tree_sha256": receipt[
                "normalized_source_tree_sha256"
            ],
            "build_descriptor_sha256": receipt["build_descriptor_sha256"],
        }
    )
    if (
        receipt["controlled_subject_source_id"] != expected_source_id
        or workload.get("controlled_subject_source_id") != expected_source_id
    ):
        raise EvidenceError(
            "E_PROFILE_SOURCE_BINDING", "profiling receipt source binding differs"
        )
    workload_body = {
        key: value for key, value in workload.items() if key != "artifact_sha256"
    }
    workload_sha256 = workload.get("artifact_sha256")
    validate_sha256(workload_sha256, "profiling_workload.artifact_sha256")
    if workload_sha256 != canonical_sha256(workload_body):
        raise EvidenceError("E_WORKLOAD_HASH", "profiling workload self-hash differs")
    if receipt["profiling_workload_sha256"] != workload_sha256:
        raise EvidenceError(
            "E_PROFILE_WORKLOAD_BINDING", "profiling receipt workload binding differs"
        )
    if receipt["runner_implementation_source_sha256"] != _expected_profiling_runner_sha256(
        receipt["results"]
    ):
        raise EvidenceError(
            "E_PROFILE_RUNNER_BINDING", "profiling runner source binding differs"
        )

    normalized: list[dict[str, Any]] = []
    for index, candidate in enumerate(receipt["results"]):
        if not isinstance(candidate, Mapping):
            raise EvidenceError(
                "E_PROFILE_RESULTS", f"results[{index}] must be an object"
            )
        row = validate_exact_object(
            dict(candidate), _PROFILING_RESULT_SCHEMA, f"profiling_results[{index}]"
        )
        behavior_id = validate_sha256(
            row["behavior_id"], f"profiling_results[{index}].behavior_id"
        )
        if not row["argv"] or any(type(item) is not str for item in row["argv"]):
            raise EvidenceError("E_PROFILE_RESULTS", "profiling argv is invalid")
        for input_index, input_sha256 in enumerate(row["input_sha256"]):
            validate_sha256(
                input_sha256,
                f"profiling_results[{index}].input_sha256[{input_index}]",
            )
        for field in ("environment_sha256", "stdout_sha256", "stderr_sha256"):
            validate_sha256(row[field], f"profiling_results[{index}].{field}")
        if not row["runner_version"]:
            raise EvidenceError("E_PROFILE_RESULTS", "runner version is absent")
        call_trace_sha256 = validate_sha256(
            row["call_trace_sha256"],
            f"profiling_results[{index}].call_trace_sha256",
        )
        call_trace = row["call_trace"]
        if call_trace_sha256 != canonical_sha256(call_trace):
            raise EvidenceError(
                "E_PROFILE_TRACE_HASH", "call trace canonical bytes differ from its hash"
            )
        technique_tags = _techniques_from_call_trace(call_trace)
        observed_sites = row["observed_site_ids"]
        for site_index, site_id in enumerate(observed_sites):
            validate_sha256(
                site_id,
                f"profiling_results[{index}].observed_site_ids[{site_index}]",
            )
        if observed_sites != sorted(set(observed_sites)):
            raise EvidenceError("E_PROFILE_RESULTS", "observed site IDs are not canonical")
        status = row["status"]
        if status == "SUCCESS":
            if (
                row["exit_code"] != 0
                or row["timed_out"]
                or row["failure_code"]
                or not call_trace
            ):
                raise EvidenceError(
                    "E_PROFILE_RESULTS", "successful profiling result is inconsistent"
                )
        elif status in _UNRESOLVED_STATUSES:
            if row["timed_out"] != (status == "TIMEOUT") or not row["failure_code"]:
                raise EvidenceError(
                    "E_PROFILE_RESULTS", "unresolved profiling result is inconsistent"
                )
            if call_trace:
                raise EvidenceError(
                    "E_PROFILE_TRACE", "unresolved result cannot contain a call trace"
                )
        else:
            raise EvidenceError(
                "E_PROFILE_RESULTS", f"unsupported profiling status: {status!r}"
            )
        normalized.append(
            {
                **row,
                "behavior_id": behavior_id,
                "technique_tags": technique_tags,
            }
        )
    if [row["behavior_id"] for row in normalized] != sorted(
        row["behavior_id"] for row in normalized
    ):
        raise EvidenceError("E_PROFILE_RESULTS", "profiling results are not canonical")
    return normalized


def classify_technique(
    workload: Mapping[str, Any],
    profiling_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(workload, Mapping):
        raise EvidenceError("E_WORKLOAD", "profiling workload must be an object")
    selected_rows = workload.get("selected_rows")
    if not isinstance(selected_rows, list):
        raise EvidenceError("E_WORKLOAD", "selected_rows are absent")
    selected: list[dict[str, Any]] = []
    selected_ids: list[str] = []
    seen_ids: set[str] = set()
    for index, candidate in enumerate(selected_rows):
        if not isinstance(candidate, Mapping):
            raise EvidenceError("E_WORKLOAD_ROW", f"selected_rows[{index}] must be an object")
        behavior_id = validate_sha256(
            candidate.get("behavior_id"), f"selected_rows[{index}].behavior_id"
        )
        category = candidate.get("category")
        if category not in _BEHAVIOR_CATEGORIES:
            raise EvidenceError("E_WORKLOAD_ROW", f"selected_rows[{index}] category is invalid")
        if behavior_id in seen_ids:
            raise EvidenceError("E_WORKLOAD_ROW", f"duplicate selected behavior: {behavior_id}")
        seen_ids.add(behavior_id)
        selected.append({"behavior_id": behavior_id, "category": category})
        selected_ids.append(behavior_id)
    profiling_results = _validated_profiling_rows(workload, profiling_receipt)
    results_by_id: dict[str, Mapping[str, Any]] = {}
    for index, candidate in enumerate(profiling_results):
        if not isinstance(candidate, Mapping):
            raise EvidenceError("E_PROFILE_RESULTS", f"profiling_results[{index}] must be an object")
        behavior_id = validate_sha256(
            candidate.get("behavior_id"), f"profiling_results[{index}].behavior_id"
        )
        if behavior_id not in seen_ids:
            raise EvidenceError(
                "E_PROFILE_RESULTS",
                f"result behavior is not in workload: {behavior_id}",
            )
        if behavior_id in results_by_id:
            raise EvidenceError("E_PROFILE_RESULTS", f"duplicate result: {behavior_id}")
        results_by_id[behavior_id] = candidate
    if set(results_by_id) != seen_ids:
        missing = sorted(seen_ids - set(results_by_id))
        raise EvidenceError(
            "E_PROFILE_RESULTS",
            f"profiling results do not cover selected rows: {missing[0]}",
        )

    categories = [
        category
        for category in BEHAVIOR_CATEGORY_ORDER
        if any(row["category"] == category for row in selected)
    ]
    if not categories:
        return {
            "lower_scores": {},
            "upper_scores": {},
            "confirmed_tags": [],
            "possible_tags": [],
            "primary_technique": "TECH_UNCERTAIN",
            "category_funnel": [],
        }

    category_size = Fraction(len(categories))
    lower: dict[str, Fraction] = {technique: Fraction(0) for technique in _PROFILE_TECHNIQUES}
    upper: dict[str, Fraction] = {technique: Fraction(0) for technique in _PROFILE_TECHNIQUES}
    funnel: list[dict[str, Any]] = []
    unresolved_total = 0
    missing_success_category = False

    for category in categories:
        category_rows = [row for row in selected if row["category"] == category]
        n_c = len(category_rows)
        success_count = 0
        unresolved_count = 0
        technique_counts = {technique: 0 for technique in _PROFILE_TECHNIQUES}
        for row in category_rows:
            result = results_by_id[row["behavior_id"]]
            status = result.get("status")
            tags = result.get("technique_tags")
            if status in _UNRESOLVED_STATUSES:
                unresolved_count += 1
                continue
            if status != "SUCCESS":
                raise EvidenceError(
                    "E_PROFILE_RESULTS",
                    f"unsupported profiling status for {row['behavior_id']}: {status!r}",
                )
            success_count += 1
            if tags is None:
                tags = []
            if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
                raise EvidenceError(
                    "E_PROFILE_RESULTS",
                    f"technique_tags must be a string list for {row['behavior_id']}",
                )
            for tag in tags:
                if tag == "TECH_UNCERTAIN":
                    continue
                if tag not in _TECHNIQUES:
                    raise EvidenceError(
                        "E_PROFILE_RESULTS",
                        f"unknown technique tag for {row['behavior_id']}: {tag}",
                    )
                technique_counts[tag] += 1
        if success_count == 0:
            missing_success_category = True
        unresolved_total += unresolved_count
        n_fraction = Fraction(n_c)
        for technique in _PROFILE_TECHNIQUES:
            a_ct = Fraction(technique_counts[technique])
            lower[technique] += (a_ct / n_fraction) / category_size
            upper[technique] += ((a_ct + Fraction(unresolved_count)) / n_fraction) / category_size
        funnel.append(
            {
                "category": category,
                "n_c": n_c,
                "successful_count": success_count,
                "unresolved_count": unresolved_count,
                "technique_counts": {
                    technique: count
                    for technique, count in technique_counts.items()
                    if count > 0
                },
            }
        )

    confirmed_tags = [
        technique for technique in _PROFILE_TECHNIQUES if lower[technique] > 0
    ]
    possible_tags = [
        technique for technique in _PROFILE_TECHNIQUES if upper[technique] > 0
    ]
    lower_scores = {
        technique: _serialize_fraction(lower[technique]) for technique in confirmed_tags
    }
    upper_scores = {
        technique: _serialize_fraction(upper[technique]) for technique in possible_tags
    }

    if missing_success_category:
        primary = "TECH_UNCERTAIN"
    elif unresolved_total == 0:
        best_score = max((lower[technique] for technique in _PROFILE_TECHNIQUES), default=Fraction(0))
        if best_score <= 0:
            primary = "TECH_UNCERTAIN"
        else:
            winners = [
                technique
                for technique in _PROFILE_TECHNIQUES
                if lower[technique] == best_score
            ]
            primary = winners[0]
    else:
        primary = "TECH_UNCERTAIN"
        for technique in _PROFILE_TECHNIQUES:
            rival_upper = max(
                (
                    upper[other]
                    for other in _PROFILE_TECHNIQUES
                    if other != technique
                ),
                default=Fraction(0),
            )
            if lower[technique] > rival_upper:
                primary = technique
                break

    return {
        "lower_scores": lower_scores,
        "upper_scores": upper_scores,
        "confirmed_tags": confirmed_tags,
        "possible_tags": possible_tags,
        "primary_technique": primary,
        "category_funnel": funnel,
    }


def _seed_block(seed: int, counter: int) -> bytes:
    return hashlib.sha256(
        b"P3-INPUT-STREAM-v1" + seed.to_bytes(8, "big") + counter.to_bytes(8, "big")
    ).digest()


def _reject_forbidden_generator_inputs(value: Any, context: str) -> None:
    if isinstance(value, Mapping):
        forbidden = sorted(set(value) & _FORBIDDEN_GENERATOR_INPUT_KEYS)
        if forbidden:
            raise EvidenceError(
                "E_GENERATOR_INPUT",
                f"{context} contains forbidden generator inputs: {forbidden}",
            )
        for key, item in value.items():
            _reject_forbidden_generator_inputs(item, f"{context}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_forbidden_generator_inputs(item, f"{context}[{index}]")


def _validate_input_generator_registry_structure(
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    value = validate_exact_object(
        dict(registry), _GENERATOR_REGISTRY_SCHEMA, "input_generator_registry"
    )
    if value["schema_version"] != "p3-input-generator-registry-v1":
        raise EvidenceError("E_GENERATOR_REGISTRY", "input generator registry version differs")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError(
            "E_GENERATOR_REGISTRY_HASH", "input generator registry self-hash differs"
        )
    generators = value["generators"]
    if not isinstance(generators, list) or len(generators) != len(E_COMMON_GENERATOR_IDS):
        raise EvidenceError(
            "E_GENERATOR_ALLOWLIST",
            "input generator registry must list the five E_COMMON generators exactly",
        )
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, candidate in enumerate(generators):
        entry = validate_exact_object(
            candidate, _GENERATOR_ENTRY_SCHEMA, f"generators[{index}]"
        )
        generator_id = entry["generator_id"]
        if generator_id not in _E_COMMON_GENERATOR_ID_SET:
            raise EvidenceError(
                "E_GENERATOR_ALLOWLIST", f"generator not in E_COMMON allowlist: {generator_id}"
            )
        if generator_id in seen:
            raise EvidenceError("E_GENERATOR_DUPLICATE", f"duplicate generator: {generator_id}")
        seen.add(generator_id)
        if entry["schema_kind"] != generator_id:
            raise EvidenceError(
                "E_GENERATOR_KIND",
                f"schema_kind must equal generator_id for {generator_id}",
            )
        if not isinstance(entry["failure_code"], str) or not entry["failure_code"]:
            raise EvidenceError(
                "E_GENERATOR_FAILURE_CODE", f"failure_code missing for {generator_id}"
            )
        output_schema = entry["output_schema"]
        if output_schema.get("generator_id") != generator_id:
            raise EvidenceError(
                "E_GENERATOR_OUTPUT_SCHEMA",
                f"output_schema.generator_id differs for {generator_id}",
            )
        safe_relative_path(entry["implementation_path"])
        validate_sha256(entry["source_sha256"], f"generators[{index}].source_sha256")
        normalized.append(entry)
    if seen != _E_COMMON_GENERATOR_ID_SET:
        raise EvidenceError("E_GENERATOR_ALLOWLIST", "E_COMMON generator set differs")
    return {
        "schema_version": value["schema_version"],
        "generators": normalized,
        "artifact_sha256": value["artifact_sha256"],
    }


def validate_input_generator_registry(
    registry: Mapping[str, Any], implementation_source: SourceSnapshot
) -> dict[str, Any]:
    value = _validate_input_generator_registry_structure(registry)
    _validate_source_snapshot(implementation_source)
    snapshots = {
        entry["generator_id"]: _implementation_snapshot(
            implementation_source, entry, entry["generator_id"], "generator"
        )
        for entry in value["generators"]
    }
    return {
        **value,
        "_implementation_source": implementation_source,
        "_implementation_snapshots": snapshots,
    }


def _load_input_generator_callable(
    snapshot: _VerifiedImplementationSnapshot, generator_id: str
) -> Callable[[bytes, int], Mapping[str, Any]]:
    namespace = {
        "__name__": f"p3_v3_input_generator_{generator_id.lower()}",
        "__file__": snapshot.logical_filename,
    }
    try:
        exec(
            compile(
                snapshot.source_bytes,
                snapshot.logical_filename,
                "exec",
            ),
            namespace,
        )
    except Exception as exc:
        raise EvidenceError(
            "E_GENERATOR_LOAD", f"unable to load generator: {generator_id}"
        ) from exc
    generate = namespace.get("generate")
    if not callable(generate):
        raise EvidenceError("E_GENERATOR_LOAD", f"generator lacks generate(): {generator_id}")
    return generate


def _common_input_seed(source_id: str, ordinal: int) -> int:
    digest = canonical_sha256(
        {
            "domain": "P3-E-COMMON-SEED-v1",
            "controlled_subject_source_id": source_id,
            "ordinal": ordinal,
        }
    )
    return int.from_bytes(bytes.fromhex(digest)[:8], "big")


def _eligible_public_schemas(
    public_frame: Mapping[str, Any],
    kind_to_generator: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    raw_schemas = public_frame.get("public_schemas")
    if raw_schemas is None:
        raw_schemas = []
    if not isinstance(raw_schemas, list):
        raise EvidenceError("E_PUBLIC_SCHEMAS", "public_schemas must be a list")
    eligible: list[dict[str, Any]] = []
    seen_raw: set[str] = set()
    for index, candidate in enumerate(raw_schemas):
        if not isinstance(candidate, Mapping):
            raise EvidenceError("E_PUBLIC_SCHEMAS", f"public_schemas[{index}] must be an object")
        _reject_forbidden_generator_inputs(candidate, f"public_schemas[{index}]")
        schema_kind = candidate.get("schema_kind")
        if schema_kind not in kind_to_generator:
            continue
        if "raw_schema" not in candidate:
            raise EvidenceError(
                "E_PUBLIC_SCHEMAS", f"public_schemas[{index}] lacks raw_schema"
            )
        raw_schema = candidate["raw_schema"]
        provenance_path = candidate.get("provenance_path")
        provenance_span = candidate.get("provenance_span_or_key")
        if not isinstance(provenance_path, str) or not provenance_path:
            raise EvidenceError(
                "E_PUBLIC_SCHEMAS",
                f"public_schemas[{index}] lacks provenance_path",
            )
        safe_relative_path(provenance_path)
        if not isinstance(provenance_span, str) or not provenance_span:
            raise EvidenceError(
                "E_PUBLIC_SCHEMAS",
                f"public_schemas[{index}] lacks provenance_span_or_key",
            )
        raw_schema_sha256 = canonical_sha256(raw_schema)
        if raw_schema_sha256 in seen_raw:
            continue
        seen_raw.add(raw_schema_sha256)
        selection_body = {
            key: value
            for key, value in candidate.items()
            if key not in _SCHEMA_ALIAS_KEYS
        }
        schema_selection_key = canonical_sha256(selection_body)
        eligible.append(
            {
                "schema_kind": schema_kind,
                "raw_schema": raw_schema,
                "raw_schema_sha256": raw_schema_sha256,
                "schema_selection_key": schema_selection_key,
                "schema_provenance_path": provenance_path,
                "schema_provenance_span_or_key": provenance_span,
                "canonical_schema_bytes": canonical_json_bytes(raw_schema),
                "generator": kind_to_generator[schema_kind],
            }
        )
    eligible.sort(
        key=lambda item: (item["schema_selection_key"], item["raw_schema_sha256"])
    )
    return eligible


def _common_input_id(
    source_id: str,
    ordinal: int,
    *,
    generator_id: str | None,
    schema_selection_key: str | None,
    raw_schema_sha256: str | None,
    schema_provenance_path: str | None,
    schema_provenance_span_or_key: str | None,
    generator_source_sha256: str | None,
    raw_payload_sha256: str | None,
    status: str,
    failure_code: str,
) -> str:
    return canonical_sha256(
        {
            "controlled_subject_source_id": source_id,
            "ordinal": ordinal,
            "generator_id": generator_id,
            "schema_selection_key": schema_selection_key,
            "raw_schema_sha256": raw_schema_sha256,
            "schema_provenance_path": schema_provenance_path,
            "schema_provenance_span_or_key": schema_provenance_span_or_key,
            "generator_source_sha256": generator_source_sha256,
            "raw_payload_sha256": raw_payload_sha256,
            "status": status,
            "failure_code": failure_code,
            "domain": "P3-E-COMMON-INPUT-v1",
        }
    )


def build_common_inputs(
    source_record: Mapping[str, Any],
    public_frame: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    source = validate_exact_object(dict(source_record), _SOURCE_RECORD_SCHEMA, "source_record")
    validate_sha256(source["normalized_source_tree_sha256"], "normalized_source_tree_sha256")
    validate_sha256(source["build_descriptor_sha256"], "build_descriptor_sha256")
    if not isinstance(public_frame, Mapping):
        raise EvidenceError("E_FRAME", "public behavior frame must be an object")
    implementation_source = (
        registry.get("_implementation_source")
        if isinstance(registry, Mapping)
        else None
    )
    implementation_snapshots = (
        registry.get("_implementation_snapshots")
        if isinstance(registry, Mapping)
        else None
    )
    registry_body = {
        key: value
        for key, value in dict(registry).items()
        if key not in {"_implementation_source", "_implementation_snapshots"}
    }
    validated_registry = _validate_input_generator_registry_structure(
        registry_body
    )
    if {
        entry["generator_id"] for entry in validated_registry["generators"]
    } != _E_COMMON_GENERATOR_ID_SET:
        raise EvidenceError("E_GENERATOR_ALLOWLIST", "input generator registry is incomplete")
    validated_registry = {
        **validated_registry,
        "_implementation_source": implementation_source,
        "_implementation_snapshots": implementation_snapshots,
    }
    snapshots = _validated_snapshot_map(
        validated_registry,
        validated_registry["generators"],
        "generator_id",
        "E_GENERATOR_REGISTRY",
    )
    source_id = _controlled_subject_source_id(source)
    frame_source_id = public_frame.get("controlled_subject_source_id")
    if frame_source_id != source_id:
        raise EvidenceError(
            "E_FRAME_SOURCE",
            "public frame controlled_subject_source_id differs from source_record",
        )
    discovery_status = public_frame.get("discovery_status")
    if discovery_status not in {
        "EXECUTABLE",
        "ADAPTER_UNSUPPORTED",
        "ADAPTER_EXECUTION_FAILED",
    }:
        raise EvidenceError("E_FRAME", "public frame discovery status is invalid")
    kind_to_generator = {
        entry["schema_kind"]: entry for entry in validated_registry["generators"]
    }
    eligible = _eligible_public_schemas(public_frame, kind_to_generator)
    if discovery_status in {"ADAPTER_UNSUPPORTED", "ADAPTER_EXECUTION_FAILED"} and eligible:
        raise EvidenceError(
            "E_FRAME", "unsupported discovery cannot carry eligible public schemas"
        )
    rows: list[dict[str, Any]] = []
    if not eligible:
        for ordinal in range(E_COMMON_COUNT):
            seed = _common_input_seed(source_id, ordinal)
            status = "COMMON_INPUT_UNAVAILABLE"
            failure_code = "COMMON_INPUT_UNAVAILABLE"
            input_id = _common_input_id(
                source_id,
                ordinal,
                generator_id=None,
                schema_selection_key=None,
                raw_schema_sha256=None,
                schema_provenance_path=None,
                schema_provenance_span_or_key=None,
                generator_source_sha256=None,
                raw_payload_sha256=None,
                status=status,
                failure_code=failure_code,
            )
            rows.append(
                {
                    "ordinal": ordinal,
                    "seed": seed,
                    "generator_id": None,
                    "schema_kind": None,
                    "schema_selection_key": None,
                    "raw_schema_sha256": None,
                    "schema_provenance_path": None,
                    "schema_provenance_span_or_key": None,
                    "generator_source_sha256": None,
                    "status": status,
                    "failure_code": failure_code,
                    "envelope": None,
                    "raw_payload_sha256": None,
                    "input_id": input_id,
                }
            )
    else:
        callables: dict[str, Callable[[bytes, int], Mapping[str, Any]]] = {}
        selected_generator_ids = {
            item["generator"]["generator_id"] for item in eligible
        }
        for entry in validated_registry["generators"]:
            generator_id = entry["generator_id"]
            if generator_id not in _E_COMMON_GENERATOR_ID_SET:
                raise EvidenceError(
                    "E_GENERATOR_ALLOWLIST",
                    f"unregistered generator dispatch: {generator_id}",
                )
            if generator_id in selected_generator_ids:
                snapshot = snapshots[generator_id]
                callables[generator_id] = _execute_verified_python(
                    lambda snapshot=snapshot, generator_id=generator_id: (
                        _load_input_generator_callable(snapshot, generator_id)
                    )
                )

        for ordinal in range(E_COMMON_COUNT):
            seed = _common_input_seed(source_id, ordinal)
            schema = eligible[ordinal % len(eligible)]
            generator_entry = schema["generator"]
            generator_id = generator_entry["generator_id"]
            failure_code = generator_entry["failure_code"]
            generate = callables[generator_id]
            try:
                result = _execute_verified_python(
                    lambda: generate(schema["canonical_schema_bytes"], seed)
                )
            except EvidenceError:
                raise
            except Exception:  # noqa: BLE001 - generator failures occupy the ordinal
                result = {"failure_code": failure_code}
            if not isinstance(result, Mapping):
                result = {"failure_code": failure_code}
            if result.get("failure_code"):
                status = "COMMON_INPUT_INVALID"
                code = str(result.get("failure_code") or failure_code)
                envelope = None
                raw_payload_sha256 = None
            elif "envelope" in result and "raw_payload_sha256" in result:
                status = "COMMON_INPUT_EXECUTABLE"
                code = ""
                envelope = result["envelope"]
                raw_payload_sha256 = validate_sha256(
                    result["raw_payload_sha256"], "raw_payload_sha256"
                )
            else:
                status = "COMMON_INPUT_INVALID"
                code = failure_code
                envelope = None
                raw_payload_sha256 = None
            input_id = _common_input_id(
                source_id,
                ordinal,
                generator_id=generator_id,
                schema_selection_key=schema["schema_selection_key"],
                raw_schema_sha256=schema["raw_schema_sha256"],
                schema_provenance_path=schema["schema_provenance_path"],
                schema_provenance_span_or_key=schema[
                    "schema_provenance_span_or_key"
                ],
                generator_source_sha256=generator_entry["source_sha256"],
                raw_payload_sha256=raw_payload_sha256,
                status=status,
                failure_code=code,
            )
            rows.append(
                {
                    "ordinal": ordinal,
                    "seed": seed,
                    "generator_id": generator_id,
                    "schema_kind": schema["schema_kind"],
                    "schema_selection_key": schema["schema_selection_key"],
                    "raw_schema_sha256": schema["raw_schema_sha256"],
                    "schema_provenance_path": schema["schema_provenance_path"],
                    "schema_provenance_span_or_key": schema[
                        "schema_provenance_span_or_key"
                    ],
                    "generator_source_sha256": generator_entry["source_sha256"],
                    "status": status,
                    "failure_code": code,
                    "envelope": envelope,
                    "raw_payload_sha256": raw_payload_sha256,
                    "input_id": input_id,
                }
            )

    if (
        discovery_status == "EXECUTABLE"
        and eligible
        and not any(
            row["status"] == "COMMON_INPUT_EXECUTABLE" for row in rows
        )
    ):
        raise EvidenceError(
            "E_COMMON_EXECUTABLE",
            "supported subject produced no executable common input",
        )
    body = {
        "schema_version": "p3-evaluation-inputs-common-v1",
        "controlled_subject_source_id": source_id,
        "eligible_schema_count": len(eligible),
        "rows": rows,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _bind_artifact(
    artifact: Mapping[str, Any], bindings: Mapping[str, Any]
) -> dict[str, Any]:
    body = {
        **{key: value for key, value in artifact.items() if key != "artifact_sha256"},
        **bindings,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def derive_subject_material(
    subject_spec: Mapping[str, Any], bridge_record: Mapping[str, Any]
) -> dict[str, Any]:
    """Derive one subject solely from verified source/build material."""

    if not isinstance(subject_spec, Mapping):
        raise EvidenceError("E_SUBJECT_SPEC", "subject_spec must be an object")
    spec = validate_exact_object(
        dict(subject_spec), _SUBJECT_SPEC_SCHEMA, "subject_spec"
    )
    record = validate_exact_object(
        dict(bridge_record), _RECORD_SCHEMA, "bridge_record"
    )
    neutral = validate_sha256(
        spec["neutral_snapshot_id"], "subject_spec.neutral_snapshot_id"
    )
    if neutral != record["neutral_snapshot_id"]:
        raise EvidenceError("E_SUBJECT_SPEC_BINDING", "neutral snapshot ID differs")
    source_record = validate_exact_object(
        spec["source_record"], _SOURCE_RECORD_SCHEMA, "subject_spec.source_record"
    )
    for field in ("normalized_source_tree_sha256", "build_descriptor_sha256"):
        validate_sha256(source_record[field], f"subject_spec.source_record.{field}")
        if source_record[field] != record[field]:
            raise EvidenceError(
                "E_SUBJECT_SPEC_BINDING", f"subject source binding differs: {field}"
            )
    if not isinstance(spec["build_descriptor"], Mapping):
        raise EvidenceError("E_BUILD_DESCRIPTOR", "build_descriptor must be an object")
    if canonical_sha256(spec["build_descriptor"]) != record["build_descriptor_sha256"]:
        raise EvidenceError(
            "E_BUILD_DESCRIPTOR_COMMITMENT", "build descriptor commitment differs"
        )
    source_snapshot = spec["source_snapshot"]
    _validate_source_snapshot(source_snapshot)
    if canonical_source_tree_sha256(source_snapshot) != record[
        "normalized_source_tree_sha256"
    ]:
        raise EvidenceError(
            "E_SOURCE_TREE_COMMITMENT", "normalized source-tree commitment differs"
        )
    ecosystem = spec["build_descriptor"].get("ecosystem")
    if not isinstance(ecosystem, str) or not ecosystem:
        raise EvidenceError("E_BUILD_DESCRIPTOR", "build_descriptor ecosystem is absent")
    adapter_registry = spec["adapter_registry"]
    generator_registry = spec["input_generator_registry"]
    if not isinstance(adapter_registry, Mapping):
        raise EvidenceError("E_ADAPTER_REGISTRY", "adapter_registry must be an object")
    if not isinstance(generator_registry, Mapping):
        raise EvidenceError(
            "E_GENERATOR_REGISTRY", "input_generator_registry must be an object"
        )
    if not isinstance(adapter_registry.get("adapters"), list):
        raise EvidenceError("E_ADAPTER_REGISTRY", "adapter registry entries are absent")
    adapter_id = _ecosystem_to_adapter(adapter_registry).get(ecosystem)
    source_id = _controlled_subject_source_id(source_record)
    raw_discovery = discover_subject_or_fail_closed(
        source_snapshot,
        spec["build_descriptor"],
        adapter_registry,
        adapter_id,
    )
    discovery = _bind_artifact(
        raw_discovery,
        {
            "neutral_snapshot_id": neutral,
            "controlled_subject_source_id": source_id,
            "normalized_source_tree_sha256": record[
                "normalized_source_tree_sha256"
            ],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
            "adapter_registry_sha256": adapter_registry["artifact_sha256"],
        },
    )
    raw_public_frame = build_public_behavior_frame(source_record, raw_discovery)
    public_frame = _bind_artifact(
        raw_public_frame,
        {
            "adapter_discovery_sha256": discovery["artifact_sha256"],
        },
    )
    raw_source_scale = derive_source_scale(source_snapshot, raw_discovery)
    source_scale = _bind_artifact(
        raw_source_scale,
        {
            "neutral_snapshot_id": neutral,
            "controlled_subject_source_id": source_id,
            "normalized_source_tree_sha256": record[
                "normalized_source_tree_sha256"
            ],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
            "discovery_sha256": discovery["artifact_sha256"],
        },
    )
    workload = select_profiling_workload(public_frame, source_scale["scale_class"])
    common_inputs = build_common_inputs(
        source_record, public_frame, generator_registry
    )
    profiling_receipt = spec["profiling_results"]
    technique_body = classify_technique(workload, profiling_receipt)
    if (
        profiling_receipt["neutral_snapshot_id"] != neutral
        or profiling_receipt["normalized_source_tree_sha256"]
        != record["normalized_source_tree_sha256"]
        or profiling_receipt["build_descriptor_sha256"]
        != record["build_descriptor_sha256"]
    ):
        raise EvidenceError(
            "E_PROFILE_SUBJECT_BINDING", "profiling receipt subject binding differs"
        )
    if (
        profiling_receipt["adapter_implementation_source_sha256"]
        != discovery["implementation_source_sha256"]
    ):
        raise EvidenceError(
            "E_PROFILE_ADAPTER_BINDING", "profiling receipt adapter binding differs"
        )
    technique_profile = _bind_artifact(
        technique_body,
        {
            "neutral_snapshot_id": neutral,
            "controlled_subject_source_id": source_id,
            "normalized_source_tree_sha256": record[
                "normalized_source_tree_sha256"
            ],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
            "adapter_discovery_sha256": discovery["artifact_sha256"],
            "profiling_workload_sha256": workload["artifact_sha256"],
            "profiling_results_sha256": profiling_receipt["artifact_sha256"],
        },
    )
    primary = technique_profile["primary_technique"]
    technique_vector = sorted(set(technique_profile["confirmed_tags"]) | {primary})
    subject_seed = {
        "public_workload_set_sha256": workload["artifact_sha256"],
    }
    subject_id = _controlled_subject_id(record, subject_seed)
    subject = {
        "controlled_subject_id": subject_id,
        "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
        "build_descriptor_sha256": record["build_descriptor_sha256"],
        "public_workload_set_sha256": workload["artifact_sha256"],
        "scale_class": source_scale["scale_class"],
        "primary_technique": primary,
        "technique_vector": technique_vector,
        "sites": _sites(subject_id, discovery["sites"]),
        "neutral_snapshot_ids": [neutral],
    }
    body = {
        "neutral_snapshot_id": neutral,
        "controlled_subject_source_id": source_id,
        "adapter_discovery": discovery,
        "adapter_discovery_sha256": discovery["artifact_sha256"],
        "source_scale": source_scale,
        "source_scale_sha256": source_scale["artifact_sha256"],
        "public_behavior_frame": public_frame,
        "public_behavior_frame_sha256": public_frame["artifact_sha256"],
        "profiling_workload": workload,
        "profiling_workload_sha256": workload["artifact_sha256"],
        "common_inputs": common_inputs,
        "common_inputs_sha256": common_inputs["artifact_sha256"],
        "profiling_results": profiling_receipt,
        "profiling_results_sha256": profiling_receipt["artifact_sha256"],
        "technique_profile": technique_profile,
        "technique_profile_sha256": technique_profile["artifact_sha256"],
        "subject": subject,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def rebuild_indexed_subject(
    subject_index: Mapping[str, Any], bridge_record: Mapping[str, Any]
) -> dict[str, Any]:
    """Rebuild every deterministic subject artifact from indexed source bytes."""

    try:
        indexed = validate_exact_object(
            dict(subject_index),
            _INDEXED_SUBJECT_REBUILD_SCHEMA,
            "subject_index",
        )
        adapter_registry = _consume_verified_registry(
            indexed["adapter_registry"], registry_kind="adapter"
        )
        generator_registry = _consume_verified_registry(
            indexed["input_generator_registry"], registry_kind="input_generator"
        )
        rebuilt = derive_subject_material(
            {
                "neutral_snapshot_id": bridge_record.get("neutral_snapshot_id"),
                "source_snapshot": indexed["source_snapshot"],
                "source_record": indexed["source_record"],
                "build_descriptor": indexed["build_descriptor"],
                "adapter_registry": adapter_registry,
                "input_generator_registry": generator_registry,
                "profiling_results": indexed["profiling_results"],
            },
            bridge_record,
        )
    except EvidenceError as exc:
        raise EvidenceError(
            "E_INDEXED_SUBJECT_REDERIVATION",
            f"indexed subject cannot be rebuilt: {exc.code}",
        ) from exc

    declared = {
        "adapter_discovery": indexed["adapter_discovery"],
        "source_scale": indexed["source_scale"],
        "public_behavior_frame": indexed["public_frame"],
        "profiling_workload": indexed["profiling_workload"],
        "common_inputs": indexed["common_inputs"],
        "profiling_results": indexed["profiling_results"],
        "technique_profile": indexed["technique_profile"],
        "subject": indexed["subject"],
    }
    for field, artifact in declared.items():
        if canonical_json_bytes(artifact) != canonical_json_bytes(rebuilt[field]):
            raise EvidenceError(
                "E_INDEXED_SUBJECT_REDERIVATION",
                f"indexed {field} differs from source-derived bytes",
            )
    if canonical_json_bytes(indexed["sites"]) != canonical_json_bytes(
        rebuilt["subject"]["sites"]
    ):
        raise EvidenceError(
            "E_INDEXED_SUBJECT_REDERIVATION",
            "indexed sites differ from source-derived sites",
        )
    return rebuilt


def validate_common_inputs_on_fixed_source(
    inventory: Mapping[str, Any],
    validator: Callable[[Mapping[str, Any]], str],
    *,
    sites: Any = None,
    contracts: Any = None,
    profile: Any = None,
    frame_artifact_sha256: str | None = None,
) -> dict[str, Any]:
    if not isinstance(inventory, Mapping) or "rows" not in inventory:
        raise EvidenceError("E_COMMON_INVENTORY", "common input inventory rows are absent")
    rows = inventory["rows"]
    if not isinstance(rows, list) or len(rows) != E_COMMON_COUNT:
        raise EvidenceError(
            "E_COMMON_INVENTORY",
            f"common input inventory must contain exactly {E_COMMON_COUNT} rows",
        )
    source_id = inventory.get("controlled_subject_source_id")
    validate_sha256(source_id, "controlled_subject_source_id")
    report_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise EvidenceError("E_COMMON_INVENTORY", f"rows[{index}] must be an object")
        if row.get("ordinal") != index:
            raise EvidenceError("E_COMMON_INVENTORY", f"rows[{index}] ordinal differs")
        status = validator(row)
        if status not in {
            "COMMON_INPUT_EXECUTABLE",
            "COMMON_INPUT_INVALID",
            "COMMON_INPUT_UNAVAILABLE",
        }:
            raise EvidenceError(
                "E_COMMON_VALIDITY",
                f"validator returned unsupported status for ordinal {index}: {status!r}",
            )
        # Preserve payload identity; never replace the row.
        report_rows.append(
            {
                "ordinal": row["ordinal"],
                "input_id": row["input_id"],
                "raw_payload_sha256": row.get("raw_payload_sha256"),
                "envelope": row.get("envelope"),
                "generator_id": row.get("generator_id"),
                "schema_kind": row.get("schema_kind"),
                "schema_selection_key": row.get("schema_selection_key"),
                "raw_schema_sha256": row.get("raw_schema_sha256"),
                "seed": row.get("seed"),
                "status": status,
                "failure_code": row.get("failure_code", ""),
            }
        )
    body = {
        "schema_version": "p3-common-input-validity-v1",
        "controlled_subject_source_id": source_id,
        "inventory_artifact_sha256": inventory.get("artifact_sha256"),
        "rows": report_rows,
        "sites": sites,
        "contracts": contracts,
        "profile": profile,
        "frame_artifact_sha256": frame_artifact_sha256,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _validate_contract_generator_registry_structure(
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    value = validate_exact_object(
        dict(registry), _GENERATOR_REGISTRY_SCHEMA, "contract_generator_registry"
    )
    if value["schema_version"] != "p3-contract-generator-registry-v1":
        raise EvidenceError(
            "E_GENERATOR_REGISTRY", "contract generator registry version differs"
        )
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError(
            "E_GENERATOR_REGISTRY_HASH",
            "contract generator registry self-hash differs",
        )
    generators = value["generators"]
    if not isinstance(generators, list) or len(generators) != len(E_CONTRACT_GENERATOR_IDS):
        raise EvidenceError(
            "E_GENERATOR_ALLOWLIST",
            "contract generator registry must list the five E_CONTRACT generators exactly",
        )
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, candidate in enumerate(generators):
        entry = validate_exact_object(
            candidate, _GENERATOR_ENTRY_SCHEMA, f"generators[{index}]"
        )
        generator_id = entry["generator_id"]
        if generator_id not in _E_CONTRACT_GENERATOR_ID_SET:
            raise EvidenceError(
                "E_GENERATOR_ALLOWLIST",
                f"generator not in E_CONTRACT allowlist: {generator_id}",
            )
        if generator_id in seen:
            raise EvidenceError("E_GENERATOR_DUPLICATE", f"duplicate generator: {generator_id}")
        seen.add(generator_id)
        if entry["schema_kind"] != generator_id:
            raise EvidenceError(
                "E_GENERATOR_KIND",
                f"schema_kind must equal generator_id for {generator_id}",
            )
        if not isinstance(entry["failure_code"], str) or not entry["failure_code"]:
            raise EvidenceError(
                "E_GENERATOR_FAILURE_CODE", f"failure_code missing for {generator_id}"
            )
        output_schema = entry["output_schema"]
        if output_schema.get("generator_id") != generator_id:
            raise EvidenceError(
                "E_GENERATOR_OUTPUT_SCHEMA",
                f"output_schema.generator_id differs for {generator_id}",
            )
        safe_relative_path(entry["implementation_path"])
        validate_sha256(entry["source_sha256"], f"generators[{index}].source_sha256")
        normalized.append(entry)
    if seen != _E_CONTRACT_GENERATOR_ID_SET:
        raise EvidenceError("E_GENERATOR_ALLOWLIST", "E_CONTRACT generator set differs")
    return {
        "schema_version": value["schema_version"],
        "generators": normalized,
        "artifact_sha256": value["artifact_sha256"],
    }


def validate_contract_generator_registry(
    registry: Mapping[str, Any], source_root: str | Path
) -> dict[str, Any]:
    value = _validate_contract_generator_registry_structure(registry)
    root = Path(source_root)
    if not root.is_absolute():
        root = Path.cwd() / root
    snapshots = {
        entry["generator_id"]: _path_implementation_snapshot(
            root, entry, entry["generator_id"], "generator"
        )
        for entry in value["generators"]
    }
    return {
        **value,
        "_source_root": str(root),
        "_implementation_snapshots": snapshots,
    }


def close_slot(
    slot: Mapping[str, Any],
    canonical_sites: Sequence[Mapping[str, Any]],
    applicability_predicate: Callable[[Mapping[str, Any]], bool],
) -> dict[str, Any]:
    value = validate_exact_object(dict(slot), _SLOT_SCHEMA, "slot")
    validate_sha256(value["slot_id"], "slot.slot_id")
    validate_sha256(value["controlled_subject_id"], "slot.controlled_subject_id")
    site_id = select_first_applicable_site(canonical_sites, applicability_predicate)
    if site_id is None:
        body = {
            "schema_version": "p3-slot-closure-v1",
            "slot_id": value["slot_id"],
            "controlled_subject_id": value["controlled_subject_id"],
            "site_id": None,
            "state": "APPLICABILITY_CLOSED_NOT_APPLICABLE",
            "path": "APPLICABILITY_CLOSED_NOT_APPLICABLE",
        }
    else:
        body = {
            "schema_version": "p3-slot-closure-v1",
            "slot_id": value["slot_id"],
            "controlled_subject_id": value["controlled_subject_id"],
            "site_id": site_id,
            "state": "SITE_FROZEN",
            "path": "APPLICABLE",
        }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _contract_input_seed(subject_id: str, slot_id: str, ordinal: int) -> int:
    digest = canonical_sha256(
        {
            "domain": "P3-E-CONTRACT-SEED-v1",
            "controlled_subject_id": subject_id,
            "slot_id": slot_id,
            "ordinal": ordinal,
        }
    )
    return int.from_bytes(bytes.fromhex(digest)[:8], "big")


def _contract_input_id(
    subject_id: str,
    slot_id: str,
    ordinal: int,
    *,
    generator_id: str | None,
    domain_sha256: str | None,
    raw_payload_sha256: str | None,
    status: str,
    failure_code: str,
) -> str:
    return canonical_sha256(
        {
            "controlled_subject_id": subject_id,
            "slot_id": slot_id,
            "ordinal": ordinal,
            "generator_id": generator_id,
            "domain_sha256": domain_sha256,
            "raw_payload_sha256": raw_payload_sha256,
            "status": status,
            "failure_code": failure_code,
            "domain": "P3-E-CONTRACT-INPUT-v1",
        }
    )


def _domain_is_unsupported(domain: Mapping[str, Any]) -> bool:
    return domain.get("unsupported_domain") is True


def build_contract_inputs(
    applicable_slot: Mapping[str, Any],
    contract: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(applicable_slot, Mapping):
        raise EvidenceError("E_SLOT", "applicable_slot must be an object")
    if applicable_slot.get("path") != "APPLICABLE" or applicable_slot.get("state") != "SITE_FROZEN":
        raise EvidenceError(
            "E_SLOT_PATH",
            "contract inputs require an applicable SITE_FROZEN slot",
        )
    slot_id = validate_sha256(applicable_slot.get("slot_id"), "applicable_slot.slot_id")
    subject_id = validate_sha256(
        applicable_slot.get("controlled_subject_id"),
        "applicable_slot.controlled_subject_id",
    )
    site_id = validate_sha256(applicable_slot.get("site_id"), "applicable_slot.site_id")
    frozen = validate_exact_object(dict(contract), _CONTRACT_SCHEMA, "contract")
    validate_sha256(frozen["contract_id"], "contract.contract_id")
    validate_sha256(frozen["site_id"], "contract.site_id")
    if frozen["site_id"] != site_id:
        raise EvidenceError(
            "E_SLOT_SITE",
            "contract site_id differs from frozen applicable slot site",
        )
    _reject_forbidden_generator_inputs(frozen, "contract")
    registry_source_root = registry.get("_source_root") if isinstance(registry, Mapping) else None
    implementation_snapshots = (
        registry.get("_implementation_snapshots")
        if isinstance(registry, Mapping)
        else None
    )
    registry_body = {
        key: value
        for key, value in dict(registry).items()
        if key not in {"_source_root", "_implementation_snapshots"}
    }
    validated_registry = _validate_contract_generator_registry_structure(
        registry_body
    )
    if {
        entry["generator_id"] for entry in validated_registry["generators"]
    } != _E_CONTRACT_GENERATOR_ID_SET:
        raise EvidenceError(
            "E_GENERATOR_ALLOWLIST", "contract generator registry is incomplete"
        )
    validated_registry = {
        **validated_registry,
        "_source_root": registry_source_root,
        "_implementation_snapshots": implementation_snapshots,
    }
    snapshots = _validated_snapshot_map(
        validated_registry,
        validated_registry["generators"],
        "generator_id",
        "E_GENERATOR_REGISTRY",
    )
    generator_id = frozen["generator_id"]
    domain = frozen["domain"]
    domain_sha256 = canonical_sha256(domain)
    unsupported = (
        generator_id not in _E_CONTRACT_GENERATOR_ID_SET or _domain_is_unsupported(domain)
    )
    rows: list[dict[str, Any]] = []
    if unsupported:
        for ordinal in range(E_CONTRACT_COUNT):
            seed = _contract_input_seed(subject_id, slot_id, ordinal)
            status = "CONTRACT_INPUT_UNAVAILABLE"
            failure_code = "CONTRACT_INPUT_UNAVAILABLE"
            input_id = _contract_input_id(
                subject_id,
                slot_id,
                ordinal,
                generator_id=None,
                domain_sha256=domain_sha256,
                raw_payload_sha256=None,
                status=status,
                failure_code=failure_code,
            )
            rows.append(
                {
                    "ordinal": ordinal,
                    "seed": seed,
                    "generator_id": None,
                    "schema_kind": None,
                    "domain_sha256": domain_sha256,
                    "status": status,
                    "failure_code": failure_code,
                    "envelope": None,
                    "raw_payload_sha256": None,
                    "input_id": input_id,
                }
            )
    else:
        kind_to_generator = {
            entry["generator_id"]: entry for entry in validated_registry["generators"]
        }
        generator_entry = kind_to_generator[generator_id]
        snapshot = snapshots[generator_id]
        generate = _execute_verified_python(
            lambda: _load_input_generator_callable(snapshot, generator_id)
        )
        domain_bytes = canonical_json_bytes(domain)
        failure_code = generator_entry["failure_code"]
        for ordinal in range(E_CONTRACT_COUNT):
            seed = _contract_input_seed(subject_id, slot_id, ordinal)
            try:
                result = _execute_verified_python(
                    lambda: generate(domain_bytes, seed)
                )
            except EvidenceError:
                raise
            except Exception:  # noqa: BLE001 - generator failures occupy the ordinal
                result = {"failure_code": failure_code}
            if not isinstance(result, Mapping):
                result = {"failure_code": failure_code}
            result_failure = result.get("failure_code")
            if result_failure == "CONTRACT_INPUT_UNAVAILABLE":
                status = "CONTRACT_INPUT_UNAVAILABLE"
                code = "CONTRACT_INPUT_UNAVAILABLE"
                envelope = None
                raw_payload_sha256 = None
                row_generator_id = None
                row_schema_kind = None
            elif result_failure:
                status = "CONTRACT_INPUT_INVALID"
                code = str(result_failure)
                envelope = None
                raw_payload_sha256 = None
                row_generator_id = generator_id
                row_schema_kind = generator_id
            elif "envelope" in result and "raw_payload_sha256" in result:
                status = "CONTRACT_INPUT_GENERATED"
                code = ""
                envelope = result["envelope"]
                raw_payload_sha256 = validate_sha256(
                    result["raw_payload_sha256"], "raw_payload_sha256"
                )
                row_generator_id = generator_id
                row_schema_kind = generator_id
            else:
                status = "CONTRACT_INPUT_INVALID"
                code = failure_code
                envelope = None
                raw_payload_sha256 = None
                row_generator_id = generator_id
                row_schema_kind = generator_id
            input_id = _contract_input_id(
                subject_id,
                slot_id,
                ordinal,
                generator_id=row_generator_id,
                domain_sha256=domain_sha256,
                raw_payload_sha256=raw_payload_sha256,
                status=status,
                failure_code=code,
            )
            rows.append(
                {
                    "ordinal": ordinal,
                    "seed": seed,
                    "generator_id": row_generator_id,
                    "schema_kind": row_schema_kind,
                    "domain_sha256": domain_sha256,
                    "status": status,
                    "failure_code": code,
                    "envelope": envelope,
                    "raw_payload_sha256": raw_payload_sha256,
                    "input_id": input_id,
                }
            )

    body = {
        "schema_version": "p3-evaluation-inputs-contract-v1",
        "controlled_subject_id": subject_id,
        "slot_id": slot_id,
        "site_id": site_id,
        "contract_id": frozen["contract_id"],
        "rows": rows,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def verify_slot_chronology(slot_artifacts: Mapping[str, Any]) -> None:
    artifacts = validate_exact_object(
        dict(slot_artifacts), _SLOT_ARTIFACTS_SCHEMA, "slot_artifacts"
    )
    validate_sha256(artifacts["slot_id"], "slot_artifacts.slot_id")
    chronology = artifacts["chronology"]
    if chronology == list(NOT_APPLICABLE_SLOT_CHRONOLOGY):
        for field in ("contract", "e_contract", "patch", "certification_witness"):
            if artifacts[field] is not None:
                raise EvidenceError(
                    "E_SLOT_CHRONOLOGY",
                    f"NOT_APPLICABLE slot must not carry {field}",
                )
        return
    if chronology != list(APPLICABLE_SLOT_CHRONOLOGY):
        raise EvidenceError(
            "E_SLOT_CHRONOLOGY",
            "slot chronology must be exactly one of the two frozen paths",
        )
    if artifacts["contract"] is None:
        raise EvidenceError("E_SLOT_CHRONOLOGY", "applicable slot missing frozen contract")
    if artifacts["e_contract"] is None:
        raise EvidenceError(
            "E_SLOT_CHRONOLOGY",
            "applicable slot missing E_CONTRACT before patch",
        )
    if artifacts["patch"] is None:
        raise EvidenceError("E_SLOT_CHRONOLOGY", "applicable slot missing frozen patch")
    if artifacts["certification_witness"] is None:
        raise EvidenceError(
            "E_SLOT_CHRONOLOGY",
            "applicable slot missing certification witness",
        )
    e_contract = artifacts["e_contract"]
    if not isinstance(e_contract, Mapping) or "rows" not in e_contract:
        raise EvidenceError("E_SLOT_CHRONOLOGY", "E_CONTRACT inventory rows are absent")
    common_ids = artifacts["e_common_input_ids"]
    contract_ids = artifacts["e_contract_input_ids"]
    if any(not isinstance(item, str) for item in common_ids + contract_ids):
        raise EvidenceError("E_SLOT_CHRONOLOGY", "input inventory IDs must be strings")
    inventory_ids = set(common_ids) | set(contract_ids)
    witness = artifacts["certification_witness"]
    if not isinstance(witness, Mapping):
        raise EvidenceError("E_SLOT_CHRONOLOGY", "certification witness must be an object")
    witness_identity = witness.get("witness_id")
    if not isinstance(witness_identity, str) or not witness_identity:
        raise EvidenceError("E_SLOT_CHRONOLOGY", "certification witness_id missing")
    if witness_identity in inventory_ids:
        raise EvidenceError(
            "E_WITNESS_INVENTORY",
            "post-patch witness identity appears in an input inventory",
        )
