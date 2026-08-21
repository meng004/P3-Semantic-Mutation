#!/usr/bin/env python3
"""Admission checker for supplemental mining R1 candidate payload (R1-r4)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, NoReturn

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

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
RESERVED_RE = re.compile(
    r"(?i)(^|[^A-Za-z0-9_])(C\x45|O\x53|H\x50|T\x46|S\x49|f\x69ber|strat\x75m)"
    r"([^A-Za-z0-9_]|$)"
)
PROHIBITED_RE = re.compile(
    r"(?i)(mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|"
    r"\bkill\b|prediction|detection_result|\bfiber\b|\boperator\b)"
)

EVIDENCE_REQUIRED = {
    "neutral_id",
    "source_pool",
    "scope_sha256",
    "search_snapshot_sha256",
    "review_decisions_sha256",
    "issue_url",
    "fix_url",
    "buggy_sha",
    "fixed_sha",
    "criteria",
    "rationales",
    "evidence_urls",
    "mechanism_sentence",
}


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_sheet(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if list(reader.fieldnames or []) != HEADER:
            fail(f"sheet header must be exactly {','.join(HEADER)}")
        return list(reader)


def text_blob_for_row(row: dict[str, str], decision: dict[str, Any] | None = None) -> str:
    parts = [
        row.get("mechanism_sentence", ""),
        row.get("exclusion_reason", ""),
    ]
    if decision:
        parts.append(json.dumps(decision.get("rationales") or {}, sort_keys=True))
        parts.append(decision.get("mechanism_sentence") or "")
        parts.append(decision.get("exclusion_reason") or "")
    return "\n".join(parts)


def verify_input_hashes(scope: dict[str, Any], *, fixture_root: Path | None) -> None:
    root = fixture_root if fixture_root is not None else Path.cwd()
    for rel, expected in scope.get("input_sha256", {}).items():
        path = Path(rel)
        if not path.is_absolute():
            path = root / rel
        if not path.is_file():
            fail(f"missing immutable input for hash check: {rel}")
        actual = sha256_file(path)
        if actual != expected:
            fail(f"changed input hash for {rel}: expected {expected}, got {actual}")
    if scope.get("baseline_commit") != "0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a":
        fail("baseline_commit mismatch in SCOPE.json")


def build_expected_queries(scope: dict[str, Any]) -> list[dict[str, str]]:
    cutoff = scope["created_cutoff"]
    out: list[dict[str, str]] = []
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        for phrase in scope["phrases"]:
            out.append(
                {
                    "repo": repo,
                    "phrase": phrase,
                    "q": f'repo:{repo} is:issue is:closed created:<={cutoff} "{phrase}"',
                }
            )
    return out


def _load_miner_assign_queue():
    path = Path(__file__).resolve().parent / "mine_supplemental_r1.py"
    spec = importlib.util.spec_from_file_location("mine_supplemental_r1_for_checker", path)
    if spec is None or spec.loader is None:
        fail(f"unable to load miner module from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.assign_queue


def bind_item_to_enclosing_query(item: dict[str, Any], query: dict[str, Any]) -> dict[str, Any]:
    """Require item repo/phrase to match the enclosing query; derive exclusively from it."""
    repo = query.get("repo")
    phrase = query.get("phrase")
    item_repo = item.get("repo")
    item_phrase = item.get("phrase")
    if item_repo is not None and item_repo != repo:
        fail(
            f"snapshot item repo {item_repo!r} != enclosing query repo {repo!r} "
            f"for phrase={phrase!r}"
        )
    if item_phrase is not None and item_phrase != phrase:
        fail(
            f"snapshot item phrase {item_phrase!r} != enclosing query phrase "
            f"{phrase!r} for repo={repo!r}"
        )
    cloned = dict(item)
    cloned["repo"] = repo
    cloned["phrase"] = phrase
    return cloned


def reconstruct_queue_records(
    scope: dict[str, Any], snapshot: dict[str, Any]
) -> list[dict[str, Any]]:
    """Mechanically rebuild queue records from snapshot direct issue items."""
    assign_queue = _load_miner_assign_queue()
    hits_by_repo: dict[str, list[dict[str, Any]]] = {
        r["repo"]: [] for r in scope["repositories"]
    }
    allowed = set(hits_by_repo)
    for query in snapshot.get("queries") or []:
        repo = query.get("repo")
        if repo not in allowed:
            fail(f"snapshot repository outside SCOPE repositories list: {repo}")
        for item in query.get("items") or []:
            hits_by_repo[repo].append(bind_item_to_enclosing_query(item, query))
    return assign_queue(scope, hits_by_repo)


def require_queue_snapshot_equality(
    scope: dict[str, Any], snapshot: dict[str, Any], queue: dict[str, Any]
) -> None:
    expected = reconstruct_queue_records(scope, snapshot)
    got = queue.get("records") or []
    if got != expected:
        fail(
            "REVIEW_QUEUE.json records are not exactly equal to the queue "
            "mechanically reconstructed from SEARCH_SNAPSHOT.json items "
            f"(expected_count={len(expected)}, got_count={len(got)})"
        )


def apply_review_stop(
    records: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    *,
    max_reviewed: int,
    target_pending: int,
) -> list[str]:
    decision_by_id = {d["neutral_id"]: d for d in decisions}
    pending = 0
    reviewed_ids: list[str] = []
    for record in records:
        if pending >= target_pending or len(reviewed_ids) >= max_reviewed:
            break
        reviewed_ids.append(record["neutral_id"])
        if decision_by_id.get(record["neutral_id"], {}).get("decision") == "ADMIT_PENDING_REPRO":
            pending += 1
        # Stop after appending the decision that reaches the quota.
        if pending >= target_pending or len(reviewed_ids) >= max_reviewed:
            break
    return reviewed_ids


def require_cross_artifact_field_equality(
    *,
    nid: str,
    qrec: dict[str, Any],
    decision: dict[str, Any],
    row: dict[str, str],
    evidence: dict[str, Any],
) -> None:
    """Require exact equality for every duplicated field across artifacts."""
    if qrec.get("neutral_id") != nid or decision.get("neutral_id") != nid:
        fail(f"{nid}: neutral_id mismatch across queue/decision")
    if evidence.get("neutral_id") != nid:
        fail(f"{nid}: evidence neutral_id mismatch")

    if qrec.get("repo") != decision.get("repo"):
        fail(f"{nid}: queue/decision repository mismatch")
    repo_short = decision["repo"].split("/")[-1]
    if row.get("repo") not in {repo_short, decision["repo"]}:
        fail(f"{nid}: sheet/decision repository mismatch")

    if int(qrec.get("issue_number")) != int(decision.get("issue_number")):
        fail(f"{nid}: queue/decision issue_number mismatch")
    sheet_issue = int(str(row.get("issue_url") or "").rstrip("/").rsplit("/", 1)[-1])
    if sheet_issue != int(decision.get("issue_number")):
        fail(f"{nid}: sheet/decision issue_number mismatch")

    if qrec.get("issue_url") != decision.get("issue_url") or qrec.get("issue_url") != row.get(
        "issue_url"
    ):
        fail(f"{nid}: queue/decision/sheet issue_url mismatch")
    if evidence.get("issue_url") != row.get("issue_url"):
        fail(f"{nid}: evidence/sheet issue_url mismatch")

    if (decision.get("fix_url") or "") != (evidence.get("fix_url") or ""):
        fail(f"{nid}: decision/evidence fix_url mismatch")

    for field in ("buggy_sha", "fixed_sha", "mechanism_sentence", "decision", "exclusion_reason"):
        if (row.get(field) or "") != (decision.get(field) or ""):
            fail(f"{nid}: sheet/decision {field} mismatch")
    for field in ("buggy_sha", "fixed_sha", "mechanism_sentence"):
        if (row.get(field) or "") != (evidence.get(field) or ""):
            fail(f"{nid}: sheet/evidence {field} mismatch")

    for sheet_key, crit_key in (
        ("crit_real_defect", "real_defect"),
        ("crit_dual_arm_repro", "dual_arm_repro"),
        ("crit_in_scope", "in_scope"),
    ):
        if row.get(sheet_key) != decision.get(sheet_key):
            fail(f"{nid}: sheet/decision {sheet_key} mismatch")
        criteria = evidence.get("criteria") or {}
        if row.get(sheet_key) != criteria.get(crit_key):
            fail(f"{nid}: sheet/evidence criteria.{crit_key} mismatch")

    if (row.get("analysis_id") or "") != (decision.get("analysis_id") or ""):
        fail(f"{nid}: sheet/decision analysis_id mismatch")

    if decision.get("rationales") != evidence.get("rationales"):
        fail(f"{nid}: decision/evidence rationales mismatch")
    if decision.get("evidence_urls") != evidence.get("evidence_urls"):
        fail(f"{nid}: decision/evidence evidence_urls mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--existing-sheet", type=Path, required=True)
    parser.add_argument("--pilot-sheet", type=Path, required=True)
    parser.add_argument("--fixture-root", type=Path, default=None)
    args = parser.parse_args()

    scope = load_json(args.scope)
    snapshot = load_json(args.snapshot)
    queue = load_json(args.queue)
    decisions_payload = load_json(args.decisions)
    decisions = decisions_payload.get("decisions") or []
    rows = read_sheet(args.sheet)
    existing = read_sheet(args.existing_sheet)
    pilot = read_sheet(args.pilot_sheet)

    verify_input_hashes(scope, fixture_root=args.fixture_root)

    scope_sha = sha256_file(args.scope)
    search_sha = sha256_file(args.snapshot)
    queue_sha = sha256_file(args.queue)
    decisions_sha = sha256_file(args.decisions)

    if snapshot.get("scope_sha256") != scope_sha:
        fail("snapshot scope_sha256 does not match SCOPE.json")
    if queue.get("scope_sha256") != scope_sha:
        fail("queue scope_sha256 does not match SCOPE.json")
    if queue.get("search_snapshot_sha256") != search_sha:
        fail("queue search_snapshot_sha256 does not match SEARCH_SNAPSHOT.json")

    expected_queries = build_expected_queries(scope)
    got_queries = snapshot.get("queries") or []
    if len(got_queries) != len(expected_queries):
        fail(
            "snapshot query count differs from SCOPE cartesian product "
            f"(missing or duplicate query; expected {len(expected_queries)}, "
            f"got {len(got_queries)})"
        )
    phrases = set(scope["phrases"])
    allowed_repos = {r["repo"] for r in scope["repositories"]}
    seen_query_keys: set[tuple[str, str, str]] = set()
    for exp, got in zip(expected_queries, got_queries):
        if got.get("repo") not in allowed_repos:
            fail(f"snapshot repository outside SCOPE: {got.get('repo')}")
        if got.get("phrase") not in phrases:
            fail(f"snapshot phrase outside SCOPE: {got.get('phrase')}")
        if (
            got.get("repo") != exp["repo"]
            or got.get("phrase") != exp["phrase"]
            or got.get("q") != exp["q"]
        ):
            fail(f"snapshot query identity/order mismatch for {exp}")
        key = (got.get("repo") or "", got.get("phrase") or "", got.get("q") or "")
        if key in seen_query_keys:
            fail(f"duplicate snapshot query for {key}")
        seen_query_keys.add(key)
        if got.get("incomplete_results") is True:
            fail(f"incomplete_results in snapshot for {exp['repo']}/{exp['phrase']}")
        if int(got.get("pull_count") or 0) != 0:
            fail(f"pull_count nonzero in snapshot for {exp['repo']}/{exp['phrase']}")
        for item in got.get("items") or []:
            if item.get("state") != "closed":
                fail(f"non-closed item in snapshot: {item.get('issue_url')}")
            url = item.get("issue_url") or item.get("html_url") or ""
            if "/pull/" in url or item.get("is_pull_request") is True:
                fail(f"PR item in snapshot: {url}")
            # Explicit item↔query binding; reject tampered phrase/repo provenance.
            bind_item_to_enclosing_query(item, got)

    # Mechanical snapshot → queue reconstruction with exact record equality.
    require_queue_snapshot_equality(scope, snapshot, queue)

    prefix_by_repo = {r["repo"]: r["id_prefix"] for r in scope["repositories"]}
    allowed_short = {r["repo"].split("/")[-1] for r in scope["repositories"]}
    existing_ids = {r["neutral_id"] for r in existing} | {r["neutral_id"] for r in pilot}
    existing_urls = {r["issue_url"] for r in existing} | {r["issue_url"] for r in pilot}
    existing_pairs = {
        (r["issue_url"], r["buggy_sha"], r["fixed_sha"])
        for r in existing + pilot
        if r.get("buggy_sha") and r.get("fixed_sha")
    }

    queue_by_id = {r["neutral_id"]: r for r in queue.get("records") or []}
    decision_by_id = {d["neutral_id"]: d for d in decisions}
    if len(decision_by_id) != len(decisions):
        fail("duplicate neutral_id in decisions")
    if {r["neutral_id"] for r in rows} != set(decision_by_id):
        fail("sheet rows and decisions are not 1:1")

    # Queue-head / order binding per repository.
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        repo_queue = [r for r in queue.get("records") or [] if r["repo"] == repo]
        repo_decisions = sorted(
            [d for d in decisions if d["repo"] == repo],
            key=lambda d: d["review_order"],
        )
        expected_reviewed = apply_review_stop(
            repo_queue,
            repo_decisions,
            max_reviewed=int(scope["max_reviewed_per_repo"]),
            target_pending=int(scope["target_pending_per_repo"]),
        )
        got_reviewed = [d["neutral_id"] for d in repo_decisions]
        if got_reviewed != expected_reviewed:
            fail(
                f"{repo}: decisions are not the exact reviewed queue-head prefix "
                f"(expected {expected_reviewed}, got {got_reviewed})"
            )
        for index, decision in enumerate(repo_decisions, start=1):
            if int(decision["review_order"]) != index:
                fail(
                    f"{decision['neutral_id']}: review_order "
                    f"{decision['review_order']} != {index}"
                )

    pending_by_repo: Counter[str] = Counter()
    reviewed_by_repo: Counter[str] = Counter()
    excluded_by_repo: Counter[str] = Counter()
    seen_urls: set[str] = set()
    seen_pairs: set[tuple[str, str, str]] = set()

    for row in rows:
        nid = row["neutral_id"]
        decision = decision_by_id[nid]
        qrec = queue_by_id.get(nid)
        if qrec is None:
            fail(f"{nid}: sheet/decision row missing from queue")

        evidence_path = args.evidence_root / nid / "evidence.json"
        if not evidence_path.is_file():
            fail(f"{nid}: sheet row without a matching evidence record")
        payload = load_json(evidence_path)
        if not EVIDENCE_REQUIRED.issubset(set(payload)):
            fail(f"{nid}: evidence record missing required keys")

        require_cross_artifact_field_equality(
            nid=nid,
            qrec=qrec,
            decision=decision,
            row=row,
            evidence=payload,
        )

        repo_full = decision["repo"]
        repo_short = row["repo"]
        if repo_full not in allowed_repos:
            fail(f"{nid}: repository outside SCOPE")
        if repo_short not in allowed_short and repo_short not in allowed_repos:
            fail(f"{nid}: sheet repo not in SCOPE")
        if not nid.startswith(prefix_by_repo[repo_full]):
            fail(f"{nid}: neutral_id prefix mismatch")
        if nid in existing_ids:
            fail(f"{nid}: neutral-ID collision with existing admission sheet")
        if row["issue_url"] in existing_urls or row["issue_url"] in seen_urls:
            fail(f"{nid}: duplicate issue URL across pools")
        seen_urls.add(row["issue_url"])

        if row["crit_dual_arm_repro"] != "PENDING" or decision["crit_dual_arm_repro"] != "PENDING":
            fail(f"{nid}: A2 must remain PENDING")
        if row["analysis_id"] != "" or decision.get("analysis_id") != "":
            fail(f"{nid}: analysis_id must be blank")

        if row["decision"] == "ADMIT_PENDING_REPRO":
            if row["crit_real_defect"] != "PASS" or row["crit_in_scope"] != "PASS":
                fail(f"{nid}: ADMIT_PENDING_REPRO unless A1 and A3 both PASS")
            if not FULL_SHA.fullmatch(row["buggy_sha"] or ""):
                fail(f"{nid}: buggy_sha must be a full 40-character commit")
            if not FULL_SHA.fullmatch(row["fixed_sha"] or ""):
                fail(f"{nid}: fixed_sha must be a full 40-character commit")
            if not row["issue_url"] or not decision.get("fix_url"):
                fail(f"{nid}: missing public issue and fix URLs on an A1 PASS row")
            pending_by_repo[repo_full] += 1
        elif row["decision"] == "EXCLUDED":
            excluded_by_repo[repo_full] += 1
        else:
            fail(f"{nid}: invalid decision")

        if row["crit_real_defect"] == "PASS":
            if not FULL_SHA.fullmatch(row["buggy_sha"] or "") or not FULL_SHA.fullmatch(
                row["fixed_sha"] or ""
            ):
                fail(f"{nid}: missing full buggy/fixed SHAs on an A1 PASS row")

        blob = text_blob_for_row(row, decision)
        if RESERVED_RE.search(blob):
            fail(f"{nid}: reserved vocabulary in mechanism/rationale")
        if PROHIBITED_RE.search(blob):
            fail(f"{nid}: prohibited downstream vocabulary in mechanism/rationale")

        buggy = (row.get("buggy_sha") or "").strip()
        fixed = (row.get("fixed_sha") or "").strip()
        if buggy and fixed:
            pair = (row["issue_url"], buggy, fixed)
            if pair in existing_pairs or pair in seen_pairs:
                fail(f"{nid}: duplicate nonblank buggy/fixed pair across any pool")
            seen_pairs.add(pair)

        if payload.get("source_pool") != "supplemental_mining_r1":
            fail(f"{nid}: source_pool must be supplemental_mining_r1")
        if payload.get("scope_sha256") != scope_sha:
            fail(f"{nid}: evidence scope hash mismatch")
        if payload.get("search_snapshot_sha256") != search_sha:
            fail(f"{nid}: evidence search hash mismatch")
        if payload.get("review_decisions_sha256") != decisions_sha:
            fail(f"{nid}: evidence decision hash mismatch")
        reviewed_by_repo[repo_full] += 1

    for repo, count in pending_by_repo.items():
        if count > int(scope["target_pending_per_repo"]):
            fail(f"{repo}: more than five pending rows ({count})")
    for repo, count in reviewed_by_repo.items():
        if count > int(scope["max_reviewed_per_repo"]):
            fail(f"{repo}: more than 20 reviewed rows ({count})")
    if len(rows) != len(decisions):
        fail("loss of reviewed exclusion: sheet/decision count mismatch")

    searched = Counter()
    for query in snapshot.get("queries", []):
        searched[query.get("repo")] += int(query.get("returned") or 0)

    print("PASS: supplemental mining R1 admission structural check (full binding)")
    print(
        json.dumps(
            {
                "queue_sha256": queue_sha,
                "searched_hits": dict(searched),
                "reviewed": dict(reviewed_by_repo),
                "pending": dict(pending_by_repo),
                "excluded": dict(excluded_by_repo),
                "rows": len(rows),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
