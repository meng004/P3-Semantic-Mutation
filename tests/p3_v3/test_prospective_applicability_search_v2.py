from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from p3_v3.applicability_predicates import load_applicability_authority
from p3_v3.artifacts import EvidenceError, file_sha256

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
