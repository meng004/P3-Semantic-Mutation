"""TDD tests for supplemental mining R1 admission checker (R1-r3 full binding)."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "external_slice" / "check_supplemental_r1_admission.py"
MINER = ROOT / "scripts" / "external_slice" / "mine_supplemental_r1.py"


def _load_miner():
    spec = importlib.util.spec_from_file_location("mine_supplemental_r1", MINER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_checker_mod():
    spec = importlib.util.spec_from_file_location("check_supplemental_r1_admission", CHECKER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
HEADER = [
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
]
FULL_A = "a" * 40
FULL_B = "b" * 40


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_sheet(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scope() -> dict[str, Any]:
    return {
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
            }
        ],
        "phrases": ["wrong result"],
        "input_sha256": {},
        "forbidden_actions": ["A2 build or trigger execution"],
    }


def _row(
    *,
    neutral_id: str = "EXT-pymc-01",
    repo: str = "pymc-devs/pymc",
    issue: int = 1,
    decision: str = "ADMIT_PENDING_REPRO",
    a1: str = "PASS",
    a2: str = "PENDING",
    a3: str = "PASS",
    buggy: str = FULL_A,
    fixed: str = FULL_B,
    exclusion: str = "",
    analysis_id: str = "",
    mechanism: str = "restores the returned density normalisation constant.",
) -> dict[str, str]:
    return {
        "neutral_id": neutral_id,
        "repo": repo.split("/")[-1],
        "issue_url": f"https://github.com/{repo}/issues/{issue}",
        "buggy_sha": buggy,
        "fixed_sha": fixed,
        "mechanism_sentence": mechanism,
        "crit_real_defect": a1,
        "crit_dual_arm_repro": a2,
        "crit_in_scope": a3,
        "decision": decision,
        "exclusion_reason": exclusion,
        "analysis_id": analysis_id,
    }


def _decision_from_row(row: dict[str, str], order: int = 1, repo: str = "pymc-devs/pymc") -> dict[str, Any]:
    return {
        "neutral_id": row["neutral_id"],
        "repo": repo,
        "issue_number": int(row["issue_url"].rsplit("/", 1)[-1]),
        "issue_url": row["issue_url"],
        "fix_url": f"https://github.com/{repo}/commit/{row['fixed_sha']}"
        if row["fixed_sha"]
        else "",
        "buggy_sha": row["buggy_sha"],
        "fixed_sha": row["fixed_sha"],
        "mechanism_sentence": row["mechanism_sentence"],
        "crit_real_defect": row["crit_real_defect"],
        "crit_dual_arm_repro": row["crit_dual_arm_repro"],
        "crit_in_scope": row["crit_in_scope"],
        "decision": row["decision"],
        "exclusion_reason": row["exclusion_reason"],
        "analysis_id": row["analysis_id"],
        "rationales": {
            "real_defect": "A public defect report and an identifiable public fix commit are linked.",
            "dual_arm_repro": "No same-trigger dual-arm result is claimed in this task.",
            "in_scope": "The changed callable maps float-vector input to a float numerical output.",
        },
        "evidence_urls": [
            row["issue_url"],
            f"https://github.com/{repo}/commit/{row['fixed_sha']}"
            if row["fixed_sha"]
            else row["issue_url"],
        ],
        "review_order": order,
        "review_status": "REVIEWED",
    }


def _write_evidence(
    root: Path,
    row: dict[str, str],
    *,
    scope_sha: str,
    search_sha: str,
    decisions_sha: str,
    decision: dict[str, Any] | None = None,
) -> None:
    case_dir = root / row["neutral_id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    if decision is None:
        decision = _decision_from_row(row)
    payload = {
        "neutral_id": row["neutral_id"],
        "source_pool": "supplemental_mining_r1",
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": search_sha,
        "review_decisions_sha256": decisions_sha,
        "issue_url": row["issue_url"],
        "fix_url": decision.get("fix_url") or "",
        "buggy_sha": row["buggy_sha"],
        "fixed_sha": row["fixed_sha"],
        "criteria": {
            "real_defect": row["crit_real_defect"],
            "dual_arm_repro": row["crit_dual_arm_repro"],
            "in_scope": row["crit_in_scope"],
        },
        "rationales": decision["rationales"],
        "evidence_urls": decision["evidence_urls"],
        "mechanism_sentence": row["mechanism_sentence"],
    }
    (case_dir / "evidence.json").write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _queue_from_snapshot(scope: dict[str, Any], snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    miner = _load_miner()
    hits_by_repo = {r["repo"]: [] for r in scope["repositories"]}
    for query in snapshot.get("queries") or []:
        for item in query.get("items") or []:
            cloned = dict(item)
            cloned["phrase"] = query["phrase"]
            cloned["repo"] = query["repo"]
            hits_by_repo[query["repo"]].append(cloned)
    return miner.assign_queue(scope, hits_by_repo)


def _valid_fixture(tmp_path: Path) -> dict[str, Path]:
    base = tmp_path / "data" / "external_slice" / "supplemental_r1"
    scope_path = base / "SCOPE.json"
    snapshot_path = base / "SEARCH_SNAPSHOT.json"
    queue_path = base / "REVIEW_QUEUE.json"
    decisions_path = base / "REVIEW_DECISIONS.json"
    sheet_path = base / "admission_sheet.cursor_candidate.csv"
    evidence_root = base / "admission_evidence"
    existing = tmp_path / "existing.csv"
    pilot = tmp_path / "pilot.csv"

    protocol = tmp_path / "research" / "prereg_v2" / "external_slice_protocol.md"
    protocol.parent.mkdir(parents=True, exist_ok=True)
    protocol.write_bytes(b"protocol-fixture\n")
    scope = _scope()
    scope["input_sha256"] = {
        str(protocol.relative_to(tmp_path)): _sha256_file(protocol),
    }
    _write_json(scope_path, scope)
    scope_sha = _sha256_file(scope_path)
    q = 'repo:pymc-devs/pymc is:issue is:closed created:<=2026-08-01 "wrong result"'
    row = _row()
    snapshot = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "queries": [
            {
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "q": q,
                "total_count": 1,
                "incomplete_results": False,
                "returned": 1,
                "issue_count": 1,
                "pull_count": 0,
                "items": [
                    {
                        "repo": "pymc-devs/pymc",
                        "phrase": "wrong result",
                        "issue_number": 1,
                        "issue_url": row["issue_url"],
                        "state": "closed",
                        "created_at": "2026-01-01T00:00:00Z",
                    }
                ],
            }
        ],
    }
    _write_json(snapshot_path, snapshot)
    search_sha = _sha256_file(snapshot_path)
    queue = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": search_sha,
        "records": _queue_from_snapshot(scope, snapshot),
    }
    _write_json(queue_path, queue)
    decision = _decision_from_row(row)
    decisions = {"schema_version": 1, "decisions": [decision]}
    _write_json(decisions_path, decisions)
    _write_sheet(sheet_path, [row])
    decisions_sha = _sha256_file(decisions_path)
    _write_evidence(
        evidence_root,
        row,
        scope_sha=scope_sha,
        search_sha=search_sha,
        decisions_sha=decisions_sha,
        decision=decision,
    )
    _write_sheet(existing, [_row(neutral_id="EXT-fftw-01", repo="FFTW/fftw3", issue=20)])
    _write_sheet(pilot, [_row(neutral_id="EXT-numpy-01", repo="numpy/numpy", issue=1)])
    return {
        "scope": scope_path,
        "snapshot": snapshot_path,
        "queue": queue_path,
        "decisions": decisions_path,
        "sheet": sheet_path,
        "evidence_root": evidence_root,
        "existing": existing,
        "pilot": pilot,
        "fixture_root": tmp_path,
    }


def _run(paths: dict[str, Path]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--scope",
            str(paths["scope"]),
            "--snapshot",
            str(paths["snapshot"]),
            "--queue",
            str(paths["queue"]),
            "--decisions",
            str(paths["decisions"]),
            "--sheet",
            str(paths["sheet"]),
            "--evidence-root",
            str(paths["evidence_root"]),
            "--existing-sheet",
            str(paths["existing"]),
            "--pilot-sheet",
            str(paths["pilot"]),
            "--fixture-root",
            str(paths["fixture_root"]),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_accepts_valid_pending_row(tmp_path: Path) -> None:
    result = _run(_valid_fixture(tmp_path))
    assert result.returncode == 0, result.stderr


def test_rejects_repo_outside_scope(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    row = _row(repo="numpy/numpy", issue=99)
    _write_sheet(paths["sheet"], [row])
    decisions = {"schema_version": 1, "decisions": [_decision_from_row(row, repo="numpy/numpy")]}
    _write_json(paths["decisions"], decisions)
    result = _run(paths)
    assert result.returncode != 0


def test_rejects_decision_queue_url_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    payload = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    payload["decisions"][0]["issue_url"] = "https://github.com/pymc-devs/pymc/issues/999"
    _write_json(paths["decisions"], payload)
    # Keep sheet matching old URL so sheet/decision set still 1:1 by id, but URL mismatches queue.
    result = _run(paths)
    assert result.returncode != 0
    assert "issue_url mismatch" in result.stderr


def test_rejects_decision_queue_repo_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    payload = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    payload["decisions"][0]["repo"] = "jax-ml/jax"
    _write_json(paths["decisions"], payload)
    result = _run(paths)
    assert result.returncode != 0
    assert (
        "repository mismatch" in result.stderr
        or "outside SCOPE" in result.stderr
        or "queue-head" in result.stderr
    )


def test_rejects_decision_issue_number_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    payload = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    payload["decisions"][0]["issue_number"] = 999
    _write_json(paths["decisions"], payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "issue_number mismatch" in result.stderr


def _set_snapshot_items(
    paths: dict[str, Path],
    items: list[dict[str, Any]],
    *,
    scope: dict[str, Any] | None = None,
) -> tuple[str, str]:
    if scope is None:
        scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    scope_sha = _sha256_file(paths["scope"])
    snapshot = json.loads(paths["snapshot"].read_text(encoding="utf-8"))
    snapshot["scope_sha256"] = scope_sha
    snapshot["queries"][0]["items"] = items
    snapshot["queries"][0]["returned"] = len(items)
    snapshot["queries"][0]["issue_count"] = len(items)
    snapshot["queries"][0]["total_count"] = len(items)
    snapshot["queries"][0]["pull_count"] = 0
    _write_json(paths["snapshot"], snapshot)
    search_sha = _sha256_file(paths["snapshot"])
    queue = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": search_sha,
        "records": _queue_from_snapshot(scope, snapshot),
    }
    _write_json(paths["queue"], queue)
    return scope_sha, search_sha


def test_rejects_swapped_review_order(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    row1 = _row(neutral_id="EXT-pymc-01", issue=1)
    row2 = _row(neutral_id="EXT-pymc-02", issue=2, buggy="c" * 40, fixed="d" * 40)
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    scope_sha, search_sha = _set_snapshot_items(
        paths,
        [
            {
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "issue_number": 1,
                "issue_url": row1["issue_url"],
                "state": "closed",
                "created_at": "2026-01-02T00:00:00Z",
            },
            {
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "issue_number": 2,
                "issue_url": row2["issue_url"],
                "state": "closed",
                "created_at": "2026-01-01T00:00:00Z",
            },
        ],
        scope=scope,
    )
    # Queue order is created_at desc: issue 1 then issue 2. Swap decision orders.
    decisions = {
        "schema_version": 1,
        "decisions": [
            _decision_from_row(row2, order=1),
            _decision_from_row(row1, order=2),
        ],
    }
    _write_json(paths["decisions"], decisions)
    _write_sheet(paths["sheet"], [row2, row1])
    decisions_sha = _sha256_file(paths["decisions"])
    for row, decision in zip((row1, row2), decisions["decisions"]):
        _write_evidence(
            paths["evidence_root"],
            row,
            scope_sha=scope_sha,
            search_sha=search_sha,
            decisions_sha=decisions_sha,
            decision=decision,
        )
    result = _run(paths)
    assert result.returncode != 0
    assert "queue-head" in result.stderr or "review_order" in result.stderr


def test_rejects_skipped_queue_head(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    row1 = _row(neutral_id="EXT-pymc-01", issue=1)
    row2 = _row(neutral_id="EXT-pymc-02", issue=2, buggy="c" * 40, fixed="d" * 40)
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    scope_sha, search_sha = _set_snapshot_items(
        paths,
        [
            {
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "issue_number": 1,
                "issue_url": row1["issue_url"],
                "state": "closed",
                "created_at": "2026-01-02T00:00:00Z",
            },
            {
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "issue_number": 2,
                "issue_url": row2["issue_url"],
                "state": "closed",
                "created_at": "2026-01-01T00:00:00Z",
            },
        ],
        scope=scope,
    )
    decision = _decision_from_row(row2, order=1)
    decisions = {"schema_version": 1, "decisions": [decision]}
    _write_json(paths["decisions"], decisions)
    _write_sheet(paths["sheet"], [row2])
    decisions_sha = _sha256_file(paths["decisions"])
    _write_evidence(
        paths["evidence_root"],
        row2,
        scope_sha=scope_sha,
        search_sha=search_sha,
        decisions_sha=decisions_sha,
        decision=decision,
    )
    result = _run(paths)
    assert result.returncode != 0
    assert "queue-head" in result.stderr


def test_rejects_decisions_beyond_stop_boundary(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    rows = [
        _row(
            neutral_id=f"EXT-pymc-{i:02d}",
            issue=i,
            buggy=f"{i:040d}",
            fixed=f"{i + 100:040d}",
        )
        for i in range(1, 7)
    ]
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    scope["target_pending_per_repo"] = 2
    _write_json(paths["scope"], scope)
    # Newer created_at first so queue order matches EXT-pymc-01..06 by issue number desc...
    # Use descending created_at aligned to issue numbers so IDs map issue i -> EXT-pymc-(7-i) unless
    # we set created_at so issue 1 is newest. Keep issue i created_at day i with reverse sort:
    # issue 6 newest -> EXT-pymc-01. Simpler: one item order by created_at desc = rows order.
    items = []
    for i, row in enumerate(rows, start=1):
        items.append(
            {
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "issue_number": i,
                "issue_url": row["issue_url"],
                "state": "closed",
                "created_at": f"2026-01-{22 - i:02d}T00:00:00Z",
            }
        )
    scope_sha, search_sha = _set_snapshot_items(paths, items, scope=scope)
    queue_records = json.loads(paths["queue"].read_text(encoding="utf-8"))["records"]
    # Rebuild rows to match allocated neutral_ids / issue numbers.
    rows_by_issue = {int(r["issue_url"].rsplit("/", 1)[-1]): r for r in rows}
    ordered_rows = []
    for rec in queue_records:
        src = rows_by_issue[int(rec["issue_number"])]
        ordered_rows.append(
            _row(
                neutral_id=rec["neutral_id"],
                issue=int(rec["issue_number"]),
                buggy=src["buggy_sha"],
                fixed=src["fixed_sha"],
            )
        )
    # 3 pending admits exceeds stop after 2 pending.
    decisions_list = [
        _decision_from_row(row, order=i) for i, row in enumerate(ordered_rows[:3], 1)
    ]
    decisions = {"schema_version": 1, "decisions": decisions_list}
    _write_json(paths["decisions"], decisions)
    _write_sheet(paths["sheet"], ordered_rows[:3])
    decisions_sha = _sha256_file(paths["decisions"])
    for row, decision in zip(ordered_rows[:3], decisions_list):
        _write_evidence(
            paths["evidence_root"],
            row,
            scope_sha=scope_sha,
            search_sha=search_sha,
            decisions_sha=decisions_sha,
            decision=decision,
        )
    result = _run(paths)
    assert result.returncode != 0
    assert "queue-head" in result.stderr or "pending" in result.stderr.lower()


def test_rejects_a2_not_pending(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    row = _row(a2="PASS")
    decision = _decision_from_row(row)
    _write_sheet(paths["sheet"], [row])
    _write_json(paths["decisions"], {"schema_version": 1, "decisions": [decision]})
    _write_evidence(
        paths["evidence_root"],
        row,
        scope_sha=_sha256_file(paths["scope"]),
        search_sha=_sha256_file(paths["snapshot"]),
        decisions_sha=_sha256_file(paths["decisions"]),
        decision=decision,
    )
    result = _run(paths)
    assert result.returncode != 0
    assert "PENDING" in result.stderr


def test_rejects_missing_evidence_record(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    (paths["evidence_root"] / "EXT-pymc-01" / "evidence.json").unlink()
    result = _run(paths)
    assert result.returncode != 0
    assert "evidence" in result.stderr.lower()


def test_rejects_changed_input_hash(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    key = next(iter(scope["input_sha256"]))
    scope["input_sha256"][key] = "d" * 64
    _write_json(paths["scope"], scope)
    result = _run(paths)
    assert result.returncode != 0


def test_rejects_snapshot_queue_membership_escape(tmp_path: Path) -> None:
    """R3 escape #1: queue/decision/sheet/evidence consistently use issue 999 while
    snapshot retains issue 1. Must fail (previously exited 0)."""
    paths = _valid_fixture(tmp_path)
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    scope_sha = _sha256_file(paths["scope"])
    search_sha = _sha256_file(paths["snapshot"])
    row = _row(issue=999)
    queue = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": search_sha,
        "records": [
            {
                "neutral_id": "EXT-pymc-01",
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "issue_number": 999,
                "issue_url": row["issue_url"],
                "state": "closed",
                "created_at": "2026-01-01T00:00:00Z",
                "phrases": ["wrong result"],
                "id_prefix": "EXT-pymc-",
                "review_status": "PENDING_REVIEW",
            }
        ],
    }
    _write_json(paths["queue"], queue)
    decision = _decision_from_row(row)
    _write_json(paths["decisions"], {"schema_version": 1, "decisions": [decision]})
    _write_sheet(paths["sheet"], [row])
    decisions_sha = _sha256_file(paths["decisions"])
    _write_evidence(
        paths["evidence_root"],
        row,
        scope_sha=scope_sha,
        search_sha=search_sha,
        decisions_sha=decisions_sha,
        decision=decision,
    )
    result = _run(paths)
    assert result.returncode != 0, result.stdout
    assert "queue" in result.stderr.lower() and (
        "snapshot" in result.stderr.lower() or "equality" in result.stderr.lower()
        or "mismatch" in result.stderr.lower()
    )


def test_rejects_sheet_fixed_sha_divergence_escape(tmp_path: Path) -> None:
    """R3 escape #2: only sheet fixed_sha changes; decision/evidence keep original.
    Must fail (previously exited 0)."""
    paths = _valid_fixture(tmp_path)
    rows = list(csv.DictReader(paths["sheet"].open(encoding="utf-8")))
    rows[0]["fixed_sha"] = "c" * 40
    _write_sheet(paths["sheet"], rows)
    result = _run(paths)
    assert result.returncode != 0, result.stdout
    assert "fixed_sha" in result.stderr


def test_rejects_missing_snapshot_query(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    scope["phrases"] = ["wrong result", "incorrect value"]
    _write_json(paths["scope"], scope)
    scope_sha = _sha256_file(paths["scope"])
    # Snapshot still has only one query → missing query.
    snapshot = json.loads(paths["snapshot"].read_text(encoding="utf-8"))
    snapshot["scope_sha256"] = scope_sha
    _write_json(paths["snapshot"], snapshot)
    search_sha = _sha256_file(paths["snapshot"])
    queue = json.loads(paths["queue"].read_text(encoding="utf-8"))
    queue["scope_sha256"] = scope_sha
    queue["search_snapshot_sha256"] = search_sha
    _write_json(paths["queue"], queue)
    result = _run(paths)
    assert result.returncode != 0
    assert "query" in result.stderr.lower()


def test_rejects_duplicate_snapshot_query(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    snapshot = json.loads(paths["snapshot"].read_text(encoding="utf-8"))
    snapshot["queries"].append(dict(snapshot["queries"][0]))
    _write_json(paths["snapshot"], snapshot)
    search_sha = _sha256_file(paths["snapshot"])
    queue = json.loads(paths["queue"].read_text(encoding="utf-8"))
    queue["search_snapshot_sha256"] = search_sha
    _write_json(paths["queue"], queue)
    result = _run(paths)
    assert result.returncode != 0
    assert "query" in result.stderr.lower()


def test_rejects_queue_vs_snapshot_order_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    row1 = _row(neutral_id="EXT-pymc-01", issue=1)
    row2 = _row(neutral_id="EXT-pymc-02", issue=2, buggy="c" * 40, fixed="d" * 40)
    scope_sha, search_sha = _set_snapshot_items(
        paths,
        [
            {
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "issue_number": 1,
                "issue_url": row1["issue_url"],
                "state": "closed",
                "created_at": "2026-01-02T00:00:00Z",
            },
            {
                "repo": "pymc-devs/pymc",
                "phrase": "wrong result",
                "issue_number": 2,
                "issue_url": row2["issue_url"],
                "state": "closed",
                "created_at": "2026-01-01T00:00:00Z",
            },
        ],
        scope=scope,
    )
    queue = json.loads(paths["queue"].read_text(encoding="utf-8"))
    # Swap record order without changing IDs/contents correctly — reverse list.
    queue["records"] = list(reversed(queue["records"]))
    _write_json(paths["queue"], queue)
    # Keep only first reviewed id after reverse so decision set is smaller; just check
    # queue equality fails even before decisions.
    decision = _decision_from_row(
        _row(
            neutral_id=queue["records"][0]["neutral_id"],
            issue=int(queue["records"][0]["issue_number"]),
            buggy="c" * 40 if int(queue["records"][0]["issue_number"]) == 2 else FULL_A,
            fixed="d" * 40 if int(queue["records"][0]["issue_number"]) == 2 else FULL_B,
        )
    )
    _write_json(paths["decisions"], {"schema_version": 1, "decisions": [decision]})
    row = _row(
        neutral_id=decision["neutral_id"],
        issue=decision["issue_number"],
        buggy=decision["buggy_sha"],
        fixed=decision["fixed_sha"],
    )
    _write_sheet(paths["sheet"], [row])
    decisions_sha = _sha256_file(paths["decisions"])
    _write_evidence(
        paths["evidence_root"],
        row,
        scope_sha=scope_sha,
        search_sha=search_sha,
        decisions_sha=decisions_sha,
        decision=decision,
    )
    result = _run(paths)
    assert result.returncode != 0
    assert "queue" in result.stderr.lower()


def test_rejects_decision_sheet_mechanism_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    payload = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    payload["decisions"][0]["mechanism_sentence"] = "different mechanism sentence."
    _write_json(paths["decisions"], payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "mechanism" in result.stderr.lower()


def test_rejects_decision_evidence_rationale_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    evidence_path = paths["evidence_root"] / "EXT-pymc-01" / "evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["rationales"]["real_defect"] = "tampered rationale"
    _write_json(evidence_path, payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "rationale" in result.stderr.lower()


def test_rejects_decision_evidence_fix_url_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    evidence_path = paths["evidence_root"] / "EXT-pymc-01" / "evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["fix_url"] = f"https://github.com/pymc-devs/pymc/commit/{'e' * 40}"
    _write_json(evidence_path, payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "fix_url" in result.stderr


def test_rejects_sheet_decision_exclusion_reason_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    row = _row(decision="EXCLUDED", a1="FAIL", a3="FAIL", buggy="", fixed="", exclusion="no fix")
    decision = _decision_from_row(row)
    decision["fix_url"] = ""
    decision["evidence_urls"] = [row["issue_url"]]
    decision["rationales"] = {
        "real_defect": "No identifiable public fix commit is linked.",
        "dual_arm_repro": "No same-trigger dual-arm result is claimed in this task.",
        "in_scope": "Scope not established for an excluded row.",
    }
    _write_json(paths["decisions"], {"schema_version": 1, "decisions": [decision]})
    bad = dict(row)
    bad["exclusion_reason"] = "different exclusion"
    _write_sheet(paths["sheet"], [bad])
    scope_sha = _sha256_file(paths["scope"])
    search_sha = _sha256_file(paths["snapshot"])
    decisions_sha = _sha256_file(paths["decisions"])
    _write_evidence(
        paths["evidence_root"],
        row,
        scope_sha=scope_sha,
        search_sha=search_sha,
        decisions_sha=decisions_sha,
        decision=decision,
    )
    result = _run(paths)
    assert result.returncode != 0
    assert "exclusion" in result.stderr.lower()


def test_rejects_sheet_decision_analysis_id_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    payload = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    # analysis_id must stay blank for admission, but field equality should catch drift first.
    rows = list(csv.DictReader(paths["sheet"].open(encoding="utf-8")))
    rows[0]["analysis_id"] = "ALIAS-1"
    _write_sheet(paths["sheet"], rows)
    # Keep decision blank → mismatch (also violates blank rule).
    result = _run(paths)
    assert result.returncode != 0
    assert "analysis_id" in result.stderr


def test_checker_queue_reconstruction_matches_miner_assign_queue(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    snapshot = json.loads(paths["snapshot"].read_text(encoding="utf-8"))
    checker = _load_checker_mod()
    miner = _load_miner()
    expected = checker.reconstruct_queue_records(scope, snapshot)
    hits_by_repo = {r["repo"]: [] for r in scope["repositories"]}
    for query in snapshot["queries"]:
        for item in query["items"]:
            cloned = dict(item)
            # Derive exclusively from enclosing query (R4 binding).
            cloned["phrase"] = query["phrase"]
            cloned["repo"] = query["repo"]
            hits_by_repo[query["repo"]].append(cloned)
    assert expected == miner.assign_queue(scope, hits_by_repo)


def test_rejects_tampered_item_phrase_provenance_escape(tmp_path: Path) -> None:
    """R4 escape: item.phrase='tampered phrase' while enclosing query stays frozen.
    Previously exited 0 after queue rebuild; must hard-fail."""
    paths = _valid_fixture(tmp_path)
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    snapshot = json.loads(paths["snapshot"].read_text(encoding="utf-8"))
    snapshot["queries"][0]["items"][0]["phrase"] = "tampered phrase"
    _write_json(paths["snapshot"], snapshot)
    search_sha = _sha256_file(paths["snapshot"])
    scope_sha = _sha256_file(paths["scope"])
    # Rebuild queue preserving the tampered item phrase (the R3 helper escape path).
    miner = _load_miner()
    hits_by_repo = {r["repo"]: [] for r in scope["repositories"]}
    for query in snapshot["queries"]:
        for item in query.get("items") or []:
            cloned = dict(item)
            cloned.setdefault("phrase", query["phrase"])
            cloned.setdefault("repo", query["repo"])
            hits_by_repo[query["repo"]].append(cloned)
    queue = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": search_sha,
        "records": miner.assign_queue(scope, hits_by_repo),
    }
    _write_json(paths["queue"], queue)
    decisions = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    decisions_sha = _sha256_file(paths["decisions"])
    row = list(csv.DictReader(paths["sheet"].open(encoding="utf-8")))[0]
    _write_evidence(
        paths["evidence_root"],
        row,
        scope_sha=scope_sha,
        search_sha=search_sha,
        decisions_sha=decisions_sha,
        decision=decisions["decisions"][0],
    )
    result = _run(paths)
    assert result.returncode != 0, result.stdout
    assert "phrase" in result.stderr.lower()


def test_rejects_tampered_item_repo_vs_enclosing_query(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    snapshot = json.loads(paths["snapshot"].read_text(encoding="utf-8"))
    snapshot["queries"][0]["items"][0]["repo"] = "numpy/numpy"
    _write_json(paths["snapshot"], snapshot)
    search_sha = _sha256_file(paths["snapshot"])
    scope_sha = _sha256_file(paths["scope"])
    scope = json.loads(paths["scope"].read_text(encoding="utf-8"))
    miner = _load_miner()
    hits_by_repo = {r["repo"]: [] for r in scope["repositories"]}
    # Place the item under the query repo bucket while keeping tampered item.repo.
    for query in snapshot["queries"]:
        for item in query.get("items") or []:
            cloned = dict(item)
            cloned.setdefault("phrase", query["phrase"])
            hits_by_repo[query["repo"]].append(cloned)
    queue = {
        "schema_version": 1,
        "scope_sha256": scope_sha,
        "search_snapshot_sha256": search_sha,
        "records": miner.assign_queue(scope, hits_by_repo),
    }
    _write_json(paths["queue"], queue)
    decisions = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    row = list(csv.DictReader(paths["sheet"].open(encoding="utf-8")))[0]
    _write_evidence(
        paths["evidence_root"],
        row,
        scope_sha=scope_sha,
        search_sha=search_sha,
        decisions_sha=_sha256_file(paths["decisions"]),
        decision=decisions["decisions"][0],
    )
    result = _run(paths)
    assert result.returncode != 0, result.stdout
    assert "repo" in result.stderr.lower()


def test_rejects_evidence_neutral_id_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    evidence_path = paths["evidence_root"] / "EXT-pymc-01" / "evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["neutral_id"] = "EXT-pymc-99"
    _write_json(evidence_path, payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "neutral_id" in result.stderr


def test_rejects_evidence_issue_url_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    evidence_path = paths["evidence_root"] / "EXT-pymc-01" / "evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["issue_url"] = "https://github.com/pymc-devs/pymc/issues/999"
    _write_json(evidence_path, payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "issue_url" in result.stderr


def test_rejects_sheet_repository_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    rows = list(csv.DictReader(paths["sheet"].open(encoding="utf-8")))
    rows[0]["repo"] = "numpy"
    _write_sheet(paths["sheet"], rows)
    result = _run(paths)
    assert result.returncode != 0
    assert "repository" in result.stderr.lower() or "repo" in result.stderr.lower()


def test_rejects_sheet_decision_buggy_sha_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    rows = list(csv.DictReader(paths["sheet"].open(encoding="utf-8")))
    rows[0]["buggy_sha"] = "c" * 40
    _write_sheet(paths["sheet"], rows)
    result = _run(paths)
    assert result.returncode != 0
    assert "buggy_sha" in result.stderr


def test_rejects_sheet_decision_verdict_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    rows = list(csv.DictReader(paths["sheet"].open(encoding="utf-8")))
    rows[0]["decision"] = "EXCLUDED"
    rows[0]["exclusion_reason"] = "sheet-only exclusion"
    rows[0]["crit_real_defect"] = "FAIL"
    rows[0]["crit_in_scope"] = "FAIL"
    rows[0]["buggy_sha"] = ""
    rows[0]["fixed_sha"] = ""
    _write_sheet(paths["sheet"], rows)
    result = _run(paths)
    assert result.returncode != 0
    assert "decision" in result.stderr.lower()


def test_rejects_sheet_decision_crit_real_defect_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    rows = list(csv.DictReader(paths["sheet"].open(encoding="utf-8")))
    rows[0]["crit_real_defect"] = "FAIL"
    _write_sheet(paths["sheet"], rows)
    result = _run(paths)
    assert result.returncode != 0
    assert "crit_real_defect" in result.stderr


def test_rejects_sheet_decision_crit_dual_arm_repro_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    rows = list(csv.DictReader(paths["sheet"].open(encoding="utf-8")))
    rows[0]["crit_dual_arm_repro"] = "FAIL"
    _write_sheet(paths["sheet"], rows)
    result = _run(paths)
    assert result.returncode != 0
    assert "crit_dual_arm_repro" in result.stderr


def test_rejects_sheet_decision_crit_in_scope_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    rows = list(csv.DictReader(paths["sheet"].open(encoding="utf-8")))
    rows[0]["crit_in_scope"] = "FAIL"
    _write_sheet(paths["sheet"], rows)
    result = _run(paths)
    assert result.returncode != 0
    assert "crit_in_scope" in result.stderr


def test_rejects_evidence_mechanism_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    evidence_path = paths["evidence_root"] / "EXT-pymc-01" / "evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["mechanism_sentence"] = "tampered evidence mechanism."
    _write_json(evidence_path, payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "mechanism" in result.stderr.lower()


def test_rejects_evidence_buggy_sha_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    evidence_path = paths["evidence_root"] / "EXT-pymc-01" / "evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["buggy_sha"] = "c" * 40
    _write_json(evidence_path, payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "buggy_sha" in result.stderr


def test_rejects_evidence_fixed_sha_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    evidence_path = paths["evidence_root"] / "EXT-pymc-01" / "evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["fixed_sha"] = "c" * 40
    _write_json(evidence_path, payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "fixed_sha" in result.stderr


def test_rejects_decision_evidence_urls_mismatch(tmp_path: Path) -> None:
    paths = _valid_fixture(tmp_path)
    evidence_path = paths["evidence_root"] / "EXT-pymc-01" / "evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["evidence_urls"] = ["https://github.com/pymc-devs/pymc/issues/999"]
    _write_json(evidence_path, payload)
    result = _run(paths)
    assert result.returncode != 0
    assert "evidence_urls" in result.stderr
