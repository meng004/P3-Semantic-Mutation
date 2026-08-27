from __future__ import annotations

import copy
import concurrent.futures
import hashlib
import inspect
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import threading
from pathlib import Path

import pytest

import p3_v3.bridge_and_frames as frames_module
import scripts.p3_v3.evidence as evidence_module
from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import (
    build_public_behavior_frame,
    derive_subject_material,
    run_adapter_discovery,
    select_profiling_workload,
    validate_adapter_registry,
    validate_common_inputs_on_fixed_source,
    validate_input_generator_registry,
)

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/p3_v3/evidence.py"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "public_behavior"
ADAPTER_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "adapters"
COMMANDS = {
    "freeze-authority-lock",
    "validate-protocol",
    "verify-bridge",
    "build-frames",
    "verify-mr-inventory",
    "build-package",
    "verify-package",
    "run-preflight",
    "verify-run-records",
    "close-phase",
    "verify-evidence",
    "validate-applicability-authority",
}
SCIENTIFIC_PLAN_SHA256 = (
    "fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830"
)
EVIDENCE_DESIGN_SHA256 = (
    "7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9"
)
TECHNIQUE_ORDER = [
    "HYBRID_NATIVE",
    "TENSOR_AUTODIFF",
    "PROBABILISTIC_SURROGATE",
    "ITERATIVE_STOCHASTIC",
    "ARRAY_NUMERICAL",
    "SCALAR_CONTROL",
    "TECH_UNCERTAIN",
]
P12_OUTCOME_STATES = [
    "MR_VIOLATION",
    "MR_SATISFIED",
    "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
    "SCIENTIFIC_INCONCLUSIVE",
    "INFRASTRUCTURE_UNRESOLVED",
]
BEHAVIOR_CATEGORY_ORDER = [
    "PUBLIC_API",
    "CLI",
    "EXAMPLE",
    "BENCHMARK",
    "PROJECT_TEST",
]
_ADAPTER_SPECS = (
    ("PYTHON_PEP517_V1", "python", "adapters/python_pep517_v1.py"),
    ("CMAKE_CTEST_V1", "cmake", "adapters/cmake_ctest_v1.py"),
    ("MESON_TEST_V1", "meson", "adapters/meson_test_v1.py"),
    ("AUTOTOOLS_MAKECHECK_V1", "autotools", "adapters/autotools_makecheck_v1.py"),
)
SECRET_ORIGIN = (
    "https://audit-user:TOP_SECRET_TOKEN@github.com/" "meng004/P3-Semantic-Mutation.git"
)
SECRET_IDENTITY = "github.com/meng004/P3-Semantic-Mutation"
SECRET_ORIGIN_SHA256 = (
    "8b90a20c89d81eff7287a414ad53840b1d030a1e1d42a409a69396efbe2ec3d2"
)


def _source_snapshot(root: Path):
    entries = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.relative_to(root).parts:
            continue
        raw = path.read_bytes()
        entries.append(
            frames_module.SourceSnapshotEntry(
                relative_path=path.relative_to(root).as_posix(),
                mode="100755" if path.stat().st_mode & stat.S_IXUSR else "100644",
                sha256=hashlib.sha256(raw).hexdigest(),
                content=raw,
            )
        )
    entries.sort(key=lambda entry: entry.relative_path.encode("utf-8"))
    return frames_module.SourceSnapshot(entries=tuple(entries))


def _env():
    return {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def _digest(label: str) -> str:
    return canonical_sha256({"fixture": label})


AUTHORITY_LOCK_KEYS = {
    "schema_version",
    "task_id",
    "controller_repository",
    "subjects",
    "governing_materials",
    "protocol",
    "registries",
    "preflight",
    "jobs",
    "claim_policy",
}
_CONTROLLER_AUTHORITY_KEYS = {
    "normalized_repository_identity",
    "base_commit",
    "base_tree",
    "tracked_source_manifest_sha256",
}
_SUBJECT_AUTHORITY_KEYS = {
    "subject_id",
    "repository_role",
    "normalized_repository_identity",
    "base_commit",
    "base_tree",
    "tracked_source_manifest_sha256",
    "build_descriptor_sha256",
    "adapter_id",
}
_GOVERNING_AUTHORITY_KEYS = {
    "scientific_plan_sha256",
    "evidence_design_sha256",
    "authority_lock_design_sha256",
    "implementation_plan_sha256",
    "controller_implementation_manifest_sha256",
}
_PROTOCOL_AUTHORITY_KEYS = {
    "protocol_sha256",
    "rq_spec_sha256",
    "claim_ceiling_sha256",
    "p12_contract_sha256",
    "operator_catalogue_sha256",
    "mr_policy_sha256",
    "site_policy_sha256",
    "analysis_spec_sha256",
    "package_policy_sha256",
    "environment_lock_sha256",
    "job_derivation_policy_sha256",
}
_REGISTRY_AUTHORITY_KEYS = {
    "adapter_registry_sha256",
    "input_generator_registry_sha256",
}
_PREFLIGHT_AUTHORITY_KEYS = {
    "normalized_repository_identity",
    "base_commit",
    "base_tree",
    "dependency_lock_sha256",
    "environment_policy_sha256",
    "required_capabilities",
    "forbidden_credential_fields",
}
_JOB_AUTHORITY_KEYS = {
    "job_id",
    "phase",
    "job_role",
    "object_identity",
    "input_identity_sha256",
    "intent_template_sha256",
    "maximum_attempts",
    "retry_trigger",
    "execution_class",
    "p12_access_class",
}
_CLAIM_POLICY_AUTHORITY_KEYS = {
    "claim_ceiling_sha256",
    "required_status",
    "rq_ids",
}
_AUTHORITY_OBJECT_SCHEMAS = (
    ((), AUTHORITY_LOCK_KEYS),
    (("controller_repository",), _CONTROLLER_AUTHORITY_KEYS),
    (("subjects", 0), _SUBJECT_AUTHORITY_KEYS),
    (("governing_materials",), _GOVERNING_AUTHORITY_KEYS),
    (("protocol",), _PROTOCOL_AUTHORITY_KEYS),
    (("registries",), _REGISTRY_AUTHORITY_KEYS),
    (("preflight",), _PREFLIGHT_AUTHORITY_KEYS),
    (("jobs", 0), _JOB_AUTHORITY_KEYS),
    (("claim_policy",), _CLAIM_POLICY_AUTHORITY_KEYS),
)


def _authority_lock() -> dict:
    protocol = {
        "protocol_sha256": "6" * 64,
        "rq_spec_sha256": "7" * 64,
        "claim_ceiling_sha256": "8" * 64,
        "p12_contract_sha256": "9" * 64,
        "operator_catalogue_sha256": "a" * 64,
        "mr_policy_sha256": "b" * 64,
        "site_policy_sha256": "c" * 64,
        "analysis_spec_sha256": "d" * 64,
        "package_policy_sha256": "e" * 64,
        "environment_lock_sha256": "f" * 64,
        "job_derivation_policy_sha256": "0" * 64,
    }
    return {
        "schema_version": "P3_V3_AUTHORITY_LOCK_V1",
        "task_id": "p3-v3-foundation",
        "controller_repository": {
            "normalized_repository_identity": "github.com/example/controller",
            "base_commit": "1" * 40,
            "base_tree": "2" * 40,
            "tracked_source_manifest_sha256": "1" * 64,
        },
        "subjects": [
            {
                "subject_id": "subject-a",
                "repository_role": "CONTROLLED_A",
                "normalized_repository_identity": "github.com/example/subject-a",
                "base_commit": "3" * 40,
                "base_tree": "4" * 40,
                "tracked_source_manifest_sha256": "2" * 64,
                "build_descriptor_sha256": "4" * 64,
                "adapter_id": "PYTHON_PEP517_V1",
            },
            {
                "subject_id": "subject-b",
                "repository_role": "CONTROLLED_B",
                "normalized_repository_identity": "github.com/example/subject-b",
                "base_commit": "5" * 40,
                "base_tree": "6" * 40,
                "tracked_source_manifest_sha256": "3" * 64,
                "build_descriptor_sha256": "5" * 64,
                "adapter_id": "CMAKE_CTEST_V1",
            },
        ],
        "governing_materials": {
            "scientific_plan_sha256": "1" * 64,
            "evidence_design_sha256": "2" * 64,
            "authority_lock_design_sha256": "3" * 64,
            "implementation_plan_sha256": "4" * 64,
            "controller_implementation_manifest_sha256": "1" * 64,
        },
        "protocol": protocol,
        "registries": {
            "adapter_registry_sha256": "a" * 64,
            "input_generator_registry_sha256": "b" * 64,
        },
        "preflight": {
            "normalized_repository_identity": "github.com/example/controller",
            "base_commit": "1" * 40,
            "base_tree": "2" * 40,
            "dependency_lock_sha256": "c" * 64,
            "environment_policy_sha256": protocol["environment_lock_sha256"],
            "required_capabilities": ["cpu", "disk", "memory"],
            "forbidden_credential_fields": [
                "authorization",
                "credential",
                "password",
                "token",
            ],
        },
        "jobs": [
            {
                "job_id": "1" * 64,
                "phase": "PHASE_0",
                "job_role": "PREFLIGHT_CONTROL",
                "object_identity": "CONTROL:preflight",
                "input_identity_sha256": "2" * 64,
                "intent_template_sha256": "3" * 64,
                "maximum_attempts": 3,
                "retry_trigger": "FAIL_INFRASTRUCTURE",
                "execution_class": "NON_SCIENTIFIC_CONTROL",
                "p12_access_class": "FORBIDDEN",
            },
            {
                "job_id": "2" * 64,
                "phase": "PHASE_1",
                "job_role": "SYNTHETIC_CHECK",
                "object_identity": "SYNTHETIC:case-1",
                "input_identity_sha256": "4" * 64,
                "intent_template_sha256": "5" * 64,
                "maximum_attempts": 3,
                "retry_trigger": "FAIL_INFRASTRUCTURE",
                "execution_class": "SYNTHETIC_INFRASTRUCTURE",
                "p12_access_class": "PERMITTED",
            },
        ],
        "claim_policy": {
            "claim_ceiling_sha256": protocol["claim_ceiling_sha256"],
            "required_status": "blocked",
            "rq_ids": ["RQ1", "RQ2", "RQ3", "RQ4"],
        },
    }


def _nested_value(value, path):
    for component in path:
        value = value[component]
    return value


def test_controller_manifest_covers_exact_controller_role_roots(tmp_path):
    source = tmp_path / "src/p3_v3/controller.py"
    script = tmp_path / "scripts/p3_v3/evidence.py"
    dependency_lock = tmp_path / "requirements-frozen.txt"
    source.parent.mkdir(parents=True)
    script.parent.mkdir(parents=True)
    source.write_text("controller = True\n", encoding="utf-8")
    script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    dependency_lock.write_text("pytest==8.4.2\n", encoding="utf-8")

    manifest = evidence_module.build_tracked_source_manifest(
        tmp_path,
        ["src/p3_v3", "scripts/p3_v3", "requirements-frozen.txt"],
        "controller-source",
    )

    assert set(manifest) == {"schema_version", "role", "files"}
    assert manifest["schema_version"] == "P3_V3_TRACKED_SOURCE_MANIFEST_V1"
    assert manifest["role"] == "controller-source"
    assert manifest["files"] == [
        {
            "relative_path": "requirements-frozen.txt",
            "mode": "100644",
            "sha256": hashlib.sha256(dependency_lock.read_bytes()).hexdigest(),
        },
        {
            "relative_path": "scripts/p3_v3/evidence.py",
            "mode": "100755",
            "sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        },
        {
            "relative_path": "src/p3_v3/controller.py",
            "mode": "100644",
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        },
    ]


def test_manifest_mode_projection_uses_owner_execute_only(tmp_path):
    source = tmp_path / "subject.py"
    source.write_text("subject = True\n", encoding="utf-8")
    source.chmod((source.stat().st_mode & ~stat.S_IXUSR) | stat.S_IXGRP)

    manifest = evidence_module.build_tracked_source_manifest(
        tmp_path, ["."], "subject-source"
    )

    assert manifest["files"][0]["mode"] == "100644"


def test_controller_manifest_rejects_omitted_role_root(tmp_path):
    (tmp_path / "src/p3_v3").mkdir(parents=True)
    (tmp_path / "scripts/p3_v3").mkdir(parents=True)
    (tmp_path / "requirements-frozen.txt").write_text("locked\n", encoding="utf-8")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path,
            ["src/p3_v3", "scripts/p3_v3"],
            "controller-source",
        )


def test_subject_manifest_includes_complete_root_and_excludes_git(tmp_path):
    source = tmp_path / "subject.py"
    vendor = tmp_path / "vendor/dependency.py"
    fixture = tmp_path / "fixtures/input.txt"
    generated = tmp_path / "generated/parser.py"
    git_config = tmp_path / ".git/config"
    for path in (source, vendor, fixture, generated, git_config):
        path.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("password = token\n", encoding="utf-8")
    vendor.write_text("vendor = True\n", encoding="utf-8")
    fixture.write_text("fixture\n", encoding="utf-8")
    generated.write_text("generated = True\n", encoding="utf-8")
    git_config.write_text("authorization = credential\n", encoding="utf-8")

    manifest = evidence_module.build_tracked_source_manifest(
        tmp_path, ["."], "subject-source"
    )

    assert [row["relative_path"] for row in manifest["files"]] == [
        "fixtures/input.txt",
        "generated/parser.py",
        "subject.py",
        "vendor/dependency.py",
    ]
    assert all(set(row) == {"relative_path", "mode", "sha256"} for row in manifest["files"])
    subject_row = next(
        row for row in manifest["files"] if row["relative_path"] == "subject.py"
    )
    assert subject_row["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()


def test_subject_manifest_rejects_root_git_file(tmp_path):
    (tmp_path / "subject.py").write_text("subject = True\n", encoding="utf-8")
    (tmp_path / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["."], "subject-source"
        )


def test_subject_manifest_rejects_nested_git_directory(tmp_path):
    (tmp_path / "subject.py").write_text("subject = True\n", encoding="utf-8")
    nested_git = tmp_path / "vendor/.git"
    nested_git.mkdir(parents=True)
    (nested_git / "config").write_text("metadata\n", encoding="utf-8")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["."], "subject-source"
        )


def test_subject_manifest_rejects_selective_file_roots(tmp_path):
    (tmp_path / "subject.py").write_text("subject = True\n", encoding="utf-8")
    (tmp_path / "omitted.py").write_text("omitted = True\n", encoding="utf-8")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["subject.py"], "subject-source"
        )


@pytest.mark.parametrize(
    "transient",
    [".venv", "venv", "__pycache__", ".pytest_cache", "build", "dist"],
)
def test_subject_manifest_rejects_transient_environment_or_build_paths(
    tmp_path, transient
):
    path = tmp_path / transient / "generated.bin"
    path.parent.mkdir()
    path.write_bytes(b"transient")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["."], "subject-source"
        )


@pytest.mark.parametrize("node_kind", ["symlink", "fifo", "git-symlink"])
def test_subject_manifest_rejects_symlink_and_special_nodes(tmp_path, node_kind):
    source = tmp_path / "subject.py"
    source.write_text("subject = True\n", encoding="utf-8")
    if node_kind == "symlink":
        (tmp_path / "linked.py").symlink_to(source)
    elif node_kind == "fifo":
        os.mkfifo(tmp_path / "source.fifo")
    else:
        outside = tmp_path / "worktree-admin"
        outside.mkdir()
        (tmp_path / ".git").symlink_to(outside, target_is_directory=True)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["."], "subject-source"
        )


def test_source_manifest_rejects_missing_and_overlapping_role_roots(tmp_path):
    tree = tmp_path / "tree"
    nested = tree / "nested"
    nested.mkdir(parents=True)
    (nested / "source.py").write_text("source = True\n", encoding="utf-8")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["missing"], "fixture-source"
        )
    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["tree", "tree/nested"], "fixture-source"
        )


def test_source_manifest_rejects_symlinked_role_root_parent(tmp_path):
    actual = tmp_path / "actual/nested"
    actual.mkdir(parents=True)
    (actual / "source.py").write_text("source = True\n", encoding="utf-8")
    (tmp_path / "linked").symlink_to(tmp_path / "actual", target_is_directory=True)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_MANIFEST"):
        evidence_module.build_tracked_source_manifest(
            tmp_path, ["linked/nested"], "fixture-source"
        )


def test_controller_and_subject_manifests_are_independent(tmp_path):
    controller = tmp_path / "controller"
    subject_a = tmp_path / "subject-a"
    subject_b = tmp_path / "subject-b"
    for root, content in ((subject_a, "a\n"), (subject_b, "b\n")):
        root.mkdir()
        (root / "source.py").write_text(content, encoding="utf-8")
    (controller / "src/p3_v3").mkdir(parents=True)
    (controller / "scripts/p3_v3").mkdir(parents=True)
    (controller / "src/p3_v3/controller.py").write_text("c\n", encoding="utf-8")
    (controller / "scripts/p3_v3/evidence.py").write_text("e\n", encoding="utf-8")
    (controller / "requirements-frozen.txt").write_text("r\n", encoding="utf-8")

    manifests = [
        evidence_module.build_tracked_source_manifest(
            controller,
            ["src/p3_v3", "scripts/p3_v3", "requirements-frozen.txt"],
            "controller-source",
        ),
        evidence_module.build_tracked_source_manifest(
            subject_a, ["."], "subject-source"
        ),
        evidence_module.build_tracked_source_manifest(
            subject_b, ["."], "subject-source"
        ),
    ]

    assert len({hashlib.sha256(canonical_json_bytes(item)).hexdigest() for item in manifests}) == 3


def test_validate_authority_lock_accepts_exact_schema():
    lock = _authority_lock()

    assert evidence_module.validate_authority_lock(lock) == lock


@pytest.mark.parametrize(
    ("path", "missing_key"),
    [
        (path, key)
        for path, keys in _AUTHORITY_OBJECT_SCHEMAS
        for key in sorted(keys)
    ],
)
def test_authority_lock_rejects_every_missing_top_level_or_nested_key(
    path, missing_key
):
    lock = _authority_lock()
    del _nested_value(lock, path)[missing_key]

    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize("path", [path for path, _keys in _AUTHORITY_OBJECT_SCHEMAS])
def test_authority_lock_rejects_extra_top_level_or_nested_key(path):
    lock = _authority_lock()
    _nested_value(lock, path)["unexpected"] = "not-authority"

    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize(
    ("collection", "mutation"),
    [
        ("subjects", "swapped"),
        ("subjects", "duplicated"),
        ("jobs", "swapped"),
        ("jobs", "duplicated"),
    ],
)
def test_authority_lock_rejects_swapped_or_duplicated_rows(collection, mutation):
    lock = _authority_lock()
    if mutation == "swapped":
        lock[collection].reverse()
    else:
        lock[collection][1] = copy.deepcopy(lock[collection][0])

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.validate_authority_lock(lock)


def test_authority_lock_rejects_duplicate_intent_templates_under_distinct_job_ids():
    lock = _authority_lock()
    lock["jobs"][1]["intent_template_sha256"] = lock["jobs"][0][
        "intent_template_sha256"
    ]

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("execution_class", "RELABELED"),
        ("p12_access_class", "UNKNOWN"),
        ("retry_trigger", "ALWAYS"),
        ("maximum_attempts", 4),
    ],
)
def test_authority_lock_rejects_invalid_job_enums_and_retry_policy(field, value):
    lock = _authority_lock()
    lock["jobs"][0][field] = value

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize(
    ("path", "field", "value", "error"),
    [
        (("controller_repository",), "base_commit", "A" * 40, "E_AUTHORITY_LOCK_SCHEMA"),
        (
            ("controller_repository",),
            "tracked_source_manifest_sha256",
            "A" * 64,
            "E_SHA256",
        ),
        (("jobs", 0), "maximum_attempts", True, "E_SCHEMA_TYPE"),
        ((), "schema_version", "P3_V3_AUTHORITY_LOCK_V2", "E_AUTHORITY_LOCK_SCHEMA"),
    ],
)
def test_authority_lock_rejects_invalid_hash_type_and_version(path, field, value, error):
    lock = _authority_lock()
    _nested_value(lock, path)[field] = value

    with pytest.raises(EvidenceError, match=error):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize("field", ["required_capabilities", "forbidden_credential_fields"])
def test_authority_lock_rejects_unsorted_or_duplicated_preflight_lists(field):
    lock = _authority_lock()
    lock["preflight"][field] = list(reversed(lock["preflight"][field]))

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize("field", ["token", "password", "authorization", "credential"])
def test_authority_lock_rejects_credential_metadata_without_echoing_value(field):
    lock = _authority_lock()
    secret = "TOP_SECRET_DO_NOT_ECHO"
    lock["preflight"][field] = secret

    with pytest.raises(EvidenceError, match="E_CREDENTIAL_METADATA") as caught:
        evidence_module.validate_authority_lock(lock)

    assert secret not in str(caught.value)


def test_authority_lock_rejects_raw_origin_userinfo_without_echoing_value():
    lock = _authority_lock()
    secret = "TOP_SECRET_DO_NOT_ECHO"
    lock["controller_repository"]["normalized_repository_identity"] = (
        f"https://audit-user:{secret}@github.com/example/controller"
    )

    with pytest.raises(EvidenceError, match="E_CREDENTIAL_METADATA") as caught:
        evidence_module.validate_authority_lock(lock)

    assert secret not in str(caught.value)


@pytest.mark.parametrize(
    ("field", "secret"),
    [
        ("api_token", "TOP_SECRET_COMPOSITE_KEY"),
        ("task_id", "Authorization: Bearer TOP_SECRET_BEARER"),
        ("task_id", "https://audit-user:TOP_SECRET_USERINFO@example.invalid/repo"),
        ("task_id", "https://TOP_SECRET_USERINFO@example.invalid/repo"),
    ],
)
def test_authority_lock_rejects_composite_keys_and_credential_shaped_values(
    field, secret
):
    lock = _authority_lock()
    lock[field] = secret

    with pytest.raises(EvidenceError, match="E_CREDENTIAL_METADATA") as caught:
        evidence_module.validate_authority_lock(lock)

    assert secret not in str(caught.value)


@pytest.mark.parametrize(
    ("value", "rejected"),
    [
        ("Bearer TOKEN_AT_START", True),
        ("prefix Bearer TOKEN_AFTER_SPACE", True),
        ("Authorization:Bearer TOKEN_AFTER_COLON", True),
        ("Authorization=Bearer TOKEN_AFTER_EQUALS", True),
        ("_Bearer TOKEN_AFTER_UNDERSCORE", True),
        ("nonbearer BENIGN_VALUE", False),
        ("icebearer BENIGN_VALUE", False),
        ("éBearer BENIGN_VALUE", False),
        ("中Bearer BENIGN_VALUE", False),
        ("９Bearer BENIGN_VALUE", False),
    ],
    ids=[
        "start",
        "space",
        "colon",
        "equals",
        "underscore",
        "nonbearer",
        "icebearer",
        "latin_unicode_letter",
        "cjk_letter",
        "fullwidth_digit",
    ],
)
def test_bearer_metadata_requires_a_non_alphanumeric_left_boundary(value, rejected):
    lock = _authority_lock()
    lock["task_id"] = value

    if rejected:
        with pytest.raises(EvidenceError, match="E_CREDENTIAL_METADATA") as caught:
            evidence_module.validate_authority_lock(lock)
        assert value not in str(caught.value)
    else:
        evidence_module.validate_authority_lock(lock)


@pytest.mark.parametrize(
    "mutation",
    [
        "preflight-identity",
        "preflight-commit",
        "preflight-tree",
        "environment-policy",
        "claim-ceiling",
        "subject-role-duplicate",
        "subject-manifest-duplicate",
    ],
)
def test_authority_lock_rejects_cross_field_divergence(mutation):
    lock = _authority_lock()
    if mutation == "preflight-identity":
        lock["preflight"]["normalized_repository_identity"] = "github.com/example/other"
    elif mutation == "preflight-commit":
        lock["preflight"]["base_commit"] = "9" * 40
    elif mutation == "preflight-tree":
        lock["preflight"]["base_tree"] = "9" * 40
    elif mutation == "environment-policy":
        lock["preflight"]["environment_policy_sha256"] = "9" * 64
    elif mutation == "claim-ceiling":
        lock["claim_policy"]["claim_ceiling_sha256"] = "9" * 64
    elif mutation == "subject-role-duplicate":
        lock["subjects"][1]["repository_role"] = lock["subjects"][0]["repository_role"]
    else:
        lock["subjects"][1]["tracked_source_manifest_sha256"] = lock["subjects"][0][
            "tracked_source_manifest_sha256"
        ]

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.validate_authority_lock(lock)


def test_load_authority_lock_rejects_changed_bytes_before_parsing_fields(tmp_path):
    path = tmp_path / "authority-lock.json"
    original_raw = canonical_json_bytes(_authority_lock())
    expected_sha256 = hashlib.sha256(original_raw).hexdigest()
    path.write_bytes(b"not-json\n")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_DIGEST"):
        evidence_module.load_authority_lock(path, expected_sha256)


def test_load_authority_lock_normalizes_malformed_expected_digest(tmp_path):
    path = tmp_path / "authority-lock.json"
    path.write_bytes(canonical_json_bytes(_authority_lock()))

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_DIGEST"):
        evidence_module.load_authority_lock(path, "not-a-sha256")


def test_load_authority_lock_rejects_matching_noncanonical_bytes(tmp_path):
    path = tmp_path / "authority-lock.json"
    raw = json.dumps(_authority_lock(), sort_keys=True, indent=2).encode("utf-8") + b"\n"
    path.write_bytes(raw)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.load_authority_lock(path, hashlib.sha256(raw).hexdigest())


def test_load_authority_lock_normalizes_matching_digest_lone_surrogate(tmp_path):
    path = tmp_path / "authority-lock.json"
    raw = b'{"bad":"\\ud800"}\n'
    path.write_bytes(raw)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        evidence_module.load_authority_lock(path, hashlib.sha256(raw).hexdigest())


def _job_derivation_fixture():
    policy = {
        "schema_version": "P3_V3_JOB_DERIVATION_POLICY_V1",
        "maximum_attempts": 3,
        "retry_trigger": "FAIL_INFRASTRUCTURE",
        "templates": [
            {
                "template_id": "controlled",
                "phase": "PHASE_2",
                "job_role": "PRIMARY_CONTROLLED",
                "object_source": "SUBJECT",
                "argv_template": [
                    "runner",
                    "${subject_id}",
                    "${object_id}",
                    "${evaluation_input_id}",
                    "${environment_id}",
                    "${repetition_id}",
                    "${protocol_sha256}",
                ],
                "cwd_role": "SUBJECT_ROOT",
                "environment_role": "CONTROLLED_ENV",
                "input_roles": ["EVALUATION_INPUT"],
                "seed_rule": "REPETITION_ID",
                "timeout_seconds": 30,
                "repetition_ids": [1],
                "execution_class": "NON_SCIENTIFIC_CONTROL",
                "p12_access_class": "FORBIDDEN",
            }
        ],
    }
    controller_manifest = {
        "schema_version": "P3_V3_TRACKED_SOURCE_MANIFEST_V1",
        "role": "controller-source",
        "files": [
            {
                "relative_path": "src/p3_v3/controller.py",
                "mode": "100644",
                "sha256": _digest("controller-source"),
            }
        ],
    }
    subject_manifest = {
        "schema_version": "P3_V3_TRACKED_SOURCE_MANIFEST_V1",
        "role": "subject-source",
        "files": [
            {
                "relative_path": "subject.py",
                "mode": "100644",
                "sha256": _digest("subject-source"),
            }
        ],
    }
    build_descriptor = {"schema_version": "BUILD_V1", "language": "python"}
    governing_raw = {
        field: canonical_json_bytes({"schema_version": "GOVERNING_V1", "role": field})
        for field in (
            "scientific_plan_sha256",
            "evidence_design_sha256",
            "authority_lock_design_sha256",
            "implementation_plan_sha256",
        )
    }
    governing_raw["scientific_plan_sha256"] = (
        ROOT
        / "docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md"
    ).read_bytes()
    governing_artifacts = {
        field: {
            "schema_version": "P3_V3_RAW_AUTHORITY_BYTES_V1",
            "relative_path": f"governing/{field}.json",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes_hex": raw.hex(),
        }
        for field, raw in governing_raw.items()
    }
    governing_artifacts["controller_implementation_manifest_sha256"] = (
        controller_manifest
    )
    protocol_artifacts = {
        field: {"schema_version": "PROTOCOL_ARTIFACT_V1", "role": field}
        for field in _PROTOCOL_AUTHORITY_KEYS
    }
    rq_spec_raw = (
        ROOT / "research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md"
    ).read_bytes()
    protocol_artifacts["rq_spec_sha256"] = {
        "schema_version": "P3_V3_RAW_AUTHORITY_BYTES_V1",
        "relative_path": "protocol/rq_spec.md",
        "sha256": hashlib.sha256(rq_spec_raw).hexdigest(),
        "bytes_hex": rq_spec_raw.hex(),
    }
    protocol_artifacts["claim_ceiling_sha256"] = _claim_authority()
    protocol_artifacts["job_derivation_policy_sha256"] = copy.deepcopy(policy)
    protocol = {
        field: (
            protocol_artifacts[field]["sha256"]
            if field == "rq_spec_sha256"
            else canonical_sha256(protocol_artifacts[field])
        )
        for field in _PROTOCOL_AUTHORITY_KEYS
    }
    registry_artifacts = {
        "adapter_registry_sha256": {
            "schema_version": "ADAPTER_REGISTRY_V1",
            "implementations": ["PYTHON_PEP517_V1"],
        },
        "input_generator_registry_sha256": {
            "schema_version": "INPUT_GENERATOR_REGISTRY_V1",
            "implementations": ["DETERMINISTIC_COMMON_V1"],
        },
    }
    registries = {
        field: canonical_sha256(registry_artifacts[field])
        for field in _REGISTRY_AUTHORITY_KEYS
    }
    prepared = {
        "controller_repository": {
            "normalized_repository_identity": "github.com/example/controller",
            "base_commit": "1" * 40,
            "base_tree": "2" * 40,
            "tracked_source_manifest_sha256": canonical_sha256(
                controller_manifest
            ),
        },
        "controller_manifest": controller_manifest,
        "subjects": [
            {
                "authority_row": {
                    "subject_id": "subject-a",
                    "repository_role": "CONTROLLED_A",
                    "normalized_repository_identity": "github.com/example/subject-a",
                    "base_commit": "3" * 40,
                    "base_tree": "4" * 40,
                    "tracked_source_manifest_sha256": canonical_sha256(
                        subject_manifest
                    ),
                    "build_descriptor_sha256": canonical_sha256(build_descriptor),
                    "adapter_id": "PYTHON_PEP517_V1",
                },
                "source_manifest": subject_manifest,
                "build_descriptor": build_descriptor,
                "adapter_discovery": {"adapter_id": "PYTHON_PEP517_V1"},
                "public_behavior_frame": {"subject_id": "subject-a"},
                "profiling_workload": {"subject_id": "subject-a"},
                "common_inputs": {"input_ids": ["e-common-0"]},
            }
        ],
        "governing_materials": {
            field: artifact.get("sha256", canonical_sha256(artifact))
            for field, artifact in governing_artifacts.items()
        },
        "governing_artifacts": governing_artifacts,
        "protocol": protocol,
        "protocol_artifacts": protocol_artifacts,
        "registries": registries,
        "registry_artifacts": registry_artifacts,
        "preflight": {
            "normalized_repository_identity": "github.com/example/controller",
            "base_commit": "1" * 40,
            "base_tree": "2" * 40,
            "dependency_lock_sha256": _digest("dependency-lock"),
            "environment_policy_sha256": protocol["environment_lock_sha256"],
            "required_capabilities": ["cpu"],
            "forbidden_credential_fields": [
                "authorization",
                "credential",
                "password",
                "token",
            ],
        },
        "claim_policy": {
            "claim_ceiling_sha256": protocol["claim_ceiling_sha256"],
            "required_status": "blocked",
            "rq_ids": ["RQ1", "RQ2", "RQ3", "RQ4"],
        },
        "objects": [
            {
                "object_source": "SUBJECT",
                "inventory_id": "subject-a:mut-1:e-common-0",
                "subject_id": "subject-a",
                "object_type": "SEMANTIC_MUTANT",
                "object_id": "mut-1",
                "mr_id": "mr-1",
                "evaluation_input_class": "E_COMMON",
                "evaluation_input_id": "e-common-0",
                "inputs": [{"role": "EVALUATION_INPUT", "sha256": "b" * 64}],
            }
        ],
        "environments": [
            {
                "environment_role": "CONTROLLED_ENV",
                "environment_id": "env-1",
                "environment_sha256": "c" * 64,
            }
        ],
        "job_derivation_policy": copy.deepcopy(policy),
    }
    return prepared, policy


def test_locked_job_derivation_expands_only_prepared_byte_bound_inventory():
    prepared, policy = _job_derivation_fixture()
    intents = evidence_module.derive_base_intents(prepared, policy)
    expected_job_id = canonical_sha256(
        {
            "template_id": "controlled",
            "object_source": "SUBJECT",
            "inventory_id": "subject-a:mut-1:e-common-0",
            "repetition_id": 1,
        }
    )
    assert intents == [
        {
            "job_id": expected_job_id,
            "protocol_sha256": prepared["protocol"]["protocol_sha256"],
            "phase": "PHASE_2",
            "argv": [
                "runner",
                "subject-a",
                "mut-1",
                "e-common-0",
                "env-1",
                "1",
                prepared["protocol"]["protocol_sha256"],
            ],
            "cwd_identity": "subject:subject-a",
            "environment_sha256": "c" * 64,
            "input_sha256": ["b" * 64],
            "seed": 1,
            "timeout_seconds": 30,
            "attempt": 1,
            "object_type": "SEMANTIC_MUTANT",
            "object_id": "mut-1",
            "mr_id": "mr-1",
            "evaluation_input_class": "E_COMMON",
            "evaluation_input_id": "e-common-0",
            "repetition_id": 1,
            "environment_id": "env-1",
            "job_role": "PRIMARY_CONTROLLED",
        }
    ]
    intent = intents[0]
    assert evidence_module.derive_locked_jobs(prepared, policy) == [
        {
            "job_id": expected_job_id,
            "phase": "PHASE_2",
            "job_role": "PRIMARY_CONTROLLED",
            "object_identity": "SEMANTIC_MUTANT:mut-1",
            "input_identity_sha256": canonical_sha256(["b" * 64]),
            "intent_template_sha256": evidence_module.intent_template_sha256(
                intent
            ),
            "maximum_attempts": 3,
            "retry_trigger": "FAIL_INFRASTRUCTURE",
            "execution_class": "NON_SCIENTIFIC_CONTROL",
            "p12_access_class": "FORBIDDEN",
        }
    ]


@pytest.mark.parametrize("shape", ["caller_subset", "inconsistent_source_roles"])
def test_locked_job_derivation_requires_complete_uniform_input_roles(shape):
    prepared, policy = _job_derivation_fixture()
    if shape == "caller_subset":
        prepared["objects"][0]["inputs"].append(
            {"role": "SECOND_INPUT", "sha256": "d" * 64}
        )
    else:
        second = copy.deepcopy(prepared["objects"][0])
        second["inventory_id"] = "subject-a:mut-2:e-common-0"
        second["object_id"] = "mut-2"
        second["inputs"].append(
            {"role": "SECOND_INPUT", "sha256": "d" * 64}
        )
        prepared["objects"].append(second)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_INTENT"):
        evidence_module.derive_locked_jobs(prepared, policy)


@pytest.mark.parametrize(
    "caller_field",
    [
        "base_intents",
        "jobs",
        "intent",
        "completed_intent",
        "execution_class",
        "p12_access_class",
        "classes",
    ],
)
def test_authority_inputs_reject_caller_supplied_execution_authority_before_inventory(
    caller_field,
):
    prepared, policy = _job_derivation_fixture()
    prepared["objects"] = [{"not": "an inventory"}]
    prepared[caller_field] = (
        [] if caller_field in {"base_intents", "jobs", "classes"} else {}
    )

    with pytest.raises(EvidenceError, match="E_AUTHORITY_INPUTS"):
        evidence_module.derive_base_intents(prepared, policy)


@pytest.mark.parametrize("source", ["subject", "protocol", "registry", "environment"])
def test_locked_job_derivation_changes_when_prepared_authority_changes(source):
    prepared, policy = _job_derivation_fixture()
    original_intent = evidence_module.derive_base_intents(prepared, policy)[0]
    original_job = evidence_module.derive_locked_jobs(prepared, policy)[0]
    changed = copy.deepcopy(prepared)
    if source == "subject":
        changed["objects"][0]["object_id"] = "mut-2"
    elif source == "protocol":
        artifact = {"schema_version": "PROTOCOL_ARTIFACT_V1", "role": "changed"}
        changed["protocol_artifacts"]["protocol_sha256"] = artifact
        changed["protocol"]["protocol_sha256"] = canonical_sha256(artifact)
    elif source == "registry":
        changed["objects"][0]["inputs"][0]["sha256"] = "e" * 64
    else:
        changed["environments"][0]["environment_sha256"] = "f" * 64

    changed_intent = evidence_module.derive_base_intents(changed, policy)[0]
    changed_job = evidence_module.derive_locked_jobs(changed, policy)[0]
    assert changed_intent != original_intent
    assert changed_job != original_job


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("object_source", "UNAVAILABLE"),
        ("input_roles", ["UNAVAILABLE"]),
        ("environment_role", "UNAVAILABLE"),
    ],
)
def test_locked_job_derivation_rejects_unavailable_prepared_role(field, value):
    prepared, policy = _job_derivation_fixture()
    policy["templates"][0][field] = value
    prepared["protocol"]["job_derivation_policy_sha256"] = canonical_sha256(policy)
    prepared["job_derivation_policy"] = copy.deepcopy(policy)
    prepared["protocol_artifacts"]["job_derivation_policy_sha256"] = copy.deepcopy(
        policy
    )

    with pytest.raises(EvidenceError, match="E_AUTHORITY_INTENT"):
        evidence_module.derive_locked_jobs(prepared, policy)


def test_locked_job_derivation_rejects_reduced_protocol_mapping():
    prepared, policy = _job_derivation_fixture()
    del prepared["protocol"]["rq_spec_sha256"]

    with pytest.raises(EvidenceError, match="E_AUTHORITY_INTENT"):
        evidence_module.derive_base_intents(prepared, policy)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("execution_class", "REAL_SCIENTIFIC"),
        ("p12_access_class", "REQUIRED"),
    ],
)
def test_locked_job_derivation_rejects_locally_resealed_class_relabel(field, value):
    prepared, policy = _job_derivation_fixture()
    policy["templates"][0][field] = value
    prepared["protocol"]["job_derivation_policy_sha256"] = canonical_sha256(policy)

    with pytest.raises(
        EvidenceError, match="E_AUTHORITY_(EXECUTION_CLASS|INTENT)"
    ):
        evidence_module.derive_locked_jobs(prepared, policy)


@pytest.mark.parametrize("authority", ["subject", "registry"])
def test_locked_job_derivation_rejects_stale_top_level_authority(authority):
    prepared, policy = _job_derivation_fixture()
    if authority == "subject":
        prepared["subjects"][0]["authority_row"][
            "tracked_source_manifest_sha256"
        ] = "f" * 64
    else:
        prepared["registries"]["adapter_registry_sha256"] = "f" * 64

    with pytest.raises(EvidenceError, match="E_AUTHORITY_INTENT"):
        evidence_module.derive_base_intents(prepared, policy)


def _init_authority_repo(root: Path, origin: str) -> None:
    _run_git(root, "init")
    _run_git(root, "config", "user.name", "Authority Fixture")
    _run_git(root, "config", "user.email", "authority@example.invalid")
    _run_git(root, "remote", "add", "origin", origin)
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-m", "authority fixture")


def _authority_freeze_fixture(tmp_path: Path) -> tuple[Path, dict, dict[str, Path]]:
    controller = tmp_path / "controller"
    subject = tmp_path / "subject"
    for root in (controller, subject):
        root.mkdir()

    controller_source = controller / "src/p3_v3/controller.py"
    controller_cli = controller / "scripts/p3_v3/evidence.py"
    dependency_lock = controller / "requirements-frozen.txt"
    controller_source.parent.mkdir(parents=True)
    controller_cli.parent.mkdir(parents=True)
    controller_source.write_text("CONTROLLER = True\n", encoding="utf-8")
    controller_cli.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    controller_cli.chmod(controller_cli.stat().st_mode | stat.S_IXUSR)
    dependency_lock.write_text("pytest==8.4.2\n", encoding="utf-8")

    adapter_root = controller / "registries/adapters"
    adapter_root.mkdir(parents=True)
    adapter_registry = _adapter_registry(adapter_root)
    adapter_prefix = adapter_root.relative_to(controller)
    for row in adapter_registry["adapters"]:
        row["implementation_path"] = (
            adapter_prefix / row["implementation_path"]
        ).as_posix()
    adapter_body = {
        key: value
        for key, value in adapter_registry.items()
        if key != "artifact_sha256"
    }
    adapter_registry["artifact_sha256"] = canonical_sha256(adapter_body)
    adapter_registry_path = adapter_root / "registry.json"
    write_canonical_json(adapter_registry_path, adapter_registry, exclusive=True)

    generator_root = controller / "registries/input_generators"
    shutil.copytree(
        Path(__file__).resolve().parent / "fixtures/input_generators",
        generator_root,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    generator_registry_path = generator_root / "registry.json"
    generator_registry = json.loads(
        generator_registry_path.read_text(encoding="utf-8")
    )
    generator_prefix = generator_root.relative_to(controller)
    for row in generator_registry["generators"]:
        row["implementation_path"] = (
            generator_prefix / row["implementation_path"]
        ).as_posix()
    generator_body = {
        key: value
        for key, value in generator_registry.items()
        if key != "artifact_sha256"
    }
    generator_registry["artifact_sha256"] = canonical_sha256(generator_body)
    write_canonical_json(
        generator_registry_path, generator_registry, exclusive=False
    )

    governing_paths: dict[str, str] = {}
    governing_files: dict[str, Path] = {}
    for role in (
        "scientific_plan",
        "evidence_design",
        "authority_lock_design",
        "implementation_plan",
    ):
        path = controller / f"authorities/governing/{role}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        if role == "scientific_plan":
            path.write_bytes(
                (ROOT / "docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md").read_bytes()
            )
        elif role == "evidence_design":
            path.write_bytes(
                (ROOT / "docs/superpowers/specs/2026-08-08-p3-v3-evidence-foundation-design.md").read_bytes()
            )
        else:
            path.write_bytes(f"# {role}\nfixture bytes\n".encode())
        governing_paths[role] = path.relative_to(controller).as_posix()
        governing_files[role] = path

    protocol_root = controller / "authorities/protocol"
    protocol_root.mkdir(parents=True)
    policy = {
        "schema_version": "P3_V3_JOB_DERIVATION_POLICY_V1",
        "maximum_attempts": 3,
        "retry_trigger": "FAIL_INFRASTRUCTURE",
        "templates": [
            {
                "template_id": "subject-control",
                "phase": "PHASE_0",
                "job_role": "PRIMARY_CONTROLLED",
                "object_source": "SUBJECT",
                "argv_template": [
                    "controller",
                    "${subject_id}",
                    "${object_id}",
                    "${environment_id}",
                    "${repetition_id}",
                ],
                "cwd_role": "SUBJECT_ROOT",
                "environment_role": "CONTROLLED_ENV",
                "input_roles": [
                    "ADAPTER_REGISTRY",
                    "BUILD_DESCRIPTOR",
                    "COMMON_INPUT_INVENTORY",
                    "INPUT_GENERATOR_REGISTRY",
                    "PUBLIC_BEHAVIOR_FRAME",
                    "SOURCE_MANIFEST",
                ],
                "seed_rule": "NONE",
                "timeout_seconds": 10,
                "repetition_ids": [1],
                "execution_class": "NON_SCIENTIFIC_CONTROL",
                "p12_access_class": "FORBIDDEN",
            }
        ],
    }
    environment_lock = {
        "schema_version": "P3_V3_ENVIRONMENT_LOCK_V1",
        "required_capabilities": ["cpu"],
        "forbidden_credential_fields": [
            "authorization",
            "credential",
            "password",
            "token",
        ],
        "environments": [
            {
                "environment_role": "CONTROLLED_ENV",
                "environment_id": "fixture-env",
                "environment_sha256": _digest("fixture-env"),
            }
        ],
    }
    p12_contract = {
        "schema_version": "P3_V3_P12_CONTRACT_V1",
        "synthetic_cases": [],
    }
    claim_ceiling = _claim_authority()
    protocol_artifacts: dict[str, dict | bytes] = {
        role: {"schema_version": "P3_V3_PROTOCOL_ARTIFACT_V1", "role": role}
        for role in (
            "operator_catalogue",
            "mr_policy",
            "site_policy",
            "analysis_spec",
            "package_policy",
        )
    }
    protocol_artifacts["rq_spec"] = (
        ROOT / "research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md"
    ).read_bytes()
    protocol_artifacts.update(
        {
            "claim_ceiling": claim_ceiling,
            "p12_contract": p12_contract,
            "environment_lock": environment_lock,
            "job_derivation_policy": policy,
        }
    )
    protocol_paths: dict[str, str] = {}
    for role, artifact in protocol_artifacts.items():
        suffix = "md" if role == "rq_spec" else "json"
        path = protocol_root / f"{role}.{suffix}"
        if isinstance(artifact, bytes):
            path.write_bytes(artifact)
        else:
            write_canonical_json(path, artifact, exclusive=True)
        protocol_paths[role] = path.relative_to(controller).as_posix()

    protocol_hashes = {
        f"{role}_sha256": (
            hashlib.sha256(artifact).hexdigest()
            if isinstance(artifact, bytes)
            else canonical_sha256(artifact)
        )
        for role, artifact in protocol_artifacts.items()
        if role != "job_derivation_policy"
    }
    protocol_hashes.update(
        {
            "adapter_registry_sha256": canonical_sha256(adapter_registry),
            "input_generator_registry_sha256": canonical_sha256(
                generator_registry
            ),
        }
    )
    protocol = protocol_root / "protocol.json"
    _write_protocol(protocol, _protocol_body(**protocol_hashes))
    protocol_paths["protocol"] = protocol.relative_to(controller).as_posix()

    discovery = {
        "source_files": ["subject.py"],
        "declarations": [
            {
                "category": "PUBLIC_API",
                "provenance_path": "subject.py",
                "provenance_span_or_key": "solve",
                "entrypoint": "subject:solve",
                "normalized_entrypoint": "subject:solve",
                "declared_inputs": {"kind": "array"},
                "declared_input_schema_sha256": "a" * 64,
                "static_dependency_tags": [],
                "prerequisites": [],
            }
        ],
        "public_schemas": [
            {
                "schema_kind": "JSON_SCHEMA_DRAFT2020_12_V1",
                "raw_schema": {"type": "array", "items": {"type": "number"}},
                "provenance_path": "subject.py",
                "provenance_span_or_key": "input-schema",
            }
        ],
        "sites": [
            {
                "path": "subject.py",
                "symbol": "solve",
                "start_line": 1,
                "start_col": 0,
                "end_line": 2,
                "end_col": 1,
            }
        ],
    }
    build_descriptor = {"ecosystem": "python", "manifest_path": "discovery.json"}
    (subject / "subject.py").write_text("def solve(value):\n    return value\n", encoding="utf-8")
    write_canonical_json(subject / "discovery.json", discovery, exclusive=True)
    write_canonical_json(subject / "build.json", build_descriptor, exclusive=True)

    _init_authority_repo(controller, SECRET_ORIGIN)
    _init_authority_repo(
        subject,
        "git@github.com:example/subject-fixture.git",
    )
    inputs = {
        "schema_version": "P3_V3_AUTHORITY_INPUTS_V1",
        "task_id": "p3-v3-freeze-fixture",
        "subjects": [
            {
                "subject_id": "subject-a",
                "repository_role": "CONTROLLED_A",
                "root": str(subject),
                "build_descriptor_path": "build.json",
                "adapter_id": "PYTHON_PEP517_V1",
            }
        ],
        "governing_material_paths": governing_paths,
        "protocol_artifact_paths": protocol_paths,
        "registry_artifact_paths": {
            "adapter_registry": adapter_registry_path.relative_to(controller).as_posix(),
            "input_generator_registry": generator_registry_path.relative_to(
                controller
            ).as_posix(),
        },
    }
    return controller, inputs, governing_files


def test_authority_determinism_freezes_real_bytes_and_derived_inventory(tmp_path):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    first = evidence_module.build_authority_lock(controller, inputs)
    reordered = dict(reversed(list(inputs.items())))
    second = evidence_module.build_authority_lock(controller, reordered)

    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert first["controller_repository"]["normalized_repository_identity"] == SECRET_IDENTITY
    assert first["subjects"][0]["normalized_repository_identity"] == (
        "github.com/example/subject-fixture"
    )
    assert first["jobs"]
    assert SECRET_ORIGIN.encode() not in canonical_json_bytes(first)


def test_freeze_accepts_nested_registries_with_controller_root_relative_implementations(
    tmp_path,
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    registry_fields = (
        ("adapter_registry", "adapters"),
        ("input_generator_registry", "generators"),
    )
    registries: dict[str, dict] = {}
    for field, rows_field in registry_fields:
        relative = inputs["registry_artifact_paths"][field]
        path = controller / relative
        registry = json.loads(path.read_text(encoding="utf-8"))
        assert all(
            row["implementation_path"].startswith("registries/")
            for row in registry[rows_field]
        )
        registries[field] = registry

    lock = evidence_module.build_authority_lock(controller, inputs)

    assert lock["registries"] == {
        "adapter_registry_sha256": canonical_sha256(
            registries["adapter_registry"]
        ),
        "input_generator_registry_sha256": canonical_sha256(
            registries["input_generator_registry"]
        ),
    }


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "extra",
        "duplicate_subject",
        "reordered_subjects",
        "unsafe_artifact_path",
        "unsafe_build_path",
        "unsafe_subject_root",
        "duplicate_cross_path",
        "base_intents",
        "intent_template_sha256",
        "execution_class",
        "p12_access_class",
    ],
)
def test_freeze_authority_inputs_reject_exact_schema_and_direct_intent_fields(
    tmp_path, monkeypatch, mutation
):
    _controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    candidate = copy.deepcopy(inputs)
    if mutation == "missing":
        del candidate["task_id"]
    elif mutation == "extra":
        candidate["extra"] = True
    elif mutation == "duplicate_subject":
        candidate["subjects"].append(copy.deepcopy(candidate["subjects"][0]))
    elif mutation == "reordered_subjects":
        second = copy.deepcopy(candidate["subjects"][0])
        second["subject_id"] = "subject-b"
        second["repository_role"] = "CONTROLLED_B"
        candidate["subjects"] = [second, candidate["subjects"][0]]
    elif mutation == "unsafe_artifact_path":
        candidate["protocol_artifact_paths"]["rq_spec"] = "../rq.json"
    elif mutation == "unsafe_build_path":
        candidate["subjects"][0]["build_descriptor_path"] = "../build.json"
    elif mutation == "unsafe_subject_root":
        candidate["subjects"][0]["root"] = "subject//checkout"
    elif mutation == "duplicate_cross_path":
        candidate["registry_artifact_paths"]["adapter_registry"] = candidate[
            "protocol_artifact_paths"
        ]["rq_spec"]
    else:
        candidate[mutation] = [] if mutation == "base_intents" else "forbidden"

    def forbid_git(*_args, **_kwargs):
        raise AssertionError("Authority Inputs must fail before any Git query")

    monkeypatch.setattr(evidence_module.subprocess, "run", forbid_git)
    with pytest.raises(EvidenceError, match="E_AUTHORITY_INPUTS"):
        evidence_module.build_authority_lock(tmp_path / "unused", candidate)


def test_authority_inputs_rejects_composite_credential_metadata_before_schema():
    candidate = {
        "schema_version": "P3_V3_AUTHORITY_INPUTS_V1",
        "task_id": "fixture",
        "subjects": [],
        "governing_material_paths": {},
        "protocol_artifact_paths": {},
        "registry_artifact_paths": {},
        "api_token": "TOP_SECRET_INPUT_TOKEN",
    }

    with pytest.raises(EvidenceError, match="E_CREDENTIAL_METADATA") as caught:
        evidence_module.validate_authority_inputs(candidate)

    assert "TOP_SECRET_INPUT_TOKEN" not in str(caught.value)


def test_freeze_zero_execution_allows_only_fixed_git_and_verified_in_process(
    tmp_path, monkeypatch
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    real_run = subprocess.run
    observed: list[tuple[str, ...]] = []
    captured_commits: list[str] = []

    def fixed_git_only(argv, *args, **kwargs):
        assert argv[0] == "/usr/bin/git"
        query = _fixed_git_query(argv)
        if query == ("rev-parse", "HEAD"):
            result = real_run(argv, *args, **kwargs)
            captured_commits.append(result.stdout.decode("ascii").strip())
        else:
            allowed_after_capture = {
                ("rev-parse", f"{captured_commits[-1]}^{{tree}}"),
                ("remote", "get-url", "origin"),
                ("ls-files", "--stage", "-z"),
            }
            assert query in allowed_after_capture
            result = real_run(argv, *args, **kwargs)
        observed.append(query)
        return result

    def forbidden_execution(*_args, **_kwargs):
        raise AssertionError("freeze reached an evidence/scientific execution path")

    monkeypatch.setattr(evidence_module.subprocess, "run", fixed_git_only)
    for name in (
        "run_preflight",
        "derive_subject_material",
        "recompute_p12_summary",
        "validate_mr_inventory",
    ):
        monkeypatch.setattr(evidence_module, name, forbidden_execution)

    evidence_module.build_authority_lock(controller, inputs)

    assert observed[0] == ("rev-parse", "HEAD")
    assert observed[4] == ("rev-parse", "HEAD")
    assert observed[1] == ("rev-parse", f"{captured_commits[0]}^{{tree}}")
    assert observed[5] == ("rev-parse", f"{captured_commits[1]}^{{tree}}")
    assert len(observed) == 8
    assert all(query[0] != "status" for query in observed)
    assert (
        real_run(
            ["/usr/bin/git", "-C", str(controller), "status", "--porcelain=v1"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout
        == ""
    )


@pytest.mark.parametrize(
    "failure", ["nonzero", "dirty", "mode", "malformed", "stderr", "divergence"]
)
def test_freeze_authority_fails_closed_on_git_checkout_anomalies(
    tmp_path, monkeypatch, failure
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    if failure == "dirty":
        (controller / "src/p3_v3/controller.py").write_text("dirty\n", encoding="utf-8")
    elif failure == "mode":
        tracked = controller / "src/p3_v3/controller.py"
        tracked.chmod(tracked.stat().st_mode | stat.S_IXUSR)
    elif failure == "divergence":
        (controller / "src/p3_v3/untracked.py").write_text("untracked\n", encoding="utf-8")
    else:
        real_run = subprocess.run

        def faulty_git(argv, *args, **kwargs):
            if _fixed_git_query(argv) == ("rev-parse", "HEAD"):
                if failure == "nonzero":
                    return subprocess.CompletedProcess(argv, 1, b"", b"failure")
                if failure == "stderr":
                    return subprocess.CompletedProcess(argv, 0, b"1" * 40 + b"\n", b"warning")
                return subprocess.CompletedProcess(argv, 0, b"not-an-object\n", b"")
            return real_run(argv, *args, **kwargs)

        monkeypatch.setattr(evidence_module.subprocess, "run", faulty_git)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module.build_authority_lock(controller, inputs)


def test_fixed_git_stage_inventory_reports_exact_live_blob_and_mode(tmp_path):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)

    git = evidence_module._run_fixed_git_queries(controller)

    path = "src/p3_v3/controller.py"
    row = next(item for item in git["tracked_entries"] if item["path"] == path)
    raw = (controller / path).read_bytes()
    expected_blob = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw,
        usedforsecurity=False,
    ).hexdigest()
    assert row == {
        "mode": "100644",
        "blob_oid": expected_blob,
        "stage": 0,
        "path": path,
    }


def test_fixed_git_queries_apply_deterministic_execution_sanitizers(
    tmp_path, monkeypatch
):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    expected_commit = _run_git(controller, "rev-parse", "HEAD")
    real_run = subprocess.run
    invocations: list[tuple[list[str], dict]] = []

    def capture(argv, *args, **kwargs):
        invocations.append((list(argv), dict(kwargs)))
        return real_run(argv, *args, **kwargs)

    monkeypatch.setattr(evidence_module.subprocess, "run", capture)

    evidence_module._run_fixed_git_queries(controller)

    assert len(invocations) == 4
    assert [_fixed_git_query(argv) for argv, _kwargs in invocations] == [
        ("rev-parse", "HEAD"),
        (
            "rev-parse",
            f"{expected_commit}^{{tree}}",
        ),
        ("remote", "get-url", "origin"),
        ("ls-files", "--stage", "-z"),
    ]
    for argv, kwargs in invocations:
        joined = "\0".join(argv)
        assert argv[0] == "/usr/bin/git"
        assert "core.fsmonitor=false" in joined
        assert "core.hooksPath=" in joined
        assert "core.pager=" in joined
        assert "core.pager=cat" not in joined
        assert "credential.helper=" in joined
        assert "status.showUntrackedFiles=all" not in joined
        assert "PATH" not in kwargs["env"]
        assert "GIT_WORK_TREE" not in kwargs["env"]
        assert kwargs["env"]["TMPDIR"] == "/tmp"
        assert kwargs["env"]["GIT_CONFIG_NOSYSTEM"] == "1"
        assert kwargs["env"]["GIT_OPTIONAL_LOCKS"] == "0"
        assert kwargs["env"]["GIT_TERMINAL_PROMPT"] == "0"
        assert kwargs["env"]["GIT_PAGER"] == ""
        assert kwargs["env"]["PAGER"] == ""


def test_fixed_git_queries_never_execute_git_from_caller_path(tmp_path, monkeypatch):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    marker = tmp_path / "caller-path-git-executed"
    malicious_bin = tmp_path / "malicious-bin"
    malicious_bin.mkdir()
    malicious_git = malicious_bin / "git"
    malicious_git.write_text(
        f"#!/bin/sh\n: > {marker.as_posix()}\nprintf 'forged-git\\n'\n",
        encoding="utf-8",
    )
    malicious_git.chmod(malicious_git.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", str(malicious_bin))

    git = evidence_module._run_fixed_git_queries(controller)

    assert git["tracked"]
    assert not marker.exists()


@pytest.mark.parametrize("unsafe_kind", ["symlink", "writable"])
def test_fixed_git_binary_validation_rejects_caller_controlled_nodes(
    tmp_path, monkeypatch, unsafe_kind
):
    executable = tmp_path / "git-real"
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    candidate = executable
    if unsafe_kind == "symlink":
        candidate = tmp_path / "git"
        candidate.symlink_to(executable)
    else:
        executable.chmod(0o777)
    monkeypatch.setitem(
        evidence_module._FIXED_GIT_BINARY_BY_PLATFORM,
        sys.platform,
        candidate,
    )

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module._validated_fixed_git_binary()


def test_fixed_git_queries_reject_repository_include_config(tmp_path):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    included = tmp_path / "outside-authority.config"
    included.write_text("[user]\n\tname = Included Authority\n", encoding="utf-8")
    _run_git(controller, "config", "include.path", str(included))

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module._run_fixed_git_queries(controller)


@pytest.mark.parametrize("driver", ["clean", "process"])
@pytest.mark.parametrize("section_style", ["modern", "legacy"])
def test_fixed_git_queries_reject_executable_filter_before_first_query(
    tmp_path, monkeypatch, driver, section_style
):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    attributes = controller / ".gitattributes"
    attributes.write_text(
        "src/p3_v3/controller.py filter=audit\n", encoding="utf-8"
    )
    _run_git(controller, "add", ".gitattributes")
    _run_git(controller, "commit", "-m", "filter fixture")
    marker = tmp_path / f"filter-{driver}-executed"
    executable_filter = tmp_path / f"filter-{driver}"
    executable_filter.write_text(
        f"#!/bin/sh\n: > {marker.as_posix()}\n"
        + ("/bin/cat\n" if driver == "clean" else "exit 1\n"),
        encoding="utf-8",
    )
    executable_filter.chmod(executable_filter.stat().st_mode | stat.S_IXUSR)
    if section_style == "modern":
        _run_git(
            controller, "config", f"filter.audit.{driver}", str(executable_filter)
        )
    else:
        local_config = controller / ".git/config"
        local_config.write_text(
            local_config.read_text(encoding="utf-8")
            + f"\n[filter.audit]\n\t{driver} = {executable_filter.as_posix()}\n",
            encoding="utf-8",
        )
    invocations: list[tuple[str, ...]] = []
    real_run = subprocess.run

    def capture(argv, *args, **kwargs):
        invocations.append(_fixed_git_query(argv))
        return real_run(argv, *args, **kwargs)

    monkeypatch.setattr(evidence_module.subprocess, "run", capture)
    caught: EvidenceError | None = None
    try:
        evidence_module._run_fixed_git_queries(controller)
    except EvidenceError as exc:
        caught = exc

    assert (invocations, marker.exists()) == ([], False)
    assert caught is not None
    assert caught.code == "E_AUTHORITY_GIT"


@pytest.mark.parametrize("section_style", ["modern", "legacy"])
@pytest.mark.parametrize("worktree_change", ["touch", "modify"])
@pytest.mark.parametrize("driver", ["clean", "process"])
def test_config_race_cannot_reintroduce_worktree_filter_execution(
    tmp_path, monkeypatch, section_style, worktree_change, driver
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    attributes = controller / ".gitattributes"
    attributes.write_text(
        "src/p3_v3/controller.py filter=audit\n", encoding="utf-8"
    )
    _run_git(controller, "add", ".gitattributes")
    _run_git(controller, "commit", "-m", "filter race fixture")
    tracked = controller / "src/p3_v3/controller.py"
    marker = tmp_path / f"raced-{section_style}-{driver}-executed"
    executable_filter = tmp_path / f"raced-{section_style}-{driver}"
    executable_filter.write_text(
        f"#!/bin/sh\n: > {marker.as_posix()}\n"
        + ("/bin/cat\n" if driver == "clean" else "exit 1\n"),
        encoding="utf-8",
    )
    executable_filter.chmod(executable_filter.stat().st_mode | stat.S_IXUSR)
    section = (
        '[filter "audit"]' if section_style == "modern" else "[filter.audit]"
    )
    included = tmp_path / f"raced-{section_style}-{driver}.config"
    included.write_text(
        f"[core]\n\tfsmonitor = {executable_filter.as_posix()}\n"
        f"{section}\n\t{driver} = {executable_filter.as_posix()}\n",
        encoding="utf-8",
    )
    original_config = (controller / ".git/config").read_text(encoding="utf-8")
    real_metadata = evidence_module._validated_local_git_metadata
    raced = False

    def race_after_metadata_validation(root):
        nonlocal raced
        metadata = real_metadata(root)
        if Path(root) == controller and not raced:
            raced = True
            (metadata / "config").write_text(
                original_config
                + f"\n[include]\n\tpath = {included.as_posix()}\n",
                encoding="utf-8",
            )
            if worktree_change == "touch":
                os.utime(tracked, None)
            else:
                tracked.write_text("CONTROLLER = 'raced'\n", encoding="utf-8")
        return metadata

    monkeypatch.setattr(
        evidence_module,
        "_validated_local_git_metadata",
        race_after_metadata_validation,
    )
    caught: EvidenceError | None = None
    try:
        evidence_module.build_authority_lock(controller, inputs)
    except EvidenceError as exc:
        caught = exc

    assert raced
    assert not marker.exists()
    if worktree_change == "touch":
        assert caught is None
    else:
        assert caught is not None
        assert caught.code == "E_AUTHORITY_GIT"


@pytest.mark.parametrize("indirection", ["gitdir_file", "objects_symlink"])
def test_fixed_git_queries_reject_out_of_root_git_metadata(tmp_path, indirection):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    metadata = tmp_path / "outside-controller-git-metadata"
    if indirection == "gitdir_file":
        (controller / ".git").rename(metadata)
        (controller / ".git").write_text(
            f"gitdir: {metadata.as_posix()}\n", encoding="utf-8"
        )
    else:
        (controller / ".git/objects").rename(metadata)
        (controller / ".git/objects").symlink_to(metadata, target_is_directory=True)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module._run_fixed_git_queries(controller)


def test_fixed_git_queries_do_not_execute_repository_fsmonitor(tmp_path):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    marker = tmp_path / "fsmonitor-executed"
    fsmonitor = tmp_path / "fsmonitor-hook"
    fsmonitor.write_text(
        f"#!/bin/sh\n: > {marker.as_posix()}\nexit 0\n", encoding="utf-8"
    )
    fsmonitor.chmod(fsmonitor.stat().st_mode | stat.S_IXUSR)
    _run_git(controller, "config", "core.fsmonitor", str(fsmonitor))

    evidence_module._run_fixed_git_queries(controller)

    assert not marker.exists()


def test_fixed_git_queries_reject_submodules_with_exactly_four_processes(
    tmp_path, monkeypatch
):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    submodule_source = tmp_path / "submodule-source"
    submodule_source.mkdir()
    (submodule_source / "tracked.txt").write_text("submodule\n", encoding="utf-8")
    _init_authority_repo(
        submodule_source, "git@github.com:example/submodule-fixture.git"
    )
    _run_git(
        controller,
        "-c",
        "protocol.file.allow=always",
        "submodule",
        "add",
        str(submodule_source),
        "vendor/submodule",
    )
    _run_git(controller, "commit", "-m", "tracked submodule fixture")
    submodule = controller / "vendor/submodule"
    marker = tmp_path / "submodule-fsmonitor-executed"
    fsmonitor = tmp_path / "submodule-fsmonitor"
    fsmonitor.write_text(
        f"#!/bin/sh\n: > {marker.as_posix()}\nexit 0\n", encoding="utf-8"
    )
    fsmonitor.chmod(fsmonitor.stat().st_mode | stat.S_IXUSR)
    _run_git(submodule, "config", "core.fsmonitor", str(fsmonitor))
    (submodule / "tracked.txt").write_text("dirty submodule\n", encoding="utf-8")
    invocations: list[tuple[str, ...]] = []
    real_run = subprocess.run

    def capture(argv, *args, **kwargs):
        invocations.append(_fixed_git_query(argv))
        return real_run(argv, *args, **kwargs)

    monkeypatch.setattr(evidence_module.subprocess, "run", capture)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module._run_fixed_git_queries(controller)

    assert len(invocations) == 4
    assert [query[0] for query in invocations] == [
        "rev-parse",
        "rev-parse",
        "remote",
        "ls-files",
    ]
    assert all(query[0] != "status" for query in invocations)
    assert not marker.exists()


def test_fixed_git_tree_query_stays_bound_to_commit_captured_first(
    tmp_path, monkeypatch
):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    first_commit = _run_git(controller, "rev-parse", "HEAD")
    tracked_path = controller / "src/p3_v3/controller.py"
    tracked_path.write_text("CONTROLLER = 'second-commit'\n", encoding="utf-8")
    _run_git(controller, "add", tracked_path.relative_to(controller).as_posix())
    _run_git(controller, "commit", "-m", "second authority commit")
    second_commit = _run_git(controller, "rev-parse", "HEAD")
    _run_git(controller, "checkout", "--detach", first_commit)
    real_run = subprocess.run
    switched = False

    def switch_head_after_first_query(argv, *args, **kwargs):
        nonlocal switched
        result = real_run(argv, *args, **kwargs)
        if _fixed_git_query(argv) == ("rev-parse", "HEAD") and not switched:
            switched = True
            real_run(
                ["git", "-C", str(controller), "checkout", "--detach", second_commit],
                capture_output=True,
                check=True,
            )
        return result

    monkeypatch.setattr(evidence_module.subprocess, "run", switch_head_after_first_query)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module._run_fixed_git_queries(controller)
    assert switched


def test_git_mode_projection_rejects_owner_to_group_execute_race(
    tmp_path, monkeypatch
):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    relative = "src/p3_v3/controller.py"
    tracked_path = controller / relative
    tracked_path.chmod(tracked_path.stat().st_mode | stat.S_IXUSR)
    _run_git(controller, "add", relative)
    _run_git(controller, "commit", "-m", "owner executable authority")
    git = evidence_module._run_fixed_git_queries(controller)
    real_reader = evidence_module._read_checkout_file_snapshot

    def group_execute_snapshot(directory_fd, name, relative_path):
        raw, mode = real_reader(directory_fd, name, relative_path)
        if relative_path == relative:
            mode = (mode & ~stat.S_IXUSR) | stat.S_IXGRP
        return raw, mode

    monkeypatch.setattr(
        evidence_module, "_read_checkout_file_snapshot", group_execute_snapshot
    )

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module._capture_git_checkout_snapshot(
            controller, git["tracked_entries"]
        )


@pytest.mark.parametrize(
    "record",
    [
        b"120000 " + b"1" * 40 + b" 0\tlinked.py\0",
        b"100644 " + b"1" * 39 + b" 0\tsource.py\0",
        b"100644 " + b"1" * 40 + b" 1\tsource.py\0",
        b"100644 " + b"1" * 40 + b" 0\t../escape.py\0",
    ],
)
def test_fixed_git_stage_inventory_rejects_nonregular_or_malformed_rows(
    tmp_path, monkeypatch, record
):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    real_run = subprocess.run

    def malformed_stage(argv, *args, **kwargs):
        if _fixed_git_query(argv) == ("ls-files", "--stage", "-z"):
            return subprocess.CompletedProcess(argv, 0, record, b"")
        return real_run(argv, *args, **kwargs)

    monkeypatch.setattr(evidence_module.subprocess, "run", malformed_stage)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module._run_fixed_git_queries(controller)


def test_freeze_rejects_tracked_live_byte_drift_after_stage_inventory(
    tmp_path, monkeypatch
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    tracked_path = controller / "src/p3_v3/controller.py"
    real_run = subprocess.run
    drifted = False

    def drift_after_inventory(argv, *args, **kwargs):
        nonlocal drifted
        result = real_run(argv, *args, **kwargs)
        if _fixed_git_query(argv) == ("ls-files", "--stage", "-z") and not drifted:
            drifted = True
            tracked_path.write_text("CONTROLLER = 'drifted'\n", encoding="utf-8")
        return result

    monkeypatch.setattr(evidence_module.subprocess, "run", drift_after_inventory)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module.build_authority_lock(controller, inputs)
    assert drifted


def test_checkout_captures_each_tracked_file_once_for_all_authority_derivations(
    tmp_path, monkeypatch
):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    real_reader = evidence_module._read_checkout_file_snapshot
    reads: dict[str, int] = {}

    def counting_reader(directory_fd, name, relative_path):
        reads[relative_path] = reads.get(relative_path, 0) + 1
        return real_reader(directory_fd, name, relative_path)

    monkeypatch.setattr(
        evidence_module, "_read_checkout_file_snapshot", counting_reader
    )

    _repository, manifest, tracked, snapshot = evidence_module._checkout_authority(
        controller,
        evidence_module._CONTROLLER_ROLE_ROOTS,
        "controller-source",
    )

    assert set(reads) == set(tracked)
    assert all(count == 1 for count in reads.values())
    assert [row["relative_path"] for row in manifest["files"]] == [
        path
        for path in tracked
        if any(
            path == root or path.startswith(f"{root}/")
            for root in evidence_module._CONTROLLER_ROLE_ROOTS
        )
    ]
    assert [entry.relative_path for entry in snapshot.entries] == list(tracked)


@pytest.mark.parametrize(
    ("node_kind", "relative"),
    [
        ("regular", "ignored.txt"),
        ("directory", "ignored-dir"),
        ("transient", "build/generated.bin"),
        ("symlink", "ignored-link"),
        ("fifo", "ignored.fifo"),
    ],
)
def test_checkout_snapshot_rejects_every_ignored_non_git_node(
    tmp_path, monkeypatch, node_kind, relative
):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    candidate = controller / relative
    candidate.parent.mkdir(parents=True, exist_ok=True)
    if node_kind in {"regular", "transient"}:
        candidate.write_bytes(b"ignored checkout bytes\n")
    elif node_kind == "directory":
        candidate.mkdir()
    elif node_kind == "symlink":
        candidate.symlink_to(controller / "src/p3_v3/controller.py")
    else:
        os.mkfifo(candidate)
    with (controller / ".git/info/exclude").open("a", encoding="utf-8") as handle:
        handle.write(f"/{relative}\n")
    real_reader = evidence_module._read_checkout_file_snapshot
    reads: dict[str, int] = {}

    def counting_reader(directory_fd, name, relative_path):
        reads[relative_path] = reads.get(relative_path, 0) + 1
        return real_reader(directory_fd, name, relative_path)

    monkeypatch.setattr(
        evidence_module, "_read_checkout_file_snapshot", counting_reader
    )
    caught: EvidenceError | None = None
    try:
        evidence_module._checkout_authority(
            controller,
            evidence_module._CONTROLLER_ROLE_ROOTS,
            "controller-source",
        )
    except EvidenceError as exc:
        caught = exc

    assert caught is not None
    assert caught.code == "E_AUTHORITY_GIT"
    if node_kind == "regular":
        assert reads[relative] == 1


def test_checkout_snapshot_rejects_tracked_transient_node(tmp_path):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    generated = controller / "build/generated.bin"
    generated.parent.mkdir()
    generated.write_bytes(b"tracked transient\n")
    _run_git(controller, "add", "-f", "build/generated.bin")
    _run_git(controller, "commit", "-m", "tracked transient fixture")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module._checkout_authority(
            controller,
            evidence_module._CONTROLLER_ROLE_ROOTS,
            "controller-source",
        )


def test_checkout_snapshot_never_follows_parent_swap_during_traversal(
    tmp_path, monkeypatch
):
    controller, _inputs, _governing = _authority_freeze_fixture(tmp_path)
    source = controller / "src"
    held_source = tmp_path / "held-controller-src"
    attack_source = tmp_path / "attack-controller-src"
    shutil.copytree(source, attack_source)
    relative = "src/p3_v3/controller.py"
    original_bytes = (source / "p3_v3/controller.py").read_bytes()
    attack_bytes = b"CONTROLLER = 'attacker-controlled'\n"
    (attack_source / "p3_v3/controller.py").write_bytes(attack_bytes)
    source_inode = source.stat().st_ino
    original_parent_inode = (source / "p3_v3").stat().st_ino
    real_scandir = os.scandir
    real_reader = evidence_module._read_checkout_file_snapshot
    raced = False
    observed_parent_inode: int | None = None
    observed_bytes: bytes | None = None

    def swap_parent_before_scan(target):
        nonlocal raced
        target_is_source_path = Path(target) == source if not isinstance(target, int) else False
        target_is_source_fd = (
            isinstance(target, int) and os.fstat(target).st_ino == source_inode
        )
        if not raced and (target_is_source_path or target_is_source_fd):
            source.rename(held_source)
            source.symlink_to(attack_source, target_is_directory=True)
            raced = True
        return real_scandir(target)

    def instrument_checkout_reader(directory_fd, name, relative_path):
        nonlocal observed_parent_inode, observed_bytes
        raw, mode = real_reader(directory_fd, name, relative_path)
        if relative_path == relative:
            observed_parent_inode = os.fstat(directory_fd).st_ino
            observed_bytes = raw
        return raw, mode

    monkeypatch.setattr(evidence_module.os, "scandir", swap_parent_before_scan)
    monkeypatch.setattr(
        evidence_module, "_read_checkout_file_snapshot", instrument_checkout_reader
    )

    repository, manifest, _tracked, snapshot = evidence_module._checkout_authority(
        controller,
        evidence_module._CONTROLLER_ROLE_ROOTS,
        "controller-source",
    )

    assert raced
    assert observed_parent_inode == original_parent_inode
    assert observed_parent_inode == (held_source / "p3_v3").stat().st_ino
    assert observed_bytes == original_bytes
    assert observed_bytes != attack_bytes
    assert snapshot.read_bytes(relative) == original_bytes
    row = next(item for item in manifest["files"] if item["relative_path"] == relative)
    assert row["sha256"] == hashlib.sha256(original_bytes).hexdigest()
    assert repository["tracked_source_manifest_sha256"] == canonical_sha256(manifest)


def test_checkout_snapshot_root_open_never_follows_swapped_parent(
    tmp_path, monkeypatch
):
    authority_parent = tmp_path / "authority-parent"
    authority_parent.mkdir()
    controller, _inputs, _governing = _authority_freeze_fixture(authority_parent)
    held_parent = tmp_path / "held-authority-parent"
    parent_inode = tmp_path.stat().st_ino
    real_run = subprocess.run
    real_open = os.open
    armed = False
    raced = False

    def arm_after_stage_inventory(argv, *args, **kwargs):
        nonlocal armed
        result = real_run(argv, *args, **kwargs)
        if _fixed_git_query(argv) == ("ls-files", "--stage", "-z"):
            armed = True
        return result

    def swap_parent_before_root_open(path, flags, *args, dir_fd=None, **kwargs):
        nonlocal raced
        full_root_open = Path(path) == controller
        component_root_open = (
            path == authority_parent.name
            and dir_fd is not None
            and os.fstat(dir_fd).st_ino == parent_inode
        )
        if armed and not raced and (full_root_open or component_root_open):
            authority_parent.rename(held_parent)
            authority_parent.symlink_to(held_parent, target_is_directory=True)
            raced = True
        return real_open(path, flags, *args, dir_fd=dir_fd, **kwargs)

    monkeypatch.setattr(evidence_module.subprocess, "run", arm_after_stage_inventory)
    monkeypatch.setattr(evidence_module.os, "open", swap_parent_before_root_open)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module._checkout_authority(
            controller,
            evidence_module._CONTROLLER_ROLE_ROOTS,
            "controller-source",
        )

    assert raced


def test_freeze_rejects_staged_tree_drift_after_identity_query(
    tmp_path, monkeypatch
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    relative = "src/p3_v3/controller.py"
    tracked_path = controller / relative
    real_run = subprocess.run
    drifted = False

    def stage_drift_after_identity(argv, *args, **kwargs):
        nonlocal drifted
        result = real_run(argv, *args, **kwargs)
        if _fixed_git_query(argv) == ("remote", "get-url", "origin") and not drifted:
            drifted = True
            tracked_path.write_text("CONTROLLER = 'staged-drift'\n", encoding="utf-8")
            real_run(
                ["git", "-C", str(controller), "add", relative],
                capture_output=True,
                check=True,
            )
        return result

    monkeypatch.setattr(evidence_module.subprocess, "run", stage_drift_after_identity)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module.build_authority_lock(controller, inputs)
    assert drifted


def test_authority_determinism_raw_governing_byte_drift_changes_lock(tmp_path):
    controller, inputs, governing = _authority_freeze_fixture(tmp_path)
    first = evidence_module.build_authority_lock(controller, inputs)
    governing["authority_lock_design"].write_bytes(b"changed authority bytes\n")
    _run_git(controller, "add", ".")
    _run_git(controller, "commit", "-m", "governing drift")
    second = evidence_module.build_authority_lock(controller, inputs)

    assert first["governing_materials"] != second["governing_materials"]
    assert canonical_json_bytes(first) != canonical_json_bytes(second)


def test_authority_determinism_coordinated_registry_drift_changes_objects(tmp_path):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    original = evidence_module.prepare_authority(controller, inputs)
    adapter_registry_path = controller / inputs["registry_artifact_paths"][
        "adapter_registry"
    ]
    adapter_registry = json.loads(adapter_registry_path.read_text(encoding="utf-8"))
    unused = next(
        row
        for row in adapter_registry["adapters"]
        if row["adapter_id"] == "CMAKE_CTEST_V1"
    )
    unused_source = controller / unused["implementation_path"]
    unused_source.write_text("# coordinated registry drift\n", encoding="utf-8")
    unused["source_sha256"] = hashlib.sha256(unused_source.read_bytes()).hexdigest()
    adapter_body = {
        key: value for key, value in adapter_registry.items() if key != "artifact_sha256"
    }
    adapter_registry["artifact_sha256"] = canonical_sha256(adapter_body)
    write_canonical_json(adapter_registry_path, adapter_registry, exclusive=False)

    protocol_path = controller / inputs["protocol_artifact_paths"]["protocol"]
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    protocol["adapter_registry_sha256"] = canonical_sha256(adapter_registry)
    protocol_body = {
        key: value for key, value in protocol.items() if key != "artifact_sha256"
    }
    protocol["artifact_sha256"] = canonical_sha256(protocol_body)
    write_canonical_json(protocol_path, protocol, exclusive=False)
    _run_git(controller, "add", ".")
    _run_git(controller, "commit", "-m", "coordinated registry drift")

    changed = evidence_module.prepare_authority(controller, inputs)

    assert changed["objects"] != original["objects"]


@pytest.mark.parametrize(
    ("drift", "target_role", "expected_changed_roles"),
    [
        (
            "tracked_subject_source",
            "SOURCE_MANIFEST",
            {
                "COMMON_INPUT_INVENTORY",
                "PUBLIC_BEHAVIOR_FRAME",
                "SOURCE_MANIFEST",
            },
        ),
        (
            "selected_registry",
            "ADAPTER_REGISTRY",
            {
                "ADAPTER_REGISTRY",
                "PUBLIC_BEHAVIOR_FRAME",
            },
        ),
        (
            "build_descriptor",
            "BUILD_DESCRIPTOR",
            {
                "BUILD_DESCRIPTOR",
                "COMMON_INPUT_INVENTORY",
                "PUBLIC_BEHAVIOR_FRAME",
                "SOURCE_MANIFEST",
            },
        ),
        (
            "public_behavior_frame",
            "PUBLIC_BEHAVIOR_FRAME",
            {
                "COMMON_INPUT_INVENTORY",
                "PUBLIC_BEHAVIOR_FRAME",
                "SOURCE_MANIFEST",
            },
        ),
        (
            "common_input_derivation",
            "COMMON_INPUT_INVENTORY",
            {"COMMON_INPUT_INVENTORY", "INPUT_GENERATOR_REGISTRY"},
        ),
    ],
)
def test_real_preparation_role_drift_changes_derived_intent_and_locked_job(
    tmp_path, drift, target_role, expected_changed_roles
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    subject = Path(inputs["subjects"][0]["root"])
    assert _run_git(controller, "status", "--porcelain=v1") == ""
    assert _run_git(subject, "status", "--porcelain=v1") == ""
    original = evidence_module.prepare_authority(controller, inputs)
    original_policy = original["job_derivation_policy"]
    original_intent = evidence_module.derive_base_intents(
        original, original_policy
    )[0]
    original_job = evidence_module.derive_locked_jobs(original, original_policy)[0]
    original_subject_object = next(
        item for item in original["objects"] if item["object_source"] == "SUBJECT"
    )
    original_roles = {
        item["role"]: item["sha256"] for item in original_subject_object["inputs"]
    }

    if drift == "tracked_subject_source":
        source = subject / "subject.py"
        source.write_text(
            source.read_text(encoding="utf-8") + "\n# tracked source drift\n",
            encoding="utf-8",
        )
        _run_git(subject, "add", ".")
        _run_git(subject, "commit", "-m", "tracked subject source drift")
    elif drift == "build_descriptor":
        descriptor_path = subject / inputs["subjects"][0]["build_descriptor_path"]
        descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
        descriptor["reverse"] = True
        write_canonical_json(descriptor_path, descriptor, exclusive=False)
        _run_git(subject, "add", ".")
        _run_git(subject, "commit", "-m", "build descriptor drift")
    elif drift == "public_behavior_frame":
        discovery_path = subject / "discovery.json"
        discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
        discovery["declarations"][0]["declared_input_schema_sha256"] = "b" * 64
        write_canonical_json(discovery_path, discovery, exclusive=False)
        _run_git(subject, "add", ".")
        _run_git(subject, "commit", "-m", "public behavior frame drift")
    elif drift == "selected_registry":
        registry_path = controller / inputs["registry_artifact_paths"][
            "adapter_registry"
        ]
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        selected = next(
            row
            for row in registry["adapters"]
            if row["adapter_id"] == "PYTHON_PEP517_V1"
        )
        implementation = controller / selected["implementation_path"]
        implementation.write_text(
            implementation.read_text(encoding="utf-8")
            + "\n# selected registry drift\n",
            encoding="utf-8",
        )
        selected["source_sha256"] = hashlib.sha256(
            implementation.read_bytes()
        ).hexdigest()
        registry_body = {
            key: value for key, value in registry.items() if key != "artifact_sha256"
        }
        registry["artifact_sha256"] = canonical_sha256(registry_body)
        write_canonical_json(registry_path, registry, exclusive=False)
        protocol_path = controller / inputs["protocol_artifact_paths"]["protocol"]
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        protocol["adapter_registry_sha256"] = canonical_sha256(registry)
        protocol_body = {
            key: value for key, value in protocol.items() if key != "artifact_sha256"
        }
        protocol["artifact_sha256"] = canonical_sha256(protocol_body)
        write_canonical_json(protocol_path, protocol, exclusive=False)
        _run_git(controller, "add", ".")
        _run_git(controller, "commit", "-m", "selected registry drift")
    else:
        registry_path = controller / inputs["registry_artifact_paths"][
            "input_generator_registry"
        ]
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        selected = next(
            row
            for row in registry["generators"]
            if row["generator_id"] == "JSON_SCHEMA_DRAFT2020_12_V1"
        )
        implementation = controller / selected["implementation_path"]
        implementation.write_text(
            implementation.read_text(encoding="utf-8").replace(
                'b"P3-INPUT-STREAM-v1"', 'b"P3-INPUT-STREAM-v2"'
            ),
            encoding="utf-8",
        )
        selected["source_sha256"] = hashlib.sha256(
            implementation.read_bytes()
        ).hexdigest()
        registry_body = {
            key: value for key, value in registry.items() if key != "artifact_sha256"
        }
        registry["artifact_sha256"] = canonical_sha256(registry_body)
        write_canonical_json(registry_path, registry, exclusive=False)
        protocol_path = controller / inputs["protocol_artifact_paths"]["protocol"]
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        protocol["input_generator_registry_sha256"] = canonical_sha256(registry)
        protocol_body = {
            key: value for key, value in protocol.items() if key != "artifact_sha256"
        }
        protocol["artifact_sha256"] = canonical_sha256(protocol_body)
        write_canonical_json(protocol_path, protocol, exclusive=False)
        _run_git(controller, "add", ".")
        _run_git(controller, "commit", "-m", "common input derivation drift")

    assert _run_git(controller, "status", "--porcelain=v1") == ""
    assert _run_git(subject, "status", "--porcelain=v1") == ""
    changed = evidence_module.prepare_authority(controller, inputs)
    changed_policy = changed["job_derivation_policy"]
    changed_intent = evidence_module.derive_base_intents(changed, changed_policy)[0]
    changed_job = evidence_module.derive_locked_jobs(changed, changed_policy)[0]
    changed_subject_object = next(
        item for item in changed["objects"] if item["object_source"] == "SUBJECT"
    )
    changed_roles = {
        item["role"]: item["sha256"] for item in changed_subject_object["inputs"]
    }

    assert changed_roles[target_role] != original_roles[target_role]
    assert {
        role
        for role in original_roles
        if changed_roles[role] != original_roles[role]
    } == expected_changed_roles
    assert original_intent["input_sha256"] == sorted(original_roles.values())
    assert changed_intent["input_sha256"] == sorted(changed_roles.values())
    assert original_roles[target_role] in original_intent["input_sha256"]
    assert changed_roles[target_role] in changed_intent["input_sha256"]
    assert changed_intent["input_sha256"] != original_intent["input_sha256"]
    assert changed_job["intent_template_sha256"] != original_job[
        "intent_template_sha256"
    ]
    assert changed_job != original_job


@pytest.mark.parametrize("untracked_role", ["authority_artifact", "implementation"])
def test_freeze_authority_rejects_ignored_untracked_authority_bytes(
    tmp_path, untracked_role
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    if untracked_role == "authority_artifact":
        untracked = controller / "authorities/governing/ignored-design.md"
        untracked.write_bytes(b"ignored but authority-bearing\n")
        inputs["governing_material_paths"]["authority_lock_design"] = (
            untracked.relative_to(controller).as_posix()
        )
    else:
        registry_path = controller / inputs["registry_artifact_paths"][
            "adapter_registry"
        ]
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        unused = next(
            row
            for row in registry["adapters"]
            if row["adapter_id"] == "CMAKE_CTEST_V1"
        )
        untracked = controller / unused["implementation_path"]
        _run_git(
            controller,
            "rm",
            "--cached",
            untracked.relative_to(controller).as_posix(),
        )
        _run_git(controller, "commit", "-m", "untrack ignored implementation")
    exclude = controller / ".git/info/exclude"
    with exclude.open("a", encoding="utf-8") as handle:
        handle.write(untracked.relative_to(controller).as_posix() + "\n")

    with pytest.raises(EvidenceError, match="E_AUTHORITY_GIT"):
        evidence_module.build_authority_lock(controller, inputs)


def test_freeze_authority_executes_generator_snapshot_not_replaced_path(
    tmp_path, monkeypatch
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    marker = tmp_path / "unverified-generator-ran"
    real_validate = evidence_module.validate_input_generator_registry
    registry_path = controller / inputs["registry_artifact_paths"][
        "input_generator_registry"
    ]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    entry = next(
        row
        for row in registry["generators"]
        if row["generator_id"] == "JSON_SCHEMA_DRAFT2020_12_V1"
    )
    source = controller / entry["implementation_path"]

    def replace_after_validation(registry, source_snapshot):
        validated = real_validate(registry, source_snapshot)
        source.write_text(
            "from pathlib import Path\n"
            "def generate(_schema, _seed):\n"
            f"    Path({str(marker)!r}).write_text('executed')\n"
            "    return {'failure_code': 'UNVERIFIED'}\n",
            encoding="utf-8",
        )
        return validated

    monkeypatch.setattr(
        evidence_module,
        "validate_input_generator_registry",
        replace_after_validation,
    )
    lock = evidence_module.build_authority_lock(controller, inputs)

    assert lock["jobs"]
    assert not marker.exists()


def test_concurrent_freezes_do_not_cross_snapshots_leak_state_or_write_pyc(
    tmp_path, monkeypatch, capsys
):
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first_controller, first_inputs, _ = _authority_freeze_fixture(first_root)
    second_controller, second_inputs, _ = _authority_freeze_fixture(second_root)
    real_build_common_inputs = evidence_module.build_common_inputs
    rendezvous = threading.Barrier(2)
    observed_snapshot_ids: list[int] = []
    observed_lock = threading.Lock()

    def synchronized_common_inputs(source_record, public_frame, registry):
        rendezvous.wait(timeout=10)
        with observed_lock:
            observed_snapshot_ids.append(id(registry["_implementation_snapshots"]))
        return real_build_common_inputs(source_record, public_frame, registry)

    monkeypatch.setattr(
        evidence_module, "build_common_inputs", synchronized_common_inputs
    )
    monkeypatch.setattr(sys, "dont_write_bytecode", False)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        first_future = executor.submit(
            evidence_module.build_authority_lock,
            first_controller,
            first_inputs,
        )
        second_future = executor.submit(
            evidence_module.build_authority_lock,
            second_controller,
            second_inputs,
        )
        first_lock = first_future.result(timeout=20)
        second_lock = second_future.result(timeout=20)

    assert first_lock["jobs"] and second_lock["jobs"]
    assert len(observed_snapshot_ids) == 2
    assert len(set(observed_snapshot_ids)) == 2
    assert sys.dont_write_bytecode is False
    assert capsys.readouterr() == ("", "")
    assert not list(first_controller.rglob("__pycache__"))
    assert not list(second_controller.rglob("__pycache__"))


def test_freeze_authority_relative_subject_root_uses_inputs_parent(
    tmp_path, monkeypatch
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    inputs["subjects"][0]["root"] = "subject"
    authority_inputs = tmp_path / "authority-inputs.json"
    output = tmp_path / "authority-lock.json"
    write_canonical_json(authority_inputs, inputs, exclusive=True)
    monkeypatch.chdir(tmp_path)

    lock = evidence_module.freeze_authority_lock(
        controller,
        Path("authority-inputs.json"),
        output,
    )

    assert lock["subjects"][0]["subject_id"] == "subject-a"


def test_freeze_rq_markdown_bytes_are_the_claim_verifiers_authority(tmp_path):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    rq_path = controller / inputs["protocol_artifact_paths"]["rq_spec"]
    rq_bytes = (
        ROOT / "research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md"
    ).read_bytes() + (
        b"\n<!-- verified byte-bound RQ authority fixture -->\n"
    )
    rq_path.write_bytes(rq_bytes)
    protocol_path = controller / inputs["protocol_artifact_paths"]["protocol"]
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    protocol["rq_spec_sha256"] = hashlib.sha256(rq_bytes).hexdigest()
    protocol_body = {
        key: value for key, value in protocol.items() if key != "artifact_sha256"
    }
    protocol["artifact_sha256"] = canonical_sha256(protocol_body)
    write_canonical_json(protocol_path, protocol, exclusive=False)
    _run_git(controller, "add", ".")
    _run_git(controller, "commit", "-m", "bind markdown rq authority")

    inputs_path = tmp_path / "authority-inputs.json"
    lock_path = tmp_path / "authority-lock.json"
    write_canonical_json(inputs_path, inputs, exclusive=True)
    evidence_module.freeze_authority_lock(controller, inputs_path, lock_path)
    literal_lock_sha256 = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    lock = evidence_module.load_authority_lock(lock_path, literal_lock_sha256)

    claims = _blocked_claim_ledger("rq_spec.md")
    claims["rq_authority_sha256"] = lock["protocol"]["rq_spec_sha256"]
    claims["claim_authority_sha256"] = lock["protocol"][
        "claim_ceiling_sha256"
    ]
    claims_body = {
        key: value for key, value in claims.items() if key != "artifact_sha256"
    }
    claims["artifact_sha256"] = canonical_sha256(claims_body)
    claims_path = tmp_path / "claims.json"
    write_canonical_json(claims_path, claims, exclusive=True)
    claim_ceiling_path = (
        controller / inputs["protocol_artifact_paths"]["claim_ceiling"]
    )

    assert evidence_module._verify_claim_reconstruction(
        {
            "claims_raw": claims_path.read_bytes(),
            "indexed_paths": frozenset({"rq_spec.md"}),
            "protocol_artifact_bytes": {
                "rq_spec_sha256": rq_path.read_bytes(),
                "claim_ceiling_sha256": claim_ceiling_path.read_bytes(),
            },
            "protocol": lock["protocol"],
            "authority_rq_ids": ["RQ1", "RQ2", "RQ3", "RQ4"],
        }
    ) == claims


@pytest.mark.parametrize(
    "headings",
    [
        [
            ("RQ1", "one"),
            ("RQ2", "two"),
            ("RQ3", "three"),
            ("RQ4", "four"),
            ("RQ4", "four"),
        ],
        [("RQ2", "two"), ("RQ1", "one"), ("RQ3", "three"), ("RQ4", "four")],
        [
            ("RQ1", "one"),
            ("RQ2", "two"),
            ("RQ3", "three"),
            ("RQ4", "four"),
            ("RQ2", "contradictory"),
        ],
    ],
    ids=["duplicate", "reordered", "contradictory_duplicate"],
)
def test_rq_authority_rejects_nonexact_original_heading_sequence(headings):
    raw = "\n".join(
        f"### {rq} — {title}" for rq, title in headings
    ).encode()

    with pytest.raises(EvidenceError, match="E_CLAIM_SET"):
        evidence_module._rq_ids_from_spec_bytes(raw)


def test_build_authority_lock_relative_subject_root_uses_controller_root(tmp_path):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    subject_in_controller = controller / "subject-api"
    shutil.copytree(tmp_path / "subject", subject_in_controller)
    with (controller / ".git/info/exclude").open("a", encoding="utf-8") as handle:
        handle.write("subject-api/\n")
    inputs["subjects"][0]["root"] = "subject-api"

    lock = evidence_module.build_authority_lock(controller, inputs)

    assert lock["subjects"][0]["subject_id"] == "subject-a"


@pytest.mark.parametrize("nested_name", ["nested-subject", "build"])
def test_freeze_authority_carves_out_resolved_subject_nested_in_controller(
    tmp_path, nested_name
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    subject_in_controller = controller / nested_name
    shutil.copytree(tmp_path / "subject", subject_in_controller)
    with (controller / ".git/info/exclude").open("a", encoding="utf-8") as handle:
        handle.write(f"{nested_name}/\n")
    inputs["subjects"][0]["root"] = f"controller/{nested_name}"
    authority_inputs = tmp_path / "authority-inputs.json"
    output = tmp_path / "authority-lock.json"
    write_canonical_json(authority_inputs, inputs, exclusive=True)

    lock = evidence_module.freeze_authority_lock(
        controller,
        authority_inputs,
        output,
    )

    assert output.exists()
    assert lock["subjects"][0]["subject_id"] == "subject-a"


def test_freeze_authority_rejects_semantically_invalid_claim_ceiling(tmp_path):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    ceiling_path = controller / inputs["protocol_artifact_paths"]["claim_ceiling"]
    ceiling = json.loads(ceiling_path.read_text(encoding="utf-8"))
    ceiling["claims"][0]["initial_status"] = "accepted"
    ceiling_body = {
        key: value for key, value in ceiling.items() if key != "artifact_sha256"
    }
    ceiling["artifact_sha256"] = canonical_sha256(ceiling_body)
    write_canonical_json(ceiling_path, ceiling, exclusive=False)

    protocol_path = controller / inputs["protocol_artifact_paths"]["protocol"]
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    protocol["claim_ceiling_sha256"] = canonical_sha256(ceiling)
    protocol_body = {
        key: value for key, value in protocol.items() if key != "artifact_sha256"
    }
    protocol["artifact_sha256"] = canonical_sha256(protocol_body)
    write_canonical_json(protocol_path, protocol, exclusive=False)
    _run_git(controller, "add", ".")
    _run_git(controller, "commit", "-m", "invalid claim ceiling semantics")

    with pytest.raises(EvidenceError, match="E_CLAIM_SET"):
        evidence_module.build_authority_lock(controller, inputs)


def test_freeze_authority_refuses_overwrite_and_cli_stdout_is_thin(tmp_path):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    authority_inputs = tmp_path / "authority-inputs.json"
    output = tmp_path / "authority-lock.json"
    write_canonical_json(authority_inputs, inputs, exclusive=True)
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "freeze-authority-lock",
            "--controller-root",
            str(controller),
            "--authority-inputs",
            str(authority_inputs),
            "--output",
            str(output),
        ],
        capture_output=True,
        check=False,
        text=True,
        env={**_env(), "PYTHONDONTWRITEBYTECODE": "1"},
    )

    assert result.returncode == 0
    assert result.stdout == canonical_json_bytes(json.loads(result.stdout)).decode()
    assert result.stderr == ""
    assert set(json.loads(result.stdout)) == {
        "authority_lock_sha256",
        "controller_manifest_sha256",
        "subject_count",
    }
    original = output.read_bytes()
    repeated = subprocess.run(
        [
            "python3",
            str(CLI),
            "freeze-authority-lock",
            "--controller-root",
            str(controller),
            "--authority-inputs",
            str(authority_inputs),
            "--output",
            str(output),
        ],
        capture_output=True,
        check=False,
        text=True,
        env={**_env(), "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert repeated.returncode == 2
    assert json.loads(repeated.stderr)["code"] == "E_EXISTS"
    assert output.read_bytes() == original


@pytest.mark.parametrize(
    "metadata",
    [
        {"description": "Authorization=Bearer TOP_SECRET_REPAIR_I"},
        {
            "description": (
                "https://registry-user:TOP_SECRET_REPAIR_I@example.invalid/schema"
            )
        },
        {"api_key": "TOP_SECRET_REPAIR_I"},
    ],
    ids=["bearer_description", "userinfo_description", "api_key"],
)
def test_freeze_cli_rejects_credential_metadata_in_open_registry_schema(
    tmp_path, metadata
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    registry_path = controller / inputs["registry_artifact_paths"][
        "input_generator_registry"
    ]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["generators"][0]["output_schema"].update(metadata)
    registry_body = {
        key: value for key, value in registry.items() if key != "artifact_sha256"
    }
    registry["artifact_sha256"] = canonical_sha256(registry_body)
    write_canonical_json(registry_path, registry, exclusive=False)
    protocol_path = controller / inputs["protocol_artifact_paths"]["protocol"]
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    protocol["input_generator_registry_sha256"] = canonical_sha256(registry)
    protocol_body = {
        key: value for key, value in protocol.items() if key != "artifact_sha256"
    }
    protocol["artifact_sha256"] = canonical_sha256(protocol_body)
    write_canonical_json(protocol_path, protocol, exclusive=False)
    _run_git(controller, "add", ".")
    _run_git(controller, "commit", "-m", "registry credential metadata fixture")
    authority_inputs = tmp_path / "authority-inputs.json"
    output = tmp_path / "authority-lock.json"
    write_canonical_json(authority_inputs, inputs, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "freeze-authority-lock",
            "--controller-root",
            str(controller),
            "--authority-inputs",
            str(authority_inputs),
            "--output",
            str(output),
        ],
        capture_output=True,
        check=False,
        text=True,
        env={**_env(), "PYTHONDONTWRITEBYTECODE": "1"},
    )

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_CREDENTIAL_METADATA"
    assert result.stdout == ""
    assert "TOP_SECRET_REPAIR_I" not in result.stderr
    assert not output.exists()


def test_freeze_cli_does_not_scan_registry_implementation_source_bytes(tmp_path):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    secret = "TOP_SECRET_REPAIR_I_SOURCE"
    registry_path = controller / inputs["registry_artifact_paths"][
        "input_generator_registry"
    ]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    entry = registry["generators"][0]
    implementation = controller / entry["implementation_path"]
    implementation.write_bytes(
        implementation.read_bytes()
        + f"\n# Authorization=Bearer {secret}\n".encode()
    )
    entry["source_sha256"] = hashlib.sha256(implementation.read_bytes()).hexdigest()
    registry_body = {
        key: value for key, value in registry.items() if key != "artifact_sha256"
    }
    registry["artifact_sha256"] = canonical_sha256(registry_body)
    write_canonical_json(registry_path, registry, exclusive=False)
    protocol_path = controller / inputs["protocol_artifact_paths"]["protocol"]
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    protocol["input_generator_registry_sha256"] = canonical_sha256(registry)
    protocol_body = {
        key: value for key, value in protocol.items() if key != "artifact_sha256"
    }
    protocol["artifact_sha256"] = canonical_sha256(protocol_body)
    write_canonical_json(protocol_path, protocol, exclusive=False)
    _run_git(controller, "add", ".")
    _run_git(controller, "commit", "-m", "registry implementation source fixture")
    authority_inputs = tmp_path / "authority-inputs.json"
    output = tmp_path / "authority-lock.json"
    write_canonical_json(authority_inputs, inputs, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "freeze-authority-lock",
            "--controller-root",
            str(controller),
            "--authority-inputs",
            str(authority_inputs),
            "--output",
            str(output),
        ],
        capture_output=True,
        check=False,
        text=True,
        env={**_env(), "PYTHONDONTWRITEBYTECODE": "1"},
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["subject_count"] == 1
    assert result.stderr == ""
    assert secret not in result.stdout
    assert output.exists()


def test_freeze_cli_captures_verified_implementation_output_and_fails_closed(
    tmp_path,
):
    controller, inputs, _governing = _authority_freeze_fixture(tmp_path)
    registry_path = controller / inputs["registry_artifact_paths"][
        "adapter_registry"
    ]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    selected = next(
        row
        for row in registry["adapters"]
        if row["adapter_id"] == "PYTHON_PEP517_V1"
    )
    implementation = controller / selected["implementation_path"]
    implementation.write_text(
        implementation.read_text(encoding="utf-8").replace(
            "from __future__ import annotations\n",
            "from __future__ import annotations\n\n"
            "print('forbidden adapter output')\n",
        ),
        encoding="utf-8",
    )
    selected["source_sha256"] = hashlib.sha256(implementation.read_bytes()).hexdigest()
    registry_body = {
        key: value for key, value in registry.items() if key != "artifact_sha256"
    }
    registry["artifact_sha256"] = canonical_sha256(registry_body)
    write_canonical_json(registry_path, registry, exclusive=False)
    protocol_path = controller / inputs["protocol_artifact_paths"]["protocol"]
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    protocol["adapter_registry_sha256"] = canonical_sha256(registry)
    protocol_body = {
        key: value for key, value in protocol.items() if key != "artifact_sha256"
    }
    protocol["artifact_sha256"] = canonical_sha256(protocol_body)
    write_canonical_json(protocol_path, protocol, exclusive=False)
    _run_git(controller, "add", ".")
    _run_git(controller, "commit", "-m", "verified adapter output fixture")
    authority_inputs = tmp_path / "authority-inputs.json"
    output = tmp_path / "authority-lock.json"
    write_canonical_json(authority_inputs, inputs, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "freeze-authority-lock",
            "--controller-root",
            str(controller),
            "--authority-inputs",
            str(authority_inputs),
            "--output",
            str(output),
        ],
        capture_output=True,
        check=False,
        text=True,
        env={**_env(), "PYTHONDONTWRITEBYTECODE": "1"},
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == canonical_json_bytes(
        {"status": "FAIL", "code": "E_VERIFIED_EXECUTION_OUTPUT"}
    ).decode()
    assert not output.exists()


def test_load_authority_lock_accepts_matching_canonical_bytes(tmp_path):
    path = tmp_path / "authority-lock.json"
    raw = canonical_json_bytes(_authority_lock())
    path.write_bytes(raw)

    assert evidence_module.load_authority_lock(
        path, hashlib.sha256(raw).hexdigest()
    ) == _authority_lock()


def _source_tree_sha256(root: Path) -> str:
    files = [
        {
            "path": path.relative_to(root).as_posix(),
            "byte_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]
    return canonical_sha256({"domain": "P3-NORMALIZED-SOURCE-TREE-v1", "files": files})


def _profiling_receipt(
    workload: dict,
    source_record: dict,
    neutral: str,
    adapter_source_sha256: str | None,
) -> dict:
    rows = []
    for selected in workload["selected_rows"]:
        call_trace = [
            {
                "sequence": 1,
                "module": "fixture.subject",
                "symbol": f"scalar_{selected['behavior_id'][:12]}",
                "call_kind": "PYTHON_CALL",
                "argument_types": ["float"],
                "keyword_names": [],
            }
        ]
        rows.append({
            "behavior_id": selected["behavior_id"],
            "status": "SUCCESS",
            "argv": ["fixture-runner", selected["behavior_id"]],
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
        })
    body = {
        "schema_version": "p3-profiling-results-v1",
        "neutral_snapshot_id": neutral,
        "controlled_subject_source_id": workload["controlled_subject_source_id"],
        **source_record,
        "profiling_workload_sha256": workload["artifact_sha256"],
        "adapter_implementation_source_sha256": adapter_source_sha256,
        "runner_implementation_source_sha256": hashlib.sha256(
            Path(frames_module.__file__).read_bytes()
        ).hexdigest(),
        "results": sorted(rows, key=lambda row: row["behavior_id"]),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _run_git(root: Path, *argv: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *argv],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


def _fixed_git_query(argv: list[str]) -> tuple[str, ...]:
    for index, item in enumerate(argv):
        if item in {"rev-parse", "status", "remote", "ls-files"}:
            return tuple(argv[index:])
    raise AssertionError("fixed Git query subcommand is absent")


def _secret_preflight_fixture(tmp_path: Path) -> tuple[Path, dict]:
    root = tmp_path / "repo"
    root.mkdir()
    _run_git(root, "init")
    _run_git(root, "config", "user.name", "Fixture")
    _run_git(root, "config", "user.email", "fixture@example.invalid")
    _run_git(root, "remote", "add", "origin", SECRET_ORIGIN)
    lock = root / "requirements.lock"
    lock.write_text("dependency==1\n", encoding="utf-8")
    input_path = root / "input.json"
    input_path.write_text("{}\n", encoding="utf-8")
    _run_git(root, "add", "requirements.lock", "input.json")
    _run_git(root, "commit", "-m", "fixture")
    spec = {
        "schema_version": "p3-preflight-v1",
        "repository_identity": SECRET_IDENTITY,
        "expected_commit": _run_git(root, "rev-parse", "HEAD"),
        "dependency_lock_path": "requirements.lock",
        "dependency_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
        "phase_inputs": [
            {
                "path": "input.json",
                "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
            }
        ],
        "smoke_commands": [["python3", "-c", "print(1)"]],
        "timeout_seconds": 10,
        "phase_role": "CONTROLLED_B",
        "minimum_cpu_count": 1,
        "minimum_memory_bytes": 1,
        "minimum_disk_free_bytes": 1,
        "worker_limit": 1,
    }
    return root, spec


def _protocol_body(**overrides):
    body = {
        "schema_version": "p3-protocol-v1",
        "scientific_plan_sha256": SCIENTIFIC_PLAN_SHA256,
        "evidence_design_sha256": EVIDENCE_DESIGN_SHA256,
        "claims_initial_status": "blocked",
        "rq_spec_sha256": _digest("rq"),
        "claim_ceiling_sha256": _digest("ceiling"),
        "p12_contract_sha256": _digest("p12"),
        "operator_catalogue_sha256": _digest("operators"),
        "adapter_registry_sha256": _digest("adapters"),
        "input_generator_registry_sha256": _digest("generators"),
        "mr_policy_sha256": _digest("mr"),
        "site_policy_sha256": _digest("site"),
        "analysis_spec_sha256": _digest("analysis"),
        "package_policy_sha256": _digest("package"),
        "environment_lock_sha256": _digest("env"),
        "profiling_budgets": {"S": 10, "M": 15, "L": 20},
        "behavior_category_order": list(BEHAVIOR_CATEGORY_ORDER),
        "technique_order": list(TECHNIQUE_ORDER),
        "e_common_count": 30,
        "e_contract_count": 5,
        "p12_outcome_states": list(P12_OUTCOME_STATES),
        "p12_primary_estimand": "INTENTION_TO_EVALUATE_LOWER_BOUND",
        "infrastructure_retry_limit": 3,
    }
    body.update(overrides)
    return body


def _write_protocol(path: Path, body: dict) -> bytes:
    payload = {**body}
    if "artifact_sha256" not in payload:
        payload["artifact_sha256"] = canonical_sha256(payload)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    path.write_bytes(raw)
    return raw


def _adapter_registry(tmp_path: Path) -> dict:
    adapters = []
    for adapter_id, ecosystem, rel in _ADAPTER_SPECS:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        fixture = ADAPTER_FIXTURE_ROOT / Path(rel).name
        if fixture.is_file():
            path.write_bytes(fixture.read_bytes())
        else:
            path.write_text(f"# adapter {adapter_id}\n", encoding="utf-8")
        adapters.append(
            {
                "adapter_id": adapter_id,
                "ecosystem": ecosystem,
                "implementation_path": rel,
                "source_sha256": __import__("hashlib")
                .sha256(path.read_bytes())
                .hexdigest(),
            }
        )
    body = {"schema_version": "p3-adapter-registry-v1", "adapters": adapters}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _tagged_declarations(name: str) -> list[dict]:
    fixture = json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))
    rows = []
    for item in fixture["declarations"]:
        row = dict(item)
        row["ecosystem"] = fixture["ecosystem"]
        if fixture.get("adapter_id") is not None:
            row["adapter_id"] = fixture["adapter_id"]
        rows.append(row)
    return rows


def test_cli_help_lists_only_frozen_commands():
    result = subprocess.run(
        ["python3", str(CLI), "--help"],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    line = next(
        item for item in result.stdout.splitlines() if "{" in item and "}" in item
    )
    observed = set(line[line.index("{") + 1 : line.index("}")].split(","))
    assert observed == COMMANDS


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


def test_build_frames_subject_specs_are_the_only_subject_authority_options(tmp_path):
    help_result = subprocess.run(
        ["python3", str(CLI), "build-frames", "--help"],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert help_result.returncode == 0
    assert "--subject-specs" in help_result.stdout
    for removed in ("--declarations", "--features", "--scale-class"):
        assert removed not in help_result.stdout
        output_root = tmp_path / removed.removeprefix("--")
        result = subprocess.run(
            [
                "python3",
                str(CLI),
                "build-frames",
                "--bridge",
                str(tmp_path / "bridge.json"),
                "--subject-specs",
                str(tmp_path / "subject-specs.json"),
                "--adapter-root",
                str(tmp_path),
                "--generator-root",
                str(tmp_path),
                "--slots",
                str(tmp_path / "slots.json"),
                "--contracts",
                str(tmp_path / "contracts.json"),
                "--applicability-map",
                str(tmp_path / "applicability.json"),
                "--output-root",
                str(output_root),
                removed,
                "legacy-authority.json",
            ],
            capture_output=True,
            check=False,
            text=True,
            env=_env(),
        )
        assert result.returncode == 2
        assert f"unrecognized arguments: {removed}" in result.stderr
        assert not output_root.exists()


@pytest.mark.parametrize("case", ["missing", "duplicate", "extra"])
def test_build_frames_subject_spec_coverage_fails_before_adapter_execution(
    tmp_path, case
):
    neutral = _digest("subject-neutral")
    record = {
        "neutral_snapshot_id": neutral,
        "fixed_tree_commitment": "4" * 64,
        "normalized_source_tree_sha256": "21" * 32,
        "source_archive_sha256": "5" * 64,
        "build_descriptor_sha256": "22" * 32,
        "eligibility_reason": "fixture",
        "eligible_for_construct": True,
        "eligible_for_criterion": True,
    }
    bridge = {"records": [record]}
    base_spec = {
        "neutral_snapshot_id": neutral,
        "source_root": str(tmp_path / "must-not-execute"),
        "source_record": {
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
        },
        "build_descriptor": {"ecosystem": "python"},
        "adapter_registry": {},
        "input_generator_registry": {},
        "profiling_results": {},
    }
    if case == "missing":
        specs = []
    elif case == "duplicate":
        specs = [base_spec, dict(base_spec)]
    else:
        specs = [{**base_spec, "neutral_snapshot_id": _digest("extra-neutral")}]
    paths = {
        "bridge": tmp_path / "bridge.json",
        "specs": tmp_path / "subject-specs.json",
        "slots": tmp_path / "slots.json",
        "contracts": tmp_path / "contracts.json",
        "applicability": tmp_path / "applicability.json",
    }
    for path, value in (
        (paths["bridge"], bridge),
        (paths["specs"], specs),
        (paths["slots"], []),
        (paths["contracts"], {}),
        (paths["applicability"], {}),
    ):
        write_canonical_json(path, value, exclusive=True)
    output_root = tmp_path / "frames-out"
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
    assert json.loads(result.stderr)["code"] == "E_SUBJECT_SPEC_COVERAGE"
    assert not output_root.exists()


def test_run_preflight_stdout_and_receipt_do_not_reveal_secret_origin(tmp_path):
    root, spec = _secret_preflight_fixture(tmp_path)
    spec_path = tmp_path / "preflight.json"
    receipt_path = tmp_path / "receipt.json"
    write_canonical_json(spec_path, spec, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "run-preflight",
            "--root",
            str(root),
            "--spec",
            str(spec_path),
            "--output",
            str(receipt_path),
        ],
        capture_output=True,
        check=False,
        env=_env(),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["repository_identity"] == SECRET_IDENTITY
    assert payload["origin_transport"] == "HTTPS"
    assert payload["origin_sha256"] == SECRET_ORIGIN_SHA256
    assert "raw_origin" not in payload
    for stream in (result.stdout, result.stderr, receipt_path.read_bytes()):
        assert b"audit-user" not in stream
        assert b"TOP_SECRET_TOKEN" not in stream


def test_run_preflight_error_does_not_reveal_secret_origin(tmp_path):
    root, spec = _secret_preflight_fixture(tmp_path)
    spec["repository_identity"] = "github.com/Other/Repo"
    spec_path = tmp_path / "preflight.json"
    write_canonical_json(spec_path, spec, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "run-preflight",
            "--root",
            str(root),
            "--spec",
            str(spec_path),
        ],
        capture_output=True,
        check=False,
        env=_env(),
    )

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PREFLIGHT_REPOSITORY"
    for stream in (result.stdout, result.stderr):
        assert b"audit-user" not in stream
        assert b"TOP_SECRET_TOKEN" not in stream


def test_validate_protocol_prints_one_canonical_json_result(tmp_path):
    protocol = tmp_path / "protocol.json"
    raw = _write_protocol(protocol, _protocol_body())
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["protocol_sha256"] == __import__("hashlib").sha256(raw).hexdigest()
    assert (
        result.stdout
        == json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    )


def test_validate_protocol_rejects_a_different_well_formed_plan_hash(tmp_path):
    protocol = tmp_path / "protocol.json"
    _write_protocol(protocol, _protocol_body(scientific_plan_sha256="a" * 64))
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_AUTHORITY"


def test_validate_protocol_rejects_extra_key_before_writing_output(tmp_path):
    protocol = tmp_path / "protocol.json"
    body = _protocol_body()
    body["extra_field"] = "nope"
    body["artifact_sha256"] = canonical_sha256(
        {key: value for key, value in body.items() if key != "artifact_sha256"}
    )
    protocol.write_bytes(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "validate-protocol",
            "--protocol",
            str(protocol),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SCHEMA_KEYS"


def test_validate_protocol_rejects_missing_key(tmp_path):
    protocol = tmp_path / "protocol.json"
    body = _protocol_body()
    del body["e_common_count"]
    body["artifact_sha256"] = canonical_sha256(body)
    protocol.write_bytes(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SCHEMA_KEYS"


def test_validate_protocol_rejects_old_authority_digest(tmp_path):
    protocol = tmp_path / "protocol.json"
    _write_protocol(
        protocol,
        _protocol_body(
            scientific_plan_sha256="911562938a14ad3955a6c1e38080185ba78e92dbf4401efcb10d7c169e4a2772",
            evidence_design_sha256="e2a943b30f8096aa65a72c43aa514df67b8d58e16fcf7209930799ee4444c346",
        ),
    )
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_AUTHORITY"


def test_validate_protocol_rejects_wrong_counts_retry_or_outcome_order(tmp_path):
    cases = [
        {"e_common_count": 29},
        {"e_contract_count": 4},
        {"infrastructure_retry_limit": 4},
        {
            "p12_outcome_states": [
                "MR_SATISFIED",
                "MR_VIOLATION",
                "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
                "SCIENTIFIC_INCONCLUSIVE",
                "INFRASTRUCTURE_UNRESOLVED",
            ]
        },
    ]
    for overrides in cases:
        protocol = tmp_path / f"protocol-{next(iter(overrides))}.json"
        _write_protocol(protocol, _protocol_body(**overrides))
        result = subprocess.run(
            ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
            capture_output=True,
            check=False,
            text=True,
            env=_env(),
        )
        assert result.returncode == 2
        assert json.loads(result.stderr)["code"] in {
            "E_PROTOCOL",
            "E_PROTOCOL_COUNTS",
            "E_PROTOCOL_RETRY",
            "E_PROTOCOL_OUTCOMES",
        }


def test_verify_mr_inventory_accepts_exact_chronology(tmp_path):
    candidate_body = {
        "schema_version": "p3-mr-candidate-frame-v1",
        "artifact_type": "MR_CANDIDATE_FRAME",
        "candidate_mr_ids": ["mr-1"],
    }
    candidate = {**candidate_body, "artifact_sha256": canonical_sha256(candidate_body)}
    receipt_body = {
        "schema_version": "p3-mr-custodian-receipt-v1",
        "artifact_type": "MR_CUSTODIAN_RECEIPT",
        "candidate_frame_sha256": candidate["artifact_sha256"],
        "receipt_state": "CLOSED",
        "admitted_mr_ids": ["mr-1"],
        "excluded_mr_ids": [],
    }
    receipt = {**receipt_body, "artifact_sha256": canonical_sha256(receipt_body)}
    inventory_body = {
        "schema_version": "p3-mr-final-inventory-v1",
        "artifact_type": "MR_FINAL_INVENTORY",
        "custodian_receipt_sha256": receipt["artifact_sha256"],
        "mr_ids": ["mr-1"],
    }
    inventory = {
        **inventory_body,
        "artifact_sha256": canonical_sha256(inventory_body),
    }
    portfolios_body = {
        "schema_version": "p3-mr-portfolios-v1",
        "artifact_type": "MR_PORTFOLIOS",
        "final_inventory_sha256": inventory["artifact_sha256"],
        "portfolios": [{"portfolio_id": "primary", "mr_ids": ["mr-1"]}],
    }
    portfolios = {
        **portfolios_body,
        "artifact_sha256": canonical_sha256(portfolios_body),
    }
    paths = {}
    for name, artifact in (
        ("candidate", candidate),
        ("receipt", receipt),
        ("inventory", inventory),
        ("portfolios", portfolios),
    ):
        paths[name] = tmp_path / f"{name}.json"
        write_canonical_json(paths[name], artifact, exclusive=True)
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-mr-inventory",
            "--candidate-frame",
            str(paths["candidate"]),
            "--custodian-receipt",
            str(paths["receipt"]),
            "--final-inventory",
            str(paths["inventory"]),
            "--portfolios",
            str(paths["portfolios"]),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "PASS"

    legacy = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-mr-inventory",
            "--inventory",
            str(paths["inventory"]),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert legacy.returncode == 2
    help_result = subprocess.run(
        ["python3", str(CLI), "verify-mr-inventory", "--help"],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert "--inventory" not in help_result.stdout


def test_build_frames_writes_declared_artifacts_under_output_root_only(tmp_path):
    adapter_root = tmp_path / "adapters-root"
    adapter_root.mkdir()
    raw_registry = _adapter_registry(adapter_root)
    registry = validate_adapter_registry(raw_registry, _source_snapshot(adapter_root))
    source_root = tmp_path / "source-root"
    source_root.mkdir()
    fixture = json.loads((FIXTURE_ROOT / "python.json").read_text(encoding="utf-8"))
    for relative in fixture["source_files"]:
        path = source_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def solve(value):\n    return value\n", encoding="utf-8")
    manifest = source_root / "adapter-python.json"
    write_canonical_json(manifest, fixture, exclusive=True)
    descriptor = {
        "ecosystem": "python",
        "manifest_path": manifest.name,
        "reverse": False,
    }
    source_record = {
        "normalized_source_tree_sha256": _source_tree_sha256(source_root),
        "build_descriptor_sha256": canonical_sha256(descriptor),
    }
    neutral = canonical_sha256({"fixture": "neutral"})
    discovery = run_adapter_discovery(
        _source_snapshot(source_root), descriptor, registry, "PYTHON_PEP517_V1"
    )
    frame = build_public_behavior_frame(source_record, discovery)
    workload = select_profiling_workload(frame, "S")
    profiling_results = _profiling_receipt(
        workload,
        source_record,
        neutral,
        discovery["implementation_source_sha256"],
    )
    bridge = {
        "schema_version": "p3-p12-bridge-v1",
        "p12_release_id": "fixture",
        "p12_repository_identity": "Example/P12-Defect4MR",
        "p12_contract_path": "release/contract.json",
        "p12_contract_blob_sha": "0" * 40,
        "p12_package_root_sha256": "1" * 64,
        "p12_contract_sha256": "2" * 64,
        "eligible_inventory_root_sha256": "3" * 64,
        "eligible_item_count": 1,
        "trust_mode": "PINNED_GIT_RELEASE",
        "records": [
            {
                "neutral_snapshot_id": neutral,
                "fixed_tree_commitment": "4" * 64,
                "normalized_source_tree_sha256": source_record[
                    "normalized_source_tree_sha256"
                ],
                "source_archive_sha256": "5" * 64,
                "build_descriptor_sha256": source_record["build_descriptor_sha256"],
                "eligibility_reason": "fixture",
                "eligible_for_construct": True,
                "eligible_for_criterion": True,
            }
        ],
    }
    bridge = {**bridge, "artifact_sha256": canonical_sha256(bridge)}
    generator_registry = json.loads(
        (
            Path(__file__).resolve().parent / "fixtures/input_generators/registry.json"
        ).read_text(encoding="utf-8")
    )
    generator_root = Path(__file__).resolve().parent / "fixtures/input_generators"
    subject_specs = [
        {
            "neutral_snapshot_id": bridge["records"][0]["neutral_snapshot_id"],
            "source_root": str(source_root),
            "source_record": source_record,
            "build_descriptor": descriptor,
            "adapter_registry": raw_registry,
            "input_generator_registry": generator_registry,
            "profiling_results": profiling_results,
        }
    ]
    outside = tmp_path / "outside"
    outside.mkdir()
    output_root = tmp_path / "frames-out"
    paths = {
        "bridge": tmp_path / "bridge.json",
        "subject_specs": tmp_path / "subject-specs.json",
        "slots": tmp_path / "slots.json",
        "contracts": tmp_path / "contracts.json",
        "applicability": tmp_path / "applicability.json",
    }
    write_canonical_json(paths["bridge"], bridge, exclusive=True)
    write_canonical_json(paths["subject_specs"], subject_specs, exclusive=True)
    write_canonical_json(paths["slots"], [], exclusive=True)
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
            str(paths["subject_specs"]),
            "--adapter-root",
            str(adapter_root),
            "--generator-root",
            str(generator_root),
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
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    neutral = bridge["records"][0]["neutral_snapshot_id"]
    expected = {
        f"adapter-discovery-{neutral}.json",
        f"source-scale-{neutral}.json",
        f"public-behavior-frame-{neutral}.json",
        f"profiling-workload-{neutral}.json",
        f"evaluation-inputs-common-{neutral}.json",
        f"profiling-results-{neutral}.json",
        f"technique-profile-{neutral}.json",
        f"derived-subject-{neutral}.json",
        "subject-frames.json",
    }
    written = {path.name for path in output_root.iterdir() if path.is_file()}
    assert expected <= written
    assert list(outside.iterdir()) == []
    common = json.loads(
        (output_root / f"evaluation-inputs-common-{neutral}.json").read_text()
    )
    assert len(common["rows"]) == 30
    assert any(row["status"] == "COMMON_INPUT_EXECUTABLE" for row in common["rows"])


def _indexed_reference(index_root: Path, path: Path) -> dict:
    return {
        "path": path.relative_to(index_root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _write_evidence_index(path: Path, body: dict) -> None:
    write_canonical_json(
        path,
        {**body, "artifact_sha256": canonical_sha256(body)},
        exclusive=True,
    )


def _legacy_three_rq_claim_authority() -> dict:
    associations = {
        "C1_SEMANTIC_MUTATION_SYSTEM_PROTOCOL": ["RQ1", "RQ2", "RQ3"],
        "C2_CROSS_PROJECT_OPERATOR_EFFECTIVENESS": ["RQ1"],
        "C3_EQUIVALENCE_PROTOCOL_VALUE": ["RQ2"],
        "C4_SMS_DISCRIMINANT_VALIDITY": ["RQ2"],
        "C5_CONTROLLED_REAL_CONSISTENCY": ["RQ3"],
        "C6_STRUCTURED_VS_NATIVE_SUPERIORITY": ["RQ2"],
        "C7_REPRODUCIBLE_EVIDENCE_INFRASTRUCTURE": ["RQ1", "RQ2", "RQ3"],
    }
    claims = [
        {"claim_id": claim_id, "rqs": rqs, "initial_status": "blocked"}
        for claim_id, rqs in associations.items()
    ]
    body = {"schema_version": "p3-claim-ceiling-authority-v1", "claims": claims}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _claim_authority() -> dict:
    associations = {
        "C1_ARTIFACT_FIRST_SEMANTIC_MUTANT_PROTOCOL": [
            "RQ1",
            "RQ2",
            "RQ3",
            "RQ4",
        ],
        "C2_CERTIFIED_MUTANTS_ACROSS_SCALES_TECHNIQUES": ["RQ1"],
        "C3_SEMANTIC_CONSTRUCT_DISTINCTNESS": ["RQ2"],
        "C4_FAMILY_AWARE_SMS_RESIDUAL_EXPLANATION": ["RQ3"],
        "C5_P12_CRITERION_INCREMENTAL_VALUE": ["RQ4"],
        "C6_UNIVERSAL_SUPERIORITY_CEILING": ["RQ3", "RQ4"],
        "C7_LANGUAGE_INDEPENDENT_AUTOMATION_CEILING": ["RQ1"],
        "C8_PROFILING_REPRESENTATIVENESS_CEILING": ["RQ1"],
    }
    claims = [
        {"claim_id": claim_id, "rqs": rqs, "initial_status": "blocked"}
        for claim_id, rqs in associations.items()
    ]
    body = {"schema_version": "p3-claim-ceiling-authority-v1", "claims": claims}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _blocked_claim_ledger(*references: str) -> dict:
    evidence = sorted(set(references))
    authority = _claim_authority()
    claims = []
    for authority_claim in authority["claims"]:
        claim_body = {
            "claim_id": authority_claim["claim_id"],
            "rqs": authority_claim["rqs"],
            "evidence_references": evidence,
            "status": "blocked",
        }
        claims.append(
            {**claim_body, "artifact_sha256": canonical_sha256(claim_body)}
        )
    body = {
        "schema_version": "p3-claim-evidence-v1",
        "claim_authority_sha256": hashlib.sha256(
            canonical_json_bytes(authority)
        ).hexdigest(),
        "rq_authority_sha256": hashlib.sha256(
            (
                ROOT
                / "research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md"
            ).read_bytes()
        ).hexdigest(),
        "claims": claims,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


_PROTOCOL_ARTIFACT_FIELDS = (
    "rq_spec_sha256",
    "claim_ceiling_sha256",
    "p12_contract_sha256",
    "operator_catalogue_sha256",
    "mr_policy_sha256",
    "site_policy_sha256",
    "analysis_spec_sha256",
    "package_policy_sha256",
    "environment_lock_sha256",
    "job_derivation_policy_sha256",
)


def _install_protocol_authorities(tmp_path: Path) -> dict:
    artifact_paths = {}
    for field in _PROTOCOL_ARTIFACT_FIELDS:
        path = tmp_path / f"authority-{field}.bin"
        if field == "rq_spec_sha256":
            path.write_bytes(
                (
                    ROOT
                    / "research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md"
                ).read_bytes()
            )
        elif field == "claim_ceiling_sha256":
            path.write_bytes(canonical_json_bytes(_claim_authority()))
        else:
            path.write_bytes(f"{field}\n".encode())
        artifact_paths[field] = path

    adapter_root = tmp_path / "authority-adapters"
    adapter_root.mkdir()
    adapters = []
    for adapter_id, ecosystem, relative in _ADAPTER_SPECS:
        fixture = ADAPTER_FIXTURE_ROOT / Path(relative).name
        if not fixture.is_file():
            fixture = ADAPTER_FIXTURE_ROOT / "cmake_ctest_v1.py"
        installed_relative = fixture.relative_to(ROOT).as_posix()
        adapters.append(
            {
                "adapter_id": adapter_id,
                "ecosystem": ecosystem,
                "implementation_path": installed_relative,
                "source_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
            }
        )
    adapter_body = {
        "schema_version": "p3-adapter-registry-v1",
        "adapters": adapters,
    }
    adapter_registry = {
        **adapter_body,
        "artifact_sha256": canonical_sha256(adapter_body),
    }
    adapter_registry_path = adapter_root / "registry.json"
    write_canonical_json(adapter_registry_path, adapter_registry, exclusive=True)

    generator_fixture_root = Path(__file__).resolve().parent / "fixtures/input_generators"
    generator_root = tmp_path / "authority-generators"
    generator_root.mkdir()
    generator_registry_path = generator_root / "registry.json"
    generator_registry = json.loads(
        (generator_fixture_root / "registry.json").read_text(encoding="utf-8")
    )
    generator_rows = []
    for row in generator_registry["generators"]:
        installed = generator_fixture_root / row["implementation_path"]
        generator_rows.append(
            {
                **row,
                "implementation_path": installed.relative_to(ROOT).as_posix(),
                "source_sha256": hashlib.sha256(installed.read_bytes()).hexdigest(),
            }
        )
    generator_body = {
        "schema_version": generator_registry["schema_version"],
        "generators": generator_rows,
    }
    generator_registry = {
        **generator_body,
        "artifact_sha256": canonical_sha256(generator_body),
    }
    write_canonical_json(generator_registry_path, generator_registry, exclusive=True)

    hashes = {
        field: hashlib.sha256(path.read_bytes()).hexdigest()
        for field, path in artifact_paths.items()
        if field != "job_derivation_policy_sha256"
    }
    hashes.update(
        {
            "adapter_registry_sha256": hashlib.sha256(
                adapter_registry_path.read_bytes()
            ).hexdigest(),
            "input_generator_registry_sha256": hashlib.sha256(
                generator_registry_path.read_bytes()
            ).hexdigest(),
        }
    )
    return {
        "hashes": hashes,
        "artifacts": artifact_paths,
        "adapter_registry": adapter_registry,
        "adapter_registry_path": adapter_registry_path,
        "generator_registry": generator_registry,
        "generator_registry_path": generator_registry_path,
    }


def _install_external_authority(
    tmp_path: Path, body: dict, authorities: dict
) -> tuple[Path, str]:
    controller_source = tmp_path / "controller-source"
    shutil.copytree(
        ROOT / "src/p3_v3",
        controller_source / "src/p3_v3",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    shutil.copytree(
        ROOT / "scripts/p3_v3",
        controller_source / "scripts/p3_v3",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    shutil.copy2(
        ROOT / "requirements-frozen.txt",
        controller_source / "requirements-frozen.txt",
    )
    controller_manifest = evidence_module.build_tracked_source_manifest(
        controller_source,
        ["src/p3_v3", "scripts/p3_v3", "requirements-frozen.txt"],
        "controller-source",
    )
    controller_manifest_path = tmp_path / "controller-source-manifest.json"
    write_canonical_json(
        controller_manifest_path, controller_manifest, exclusive=True
    )

    subject_source = tmp_path / "subject-authority-source"
    subject_source.mkdir()
    (subject_source / "subject.py").write_text(
        "def subject(value):\n    return value\n", encoding="utf-8"
    )
    build_descriptor = {"ecosystem": "python", "manifest_path": "subject.py"}
    build_descriptor_path = subject_source / "build.json"
    write_canonical_json(build_descriptor_path, build_descriptor, exclusive=True)
    subject_manifest = evidence_module.build_tracked_source_manifest(
        subject_source, ["."], "subject-source"
    )
    subject_manifest_path = tmp_path / "subject-source-manifest.json"
    write_canonical_json(subject_manifest_path, subject_manifest, exclusive=True)

    protocol_path = tmp_path / body["protocol"]["path"]
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    intent_paths = sorted((tmp_path / body["job_root"]).rglob("intent.json"))
    locked_jobs = []
    for intent_path in intent_paths:
        intent = json.loads(intent_path.read_text(encoding="utf-8"))
        intent_template = {key: value for key, value in intent.items() if key != "attempt"}
        locked_jobs.append(
            {
                "job_id": intent["job_id"],
                "phase": intent["phase"],
                "job_role": intent["job_role"],
                "object_identity": f'{intent["object_type"]}:{intent["object_id"]}',
                "input_identity_sha256": canonical_sha256(intent["input_sha256"]),
                "intent_template_sha256": canonical_sha256(intent_template),
                "maximum_attempts": 3,
                "retry_trigger": "FAIL_INFRASTRUCTURE",
                "execution_class": "NON_SCIENTIFIC_CONTROL",
                "p12_access_class": "FORBIDDEN",
            }
        )
    if not locked_jobs:
        locked_jobs = copy.deepcopy(_authority_lock()["jobs"])
    locked_jobs.sort(key=lambda row: row["job_id"])

    dependency_sha256 = hashlib.sha256(
        (controller_source / "requirements-frozen.txt").read_bytes()
    ).hexdigest()
    preflight = {
        "normalized_repository_identity": "github.com/example/controller",
        "base_commit": "1" * 40,
        "base_tree": "2" * 40,
        "dependency_lock_sha256": dependency_sha256,
        "environment_policy_sha256": protocol["environment_lock_sha256"],
        "required_capabilities": ["CPU"],
        "forbidden_credential_fields": [
            "authorization",
            "credential",
            "password",
            "token",
        ],
    }
    controller_manifest_sha256 = canonical_sha256(controller_manifest)
    subject_manifest_sha256 = canonical_sha256(subject_manifest)
    lock = {
        "schema_version": "P3_V3_AUTHORITY_LOCK_V1",
        "task_id": "p3-v3-final-verifier-fixture",
        "controller_repository": {
            "normalized_repository_identity": preflight[
                "normalized_repository_identity"
            ],
            "base_commit": preflight["base_commit"],
            "base_tree": preflight["base_tree"],
            "tracked_source_manifest_sha256": controller_manifest_sha256,
        },
        "subjects": [
            {
                "subject_id": "subject-a",
                "repository_role": "CONTROLLED_A",
                "normalized_repository_identity": "github.com/example/subject-a",
                "base_commit": "3" * 40,
                "base_tree": "4" * 40,
                "tracked_source_manifest_sha256": subject_manifest_sha256,
                "build_descriptor_sha256": canonical_sha256(build_descriptor),
                "adapter_id": "PYTHON_PEP517_V1",
            }
        ],
        "governing_materials": {
            "scientific_plan_sha256": "5" * 64,
            "evidence_design_sha256": "6" * 64,
            "authority_lock_design_sha256": "7" * 64,
            "implementation_plan_sha256": "8" * 64,
            "controller_implementation_manifest_sha256": controller_manifest_sha256,
        },
        "protocol": {
            "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            **{
                field: protocol[field]
                for field in _PROTOCOL_AUTHORITY_KEYS
                if field != "protocol_sha256" and field in protocol
            },
            "job_derivation_policy_sha256": hashlib.sha256(
                authorities["artifacts"]["job_derivation_policy_sha256"].read_bytes()
            ).hexdigest(),
        },
        "registries": {
            "adapter_registry_sha256": canonical_sha256(
                authorities["adapter_registry"]
            ),
            "input_generator_registry_sha256": canonical_sha256(
                authorities["generator_registry"]
            ),
        },
        "preflight": preflight,
        "jobs": locked_jobs,
        "claim_policy": {
            "claim_ceiling_sha256": protocol["claim_ceiling_sha256"],
            "required_status": "blocked",
            "rq_ids": ["RQ1", "RQ2", "RQ3", "RQ4"],
        },
    }
    lock_path = tmp_path / "authority-lock.json"
    write_canonical_json(lock_path, lock, exclusive=True)

    event_body = {
        "schema_version": "P3_V3_PREFLIGHT_EVENT_V1",
        **{
            field: preflight[field]
            for field in (
                "normalized_repository_identity",
                "base_commit",
                "base_tree",
                "dependency_lock_sha256",
                "environment_policy_sha256",
            )
        },
        "capability_results": [
            {
                "capability": "CPU",
                "status": "PASS",
                "observation_sha256": "9" * 64,
            }
        ],
    }
    event = {**event_body, "event_sha256": canonical_sha256(event_body)}
    event_path = tmp_path / "phase-0-preflight-event.json"
    write_canonical_json(event_path, event, exclusive=True)
    origin_body = {
        "schema_version": "P3_V3_ORIGIN_RECEIPT_V1",
        **{
            field: preflight[field]
            for field in (
                "normalized_repository_identity",
                "base_commit",
                "base_tree",
                "dependency_lock_sha256",
                "environment_policy_sha256",
            )
        },
        "required_capability_results": event_body["capability_results"],
        "preflight_event_sha256": event["event_sha256"],
    }
    origin = {**origin_body, "artifact_sha256": canonical_sha256(origin_body)}
    origin_path = tmp_path / "origin-receipt.json"
    write_canonical_json(origin_path, origin, exclusive=True)

    body.update(
        {
            "schema_version": "P3_V3_EVIDENCE_INDEX_V3",
            "controller_source": {
                "root": controller_source.relative_to(tmp_path).as_posix(),
                "manifest": _indexed_reference(tmp_path, controller_manifest_path),
            },
            "subject_sources": [
                {
                    "subject_id": "subject-a",
                    "root": subject_source.relative_to(tmp_path).as_posix(),
                    "manifest": _indexed_reference(tmp_path, subject_manifest_path),
                }
            ],
            "preflight_event": _indexed_reference(tmp_path, event_path),
            "origin_receipt": _indexed_reference(tmp_path, origin_path),
        }
    )
    expected_lock_sha256 = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    return lock_path, expected_lock_sha256


def _refresh_external_authority_jobs(tmp_path: Path, index: dict) -> None:
    lock_path = tmp_path / "authority-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    jobs = []
    for intent_path in sorted((tmp_path / index["job_root"]).rglob("intent.json")):
        intent = json.loads(intent_path.read_text(encoding="utf-8"))
        template = {key: value for key, value in intent.items() if key != "attempt"}
        role = intent["job_role"]
        jobs.append(
            {
                "job_id": intent["job_id"],
                "phase": intent["phase"],
                "job_role": role,
                "object_identity": f'{intent["object_type"]}:{intent["object_id"]}',
                "input_identity_sha256": canonical_sha256(intent["input_sha256"]),
                "intent_template_sha256": canonical_sha256(template),
                "maximum_attempts": 3,
                "retry_trigger": "FAIL_INFRASTRUCTURE",
                "execution_class": (
                    "REAL_SCIENTIFIC" if role == "P12" else "NON_SCIENTIFIC_CONTROL"
                ),
                "p12_access_class": "REQUIRED" if role == "P12" else "FORBIDDEN",
            }
        )
    lock["jobs"] = sorted(jobs, key=lambda row: row["job_id"])
    lock_path.write_bytes(canonical_json_bytes(lock))


def _bind_external_subject_source(
    tmp_path: Path, index: dict, source_root: Path, build_descriptor: dict
) -> None:
    previous_root = tmp_path / index["subject_sources"][0]["root"]
    manifest = evidence_module.build_tracked_source_manifest(
        source_root, ["."], "subject-source"
    )
    manifest_path = tmp_path / index["subject_sources"][0]["manifest"]["path"]
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    index["subject_sources"][0] = {
        "subject_id": "subject-a",
        "root": source_root.relative_to(tmp_path).as_posix(),
        "manifest": _indexed_reference(tmp_path, manifest_path),
    }
    if previous_root != source_root:
        shutil.rmtree(previous_root)
    lock_path = tmp_path / "authority-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    lock["subjects"][0]["tracked_source_manifest_sha256"] = canonical_sha256(
        manifest
    )
    lock["subjects"][0]["build_descriptor_sha256"] = canonical_sha256(
        build_descriptor
    )
    lock_path.write_bytes(canonical_json_bytes(lock))


def _empty_evidence_index_body(tmp_path: Path) -> dict:
    authorities = _install_protocol_authorities(tmp_path)
    protocol = tmp_path / "protocol.json"
    _write_protocol(protocol, _protocol_body(**authorities["hashes"]))
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"")
    (tmp_path / "jobs").mkdir()
    claims = _blocked_claim_ledger(
        "authority-rq_spec_sha256.bin",
        "authority-claim_ceiling_sha256.bin",
        "protocol.json",
    )
    claims_path = tmp_path / "claims.json"
    write_canonical_json(claims_path, claims, exclusive=True)
    body = {
        "schema_version": "P3_V3_EVIDENCE_INDEX_V1",
        "phase_coverage": [],
        "protocol": _indexed_reference(tmp_path, protocol),
        "protocol_artifacts": {
            field: _indexed_reference(tmp_path, authorities["artifacts"][field])
            for field in _PROTOCOL_ARTIFACT_FIELDS
        },
        "adapter_registries": [
            _indexed_reference(tmp_path, authorities["adapter_registry_path"])
        ],
        "input_generator_registries": [
            _indexed_reference(tmp_path, authorities["generator_registry_path"])
        ],
        "subjects": [],
        "packages": [],
        "mr_chain": {},
        "job_root": "jobs",
        "ledger": _indexed_reference(tmp_path, ledger),
        "phase_receipts": [],
        "p12": {},
        "claims": _indexed_reference(tmp_path, claims_path),
    }
    _install_external_authority(tmp_path, body, authorities)
    return body


def _run_evidence_index(
    index_path: Path,
    *,
    lock_path: Path | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess:
    if lock_path is None:
        lock_path = index_path.parent / "authority-lock.json"
    expected_lock_sha256 = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    return subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--index",
            str(index_path),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            expected_lock_sha256,
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
        timeout=timeout,
    )


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("extra_key", "E_SCHEMA_KEYS"),
        ("missing_key", "E_SCHEMA_KEYS"),
        ("unsafe_path", "E_PATH"),
        ("duplicate_path", "E_INDEX_DUPLICATE"),
        ("hash_mismatch", "E_INDEX_FILE_HASH"),
        ("unknown_phase", "E_INDEX_PHASE"),
        ("empty_phase_collections", "E_INDEX_COVERAGE"),
    ],
)
def test_evidence_index_rejects_structural_forgery(tmp_path, mutation, expected_code):
    body = _empty_evidence_index_body(tmp_path)
    if mutation == "extra_key":
        body["unbound"] = []
    elif mutation == "missing_key":
        del body["claims"]
    elif mutation == "unsafe_path":
        body["protocol"] = {**body["protocol"], "path": "../protocol.json"}
    elif mutation == "duplicate_path":
        body["claims"] = dict(body["protocol"])
    elif mutation == "hash_mismatch":
        body["protocol"] = {**body["protocol"], "sha256": "0" * 64}
    elif mutation == "unknown_phase":
        body["phase_coverage"] = ["PHASE_8"]
    elif mutation == "empty_phase_collections":
        body["phase_coverage"] = ["PHASE_0"]
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, body)

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == expected_code
    assert not result.stdout


def test_evidence_index_rejects_noncanonical_bytes(tmp_path):
    body = _empty_evidence_index_body(tmp_path)
    index = {**body, "artifact_sha256": canonical_sha256(body)}
    index_path = tmp_path / "evidence-index.json"
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_NONCANONICAL_JSON"
    assert not result.stdout


def test_evidence_index_rejects_composite_credential_metadata_before_schema(
    tmp_path,
):
    body = _empty_evidence_index_body(tmp_path)
    body["access_token"] = "TOP_SECRET_INDEX_TOKEN"
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, body)

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_CREDENTIAL_METADATA"
    assert "TOP_SECRET_INDEX_TOKEN" not in result.stderr
    assert not result.stdout


@pytest.mark.parametrize("scope", ["authority_inputs", "authority_lock", "index"])
@pytest.mark.parametrize("field", ["api_key", "apiKey", "client_secret"])
def test_key_and_secret_credential_composites_fail_at_every_metadata_boundary(
    tmp_path, scope, field
):
    secret = "TOP_SECRET_D2_CREDENTIAL"
    if scope == "authority_lock":
        candidate = _authority_lock()
        candidate[field] = secret
        with pytest.raises(EvidenceError, match="E_CREDENTIAL_METADATA") as caught:
            evidence_module.validate_authority_lock(candidate)
        assert secret not in str(caught.value)
        return
    if scope == "authority_inputs":
        candidate = {
            "schema_version": "P3_V3_AUTHORITY_INPUTS_V1",
            "task_id": "fixture",
            "subjects": [],
            "governing_material_paths": {},
            "protocol_artifact_paths": {},
            "registry_artifact_paths": {},
            field: secret,
        }
        with pytest.raises(EvidenceError, match="E_CREDENTIAL_METADATA") as caught:
            evidence_module.validate_authority_inputs(candidate)
        assert secret not in str(caught.value)
        return

    body = _empty_evidence_index_body(tmp_path)
    body[field] = secret
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, body)
    result = _run_evidence_index(index_path)
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_CREDENTIAL_METADATA"
    assert secret not in result.stderr
    assert not result.stdout


def test_indexed_file_hash_and_canonical_parse_share_one_immutable_read(
    tmp_path, monkeypatch
):
    original = {"snapshot": "original"}
    replacement = {"snapshot": "replacement"}
    artifact = tmp_path / "artifact.json"
    artifact.write_bytes(canonical_json_bytes(original))
    reference = _indexed_reference(tmp_path, artifact)
    real_reader = evidence_module.read_canonical_regular_bytes
    artifact_reads = 0

    def read_then_swap(path, context):
        nonlocal artifact_reads
        raw = real_reader(path, context)
        if Path(path) == artifact:
            artifact_reads += 1
            artifact.write_bytes(canonical_json_bytes(replacement))
        return raw

    monkeypatch.setattr(
        evidence_module, "read_canonical_regular_bytes", read_then_swap
    )

    _path, value = evidence_module._indexed_file(
        tmp_path, reference, set(), {}, "artifact"
    )

    assert value == original
    assert artifact_reads == 1


def _complete_phase_zero_evidence_index(tmp_path: Path) -> Path:
    from p3_v3.packages import build_package
    from p3_v3.run_records import (
        close_phase,
        create_intent,
        reconstruct_attempt_events,
        write_result,
    )

    authorities = _install_protocol_authorities(tmp_path)
    protocol = tmp_path / "protocol.json"
    protocol_raw = _write_protocol(protocol, _protocol_body(**authorities["hashes"]))
    package_root = tmp_path / "package-a"
    package_root.mkdir()
    (package_root / "source.py").write_bytes(b"print(1)\n")
    manifest = build_package(
        "CONSTRUCTION_A",
        package_root,
        [{"path": "source.py", "class": "SOURCE"}],
        [],
    )
    manifest_path = tmp_path / "package-a-manifest.json"
    output_manifest_path = tmp_path / "phase-0-output-manifest.json"
    write_canonical_json(manifest_path, manifest, exclusive=True)
    write_canonical_json(output_manifest_path, manifest, exclusive=True)

    job_id = _digest("phase-0-job")
    attempt = tmp_path / f"jobs/PHASE_0/{job_id}/1"
    intent = {
        "job_id": job_id,
        "protocol_sha256": hashlib.sha256(protocol_raw).hexdigest(),
        "phase": "PHASE_0",
        "argv": ["python3", "-c", "print(1)"],
        "cwd_identity": "fixture-root",
        "environment_sha256": "b" * 64,
        "input_sha256": ["c" * 64],
        "seed": None,
        "timeout_seconds": 30,
        "attempt": 1,
        "object_type": "PREFLIGHT",
        "object_id": "phase-0",
        "mr_id": "not-applicable",
        "evaluation_input_class": "E_COMMON",
        "evaluation_input_id": "phase-0-input",
        "repetition_id": 1,
        "environment_id": "env-1",
        "job_role": "PRIMARY_CONTROLLED",
    }
    create_intent(attempt, intent)
    write_result(
        attempt,
        {
            "job_id": job_id,
            "attempt": 1,
            "status": "PASS",
            "exit_code": 0,
            "stdout_sha256": "d" * 64,
            "stderr_sha256": "e" * 64,
            "duration_seconds": 0.25,
            "failure_code": "",
            "scientific_outcome": None,
            "call_trace_sha256": None,
            "call_trace_identity": None,
        },
    )
    events = reconstruct_attempt_events(tmp_path / "jobs")
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(
        b"".join(
            json.dumps(event, sort_keys=True, separators=(",", ":")).encode() + b"\n"
            for event in events
        )
    )
    expected_jobs_path = tmp_path / "phase-0-expected-jobs.json"
    write_canonical_json(expected_jobs_path, [job_id], exclusive=True)
    receipt = close_phase(
        "PHASE_0",
        hashlib.sha256(protocol_raw).hexdigest(),
        [job_id],
        ledger,
        manifest["artifact_sha256"],
    )
    receipt_path = tmp_path / "phase-0-receipt.json"
    write_canonical_json(receipt_path, receipt, exclusive=True)
    claims_path = tmp_path / "claims.json"
    write_canonical_json(
        claims_path,
        _blocked_claim_ledger(
            "authority-rq_spec_sha256.bin",
            "authority-claim_ceiling_sha256.bin",
            "protocol.json",
        ),
        exclusive=True,
    )
    body = {
        "schema_version": "P3_V3_EVIDENCE_INDEX_V1",
        "phase_coverage": ["PHASE_0"],
        "protocol": _indexed_reference(tmp_path, protocol),
        "protocol_artifacts": {
            field: _indexed_reference(tmp_path, authorities["artifacts"][field])
            for field in _PROTOCOL_ARTIFACT_FIELDS
        },
        "adapter_registries": [
            _indexed_reference(tmp_path, authorities["adapter_registry_path"])
        ],
        "input_generator_registries": [
            _indexed_reference(tmp_path, authorities["generator_registry_path"])
        ],
        "subjects": [],
        "packages": [
            {
                "phase": "PHASE_0",
                "input_role": "A",
                "root": package_root.relative_to(tmp_path).as_posix(),
                "manifest": _indexed_reference(tmp_path, manifest_path),
            }
        ],
        "mr_chain": {},
        "job_root": "jobs",
        "ledger": _indexed_reference(tmp_path, ledger),
        "phase_receipts": [
            {
                "phase": "PHASE_0",
                "receipt": _indexed_reference(tmp_path, receipt_path),
                "expected_jobs": _indexed_reference(tmp_path, expected_jobs_path),
                "output_manifest": _indexed_reference(tmp_path, output_manifest_path),
            }
        ],
        "p12": {},
        "claims": _indexed_reference(tmp_path, claims_path),
    }
    _install_external_authority(tmp_path, body, authorities)
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, body)
    return index_path


def _refresh_attempt_evidence(tmp_path: Path, index: dict) -> None:
    from p3_v3.run_records import close_phase, reconstruct_attempt_events

    events = reconstruct_attempt_events(tmp_path / index["job_root"])
    ledger_path = tmp_path / index["ledger"]["path"]
    ledger_path.write_bytes(b"".join(canonical_json_bytes(event) for event in events))
    index["ledger"]["sha256"] = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    protocol_sha256 = index["protocol"]["sha256"]
    for entry in index["phase_receipts"]:
        expected_path = tmp_path / entry["expected_jobs"]["path"]
        output_path = tmp_path / entry["output_manifest"]["path"]
        expected = json.loads(expected_path.read_text())
        output = json.loads(output_path.read_text())
        receipt = close_phase(
            entry["phase"],
            protocol_sha256,
            expected,
            ledger_path,
            output["artifact_sha256"],
        )
        receipt_path = tmp_path / entry["receipt"]["path"]
        receipt_path.write_bytes(canonical_json_bytes(receipt))
        entry["receipt"]["sha256"] = hashlib.sha256(
            receipt_path.read_bytes()
        ).hexdigest()


def _complete_reconstructable_subject_index(tmp_path: Path) -> Path:
    from p3_v3.run_records import create_intent, write_result

    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    adapter_registry_path = tmp_path / index["adapter_registries"][0]["path"]
    generator_registry_path = tmp_path / index["input_generator_registries"][0]["path"]
    adapter_registry = validate_adapter_registry(
        json.loads(adapter_registry_path.read_text()), _source_snapshot(ROOT)
    )
    generator_registry = validate_input_generator_registry(
        json.loads(generator_registry_path.read_text()), _source_snapshot(ROOT)
    )
    for cache in generator_registry_path.parent.rglob("__pycache__"):
        shutil.rmtree(cache)
    source_root = tmp_path / "indexed-subject-source"
    source_root.mkdir()
    fixture = json.loads((FIXTURE_ROOT / "python.json").read_text())
    for relative in fixture["source_files"]:
        source = source_root / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("def solve(value):\n    return value\n", encoding="utf-8")
    manifest_path = source_root / "adapter-python.json"
    write_canonical_json(manifest_path, fixture, exclusive=True)
    descriptor = {
        "ecosystem": "python",
        "manifest_path": manifest_path.name,
        "reverse": False,
    }
    source_record = {
        "normalized_source_tree_sha256": _source_tree_sha256(source_root),
        "build_descriptor_sha256": canonical_sha256(descriptor),
    }
    neutral = canonical_sha256({"fixture": "final-subject"})
    bridge_record = {
        "neutral_snapshot_id": neutral,
        "fixed_tree_commitment": "4" * 64,
        "normalized_source_tree_sha256": source_record[
            "normalized_source_tree_sha256"
        ],
        "source_archive_sha256": "5" * 64,
        "build_descriptor_sha256": source_record["build_descriptor_sha256"],
        "eligibility_reason": "fixture",
        "eligible_for_construct": True,
        "eligible_for_criterion": True,
    }
    discovery = run_adapter_discovery(
        _source_snapshot(source_root), descriptor, adapter_registry, "PYTHON_PEP517_V1"
    )
    frame = build_public_behavior_frame(source_record, discovery)
    workload = select_profiling_workload(frame, "S")
    profiling_results = _profiling_receipt(
        workload,
        source_record,
        neutral,
        discovery["implementation_source_sha256"],
    )
    material = derive_subject_material(
        {
            "neutral_snapshot_id": neutral,
            "source_snapshot": _source_snapshot(source_root),
            "source_record": source_record,
            "build_descriptor": descriptor,
            "adapter_registry": adapter_registry,
            "input_generator_registry": generator_registry,
            "profiling_results": profiling_results,
        },
        bridge_record,
    )
    validity = validate_common_inputs_on_fixed_source(
        material["common_inputs"],
        lambda row: row["status"],
        sites=[],
        contracts=[],
        profile={},
        frame_artifact_sha256=material["public_behavior_frame"]["artifact_sha256"],
    )

    trace_entries = []
    protocol_sha256 = index["protocol"]["sha256"]
    for ordinal, row in enumerate(profiling_results["results"], start=1):
        job_id = _digest(f"profile-{ordinal:02d}")
        trace_path = tmp_path / f"profile-trace-{ordinal:02d}.json"
        write_canonical_json(trace_path, row["call_trace"], exclusive=True)
        trace_sha256 = hashlib.sha256(trace_path.read_bytes()).hexdigest()
        trace_identity = canonical_sha256(
            {
                "job_id": job_id,
                "attempt": 1,
                "behavior_id": row["behavior_id"],
                "call_trace_sha256": trace_sha256,
                "domain": "P3-PROFILING-TRACE-v1",
            }
        )
        attempt = tmp_path / f"jobs/PHASE_1/{job_id}/1"
        create_intent(
            attempt,
            {
                "job_id": job_id,
                "protocol_sha256": protocol_sha256,
                "phase": "PHASE_1",
                "argv": row["argv"],
                "cwd_identity": "subject:subject-a",
                "environment_sha256": row["environment_sha256"],
                "input_sha256": row["input_sha256"],
                "seed": None,
                "timeout_seconds": 30,
                "attempt": 1,
                "object_type": "PROFILING_BEHAVIOR",
                "object_id": row["behavior_id"],
                "mr_id": "not-applicable",
                "evaluation_input_class": "E_COMMON",
                "evaluation_input_id": material["common_inputs"]["rows"][0]["input_id"],
                "repetition_id": 1,
                "environment_id": "profile-env",
                "job_role": "PROFILING",
            },
        )
        write_result(
            attempt,
            {
                "job_id": job_id,
                "attempt": 1,
                "status": "PASS",
                "exit_code": row["exit_code"],
                "stdout_sha256": row["stdout_sha256"],
                "stderr_sha256": row["stderr_sha256"],
                "duration_seconds": 0.25,
                "failure_code": row["failure_code"],
                "scientific_outcome": None,
                "call_trace_sha256": trace_sha256,
                "call_trace_identity": trace_identity,
            },
        )
        trace_entries.append(
            {
                "job_id": job_id,
                "attempt": 1,
                "behavior_id": row["behavior_id"],
                "artifact": _indexed_reference(tmp_path, trace_path),
            }
        )

    artifacts = {
        "bridge_record": bridge_record,
        "source_record": source_record,
        "build_descriptor": descriptor,
        "adapter_discovery": material["adapter_discovery"],
        "source_scale": material["source_scale"],
        "public_frame": material["public_behavior_frame"],
        "profiling_workload": material["profiling_workload"],
        "profiling_results": profiling_results,
        "common_inputs": material["common_inputs"],
        "common_input_validity": validity,
        "technique_profile": material["technique_profile"],
        "sites": material["subject"]["sites"],
        "subject": material["subject"],
    }
    references = {}
    for name, artifact in artifacts.items():
        path = tmp_path / f"indexed-{name}.json"
        write_canonical_json(path, artifact, exclusive=True)
        references[name] = _indexed_reference(tmp_path, path)
    index["subjects"] = [
        {
            "subject_id": "subject-a",
            "phase": "PHASE_1",
            "controlled_subject_source_id": material["controlled_subject_source_id"],
            "controlled_subject_id": material["subject"]["controlled_subject_id"],
            "bridge_record": references["bridge_record"],
            "source_root": source_root.relative_to(tmp_path).as_posix(),
            "source_record": references["source_record"],
            "build_descriptor": references["build_descriptor"],
            "adapter_registry_sha256": adapter_registry["artifact_sha256"],
            "input_generator_registry_sha256": generator_registry["artifact_sha256"],
            "adapter_discovery": references["adapter_discovery"],
            "source_scale": references["source_scale"],
            "public_frame": references["public_frame"],
            "profiling_workload": references["profiling_workload"],
            "profiling_results": references["profiling_results"],
            "profiling_traces": trace_entries,
            "common_inputs": references["common_inputs"],
            "common_input_validity": references["common_input_validity"],
            "technique_profile": references["technique_profile"],
            "sites": references["sites"],
            "subject": references["subject"],
            "slot_artifacts": [],
        }
    ]
    expected_jobs = sorted(entry["job_id"] for entry in trace_entries)
    expected_path = tmp_path / "phase-1-expected-jobs.json"
    write_canonical_json(expected_path, expected_jobs, exclusive=True)
    output_path = tmp_path / "phase-1-output.json"
    output_body = {
        "schema_version": "p3-phase-output-fixture-v1",
        "subject_sha256": canonical_sha256(material["subject"]),
    }
    write_canonical_json(
        output_path,
        {**output_body, "artifact_sha256": canonical_sha256(output_body)},
        exclusive=True,
    )
    receipt_path = tmp_path / "phase-1-receipt.json"
    write_canonical_json(receipt_path, {"pending": True}, exclusive=True)
    index["phase_coverage"] = ["PHASE_0", "PHASE_1"]
    index["phase_receipts"].append(
        {
            "phase": "PHASE_1",
            "receipt": _indexed_reference(tmp_path, receipt_path),
            "expected_jobs": _indexed_reference(tmp_path, expected_path),
            "output_manifest": _indexed_reference(tmp_path, output_path),
        }
    )
    for cache in [
        *adapter_registry_path.parent.rglob("__pycache__"),
        *generator_registry_path.parent.rglob("__pycache__"),
    ]:
        shutil.rmtree(cache)
    _refresh_attempt_evidence(tmp_path, index)
    _bind_external_subject_source(tmp_path, index, source_root, descriptor)
    _refresh_external_authority_jobs(tmp_path, index)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))
    return index_path


def test_evidence_index_reconstructs_a_complete_phase_zero_set(tmp_path):
    result = _run_evidence_index(_complete_phase_zero_evidence_index(tmp_path))

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "status": "PASS",
        "authority_lock_sha256": hashlib.sha256(
            (tmp_path / "authority-lock.json").read_bytes()
        ).hexdigest(),
        "evidence_index_sha256": hashlib.sha256(
            (tmp_path / "evidence-index.json").read_bytes()
        ).hexdigest(),
        "subject_count": 1,
        "authorized_real_p12_job_count": 0,
        "recorded_real_scientific_terminal_count": 0,
        "claims_status": "blocked",
    }


def test_phase_receipt_cannot_close_a_prefix_or_subset_of_locked_phase_jobs(
    tmp_path,
):
    from p3_v3.run_records import (
        close_phase,
        create_intent,
        reconstruct_attempt_events,
        write_result,
    )

    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    first_intent_path = next((tmp_path / index["job_root"]).rglob("intent.json"))
    first_intent = json.loads(first_intent_path.read_text(encoding="utf-8"))
    first_result = json.loads(
        first_intent_path.with_name("result.json").read_text(encoding="utf-8")
    )
    second_job_id = "f" * 64
    second_intent = {**first_intent, "job_id": second_job_id}
    second_result = {**first_result, "job_id": second_job_id}
    second_attempt = tmp_path / f"jobs/PHASE_0/{second_job_id}/1"
    create_intent(second_attempt, second_intent)
    write_result(second_attempt, second_result)

    events = reconstruct_attempt_events(tmp_path / index["job_root"])
    ledger_path = tmp_path / index["ledger"]["path"]
    ledger_path.write_bytes(b"".join(canonical_json_bytes(event) for event in events))
    index["ledger"]["sha256"] = hashlib.sha256(ledger_path.read_bytes()).hexdigest()

    receipt_entry = index["phase_receipts"][0]
    expected_path = tmp_path / receipt_entry["expected_jobs"]["path"]
    expected_path.write_bytes(canonical_json_bytes([first_intent["job_id"]]))
    receipt_entry["expected_jobs"]["sha256"] = hashlib.sha256(
        expected_path.read_bytes()
    ).hexdigest()
    prefix_ledger = tmp_path / "phase-0-prefix-ledger.jsonl"
    prefix_ledger.write_bytes(
        b"".join(canonical_json_bytes(event) for event in events[:2])
    )
    output_path = tmp_path / receipt_entry["output_manifest"]["path"]
    output = json.loads(output_path.read_text(encoding="utf-8"))
    receipt = close_phase(
        "PHASE_0",
        index["protocol"]["sha256"],
        [first_intent["job_id"]],
        prefix_ledger,
        output["artifact_sha256"],
    )
    prefix_ledger.unlink()
    receipt_path = tmp_path / receipt_entry["receipt"]["path"]
    receipt_path.write_bytes(canonical_json_bytes(receipt))
    receipt_entry["receipt"]["sha256"] = hashlib.sha256(
        receipt_path.read_bytes()
    ).hexdigest()
    _refresh_external_authority_jobs(tmp_path, index)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PHASE_RECEIPT"
    assert not result.stdout


@pytest.mark.parametrize("mutation", ["file_symlink", "parent_symlink", "fifo"])
def test_evidence_index_rejects_unsafe_declared_index_path_without_leaking(
    tmp_path, mutation
):
    secret = "TOP_SECRET_DECLARED_INDEX"
    real_root = tmp_path / "real-root"
    real_root.mkdir()
    real_index = _complete_phase_zero_evidence_index(real_root)
    lock_path = real_root / "authority-lock.json"

    if mutation == "file_symlink":
        symlink_target = tmp_path / f"{secret}-target.json"
        real_index.rename(symlink_target)
        real_index.symlink_to(symlink_target)
        declared_index = real_index
    elif mutation == "parent_symlink":
        declared_root = tmp_path / f"{secret}-parent"
        declared_root.symlink_to(real_root, target_is_directory=True)
        declared_index = declared_root / real_index.name
    else:
        real_index.unlink()
        os.mkfifo(real_index)
        declared_index = real_index

    result = _run_evidence_index(
        declared_index,
        lock_path=lock_path,
        timeout=2,
    )

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_INDEX_PATH"
    assert not result.stdout
    assert secret not in result.stderr


def test_coordinated_reseal_cannot_replace_external_authority_digest(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    lock_path = tmp_path / "authority-lock.json"
    expected_lock_sha256 = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    lock["task_id"] = "coordinated-reseal"
    lock_path.write_bytes(canonical_json_bytes(lock))
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index_body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--index",
            str(index_path),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            expected_lock_sha256,
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_LOCK_DIGEST"


def test_coordinated_reseal_execution_relabel_stops_at_external_digest(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    lock_path = tmp_path / "authority-lock.json"
    expected_lock_sha256 = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    lock["jobs"][0]["execution_class"] = "REAL_SCIENTIFIC"
    lock_path.write_bytes(canonical_json_bytes(lock))
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index_body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--index",
            str(index_path),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            expected_lock_sha256,
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_LOCK_DIGEST"


def test_coordinated_reseal_terminal_intent_relabel_fails_locked_intent(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    intent_path = next((tmp_path / "jobs/PHASE_0").rglob("intent.json"))
    intent = json.loads(intent_path.read_text(encoding="utf-8"))
    intent["object_id"] = "coordinated-relabel"
    intent_path.write_bytes(canonical_json_bytes(intent))
    _refresh_attempt_evidence(tmp_path, index)
    index_body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_INTENT"


def test_locked_intent_failure_precedes_malformed_claim_reconstruction(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    intent_path = next((tmp_path / "jobs/PHASE_0").rglob("intent.json"))
    intent = json.loads(intent_path.read_text(encoding="utf-8"))
    intent["object_id"] = "lock-mismatched-intent"
    intent_path.write_bytes(canonical_json_bytes(intent))
    _refresh_attempt_evidence(tmp_path, index)

    claims_path = tmp_path / index["claims"]["path"]
    claims = json.loads(claims_path.read_text(encoding="utf-8"))
    claims["claims"][0]["status"] = "released"
    claims_path.write_bytes(canonical_json_bytes(claims))
    index["claims"] = _indexed_reference(tmp_path, claims_path)
    index_body = {key: item for key, item in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_INTENT"


@pytest.mark.parametrize("claim_bytes", [b"{invalid", b'{\n  "claims": []\n}\n'])
def test_locked_intent_failure_precedes_claim_json_parsing(tmp_path, claim_bytes):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    intent_path = next((tmp_path / "jobs/PHASE_0").rglob("intent.json"))
    intent = json.loads(intent_path.read_text(encoding="utf-8"))
    intent["object_id"] = "lock-mismatched-before-claim-json"
    intent_path.write_bytes(canonical_json_bytes(intent))
    _refresh_attempt_evidence(tmp_path, index)

    claims_path = tmp_path / index["claims"]["path"]
    claims_path.write_bytes(claim_bytes)
    index["claims"] = _indexed_reference(tmp_path, claims_path)
    index_body = {key: item for key, item in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_INTENT"


@pytest.mark.parametrize("target", ["origin_receipt", "preflight_event"])
def test_authority_origin_rejects_package_local_reseal(tmp_path, target):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    target_path = tmp_path / index[target]["path"]
    value = json.loads(target_path.read_text(encoding="utf-8"))
    value["base_tree"] = "f" * 40
    if target == "origin_receipt":
        body = {key: item for key, item in value.items() if key != "artifact_sha256"}
        value["artifact_sha256"] = canonical_sha256(body)
    else:
        body = {key: item for key, item in value.items() if key != "event_sha256"}
        value["event_sha256"] = canonical_sha256(body)
        origin_path = tmp_path / index["origin_receipt"]["path"]
        origin = json.loads(origin_path.read_text(encoding="utf-8"))
        origin["preflight_event_sha256"] = value["event_sha256"]
        origin_body = {
            key: item for key, item in origin.items() if key != "artifact_sha256"
        }
        origin["artifact_sha256"] = canonical_sha256(origin_body)
        origin_path.write_bytes(canonical_json_bytes(origin))
        index["origin_receipt"] = _indexed_reference(tmp_path, origin_path)
    target_path.write_bytes(canonical_json_bytes(value))
    index[target] = _indexed_reference(tmp_path, target_path)
    index_body = {key: item for key, item in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_ORIGIN"


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("https_userinfo", "E_CREDENTIAL_METADATA"),
        ("authorization", "E_CREDENTIAL_METADATA"),
        ("git_config", "E_AUTHORITY_MANIFEST"),
        ("symlinked_manifest", "E_INDEX_PATH"),
        ("out_of_root", "E_PATH"),
    ],
)
def test_authority_credential_metadata_never_echoes_secret(
    tmp_path, mutation, expected_code
):
    secret = "TOP_SECRET_AUTHORITY_TOKEN"
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if mutation in {"https_userinfo", "authorization"}:
        event_path = tmp_path / index["preflight_event"]["path"]
        event = json.loads(event_path.read_text(encoding="utf-8"))
        if mutation == "https_userinfo":
            event["normalized_repository_identity"] = (
                f"https://audit:{secret}@example.invalid/controller.git"
            )
        else:
            event["authorization"] = f"Bearer {secret}"
        event_body = {
            key: value for key, value in event.items() if key != "event_sha256"
        }
        event["event_sha256"] = canonical_sha256(event_body)
        event_path.write_bytes(canonical_json_bytes(event))
        index["preflight_event"] = _indexed_reference(tmp_path, event_path)
    elif mutation == "git_config":
        subject_root = tmp_path / index["subject_sources"][0]["root"]
        git_dir = subject_root / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text(secret, encoding="utf-8")
    elif mutation == "symlinked_manifest":
        reference = index["subject_sources"][0]["manifest"]
        manifest_path = tmp_path / reference["path"]
        target = tmp_path / f"{secret}.json"
        target.write_bytes(manifest_path.read_bytes())
        manifest_path.unlink()
        manifest_path.symlink_to(target)
    else:
        index["subject_sources"][0]["manifest"]["path"] = f"../{secret}.json"
    index_body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == expected_code
    assert not result.stdout
    assert secret not in result.stdout
    assert secret not in result.stderr


@pytest.mark.parametrize("role", ["controller", "subject"])
def test_authority_manifest_rejects_reclosed_source_replacement(tmp_path, role):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if role == "controller":
        source = tmp_path / index["controller_source"]["root"]
        (source / "scripts/p3_v3/evidence.py").write_text(
            "# coordinated controller replacement\n", encoding="utf-8"
        )
        manifest = evidence_module.build_tracked_source_manifest(
            source,
            ["src/p3_v3", "scripts/p3_v3", "requirements-frozen.txt"],
            "controller-source",
        )
        reference = index["controller_source"]["manifest"]
    else:
        source = tmp_path / index["subject_sources"][0]["root"]
        (source / "subject.py").write_text(
            "def subject(value):\n    return value + 1\n", encoding="utf-8"
        )
        manifest = evidence_module.build_tracked_source_manifest(
            source, ["."], "subject-source"
        )
        reference = index["subject_sources"][0]["manifest"]
    manifest_path = tmp_path / reference["path"]
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    reference["sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    index_body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_MANIFEST"


def _copy_installed_controller(tmp_path: Path) -> Path:
    installed_root = tmp_path / "installed-controller"
    for relative in (
        Path("src/p3_v3"),
        Path("scripts/p3_v3"),
        Path("tests/p3_v3/fixtures/adapters"),
        Path("tests/p3_v3/fixtures/input_generators"),
    ):
        shutil.copytree(
            ROOT / relative,
            installed_root / relative,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    shutil.copy2(
        ROOT / "requirements-frozen.txt", installed_root / "requirements-frozen.txt"
    )
    return installed_root


@pytest.mark.parametrize(
    "mutation",
    ["changed_controller", "missing_controller", "changed_adapter"],
)
def test_authority_manifest_rejects_installed_drift_through_production_dispatch(
    tmp_path, tmp_path_factory, monkeypatch, mutation
):
    index_path = _complete_reconstructable_subject_index(tmp_path)
    installed_root = _copy_installed_controller(
        tmp_path_factory.mktemp(f"{mutation}-root")
    )
    monkeypatch.setattr(
        evidence_module,
        "__file__",
        str(installed_root / "scripts/p3_v3/evidence.py"),
    )
    if mutation == "changed_controller":
        (installed_root / "scripts/p3_v3/evidence.py").write_text(
            "# installed controller drift\n", encoding="utf-8"
        )
    elif mutation == "missing_controller":
        (installed_root / "requirements-frozen.txt").unlink()
    else:
        registry = json.loads(
            (tmp_path / "authority-adapters/registry.json").read_text(
                encoding="utf-8"
            )
        )
        adapter_path = installed_root / registry["adapters"][0]["implementation_path"]
        adapter_path.write_text("# installed adapter drift\n", encoding="utf-8")

    calls = {"adapter": 0, "generator": 0}

    def adapter_attempt(*_args, **_kwargs):
        calls["adapter"] += 1
        raise AssertionError("adapter must not execute after installed byte drift")

    def generator_attempt(*_args, **_kwargs):
        calls["generator"] += 1
        raise AssertionError("generator must not execute after installed byte drift")

    monkeypatch.setattr(frames_module, "_load_adapter_discover", adapter_attempt)
    monkeypatch.setattr(
        frames_module, "_load_input_generator_callable", generator_attempt
    )
    lock_path = tmp_path / "authority-lock.json"
    args = evidence_module.build_parser().parse_args(
        [
            "verify-evidence",
            "--index",
            str(index_path),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            hashlib.sha256(lock_path.read_bytes()).hexdigest(),
        ]
    )

    with pytest.raises(EvidenceError) as exc_info:
        evidence_module.dispatch(args)

    assert exc_info.value.code == "E_AUTHORITY_MANIFEST"
    assert calls == {"adapter": 0, "generator": 0}


def test_authority_manifest_rejects_registry_implementation_under_evidence_root(
    tmp_path, tmp_path_factory, monkeypatch
):
    _complete_phase_zero_evidence_index(tmp_path)
    installed_root = _copy_installed_controller(
        tmp_path_factory.mktemp("nested-evidence-controller")
    )
    evidence_root = installed_root / "nested-evidence"
    evidence_root.mkdir()
    nested_implementation = evidence_root / "adapter.py"
    nested_implementation.write_text(
        "def discover(_root):\n    return {}\n", encoding="utf-8"
    )
    monkeypatch.setattr(
        evidence_module,
        "__file__",
        str(installed_root / "scripts/p3_v3/evidence.py"),
    )
    lock = json.loads((tmp_path / "authority-lock.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (tmp_path / "controller-source-manifest.json").read_text(encoding="utf-8")
    )
    adapter_registry = json.loads(
        (tmp_path / "authority-adapters/registry.json").read_text(encoding="utf-8")
    )
    generator_registry = json.loads(
        (tmp_path / "authority-generators/registry.json").read_text(encoding="utf-8")
    )
    adapter_registry["adapters"][0]["implementation_path"] = (
        nested_implementation.relative_to(installed_root).as_posix()
    )
    adapter_registry["adapters"][0]["source_sha256"] = hashlib.sha256(
        nested_implementation.read_bytes()
    ).hexdigest()
    adapter_body = {
        key: value
        for key, value in adapter_registry.items()
        if key != "artifact_sha256"
    }
    adapter_registry["artifact_sha256"] = canonical_sha256(adapter_body)
    lock["registries"]["adapter_registry_sha256"] = canonical_sha256(
        adapter_registry
    )

    calls = {"controller": 0, "adapter": 0, "generator": 0}
    original_controller_verifier = evidence_module.verify_running_controller
    original_adapter_validator = evidence_module.validate_adapter_registry
    original_generator_validator = evidence_module.validate_input_generator_registry

    def adapter_attempt(*args, **kwargs):
        calls["adapter"] += 1
        return original_adapter_validator(*args, **kwargs)

    def generator_attempt(*args, **kwargs):
        calls["generator"] += 1
        return original_generator_validator(*args, **kwargs)

    def controller_attempt(*args, **kwargs):
        calls["controller"] += 1
        return original_controller_verifier(*args, **kwargs)

    monkeypatch.setattr(
        evidence_module, "verify_running_controller", controller_attempt
    )
    monkeypatch.setattr(evidence_module, "validate_adapter_registry", adapter_attempt)
    monkeypatch.setattr(
        evidence_module, "validate_input_generator_registry", generator_attempt
    )

    with pytest.raises(EvidenceError) as exc_info:
        evidence_module._verify_running_controller_for_evidence(
            lock,
            manifest,
            {
                "adapter_registry": adapter_registry,
                "input_generator_registry": generator_registry,
            },
            evidence_root,
        )

    assert exc_info.value.code == "E_AUTHORITY_MANIFEST"
    assert calls == {"controller": 0, "adapter": 0, "generator": 0}


def test_verify_running_controller_public_interface_has_exact_three_arguments():
    assert list(inspect.signature(evidence_module.verify_running_controller).parameters) == [
        "lock",
        "controller_manifest",
        "locked_registries",
    ]


def test_authority_manifest_checks_registry_bytes_before_protocol_bytes(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    registry_reference = index["adapter_registries"][0]
    registry_path = tmp_path / registry_reference["path"]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["adapters"][0]["source_sha256"] = "0" * 64
    registry_body = {
        key: value for key, value in registry.items() if key != "artifact_sha256"
    }
    registry["artifact_sha256"] = canonical_sha256(registry_body)
    registry_path.write_bytes(canonical_json_bytes(registry))
    registry_reference["sha256"] = hashlib.sha256(
        registry_path.read_bytes()
    ).hexdigest()
    protocol_path = tmp_path / index["protocol"]["path"]
    protocol_path.write_bytes(b"{}\n")
    index_body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_MANIFEST"


def test_verify_evidence_reconstructs_every_indexed_subject(tmp_path):
    result = _run_evidence_index(_complete_reconstructable_subject_index(tmp_path))

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["subject_count"] == 1


def test_verify_evidence_consumes_one_locked_execution_snapshot_after_swap(
    tmp_path, monkeypatch
):
    index_path = _complete_reconstructable_subject_index(tmp_path)
    original_snapshot_verifier = evidence_module._verify_locked_execution_snapshot
    swapped = False

    def verify_then_swap(*args, **kwargs):
        nonlocal swapped
        snapshot = original_snapshot_verifier(*args, **kwargs)
        result_path = next((tmp_path / "jobs/PHASE_1").rglob("result.json"))
        changed = json.loads(result_path.read_text(encoding="utf-8"))
        changed["stdout_sha256"] = "0" * 64
        result_path.write_bytes(canonical_json_bytes(changed))
        (tmp_path / "ledger.jsonl").write_bytes(b"{}\n")
        swapped = True
        return snapshot

    monkeypatch.setattr(
        evidence_module, "_verify_locked_execution_snapshot", verify_then_swap
    )
    lock_path = tmp_path / "authority-lock.json"
    args = evidence_module.build_parser().parse_args(
        [
            "verify-evidence",
            "--index",
            str(index_path),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            hashlib.sha256(lock_path.read_bytes()).hexdigest(),
        ]
    )

    result = evidence_module.dispatch(args)

    assert swapped
    assert result["status"] == "PASS"


def test_verify_evidence_rederives_subject_only_from_manifest_snapshot(
    tmp_path, monkeypatch
):
    index_path = _complete_reconstructable_subject_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    source_root = tmp_path / index["subject_sources"][0]["root"]
    descriptor_reference = index["subjects"][0]["build_descriptor"]
    descriptor = json.loads(
        (tmp_path / descriptor_reference["path"]).read_text(encoding="utf-8")
    )
    adapter_manifest = source_root / descriptor["manifest_path"]
    original_verifier = evidence_module._verify_running_controller_for_evidence
    swapped = False

    def verify_then_swap(*args, **kwargs):
        nonlocal swapped
        installed = original_verifier(*args, **kwargs)
        adapter_manifest.write_bytes(b"{}\n")
        swapped = True
        return installed

    monkeypatch.setattr(
        evidence_module,
        "_verify_running_controller_for_evidence",
        verify_then_swap,
    )
    lock_path = tmp_path / "authority-lock.json"
    args = evidence_module.build_parser().parse_args(
        [
            "verify-evidence",
            "--index",
            str(index_path),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            hashlib.sha256(lock_path.read_bytes()).hexdigest(),
        ]
    )

    result = evidence_module.dispatch(args)

    assert swapped
    assert result["status"] == "PASS"


@pytest.mark.parametrize("replacement", ["bytes", "symlink"])
def test_verify_evidence_consumes_verified_registry_snapshot_after_path_swap(
    tmp_path, tmp_path_factory, monkeypatch, replacement
):
    index_path = _complete_reconstructable_subject_index(tmp_path)
    installed_root = _copy_installed_controller(
        tmp_path_factory.mktemp(f"registry-snapshot-{replacement}")
    )
    monkeypatch.setattr(
        evidence_module,
        "__file__",
        str(installed_root / "scripts/p3_v3/evidence.py"),
    )
    original_verifier = evidence_module._verify_running_controller_for_evidence
    original_consumer = frames_module._consume_verified_registry
    state = {"swapped": False, "consumer_calls": 0, "path_reads": 0}

    def verify_then_swap(*args, **kwargs):
        installed = original_verifier(*args, **kwargs)
        relative = installed["adapter_registry"]["adapters"][0][
            "implementation_path"
        ]
        implementation = installed_root / relative
        replacement_path = installed_root / "replacement-adapter.py"
        replacement_path.write_text(
            "raise RuntimeError('replacement registry bytes executed')\n",
            encoding="utf-8",
        )
        implementation.unlink()
        if replacement == "symlink":
            implementation.symlink_to(replacement_path)
        else:
            implementation.write_bytes(replacement_path.read_bytes())
        state["swapped"] = True
        return installed

    def counting_consumer(*args, **kwargs):
        state["consumer_calls"] += 1
        return original_consumer(*args, **kwargs)

    def forbidden_path_read(*_args, **_kwargs):
        state["path_reads"] += 1
        raise AssertionError("downstream registry consumer reopened a path")

    monkeypatch.setattr(
        evidence_module,
        "_verify_running_controller_for_evidence",
        verify_then_swap,
    )
    monkeypatch.setattr(
        frames_module, "_consume_verified_registry", counting_consumer
    )
    monkeypatch.setattr(
        frames_module, "read_canonical_regular_bytes", forbidden_path_read
    )
    lock_path = tmp_path / "authority-lock.json"
    args = evidence_module.build_parser().parse_args(
        [
            "verify-evidence",
            "--index",
            str(index_path),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            hashlib.sha256(lock_path.read_bytes()).hexdigest(),
        ]
    )

    result = evidence_module.dispatch(args)

    assert state["swapped"]
    assert state["consumer_calls"] >= 2
    assert state["path_reads"] == 0
    assert result["status"] == "PASS"


def _complete_two_subject_reconstructable_index(tmp_path: Path) -> Path:
    index_path = _complete_reconstructable_subject_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    subject_a = index["subjects"][0]
    subject_b = copy.deepcopy(subject_a)

    source_a = tmp_path / index["subject_sources"][0]["root"]
    source_b = tmp_path / "indexed-subject-source-b"
    shutil.copytree(source_a, source_b)
    mode_marker = next(path for path in sorted(source_b.rglob("*")) if path.is_file())
    mode_marker.chmod(mode_marker.stat().st_mode | stat.S_IXUSR)
    manifest_b = evidence_module.build_tracked_source_manifest(
        source_b, ["."], "subject-source"
    )
    manifest_b_path = tmp_path / "subject-source-b-manifest.json"
    write_canonical_json(manifest_b_path, manifest_b, exclusive=True)
    index["subject_sources"].append(
        {
            "subject_id": "subject-b",
            "root": source_b.relative_to(tmp_path).as_posix(),
            "manifest": _indexed_reference(tmp_path, manifest_b_path),
        }
    )

    lock_path = tmp_path / "authority-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    lock_subject_b = copy.deepcopy(lock["subjects"][0])
    lock_subject_b.update(
        {
            "subject_id": "subject-b",
            "repository_role": "CONTROLLED_B",
            "normalized_repository_identity": "github.com/example/subject-b",
            "tracked_source_manifest_sha256": canonical_sha256(manifest_b),
        }
    )
    lock["subjects"].append(lock_subject_b)
    lock_path.write_bytes(canonical_json_bytes(lock))

    reference_fields = (
        "bridge_record",
        "source_record",
        "build_descriptor",
        "adapter_discovery",
        "source_scale",
        "public_frame",
        "profiling_workload",
        "profiling_results",
        "common_inputs",
        "common_input_validity",
        "technique_profile",
        "sites",
        "subject",
    )
    for field in reference_fields:
        source = tmp_path / subject_a[field]["path"]
        clone = tmp_path / f"subject-b-{field}.json"
        clone.write_bytes(source.read_bytes())
        subject_b[field] = _indexed_reference(tmp_path, clone)

    cloned_job_ids = []
    cloned_traces = []
    for ordinal, trace_a in enumerate(subject_a["profiling_traces"], start=1):
        trace_source = tmp_path / trace_a["artifact"]["path"]
        trace_clone = tmp_path / f"subject-b-profile-trace-{ordinal:02d}.json"
        trace_clone.write_bytes(trace_source.read_bytes())
        job_id = _digest(f"subject-b-profile-{ordinal:02d}")
        cloned_job_ids.append(job_id)
        attempt_a = tmp_path / f"jobs/PHASE_1/{trace_a['job_id']}/1"
        intent = json.loads((attempt_a / "intent.json").read_text(encoding="utf-8"))
        result = json.loads((attempt_a / "result.json").read_text(encoding="utf-8"))
        intent["job_id"] = job_id
        intent["cwd_identity"] = "subject:subject-b"
        result["job_id"] = job_id
        result["call_trace_identity"] = canonical_sha256(
            {
                "job_id": job_id,
                "attempt": 1,
                "behavior_id": trace_a["behavior_id"],
                "call_trace_sha256": trace_a["artifact"]["sha256"],
                "domain": "P3-PROFILING-TRACE-v1",
            }
        )
        attempt_b = tmp_path / f"jobs/PHASE_1/{job_id}/1"
        attempt_b.mkdir(parents=True)
        (attempt_b / "intent.json").write_bytes(canonical_json_bytes(intent))
        (attempt_b / "result.json").write_bytes(canonical_json_bytes(result))
        cloned_traces.append(
            {
                **trace_a,
                "job_id": job_id,
                "artifact": _indexed_reference(tmp_path, trace_clone),
            }
        )
    subject_b.update(
        {
            "subject_id": "subject-b",
            "source_root": source_b.relative_to(tmp_path).as_posix(),
            "profiling_traces": cloned_traces,
        }
    )
    index["subjects"].append(subject_b)

    phase_one = next(
        entry for entry in index["phase_receipts"] if entry["phase"] == "PHASE_1"
    )
    expected_path = tmp_path / phase_one["expected_jobs"]["path"]
    expected_jobs = json.loads(expected_path.read_text(encoding="utf-8"))
    expected_path.write_bytes(canonical_json_bytes(sorted(expected_jobs + cloned_job_ids)))
    phase_one["expected_jobs"] = _indexed_reference(tmp_path, expected_path)
    _refresh_attempt_evidence(tmp_path, index)
    _refresh_external_authority_jobs(tmp_path, index)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))
    return index_path


def test_verify_evidence_accepts_complete_sorted_two_subject_set(tmp_path):
    result = _run_evidence_index(_complete_two_subject_reconstructable_index(tmp_path))

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["subject_count"] == 2


@pytest.mark.parametrize("mutation", ["omission", "duplicate_clone", "swap_order"])
def test_verify_evidence_rejects_subject_rows_not_exactly_covering_lock(
    tmp_path, mutation
):
    index_path = _complete_two_subject_reconstructable_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if mutation == "omission":
        index["subjects"].pop()
    elif mutation == "duplicate_clone":
        index["subjects"][1]["subject_id"] = "subject-a"
        index["subjects"][1]["source_root"] = index["subjects"][0]["source_root"]
        for trace_a, trace_clone in zip(
            index["subjects"][0]["profiling_traces"],
            index["subjects"][1]["profiling_traces"],
        ):
            trace_clone["job_id"] = trace_a["job_id"]
    else:
        index["subjects"].reverse()
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_MANIFEST"


def test_verify_evidence_accepts_locked_subject_root_profiling_cwd(tmp_path):
    index_path = _complete_reconstructable_subject_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    for intent_path in sorted((tmp_path / "jobs/PHASE_1").rglob("intent.json")):
        intent = json.loads(intent_path.read_text(encoding="utf-8"))
        intent["cwd_identity"] = "subject:subject-a"
        intent_path.write_bytes(canonical_json_bytes(intent))
    _refresh_attempt_evidence(tmp_path, index)
    _refresh_external_authority_jobs(tmp_path, index)
    index_body = {
        key: value for key, value in index.items() if key != "artifact_sha256"
    }
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))
    lock_path = tmp_path / "authority-lock.json"
    literal_lock_sha256 = hashlib.sha256(lock_path.read_bytes()).hexdigest()

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--index",
            str(index_path),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            literal_lock_sha256,
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "PASS"


def test_no_execution_verifier_uses_only_installed_reviewed_registries(
    tmp_path, monkeypatch
):
    index_path = _complete_reconstructable_subject_index(tmp_path)
    index = json.loads(index_path.read_text(encoding="utf-8"))
    phase_zero_intent = next((tmp_path / "jobs/PHASE_0").rglob("intent.json"))
    intent = json.loads(phase_zero_intent.read_text(encoding="utf-8"))
    intent["argv"] = [
        "verify-only",
        "https://example.invalid/plausible-command?argv=python3",
    ]
    phase_zero_intent.write_bytes(canonical_json_bytes(intent))
    _refresh_attempt_evidence(tmp_path, index)
    _refresh_external_authority_jobs(tmp_path, index)
    index_body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    counts = {
        "process": 0,
        "dns": 0,
        "connection": 0,
        "socket": 0,
        "reviewed_executor": 0,
        "installed_loader": 0,
        "evidence_loader": 0,
    }

    def process_attempt(*_args, **_kwargs):
        counts["process"] += 1
        raise AssertionError("verification must not launch a process")

    def dns_attempt(*_args, **_kwargs):
        counts["dns"] += 1
        raise AssertionError("verification must not resolve DNS")

    def connection_attempt(*_args, **_kwargs):
        counts["connection"] += 1
        raise AssertionError("verification must not connect")

    def socket_attempt(*_args, **_kwargs):
        counts["socket"] += 1
        raise AssertionError("verification must not create sockets")

    original_executor = frames_module._execute_verified_python
    original_adapter_loader = frames_module._load_adapter_discover
    original_generator_loader = frames_module._load_input_generator_callable

    def reviewed_executor(operation):
        counts["reviewed_executor"] += 1
        return original_executor(operation)

    def adapter_loader(logical_filename, adapter_id, source_bytes):
        assert type(logical_filename) is str
        assert not Path(logical_filename).is_absolute()
        counts["installed_loader"] += 1
        return original_adapter_loader(logical_filename, adapter_id, source_bytes)

    def generator_loader(snapshot, generator_id):
        assert type(snapshot.logical_filename) is str
        assert not Path(snapshot.logical_filename).is_absolute()
        counts["installed_loader"] += 1
        return original_generator_loader(snapshot, generator_id)

    monkeypatch.setattr(subprocess, "run", process_attempt)
    monkeypatch.setattr(subprocess, "Popen", process_attempt)
    monkeypatch.setattr(os, "system", process_attempt)
    monkeypatch.setattr(socket, "socket", socket_attempt)
    monkeypatch.setattr(socket, "create_connection", connection_attempt)
    monkeypatch.setattr(socket, "getaddrinfo", dns_attempt)
    monkeypatch.setattr(frames_module, "_execute_verified_python", reviewed_executor)
    monkeypatch.setattr(frames_module, "_load_adapter_discover", adapter_loader)
    monkeypatch.setattr(
        frames_module, "_load_input_generator_callable", generator_loader
    )

    lock_path = tmp_path / "authority-lock.json"
    expected_lock_sha256 = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    args = evidence_module.build_parser().parse_args(
        [
            "verify-evidence",
            "--index",
            str(index_path),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            expected_lock_sha256,
        ]
    )
    result = evidence_module.dispatch(args)

    assert result["status"] == "PASS"
    assert counts["process"] == 0
    assert counts["dns"] == 0
    assert counts["connection"] == 0
    assert counts["socket"] == 0
    assert counts["reviewed_executor"] > 0
    assert counts["installed_loader"] > 0
    assert counts["evidence_loader"] == 0


def test_verify_evidence_rejects_legacy_subject_mixed_with_reconstructable(tmp_path):
    index_path = _complete_reconstructable_subject_index(tmp_path)
    index = json.loads(index_path.read_text())
    legacy = {
        key: value
        for key, value in index["subjects"][0].items()
        if key
        in {
            "phase",
            "controlled_subject_source_id",
            "controlled_subject_id",
            "public_frame",
            "profiling_workload",
            "profiling_results",
            "common_inputs",
            "common_input_validity",
            "slot_artifacts",
        }
    }
    index["subjects"].append(legacy)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SCHEMA_KEYS"


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_role",
        "missing_trace_digest",
        "altered_trace_bytes",
        "cross_subject_swap",
        "stdout_only_forgery",
    ],
)
def test_verify_evidence_authenticates_profile_trace_to_terminal_attempt(
    tmp_path, mutation
):
    index_path = _complete_reconstructable_subject_index(tmp_path)
    index = json.loads(index_path.read_text())
    trace_entry = index["subjects"][0]["profiling_traces"][0]
    attempt_root = tmp_path / f"jobs/PHASE_1/{trace_entry['job_id']}/1"
    intent_path = attempt_root / "intent.json"
    result_path = attempt_root / "result.json"
    intent = json.loads(intent_path.read_text())
    result_record = json.loads(result_path.read_text())
    if mutation == "wrong_role":
        intent["job_role"] = "PRIMARY_CONTROLLED"
    elif mutation == "missing_trace_digest":
        result_record["call_trace_sha256"] = None
    elif mutation == "altered_trace_bytes":
        trace_path = tmp_path / trace_entry["artifact"]["path"]
        trace = json.loads(trace_path.read_text())
        trace.append({"module": "forged.subject", "symbol": "forged"})
        trace_path.write_bytes(canonical_json_bytes(trace))
        trace_entry["artifact"]["sha256"] = hashlib.sha256(
            trace_path.read_bytes()
        ).hexdigest()
    elif mutation == "cross_subject_swap":
        intent["cwd_identity"] = "0" * 64
    else:
        result_record["stdout_sha256"] = result_record["call_trace_sha256"]
        result_record["call_trace_sha256"] = None
        result_record["call_trace_identity"] = None
    if mutation in {"wrong_role", "cross_subject_swap"}:
        intent_path.write_bytes(canonical_json_bytes(intent))
    if mutation in {"missing_trace_digest", "stdout_only_forgery"}:
        result_path.write_bytes(canonical_json_bytes(result_record))
    if mutation == "cross_subject_swap":
        _refresh_attempt_evidence(tmp_path, index)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] in {
        "E_AUTHORITY_INTENT",
        "E_PROFILE_TRACE_BINDING",
        "E_PROFILE_ATTEMPT_BINDING",
    }
    assert not result.stdout


def _complete_p12_evidence_index(tmp_path: Path) -> Path:
    from p3_v3.run_records import (
        create_intent,
        freeze_p12_denominator,
        recompute_p12_summary,
        write_result,
    )

    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    job = {
        "job_id": _digest("p12-job-01"),
        "object_type": "P12_FAULT",
        "object_id": "fault-01",
        "mr_id": "mr-01",
        "evaluation_input_class": "E_COMMON",
        "evaluation_input_id": "p12-common-01",
        "repetition_id": 1,
        "environment_id": "p12-env-01",
        "job_role": "P12",
        "weight": 1,
    }
    denominator = freeze_p12_denominator(["fault-01"], [job])
    intent = {
        key: value for key, value in job.items() if key != "weight"
    } | {
        "protocol_sha256": index["protocol"]["sha256"],
        "phase": "PHASE_7",
        "argv": ["p12-runner", "fault-01"],
        "cwd_identity": "p12-fixture-root",
        "environment_sha256": "8" * 64,
        "input_sha256": ["9" * 64],
        "seed": None,
        "timeout_seconds": 30,
        "attempt": 1,
    }
    attempt = tmp_path / f"jobs/PHASE_7/{job['job_id']}/1"
    create_intent(attempt, intent)
    result_record = {
        "job_id": job["job_id"],
        "attempt": 1,
        "status": "PASS",
        "exit_code": 0,
        "stdout_sha256": "a" * 64,
        "stderr_sha256": "b" * 64,
        "duration_seconds": 0.25,
        "failure_code": "",
        "scientific_outcome": "MR_SATISFIED",
        "call_trace_sha256": None,
        "call_trace_identity": None,
    }
    write_result(attempt, result_record)
    terminal = [{"intent": intent, "result": result_record}]
    result_rows = [
        {
            "job_id": job["job_id"],
            "scientific_outcome": result_record["scientific_outcome"],
        }
    ]
    summary = recompute_p12_summary(denominator, terminal)
    p12_paths = {}
    for name, artifact in {
        "denominator": denominator,
        "result_rows": result_rows,
        "summary": summary,
    }.items():
        path = tmp_path / f"p12-{name}.json"
        write_canonical_json(path, artifact, exclusive=True)
        p12_paths[name] = path
    expected_path = tmp_path / "phase-7-expected-jobs.json"
    write_canonical_json(expected_path, [job["job_id"]], exclusive=True)
    output_path = tmp_path / "phase-7-output.json"
    output_body = {
        "schema_version": "p3-phase-output-fixture-v1",
        "denominator_sha256": denominator["artifact_sha256"],
    }
    write_canonical_json(
        output_path,
        {**output_body, "artifact_sha256": canonical_sha256(output_body)},
        exclusive=True,
    )
    receipt_path = tmp_path / "phase-7-receipt.json"
    write_canonical_json(receipt_path, {"pending": True}, exclusive=True)
    index["phase_coverage"] = ["PHASE_0", "PHASE_7"]
    index["phase_receipts"].append(
        {
            "phase": "PHASE_7",
            "receipt": _indexed_reference(tmp_path, receipt_path),
            "expected_jobs": _indexed_reference(tmp_path, expected_path),
            "output_manifest": _indexed_reference(tmp_path, output_path),
        }
    )
    index["p12"] = {
        name: _indexed_reference(tmp_path, path) for name, path in p12_paths.items()
    }
    _refresh_attempt_evidence(tmp_path, index)
    _refresh_external_authority_jobs(tmp_path, index)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))
    return index_path


def test_verify_evidence_rebuilds_p12_rows_and_summary_from_terminal_attempts(tmp_path):
    result = _run_evidence_index(_complete_p12_evidence_index(tmp_path))

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["authorized_real_p12_job_count"] == 1
    assert json.loads(result.stdout)["recorded_real_scientific_terminal_count"] == 1


@pytest.mark.parametrize(
    ("field", "expected_code"),
    [("result_rows", "E_P12_RESULT_ROWS"), ("summary", "E_P12_SUMMARY")],
)
def test_verify_evidence_rejects_rehashed_p12_declarations(
    tmp_path, field, expected_code
):
    index_path = _complete_p12_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    reference = index["p12"][field]
    path = tmp_path / reference["path"]
    artifact = json.loads(path.read_text())
    if field == "result_rows":
        artifact[0]["scientific_outcome"] = "MR_VIOLATION"
    else:
        artifact["lower_numerator"] = 1
        body = {
            key: value for key, value in artifact.items() if key != "artifact_sha256"
        }
        artifact["artifact_sha256"] = canonical_sha256(body)
    path.write_bytes(canonical_json_bytes(artifact))
    reference["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == expected_code
    assert not result.stdout


@pytest.mark.parametrize(
    "field",
    [
        *_PROTOCOL_ARTIFACT_FIELDS,
        "adapter_registry_sha256",
        "input_generator_registry_sha256",
    ],
)
def test_protocol_binding_rejects_every_rehashed_authority_byte(tmp_path, field):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    if field == "adapter_registry_sha256":
        reference = index["adapter_registries"][0]
    elif field == "input_generator_registry_sha256":
        reference = index["input_generator_registries"][0]
    else:
        reference = index["protocol_artifacts"][field]
    artifact_path = tmp_path / reference["path"]
    artifact_path.write_bytes(artifact_path.read_bytes() + b"forged\n")
    reference["sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] in {
        "E_PROTOCOL_BINDING",
        "E_ADAPTER_REGISTRY_HASH",
        "E_AUTHORITY_MANIFEST",
        "E_GENERATOR_REGISTRY_HASH",
        "E_NONCANONICAL_JSON",
    }


@pytest.mark.parametrize("collection", ["adapter_registries", "input_generator_registries"])
def test_protocol_binding_rejects_omitted_mandatory_registry(tmp_path, collection):
    body = _empty_evidence_index_body(tmp_path)
    body[collection] = []
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, body)

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_BINDING"


@pytest.mark.parametrize("collection", ["adapter_registries", "input_generator_registries"])
def test_protocol_binding_requires_exactly_one_registry_authority(tmp_path, collection):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    source = tmp_path / index[collection][0]["path"]
    duplicate = tmp_path / f"duplicate-{collection}.json"
    duplicate.write_bytes(source.read_bytes())
    index[collection].append(_indexed_reference(tmp_path, duplicate))
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_BINDING"


def test_mapping_free_yaml_claim_ceiling_fails_closed(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    authority_ref = index["protocol_artifacts"]["claim_ceiling_sha256"]
    authority_path = tmp_path / authority_ref["path"]
    authority_path.write_text("claims_initial_status: blocked\n", encoding="utf-8")
    authority_ref["sha256"] = hashlib.sha256(authority_path.read_bytes()).hexdigest()
    protocol_path = tmp_path / index["protocol"]["path"]
    protocol = json.loads(protocol_path.read_text())
    protocol["claim_ceiling_sha256"] = authority_ref["sha256"]
    protocol_body = {
        key: value for key, value in protocol.items() if key != "artifact_sha256"
    }
    protocol["artifact_sha256"] = canonical_sha256(protocol_body)
    protocol_path.write_bytes(canonical_json_bytes(protocol))
    index["protocol"]["sha256"] = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    index_body = {
        key: value for key, value in index.items() if key != "artifact_sha256"
    }
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(canonical_json_bytes(index))

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_PROTOCOL"
    assert not result.stdout


@pytest.mark.parametrize("field", _PROTOCOL_ARTIFACT_FIELDS)
def test_protocol_binding_rejects_omitted_mandatory_policy(tmp_path, field):
    body = _empty_evidence_index_body(tmp_path)
    del body["protocol_artifacts"][field]
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, body)

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SCHEMA_KEYS"


@pytest.mark.parametrize("late_target", ["claims", "rq_spec", "claim_ceiling"])
def test_claim_verification_uses_indexed_immutable_bytes_after_late_path_swap(
    tmp_path, late_target
):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    lock_path = tmp_path / "authority-lock.json"
    lock = evidence_module.load_authority_lock(
        lock_path, hashlib.sha256(lock_path.read_bytes()).hexdigest()
    )
    _index, material = evidence_module._load_evidence_index(
        index_path, lock, lock_path
    )
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if late_target == "claims":
        swapped = tmp_path / index["claims"]["path"]
        swapped.write_bytes(canonical_json_bytes({"forged": True}))
    else:
        field = f"{late_target}_sha256"
        swapped = tmp_path / index["protocol_artifacts"][field]["path"]
        swapped.write_bytes(
            b"# forged RQ authority\n"
            if late_target == "rq_spec"
            else canonical_json_bytes({"forged": True})
        )

    claims = evidence_module._verify_claim_reconstruction(material)

    assert claims["schema_version"] == "p3-claim-evidence-v1"


@pytest.mark.parametrize(
    "mutation",
    ["unindexed", "supported", "result_prose", "missing", "extra", "renamed", "rq_swap"],
)
def test_claim_ledger_is_fail_closed_in_final_verification(tmp_path, mutation):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    claims_path = tmp_path / index["claims"]["path"]
    claims = json.loads(claims_path.read_text())
    claim = claims["claims"][0]
    if mutation == "unindexed":
        claim["evidence_references"] = ["not-indexed.json"]
    elif mutation == "supported":
        claim["status"] = "supported"
    else:
        if mutation == "result_prose":
            claim["result_prose"] = "The results support the claim."
        elif mutation == "missing":
            claims["claims"].pop()
        elif mutation == "extra":
            extra = json.loads(json.dumps(claims["claims"][-1]))
            extra["claim_id"] = "C8_FORGED"
            extra_body = {
                key: value for key, value in extra.items() if key != "artifact_sha256"
            }
            extra["artifact_sha256"] = canonical_sha256(extra_body)
            claims["claims"].append(extra)
        elif mutation == "renamed":
            claim["claim_id"] = "C1_RENAMED"
        else:
            claim["rqs"] = ["RQ3"]
    if mutation not in {"missing", "extra"}:
        claim_body = {
            key: value for key, value in claim.items() if key != "artifact_sha256"
        }
        claim["artifact_sha256"] = canonical_sha256(claim_body)
    claims_body = {
        key: value for key, value in claims.items() if key != "artifact_sha256"
    }
    claims["artifact_sha256"] = canonical_sha256(claims_body)
    claims_path.write_bytes(
        json.dumps(claims, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    index["claims"]["sha256"] = hashlib.sha256(claims_path.read_bytes()).hexdigest()
    index_body = {
        key: value for key, value in index.items() if key != "artifact_sha256"
    }
    index["artifact_sha256"] = canonical_sha256(index_body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] in {
        "E_CLAIM_EVIDENCE",
        "E_CLAIM_STATUS",
        "E_CLAIM_SET",
        "E_SCHEMA_KEYS",
    }
    assert not result.stdout


def test_evidence_index_rejects_unindexed_attempt_file(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    job_id = _digest("phase-0-job")
    (tmp_path / f"jobs/PHASE_0/{job_id}/1/unindexed.txt").write_text("x")

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_INTENT"


def test_evidence_index_rejects_unindexed_file_outside_declared_roots(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    (tmp_path / "unindexed-root.txt").write_text("forged", encoding="utf-8")

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_INDEX_UNINDEXED"


def test_evidence_index_rejects_symlink_in_indexed_path_ancestor(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    claims_path = tmp_path / index["claims"]["path"]
    outside = tmp_path / "outside"
    outside.mkdir()
    os.rename(claims_path, outside / "claims.json")
    (tmp_path / "linked").symlink_to(outside, target_is_directory=True)
    index["claims"] = {
        "path": "linked/claims.json",
        "sha256": hashlib.sha256((outside / "claims.json").read_bytes()).hexdigest(),
    }
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_INDEX_PATH"


def test_evidence_index_rejects_duplicate_phase_receipt(tmp_path):
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    duplicate = {"phase": "PHASE_0"}
    for field in ("receipt", "expected_jobs", "output_manifest"):
        source = tmp_path / index["phase_receipts"][0][field]["path"]
        target = tmp_path / f"duplicate-{field}.json"
        target.write_bytes(source.read_bytes())
        duplicate[field] = _indexed_reference(tmp_path, target)
    index["phase_receipts"].append(duplicate)
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_INDEX_COVERAGE"


def test_evidence_index_rejects_rebuilt_attempts_bound_to_another_protocol(tmp_path):
    from p3_v3.run_records import close_phase, reconstruct_attempt_events

    index_path = _complete_phase_zero_evidence_index(tmp_path)
    index = json.loads(index_path.read_text())
    job_id = _digest("phase-0-job")
    intent_path = tmp_path / f"jobs/PHASE_0/{job_id}/1/intent.json"
    intent = json.loads(intent_path.read_text())
    intent["protocol_sha256"] = "0" * 64
    intent_path.write_bytes(
        json.dumps(intent, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    events = reconstruct_attempt_events(tmp_path / "jobs")
    ledger_path = tmp_path / index["ledger"]["path"]
    ledger_path.write_bytes(
        b"".join(
            json.dumps(event, sort_keys=True, separators=(",", ":")).encode() + b"\n"
            for event in events
        )
    )
    index["ledger"]["sha256"] = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    receipt_entry = index["phase_receipts"][0]
    output_manifest = json.loads(
        (tmp_path / receipt_entry["output_manifest"]["path"]).read_text()
    )
    receipt = close_phase(
        "PHASE_0",
        "0" * 64,
        [job_id],
        ledger_path,
        output_manifest["artifact_sha256"],
    )
    receipt_path = tmp_path / receipt_entry["receipt"]["path"]
    receipt_path.write_bytes(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    receipt_entry["receipt"]["sha256"] = hashlib.sha256(
        receipt_path.read_bytes()
    ).hexdigest()
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_AUTHORITY_INTENT"


def _phase_zero_index_with_slots(tmp_path: Path, slots: list[dict]) -> Path:
    index_path = _complete_phase_zero_evidence_index(tmp_path)
    source_id = "21" * 32
    rows = []
    for ordinal in range(1, 31):
        seed_digest = canonical_sha256(
            {
                "domain": "P3-E-COMMON-SEED-v1",
                "controlled_subject_source_id": source_id,
                "ordinal": ordinal,
            }
        )
        seed = int.from_bytes(bytes.fromhex(seed_digest)[:8], "big")
        identity = {
            "controlled_subject_source_id": source_id,
            "ordinal": ordinal,
            "generator_id": None,
            "schema_selection_key": None,
            "raw_schema_sha256": None,
            "schema_provenance_path": None,
            "schema_provenance_span_or_key": None,
            "generator_source_sha256": None,
            "raw_payload_sha256": None,
            "status": "COMMON_INPUT_UNAVAILABLE",
            "failure_code": "COMMON_INPUT_UNAVAILABLE",
            "domain": "P3-E-COMMON-INPUT-v1",
        }
        rows.append(
            {
                "ordinal": ordinal,
                "seed": seed,
                "generator_id": None,
                "schema_kind": None,
                "schema_selection_key": None,
                "raw_schema_sha256": None,
                "schema_provenance_path": None,
                "schema_provenance_span_or_key": None,
                "generator_source_sha256": None,
                "status": "COMMON_INPUT_UNAVAILABLE",
                "failure_code": "COMMON_INPUT_UNAVAILABLE",
                "envelope": None,
                "raw_payload_sha256": None,
                "input_id": canonical_sha256(identity),
            }
        )
    frame_body = {
        "schema_version": "p3-public-behavior-frame-v1",
        "controlled_subject_source_id": source_id,
        "rows": [],
        "public_schemas": [],
    }
    frame = {**frame_body, "artifact_sha256": canonical_sha256(frame_body)}
    workload = select_profiling_workload(frame, "S")
    common_body = {
        "schema_version": "p3-evaluation-inputs-common-v1",
        "controlled_subject_source_id": source_id,
        "eligible_schema_count": 0,
        "rows": rows,
    }
    common = {**common_body, "artifact_sha256": canonical_sha256(common_body)}
    validity_body = {
        "schema_version": "p3-common-input-validity-v1",
        "controlled_subject_source_id": source_id,
        "inventory_artifact_sha256": common["artifact_sha256"],
        "rows": [
            {
                key: row[key]
                for key in (
                    "ordinal",
                    "input_id",
                    "raw_payload_sha256",
                    "envelope",
                    "generator_id",
                    "schema_kind",
                    "schema_selection_key",
                    "raw_schema_sha256",
                    "seed",
                    "status",
                    "failure_code",
                )
            }
            for row in rows
        ],
        "sites": [],
        "contracts": [],
        "profile": {},
        "frame_artifact_sha256": frame["artifact_sha256"],
    }
    validity = {**validity_body, "artifact_sha256": canonical_sha256(validity_body)}
    artifacts = {
        "public-frame.json": frame,
        "workload.json": workload,
        "profiling-results.json": {"status": "NOT_RUN"},
        "common.json": common,
        "validity.json": validity,
    }
    for name, artifact in artifacts.items():
        write_canonical_json(tmp_path / name, artifact, exclusive=True)
    slot_refs = []
    for index, slot in enumerate(slots):
        path = tmp_path / f"slot-{index}.json"
        write_canonical_json(path, slot, exclusive=True)
        slot_refs.append(
            {
                "slot_id": slot["slot_id"],
                "controlled_subject_id": "22" * 32,
                "artifact": _indexed_reference(tmp_path, path),
            }
        )
    index = json.loads(index_path.read_text())
    index["subjects"] = [
        {
            "phase": "PHASE_0",
            "controlled_subject_source_id": source_id,
            "controlled_subject_id": "22" * 32,
            "public_frame": _indexed_reference(
                tmp_path, tmp_path / "public-frame.json"
            ),
            "profiling_workload": _indexed_reference(
                tmp_path, tmp_path / "workload.json"
            ),
            "profiling_results": _indexed_reference(
                tmp_path, tmp_path / "profiling-results.json"
            ),
            "common_inputs": _indexed_reference(tmp_path, tmp_path / "common.json"),
            "common_input_validity": _indexed_reference(
                tmp_path, tmp_path / "validity.json"
            ),
            "slot_artifacts": slot_refs,
        }
    ]
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    return index_path


def _reconstructable_index_with_slots(tmp_path: Path, slots: list[dict]) -> Path:
    index_path = _complete_reconstructable_subject_index(tmp_path)
    index = json.loads(index_path.read_text())
    controlled_subject_id = index["subjects"][0]["controlled_subject_id"]
    slot_refs = []
    for ordinal, slot in enumerate(slots):
        path = tmp_path / f"slot-{ordinal}.json"
        write_canonical_json(path, slot, exclusive=True)
        slot_refs.append(
            {
                "slot_id": slot["slot_id"],
                "controlled_subject_id": controlled_subject_id,
                "artifact": _indexed_reference(tmp_path, path),
            }
        )
    index["subjects"][0]["slot_artifacts"] = slot_refs
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(canonical_json_bytes(index))
    return index_path


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("coordinate", "E_SLOT_COORDINATE"),
        ("input_role", "E_SLOT_INPUT_ROLE"),
        ("unknown_common", "E_SLOT_INPUT_ROLE"),
    ],
)
def test_evidence_index_rejects_slot_coordinate_or_input_role_drift(
    tmp_path, mutation, expected_code
):
    slot_id = "61" * 32
    not_applicable = {
        "slot_id": slot_id,
        "chronology": ["APPLICABILITY_CLOSED_NOT_APPLICABLE"],
        "contract": None,
        "e_contract": None,
        "patch": None,
        "certification_witness": None,
        "e_common_input_ids": [],
        "e_contract_input_ids": [],
    }
    if mutation == "coordinate":
        slots = [not_applicable, dict(not_applicable)]
    else:
        common_id = "71" * 32
        contract_id = common_id if mutation == "input_role" else "75" * 32
        slots = [
            {
                "slot_id": slot_id,
                "chronology": [
                    "SITE_FROZEN",
                    "CONTRACT_FROZEN",
                    "E_CONTRACT_FROZEN",
                    "PATCH_FROZEN",
                    "CERTIFICATION_WITNESS_SELECTED",
                    "TERMINAL_STATE",
                ],
                "contract": {"contract_id": "72" * 32},
                "e_contract": {"rows": []},
                "patch": {"patch_id": "73" * 32},
                "certification_witness": {"witness_id": "74" * 32},
                "e_common_input_ids": [common_id],
                "e_contract_input_ids": [contract_id],
            }
        ]
    result = _run_evidence_index(_reconstructable_index_with_slots(tmp_path, slots))

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == expected_code


@pytest.mark.parametrize("mutation", ["contract_rows", "hidden_overlap"])
def test_evidence_index_binds_slot_role_lists_to_real_inventories(tmp_path, mutation):
    slot_id = "61" * 32
    slot = {
        "slot_id": slot_id,
        "chronology": [
            "SITE_FROZEN",
            "CONTRACT_FROZEN",
            "E_CONTRACT_FROZEN",
            "PATCH_FROZEN",
            "CERTIFICATION_WITNESS_SELECTED",
            "TERMINAL_STATE",
        ],
        "contract": {"contract_id": "72" * 32},
        "e_contract": {"rows": [{"input_id": "75" * 32}]},
        "patch": {"patch_id": "73" * 32},
        "certification_witness": {"witness_id": "74" * 32},
        "e_common_input_ids": [],
        "e_contract_input_ids": ["76" * 32],
    }
    index_path = _reconstructable_index_with_slots(tmp_path, [slot])
    index = json.loads(index_path.read_text())
    common = json.loads(
        (tmp_path / index["subjects"][0]["common_inputs"]["path"]).read_text()
    )
    common_id = common["rows"][0]["input_id"]
    slot_path = tmp_path / index["subjects"][0]["slot_artifacts"][0]["artifact"]["path"]
    material = json.loads(slot_path.read_text())
    if mutation == "contract_rows":
        material["e_contract_input_ids"] = ["76" * 32]
    else:
        material["e_common_input_ids"] = [common_id]
        material["e_contract"]["rows"] = [{"input_id": common_id}]
        material["e_contract_input_ids"] = ["76" * 32]
    slot_path.write_bytes(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    index["subjects"][0]["slot_artifacts"][0]["artifact"]["sha256"] = hashlib.sha256(
        slot_path.read_bytes()
    ).hexdigest()
    body = {key: value for key, value in index.items() if key != "artifact_sha256"}
    index["artifact_sha256"] = canonical_sha256(body)
    index_path.write_bytes(
        json.dumps(index, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )

    result = _run_evidence_index(index_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SLOT_INPUT_ROLE"


def test_forged_evidence_index_is_rejected_without_pass_receipt(tmp_path):
    """Removing reconstruction cannot turn self-consistent declarations into PASS."""

    protocol = tmp_path / "protocol.json"
    _write_protocol(protocol, _protocol_body())
    claims = _blocked_claim_ledger("protocol.json")
    claims_path = tmp_path / "claims.json"
    write_canonical_json(claims_path, claims, exclusive=True)

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"")

    common_body = {
        "schema_version": "p3-evaluation-inputs-common-v1",
        "controlled_subject_source_id": "21" * 32,
        "eligible_schema_count": 0,
        "rows": [{"status": "FABRICATED"} for _ in range(30)],
    }
    common = {**common_body, "artifact_sha256": canonical_sha256(common_body)}
    common_path = tmp_path / "common.json"
    write_canonical_json(common_path, common, exclusive=True)

    denominator_body = {
        "schema_version": "p3-p12-denominator-v1",
        "p12_paired_ids": [],
        "jobs": [],
        "planned_count": 0,
        "job_inventory_sha256": canonical_sha256([]),
        "paired_ids_sha256": canonical_sha256([]),
    }
    denominator = {
        **denominator_body,
        "artifact_sha256": canonical_sha256(denominator_body),
    }
    denom_path = tmp_path / "denominator.json"
    write_canonical_json(denom_path, denominator, exclusive=True)
    summary_body = {
        "planned_count": 0,
        "denominator_sha256": denominator["artifact_sha256"],
        "status": "FABRICATED",
    }
    summary = {**summary_body, "artifact_sha256": canonical_sha256(summary_body)}
    summary_path = tmp_path / "summary.json"
    write_canonical_json(summary_path, summary, exclusive=True)

    result_rows_path = tmp_path / "p12-results.json"
    write_canonical_json(result_rows_path, [], exclusive=True)
    validity_path = tmp_path / "common-validity.json"
    write_canonical_json(validity_path, {"status": "FABRICATED"}, exclusive=True)
    public_frame_path = tmp_path / "public-frame.json"
    write_canonical_json(public_frame_path, {"status": "FABRICATED"}, exclusive=True)
    workload_path = tmp_path / "profiling-workload.json"
    write_canonical_json(workload_path, {"status": "FABRICATED"}, exclusive=True)
    profiling_path = tmp_path / "profiling-results.json"
    write_canonical_json(profiling_path, {"status": "FABRICATED"}, exclusive=True)

    index_body = {
        "schema_version": "P3_V3_EVIDENCE_INDEX_V1",
        "phase_coverage": ["PHASE_1"],
        "protocol": _indexed_reference(tmp_path, protocol),
        "adapter_registries": [],
        "input_generator_registries": [],
        "subjects": [
            {
                "phase": "PHASE_1",
                "controlled_subject_source_id": "21" * 32,
                "controlled_subject_id": "22" * 32,
                "public_frame": _indexed_reference(tmp_path, public_frame_path),
                "profiling_workload": _indexed_reference(tmp_path, workload_path),
                "profiling_results": _indexed_reference(tmp_path, profiling_path),
                "common_inputs": _indexed_reference(tmp_path, common_path),
                "common_input_validity": _indexed_reference(tmp_path, validity_path),
                "slot_artifacts": [],
            }
        ],
        "packages": [],
        "mr_chain": {},
        "job_root": "jobs",
        "ledger": _indexed_reference(tmp_path, ledger),
        "phase_receipts": [],
        "p12": {
            "denominator": _indexed_reference(tmp_path, denom_path),
            "result_rows": _indexed_reference(tmp_path, result_rows_path),
            "summary": _indexed_reference(tmp_path, summary_path),
        },
        "claims": _indexed_reference(tmp_path, claims_path),
    }
    index_path = tmp_path / "evidence-index.json"
    _write_evidence_index(index_path, index_body)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--index",
            str(index_path),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode != 0
    assert not result.stdout
    assert b'"status":"PASS"' not in result.stdout.encode()


def test_verify_evidence_accepts_only_one_index_argument():
    result = subprocess.run(
        ["python3", str(CLI), "verify-evidence", "--help"],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    assert "--index" in result.stdout
    assert "--authority-lock" in result.stdout
    assert "--authority-lock-sha256" in result.stdout
    for legacy in (
        "--protocol",
        "--manifest",
        "--ledger",
        "--phase-receipt",
        "--slot-artifacts",
        "--common-inputs",
        "--denominator",
        "--p12-summary",
        "--claims",
    ):
        assert legacy not in result.stdout


def test_external_authority_digest_fails_before_index_loading(tmp_path):
    lock_path = tmp_path / "authority-lock.json"
    lock_path.write_bytes(canonical_json_bytes(_authority_lock()))
    missing_index = tmp_path / "missing-index.json"

    missing = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--index",
            str(missing_index),
            "--authority-lock",
            str(lock_path),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert missing.returncode == 2
    assert "--authority-lock-sha256" in missing.stderr
    assert "E_INDEX" not in missing.stderr

    malformed = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--index",
            str(missing_index),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            "not-a-sha256",
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert malformed.returncode == 2
    assert json.loads(malformed.stderr)["code"] == "E_AUTHORITY_LOCK_DIGEST"
    assert "E_INDEX" not in malformed.stderr

    changed_lock = _authority_lock()
    changed_lock["task_id"] = "coordinated-reseal"
    lock_path.write_bytes(canonical_json_bytes(changed_lock))
    unchanged_expected_digest = hashlib.sha256(
        canonical_json_bytes(_authority_lock())
    ).hexdigest()
    changed = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--index",
            str(missing_index),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            unchanged_expected_digest,
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert changed.returncode == 2
    assert json.loads(changed.stderr)["code"] == "E_AUTHORITY_LOCK_DIGEST"
    assert "E_INDEX" not in changed.stderr


@pytest.mark.parametrize("expected_digest", ["not-a-sha256", "0" * 64])
def test_verify_evidence_parser_dispatch_checks_external_digest_before_index(
    tmp_path, monkeypatch, expected_digest
):
    lock_path = tmp_path / "authority-lock.json"
    lock_path.write_bytes(canonical_json_bytes(_authority_lock()))
    index_path = tmp_path / "missing-index.json"
    args = evidence_module.build_parser().parse_args(
        [
            "verify-evidence",
            "--index",
            str(index_path),
            "--authority-lock",
            str(lock_path),
            "--authority-lock-sha256",
            expected_digest,
        ]
    )

    def forbid_index_loading(*_args, **_kwargs):
        raise AssertionError("index loaded before external authority digest")

    monkeypatch.setattr(evidence_module, "_load_evidence_index", forbid_index_loading)
    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_DIGEST"):
        evidence_module.dispatch(args)


def test_cli_verify_package_rejects_unknown_pilot_schema(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_bytes(
        canonical_json_bytes(
            {
                "schema_version": "p3-pilot-future-v9",
                "role": "CONSTRUCTION_A",
                "parents": [],
                "files": [],
                "package_tree_sha256": "0" * 64,
                "artifact_sha256": "0" * 64,
            }
        )
    )
    args = evidence_module.build_parser().parse_args(
        ["verify-package", "--root", str(tmp_path), "--manifest", str(manifest)]
    )
    with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR_LEAK"):
        evidence_module.dispatch(args)


def test_cli_verify_run_records_rejects_pilot_schema_before_ledger_validation(
    tmp_path,
):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(
        canonical_json_bytes(
            {
                "schema_version": "p3-pilot-future-v9",
                "execution_class": "PILOT_ONLY",
                "denominator": "PILOT_ONLY",
            }
        )
    )
    args = evidence_module.build_parser().parse_args(
        ["verify-run-records", "--ledger", str(ledger)]
    )
    with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR_LEAK"):
        evidence_module.dispatch(args)


def test_cli_verify_evidence_rejects_pilot_artifact_before_confirmatory_validation(
    tmp_path,
):
    lock = tmp_path / "authority-lock.json"
    lock.write_bytes(
        canonical_json_bytes(
            {
                "schema_version": "p3-pilot-future-v9",
                "execution_class": "PILOT_ONLY",
                "denominator": "PILOT_ONLY",
            }
        )
    )
    index = tmp_path / "index.json"
    index.write_bytes(canonical_json_bytes({"schema_version": "p3-pilot-future-v9"}))
    args = evidence_module.build_parser().parse_args(
        [
            "verify-evidence",
            "--index",
            str(index),
            "--authority-lock",
            str(lock),
            "--authority-lock-sha256",
            file_sha256(lock),
        ]
    )
    with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR_LEAK"):
        evidence_module.dispatch(args)


def test_pilot_cli_forbids_source_and_execution_verbs():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    for verb in ("validate-source", "extract", "freeze", "execute", "certify"):
        with pytest.raises(SystemExit):
            parser.parse_args([verb])


def test_cxx_header_workload_cli_requires_command_and_paths():
    import scripts.p3_v3.profile as profile_cli

    parser = profile_cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])
    with pytest.raises(SystemExit):
        parser.parse_args(["run-cxx-header-workload"])
    required = {
        "--workload": "w.json",
        "--source-root": "src",
        "--compiler": "/usr/bin/c++",
        "--runtime-root": "rt",
        "--output": "out.json",
    }
    for omitted in required:
        argv = ["run-cxx-header-workload"]
        for flag, value in required.items():
            if flag != omitted:
                argv.extend([flag, value])
        with pytest.raises(SystemExit):
            parser.parse_args(argv)
    parsed = parser.parse_args(
        [
            "run-cxx-header-workload",
            "--workload",
            "w.json",
            "--source-root",
            "src",
            "--compiler",
            "/usr/bin/c++",
            "--runtime-root",
            "rt",
            "--output",
            "out.json",
        ]
    )
    assert parsed.command == "run-cxx-header-workload"
    assert parsed.workload == "w.json"
    assert parsed.source_root == "src"
    assert parsed.compiler == "/usr/bin/c++"
    assert parsed.runtime_root == "rt"
    assert parsed.output == "out.json"


def test_cxx_header_workload_cli_delegates_to_runner(tmp_path, monkeypatch):
    import scripts.p3_v3.profile as profile_cli

    workload_path = tmp_path / "workload.json"
    source_root = tmp_path / "source"
    runtime_root = tmp_path / "runtime"
    output = tmp_path / "receipt.json"
    workload = {"marker": True}
    write_canonical_json(workload_path, workload, exclusive=True)
    called = []

    def fake_run(loaded, *, source_root, compiler, runtime_root, receipt_path):
        called.append((loaded, source_root, compiler, runtime_root, receipt_path))

    monkeypatch.setattr(profile_cli, "run_cxx_header_workload", fake_run)
    assert profile_cli.main(
        [
            "run-cxx-header-workload",
            "--workload",
            str(workload_path),
            "--source-root",
            str(source_root),
            "--compiler",
            "/usr/bin/c++",
            "--runtime-root",
            str(runtime_root),
            "--output",
            str(output),
        ]
    ) == 0
    assert called == [
        (workload, source_root, Path("/usr/bin/c++"), runtime_root, output)
    ]
