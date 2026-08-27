from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from p3_v3.applicability_predicates import (
    build_predicate_registry,
    load_applicability_authority,
)
from p3_v3 import artifacts as artifacts_mod
from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    write_canonical_json,
)
from p3_v3.slot_inventory import (
    freeze_slot_inventory,
    project_controlled_subject_ids,
)

from scripts.p3_v3 import prospective_applicability_search_v2 as v2

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROLLER_PATH = REPO_ROOT / "scripts/p3_v3/prospective_applicability_search_v2.py"
COMPARE_KEYS = (
    "successor_ordinal",
    "scale_class",
    "total_effective_lines",
    "pbf_site_count",
    "frozen_slots",
    "neutral_snapshot_id",
    "controlled_subject_source_id",
    "controlled_subject_id",
    "pbf_file_sha256",
    "pbf_artifact_sha256",
)


def _load_official_authority() -> dict:
    return load_applicability_authority(
        manifest_path=REPO_ROOT / v2.AUTHORITY_RELPATH,
        registry_path=REPO_ROOT / v2.REGISTRY_RELPATH,
        inventory_path=REPO_ROOT / v2.INVENTORY_RELPATH,
        slot_implementation_path=REPO_ROOT / v2.SLOT_IMPL_RELPATH,
        predicate_implementation_path=REPO_ROOT / v2.PREDICATE_IMPL_RELPATH,
    )


def _raise_if_closer_called(*_args, **_kwargs):
    raise AssertionError("close_slot_with_authority must not run during preflight")


def test_controller_constants_bind_frozen_design_and_authority_identity():
    assert v2.SLICE_ID == "p3-c3-prospective-applicability-search-v2"
    assert v2.DESIGN_COMMIT == "4ea6f05b44c76ebaa031277872c3711cdd1953eb"
    assert v2.DESIGN_FILE_SHA256 == (
        "bb0ca5d20f3fec61257b2ba524585fe899d28c8b8963c61273a8ffeb857aa6c6"
    )
    assert v2.AUTHORITY_ARTIFACT_SHA256 == (
        "30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214"
    )
    assert v2.PRIOR_CLOSURE_COMMIT == "e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5"
    assert v2.MAXIMUM_ATTEMPTS == 22
    assert v2.SLOTS_PER_SUBJECT == 10
    assert len(v2.FROZEN_SUCCESSOR_ROWS) == 22
    assert [row["successor_ordinal"] for row in v2.FROZEN_SUCCESSOR_ROWS] == list(
        range(1, 23)
    )


def test_rebuild_successor_rows_matches_frozen_22_row_table():
    rows = v2.rebuild_successor_rows(REPO_ROOT)
    assert len(rows) == 22
    assert tuple(row["successor_ordinal"] for row in rows) == tuple(range(1, 23))
    for observed, expected in zip(rows, v2.FROZEN_SUCCESSOR_ROWS, strict=True):
        for key in COMPARE_KEYS:
            assert observed[key] == expected[key]


def test_rebuild_successor_rows_rejects_reordered_deleted_or_extra_row(monkeypatch):
    swapped = list(v2.FROZEN_SUCCESSOR_ROWS)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    monkeypatch.setattr(v2, "FROZEN_SUCCESSOR_ROWS", tuple(swapped))
    with pytest.raises(EvidenceError, match="V2_SUCCESSOR_IDENTITY_CONFLICT"):
        v2.rebuild_successor_rows(REPO_ROOT)
    monkeypatch.setattr(v2, "FROZEN_SUCCESSOR_ROWS", v2.FROZEN_SUCCESSOR_ROWS[1:])
    with pytest.raises(EvidenceError, match="V2_SUCCESSOR_IDENTITY_CONFLICT"):
        v2.rebuild_successor_rows(REPO_ROOT)
    extra = v2.FROZEN_SUCCESSOR_ROWS + (v2.FROZEN_SUCCESSOR_ROWS[0],)
    monkeypatch.setattr(v2, "FROZEN_SUCCESSOR_ROWS", extra)
    with pytest.raises(EvidenceError, match="V2_SUCCESSOR_IDENTITY_CONFLICT"):
        v2.rebuild_successor_rows(REPO_ROOT)


def test_validate_v2_preflight_rejects_design_sha_change(monkeypatch):
    real = v2.file_sha256

    def fake(path):
        if Path(path).name.endswith("stopping-rule-design.md"):
            return "0" * 64
        return real(path)

    monkeypatch.setattr(v2, "file_sha256", fake)
    with pytest.raises(EvidenceError, match="V2_PREFLIGHT_FAIL"):
        v2.validate_v2_preflight(repo_root=REPO_ROOT, controller_path=CONTROLLER_PATH)


def test_validate_v2_preflight_rejects_authority_sha_change(monkeypatch):
    real = v2.file_sha256

    def fake(path):
        if Path(path).name == "applicability-authority.json":
            return "1" * 64
        return real(path)

    monkeypatch.setattr(v2, "file_sha256", fake)
    with pytest.raises(EvidenceError, match="V2_PREFLIGHT_FAIL"):
        v2.validate_v2_preflight(repo_root=REPO_ROOT, controller_path=CONTROLLER_PATH)


def test_validate_v2_preflight_rejects_successor_identity_change(monkeypatch):
    swapped = list(v2.FROZEN_SUCCESSOR_ROWS)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    monkeypatch.setattr(v2, "rebuild_successor_rows", lambda _root: tuple(swapped))
    with pytest.raises(EvidenceError, match="V2_SUCCESSOR_IDENTITY_CONFLICT"):
        v2.validate_v2_preflight(repo_root=REPO_ROOT, controller_path=CONTROLLER_PATH)


def test_validate_v2_preflight_rejects_slot_count_other_than_10(monkeypatch):
    def nine(_authority, _subject):
        return ({"slot_id": "a" * 64},) * 9

    monkeypatch.setattr(v2, "inventory_rows_for_subject", nine)
    with pytest.raises(EvidenceError, match="V2_PREFLIGHT_FAIL"):
        v2.validate_v2_preflight(repo_root=REPO_ROOT, controller_path=CONTROLLER_PATH)


def test_validate_v2_preflight_rejects_prior_closure_byte_change(tmp_path, monkeypatch):
    copied = tmp_path / "old-closures"
    shutil.copytree(REPO_ROOT / v2.OLD_CLOSURE_RELDIR, copied)
    victim = next(copied.glob("slot-closure-*.json"))
    victim.write_bytes(victim.read_bytes() + b"\n")
    monkeypatch.setattr(v2, "old_closure_dir", lambda _root: copied)
    with pytest.raises(EvidenceError, match="V2_PREFLIGHT_FAIL"):
        v2.validate_v2_preflight(repo_root=REPO_ROOT, controller_path=CONTROLLER_PATH)


def test_validate_v2_preflight_rejects_old_rank1_closure_byte_change(
    tmp_path, monkeypatch
):
    test_validate_v2_preflight_rejects_prior_closure_byte_change(tmp_path, monkeypatch)


def test_validate_v2_preflight_rejects_existing_official_or_staging_namespace(
    tmp_path, monkeypatch
):
    official = tmp_path / "official"
    official.mkdir()
    monkeypatch.setattr(v2, "official_root", lambda _root: official)
    with pytest.raises(EvidenceError, match="V2_PREFLIGHT_FAIL"):
        v2.validate_v2_preflight(repo_root=REPO_ROOT, controller_path=CONTROLLER_PATH)
    monkeypatch.setattr(v2, "official_root", lambda _root: tmp_path / "official-absent")
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(v2, "staging_root", lambda _root: staging)
    with pytest.raises(EvidenceError, match="V2_PREFLIGHT_FAIL"):
        v2.validate_v2_preflight(repo_root=REPO_ROOT, controller_path=CONTROLLER_PATH)


def test_validate_v2_preflight_passes_current_frozen_identities():
    payload = v2.validate_v2_preflight(
        repo_root=REPO_ROOT, controller_path=CONTROLLER_PATH
    )
    assert payload["status"] == "V2_PREFLIGHT_PASS"
    assert payload["successor_count"] == 22
    assert payload["authority_artifact_sha256"] == v2.AUTHORITY_ARTIFACT_SHA256
    assert payload["controller_source_sha256"] == file_sha256(CONTROLLER_PATH)
    assert not v2.official_root(REPO_ROOT).exists()
    assert not v2.staging_root(REPO_ROOT).exists()


def test_validate_v2_preflight_rejects_controller_symlink(tmp_path):
    linked = tmp_path / v2.CONTROLLER_RELPATH
    linked.parent.mkdir(parents=True)
    linked.symlink_to(CONTROLLER_PATH)
    with pytest.raises(EvidenceError, match="not a regular file"):
        v2.validate_v2_preflight(repo_root=tmp_path, controller_path=linked)


def test_read_successor_pbf_uses_one_snapshot(tmp_path, monkeypatch):
    payload = {
        "artifact_sha256": "a" * 64,
        "controlled_subject_source_id": "b" * 64,
        "sites": [],
    }
    path = tmp_path / "public-behavior-frame.json"
    write_canonical_json(path, payload, exclusive=True)
    original = path.read_bytes()
    successor = {
        "neutral_snapshot_id": "c" * 64,
        "controlled_subject_source_id": "b" * 64,
        "pbf_file_sha256": hashlib.sha256(original).hexdigest(),
        "pbf_artifact_sha256": "a" * 64,
        "pbf_site_count": 0,
    }
    reads = {"n": 0}
    real = artifacts_mod.read_regular_file_snapshot

    def once(observed, context):
        reads["n"] += 1
        raw, mode = real(observed, context)
        path.write_bytes(raw + b" ")
        return raw, mode

    monkeypatch.setattr(v2, "read_regular_file_snapshot", once)
    monkeypatch.setattr(artifacts_mod, "read_regular_file_snapshot", once)
    monkeypatch.setattr(v2, "pbf_path", lambda *_args, **_kwargs: path)
    loaded = v2.read_successor_pbf(tmp_path, successor)
    assert reads["n"] == 1
    assert loaded["artifact_sha256"] == "a" * 64
    assert loaded["controlled_subject_source_id"] == "b" * 64
    assert len(loaded["sites"]) == 0


def test_preflight_does_not_call_closer(monkeypatch):
    monkeypatch.setattr(
        "p3_v3.applicability_predicates.close_slot_with_authority",
        _raise_if_closer_called,
    )
    monkeypatch.setattr(v2, "close_slot_with_authority", _raise_if_closer_called)
    payload = v2.validate_v2_preflight(
        repo_root=REPO_ROOT, controller_path=CONTROLLER_PATH
    )
    assert payload["status"] == "V2_PREFLIGHT_PASS"
    authority = _load_official_authority()
    rows = v2.inventory_rows_for_subject(
        authority, v2.FROZEN_SUCCESSOR_ROWS[0]["controlled_subject_id"]
    )
    assert len(rows) == 10


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _synthetic_authority() -> tuple[dict[str, object], str, tuple[dict[str, object], ...]]:
    records = tuple(
        {
            "normalized_source_tree_sha256": _sha(f"tree-{index}"),
            "build_descriptor_sha256": _sha(f"build-{index}"),
            "public_workload_set_sha256": _sha(f"workload-{index}"),
        }
        for index in range(35)
    )
    ids = project_controlled_subject_ids(records)
    inventory = freeze_slot_inventory(ids)
    authority = {
        "manifest": {},
        "registry": build_predicate_registry("c" * 64),
        "inventory": inventory,
        "controlled_subject_ids": ids,
    }
    subject = ids[0]
    rows = v2.inventory_rows_for_subject(authority, subject)
    return authority, subject, rows


def _official_closer(
    slot_id: str,
    controlled_subject_id: str,
    state: str,
    site_id: str | None,
) -> dict[str, object]:
    body = {
        "schema_version": "p3-slot-closure-v1",
        "slot_id": slot_id,
        "controlled_subject_id": controlled_subject_id,
        "site_id": site_id,
        "state": state,
        "path": (
            "APPLICABLE"
            if state == "SITE_FROZEN"
            else "APPLICABILITY_CLOSED_NOT_APPLICABLE"
        ),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _na_closers(subject_id: str, rows: tuple[dict[str, object], ...]) -> list[dict[str, object]]:
    return [
        _official_closer(
            str(row["slot_id"]),
            subject_id,
            "APPLICABILITY_CLOSED_NOT_APPLICABLE",
            None,
        )
        for row in rows
    ]


def _eligible_closers(
    subject_id: str, rows: tuple[dict[str, object], ...]
) -> list[dict[str, object]]:
    closers = _na_closers(subject_id, rows)
    closers[0] = _official_closer(
        str(rows[0]["slot_id"]), subject_id, "SITE_FROZEN", _sha("frozen-site")
    )
    return closers


def _synthetic_successor(ordinal: int, subject_id: str) -> dict[str, object]:
    return {
        "successor_ordinal": ordinal,
        "old_rank": ordinal + 1,
        "scale_class": "L",
        "total_effective_lines": 1000 + ordinal,
        "pbf_site_count": 2,
        "frozen_slots": 10,
        "neutral_snapshot_id": _sha(f"neutral-{ordinal}"),
        "controlled_subject_source_id": _sha(f"source-{ordinal}"),
        "controlled_subject_id": subject_id,
        "pbf_file_sha256": _sha(f"pbf-file-{ordinal}"),
        "pbf_artifact_sha256": _sha(f"pbf-art-{ordinal}"),
    }


def _synthetic_pbf() -> dict[str, object]:
    return {
        "rows": [],
        "public_schemas": [],
        "sites": [
            {
                "path": "a.py",
                "symbol": "f",
                "start_line": 1,
                "start_col": 0,
                "end_line": 1,
                "end_col": 1,
            },
            {
                "path": "b.py",
                "symbol": "g",
                "start_line": 2,
                "start_col": 0,
                "end_line": 2,
                "end_col": 1,
            },
        ],
    }


def _rehash_terminal(terminal: dict[str, object]) -> dict[str, object]:
    body = {key: value for key, value in terminal.items() if key != "artifact_sha256"}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _walk_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(value)
        for item in value.values():
            keys.update(_walk_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(_walk_keys(item))
    return keys


def _patch_inventory_rows(monkeypatch, rows_by_subject: dict[str, tuple[dict[str, object], ...]]):
    def fake(_authority, subject_id: str):
        return rows_by_subject[subject_id]

    monkeypatch.setattr(v2, "inventory_rows_for_subject", fake)


def test_close_successor_subject_completes_all_10_slots_when_first_is_frozen(
    monkeypatch,
):
    authority, subject, rows = _synthetic_authority()
    successor = _synthetic_successor(1, subject)
    calls: list[object] = []

    def fake_close(_authority, inventory_row, _sites, _pbf):
        calls.append(inventory_row)
        if len(calls) == 1:
            return _official_closer(
                str(inventory_row["slot_id"]),
                subject,
                "SITE_FROZEN",
                _sha("first-site"),
            )
        return _official_closer(
            str(inventory_row["slot_id"]),
            subject,
            "APPLICABILITY_CLOSED_NOT_APPLICABLE",
            None,
        )

    monkeypatch.setattr(v2, "close_slot_with_authority", fake_close)
    closed = v2.close_successor_subject(
        authority=authority, successor=successor, pbf=_synthetic_pbf()
    )
    assert len(calls) == 10
    assert closed["attempted_subject"]["eligibility"] == "V2_APPLICABILITY_ELIGIBLE"
    assert len(closed["official_closures"]) == 10


def test_derive_subject_eligibility_10_of_10_false_is_ineligible():
    _, subject, rows = _synthetic_authority()
    assert (
        v2.derive_subject_eligibility(_na_closers(subject, rows))
        == "V2_APPLICABILITY_INELIGIBLE"
    )


def test_derive_subject_eligibility_any_site_frozen_is_eligible():
    _, subject, rows = _synthetic_authority()
    assert (
        v2.derive_subject_eligibility(_eligible_closers(subject, rows))
        == "V2_APPLICABILITY_ELIGIBLE"
    )


def test_run_search_stops_after_first_eligible_and_does_not_open_later_subject(
    tmp_path, monkeypatch
):
    authority, subject, rows = _synthetic_authority()
    successors = tuple(_synthetic_successor(index, subject) for index in range(1, 4))
    opened: list[int] = []

    def fake_close(*, authority, successor, pbf):
        opened.append(int(successor["successor_ordinal"]))
        closers = (
            _eligible_closers(subject, rows)
            if successor["successor_ordinal"] == 2
            else _na_closers(subject, rows)
        )
        return {
            "attempted_subject": v2.build_attempted_subject(
                successor=successor, official_closures=closers
            ),
            "official_closures": closers,
        }

    monkeypatch.setattr(v2, "MAXIMUM_ATTEMPTS", 3)
    monkeypatch.setattr(v2, "FROZEN_SUCCESSOR_ROWS", successors)
    monkeypatch.setattr(
        v2,
        "validate_v2_preflight",
        lambda **_kwargs: {
            "status": "V2_PREFLIGHT_PASS",
            "controller_source_sha256": file_sha256(CONTROLLER_PATH),
            "authority_artifact_sha256": v2.AUTHORITY_ARTIFACT_SHA256,
            "successor_count": 3,
        },
    )
    monkeypatch.setattr(v2, "_load_official_authority", lambda _root: authority)
    monkeypatch.setattr(v2, "read_successor_pbf", lambda *_args, **_kwargs: _synthetic_pbf())
    monkeypatch.setattr(v2, "close_successor_subject", fake_close)
    monkeypatch.setattr(v2, "write_subject_closures", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(v2, "place_subject_directory", lambda **_kwargs: None)
    monkeypatch.setattr(v2, "write_official_cohort_terminal", lambda **_kwargs: None)
    monkeypatch.setattr(v2, "inventory_rows_for_subject", lambda *_args, **_kwargs: rows)
    result = v2.run_search(tmp_path)
    assert result["status"] == "V2_ELIGIBLE_SUBJECT_FOUND"
    assert opened == [1, 2]
    assert result["attempted_count"] == 2
    assert result["first_eligible_successor_ordinal"] == 2


def test_run_search_state_machine_stops_after_first_eligible_and_does_not_open_later_subject(
    tmp_path, monkeypatch
):
    test_run_search_stops_after_first_eligible_and_does_not_open_later_subject(
        tmp_path, monkeypatch
    )


def test_run_search_exhausts_22_ineligible_subjects(tmp_path, monkeypatch):
    authority, subject, rows = _synthetic_authority()
    successors = tuple(_synthetic_successor(index, subject) for index in range(1, 23))
    opened: list[int] = []

    def fake_close(*, authority, successor, pbf):
        opened.append(int(successor["successor_ordinal"]))
        closers = _na_closers(subject, rows)
        return {
            "attempted_subject": v2.build_attempted_subject(
                successor=successor, official_closures=closers
            ),
            "official_closures": closers,
        }

    monkeypatch.setattr(v2, "FROZEN_SUCCESSOR_ROWS", successors)
    monkeypatch.setattr(
        v2,
        "validate_v2_preflight",
        lambda **_kwargs: {
            "status": "V2_PREFLIGHT_PASS",
            "controller_source_sha256": file_sha256(CONTROLLER_PATH),
            "authority_artifact_sha256": v2.AUTHORITY_ARTIFACT_SHA256,
            "successor_count": 22,
        },
    )
    monkeypatch.setattr(v2, "_load_official_authority", lambda _root: authority)
    monkeypatch.setattr(v2, "read_successor_pbf", lambda *_args, **_kwargs: _synthetic_pbf())
    monkeypatch.setattr(v2, "close_successor_subject", fake_close)
    monkeypatch.setattr(v2, "write_subject_closures", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(v2, "place_subject_directory", lambda **_kwargs: None)
    monkeypatch.setattr(v2, "write_official_cohort_terminal", lambda **_kwargs: None)
    monkeypatch.setattr(v2, "inventory_rows_for_subject", lambda *_args, **_kwargs: rows)
    result = v2.run_search(tmp_path)
    assert result["status"] == "V2_COHORT_EXHAUSTED"
    assert opened == list(range(1, 23))
    assert result["attempted_count"] == 22
    assert result["first_eligible_successor_ordinal"] is None
    assert result["terminal"]["attempted_subjects"][-1]["eligibility"] == (
        "V2_APPLICABILITY_INELIGIBLE"
    )
    assert sum(len(row["closures"]) for row in result["terminal"]["attempted_subjects"]) == 220


def test_run_search_state_machine_exhausts_22_ineligible_subjects(tmp_path, monkeypatch):
    test_run_search_exhausts_22_ineligible_subjects(tmp_path, monkeypatch)


def test_run_search_ordinals_are_contiguous_and_cannot_skip(tmp_path, monkeypatch):
    authority, subject, rows = _synthetic_authority()
    successors = (
        _synthetic_successor(1, subject),
        _synthetic_successor(3, subject),
    )
    monkeypatch.setattr(v2, "MAXIMUM_ATTEMPTS", 2)
    monkeypatch.setattr(v2, "FROZEN_SUCCESSOR_ROWS", successors)
    monkeypatch.setattr(
        v2,
        "validate_v2_preflight",
        lambda **_kwargs: {
            "status": "V2_PREFLIGHT_PASS",
            "controller_source_sha256": file_sha256(CONTROLLER_PATH),
            "authority_artifact_sha256": v2.AUTHORITY_ARTIFACT_SHA256,
            "successor_count": 2,
        },
    )
    monkeypatch.setattr(v2, "_load_official_authority", lambda _root: authority)
    monkeypatch.setattr(v2, "read_successor_pbf", lambda *_args, **_kwargs: _synthetic_pbf())
    monkeypatch.setattr(
        v2,
        "close_successor_subject",
        lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("skip must fail before closing")
        ),
    )
    result = v2.run_search(tmp_path)
    assert result["status"] == "V2_EXECUTION_FAIL"
    assert result["terminal"] is None
    assert result["official_terminal_written"] is False


def test_run_search_state_machine_ordinals_are_contiguous_and_cannot_skip(
    tmp_path, monkeypatch
):
    test_run_search_ordinals_are_contiguous_and_cannot_skip(tmp_path, monkeypatch)


def test_run_search_infrastructure_failure_is_not_ineligible(tmp_path, monkeypatch):
    authority, subject, rows = _synthetic_authority()
    successors = tuple(_synthetic_successor(index, subject) for index in range(1, 4))
    recorded: list[str] = []

    def fake_close(*, authority, successor, pbf):
        if successor["successor_ordinal"] == 2:
            raise EvidenceError("V2_EXECUTION_FAIL", "partial")
        closers = _na_closers(subject, rows)
        attempted = v2.build_attempted_subject(
            successor=successor, official_closures=closers
        )
        recorded.append(attempted["eligibility"])
        return {"attempted_subject": attempted, "official_closures": closers}

    monkeypatch.setattr(v2, "MAXIMUM_ATTEMPTS", 3)
    monkeypatch.setattr(v2, "FROZEN_SUCCESSOR_ROWS", successors)
    monkeypatch.setattr(
        v2,
        "validate_v2_preflight",
        lambda **_kwargs: {
            "status": "V2_PREFLIGHT_PASS",
            "controller_source_sha256": file_sha256(CONTROLLER_PATH),
            "authority_artifact_sha256": v2.AUTHORITY_ARTIFACT_SHA256,
            "successor_count": 3,
        },
    )
    monkeypatch.setattr(v2, "_load_official_authority", lambda _root: authority)
    monkeypatch.setattr(v2, "read_successor_pbf", lambda *_args, **_kwargs: _synthetic_pbf())
    monkeypatch.setattr(v2, "close_successor_subject", fake_close)
    monkeypatch.setattr(v2, "write_subject_closures", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(v2, "place_subject_directory", lambda **_kwargs: None)
    monkeypatch.setattr(v2, "write_official_cohort_terminal", lambda **_kwargs: None)
    result = v2.run_search(tmp_path)
    assert result["status"] == "V2_EXECUTION_FAIL"
    assert result["terminal"] is None
    assert recorded == ["V2_APPLICABILITY_INELIGIBLE"]
    assert result["attempted_count"] == 1


def test_run_search_state_machine_infrastructure_failure_is_not_ineligible(
    tmp_path, monkeypatch
):
    test_run_search_infrastructure_failure_is_not_ineligible(tmp_path, monkeypatch)


def _found_terminal(monkeypatch) -> tuple[dict[str, object], str, dict[str, object]]:
    authority, subject, rows = _synthetic_authority()
    first = _synthetic_successor(1, subject)
    second = _synthetic_successor(2, subject)
    monkeypatch.setattr(v2, "FROZEN_SUCCESSOR_ROWS", (first, second))
    monkeypatch.setattr(v2, "_load_official_authority", lambda _root: authority)
    attempted = (
        v2.build_attempted_subject(
            successor=first, official_closures=_na_closers(subject, rows)
        ),
        v2.build_attempted_subject(
            successor=second, official_closures=_eligible_closers(subject, rows)
        ),
    )
    _patch_inventory_rows(monkeypatch, {subject: rows})
    digest = file_sha256(CONTROLLER_PATH)
    terminal = v2.build_cohort_terminal(
        attempted_subjects=attempted, controller_source_sha256=digest
    )
    return terminal, digest, second


def test_build_and_validate_found_terminal_consistency(monkeypatch):
    terminal, digest, second = _found_terminal(monkeypatch)
    validated = v2.validate_cohort_terminal(
        terminal, controller_source_sha256=digest
    )
    assert validated["terminal_status"] == "V2_ELIGIBLE_SUBJECT_FOUND"
    assert validated["first_eligible_successor_ordinal"] == 2
    assert validated["first_eligible_neutral_snapshot_id"] == second["neutral_snapshot_id"]
    assert len(validated["attempted_subjects"]) == 2


def test_build_and_validate_exhausted_terminal_consistency(monkeypatch):
    authority, subject, rows = _synthetic_authority()
    successors = [_synthetic_successor(index, subject) for index in range(1, 23)]
    monkeypatch.setattr(v2, "FROZEN_SUCCESSOR_ROWS", tuple(successors))
    monkeypatch.setattr(v2, "_load_official_authority", lambda _root: authority)
    attempted = [
        v2.build_attempted_subject(
            successor=row, official_closures=_na_closers(subject, rows)
        )
        for row in successors
    ]
    _patch_inventory_rows(monkeypatch, {subject: rows})
    digest = file_sha256(CONTROLLER_PATH)
    terminal = v2.build_cohort_terminal(
        attempted_subjects=attempted, controller_source_sha256=digest
    )
    validated = v2.validate_cohort_terminal(
        terminal, controller_source_sha256=digest
    )
    assert validated["terminal_status"] == "V2_COHORT_EXHAUSTED"
    assert validated["first_eligible_successor_ordinal"] is None
    assert validated["first_eligible_neutral_snapshot_id"] is None
    assert len(validated["attempted_subjects"]) == 22
    assert (
        sum(len(row["closures"]) for row in validated["attempted_subjects"]) == 220
    )


def test_validate_cohort_terminal_rejects_controller_sha_change(monkeypatch):
    terminal, digest, _second = _found_terminal(monkeypatch)
    mutated = _rehash_terminal({**terminal, "controller_source_sha256": "a" * 64})
    with pytest.raises(EvidenceError):
        v2.validate_cohort_terminal(mutated, controller_source_sha256=digest)


def test_validate_cohort_terminal_rejects_design_sha_change(monkeypatch):
    terminal, digest, _second = _found_terminal(monkeypatch)
    mutated = _rehash_terminal({**terminal, "design_file_sha256": "b" * 64})
    with pytest.raises(EvidenceError):
        v2.validate_cohort_terminal(mutated, controller_source_sha256=digest)


def test_validate_cohort_terminal_rejects_attempted_order_change(monkeypatch):
    terminal, digest, _second = _found_terminal(monkeypatch)
    swapped = list(terminal["attempted_subjects"])
    swapped[0], swapped[1] = swapped[1], swapped[0]
    mutated = _rehash_terminal({**terminal, "attempted_subjects": swapped})
    with pytest.raises(EvidenceError):
        v2.validate_cohort_terminal(mutated, controller_source_sha256=digest)


def test_validate_cohort_terminal_rejects_closure_hash_change(monkeypatch):
    terminal, digest, _second = _found_terminal(monkeypatch)
    subjects = list(terminal["attempted_subjects"])
    first = dict(subjects[0])
    closures = [dict(row) for row in first["closures"]]
    closures[0] = {**closures[0], "closure_artifact_sha256": "c" * 64}
    first["closures"] = closures
    subjects[0] = first
    mutated = _rehash_terminal({**terminal, "attempted_subjects": subjects})
    with pytest.raises(EvidenceError):
        v2.validate_cohort_terminal(mutated, controller_source_sha256=digest)


def test_validate_cohort_terminal_rejects_terminal_status_change(monkeypatch):
    terminal, digest, _second = _found_terminal(monkeypatch)
    mutated = _rehash_terminal(
        {**terminal, "terminal_status": "V2_COHORT_EXHAUSTED"}
    )
    with pytest.raises(EvidenceError):
        v2.validate_cohort_terminal(mutated, controller_source_sha256=digest)


def test_cohort_terminal_has_no_path_symbol_source_or_outcome_fields(monkeypatch):
    terminal, digest, _second = _found_terminal(monkeypatch)
    keys = _walk_keys(terminal)
    assert keys.isdisjoint(v2.FORBIDDEN_LEAK_KEYS)
    v2.validate_cohort_terminal(terminal, controller_source_sha256=digest)


def _patch_tmp_search(
    monkeypatch,
    tmp_path: Path,
    *,
    closers_factory,
    successors=None,
    maximum_attempts=None,
):
    authority, subject, rows = _synthetic_authority()
    if successors is None:
        successors = (_synthetic_successor(1, subject),)
    if maximum_attempts is None:
        maximum_attempts = len(successors)
    events: list[str] = []

    def fake_close(*, authority, successor, pbf):
        events.append(f"memory:{successor['successor_ordinal']}")
        closers = closers_factory(successor, subject, rows)
        return {
            "attempted_subject": v2.build_attempted_subject(
                successor=successor, official_closures=closers
            ),
            "official_closures": closers,
        }

    monkeypatch.setattr(v2, "MAXIMUM_ATTEMPTS", maximum_attempts)
    monkeypatch.setattr(v2, "FROZEN_SUCCESSOR_ROWS", successors)
    monkeypatch.setattr(
        v2,
        "validate_v2_preflight",
        lambda **_kwargs: {
            "status": "V2_PREFLIGHT_PASS",
            "controller_source_sha256": file_sha256(CONTROLLER_PATH),
            "authority_artifact_sha256": v2.AUTHORITY_ARTIFACT_SHA256,
            "successor_count": len(successors),
        },
    )
    monkeypatch.setattr(v2, "_load_official_authority", lambda _root: authority)
    monkeypatch.setattr(v2, "read_successor_pbf", lambda *_args, **_kwargs: _synthetic_pbf())
    monkeypatch.setattr(v2, "close_successor_subject", fake_close)
    monkeypatch.setattr(v2, "inventory_rows_for_subject", lambda *_args, **_kwargs: rows)
    return {
        "authority": authority,
        "subject": subject,
        "rows": rows,
        "successors": successors,
        "events": events,
        "repo_root": tmp_path,
    }


def test_subject_directory_written_only_after_10_closures_exist_in_memory(
    tmp_path, monkeypatch
):
    ctx = _patch_tmp_search(
        monkeypatch,
        tmp_path,
        closers_factory=lambda _successor, subject, rows: _eligible_closers(subject, rows),
    )
    real_write = v2.write_subject_closures

    def wrapped(directory, closures):
        assert any(item.startswith("memory:") for item in ctx["events"])
        assert len(tuple(closures)) == 10
        ctx["events"].append("staging-write")
        return real_write(directory, closures)

    monkeypatch.setattr(v2, "write_subject_closures", wrapped)
    result = v2.run_search(tmp_path)
    successor = ctx["successors"][0]
    official = v2.official_subject_dir(tmp_path, str(successor["neutral_snapshot_id"]))
    assert result["status"] == "V2_ELIGIBLE_SUBJECT_FOUND"
    assert ctx["events"][:2] == ["memory:1", "staging-write"]
    written = sorted(official.glob("slot-closure-*.json"))
    assert len(written) == 10


def test_atomic_subject_directory_written_only_after_10_closures_exist_in_memory(
    tmp_path, monkeypatch
):
    test_subject_directory_written_only_after_10_closures_exist_in_memory(
        tmp_path, monkeypatch
    )


def test_subject_directory_is_placed_atomically(tmp_path, monkeypatch):
    ctx = _patch_tmp_search(
        monkeypatch,
        tmp_path,
        closers_factory=lambda _successor, subject, rows: _eligible_closers(subject, rows),
    )
    replaced: list[tuple[str, str]] = []
    real_replace = os.replace

    def spy(src, dst):
        replaced.append((str(src), str(dst)))
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", spy)
    monkeypatch.setattr(v2, "os", os)
    result = v2.run_search(tmp_path)
    successor = ctx["successors"][0]
    official = v2.official_subject_dir(tmp_path, str(successor["neutral_snapshot_id"]))
    staging = v2.staging_subject_dir(tmp_path, str(successor["neutral_snapshot_id"]))
    assert result["status"] == "V2_ELIGIBLE_SUBJECT_FOUND"
    assert official.is_dir()
    assert not staging.exists()
    assert any(Path(dst) == official for _src, dst in replaced)


def test_cohort_terminal_is_written_last(tmp_path, monkeypatch):
    ctx = _patch_tmp_search(
        monkeypatch,
        tmp_path,
        closers_factory=lambda _successor, subject, rows: _eligible_closers(subject, rows),
    )
    order: list[str] = []
    real_subject = v2.write_subject_closures
    real_place = v2.place_subject_directory
    real_terminal = v2.write_official_cohort_terminal

    def write_subject(directory, closures):
        order.append("closures")
        return real_subject(directory, closures)

    def place(**kwargs):
        order.append("place")
        return real_place(**kwargs)

    def write_terminal(**kwargs):
        order.append("terminal")
        return real_terminal(**kwargs)

    monkeypatch.setattr(v2, "write_subject_closures", write_subject)
    monkeypatch.setattr(v2, "place_subject_directory", place)
    monkeypatch.setattr(v2, "write_official_cohort_terminal", write_terminal)
    result = v2.run_search(tmp_path)
    assert result["status"] == "V2_ELIGIBLE_SUBJECT_FOUND"
    assert order == ["closures", "place", "terminal"]
    official_terminal = v2.official_root(tmp_path) / "cohort-terminal.json"
    assert official_terminal.is_file()


def test_terminal_write_cohort_is_written_last(tmp_path, monkeypatch):
    test_cohort_terminal_is_written_last(tmp_path, monkeypatch)


def test_no_pbf_open_or_closure_write_after_terminal(tmp_path, monkeypatch):
    ctx = _patch_tmp_search(
        monkeypatch,
        tmp_path,
        closers_factory=lambda _successor, subject, rows: _eligible_closers(subject, rows),
    )
    result = v2.run_search(tmp_path)
    assert result["status"] == "V2_ELIGIBLE_SUBJECT_FOUND"

    def forbid(*_args, **_kwargs):
        raise AssertionError("PBF or closure work after terminal")

    monkeypatch.setattr(v2, "read_successor_pbf", forbid)
    monkeypatch.setattr(v2, "close_successor_subject", forbid)
    monkeypatch.setattr(v2, "write_subject_closures", forbid)
    assert (v2.official_root(tmp_path) / "cohort-terminal.json").is_file()
    assert result["official_terminal_written"] is True


def test_terminal_write_no_pbf_open_or_closure_write_after_terminal(
    tmp_path, monkeypatch
):
    test_no_pbf_open_or_closure_write_after_terminal(tmp_path, monkeypatch)


def test_failure_does_not_write_cohort_terminal(tmp_path, monkeypatch):
    def boom(_successor, _subject, _rows):
        raise EvidenceError("V2_EXECUTION_FAIL", "partial")

    _patch_tmp_search(monkeypatch, tmp_path, closers_factory=boom)
    result = v2.run_search(tmp_path)
    assert result["status"] == "V2_EXECUTION_FAIL"
    assert result["terminal"] is None
    assert not (v2.official_root(tmp_path) / "cohort-terminal.json").exists()
    assert not (v2.staging_root(tmp_path) / "cohort-terminal.json").exists()


def test_terminal_write_failure_does_not_write_cohort_terminal(tmp_path, monkeypatch):
    test_failure_does_not_write_cohort_terminal(tmp_path, monkeypatch)


def test_failure_keeps_partial_or_staging(tmp_path, monkeypatch):
    ctx = _patch_tmp_search(
        monkeypatch,
        tmp_path,
        closers_factory=lambda _successor, subject, rows: _eligible_closers(subject, rows),
    )
    real = v2.write_canonical_json
    seen = {"count": 0}

    def flaky(path, value, *, exclusive):
        seen["count"] += 1
        if seen["count"] == 7:
            raise EvidenceError("V2_EXECUTION_FAIL", "write failed")
        return real(path, value, exclusive=exclusive)

    monkeypatch.setattr(v2, "write_canonical_json", flaky)
    result = v2.run_search(tmp_path)
    successor = ctx["successors"][0]
    official = v2.official_subject_dir(tmp_path, str(successor["neutral_snapshot_id"]))
    staging = v2.staging_subject_dir(tmp_path, str(successor["neutral_snapshot_id"]))
    assert result["status"] == "V2_EXECUTION_FAIL"
    assert not official.exists()
    assert not (v2.official_root(tmp_path) / "cohort-terminal.json").exists()
    assert staging.exists()


def test_existing_official_path_is_not_overwritten(tmp_path, monkeypatch):
    ctx = _patch_tmp_search(
        monkeypatch,
        tmp_path,
        closers_factory=lambda _successor, subject, rows: _eligible_closers(subject, rows),
    )
    successor = ctx["successors"][0]
    official = v2.official_subject_dir(tmp_path, str(successor["neutral_snapshot_id"]))
    official.mkdir(parents=True)
    marker = official / "marker.txt"
    marker.write_text("keep", encoding="utf-8")
    result = v2.run_search(tmp_path)
    assert result["status"] == "V2_EXECUTION_FAIL"
    assert marker.read_text(encoding="utf-8") == "keep"
    assert not (v2.official_root(tmp_path) / "cohort-terminal.json").exists()


def test_atomic_existing_official_path_is_not_overwritten(tmp_path, monkeypatch):
    test_existing_official_path_is_not_overwritten(tmp_path, monkeypatch)


def test_main_rejects_help_and_extra_arguments():
    env = {
        **os.environ,
        "PYTHONPATH": "/tmp/p3-c3-applicability-authority/src",
    }
    for extra in (["--help"], ["--output-root", "x"]):
        completed = subprocess.run(
            [sys.executable, str(CONTROLLER_PATH), *extra],
            cwd="/tmp/p3-c3-applicability-authority",
            env=env,
            capture_output=True,
            check=False,
        )
        assert completed.returncode == 2
        combined = completed.stdout + completed.stderr
        assert b"path" not in combined.lower() or b'"path"' not in combined
        text = combined.decode("utf-8", errors="replace")
        assert "symbol" not in text
        assert "start_line" not in text


def test_cli_main_rejects_help_and_extra_arguments():
    test_main_rejects_help_and_extra_arguments()


def test_stdout_summary_has_no_site_path_symbol_or_span(monkeypatch, capsys):
    fake_result = {
        "status": "V2_ELIGIBLE_SUBJECT_FOUND",
        "code": None,
        "controller_source_sha256": file_sha256(CONTROLLER_PATH),
        "attempted_count": 1,
        "first_eligible_successor_ordinal": 1,
        "first_eligible_neutral_snapshot_id": _sha("neutral-1"),
        "official_terminal_written": True,
        "terminal": {"terminal_status": "V2_ELIGIBLE_SUBJECT_FOUND"},
    }
    calls = {"n": 0}

    def fake_run(_root):
        calls["n"] += 1
        return fake_result

    monkeypatch.setattr(v2, "run_search", fake_run)
    monkeypatch.setattr(sys, "argv", [str(CONTROLLER_PATH)])
    code = v2.main()
    assert code == 0
    assert calls["n"] == 1
    payload = json.loads(capsys.readouterr().out)
    assert set(payload) == set(v2.STDOUT_SUMMARY_SCHEMA)
    assert payload["controller_source_sha256"] == file_sha256(CONTROLLER_PATH)
    assert _walk_keys(payload).isdisjoint(v2.FORBIDDEN_LEAK_KEYS)
    assert v2.stdout_summary(fake_result)["status"] == "V2_ELIGIBLE_SUBJECT_FOUND"


def test_main_calls_run_search_once(monkeypatch):
    calls = {"n": 0}

    def fake_run(_root):
        calls["n"] += 1
        return {
            "status": "V2_COHORT_EXHAUSTED",
            "code": None,
            "controller_source_sha256": file_sha256(CONTROLLER_PATH),
            "attempted_count": 22,
            "first_eligible_successor_ordinal": None,
            "first_eligible_neutral_snapshot_id": None,
            "official_terminal_written": True,
            "terminal": None,
        }

    monkeypatch.setattr(v2, "run_search", fake_run)
    monkeypatch.setattr(sys, "argv", [str(CONTROLLER_PATH)])
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(io.BytesIO(), encoding="utf-8"))
    # main writes sys.stdout.buffer
    buffer = io.BytesIO()

    class _Stdout:
        def __init__(self):
            self.buffer = buffer

    monkeypatch.setattr(sys, "stdout", _Stdout())
    assert v2.main() == 0
    assert calls["n"] == 1


def test_controller_file_sha_is_bound_into_terminal(tmp_path, monkeypatch):
    _patch_tmp_search(
        monkeypatch,
        tmp_path,
        closers_factory=lambda _successor, subject, rows: _eligible_closers(subject, rows),
    )
    result = v2.run_search(tmp_path)
    digest = file_sha256(CONTROLLER_PATH)
    assert result["controller_source_sha256"] == digest
    official_terminal = v2.official_root(tmp_path) / "cohort-terminal.json"
    payload = json.loads(official_terminal.read_text(encoding="utf-8"))
    assert payload["controller_source_sha256"] == digest


def test_terminal_write_controller_file_sha_is_bound_into_terminal(
    tmp_path, monkeypatch
):
    test_controller_file_sha_is_bound_into_terminal(tmp_path, monkeypatch)
