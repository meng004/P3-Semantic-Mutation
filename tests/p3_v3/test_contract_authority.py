from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from p3_v3.artifacts import read_canonical_json
from p3_v3.artifacts import EvidenceError
from p3_v3.bridge_and_frames import (
    E_CONTRACT_GENERATOR_IDS,
    validate_contract_generator_registry,
)
from p3_v3.contract_generators import (
    array_domain,
    enum_domain,
    numeric_domain,
    relation_pair_domain,
    sequence_domain,
)
from p3_v3.contract_authority import (
    CONTRACT_DOMAIN,
    ORDINAL8_SUBJECT_ID,
    build_ordinal8_contracts,
    freeze_ordinal8_package,
)
from p3_v3.artifacts import canonical_json_bytes, canonical_sha256


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "data/p3_v3/protocol/contract-generator-registry.json"
CLOSURE_ROOT = (
    REPO_ROOT
    / "data/p3_v3/phase2/prospective-applicability-search-v2/subjects"
    / "4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b"
)


def _assert_success(module, domain: dict, seed: int = 7) -> dict:
    encoded = json.dumps(
        domain, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    first = module.generate(encoded, seed)
    second = module.generate(encoded, seed)
    assert first == second
    assert set(first) == {"envelope", "raw_payload_sha256"}
    envelope = first["envelope"]
    assert envelope["schema_version"] == "p3-contract-input-envelope-v1"
    assert envelope["generator_id"] == module.GENERATOR_ID
    payload_bytes = json.dumps(
        envelope["payload"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert first["raw_payload_sha256"] == hashlib.sha256(payload_bytes).hexdigest()
    return envelope["payload"]


def test_production_registry_binds_the_existing_five_generators():
    registry = validate_contract_generator_registry(
        read_canonical_json(REGISTRY_PATH), REPO_ROOT
    )
    assert tuple(row["generator_id"] for row in registry["generators"]) == tuple(
        E_CONTRACT_GENERATOR_IDS
    )


@pytest.mark.parametrize(
    "module",
    [
        enum_domain,
        numeric_domain,
        array_domain,
        sequence_domain,
        relation_pair_domain,
    ],
)
def test_contract_generators_reject_empty_domains(module):
    encoded = b"{}"
    assert module.generate(encoded, 0) == {"failure_code": module.FAILURE_CODE}


def test_enum_generator_selects_a_declared_value():
    payload = _assert_success(enum_domain, {"values": ["lower", "upper"]})
    assert payload["value"] in {"lower", "upper"}


def test_numeric_generator_stays_inside_frozen_bounds():
    payload = _assert_success(numeric_domain, {"lower": -4.0, "upper": 9.0})
    assert -4.0 <= payload["value"] <= 9.0


def test_array_generator_emits_symmetric_strictly_diagonally_dominant_matrix():
    payload = _assert_success(
        array_domain,
        {"matrix_size": 3, "diagonal_min": 2.0, "off_diagonal_max": 0.25},
    )
    matrix = payload["matrix"]
    assert len(matrix) == 3
    assert all(len(row) == 3 for row in matrix)
    assert matrix == [list(row) for row in zip(*matrix)]
    for index, row in enumerate(matrix):
        assert row[index] > sum(abs(value) for column, value in enumerate(row) if column != index)


def test_sequence_generator_contains_accepted_and_rejected_suffixes():
    payload = _assert_success(
        sequence_domain,
        {
            "accepted_suffixes": [".py", ".pyi"],
            "rejected_suffixes": [".txt"],
            "entry_count": 5,
        },
    )
    entries = payload["entries"]
    assert len(entries) == 5
    assert any(name.endswith((".py", ".pyi")) for name in entries)
    assert any(name.endswith(".txt") for name in entries)


def test_relation_pair_generator_emits_an_ordered_pair():
    payload = _assert_success(
        relation_pair_domain,
        {"lower": -32, "upper": 32, "integer": True},
    )
    assert -32 <= payload["left"] <= payload["right"] <= 32


def _closures() -> list[dict]:
    return [read_canonical_json(path) for path in sorted(CLOSURE_ROOT.glob("*.json"))]


def test_ordinal8_contracts_cover_only_the_six_frozen_slots():
    closures = _closures()
    contracts = build_ordinal8_contracts(closures)
    frozen = {row["slot_id"] for row in closures if row["state"] == "SITE_FROZEN"}
    closed = {
        row["slot_id"]
        for row in closures
        if row["state"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE"
    }
    assert len(closures) == 10
    assert len(contracts) == len(frozen) == 6
    assert set(contracts) == frozen
    assert set(contracts).isdisjoint(closed)


def test_ordinal8_contract_ids_bind_slot_site_generator_and_domain():
    contracts = build_ordinal8_contracts(_closures())
    for slot_id, contract in contracts.items():
        expected = canonical_sha256(
            {
                "domain": CONTRACT_DOMAIN,
                "slot_id": slot_id,
                "generator_id": contract["generator_id"],
                "site_id": contract["site_id"],
                "contract_domain": contract["domain"],
            }
        )
        assert contract["contract_id"] == expected
    assert {row["generator_id"] for row in contracts.values()} == {
        "CONTRACT_ARRAY_DOMAIN_V1",
        "CONTRACT_RELATION_PAIR_DOMAIN_V1",
        "CONTRACT_SEQUENCE_DOMAIN_V1",
    }


def test_ordinal8_package_generates_thirty_rows_through_existing_seam():
    registry = validate_contract_generator_registry(
        read_canonical_json(REGISTRY_PATH), REPO_ROOT
    )
    package = freeze_ordinal8_package(closures=_closures(), registry=registry)
    assert set(package) == {"contracts", "inventories"}
    assert len(package["contracts"]) == len(package["inventories"]) == 6
    rows = [
        row
        for inventory in package["inventories"].values()
        for row in inventory["rows"]
    ]
    assert len(rows) == 30
    assert {row["status"] for row in rows} == {"CONTRACT_INPUT_GENERATED"}
    assert len({row["input_id"] for row in rows}) == 30


def test_ordinal8_package_rejects_an_alternate_valid_registry():
    raw = read_canonical_json(REGISTRY_PATH)
    raw["generators"][0]["failure_code"] = "ALTERNATE_ENUM_FAILURE"
    body = {key: value for key, value in raw.items() if key != "artifact_sha256"}
    raw["artifact_sha256"] = canonical_sha256(body)
    registry = validate_contract_generator_registry(raw, REPO_ROOT)
    with pytest.raises(EvidenceError, match="contract generator registry differs"):
        freeze_ordinal8_package(closures=_closures(), registry=registry)


def test_ordinal8_authority_fails_closed_on_missing_closure():
    with pytest.raises(Exception, match="ten ordinal-8 closures"):
        build_ordinal8_contracts(_closures()[:-1])


def test_ordinal8_authority_fails_closed_on_subject_identity_change():
    closures = _closures()
    closures[0] = {**closures[0], "controlled_subject_id": "00" * 32}
    with pytest.raises(Exception, match=ORDINAL8_SUBJECT_ID):
        build_ordinal8_contracts(closures)


def _freeze_cli():
    path = REPO_ROOT / "scripts/p3_v3/freeze_ordinal8_contracts.py"
    spec = importlib.util.spec_from_file_location("freeze_ordinal8_contracts", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cli_args(output_root: Path, closure_root: Path = CLOSURE_ROOT) -> list[str]:
    return [
        "--closure-root",
        str(closure_root),
        "--registry",
        str(REGISTRY_PATH),
        "--generator-root",
        str(REPO_ROOT),
        "--output-root",
        str(output_root),
    ]


def test_freeze_cli_atomically_writes_one_contract_map_and_six_inventories(tmp_path):
    output_root = tmp_path / "formal-output"
    result = _freeze_cli().main(_cli_args(output_root))
    assert result == 0
    assert not output_root.with_name(output_root.name + ".staging").exists()
    files = sorted(path.name for path in output_root.iterdir())
    assert files[0] == "contracts.json"
    assert len(files) == 7
    contracts = read_canonical_json(output_root / "contracts.json")
    assert len(contracts) == 6


def test_freeze_cli_refuses_existing_output_root(tmp_path):
    output_root = tmp_path / "formal-output"
    output_root.mkdir()
    with pytest.raises(EvidenceError, match="output root already exists"):
        _freeze_cli().main(_cli_args(output_root))
    assert list(output_root.iterdir()) == []


def test_freeze_cli_leaves_no_output_when_closure_identity_fails(tmp_path):
    closure_root = tmp_path / "closures"
    shutil.copytree(CLOSURE_ROOT, closure_root)
    target = next(closure_root.glob("*.json"))
    value = read_canonical_json(target)
    value["controlled_subject_id"] = "00" * 32
    target.write_bytes(canonical_json_bytes(value))
    output_root = tmp_path / "formal-output"
    with pytest.raises(EvidenceError, match=ORDINAL8_SUBJECT_ID):
        _freeze_cli().main(_cli_args(output_root, closure_root))
    assert not output_root.exists()
    assert not output_root.with_name(output_root.name + ".staging").exists()
