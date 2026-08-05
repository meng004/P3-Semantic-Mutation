"""TDD tests for supplemental mining R1 miner (R1-r2 hard-fail)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
MINER = ROOT / "scripts" / "external_slice" / "mine_supplemental_r1.py"

SCOPE = {
    "schema_version": 1,
    "task": "SUPPLEMENTAL_MINING_R1",
    "baseline_commit": "0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a",
    "created_cutoff": "2026-08-01",
    "search_sort": "created",
    "search_order": "desc",
    "max_results_per_phrase": 20,
    "max_reviewed_per_repo": 20,
    "target_pending_per_repo": 5,
    "repositories": [
        {
            "repo": "pymc-devs/pymc",
            "id_prefix": "EXT-pymc-",
            "restriction": "numerical kernels only",
        },
        {
            "repo": "cornellius-gp/gpytorch",
            "id_prefix": "EXT-gpytorch-",
            "restriction": "numerical kernels only",
        },
    ],
    "phrases": ["wrong result", "incorrect value", "numerical regression"],
    "input_sha256": {
        "research/prereg_v2/external_slice_protocol.md": "a" * 64,
    },
    "forbidden_actions": ["A2 build or trigger execution"],
}


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _issue(
    number: int,
    *,
    created_at: str,
    repo: str = "pymc-devs/pymc",
    state: str = "closed",
) -> dict[str, Any]:
    owner, name = repo.split("/")
    return {
        "id": 1000 + number,
        "number": number,
        "state": state,
        "created_at": created_at,
        "updated_at": created_at,
        "closed_at": created_at,
        "html_url": f"https://github.com/{repo}/issues/{number}",
        "title": f"issue {number}",
        "body": f"SECRET_BODY_{number}",
        "repository_url": f"https://api.github.com/repos/{owner}/{name}",
        "pull_request": None,
    }


def _pr(number: int, *, created_at: str, repo: str = "pymc-devs/pymc") -> dict[str, Any]:
    item = _issue(number, created_at=created_at, repo=repo)
    item["html_url"] = f"https://github.com/{repo}/pull/{number}"
    item["pull_request"] = {"url": f"https://api.github.com/repos/{repo}/pulls/{number}"}
    return item


@pytest.fixture()
def scope_path(tmp_path: Path) -> Path:
    path = tmp_path / "SCOPE.json"
    _write_json(path, SCOPE)
    return path


def _import_miner():
    sys.path.insert(0, str(MINER.parent))
    import mine_supplemental_r1 as miner

    return miner


def test_scope_repository_and_phrase_order_preserved(scope_path: Path) -> None:
    miner = _import_miner()
    queries = miner.build_queries(SCOPE)
    assert [q["repo"] for q in queries[:3]] == ["pymc-devs/pymc"] * 3
    assert [q["phrase"] for q in queries[:3]] == [
        "wrong result",
        "incorrect value",
        "numerical regression",
    ]
    assert queries[3]["repo"] == "cornellius-gp/gpytorch"
    assert len(queries) == 6


def test_every_query_contains_required_filters(scope_path: Path) -> None:
    miner = _import_miner()
    for query in miner.build_queries(SCOPE):
        q = query["q"]
        assert "is:issue" in q
        assert "is:closed" in q
        assert "created:<=2026-08-01" in q
        assert f'repo:{query["repo"]}' in q
        assert f'"{query["phrase"]}"' in q


def test_search_uses_per_page_20_and_created_desc(
    scope_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    miner = _import_miner()
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(list(cmd))
        payload = {"total_count": 0, "incomplete_results": False, "items": []}
        return subprocess.CompletedProcess(cmd, 0, json.dumps(payload), "")

    monkeypatch.setattr(miner.subprocess, "run", fake_run)
    miner.cmd_search(
        scope_path,
        tmp_path / "SEARCH_SNAPSHOT.json",
        tmp_path / "REVIEW_QUEUE.json",
        tmp_path / "COMMAND_LOG.json",
    )
    assert calls
    for cmd in calls:
        assert cmd[:4] == ["gh", "api", "-X", "GET"]
        joined = " ".join(cmd)
        assert "search/issues" in joined
        assert "per_page=20" in joined
        assert "sort=created" in joined
        assert "order=desc" in joined


def test_duplicate_issue_urls_collapse_and_queue_order(
    scope_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    miner = _import_miner()
    responses = {
        ("pymc-devs/pymc", "wrong result"): [
            _issue(10, created_at="2026-01-02T00:00:00Z"),
            _issue(9, created_at="2026-01-03T00:00:00Z"),
        ],
        ("pymc-devs/pymc", "incorrect value"): [
            _issue(9, created_at="2026-01-03T00:00:00Z"),
            _issue(8, created_at="2026-01-03T00:00:00Z"),
        ],
        ("pymc-devs/pymc", "numerical regression"): [],
        ("cornellius-gp/gpytorch", "wrong result"): [],
        ("cornellius-gp/gpytorch", "incorrect value"): [],
        ("cornellius-gp/gpytorch", "numerical regression"): [],
    }

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        joined = " ".join(cmd)
        for (repo, phrase), items in responses.items():
            if f"repo:{repo}" in joined and f'"{phrase}"' in joined:
                payload = {
                    "total_count": len(items),
                    "incomplete_results": False,
                    "items": items,
                }
                return subprocess.CompletedProcess(cmd, 0, json.dumps(payload), "")
        raise AssertionError(joined)

    monkeypatch.setattr(miner.subprocess, "run", fake_run)
    queue = tmp_path / "REVIEW_QUEUE.json"
    miner.cmd_search(
        scope_path,
        tmp_path / "SEARCH_SNAPSHOT.json",
        queue,
        tmp_path / "COMMAND_LOG.json",
    )
    pymc = [
        r
        for r in json.loads(queue.read_text(encoding="utf-8"))["records"]
        if r["repo"] == "pymc-devs/pymc"
    ]
    assert [r["issue_number"] for r in pymc] == [9, 8, 10]
    assert [r["neutral_id"] for r in pymc] == ["EXT-pymc-01", "EXT-pymc-02", "EXT-pymc-03"]


def test_hard_fail_on_pr_search_item(
    scope_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    miner = _import_miner()

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        payload = {
            "total_count": 1,
            "incomplete_results": False,
            "items": [_pr(1, created_at="2026-01-01T00:00:00Z")],
        }
        return subprocess.CompletedProcess(cmd, 0, json.dumps(payload), "")

    monkeypatch.setattr(miner.subprocess, "run", fake_run)
    with pytest.raises(miner.SearchHardFail, match="PR returned"):
        miner.cmd_search(
            scope_path,
            tmp_path / "SEARCH_SNAPSHOT.json",
            tmp_path / "REVIEW_QUEUE.json",
            tmp_path / "COMMAND_LOG.json",
        )


def test_hard_fail_on_open_item(
    scope_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    miner = _import_miner()

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        payload = {
            "total_count": 1,
            "incomplete_results": False,
            "items": [_issue(1, created_at="2026-01-01T00:00:00Z", state="open")],
        }
        return subprocess.CompletedProcess(cmd, 0, json.dumps(payload), "")

    monkeypatch.setattr(miner.subprocess, "run", fake_run)
    with pytest.raises(miner.SearchHardFail, match="non-closed"):
        miner.cmd_search(
            scope_path,
            tmp_path / "SEARCH_SNAPSHOT.json",
            tmp_path / "REVIEW_QUEUE.json",
            tmp_path / "COMMAND_LOG.json",
        )


def test_hard_fail_on_incomplete_results(
    scope_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    miner = _import_miner()

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        payload = {"total_count": 0, "incomplete_results": True, "items": []}
        return subprocess.CompletedProcess(cmd, 0, json.dumps(payload), "")

    monkeypatch.setattr(miner.subprocess, "run", fake_run)
    with pytest.raises(miner.SearchHardFail, match="incomplete_results"):
        miner.cmd_search(
            scope_path,
            tmp_path / "SEARCH_SNAPSHOT.json",
            tmp_path / "REVIEW_QUEUE.json",
            tmp_path / "COMMAND_LOG.json",
        )


def test_hard_fail_on_nonzero_github_exit(
    scope_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    miner = _import_miner()

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, 1, "", "boom")

    monkeypatch.setattr(miner.subprocess, "run", fake_run)
    with pytest.raises(miner.SearchHardFail, match="nonzero GitHub request"):
        miner.cmd_search(
            scope_path,
            tmp_path / "SEARCH_SNAPSHOT.json",
            tmp_path / "REVIEW_QUEUE.json",
            tmp_path / "COMMAND_LOG.json",
        )


def test_hard_fail_on_altered_query_options_in_snapshot_validation(
    scope_path: Path, tmp_path: Path
) -> None:
    miner = _import_miner()
    snapshot = {
        "schema_version": 1,
        "scope_sha256": "0" * 64,
        "queries": [
            {
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "q": 'repo:pymc-devs/pymc is:issue is:closed created:<=2026-08-01 "wrong result" extra',
                "incomplete_results": False,
                "pull_count": 0,
                "items": [],
            }
        ],
    }
    # Use validate via direct comparison helper through cmd_validate path with fixtures.
    _write_json(tmp_path / "SEARCH_SNAPSHOT.json", snapshot)
    _write_json(
        tmp_path / "REVIEW_QUEUE.json",
        {
            "schema_version": 1,
            "scope_sha256": miner.sha256_file(scope_path),
            "search_snapshot_sha256": miner.sha256_file(tmp_path / "SEARCH_SNAPSHOT.json"),
            "records": [],
        },
    )
    # Fix scope hash on snapshot for the specific mismatch under test.
    snapshot["scope_sha256"] = miner.sha256_file(scope_path)
    _write_json(tmp_path / "SEARCH_SNAPSHOT.json", snapshot)
    queue = {
        "schema_version": 1,
        "scope_sha256": miner.sha256_file(scope_path),
        "search_snapshot_sha256": miner.sha256_file(tmp_path / "SEARCH_SNAPSHOT.json"),
        "records": [],
    }
    _write_json(tmp_path / "REVIEW_QUEUE.json", queue)
    _write_json(tmp_path / "REVIEW_DECISIONS.json", {"schema_version": 1, "decisions": []})
    _write_json(tmp_path / "existing.csv", {})  # placeholder overwritten below
    import csv

    for name in ("existing.csv", "pilot.csv"):
        with (tmp_path / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "neutral_id",
                    "repo",
                    "issue_url",
                    "buggy_sha",
                    "fixed_sha",
                    "mechanism_sentence",
                    "crit_real_defect",
                    "crit_dual_arm_repro",
                    "crit_in_scope",
                    "decision",
                    "exclusion_reason",
                    "analysis_id",
                ],
            )
            writer.writeheader()
    with pytest.raises(SystemExit):
        miner.cmd_validate_decisions(
            scope_path,
            tmp_path / "SEARCH_SNAPSHOT.json",
            tmp_path / "REVIEW_QUEUE.json",
            tmp_path / "REVIEW_DECISIONS.json",
            tmp_path / "existing.csv",
            tmp_path / "pilot.csv",
        )


def test_review_stop_rules_and_not_reviewed_after_stop() -> None:
    miner = _import_miner()
    records = [
        {
            "neutral_id": f"EXT-pymc-{i:02d}",
            "repo": "pymc-devs/pymc",
            "issue_number": 100 - i,
            "issue_url": f"https://github.com/pymc-devs/pymc/issues/{100 - i}",
            "created_at": f"2026-01-{i:02d}T00:00:00Z",
        }
        for i in range(1, 9)
    ]
    decisions = [
        {"neutral_id": f"EXT-pymc-{i:02d}", "decision": "ADMIT_PENDING_REPRO"}
        for i in range(1, 6)
    ]
    annotated = miner.apply_review_stop(
        records, decisions, max_reviewed=20, target_pending=5
    )
    reviewed = [r for r in annotated if r["review_status"] == "REVIEWED"]
    stopped = [r for r in annotated if r["review_status"] == "NOT_REVIEWED_AFTER_STOP"]
    assert len(reviewed) == 5
    assert len(stopped) == 3


def test_raw_auth_and_bodies_never_persisted(
    scope_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    miner = _import_miner()

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        item = _issue(1, created_at="2026-01-01T00:00:00Z")
        item["body"] = "TOKEN ghp_abcdefghijklmnopqrstuvwxyz0123456789"
        payload = {"total_count": 1, "incomplete_results": False, "items": [item]}
        return subprocess.CompletedProcess(
            cmd,
            0,
            json.dumps(payload),
            "Authorization: Bearer ghp_abcdefghijklmnopqrstuvwxyz0123456789",
        )

    monkeypatch.setattr(miner.subprocess, "run", fake_run)
    snapshot = tmp_path / "SEARCH_SNAPSHOT.json"
    queue = tmp_path / "REVIEW_QUEUE.json"
    command_log = tmp_path / "COMMAND_LOG.json"
    miner.cmd_search(scope_path, snapshot, queue, command_log)
    for path in (snapshot, queue, command_log):
        text = path.read_text(encoding="utf-8")
        assert "SECRET_BODY" not in text
        assert "ghp_" not in text
        assert "Bearer " not in text
        assert "Authorization" not in text
