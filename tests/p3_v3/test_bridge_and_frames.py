from __future__ import annotations

import copy
import concurrent.futures
import hashlib
import inspect
import json
import shutil
import socket
import stat
import subprocess
import sys
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import pytest

import p3_v3.artifacts as artifacts_module
import p3_v3.bridge_and_frames as frames_module
from p3_v3.artifacts import EvidenceError, canonical_sha256, file_sha256
from p3_v3.bridge_and_frames import (
    BEHAVIOR_CATEGORY_ORDER,
    E_COMMON_COUNT,
    E_COMMON_GENERATOR_IDS,
    E_CONTRACT_COUNT,
    E_CONTRACT_GENERATOR_IDS,
    UNAVAILABLE_NOT_CLAIMED,
    build_common_inputs,
    build_contract_inputs,
    build_phase1_unresolved_profiling_receipt,
    build_public_behavior_frame,
    build_subject_frames,
    canonical_source_tree_sha256,
    classify_technique,
    close_slot,
    derive_source_scale,
    derive_subject_material,
    discover_subject_or_fail_closed,
    rebuild_indexed_subject,
    run_adapter_discovery,
    select_construct_subjects,
    select_first_applicable_site,
    select_profiling_workload,
    tag_site_reachability,
    validate_adapter_registry,
    validate_bridge_document,
    validate_common_inputs_on_fixed_source,
    validate_contract_generator_registry,
    validate_input_generator_registry,
    validate_mr_inventory,
    validate_proposal_record,
    verify_pinned_bridge,
    verify_reveal,
    verify_slot_chronology,
)

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "public_behavior"
ADAPTER_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "adapters"
GENERATOR_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "input_generators"
CONFIRMATORY_ADAPTERS = {
    "PYTHON_PEP517_V1",
    "CMAKE_CTEST_V1",
    "MESON_TEST_V1",
    "AUTOTOOLS_MAKECHECK_V1",
}
_ADAPTER_SPECS = (
    ("PYTHON_PEP517_V1", "python", "adapters/python_pep517_v1.py"),
    ("CMAKE_CTEST_V1", "cmake", "adapters/cmake_ctest_v1.py"),
    ("MESON_TEST_V1", "meson", "adapters/meson_test_v1.py"),
    ("AUTOTOOLS_MAKECHECK_V1", "autotools", "adapters/autotools_makecheck_v1.py"),
)


def _bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode() + b"\n"


def _sha(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def _source_tree_sha256(root: Path) -> str:
    excluded = {
        ".git",
        ".hg",
        ".svn",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "fixtures",
        "node_modules",
        "target",
        "vendor",
        "venv",
    }
    files = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if any(part.casefold() in excluded for part in Path(relative).parts):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        files.append(
            {
                "path": relative,
                "byte_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return canonical_sha256(
        {
            "domain": "P3-NORMALIZED-SOURCE-TREE-v1",
            "files": files,
        }
    )


def _source_snapshot(root: Path):
    entry_type = frames_module.SourceSnapshotEntry
    snapshot_type = frames_module.SourceSnapshot
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise EvidenceError(
                "E_SOURCE_TREE_PATH", "test source snapshot contains a symlink"
            )
        if not path.is_file() or ".git" in path.relative_to(root).parts:
            continue
        raw = path.read_bytes()
        entries.append(
            entry_type(
                relative_path=path.relative_to(root).as_posix(),
                mode="100755" if path.stat().st_mode & stat.S_IXUSR else "100644",
                sha256=hashlib.sha256(raw).hexdigest(),
                content=raw,
            )
        )
    entries.sort(key=lambda entry: entry.relative_path.encode("utf-8"))
    return snapshot_type(entries=tuple(entries))


@pytest.mark.parametrize("invalid_mode", ["100600", [], {}])
def test_source_snapshot_consumer_revalidates_entry_integrity(tmp_path, invalid_mode):
    assert hasattr(frames_module, "SourceSnapshotEntry")
    assert hasattr(frames_module, "SourceSnapshot")
    source = tmp_path / "source.py"
    source.write_bytes(b"value = 1\n")
    snapshot = _source_snapshot(tmp_path)
    object.__setattr__(snapshot.entries[0], "mode", invalid_mode)

    with pytest.raises(EvidenceError, match="E_SOURCE_SNAPSHOT"):
        frames_module.canonical_source_tree_sha256(snapshot)


def _run(root: Path, *argv: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *argv], capture_output=True, check=True, text=True
    )
    return result.stdout.strip()


@dataclass
class SyntheticRelease:
    root: Path
    lock: dict
    bridge: dict
    fixed_oid: str
    nonce_hex: str


@pytest.fixture
def synthetic_release(tmp_path) -> SyntheticRelease:
    root = tmp_path / "p12"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "P12 Fixture")
    _run(root, "config", "user.email", "p12@example.invalid")
    contract_path = "release/p3-contract.json"
    bridge_path = "release/p3-bridge.json"
    (root / "release").mkdir()
    contract = {"schema_version": "p12-p3-contract-v2", "claim": "fixture"}
    (root / contract_path).write_bytes(_bytes(contract))
    contract_blob = _run(root, "hash-object", contract_path)

    package_root = "1" * 64
    source_sha = "2" * 64
    archive_sha = "3" * 64
    build_sha = "4" * 64
    fixed_oid = "5" * 40
    nonce = bytes.fromhex("6" * 64)
    commitment = hashlib.sha256(
        b"P3-FIXED-TREE-v1"
        + package_root.encode()
        + fixed_oid.encode()
        + nonce
    ).hexdigest()
    neutral = _sha(
        {
            "p12_package_root_sha256": package_root,
            "normalized_source_tree_sha256": source_sha,
            "source_archive_sha256": archive_sha,
            "domain": "P3-NEUTRAL-SNAPSHOT-v1",
        }
    )
    records = [
        {
            "neutral_snapshot_id": neutral,
            "fixed_tree_commitment": commitment,
            "normalized_source_tree_sha256": source_sha,
            "source_archive_sha256": archive_sha,
            "build_descriptor_sha256": build_sha,
            "eligibility_reason": "synthetic complete record",
            "eligible_for_construct": True,
            "eligible_for_criterion": True,
        }
    ]
    body = {
        "schema_version": "p3-p12-bridge-v1",
        "p12_release_id": "p12-synthetic-v2",
        "p12_repository_identity": "example/P12-Defect4MR",
        "p12_contract_path": contract_path,
        "p12_contract_blob_sha": contract_blob,
        "p12_package_root_sha256": package_root,
        "p12_contract_sha256": hashlib.sha256(_bytes(contract)).hexdigest(),
        "eligible_inventory_root_sha256": _sha(records),
        "eligible_item_count": 1,
        "records": records,
        "trust_mode": "PINNED_GIT_RELEASE",
    }
    bridge = {**body, "artifact_sha256": _sha(body)}
    (root / bridge_path).write_bytes(_bytes(bridge))
    _run(root, "add", "release")
    _run(root, "commit", "-m", "release fixture")
    release_commit = _run(root, "rev-parse", "HEAD")
    bridge_blob = _run(root, "rev-parse", f"{release_commit}:{bridge_path}")
    contract_blob = _run(root, "rev-parse", f"{release_commit}:{contract_path}")
    lock = {
        "repository_identity": "example/P12-Defect4MR",
        "release_commit_sha": release_commit,
        "bridge_path": bridge_path,
        "bridge_blob_sha": bridge_blob,
        "contract_path": contract_path,
        "contract_blob_sha": contract_blob,
        "package_root_sha256": package_root,
    }
    return SyntheticRelease(root, lock, bridge, fixed_oid, nonce.hex())


def test_bridge_is_read_from_exact_pinned_git_release(synthetic_release):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    assert verified["trust_mode"] == "PINNED_GIT_RELEASE"
    assert verified["eligible_item_count"] == 1


def test_bridge_rejects_wrong_external_blob_pin(synthetic_release):
    lock = {**synthetic_release.lock, "bridge_blob_sha": "0" * 40}
    with pytest.raises(EvidenceError, match="E_PINNED_BRIDGE_BLOB"):
        verify_pinned_bridge(synthetic_release.root, lock)


def _self_hashed(body: dict) -> dict:
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _mr_chain():
    candidate = _self_hashed(
        {
            "schema_version": "p3-mr-candidate-frame-v1",
            "artifact_type": "MR_CANDIDATE_FRAME",
            "candidate_mr_ids": ["mr-1", "mr-2"],
        }
    )
    receipt = _self_hashed(
        {
            "schema_version": "p3-mr-custodian-receipt-v1",
            "artifact_type": "MR_CUSTODIAN_RECEIPT",
            "candidate_frame_sha256": candidate["artifact_sha256"],
            "receipt_state": "CLOSED",
            "admitted_mr_ids": ["mr-1"],
            "excluded_mr_ids": ["mr-2"],
        }
    )
    final_inventory = _self_hashed(
        {
            "schema_version": "p3-mr-final-inventory-v1",
            "artifact_type": "MR_FINAL_INVENTORY",
            "custodian_receipt_sha256": receipt["artifact_sha256"],
            "mr_ids": ["mr-1"],
        }
    )
    portfolios = _self_hashed(
        {
            "schema_version": "p3-mr-portfolios-v1",
            "artifact_type": "MR_PORTFOLIOS",
            "final_inventory_sha256": final_inventory["artifact_sha256"],
            "portfolios": [
                {"portfolio_id": "portfolio-1", "mr_ids": ["mr-1"]}
            ],
        }
    )
    return candidate, receipt, final_inventory, portfolios


def _rehashed(artifact: dict, **changes) -> dict:
    body = {
        key: value
        for key, value in {**artifact, **changes}.items()
        if key != "artifact_sha256"
    }
    return _self_hashed(body)


def test_mr_chain_accepts_exact_hash_parent_chain():
    validate_mr_inventory(*_mr_chain())


@pytest.mark.parametrize(
    ("artifact_index", "artifact_type"),
    [
        (0, "MR_FINAL_INVENTORY"),
        (1, "MR_PORTFOLIOS"),
        (2, "MR_CANDIDATE_FRAME"),
        (3, "MR_CUSTODIAN_RECEIPT"),
    ],
)
def test_mr_chain_rejects_mutated_exact_artifact_type(
    artifact_index, artifact_type
):
    artifacts = list(_mr_chain())
    artifacts[artifact_index] = _rehashed(
        artifacts[artifact_index], artifact_type=artifact_type
    )
    with pytest.raises(EvidenceError, match="E_MR_ARTIFACT_TYPE"):
        validate_mr_inventory(*artifacts)


@pytest.mark.parametrize("artifact_index", range(4))
def test_mr_chain_rejects_mutated_self_hash(artifact_index):
    artifacts = list(_mr_chain())
    artifacts[artifact_index] = {
        **artifacts[artifact_index],
        "artifact_sha256": "0" * 64,
    }
    with pytest.raises(EvidenceError, match="E_MR_ARTIFACT_HASH"):
        validate_mr_inventory(*artifacts)


@pytest.mark.parametrize(
    ("artifact_index", "parent_field"),
    [
        (1, "candidate_frame_sha256"),
        (2, "custodian_receipt_sha256"),
        (3, "final_inventory_sha256"),
    ],
)
def test_mr_chain_rejects_mutated_parent_reference(artifact_index, parent_field):
    artifacts = list(_mr_chain())
    artifacts[artifact_index] = _rehashed(
        artifacts[artifact_index], **{parent_field: "9" * 64}
    )
    with pytest.raises(EvidenceError, match="E_MR_PARENT"):
        validate_mr_inventory(*artifacts)


def test_mr_chain_receipt_is_fail_closed_and_partitions_candidates():
    candidate, receipt, final_inventory, portfolios = _mr_chain()
    open_receipt = _rehashed(receipt, receipt_state="OPEN")
    with pytest.raises(EvidenceError, match="E_MR_RECEIPT_STATE"):
        validate_mr_inventory(candidate, open_receipt, final_inventory, portfolios)

    incomplete_receipt = _rehashed(receipt, excluded_mr_ids=[])
    with pytest.raises(EvidenceError, match="E_MR_RECEIPT_MEMBERSHIP"):
        validate_mr_inventory(
            candidate,
            incomplete_receipt,
            final_inventory,
            portfolios,
        )


def test_mr_chain_final_inventory_and_portfolios_bind_admitted_membership():
    candidate, receipt, final_inventory, portfolios = _mr_chain()
    wrong_inventory = _rehashed(final_inventory, mr_ids=["mr-2"])
    with pytest.raises(EvidenceError, match="E_MR_INVENTORY_MEMBERSHIP"):
        validate_mr_inventory(candidate, receipt, wrong_inventory, portfolios)

    wrong_portfolios = _rehashed(
        portfolios,
        portfolios=[{"portfolio_id": "portfolio-1", "mr_ids": ["mr-2"]}],
    )
    with pytest.raises(EvidenceError, match="E_MR_PORTFOLIO_MEMBERSHIP"):
        validate_mr_inventory(
            candidate,
            receipt,
            final_inventory,
            wrong_portfolios,
        )


@pytest.mark.parametrize("artifact_index", range(4))
def test_mr_chain_requires_exact_top_level_keys(artifact_index):
    artifacts = list(_mr_chain())
    artifacts[artifact_index] = _rehashed(
        artifacts[artifact_index], chronology=["untrusted-declaration"]
    )
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        validate_mr_inventory(*artifacts)


def test_chronology_list_with_four_unrelated_hashes_is_not_mr_chain_evidence():
    legacy_body = {
        "schema_version": "p3-mr-inventory-v1",
        "candidate_frame_sha256": canonical_sha256({"stage": "candidate"}),
        "custodian_receipt_sha256": canonical_sha256({"stage": "receipt"}),
        "final_inventory_sha256": canonical_sha256({"stage": "final"}),
        "portfolios_sha256": canonical_sha256({"stage": "portfolios"}),
        "chronology": [
            "candidate_frame",
            "custodian_receipt",
            "final_inventory",
            "portfolios",
        ],
    }
    with pytest.raises(TypeError):
        validate_mr_inventory(_self_hashed(legacy_body))


def test_visible_bridge_rejects_fixed_tree_oid_even_when_rehashed(synthetic_release):
    bridge = json.loads(json.dumps(synthetic_release.bridge))
    bridge["records"][0]["fixed_git_tree_oid"] = synthetic_release.fixed_oid
    body = {key: value for key, value in bridge.items() if key != "artifact_sha256"}
    bridge["artifact_sha256"] = _sha(body)
    with pytest.raises(EvidenceError, match="E_BRIDGE_RECORD_KEYS"):
        validate_bridge_document(bridge, synthetic_release.lock)


def _features(neutral_id: str):
    return [
        {
            "neutral_snapshot_id": neutral_id,
            "public_workload_set_sha256": "7" * 64,
            "scale_class": "S",
            "primary_technique": "ARRAY_NUMERICAL",
            "technique_vector": ["ARRAY_NUMERICAL", "SCALAR_CONTROL"],
            "sites": [
                {
                    "path": "src/a.py",
                    "symbol": "solve",
                    "start_line": 10,
                    "start_col": 4,
                    "end_line": 10,
                    "end_col": 20,
                }
            ],
        }
    ]


def test_build_subject_frames_rejects_legacy_caller_authority(synthetic_release):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    features = _features(verified["records"][0]["neutral_snapshot_id"])
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        build_subject_frames(verified, features)


def test_subject_frame_rejects_missing_derived_subject(synthetic_release):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    with pytest.raises(EvidenceError, match="E_SUBJECT_SPEC_COVERAGE"):
        build_subject_frames(verified, [])


def _subject(subject_id: str, technique: str) -> dict:
    return {
        "controlled_subject_id": subject_id,
        "scale_class": "S",
        "primary_technique": technique,
        "technique_vector": [technique],
    }


def test_construct_selection_continues_strict_round_robin_by_cell():
    subjects = [
        _subject("1" * 64, "ARRAY_NUMERICAL"),
        _subject("2" * 64, "ARRAY_NUMERICAL"),
        _subject("3" * 64, "SCALAR_CONTROL"),
        _subject("4" * 64, "SCALAR_CONTROL"),
    ]
    selected = select_construct_subjects(
        subjects, {item["controlled_subject_id"] for item in subjects}, limit=4
    )
    cell_by_id = {
        item["controlled_subject_id"]: item["primary_technique"] for item in subjects
    }
    assert [cell_by_id[item] for item in selected] == [
        "ARRAY_NUMERICAL",
        "SCALAR_CONTROL",
        "ARRAY_NUMERICAL",
        "SCALAR_CONTROL",
    ]


def test_slot_selects_first_applicable_canonical_site_or_none():
    sites = [
        {
            "path": "a.py",
            "symbol": "f",
            "start_line": 1,
            "start_col": 0,
            "end_line": 1,
            "end_col": 1,
            "site_id": "1" * 64,
        },
        {
            "path": "b.py",
            "symbol": "g",
            "start_line": 2,
            "start_col": 0,
            "end_line": 2,
            "end_col": 1,
            "site_id": "2" * 64,
        },
    ]
    assert select_first_applicable_site(sites, lambda site: site["symbol"] in {"f", "g"}) == "1" * 64
    assert select_first_applicable_site(sites, lambda _site: False) is None


def test_reveal_binds_nonce_oid_commitment_and_normalized_source(synthetic_release):
    record = synthetic_release.bridge["records"][0]
    reveal = {
        "neutral_snapshot_id": record["neutral_snapshot_id"],
        "fixed_git_tree_oid": synthetic_release.fixed_oid,
        "reveal_nonce": synthetic_release.nonce_hex,
        "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
    }
    verify_reveal(
        record,
        reveal,
        synthetic_release.bridge["p12_package_root_sha256"],
        observed_tree_oid=synthetic_release.fixed_oid,
        observed_normalized_sha256=record["normalized_source_tree_sha256"],
    )
    bad = {**reveal, "reveal_nonce": "0" * 64}
    with pytest.raises(EvidenceError, match="E_REVEAL_COMMITMENT"):
        verify_reveal(
            record,
            bad,
            synthetic_release.bridge["p12_package_root_sha256"],
            observed_tree_oid=synthetic_release.fixed_oid,
            observed_normalized_sha256=record["normalized_source_tree_sha256"],
        )


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def _adapter_registry(tmp_path: Path) -> dict:
    adapters = []
    for adapter_id, ecosystem, rel in _ADAPTER_SPECS:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        fixture = ADAPTER_FIXTURE_ROOT / Path(rel).name
        if fixture.is_file():
            shutil.copyfile(fixture, path)
        else:
            path.write_text(f"# adapter {adapter_id}\n", encoding="utf-8")
        adapters.append(
            {
                "adapter_id": adapter_id,
                "ecosystem": ecosystem,
                "implementation_path": rel,
                "source_sha256": file_sha256(path),
            }
        )
    body = {
        "schema_version": "p3-adapter-registry-v1",
        "adapters": adapters,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _source_record() -> dict:
    return {
        "normalized_source_tree_sha256": "21" * 32,
        "build_descriptor_sha256": "22" * 32,
    }


def _tagged_declarations(fixture: dict) -> list[dict]:
    rows = []
    for item in fixture["declarations"]:
        row = copy.deepcopy(item)
        row["ecosystem"] = fixture["ecosystem"]
        if fixture.get("adapter_id") is not None:
            row["adapter_id"] = fixture["adapter_id"]
        rows.append(row)
    return rows


def _combined_executable_declarations() -> list[dict]:
    return _tagged_declarations(_load_fixture("python.json")) + _tagged_declarations(
        _load_fixture("cmake.json")
    )


def _discovery_receipt(
    declarations: list[dict],
    *,
    adapter_id: str | None = "PYTHON_PEP517_V1",
    ecosystem: str = "python",
    status: str = "EXECUTABLE",
    public_schemas: list[dict] | None = None,
    sites: list[dict] | None = None,
) -> dict:
    normalized_declarations = copy.deepcopy(declarations)
    for declaration in normalized_declarations:
        for field in ("static_dependency_tags", "prerequisites"):
            collection = declaration.get(field)
            if isinstance(collection, list) and all(
                isinstance(item, str) for item in collection
            ):
                declaration[field] = sorted(set(collection))
    body = {
        "schema_version": "p3-adapter-discovery-v1",
        "adapter_id": adapter_id,
        "ecosystem": ecosystem,
        "discovery_status": status,
        "implementation_source_sha256": "31" * 32 if adapter_id is not None else None,
        "source_files": [],
        "declarations": sorted(normalized_declarations, key=_bytes),
        "public_schemas": sorted(public_schemas or [], key=_bytes),
        "sites": sorted(sites or [], key=_bytes),
        "unsupported_or_exclusion_reason": ""
        if status == "EXECUTABLE"
        else "ecosystem has no confirmatory adapter; hand-selected commands are forbidden",
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _write_adapter_project(root: Path, fixture_name: str, *, reverse: bool = False) -> dict:
    fixture = _load_fixture(fixture_name)
    source_files = fixture["source_files"]
    for index, relative in enumerate(source_files):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        suffix = path.suffix
        if suffix == ".py":
            path.write_text("# ignored\n\ndef solve(value):\n    return value\n", encoding="utf-8")
        elif suffix in {".hpp", ".cpp", ".cc", ".cxx", ".h"}:
            path.write_text(
                "// ignored\nint solve(int value) { return value; }\n",
                encoding="utf-8",
            )
        else:
            path.write_text(f"source-{index}\n", encoding="utf-8")
    manifest = root / f"adapter-{fixture['ecosystem']}.json"
    manifest.write_bytes(_bytes(fixture))
    return {"manifest_path": manifest.name, "reverse": reverse}


def _derived_subject_spec(
    root: Path,
    fixture_name: str,
    record: dict,
    adapter_registry: dict,
    generator_registry: dict,
    technique: str,
    *,
    effective_lines: int | None = None,
) -> dict:
    descriptor = _write_adapter_project(root, fixture_name)
    if effective_lines is not None:
        source_path = root / _load_fixture(fixture_name)["source_files"][0]
        source_path.write_text("int value = 1;\n" * effective_lines, encoding="utf-8")
    ecosystem = _load_fixture(fixture_name)["ecosystem"]
    descriptor = {**descriptor, "ecosystem": ecosystem}
    source_snapshot = _source_snapshot(root)
    record["normalized_source_tree_sha256"] = _source_tree_sha256(root)
    record["build_descriptor_sha256"] = canonical_sha256(descriptor)
    adapter_id = {
        "python": "PYTHON_PEP517_V1",
        "cmake": "CMAKE_CTEST_V1",
    }[ecosystem]
    discovery = run_adapter_discovery(
        source_snapshot, descriptor, adapter_registry, adapter_id
    )
    frame = build_public_behavior_frame(
        {
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
        },
        discovery,
    )
    scale = derive_source_scale(source_snapshot, discovery)["scale_class"]
    workload = select_profiling_workload(frame, scale)
    profiling_results = _profiling_receipt(
        workload,
        [_success(row["behavior_id"], technique) for row in workload["selected_rows"]],
        neutral_snapshot_id=record["neutral_snapshot_id"],
        normalized_source_tree_sha256=record["normalized_source_tree_sha256"],
        build_descriptor_sha256=record["build_descriptor_sha256"],
        adapter_implementation_source_sha256=discovery[
            "implementation_source_sha256"
        ],
    )
    return {
        "neutral_snapshot_id": record["neutral_snapshot_id"],
        "source_snapshot": source_snapshot,
        "source_record": {
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
        },
        "build_descriptor": descriptor,
        "adapter_registry": adapter_registry,
        "input_generator_registry": generator_registry,
        "profiling_results": profiling_results,
    }


def test_subject_material_recomputes_source_tree_commitment_before_adapter(
    synthetic_release, tmp_path
):
    adapter_root = tmp_path / "adapters"
    adapter_root.mkdir()
    adapter_registry = validate_adapter_registry(
        _adapter_registry(adapter_root), _source_snapshot(adapter_root)
    )
    generator_registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    record = verify_pinned_bridge(
        synthetic_release.root, synthetic_release.lock
    )["records"][0]
    source_root = tmp_path / "python-subject"
    source_root.mkdir()
    spec = _derived_subject_spec(
        source_root,
        "python.json",
        record,
        adapter_registry,
        generator_registry,
        "SCALAR_CONTROL",
    )
    source_path = source_root / _load_fixture("python.json")["source_files"][0]
    source_path.write_bytes(source_path.read_bytes() + b"\n# unauthorized mutation\n")
    spec["source_snapshot"] = _source_snapshot(source_root)

    with pytest.raises(EvidenceError, match="E_SOURCE_TREE_COMMITMENT"):
        frames_module.derive_subject_material(spec, record)


def _subject_index_for_rederivation(spec: dict, material: dict, adapter_root: Path) -> dict:
    return {
        "source_snapshot": spec["source_snapshot"],
        "source_record": spec["source_record"],
        "build_descriptor": spec["build_descriptor"],
        "adapter_registry": spec["adapter_registry"],
        "input_generator_registry": spec["input_generator_registry"],
        "profiling_results": spec["profiling_results"],
        "adapter_discovery": material["adapter_discovery"],
        "source_scale": material["source_scale"],
        "public_frame": material["public_behavior_frame"],
        "profiling_workload": material["profiling_workload"],
        "common_inputs": material["common_inputs"],
        "technique_profile": material["technique_profile"],
        "sites": material["subject"]["sites"],
        "subject": material["subject"],
    }


@pytest.mark.parametrize(
    "mutation",
    ["declaration", "scale", "workload", "site", "technique", "schema"],
)
def test_rederive_subject_rejects_rehashed_declared_derivation(
    synthetic_release, tmp_path, mutation
):
    adapter_root = tmp_path / "rederive-adapters"
    adapter_root.mkdir()
    adapter_registry = validate_adapter_registry(
        _adapter_registry(adapter_root), _source_snapshot(adapter_root)
    )
    generator_registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    record = verify_pinned_bridge(
        synthetic_release.root, synthetic_release.lock
    )["records"][0]
    source_root = tmp_path / "rederive-subject"
    source_root.mkdir()
    spec = _derived_subject_spec(
        source_root,
        "python.json",
        record,
        adapter_registry,
        generator_registry,
        "SCALAR_CONTROL",
    )
    material = frames_module.derive_subject_material(spec, record)
    indexed = _subject_index_for_rederivation(spec, material, adapter_root)

    if mutation == "declaration":
        indexed["public_frame"]["rows"][0]["entrypoint"] += "_forged"
        indexed["public_frame"]["artifact_sha256"] = canonical_sha256(
            {k: v for k, v in indexed["public_frame"].items() if k != "artifact_sha256"}
        )
    elif mutation == "scale":
        indexed["source_scale"]["scale_class"] = "L"
        indexed["source_scale"]["artifact_sha256"] = canonical_sha256(
            {k: v for k, v in indexed["source_scale"].items() if k != "artifact_sha256"}
        )
    elif mutation == "workload":
        indexed["profiling_workload"]["budget"] += 1
        indexed["profiling_workload"]["artifact_sha256"] = canonical_sha256(
            {
                k: v
                for k, v in indexed["profiling_workload"].items()
                if k != "artifact_sha256"
            }
        )
    elif mutation == "site":
        indexed["sites"][0]["symbol"] += "_forged"
    elif mutation == "technique":
        indexed["technique_profile"]["primary_technique"] = "HYBRID_NATIVE"
        indexed["technique_profile"]["artifact_sha256"] = canonical_sha256(
            {
                k: v
                for k, v in indexed["technique_profile"].items()
                if k != "artifact_sha256"
            }
        )
    else:
        indexed["public_frame"]["public_schemas"][0]["schema_kind"] = "forged"
        indexed["public_frame"]["artifact_sha256"] = canonical_sha256(
            {k: v for k, v in indexed["public_frame"].items() if k != "artifact_sha256"}
        )

    with pytest.raises(EvidenceError, match="E_INDEXED_SUBJECT_REDERIVATION"):
        rebuild_indexed_subject(indexed, record)


def test_rederive_subject_starts_from_source_and_adapter_bytes(
    synthetic_release, tmp_path
):
    adapter_root = tmp_path / "rederive-byte-adapters"
    adapter_root.mkdir()
    adapter_registry = validate_adapter_registry(
        _adapter_registry(adapter_root), _source_snapshot(adapter_root)
    )
    generator_registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    record = verify_pinned_bridge(
        synthetic_release.root, synthetic_release.lock
    )["records"][0]
    source_root = tmp_path / "rederive-byte-subject"
    source_root.mkdir()
    spec = _derived_subject_spec(
        source_root,
        "python.json",
        record,
        adapter_registry,
        generator_registry,
        "SCALAR_CONTROL",
    )
    material = frames_module.derive_subject_material(spec, record)
    indexed = _subject_index_for_rederivation(spec, material, adapter_root)

    rebuilt = rebuild_indexed_subject(indexed, record)
    assert rebuilt == material

    source_path = source_root / _load_fixture("python.json")["source_files"][0]
    source_path.write_bytes(source_path.read_bytes() + b"# mutation\n")
    indexed["source_snapshot"] = _source_snapshot(source_root)
    with pytest.raises(EvidenceError, match="E_INDEXED_SUBJECT_REDERIVATION"):
        rebuild_indexed_subject(indexed, record)


@pytest.mark.parametrize(
    "relative_path",
    ["vendor/runtime.py", "fixtures/external/input.json"],
)
def test_source_tree_commitment_binds_vendor_fixture_and_external_bytes(
    synthetic_release, tmp_path, relative_path
):
    adapter_root = tmp_path / "adapters"
    adapter_root.mkdir()
    adapter_registry = validate_adapter_registry(
        _adapter_registry(adapter_root), _source_snapshot(adapter_root)
    )
    generator_registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    record = verify_pinned_bridge(
        synthetic_release.root, synthetic_release.lock
    )["records"][0]
    source_root = tmp_path / "python-subject"
    source_root.mkdir()
    included = source_root / relative_path
    included.parent.mkdir(parents=True)
    included.write_bytes(b"project-material-v1")
    spec = _derived_subject_spec(
        source_root,
        "python.json",
        record,
        adapter_registry,
        generator_registry,
        "SCALAR_CONTROL",
    )
    committed = record["normalized_source_tree_sha256"]

    included.write_bytes(b"project-material-v2")

    changed_snapshot = _source_snapshot(source_root)
    assert frames_module.canonical_source_tree_sha256(changed_snapshot) != committed
    spec["source_snapshot"] = changed_snapshot
    with pytest.raises(EvidenceError, match="E_SOURCE_TREE_COMMITMENT"):
        frames_module.derive_subject_material(spec, record)


def test_source_tree_commitment_sorts_all_project_files_and_excludes_only_vcs_metadata(
    tmp_path,
):
    root = tmp_path / "source"
    (root / "a").mkdir(parents=True)
    (root / ".git").mkdir()
    (root / "vendor").mkdir()
    (root / "a/z.txt").write_bytes(b"nested")
    (root / "a.txt").write_bytes(b"root")
    (root / "vendor/runtime.py").write_bytes(b"vendored")
    (root / ".git/index").write_bytes(b"vcs-v1")
    expected = canonical_sha256(
        {
            "domain": "P3-NORMALIZED-SOURCE-TREE-v1",
            "files": [
                {
                    "path": "a.txt",
                    "byte_sha256": hashlib.sha256(b"root").hexdigest(),
                },
                {
                    "path": "a/z.txt",
                    "byte_sha256": hashlib.sha256(b"nested").hexdigest(),
                },
                {
                    "path": "vendor/runtime.py",
                    "byte_sha256": hashlib.sha256(b"vendored").hexdigest(),
                },
            ],
        }
    )

    observed = frames_module.canonical_source_tree_sha256(_source_snapshot(root))
    (root / ".git/index").write_bytes(b"vcs-v2")

    assert observed == expected
    assert frames_module.canonical_source_tree_sha256(_source_snapshot(root)) == expected


@pytest.mark.parametrize("transient", ["build/output.o", ".venv/bin/python"])
def test_source_tree_commitment_rejects_transient_build_or_environment_output(
    tmp_path, transient
):
    root = tmp_path / "source"
    root.mkdir()
    path = root / transient
    path.parent.mkdir(parents=True)
    path.write_bytes(b"transient")

    with pytest.raises(EvidenceError, match="E_SOURCE_TREE_PATH"):
        frames_module.canonical_source_tree_sha256(_source_snapshot(root))


def test_source_tree_commitment_rejects_included_symlink(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    target = root / "target.txt"
    target.write_bytes(b"target")
    (root / "alias.txt").symlink_to(target)

    with pytest.raises(EvidenceError, match="E_SOURCE_TREE_PATH"):
        frames_module.canonical_source_tree_sha256(_source_snapshot(root))


def test_subject_material_recomputes_build_descriptor_commitment_before_adapter(
    synthetic_release, tmp_path
):
    adapter_root = tmp_path / "adapters"
    adapter_root.mkdir()
    adapter_registry = validate_adapter_registry(
        _adapter_registry(adapter_root), _source_snapshot(adapter_root)
    )
    generator_registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    record = verify_pinned_bridge(
        synthetic_release.root, synthetic_release.lock
    )["records"][0]
    source_root = tmp_path / "python-subject"
    source_root.mkdir()
    spec = _derived_subject_spec(
        source_root,
        "python.json",
        record,
        adapter_registry,
        generator_registry,
        "SCALAR_CONTROL",
    )
    spec["build_descriptor"] = {**spec["build_descriptor"], "reverse": True}

    with pytest.raises(EvidenceError, match="E_BUILD_DESCRIPTOR_COMMITMENT"):
        frames_module.derive_subject_material(spec, record)


def test_two_subject_material_is_fully_derived_and_order_invariant(
    synthetic_release, tmp_path
):
    derive_subject_material = getattr(frames_module, "derive_subject_material", None)
    assert callable(derive_subject_material)
    adapter_root = tmp_path / "adapters"
    adapter_root.mkdir()
    adapter_registry = validate_adapter_registry(
        _adapter_registry(adapter_root), _source_snapshot(adapter_root)
    )
    generator_registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    python_record = verified["records"][0]
    cmake_record = {
        **python_record,
        "neutral_snapshot_id": "7" * 64,
        "normalized_source_tree_sha256": "8" * 64,
        "build_descriptor_sha256": "9" * 64,
        "fixed_tree_commitment": "a" * 64,
    }
    bridge = {**verified, "records": [python_record, cmake_record]}
    python_root = tmp_path / "python-subject"
    cmake_root = tmp_path / "cmake-subject"
    python_root.mkdir()
    cmake_root.mkdir()
    python_spec = _derived_subject_spec(
        python_root,
        "python.json",
        python_record,
        adapter_registry,
        generator_registry,
        "SCALAR_CONTROL",
    )
    cmake_spec = _derived_subject_spec(
        cmake_root,
        "cmake.json",
        cmake_record,
        adapter_registry,
        generator_registry,
        "ARRAY_NUMERICAL",
        effective_lines=10_000,
    )

    python_material = derive_subject_material(python_spec, python_record)
    cmake_material = derive_subject_material(cmake_spec, cmake_record)
    assert set(python_material) == {
        "neutral_snapshot_id",
        "controlled_subject_source_id",
        "adapter_discovery",
        "adapter_discovery_sha256",
        "source_scale",
        "source_scale_sha256",
        "public_behavior_frame",
        "public_behavior_frame_sha256",
        "profiling_workload",
        "profiling_workload_sha256",
        "common_inputs",
        "common_inputs_sha256",
        "profiling_results",
        "profiling_results_sha256",
        "technique_profile",
        "technique_profile_sha256",
        "subject",
        "artifact_sha256",
    }
    assert python_material["adapter_discovery"]["ecosystem"] == "python"
    assert cmake_material["adapter_discovery"]["ecosystem"] == "cmake"
    assert python_material["source_scale"]["scale_class"] == "S"
    assert cmake_material["source_scale"]["scale_class"] == "M"
    for field in (
        "adapter_discovery",
        "source_scale",
        "public_behavior_frame",
        "profiling_workload",
        "common_inputs",
        "technique_profile",
    ):
        assert (
            python_material[field]["artifact_sha256"]
            != cmake_material[field]["artifact_sha256"]
        )
    assert canonical_sha256(python_material["subject"]["sites"]) != canonical_sha256(
        cmake_material["subject"]["sites"]
    )
    assert [row["ordinal"] for row in python_material["common_inputs"]["rows"]] == list(
        range(30)
    )
    assert any(
        row["status"] == "COMMON_INPUT_EXECUTABLE"
        for row in python_material["common_inputs"]["rows"]
    )
    assert all(
        row["schema_provenance_path"] and row["generator_source_sha256"]
        for row in python_material["common_inputs"]["rows"]
    )

    first = build_subject_frames(bridge, [python_material, cmake_material])
    second = build_subject_frames(bridge, [cmake_material, python_material])
    assert _bytes(first) == _bytes(second)


def _two_subject_material_fixture(synthetic_release, tmp_path):
    adapter_root = tmp_path / "parent-binding-adapters"
    adapter_root.mkdir()
    adapter_registry = validate_adapter_registry(
        _adapter_registry(adapter_root), _source_snapshot(adapter_root)
    )
    generator_registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    python_record = verified["records"][0]
    cmake_record = {
        **python_record,
        "neutral_snapshot_id": "b" * 64,
        "fixed_tree_commitment": "c" * 64,
    }
    python_root = tmp_path / "parent-python"
    cmake_root = tmp_path / "parent-cmake"
    python_root.mkdir()
    cmake_root.mkdir()
    python_spec = _derived_subject_spec(
        python_root,
        "python.json",
        python_record,
        adapter_registry,
        generator_registry,
        "SCALAR_CONTROL",
    )
    cmake_spec = _derived_subject_spec(
        cmake_root,
        "cmake.json",
        cmake_record,
        adapter_registry,
        generator_registry,
        "ARRAY_NUMERICAL",
        effective_lines=10_000,
    )
    bridge = {**verified, "records": [python_record, cmake_record]}
    return (
        bridge,
        frames_module.derive_subject_material(python_spec, python_record),
        frames_module.derive_subject_material(cmake_spec, cmake_record),
    )


def test_derived_subject_artifacts_carry_direct_parent_bindings(
    synthetic_release, tmp_path
):
    _bridge, material, _other = _two_subject_material_fixture(
        synthetic_release, tmp_path
    )
    neutral = material["neutral_snapshot_id"]
    source_id = material["controlled_subject_source_id"]

    assert material["adapter_discovery"]["neutral_snapshot_id"] == neutral
    assert material["adapter_discovery"]["controlled_subject_source_id"] == source_id
    assert material["source_scale"]["neutral_snapshot_id"] == neutral
    assert material["source_scale"]["controlled_subject_source_id"] == source_id
    assert material["source_scale"]["discovery_sha256"] == material[
        "adapter_discovery"
    ]["artifact_sha256"]
    assert material["technique_profile"]["neutral_snapshot_id"] == neutral
    assert material["technique_profile"]["controlled_subject_source_id"] == source_id
    assert material["technique_profile"]["profiling_workload_sha256"] == material[
        "profiling_workload"
    ]["artifact_sha256"]
    assert material["technique_profile"]["profiling_results_sha256"] == material[
        "profiling_results"
    ]["artifact_sha256"]
    for field in (
        "adapter_discovery",
        "source_scale",
        "public_behavior_frame",
        "profiling_workload",
        "common_inputs",
        "profiling_results",
        "technique_profile",
    ):
        assert material[f"{field}_sha256"] == material[field]["artifact_sha256"]


@pytest.mark.parametrize(
    "field", ["adapter_discovery", "source_scale", "technique_profile"]
)
def test_subject_frames_reject_cross_subject_parent_swap_after_rehash(
    synthetic_release, tmp_path, field
):
    bridge, first, second = _two_subject_material_fixture(synthetic_release, tmp_path)
    forged_body = {
        key: copy.deepcopy(value)
        for key, value in first.items()
        if key != "artifact_sha256"
    }
    forged_body[field] = copy.deepcopy(second[field])
    forged = {**forged_body, "artifact_sha256": canonical_sha256(forged_body)}

    with pytest.raises(EvidenceError, match="E_DERIVED_SUBJECT_BINDING"):
        build_subject_frames(bridge, [forged, second])


def _rehash_material_artifact(material: dict, field: str) -> None:
    body = {
        key: value
        for key, value in material[field].items()
        if key != "artifact_sha256"
    }
    material[field] = {**body, "artifact_sha256": canonical_sha256(body)}
    material[f"{field}_sha256"] = material[field]["artifact_sha256"]


def _rehash_derived_material(material: dict) -> dict:
    body = {key: value for key, value in material.items() if key != "artifact_sha256"}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _site_with_subject_id(site: dict, subject_id: str) -> dict:
    raw = {key: value for key, value in site.items() if key != "site_id"}
    site_id = canonical_sha256(
        {"controlled_subject_id": subject_id, **raw, "domain": "P3-SITE-v1"}
    )
    return {**raw, "site_id": site_id}


@pytest.mark.parametrize(
    "mutation",
    [
        "subject_id",
        "scale_L",
        "technique_hybrid_native",
        "fake_workload",
        "canonical_site",
        "profiling_parent",
    ],
)
def test_subject_frames_recompute_nested_derivations_after_layered_rehash(
    synthetic_release, tmp_path, mutation
):
    bridge, material, other = _two_subject_material_fixture(
        synthetic_release, tmp_path
    )
    forged = copy.deepcopy(material)
    subject = forged["subject"]

    if mutation == "subject_id":
        subject["controlled_subject_id"] = "d" * 64
    elif mutation == "scale_L":
        forged["source_scale"]["scale_class"] = "L"
        _rehash_material_artifact(forged, "source_scale")
        subject["scale_class"] = "L"
    elif mutation == "technique_hybrid_native":
        forged["technique_profile"].update(
            {
                "confirmed_tags": ["HYBRID_NATIVE"],
                "possible_tags": ["HYBRID_NATIVE"],
                "primary_technique": "HYBRID_NATIVE",
            }
        )
        _rehash_material_artifact(forged, "technique_profile")
        subject["primary_technique"] = "HYBRID_NATIVE"
        subject["technique_vector"] = ["HYBRID_NATIVE"]
    elif mutation == "fake_workload":
        forged["profiling_workload"]["budget"] += 1
        _rehash_material_artifact(forged, "profiling_workload")
        forged["profiling_results"]["profiling_workload_sha256"] = forged[
            "profiling_workload_sha256"
        ]
        _rehash_material_artifact(forged, "profiling_results")
        forged["technique_profile"].update(
            {
                "profiling_workload_sha256": forged["profiling_workload_sha256"],
                "profiling_results_sha256": forged["profiling_results_sha256"],
            }
        )
        _rehash_material_artifact(forged, "technique_profile")
        subject["public_workload_set_sha256"] = forged["profiling_workload_sha256"]
        subject_id = canonical_sha256(
            {
                "normalized_source_tree_sha256": subject[
                    "normalized_source_tree_sha256"
                ],
                "build_descriptor_sha256": subject["build_descriptor_sha256"],
                "public_workload_set_sha256": subject[
                    "public_workload_set_sha256"
                ],
                "domain": "P3-SUBJECT-v1",
            }
        )
        subject["controlled_subject_id"] = subject_id
        subject["sites"] = [
            _site_with_subject_id(site, subject_id) for site in subject["sites"]
        ]
    elif mutation == "canonical_site":
        changed = copy.deepcopy(subject["sites"][0])
        changed["symbol"] = f"{changed['symbol']}_forged"
        subject["sites"][0] = _site_with_subject_id(
            changed, subject["controlled_subject_id"]
        )
    else:
        forged["profiling_results"]["runner_implementation_source_sha256"] = (
            "e" * 64
        )
        _rehash_material_artifact(forged, "profiling_results")
        forged["technique_profile"]["profiling_results_sha256"] = forged[
            "profiling_results_sha256"
        ]
        _rehash_material_artifact(forged, "technique_profile")

    forged = _rehash_derived_material(forged)

    with pytest.raises(EvidenceError, match="E_DERIVED_SUBJECT_BINDING"):
        build_subject_frames(bridge, [forged, other])


def test_subject_alias_merge_does_not_mutate_derived_material(
    synthetic_release, tmp_path
):
    adapter_root = tmp_path / "adapters"
    adapter_root.mkdir()
    adapter_registry = validate_adapter_registry(
        _adapter_registry(adapter_root), _source_snapshot(adapter_root)
    )
    generator_registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    first_record = verified["records"][0]
    second_record = {
        **first_record,
        "neutral_snapshot_id": "7" * 64,
        "fixed_tree_commitment": "8" * 64,
    }
    bridge = {**verified, "records": [first_record, second_record]}
    source_root = tmp_path / "python-subject"
    source_root.mkdir()
    first_spec = _derived_subject_spec(
        source_root,
        "python.json",
        first_record,
        adapter_registry,
        generator_registry,
        "SCALAR_CONTROL",
    )
    second_record["normalized_source_tree_sha256"] = first_record[
        "normalized_source_tree_sha256"
    ]
    second_record["build_descriptor_sha256"] = first_record[
        "build_descriptor_sha256"
    ]
    second_spec = _derived_subject_spec(
        source_root,
        "python.json",
        second_record,
        adapter_registry,
        generator_registry,
        "SCALAR_CONTROL",
    )
    first_material = frames_module.derive_subject_material(first_spec, first_record)
    second_material = frames_module.derive_subject_material(second_spec, second_record)
    before = _bytes([first_material, second_material])

    frames = build_subject_frames(bridge, [first_material, second_material])

    assert _bytes([first_material, second_material]) == before
    assert frames["subjects"][0]["neutral_snapshot_ids"] == sorted(
        [first_record["neutral_snapshot_id"], second_record["neutral_snapshot_id"]]
    )


@pytest.mark.parametrize("mutation", ["extra", "missing"])
def test_subject_spec_rejects_non_exact_keys_before_adapter_execution(
    synthetic_release, tmp_path, mutation
):
    derive_subject_material = getattr(frames_module, "derive_subject_material", None)
    assert callable(derive_subject_material)
    record = verify_pinned_bridge(
        synthetic_release.root, synthetic_release.lock
    )["records"][0]
    spec: dict[str, object] = {
        "neutral_snapshot_id": record["neutral_snapshot_id"],
        "source_snapshot": object(),
        "source_record": {
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
        },
        "build_descriptor": {"ecosystem": "python"},
        "adapter_registry": {},
        "input_generator_registry": {},
        "profiling_results": [],
    }
    if mutation == "extra":
        spec["scale_class"] = "S"
    else:
        del spec["profiling_results"]
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        derive_subject_material(spec, record)


def test_unsupported_subject_common_inputs_remain_explicitly_unavailable(
    synthetic_release, tmp_path
):
    adapter_root = tmp_path / "adapters"
    adapter_root.mkdir()
    adapter_registry = validate_adapter_registry(
        _adapter_registry(adapter_root), _source_snapshot(adapter_root)
    )
    generator_registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    record = verify_pinned_bridge(
        synthetic_release.root, synthetic_release.lock
    )["records"][0]
    source_root = tmp_path / "unsupported-source"
    source_root.mkdir()
    descriptor = {"ecosystem": "rust"}
    record["normalized_source_tree_sha256"] = _source_tree_sha256(source_root)
    record["build_descriptor_sha256"] = canonical_sha256(descriptor)
    source_record = {
        "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
        "build_descriptor_sha256": record["build_descriptor_sha256"],
    }
    discovery = run_adapter_discovery(
        _source_snapshot(source_root), descriptor, adapter_registry, None
    )
    frame = build_public_behavior_frame(source_record, discovery)
    workload = select_profiling_workload(
        frame, derive_source_scale(_source_snapshot(source_root), discovery)["scale_class"]
    )
    spec = {
        "neutral_snapshot_id": record["neutral_snapshot_id"],
        "source_snapshot": _source_snapshot(source_root),
        "source_record": source_record,
        "build_descriptor": descriptor,
        "adapter_registry": adapter_registry,
        "input_generator_registry": generator_registry,
        "profiling_results": _profiling_receipt(
            workload,
            [],
            neutral_snapshot_id=record["neutral_snapshot_id"],
            normalized_source_tree_sha256=record["normalized_source_tree_sha256"],
            build_descriptor_sha256=record["build_descriptor_sha256"],
            adapter_implementation_source_sha256=None,
        ),
    }
    material = frames_module.derive_subject_material(spec, record)
    assert material["adapter_discovery"]["discovery_status"] == "ADAPTER_UNSUPPORTED"
    assert material["subject"]["sites"] == []
    assert material["technique_profile"]["primary_technique"] == "TECH_UNCERTAIN"
    assert [row["ordinal"] for row in material["common_inputs"]["rows"]] == list(
        range(30)
    )
    assert {row["status"] for row in material["common_inputs"]["rows"]} == {
        "COMMON_INPUT_UNAVAILABLE"
    }


def test_adapter_registry_binds_exact_implementation_paths_and_source_hashes(tmp_path):
    registry = _adapter_registry(tmp_path)
    validated = validate_adapter_registry(registry, _source_snapshot(tmp_path))
    assert {item["adapter_id"] for item in validated["adapters"]} == CONFIRMATORY_ADAPTERS
    for item in validated["adapters"]:
        absolute = tmp_path / item["implementation_path"]
        assert file_sha256(absolute) == item["source_sha256"]


@pytest.mark.parametrize(
    "mutator",
    [
        lambda reg: {
            **reg,
            "adapters": [
                {**item, "source_sha256": "0" * 64} if item["adapter_id"] == "PYTHON_PEP517_V1" else item
                for item in reg["adapters"]
            ],
        },
        lambda reg: {
            **reg,
            "adapters": [
                {
                    **item,
                    "implementation_path": "adapters/missing_python.py",
                }
                if item["adapter_id"] == "PYTHON_PEP517_V1"
                else item
                for item in reg["adapters"]
            ],
        },
        lambda reg: {
            **reg,
            "adapters": reg["adapters"]
            + [
                {
                    "adapter_id": "CARGO_TEST_V1",
                    "ecosystem": "cargo",
                    "implementation_path": "adapters/cargo_test_v1.py",
                    "source_sha256": "1" * 64,
                }
            ],
        },
    ],
)
def test_adapter_registry_rejects_one_field_mutations(tmp_path, mutator):
    registry = mutator(_adapter_registry(tmp_path))
    body = {key: value for key, value in registry.items() if key != "artifact_sha256"}
    registry = {**body, "artifact_sha256": canonical_sha256(body)}
    with pytest.raises(EvidenceError):
        validate_adapter_registry(registry, _source_snapshot(tmp_path))


def _rehash_adapter_registry(registry: dict, root: Path, adapter_id: str) -> dict:
    adapters = []
    for entry in registry["adapters"]:
        if entry["adapter_id"] == adapter_id:
            entry = {
                **entry,
                "source_sha256": file_sha256(root / entry["implementation_path"]),
            }
        adapters.append(entry)
    body = {
        "schema_version": registry["schema_version"],
        "adapters": adapters,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


@pytest.mark.parametrize(
    ("adapter_id", "fixture_name", "expected_ecosystem"),
    [
        ("PYTHON_PEP517_V1", "python.json", "python"),
        ("CMAKE_CTEST_V1", "cmake.json", "cmake"),
    ],
)
def test_pinned_adapter_executes_and_normalizes_discovery(
    tmp_path, adapter_id, fixture_name, expected_ecosystem
):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = validate_adapter_registry(
        _adapter_registry(implementation_root), _source_snapshot(implementation_root)
    )
    descriptor = _write_adapter_project(source_root, fixture_name)
    first = run_adapter_discovery(
        _source_snapshot(source_root), descriptor, registry, adapter_id
    )
    shuffled = run_adapter_discovery(
        _source_snapshot(source_root),
        {**descriptor, "reverse": True},
        registry,
        adapter_id,
    )
    fixture = _load_fixture(fixture_name)
    assert first == shuffled
    assert first["adapter_id"] == adapter_id
    assert first["ecosystem"] == expected_ecosystem
    assert first["discovery_status"] == "EXECUTABLE"
    assert first["source_files"] == sorted(fixture["source_files"])
    assert first["public_schemas"]
    assert first["sites"]
    assert first["artifact_sha256"] == canonical_sha256(
        {key: value for key, value in first.items() if key != "artifact_sha256"}
    )


def test_adapter_execution_consumes_validated_snapshot_without_path_reopen(tmp_path):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = validate_adapter_registry(
        _adapter_registry(implementation_root), _source_snapshot(implementation_root)
    )
    descriptor = _write_adapter_project(source_root, "python.json")
    implementation = implementation_root / "adapters/python_pep517_v1.py"
    implementation.write_text("raise RuntimeError('changed bytes executed')\n", encoding="utf-8")

    discovery = run_adapter_discovery(
        _source_snapshot(source_root), descriptor, registry, "PYTHON_PEP517_V1"
    )

    assert discovery["discovery_status"] == "EXECUTABLE"


@pytest.mark.parametrize("replacement", ["bytes", "symlink"])
def test_verified_registry_consumer_compiles_captured_bytes_without_path_reopen(
    tmp_path, monkeypatch, replacement
):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    verified = validate_adapter_registry(
        _adapter_registry(implementation_root), _source_snapshot(implementation_root)
    )
    consumed = frames_module._consume_verified_registry(
        verified, registry_kind="adapter"
    )
    descriptor = _write_adapter_project(source_root, "python.json")
    implementation = implementation_root / "adapters/python_pep517_v1.py"
    replacement_path = tmp_path / "replacement.py"
    replacement_path.write_text(
        "raise RuntimeError('replacement bytes executed')\n", encoding="utf-8"
    )
    implementation.unlink()
    if replacement == "symlink":
        implementation.symlink_to(replacement_path)
    else:
        implementation.write_bytes(replacement_path.read_bytes())
    path_reads = 0

    def forbidden_path_read(*_args, **_kwargs):
        nonlocal path_reads
        path_reads += 1
        raise AssertionError("verified registry consumer reopened an implementation path")

    monkeypatch.setattr(
        frames_module, "read_canonical_regular_bytes", forbidden_path_read
    )

    discovery = run_adapter_discovery(
        _source_snapshot(source_root), descriptor, consumed, "PYTHON_PEP517_V1"
    )

    assert discovery["discovery_status"] == "EXECUTABLE"
    assert path_reads == 0


def test_verified_registry_consumer_revalidates_in_memory_snapshot_digest(tmp_path):
    verified = validate_adapter_registry(
        _adapter_registry(tmp_path), _source_snapshot(tmp_path)
    )
    snapshot = verified["_implementation_snapshots"]["PYTHON_PEP517_V1"]
    object.__setattr__(snapshot, "source_bytes", b"raise RuntimeError('forged')\n")

    with pytest.raises(EvidenceError, match="E_ADAPTER_REGISTRY"):
        frames_module._consume_verified_registry(verified, registry_kind="adapter")


def test_verified_registry_consumer_captures_snapshot_from_single_mapping_get(tmp_path):
    class FlippingSnapshotMap(Mapping):
        def __init__(self, snapshots, snapshot_id, forged):
            self.snapshots = snapshots
            self.snapshot_id = snapshot_id
            self.forged = forged
            self.get_calls = 0
            self.item_reads = 0

        def __iter__(self):
            return iter(self.snapshots)

        def __len__(self):
            return len(self.snapshots)

        def get(self, key, default=None):
            self.get_calls += 1
            return self.snapshots.get(key, default)

        def __getitem__(self, key):
            self.item_reads += 1
            return self.forged if key == self.snapshot_id else self.snapshots[key]

    verified = validate_adapter_registry(
        _adapter_registry(tmp_path), _source_snapshot(tmp_path)
    )
    snapshot_id = "PYTHON_PEP517_V1"
    genuine_snapshots = verified["_implementation_snapshots"]
    genuine = genuine_snapshots[snapshot_id]
    forged = copy.copy(genuine)
    object.__setattr__(forged, "source_bytes", b"raise RuntimeError('forged')\n")
    flipping = FlippingSnapshotMap(genuine_snapshots, snapshot_id, forged)
    verified["_implementation_snapshots"] = flipping

    consumed = frames_module._consume_verified_registry(
        verified, registry_kind="adapter"
    )

    captured = consumed["_implementation_snapshots"][snapshot_id]
    assert captured.source_bytes == genuine.source_bytes
    assert flipping.get_calls == len(genuine_snapshots)
    assert flipping.item_reads == 0


@pytest.mark.parametrize("registry_kind", ["adapter", "input_generator"])
def test_verified_registry_consumer_drops_trapping_caller_absolute_path(
    tmp_path, registry_kind
):
    class Trap:
        def __str__(self):
            raise AssertionError("caller path object must not be stringified")

        def __fspath__(self):
            raise AssertionError("caller path object must not be path-converted")

    if registry_kind == "adapter":
        implementation_root = tmp_path / "implementations"
        source_root = tmp_path / "source"
        source_root.mkdir()
        verified = validate_adapter_registry(
            _adapter_registry(implementation_root),
            _source_snapshot(implementation_root),
        )
        snapshot_id = "PYTHON_PEP517_V1"
    else:
        verified = validate_input_generator_registry(
            _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
        )
        snapshot_id = "TEXT_IO_SCHEMA_V1"
    snapshot = verified["_implementation_snapshots"][snapshot_id]
    object.__setattr__(snapshot, "absolute_path", Trap())

    consumed = frames_module._consume_verified_registry(
        verified, registry_kind=registry_kind
    )

    if registry_kind == "adapter":
        descriptor = _write_adapter_project(source_root, "python.json")
        discovery = run_adapter_discovery(
            _source_snapshot(source_root), descriptor, consumed, snapshot_id
        )
        assert discovery["discovery_status"] == "EXECUTABLE"
    else:
        generate = frames_module._load_input_generator_callable(
            consumed["_implementation_snapshots"][snapshot_id], snapshot_id
        )
        assert callable(generate)


@pytest.mark.parametrize("registry_kind", ["adapter", "input_generator"])
@pytest.mark.parametrize("field", ["source_bytes", "source_sha256", "logical_filename"])
@pytest.mark.parametrize("invalid_factory", [list, dict])
def test_verified_registry_consumer_rejects_nonexact_snapshot_field_types(
    tmp_path, registry_kind, field, invalid_factory
):
    if registry_kind == "adapter":
        verified = validate_adapter_registry(
            _adapter_registry(tmp_path), _source_snapshot(tmp_path)
        )
        snapshot_id = "PYTHON_PEP517_V1"
        expected_code = "E_ADAPTER_REGISTRY"
    else:
        verified = validate_input_generator_registry(
            _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
        )
        snapshot_id = "TEXT_IO_SCHEMA_V1"
        expected_code = "E_GENERATOR_REGISTRY"
    snapshot = verified["_implementation_snapshots"][snapshot_id]
    object.__setattr__(snapshot, field, invalid_factory())

    with pytest.raises(EvidenceError) as exc_info:
        frames_module._consume_verified_registry(
            verified, registry_kind=registry_kind
        )

    assert exc_info.value.code == expected_code


@pytest.mark.parametrize("registry_kind", ["contract"])
@pytest.mark.parametrize("replacement", ["symlink", "bytes"])
def test_registry_snapshot_safe_read_fails_closed_on_post_lstat_replacement(
    tmp_path, monkeypatch, registry_kind, replacement
):
    if registry_kind == "adapter":
        registry = _adapter_registry(tmp_path)
        entry = next(
            row
            for row in registry["adapters"]
            if row["adapter_id"] == "CMAKE_CTEST_V1"
        )
        validate = validate_adapter_registry
    elif registry_kind == "generator":
        shutil.copytree(GENERATOR_FIXTURE_ROOT, tmp_path, dirs_exist_ok=True)
        registry = _load_generator_registry()
        entry = next(
            row
            for row in registry["generators"]
            if row["generator_id"] == "TEXT_IO_SCHEMA_V1"
        )
        validate = validate_input_generator_registry
    else:
        registry = _contract_generator_registry(tmp_path)
        entry = registry["generators"][1]
        validate = validate_contract_generator_registry
    implementation = tmp_path / entry["implementation_path"]
    replacement_path = tmp_path / "replacement.py"
    replacement_path.write_bytes(implementation.read_bytes())
    real_lstat = artifacts_module._lstat_regular_path

    def replace_after_lstat(path, context):
        verified = real_lstat(path, context)
        if Path(path) == implementation:
            implementation.unlink()
            if replacement == "symlink":
                implementation.symlink_to(replacement_path)
            else:
                implementation.write_bytes(b"# replacement bytes\n")
        return verified

    monkeypatch.setattr(artifacts_module, "_lstat_regular_path", replace_after_lstat)

    with pytest.raises(
        EvidenceError,
        match="E_(AUTHORITY_LOCK_PATH|ADAPTER_SOURCE_HASH|GENERATOR_SOURCE_HASH)",
    ):
        validate(registry, tmp_path)


@pytest.mark.parametrize(
    "effect",
    ["stdout", "stderr", "socket", "dns", "create_connection"],
)
def test_verified_adapter_execution_rejects_output_and_network_side_effects(
    tmp_path, monkeypatch, capsys, effect
):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = _adapter_registry(implementation_root)
    descriptor = _write_adapter_project(source_root, "python.json")
    implementation = implementation_root / "adapters/python_pep517_v1.py"
    fixture_result = {
        "adapter_id": "PYTHON_PEP517_V1",
        "ecosystem": "python",
        "source_files": ["src/demo_pkg/api.py"],
        "declarations": [],
        "public_schemas": [],
        "sites": [],
    }
    actions = {
        "stdout": "print('adapter stdout leak')",
        "stderr": "print('adapter stderr leak', file=sys.stderr)",
        "socket": "socket.socket()",
        "dns": "socket.getaddrinfo('example.invalid', 80)",
        "create_connection": "socket.create_connection(('example.invalid', 80))",
    }
    implementation.write_text(
        "import socket\n"
        "import sys\n"
        "def discover(source_snapshot, build_descriptor):\n"
        f"    {actions[effect]}\n"
        f"    return {fixture_result!r}\n",
        encoding="utf-8",
    )
    registry = _rehash_adapter_registry(
        registry, implementation_root, "PYTHON_PEP517_V1"
    )
    validated = validate_adapter_registry(
        registry, _source_snapshot(implementation_root)
    )

    def forbid_real_network(*_args, **_kwargs):
        raise AssertionError("test must not perform real network access")

    if effect in {"socket", "dns", "create_connection"}:
        attribute = effect if effect != "dns" else "getaddrinfo"
        monkeypatch.setattr(socket, attribute, forbid_real_network)

    with pytest.raises(
        EvidenceError, match="E_VERIFIED_EXECUTION_(OUTPUT|NETWORK)"
    ):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, validated, "PYTHON_PEP517_V1"
        )

    assert capsys.readouterr() == ("", "")


def test_verified_execution_context_serializes_and_restores_process_state(
    tmp_path, monkeypatch, capsys
):
    executions = []
    for name, noisy in (("clean", False), ("noisy", True)):
        root = tmp_path / name
        implementation_root = root / "implementations"
        source_root = root / "source"
        source_root.mkdir(parents=True)
        registry = _adapter_registry(implementation_root)
        descriptor = _write_adapter_project(source_root, "python.json")
        if noisy:
            implementation = implementation_root / "adapters/python_pep517_v1.py"
            implementation.write_text(
                implementation.read_text(encoding="utf-8").replace(
                    "from __future__ import annotations\n",
                    "from __future__ import annotations\n\n"
                    "print('concurrent adapter leak')\n",
                ),
                encoding="utf-8",
            )
            registry = _rehash_adapter_registry(
                registry, implementation_root, "PYTHON_PEP517_V1"
            )
        executions.append(
            (
                _source_snapshot(source_root),
                descriptor,
                validate_adapter_registry(
                    registry, _source_snapshot(implementation_root)
                ),
            )
        )

    rendezvous = threading.Barrier(2)
    monkeypatch.setattr(sys, "dont_write_bytecode", False)

    def execute(arguments):
        rendezvous.wait(timeout=10)
        try:
            discovery = run_adapter_discovery(
                *arguments, "PYTHON_PEP517_V1"
            )
            return discovery["discovery_status"]
        except EvidenceError as exc:
            return exc.code

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(execute, executions))

    assert outcomes == ["EXECUTABLE", "E_VERIFIED_EXECUTION_OUTPUT"]
    assert sys.dont_write_bytecode is False
    assert capsys.readouterr() == ("", "")
    assert not list(tmp_path.rglob("__pycache__"))


def test_adapter_registry_is_revalidated_at_execution_boundary(tmp_path):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = validate_adapter_registry(
        _adapter_registry(implementation_root), _source_snapshot(implementation_root)
    )
    descriptor = _write_adapter_project(source_root, "python.json")
    mutated = copy.deepcopy(registry)
    mutated["adapters"][0]["source_sha256"] = "0" * 64
    with pytest.raises(EvidenceError, match="E_ADAPTER_REGISTRY_HASH"):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, mutated, "PYTHON_PEP517_V1"
        )


def test_adapter_rejects_unregistered_and_wrong_returned_adapter_ids(tmp_path):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = _adapter_registry(implementation_root)
    descriptor = _write_adapter_project(source_root, "python.json")
    validated = validate_adapter_registry(
        registry, _source_snapshot(implementation_root)
    )
    with pytest.raises(EvidenceError, match="E_ADAPTER_UNREGISTERED"):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, validated, "CARGO_TEST_V1"
        )

    implementation = implementation_root / "adapters/python_pep517_v1.py"
    implementation.write_text(
        implementation.read_text(encoding="utf-8").replace(
            '"PYTHON_PEP517_V1"', '"CMAKE_CTEST_V1"'
        ),
        encoding="utf-8",
    )
    validated = validate_adapter_registry(
        _rehash_adapter_registry(registry, implementation_root, "PYTHON_PEP517_V1"),
        _source_snapshot(implementation_root),
    )
    with pytest.raises(EvidenceError, match="E_ADAPTER_ID"):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, validated, "PYTHON_PEP517_V1"
        )


@pytest.mark.parametrize("result_mutation", ["missing", "extra", "bad_signature"])
def test_adapter_requires_exact_callable_and_result_schema(tmp_path, result_mutation):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = _adapter_registry(implementation_root)
    descriptor = _write_adapter_project(source_root, "python.json")
    implementation = implementation_root / "adapters/python_pep517_v1.py"
    fixture_result = {
        "adapter_id": "PYTHON_PEP517_V1",
        "ecosystem": "python",
        "source_files": ["src/demo_pkg/api.py"],
        "declarations": [],
        "public_schemas": [],
        "sites": [],
    }
    if result_mutation == "missing":
        fixture_result.pop("sites")
    elif result_mutation == "extra":
        fixture_result["manual_fallback"] = "python -m demo"
    signature = (
        "source_snapshot, build_descriptor, caller_discovery=None"
        if result_mutation == "bad_signature"
        else "source_snapshot, build_descriptor"
    )
    implementation.write_text(
        f"def discover({signature}):\n    return {fixture_result!r}\n",
        encoding="utf-8",
    )
    validated = validate_adapter_registry(
        _rehash_adapter_registry(registry, implementation_root, "PYTHON_PEP517_V1"),
        _source_snapshot(implementation_root),
    )
    with pytest.raises(EvidenceError, match="E_ADAPTER_(SIGNATURE|RESULT)"):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, validated, "PYTHON_PEP517_V1"
        )


@pytest.mark.parametrize("field", ["static_dependency_tags", "prerequisites"])
def test_adapter_rejects_mixed_type_declaration_collections_with_evidence_error(
    tmp_path, field
):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = validate_adapter_registry(
        _adapter_registry(implementation_root), _source_snapshot(implementation_root)
    )
    descriptor = _write_adapter_project(source_root, "python.json")
    manifest = source_root / descriptor["manifest_path"]
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["declarations"][0][field] = ["valid", 7]
    manifest.write_bytes(_bytes(value))
    with pytest.raises(EvidenceError, match="E_ADAPTER_RESULT"):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, registry, "PYTHON_PEP517_V1"
        )


@pytest.mark.parametrize("field", ["static_dependency_tags", "prerequisites"])
def test_adapter_rejects_non_list_declaration_collections_with_evidence_error(
    tmp_path, field
):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = validate_adapter_registry(
        _adapter_registry(implementation_root), _source_snapshot(implementation_root)
    )
    descriptor = _write_adapter_project(source_root, "python.json")
    manifest = source_root / descriptor["manifest_path"]
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["declarations"][0][field] = "not-a-list"
    manifest.write_bytes(_bytes(value))
    with pytest.raises(EvidenceError, match="E_ADAPTER_RESULT"):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, registry, "PYTHON_PEP517_V1"
        )


def test_adapter_rejects_non_object_site_with_evidence_error(tmp_path):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = validate_adapter_registry(
        _adapter_registry(implementation_root), _source_snapshot(implementation_root)
    )
    descriptor = _write_adapter_project(source_root, "python.json")
    manifest = source_root / descriptor["manifest_path"]
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["sites"] = [["not", "an", "object"]]
    manifest.write_bytes(_bytes(value))
    with pytest.raises(EvidenceError, match="E_ADAPTER_RESULT"):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, registry, "PYTHON_PEP517_V1"
        )


def test_adapter_rejects_convertible_list_of_pairs_site(tmp_path):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = validate_adapter_registry(
        _adapter_registry(implementation_root), _source_snapshot(implementation_root)
    )
    descriptor = _write_adapter_project(source_root, "python.json")
    manifest = source_root / descriptor["manifest_path"]
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["sites"] = [
        [
            ["path", "src/demo_pkg/api.py"],
            ["symbol", "solve"],
            ["start_line", 1],
            ["start_col", 0],
            ["end_line", 1],
            ["end_col", 5],
        ]
    ]
    manifest.write_bytes(_bytes(value))
    with pytest.raises(EvidenceError, match="E_ADAPTER_RESULT"):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, registry, "PYTHON_PEP517_V1"
        )


@pytest.mark.parametrize("source_files", [["../escape.py"], ["src/a.py", "src/a.py"]])
def test_adapter_rejects_unsafe_or_duplicate_source_paths(tmp_path, source_files):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = validate_adapter_registry(
        _adapter_registry(implementation_root), _source_snapshot(implementation_root)
    )
    descriptor = _write_adapter_project(source_root, "python.json")
    manifest = source_root / descriptor["manifest_path"]
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["source_files"] = source_files
    manifest.write_bytes(_bytes(value))
    with pytest.raises(EvidenceError, match="E_ADAPTER_SOURCE_PATH"):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, registry, "PYTHON_PEP517_V1"
        )


def test_adapter_rejects_caller_supplied_discovery_collections(tmp_path):
    implementation_root = tmp_path / "implementations"
    source_root = tmp_path / "source"
    source_root.mkdir()
    registry = validate_adapter_registry(
        _adapter_registry(implementation_root), _source_snapshot(implementation_root)
    )
    descriptor = _write_adapter_project(source_root, "python.json")
    descriptor["declarations"] = _load_fixture("python.json")["declarations"]
    with pytest.raises(EvidenceError, match="E_ADAPTER_AUTHORITY"):
        run_adapter_discovery(
            _source_snapshot(source_root), descriptor, registry, "PYTHON_PEP517_V1"
        )


def test_unsupported_adapter_emits_receipt_without_manual_fallback(tmp_path):
    fixture = _load_fixture("unsupported.json")
    assert fixture["declarations"] == []
    assert "hand_command" not in json.dumps(fixture)
    registry = validate_adapter_registry(
        _adapter_registry(tmp_path), _source_snapshot(tmp_path)
    )
    discovery = run_adapter_discovery(
        _source_snapshot(tmp_path),
        {"ecosystem": "cargo"},
        registry,
        None,
    )
    assert discovery["discovery_status"] == "ADAPTER_UNSUPPORTED"
    assert discovery["adapter_id"] is None
    assert discovery["declarations"] == []
    assert discovery["public_schemas"] == []
    assert discovery["sites"] == []
    assert "hand_command" not in discovery


@pytest.mark.parametrize(
    ("effective_lines", "expected_scale"),
    [(9_999, "S"), (10_000, "M"), (99_999, "M"), (100_000, "L")],
)
def test_source_scale_is_derived_at_frozen_boundaries(
    tmp_path, effective_lines, expected_scale
):
    source = tmp_path / "src/program.py"
    source.parent.mkdir(parents=True)
    source.write_text("# comment\n\n" + "value = 1\n" * effective_lines, encoding="utf-8")
    discovery = _discovery_receipt([])
    discovery["source_files"] = ["src/program.py"]
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    scale = derive_source_scale(_source_snapshot(tmp_path), discovery)
    assert scale["per_file_effective_lines"] == [
        {"path": "src/program.py", "effective_lines": effective_lines}
    ]
    assert scale["total_effective_lines"] == effective_lines
    assert scale["scale_class"] == expected_scale
    assert scale["discovery_sha256"] == discovery["artifact_sha256"]
    assert scale["artifact_sha256"] == canonical_sha256(
        {key: value for key, value in scale.items() if key != "artifact_sha256"}
    )


@pytest.mark.parametrize(
    "relative",
    [
        "vendor/a.py",
        "generated/a.py",
        ".git/a.py",
        ".venv/a.py",
        "build/a.py",
        "_build/a.py",
        "out/a.py",
        "target/a.py",
        "build-release/a.py",
        "CMakeFiles/generated.cpp",
        "Debug/generated.obj",
        "site-packages/pkg/a.py",
        ".bzr/state.py",
        "CMakeCache.txt",
        "tests/fixtures/a.py",
    ],
)
def test_source_scale_rejects_excluded_source_paths(tmp_path, relative):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("value = 1\n", encoding="utf-8")
    discovery = _discovery_receipt([])
    discovery["source_files"] = [relative]
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="E_SCALE_SOURCE_PATH"):
        derive_source_scale(_source_snapshot(tmp_path), discovery)


def test_source_scale_counts_frozen_python_and_cmake_comment_rules(tmp_path):
    python_source = tmp_path / "src/a.py"
    cmake_source = tmp_path / "src/a.cpp"
    python_source.parent.mkdir(parents=True)
    python_source.write_text("# comment\nvalue = 1  # code\n\n", encoding="utf-8")
    cmake_source.write_text(
        "// comment\n/* block\nstill block */\nint value = 1; // code\n",
        encoding="utf-8",
    )
    python_discovery = _discovery_receipt([])
    python_discovery["source_files"] = ["src/a.py"]
    body = {key: value for key, value in python_discovery.items() if key != "artifact_sha256"}
    python_discovery["artifact_sha256"] = canonical_sha256(body)
    cmake_discovery = _discovery_receipt(
        [], adapter_id="CMAKE_CTEST_V1", ecosystem="cmake"
    )
    cmake_discovery["source_files"] = ["src/a.cpp"]
    body = {key: value for key, value in cmake_discovery.items() if key != "artifact_sha256"}
    cmake_discovery["artifact_sha256"] = canonical_sha256(body)
    snapshot = _source_snapshot(tmp_path)
    assert derive_source_scale(snapshot, python_discovery)["total_effective_lines"] == 1
    assert derive_source_scale(snapshot, cmake_discovery)["total_effective_lines"] == 1


def test_cmake_adapter_counts_cpp_directives_and_comment_markers_in_strings(tmp_path):
    source = tmp_path / "src/a.cpp"
    source.parent.mkdir(parents=True)
    source.write_text(
        '#include <vector>\nconst char *marker = "/*";\n/* comment */\nint value = 1;\n',
        encoding="utf-8",
    )
    discovery = _discovery_receipt(
        [], adapter_id="CMAKE_CTEST_V1", ecosystem="cmake"
    )
    discovery["source_files"] = ["src/a.cpp"]
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    assert derive_source_scale(_source_snapshot(tmp_path), discovery)["total_effective_lines"] == 3


@pytest.mark.parametrize(
    ("adapter_id", "ecosystem", "sources", "expected_counts"),
    [
        (
            "PYTHON_PEP517_V1",
            "python",
            {
                "src/main.py": "# comment\nvalue = 1\n",
                "native/helper.cpp": "// comment\n#include <vector>\nint value = 1;\n",
            },
            {"native/helper.cpp": 2, "src/main.py": 1},
        ),
        (
            "CMAKE_CTEST_V1",
            "cmake",
            {
                "src/main.cpp": "// comment\nint value = 1;\n",
                "tools/helper.py": "# comment\nvalue = 1\n",
                "CMakeLists.txt": "# comment\nset(VALUE 1)\n",
            },
            {"CMakeLists.txt": 1, "src/main.cpp": 1, "tools/helper.py": 1},
        ),
    ],
)
def test_source_scale_dispatches_frozen_comment_rules_per_file_language(
    tmp_path, adapter_id, ecosystem, sources, expected_counts
):
    for relative, contents in sources.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    discovery = _discovery_receipt(
        [], adapter_id=adapter_id, ecosystem=ecosystem
    )
    discovery["source_files"] = sorted(sources)
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    scale = derive_source_scale(_source_snapshot(tmp_path), discovery)
    assert {
        row["path"]: row["effective_lines"]
        for row in scale["per_file_effective_lines"]
    } == expected_counts


def test_source_scale_rejects_unsupported_source_language(tmp_path):
    source = tmp_path / "src/lib.rs"
    source.parent.mkdir(parents=True)
    source.write_text("fn main() {}\n", encoding="utf-8")
    discovery = _discovery_receipt([])
    discovery["source_files"] = ["src/lib.rs"]
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="E_SCALE_SOURCE_LANGUAGE"):
        derive_source_scale(_source_snapshot(tmp_path), discovery)


def test_non_utf8_unsupported_source_reports_language_error_before_decode(tmp_path):
    source = tmp_path / "src/lib.rs"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"\xff\xfe")
    discovery = _discovery_receipt([])
    discovery["source_files"] = ["src/lib.rs"]
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="E_SCALE_SOURCE_LANGUAGE"):
        derive_source_scale(_source_snapshot(tmp_path), discovery)


@pytest.mark.parametrize(
    "mutation",
    ["unsafe_source", "duplicate_source", "unsorted_declarations", "forbidden_schema", "bad_site"],
)
def test_discovery_receipts_are_deeply_validated_before_consumption(tmp_path, mutation):
    source = tmp_path / "src/a.py"
    source.parent.mkdir(parents=True)
    source.write_text("value = 1\n", encoding="utf-8")
    declarations = _tagged_declarations(_load_fixture("python.json"))[:2]
    discovery = _discovery_receipt(
        declarations,
        public_schemas=_load_fixture("python.json")["public_schemas"],
        sites=_load_fixture("python.json")["sites"],
    )
    discovery["source_files"] = ["src/a.py"]
    if mutation == "unsafe_source":
        discovery["source_files"] = ["../a.py"]
    elif mutation == "duplicate_source":
        discovery["source_files"] = ["src/a.py", "src/a.py"]
    elif mutation == "unsorted_declarations":
        discovery["declarations"] = list(reversed(discovery["declarations"]))
    elif mutation == "forbidden_schema":
        discovery["public_schemas"][0]["project_test_body"] = "assert True"
    elif mutation == "bad_site":
        discovery["sites"][0]["start_line"] = -1
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError):
        derive_source_scale(_source_snapshot(tmp_path), discovery)


@pytest.mark.parametrize("field", ["static_dependency_tags", "prerequisites"])
def test_discovery_rejects_mixed_type_collections_with_evidence_error(tmp_path, field):
    discovery = _discovery_receipt(
        _tagged_declarations(_load_fixture("python.json"))[:1]
    )
    discovery["declarations"][0][field] = ["valid", 7]
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="E_ADAPTER_RESULT"):
        derive_source_scale(_source_snapshot(tmp_path), discovery)


@pytest.mark.parametrize("field", ["static_dependency_tags", "prerequisites"])
def test_discovery_rejects_non_list_collections_with_evidence_error(tmp_path, field):
    discovery = _discovery_receipt(
        _tagged_declarations(_load_fixture("python.json"))[:1]
    )
    discovery["declarations"][0][field] = "not-a-list"
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="E_ADAPTER_RESULT"):
        derive_source_scale(_source_snapshot(tmp_path), discovery)


def test_discovery_rejects_non_object_site_with_evidence_error(tmp_path):
    discovery = _discovery_receipt([])
    discovery["sites"] = [["not", "an", "object"]]
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="E_ADAPTER_RESULT"):
        derive_source_scale(_source_snapshot(tmp_path), discovery)


def test_discovery_rejects_convertible_list_of_pairs_site(tmp_path):
    discovery = _discovery_receipt([])
    discovery["sites"] = [
        [
            ["path", "src/a.py"],
            ["symbol", "solve"],
            ["start_line", 1],
            ["start_col", 0],
            ["end_line", 1],
            ["end_col", 5],
        ]
    ]
    body = {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    discovery["artifact_sha256"] = canonical_sha256(body)
    with pytest.raises(EvidenceError, match="E_ADAPTER_RESULT"):
        derive_source_scale(_source_snapshot(tmp_path), discovery)


def test_scale_interface_has_no_caller_scale_class():
    assert list(inspect.signature(derive_source_scale).parameters) == [
        "source_snapshot",
        "discovery",
    ]


def test_discovery_and_public_frame_interfaces_reject_legacy_caller_authority():
    assert list(inspect.signature(run_adapter_discovery).parameters) == [
        "source_snapshot",
        "build_descriptor",
        "registry",
        "adapter_id",
    ]
    assert list(inspect.signature(build_public_behavior_frame).parameters) == [
        "source_record",
        "discovery",
    ]


def test_public_behavior_frame_accounts_all_categories_and_preserves_public_schemas(tmp_path):
    declarations = (
        _tagged_declarations(_load_fixture("python.json"))
        + [
            {
                "category": "CLI",
                "ecosystem": "python",
                "adapter_id": "PYTHON_PEP517_V1",
                "provenance_path": "docs/broken.md",
                "provenance_span_or_key": "broken",
                "entrypoint": "",
                "normalized_entrypoint": "",
                "declared_inputs": {"kind": "cli_tokens"},
                "declared_input_schema_sha256": "bb" * 32,
                "static_dependency_tags": [],
                "prerequisites": [],
            }
        ]
    )
    assert len(declarations) > 20
    public_schemas = _load_fixture("python.json")["public_schemas"]
    frame = build_public_behavior_frame(
        _source_record(),
        _discovery_receipt(declarations, public_schemas=public_schemas),
    )
    accounting = frame["category_accounting"]
    assert [row["category"] for row in accounting] == BEHAVIOR_CATEGORY_ORDER
    assert all("discovered_count" in row for row in accounting)
    assert all(row["discovered_count"] >= 0 for row in accounting)
    empty_frame = build_public_behavior_frame(
        _source_record(),
        _discovery_receipt(
            [
                {
                    "category": "PUBLIC_API",
                    "provenance_path": "src/only.py",
                    "provenance_span_or_key": "only",
                    "entrypoint": "only:f",
                    "normalized_entrypoint": "only:f",
                    "declared_inputs": {"kind": "none"},
                    "declared_input_schema_sha256": "cc" * 32,
                    "static_dependency_tags": [],
                    "prerequisites": [],
                }
            ]
        ),
    )
    assert [row["category"] for row in empty_frame["category_accounting"]] == BEHAVIOR_CATEGORY_ORDER
    assert sum(1 for row in empty_frame["category_accounting"] if row["discovered_count"] == 0) == 4

    invalid = [row for row in frame["rows"] if row["discovery_status"] == "INVALID_DECLARATION"]
    assert len(invalid) == 1
    assert invalid[0]["provenance_path"] == "docs/broken.md"
    assert invalid[0]["unsupported_or_exclusion_reason"]
    executable = [row for row in frame["rows"] if row["discovery_status"] == "EXECUTABLE"]
    assert len(executable) == 20
    assert frame["public_schemas"] == public_schemas
    assert frame["controlled_subject_source_id"] == canonical_sha256(
        {
            "normalized_source_tree_sha256": "21" * 32,
            "build_descriptor_sha256": "22" * 32,
            "domain": "P3-SOURCE-v1",
        }
    )


def test_public_behavior_rejects_missing_provenance(tmp_path):
    declaration = {
        "category": "PUBLIC_API",
        "ecosystem": "python",
        "adapter_id": "PYTHON_PEP517_V1",
        "provenance_path": "",
        "provenance_span_or_key": "solve",
        "entrypoint": "pkg:solve",
        "normalized_entrypoint": "pkg:solve",
        "declared_inputs": {"kind": "none"},
        "declared_input_schema_sha256": "dd" * 32,
        "static_dependency_tags": [],
        "prerequisites": [],
    }
    with pytest.raises(EvidenceError, match="E_PROVENANCE"):
        build_public_behavior_frame(_source_record(), _discovery_receipt([declaration]))


def test_public_behavior_frame_is_input_order_invariant(tmp_path):
    declarations = _tagged_declarations(_load_fixture("python.json"))
    first = build_public_behavior_frame(
        _source_record(), _discovery_receipt(declarations)
    )
    second = build_public_behavior_frame(
        _source_record(), _discovery_receipt(list(reversed(declarations)))
    )
    assert first == second


def test_unsupported_ecosystem_has_no_hand_command_fallback(tmp_path):
    discovery = _discovery_receipt(
        [], adapter_id=None, ecosystem="cargo", status="ADAPTER_UNSUPPORTED"
    )
    frame = build_public_behavior_frame(_source_record(), discovery)
    assert frame["rows"] == []
    assert all(row["executable_count"] == 0 for row in frame["category_accounting"])
    workload = select_profiling_workload(frame, "S")
    assert workload["selected_behavior_ids"] == []
    assert workload["budget"] == 10


def test_profiling_workload_selection_is_balanced_and_outcome_blind(tmp_path):
    declarations = _tagged_declarations(_load_fixture("python.json"))
    assert len(declarations) == 20
    frame = build_public_behavior_frame(
        _source_record(), _discovery_receipt(declarations)
    )
    workload = select_profiling_workload(frame, "L")
    assert workload["budget"] == 20
    assert workload["category_order"] == [
        "PUBLIC_API",
        "CLI",
        "EXAMPLE",
        "BENCHMARK",
        "PROJECT_TEST",
    ]
    assert workload["selected_category_counts"] == {
        "PUBLIC_API": 5,
        "CLI": 4,
        "EXAMPLE": 4,
        "BENCHMARK": 3,
        "PROJECT_TEST": 4,
    }
    assert len(workload["selected_behavior_ids"]) == 20
    baseline_ids = list(workload["selected_behavior_ids"])

    poisoned = []
    for index, item in enumerate(declarations):
        row = copy.deepcopy(item)
        row["execution_success"] = index % 2 == 0
        row["coverage"] = 0.01 * index
        row["technique_label"] = "ARRAY_NUMERICAL" if index % 2 else "SCALAR_CONTROL"
        row["mr_outcome"] = "MR_VIOLATION"
        row["p12_fault_id"] = f"fault-{index}"
        poisoned.append(row)
    poisoned_frame = build_public_behavior_frame(
        _source_record(), _discovery_receipt(poisoned)
    )
    poisoned_workload = select_profiling_workload(poisoned_frame, "L")
    assert poisoned_workload["selected_behavior_ids"] == baseline_ids

    shuffled_frame = build_public_behavior_frame(
        _source_record(), _discovery_receipt(list(reversed(poisoned)))
    )
    shuffled_workload = select_profiling_workload(shuffled_frame, "L")
    assert shuffled_workload["selected_behavior_ids"] == baseline_ids


def test_profiling_workload_prefers_unseen_diversity_then_behavior_id(tmp_path):
    schema = "ee" * 32
    declarations = []
    for category in BEHAVIOR_CATEGORY_ORDER:
        for index in range(3):
            declarations.append(
                {
                    "category": category,
                    "ecosystem": "python",
                    "adapter_id": "PYTHON_PEP517_V1",
                    "provenance_path": f"docs/{category.lower()}.md",
                    "provenance_span_or_key": f"item-{index}",
                    "entrypoint": f"{category.lower()}:entry_{index}",
                    "normalized_entrypoint": f"{category.lower()}:shared",
                    "declared_inputs": {"kind": "none"},
                    "declared_input_schema_sha256": schema,
                    "static_dependency_tags": ["shared"],
                    "prerequisites": [],
                }
            )
    frame = build_public_behavior_frame(
        _source_record(), _discovery_receipt(declarations)
    )
    executable = [row for row in frame["rows"] if row["discovery_status"] == "EXECUTABLE"]
    by_category: dict[str, list[dict]] = {category: [] for category in BEHAVIOR_CATEGORY_ORDER}
    for row in executable:
        by_category[row["category"]].append(row)
    for rows in by_category.values():
        rows.sort(key=lambda item: (item["diversity_signature_sha256"], item["behavior_id"]))
    expected_first_pass = [by_category[category][0]["behavior_id"] for category in BEHAVIOR_CATEGORY_ORDER]
    workload = select_profiling_workload(frame, "S")
    assert workload["selected_behavior_ids"][:5] == expected_first_pass
    assert len(workload["selected_behavior_ids"]) == 10


def test_profiling_fallback_uses_behavior_id_after_unseen_diversity_is_exhausted():
    source_id = "21" * 32
    rows = []
    for behavior_id, diversity in (
        ("f" * 64, "0" * 64),
        ("e" * 64, "1" * 64),
        ("d" * 64, "2" * 64),
        ("c" * 64, "1" * 64),
        ("0" * 64, "2" * 64),
    ):
        rows.append(
            {
                "controlled_subject_source_id": source_id,
                "category": "PUBLIC_API",
                "provenance_path": f"docs/{behavior_id[0]}.md",
                "provenance_span_or_key": behavior_id[0],
                "entrypoint": f"entry:{behavior_id[0]}",
                "normalized_entrypoint": f"entry:{behavior_id[0]}",
                "declared_inputs": {"kind": "none"},
                "declared_input_schema_sha256": "a" * 64,
                "static_dependency_tags": [],
                "prerequisites": [],
                "ecosystem": "python",
                "adapter_id": "PYTHON_PEP517_V1",
                "discovery_status": "EXECUTABLE",
                "unsupported_or_exclusion_reason": "",
                "diversity_signature_sha256": diversity,
                "behavior_id": behavior_id,
                "artifact_sha256": "b" * 64,
            }
        )
    workload = select_profiling_workload(
        {"controlled_subject_source_id": source_id, "rows": rows}, "S"
    )
    assert workload["selected_behavior_ids"][:4] == [
        "f" * 64,
        "c" * 64,
        "0" * 64,
        "d" * 64,
    ]


def _behavior_id(label: str) -> str:
    return canonical_sha256(
        {
            "domain": "P3-TEST-BEHAVIOR-v1",
            "label": label,
        }
    )


def _synthetic_workload(rows: list[tuple[str, str]]) -> dict:
    selected_rows = [
        {
            "behavior_id": behavior_id,
            "category": category,
            "diversity_signature_sha256": "ab" * 32,
            "normalized_entrypoint": f"entry:{behavior_id[:8]}",
            "declared_input_schema_sha256": "cd" * 32,
            "static_dependency_tags": [],
            "provenance_path": f"docs/{category.lower()}.md",
            "provenance_span_or_key": behavior_id[:8],
            "entrypoint": f"entry:{behavior_id[:8]}",
        }
        for behavior_id, category in rows
    ]
    counts = {
        category: sum(1 for _, item_category in rows if item_category == category)
        for category in BEHAVIOR_CATEGORY_ORDER
        if any(item_category == category for _, item_category in rows)
    }
    source_id = canonical_sha256(
        {
            "normalized_source_tree_sha256": "41" * 32,
            "build_descriptor_sha256": "42" * 32,
            "domain": "P3-SOURCE-v1",
        }
    )
    body = {
        "schema_version": "p3-profiling-workload-v1",
        "controlled_subject_source_id": source_id,
        "scale_class": "S",
        "budget": 10,
        "category_order": list(BEHAVIOR_CATEGORY_ORDER),
        "selected_rows": selected_rows,
        "selected_behavior_ids": [behavior_id for behavior_id, _ in rows],
        "selected_category_counts": counts,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _success(behavior_id: str, *tags: str) -> dict:
    call_by_technique = {
        "HYBRID_NATIVE": ("ctypes.cdll", "invoke", "NATIVE_CALL"),
        "TENSOR_AUTODIFF": ("torch.autograd", "backward", "PYTHON_CALL"),
        "PROBABILISTIC_SURROGATE": (
            "sklearn.gaussian_process",
            "predict",
            "PYTHON_CALL",
        ),
        "ITERATIVE_STOCHASTIC": ("scipy.optimize", "minimize", "PYTHON_CALL"),
        "ARRAY_NUMERICAL": ("numpy.linalg", "solve", "PYTHON_CALL"),
        "SCALAR_CONTROL": ("builtins", "abs", "PYTHON_CALL"),
    }
    call_trace = [
        {
            "sequence": sequence,
            "module": call_by_technique[tag][0],
            "symbol": call_by_technique[tag][1],
            "call_kind": call_by_technique[tag][2],
            "argument_types": ["float"],
            "keyword_names": [],
        }
        for sequence, tag in enumerate(tags, start=1)
    ]
    return {
        "behavior_id": behavior_id,
        "status": "SUCCESS",
        "argv": ["fixture-runner", behavior_id],
        "input_sha256": ["51" * 32],
        "environment_sha256": "52" * 32,
        "runner_version": "fixture-runner-v1",
        "exit_code": 0,
        "stdout_sha256": "53" * 32,
        "stderr_sha256": "54" * 32,
        "call_trace": call_trace,
        "call_trace_sha256": canonical_sha256(call_trace),
        "timed_out": False,
        "failure_code": "",
        "observed_site_ids": [],
    }


def _unresolved(behavior_id: str, status: str) -> dict:
    return {
        "behavior_id": behavior_id,
        "status": status,
        "argv": ["fixture-runner", behavior_id],
        "input_sha256": ["51" * 32],
        "environment_sha256": "52" * 32,
        "runner_version": "fixture-runner-v1",
        "exit_code": None,
        "stdout_sha256": "53" * 32,
        "stderr_sha256": "54" * 32,
        "call_trace": [],
        "call_trace_sha256": canonical_sha256([]),
        "timed_out": status == "TIMEOUT",
        "failure_code": f"PROFILE_{status}",
        "observed_site_ids": [],
    }


def _profiling_receipt(workload: dict, rows: list[dict], **overrides) -> dict:
    body = {
        "schema_version": "p3-profiling-results-v1",
        "neutral_snapshot_id": "61" * 32,
        "controlled_subject_source_id": workload["controlled_subject_source_id"],
        "normalized_source_tree_sha256": "41" * 32,
        "build_descriptor_sha256": "42" * 32,
        "profiling_workload_sha256": workload["artifact_sha256"],
        "adapter_implementation_source_sha256": "31" * 32,
        "runner_implementation_source_sha256": file_sha256(
            Path(frames_module.__file__)
        ),
        "results": sorted(rows, key=lambda row: row["behavior_id"]),
    }
    body.update(overrides)
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _classify(workload: dict, rows: list[dict]) -> dict:
    return classify_technique(workload, _profiling_receipt(workload, rows))


def test_profiling_receipt_derives_technique_from_raw_call_trace():
    behavior_id = _behavior_id("derived-scalar")
    workload = _synthetic_workload([(behavior_id, "PUBLIC_API")])

    profile = _classify(workload, [_success(behavior_id, "SCALAR_CONTROL")])

    assert profile["confirmed_tags"] == ["SCALAR_CONTROL"]
    assert profile["primary_technique"] == "SCALAR_CONTROL"


def test_profiling_receipt_rejects_direct_trace_features_after_rehash():
    behavior_id = _behavior_id("forged-feature")
    workload = _synthetic_workload([(behavior_id, "PUBLIC_API")])
    row = {
        **_success(behavior_id, "SCALAR_CONTROL"),
        "trace_features": ["TENSOR_AUTODIFF_OPERATION"],
    }
    receipt = _profiling_receipt(workload, [row])

    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        classify_technique(workload, receipt)


def test_profiling_receipt_rejects_direct_technique_tags_after_rehash():
    behavior_id = _behavior_id("forged-label")
    workload = _synthetic_workload([(behavior_id, "PUBLIC_API")])
    row = {**_success(behavior_id), "technique_tags": ["HYBRID_NATIVE"]}
    receipt = _profiling_receipt(workload, [row])

    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        classify_technique(workload, receipt)


def test_profiling_receipt_rejects_call_trace_bytes_with_stale_hash():
    behavior_id = _behavior_id("stale-trace-hash")
    workload = _synthetic_workload([(behavior_id, "PUBLIC_API")])
    row = _success(behavior_id, "ARRAY_NUMERICAL")
    row["call_trace"][0]["symbol"] = "backward"
    receipt = _profiling_receipt(workload, [row])

    with pytest.raises(EvidenceError, match="E_PROFILE_TRACE_HASH"):
        classify_technique(workload, receipt)


def test_profiling_call_symbol_changes_mechanically_derived_technique():
    behavior_id = _behavior_id("symbol-derived-technique")
    workload = _synthetic_workload([(behavior_id, "PUBLIC_API")])
    scalar_row = _success(behavior_id, "SCALAR_CONTROL")
    scalar_row["call_trace"][0].update(
        {"module": "subject.kernel", "symbol": "scalar_add"}
    )
    scalar_row["call_trace_sha256"] = canonical_sha256(scalar_row["call_trace"])
    tensor_row = copy.deepcopy(scalar_row)
    tensor_row["call_trace"][0]["symbol"] = "tensor_backward"
    tensor_row["call_trace_sha256"] = canonical_sha256(tensor_row["call_trace"])

    scalar = _classify(workload, [scalar_row])
    tensor = _classify(workload, [tensor_row])

    assert scalar["primary_technique"] == "SCALAR_CONTROL"
    assert tensor["primary_technique"] == "TENSOR_AUTODIFF"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("normalized_source_tree_sha256", "71" * 32, "E_PROFILE_SOURCE_BINDING"),
        ("build_descriptor_sha256", "72" * 32, "E_PROFILE_SOURCE_BINDING"),
        ("profiling_workload_sha256", "73" * 32, "E_PROFILE_WORKLOAD_BINDING"),
        (
            "runner_implementation_source_sha256",
            "74" * 32,
            "E_PROFILE_RUNNER_BINDING",
        ),
    ],
)
def test_profiling_receipt_rejects_rehashed_parent_or_runner_forgery(
    field, value, code
):
    behavior_id = _behavior_id(f"forged-{field}")
    workload = _synthetic_workload([(behavior_id, "PUBLIC_API")])
    receipt = _profiling_receipt(workload, [_success(behavior_id)])
    body = {key: item for key, item in receipt.items() if key != "artifact_sha256"}
    body[field] = value
    forged = {**body, "artifact_sha256": canonical_sha256(body)}

    with pytest.raises(EvidenceError, match=code):
        classify_technique(workload, forged)


def _category_balanced_fixture():
    scalar_ids = [_behavior_id(f"scalar-{index}") for index in range(8)]
    array_id = _behavior_id("array-0")
    rows = [(behavior_id, "PUBLIC_API") for behavior_id in scalar_ids]
    rows.append((array_id, "CLI"))
    workload = _synthetic_workload(rows)
    results = [_success(behavior_id, "SCALAR_CONTROL") for behavior_id in scalar_ids]
    results.append(_success(array_id, "ARRAY_NUMERICAL"))
    return workload, results, array_id


def test_classify_technique_is_category_equal_not_row_weighted():
    workload, results, array_id = _category_balanced_fixture()
    profile = _classify(workload, results)
    assert profile["lower_scores"]["SCALAR_CONTROL"] == "0.5"
    assert profile["lower_scores"]["ARRAY_NUMERICAL"] == "0.5"
    assert profile["upper_scores"]["SCALAR_CONTROL"] == "0.5"
    assert profile["upper_scores"]["ARRAY_NUMERICAL"] == "0.5"
    assert set(profile["confirmed_tags"]) == {"ARRAY_NUMERICAL", "SCALAR_CONTROL"}
    assert set(profile["possible_tags"]) == {"ARRAY_NUMERICAL", "SCALAR_CONTROL"}

    failed_ids = [_behavior_id(f"cli-fail-{index}") for index in range(3)]
    extended_rows = [
        (row["behavior_id"], row["category"]) for row in workload["selected_rows"]
    ] + [(behavior_id, "CLI") for behavior_id in failed_ids]
    extended_workload = _synthetic_workload(extended_rows)
    extended_results = list(results) + [
        _unresolved(behavior_id, "FAILURE") for behavior_id in failed_ids
    ]
    widened = _classify(extended_workload, extended_results)
    assert widened["lower_scores"]["SCALAR_CONTROL"] == "0.5"
    assert widened["lower_scores"]["ARRAY_NUMERICAL"] == "0.125"
    assert widened["upper_scores"]["SCALAR_CONTROL"] == "0.875"
    assert widened["upper_scores"]["ARRAY_NUMERICAL"] == "0.5"
    for technique, upper in widened["upper_scores"].items():
        baseline = profile["upper_scores"].get(technique, "0")
        assert float(upper) >= float(baseline)
    funnel = {row["category"]: row for row in widened["category_funnel"]}
    assert funnel["CLI"]["n_c"] == 4
    assert funnel["CLI"]["unresolved_count"] == 3
    assert funnel["PUBLIC_API"]["n_c"] == 8
    assert array_id in extended_workload["selected_behavior_ids"]


def test_classify_technique_requires_success_in_every_selected_category():
    scalar_id = _behavior_id("only-scalar")
    failed_id = _behavior_id("failed-cli")
    workload = _synthetic_workload(
        [(scalar_id, "PUBLIC_API"), (failed_id, "CLI")]
    )
    results = [
        _success(scalar_id, "SCALAR_CONTROL"),
        _unresolved(failed_id, "TIMEOUT"),
    ]
    profile = _classify(workload, results)
    assert profile["primary_technique"] == "TECH_UNCERTAIN"


def test_classify_technique_overlapping_intervals_are_uncertain():
    workload, results, _array_id = _category_balanced_fixture()
    failed_ids = [_behavior_id(f"overlap-fail-{index}") for index in range(3)]
    rows = [(row["behavior_id"], row["category"]) for row in workload["selected_rows"]]
    rows.extend((behavior_id, "CLI") for behavior_id in failed_ids)
    workload = _synthetic_workload(rows)
    results = list(results) + [
        _unresolved(behavior_id, "ADAPTER_UNCERTAIN") for behavior_id in failed_ids
    ]
    profile = _classify(workload, results)
    assert profile["primary_technique"] == "TECH_UNCERTAIN"


def test_classify_technique_strict_lower_bound_winner():
    left = _behavior_id("winner-left")
    right = _behavior_id("winner-right")
    uncertain = _behavior_id("winner-uncertain")
    workload = _synthetic_workload(
        [
            (left, "PUBLIC_API"),
            (right, "CLI"),
            (uncertain, "CLI"),
        ]
    )
    results = [
        _success(left, "SCALAR_CONTROL"),
        _success(right, "SCALAR_CONTROL"),
        _unresolved(uncertain, "MISSING_TRACE"),
    ]
    profile = _classify(workload, results)
    assert profile["lower_scores"]["SCALAR_CONTROL"] == "0.75"
    assert profile["upper_scores"]["SCALAR_CONTROL"] == "1"
    assert profile["primary_technique"] == "SCALAR_CONTROL"
    assert profile["confirmed_tags"] == ["SCALAR_CONTROL"]
    assert profile["category_funnel"][1]["n_c"] == 2
    assert profile["category_funnel"][1]["unresolved_count"] == 1


def test_classify_technique_tie_breaks_with_frozen_technique_order():
    left = _behavior_id("tie-left")
    right = _behavior_id("tie-right")
    workload = _synthetic_workload([(left, "PUBLIC_API"), (right, "CLI")])
    results = [
        _success(left, "SCALAR_CONTROL"),
        _success(right, "ARRAY_NUMERICAL"),
    ]
    profile = _classify(workload, results)
    assert profile["lower_scores"]["SCALAR_CONTROL"] == "0.5"
    assert profile["lower_scores"]["ARRAY_NUMERICAL"] == "0.5"
    assert profile["primary_technique"] == "ARRAY_NUMERICAL"


def test_classify_technique_is_result_order_invariant():
    workload, results, _array_id = _category_balanced_fixture()
    first = _classify(workload, results)
    second = _classify(workload, list(reversed(results)))
    assert first == second
    assert canonical_sha256(first) == canonical_sha256(second)


def test_build_subject_frames_has_no_caller_technique_profile_authority(
    synthetic_release,
):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    features = _features(verified["records"][0]["neutral_snapshot_id"])
    assert features[0]["primary_technique"] == "ARRAY_NUMERICAL"
    left = _behavior_id("frame-left")
    right = _behavior_id("frame-right")
    workload = _synthetic_workload([(left, "PUBLIC_API"), (right, "CLI")])
    results = [
        _success(left, "SCALAR_CONTROL"),
        _success(right, "SCALAR_CONTROL"),
    ]
    profile = _classify(workload, results)
    assert profile["primary_technique"] == "SCALAR_CONTROL"
    with pytest.raises(TypeError):
        build_subject_frames(verified, features, technique_profile=profile)


def _load_generator_registry() -> dict:
    return json.loads((GENERATOR_FIXTURE_ROOT / "registry.json").read_text(encoding="utf-8"))


def _public_schema(schema_kind: str, raw_schema: dict, **aliases) -> dict:
    record = {
        "schema_kind": schema_kind,
        "raw_schema": raw_schema,
        "provenance_path": "public-schema.json",
        "provenance_span_or_key": schema_kind,
    }
    record.update(aliases)
    return record


def _public_frame_with_schemas(
    schemas: list[dict], *, discovery_status: str = "EXECUTABLE"
) -> dict:
    source_id = canonical_sha256(
        {
            "normalized_source_tree_sha256": "21" * 32,
            "build_descriptor_sha256": "22" * 32,
            "domain": "P3-SOURCE-v1",
        }
    )
    body = {
        "schema_version": "p3-public-behavior-frame-v1",
        "controlled_subject_source_id": source_id,
        "discovery_status": discovery_status,
        "category_accounting": [
            {
                "category": category,
                "discovered_count": 0,
                "executable_count": 0,
                "adapter_unsupported_count": 0,
                "invalid_count": 0,
            }
            for category in BEHAVIOR_CATEGORY_ORDER
        ],
        "rows": [],
        "public_schemas": schemas,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def test_input_generator_registry_binds_exact_five_e_common_ids_and_source_hashes():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    assert {item["generator_id"] for item in registry["generators"]} == set(
        E_COMMON_GENERATOR_IDS
    )
    assert len(registry["generators"]) == 5
    for item in registry["generators"]:
        absolute = GENERATOR_FIXTURE_ROOT / item["implementation_path"]
        assert file_sha256(absolute) == item["source_sha256"]
        assert item["schema_kind"] == item["generator_id"]
        assert item["failure_code"]
        assert item["output_schema"]["generator_id"] == item["generator_id"]


def test_input_generator_registry_rejects_source_hash_mismatch(tmp_path):
    registry = _load_generator_registry()
    for item in registry["generators"]:
        src = GENERATOR_FIXTURE_ROOT / item["implementation_path"]
        dst = tmp_path / item["implementation_path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
    mutated = {
        **registry,
        "generators": [
            {
                **item,
                "source_sha256": "0" * 64
                if item["generator_id"] == "NUMERIC_ARRAY_DOMAIN_V1"
                else item["source_sha256"],
            }
            for item in registry["generators"]
        ],
    }
    body = {key: value for key, value in mutated.items() if key != "artifact_sha256"}
    mutated = {**body, "artifact_sha256": canonical_sha256(body)}
    with pytest.raises(EvidenceError, match="E_GENERATOR_SOURCE_HASH"):
        validate_input_generator_registry(mutated, _source_snapshot(tmp_path))


def test_generator_execution_consumes_validated_snapshot_without_path_reopen(
    tmp_path,
):
    shutil.copytree(GENERATOR_FIXTURE_ROOT, tmp_path, dirs_exist_ok=True)
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(tmp_path)
    )
    selected = next(
        row
        for row in registry["generators"]
        if row["generator_id"] == "NUMERIC_ARRAY_DOMAIN_V1"
    )
    (tmp_path / selected["implementation_path"]).write_text(
        "raise RuntimeError('changed generator bytes executed')\n", encoding="utf-8"
    )
    frame = _public_frame_with_schemas(
        [
            _public_schema(
                "NUMERIC_ARRAY_DOMAIN_V1", {"domain": "numeric", "shape": [2]}
            )
        ]
    )

    inventory = build_common_inputs(_source_record(), frame, registry)

    assert {row["status"] for row in inventory["rows"]} == {
        "COMMON_INPUT_EXECUTABLE"
    }


@pytest.mark.parametrize("effect", ["stdout", "socket"])
def test_verified_generator_execution_rejects_output_and_network_side_effects(
    tmp_path, monkeypatch, capsys, effect
):
    shutil.copytree(GENERATOR_FIXTURE_ROOT, tmp_path, dirs_exist_ok=True)
    registry = _load_generator_registry()
    selected = next(
        row
        for row in registry["generators"]
        if row["generator_id"] == "NUMERIC_ARRAY_DOMAIN_V1"
    )
    implementation = tmp_path / selected["implementation_path"]
    source = implementation.read_text(encoding="utf-8").replace(
        "import hashlib\n", "import hashlib\nimport socket\n"
    )
    action = (
        "    print('generator stdout leak')\n"
        if effect == "stdout"
        else "    socket.create_connection(('example.invalid', 80))\n"
    )
    source = source.replace(
        "def generate(schema_bytes: bytes, seed: int) -> dict[str, Any]:\n",
        "def generate(schema_bytes: bytes, seed: int) -> dict[str, Any]:\n" + action,
    )
    implementation.write_text(source, encoding="utf-8")
    selected["source_sha256"] = hashlib.sha256(implementation.read_bytes()).hexdigest()
    body = {key: value for key, value in registry.items() if key != "artifact_sha256"}
    registry = {**body, "artifact_sha256": canonical_sha256(body)}
    validated = validate_input_generator_registry(
        registry, _source_snapshot(tmp_path)
    )
    frame = _public_frame_with_schemas(
        [
            _public_schema(
                "NUMERIC_ARRAY_DOMAIN_V1", {"domain": "numeric", "shape": [2]}
            )
        ]
    )

    def forbid_real_network(*_args, **_kwargs):
        raise AssertionError("test must not perform real network access")

    if effect == "socket":
        monkeypatch.setattr(socket, "create_connection", forbid_real_network)

    with pytest.raises(
        EvidenceError, match="E_VERIFIED_EXECUTION_(OUTPUT|NETWORK)"
    ):
        build_common_inputs(_source_record(), frame, validated)

    assert capsys.readouterr() == ("", "")


def test_build_common_inputs_ordinals_seeds_dedupe_and_round_robin():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    schemas = [
        _public_schema(
            "NUMERIC_ARRAY_DOMAIN_V1",
            {"domain": "numeric", "shape": [2], "label": "a"},
            subject_alias="subject-a",
            project_alias="proj-a",
        ),
        _public_schema(
            "CLI_TOKEN_GRAMMAR_V1",
            {"domain": "cli", "tokens": ["--x"], "label": "b"},
            subject_alias="subject-b",
        ),
        _public_schema(
            "NUMERIC_ARRAY_DOMAIN_V1",
            {"domain": "numeric", "shape": [2], "label": "a"},
            subject_alias="subject-duplicate",
            project_alias="proj-duplicate",
        ),
        _public_schema(
            "TEXT_IO_SCHEMA_V1",
            {"domain": "text", "encoding": "utf-8", "label": "c"},
        ),
    ]
    frame = _public_frame_with_schemas(schemas)
    inventory = build_common_inputs(_source_record(), frame, registry)
    assert inventory["schema_version"] == "p3-evaluation-inputs-common-v1"
    assert len(inventory["rows"]) == E_COMMON_COUNT == 30
    assert [row["ordinal"] for row in inventory["rows"]] == list(range(30))

    source_id = frame["controlled_subject_source_id"]
    for ordinal, row in enumerate(inventory["rows"]):
        expected_seed = int.from_bytes(
            bytes.fromhex(
                canonical_sha256(
                    {
                        "domain": "P3-E-COMMON-SEED-v1",
                        "controlled_subject_source_id": source_id,
                        "ordinal": ordinal,
                    }
                )
            )[:8],
            "big",
        )
        assert row["seed"] == expected_seed

    # Deduplicate by raw schema SHA-256 -> three eligible schemas.
    unique_raw = []
    seen_raw = set()
    for schema in schemas:
        raw_sha = canonical_sha256(schema["raw_schema"])
        if raw_sha in seen_raw:
            continue
        seen_raw.add(raw_sha)
        selection_body = {
            key: value
            for key, value in schema.items()
            if key not in {"subject_alias", "project_alias", "controlled_subject_source_id"}
        }
        unique_raw.append(
            (
                canonical_sha256(selection_body),
                raw_sha,
                schema["schema_kind"],
            )
        )
    unique_raw.sort(key=lambda item: (item[0], item[1]))
    assert len(unique_raw) == 3
    for index, row in enumerate(inventory["rows"]):
        expected_kind = unique_raw[index % 3][2]
        assert row["schema_kind"] == expected_kind
        assert row["generator_id"] == expected_kind
        assert row["status"] == "COMMON_INPUT_EXECUTABLE"
        assert row["raw_payload_sha256"]
        assert row["envelope"]["generator_id"] == expected_kind
        assert row["schema_provenance_path"] == "public-schema.json"
        assert row["schema_provenance_span_or_key"] == expected_kind
        assert len(row["generator_source_sha256"]) == 64

    shuffled = _public_frame_with_schemas(list(reversed(schemas)))
    shuffled_inventory = build_common_inputs(_source_record(), shuffled, registry)
    assert [row["raw_payload_sha256"] for row in shuffled_inventory["rows"]] == [
        row["raw_payload_sha256"] for row in inventory["rows"]
    ]
    assert [row["envelope"] for row in shuffled_inventory["rows"]] == [
        row["envelope"] for row in inventory["rows"]
    ]


def test_build_common_inputs_rejects_forbidden_generator_inputs():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    base_schemas = [
        _public_schema("NUMERIC_ARRAY_DOMAIN_V1", {"domain": "numeric", "shape": [1]})
    ]
    forbidden_cases = [
        {"project_test_body": "assert True"},
        {"project_test_fixture": {"x": 1}},
        {"contracts": [{"id": "c1"}]},
        {"contract": {"id": "c1"}},
        {"sites": [{"path": "a.py"}]},
        {"site": {"path": "a.py"}},
        {"profiling_results": [{"status": "SUCCESS"}]},
        {"profiling_result": {"status": "SUCCESS"}},
        {"patch": {"diff": "+x"}},
        {"mr": {"id": "mr-1"}},
        {"p12": {"fault_id": "f1"}},
        {"outcome": "MR_VIOLATION"},
        {"mr_outcome": "MR_VIOLATION"},
    ]
    for forbidden in forbidden_cases:
        poisoned_schema = {
            **base_schemas[0],
            **forbidden,
        }
        frame = _public_frame_with_schemas([poisoned_schema])
        with pytest.raises(EvidenceError, match="E_GENERATOR_INPUT"):
            build_common_inputs(_source_record(), frame, registry)


def test_generator_failure_occupies_ordinal_as_common_input_invalid():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    schemas = [
        _public_schema(
            "JSON_SCHEMA_DRAFT2020_12_V1",
            {"force_invalid": True},
        ),
        _public_schema(
            "NUMERIC_ARRAY_DOMAIN_V1",
            {"domain": "numeric", "shape": [3]},
        ),
    ]
    inventory = build_common_inputs(
        _source_record(), _public_frame_with_schemas(schemas), registry
    )
    assert len(inventory["rows"]) == 30
    invalid_rows = [
        row for row in inventory["rows"] if row["status"] == "COMMON_INPUT_INVALID"
    ]
    generated_rows = [
        row for row in inventory["rows"] if row["status"] == "COMMON_INPUT_EXECUTABLE"
    ]
    assert invalid_rows
    assert generated_rows
    for row in invalid_rows:
        assert row["ordinal"] in range(30)
        assert row["failure_code"] == "JSON_SCHEMA_DRAFT2020_12_V1_INVALID"
        assert row["envelope"] is None
        assert row["raw_payload_sha256"] is None
        assert row["schema_kind"] == "JSON_SCHEMA_DRAFT2020_12_V1"
    for row in generated_rows:
        assert row["schema_kind"] == "NUMERIC_ARRAY_DOMAIN_V1"
        assert row["envelope"] is not None
    # Ordinals assigned to the failing schema via i mod k remain invalid and are not replaced.
    ordered = []
    for schema in schemas:
        selection_body = {
            key: value
            for key, value in schema.items()
            if key not in {"subject_alias", "project_alias", "controlled_subject_source_id"}
        }
        ordered.append(
            (
                canonical_sha256(selection_body),
                canonical_sha256(schema["raw_schema"]),
                schema["schema_kind"],
            )
        )
    ordered.sort(key=lambda item: (item[0], item[1]))
    failing_index = next(
        index
        for index, item in enumerate(ordered)
        if item[2] == "JSON_SCHEMA_DRAFT2020_12_V1"
    )
    assert [row["ordinal"] for row in invalid_rows] == [
        ordinal for ordinal in range(30) if ordinal % 2 == failing_index
    ]
    assert len(invalid_rows) + len(generated_rows) == 30


def test_supported_common_input_generation_fails_closed_when_all_rows_invalid():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    frame = _public_frame_with_schemas(
        [
            _public_schema(
                "JSON_SCHEMA_DRAFT2020_12_V1",
                {"force_invalid": True},
            )
        ]
    )

    with pytest.raises(EvidenceError, match="E_COMMON_EXECUTABLE"):
        build_common_inputs(_source_record(), frame, registry)


def test_executable_discovery_with_zero_eligible_schemas_yields_unavailable_rows():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    inventory = build_common_inputs(
        _source_record(), _public_frame_with_schemas([]), registry
    )
    assert len(inventory["rows"]) == 30
    assert {row["status"] for row in inventory["rows"]} == {
        "COMMON_INPUT_UNAVAILABLE"
    }
    assert [row["ordinal"] for row in inventory["rows"]] == list(range(30))


def test_unsupported_discovery_yields_thirty_unavailable_rows():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    inventory = build_common_inputs(
        _source_record(),
        _public_frame_with_schemas([], discovery_status="ADAPTER_UNSUPPORTED"),
        registry,
    )
    assert len(inventory["rows"]) == 30
    assert {row["status"] for row in inventory["rows"]} == {"COMMON_INPUT_UNAVAILABLE"}
    assert [row["ordinal"] for row in inventory["rows"]] == list(range(30))
    assert all(row["envelope"] is None for row in inventory["rows"])
    assert all(row["raw_payload_sha256"] is None for row in inventory["rows"])


def test_fail_closed_discovery_yields_thirty_unavailable_rows():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    inventory = build_common_inputs(
        _source_record(),
        _public_frame_with_schemas(
            [], discovery_status="ADAPTER_EXECUTION_FAILED"
        ),
        registry,
    )
    assert len(inventory["rows"]) == 30
    assert {row["status"] for row in inventory["rows"]} == {
        "COMMON_INPUT_UNAVAILABLE"
    }


def test_validate_common_inputs_on_fixed_source_preserves_identities():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    schemas = [
        _public_schema("CLI_TOKEN_GRAMMAR_V1", {"domain": "cli", "tokens": ["a"]}),
        _public_schema(
            "BINARY_RECORD_SCHEMA_V1",
            {"force_invalid": True},
        ),
    ]
    inventory = build_common_inputs(
        _source_record(), _public_frame_with_schemas(schemas), registry
    )
    frozen_payloads = [
        (row["ordinal"], row["input_id"], row["raw_payload_sha256"], row["envelope"])
        for row in inventory["rows"]
    ]
    sites = [{"site_id": "1" * 64}]
    contracts = [{"contract_id": "2" * 64}]
    profile = {"primary_technique": "SCALAR_CONTROL"}
    frame_hash = "3" * 64

    def validator(row):
        if row["status"] == "COMMON_INPUT_UNAVAILABLE":
            return "COMMON_INPUT_UNAVAILABLE"
        if row["status"] == "COMMON_INPUT_INVALID":
            return "COMMON_INPUT_INVALID"
        if row["ordinal"] % 3 == 0:
            return "COMMON_INPUT_INVALID"
        return "COMMON_INPUT_EXECUTABLE"

    report = validate_common_inputs_on_fixed_source(
        inventory,
        validator,
        sites=sites,
        contracts=contracts,
        profile=profile,
        frame_artifact_sha256=frame_hash,
    )
    assert len(report["rows"]) == 30
    assert {row["status"] for row in report["rows"]} <= {
        "COMMON_INPUT_EXECUTABLE",
        "COMMON_INPUT_INVALID",
        "COMMON_INPUT_UNAVAILABLE",
    }
    assert all(
        row["status"]
        in {
            "COMMON_INPUT_EXECUTABLE",
            "COMMON_INPUT_INVALID",
            "COMMON_INPUT_UNAVAILABLE",
        }
        for row in report["rows"]
    )
    assert [row["ordinal"] for row in report["rows"]] == list(range(30))
    for before, after in zip(frozen_payloads, report["rows"], strict=True):
        assert after["ordinal"] == before[0]
        assert after["input_id"] == before[1]
        assert after["raw_payload_sha256"] == before[2]
        assert after["envelope"] == before[3]
    assert report["sites"] == sites
    assert report["contracts"] == contracts
    assert report["profile"] == profile
    assert report["frame_artifact_sha256"] == frame_hash
    # Validator cannot replace rows: still exactly 30 predetermined identities.
    assert len({row["input_id"] for row in report["rows"]}) == 30


APPLICABLE_CHRONOLOGY = [
    "SITE_FROZEN",
    "CONTRACT_FROZEN",
    "E_CONTRACT_FROZEN",
    "PATCH_FROZEN",
    "CERTIFICATION_WITNESS_SELECTED",
    "TERMINAL_STATE",
]

_CONTRACT_GENERATOR_TEMPLATE = '''\
"""Deterministic synthetic {generator_id} contract input generator."""

from __future__ import annotations

import hashlib
import json
from typing import Any


FAILURE_CODE = "{failure_code}"
GENERATOR_ID = "{generator_id}"


def _seed_block(seed: int, counter: int) -> bytes:
    return hashlib.sha256(
        b"P3-INPUT-STREAM-v1" + seed.to_bytes(8, "big") + counter.to_bytes(8, "big")
    ).digest()


def generate(schema_bytes: bytes, seed: int) -> dict[str, Any]:
    if not schema_bytes:
        return {{"failure_code": FAILURE_CODE}}
    try:
        schema = json.loads(schema_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {{"failure_code": FAILURE_CODE}}
    if isinstance(schema, dict) and schema.get("force_invalid") is True:
        return {{"failure_code": FAILURE_CODE}}
    if isinstance(schema, dict) and schema.get("unsupported_domain") is True:
        return {{"failure_code": "CONTRACT_INPUT_UNAVAILABLE"}}
    block = _seed_block(seed, 0)
    payload = {{
        "generator_id": GENERATOR_ID,
        "stream": block.hex(),
        "schema_fingerprint": hashlib.sha256(schema_bytes).hexdigest(),
    }}
    raw = (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        + b"\\n"
    )
    envelope = {{
        "schema_version": "p3-contract-input-envelope-v1",
        "generator_id": GENERATOR_ID,
        "payload": payload,
    }}
    return {{
        "envelope": envelope,
        "raw_payload_sha256": hashlib.sha256(raw).hexdigest(),
    }}
'''


def _canonical_sites() -> list[dict]:
    return [
        {
            "path": "a.py",
            "symbol": "f",
            "start_line": 1,
            "start_col": 0,
            "end_line": 1,
            "end_col": 1,
            "site_id": "a1" * 32,
        },
        {
            "path": "b.py",
            "symbol": "g",
            "start_line": 2,
            "start_col": 0,
            "end_line": 2,
            "end_col": 1,
            "site_id": "b2" * 32,
        },
    ]


def _slot() -> dict:
    return {
        "slot_id": "c3" * 32,
        "controlled_subject_id": "d4" * 32,
    }


def _contract_generator_registry(tmp_path: Path) -> dict:
    generators = []
    for generator_id in E_CONTRACT_GENERATOR_IDS:
        rel = f"generators/{generator_id.lower()}.py"
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        failure_code = f"{generator_id}_INVALID"
        source = _CONTRACT_GENERATOR_TEMPLATE.format(
            generator_id=generator_id,
            failure_code=failure_code,
        )
        path.write_text(source, encoding="utf-8")
        generators.append(
            {
                "generator_id": generator_id,
                "schema_kind": generator_id,
                "implementation_path": rel,
                "source_sha256": file_sha256(path),
                "output_schema": {
                    "generator_id": generator_id,
                    "schema_version": "p3-contract-input-envelope-v1",
                },
                "failure_code": failure_code,
            }
        )
    body = {
        "schema_version": "p3-contract-generator-registry-v1",
        "generators": generators,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _frozen_contract(generator_id: str, domain: dict) -> dict:
    return {
        "contract_id": "e5" * 32,
        "generator_id": generator_id,
        "domain": domain,
        "site_id": "a1" * 32,
    }


def test_contract_generator_registry_binds_exact_five_e_contract_ids(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    assert {item["generator_id"] for item in registry["generators"]} == set(
        E_CONTRACT_GENERATOR_IDS
    )
    assert len(registry["generators"]) == E_CONTRACT_COUNT == 5
    for item in registry["generators"]:
        absolute = tmp_path / item["implementation_path"]
        assert file_sha256(absolute) == item["source_sha256"]
        assert item["schema_kind"] == item["generator_id"]


def test_contract_generator_execution_consumes_snapshot_without_path_reopen(
    tmp_path,
):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    generator_id = E_CONTRACT_GENERATOR_IDS[0]
    selected = next(
        row for row in registry["generators"] if row["generator_id"] == generator_id
    )
    (tmp_path / selected["implementation_path"]).write_text(
        "raise RuntimeError('changed contract generator bytes executed')\n",
        encoding="utf-8",
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda site: site["symbol"] == "f")
    contract = _frozen_contract(generator_id, {"domain": "fixture"})

    inventory = build_contract_inputs(slot, contract, registry)

    assert {row["status"] for row in inventory["rows"]} == {
        "CONTRACT_INPUT_GENERATED"
    }


def test_verified_contract_generator_rejects_python_output(tmp_path, capsys):
    registry = _contract_generator_registry(tmp_path)
    generator_id = E_CONTRACT_GENERATOR_IDS[0]
    selected = next(
        row for row in registry["generators"] if row["generator_id"] == generator_id
    )
    implementation = tmp_path / selected["implementation_path"]
    implementation.write_text(
        implementation.read_text(encoding="utf-8").replace(
            "from __future__ import annotations\n",
            "from __future__ import annotations\n\n"
            "print('contract generator output leak')\n",
        ),
        encoding="utf-8",
    )
    selected["source_sha256"] = hashlib.sha256(implementation.read_bytes()).hexdigest()
    body = {key: value for key, value in registry.items() if key != "artifact_sha256"}
    registry = {**body, "artifact_sha256": canonical_sha256(body)}
    validated = validate_contract_generator_registry(registry, tmp_path)
    slot = close_slot(_slot(), _canonical_sites(), lambda site: site["symbol"] == "f")
    contract = _frozen_contract(generator_id, {"domain": "fixture"})

    with pytest.raises(EvidenceError, match="E_VERIFIED_EXECUTION_OUTPUT"):
        build_contract_inputs(slot, contract, validated)

    assert capsys.readouterr() == ("", "")


def test_close_slot_two_paths_not_applicable_or_site_frozen():
    slot = _slot()
    sites = _canonical_sites()
    closed = close_slot(slot, sites, lambda _site: False)
    assert closed["state"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE"
    assert closed["path"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE"
    assert closed["site_id"] is None
    assert closed["slot_id"] == slot["slot_id"]
    assert closed["controlled_subject_id"] == slot["controlled_subject_id"]

    applicable = close_slot(slot, sites, lambda site: site["symbol"] == "g")
    assert applicable["state"] == "SITE_FROZEN"
    assert applicable["path"] == "APPLICABLE"
    assert applicable["site_id"] == "b2" * 32


def test_build_contract_inputs_five_ordinals_seeds_and_named_generator(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda site: site["symbol"] == "f")
    contract = _frozen_contract(
        "CONTRACT_NUMERIC_DOMAIN_V1",
        {"domain": "numeric", "bounds": [0, 1]},
    )
    inventory = build_contract_inputs(slot, contract, registry)
    assert inventory["schema_version"] == "p3-evaluation-inputs-contract-v1"
    assert len(inventory["rows"]) == E_CONTRACT_COUNT == 5
    assert [row["ordinal"] for row in inventory["rows"]] == list(range(5))
    subject_id = slot["controlled_subject_id"]
    slot_id = slot["slot_id"]
    for ordinal, row in enumerate(inventory["rows"]):
        expected_seed = int.from_bytes(
            bytes.fromhex(
                canonical_sha256(
                    {
                        "domain": "P3-E-CONTRACT-SEED-v1",
                        "controlled_subject_id": subject_id,
                        "slot_id": slot_id,
                        "ordinal": ordinal,
                    }
                )
            )[:8],
            "big",
        )
        assert row["seed"] == expected_seed
        assert row["generator_id"] == "CONTRACT_NUMERIC_DOMAIN_V1"
        assert row["status"] == "CONTRACT_INPUT_GENERATED"
        assert row["raw_payload_sha256"]
        assert row["envelope"]["generator_id"] == "CONTRACT_NUMERIC_DOMAIN_V1"
        assert row["input_id"]


def test_unsupported_domain_yields_five_contract_input_unavailable(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda site: True)
    contract = _frozen_contract(
        "CONTRACT_ENUM_DOMAIN_V1",
        {"unsupported_domain": True},
    )
    inventory = build_contract_inputs(slot, contract, registry)
    assert len(inventory["rows"]) == 5
    assert {row["status"] for row in inventory["rows"]} == {"CONTRACT_INPUT_UNAVAILABLE"}
    assert all(row["envelope"] is None for row in inventory["rows"])
    assert all(row["raw_payload_sha256"] is None for row in inventory["rows"])
    # Cannot invent a replacement generator or site.
    assert {row["generator_id"] for row in inventory["rows"]} == {None}
    assert inventory["site_id"] == slot["site_id"]


def test_build_contract_inputs_rejects_not_applicable_slot(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda _site: False)
    contract = _frozen_contract(
        "CONTRACT_ARRAY_DOMAIN_V1",
        {"domain": "array", "shape": [2]},
    )
    with pytest.raises(EvidenceError, match="E_SLOT_PATH"):
        build_contract_inputs(slot, contract, registry)


def test_verify_slot_chronology_accepts_exactly_one_of_two_paths(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    not_applicable = {
        "slot_id": "c3" * 32,
        "chronology": ["APPLICABILITY_CLOSED_NOT_APPLICABLE"],
        "contract": None,
        "e_contract": None,
        "patch": None,
        "certification_witness": None,
        "e_common_input_ids": [],
        "e_contract_input_ids": [],
    }
    verify_slot_chronology(not_applicable)

    slot = close_slot(_slot(), _canonical_sites(), lambda site: site["symbol"] == "f")
    contract = _frozen_contract(
        "CONTRACT_SEQUENCE_DOMAIN_V1",
        {"domain": "sequence", "length": 3},
    )
    inventory = build_contract_inputs(slot, contract, registry)
    applicable = {
        "slot_id": slot["slot_id"],
        "chronology": list(APPLICABLE_CHRONOLOGY),
        "contract": contract,
        "e_contract": inventory,
        "patch": {"patch_id": "f6" * 32},
        "certification_witness": {"witness_id": "a7" * 32},
        "e_common_input_ids": ["b8" * 32],
        "e_contract_input_ids": [row["input_id"] for row in inventory["rows"]],
    }
    verify_slot_chronology(applicable)


def test_inapplicable_slot_carrying_downstream_artifacts_fails():
    for field, value in (
        ("contract", {"contract_id": "e5" * 32}),
        ("e_contract", {"rows": []}),
        ("patch", {"patch_id": "f6" * 32}),
        ("certification_witness", {"witness_id": "a7" * 32}),
    ):
        artifacts = {
            "slot_id": "c3" * 32,
            "chronology": ["APPLICABILITY_CLOSED_NOT_APPLICABLE"],
            "contract": None,
            "e_contract": None,
            "patch": None,
            "certification_witness": None,
            "e_common_input_ids": [],
            "e_contract_input_ids": [],
        }
        artifacts[field] = value
        with pytest.raises(EvidenceError, match="E_SLOT_CHRONOLOGY"):
            verify_slot_chronology(artifacts)


def test_applicable_slot_missing_e_contract_before_patch_fails(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda site: True)
    contract = _frozen_contract(
        "CONTRACT_RELATION_PAIR_DOMAIN_V1",
        {"domain": "relation", "pairs": [[0, 1]]},
    )
    inventory = build_contract_inputs(slot, contract, registry)
    missing_e_contract = {
        "slot_id": slot["slot_id"],
        "chronology": [
            "SITE_FROZEN",
            "CONTRACT_FROZEN",
            "PATCH_FROZEN",
            "CERTIFICATION_WITNESS_SELECTED",
            "TERMINAL_STATE",
        ],
        "contract": contract,
        "e_contract": None,
        "patch": {"patch_id": "f6" * 32},
        "certification_witness": {"witness_id": "a7" * 32},
        "e_common_input_ids": [],
        "e_contract_input_ids": [row["input_id"] for row in inventory["rows"]],
    }
    with pytest.raises(EvidenceError, match="E_SLOT_CHRONOLOGY"):
        verify_slot_chronology(missing_e_contract)

    patch_without_inventory = {
        "slot_id": slot["slot_id"],
        "chronology": list(APPLICABLE_CHRONOLOGY),
        "contract": contract,
        "e_contract": None,
        "patch": {"patch_id": "f6" * 32},
        "certification_witness": {"witness_id": "a7" * 32},
        "e_common_input_ids": [],
        "e_contract_input_ids": [],
    }
    with pytest.raises(EvidenceError, match="E_SLOT_CHRONOLOGY"):
        verify_slot_chronology(patch_without_inventory)


def test_post_patch_witness_in_either_input_inventory_fails(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda site: True)
    contract = _frozen_contract(
        "CONTRACT_ENUM_DOMAIN_V1",
        {"domain": "enum", "values": ["a", "b"]},
    )
    inventory = build_contract_inputs(slot, contract, registry)
    witness_from_contract = inventory["rows"][0]["input_id"]
    artifacts = {
        "slot_id": slot["slot_id"],
        "chronology": list(APPLICABLE_CHRONOLOGY),
        "contract": contract,
        "e_contract": inventory,
        "patch": {"patch_id": "f6" * 32},
        "certification_witness": {"witness_id": witness_from_contract},
        "e_common_input_ids": ["b8" * 32],
        "e_contract_input_ids": [row["input_id"] for row in inventory["rows"]],
    }
    with pytest.raises(EvidenceError, match="E_WITNESS_INVENTORY"):
        verify_slot_chronology(artifacts)

    artifacts_common = {
        **artifacts,
        "certification_witness": {"witness_id": "b8" * 32},
    }
    with pytest.raises(EvidenceError, match="E_WITNESS_INVENTORY"):
        verify_slot_chronology(artifacts_common)


def test_unexecuted_static_site_is_unprofiled_not_not_applicable():
    sites = _canonical_sites()
    tagged = tag_site_reachability(sites, [], lambda _site: True)
    assert [row["site_id"] for row in tagged] == ["a1" * 32, "b2" * 32]
    assert all(row["reachability"] == "UNPROFILED" for row in tagged)
    assert all(row["applicability"] == "APPLICABLE" for row in tagged)
    assert all(row["reachability"] != "NOT_APPLICABLE" for row in tagged)
    assert all(row["reachability"] != row["applicability"] or row["reachability"] == "UNPROFILED" for row in tagged)

    failed_predicate = tag_site_reachability(sites, [], lambda _site: False)
    assert all(row["reachability"] == "UNPROFILED" for row in failed_predicate)
    assert all(row["applicability"] == "NOT_APPLICABLE" for row in failed_predicate)


def test_only_failed_static_semantic_predicate_yields_not_applicable():
    sites = _canonical_sites()
    results = [
        {
            "behavior_id": "11" * 32,
            "status": "SUCCESS",
            "technique_tags": ["SCALAR_CONTROL"],
            "observed_site_ids": ["a1" * 32],
        }
    ]
    tagged = tag_site_reachability(
        sites, results, lambda site: site["symbol"] == "f"
    )
    by_id = {row["site_id"]: row for row in tagged}
    assert by_id["a1" * 32]["reachability"] == "OBSERVED_REACHABLE"
    assert by_id["a1" * 32]["applicability"] == "APPLICABLE"
    assert by_id["b2" * 32]["reachability"] == "UNPROFILED"
    assert by_id["b2" * 32]["applicability"] == "NOT_APPLICABLE"

    # Independent reconstruction: reachability from observed ids only; applicability
    # from predicate only. Unobserved + applicable is never NOT_APPLICABLE.
    observed = {"a1" * 32}
    rebuilt = []
    for site in sites:
        reachability = (
            "OBSERVED_REACHABLE" if site["site_id"] in observed else "UNPROFILED"
        )
        applicability = (
            "APPLICABLE" if site["symbol"] == "f" else "NOT_APPLICABLE"
        )
        rebuilt.append(
            {
                "site_id": site["site_id"],
                "reachability": reachability,
                "applicability": applicability,
            }
        )
    assert tagged == rebuilt


def test_proposal_record_rejects_missing_hashes_and_fabricated_provider_parameters():
    base = {
        "schema_version": "p3-proposal-record-v1",
        "provider_model": "synthetic/fixture-v1",
        "prompt_sha256": "a1" * 32,
        "context_sha256": "b2" * 32,
        "response_sha256": "c3" * 32,
        "timestamp_utc": "2026-08-10T00:00:00Z",
        "exposed_generation_metadata": {"finish_reason": "stop"},
        "temperature": UNAVAILABLE_NOT_CLAIMED,
        "seed": UNAVAILABLE_NOT_CLAIMED,
        "top_p": UNAVAILABLE_NOT_CLAIMED,
    }
    accepted = validate_proposal_record(base)
    assert accepted["temperature"] == UNAVAILABLE_NOT_CLAIMED
    assert accepted["seed"] == UNAVAILABLE_NOT_CLAIMED
    assert accepted["top_p"] == UNAVAILABLE_NOT_CLAIMED
    assert "artifact_sha256" in accepted

    for missing in ("prompt_sha256", "context_sha256", "response_sha256"):
        broken = {key: value for key, value in base.items() if key != missing}
        with pytest.raises(EvidenceError, match="E_PROPOSAL"):
            validate_proposal_record(broken)

    fabricated = {**base, "temperature": 0.7, "seed": 42}
    with pytest.raises(EvidenceError, match="E_PROPOSAL_UNAVAILABLE"):
        validate_proposal_record(fabricated)


# --- Real source-derived implementations (charter Task 2) -------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_PROJECT_ROOT = (
    Path(__file__).resolve().parent / "fixtures" / "real_python_project"
)
REAL_ADAPTER_RELATIVE = "src/p3_v3/adapters/python_pep517_v1.py"
REAL_ADAPTER_STUBS = {
    "CMAKE_CTEST_V1": ("cmake", "src/p3_v3/adapters/cmake_ctest_v1.py"),
    "MESON_TEST_V1": ("meson", "src/p3_v3/adapters/meson_test_v1.py"),
    "AUTOTOOLS_MAKECHECK_V1": (
        "autotools",
        "src/p3_v3/adapters/autotools_makecheck_v1.py",
    ),
}
REAL_GENERATOR_RELATIVE = {
    "JSON_SCHEMA_DRAFT2020_12_V1": "src/p3_v3/input_generators/json_schema_draft2020_12_v1.py",
    "CLI_TOKEN_GRAMMAR_V1": "src/p3_v3/input_generators/cli_token_grammar_v1.py",
    "NUMERIC_ARRAY_DOMAIN_V1": "src/p3_v3/input_generators/numeric_array_domain_v1.py",
    "TEXT_IO_SCHEMA_V1": "src/p3_v3/input_generators/text_io_schema_v1.py",
    "BINARY_RECORD_SCHEMA_V1": "src/p3_v3/input_generators/binary_record_schema_v1.py",
}
REAL_VALID_SCHEMAS = {
    "JSON_SCHEMA_DRAFT2020_12_V1": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "kind": "JSON_SCHEMA_DRAFT2020_12_V1",
        "type": "object",
        "properties": {"alpha": {"type": "integer"}, "beta": {"type": "string"}},
        "required": ["alpha", "beta"],
        "additionalProperties": False,
    },
    "CLI_TOKEN_GRAMMAR_V1": {
        "kind": "CLI_TOKEN_GRAMMAR_V1",
        "program": "demo-cli",
        "tokens": {"min": 0, "max": 3},
        "vocabulary": ["--help", "--version", "demo-cli"],
    },
    "NUMERIC_ARRAY_DOMAIN_V1": {
        "kind": "NUMERIC_ARRAY_DOMAIN_V1",
        "parameters": ["a", "b"],
        "element_count": 2,
        "dtype": "int64",
        "minimum": -1000000,
        "maximum": 1000000,
    },
    "TEXT_IO_SCHEMA_V1": {
        "kind": "TEXT_IO_SCHEMA_V1",
        "fields": ["prefix", "suffix"],
        "max_length": 256,
        "charset": "printable_ascii",
    },
    "BINARY_RECORD_SCHEMA_V1": {
        "kind": "BINARY_RECORD_SCHEMA_V1",
        "fields": ["payload"],
        "record_bytes": 32,
    },
}
_TEXT_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789 "


def _repo_file_entry(relative: str):
    raw = (REPO_ROOT / relative).read_bytes()
    return frames_module.SourceSnapshotEntry(
        relative_path=relative,
        mode="100644",
        sha256=hashlib.sha256(raw).hexdigest(),
        content=raw,
    )


def _real_controller_snapshot():
    paths = sorted(
        [
            REAL_ADAPTER_RELATIVE,
            *(relative for _eco, relative in REAL_ADAPTER_STUBS.values()),
            *REAL_GENERATOR_RELATIVE.values(),
        ]
    )
    entries = sorted(
        (_repo_file_entry(path) for path in paths),
        key=lambda entry: entry.relative_path.encode("utf-8"),
    )
    return frames_module.SourceSnapshot(entries=tuple(entries))


def _real_adapter_registry() -> dict:
    adapters = [
        {
            "adapter_id": "PYTHON_PEP517_V1",
            "ecosystem": "python",
            "implementation_path": REAL_ADAPTER_RELATIVE,
            "source_sha256": hashlib.sha256(
                (REPO_ROOT / REAL_ADAPTER_RELATIVE).read_bytes()
            ).hexdigest(),
        }
    ]
    for adapter_id, (ecosystem, relative) in sorted(REAL_ADAPTER_STUBS.items()):
        adapters.append(
            {
                "adapter_id": adapter_id,
                "ecosystem": ecosystem,
                "implementation_path": relative,
                "source_sha256": hashlib.sha256(
                    (REPO_ROOT / relative).read_bytes()
                ).hexdigest(),
            }
        )
    body = {"schema_version": "p3-adapter-registry-v1", "adapters": adapters}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _real_generator_registry() -> dict:
    generators = []
    for generator_id, relative in sorted(REAL_GENERATOR_RELATIVE.items()):
        raw = (REPO_ROOT / relative).read_bytes()
        generators.append(
            {
                "generator_id": generator_id,
                "schema_kind": generator_id,
                "implementation_path": relative,
                "source_sha256": hashlib.sha256(raw).hexdigest(),
                "output_schema": {
                    "generator_id": generator_id,
                    "schema_version": "p3-common-input-envelope-v1",
                },
                "failure_code": f"{generator_id}_INVALID",
            }
        )
    body = {
        "schema_version": "p3-input-generator-registry-v1",
        "generators": generators,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _real_discovery():
    registry = validate_adapter_registry(
        _real_adapter_registry(), _real_controller_snapshot()
    )
    return run_adapter_discovery(
        _source_snapshot(REAL_PROJECT_ROOT),
        {"ecosystem": "python"},
        registry,
        "PYTHON_PEP517_V1",
    )


def _load_real_generator(generator_id: str):
    source = (REPO_ROOT / REAL_GENERATOR_RELATIVE[generator_id]).read_bytes()
    namespace: dict = {"__name__": f"test_real_{generator_id.lower()}"}
    exec(compile(source, REAL_GENERATOR_RELATIVE[generator_id], "exec"), namespace)
    return namespace["generate"]


def test_real_python_adapter_discovers_all_five_categories():
    discovery = _real_discovery()
    assert discovery["discovery_status"] == "EXECUTABLE"
    categories = [row["category"] for row in discovery["declarations"]]
    assert set(categories) == set(BEHAVIOR_CATEGORY_ORDER)
    assert categories.count("PUBLIC_API") == 6
    assert categories.count("CLI") == 1
    assert categories.count("EXAMPLE") == 1
    assert categories.count("BENCHMARK") == 1
    assert categories.count("PROJECT_TEST") == 1
    assert "build/generated.py" not in discovery["source_files"]
    assert all(site["path"] != "build/generated.py" for site in discovery["sites"])
    assert "src/demopkg/core.py" in discovery["source_files"]
    assert "tests/test_core.py" in discovery["source_files"]


def test_real_python_adapter_respects_public_and_all_restrictions():
    discovery = _real_discovery()
    entrypoints = {row["entrypoint"] for row in discovery["declarations"]}
    assert "demopkg.core:add" in entrypoints
    assert "demopkg.core:hidden_public" not in entrypoints
    assert "demopkg.core:main" not in entrypoints
    assert all(
        row["provenance_path"] != "src/demopkg/_internal.py"
        for row in discovery["declarations"]
    )
    assert all(
        site["path"] != "src/demopkg/_internal.py" for site in discovery["sites"]
    )


def test_real_python_adapter_schema_mapping_classes():
    discovery = _real_discovery()
    kinds = sorted(schema["schema_kind"] for schema in discovery["public_schemas"])
    assert kinds == [
        "BINARY_RECORD_SCHEMA_V1",
        "CLI_TOKEN_GRAMMAR_V1",
        "JSON_SCHEMA_DRAFT2020_12_V1",
        "NUMERIC_ARRAY_DOMAIN_V1",
        "NUMERIC_ARRAY_DOMAIN_V1",
        "TEXT_IO_SCHEMA_V1",
    ]
    assert all(
        schema["raw_schema"].get("kind") != "NO_INPUT"
        for schema in discovery["public_schemas"]
    )
    reset_rows = [
        row
        for row in discovery["declarations"]
        if row["entrypoint"] == "demopkg.core:reset"
    ]
    assert len(reset_rows) == 1
    assert reset_rows[0]["declared_input_schema_sha256"] == canonical_sha256(
        {"kind": "NO_INPUT"}
    )


def test_real_python_adapter_is_deterministic():
    first = _real_discovery()
    second = _real_discovery()
    assert first["artifact_sha256"] == second["artifact_sha256"]


def test_real_python_adapter_requires_pyproject(tmp_path):
    (tmp_path / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    registry = validate_adapter_registry(
        _real_adapter_registry(), _real_controller_snapshot()
    )
    with pytest.raises(EvidenceError, match="E_ADAPTER_EXECUTION"):
        run_adapter_discovery(
            _source_snapshot(tmp_path),
            {"ecosystem": "python"},
            registry,
            "PYTHON_PEP517_V1",
        )


def test_discover_subject_or_fail_closed_keeps_missing_cmakelists_visible(tmp_path):
    source = tmp_path / "subject"
    source.mkdir()
    (source / "README.md").write_text("no cmake root\n", encoding="utf-8")
    registry = validate_adapter_registry(
        _real_adapter_registry(), _real_controller_snapshot()
    )
    discovery = discover_subject_or_fail_closed(
        _source_snapshot(source),
        {"ecosystem": "cmake", "language_family": "c"},
        registry,
        "CMAKE_CTEST_V1",
    )
    assert discovery["discovery_status"] == "ADAPTER_EXECUTION_FAILED"
    assert discovery["adapter_id"] == "CMAKE_CTEST_V1"
    assert discovery["ecosystem"] == "cmake"
    assert discovery["implementation_source_sha256"]
    assert discovery["source_files"] == []
    assert discovery["declarations"] == []
    assert discovery["public_schemas"] == []
    assert discovery["sites"] == []
    assert discovery["unsupported_or_exclusion_reason"] == "CMakeLists.txt is absent"
    assert discovery["artifact_sha256"] == canonical_sha256(
        {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    )


def test_run_adapter_discovery_still_raises_on_missing_build_file(tmp_path):
    source = tmp_path / "subject"
    source.mkdir()
    (source / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    registry = validate_adapter_registry(
        _real_adapter_registry(), _real_controller_snapshot()
    )
    with pytest.raises(EvidenceError, match="E_ADAPTER_EXECUTION"):
        run_adapter_discovery(
            _source_snapshot(source),
            {"ecosystem": "python"},
            registry,
            "PYTHON_PEP517_V1",
        )


def test_phase1_unresolved_receipt_covers_selected_rows_and_classifies_uncertain():
    behavior_id = _behavior_id("phase1-unexecuted")
    workload = _synthetic_workload([(behavior_id, "PUBLIC_API")])
    receipt = build_phase1_unresolved_profiling_receipt(
        workload,
        {
            "normalized_source_tree_sha256": "41" * 32,
            "build_descriptor_sha256": "42" * 32,
        },
        neutral_snapshot_id="61" * 32,
        adapter_implementation_source_sha256="31" * 32,
    )
    assert receipt["schema_version"] == "p3-profiling-results-v1"
    assert len(receipt["results"]) == 1
    row = receipt["results"][0]
    assert row["status"] == "ADAPTER_UNCERTAIN"
    assert row["failure_code"] == "PHASE1_PROFILING_NOT_EXECUTED"
    assert row["call_trace"] == []
    assert row["timed_out"] is False
    profile = classify_technique(workload, receipt)
    assert profile["primary_technique"] == "TECH_UNCERTAIN"


def test_phase1_unresolved_receipt_covers_empty_workload():
    workload = _synthetic_workload([])
    receipt = build_phase1_unresolved_profiling_receipt(
        workload,
        {
            "normalized_source_tree_sha256": "41" * 32,
            "build_descriptor_sha256": "42" * 32,
        },
        neutral_snapshot_id="61" * 32,
        adapter_implementation_source_sha256=None,
    )
    assert receipt["results"] == []
    profile = classify_technique(workload, receipt)
    assert profile["primary_technique"] == "TECH_UNCERTAIN"


def test_derive_subject_material_keeps_cmake_execution_failure_in_funnel(tmp_path):
    source = tmp_path / "subject"
    source.mkdir()
    (source / "README.md").write_text("no cmake root\n", encoding="utf-8")
    snapshot = _source_snapshot(source)
    descriptor = {"ecosystem": "cmake", "language_family": "c"}
    source_record = {
        "normalized_source_tree_sha256": canonical_source_tree_sha256(snapshot),
        "build_descriptor_sha256": canonical_sha256(descriptor),
    }
    adapter_registry = validate_adapter_registry(
        _real_adapter_registry(), _real_controller_snapshot()
    )
    generator_registry = validate_input_generator_registry(
        _real_generator_registry(), _real_controller_snapshot()
    )
    discovery = discover_subject_or_fail_closed(
        snapshot, descriptor, adapter_registry, "CMAKE_CTEST_V1"
    )
    frame = build_public_behavior_frame(source_record, discovery)
    scale = derive_source_scale(snapshot, discovery)
    workload = select_profiling_workload(frame, scale["scale_class"])
    receipt = build_phase1_unresolved_profiling_receipt(
        workload,
        source_record,
        neutral_snapshot_id="ab" * 32,
        adapter_implementation_source_sha256=discovery[
            "implementation_source_sha256"
        ],
    )
    record = {
        "neutral_snapshot_id": "ab" * 32,
        "fixed_tree_commitment": "11" * 32,
        "normalized_source_tree_sha256": source_record[
            "normalized_source_tree_sha256"
        ],
        "source_archive_sha256": "12" * 32,
        "build_descriptor_sha256": source_record["build_descriptor_sha256"],
        "eligibility_reason": "fixture",
        "eligible_for_construct": True,
        "eligible_for_criterion": True,
    }
    material = derive_subject_material(
        {
            "neutral_snapshot_id": "ab" * 32,
            "source_snapshot": snapshot,
            "source_record": source_record,
            "build_descriptor": descriptor,
            "adapter_registry": adapter_registry,
            "input_generator_registry": generator_registry,
            "profiling_results": receipt,
        },
        record,
    )
    assert material["adapter_discovery"]["discovery_status"] == (
        "ADAPTER_EXECUTION_FAILED"
    )
    assert len(material["common_inputs"]["rows"]) == 30
    assert {row["status"] for row in material["common_inputs"]["rows"]} == {
        "COMMON_INPUT_UNAVAILABLE"
    }
    assert material["technique_profile"]["primary_technique"] == "TECH_UNCERTAIN"


def test_real_python_adapter_never_reads_test_or_example_bodies_for_schemas():
    discovery = _real_discovery()
    for schema in discovery["public_schemas"]:
        provenance = schema["provenance_path"]
        assert provenance == "pyproject.toml" or provenance.startswith("src/")


def test_real_python_adapter_sites_are_canonical():
    discovery = _real_discovery()
    symbols = {site["symbol"] for site in discovery["sites"]}
    assert "demopkg.core:_helper" in symbols
    assert "demopkg.core:Accumulator.add" in symbols
    assert "demopkg.core:Accumulator.__init__" in symbols
    for site in discovery["sites"]:
        assert site["end_line"] >= site["start_line"] >= 1
        assert site["start_col"] >= 0 and site["end_col"] >= 0


@pytest.mark.parametrize("generator_id", sorted(REAL_GENERATOR_RELATIVE))
def test_real_generator_is_deterministic_and_seed_sensitive(generator_id):
    generate = _load_real_generator(generator_id)
    schema_bytes = artifacts_module.canonical_json_bytes(
        REAL_VALID_SCHEMAS[generator_id]
    )
    first = generate(schema_bytes, 7)
    second = generate(schema_bytes, 7)
    other = generate(schema_bytes, 8)
    assert first == second
    assert "failure_code" not in first
    envelope = first["envelope"]
    assert envelope["schema_version"] == "p3-common-input-envelope-v1"
    assert envelope["generator_id"] == generator_id
    assert first["raw_payload_sha256"] == hashlib.sha256(
        artifacts_module.canonical_json_bytes(envelope["payload"])
    ).hexdigest()
    assert other["raw_payload_sha256"] != first["raw_payload_sha256"]


@pytest.mark.parametrize("generator_id", sorted(REAL_GENERATOR_RELATIVE))
def test_real_generator_rejects_invalid_schema_bytes(generator_id):
    generate = _load_real_generator(generator_id)
    for invalid in (b"", b"not json", b'{"kind": "WRONG_KIND"}\n'):
        result = generate(invalid, 7)
        assert result == {"failure_code": f"{generator_id}_INVALID"}


def test_real_generator_payloads_conform_to_their_schemas():
    payloads = {}
    for generator_id in sorted(REAL_GENERATOR_RELATIVE):
        generate = _load_real_generator(generator_id)
        schema = REAL_VALID_SCHEMAS[generator_id]
        result = generate(artifacts_module.canonical_json_bytes(schema), 11)
        payloads[generator_id] = result["envelope"]["payload"]

    json_arguments = payloads["JSON_SCHEMA_DRAFT2020_12_V1"]["arguments"]
    assert sorted(json_arguments) == ["alpha", "beta"]
    assert isinstance(json_arguments["alpha"], int)
    assert isinstance(json_arguments["beta"], str)

    argv = payloads["CLI_TOKEN_GRAMMAR_V1"]["argv"]
    assert argv[0] == "demo-cli"
    assert 0 <= len(argv) - 1 <= 3
    assert all(token in {"--help", "--version", "demo-cli"} for token in argv[1:])

    numeric = payloads["NUMERIC_ARRAY_DOMAIN_V1"]
    assert numeric["dtype"] == "int64"
    assert len(numeric["values"]) == 2
    assert all(-1000000 <= value <= 1000000 for value in numeric["values"])
    assert all(isinstance(value, int) for value in numeric["values"])

    text_fields = payloads["TEXT_IO_SCHEMA_V1"]["fields"]
    assert sorted(text_fields) == ["prefix", "suffix"]
    for value in text_fields.values():
        assert 1 <= len(value) <= 64
        assert all(character in _TEXT_ALPHABET for character in value)

    binary_fields = payloads["BINARY_RECORD_SCHEMA_V1"]["fields"]
    assert sorted(binary_fields) == ["payload"]
    assert len(binary_fields["payload"]) == 64
    assert set(binary_fields["payload"]) <= set("0123456789abcdef")


def test_real_pipeline_end_to_end_produces_executable_common_inputs():
    discovery = _real_discovery()
    subject_snapshot = _source_snapshot(REAL_PROJECT_ROOT)
    scale = derive_source_scale(subject_snapshot, discovery)
    assert scale["scale_class"] == "S"
    frame = build_public_behavior_frame(_source_record(), discovery)
    executable_rows = [
        row for row in frame["rows"] if row["discovery_status"] == "EXECUTABLE"
    ]
    assert len(executable_rows) == 10
    workload = select_profiling_workload(frame, scale["scale_class"])
    assert workload["budget"] == 10
    assert len(workload["selected_rows"]) == 10
    registry = validate_input_generator_registry(
        _real_generator_registry(), _real_controller_snapshot()
    )
    inventory = build_common_inputs(_source_record(), frame, registry)
    assert [row["ordinal"] for row in inventory["rows"]] == list(range(30))
    statuses = {row["status"] for row in inventory["rows"]}
    assert statuses == {"COMMON_INPUT_EXECUTABLE"}


def test_cxx_profile_maps_frozen_entrypoint_to_attempt2_include_boundary(tmp_path):
    from p3_v3 import profiling_runner

    source = tmp_path / "source"
    include = source / "include"
    cpp = tmp_path / "probe.cpp"
    obj = tmp_path / "probe.o"
    dep = tmp_path / "probe.d"
    entrypoint = "include/boost/math/statistics/runs_test.hpp"

    assert profiling_runner.header_include(entrypoint) == (
        "boost/math/statistics/runs_test.hpp"
    )
    assert profiling_runner.translation_unit_bytes(entrypoint) == (
        b"#include <boost/math/statistics/runs_test.hpp>\n"
        b"int main() { return 0; }\n"
    )
    assert profiling_runner.compile_argv(
        Path("/usr/bin/c++"), include, cpp, obj, dep
    ) == [
        "/usr/bin/c++",
        "-std=c++14",
        "-DBOOST_MATH_STANDALONE=1",
        "-I",
        include.as_posix(),
        "-MD",
        "-MF",
        dep.as_posix(),
        "-MT",
        obj.as_posix(),
        "-c",
        cpp.as_posix(),
        "-o",
        obj.as_posix(),
    ]


@pytest.mark.parametrize(
    "entrypoint",
    [
        "boost/math/statistics/runs_test.hpp",
        "include/not-boost/header.hpp",
        "include/boost/../escape.hpp",
        "/include/boost/math/header.hpp",
    ],
)
def test_cxx_profile_rejects_noncanonical_header_entrypoint(entrypoint):
    from p3_v3 import profiling_runner

    with pytest.raises(EvidenceError, match="E_PROFILE_HEADER_ENTRYPOINT"):
        profiling_runner.header_include(entrypoint)


def test_cxx_profile_depfile_accepts_only_controlled_boost_headers(tmp_path):
    from p3_v3 import profiling_runner

    include = tmp_path / "source" / "include"
    requested = "boost/math/statistics/runs_test.hpp"
    depfile = (
        f"probe.o: probe.cpp {include / requested} \\\n"
        f" {include / 'boost/math/tools/config.hpp'} /usr/include/c++/v1/vector\n"
    ).encode("utf-8")

    profiling_runner.validate_depfile_containment(depfile, include, requested)


def test_cxx_profile_depfile_rejects_system_boost_fallback(tmp_path):
    from p3_v3 import profiling_runner

    include = tmp_path / "source" / "include"
    depfile = (
        f"probe.o: probe.cpp {include / 'boost/math/statistics/runs_test.hpp'} "
        "/usr/include/boost/math/tools/config.hpp\n"
    ).encode("utf-8")

    with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
        profiling_runner.validate_depfile_containment(
            depfile, include, "boost/math/statistics/runs_test.hpp"
        )


def test_cxx_profile_depfile_requires_requested_controlled_header(tmp_path):
    from p3_v3 import profiling_runner

    include = tmp_path / "source" / "include"
    depfile = b"probe.o: probe.cpp /usr/include/c++/v1/vector\n"

    with pytest.raises(EvidenceError, match="E_PROFILE_DEPFILE"):
        profiling_runner.validate_depfile_containment(
            depfile, include, "boost/math/statistics/runs_test.hpp"
        )
