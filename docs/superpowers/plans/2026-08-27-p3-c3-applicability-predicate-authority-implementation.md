# P3 C3 Applicability Predicate Authority Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and freeze the approved 35-subject, 350-slot, outcome-blind applicability authority without opening real subject sites or running site selection.

**Architecture:** `slot_inventory.py` rebuilds 35 `controlled_subject_id` values from an identity-only allowlist and mechanically emits one 350-row inventory. `applicability_predicates.py` holds five pure static predicates, exact join/tail/token helpers, one registry builder, and the unique authority loader. Official JSON is generated only after both Python sources are byte-stable, then bound by one `applicability-authority.json` that every later consumer must load.

**Tech Stack:** Python 3.12、现有 `p3_v3` canonical artifact helpers、JSON、pytest。

## Global Constraints

- HEAD at implementation start must still be `25f0ebf5944328aa5b436c810739c8f9176213a9` plus only the approved untracked design/review files and the files this plan creates.
- Approved design: `docs/superpowers/specs/2026-08-27-p3-c3-applicability-predicate-authority-design.md` SHA-256 `78f45d2a20a256e0dbc0291740d1e8427d74f8e945494b16a3475ba2ffebc193`.
- Single-subject design remains unmodified: SHA-256 `d44f39e6b9258c8f11b069d207ca4ef42106d67e21b607bea9c9cb5423d9e3ff`.
- Bind these current file hashes, do not edit the files:
  - `data/p3_v3/protocol/site_policy.md` = `9772430e0a2539667a9aaa776b47ecae92a7830e19ec0a6e75a5dda9cfdfdcf7`
  - `data/p3_v3/protocol/operator_catalogue.md` = `060671a031c36699fe63c7376afbb4714c84b25eab28f06445804ee8d232a635`
- Cohort is the existing 35 Phase-1 controlled subjects. Do not add or drop subjects.
- Family order is exactly `("INV", "MONO", "CONV", "DYN", "CMP")`.
- Mechanism order is exactly `("CE", "OS", "HP", "TF", "SI")`.
- `mechanism = MECHANISM_ORDER[(subject_index + slot_ordinal) % 5]` for every family.
- Counts must be 350 total, 10 per subject, 70 per family, 14 per family/mechanism.
- `slot_id` domain is `P3-SLOT-IDENTITY-v1`. Subject identity domain remains `P3-SUBJECT-v1`.
- Identity projection allowlist is exactly `{normalized_source_tree_sha256, build_descriptor_sha256, public_workload_set_sha256}`. Extra keys fail closed.
- Do not read derived-subject documents, profiling-result files, technique profiles, archives, source files, or any real PBF site row.
- Predicates read only the current canonical site, joined static PBF rows after `schema_kind` attachment, family, and the frozen registry rule.
- One registry, one inventory, one authority manifest, one loader. No second ledger, no new schema file, no per-subject predicate, no per-family Python module.
- `close_slot` keeps `_SLOT_SCHEMA = {slot_id, controlled_subject_id}`. Pass only that two-field subset.
- `bridge_and_frames.py` is not modified.
- Claim ledger is not modified. C3 remains `blocked`.
- Do not run first-applicable on real sites, do not write `SITE_FROZEN` production closures, do not create contracts, `E_CONTRACT`, patches, or mutants.
- Do not run the full pytest suite, subject builds, compilers, profiling, mutation, benchmarks, qualification, or Attempt-2.
- Cursor Cloud commands use `python3`, `git`, `sha256sum`, and `jq`. Do not use `rtk`.
- If an approved design rule cannot be implemented without changing the scientific rule, stop and return to design review. Do not invent a replacement rule.
- After the four tasks and focused verification, stop. The later independent recovery task is `P3_C3_SELECTED_SUBJECT_SITE_SELECTION_RECOVERY`.

### Locked production interfaces

```python
def slot_id(
    controlled_subject_id: str,
    semantic_contract_family: str,
    slot_ordinal: int,
    permitted_construction_mechanism: str,
) -> str: ...

def project_controlled_subject_ids(
    phase1_identity_records: Sequence[Mapping[str, object]],
) -> tuple[str, ...]: ...

def freeze_slot_inventory(
    controlled_subject_ids: Sequence[str],
) -> dict[str, object]: ...

def symbol_tail(value: str) -> str: ...

def static_tokens(value: str) -> tuple[str, ...]: ...

def join_site_to_public_rows(
    site: Mapping[str, object],
    public_rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]: ...

def attach_schema_kind(
    row: Mapping[str, object],
    public_schemas: Sequence[Mapping[str, object]],
) -> dict[str, object]: ...

def evaluate_predicate(
    predicate_id: str,
    site: Mapping[str, object],
    joined_public_rows: Sequence[Mapping[str, object]],
) -> bool: ...

def build_predicate_registry(
    implementation_source_sha256: str,
) -> dict[str, object]: ...

def load_applicability_authority(
    *,
    manifest_path: Path,
    registry_path: Path,
    inventory_path: Path,
    slot_implementation_path: Path,
    predicate_implementation_path: Path,
) -> dict[str, object]: ...

def close_slot_with_authority(
    authority: Mapping[str, object],
    inventory_row: Mapping[str, object],
    canonical_sites: Sequence[Mapping[str, object]],
    public_behavior_frame: Mapping[str, object],
) -> dict[str, object]: ...

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
) -> dict[str, object]: ...
```

`attach_schema_kind`, `close_slot_with_authority`, and `materialize_applicability_authority` are required by the approved design and live in the two allowed Python modules. They are not a sixth production module.

### Locked artifact shapes

Slot inventory object:

```text
{
  "schema_version": "p3-slot-inventory-v1",
  "slots": [350 rows],
  "artifact_sha256": canonical_sha256(body without artifact_sha256)
}
```

Each slot row exactly:

```text
{
  "slot_id": <sha256>,
  "controlled_subject_id": <sha256>,
  "semantic_contract_family": "INV"|"MONO"|"CONV"|"DYN"|"CMP",
  "slot_ordinal": 0|1,
  "permitted_construction_mechanism": "CE"|"OS"|"HP"|"TF"|"SI"
}
```

Predicate registry object:

```text
{
  "schema_version": "p3-applicability-predicate-registry-v1",
  "predicates": [five rows in family order],
  "artifact_sha256": canonical_sha256(body without artifact_sha256)
}
```

Authority manifest object, `artifact_sha256` excluded from its own hash:

```text
{
  "authority_id": "p3-v3-phase2-applicability-authority-v1",
  "schema_version": "p3-applicability-authority-v1",
  "subject_identity_projection": [<35 sorted sha256 strings>],
  "subject_identity_projection_sha256": canonical_sha256(that array),
  "site_policy_sha256": file_sha256(site_policy.md),
  "operator_catalogue_sha256": file_sha256(operator_catalogue.md),
  "slot_inventory_artifact_sha256": inventory["artifact_sha256"],
  "slot_implementation_source_sha256": file_sha256(slot_inventory.py),
  "predicate_registry_artifact_sha256": registry["artifact_sha256"],
  "predicate_implementation_source_sha256": file_sha256(applicability_predicates.py),
  "canonicalization_implementation_source_sha256": file_sha256(artifacts.py),
  "artifact_sha256": canonical_sha256(body without artifact_sha256)
}
```

`slot_inventory_artifact_sha256` and `predicate_registry_artifact_sha256` bind the inner `artifact_sha256` fields, not the raw file digest. Implementation and protocol markdown bindings use `file_sha256`.

### Official generation order

1. Finish Task 1 and Task 2 Python sources and their focused tests. Do not write official JSON yet.
2. Freeze those two Python files. Compute `file_sha256` of each plus `src/p3_v3/artifacts.py`.
3. Build the 35-ID projection from identity-only Phase-1 fields and call `freeze_slot_inventory`.
4. Call `build_predicate_registry(predicate_implementation_source_sha256)`.
5. Read the two artifacts' inner `artifact_sha256` fields.
6. Write the unique manifest from those identities. Hash the manifest body without `artifact_sha256`.
7. Reload with `read_canonical_json` and `load_applicability_authority`.
8. If any already-bound source byte changes after step 6, validation must fail and the implementer must stop rather than silently rewrite the manifest.

---

### Task 1: Cohort identity projection and slot inventory

**Files:**
- Create: `src/p3_v3/slot_inventory.py`
- Create: `tests/p3_v3/test_applicability_authority.py`
- Do not create: `data/p3_v3/phase2/slot-inventory.json`

**Consumes:** `canonical_sha256`, `validate_sha256`, `validate_exact_object`, `EvidenceError` from `src/p3_v3/artifacts.py`.
**Produces:** `slot_id`, `project_controlled_subject_ids`, `freeze_slot_inventory`, `SEMANTIC_CONTRACT_FAMILIES`, `MECHANISM_ORDER`, and in-memory inventory objects.

- [ ] **Step 1: Write the failing slot-inventory tests**

Create `tests/p3_v3/test_applicability_authority.py` with this exact helper and tests. Use synthetic SHA-256 strings only.

```python
from __future__ import annotations

import hashlib
import inspect
from collections import Counter
from collections.abc import Mapping

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256, validate_sha256
from p3_v3.slot_inventory import (
    MECHANISM_ORDER,
    SEMANTIC_CONTRACT_FAMILIES,
    freeze_slot_inventory,
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
```

- [ ] **Step 2: Run RED**

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_applicability_authority.py -q
```

Expected: collection fails with `ModuleNotFoundError` or `ImportError` for `p3_v3.slot_inventory`. No tests pass.

- [ ] **Step 3: Implement the minimal inventory module**

Create `src/p3_v3/slot_inventory.py` with this implementation. Do not read files in these functions.

```python
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from p3_v3.artifacts import EvidenceError, canonical_sha256, validate_exact_object, validate_sha256

SEMANTIC_CONTRACT_FAMILIES = ("INV", "MONO", "CONV", "DYN", "CMP")
MECHANISM_ORDER = ("CE", "OS", "HP", "TF", "SI")
_IDENTITY_SCHEMA = {
    "normalized_source_tree_sha256": str,
    "build_descriptor_sha256": str,
    "public_workload_set_sha256": str,
}
_SLOT_ROW_SCHEMA = {
    "slot_id": str,
    "controlled_subject_id": str,
    "semantic_contract_family": str,
    "slot_ordinal": int,
    "permitted_construction_mechanism": str,
}


def slot_id(
    controlled_subject_id: str,
    semantic_contract_family: str,
    slot_ordinal: int,
    permitted_construction_mechanism: str,
) -> str:
    validate_sha256(controlled_subject_id, "controlled_subject_id")
    if semantic_contract_family not in SEMANTIC_CONTRACT_FAMILIES:
        raise EvidenceError("E_SLOT_INVENTORY", "unknown semantic_contract_family")
    if slot_ordinal not in (0, 1):
        raise EvidenceError("E_SLOT_INVENTORY", "slot_ordinal must be 0 or 1")
    if permitted_construction_mechanism not in MECHANISM_ORDER:
        raise EvidenceError("E_SLOT_INVENTORY", "unknown permitted_construction_mechanism")
    return canonical_sha256(
        {
            "domain": "P3-SLOT-IDENTITY-v1",
            "controlled_subject_id": controlled_subject_id,
            "semantic_contract_family": semantic_contract_family,
            "slot_ordinal": slot_ordinal,
            "permitted_construction_mechanism": permitted_construction_mechanism,
        }
    )


def project_controlled_subject_ids(
    phase1_identity_records: Sequence[Mapping[str, object]],
) -> tuple[str, ...]:
    if not isinstance(phase1_identity_records, Sequence) or isinstance(
        phase1_identity_records, (str, bytes)
    ):
        raise EvidenceError("E_SUBJECT_IDENTITY", "identity records must be a sequence")
    if len(phase1_identity_records) != 35:
        raise EvidenceError("E_SUBJECT_IDENTITY", "identity projection requires 35 records")
    ids: list[str] = []
    seen: set[str] = set()
    for index, raw in enumerate(phase1_identity_records):
        try:
            record = validate_exact_object(dict(raw), _IDENTITY_SCHEMA, f"identity[{index}]")
        except EvidenceError as exc:
            raise EvidenceError("E_SUBJECT_IDENTITY", str(exc)) from exc
        tree = validate_sha256(record["normalized_source_tree_sha256"], "normalized_source_tree_sha256")
        build = validate_sha256(record["build_descriptor_sha256"], "build_descriptor_sha256")
        workload = validate_sha256(record["public_workload_set_sha256"], "public_workload_set_sha256")
        subject = canonical_sha256(
            {
                "normalized_source_tree_sha256": tree,
                "build_descriptor_sha256": build,
                "public_workload_set_sha256": workload,
                "domain": "P3-SUBJECT-v1",
            }
        )
        if subject in seen:
            raise EvidenceError("E_SUBJECT_IDENTITY", "duplicate controlled_subject_id")
        seen.add(subject)
        ids.append(subject)
    return tuple(sorted(ids))


def freeze_slot_inventory(
    controlled_subject_ids: Sequence[str],
) -> dict[str, object]:
    if not isinstance(controlled_subject_ids, Sequence) or isinstance(
        controlled_subject_ids, (str, bytes)
    ):
        raise EvidenceError("E_SLOT_INVENTORY", "controlled_subject_ids must be a sequence")
    validated: list[str] = []
    seen: set[str] = set()
    for index, raw in enumerate(controlled_subject_ids):
        subject_id = validate_sha256(raw, f"controlled_subject_ids[{index}]")
        if subject_id in seen:
            raise EvidenceError("E_SLOT_INVENTORY", "duplicate controlled_subject_id")
        seen.add(subject_id)
        validated.append(subject_id)
    if len(validated) != 35:
        raise EvidenceError("E_SLOT_INVENTORY", "inventory requires 35 subject IDs")
    validated.sort()
    rows: list[dict[str, Any]] = []
    for subject_index, subject in enumerate(validated):
        for family in SEMANTIC_CONTRACT_FAMILIES:
            for ordinal in (0, 1):
                mechanism = MECHANISM_ORDER[(subject_index + ordinal) % 5]
                row = {
                    "slot_id": slot_id(subject, family, ordinal, mechanism),
                    "controlled_subject_id": subject,
                    "semantic_contract_family": family,
                    "slot_ordinal": ordinal,
                    "permitted_construction_mechanism": mechanism,
                }
                validate_exact_object(row, _SLOT_ROW_SCHEMA, "slot")
                rows.append(row)
    rows.sort(
        key=lambda row: (
            row["controlled_subject_id"],
            SEMANTIC_CONTRACT_FAMILIES.index(row["semantic_contract_family"]),
            row["slot_ordinal"],
            MECHANISM_ORDER.index(row["permitted_construction_mechanism"]),
            row["slot_id"],
        )
    )
    if len(rows) != 350:
        raise EvidenceError("E_SLOT_INVENTORY", "inventory must contain 350 rows")
    body = {"schema_version": "p3-slot-inventory-v1", "slots": rows}
    return {**body, "artifact_sha256": canonical_sha256(body)}
```

Also add this identity-file helper in the same module. It is used in Task 3. It may read Phase-1 identity files, but it must copy only allowlisted fields and must not return snapshot IDs, project names, or workload rows.

```python
from pathlib import Path

from p3_v3.artifacts import read_canonical_json


def load_phase1_identity_records(
    *,
    verified_bridge_path: Path,
    workload_root: Path,
) -> tuple[dict[str, str], ...]:
    bridge = read_canonical_json(verified_bridge_path)
    records = bridge.get("records") if isinstance(bridge, Mapping) else None
    if not isinstance(records, list) or len(records) != 35:
        raise EvidenceError("E_SUBJECT_IDENTITY", "verified bridge must contain 35 records")
    narrowed: list[dict[str, str]] = []
    seen_neutrals: set[str] = set()
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            raise EvidenceError("E_SUBJECT_IDENTITY", f"bridge.records[{index}] must be an object")
        neutral = validate_sha256(raw.get("neutral_snapshot_id"), f"records[{index}].neutral_snapshot_id")
        if neutral in seen_neutrals:
            raise EvidenceError("E_SUBJECT_IDENTITY", "duplicate neutral_snapshot_id")
        seen_neutrals.add(neutral)
        workload = read_canonical_json(Path(workload_root) / f"profiling-workload-{neutral}.json")
        if not isinstance(workload, Mapping):
            raise EvidenceError("E_SUBJECT_IDENTITY", "workload artifact must be an object")
        narrowed.append(
            {
                "normalized_source_tree_sha256": raw["normalized_source_tree_sha256"],
                "build_descriptor_sha256": raw["build_descriptor_sha256"],
                "public_workload_set_sha256": workload["artifact_sha256"],
            }
        )
    return tuple(narrowed)
```

The helper uses `neutral_snapshot_id` only as a filename key. The returned tuples contain the three allowlist fields only.

- [ ] **Step 4: Run GREEN and the inventory-focused regressions**

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_applicability_authority.py -q
git diff --check
```

Expected: the seven Task 1 tests pass. `git diff --check` is silent.

- [ ] **Step 5: Commit**

```bash
git add src/p3_v3/slot_inventory.py tests/p3_v3/test_applicability_authority.py
git commit -m "feat(p3-v3): define cohort slot inventory"
```

Do not generate `data/p3_v3/phase2/slot-inventory.json` in this commit.

---

### Task 2: Pure applicability predicates and registry

**Files:**
- Create: `src/p3_v3/applicability_predicates.py`
- Modify: `tests/p3_v3/test_applicability_authority.py`
- Do not create: `data/p3_v3/protocol/applicability-predicate-registry.json`

**Consumes:** Task 1 inventory helpers; `canonical_sha256`, `file_sha256`, `read_canonical_json`, `write_canonical_json`, `validate_exact_object`, `validate_sha256`, `EvidenceError`; existing `select_first_applicable_site` and `close_slot`.
**Produces:** `symbol_tail`, `static_tokens`, `join_site_to_public_rows`, `attach_schema_kind`, `evaluate_predicate`, `build_predicate_registry`, `load_applicability_authority`, `close_slot_with_authority`, `materialize_applicability_authority`.

This module may import `Path` only for the loader and materializer. `symbol_tail`, `static_tokens`, `join_site_to_public_rows`, `attach_schema_kind`, and `evaluate_predicate` must not call the filesystem, environment, or network.

- [ ] **Step 1: Append the failing predicate and synthetic-selection tests**

Add these tests to `tests/p3_v3/test_applicability_authority.py`. Every path and symbol is synthetic.

```python
import ast
from pathlib import Path

from p3_v3.artifacts import file_sha256, write_canonical_json
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
from p3_v3.slot_inventory import freeze_slot_inventory, project_controlled_subject_ids


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
    attached_numeric = attach_schema_kind(public_api, [{"schema_kind": "NUMERIC_ARRAY_DOMAIN_V1", "raw_schema": schema}])
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
    assert evaluate_predicate("APPLICABILITY_CONV_V1", _site("pkg/bench.py", "bench.iterate", "d" * 64), [conv_row]) is True
    assert evaluate_predicate("APPLICABILITY_CONV_V1", _site("pkg/bench.py", "bench.converged", "e" * 64), [conv_row]) is False
    assert evaluate_predicate("APPLICABILITY_DYN_V1", _site("pkg/sim/run.py", "demo.main", "f" * 64), [dyn_row]) is True
    assert evaluate_predicate("APPLICABILITY_DYN_V1", _site("pkg/simulation/run.py", "demo.main", "0" * 64), [dyn_row]) is False
    assert evaluate_predicate("APPLICABILITY_CMP_V1", _site("pkg/cli.py", "cli.main", "1" * 64), [cmp_cli]) is True
    assert evaluate_predicate("APPLICABILITY_CMP_V1", _site("pkg/api.py", "api.public_fn", "2" * 64), [cmp_text]) is True
    empty_site = _site("pkg/none.py", "none.fn", "3" * 64)
    for predicate_id in PREDICATE_IDS:
        assert evaluate_predicate(predicate_id, empty_site, []) is False
        assert evaluate_predicate(predicate_id, inv_site, [{**public_api, "category": "PROJECT_TEST"}]) is False


def test_evaluate_predicate_fail_closed_and_has_no_subject_parameter():
    site = _site("pkg/api.py", "api.fn", "4" * 64)
    with pytest.raises(EvidenceError, match="E_APPLICABILITY_PREDICATE"):
        evaluate_predicate("APPLICABILITY_UNKNOWN_V1", site, [])
    with pytest.raises(EvidenceError, match="E_APPLICABILITY_PREDICATE"):
        evaluate_predicate("APPLICABILITY_INV_V1", {"symbol": "fn"}, [])
    signature = inspect.signature(evaluate_predicate)
    assert list(signature.parameters) == ["predicate_id", "site", "joined_public_rows"]
    import p3_v3.applicability_predicates as predicates_module
    for name in ("symbol_tail", "static_tokens", "join_site_to_public_rows", "evaluate_predicate"):
        source = inspect.getsource(getattr(predicates_module, name))
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in {"environ", "getenv"}:
                raise AssertionError(f"{name} reads the environment")
            if isinstance(node, ast.Name) and node.id in {"open", "Path", "os", "subprocess"}:
                raise AssertionError(f"{name} uses {node.id}")


def test_close_slot_with_authority_selects_first_or_not_applicable():
    ids = project_controlled_subject_ids(_identity_records())
    inventory = freeze_slot_inventory(ids)
    registry = build_predicate_registry("c" * 64)
    inv_row = next(
        row
        for row in inventory["slots"]
        if row["controlled_subject_id"] == ids[0] and row["semantic_contract_family"] == "CONV"
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
    closed = close_slot_with_authority(authority, inv_row, sites, {"rows": [], "public_schemas": []})
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
        if row["controlled_subject_id"] == ids[0] and row["semantic_contract_family"] == "INV"
    )
    other = close_slot_with_authority(authority, second, sites, pbf)
    assert other["state"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE"
    assert other["slot_id"] == second["slot_id"]
    assert applicable["slot_id"] == inv_row["slot_id"]
```

- [ ] **Step 2: Run RED**

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_applicability_authority.py -q
```

Expected: Task 1 tests still pass. New tests fail with `ImportError` for `p3_v3.applicability_predicates`.

- [ ] **Step 3: Implement the predicate module, including loader and materializer**

Create `src/p3_v3/applicability_predicates.py`. Implement the helpers first, then the five predicates, then registry/loader/materializer in the same file so Task 3 does not edit this file again.

```python
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
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
from p3_v3.bridge_and_frames import close_slot, select_first_applicable_site
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
    "INV": 'Return true if and only if at least one joined row has category == "PUBLIC_API" and schema_kind in {"NUMERIC_ARRAY_DOMAIN_V1", "JSON_SCHEMA_DRAFT2020_12_V1"}.',
    "MONO": 'Return true if and only if at least one joined row has category == "PUBLIC_API" and schema_kind == "NUMERIC_ARRAY_DOMAIN_V1".',
    "CONV": 'Return true if and only if at least one joined row has category in {"BENCHMARK", "EXAMPLE"} and the site-symbol token set intersects {"iterate", "step", "solve", "minimize", "converge"}.',
    "DYN": 'Return true if and only if at least one joined row has category in {"EXAMPLE", "PROJECT_TEST"} and the site-path token set intersects {"sim", "traj", "dyn", "evolve", "integrate"}.',
    "CMP": 'Return true if and only if at least one joined row has category == "CLI" or schema_kind in {"TEXT_IO_SCHEMA_V1", "CLI_TOKEN_GRAMMAR_V1"}.',
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
    if not isinstance(site, Mapping) or type(site.get("path")) is not str or type(site.get("symbol")) is not str:
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
    if not isinstance(site, Mapping) or type(site.get("path")) is not str or type(site.get("symbol")) is not str:
        raise EvidenceError("E_APPLICABILITY_PREDICATE", "site path and symbol are required")
    rows = [dict(row) for row in joined_public_rows if isinstance(row, Mapping)]
    if predicate_id == "APPLICABILITY_INV_V1":
        result = any(
            row.get("category") == "PUBLIC_API" and row.get("schema_kind") in _INV_KINDS
            for row in rows
        )
    elif predicate_id == "APPLICABILITY_MONO_V1":
        result = any(
            row.get("category") == "PUBLIC_API" and row.get("schema_kind") == "NUMERIC_ARRAY_DOMAIN_V1"
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
```

Then add `load_applicability_authority`, `close_slot_with_authority`, and `materialize_applicability_authority` in the same file:

```python
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
    registry = _self_hash(read_canonical_json(registry_path), "E_APPLICABILITY_AUTHORITY", "registry")
    inventory = _self_hash(read_canonical_json(inventory_path), "E_APPLICABILITY_AUTHORITY", "inventory")
    ids = tuple(manifest["subject_identity_projection"])
    if ids != tuple(sorted(ids)) or len(ids) != 35:
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "subject projection must be 35 sorted IDs")
    for index, item in enumerate(ids):
        validate_sha256(item, f"subject_identity_projection[{index}]")
    if canonical_sha256(list(ids)) != manifest["subject_identity_projection_sha256"]:
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "subject projection hash differs")
    rebuilt_inventory = freeze_slot_inventory(ids)
    rebuilt_registry = build_predicate_registry(file_sha256(predicate_implementation_path))
    if rebuilt_inventory != inventory:
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "slot inventory bytes differ from rebuild")
    if rebuilt_registry != registry:
        raise EvidenceError("E_APPLICABILITY_AUTHORITY", "predicate registry bytes differ from rebuild")
    repo_root = Path(__file__).resolve().parents[2]
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
    family = inventory_row.get("semantic_contract_family")
    predicate_id = FAMILY_TO_PREDICATE_ID.get(family)
    if predicate_id is None:
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
            attach_schema_kind(row, schemas)
            for row in join_site_to_public_rows(site, rows)
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
```

The loader hashes the caller-supplied slot and predicate implementation paths. It hashes `artifacts.py` beside this module and the two protocol markdown files from the repository root. It does not add a sixth production file.

- [ ] **Step 4: Add in-memory authority binding tests that do not write official JSON**

```python
def test_load_applicability_authority_accepts_tmp_bindings_and_rejects_byte_drift(tmp_path):
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
```

The tmp-file loader test uses copies of the two implementation files so Task 3 can later bind the real paths. If `load_applicability_authority` always hashes `src/p3_v3/applicability_predicates.py` rather than `predicate_implementation_path`, this test cannot pass. The implementation above hashes the passed implementation paths and must keep doing so.

- [ ] **Step 5: Run GREEN and the focused selection regressions**

```bash
PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_applicability_authority.py \
  tests/p3_v3/test_bridge_and_frames.py::test_slot_selects_first_applicable_canonical_site_or_none \
  tests/p3_v3/test_bridge_and_frames.py::test_close_slot_two_paths_not_applicable_or_site_frozen \
  -q
git diff --check
```

Expected: all selected tests pass. `git diff --check` is silent.

- [ ] **Step 6: Commit**

```bash
git add src/p3_v3/applicability_predicates.py tests/p3_v3/test_applicability_authority.py
git commit -m "feat(p3-v3): define static applicability predicates"
```

Do not write official registry/inventory/manifest files. After this commit, do not edit the two Python implementation files again unless a focused test proves they are wrong. A later edit forces a new authority version.

---

### Task 3: Generate and bind authority artifacts

**Files:**
- Generate: `data/p3_v3/protocol/applicability-predicate-registry.json`
- Generate: `data/p3_v3/phase2/slot-inventory.json`
- Generate: `data/p3_v3/phase2/applicability-authority.json`
- Test: `tests/p3_v3/test_applicability_authority.py`
- Do not modify `src/p3_v3/slot_inventory.py` or `src/p3_v3/applicability_predicates.py` unless a Task 2 test is red. If either file changes after the official manifest is written, delete the three JSON files and regenerate them in this same task; do not leave a stale binding.

**Consumes:** stable Task 1/2 sources; `verified_bridge.json` identity fields; each `profiling-workload-*.json` `artifact_sha256` only.
**Produces:** the three official artifacts and loader tests against those files.

- [ ] **Step 1: Write official-artifact tests before generating the files**

```python
from p3_v3.artifacts import file_sha256, read_canonical_json
from p3_v3.applicability_predicates import load_applicability_authority

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
```

- [ ] **Step 2: Run RED**

```bash
PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_applicability_authority.py::test_official_authority_artifacts_bind_and_count \
  tests/p3_v3/test_applicability_authority.py::test_official_authority_rejects_implementation_or_inventory_byte_change \
  -q
```

Expected: both tests fail because the three official JSON files are absent.

- [ ] **Step 3: Materialize the three official files from identity-only inputs**

Run this exact command and no other generation command. It must print only counts, never subject IDs, snapshot IDs, paths, or symbols.

```bash
PYTHONPATH=src python3 - <<'PY'
from pathlib import Path
from collections import Counter
from p3_v3.applicability_predicates import materialize_applicability_authority
from p3_v3.slot_inventory import SEMANTIC_CONTRACT_FAMILIES

root = Path('.')
loaded = materialize_applicability_authority(
    verified_bridge_path=root / 'data/p3_v3/p12_intake/verified_bridge.json',
    workload_root=root / 'data/p3_v3/phase1_frames/out',
    site_policy_path=root / 'data/p3_v3/protocol/site_policy.md',
    operator_catalogue_path=root / 'data/p3_v3/protocol/operator_catalogue.md',
    slot_implementation_path=root / 'src/p3_v3/slot_inventory.py',
    predicate_implementation_path=root / 'src/p3_v3/applicability_predicates.py',
    canonicalization_implementation_path=root / 'src/p3_v3/artifacts.py',
    registry_path=root / 'data/p3_v3/protocol/applicability-predicate-registry.json',
    inventory_path=root / 'data/p3_v3/phase2/slot-inventory.json',
    manifest_path=root / 'data/p3_v3/phase2/applicability-authority.json',
)
slots = loaded['inventory']['slots']
print({
    'subjects': len(loaded['controlled_subject_ids']),
    'slots': len(slots),
    'per_subject': sorted(set(Counter(row['controlled_subject_id'] for row in slots).values())),
    'per_family': dict(Counter(row['semantic_contract_family'] for row in slots)),
    'per_cell': sorted(set(Counter((row['semantic_contract_family'], row['permitted_construction_mechanism']) for row in slots).values())),
})
PY
```

Expected stdout:

```text
{'subjects': 35, 'slots': 350, 'per_subject': [10], 'per_family': {'CMP': 70, 'CONV': 70, 'DYN': 70, 'INV': 70, 'MONO': 70}, 'per_cell': [14]}
```

Then validate canonical self-hashes:

```bash
PYTHONPATH=src python3 - <<'PY'
from pathlib import Path
from p3_v3.artifacts import canonical_sha256, read_canonical_json

for path in (
    Path('data/p3_v3/protocol/applicability-predicate-registry.json'),
    Path('data/p3_v3/phase2/slot-inventory.json'),
    Path('data/p3_v3/phase2/applicability-authority.json'),
):
    value = read_canonical_json(path)
    body = {key: item for key, item in value.items() if key != 'artifact_sha256'}
    assert value['artifact_sha256'] == canonical_sha256(body), path
    print(path, 'PASS', value['artifact_sha256'])
PY
```

Expected: three `PASS` lines. Do not open PBF files or subject source while generating.

- [ ] **Step 4: Run GREEN**

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_applicability_authority.py -q
git diff --check
```

Expected: all authority tests pass, including official binding and byte-drift failure. `git diff --check` is silent.

- [ ] **Step 5: Commit**

```bash
git add \
  data/p3_v3/protocol/applicability-predicate-registry.json \
  data/p3_v3/phase2/slot-inventory.json \
  data/p3_v3/phase2/applicability-authority.json \
  tests/p3_v3/test_applicability_authority.py
git commit -m "feat(p3-v3): freeze applicability authority artifacts"
```

Do not edit the two Python sources after this commit.

---

### Task 4: Integrate the single consumer seam

**Files:**
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_cli.py`
- Modify only if a CLI test needs a library assertion: `tests/p3_v3/test_applicability_authority.py`
- Do not modify: `src/p3_v3/bridge_and_frames.py`, contract builders, the claim ledger, or Phase-1 artifacts.

**Consumes:** `load_applicability_authority`.
**Produces:** CLI command `validate-applicability-authority`; `build-frames` keeps empty-slot fixtures and refuses handwritten non-empty applicability maps and confirmatory slot closure.

`bridge_and_frames.py` stays unmodified because `close_slot` / `select_first_applicable_site` already accept a callback, and the approved design says the wrapper passes the two-field subset rather than widening `_SLOT_SCHEMA`.

- [ ] **Step 1: Write the failing CLI tests**

In `tests/p3_v3/test_cli.py`, add `"validate-applicability-authority"` to `COMMANDS` and add:

```python
def test_validate_applicability_authority_passes_official_bindings():
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "validate-applicability-authority",
            "--manifest",
            str(ROOT / "data/p3_v3/phase2/applicability-authority.json"),
            "--registry",
            str(ROOT / "data/p3_v3/protocol/applicability-predicate-registry.json"),
            "--inventory",
            str(ROOT / "data/p3_v3/phase2/slot-inventory.json"),
            "--slot-implementation",
            str(ROOT / "src/p3_v3/slot_inventory.py"),
            "--predicate-implementation",
            str(ROOT / "src/p3_v3/applicability_predicates.py"),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["subject_count"] == 35
    assert payload["slot_count"] == 350
    assert "site_id" not in payload


def test_validate_applicability_authority_fails_on_bound_byte_change(tmp_path):
    drifted = tmp_path / "applicability_predicates.py"
    drifted.write_bytes(
        (ROOT / "src/p3_v3/applicability_predicates.py").read_bytes() + b"#drift\n"
    )
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "validate-applicability-authority",
            "--manifest",
            str(ROOT / "data/p3_v3/phase2/applicability-authority.json"),
            "--registry",
            str(ROOT / "data/p3_v3/protocol/applicability-predicate-registry.json"),
            "--inventory",
            str(ROOT / "data/p3_v3/phase2/slot-inventory.json"),
            "--slot-implementation",
            str(ROOT / "src/p3_v3/slot_inventory.py"),
            "--predicate-implementation",
            str(drifted),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_APPLICABILITY_AUTHORITY"


def test_build_frames_rejects_nonempty_handwritten_applicability_map(tmp_path):
    paths = {
        "bridge": tmp_path / "bridge.json",
        "specs": tmp_path / "subject-specs.json",
        "slots": tmp_path / "slots.json",
        "contracts": tmp_path / "contracts.json",
        "applicability": tmp_path / "applicability.json",
    }
    write_canonical_json(paths["bridge"], {"records": []}, exclusive=True)
    write_canonical_json(paths["specs"], [], exclusive=True)
    write_canonical_json(paths["slots"], [], exclusive=True)
    write_canonical_json(paths["contracts"], {}, exclusive=True)
    write_canonical_json(paths["applicability"], {"a" * 64: True}, exclusive=True)
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "build-frames",
            "--bridge",
            str(paths["bridge"]),
            "--subject-specs",
            str(paths["specs"]),
            "--adapter-root",
            str(tmp_path),
            "--generator-root",
            str(tmp_path),
            "--slots",
            str(paths["slots"]),
            "--contracts",
            str(paths["contracts"]),
            "--applicability-map",
            str(paths["applicability"]),
            "--output-root",
            str(tmp_path / "out"),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_APPLICABILITY"


def test_build_frames_rejects_nonempty_slots_without_running_closure(tmp_path):
    output_root = tmp_path / "out"
    paths = {
        "bridge": tmp_path / "bridge.json",
        "specs": tmp_path / "subject-specs.json",
        "slots": tmp_path / "slots.json",
        "contracts": tmp_path / "contracts.json",
        "applicability": tmp_path / "applicability.json",
    }
    write_canonical_json(paths["bridge"], {"records": []}, exclusive=True)
    write_canonical_json(paths["specs"], [], exclusive=True)
    write_canonical_json(
        paths["slots"],
        [{"slot_id": "a" * 64, "controlled_subject_id": "b" * 64}],
        exclusive=True,
    )
    write_canonical_json(paths["contracts"], {}, exclusive=True)
    write_canonical_json(paths["applicability"], {}, exclusive=True)
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "build-frames",
            "--bridge",
            str(paths["bridge"]),
            "--subject-specs",
            str(paths["specs"]),
            "--adapter-root",
            str(tmp_path),
            "--generator-root",
            str(tmp_path),
            "--slots",
            str(paths["slots"]),
            "--contracts",
            str(paths["contracts"]),
            "--applicability-map",
            str(paths["applicability"]),
            "--output-root",
            str(output_root),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SLOTS"
    assert not output_root.exists() or not any(output_root.glob("slot-closure-*.json"))
```

Existing empty `[]` / `{}` build-frames tests must remain unchanged.

- [ ] **Step 2: Run RED**

```bash
PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_cli.py::test_cli_help_lists_only_frozen_commands \
  tests/p3_v3/test_cli.py::test_validate_applicability_authority_passes_official_bindings \
  tests/p3_v3/test_cli.py::test_validate_applicability_authority_fails_on_bound_byte_change \
  tests/p3_v3/test_cli.py::test_build_frames_rejects_nonempty_handwritten_applicability_map \
  tests/p3_v3/test_cli.py::test_build_frames_rejects_nonempty_slots_without_running_closure \
  -q
```

Expected:
- `test_cli_help_lists_only_frozen_commands` fails because the CLI help set does not yet include `validate-applicability-authority`.
- The two validate tests fail with argparse / unsupported-command errors.
- The handwritten-map test fails because `build-frames` still accepts a non-empty map.
- The nonempty-slots test fails because `build-frames` still attempts closure.

- [ ] **Step 3: Implement the CLI seam only**

In `scripts/p3_v3/evidence.py`:

1. Import `load_applicability_authority` from `p3_v3.applicability_predicates`.
2. Add parser:

```python
command = sub.add_parser("validate-applicability-authority")
command.add_argument("--manifest", required=True)
command.add_argument("--registry", required=True)
command.add_argument("--inventory", required=True)
command.add_argument("--slot-implementation", required=True)
command.add_argument("--predicate-implementation", required=True)
```

3. In `dispatch`:

```python
if args.command == "validate-applicability-authority":
    loaded = load_applicability_authority(
        manifest_path=Path(args.manifest),
        registry_path=Path(args.registry),
        inventory_path=Path(args.inventory),
        slot_implementation_path=Path(args.slot_implementation),
        predicate_implementation_path=Path(args.predicate_implementation),
    )
    return {
        "status": "PASS",
        "authority_id": loaded["manifest"]["authority_id"],
        "subject_count": len(loaded["controlled_subject_ids"]),
        "slot_count": len(loaded["inventory"]["slots"]),
        "manifest_sha256": loaded["manifest"]["artifact_sha256"],
    }
```

4. At the start of `_dispatch_build_frames`, before reading the bridge or deriving subjects, add:

```python
slots = read_canonical_json(args.slots)
contracts = read_canonical_json(args.contracts)
applicability_map = read_canonical_json(args.applicability_map)
if not isinstance(slots, list):
    raise EvidenceError("E_SLOTS", "slots must be a list")
if not isinstance(contracts, Mapping):
    raise EvidenceError("E_CONTRACTS", "contracts must be an object")
if not isinstance(applicability_map, Mapping):
    raise EvidenceError("E_APPLICABILITY", "applicability-map must be an object")
if applicability_map:
    raise EvidenceError(
        "E_APPLICABILITY",
        "handwritten applicability-map is forbidden; validate frozen authority",
    )
if slots:
    raise EvidenceError(
        "E_SLOTS",
        "build-frames does not close confirmatory slots; use validate-applicability-authority",
    )
```

Keep the later empty-list loop as it is today. Remove the second `read_canonical_json` of those three files so they are read once. Empty `[]` / `{}` still proceeds into the existing frame-derivation path. Do not call `close_slot` or `close_slot_with_authority` from the CLI in this task. Do not add a site-selection subcommand.

- [ ] **Step 4: Run GREEN and the focused CLI / closure regressions**

```bash
PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_applicability_authority.py \
  tests/p3_v3/test_cli.py::test_cli_help_lists_only_frozen_commands \
  tests/p3_v3/test_cli.py::test_validate_applicability_authority_passes_official_bindings \
  tests/p3_v3/test_cli.py::test_validate_applicability_authority_fails_on_bound_byte_change \
  tests/p3_v3/test_cli.py::test_build_frames_rejects_nonempty_handwritten_applicability_map \
  tests/p3_v3/test_cli.py::test_build_frames_rejects_nonempty_slots_without_running_closure \
  tests/p3_v3/test_cli.py::test_build_frames_subject_specs_are_the_only_subject_authority_options \
  tests/p3_v3/test_bridge_and_frames.py::test_slot_selects_first_applicable_canonical_site_or_none \
  tests/p3_v3/test_bridge_and_frames.py::test_close_slot_two_paths_not_applicable_or_site_frozen \
  tests/p3_v3/test_artifacts.py::test_canonical_file_has_sorted_keys_and_one_terminal_lf \
  tests/p3_v3/test_artifacts.py::test_reader_rejects_noncanonical_json_bytes \
  -q
git diff --check
```

Expected: all listed tests pass. Empty `--slots []` and `--applicability-map {}` behavior is unchanged. No `slot-closure-*.json` is written. `git diff --check` is silent.

- [ ] **Step 5: Commit**

```bash
git add scripts/p3_v3/evidence.py tests/p3_v3/test_cli.py
git commit -m "feat(p3-v3): require frozen applicability authority"
```

---

## Stop conditions

Implementation is complete when the four tasks have produced one loader, one registry, one 350-row inventory, and one authority manifest, and the focused tests above are green.

That result is engineering authority only. It is not C3 experimental data. After those artifacts and tests, stop.

Do not:

- open any real PBF site row, archive, or subject source file;
- run first-applicable on confirmatory subjects;
- write production `SITE_FROZEN` closures;
- create contracts, `E_CONTRACT`, patches, or mutants;
- edit `research/evidence/p3_claim_ledger_v1.3.0.yml`.

C3 remains `blocked` with upgrade condition `RQ2 paired evidence and uncertainty accounting complete`.

If an approved design rule contradicts the existing Phase-0 scientific authority or cannot be expressed with static site/PBF inputs, stop and return to design review. Do not change the scientific rule in code.

The next independent task after this implementation is finished is:

`P3_C3_SELECTED_SUBJECT_SITE_SELECTION_RECOVERY`

This plan itself is executed by:

`P3_C3_APPLICABILITY_PREDICATE_AUTHORITY_IMPLEMENTATION`

---

## Final focused verification

After Task 4, run only:

```bash
PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_applicability_authority.py \
  tests/p3_v3/test_cli.py::test_cli_help_lists_only_frozen_commands \
  tests/p3_v3/test_cli.py::test_validate_applicability_authority_passes_official_bindings \
  tests/p3_v3/test_cli.py::test_validate_applicability_authority_fails_on_bound_byte_change \
  tests/p3_v3/test_cli.py::test_build_frames_rejects_nonempty_handwritten_applicability_map \
  tests/p3_v3/test_cli.py::test_build_frames_rejects_nonempty_slots_without_running_closure \
  tests/p3_v3/test_cli.py::test_build_frames_subject_specs_are_the_only_subject_authority_options \
  tests/p3_v3/test_bridge_and_frames.py::test_slot_selects_first_applicable_canonical_site_or_none \
  tests/p3_v3/test_bridge_and_frames.py::test_close_slot_two_paths_not_applicable_or_site_frozen \
  tests/p3_v3/test_artifacts.py::test_canonical_file_has_sorted_keys_and_one_terminal_lf \
  tests/p3_v3/test_artifacts.py::test_reader_rejects_noncanonical_json_bytes \
  -q

PYTHONPATH=src python3 - <<'PY'
from collections import Counter
from pathlib import Path
from p3_v3.applicability_predicates import load_applicability_authority
from p3_v3.artifacts import canonical_sha256, read_canonical_json
from p3_v3.slot_inventory import SEMANTIC_CONTRACT_FAMILIES

root = Path('.')
for rel in (
    'data/p3_v3/protocol/applicability-predicate-registry.json',
    'data/p3_v3/phase2/slot-inventory.json',
    'data/p3_v3/phase2/applicability-authority.json',
):
    value = read_canonical_json(root / rel)
    body = {key: item for key, item in value.items() if key != 'artifact_sha256'}
    assert value['artifact_sha256'] == canonical_sha256(body)

loaded = load_applicability_authority(
    manifest_path=root / 'data/p3_v3/phase2/applicability-authority.json',
    registry_path=root / 'data/p3_v3/protocol/applicability-predicate-registry.json',
    inventory_path=root / 'data/p3_v3/phase2/slot-inventory.json',
    slot_implementation_path=root / 'src/p3_v3/slot_inventory.py',
    predicate_implementation_path=root / 'src/p3_v3/applicability_predicates.py',
)
slots = loaded['inventory']['slots']
assert len(loaded['controlled_subject_ids']) == 35
assert len(slots) == 350
assert set(Counter(row['controlled_subject_id'] for row in slots).values()) == {10}
assert Counter(row['semantic_contract_family'] for row in slots) == {
    family: 70 for family in SEMANTIC_CONTRACT_FAMILIES
}
assert set(
    Counter(
        (row['semantic_contract_family'], row['permitted_construction_mechanism'])
        for row in slots
    ).values()
) == {14}
print('AUTHORITY_COUNTS_PASS')
PY

git diff --check
```

Expected: pytest focused selection is green, `AUTHORITY_COUNTS_PASS`, and `git diff --check` is silent.

Do not run `pytest tests/` or any subject/profiling/mutation command.

---

## File map

| Path | Task | Role |
|---|---|---|
| `src/p3_v3/slot_inventory.py` | 1 | Identity projection and 350-slot generation |
| `src/p3_v3/applicability_predicates.py` | 2 | Predicates, registry, unique loader, materializer |
| `tests/p3_v3/test_applicability_authority.py` | 1–3 | Focused authority tests |
| `data/p3_v3/phase2/slot-inventory.json` | 3 | Official 350-row inventory |
| `data/p3_v3/protocol/applicability-predicate-registry.json` | 3 | Official five-predicate registry |
| `data/p3_v3/phase2/applicability-authority.json` | 3 | Unique authority manifest |
| `scripts/p3_v3/evidence.py` | 4 | Validate-only consumer seam |
| `tests/p3_v3/test_cli.py` | 4 | CLI validation and empty-fixture compatibility |

No sixth production module. No second manifest. No new schema file. No claim-ledger edit.

## Design-to-task map

| Design requirement | Task |
|---|---|
| 35-subject identity allowlist and sort | 1 |
| 350 / 10 / 70 / 14 mathematics and `slot_id` | 1 |
| Exact join, tail, tokens, `schema_kind` attachment | 2 |
| Five predicates and registry rows | 2 |
| Unique loader and `close_slot` two-field wrapper | 2 |
| Official JSON generation after source SHA freeze | 3 |
| Authority byte-binding proof tests | 3 |
| CLI validation without site-selection run | 4 |
| Empty slots/applicability fixture compatibility | 4 |
| C3 remains `blocked` | all tasks |

This plan does not execute `P3_C3_APPLICABILITY_PREDICATE_AUTHORITY_IMPLEMENTATION`.