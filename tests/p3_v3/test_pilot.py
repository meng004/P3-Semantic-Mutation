from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    write_canonical_json,
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _install_valid_verdict(monkeypatch, tmp_path: Path, markdown: Path) -> Path:
    import p3_v3.pilot as pilot

    verdict = tmp_path / "boost_math_pilot_foundation_sol_high_review.md"
    write_canonical_json(
        verdict,
        {
            "reviewed_plan_path": (
                "docs/superpowers/plans/"
                "2026-08-16-p3-boost-math-pilot-foundation-only.md"
            ),
            "reviewed_plan_sha256": _sha256_bytes(markdown.read_bytes()),
            "verdict": "PASS",
            "authorized_state": "PILOT_PLAN_FROZEN",
            "claims": "blocked",
        },
        exclusive=True,
    )
    monkeypatch.setattr(pilot, "CANONICAL_FOUNDATION_VERDICT_PATH", verdict)
    return verdict


def test_pilot_plan_requires_exact_keys():
    from p3_v3.pilot import validate_pilot_plan

    value = {
        "schema_version": "p3-pilot-plan-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
    }
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        validate_pilot_plan(value)


def test_pilot_plan_requires_self_hash(tmp_path, monkeypatch):
    from p3_v3.pilot import write_pilot_plan, validate_pilot_plan

    markdown = tmp_path / "plan.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    _install_valid_verdict(monkeypatch, tmp_path, markdown)
    written = write_pilot_plan(markdown, output)
    broken = dict(written)
    broken["artifact_sha256"] = "0" * 64
    with pytest.raises(EvidenceError, match="E_PILOT_PLAN_HASH"):
        validate_pilot_plan(broken)


def test_pilot_plan_binds_markdown_and_verdict(tmp_path, monkeypatch):
    from p3_v3.pilot import write_pilot_plan, validate_pilot_plan

    markdown = tmp_path / "plan.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    verdict = _install_valid_verdict(monkeypatch, tmp_path, markdown)
    written = write_pilot_plan(markdown, output)
    validated = validate_pilot_plan(written)
    assert validated["markdown_plan_sha256"] == _sha256_bytes(markdown.read_bytes())
    assert validated["sol_high_plan_verdict_sha256"] == _sha256_bytes(
        verdict.read_bytes()
    )
    assert validated["claims"] == "blocked"
    assert validated["formal_denominator_membership"] is False
    assert validated["rq4_supported"] is False
    assert validated["execution_class"] == "PILOT_ONLY"
    assert validated["denominator"] == "PILOT_ONLY"


def test_pilot_plan_predecessors_equal_plan_and_verdict(tmp_path, monkeypatch):
    from p3_v3.pilot import write_pilot_plan, validate_pilot_plan

    markdown = tmp_path / "plan.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    verdict = _install_valid_verdict(monkeypatch, tmp_path, markdown)
    validated = validate_pilot_plan(write_pilot_plan(markdown, output))
    assert validated["predecessor_sha256"] == sorted(
        [
            _sha256_bytes(markdown.read_bytes()),
            _sha256_bytes(verdict.read_bytes()),
        ]
    )


def test_pilot_plan_rejects_extra_predecessor(tmp_path, monkeypatch):
    from p3_v3.pilot import write_pilot_plan, validate_pilot_plan

    markdown = tmp_path / "plan.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    _install_valid_verdict(monkeypatch, tmp_path, markdown)
    written = write_pilot_plan(markdown, output)
    extra = list(written["predecessor_sha256"]) + ["0" * 64]
    written["predecessor_sha256"] = sorted(extra)
    with pytest.raises(EvidenceError, match="E_PILOT_PLAN_PREDECESSOR"):
        validate_pilot_plan(written)


def test_write_plan_rejects_missing_canonical_verdict(tmp_path, monkeypatch):
    import p3_v3.pilot as pilot

    markdown = tmp_path / "plan.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    missing = tmp_path / "missing-verdict.md"
    monkeypatch.setattr(pilot, "CANONICAL_FOUNDATION_VERDICT_PATH", missing)
    with pytest.raises(EvidenceError, match="E_PILOT_PLAN_VERDICT_ABSENT"):
        pilot.write_pilot_plan(markdown, output)


def test_write_plan_rejects_arbitrary_verdict_text(tmp_path, monkeypatch):
    import p3_v3.pilot as pilot

    markdown = tmp_path / "plan.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    verdict = tmp_path / "boost_math_pilot_foundation_sol_high_review.md"
    verdict.write_text("not a foundation verdict object\n", encoding="utf-8")
    monkeypatch.setattr(pilot, "CANONICAL_FOUNDATION_VERDICT_PATH", verdict)
    with pytest.raises(EvidenceError, match="E_PILOT_PLAN_VERDICT"):
        pilot.write_pilot_plan(markdown, output)


def test_write_plan_rejects_non_pass_verdict(tmp_path, monkeypatch):
    import p3_v3.pilot as pilot

    markdown = tmp_path / "plan.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    verdict = tmp_path / "boost_math_pilot_foundation_sol_high_review.md"
    write_canonical_json(
        verdict,
        {
            "reviewed_plan_path": (
                "docs/superpowers/plans/"
                "2026-08-16-p3-boost-math-pilot-foundation-only.md"
            ),
            "reviewed_plan_sha256": _sha256_bytes(markdown.read_bytes()),
            "verdict": "BLOCK",
            "authorized_state": "PILOT_PLAN_FROZEN",
            "claims": "blocked",
        },
        exclusive=True,
    )
    monkeypatch.setattr(pilot, "CANONICAL_FOUNDATION_VERDICT_PATH", verdict)
    with pytest.raises(EvidenceError, match="E_PILOT_PLAN_VERDICT"):
        pilot.write_pilot_plan(markdown, output)


def test_write_plan_rejects_verdict_plan_hash_mismatch(tmp_path, monkeypatch):
    import p3_v3.pilot as pilot

    markdown = tmp_path / "plan.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    verdict = tmp_path / "boost_math_pilot_foundation_sol_high_review.md"
    write_canonical_json(
        verdict,
        {
            "reviewed_plan_path": (
                "docs/superpowers/plans/"
                "2026-08-16-p3-boost-math-pilot-foundation-only.md"
            ),
            "reviewed_plan_sha256": "0" * 64,
            "verdict": "PASS",
            "authorized_state": "PILOT_PLAN_FROZEN",
            "claims": "blocked",
        },
        exclusive=True,
    )
    monkeypatch.setattr(pilot, "CANONICAL_FOUNDATION_VERDICT_PATH", verdict)
    with pytest.raises(EvidenceError, match="E_PILOT_PLAN_VERDICT"):
        pilot.write_pilot_plan(markdown, output)


def test_write_plan_cli_has_no_verdict_override():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "write-plan",
                "--markdown",
                "docs/superpowers/plans/"
                "2026-08-16-p3-boost-math-pilot-foundation-only.md",
                "--verdict",
                "docs/review_20260816/forged-verdict.md",
                "--output",
                "data/p3_v3/pilot/boost_math/pilot-plan.json",
            ]
        )


def test_pilot_plan_rejected_as_source_manifest():
    from p3_v3.pilot import validate_pilot_plan

    forged = {
        "schema_version": "p3-pilot-source-manifest-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "archive_sha256": "0" * 64,
        "archive_bytes": 1,
    }
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        validate_pilot_plan(forged)


def test_foundation_cannot_create_source_manifest():
    import p3_v3.pilot as pilot

    assert not hasattr(pilot, "write_source_manifest")
    assert not hasattr(pilot, "validate_pilot_source_manifest")


def test_foundation_cannot_enter_source_or_execution_gate():
    import p3_v3.pilot as pilot

    forbidden = (
        "prepare_source",
        "enter_source_gate",
        "enter_execution_gate",
        "write_execution_plan",
        "write_freeze",
        "write_result",
    )
    for name in forbidden:
        assert not hasattr(pilot, name)


def test_validate_source_cli_accepts_only_archive_and_materialize_root():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    args = parser.parse_args(
        [
            "validate-source",
            "--archive",
            "synthetic.zip",
            "--materialize-root",
            "synthetic-root",
        ]
    )
    assert args.command == "validate-source"
    assert args.archive == "synthetic.zip"
    assert args.materialize_root == "synthetic-root"


def test_write_plan_hashes_the_validated_verdict_snapshot(tmp_path, monkeypatch):
    import p3_v3.pilot as pilot

    markdown = tmp_path / "plan.md"
    output = tmp_path / "pilot-plan.json"
    markdown.write_text("foundation markdown\n", encoding="utf-8")
    verdict = _install_valid_verdict(monkeypatch, tmp_path, markdown)
    validated_verdict_sha256 = _sha256_bytes(verdict.read_bytes())
    original_validate = pilot.validate_foundation_verdict

    def validate_then_replace(value, markdown_plan_sha256):
        result = original_validate(value, markdown_plan_sha256)
        replacement = dict(value)
        replacement["claims"] = "not-blocked"
        verdict.write_bytes(canonical_json_bytes(replacement))
        return result

    monkeypatch.setattr(
        pilot,
        "validate_foundation_verdict",
        validate_then_replace,
    )
    written = pilot.write_pilot_plan(markdown, output)

    assert _sha256_bytes(verdict.read_bytes()) != validated_verdict_sha256
    assert (
        written["sol_high_plan_verdict_sha256"]
        == validated_verdict_sha256
    )


def test_build_preflight_cli_accepts_only_frozen_roots():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    args = parser.parse_args(
        [
            "build-preflight",
            "--source-root",
            "/tmp/p3-boost-math-pilot-production-source",
            "--build-root",
            "/tmp/p3-boost-math-pilot-build-preflight",
        ]
    )
    assert args.command == "build-preflight"
    assert args.source_root == "/tmp/p3-boost-math-pilot-production-source"
    assert args.build_root == "/tmp/p3-boost-math-pilot-build-preflight"


def test_build_preflight_cli_rejects_overrides():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    forbidden = [
        ["build-preflight", "--authorization", "x"],
        ["build-preflight", "--intent", "x"],
        ["build-preflight", "--output", "x"],
        ["build-preflight", "--expected-hash", "x"],
        ["build-preflight", "--timeout", "1"],
        ["build-preflight", "--job-count", "3"],
        ["build-preflight", "--harness", "x"],
        ["build-preflight", "--compiler", "x"],
        ["build-preflight", "--cmake-argv", "x"],
        ["build-preflight", "--mutant", "x"],
        ["build-preflight", "--mr", "x"],
        ["build-preflight", "--execution-plan", "x"],
    ]
    for argv in forbidden:
        try:
            parser.parse_args(argv)
        except SystemExit:
            continue
        raise AssertionError(f"override was accepted: {argv}")
def test_build_preflight_attempt_2_cli_delegates_frozen_arguments(monkeypatch):
    import importlib.util

    spec = importlib.util.spec_from_file_location("pilot_cli_attempt2", "scripts/p3_v3/pilot.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    called = []
    from p3_v3 import pilot_build
    monkeypatch.setattr(pilot_build, "run_build_preflight_attempt_2", lambda *args: called.append(args))
    assert module.main(["build-preflight-attempt-2", "--archive", pilot_build.ATTEMPT2_ARCHIVE_PATH.as_posix(),
        "--source-root", pilot_build.ATTEMPT2_SOURCE_ROOT.as_posix(),
        "--build-root", pilot_build.ATTEMPT2_BUILD_ROOT.as_posix()]) == 0
    assert called == [(pilot_build.ATTEMPT2_ARCHIVE_PATH, pilot_build.ATTEMPT2_SOURCE_ROOT,
                       pilot_build.ATTEMPT2_BUILD_ROOT)]


def test_attempt1_observable_e_pilot_build_preexisting_constant():
    from p3_v3 import pilot_build
    assert pilot_build.INTENT_PATH.name == "build-preflight-intent.json"
    assert pilot_build.RESULT_PATH.name == "build-preflight-result.json"
