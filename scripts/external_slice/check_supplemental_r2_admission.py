#!/usr/bin/env python3
"""Field-level binding checker for supplemental mining R2 admission artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, NoReturn

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_GATE = "SUPPLEMENTAL_ADMISSION_R2-r7"
TRANSPORT_BASELINE_COMMIT = "020b60fb83f7eb1d34f143458fca62beab5aa398"
TRANSPORT_BASELINE_PREFIX = "data/external_slice/supplemental_r2"
TRANSPORT_FREEZE_FILES = (
    "SCOPE.json",
    "TRANSPORT_CONTRACT.json",
    "QUOTAS.json",
    "ISSUE_SNAPSHOT.json",
    "COMMAND_LOG.json",
    "PUBLISH_COMMIT.json",
)
TRANSPORT_FREEZE_TREES = (
    "transport_pages",
    "failed_runs",
)
PROHIBITED_VOCAB_RE = re.compile(
    r"(?i)(mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|"
    r"\bkill\b|prediction|detection_result|\bfiber\b|\boperator\b|"
    r"(^|[^A-Za-z0-9_])(CE|OS|HP|TF|SI|fiber|stratum)([^A-Za-z0-9_]|$))"
)
DOWNSTREAM_SENTINEL_RE = re.compile(
    r"(?i)("
    r"readiness|"
    r"\bcanonical_freeze\b|"
    r"\bcanonical-freeze\b|"
    r"\bannotation\b|"
    r"\bprediction\b|"
    r"\bdetection_result\b|"
    r"\bdetection-result\b"
    r")"
)
FORBIDDEN_PATH_NAME_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9])("
    r"readiness|canonical_freeze|canonical-freeze|freeze|"
    r"annotation|prediction|detection"
    r")(?![A-Za-z0-9])"
)

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

QUEUE_COPIED = [
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
]

DECISION_COPIED = [
    "neutral_id",
    "snapshot_record_id",
    "snapshot_record_sha256",
    "repository",
    "issue_node_id",
    "issue_number",
    "issue_url",
    "repository_review_order",
    "matched_phrases",
]

SHEET_BOUND = [
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
]

EVIDENCE_BOUND = [
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
]


class AdmissionError(Exception):
    pass


def fail(message: str) -> NoReturn:
    raise AdmissionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_miner():
    path = Path(__file__).resolve().parent / "mine_supplemental_r2.py"
    spec = importlib.util.spec_from_file_location("mine_supplemental_r2_for_checker", path)
    if spec is None or spec.loader is None:
        fail(f"unable to load miner from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_sheet(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if list(reader.fieldnames or []) != SHEET_HEADER:
            fail(f"sheet header mismatch: {reader.fieldnames}")
        return list(reader)


def verify_frozen_inputs(root: Path, scope: dict[str, Any]) -> None:
    for name in ("SCOPE.json", "TRANSPORT_CONTRACT.json", "QUOTAS.json"):
        if not (root / name).is_file():
            fail(f"missing frozen file {name}")
    repo_root = Path(__file__).resolve().parents[2]
    if not _baseline_contract_files_match(root, repo_root):
        fail(
            "immutable contract files drifted from transport baseline "
            f"{TRANSPORT_BASELINE_COMMIT}"
        )
    transport = load_json(root / "TRANSPORT_CONTRACT.json")
    quotas = load_json(root / "QUOTAS.json")
    if scope.get("task") != "SUPPLEMENTAL_MINING_R2":
        fail("SCOPE task mismatch")
    if transport.get("task") != "SUPPLEMENTAL_MINING_R2":
        fail("TRANSPORT_CONTRACT task mismatch")
    if quotas.get("task") != "SUPPLEMENTAL_MINING_R2":
        fail("QUOTAS task mismatch")
    doc = transport.get("query_document") or ""
    if hashlib.sha256(doc.encode("utf-8")).hexdigest() != transport.get(
        "query_document_sha256"
    ):
        fail("query_document_sha256 drift")
    if transport.get("transport") != "github_graphql_repository_issues":
        fail("forbidden transport in contract")
    # Quota immutability checks against expected frozen shape.
    starting = quotas.get("starting_state") or {}
    if starting.get("accepted_ready_defects") != 18:
        fail("changed starting accepted_ready_defects")
    if starting.get("qualifying_projects") != 2:
        fail("changed starting qualifying_projects")
    order = quotas.get("readiness_quota_order") or []
    expected_repos = [
        "pymc-devs/pymc",
        "cornellius-gp/gpytorch",
        "jonathf/chaospy",
        "SALib/SALib",
        "pytorch/pytorch",
        "jax-ml/jax",
    ]
    if [e.get("repo") for e in order] != expected_repos:
        fail("quota repository order/replacement drift")
    expected_targets = [3, 3, 3, 3, 0, 0]
    if [int(e.get("additional_ready_target")) for e in order] != expected_targets:
        fail("quota target values changed")
    if quotas.get("replacement_policy") != "forbidden":
        fail("replacement_policy must be forbidden")
    projection = quotas.get("projection_if_quotas_met") or {}
    if int(projection.get("qualifying_projects", -1)) != 6:
        fail("incorrect J projection")
    if int(projection.get("ready_defects_lower_bound", -1)) != 30:
        fail("incorrect n projection")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_match_text(text: str) -> str:
    """Checker-owned NFC/casefold normalization for phrase surfaces."""
    return unicodedata.normalize("NFC", text or "").casefold()


def parse_created_at(value: str) -> datetime:
    # Python 3.11+ accepts trailing Z; keep checker-local and ruff-clean.
    return datetime.fromisoformat(value)


def validate_raw_issue_node(node: Any, *, repository: str) -> dict[str, Any]:
    """Independently enforce Issue shape, CLOSED state, URL, and complete labels."""
    if not isinstance(node, dict):
        fail(f"{repository}: raw node is not an object")
    typename = node.get("__typename")
    if typename != "Issue":
        fail(f"{repository}: typename not Issue: got {typename!r}")
    state = node.get("state")
    if state != "CLOSED":
        fail(f"{repository}: state not CLOSED: got {state!r}")
    closed_at = node.get("closedAt")
    if closed_at in (None, ""):
        fail(f"{repository}: closedAt missing/empty for issue {node.get('number')}")
    number = node.get("number")
    if not isinstance(number, int):
        fail(f"{repository}: issue number missing or non-int")
    if "/" not in repository:
        fail(f"{repository}: bad repository identity")
    owner, name = repository.split("/", 1)
    expected_url = f"https://github.com/{owner}/{name}/issues/{number}"
    url = node.get("url") or ""
    if url != expected_url or "/pull/" in url:
        fail(
            f"{repository}: canonical URL mismatch: got {url!r} expected {expected_url!r}"
        )
    for required in (
        "id",
        "title",
        "bodyText",
        "createdAt",
        "updatedAt",
        "closedAt",
    ):
        if required not in node or node[required] is None:
            fail(f"{repository}#{number}: missing required field {required}")
    if "labels" not in node or not isinstance(node["labels"], dict):
        fail(f"{repository}#{number}: labels must be an object")
    labels = node["labels"]
    if "pageInfo" not in labels or not isinstance(labels["pageInfo"], dict):
        fail(f"{repository}#{number}: labels.pageInfo must be an object")
    page_info = labels["pageInfo"]
    if "hasNextPage" not in page_info or page_info["hasNextPage"] is not False:
        fail(
            f"{repository}#{number}: incomplete labels "
            f"(hasNextPage must be false, got {page_info.get('hasNextPage')!r})"
        )
    label_nodes = labels.get("nodes")
    if not isinstance(label_nodes, list):
        fail(f"{repository}#{number}: labels.nodes missing")
    for lab in label_nodes:
        if not isinstance(lab, dict) or "name" not in lab:
            fail(f"{repository}#{number}: incomplete label entry")
    return node


def match_surfaces(issue: dict[str, Any], phrase: str) -> list[str]:
    """Checker-owned phrase surface matching over title/body/labels."""
    norm_phrase = normalize_match_text(phrase)
    surfaces: list[str] = []
    if norm_phrase in normalize_match_text(issue.get("title") or ""):
        surfaces.append("title")
    if norm_phrase in normalize_match_text(issue.get("bodyText") or ""):
        surfaces.append("body")
    for lab in (issue.get("labels") or {}).get("nodes") or []:
        name = lab.get("name") or ""
        if norm_phrase in normalize_match_text(name):
            surfaces.append(f"label:{name}")
    return surfaces


def build_snapshot_record(
    *,
    repository: str,
    repository_order: int,
    issue: dict[str, Any],
    matched_phrases: list[str],
    match_surfaces_map: dict[str, list[str]],
    source_page_index: int,
    source_page_sha256: str,
    query_document_sha256: str,
    variables_sha256: str,
    node_index: int,
    record_index: int,
) -> dict[str, Any]:
    """Checker-owned snapshot record construction and hashing."""
    ordered_labels = [
        lab["name"] for lab in (issue.get("labels") or {}).get("nodes") or []
    ]
    base = {
        "snapshot_record_id": f"SSR2-{repository_order:02d}-{record_index:04d}",
        "repository": repository,
        "repository_order": repository_order,
        "issue_node_id": issue["id"],
        "issue_number": int(issue["number"]),
        "issue_url": issue["url"],
        "state": issue["state"],
        "created_at": issue["createdAt"],
        "updated_at": issue["updatedAt"],
        "closed_at": issue["closedAt"],
        "title_sha256": sha256_text(issue.get("title") or ""),
        "body_text_sha256": sha256_text(issue.get("bodyText") or ""),
        "ordered_labels": ordered_labels,
        "matched_phrases": list(matched_phrases),
        "match_surfaces": {
            p: list(match_surfaces_map.get(p, [])) for p in matched_phrases
        },
        "source_page_index": source_page_index,
        "source_page_sha256": source_page_sha256,
        "query_document_sha256": query_document_sha256,
        "variables_sha256": variables_sha256,
        "node_index": node_index,
    }
    base["snapshot_record_sha256"] = canonical_sha256(base)
    return base


def select_phrase_union(
    *,
    scope: dict[str, Any],
    repository: str,
    repository_order: int,
    issues_with_meta: list[dict[str, Any]],
    query_document_sha256: str,
) -> list[dict[str, Any]]:
    """Checker-owned cutoff, per-phrase top-20, dedupe, ordering, and IDs."""
    cutoff = parse_created_at(scope["created_cutoff"])
    max_per_phrase = int(scope["max_results_per_phrase"])
    phrases: list[str] = list(scope["phrases"])

    eligible: list[dict[str, Any]] = []
    for item in issues_with_meta:
        created = parse_created_at(item["issue"]["createdAt"])
        if created > cutoff:
            continue
        eligible.append(item)

    phrase_lists: dict[str, list[dict[str, Any]]] = {p: [] for p in phrases}
    for item in eligible:
        issue = item["issue"]
        for phrase in phrases:
            surfaces = match_surfaces(issue, phrase)
            if not surfaces:
                continue
            bucket = phrase_lists[phrase]
            if len(bucket) >= max_per_phrase:
                continue
            bucket.append({**item, "match_surfaces_for_phrase": surfaces})

    by_url: dict[str, dict[str, Any]] = {}
    for phrase in phrases:
        for item in phrase_lists[phrase]:
            url = item["issue"]["url"]
            if url not in by_url:
                by_url[url] = {
                    "item": item,
                    "matched_phrases": [],
                    "match_surfaces": {},
                }
            entry = by_url[url]
            if phrase not in entry["matched_phrases"]:
                entry["matched_phrases"].append(phrase)
            entry["match_surfaces"][phrase] = list(item["match_surfaces_for_phrase"])

    ordered = sorted(
        by_url.values(),
        key=lambda e: (
            e["item"]["issue"]["createdAt"],
            int(e["item"]["issue"]["number"]),
        ),
        reverse=True,
    )

    records: list[dict[str, Any]] = []
    for idx, entry in enumerate(ordered, start=1):
        item = entry["item"]
        matched = [p for p in phrases if p in entry["matched_phrases"]]
        records.append(
            build_snapshot_record(
                repository=repository,
                repository_order=repository_order,
                issue=item["issue"],
                matched_phrases=matched,
                match_surfaces_map=entry["match_surfaces"],
                source_page_index=item["source_page_index"],
                source_page_sha256=item["source_page_sha256"],
                query_document_sha256=query_document_sha256,
                variables_sha256=item["variables_sha256"],
                node_index=item["node_index"],
                record_index=idx,
            )
        )
    return records


def reconstruct_snapshot_records_from_raw_pages(
    root: Path,
    *,
    scope: dict[str, Any],
    snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    """Rebuild ordered snapshot records from hash-bound pages without producer builders."""
    manifest = snapshot.get("page_manifest") or []
    if not isinstance(manifest, list) or not manifest:
        fail("snapshot page_manifest missing for reconstruction")
    query_sha = snapshot.get("query_document_sha256")
    if not isinstance(query_sha, str) or not query_sha:
        fail("snapshot query_document_sha256 missing for reconstruction")

    by_repo: dict[str, list[dict[str, Any]]] = {}
    for man in manifest:
        repo = str(man.get("repository"))
        by_repo.setdefault(repo, []).append(man)

    reconstructed: list[dict[str, Any]] = []
    for repo_entry in scope["repositories"]:
        repo = str(repo_entry["repo"])
        mans = by_repo.get(repo, [])
        issues_with_meta: list[dict[str, Any]] = []
        for man in mans:
            rel = man.get("path")
            if not isinstance(rel, str):
                fail(f"{repo}: manifest path missing")
            page_path = root / rel
            if not page_path.is_file():
                fail(f"{repo}: missing raw page {rel}")
            actual_sha = sha256_file(page_path)
            if actual_sha != man.get("sha256"):
                fail(f"{repo}: raw page sha256 drift for {rel}")
            payload = load_json(page_path)
            issues = _raw_issues_connection(payload)
            nodes = issues.get("nodes")
            if not isinstance(nodes, list):
                fail(f"{repo}: raw page nodes missing in {rel}")
            if len(nodes) != int(man.get("node_count", -1)):
                fail(f"{repo}: raw node_count drift in {rel}")
            page_index = int(man["page_index"])
            variables_sha = man.get("variables_sha256")
            if not isinstance(variables_sha, str):
                fail(f"{repo}: variables_sha256 missing in manifest page {page_index}")
            for node_index, node in enumerate(nodes):
                issue = validate_raw_issue_node(node, repository=repo)
                issues_with_meta.append(
                    {
                        "issue": issue,
                        "source_page_index": page_index,
                        "source_page_sha256": man["sha256"],
                        "variables_sha256": variables_sha,
                        "node_index": node_index,
                    }
                )
        records = select_phrase_union(
            scope=scope,
            repository=repo,
            repository_order=int(repo_entry["order"]),
            issues_with_meta=issues_with_meta,
            query_document_sha256=query_sha,
        )
        reconstructed.extend(records)
    return reconstructed


def verify_snapshot_bound_to_raw_pages(
    root: Path,
    *,
    scope: dict[str, Any],
    snapshot: dict[str, Any],
) -> None:
    """Exact field/order/cardinality compare vs independent raw-page reconstruction."""
    expected = reconstruct_snapshot_records_from_raw_pages(
        root, scope=scope, snapshot=snapshot
    )
    got = snapshot.get("records")
    if not isinstance(got, list):
        fail("snapshot records missing")
    if len(got) != len(expected):
        fail(
            f"snapshot cardinality mismatch: reconstructed={len(expected)} "
            f"committed={len(got)}"
        )
    for idx, (exp, rec) in enumerate(zip(expected, got)):
        if not isinstance(rec, dict):
            fail(f"snapshot record[{idx}] is not an object")
        if exp == rec:
            continue
        exp_keys = sorted(exp)
        got_keys = sorted(rec)
        if exp_keys != got_keys:
            fail(
                f"snapshot record[{idx}] key mismatch: "
                f"expected_keys={exp_keys} got_keys={got_keys}"
            )
        for key in exp_keys:
            if exp.get(key) != rec.get(key):
                fail(
                    f"snapshot record[{idx}] field mismatch on {key}: "
                    f"reconstructed={exp.get(key)!r} committed={rec.get(key)!r}"
                )
        fail(f"snapshot record[{idx}] mismatch without field delta")


def verify_snapshot_records(scope: dict[str, Any], snapshot: dict[str, Any]) -> None:
    records = snapshot.get("records") or []
    if not isinstance(records, list):
        fail("snapshot records missing")
    seen_urls: set[str] = set()
    seen_ids: set[str] = set()
    phrases = list(scope["phrases"])
    for rec in records:
        required = [
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
            "snapshot_record_sha256",
        ]
        for field in required:
            if field not in rec:
                fail(f"snapshot missing field {field}")
        body = {k: rec[k] for k in required if k != "snapshot_record_sha256"}
        actual = canonical_sha256(body)
        if actual != rec["snapshot_record_sha256"]:
            fail(f"snapshot_record_sha256 mismatch for {rec['snapshot_record_id']}")
        if rec["state"] != "CLOSED":
            fail(f"snapshot state not CLOSED: {rec['snapshot_record_id']}")
        if "/pull/" in rec["issue_url"]:
            fail(f"pull URL in snapshot: {rec['issue_url']}")
        if rec["issue_url"] in seen_urls:
            fail(f"duplicate snapshot URL {rec['issue_url']}")
        if rec["issue_node_id"] in seen_ids:
            fail(f"duplicate snapshot node {rec['issue_node_id']}")
        seen_urls.add(rec["issue_url"])
        seen_ids.add(rec["issue_node_id"])
        matched = rec["matched_phrases"]
        if matched != [p for p in phrases if p in matched]:
            fail(f"phrase order wrong for {rec['snapshot_record_id']}")
        if not matched:
            fail(f"empty matched_phrases for {rec['snapshot_record_id']}")
        surfaces = rec["match_surfaces"]
        for phrase in matched:
            if phrase not in surfaces or not surfaces[phrase]:
                fail(f"match surface missing for {phrase}")
        repo_ok = any(r["repo"] == rec["repository"] for r in scope["repositories"])
        if not repo_ok:
            fail(f"repository outside scope: {rec['repository']}")


def verify_run_code_binding(root: Path, snapshot: dict[str, Any]) -> tuple[str, str]:
    """Field-by-field run_id/code_commit consistency across owner artifacts."""
    run_id = snapshot.get("run_id")
    code_commit = snapshot.get("code_commit")
    if not isinstance(run_id, str) or not run_id.strip():
        fail("snapshot missing run_id")
    if not isinstance(code_commit, str) or not FULL_SHA.fullmatch(code_commit):
        fail(f"snapshot illegal code_commit: {code_commit!r}")

    log_path = root / "COMMAND_LOG.json"
    if not log_path.is_file():
        fail("COMMAND_LOG.json missing")
    log = load_json(log_path)
    if log.get("run_id") != run_id:
        fail(
            f"command log run_id mismatch: log={log.get('run_id')!r} "
            f"snapshot={run_id!r}"
        )
    if log.get("code_commit") != code_commit:
        fail(
            f"command log code_commit mismatch: log={log.get('code_commit')!r} "
            f"snapshot={code_commit!r}"
        )
    entries = log.get("entries")
    if not isinstance(entries, list):
        fail("command log entries must be a list")
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"command log entry[{idx}] is not an object")
        if entry.get("run_id") != run_id:
            fail(
                f"command log entry[{idx}] run_id mismatch: "
                f"{entry.get('run_id')!r} != {run_id!r}"
            )
        if entry.get("code_commit") != code_commit:
            fail(
                f"command log entry[{idx}] code_commit mismatch: "
                f"{entry.get('code_commit')!r} != {code_commit!r}"
            )

    queue_path = root / "REVIEW_QUEUE.json"
    if not queue_path.is_file():
        fail("REVIEW_QUEUE.json missing")
    queue = load_json(queue_path)
    if queue.get("run_id") != run_id:
        fail(
            f"queue run_id mismatch: queue={queue.get('run_id')!r} "
            f"snapshot={run_id!r}"
        )
    if queue.get("code_commit") != code_commit:
        fail(
            f"queue code_commit mismatch: queue={queue.get('code_commit')!r} "
            f"snapshot={code_commit!r}"
        )

    publish_path = root / "PUBLISH_COMMIT.json"
    if not publish_path.is_file():
        fail("PUBLISH_COMMIT.json missing; sequential artifacts are incomplete")
    publish = load_json(publish_path)
    if publish.get("run_id") != run_id:
        fail(
            f"publish commit run_id mismatch: publish={publish.get('run_id')!r} "
            f"snapshot={run_id!r}"
        )
    if publish.get("code_commit") != code_commit:
        fail(
            f"publish commit code_commit mismatch: "
            f"publish={publish.get('code_commit')!r} snapshot={code_commit!r}"
        )

    diag_path = root / "RETRIEVAL_HARD_FAIL.json"
    if diag_path.is_file():
        diag = load_json(diag_path)
        if diag.get("run_id") != run_id:
            fail(
                f"diagnostic run_id mismatch: diag={diag.get('run_id')!r} "
                f"snapshot={run_id!r}"
            )
        if diag.get("code_commit") != code_commit:
            fail(
                f"diagnostic code_commit mismatch: "
                f"diag={diag.get('code_commit')!r} snapshot={code_commit!r}"
            )
        fail("success admission root must not contain RETRIEVAL_HARD_FAIL.json")

    return run_id, code_commit


def verify_publish_commit(
    root: Path,
    *,
    snapshot: dict[str, Any],
    miner: Any,
) -> dict[str, Any]:
    """Reject sequential partial publishes lacking a matching hash-bound identity."""
    publish_path = root / "PUBLISH_COMMIT.json"
    if not publish_path.is_file():
        fail("PUBLISH_COMMIT.json missing")
    publish = load_json(publish_path)
    page_files = {
        path.relative_to(root).as_posix(): miner.sha256_file(path)
        for path in sorted((root / "transport_pages").glob("*.json"))
    }
    expected = miner.build_publish_commit_identity(
        run_id=snapshot["run_id"],
        code_commit=snapshot["code_commit"],
        snapshot=snapshot,
        transport_page_sha256=page_files,
    )
    for field in (
        "run_id",
        "code_commit",
        "snapshot_sha256",
        "page_manifest_sha256",
        "transport_pages",
        "publish_commit_sha256",
    ):
        if publish.get(field) != expected.get(field):
            fail(f"publish commit field mismatch: {field}")
    return publish


def _raw_issues_connection(page_payload: dict[str, Any]) -> dict[str, Any]:
    data = page_payload.get("data")
    if not isinstance(data, dict):
        fail("transport page missing data")
    repo_obj = data.get("repository")
    if not isinstance(repo_obj, dict):
        fail("transport page missing repository")
    issues = repo_obj.get("issues")
    if not isinstance(issues, dict):
        fail("transport page missing issues connection")
    return issues


def verify_page_log_reconstruction(
    root: Path,
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    """Reconstruct page logs against manifest, hashes, variables, and continuity."""
    log = load_json(root / "COMMAND_LOG.json")
    entries = log.get("entries") or []
    page_entries = [e for e in entries if isinstance(e.get("page_index"), int)]
    if not page_entries:
        fail("command log has no page records")
    if any(not e.get("page_ok", False) for e in page_entries):
        fail("success admission root contains failed page log records")

    manifest = snapshot.get("page_manifest") or []
    if not isinstance(manifest, list) or not manifest:
        fail("snapshot page_manifest missing")
    if canonical_sha256(manifest) != snapshot.get("page_manifest_sha256"):
        fail("page_manifest_sha256 mismatch")
    if len(page_entries) != len(manifest):
        fail(
            f"page log/manifest cardinality mismatch: "
            f"log={len(page_entries)} manifest={len(manifest)}"
        )

    query_sha = contract.get("query_document_sha256")
    prev_by_repo: dict[str, dict[str, Any]] = {}
    for idx, (entry, man) in enumerate(zip(page_entries, manifest)):
        for field in (
            "repository",
            "page_index",
            "after",
            "endCursor",
            "hasNextPage",
            "variables_sha256",
            "response_page_sha256",
        ):
            if entry.get(field) != man.get(field):
                fail(f"page[{idx}] log/manifest mismatch on {field}")
        if entry.get("query_document_sha256") != query_sha:
            fail(f"page[{idx}] query_document_sha256 drift")
        if entry.get("operation_name") != contract.get("operation_name"):
            fail(f"page[{idx}] operation_name drift")
        variables = entry.get("variables")
        if not isinstance(variables, dict):
            fail(f"page[{idx}] variables missing")
        if man.get("variables") != variables:
            fail(f"page[{idx}] manifest variables mismatch")
        if canonical_sha256(variables) != entry.get("variables_sha256"):
            fail(f"page[{idx}] variables_sha256 reconstruction failed")
        if variables.get("after") != entry.get("after"):
            fail(f"page[{idx}] variables.after != after")
        rel = man.get("path")
        if not isinstance(rel, str) or not rel.startswith("transport_pages/"):
            fail(f"page[{idx}] invalid manifest path")
        page_path = root / rel
        if not page_path.is_file():
            fail(f"page[{idx}] missing transport page {rel}")
        actual_page_sha = sha256_file(page_path)
        if actual_page_sha != man.get("sha256"):
            fail(f"page[{idx}] transport page sha256 mismatch")
        if entry.get("exit_code") != 0:
            fail(f"page[{idx}] exit_code is nonzero in success log")
        if "endCursor" not in entry:
            fail(f"page[{idx}] missing verified endCursor")
        if "hasNextPage" not in entry:
            fail(f"page[{idx}] missing verified hasNextPage")

        repo = entry["repository"]
        prev = prev_by_repo.get(repo)
        if prev is None:
            if entry.get("after") is not None:
                fail(f"page[{idx}] first page after must be null")
            if entry.get("page_index") != 0:
                fail(f"page[{idx}] first page_index must be 0")
        else:
            if entry.get("after") != prev.get("endCursor"):
                fail(
                    f"page[{idx}] continuity break: after={entry.get('after')!r} "
                    f"prev.endCursor={prev.get('endCursor')!r}"
                )
            if entry.get("page_index") != int(prev.get("page_index")) + 1:
                fail(f"page[{idx}] page_index discontinuity")
        prev_by_repo[repo] = entry
    return page_entries


def verify_scope_page_coverage(
    root: Path,
    *,
    scope: dict[str, Any],
    snapshot: dict[str, Any],
    page_entries: list[dict[str, Any]],
) -> None:
    """Independently verify six-repo page blocks from SCOPE.json."""
    repos = scope.get("repositories") or []
    if not isinstance(repos, list) or len(repos) != 6:
        fail("SCOPE must list exactly six repositories")
    ordered = sorted(repos, key=lambda r: int(r.get("order", -1)))
    expected_repos = [str(r["repo"]) for r in ordered]
    if [int(r["order"]) for r in ordered] != [1, 2, 3, 4, 5, 6]:
        fail("SCOPE repository order must be fixed 1..6")
    if expected_repos != [str(r["repo"]) for r in repos]:
        fail("SCOPE repositories must already be listed in fixed order")

    manifest = snapshot.get("page_manifest") or []
    blocks: list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]] = []
    for man, entry in zip(manifest, page_entries):
        repo = str(man.get("repository"))
        if not blocks or blocks[-1][0] != repo:
            blocks.append((repo, [man], [entry]))
        else:
            blocks[-1][1].append(man)
            blocks[-1][2].append(entry)

    if [repo for repo, _, _ in blocks] != expected_repos:
        fail(
            "page blocks must cover SCOPE repositories in fixed order: "
            f"expected={expected_repos} got={[repo for repo, _, _ in blocks]}"
        )
    if any(repo != expected for (repo, _, _), expected in zip(blocks, expected_repos)):
        fail("page block repository identity drift vs SCOPE")

    # Shared across all six repositories; issue numbers remain per-repo.
    global_node_ids: set[str] = set()
    global_urls: set[str] = set()

    for repo, mans, logs in blocks:
        if not mans:
            fail(f"empty page block for {repo}")
        if "/" not in repo:
            fail(f"SCOPE repository not owner/name: {repo}")
        scope_owner, scope_name = repo.split("/", 1)
        for i, (man, entry) in enumerate(zip(mans, logs)):
            if int(man.get("page_index", -1)) != i or int(entry.get("page_index", -1)) != i:
                fail(f"{repo}: page block must be contiguous starting at 0")
            if man.get("repository_order") != ordered[expected_repos.index(repo)]["order"]:
                fail(f"{repo}: repository_order mismatch vs SCOPE")

            page_payload = load_json(root / man["path"])
            issues = _raw_issues_connection(page_payload)
            page_info = issues.get("pageInfo") or {}
            raw_has_next = page_info.get("hasNextPage")
            raw_end = page_info.get("endCursor")
            if raw_has_next is not True and raw_has_next is not False:
                fail(f"{repo} page {i}: raw hasNextPage must be boolean")
            if man.get("hasNextPage") != raw_has_next:
                fail(f"{repo} page {i}: manifest hasNextPage != raw pageInfo")
            if entry.get("hasNextPage") != raw_has_next:
                fail(f"{repo} page {i}: log hasNextPage != raw pageInfo")
            if man.get("endCursor") != raw_end:
                fail(f"{repo} page {i}: manifest endCursor != raw pageInfo")
            if entry.get("endCursor") != raw_end:
                fail(f"{repo} page {i}: log endCursor != raw pageInfo")

            is_last = i == len(mans) - 1
            if is_last:
                if raw_has_next is not False:
                    fail(f"{repo}: last page must terminate (hasNextPage=false)")
            else:
                if raw_has_next is not True:
                    fail(f"{repo}: middle page {i} must continue (hasNextPage=true)")
                if not raw_end:
                    fail(f"{repo}: middle page {i} missing endCursor")

        first_total: int | None = None
        seen_numbers: set[int] = set()
        node_total = 0
        for i, man in enumerate(mans):
            issues = _raw_issues_connection(load_json(root / man["path"]))
            total_count = issues.get("totalCount")
            if not isinstance(total_count, int):
                fail(f"{repo} page {i}: totalCount missing")
            if first_total is None:
                first_total = total_count
            elif total_count != first_total:
                fail(
                    f"{repo}: totalCount drift page {i}: "
                    f"{total_count} != {first_total}"
                )
            if man.get("totalCount") != total_count:
                fail(f"{repo} page {i}: manifest totalCount != raw")
            nodes = issues.get("nodes")
            if not isinstance(nodes, list):
                fail(f"{repo} page {i}: nodes missing")
            if man.get("node_count") != len(nodes):
                fail(f"{repo} page {i}: manifest node_count != raw nodes")
            node_total += len(nodes)
            for node in nodes:
                if not isinstance(node, dict):
                    fail(f"{repo} page {i}: node is not an object")
                node_id = node.get("id")
                number = node.get("number")
                url = node.get("url")
                if not isinstance(node_id, str) or not node_id:
                    fail(f"{repo} page {i}: node id missing")
                if not isinstance(number, int):
                    fail(f"{repo} page {i}: node number missing")
                if not isinstance(url, str) or not url:
                    fail(f"{repo} page {i}: node url missing")
                # Shared six-repo uniqueness before per-repo URL binding.
                if node_id in global_node_ids:
                    fail(
                        f"duplicate node id across SCOPE repositories: {node_id}"
                    )
                if url in global_urls:
                    fail(
                        f"duplicate node url across SCOPE repositories: {url}"
                    )
                if number in seen_numbers:
                    fail(f"{repo}: duplicate node number {number}")
                expected_url = (
                    f"https://github.com/{scope_owner}/{scope_name}/issues/{number}"
                )
                if url != expected_url:
                    fail(
                        f"{repo} page {i}: URL owner/repository mismatch: "
                        f"got {url!r} expected {expected_url!r}"
                    )
                global_node_ids.add(node_id)
                global_urls.add(url)
                seen_numbers.add(number)
        assert first_total is not None
        if node_total != first_total:
            fail(
                f"{repo}: node total {node_total} != totalCount {first_total}"
            )


def verify_queue_binding(
    miner: Any, scope: dict[str, Any], snapshot: dict[str, Any], queue: dict[str, Any]
) -> list[dict[str, Any]]:
    if queue.get("run_id") != snapshot.get("run_id"):
        fail(
            f"queue/snapshot run_id mismatch: queue={queue.get('run_id')!r} "
            f"snapshot={snapshot.get('run_id')!r}"
        )
    if queue.get("code_commit") != snapshot.get("code_commit"):
        fail(
            f"queue/snapshot code_commit mismatch: "
            f"queue={queue.get('code_commit')!r} "
            f"snapshot={snapshot.get('code_commit')!r}"
        )
    expected = miner.build_queue_from_snapshot(scope, snapshot)
    got = queue.get("records") or []
    if len(got) != len(expected):
        fail(f"queue cardinality mismatch expected={len(expected)} got={len(got)}")
    # Compare semantic records ignoring review_status mutations after payload build.
    def semantic(row: dict[str, Any]) -> dict[str, Any]:
        out = dict(row)
        # review_status may be updated by build-payload; compare core identity fields.
        return {k: out.get(k) for k in (
            "neutral_id",
            "union_order",
            "repository_review_order",
            *QUEUE_COPIED,
        )}

    for idx, (exp, row) in enumerate(zip(expected, got)):
        if semantic(exp) != semantic(row):
            fail(f"queue row mismatch at index {idx}: {row.get('neutral_id')}")
        if row.get("union_order") != idx % 10**9 and row.get("repository_review_order") != row.get(
            "union_order"
        ):
            # Contiguity per repository checked below.
            pass
        snap = next(
            r
            for r in snapshot["records"]
            if r["snapshot_record_id"] == row["snapshot_record_id"]
        )
        for field in QUEUE_COPIED:
            if row.get(field) != snap.get(field):
                fail(f"queue/snapshot field mismatch {row['neutral_id']}:{field}")
        if row.get("snapshot_record_sha256") != snap.get("snapshot_record_sha256"):
            fail(f"queue snapshot hash mismatch {row['neutral_id']}")

    # Contiguous IDs / orders per repository.
    by_repo: dict[str, list[dict[str, Any]]] = {}
    for row in got:
        by_repo.setdefault(row["repository"], []).append(row)
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        rows = by_repo.get(repo, [])
        for i, row in enumerate(rows, start=1):
            if row["union_order"] != i or row["repository_review_order"] != i:
                fail(f"noncontiguous order in {repo}: {row['neutral_id']}")
            expected_id = f"{repo_entry['id_prefix']}{i:02d}"
            if row["neutral_id"] != expected_id:
                fail(f"wrong neutral_id: got {row['neutral_id']} expected {expected_id}")
    return got


def earliest_review_stop(
    decisions: list[dict[str, Any]],
    *,
    queue_count: int,
    max_reviewed: int,
    target_pending: int,
) -> tuple[int, str]:
    """Independent earliest-stop index (no producer import)."""
    if queue_count == 0:
        return 0, "queue_exhausted"
    pending = 0
    for index, decision in enumerate(decisions, start=1):
        if decision.get("decision") == "ADMIT_PENDING_REPRO":
            pending += 1
        hit_five = pending >= target_pending
        hit_cap = index >= max_reviewed
        hit_end = index >= queue_count
        if not (hit_five or hit_cap or hit_end):
            continue
        if hit_end:
            return index, "queue_exhausted"
        if hit_five:
            return index, "five_admit_pending_repro"
        return index, "twenty_reviewed"
    return -1, "invalid_early_stop"


def review_stop_reason(
    decisions: list[dict[str, Any]],
    *,
    queue_count: int,
    max_reviewed: int,
    target_pending: int,
) -> str:
    _stop_at, reason = earliest_review_stop(
        decisions,
        queue_count=queue_count,
        max_reviewed=max_reviewed,
        target_pending=target_pending,
    )
    return reason


def _project_quota_feasibility(
    quotas: dict[str, Any], decisions: list[dict[str, Any]]
) -> dict[str, Any]:
    pending_by_repo: dict[str, int] = {}
    for decision in decisions:
        if decision.get("decision") == "ADMIT_PENDING_REPRO":
            repo = decision["repository"]
            pending_by_repo[repo] = pending_by_repo.get(repo, 0) + 1
    shortfalls: list[dict[str, Any]] = []
    for entry in quotas["readiness_quota_order"]:
        repo = entry["repo"]
        target = int(entry["additional_ready_target"])
        have = pending_by_repo.get(repo, 0)
        if have < target:
            shortfalls.append(
                {
                    "repo": repo,
                    "additional_ready_target": target,
                    "pending_admit_rows": have,
                    "shortfall": target - have,
                }
            )
    status = "FEASIBLE" if not shortfalls else quotas["shortfall_status"]
    starting = quotas["starting_state"]
    return {
        "status": status,
        "shortfalls": shortfalls,
        "pending_by_repo": pending_by_repo,
        "starting_accepted_ready_defects": starting["accepted_ready_defects"],
        "starting_qualifying_projects": starting["qualifying_projects"],
        "projection_if_quotas_met": quotas["projection_if_quotas_met"],
        "claims_ready_success": False,
        "claims_readiness_executed": False,
        "claims_canonical_freeze": False,
    }


_GIT_SHOW_CACHE: dict[tuple[str, str], bytes | None] = {}
_GIT_LS_TREE_CACHE: dict[str, list[str]] = {}


def _git_show_bytes(repo_root: Path, commit: str, rel: str) -> bytes | None:
    key = (commit, rel)
    if key in _GIT_SHOW_CACHE:
        return _GIT_SHOW_CACHE[key]
    proc = subprocess.run(
        ["git", "show", f"{commit}:{rel}"],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )
    value = None if proc.returncode != 0 else proc.stdout
    _GIT_SHOW_CACHE[key] = value
    return value


def _baseline_ls_tree(repo_root: Path, rel_prefix: str) -> list[str]:
    if rel_prefix in _GIT_LS_TREE_CACHE:
        return _GIT_LS_TREE_CACHE[rel_prefix]
    proc = subprocess.run(
        [
            "git",
            "ls-tree",
            "-r",
            "--name-only",
            TRANSPORT_BASELINE_COMMIT,
            "--",
            rel_prefix,
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        _GIT_LS_TREE_CACHE[rel_prefix] = []
        return []
    values = [line.replace("\\", "/") for line in proc.stdout.splitlines() if line.strip()]
    _GIT_LS_TREE_CACHE[rel_prefix] = values
    return values

def _baseline_contract_files_match(root: Path, repo_root: Path) -> bool:
    for name in ("SCOPE.json", "TRANSPORT_CONTRACT.json", "QUOTAS.json"):
        path = root / name
        if not path.is_file():
            return False
        expected = _git_show_bytes(
            repo_root,
            TRANSPORT_BASELINE_COMMIT,
            f"{TRANSPORT_BASELINE_PREFIX}/{name}",
        )
        if expected is None or path.read_bytes() != expected:
            return False
    return True



def _baseline_input_sha256(repo_root: Path) -> dict[str, str]:
    raw = _git_show_bytes(
        repo_root,
        TRANSPORT_BASELINE_COMMIT,
        f"{TRANSPORT_BASELINE_PREFIX}/SCOPE.json",
    )
    if raw is None:
        return {}
    try:
        scope = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    payload = scope.get("input_sha256") or {}
    if not isinstance(payload, dict):
        return {}
    return {str(k): str(v) for k, v in payload.items()}


# Test-only override; production must leave this None.
_TEST_TRANSPORT_FREEZE_PROVIDER = None


def _full_transport_freeze_match(root: Path, repo_root: Path) -> bool:
    """Unconditional byte/tree equality for every frozen transport path."""
    for name in TRANSPORT_FREEZE_FILES:
        path = root / name
        if not path.is_file():
            return False
        expected = _git_show_bytes(
            repo_root,
            TRANSPORT_BASELINE_COMMIT,
            f"{TRANSPORT_BASELINE_PREFIX}/{name}",
        )
        if expected is None or path.read_bytes() != expected:
            return False
    for tree in TRANSPORT_FREEZE_TREES:
        prefix = f"{TRANSPORT_BASELINE_PREFIX}/{tree}"
        baseline_rels = _baseline_ls_tree(repo_root, prefix)
        baseline_suffixes = {
            rel[len(TRANSPORT_BASELINE_PREFIX) + 1 :] for rel in baseline_rels
        }
        tree_root = root / tree
        actual_suffixes: set[str] = set()
        if tree_root.is_dir():
            for path in tree_root.rglob("*"):
                if path.is_file():
                    actual_suffixes.add(path.relative_to(root).as_posix())
        elif tree_root.exists():
            return False
        if actual_suffixes != baseline_suffixes:
            return False
        for suffix in sorted(baseline_suffixes):
            expected = _git_show_bytes(
                repo_root,
                TRANSPORT_BASELINE_COMMIT,
                f"{TRANSPORT_BASELINE_PREFIX}/{suffix}",
            )
            path = root / suffix
            if expected is None or not path.is_file() or path.read_bytes() != expected:
                return False
    for rel, expected_hash in _baseline_input_sha256(repo_root).items():
        path = repo_root / rel
        if not path.is_file() or sha256_file(path) != expected_hash:
            return False
    return True


def _transport_freeze_matches_baseline(root: Path, repo_root: Path) -> bool:
    """Compare the complete frozen transport set to 020b60fb... with no fallback.

    Tests may install ``_TEST_TRANSPORT_FREEZE_PROVIDER``; production leaves it None.
    """
    provider = _TEST_TRANSPORT_FREEZE_PROVIDER
    if callable(provider):
        return bool(provider(root, repo_root))
    return _full_transport_freeze_match(root, repo_root)


def _command_blob_sentinel_hits(blobs: list[str]) -> tuple[bool, bool]:
    readiness_hit = False
    freeze_hit = False
    for blob in blobs:
        if not DOWNSTREAM_SENTINEL_RE.search(blob):
            continue
        lower = blob.lower()
        if "readiness" in lower:
            readiness_hit = True
        if re.search(r"\bcanonical[_-]freeze\b", lower) or re.search(
            r"\bcanonical\b.*\bfreeze\b", lower
        ):
            freeze_hit = True
        if re.search(r"\bannotation\b|\bprediction\b|\bdetection_result\b", lower):
            freeze_hit = True
    return readiness_hit, freeze_hit


def _command_sources_sentinel_hits(root: Path) -> tuple[bool, bool]:
    """Scan COMMAND_LOG.json and VERIFICATION_LOG.json for downstream sentinels."""
    blobs: list[str] = []
    command_log_path = root / "COMMAND_LOG.json"
    if command_log_path.is_file():
        command_log = load_json(command_log_path)
        for entry in command_log.get("entries") or []:
            blobs.append(json.dumps(entry, sort_keys=True, ensure_ascii=False))
    vlog_path = root / "VERIFICATION_LOG.json"
    if vlog_path.is_file():
        vlog = load_json(vlog_path)
        for entry in vlog.get("commands") or []:
            blobs.append(json.dumps(entry, sort_keys=True, ensure_ascii=False))
    return _command_blob_sentinel_hits(blobs)


def _classify_forbidden_rel(rel: str) -> tuple[bool, bool, bool]:
    tokens = {
        match.group(1).lower() for match in FORBIDDEN_PATH_NAME_RE.finditer(rel)
    }
    if not tokens:
        return False, False, False
    readiness = "readiness" in tokens
    freeze = bool(tokens - {"readiness"})
    return True, readiness, freeze


def _path_bytes_match_baseline(repo_root: Path, rel: str) -> bool:
    expected = _git_show_bytes(repo_root, TRANSPORT_BASELINE_COMMIT, rel)
    if expected is None:
        return False
    path = repo_root / rel
    return path.is_file() and path.read_bytes() == expected


def _forbidden_path_scan(
    root: Path, *, repo_root: Path | None = None
) -> tuple[bool, bool, bool]:
    """Reject new/changed readiness/freeze paths vs transport baseline; allow historical."""
    forbidden_path_hit = False
    readiness_file_hit = False
    freeze_file_hit = False
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    repo_resolved = repo_root.resolve()
    root_resolved = root.resolve() if root.is_dir() else None
    baseline_paths = set(_baseline_ls_tree(repo_root, ""))
    # Limit baseline index to the whole repo tree at the freeze commit.
    proc_base = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", TRANSPORT_BASELINE_COMMIT],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc_base.returncode == 0:
        baseline_paths = {
            line.replace("\\", "/") for line in proc_base.stdout.splitlines() if line
        }

    seen: set[str] = set()

    def _consume(rel: str, *, abs_path: Path | None = None) -> None:
        nonlocal forbidden_path_hit, readiness_file_hit, freeze_file_hit
        rel = rel.replace("\\", "/")
        if rel in seen:
            return
        seen.add(rel)
        hit, readiness, freeze = _classify_forbidden_rel(rel)
        if not hit:
            return
        # Historical unchanged baseline paths are admitted; new/changed are not.
        if rel in baseline_paths and _path_bytes_match_baseline(repo_root, rel):
            return
        if abs_path is not None and rel not in baseline_paths:
            # Fixture paths outside the git tree still count as newly introduced.
            pass
        elif rel in baseline_paths and abs_path is not None:
            expected = _git_show_bytes(repo_root, TRANSPORT_BASELINE_COMMIT, rel)
            if expected is not None and abs_path.is_file() and abs_path.read_bytes() == expected:
                return
        forbidden_path_hit = True
        readiness_file_hit = readiness_file_hit or readiness
        freeze_file_hit = freeze_file_hit or freeze

    # Also walk the admission root and its sibling boundary (tmp fixtures).
    scan_roots: list[Path] = []
    if root.is_dir():
        scan_roots.append(root)
        if root.parent.is_dir():
            scan_roots.append(root.parent)
    for base in scan_roots:
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.name in {"VERIFICATION_LOG.json", "HANDOFF_SUPPLEMENTAL_R2.json"}:
                continue
            try:
                rel = path.resolve().relative_to(repo_resolved).as_posix()
            except ValueError:
                # Outside repo: treat basename/path under fixture parent as new.
                if root_resolved and path.resolve().is_relative_to(root_resolved):
                    rel = path.resolve().relative_to(root_resolved).as_posix()
                    rel = f"{TRANSPORT_BASELINE_PREFIX}/{rel}"
                else:
                    rel = path.name
            _consume(rel, abs_path=path)

    return forbidden_path_hit, readiness_file_hit, freeze_file_hit


def _compute_confirmations(
    *,
    root: Path,
    scope: dict[str, Any],
    decisions: list[dict[str, Any]],
    repo_root: Path | None = None,
) -> dict[str, bool]:
    """Independently prove confirmations (no producer import, no SCOPE trust)."""
    del scope  # Never trust mutable SCOPE self-hashes; baseline is authoritative.
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    a2_all_pending = all(
        d.get("crit_dual_arm_repro") == "PENDING" for d in decisions
    )
    analysis_id_all_blank = all(
        d.get("analysis_id") in (None, "") for d in decisions
    )
    vocab_clean = True
    for decision in decisions:
        for text_key in ("mechanism", "decision_reason"):
            if PROHIBITED_VOCAB_RE.search(decision.get(text_key) or ""):
                vocab_clean = False
                break
        if not vocab_clean:
            break
    readiness_cmd, freeze_cmd = _command_sources_sentinel_hits(root)
    path_hit, readiness_file, freeze_file = _forbidden_path_scan(
        root, repo_root=repo_root
    )
    existing_files_unchanged = _transport_freeze_matches_baseline(root, repo_root)
    return {
        "a2_all_pending": a2_all_pending,
        "analysis_id_all_blank": analysis_id_all_blank,
        "forbidden_data_absent": vocab_clean and not path_hit,
        "readiness_ran": bool(readiness_cmd or readiness_file),
        "canonical_freeze_claimed": bool(freeze_cmd or freeze_file),
        "existing_files_unchanged": existing_files_unchanged,
    }


def recompute_admission_summary(
    *,
    root: Path,
    scope: dict[str, Any],
    quotas: dict[str, Any],
    queue: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Independently recompute handoff summary fields (no producer import)."""
    max_reviewed = int(scope["max_reviewed_per_repo"])
    target_pending = int(scope["target_pending_per_repo"])
    by_repo_q: dict[str, list[dict[str, Any]]] = {
        r["repo"]: [] for r in scope["repositories"]
    }
    for row in queue:
        by_repo_q.setdefault(row["repository"], []).append(row)
    by_repo_d: dict[str, list[dict[str, Any]]] = {
        r["repo"]: [] for r in scope["repositories"]
    }
    for decision in decisions:
        by_repo_d.setdefault(decision["repository"], []).append(decision)

    repository_review_counts: dict[str, Any] = {}
    for repo_entry in scope["repositories"]:
        repo = repo_entry["repo"]
        qrows = by_repo_q.get(repo, [])
        drows = by_repo_d.get(repo, [])
        admits = sum(1 for d in drows if d.get("decision") == "ADMIT_PENDING_REPRO")
        excluded = sum(1 for d in drows if d.get("decision") == "EXCLUDED")
        excl_classes: dict[str, int] = {}
        for d in drows:
            if d.get("decision") != "EXCLUDED":
                continue
            key = d.get("exclusion_class") or "(A1/A3 fail)"
            excl_classes[key] = excl_classes.get(key, 0) + 1
        status_counts: dict[str, int] = {}
        for row in qrows:
            st = str(row.get("review_status") or "")
            status_counts[st] = status_counts.get(st, 0) + 1
        reason = review_stop_reason(
            drows,
            queue_count=len(qrows),
            max_reviewed=max_reviewed,
            target_pending=target_pending,
        )
        repository_review_counts[repo] = {
            "queue_size": len(qrows),
            "reviewed": len(drows),
            "admit_pending_repro": admits,
            "excluded": excluded,
            "exclusion_class_counts": excl_classes,
            "review_status_counts": status_counts,
            "stop_reason": reason,
        }
    return {
        "decision_totals": {
            "decisions": len(decisions),
            "admit_pending_repro": sum(
                1 for d in decisions if d.get("decision") == "ADMIT_PENDING_REPRO"
            ),
            "excluded": sum(1 for d in decisions if d.get("decision") == "EXCLUDED"),
        },
        "repository_review_counts": repository_review_counts,
        "quota_feasibility": _project_quota_feasibility(quotas, decisions),
        "confirmations": _compute_confirmations(
            root=root, scope=scope, decisions=decisions, repo_root=repo_root
        ),
    }


def _deep_equal(expected: Any, actual: Any, *, path: str) -> None:
    if isinstance(expected, dict) and isinstance(actual, dict):
        exp_keys = set(expected)
        act_keys = set(actual)
        for key in sorted(exp_keys - act_keys):
            fail(f"{path}.{key}: missing")
        for key in sorted(act_keys - exp_keys):
            fail(f"{path}.{key}: unexpected")
        for key in sorted(exp_keys & act_keys):
            _deep_equal(expected[key], actual[key], path=f"{path}.{key}")
        return
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            fail(f"{path}: list length expected {len(expected)}, got {len(actual)}")
        for idx, (exp_item, act_item) in enumerate(zip(expected, actual)):
            _deep_equal(exp_item, act_item, path=f"{path}[{idx}]")
        return
    if expected != actual:
        fail(f"{path}: expected {expected!r}, got {actual!r}")


def verify_decisions(
    scope: dict[str, Any],
    queue: list[dict[str, Any]],
    decisions_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    decisions = decisions_payload.get("decisions") or []
    exclusion_classes = set(scope["exclusion_classes"])
    max_reviewed = int(scope["max_reviewed_per_repo"])
    target_pending = int(scope["target_pending_per_repo"])
    scope_repos = [entry["repo"] for entry in scope["repositories"]]
    scope_set = set(scope_repos)

    by_repo_q: dict[str, list[dict[str, Any]]] = {repo: [] for repo in scope_repos}
    for row in queue:
        repo = row["repository"]
        if repo not in scope_set:
            fail(f"out-of-scope queue row: {repo}")
        by_repo_q[repo].append(row)
    by_repo_d: dict[str, list[dict[str, Any]]] = {repo: [] for repo in scope_repos}
    for decision in decisions:
        repo = decision["repository"]
        if repo not in scope_set:
            fail(f"out-of-scope decision: {repo}")
        by_repo_d[repo].append(decision)

    expected: list[dict[str, Any]] = []
    for repo in scope_repos:
        qrows = by_repo_q[repo]
        dreviews = by_repo_d[repo]
        if not qrows:
            if dreviews:
                fail(f"empty-queue decision for {repo}")
            continue
        if not dreviews:
            fail(f"no decisions for non-empty queue: {repo}")
        for idx, decision in enumerate(dreviews):
            if idx >= len(qrows):
                fail(f"extra decision for {repo}")
            qrow = qrows[idx]
            if qrow.get("review_status") == "NOT_REVIEWED_AFTER_STOP":
                fail(
                    f"decision for NOT_REVIEWED_AFTER_STOP: {decision.get('neutral_id')}"
                )
            for field in DECISION_COPIED:
                if decision.get(field) != qrow.get(field):
                    fail(
                        f"decision/queue mismatch {decision.get('neutral_id')}:{field}"
                    )
            if decision.get("crit_dual_arm_repro") != "PENDING":
                fail(f"non-PENDING A2 for {decision.get('neutral_id')}")
            if decision.get("analysis_id") not in (None, ""):
                fail(f"nonblank analysis_id for {decision.get('neutral_id')}")
            a1 = decision.get("crit_real_public_fix")
            a3 = decision.get("crit_in_numerical_scope")
            verdict = decision.get("decision")
            excl = decision.get("exclusion_class") or ""
            for text_key in ("mechanism", "decision_reason"):
                if PROHIBITED_VOCAB_RE.search(decision.get(text_key) or ""):
                    fail(
                        f"forbidden vocabulary in {decision.get('neutral_id')}:{text_key}"
                    )
            if a1 == "PASS":
                for field in ("buggy_sha", "fixed_sha"):
                    if not FULL_SHA.match(str(decision.get(field) or "")):
                        fail(f"short SHA {decision.get('neutral_id')}:{field}")
                for field in ("public_issue_url", "public_fix_url"):
                    if not decision.get(field):
                        fail(f"missing public URL {decision.get('neutral_id')}:{field}")
            if verdict == "ADMIT_PENDING_REPRO":
                if a1 != "PASS" or a3 != "PASS" or excl:
                    fail(f"ADMIT inconsistency {decision.get('neutral_id')}")
            elif verdict == "EXCLUDED":
                if excl and excl not in exclusion_classes:
                    fail(f"invalid exclusion class {excl}")
                if not excl and a1 == "PASS" and a3 == "PASS":
                    fail(f"excluded without class/failure {decision.get('neutral_id')}")
            else:
                fail(f"invalid decision {verdict}")

        pending = sum(1 for d in dreviews if d.get("decision") == "ADMIT_PENDING_REPRO")
        decision_count = len(dreviews)
        queue_count = len(qrows)
        if decision_count > max_reviewed:
            fail(f"reviewed over cap for {repo}")
        if pending > target_pending:
            fail(f"pending over cap for {repo}")
        if decision_count > queue_count:
            fail(f"extra decision for {repo}")
        stop_at, reason = earliest_review_stop(
            dreviews,
            queue_count=queue_count,
            max_reviewed=max_reviewed,
            target_pending=target_pending,
        )
        if stop_at < 0:
            fail(
                f"invalid early stop for {repo}: "
                f"decisions={decision_count}, queue={queue_count}, pending={pending}"
            )
        if decision_count != stop_at:
            fail(
                f"submitted prefix {decision_count} != earliest stop {stop_at} "
                f"({reason}) for {repo}"
            )

        for idx, qrow in enumerate(qrows):
            status = qrow.get("review_status")
            if idx < decision_count:
                if status == "NOT_REVIEWED_AFTER_STOP":
                    fail(
                        f"decision for NOT_REVIEWED_AFTER_STOP: "
                        f"{qrow.get('neutral_id')}"
                    )
            elif status == "REVIEWED":
                fail(
                    f"omitted reviewed decision for {qrow.get('neutral_id')}: "
                    "queue row marked REVIEWED without a decision"
                )
        expected.extend(dreviews)

    got_ids = [d["neutral_id"] for d in decisions]
    expected_ids = [d["neutral_id"] for d in expected]
    if got_ids != expected_ids:
        fail(
            f"global decisions != legal per-repo prefixes: {got_ids!r} vs {expected_ids!r}"
        )
    return decisions


def verify_sheet_and_evidence(
    decisions: list[dict[str, Any]],
    sheet_rows: list[dict[str, str]],
    evidence_snapshot: dict[str, Any],
    root: Path,
) -> None:
    if len(sheet_rows) != len(decisions):
        fail(
            f"sheet/decision cardinality mismatch "
            f"{len(sheet_rows)} != {len(decisions)}"
        )
    manifest = evidence_snapshot.get("records") or []
    if len(manifest) != len(decisions):
        fail("evidence manifest cardinality mismatch")
    seen_evidence: set[str] = set()
    for decision, row, man in zip(decisions, sheet_rows, manifest):
        nid = decision["neutral_id"]
        if row.get("neutral_id") != nid or man.get("neutral_id") != nid:
            fail(f"sheet/evidence order mismatch around {nid}")
        if row.get("source_cohort") != "supplemental_r2":
            fail(f"wrong cohort for {nid}")
        if row.get("analysis_id") not in (None, ""):
            fail(f"nonblank alias for {nid}")
        if row.get("crit_dual_arm_repro") != "PENDING":
            fail(f"sheet A2 not PENDING for {nid}")
        for field in SHEET_BOUND:
            sheet_val = row.get(field) or ""
            if field == "mechanism":
                dec_val = decision.get("mechanism") or ""
            elif field == "decision_reason":
                dec_val = decision.get("decision_reason") or ""
            elif field in {
                "buggy_sha",
                "fixed_sha",
                "crit_real_public_fix",
                "crit_dual_arm_repro",
                "crit_in_numerical_scope",
                "decision",
                "neutral_id",
                "repository",
                "issue_url",
            }:
                dec_val = str(decision.get(field) or "")
                if field == "crit_dual_arm_repro":
                    dec_val = "PENDING"
            else:
                dec_val = str(decision.get(field) or "")
            if sheet_val != dec_val:
                fail(f"sheet/decision mismatch {nid}:{field}")
        for text_key in ("mechanism", "decision_reason"):
            if PROHIBITED_VOCAB_RE.search(row.get(text_key) or ""):
                fail(f"forbidden vocabulary in sheet {nid}:{text_key}")

        rel = (man.get("path") or "").replace("\\", "/")
        candidates = [
            root / "admission_evidence" / nid / "evidence.json",
            root / rel,
            Path.cwd() / rel,
        ]
        if "admission_evidence/" in rel:
            suffix = rel.split("admission_evidence/", 1)[1]
            candidates.insert(0, root / "admission_evidence" / suffix)
        candidate = next((p for p in candidates if p.is_file()), None)
        if candidate is None:
            fail(f"missing evidence file for {nid}: {rel}")
        actual_sha = sha256_file(candidate)
        if actual_sha != man.get("sha256"):
            fail(f"evidence hash mismatch for {nid}")
        if nid in seen_evidence:
            fail(f"duplicate evidence for {nid}")
        seen_evidence.add(nid)
        evidence = load_json(candidate)
        for field in EVIDENCE_BOUND:
            if field == "crit_dual_arm_repro":
                if evidence.get(field) != "PENDING":
                    fail(f"evidence A2 not PENDING for {nid}")
                continue
            if evidence.get(field) != decision.get(field) and not (
                (evidence.get(field) in (None, ""))
                and (decision.get(field) in (None, ""))
            ):
                # string normalize
                if str(evidence.get(field) or "") != str(decision.get(field) or ""):
                    fail(f"evidence/decision mismatch {nid}:{field}")
        if evidence.get("analysis_id") not in (None, ""):
            fail(f"evidence nonblank analysis_id for {nid}")
        # Cross-check sheet vs evidence for overlapping fields.
        for field in (
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
        ):
            if str(row.get(field) or "") != str(evidence.get(field) or ""):
                fail(f"sheet/evidence mismatch {nid}:{field}")


def verify_gate_binding(root: Path, handoff: dict[str, Any] | None) -> None:
    """Require handoff + verification log, hash-bind them, and enforce r4 gate."""
    handoff_path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
    vlog_path = root / "VERIFICATION_LOG.json"
    if not handoff_path.is_file():
        fail("missing HANDOFF_SUPPLEMENTAL_R2.json")
    if handoff is None:
        handoff = load_json(handoff_path)
    if not vlog_path.is_file():
        fail("missing VERIFICATION_LOG.json")
    vlog = load_json(vlog_path)
    file_sha = handoff.get("file_sha256") or {}
    expected_vl = file_sha.get("VERIFICATION_LOG.json")
    if not expected_vl:
        fail("handoff file_sha256 missing VERIFICATION_LOG.json")
    actual_vl = sha256_file(vlog_path)
    if actual_vl != expected_vl:
        fail(
            "VERIFICATION_LOG.json hash mismatch: "
            f"expected {expected_vl}, got {actual_vl}"
        )
    hgate = handoff.get("gate_requested")
    vgate = vlog.get("gate_requested")
    if hgate != EXPECTED_GATE:
        fail(f"handoff gate_requested {hgate!r} != {EXPECTED_GATE!r}")
    if vgate != EXPECTED_GATE:
        fail(f"verification_log gate_requested {vgate!r} != {EXPECTED_GATE!r}")
    if hgate != vgate:
        fail(
            "gate mismatch between handoff and verification_log: "
            f"{hgate!r} vs {vgate!r}"
        )


def verify_confirmation_policy(confirmations: dict[str, bool]) -> None:
    """Fail closed when baseline/path/command evidence shows downstream drift."""
    if not confirmations.get("a2_all_pending"):
        fail("A2 is not all PENDING")
    if not confirmations.get("analysis_id_all_blank"):
        fail("analysis_id is not all blank")
    if not confirmations.get("forbidden_data_absent"):
        fail("forbidden data or downstream path present")
    if confirmations.get("readiness_ran"):
        fail("readiness sentinel detected")
    if confirmations.get("canonical_freeze_claimed"):
        fail("canonical freeze sentinel detected")
    if not confirmations.get("existing_files_unchanged"):
        fail("immutable inputs drifted from transport baseline")


def verify_handoff_summary(
    *,
    root: Path,
    scope: dict[str, Any],
    quotas: dict[str, Any],
    queue: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    handoff: dict[str, Any] | None,
) -> None:
    """Independently recompute summary/confirmations and compare when handoff exists."""
    expected = recompute_admission_summary(
        root=root, scope=scope, quotas=quotas, queue=queue, decisions=decisions
    )
    verify_confirmation_policy(expected["confirmations"])
    if handoff is None:
        fail("missing HANDOFF_SUPPLEMENTAL_R2.json")
    _deep_equal(
        expected["decision_totals"],
        handoff.get("decision_totals"),
        path="decision_totals",
    )
    _deep_equal(
        expected["repository_review_counts"],
        handoff.get("repository_review_counts"),
        path="repository_review_counts",
    )
    _deep_equal(
        expected["quota_feasibility"],
        handoff.get("quota_feasibility"),
        path="quota_feasibility",
    )
    _deep_equal(
        expected["confirmations"],
        handoff.get("confirmations"),
        path="confirmations",
    )


def verify_admission(root: Path) -> int:
    """Library entry point: return 0 on success, nonzero on failure."""
    try:
        if not root.is_dir():
            fail(f"root not a directory: {root}")
        scope = load_json(root / "SCOPE.json")
        verify_frozen_inputs(root, scope)
        miner = _load_miner()
        snapshot = load_json(root / "ISSUE_SNAPSHOT.json")
        verify_run_code_binding(root, snapshot)
        contract = load_json(root / "TRANSPORT_CONTRACT.json")
        page_entries = verify_page_log_reconstruction(
            root, snapshot=snapshot, contract=contract
        )
        verify_scope_page_coverage(
            root,
            scope=scope,
            snapshot=snapshot,
            page_entries=page_entries,
        )
        verify_snapshot_bound_to_raw_pages(root, scope=scope, snapshot=snapshot)
        verify_snapshot_records(scope, snapshot)
        queue_payload = load_json(root / "REVIEW_QUEUE.json")
        verify_publish_commit(root, snapshot=snapshot, miner=miner)
        queue = verify_queue_binding(miner, scope, snapshot, queue_payload)
        decisions_payload = load_json(root / "REVIEW_DECISIONS.json")
        decisions = verify_decisions(scope, queue, decisions_payload)
        sheet_path = root / "admission_sheet.cursor_candidate.csv"
        sheet_rows = read_sheet(sheet_path)
        evidence_snapshot = load_json(root / "EVIDENCE_SNAPSHOT.json")
        verify_sheet_and_evidence(decisions, sheet_rows, evidence_snapshot, root)
        quotas = load_json(root / "QUOTAS.json")
        handoff_path = root / "HANDOFF_SUPPLEMENTAL_R2.json"
        if not handoff_path.is_file():
            fail("missing HANDOFF_SUPPLEMENTAL_R2.json")
        handoff = load_json(handoff_path)
        verify_gate_binding(root, handoff)
        verify_handoff_summary(
            root=root,
            scope=scope,
            quotas=quotas,
            queue=queue,
            decisions=decisions,
            handoff=handoff,
        )
        print("ADMISSION_CHECK_OK")
        return 0
    except AdmissionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: unexpected: {exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/external_slice/supplemental_r2"),
    )
    args = parser.parse_args(argv)
    return verify_admission(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
