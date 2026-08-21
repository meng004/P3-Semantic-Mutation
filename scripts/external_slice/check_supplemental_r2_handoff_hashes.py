#!/usr/bin/env python3
"""Verify supplemental R2 handoff SHA-256 bindings, counts, and SELF parent relationship."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_self_commit(handoff: dict[str, Any], *, cwd: Path) -> str | None:
    """Resolve handoff_commit.value SELF to current HEAD when present."""
    hc = handoff.get("handoff_commit") or {}
    value = hc.get("value")
    if value != "SELF":
        return value
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def verify_parent_relationship(
    handoff: dict[str, Any], *, cwd: Path, handoff_commit: str | None
) -> list[str]:
    errors: list[str] = []
    hc = handoff.get("handoff_commit") or {}
    required_parent = hc.get("direct_parent_required") or handoff.get("payload_commit")
    if not required_parent:
        errors.append("missing direct_parent_required / payload_commit")
        return errors
    if handoff.get("payload_commit") and handoff["payload_commit"] != required_parent:
        if handoff["payload_commit"] != required_parent:
            errors.append("payload_commit != direct_parent_required")
    if not handoff_commit:
        errors.append("unable to resolve handoff commit")
        return errors
    proc = subprocess.run(
        ["git", "rev-parse", f"{handoff_commit}^"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        errors.append(f"unable to resolve parent of {handoff_commit}")
        return errors
    actual_parent = proc.stdout.strip()
    if actual_parent != required_parent:
        errors.append(
            f"handoff parent mismatch: expected {required_parent}, got {actual_parent}"
        )
    return errors


def _resolve_declared_path(rel: str, *, handoff_path: Path, cwd: Path) -> Path | None:
    """Resolve a handoff-relative path against root, cwd, or repo root."""
    candidates = [
        handoff_path.parent / rel,
        cwd / rel,
        Path(__file__).resolve().parents[2] / rel,
    ]
    if rel.startswith("data/external_slice/supplemental_r2/"):
        suffix = rel.split("data/external_slice/supplemental_r2/", 1)[1]
        candidates.insert(0, handoff_path.parent / suffix)
    return next((p for p in candidates if p.is_file()), None)


def _earliest_review_stop(
    decisions: list[dict[str, Any]],
    *,
    queue_count: int,
    max_reviewed: int,
    target_pending: int,
) -> tuple[int, str]:
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


def _review_stop_reason(
    decisions: list[dict[str, Any]],
    *,
    queue_count: int,
    max_reviewed: int,
    target_pending: int,
) -> str:
    _stop_at, reason = _earliest_review_stop(
        decisions,
        queue_count=queue_count,
        max_reviewed=max_reviewed,
        target_pending=target_pending,
    )
    return reason


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
    """Independently prove confirmations from baseline hashes and command/path scans."""
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


def _project_quota_feasibility(
    quotas: dict[str, Any], decisions: list[dict[str, Any]]
) -> dict[str, Any]:
    pending_by_repo: dict[str, int] = {}
    for d in decisions:
        if d.get("decision") == "ADMIT_PENDING_REPRO":
            pending_by_repo[d["repository"]] = pending_by_repo.get(d["repository"], 0) + 1
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
    projection = quotas["projection_if_quotas_met"]
    return {
        "status": status,
        "shortfalls": shortfalls,
        "pending_by_repo": pending_by_repo,
        "starting_accepted_ready_defects": starting["accepted_ready_defects"],
        "starting_qualifying_projects": starting["qualifying_projects"],
        "projection_if_quotas_met": projection,
        "claims_ready_success": False,
        "claims_readiness_executed": False,
        "claims_canonical_freeze": False,
    }


def recompute_admission_summary(
    *,
    root: Path,
    scope: dict[str, Any],
    quotas: dict[str, Any],
    queue: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    sheet_rows: list[dict[str, str]],
    evidence_snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Independently recompute handoff summary fields from artifacts."""
    if len(sheet_rows) != len(decisions):
        raise ValueError(
            f"sheet/decision cardinality mismatch {len(sheet_rows)} != {len(decisions)}"
        )
    manifest = evidence_snapshot.get("records") or []
    if len(manifest) != len(decisions):
        raise ValueError("evidence manifest cardinality mismatch")
    for decision, row, man in zip(decisions, sheet_rows, manifest):
        nid = decision["neutral_id"]
        if row.get("neutral_id") != nid or man.get("neutral_id") != nid:
            raise ValueError(f"sheet/evidence order mismatch around {nid}")
        if str(row.get("decision") or "") != str(decision.get("decision") or ""):
            raise ValueError(f"sheet/decision mismatch {nid}:decision")

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
        reason = _review_stop_reason(
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

    feasibility = _project_quota_feasibility(quotas, decisions)
    return {
        "decision_totals": {
            "decisions": len(decisions),
            "admit_pending_repro": sum(
                1 for d in decisions if d.get("decision") == "ADMIT_PENDING_REPRO"
            ),
            "excluded": sum(1 for d in decisions if d.get("decision") == "EXCLUDED"),
        },
        "repository_review_counts": repository_review_counts,
        "quota_feasibility": feasibility,
        "confirmations": _compute_confirmations(
            root=root, scope=scope, decisions=decisions
        ),
    }


def _deep_equal(expected: Any, actual: Any, *, path: str) -> list[str]:
    errors: list[str] = []
    if type(expected) is not type(actual) and not (
        isinstance(expected, (int, float)) and isinstance(actual, (int, float))
    ):
        # Allow dict key order differences only via recursive compare.
        if not (isinstance(expected, dict) and isinstance(actual, dict)):
            if expected != actual:
                errors.append(f"{path}: expected {expected!r}, got {actual!r}")
            return errors
    if isinstance(expected, dict):
        exp_keys = set(expected)
        act_keys = set(actual)
        for key in sorted(exp_keys - act_keys):
            errors.append(f"{path}.{key}: missing in handoff")
        for key in sorted(act_keys - exp_keys):
            errors.append(f"{path}.{key}: unexpected in handoff")
        for key in sorted(exp_keys & act_keys):
            errors.extend(
                _deep_equal(expected[key], actual[key], path=f"{path}.{key}")
            )
        return errors
    if isinstance(expected, list):
        if len(expected) != len(actual):
            errors.append(
                f"{path}: list length expected {len(expected)}, got {len(actual)}"
            )
            return errors
        for idx, (exp_item, act_item) in enumerate(zip(expected, actual)):
            errors.extend(_deep_equal(exp_item, act_item, path=f"{path}[{idx}]"))
        return errors
    if expected != actual:
        errors.append(f"{path}: expected {expected!r}, got {actual!r}")
    return errors


def verify_decision_guards(
    scope: dict[str, Any],
    queue: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
) -> list[str]:
    """Reject out-of-scope, empty-queue, and post-stop decision prefixes."""
    errors: list[str] = []
    max_reviewed = int(scope["max_reviewed_per_repo"])
    target_pending = int(scope["target_pending_per_repo"])
    scope_repos = [entry["repo"] for entry in scope["repositories"]]
    scope_set = set(scope_repos)
    by_repo_q: dict[str, list[dict[str, Any]]] = {repo: [] for repo in scope_repos}
    for row in queue:
        repo = row["repository"]
        if repo not in scope_set:
            errors.append(f"out-of-scope queue row: {repo}")
            continue
        by_repo_q[repo].append(row)
    by_repo_d: dict[str, list[dict[str, Any]]] = {repo: [] for repo in scope_repos}
    for decision in decisions:
        repo = decision["repository"]
        if repo not in scope_set:
            errors.append(f"out-of-scope decision: {repo}")
            continue
        by_repo_d[repo].append(decision)
    legal_ids: list[str] = []
    for repo in scope_repos:
        qrows = by_repo_q.get(repo, [])
        drows = by_repo_d.get(repo, [])
        if not qrows:
            if drows:
                errors.append(f"empty-queue decision for {repo}")
            continue
        stop_at, reason = _earliest_review_stop(
            drows,
            queue_count=len(qrows),
            max_reviewed=max_reviewed,
            target_pending=target_pending,
        )
        if stop_at < 0:
            errors.append(f"invalid early stop for {repo}")
            continue
        if len(drows) != stop_at:
            errors.append(
                f"submitted prefix {len(drows)} != earliest stop {stop_at} "
                f"({reason}) for {repo}"
            )
        legal_ids.extend(d["neutral_id"] for d in drows[:stop_at])
    got_ids = [d["neutral_id"] for d in decisions]
    if got_ids != legal_ids:
        errors.append(
            f"global decisions != legal per-repo prefixes: {got_ids!r} vs {legal_ids!r}"
        )
    return errors


def verify_handoff_summary_counts(
    handoff: dict[str, Any], *, handoff_path: Path
) -> list[str]:
    """Recompute totals/stop/pending/shortfalls from artifacts and compare strictly."""
    root = handoff_path.parent
    required = [
        "SCOPE.json",
        "QUOTAS.json",
        "REVIEW_QUEUE.json",
        "REVIEW_DECISIONS.json",
        "admission_sheet.cursor_candidate.csv",
        "EVIDENCE_SNAPSHOT.json",
    ]
    has_artifacts = all((root / name).is_file() for name in required)
    has_claims = any(
        key in handoff
        for key in (
            "decision_totals",
            "repository_review_counts",
            "quota_feasibility",
            "confirmations",
        )
    )
    if not has_artifacts:
        if has_claims:
            return ["summary claims present but admission artifacts missing"]
        # Hash/parent-only fixtures may omit the admission artifact set.
        return []
    errors: list[str] = []
    if not has_claims:
        return [
            "missing decision_totals / repository_review_counts / "
            "quota_feasibility / confirmations"
        ]

    scope = load_json(root / "SCOPE.json")
    quotas = load_json(root / "QUOTAS.json")
    queue = load_json(root / "REVIEW_QUEUE.json")["records"]
    decisions = load_json(root / "REVIEW_DECISIONS.json")["decisions"]
    errors.extend(verify_decision_guards(scope, queue, decisions))
    with (root / "admission_sheet.cursor_candidate.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        sheet_rows = list(csv.DictReader(handle))
    evidence_snapshot = load_json(root / "EVIDENCE_SNAPSHOT.json")
    try:
        expected = recompute_admission_summary(
            root=root,
            scope=scope,
            quotas=quotas,
            queue=queue,
            decisions=decisions,
            sheet_rows=sheet_rows,
            evidence_snapshot=evidence_snapshot,
        )
    except ValueError as exc:
        return [f"summary recompute failed: {exc}"]

    errors.extend(verify_confirmation_policy(expected["confirmations"]))
    errors.extend(
        _deep_equal(
            expected["decision_totals"],
            handoff.get("decision_totals"),
            path="decision_totals",
        )
    )
    errors.extend(
        _deep_equal(
            expected["repository_review_counts"],
            handoff.get("repository_review_counts"),
            path="repository_review_counts",
        )
    )
    errors.extend(
        _deep_equal(
            expected["quota_feasibility"],
            handoff.get("quota_feasibility"),
            path="quota_feasibility",
        )
    )
    errors.extend(
        _deep_equal(
            expected["confirmations"],
            handoff.get("confirmations"),
            path="confirmations",
        )
    )
    return errors


def verify_gate_binding(handoff: dict[str, Any], *, handoff_path: Path) -> list[str]:
    # Hash/parent-only fixtures may use alternate filenames without gate claims.
    if handoff_path.name != "HANDOFF_SUPPLEMENTAL_R2.json":
        return []
    errors: list[str] = []
    vlog_path = handoff_path.parent / "VERIFICATION_LOG.json"
    if not vlog_path.is_file():
        errors.append("missing VERIFICATION_LOG.json")
    file_sha = handoff.get("file_sha256") or {}
    expected_vl = file_sha.get("VERIFICATION_LOG.json")
    if not expected_vl:
        errors.append("handoff file_sha256 missing VERIFICATION_LOG.json")
    elif vlog_path.is_file():
        actual_vl = sha256_file(vlog_path)
        if actual_vl != expected_vl:
            errors.append(
                "VERIFICATION_LOG.json hash mismatch: "
                f"expected {expected_vl}, got {actual_vl}"
            )
    gate = handoff.get("gate_requested")
    if gate != EXPECTED_GATE:
        errors.append(f"handoff gate_requested {gate!r} != {EXPECTED_GATE!r}")
    if vlog_path.is_file():
        vlog = load_json(vlog_path)
        vgate = vlog.get("gate_requested")
        if vgate != EXPECTED_GATE:
            errors.append(
                f"verification_log gate_requested {vgate!r} != {EXPECTED_GATE!r}"
            )
        if gate != vgate:
            errors.append(
                f"gate mismatch between handoff and verification_log: "
                f"{gate!r} vs {vgate!r}"
            )
    return errors


def verify_confirmation_policy(confirmations: dict[str, bool]) -> list[str]:
    errors: list[str] = []
    if not confirmations.get("a2_all_pending"):
        errors.append("A2 is not all PENDING")
    if not confirmations.get("analysis_id_all_blank"):
        errors.append("analysis_id is not all blank")
    if not confirmations.get("forbidden_data_absent"):
        errors.append("forbidden data or downstream path present")
    if confirmations.get("readiness_ran"):
        errors.append("readiness sentinel detected")
    if confirmations.get("canonical_freeze_claimed"):
        errors.append("canonical freeze sentinel detected")
    if not confirmations.get("existing_files_unchanged"):
        errors.append("immutable inputs drifted from transport baseline")
    return errors


def verify_handoff_hashes(
    handoff_path: Path,
    *,
    cwd: Path | None = None,
    check_parent: bool = True,
    git_cwd: Path | None = None,
) -> int:
    cwd = cwd or Path.cwd()
    git_cwd = git_cwd or cwd
    handoff = load_json(handoff_path)
    mismatches: list[str] = []
    mismatches.extend(verify_gate_binding(handoff, handoff_path=handoff_path))

    for rel, expected in (handoff.get("file_sha256") or {}).items():
        # VERIFICATION_LOG.json is owned by verify_gate_binding (required + hash).
        if rel == "VERIFICATION_LOG.json":
            continue
        path = _resolve_declared_path(rel, handoff_path=handoff_path, cwd=cwd)
        if path is None:
            mismatches.append(f"missing file {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected}, got {actual}")

    for rel, expected in (handoff.get("evidence_sha256") or {}).items():
        path = _resolve_declared_path(rel, handoff_path=handoff_path, cwd=cwd)
        if path is None:
            mismatches.append(f"missing evidence {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected}, got {actual}")

    mismatches.extend(verify_handoff_summary_counts(handoff, handoff_path=handoff_path))

    # SELF resolution always attempted for reporting.
    resolved = resolve_self_commit(handoff, cwd=git_cwd)
    if (handoff.get("handoff_commit") or {}).get("value") == "SELF" and not resolved:
        mismatches.append("SELF resolution failed")

    if check_parent and (handoff.get("handoff_commit") or {}).get(
        "direct_parent_required"
    ):
        mismatches.extend(
            verify_parent_relationship(
                handoff, cwd=git_cwd, handoff_commit=resolved
            )
        )

    if mismatches:
        print("HASH_CHECK_FAIL", file=sys.stderr)
        for item in mismatches:
            print(f"ERROR: {item}", file=sys.stderr)
        return 1
    print("HASH_CHECK_OK")
    print(f"handoff_commit_resolved={resolved}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument(
        "--skip-parent-check",
        action="store_true",
        help="Skip git parent relationship check (fixture use)",
    )
    args = parser.parse_args(argv)
    return verify_handoff_hashes(
        args.handoff, check_parent=not args.skip_parent_check
    )


if __name__ == "__main__":
    raise SystemExit(main())
