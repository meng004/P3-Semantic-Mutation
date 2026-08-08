from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.preflight import normalize_repository_identity, run_preflight


def _run(root: Path, *argv: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *argv],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


@pytest.fixture
def git_repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "Fixture")
    _run(root, "config", "user.email", "fixture@example.invalid")
    _run(root, "remote", "add", "origin", "git@github.com:Example/Repo.git")
    lock = root / "requirements.lock"
    lock.write_text("dependency==1\n", encoding="utf-8")
    input_path = root / "input.json"
    input_path.write_text("{}\n", encoding="utf-8")
    _run(root, "add", "requirements.lock", "input.json")
    _run(root, "commit", "-m", "fixture")
    return root


def _spec(root: Path, smoke=None):
    return {
        "schema_version": "p3-preflight-v1",
        "repository_identity": "Example/Repo",
        "expected_commit": _run(root, "rev-parse", "HEAD"),
        "dependency_lock_path": "requirements.lock",
        "dependency_lock_sha256": hashlib.sha256(
            (root / "requirements.lock").read_bytes()
        ).hexdigest(),
        "phase_inputs": [
            {
                "path": "input.json",
                "sha256": hashlib.sha256((root / "input.json").read_bytes()).hexdigest(),
            }
        ],
        "smoke_commands": smoke or [["python3", "-c", "print(1)"]],
        "timeout_seconds": 10,
    }


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://github.com/Example/Repo.git", "Example/Repo"),
        ("https://github.com/Example/RepoXgit", "Example/RepoXgit"),
        ("git@github.com:Example/Repo.git", "Example/Repo"),
        ("ssh://git@github.com/Example/Repo.git", "Example/Repo"),
    ],
)
def test_repository_identity_normalizes_transport_spelling(raw, expected):
    assert normalize_repository_identity(raw) == expected


def test_preflight_passes_without_creating_scientific_intent(git_repo):
    result = run_preflight(git_repo, _spec(git_repo))
    assert result["status"] == "PASS"
    assert result["repository_identity"] == "Example/Repo"
    assert result["smoke"][0]["exit_code"] == 0
    assert not list(git_repo.glob("**/intent.json"))


def test_preflight_failure_is_repeatable_and_not_scientific(git_repo):
    spec = _spec(git_repo, smoke=[["python3", "-c", "raise SystemExit(7)"]])
    first = run_preflight(git_repo, spec)
    second = run_preflight(git_repo, spec)
    assert first["status"] == second["status"] == "FAIL"
    assert first["failure_code"] == second["failure_code"] == "E_PREFLIGHT_SMOKE"
    assert not list(git_repo.glob("**/intent.json"))


def test_preflight_rejects_wrong_commit_before_smoke(git_repo):
    spec = {**_spec(git_repo), "expected_commit": "0" * 40}
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_COMMIT"):
        run_preflight(git_repo, spec)
