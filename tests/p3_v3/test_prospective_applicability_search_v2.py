from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest

from p3_v3.applicability_predicates import (
    build_predicate_registry,
    load_applicability_authority,
)
from p3_v3.artifacts import EvidenceError, canonical_sha256, file_sha256
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
