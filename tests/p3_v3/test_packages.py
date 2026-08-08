from __future__ import annotations

import copy

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.packages import build_package, materialize_package, verify_package


def test_package_builds_and_verifies_regular_file(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "program.py").write_text("print(1)\n", encoding="utf-8")
    manifest = build_package(
        "CONSTRUCTION_A",
        source,
        [{"path": "program.py", "class": "SOURCE"}],
        ["a" * 64],
    )
    verify_package(source, manifest)
    assert manifest["files"][0]["path"] == "program.py"
    assert manifest["files"][0]["size"] == 9


def test_package_rejects_symlink(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "real").write_text("x", encoding="utf-8")
    (source / "link").symlink_to("real")
    with pytest.raises(EvidenceError, match="E_PACKAGE_FILE_TYPE"):
        build_package(
            "CONSTRUCTION_A", source, [{"path": "link", "class": "SOURCE"}], []
        )


def test_package_rejects_duplicate_normalized_path(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "x").write_text("x", encoding="utf-8")
    with pytest.raises(EvidenceError, match="E_PACKAGE_DUPLICATE"):
        build_package(
            "CONSTRUCTION_A",
            source,
            [{"path": "x", "class": "SOURCE"}, {"path": "x", "class": "BUILD"}],
            [],
        )


def test_package_role_rejects_holdout_content_in_package_a(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "reveal.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(EvidenceError, match="E_PACKAGE_CONTENT_CLASS"):
        build_package(
            "CONSTRUCTION_A",
            source,
            [{"path": "reveal.json", "class": "P12_REVEAL"}],
            [],
        )


def test_verifier_rejects_byte_drift(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    path = source / "program.py"
    path.write_text("print(1)\n", encoding="utf-8")
    manifest = build_package(
        "CONSTRUCTION_A", source, [{"path": "program.py", "class": "SOURCE"}], []
    )
    path.write_text("print(2)\n", encoding="utf-8")
    with pytest.raises(EvidenceError, match="E_PACKAGE_SHA256"):
        verify_package(source, manifest)


def test_manifest_tampering_fails_before_file_verification(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "program.py").write_text("print(1)\n", encoding="utf-8")
    manifest = build_package(
        "CONSTRUCTION_A", source, [{"path": "program.py", "class": "SOURCE"}], []
    )
    changed = copy.deepcopy(manifest)
    changed["files"][0]["size"] = 0
    with pytest.raises(EvidenceError, match="E_PACKAGE_MANIFEST_HASH"):
        verify_package(source, changed)


def test_materialization_is_exact_and_requires_new_target(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "nested").mkdir()
    (source / "nested/program.py").write_text("print(1)\n", encoding="utf-8")
    manifest = build_package(
        "CONSTRUCTION_A",
        source,
        [{"path": "nested/program.py", "class": "SOURCE"}],
        [],
    )
    target = tmp_path / "materialized"
    materialize_package(source, target, manifest)
    assert (target / "nested/program.py").read_bytes() == b"print(1)\n"
    verify_package(target, manifest)
    with pytest.raises(EvidenceError, match="E_PACKAGE_TARGET_EXISTS"):
        materialize_package(source, target, manifest)
