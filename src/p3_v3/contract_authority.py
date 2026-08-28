"""Outcome-blind contract authority for the first eligible C3 v2 subject."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from p3_v3.artifacts import EvidenceError, canonical_sha256, validate_sha256
from p3_v3.bridge_and_frames import build_contract_inputs

ORDINAL8_SUBJECT_ID = "0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48"
CONTRACT_DOMAIN = "P3-CONTRACT-v1"
CONTRACT_REGISTRY_ARTIFACT_SHA256 = (
    "1ab44d2e0627e7ab58325dd3d48c282132fc6c9c275530021fafba53affbbb97"
)

_SLOT_ORDER = (
    "a2f7a2164e7968cb5a6edf0aafa9bb406b8ba089df79cccdc565bdd9164cd913",
    "e8fd94d60c42ed7357d8e00ebc1135b55b44dbde4978f887ab54abe94b261c6c",
    "77f69dc9343febceb4f3f5163d6da260dbb08ed3e1a08bd30828bec11d9ca40a",
    "07546603ddbc9fca6e73bc7f7e551fa52f9dfd94c648c19e7b96cb12bcb0aac0",
    "dcb97c96442fc4fb63f749667ebb9db5eb4c5df8bfe66fc6532848b2c57e270e",
    "d321563a43ccefbbbd327f2e419279642243f89a279848fa3df4ad8ec18cb8ef",
    "c97950fc2ea22c2e9c2b51be527f9ecbb1d40021fa4225bda1f1aae6fa4c981e",
    "e79a25d80eb20c476124cf5518eb52554233a4c8cd1fef8f2dfd937f342294ac",
    "e0b42ce7f2c60d9b3d0feae5ce3280d1619ec78b75c22c3e41fc6c936c3485e6",
    "06556e4b744f26766ef8593fc4ae727103082944ae6b26c6179fc947c3a2f1f5",
)
_INV_SITE = "f37fc591deeeadf562c46130a6cc598ca142c552bbadd1d66b0d5b0d143e2fd3"
_MONO_SITE = "4cb47f51680a67b3c0169d25aecdaf68e19cf82b42f4b7c7b7009a968525a9eb"
_CMP_SITE = "c7ca9add6d16308fcbc02989173ca8e786eab212724104feb6250ebf1a333c35"
_EXPECTED_SITES = {
    _SLOT_ORDER[0]: _INV_SITE,
    _SLOT_ORDER[1]: _INV_SITE,
    _SLOT_ORDER[2]: _MONO_SITE,
    _SLOT_ORDER[3]: _MONO_SITE,
    _SLOT_ORDER[4]: None,
    _SLOT_ORDER[5]: None,
    _SLOT_ORDER[6]: None,
    _SLOT_ORDER[7]: None,
    _SLOT_ORDER[8]: _CMP_SITE,
    _SLOT_ORDER[9]: _CMP_SITE,
}

_INV_DOMAIN = {
    "semantic_contract_family": "INV",
    "executable_predicate": "factor_times_transpose_reconstructs_input",
    "oracle": "CHOLESKY_RECONSTRUCTION_V1",
    "tolerance": {"absolute": 1e-10, "relative": 1e-10},
    "activation_obligation": "factorization_succeeds",
    "expected_violation_direction": "reconstruction_error_exceeds_tolerance",
    "matrix_size": 3,
    "diagonal_min": 2.0,
    "off_diagonal_max": 0.25,
}
_CMP_DOMAIN = {
    "semantic_contract_family": "CMP",
    "executable_predicate": "yielded_ids_equal_python_suffix_projection",
    "oracle": "PYTHON_SUFFIX_PROJECTION_V1",
    "tolerance": {"comparison": "exact_set"},
    "activation_obligation": "at_least_one_accepted_and_one_rejected_suffix",
    "expected_violation_direction": "yielded_ids_differ_from_suffix_projection",
    "accepted_suffixes": [".py", ".pyi"],
    "rejected_suffixes": [".txt"],
    "entry_count": 5,
}

_CONTRACT_TEMPLATES = {
    _SLOT_ORDER[0]: ("CONTRACT_ARRAY_DOMAIN_V1", _INV_DOMAIN),
    _SLOT_ORDER[1]: ("CONTRACT_ARRAY_DOMAIN_V1", _INV_DOMAIN),
    _SLOT_ORDER[8]: ("CONTRACT_SEQUENCE_DOMAIN_V1", _CMP_DOMAIN),
    _SLOT_ORDER[9]: ("CONTRACT_SEQUENCE_DOMAIN_V1", _CMP_DOMAIN),
}


def _validated_closures(
    closures: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    if not isinstance(closures, Sequence) or len(closures) != 10:
        raise EvidenceError("E_CONTRACT_AUTHORITY", "ten ordinal-8 closures are required")
    by_slot: dict[str, dict[str, object]] = {}
    expected_keys = {
        "schema_version",
        "slot_id",
        "controlled_subject_id",
        "site_id",
        "state",
        "path",
        "artifact_sha256",
    }
    for index, raw in enumerate(closures):
        if not isinstance(raw, Mapping) or set(raw) != expected_keys:
            raise EvidenceError("E_CONTRACT_AUTHORITY", f"closure {index} fields differ")
        value = dict(raw)
        if value["controlled_subject_id"] != ORDINAL8_SUBJECT_ID:
            raise EvidenceError(
                "E_CONTRACT_AUTHORITY",
                f"controlled subject must be {ORDINAL8_SUBJECT_ID}",
            )
        slot_id = validate_sha256(value["slot_id"], f"closures[{index}].slot_id")
        if slot_id in by_slot:
            raise EvidenceError("E_CONTRACT_AUTHORITY", f"duplicate closure {slot_id}")
        digest = validate_sha256(
            value["artifact_sha256"], f"closures[{index}].artifact_sha256"
        )
        body = {key: item for key, item in value.items() if key != "artifact_sha256"}
        if digest != canonical_sha256(body):
            raise EvidenceError("E_CONTRACT_AUTHORITY", f"closure {slot_id} hash differs")
        expected_site = _EXPECTED_SITES.get(slot_id, object())
        if expected_site is None:
            if (
                value["site_id"] is not None
                or value["state"] != "APPLICABILITY_CLOSED_NOT_APPLICABLE"
                or value["path"] != "APPLICABILITY_CLOSED_NOT_APPLICABLE"
            ):
                raise EvidenceError("E_CONTRACT_AUTHORITY", f"closed slot {slot_id} differs")
        elif not isinstance(expected_site, str):
            raise EvidenceError("E_CONTRACT_AUTHORITY", f"unknown ordinal-8 slot {slot_id}")
        elif (
            value["site_id"] != expected_site
            or value["state"] != "SITE_FROZEN"
            or value["path"] != "APPLICABLE"
        ):
            raise EvidenceError("E_CONTRACT_AUTHORITY", f"frozen slot {slot_id} differs")
        by_slot[slot_id] = value
    if set(by_slot) != set(_SLOT_ORDER):
        raise EvidenceError("E_CONTRACT_AUTHORITY", "ordinal-8 slot coverage differs")
    return by_slot


def build_ordinal8_contracts(
    closures: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, Any]]:
    by_slot = _validated_closures(closures)
    contracts: dict[str, dict[str, Any]] = {}
    for slot_id in _SLOT_ORDER:
        template = _CONTRACT_TEMPLATES.get(slot_id)
        if template is None:
            continue
        generator_id, raw_domain = template
        domain = dict(raw_domain)
        site_id = str(by_slot[slot_id]["site_id"])
        contract_id = canonical_sha256(
            {
                "domain": CONTRACT_DOMAIN,
                "slot_id": slot_id,
                "generator_id": generator_id,
                "site_id": site_id,
                "contract_domain": domain,
            }
        )
        contracts[slot_id] = {
            "contract_id": contract_id,
            "generator_id": generator_id,
            "domain": domain,
            "site_id": site_id,
        }
    return contracts


def freeze_ordinal8_package(
    *,
    closures: Sequence[Mapping[str, object]],
    registry: Mapping[str, object],
) -> dict[str, object]:
    if registry.get("artifact_sha256") != CONTRACT_REGISTRY_ARTIFACT_SHA256:
        raise EvidenceError(
            "E_CONTRACT_AUTHORITY", "contract generator registry differs"
        )
    by_slot = _validated_closures(closures)
    contracts = build_ordinal8_contracts(closures)
    inventories: dict[str, dict[str, object]] = {}
    for slot_id, contract in contracts.items():
        inventory = build_contract_inputs(by_slot[slot_id], contract, registry)
        rows = inventory["rows"]
        if len(rows) != 5 or {row["status"] for row in rows} != {
            "CONTRACT_INPUT_GENERATED"
        }:
            raise EvidenceError(
                "E_CONTRACT_AUTHORITY", f"slot {slot_id} did not generate five inputs"
            )
        inventories[slot_id] = inventory
    return {"contracts": contracts, "inventories": inventories}
