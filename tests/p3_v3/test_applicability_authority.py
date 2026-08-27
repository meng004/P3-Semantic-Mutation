from __future__ import annotations

import ast
import hashlib
import inspect
from collections import Counter
from collections.abc import Mapping
from pathlib import Path

import pytest

from p3_v3.applicability_predicates import (
    FAMILY_TO_PREDICATE_ID,
    PREDICATE_IDS,
    attach_schema_kind,
    build_predicate_registry,
    close_slot_with_authority,
    evaluate_predicate,
    join_site_to_public_rows,
    load_applicability_authority,
    static_tokens,
    symbol_tail,
)
from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.slot_inventory import (
    MECHANISM_ORDER,
    SEMANTIC_CONTRACT_FAMILIES,
    freeze_slot_inventory,
    load_phase1_identity_records,
    project_controlled_subject_ids,
    slot_id,
)

FORBIDDEN_SLOT_FIELDS = {
    "site",
    "site_id",
    "path",
    "symbol",
    "applicability",
    "profiling",
    "profiling_results",
    "contract",
    "patch",
    "outcome",
    "technique",
    "project",
}


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _identity_records(count: int = 35) -> list[dict[str, str]]:
    return [
        {
            "normalized_source_tree_sha256": _digest(f"tree-{index}"),
            "build_descriptor_sha256": _digest(f"build-{index}"),
            "public_workload_set_sha256": _digest(f"work-{index}"),
        }
        for index in range(count)
    ]


def test_project_controlled_subject_ids_sorts_35_unique_sha256():
    records = list(reversed(_identity_records()))
    ids = project_controlled_subject_ids(records)
    assert len(ids) == 35
    assert len(set(ids)) == 35
    assert ids == tuple(sorted(ids))
    assert ids == project_controlled_subject_ids(_identity_records())
    for item in ids:
        validate_sha256(item, "controlled_subject_id")
        assert item == item.lower()


def test_project_controlled_subject_ids_rejects_extra_or_missing_fields():
    extra = {**_identity_records()[0], "scale_class": "S"}
    with pytest.raises(EvidenceError, match="E_SUBJECT_IDENTITY"):
        project_controlled_subject_ids([extra, *_identity_records()[1:]])
    missing = {
        "normalized_source_tree_sha256": _digest("tree"),
        "build_descriptor_sha256": _digest("build"),
    }
    with pytest.raises(EvidenceError, match="E_SUBJECT_IDENTITY"):
        project_controlled_subject_ids([missing, *_identity_records()[1:]])


def test_project_controlled_subject_ids_rejects_duplicate_missing_or_illegal_count():
    records = _identity_records()
    with pytest.raises(EvidenceError, match="E_SUBJECT_IDENTITY"):
        project_controlled_subject_ids(records + [records[0]])
    with pytest.raises(EvidenceError, match="E_SUBJECT_IDENTITY"):
        project_controlled_subject_ids(records[:34])
    bad = {**records[0], "public_workload_set_sha256": "not-a-sha"}
    with pytest.raises(EvidenceError, match="E_SHA256"):
        project_controlled_subject_ids([bad, *records[1:]])


def test_freeze_slot_inventory_counts_and_rebuildable_ids():
    ids = project_controlled_subject_ids(_identity_records())
    inventory = freeze_slot_inventory(ids)
    slots = inventory["slots"]
    assert inventory["schema_version"] == "p3-slot-inventory-v1"
    assert inventory["artifact_sha256"] == canonical_sha256(
        {key: value for key, value in inventory.items() if key != "artifact_sha256"}
    )
    assert len(slots) == 350
    assert {row["controlled_subject_id"] for row in slots} == set(ids)
    per_subject = Counter(row["controlled_subject_id"] for row in slots)
    assert set(per_subject.values()) == {10}
    per_family = Counter(row["semantic_contract_family"] for row in slots)
    assert per_family == {family: 70 for family in SEMANTIC_CONTRACT_FAMILIES}
    per_cell = Counter(
        (row["semantic_contract_family"], row["permitted_construction_mechanism"])
        for row in slots
    )
    assert len(per_cell) == 25
    assert set(per_cell.values()) == {14}
    rebuilt = {
        slot_id(
            row["controlled_subject_id"],
            row["semantic_contract_family"],
            row["slot_ordinal"],
            row["permitted_construction_mechanism"],
        )
        for row in slots
    }
    assert rebuilt == {row["slot_id"] for row in slots}
    assert len(rebuilt) == 350


def test_freeze_slot_inventory_ignores_input_order_and_omits_outcome_fields():
    ids = project_controlled_subject_ids(_identity_records())
    left = freeze_slot_inventory(ids)
    right = freeze_slot_inventory(list(reversed(ids)))
    assert left == right
    for row in left["slots"]:
        assert set(row) == {
            "slot_id",
            "controlled_subject_id",
            "semantic_contract_family",
            "slot_ordinal",
            "permitted_construction_mechanism",
        }
        assert FORBIDDEN_SLOT_FIELDS.isdisjoint(row)
    ordered = left["slots"]
    assert ordered == sorted(
        ordered,
        key=lambda row: (
            row["controlled_subject_id"],
            SEMANTIC_CONTRACT_FAMILIES.index(row["semantic_contract_family"]),
            row["slot_ordinal"],
            MECHANISM_ORDER.index(row["permitted_construction_mechanism"]),
            row["slot_id"],
        ),
    )


def test_freeze_slot_inventory_rejects_illegal_subject_ids():
    ids = list(project_controlled_subject_ids(_identity_records()))
    with pytest.raises(EvidenceError, match="E_SLOT_INVENTORY"):
        freeze_slot_inventory(ids + [ids[0]])
    with pytest.raises(EvidenceError, match="E_SHA256"):
        freeze_slot_inventory(["not-a-sha", *ids[1:]])
    with pytest.raises(EvidenceError, match="E_SLOT_INVENTORY"):
        freeze_slot_inventory(ids[:10])


def test_mechanism_formula_is_index_plus_ordinal_mod_five():
    ids = project_controlled_subject_ids(_identity_records())
    slots = freeze_slot_inventory(ids)["slots"]
    by_subject = {subject_id: [] for subject_id in ids}
    for row in slots:
        by_subject[row["controlled_subject_id"]].append(row)
    for subject_index, subject_id in enumerate(ids):
        rows = by_subject[subject_id]
        assert len(rows) == 10
        for row in rows:
            expected = MECHANISM_ORDER[(subject_index + row["slot_ordinal"]) % 5]
            assert row["permitted_construction_mechanism"] == expected


def _site(path: str, symbol: str, site_id: str) -> dict[str, object]:
    return {
        "path": path,
        "symbol": symbol,
        "start_line": 1,
        "start_col": 0,
        "end_line": 1,
        "end_col": 1,
        "site_id": site_id,
    }


def _row(
    *,
    path: str,
    entrypoint: str,
    category: str,
    behavior_id: str,
    artifact_sha256: str,
    schema_hash: str,
) -> dict[str, object]:
    return {
        "behavior_id": behavior_id,
        "artifact_sha256": artifact_sha256,
        "category": category,
        "provenance_path": path,
        "entrypoint": entrypoint,
        "declared_input_schema_sha256": schema_hash,
    }


def test_symbol_tail_uses_last_colon_then_last_dot():
    assert symbol_tail("ns:pkg.Type.method") == "method"
    assert symbol_tail("Type.method") == "method"
    assert symbol_tail("method") == "method"
    assert symbol_tail("ns:method") == "method"
    assert symbol_tail("pkg.Type") == "Type"


def test_static_tokens_reject_substring_hits():
    assert static_tokens("do_iterate") == ("do", "iterate")
    assert "iterate" not in static_tokens("myIterate")
    assert "converge" not in static_tokens("converged")
    assert static_tokens("path/sim/run.py") == ("path", "sim", "run", "py")
    assert "sim" not in static_tokens("simulation")
    assert static_tokens("traj-evolve") == ("traj", "evolve")


def test_exact_join_success_failure_and_canonical_order():
    site = _site("pkg/synth.py", "ns:pkg.Synth.iterate", "a" * 64)
    late = _row(
        path="pkg/synth.py",
        entrypoint="pkg.Synth.iterate",
        category="EXAMPLE",
        behavior_id="f" * 64,
        artifact_sha256="2" * 64,
        schema_hash="3" * 64,
    )
    early = _row(
        path="pkg/synth.py",
        entrypoint="other:Synth.iterate",
        category="BENCHMARK",
        behavior_id="0" * 64,
        artifact_sha256="1" * 64,
        schema_hash="4" * 64,
    )
    miss_path = {**late, "provenance_path": "pkg/other.py", "behavior_id": "e" * 64}
    miss_tail = {**late, "entrypoint": "pkg.Synth.step", "behavior_id": "d" * 64}
    joined = join_site_to_public_rows(site, [late, miss_path, miss_tail, early])
    assert [row["behavior_id"] for row in joined] == ["0" * 64, "f" * 64]
    assert join_site_to_public_rows(site, [miss_path, miss_tail]) == ()


def test_five_predicates_true_false_and_zero_rows():
    schema = {"kind": "numeric-array"}
    schema_hash = canonical_sha256(schema)
    public_api = _row(
        path="pkg/api.py",
        entrypoint="api.public_fn",
        category="PUBLIC_API",
        behavior_id="1" * 64,
        artifact_sha256="2" * 64,
        schema_hash=schema_hash,
    )
    attached_numeric = attach_schema_kind(
        public_api, [{"schema_kind": "NUMERIC_ARRAY_DOMAIN_V1", "raw_schema": schema}]
    )
    attached_json = attach_schema_kind(
        public_api,
        [{"schema_kind": "JSON_SCHEMA_DRAFT2020_12_V1", "raw_schema": schema}],
    )
    conv_row = _row(
        path="pkg/bench.py",
        entrypoint="bench.iterate",
        category="BENCHMARK",
        behavior_id="3" * 64,
        artifact_sha256="4" * 64,
        schema_hash="5" * 64,
    )
    dyn_row = _row(
        path="pkg/sim/run.py",
        entrypoint="demo.main",
        category="EXAMPLE",
        behavior_id="6" * 64,
        artifact_sha256="7" * 64,
        schema_hash="8" * 64,
    )
    cmp_cli = _row(
        path="pkg/cli.py",
        entrypoint="cli.main",
        category="CLI",
        behavior_id="9" * 64,
        artifact_sha256="a" * 64,
        schema_hash="b" * 64,
    )
    cmp_text = attach_schema_kind(
        {**public_api, "category": "EXAMPLE"},
        [{"schema_kind": "TEXT_IO_SCHEMA_V1", "raw_schema": schema}],
    )
    inv_site = _site("pkg/api.py", "api.public_fn", "c" * 64)
    assert evaluate_predicate("APPLICABILITY_INV_V1", inv_site, [attached_numeric]) is True
    assert evaluate_predicate("APPLICABILITY_INV_V1", inv_site, [attached_json]) is True
    assert evaluate_predicate("APPLICABILITY_MONO_V1", inv_site, [attached_numeric]) is True
    assert evaluate_predicate("APPLICABILITY_MONO_V1", inv_site, [attached_json]) is False
    injected = attach_schema_kind({**public_api, "schema_kind": "NUMERIC_ARRAY_DOMAIN_V1"}, [])
    assert "schema_kind" not in injected
    assert evaluate_predicate("APPLICABILITY_INV_V1", inv_site, [injected]) is False
    assert (
        evaluate_predicate(
            "APPLICABILITY_CONV_V1",
            _site("pkg/bench.py", "bench.iterate", "d" * 64),
            [conv_row],
        )
        is True
    )
    assert (
        evaluate_predicate(
            "APPLICABILITY_CONV_V1",
            _site("pkg/bench.py", "bench.converged", "e" * 64),
            [conv_row],
        )
        is False
    )
    assert (
        evaluate_predicate(
            "APPLICABILITY_DYN_V1",
            _site("pkg/sim/run.py", "demo.main", "f" * 64),
            [dyn_row],
        )
        is True
    )
    assert (
        evaluate_predicate(
            "APPLICABILITY_DYN_V1",
            _site("pkg/simulation/run.py", "demo.main", "0" * 64),
            [dyn_row],
        )
        is False
    )
    assert (
        evaluate_predicate(
            "APPLICABILITY_CMP_V1",
            _site("pkg/cli.py", "cli.main", "1" * 64),
            [cmp_cli],
        )
        is True
    )
    assert (
        evaluate_predicate(
            "APPLICABILITY_CMP_V1",
            _site("pkg/api.py", "api.public_fn", "2" * 64),
            [cmp_text],
        )
        is True
    )
    empty_site = _site("pkg/none.py", "none.fn", "3" * 64)
    for predicate_id in PREDICATE_IDS:
        assert evaluate_predicate(predicate_id, empty_site, []) is False
        assert (
            evaluate_predicate(
                predicate_id, inv_site, [{**public_api, "category": "PROJECT_TEST"}]
            )
            is False
        )


def test_evaluate_predicate_fail_closed_and_has_no_subject_parameter():
    site = _site("pkg/api.py", "api.fn", "4" * 64)
    with pytest.raises(EvidenceError, match="E_APPLICABILITY_PREDICATE"):
        evaluate_predicate("APPLICABILITY_UNKNOWN_V1", site, [])
    with pytest.raises(EvidenceError, match="E_APPLICABILITY_PREDICATE"):
        evaluate_predicate("APPLICABILITY_INV_V1", {"symbol": "fn"}, [])
    signature = inspect.signature(evaluate_predicate)
    assert list(signature.parameters) == ["predicate_id", "site", "joined_public_rows"]
    import p3_v3.applicability_predicates as predicates_module

    for name in (
        "symbol_tail",
        "static_tokens",
        "join_site_to_public_rows",
        "evaluate_predicate",
    ):
        source = inspect.getsource(getattr(predicates_module, name))
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in {"environ", "getenv"}:
                raise AssertionError(f"{name} reads the environment")
            if isinstance(node, ast.Name) and node.id in {
                "open",
                "Path",
                "os",
                "subprocess",
            }:
                raise AssertionError(f"{name} uses {node.id}")


def test_close_slot_with_authority_selects_first_or_not_applicable():
    ids = project_controlled_subject_ids(_identity_records())
    inventory = freeze_slot_inventory(ids)
    registry = build_predicate_registry("c" * 64)
    inv_row = next(
        row
        for row in inventory["slots"]
        if row["controlled_subject_id"] == ids[0]
        and row["semantic_contract_family"] == "CONV"
    )
    sites = [
        _site("pkg/a.py", "demo.other", "a" * 64),
        _site("pkg/b.py", "demo.iterate", "b" * 64),
    ]
    pbf = {
        "rows": [
            _row(
                path="pkg/b.py",
                entrypoint="demo.iterate",
                category="EXAMPLE",
                behavior_id="1" * 64,
                artifact_sha256="2" * 64,
                schema_hash="3" * 64,
            )
        ],
        "public_schemas": [],
    }
    authority = {
        "registry": registry,
        "inventory": inventory,
        "controlled_subject_ids": ids,
    }
    applicable = close_slot_with_authority(authority, inv_row, sites, pbf)
    assert applicable["state"] == "SITE_FROZEN"
    assert applicable["site_id"] == "b" * 64
    closed = close_slot_with_authority(
        authority, inv_row, sites, {"rows": [], "public_schemas": []}
    )
    assert closed["state"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE"
    assert closed["site_id"] is None
    with pytest.raises(EvidenceError, match="E_SITE_ORDER"):
        close_slot_with_authority(authority, inv_row, list(reversed(sites)), pbf)
    shuffled = close_slot_with_authority(
        authority,
        inv_row,
        sites,
        {"rows": list(reversed(pbf["rows"])), "public_schemas": []},
    )
    assert shuffled["site_id"] == applicable["site_id"]
    second = next(
        row
        for row in inventory["slots"]
        if row["controlled_subject_id"] == ids[0]
        and row["semantic_contract_family"] == "INV"
    )
    other = close_slot_with_authority(authority, second, sites, pbf)
    assert other["state"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE"
    assert other["slot_id"] == second["slot_id"]
    assert applicable["slot_id"] == inv_row["slot_id"]
    mutated = {**inv_row, "semantic_contract_family": "INV"}
    with pytest.raises(EvidenceError, match="E_APPLICABILITY_AUTHORITY"):
        close_slot_with_authority(authority, mutated, sites, pbf)


def test_load_applicability_authority_accepts_tmp_bindings_and_rejects_byte_drift(
    tmp_path,
):
    ids = project_controlled_subject_ids(
        load_phase1_identity_records(
            verified_bridge_path=Path("data/p3_v3/p12_intake/verified_bridge.json"),
            workload_root=Path("data/p3_v3/phase1_frames/out"),
        )
    )
    inventory = freeze_slot_inventory(ids)
    slot_impl = tmp_path / "slot_inventory.py"
    pred_impl = tmp_path / "applicability_predicates.py"
    slot_impl.write_bytes(Path("src/p3_v3/slot_inventory.py").read_bytes())
    pred_impl.write_bytes(Path("src/p3_v3/applicability_predicates.py").read_bytes())
    registry = build_predicate_registry(file_sha256(pred_impl))
    body = {
        "authority_id": "p3-v3-phase2-applicability-authority-v1",
        "schema_version": "p3-applicability-authority-v1",
        "subject_identity_projection": list(ids),
        "subject_identity_projection_sha256": canonical_sha256(list(ids)),
        "site_policy_sha256": file_sha256(Path("data/p3_v3/protocol/site_policy.md")),
        "operator_catalogue_sha256": file_sha256(
            Path("data/p3_v3/protocol/operator_catalogue.md")
        ),
        "slot_inventory_artifact_sha256": inventory["artifact_sha256"],
        "slot_implementation_source_sha256": file_sha256(slot_impl),
        "predicate_registry_artifact_sha256": registry["artifact_sha256"],
        "predicate_implementation_source_sha256": file_sha256(pred_impl),
        "canonicalization_implementation_source_sha256": file_sha256(
            Path("src/p3_v3/artifacts.py")
        ),
    }
    manifest = {**body, "artifact_sha256": canonical_sha256(body)}
    manifest_path = tmp_path / "authority.json"
    registry_path = tmp_path / "registry.json"
    inventory_path = tmp_path / "inventory.json"
    write_canonical_json(manifest_path, manifest, exclusive=True)
    write_canonical_json(registry_path, registry, exclusive=True)
    write_canonical_json(inventory_path, inventory, exclusive=True)
    loaded = load_applicability_authority(
        manifest_path=manifest_path,
        registry_path=registry_path,
        inventory_path=inventory_path,
        slot_implementation_path=slot_impl,
        predicate_implementation_path=pred_impl,
    )
    assert loaded["controlled_subject_ids"] == ids
    assert "SITE_FROZEN" not in loaded["manifest"]
    drifted = tmp_path / "drift-inventory.json"
    broken = dict(inventory)
    broken["slots"] = inventory["slots"][:349]
    broken.pop("artifact_sha256")
    broken["artifact_sha256"] = canonical_sha256(broken)
    write_canonical_json(drifted, broken, exclusive=True)
    with pytest.raises(EvidenceError, match="E_APPLICABILITY_AUTHORITY"):
        load_applicability_authority(
            manifest_path=manifest_path,
            registry_path=registry_path,
            inventory_path=drifted,
            slot_implementation_path=slot_impl,
            predicate_implementation_path=pred_impl,
        )


def test_load_applicability_authority_rejects_synthetic_projection(tmp_path):
    ids = project_controlled_subject_ids(_identity_records())
    inventory = freeze_slot_inventory(ids)
    slot_impl = tmp_path / "slot_inventory.py"
    pred_impl = tmp_path / "applicability_predicates.py"
    slot_impl.write_bytes(Path("src/p3_v3/slot_inventory.py").read_bytes())
    pred_impl.write_bytes(Path("src/p3_v3/applicability_predicates.py").read_bytes())
    registry = build_predicate_registry(file_sha256(pred_impl))
    body = {
        "authority_id": "p3-v3-phase2-applicability-authority-v1",
        "schema_version": "p3-applicability-authority-v1",
        "subject_identity_projection": list(ids),
        "subject_identity_projection_sha256": canonical_sha256(list(ids)),
        "site_policy_sha256": file_sha256(Path("data/p3_v3/protocol/site_policy.md")),
        "operator_catalogue_sha256": file_sha256(
            Path("data/p3_v3/protocol/operator_catalogue.md")
        ),
        "slot_inventory_artifact_sha256": inventory["artifact_sha256"],
        "slot_implementation_source_sha256": file_sha256(slot_impl),
        "predicate_registry_artifact_sha256": registry["artifact_sha256"],
        "predicate_implementation_source_sha256": file_sha256(pred_impl),
        "canonicalization_implementation_source_sha256": file_sha256(
            Path("src/p3_v3/artifacts.py")
        ),
    }
    manifest = {**body, "artifact_sha256": canonical_sha256(body)}
    manifest_path = tmp_path / "authority.json"
    registry_path = tmp_path / "registry.json"
    inventory_path = tmp_path / "inventory.json"
    write_canonical_json(manifest_path, manifest, exclusive=True)
    write_canonical_json(registry_path, registry, exclusive=True)
    write_canonical_json(inventory_path, inventory, exclusive=True)
    with pytest.raises(EvidenceError, match="E_APPLICABILITY_AUTHORITY"):
        load_applicability_authority(
            manifest_path=manifest_path,
            registry_path=registry_path,
            inventory_path=inventory_path,
            slot_implementation_path=slot_impl,
            predicate_implementation_path=pred_impl,
        )


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/p3_v3/phase2/applicability-authority.json"
REGISTRY = ROOT / "data/p3_v3/protocol/applicability-predicate-registry.json"
INVENTORY = ROOT / "data/p3_v3/phase2/slot-inventory.json"


def test_official_authority_artifacts_bind_and_count():
    loaded = load_applicability_authority(
        manifest_path=MANIFEST,
        registry_path=REGISTRY,
        inventory_path=INVENTORY,
        slot_implementation_path=ROOT / "src/p3_v3/slot_inventory.py",
        predicate_implementation_path=ROOT / "src/p3_v3/applicability_predicates.py",
    )
    slots = loaded["inventory"]["slots"]
    assert len(loaded["controlled_subject_ids"]) == 35
    assert len(slots) == 350
    assert set(Counter(row["controlled_subject_id"] for row in slots).values()) == {10}
    assert Counter(row["semantic_contract_family"] for row in slots) == {
        family: 70 for family in SEMANTIC_CONTRACT_FAMILIES
    }
    assert set(
        Counter(
            (row["semantic_contract_family"], row["permitted_construction_mechanism"])
            for row in slots
        ).values()
    ) == {14}
    assert loaded["manifest"]["site_policy_sha256"] == (
        "9772430e0a2539667a9aaa776b47ecae92a7830e19ec0a6e75a5dda9cfdfdcf7"
    )
    assert loaded["manifest"]["operator_catalogue_sha256"] == (
        "060671a031c36699fe63c7376afbb4714c84b25eab28f06445804ee8d232a635"
    )
    projection = loaded["manifest"]["subject_identity_projection"]
    assert all(len(item) == 64 and item == item.lower() for item in projection)
    assert set(loaded["manifest"]).isdisjoint({"site_id", "contract", "patch", "outcome"})


def test_official_authority_rejects_implementation_or_inventory_byte_change(tmp_path):
    drifted = tmp_path / "slot_inventory.py"
    drifted.write_bytes((ROOT / "src/p3_v3/slot_inventory.py").read_bytes() + b"\n")
    with pytest.raises(EvidenceError, match="E_APPLICABILITY_AUTHORITY"):
        load_applicability_authority(
            manifest_path=MANIFEST,
            registry_path=REGISTRY,
            inventory_path=INVENTORY,
            slot_implementation_path=drifted,
            predicate_implementation_path=ROOT / "src/p3_v3/applicability_predicates.py",
        )
