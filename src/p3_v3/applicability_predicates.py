from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from pathlib import Path

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import close_slot
from p3_v3.slot_inventory import (
    SEMANTIC_CONTRACT_FAMILIES,
    freeze_slot_inventory,
    load_phase1_identity_records,
    project_controlled_subject_ids,
)

PREDICATE_IDS = (
    "APPLICABILITY_INV_V1",
    "APPLICABILITY_MONO_V1",
    "APPLICABILITY_CONV_V1",
    "APPLICABILITY_DYN_V1",
    "APPLICABILITY_CMP_V1",
)
FAMILY_TO_PREDICATE_ID = dict(zip(SEMANTIC_CONTRACT_FAMILIES, PREDICATE_IDS, strict=True))
_CONV_TOKENS = frozenset({"iterate", "step", "solve", "minimize", "converge"})
_DYN_TOKENS = frozenset({"sim", "traj", "dyn", "evolve", "integrate"})
_INV_KINDS = frozenset({"NUMERIC_ARRAY_DOMAIN_V1", "JSON_SCHEMA_DRAFT2020_12_V1"})
_CMP_KINDS = frozenset({"TEXT_IO_SCHEMA_V1", "CLI_TOKEN_GRAMMAR_V1"})
_TOKEN_SPLIT = re.compile(r"[^0-9A-Za-z]+")
_DECISION_RULES = {
    "INV": (
        'Return true if and only if at least one joined row has category == '
        '"PUBLIC_API" and schema_kind in {"NUMERIC_ARRAY_DOMAIN_V1", '
        '"JSON_SCHEMA_DRAFT2020_12_V1"}.'
    ),
    "MONO": (
        'Return true if and only if at least one joined row has category == '
        '"PUBLIC_API" and schema_kind == "NUMERIC_ARRAY_DOMAIN_V1".'
    ),
    "CONV": (
        'Return true if and only if at least one joined row has category in '
        '{"BENCHMARK", "EXAMPLE"} and the site-symbol token set intersects '
        '{"iterate", "step", "solve", "minimize", "converge"}.'
    ),
    "DYN": (
        'Return true if and only if at least one joined row has category in '
        '{"EXAMPLE", "PROJECT_TEST"} and the site-path token set intersects '
        '{"sim", "traj", "dyn", "evolve", "integrate"}.'
    ),
    "CMP": (
        'Return true if and only if at least one joined row has category == '
        '"CLI" or schema_kind in {"TEXT_IO_SCHEMA_V1", "CLI_TOKEN_GRAMMAR_V1"}.'
    ),
}
_ACCEPTED = {
    "INV": ["PUBLIC_API"],
    "MONO": ["PUBLIC_API"],
    "CONV": ["BENCHMARK", "EXAMPLE"],
    "DYN": ["EXAMPLE", "PROJECT_TEST"],
    "CMP": ["CLI"],
}
_REQUIRED_FIELDS = {
    "INV": ["site.path", "site.symbol", "row.category", "row.schema_kind"],
    "MONO": ["site.path", "site.symbol", "row.category", "row.schema_kind"],
    "CONV": ["site.path", "site.symbol", "row.category"],
    "DYN": ["site.path", "row.category"],
    "CMP": ["site.path", "site.symbol", "row.category_or_schema_kind"],
}
_MANIFEST_SCHEMA = {
    "authority_id": str,
    "schema_version": str,
    "subject_identity_projection": list,
    "subject_identity_projection_sha256": str,
    "site_policy_sha256": str,
    "operator_catalogue_sha256": str,
    "slot_inventory_artifact_sha256": str,
    "slot_implementation_source_sha256": str,
    "predicate_registry_artifact_sha256": str,
    "predicate_implementation_source_sha256": str,
    "canonicalization_implementation_source_sha256": str,
    "artifact_sha256": str,
}


def symbol_tail(value: str) -> str:
    if type(value) is not str:
        raise EvidenceError("E_APPLICABILITY_PREDICATE", "symbol tail requires a string")
    return value.rsplit(":", 1)[-1].rsplit(".", 1)[-1]


def static_tokens(value: str) -> tuple[str, ...]:
    if type(value) is not str:
        raise EvidenceError("E_APPLICABILITY_PREDICATE", "tokens require a string")
    return tuple(token for token in _TOKEN_SPLIT.split(value.casefold()) if token)


def join_site_to_public_rows(
    site: Mapping[str, object],
    public_rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    if (
        not isinstance(site, Mapping)
        or type(site.get("path")) is not str
        or type(site.get("symbol")) is not str
    ):
        raise EvidenceError("E_APPLICABILITY_PREDICATE", "site path and symbol are required")
    joined: list[dict[str, object]] = []
    for raw in public_rows:
        if not isinstance(raw, Mapping):
            continue
        if type(raw.get("provenance_path")) is not str or type(raw.get("entrypoint")) is not str:
            continue
        if type(raw.get("behavior_id")) is not str or type(raw.get("artifact_sha256")) is not str:
            continue
        if raw["provenance_path"] != site["path"]:
            continue
        if symbol_tail(site["symbol"]) != symbol_tail(raw["entrypoint"]):
            continue
        joined.append(dict(raw))
    joined.sort(key=lambda row: (row["behavior_id"], row["artifact_sha256"]))
    return tuple(joined)


def attach_schema_kind(
    row: Mapping[str, object],
    public_schemas: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    attached = dict(row)
    attached.pop("schema_kind", None)
    target = row.get("declared_input_schema_sha256")
    matches: list[str] = []
    for schema in public_schemas:
        if not isinstance(schema, Mapping) or "raw_schema" not in schema:
            continue
        if canonical_sha256(schema["raw_schema"]) == target:
            kind = schema.get("schema_kind")
            if type(kind) is str:
                matches.append(kind)
    if len(matches) == 1:
        attached["schema_kind"] = matches[0]
    return attached


def evaluate_predicate(
    predicate_id: str,
    site: Mapping[str, object],
    joined_public_rows: Sequence[Mapping[str, object]],
) -> bool:
    if predicate_id not in PREDICATE_IDS:
        raise EvidenceError("E_APPLICABILITY_PREDICATE", "unknown predicate_id")
    if (
        not isinstance(site, Mapping)
        or type(site.get("path")) is not str
        or type(site.get("symbol")) is not str
    ):
        raise EvidenceError("E_APPLICABILITY_PREDICATE", "site path and symbol are required")
    rows = [dict(row) for row in joined_public_rows if isinstance(row, Mapping)]
    if predicate_id == "APPLICABILITY_INV_V1":
        result = any(
            row.get("category") == "PUBLIC_API" and row.get("schema_kind") in _INV_KINDS
            for row in rows
        )
    elif predicate_id == "APPLICABILITY_MONO_V1":
        result = any(
            row.get("category") == "PUBLIC_API"
            and row.get("schema_kind") == "NUMERIC_ARRAY_DOMAIN_V1"
            for row in rows
        )
    elif predicate_id == "APPLICABILITY_CONV_V1":
        tokens = set(static_tokens(site["symbol"]))
        result = any(
            row.get("category") in {"BENCHMARK", "EXAMPLE"} and tokens & _CONV_TOKENS
            for row in rows
        )
    elif predicate_id == "APPLICABILITY_DYN_V1":
        tokens = set(static_tokens(site["path"]))
        result = any(
            row.get("category") in {"EXAMPLE", "PROJECT_TEST"} and tokens & _DYN_TOKENS
            for row in rows
        )
    else:
        result = any(
            row.get("category") == "CLI" or row.get("schema_kind") in _CMP_KINDS
            for row in rows
        )
    if type(result) is not bool:
        raise EvidenceError("E_APPLICABILITY_RESULT", "predicate must return bool")
    return result


def build_predicate_registry(implementation_source_sha256: str) -> dict[str, object]:
    digest = validate_sha256(implementation_source_sha256, "implementation_source_sha256")
    predicates = []
    for family, predicate_id in FAMILY_TO_PREDICATE_ID.items():
        predicates.append(
            {
                "predicate_id": predicate_id,
                "semantic_contract_family": family,
                "accepted_site_categories": list(_ACCEPTED[family]),
                "required_static_fields": list(_REQUIRED_FIELDS[family]),
                "decision_rule": _DECISION_RULES[family],
                "implementation_path": "src/p3_v3/applicability_predicates.py",
                "implementation_source_sha256": digest,
            }
        )
    body = {
        "schema_version": "p3-applicability-predicate-registry-v1",
        "predicates": predicates,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _self_hash(value: Mapping[str, object], code: str, context: str) -> dict[str, object]:
    payload = dict(value)
    digest = validate_sha256(payload.get("artifact_sha256"), f"{context}.artifact_sha256")
    body = {key: item for key, item in payload.items() if key != "artifact_sha256"}
    if digest != canonical_sha256(body):
        raise EvidenceError(code, f"{context} canonical self-hash differs")
    return payload


def load_applicability_authority(
    *,
    manifest_path: Path,
    registry_path: Path,
    inventory_path: Path,
    slot_implementation_path: Path,
    predicate_implementation_path: Path,
) -> dict[str, object]:
    manifest = _self_hash(
        validate_exact_object(read_canonical_json(manifest_path), _MANIFEST_SCHEMA, "authority"),
        "E_APPLICABILITY_AUTHORITY",
        "authority",
    )
    if (
        manifest["authority_id"] != "p3-v3-phase2-applicability-authority-v1"
        or manifest["schema_version"] != "p3-applicability-authority-v1"
    ):
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "unsupported authority identity")
    registry = _self_hash(
        read_canonical_json(registry_path), "E_APPLICABILITY_AUTHORITY", "registry"
    )
    inventory = _self_hash(
        read_canonical_json(inventory_path), "E_APPLICABILITY_AUTHORITY", "inventory"
    )
    ids = tuple(manifest["subject_identity_projection"])
    if ids != tuple(sorted(ids)) or len(ids) != 35:
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "subject projection must be 35 sorted IDs")
    for index, item in enumerate(ids):
        validate_sha256(item, f"subject_identity_projection[{index}]")
    if canonical_sha256(list(ids)) != manifest["subject_identity_projection_sha256"]:
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "subject projection hash differs")
    repo_root = Path(__file__).resolve().parents[2]
    phase1_ids = project_controlled_subject_ids(
        load_phase1_identity_records(
            verified_bridge_path=repo_root / "data/p3_v3/p12_intake/verified_bridge.json",
            workload_root=repo_root / "data/p3_v3/phase1_frames/out",
        )
    )
    if ids != phase1_ids:
        raise EvidenceError(
            "E_APPLICABILITY_AUTHORITY",
            "subject projection differs from Phase-1 rebuild",
        )
    rebuilt_inventory = freeze_slot_inventory(ids)
    rebuilt_registry = build_predicate_registry(file_sha256(predicate_implementation_path))
    if rebuilt_inventory != inventory:
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "slot inventory bytes differ from rebuild")
    if rebuilt_registry != registry:
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "predicate registry bytes differ from rebuild")
    checks = {
        "site_policy_sha256": file_sha256(repo_root / "data/p3_v3/protocol/site_policy.md"),
        "operator_catalogue_sha256": file_sha256(
            repo_root / "data/p3_v3/protocol/operator_catalogue.md"
        ),
        "slot_inventory_artifact_sha256": inventory["artifact_sha256"],
        "predicate_registry_artifact_sha256": registry["artifact_sha256"],
        "slot_implementation_source_sha256": file_sha256(slot_implementation_path),
        "predicate_implementation_source_sha256": file_sha256(predicate_implementation_path),
        "canonicalization_implementation_source_sha256": file_sha256(
            Path(__file__).resolve().with_name("artifacts.py")
        ),
    }
    for field, observed in checks.items():
        if manifest[field] != observed:
            raise EvidenceError("E_APPLICABILITY_AUTHORITY", f"{field} binding differs")
    forbidden = {"site_id", "contract", "patch", "outcome", "SITE_FROZEN"}
    if forbidden.intersection(manifest):
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "authority contains outcome fields")
    return {
        "manifest": manifest,
        "registry": registry,
        "inventory": inventory,
        "controlled_subject_ids": ids,
    }


def close_slot_with_authority(
    authority: Mapping[str, object],
    inventory_row: Mapping[str, object],
    canonical_sites: Sequence[Mapping[str, object]],
    public_behavior_frame: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(authority, Mapping):
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "authority is required")
    inventory = authority.get("inventory")
    registry = authority.get("registry")
    if not isinstance(inventory, Mapping) or not isinstance(registry, Mapping):
        raise EvidenceError(
            "E_APPLICABILITY_AUTHORITY",
            "authority inventory and registry are required",
        )
    slots = inventory.get("slots")
    predicates = registry.get("predicates")
    if not isinstance(slots, Sequence) or isinstance(slots, (str, bytes)):
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "inventory slots are required")
    if not isinstance(predicates, Sequence) or isinstance(predicates, (str, bytes)):
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "registry predicates are required")
    if not isinstance(inventory_row, Mapping):
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "inventory row must be an object")
    frozen = next((dict(row) for row in slots if dict(row) == dict(inventory_row)), None)
    if frozen is None:
        raise EvidenceError(
            "E_APPLICABILITY_AUTHORITY",
            "inventory row is not in the frozen inventory",
        )
    family = frozen.get("semantic_contract_family")
    predicate_id = next(
        (
            item.get("predicate_id")
            for item in predicates
            if isinstance(item, Mapping) and item.get("semantic_contract_family") == family
        ),
        None,
    )
    if predicate_id not in PREDICATE_IDS:
        raise EvidenceError("E_APPLICABILITY_PREDICATE", "inventory row family is unknown")
    rows = public_behavior_frame.get("rows")
    schemas = public_behavior_frame.get("public_schemas")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        raise EvidenceError("E_APPLICABILITY_PREDICATE", "public rows must be a sequence")
    if schemas is None:
        schemas = []
    if not isinstance(schemas, Sequence) or isinstance(schemas, (str, bytes)):
        raise EvidenceError("E_APPLICABILITY_PREDICATE", "public_schemas must be a sequence")

    def predicate(site: Mapping[str, object]) -> bool:
        joined = [
            attach_schema_kind(row, schemas) for row in join_site_to_public_rows(site, rows)
        ]
        return evaluate_predicate(predicate_id, site, joined)

    return close_slot(
        {
            "slot_id": inventory_row["slot_id"],
            "controlled_subject_id": inventory_row["controlled_subject_id"],
        },
        canonical_sites,
        predicate,
    )


def materialize_applicability_authority(
    *,
    verified_bridge_path: Path,
    workload_root: Path,
    site_policy_path: Path,
    operator_catalogue_path: Path,
    slot_implementation_path: Path,
    predicate_implementation_path: Path,
    canonicalization_implementation_path: Path,
    registry_path: Path,
    inventory_path: Path,
    manifest_path: Path,
) -> dict[str, object]:
    ids = project_controlled_subject_ids(
        load_phase1_identity_records(
            verified_bridge_path=verified_bridge_path,
            workload_root=workload_root,
        )
    )
    inventory = freeze_slot_inventory(ids)
    registry = build_predicate_registry(file_sha256(predicate_implementation_path))
    body = {
        "authority_id": "p3-v3-phase2-applicability-authority-v1",
        "schema_version": "p3-applicability-authority-v1",
        "subject_identity_projection": list(ids),
        "subject_identity_projection_sha256": canonical_sha256(list(ids)),
        "site_policy_sha256": file_sha256(site_policy_path),
        "operator_catalogue_sha256": file_sha256(operator_catalogue_path),
        "slot_inventory_artifact_sha256": inventory["artifact_sha256"],
        "slot_implementation_source_sha256": file_sha256(slot_implementation_path),
        "predicate_registry_artifact_sha256": registry["artifact_sha256"],
        "predicate_implementation_source_sha256": file_sha256(predicate_implementation_path),
        "canonicalization_implementation_source_sha256": file_sha256(
            canonicalization_implementation_path
        ),
    }
    manifest = {**body, "artifact_sha256": canonical_sha256(body)}
    write_canonical_json(inventory_path, inventory, exclusive=True)
    write_canonical_json(registry_path, registry, exclusive=True)
    write_canonical_json(manifest_path, manifest, exclusive=True)
    return load_applicability_authority(
        manifest_path=manifest_path,
        registry_path=registry_path,
        inventory_path=inventory_path,
        slot_implementation_path=slot_implementation_path,
        predicate_implementation_path=predicate_implementation_path,
    )
