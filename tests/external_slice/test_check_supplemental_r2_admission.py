"""Binding/admission negatives for supplemental mining R2 (§6.2–6.5)."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "data" / "external_slice" / "supplemental_r2"
MINER_PATH = ROOT / "scripts" / "external_slice" / "mine_supplemental_r2.py"
CHECKER_PATH = ROOT / "scripts" / "external_slice" / "check_supplemental_r2_admission.py"
HANDOFF_PATH = ROOT / "scripts" / "external_slice" / "check_supplemental_r2_handoff_hashes.py"

SHEET_HEADER = [
    "neutral_id",
    "source_cohort",
    "repository",
    "issue_url",
    "buggy_sha",
    "fixed_sha",
    "mechanism",
    "crit_real_public_fix",
    "crit_dual_arm_repro",
    "crit_in_numerical_scope",
    "decision",
    "decision_reason",
    "analysis_id",
]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


miner = load_module(MINER_PATH, "mine_supplemental_r2")
checker = load_module(CHECKER_PATH, "check_supplemental_r2_admission")
handoff_mod = load_module(HANDOFF_PATH, "check_supplemental_r2_handoff_hashes")


@pytest.fixture(autouse=True)
def _install_synthetic_transport_freeze_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Synthetic retrieve fixtures have no baseline transport bytes; opt in explicitly.

    Live-copy / full-chain freeze tests must call ``_use_production_transport_freeze``.
    """

    def _provider(root: Path, repo_root: Path | None = None) -> bool:
        del root, repo_root
        return True

    monkeypatch.setattr(miner, "_TEST_TRANSPORT_FREEZE_PROVIDER", _provider)
    monkeypatch.setattr(checker, "_TEST_TRANSPORT_FREEZE_PROVIDER", _provider)
    monkeypatch.setattr(handoff_mod, "_TEST_TRANSPORT_FREEZE_PROVIDER", _provider)


def _use_production_transport_freeze(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear the test-only provider so Git-object freeze compare runs."""
    monkeypatch.setattr(miner, "_TEST_TRANSPORT_FREEZE_PROVIDER", None)
    monkeypatch.setattr(checker, "_TEST_TRANSPORT_FREEZE_PROVIDER", None)
    monkeypatch.setattr(handoff_mod, "_TEST_TRANSPORT_FREEZE_PROVIDER", None)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def seed_root(tmp_path: Path) -> Path:
    root = tmp_path / "supplemental_r2"
    root.mkdir(parents=True)
    for name in ("SCOPE.json", "TRANSPORT_CONTRACT.json", "QUOTAS.json"):
        shutil.copy2(FROZEN / name, root / name)
    return root


def make_issue(**kwargs: Any) -> dict[str, Any]:
    # Reuse miner test helpers via local minimal copy.
    number = kwargs["number"]
    owner = kwargs["owner"]
    name = kwargs["name"]
    return {
        "__typename": kwargs.get("typename", "Issue"),
        "id": f"ISSUE_{owner}_{name}_{number}",
        "number": number,
        "url": kwargs.get("url")
        or f"https://github.com/{owner}/{name}/issues/{number}",
        "state": kwargs.get("state", "CLOSED"),
        "title": kwargs["title"],
        "bodyText": kwargs.get("body", ""),
        "createdAt": kwargs["created_at"],
        "updatedAt": kwargs.get("updated_at", kwargs["created_at"]),
        "closedAt": kwargs.get("closed_at", "2026-01-02T00:00:00Z"),
        "labels": {
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [{"name": lab} for lab in kwargs.get("labels", [])],
        },
    }


def make_page(
    owner: str,
    name: str,
    nodes: list[dict[str, Any]],
    *,
    total_count: int | None = None,
    has_next: bool = False,
    end_cursor: str | None = "E",
) -> dict[str, Any]:
    return {
        "data": {
            "repository": {
                "issues": {
                    "totalCount": total_count if total_count is not None else len(nodes),
                    "pageInfo": {"hasNextPage": has_next, "endCursor": end_cursor},
                    "nodes": nodes,
                }
            }
        }
    }


def build_fixture_runner() -> Any:
    scope = json.loads((FROZEN / "SCOPE.json").read_text())
    pages: dict[tuple[str, str], dict[str, Any]] = {}
    for repo in scope["repositories"]:
        # Enough issues to exercise stop-rule / exclusions.
        nodes = []
        for i, n in enumerate([30, 29, 28, 27, 26], start=0):
            title = "wrong result" if i < 4 else "docs only"
            month = 6 - i
            nodes.append(
                make_issue(
                    number=n,
                    owner=repo["owner"],
                    name=repo["name"],
                    created_at=f"2025-0{month}-01T00:00:00Z",
                    title=title,
                    body="numerical regression" if i == 1 else "",
                )
            )
        pages[(repo["owner"], repo["name"])] = make_page(
            repo["owner"], repo["name"], nodes
        )

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        key = (variables["owner"], variables["name"])
        return 0, json.dumps(pages[key]), ""

    return runner


def write_sheet(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SHEET_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def build_multipage_coverage_runner() -> Any:
    """First SCOPE repo has 3 pages; remaining repos are single terminal pages."""
    scope = json.loads((FROZEN / "SCOPE.json").read_text(encoding="utf-8"))
    pages: dict[tuple[str, str], list[dict[str, Any]]] = {}
    first = scope["repositories"][0]
    first_key = (first["owner"], first["name"])
    first_nodes = [
        [
            make_issue(
                number=30,
                owner=first["owner"],
                name=first["name"],
                created_at="2025-06-01T00:00:00Z",
                title="wrong result",
            )
        ],
        [
            make_issue(
                number=29,
                owner=first["owner"],
                name=first["name"],
                created_at="2025-05-01T00:00:00Z",
                title="incorrect value",
            )
        ],
        [
            make_issue(
                number=28,
                owner=first["owner"],
                name=first["name"],
                created_at="2025-04-01T00:00:00Z",
                title="precision loss",
            ),
            make_issue(
                number=27,
                owner=first["owner"],
                name=first["name"],
                created_at="2025-03-01T00:00:00Z",
                title="docs only",
            ),
        ],
    ]
    pages[first_key] = [
        make_page(
            first["owner"],
            first["name"],
            first_nodes[0],
            total_count=4,
            has_next=True,
            end_cursor="C1",
        ),
        make_page(
            first["owner"],
            first["name"],
            first_nodes[1],
            total_count=4,
            has_next=True,
            end_cursor="C2",
        ),
        make_page(
            first["owner"],
            first["name"],
            first_nodes[2],
            total_count=4,
            has_next=False,
            end_cursor="C3",
        ),
    ]
    for repo in scope["repositories"][1:]:
        nodes = [
            make_issue(
                number=30,
                owner=repo["owner"],
                name=repo["name"],
                created_at="2025-06-01T00:00:00Z",
                title="wrong result",
            ),
            make_issue(
                number=29,
                owner=repo["owner"],
                name=repo["name"],
                created_at="2025-05-01T00:00:00Z",
                title="numerical regression",
            ),
            make_issue(
                number=28,
                owner=repo["owner"],
                name=repo["name"],
                created_at="2025-04-01T00:00:00Z",
                title="docs only",
            ),
        ]
        pages[(repo["owner"], repo["name"])] = [
            make_page(repo["owner"], repo["name"], nodes, end_cursor="E")
        ]

    def runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
        key = (variables["owner"], variables["name"])
        after = variables.get("after")
        repo_pages = pages[key]
        if after is None:
            return 0, json.dumps(repo_pages[0]), ""
        for idx, page in enumerate(repo_pages[:-1]):
            if after == page["data"]["repository"]["issues"]["pageInfo"]["endCursor"]:
                return 0, json.dumps(repo_pages[idx + 1]), ""
        return 1, "", f"unexpected after {after}"

    return runner


def reseal_publish_commit(root: Path) -> None:
    """Refresh manifest page hashes + PUBLISH_COMMIT after intentional tamper."""
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    for man in snap["page_manifest"]:
        page_path = root / man["path"]
        if page_path.is_file():
            man["sha256"] = miner.sha256_file(page_path)
    snap["page_manifest_sha256"] = checker.canonical_sha256(snap["page_manifest"])
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    page_files = {
        path.relative_to(root).as_posix(): miner.sha256_file(path)
        for path in sorted((root / "transport_pages").glob("*.json"))
    }
    publish = miner.build_publish_commit_identity(
        run_id=snap["run_id"],
        code_commit=snap["code_commit"],
        snapshot=snap,
        transport_page_sha256=page_files,
    )
    _write_json(root / "PUBLISH_COMMIT.json", publish)


def rehash_snapshot_record(rec: dict[str, Any]) -> None:
    body = {k: rec[k] for k in rec if k != "snapshot_record_sha256"}
    rec["snapshot_record_sha256"] = checker.canonical_sha256(body)


def fully_reseal_snapshot(root: Path) -> None:
    """Persist snapshot tamper and refresh the hash-bound PUBLISH_COMMIT seal."""
    reseal_publish_commit(root)


def sync_decisions_from_queue(root: Path) -> None:
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
    decisions_payload = json.loads(
        (root / "REVIEW_DECISIONS.json").read_text(encoding="utf-8")
    )
    by_neutral = {row["neutral_id"]: row for row in queue["records"]}
    for decision in decisions_payload["decisions"]:
        row = by_neutral[decision["neutral_id"]]
        for field in (
            "snapshot_record_id",
            "snapshot_record_sha256",
            "repository",
            "issue_node_id",
            "issue_number",
            "issue_url",
            "repository_review_order",
            "matched_phrases",
        ):
            decision[field] = row[field]
    _write_json(root / "REVIEW_DECISIONS.json", decisions_payload)


def rebuild_downstream_from_snapshot(root: Path) -> None:
    """Reseal publish, rebuild queue/decisions/sheet/evidence from tampered snapshot."""
    fully_reseal_snapshot(root)
    assert miner.cmd_build_queue(root) == 0
    sync_decisions_from_queue(root)
    assert miner.cmd_build_payload(root) == 0


def fully_sync_raw_page_tamper_and_rebuild(root: Path) -> None:
    """Sync raw-page/manifest/source/record hashes; rebuild queue→evidence→publish."""
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    for man in snap["page_manifest"]:
        page_path = root / man["path"]
        if page_path.is_file():
            man["sha256"] = miner.sha256_file(page_path)
    snap["page_manifest_sha256"] = checker.canonical_sha256(snap["page_manifest"])
    man_by_key = {
        (m["repository"], int(m["page_index"])): m for m in snap["page_manifest"]
    }
    for rec in snap["records"]:
        man = man_by_key[(rec["repository"], int(rec["source_page_index"]))]
        rec["source_page_sha256"] = man["sha256"]
        rehash_snapshot_record(rec)
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    sync_page_log_from_manifest(root)
    page_files = {
        path.relative_to(root).as_posix(): miner.sha256_file(path)
        for path in sorted((root / "transport_pages").glob("*.json"))
    }
    publish = miner.build_publish_commit_identity(
        run_id=snap["run_id"],
        code_commit=snap["code_commit"],
        snapshot=snap,
        transport_page_sha256=page_files,
    )
    _write_json(root / "PUBLISH_COMMIT.json", publish)
    assert miner.cmd_build_queue(root) == 0
    sync_decisions_from_queue(root)
    assert miner.cmd_build_payload(root) == 0
    seal_handoff_bundle(root)


def raw_page_node_for_record(
    root: Path, rec: dict[str, Any]
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    """Locate the hash-bound raw page and node object for a snapshot record."""
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    man = next(
        m
        for m in snap["page_manifest"]
        if m["repository"] == rec["repository"]
        and int(m["page_index"]) == int(rec["source_page_index"])
    )
    page_path = root / man["path"]
    page = json.loads(page_path.read_text(encoding="utf-8"))
    node = page["data"]["repository"]["issues"]["nodes"][int(rec["node_index"])]
    return page_path, page, node


def sync_page_log_from_manifest(root: Path) -> None:
    """Keep COMMAND_LOG page records aligned with tampered manifest fields."""
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    page_entries = [e for e in log["entries"] if isinstance(e.get("page_index"), int)]
    for entry, man in zip(page_entries, snap["page_manifest"]):
        for field in (
            "repository",
            "page_index",
            "after",
            "endCursor",
            "hasNextPage",
            "variables_sha256",
            "response_page_sha256",
            "variables",
        ):
            if field in man:
                entry[field] = man[field]
    _write_json(root / "COMMAND_LOG.json", log)


def load_first_repo_pages(root: Path) -> list[dict[str, Any]]:
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    first_repo = snap["page_manifest"][0]["repository"]
    return [m for m in snap["page_manifest"] if m["repository"] == first_repo]


def build_decision_from_queue_row(
    row: dict[str, Any],
    *,
    admit: bool = True,
    exclusion_class: str = "",
) -> dict[str, Any]:
    sha_a = "a" * 40
    sha_b = "b" * 40
    if admit:
        return {
            "neutral_id": row["neutral_id"],
            "snapshot_record_id": row["snapshot_record_id"],
            "snapshot_record_sha256": row["snapshot_record_sha256"],
            "repository": row["repository"],
            "issue_node_id": row["issue_node_id"],
            "issue_number": row["issue_number"],
            "issue_url": row["issue_url"],
            "repository_review_order": row["repository_review_order"],
            "matched_phrases": list(row["matched_phrases"]),
            "buggy_sha": sha_a,
            "fixed_sha": sha_b,
            "public_issue_url": row["issue_url"],
            "public_fix_url": f"{row['issue_url'].replace('/issues/', '/commit/')}-fix",
            "mechanism": "restores the numerical return value for the reported input.",
            "exclusion_class": "",
            "crit_real_public_fix": "PASS",
            "crit_in_numerical_scope": "PASS",
            "crit_dual_arm_repro": "PENDING",
            "decision": "ADMIT_PENDING_REPRO",
            "decision_reason": "A1 and A3 pass on public evidence.",
            "analysis_id": "",
        }
    return {
        "neutral_id": row["neutral_id"],
        "snapshot_record_id": row["snapshot_record_id"],
        "snapshot_record_sha256": row["snapshot_record_sha256"],
        "repository": row["repository"],
        "issue_node_id": row["issue_node_id"],
        "issue_number": row["issue_number"],
        "issue_url": row["issue_url"],
        "repository_review_order": row["repository_review_order"],
        "matched_phrases": list(row["matched_phrases"]),
        "buggy_sha": "",
        "fixed_sha": "",
        "public_issue_url": row["issue_url"],
        "public_fix_url": "",
        "mechanism": "excluded as documentation-only report.",
        "exclusion_class": exclusion_class or "documentation",
        "crit_real_public_fix": "FAIL",
        "crit_in_numerical_scope": "FAIL",
        "crit_dual_arm_repro": "PENDING",
        "decision": "EXCLUDED",
        "decision_reason": "documentation exclusion class applies.",
        "analysis_id": "",
    }


def build_valid_payload(
    root: Path,
    *,
    admits_per_quota_repo: int = 3,
    runner: Any | None = None,
) -> None:
    assert miner.cmd_retrieve(root, runner=runner or build_fixture_runner()) == 0
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())["records"]
    quotas = json.loads((root / "QUOTAS.json").read_text())
    scope = json.loads((root / "SCOPE.json").read_text())
    max_reviewed = int(scope["max_reviewed_per_repo"])
    target_pending = int(scope["target_pending_per_repo"])
    positive = {
        e["repo"]
        for e in quotas["readiness_quota_order"]
        if int(e["additional_ready_target"]) > 0
    }
    decisions: list[dict[str, Any]] = []
    by_repo: dict[str, list[dict[str, Any]]] = {}
    for row in queue:
        by_repo.setdefault(row["repository"], []).append(row)
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        rows = by_repo.get(repo, [])
        if not rows:
            continue
        admit_n = admits_per_quota_repo if repo in positive else 1
        repo_decisions: list[dict[str, Any]] = []
        for idx, row in enumerate(rows):
            repo_decisions.append(
                build_decision_from_queue_row(row, admit=idx < admit_n)
            )
            stop_at, _reason = miner.earliest_review_stop(
                repo_decisions,
                queue_count=len(rows),
                max_reviewed=max_reviewed,
                target_pending=target_pending,
            )
            if stop_at == len(repo_decisions):
                break
        decisions.extend(repo_decisions)
    _write_json(
        root / "REVIEW_DECISIONS.json",
        {"schema_version": 1, "task": "SUPPLEMENTAL_MINING_R2", "decisions": decisions},
    )
    assert miner.cmd_build_payload(root) == 0
    seal_handoff_bundle(root)


def seal_handoff_bundle(root: Path, *, payload_commit: str = "c0" * 20) -> None:
    """Write gate-bound VERIFICATION_LOG + handoff for both-checker verification."""
    _write_json(
        root / "VERIFICATION_LOG.json",
        {
            "schema_version": 1,
            "task": "SUPPLEMENTAL_MINING_R2",
            "gate_requested": miner.EXPECTED_GATE,
            "commands": [],
        },
    )
    assert miner.cmd_write_handoff(root, payload_commit=payload_commit) == 0


def both_checkers_fail(root: Path) -> None:
    assert checker.verify_admission(root) != 0
    assert (
        handoff_mod.verify_handoff_hashes(
            root / "HANDOFF_SUPPLEMENTAL_R2.json",
            cwd=root,
            check_parent=False,
            git_cwd=ROOT,
        )
        != 0
    )


def both_checkers_pass(root: Path) -> None:
    assert checker.verify_admission(root) == 0
    assert (
        handoff_mod.verify_handoff_hashes(
            root / "HANDOFF_SUPPLEMENTAL_R2.json",
            cwd=root,
            check_parent=False,
            git_cwd=ROOT,
        )
        == 0
    )


CANDIDATE_ARTIFACTS = (
    "ISSUE_SNAPSHOT.json",
    "REVIEW_QUEUE.json",
    "REVIEW_DECISIONS.json",
    "admission_sheet.cursor_candidate.csv",
    "EVIDENCE_SNAPSHOT.json",
    "HANDOFF_SUPPLEMENTAL_R2.json",
    "PUBLISH_COMMIT.json",
    "transport_pages",
    "admission_evidence",
)


def present_candidates(root: Path) -> set[str]:
    return {name for name in CANDIDATE_ARTIFACTS if (root / name).exists()}


def assert_checker_fails_without_new_mint(root: Path, before: set[str]) -> None:
    code = checker.verify_admission(root)
    assert code != 0
    after = present_candidates(root)
    assert after <= before, f"newly minted candidates: {after - before}"


def test_positive_admission_check(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, admits_per_quota_repo=3)
    assert checker.verify_admission(root) == 0


def _init_decoy_git(repo: Path) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def test_real_repo_docs_protocol_freeze_does_not_hit_seeded_root(
    tmp_path: Path,
) -> None:
    """Workspace docs with freeze tokens must not classify a fixture."""
    root = seed_root(tmp_path)
    hit, readiness, freeze = checker._forbidden_path_scan(
        root, repo_root=ROOT
    )
    assert (hit, readiness, freeze) == (False, False, False)
    hit_h, readiness_h, freeze_h = (
        handoff_mod._forbidden_path_scan(root, repo_root=ROOT)
    )
    hit_m, readiness_m, freeze_m = miner._forbidden_path_scan(
        root, repo_root=ROOT
    )
    assert (hit_h, readiness_h, freeze_h) == (False, False, False)
    assert (hit_m, readiness_m, freeze_m) == (False, False, False)


def test_unrelated_docs_protocol_freeze_outside_sibling_is_ignored(
    tmp_path: Path,
) -> None:
    """A new decoy freeze path outside sibling must not be a hit."""
    decoy_repo = tmp_path
    admission_home = decoy_repo / "admission_home"
    root = seed_root(admission_home)
    unrelated = (
        decoy_repo
        / "docs"
        / "review_20260812"
        / "phase0_protocol_freeze_task_report.md"
    )
    unrelated.parent.mkdir(parents=True, exist_ok=True)
    unrelated.write_text(
        "unrelated protocol freeze note\n",
        encoding="utf-8",
    )
    _init_decoy_git(decoy_repo)
    hit, readiness, freeze = checker._forbidden_path_scan(
        root, repo_root=decoy_repo
    )
    assert (hit, readiness, freeze) == (False, False, False)


def test_admission_root_protocol_freeze_file_still_rejected(
    tmp_path: Path,
) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, admits_per_quota_repo=3)
    (root / "protocol_freeze.md").write_text("x\n", encoding="utf-8")
    seal_handoff_bundle(root)
    both_checkers_fail(root)
    hit, readiness, freeze = checker._forbidden_path_scan(
        root, repo_root=tmp_path
    )
    assert hit is True
    assert freeze is True
    assert readiness is False


def test_three_forbidden_path_scan_classifications_match(
    tmp_path: Path,
) -> None:
    admission_home = tmp_path / "admission_home"
    root = seed_root(admission_home)
    unrelated = (
        tmp_path
        / "docs"
        / "superpowers"
        / "plans"
        / "2026-08-12-p3-phase0-protocol-freeze.md"
    )
    unrelated.parent.mkdir(parents=True, exist_ok=True)
    unrelated.write_text("unrelated\n", encoding="utf-8")
    (root / "readiness_note.md").write_text("x\n", encoding="utf-8")
    (admission_home / "freeze.json").write_text("{}\n", encoding="utf-8")
    _init_decoy_git(tmp_path)
    scanned = [
        mod._forbidden_path_scan(root, repo_root=tmp_path)
        for mod in (checker, handoff_mod, miner)
    ]
    assert scanned[0] == scanned[1] == scanned[2]
    hit, readiness, freeze = scanned[0]
    assert hit is True
    assert readiness is True
    assert freeze is True


@pytest.mark.parametrize(
    "target,field",
    [
        ("log_top", "run_id"),
        ("log_top", "code_commit"),
        ("log_entry", "run_id"),
        ("log_entry", "code_commit"),
        ("snapshot", "run_id"),
        ("snapshot", "code_commit"),
        ("queue", "run_id"),
        ("queue", "code_commit"),
    ],
)
def test_run_code_binding_field_tamper(
    tmp_path: Path, target: str, field: str
) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    if target == "log_top":
        payload = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
        payload[field] = "0" * 40 if field == "code_commit" else "tampered-run"
        _write_json(root / "COMMAND_LOG.json", payload)
    elif target == "log_entry":
        payload = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
        payload["entries"][0][field] = (
            "0" * 40 if field == "code_commit" else "tampered-run"
        )
        _write_json(root / "COMMAND_LOG.json", payload)
    elif target == "snapshot":
        payload = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
        payload[field] = "0" * 40 if field == "code_commit" else "tampered-run"
        _write_json(root / "ISSUE_SNAPSHOT.json", payload)
    else:
        payload = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
        payload[field] = "0" * 40 if field == "code_commit" else "tampered-run"
        _write_json(root / "REVIEW_QUEUE.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_queue_rebuild_preserves_run_code_binding(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    snapshot = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    (root / "REVIEW_QUEUE.json").unlink()
    assert miner.cmd_build_queue(root) == 0
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
    assert queue["run_id"] == snapshot["run_id"]
    assert queue["code_commit"] == snapshot["code_commit"]
    # Queue rebuild refreshes review_status_counts; reseal handoff bindings.
    seal_handoff_bundle(root)
    assert checker.verify_admission(root) == 0


def test_diagnostic_run_code_mismatch_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    _write_json(
        root / "RETRIEVAL_HARD_FAIL.json",
        {
            "schema_version": 1,
            "task": "SUPPLEMENTAL_MINING_R2",
            "invariant": "unexpected_error",
            "detail": "stale",
            "timestamp_utc": "2026-08-02T14:14:29Z",
            "run_id": "other-run",
            "code_commit": snap["code_commit"],
            "terminal": True,
        },
    )
    assert_checker_fails_without_new_mint(root, before)


@pytest.mark.parametrize(
    "field",
    [
        "after",
        "endCursor",
        "hasNextPage",
        "variables_sha256",
        "response_page_sha256",
        "page_index",
        "repository",
    ],
)
def test_page_log_manifest_field_tamper(tmp_path: Path, field: str) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    page = next(e for e in log["entries"] if isinstance(e.get("page_index"), int))
    if field in {"page_index"}:
        page[field] = int(page[field]) + 7
    elif field in {"variables_sha256", "response_page_sha256"}:
        page[field] = "0" * 64
    elif field == "hasNextPage":
        page[field] = not bool(page.get(field))
    else:
        page[field] = f"TAMPERED-{page.get(field)}"
    _write_json(root / "COMMAND_LOG.json", log)
    assert_checker_fails_without_new_mint(root, before)


def test_page_continuity_break_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    assert miner.cmd_retrieve(root, runner=build_fixture_runner()) == 0
    # Force a second page into the log/manifest reconstruction path via tamper.
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    first = next(e for e in log["entries"] if isinstance(e.get("page_index"), int))
    twin = dict(first)
    twin["page_index"] = 1
    twin["after"] = "NOT_PREV_END"
    twin["endCursor"] = "E2"
    # Insert after first page entry.
    idx = log["entries"].index(first)
    log["entries"].insert(idx + 1, twin)
    man = dict(snap["page_manifest"][0])
    man["page_index"] = 1
    man["after"] = "NOT_PREV_END"
    man["endCursor"] = "E2"
    snap["page_manifest"].insert(1, man)
    snap["page_manifest_sha256"] = checker.canonical_sha256(snap["page_manifest"])
    _write_json(root / "COMMAND_LOG.json", log)
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    # Re-seal publish commit to the tampered snapshot so binding gets past publish hash
    # only if we also refresh it; here we leave publish stale → either check may fail.
    before = present_candidates(root)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_publish_commit_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    (root / "PUBLISH_COMMIT.json").unlink()
    before = before - {"PUBLISH_COMMIT.json"}
    assert_checker_fails_without_new_mint(root, before)


def test_publish_commit_hash_tamper_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    publish = json.loads((root / "PUBLISH_COMMIT.json").read_text(encoding="utf-8"))
    publish["publish_commit_sha256"] = "0" * 64
    _write_json(root / "PUBLISH_COMMIT.json", publish)
    assert_checker_fails_without_new_mint(root, before)


def test_sequential_snapshot_without_matching_publish_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    snap["records"] = list(snap["records"])  # touch identity without rebinding publish
    snap["created_cutoff"] = "1999-01-01T00:00:00Z"
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    assert_checker_fails_without_new_mint(root, before)


def test_positive_scope_page_coverage_multipage(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    assert checker.verify_admission(root) == 0
    first_pages = load_first_repo_pages(root)
    assert len(first_pages) == 3
    assert first_pages[0]["hasNextPage"] is True
    assert first_pages[1]["hasNextPage"] is True
    assert first_pages[2]["hasNextPage"] is False


def test_delete_repo_block_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    dropped = snap["page_manifest"][0]["repository"]
    keep_manifest = [m for m in snap["page_manifest"] if m["repository"] != dropped]
    for man in snap["page_manifest"]:
        if man["repository"] == dropped:
            path = root / man["path"]
            if path.exists():
                path.unlink()
    snap["page_manifest"] = keep_manifest
    snap["records"] = [r for r in snap["records"] if r["repository"] != dropped]
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    log["entries"] = [
        e
        for e in log["entries"]
        if not (isinstance(e.get("page_index"), int) and e.get("repository") == dropped)
    ]
    _write_json(root / "COMMAND_LOG.json", log)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_reorder_repo_blocks_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    by_repo: dict[str, list[dict[str, Any]]] = {}
    for man in snap["page_manifest"]:
        by_repo.setdefault(man["repository"], []).append(man)
    repos = list(by_repo)
    # Swap first two repository blocks while keeping internal page order.
    repos[0], repos[1] = repos[1], repos[0]
    snap["page_manifest"] = [m for repo in repos for m in by_repo[repo]]
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    sync_page_log_from_manifest(root)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_middle_page_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    first_repo = snap["page_manifest"][0]["repository"]
    middle = next(
        m
        for m in snap["page_manifest"]
        if m["repository"] == first_repo and m["page_index"] == 1
    )
    (root / middle["path"]).unlink()
    snap["page_manifest"] = [m for m in snap["page_manifest"] if m is not middle]
    # Leave page_index 0 then 2 → non-contiguous block.
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    log["entries"] = [
        e
        for e in log["entries"]
        if not (
            isinstance(e.get("page_index"), int)
            and e.get("repository") == first_repo
            and e.get("page_index") == 1
        )
    ]
    _write_json(root / "COMMAND_LOG.json", log)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_last_page_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    first_repo = snap["page_manifest"][0]["repository"]
    last = next(
        m
        for m in snap["page_manifest"]
        if m["repository"] == first_repo and m["page_index"] == 2
    )
    (root / last["path"]).unlink()
    snap["page_manifest"] = [m for m in snap["page_manifest"] if m is not last]
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    log["entries"] = [
        e
        for e in log["entries"]
        if not (
            isinstance(e.get("page_index"), int)
            and e.get("repository") == first_repo
            and e.get("page_index") == 2
        )
    ]
    _write_json(root / "COMMAND_LOG.json", log)
    sync_page_log_from_manifest(root)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_fake_termination_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    first_repo = snap["page_manifest"][0]["repository"]
    # Drop trailing pages and falsely terminate page 0 while totalCount stays 4.
    keep = []
    for man in snap["page_manifest"]:
        if man["repository"] != first_repo:
            keep.append(man)
            continue
        if man["page_index"] == 0:
            page = json.loads((root / man["path"]).read_text(encoding="utf-8"))
            page["data"]["repository"]["issues"]["pageInfo"]["hasNextPage"] = False
            _write_json(root / man["path"], page)
            man["hasNextPage"] = False
            man["node_count"] = len(page["data"]["repository"]["issues"]["nodes"])
            keep.append(man)
        else:
            path = root / man["path"]
            if path.exists():
                path.unlink()
    snap["page_manifest"] = keep
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    log["entries"] = [
        e
        for e in log["entries"]
        if not (
            isinstance(e.get("page_index"), int)
            and e.get("repository") == first_repo
            and int(e.get("page_index")) > 0
        )
    ]
    _write_json(root / "COMMAND_LOG.json", log)
    sync_page_log_from_manifest(root)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_total_count_drift_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    middle = next(
        m for m in snap["page_manifest"] if m["page_index"] == 1
    )
    page = json.loads((root / middle["path"]).read_text(encoding="utf-8"))
    page["data"]["repository"]["issues"]["totalCount"] = 99
    _write_json(root / middle["path"], page)
    middle["totalCount"] = 99
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    sync_page_log_from_manifest(root)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_node_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    first = snap["page_manifest"][0]
    page = json.loads((root / first["path"]).read_text(encoding="utf-8"))
    page["data"]["repository"]["issues"]["nodes"] = []
    _write_json(root / first["path"], page)
    first["node_count"] = 0
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    sync_page_log_from_manifest(root)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_duplicate_node_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    first_repo = snap["page_manifest"][0]["repository"]
    page0 = next(
        m
        for m in snap["page_manifest"]
        if m["repository"] == first_repo and m["page_index"] == 0
    )
    page1 = next(
        m
        for m in snap["page_manifest"]
        if m["repository"] == first_repo and m["page_index"] == 1
    )
    raw0 = json.loads((root / page0["path"]).read_text(encoding="utf-8"))
    raw1 = json.loads((root / page1["path"]).read_text(encoding="utf-8"))
    # Copy page0 node identity onto page1 → duplicate across the block.
    raw1["data"]["repository"]["issues"]["nodes"] = json.loads(
        json.dumps(raw0["data"]["repository"]["issues"]["nodes"])
    )
    _write_json(root / page1["path"], raw1)
    page1["node_count"] = len(raw1["data"]["repository"]["issues"]["nodes"])
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    sync_page_log_from_manifest(root)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_cross_repo_duplicate_node_id_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    first_repo = snap["page_manifest"][0]["repository"]
    second_repo = next(
        m["repository"]
        for m in snap["page_manifest"]
        if m["repository"] != first_repo
    )
    page_a = next(
        m
        for m in snap["page_manifest"]
        if m["repository"] == first_repo and m["page_index"] == 0
    )
    page_b = next(
        m
        for m in snap["page_manifest"]
        if m["repository"] == second_repo and m["page_index"] == 0
    )
    raw_a = json.loads((root / page_a["path"]).read_text(encoding="utf-8"))
    raw_b = json.loads((root / page_b["path"]).read_text(encoding="utf-8"))
    donor_id = raw_a["data"]["repository"]["issues"]["nodes"][0]["id"]
    # Keep repo-B URL/number valid for SCOPE; only the GraphQL node id collides.
    raw_b["data"]["repository"]["issues"]["nodes"][0]["id"] = donor_id
    _write_json(root / page_b["path"], raw_b)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_cross_repo_duplicate_url_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    first_repo = snap["page_manifest"][0]["repository"]
    second_repo = next(
        m["repository"]
        for m in snap["page_manifest"]
        if m["repository"] != first_repo
    )
    page_a = next(
        m
        for m in snap["page_manifest"]
        if m["repository"] == first_repo and m["page_index"] == 0
    )
    page_b = next(
        m
        for m in snap["page_manifest"]
        if m["repository"] == second_repo and m["page_index"] == 0
    )
    raw_a = json.loads((root / page_a["path"]).read_text(encoding="utf-8"))
    raw_b = json.loads((root / page_b["path"]).read_text(encoding="utf-8"))
    donor_url = raw_a["data"]["repository"]["issues"]["nodes"][0]["url"]
    raw_b["data"]["repository"]["issues"]["nodes"][0]["url"] = donor_url
    _write_json(root / page_b["path"], raw_b)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_wrong_repo_url_fails_after_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    page = snap["page_manifest"][0]
    raw = json.loads((root / page["path"]).read_text(encoding="utf-8"))
    number = raw["data"]["repository"]["issues"]["nodes"][0]["number"]
    raw["data"]["repository"]["issues"]["nodes"][0]["url"] = (
        f"https://github.com/evil-org/evil-repo/issues/{number}"
    )
    _write_json(root / page["path"], raw)
    reseal_publish_commit(root)
    assert_checker_fails_without_new_mint(root, before)


def test_same_issue_number_across_repos_allowed(tmp_path: Path) -> None:
    """Issue numbers remain unique only within a repository."""
    root = seed_root(tmp_path)
    build_valid_payload(root, runner=build_multipage_coverage_runner())
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    numbers_by_repo: dict[str, set[int]] = {}
    for man in snap["page_manifest"]:
        page = json.loads((root / man["path"]).read_text(encoding="utf-8"))
        for node in page["data"]["repository"]["issues"]["nodes"]:
            numbers_by_repo.setdefault(man["repository"], set()).add(node["number"])
    shared = set.intersection(*numbers_by_repo.values())
    assert shared, "fixture should reuse issue numbers across repositories"
    assert checker.verify_admission(root) == 0


@pytest.mark.parametrize(
    "field",
    [
        "snapshot_record_id",
        "snapshot_record_sha256",
        "repository",
        "repository_order",
        "issue_node_id",
        "issue_number",
        "issue_url",
        "state",
        "created_at",
        "matched_phrases",
        "source_page_sha256",
    ],
)
def test_queue_copied_field_mutation(tmp_path: Path, field: str) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    row = queue["records"][0]
    if field == "issue_number":
        row[field] = int(row[field]) + 99
    elif field == "matched_phrases":
        row[field] = ["tampered phrase"]
    elif field == "repository_order":
        row[field] = 99
    else:
        row[field] = f"TAMPERED-{row.get(field)}"
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert_checker_fails_without_new_mint(root, before)


def test_snapshot_record_hash_mutation(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    snap["records"][0]["snapshot_record_sha256"] = "0" * 64
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    assert_checker_fails_without_new_mint(root, before)


def test_live_snapshot_reconstructs_from_raw_pages() -> None:
    """Committed Task-4 snapshot must equal independent raw-page reconstruction."""
    root = FROZEN
    if not (root / "ISSUE_SNAPSHOT.json").is_file():
        pytest.skip("live ISSUE_SNAPSHOT.json absent")
    if not (root / "transport_pages").is_dir():
        pytest.skip("live transport_pages absent")
    scope = json.loads((root / "SCOPE.json").read_text(encoding="utf-8"))
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rebuilt = checker.reconstruct_snapshot_records_from_raw_pages(
        root, scope=scope, snapshot=snap
    )
    assert rebuilt == snap["records"]
    checker.verify_snapshot_bound_to_raw_pages(root, scope=scope, snapshot=snap)


def test_snapshot_reconstruction_does_not_call_producer_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    loaded = checker._load_miner()

    def boom(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("producer selection/builder must not be called")

    monkeypatch.setattr(loaded, "select_phrase_union", boom)
    monkeypatch.setattr(loaded, "build_snapshot_record", boom)
    monkeypatch.setattr(loaded, "match_surfaces", boom)
    monkeypatch.setattr(loaded, "normalize_match_text", boom)
    monkeypatch.setattr(checker, "_load_miner", lambda: loaded)
    assert checker.verify_admission(root) == 0


def test_false_phrase_match(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    snap["records"][0]["matched_phrases"] = ["not a frozen phrase"]
    # Keep hash consistent with mutated body so hash check isn't the only failure.
    body = {
        k: snap["records"][0][k]
        for k in snap["records"][0]
        if k != "snapshot_record_sha256"
    }
    snap["records"][0]["snapshot_record_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    assert_checker_fails_without_new_mint(root, before)


def test_fake_frozen_phrase_fails_after_full_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    rec["matched_phrases"] = ["wrong result", "fabricated frozen phrase"]
    rec["match_surfaces"] = {
        "wrong result": list(rec["match_surfaces"].get("wrong result") or ["title"]),
        "fabricated frozen phrase": ["title"],
    }
    rehash_snapshot_record(rec)
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    fully_reseal_snapshot(root)
    assert_checker_fails_without_new_mint(root, before)


def test_real_frozen_unmatched_phrase_fails_after_downstream_rebuild(
    tmp_path: Path,
) -> None:
    """Inject a real SCOPE phrase absent from raw surfaces; rebuild downstream."""
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    scope = json.loads((root / "SCOPE.json").read_text(encoding="utf-8"))
    phrases = list(scope["phrases"])
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    page_path, page, node = raw_page_node_for_record(root, rec)
    unmatched = next(p for p in phrases if p not in rec["matched_phrases"])
    assert checker.match_surfaces(node, unmatched) == []
    rec["matched_phrases"] = [p for p in phrases if p in set(rec["matched_phrases"]) | {unmatched}]
    rec["match_surfaces"] = {
        **dict(rec.get("match_surfaces") or {}),
        unmatched: ["title"],
    }
    rehash_snapshot_record(rec)
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    # Keep raw page bytes unchanged; only reseal/rebuild derived artifacts.
    assert page_path.is_file()
    _ = page
    rebuild_downstream_from_snapshot(root)
    assert_checker_fails_without_new_mint(root, before)


def _apply_label_pageinfo_mutator(node: dict[str, Any], kind: str) -> None:
    if kind == "labels_missing":
        node.pop("labels", None)
        return
    if kind == "labels_null":
        node["labels"] = None
        return
    if kind == "pageinfo_missing":
        labels = node.setdefault("labels", {"nodes": []})
        assert isinstance(labels, dict)
        labels.pop("pageInfo", None)
        return
    if kind == "pageinfo_null":
        labels = node.setdefault("labels", {"nodes": []})
        assert isinstance(labels, dict)
        labels["pageInfo"] = None
        return
    labels = node.setdefault("labels", {"nodes": []})
    assert isinstance(labels, dict)
    page_info = labels.get("pageInfo")
    if not isinstance(page_info, dict):
        page_info = {}
        labels["pageInfo"] = page_info
    if kind == "hasnext_missing":
        page_info.pop("hasNextPage", None)
    elif kind == "hasnext_null":
        page_info["hasNextPage"] = None
    elif kind == "hasnext_nonbool":
        page_info["hasNextPage"] = "yes"
    elif kind == "hasnext_true":
        page_info["hasNextPage"] = True
    elif kind == "hasnext_false":
        page_info["hasNextPage"] = False
    else:
        raise AssertionError(f"unknown label mutator kind: {kind}")


def test_pullrequest_typename_fails_after_full_sync_rebuild(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    page_path, page, node = raw_page_node_for_record(root, rec)
    node["__typename"] = "PullRequest"
    _write_json(page_path, page)
    fully_sync_raw_page_tamper_and_rebuild(root)
    assert_checker_fails_without_new_mint(root, before)


@pytest.mark.parametrize(
    "kind",
    [
        "labels_missing",
        "labels_null",
        "pageinfo_missing",
        "pageinfo_null",
        "hasnext_missing",
        "hasnext_null",
        "hasnext_nonbool",
        "hasnext_true",
    ],
)
def test_incomplete_labels_fails_after_full_sync_rebuild(
    tmp_path: Path, kind: str
) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    page_path, page, node = raw_page_node_for_record(root, rec)
    _apply_label_pageinfo_mutator(node, kind)
    _write_json(page_path, page)
    fully_sync_raw_page_tamper_and_rebuild(root)
    assert_checker_fails_without_new_mint(root, before)


def test_hasnext_false_positive_control_after_full_sync_rebuild(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    page_path, page, node = raw_page_node_for_record(root, rec)
    _apply_label_pageinfo_mutator(node, "hasnext_false")
    _write_json(page_path, page)
    fully_sync_raw_page_tamper_and_rebuild(root)
    assert checker.verify_admission(root) == 0


def test_removing_typename_guard_turns_pullrequest_negative_red(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without typename guard, a fully synced PullRequest attack admits."""
    root = seed_root(tmp_path)
    build_valid_payload(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    page_path, page, node = raw_page_node_for_record(root, rec)
    node["__typename"] = "PullRequest"
    _write_json(page_path, page)
    fully_sync_raw_page_tamper_and_rebuild(root)
    assert checker.verify_admission(root) != 0

    real = checker.validate_raw_issue_node

    def without_typename_guard(raw_node: Any, *, repository: str) -> dict[str, Any]:
        if isinstance(raw_node, dict) and raw_node.get("__typename") != "Issue":
            patched = dict(raw_node)
            patched["__typename"] = "Issue"
            return real(patched, repository=repository)
        return real(raw_node, repository=repository)

    monkeypatch.setattr(checker, "validate_raw_issue_node", without_typename_guard)
    assert checker.verify_admission(root) == 0


def test_removing_label_guard_turns_incomplete_label_negative_red(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without label completeness guard, fully synced hasNextPage=true admits."""
    root = seed_root(tmp_path)
    build_valid_payload(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    page_path, page, node = raw_page_node_for_record(root, rec)
    _apply_label_pageinfo_mutator(node, "hasnext_true")
    _write_json(page_path, page)
    fully_sync_raw_page_tamper_and_rebuild(root)
    assert checker.verify_admission(root) != 0

    real = checker.validate_raw_issue_node

    def without_label_guard(raw_node: Any, *, repository: str) -> dict[str, Any]:
        if not isinstance(raw_node, dict):
            return real(raw_node, repository=repository)
        patched = json.loads(json.dumps(raw_node))
        labels = patched.get("labels")
        if not isinstance(labels, dict):
            patched["labels"] = {
                "pageInfo": {"hasNextPage": False, "endCursor": None},
                "nodes": [],
            }
        else:
            page_info = labels.get("pageInfo")
            if not isinstance(page_info, dict):
                labels["pageInfo"] = {"hasNextPage": False, "endCursor": None}
            else:
                page_info["hasNextPage"] = False
            if not isinstance(labels.get("nodes"), list):
                labels["nodes"] = []
        return real(patched, repository=repository)

    monkeypatch.setattr(checker, "validate_raw_issue_node", without_label_guard)
    assert checker.verify_admission(root) == 0


def test_fake_match_surface_fails_after_full_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    phrase = rec["matched_phrases"][0]
    rec["match_surfaces"][phrase] = ["body", "title", "label:fabricated"]
    rehash_snapshot_record(rec)
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    fully_reseal_snapshot(root)
    assert_checker_fails_without_new_mint(root, before)


def test_title_body_hash_tamper_fails_after_full_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    rec["title_sha256"] = "a" * 64
    rec["body_text_sha256"] = "b" * 64
    rehash_snapshot_record(rec)
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    fully_reseal_snapshot(root)
    assert_checker_fails_without_new_mint(root, before)


def test_ordered_labels_tamper_fails_after_full_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    rec["ordered_labels"] = list(rec.get("ordered_labels") or []) + ["fabricated-label"]
    rehash_snapshot_record(rec)
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    fully_reseal_snapshot(root)
    assert_checker_fails_without_new_mint(root, before)


def test_source_page_binding_tamper_fails_after_full_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    rec = snap["records"][0]
    rec["source_page_index"] = int(rec["source_page_index"]) + 7
    rec["source_page_sha256"] = "c" * 64
    rehash_snapshot_record(rec)
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    fully_reseal_snapshot(root)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_snapshot_record_fails_after_full_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    assert len(snap["records"]) >= 2
    snap["records"] = snap["records"][1:]
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    fully_reseal_snapshot(root)
    assert_checker_fails_without_new_mint(root, before)


def test_extra_snapshot_record_fails_after_full_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    clone = json.loads(json.dumps(snap["records"][0]))
    clone["snapshot_record_id"] = "SSR2-99-9999"
    clone["issue_node_id"] = "ISSUE_FABRICATED_EXTRA"
    clone["issue_url"] = "https://github.com/pymc-devs/pymc/issues/999999"
    clone["issue_number"] = 999999
    rehash_snapshot_record(clone)
    snap["records"] = list(snap["records"]) + [clone]
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    fully_reseal_snapshot(root)
    assert_checker_fails_without_new_mint(root, before)


def test_reordered_snapshot_records_fail_after_full_reseal(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    repo = snap["records"][0]["repository"]
    idxs = [i for i, r in enumerate(snap["records"]) if r["repository"] == repo]
    assert len(idxs) >= 2
    i0, i1 = idxs[0], idxs[1]
    snap["records"][i0], snap["records"][i1] = snap["records"][i1], snap["records"][i0]
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    fully_reseal_snapshot(root)
    assert_checker_fails_without_new_mint(root, before)


def test_wrong_phrase_order(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    # Find a record with >=2 phrases if possible; else inject reversed pair.
    rec = snap["records"][0]
    rec["matched_phrases"] = list(reversed(rec["matched_phrases"])) or [
        "incorrect value",
        "wrong result",
    ]
    if len(rec["matched_phrases"]) == 1:
        rec["matched_phrases"] = ["incorrect value", "wrong result"]
        rec["match_surfaces"] = {
            "incorrect value": ["title"],
            "wrong result": ["title"],
        }
    body = {k: rec[k] for k in rec if k != "snapshot_record_sha256"}
    rec["snapshot_record_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    assert_checker_fails_without_new_mint(root, before)


def test_reordered_union(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    pymc = [r for r in queue["records"] if r["repository"] == "pymc-devs/pymc"]
    if len(pymc) >= 2:
        # Swap first two pymc rows in the full list.
        i0 = queue["records"].index(pymc[0])
        i1 = queue["records"].index(pymc[1])
        queue["records"][i0], queue["records"][i1] = (
            queue["records"][i1],
            queue["records"][i0],
        )
        _write_json(root / "REVIEW_QUEUE.json", queue)
        assert_checker_fails_without_new_mint(root, before)
    else:
        pytest.skip("need >=2 pymc rows")


def test_wrong_neutral_id(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    queue["records"][0]["neutral_id"] = "EXT-pymc-99"
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_snapshot_item(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    snap = json.loads((root / "ISSUE_SNAPSHOT.json").read_text())
    snap["records"].pop(0)
    _write_json(root / "ISSUE_SNAPSHOT.json", snap)
    assert_checker_fails_without_new_mint(root, before)


def test_extra_queue_row(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    clone = dict(queue["records"][0])
    clone["neutral_id"] = "EXT-pymc-99"
    clone["union_order"] = 99
    clone["repository_review_order"] = 99
    queue["records"].append(clone)
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert_checker_fails_without_new_mint(root, before)


@pytest.mark.parametrize(
    "field",
    [
        "neutral_id",
        "snapshot_record_id",
        "snapshot_record_sha256",
        "repository",
        "issue_node_id",
        "issue_number",
        "issue_url",
        "repository_review_order",
        "matched_phrases",
    ],
)
def test_decision_copied_field_mutation(tmp_path: Path, field: str) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    d = payload["decisions"][0]
    if field == "issue_number":
        d[field] = int(d[field]) + 7
    elif field == "matched_phrases":
        d[field] = ["tampered"]
    elif field == "repository_review_order":
        d[field] = 99
    else:
        d[field] = f"TAMPERED-{d.get(field)}"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_decision_for_unreviewed_row(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text())
    # Mark first as NOT_REVIEWED_AFTER_STOP while decision remains.
    queue["records"][0]["review_status"] = "NOT_REVIEWED_AFTER_STOP"
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert_checker_fails_without_new_mint(root, before)


def test_invalid_exclusion_class(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    for d in payload["decisions"]:
        if d["decision"] == "EXCLUDED":
            d["exclusion_class"] = "not-a-real-class"
            break
    else:
        payload["decisions"][0]["decision"] = "EXCLUDED"
        payload["decisions"][0]["exclusion_class"] = "not-a-real-class"
        payload["decisions"][0]["crit_real_public_fix"] = "FAIL"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_short_sha_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    payload["decisions"][0]["buggy_sha"] = "abc"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_public_url(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    payload["decisions"][0]["public_fix_url"] = ""
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_non_pending_a2(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    payload["decisions"][0]["crit_dual_arm_repro"] = "PASS"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_admit_inconsistency(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    payload["decisions"][0]["crit_in_numerical_scope"] = "FAIL"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


def test_reordered_decisions(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    if len(payload["decisions"]) < 2:
        pytest.skip("need >=2 decisions")
    payload["decisions"][0], payload["decisions"][1] = (
        payload["decisions"][1],
        payload["decisions"][0],
    )
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert_checker_fails_without_new_mint(root, before)


@pytest.mark.parametrize(
    "field",
    [
        "neutral_id",
        "repository",
        "issue_url",
        "buggy_sha",
        "fixed_sha",
        "mechanism",
        "crit_real_public_fix",
        "crit_dual_arm_repro",
        "crit_in_numerical_scope",
        "decision",
        "decision_reason",
    ],
)
def test_sheet_field_mutation(tmp_path: Path, field: str) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    rows = list(csv.DictReader((root / "admission_sheet.cursor_candidate.csv").open()))
    if field == "crit_dual_arm_repro":
        rows[0][field] = "PASS"
    elif field == "source_cohort":
        rows[0][field] = "tampered"
    else:
        rows[0][field] = f"TAMPERED-{rows[0].get(field)}"
    write_sheet(root / "admission_sheet.cursor_candidate.csv", rows)
    assert_checker_fails_without_new_mint(root, before)


def test_wrong_cohort(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    rows = list(csv.DictReader((root / "admission_sheet.cursor_candidate.csv").open()))
    rows[0]["source_cohort"] = "supplemental_r1"
    write_sheet(root / "admission_sheet.cursor_candidate.csv", rows)
    assert_checker_fails_without_new_mint(root, before)


def test_nonblank_alias(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    rows = list(csv.DictReader((root / "admission_sheet.cursor_candidate.csv").open()))
    rows[0]["analysis_id"] = "CE-01"
    write_sheet(root / "admission_sheet.cursor_candidate.csv", rows)
    assert_checker_fails_without_new_mint(root, before)


def test_forbidden_vocabulary_in_sheet(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    rows = list(csv.DictReader((root / "admission_sheet.cursor_candidate.csv").open()))
    rows[0]["mechanism"] = "uses operator fiber mapping"
    write_sheet(root / "admission_sheet.cursor_candidate.csv", rows)
    assert_checker_fails_without_new_mint(root, before)


@pytest.mark.parametrize(
    "field",
    [
        "neutral_id",
        "snapshot_record_id",
        "snapshot_record_sha256",
        "repository",
        "issue_node_id",
        "issue_number",
        "issue_url",
        "buggy_sha",
        "fixed_sha",
        "public_issue_url",
        "public_fix_url",
        "mechanism",
        "exclusion_class",
        "crit_real_public_fix",
        "crit_dual_arm_repro",
        "crit_in_numerical_scope",
        "decision",
    ],
)
def test_evidence_field_mutation(tmp_path: Path, field: str) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    manifest = json.loads((root / "EVIDENCE_SNAPSHOT.json").read_text())
    nid = manifest["records"][0]["neutral_id"]
    path = root / "admission_evidence" / nid / "evidence.json"
    evidence = json.loads(path.read_text())
    if field == "issue_number":
        evidence[field] = int(evidence[field]) + 3
    elif field == "crit_dual_arm_repro":
        evidence[field] = "PASS"
    else:
        evidence[field] = f"TAMPERED-{evidence.get(field)}"
    _write_json(path, evidence)
    # Keep manifest hash pointing at old bytes → hash mismatch also fails.
    assert_checker_fails_without_new_mint(root, before)


def test_evidence_hash_mismatch(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    manifest = json.loads((root / "EVIDENCE_SNAPSHOT.json").read_text())
    manifest["records"][0]["sha256"] = "0" * 64
    _write_json(root / "EVIDENCE_SNAPSHOT.json", manifest)
    assert_checker_fails_without_new_mint(root, before)


def test_missing_evidence_row(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    manifest = json.loads((root / "EVIDENCE_SNAPSHOT.json").read_text())
    nid = manifest["records"][0]["neutral_id"]
    shutil.rmtree(root / "admission_evidence" / nid)
    manifest["records"].pop(0)
    _write_json(root / "EVIDENCE_SNAPSHOT.json", manifest)
    assert_checker_fails_without_new_mint(root, before)


def test_extra_sheet_row(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    rows = list(csv.DictReader((root / "admission_sheet.cursor_candidate.csv").open()))
    clone = dict(rows[0])
    clone["neutral_id"] = "EXT-pymc-99"
    rows.append(clone)
    write_sheet(root / "admission_sheet.cursor_candidate.csv", rows)
    assert_checker_fails_without_new_mint(root, before)


def test_changed_starting_counts(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    quotas = json.loads((root / "QUOTAS.json").read_text())
    quotas["starting_state"]["accepted_ready_defects"] = 17
    _write_json(root / "QUOTAS.json", quotas)
    assert_checker_fails_without_new_mint(root, before)


def test_quota_target_change(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    quotas = json.loads((root / "QUOTAS.json").read_text())
    quotas["readiness_quota_order"][0]["additional_ready_target"] = 9
    _write_json(root / "QUOTAS.json", quotas)
    assert_checker_fails_without_new_mint(root, before)


def test_replacement_repository(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    quotas = json.loads((root / "QUOTAS.json").read_text())
    quotas["readiness_quota_order"][0]["repo"] = "numpy/numpy"
    _write_json(root / "QUOTAS.json", quotas)
    assert_checker_fails_without_new_mint(root, before)


def test_incorrect_projection(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    quotas = json.loads((root / "QUOTAS.json").read_text())
    quotas["projection_if_quotas_met"]["qualifying_projects"] = 4
    _write_json(root / "QUOTAS.json", quotas)
    assert_checker_fails_without_new_mint(root, before)


def test_handoff_claims_ready_success(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="a" * 40) == 0
    before = present_candidates(root)
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["quota_feasibility"]["claims_ready_success"] = True
    _write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
    assert_checker_fails_without_new_mint(root, before)


def test_handoff_missing_shortfall_disclosure(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    # Only 1 admit per positive repo → shortfall expected.
    build_valid_payload(root, admits_per_quota_repo=1)
    assert miner.cmd_write_handoff(root, payload_commit="b" * 40) == 0
    before = present_candidates(root)
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["quota_feasibility"]["shortfalls"] = []
    handoff["quota_feasibility"]["status"] = "DISTRIBUTION_TARGET_AT_RISK"
    _write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
    assert_checker_fails_without_new_mint(root, before)


def test_handoff_hash_mismatch(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="c" * 40) == 0
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["file_sha256"]["ISSUE_SNAPSHOT.json"] = "0" * 64
    path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
    _write_json(path, handoff)
    code = handoff_mod.verify_handoff_hashes(
        path, cwd=root, check_parent=False, git_cwd=ROOT
    )
    assert code != 0


def test_handoff_self_resolution_and_parent(tmp_path: Path) -> None:
    # Bare fixture directory: hash/parent only (no admission summary artifacts).
    bare = tmp_path / "bare_handoff"
    bare.mkdir()
    scope_src = FROZEN / "SCOPE.json"
    scope_dst = bare / "SCOPE.json"
    scope_dst.write_bytes(scope_src.read_bytes())
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    parent = subprocess.run(
        ["git", "rev-parse", "HEAD^"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    handoff = {
        "file_sha256": {
            "SCOPE.json": hashlib.sha256(scope_dst.read_bytes()).hexdigest()
        },
        "evidence_sha256": {},
        "payload_commit": parent,
        "handoff_commit": {
            "value": "SELF",
            "direct_parent_required": parent,
            "resolution": "git rev-parse HEAD",
        },
    }
    path = bare / "HANDOFF_SELF.json"
    _write_json(path, handoff)
    code = handoff_mod.verify_handoff_hashes(
        path, cwd=bare, check_parent=True, git_cwd=ROOT
    )
    assert code == 0

    handoff["handoff_commit"]["direct_parent_required"] = "0" * 40
    handoff["payload_commit"] = "0" * 40
    _write_json(path, handoff)
    code = handoff_mod.verify_handoff_hashes(
        path, cwd=bare, check_parent=True, git_cwd=ROOT
    )
    assert code != 0
    assert head


def test_stale_code_hash_in_handoff(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="d" * 40) == 0
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    script_key = "scripts/external_slice/mine_supplemental_r2.py"
    handoff["file_sha256"][script_key] = "1" * 64
    path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
    _write_json(path, handoff)
    code = handoff_mod.verify_handoff_hashes(
        path, cwd=root, check_parent=False, git_cwd=ROOT
    )
    assert code != 0


def test_validate_decisions_cli(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_validate_decisions(root) == 0
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text())
    payload["decisions"][0]["crit_dual_arm_repro"] = "PASS"
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    assert miner.cmd_validate_decisions(root) != 0


def _repo_rows(root: Path, repo: str) -> list[dict[str, Any]]:
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
    return [r for r in queue["records"] if r["repository"] == repo]


def _rewrite_repo_decisions(
    root: Path, repo: str, new_repo_decisions: list[dict[str, Any]]
) -> None:
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text(encoding="utf-8"))
    kept = [d for d in payload["decisions"] if d["repository"] != repo]
    # Preserve repository order used by checker expected_ids.
    scope = json.loads((root / "SCOPE.json").read_text(encoding="utf-8"))
    by_repo: dict[str, list[dict[str, Any]]] = {}
    for d in kept + new_repo_decisions:
        by_repo.setdefault(d["repository"], []).append(d)
    ordered: list[dict[str, Any]] = []
    for entry in scope["repositories"]:
        ordered.extend(by_repo.get(entry["repo"], []))
    payload["decisions"] = ordered
    _write_json(root / "REVIEW_DECISIONS.json", payload)


def _synthetic_queue_row(
    *,
    repo: str,
    order: int,
    prefix: str,
) -> dict[str, Any]:
    nid = f"{prefix}{order:02d}"
    return {
        "neutral_id": nid,
        "snapshot_record_id": f"SSR2-{order:04d}",
        "snapshot_record_sha256": "a" * 64,
        "repository": repo,
        "repository_order": 1,
        "issue_node_id": f"NODE-{order}",
        "issue_number": 1000 + order,
        "issue_url": f"https://github.com/{repo}/issues/{1000 + order}",
        "state": "CLOSED",
        "created_at": "2025-01-01T00:00:00Z",
        "matched_phrases": ["wrong result"],
        "source_page_sha256": "b" * 64,
        "repository_review_order": order,
        "review_status": "REVIEWED",
    }


def test_decision_after_fifth_admit_rejected() -> None:
    scope = json.loads((FROZEN / "SCOPE.json").read_text(encoding="utf-8"))
    repo = "pymc-devs/pymc"
    prefix = "EXT-pymc-"
    queue = [
        _synthetic_queue_row(repo=repo, order=i, prefix=prefix) for i in range(1, 25)
    ]
    for row in queue:
        row["review_status"] = "PENDING_REVIEW"
    # Fifth admit at row 5, but continue reviewing through row 20.
    decisions = []
    for idx, row in enumerate(queue[:20]):
        decisions.append(build_decision_from_queue_row(row, admit=idx < 5))
    with pytest.raises(checker.AdmissionError, match="earliest stop"):
        checker.verify_decisions(scope, queue, {"decisions": decisions})
    with pytest.raises(miner.HardFail, match="earliest stop"):
        miner.validate_decisions_payload(
            scope=scope, queue=queue, decisions=decisions
        )


def test_row20_fifth_admit_cap_tie_accepted() -> None:
    scope = json.loads((FROZEN / "SCOPE.json").read_text(encoding="utf-8"))
    repo = "pymc-devs/pymc"
    prefix = "EXT-pymc-"
    queue = [
        _synthetic_queue_row(repo=repo, order=i, prefix=prefix) for i in range(1, 25)
    ]
    for row in queue:
        row["review_status"] = "PENDING_REVIEW"
    # Rows 1-15 excluded, 16-20 admit → fifth admit and 20-cap tie at index 20.
    decisions = []
    for idx, row in enumerate(queue[:20]):
        decisions.append(build_decision_from_queue_row(row, admit=idx >= 15))
    stop_at, reason = checker.earliest_review_stop(
        decisions, queue_count=len(queue), max_reviewed=20, target_pending=5
    )
    assert (stop_at, reason) == (20, "five_admit_pending_repro")
    assert (
        checker.verify_decisions(scope, queue, {"decisions": decisions}) == decisions
    )
    miner.validate_decisions_payload(scope=scope, queue=queue, decisions=decisions)


def test_out_of_scope_decision_rejected() -> None:
    scope = json.loads((FROZEN / "SCOPE.json").read_text(encoding="utf-8"))
    repo = "pymc-devs/pymc"
    row = _synthetic_queue_row(repo=repo, order=1, prefix="EXT-pymc-")
    ok = build_decision_from_queue_row(row, admit=False)
    bad = dict(ok)
    bad["repository"] = "evil/not-in-scope"
    bad["neutral_id"] = "EXT-evil-01"
    with pytest.raises(checker.AdmissionError, match="out-of-scope decision"):
        checker.verify_decisions(scope, [row], {"decisions": [ok, bad]})
    with pytest.raises(miner.HardFail, match="out_of_scope_decision"):
        miner.validate_decisions_payload(
            scope=scope, queue=[row], decisions=[ok, bad]
        )


def test_empty_queue_decision_rejected() -> None:
    scope = json.loads((FROZEN / "SCOPE.json").read_text(encoding="utf-8"))
    # SALib is in scope; leave its queue empty and inject a decision.
    decision = {
        "neutral_id": "EXT-SALib-01",
        "snapshot_record_id": "SSR2-SALib-1",
        "snapshot_record_sha256": "c" * 64,
        "repository": "SALib/SALib",
        "issue_node_id": "NODE-SALib",
        "issue_number": 1,
        "issue_url": "https://github.com/SALib/SALib/issues/1",
        "repository_review_order": 1,
        "matched_phrases": ["wrong result"],
        "buggy_sha": "",
        "fixed_sha": "",
        "public_issue_url": "https://github.com/SALib/SALib/issues/1",
        "public_fix_url": "",
        "mechanism": "empty-queue injection",
        "exclusion_class": "documentation",
        "crit_real_public_fix": "FAIL",
        "crit_in_numerical_scope": "FAIL",
        "crit_dual_arm_repro": "PENDING",
        "decision": "EXCLUDED",
        "decision_reason": "documentation exclusion class applies.",
        "analysis_id": "",
    }
    with pytest.raises(checker.AdmissionError, match="empty-queue decision"):
        checker.verify_decisions(scope, [], {"decisions": [decision]})
    with pytest.raises(miner.HardFail, match="empty_queue_decision"):
        miner.validate_decisions_payload(
            scope=scope, queue=[], decisions=[decision]
        )


def test_invalid_early_stop_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    repo = "pymc-devs/pymc"
    rows = _repo_rows(root, repo)
    assert len(rows) >= 3
    _rewrite_repo_decisions(
        root,
        repo,
        [
            build_decision_from_queue_row(rows[0], admit=True),
            build_decision_from_queue_row(rows[1], admit=False),
        ],
    )
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
    for row in queue["records"]:
        if row["repository"] != repo:
            continue
        order = int(row["repository_review_order"])
        row["review_status"] = "REVIEWED" if order <= 2 else "NOT_REVIEWED_AFTER_STOP"
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert miner.cmd_validate_decisions(root) != 0
    assert_checker_fails_without_new_mint(root, before)


def test_omitted_reviewed_exclusion_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
    repo = "pymc-devs/pymc"
    rows = [r for r in queue["records"] if r["repository"] == repo]
    _rewrite_repo_decisions(
        root,
        repo,
        [build_decision_from_queue_row(rows[0], admit=True)],
    )
    for row in queue["records"]:
        if row["repository"] != repo:
            continue
        row["review_status"] = (
            "REVIEWED"
            if int(row["repository_review_order"]) <= 2
            else "NOT_REVIEWED_AFTER_STOP"
        )
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert_checker_fails_without_new_mint(root, before)


def test_later_row_substitution_rejected(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    before = present_candidates(root)
    repo = "pymc-devs/pymc"
    rows = _repo_rows(root, repo)
    assert len(rows) >= 3
    decisions = [
        build_decision_from_queue_row(rows[0], admit=True),
        build_decision_from_queue_row(rows[2], admit=False),
        build_decision_from_queue_row(rows[1], admit=False),
    ]
    _rewrite_repo_decisions(root, repo, decisions)
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
    for row in queue["records"]:
        if row["repository"] != repo:
            continue
        row["review_status"] = (
            "REVIEWED"
            if int(row["repository_review_order"]) <= 3
            else "NOT_REVIEWED_AFTER_STOP"
        )
    _write_json(root / "REVIEW_QUEUE.json", queue)
    assert miner.cmd_validate_decisions(root) != 0
    assert_checker_fails_without_new_mint(root, before)


def test_admission_checker_rejects_totals_tamper(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="a1" * 20) == 0
    before = present_candidates(root)
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["decision_totals"]["admit_pending_repro"] = (
        int(handoff["decision_totals"]["admit_pending_repro"]) + 1
    )
    _write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
    assert_checker_fails_without_new_mint(root, before)


def test_admission_checker_rejects_per_repo_tamper(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="a2" * 20) == 0
    before = present_candidates(root)
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    repo = "pymc-devs/pymc"
    handoff["repository_review_counts"][repo]["stop_reason"] = "twenty_reviewed"
    handoff["repository_review_counts"][repo]["reviewed"] += 1
    _write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
    assert_checker_fails_without_new_mint(root, before)


def test_admission_checker_rejects_shortfall_tamper(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, admits_per_quota_repo=1)
    assert miner.cmd_write_handoff(root, payload_commit="a3" * 20) == 0
    before = present_candidates(root)
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["quota_feasibility"]["shortfalls"] = []
    handoff["quota_feasibility"]["status"] = "FEASIBLE"
    _write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
    assert_checker_fails_without_new_mint(root, before)


def test_admission_checker_rejects_confirmation_tamper(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="a4" * 20) == 0
    before = present_candidates(root)
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["confirmations"]["readiness_ran"] = True
    _write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
    assert_checker_fails_without_new_mint(root, before)


def test_handoff_checker_rejects_totals_tamper(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="h1" * 20) == 0
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["decision_totals"]["excluded"] = int(handoff["decision_totals"]["excluded"]) + 2
    path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
    _write_json(path, handoff)
    assert (
        handoff_mod.verify_handoff_hashes(
            path, cwd=root, check_parent=False, git_cwd=ROOT
        )
        != 0
    )


def test_handoff_checker_rejects_per_repo_tamper(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="h2" * 20) == 0
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    repo = "pymc-devs/pymc"
    handoff["repository_review_counts"][repo]["exclusion_class_counts"] = {
        "documentation": 99
    }
    path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
    _write_json(path, handoff)
    assert (
        handoff_mod.verify_handoff_hashes(
            path, cwd=root, check_parent=False, git_cwd=ROOT
        )
        != 0
    )


def test_handoff_checker_rejects_shortfall_tamper(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, admits_per_quota_repo=1)
    assert miner.cmd_write_handoff(root, payload_commit="h3" * 20) == 0
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["quota_feasibility"]["pending_by_repo"] = {}
    path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
    _write_json(path, handoff)
    assert (
        handoff_mod.verify_handoff_hashes(
            path, cwd=root, check_parent=False, git_cwd=ROOT
        )
        != 0
    )


def test_handoff_checker_rejects_confirmation_tamper(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    assert miner.cmd_write_handoff(root, payload_commit="h4" * 20) == 0
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    handoff["confirmations"]["a2_all_pending"] = False
    path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
    _write_json(path, handoff)
    assert (
        handoff_mod.verify_handoff_hashes(
            path, cwd=root, check_parent=False, git_cwd=ROOT
        )
        != 0
    )


def test_sheet_uses_lf_line_endings(tmp_path: Path) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root)
    raw = (root / "admission_sheet.cursor_candidate.csv").read_bytes()
    assert b"\r\n" not in raw
    assert b"\n" in raw


def _copy_live_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Full-chain fixture: copy live supplemental_r2 evidence tree."""
    _use_production_transport_freeze(monkeypatch)
    dest = tmp_path / "supplemental_r2"
    shutil.copytree(FROZEN, dest)
    for name in ("HANDOFF_SUPPLEMENTAL_R2.json", "VERIFICATION_LOG.json"):
        path = dest / name
        if path.exists():
            path.unlink()
    return dest


def _inject_top_level_json_marker(
    path: Path, marker_key: str = "__total_transport_drift__"
) -> None:
    """Fast top-level object marker inject (avoids full dump of large page trees)."""
    path.chmod(path.stat().st_mode | stat.S_IWUSR)
    text = path.read_text(encoding="utf-8")
    brace = text.find("{")
    assert brace >= 0, path
    mutated = (
        text[: brace + 1]
        + json.dumps(marker_key)
        + ": true, "
        + text[brace + 1 :]
    )
    json.loads(mutated)
    path.write_text(mutated, encoding="utf-8")


def _apply_total_transport_drift_attack(root: Path) -> None:
    """Replace all transport outputs and resync internal seals (baseline freeze remains)."""
    marker_key = "__total_transport_drift__"
    page_shas: dict[str, str] = {}
    for path in sorted((root / "transport_pages").glob("*.json")):
        _inject_top_level_json_marker(path, marker_key)
        page_shas[path.relative_to(root).as_posix()] = miner.sha256_file(path)
    for path in (root / "failed_runs").rglob("*"):
        if path.is_file():
            _inject_top_level_json_marker(path, marker_key)
    _inject_top_level_json_marker(root / "COMMAND_LOG.json", marker_key)

    snapshot = json.loads((root / "ISSUE_SNAPSHOT.json").read_text(encoding="utf-8"))
    old_to_new: dict[str, str] = {}
    for man in snapshot["page_manifest"]:
        rel = man["path"]
        new_sha = page_shas[rel]
        old_to_new[str(man["sha256"])] = new_sha
        man["sha256"] = new_sha
    snapshot["page_manifest_sha256"] = miner.canonical_sha256(snapshot["page_manifest"])
    record_fields = [
        "snapshot_record_id",
        "repository",
        "repository_order",
        "issue_node_id",
        "issue_number",
        "issue_url",
        "state",
        "created_at",
        "updated_at",
        "closed_at",
        "title_sha256",
        "body_text_sha256",
        "ordered_labels",
        "matched_phrases",
        "match_surfaces",
        "source_page_index",
        "source_page_sha256",
        "query_document_sha256",
        "variables_sha256",
        "node_index",
    ]
    for rec in snapshot["records"]:
        old_sha = str(rec["source_page_sha256"])
        if old_sha in old_to_new:
            rec["source_page_sha256"] = old_to_new[old_sha]
        body = {key: rec[key] for key in record_fields}
        rec["snapshot_record_sha256"] = miner.canonical_sha256(body)
    snapshot[marker_key] = True
    miner.write_json(root / "ISSUE_SNAPSHOT.json", snapshot)
    publish = miner.build_publish_commit_identity(
        run_id=snapshot["run_id"],
        code_commit=snapshot["code_commit"],
        snapshot=snapshot,
        transport_page_sha256=page_shas,
    )
    miner.write_json(root / "PUBLISH_COMMIT.json", publish)

    # Keep queue/decision bindings consistent with the resealed snapshot hashes.
    scope = json.loads((root / "SCOPE.json").read_text(encoding="utf-8"))
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
    status_by_id = {
        row["neutral_id"]: row.get("review_status", "PENDING_REVIEW")
        for row in queue.get("records") or []
    }
    rebuilt = miner.build_queue_from_snapshot(scope, snapshot)
    for row in rebuilt:
        row["review_status"] = status_by_id.get(row["neutral_id"], "PENDING_REVIEW")
    queue["records"] = rebuilt
    miner.write_json(root / "REVIEW_QUEUE.json", queue)

    snap_hash_by_id = {
        rec["snapshot_record_id"]: rec["snapshot_record_sha256"]
        for rec in snapshot["records"]
    }
    decisions_payload = json.loads(
        (root / "REVIEW_DECISIONS.json").read_text(encoding="utf-8")
    )
    for decision in decisions_payload["decisions"]:
        sid = decision.get("snapshot_record_id")
        if sid in snap_hash_by_id:
            decision["snapshot_record_sha256"] = snap_hash_by_id[sid]
    miner.write_json(root / "REVIEW_DECISIONS.json", decisions_payload)


def _align_queue_statuses(root: Path, decisions: list[dict[str, Any]]) -> None:
    decided = {d["neutral_id"] for d in decisions}
    queue = json.loads((root / "REVIEW_QUEUE.json").read_text(encoding="utf-8"))
    for row in queue["records"]:
        row["review_status"] = (
            "REVIEWED" if row["neutral_id"] in decided else "NOT_REVIEWED_AFTER_STOP"
        )
    _write_json(root / "REVIEW_QUEUE.json", queue)


def _sync_decisions_sheet_evidence_handoff(root: Path) -> None:
    """Fully rebuild sheet/evidence/handoff hashes after decision/queue edits.

    Bypasses producer validation so synchronized illegal payloads can exercise
    checker guards (validation itself is asserted separately).
    """
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text(encoding="utf-8"))
    decisions = payload["decisions"]
    _align_queue_statuses(root, decisions)
    sheet_rows = [miner.sheet_row_from_decision(d) for d in decisions]
    miner.write_sheet(root / "admission_sheet.cursor_candidate.csv", sheet_rows)
    evidence_root = root / "admission_evidence"
    if evidence_root.exists():
        shutil.rmtree(evidence_root)
    evidence_root.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for decision in decisions:
        evidence = miner.evidence_from_decision(decision)
        case_dir = evidence_root / decision["neutral_id"]
        case_dir.mkdir(parents=True, exist_ok=True)
        path = case_dir / "evidence.json"
        miner.write_json(path, evidence)
        rel = f"admission_evidence/{decision['neutral_id']}/evidence.json"
        manifest.append(
            {
                "neutral_id": decision["neutral_id"],
                "path": rel,
                "sha256": miner.sha256_file(path),
            }
        )
    _write_json(
        root / "EVIDENCE_SNAPSHOT.json",
        {
            "schema_version": 1,
            "task": "SUPPLEMENTAL_MINING_R2",
            "records": manifest,
        },
    )
    seal_handoff_bundle(root)


def test_full_chain_after_fifth_admit_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _copy_live_root(tmp_path, monkeypatch)
    repo = "pymc-devs/pymc"
    rows = _repo_rows(root, repo)
    rewritten = [
        build_decision_from_queue_row(row, admit=idx < 5)
        for idx, row in enumerate(rows[:20])
    ]
    _rewrite_repo_decisions(root, repo, rewritten)
    _sync_decisions_sheet_evidence_handoff(root)
    assert miner.cmd_validate_decisions(root) != 0
    both_checkers_fail(root)

    def accept_submitted(
        decisions: list[dict[str, Any]],
        *,
        queue_count: int,
        max_reviewed: int,
        target_pending: int,
    ) -> tuple[int, str]:
        n = len(decisions)
        pending = sum(
            1 for d in decisions if d.get("decision") == "ADMIT_PENDING_REPRO"
        )
        if n >= queue_count:
            return n, "queue_exhausted"
        if n >= max_reviewed:
            return n, "twenty_reviewed"
        if pending >= target_pending:
            return n, "five_admit_pending_repro"
        return n, "queue_exhausted"

    monkeypatch.setattr(checker, "earliest_review_stop", accept_submitted)
    monkeypatch.setattr(handoff_mod, "_earliest_review_stop", accept_submitted)
    monkeypatch.setattr(miner, "earliest_review_stop", accept_submitted)
    # Reseal under the removed guard so summary stop_reason labels stay consistent.
    seal_handoff_bundle(root)
    both_checkers_pass(root)


def test_full_chain_out_of_scope_decision_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    both_checkers_pass(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text(encoding="utf-8"))
    donor = dict(payload["decisions"][0])
    donor["repository"] = "evil/not-in-scope"
    donor["neutral_id"] = "EXT-evil-01"
    payload["decisions"].append(donor)
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    _sync_decisions_sheet_evidence_handoff(root)
    assert miner.cmd_validate_decisions(root) != 0
    both_checkers_fail(root)

    def without_scope_guard(scope, queue, decisions_payload):
        decisions = decisions_payload.get("decisions") or []
        for decision in decisions:
            if decision.get("crit_dual_arm_repro") != "PENDING":
                checker.fail(f"non-PENDING A2 for {decision.get('neutral_id')}")
            if decision.get("analysis_id") not in (None, ""):
                checker.fail(f"nonblank analysis_id for {decision.get('neutral_id')}")
        return decisions

    monkeypatch.setattr(checker, "verify_decisions", without_scope_guard)
    monkeypatch.setattr(handoff_mod, "verify_decision_guards", lambda *a, **k: [])
    both_checkers_pass(root)


def test_full_chain_empty_queue_decision_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    payload = json.loads((root / "REVIEW_DECISIONS.json").read_text(encoding="utf-8"))
    payload["decisions"].append(
        {
            "neutral_id": "EXT-SALib-01",
            "snapshot_record_id": "SSR2-SALib-1",
            "snapshot_record_sha256": "c" * 64,
            "repository": "SALib/SALib",
            "issue_node_id": "NODE-SALib",
            "issue_number": 1,
            "issue_url": "https://github.com/SALib/SALib/issues/1",
            "repository_review_order": 1,
            "matched_phrases": ["wrong result"],
            "buggy_sha": "",
            "fixed_sha": "",
            "public_issue_url": "https://github.com/SALib/SALib/issues/1",
            "public_fix_url": "",
            "mechanism": "excluded as documentation-only report.",
            "exclusion_class": "documentation",
            "crit_real_public_fix": "FAIL",
            "crit_in_numerical_scope": "FAIL",
            "crit_dual_arm_repro": "PENDING",
            "decision": "EXCLUDED",
            "decision_reason": "documentation exclusion class applies.",
            "analysis_id": "",
        }
    )
    _write_json(root / "REVIEW_DECISIONS.json", payload)
    _sync_decisions_sheet_evidence_handoff(root)
    assert miner.cmd_validate_decisions(root) != 0
    both_checkers_fail(root)

    def without_empty_queue_guard(scope, queue, decisions_payload):
        return decisions_payload.get("decisions") or []

    monkeypatch.setattr(checker, "verify_decisions", without_empty_queue_guard)
    monkeypatch.setattr(handoff_mod, "verify_decision_guards", lambda *a, **k: [])
    both_checkers_pass(root)


def test_full_chain_verification_log_missing_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Same-attack VLOG deletion: guard removal alone must make the attack pass."""
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    both_checkers_pass(root)
    (root / "VERIFICATION_LOG.json").unlink()
    # Keep handoff file_sha256 binding identical (still declares the missing log).
    both_checkers_fail(root)

    monkeypatch.setattr(checker, "verify_gate_binding", lambda *a, **k: None)
    monkeypatch.setattr(handoff_mod, "verify_gate_binding", lambda *a, **k: [])
    both_checkers_pass(root)


def test_full_chain_verification_log_hash_tamper_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Same-attack VLOG hash tamper with all other bindings held fixed."""
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    both_checkers_pass(root)
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    # Tamper only the declared hash; leave VERIFICATION_LOG bytes unchanged.
    handoff["file_sha256"]["VERIFICATION_LOG.json"] = "0" * 64
    _write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
    both_checkers_fail(root)

    monkeypatch.setattr(checker, "verify_gate_binding", lambda *a, **k: None)
    monkeypatch.setattr(handoff_mod, "verify_gate_binding", lambda *a, **k: [])
    both_checkers_pass(root)


def test_full_chain_scope_self_tamper_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    both_checkers_pass(root)
    scope = json.loads((root / "SCOPE.json").read_text(encoding="utf-8"))
    scope["unbound_attack_field"] = "tamper"
    _write_json(root / "SCOPE.json", scope)
    seal_handoff_bundle(root)
    both_checkers_fail(root)

    def trust_mutable_scope(
        *,
        root: Path,
        scope: dict[str, Any],
        decisions: list[dict[str, Any]],
        repo_root: Path | None = None,
    ) -> dict[str, bool]:
        repo_root = repo_root or ROOT
        conf = {
            "a2_all_pending": all(
                d.get("crit_dual_arm_repro") == "PENDING" for d in decisions
            ),
            "analysis_id_all_blank": all(
                d.get("analysis_id") in (None, "") for d in decisions
            ),
            "forbidden_data_absent": True,
            "readiness_ran": False,
            "canonical_freeze_claimed": False,
            "existing_files_unchanged": True,
        }
        for rel, expected in (scope.get("input_sha256") or {}).items():
            path = repo_root / rel
            if not path.is_file() or miner.sha256_file(path) != expected:
                conf["existing_files_unchanged"] = False
                break
        return conf

    monkeypatch.setattr(checker, "_compute_confirmations", trust_mutable_scope)
    monkeypatch.setattr(handoff_mod, "_compute_confirmations", trust_mutable_scope)
    monkeypatch.setattr(miner, "compute_confirmations", trust_mutable_scope)
    monkeypatch.setattr(checker, "verify_frozen_inputs", lambda *a, **k: None)
    monkeypatch.setattr(checker, "verify_confirmation_policy", lambda *a, **k: None)
    monkeypatch.setattr(handoff_mod, "verify_confirmation_policy", lambda *a, **k: [])
    seal_handoff_bundle(root)
    both_checkers_pass(root)


@pytest.mark.parametrize(
    "filename",
    [
        "readiness_batch99.json",  # prefix token
        "batch99_readiness.json",  # suffix token
        "foo_readiness_bar.json",  # infix token
        "readiness_supplemental_r2.json",  # sibling sentinel
        "freeze.json",  # bare freeze token
        "freeze_batch99.json",  # prefix freeze token
        "batch99_freeze.json",  # suffix freeze token
        "foo_freeze_bar.json",  # infix freeze token
    ],
)
def test_full_chain_downstream_token_filename_positions_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, filename: str
) -> None:
    """Position-independent downstream token in sibling filenames (same-attack)."""
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    both_checkers_pass(root)
    sibling = root.parent / filename
    sibling.write_text("{}\n", encoding="utf-8")
    # Same attack bytes across fail/pass: reseal only after path guard removal.
    seal_handoff_bundle(root)
    both_checkers_fail(root)

    def no_path_hits(root_path: Path, *, repo_root: Path | None = None):
        del root_path, repo_root
        return False, False, False

    monkeypatch.setattr(checker, "_forbidden_path_scan", no_path_hits)
    monkeypatch.setattr(handoff_mod, "_forbidden_path_scan", no_path_hits)
    monkeypatch.setattr(miner, "_forbidden_path_scan", no_path_hits)
    seal_handoff_bundle(root)
    both_checkers_pass(root)


@pytest.mark.parametrize(
    "filename",
    [
        "prefreeze.json",
        "freezeout.json",
    ],
)
def test_full_chain_non_token_freeze_filename_allowed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, filename: str
) -> None:
    """Substring freeze inside a larger token must not trip the path guard."""
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    both_checkers_pass(root)
    sibling = root.parent / filename
    sibling.write_text("{}\n", encoding="utf-8")
    seal_handoff_bundle(root)
    both_checkers_pass(root)


def test_full_chain_transport_command_log_mutation_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Resealed COMMAND_LOG mutation must fail both checkers until freeze guard drops."""
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    both_checkers_pass(root)
    log = json.loads((root / "COMMAND_LOG.json").read_text(encoding="utf-8"))
    log["unbound_transport_attack"] = "tamper"
    _write_json(root / "COMMAND_LOG.json", log)
    # Reseal so only baseline transport freeze remains as the failing guard.
    seal_handoff_bundle(root)
    both_checkers_fail(root)

    def freeze_ok(root_path: Path, repo_root: Path | None = None) -> bool:
        del root_path, repo_root
        return True

    monkeypatch.setattr(checker, "_transport_freeze_matches_baseline", freeze_ok)
    monkeypatch.setattr(handoff_mod, "_transport_freeze_matches_baseline", freeze_ok)
    monkeypatch.setattr(miner, "_transport_freeze_matches_baseline", freeze_ok)
    seal_handoff_bundle(root)
    both_checkers_pass(root)


def test_full_chain_total_transport_drift_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Full transport output replacement must fail without synthetic fallback."""
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    both_checkers_pass(root)
    _apply_total_transport_drift_attack(root)
    _sync_decisions_sheet_evidence_handoff(root)
    both_checkers_fail(root)

    def freeze_ok(root_path: Path, repo_root: Path | None = None) -> bool:
        del root_path, repo_root
        return True

    monkeypatch.setattr(checker, "_transport_freeze_matches_baseline", freeze_ok)
    monkeypatch.setattr(handoff_mod, "_transport_freeze_matches_baseline", freeze_ok)
    monkeypatch.setattr(miner, "_transport_freeze_matches_baseline", freeze_ok)
    _sync_decisions_sheet_evidence_handoff(root)
    both_checkers_pass(root)


def test_full_chain_verification_log_readiness_command_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    vlog = json.loads((root / "VERIFICATION_LOG.json").read_text(encoding="utf-8"))
    vlog["commands"] = [
        {
            "command": (
                "python3 run_readiness.py --root data/external_slice/supplemental_r2"
            ),
            "cwd": str(ROOT),
            "exit_code": 0,
            "key_output": "READINESS_OK",
            "phase": "payload",
        }
    ]
    _write_json(root / "VERIFICATION_LOG.json", vlog)
    assert miner.cmd_write_handoff(root, payload_commit="r6" * 20) == 0
    both_checkers_fail(root)

    def no_command_hits(root_path: Path):
        del root_path
        return False, False

    monkeypatch.setattr(checker, "_command_sources_sentinel_hits", no_command_hits)
    monkeypatch.setattr(handoff_mod, "_command_sources_sentinel_hits", no_command_hits)
    monkeypatch.setattr(miner, "_command_sources_sentinel_hits", no_command_hits)
    assert miner.cmd_write_handoff(root, payload_commit="r6" * 20) == 0
    both_checkers_pass(root)


def test_full_chain_gate_mismatch_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _copy_live_root(tmp_path, monkeypatch)
    seal_handoff_bundle(root)
    both_checkers_pass(root)
    handoff = json.loads((root / "HANDOFF_SUPPLEMENTAL_R2.json").read_text())
    assert handoff["gate_requested"] == checker.EXPECTED_GATE
    _write_json(
        root / "VERIFICATION_LOG.json",
        {
            "schema_version": 1,
            "task": "SUPPLEMENTAL_MINING_R2",
            "gate_requested": "SUPPLEMENTAL_ADMISSION_R2-r6",
            "commands": [],
        },
    )
    handoff["file_sha256"]["VERIFICATION_LOG.json"] = miner.sha256_file(
        root / "VERIFICATION_LOG.json"
    )
    _write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
    both_checkers_fail(root)

    monkeypatch.setattr(checker, "verify_gate_binding", lambda *a, **k: None)
    monkeypatch.setattr(handoff_mod, "verify_gate_binding", lambda *a, **k: [])
    both_checkers_pass(root)
