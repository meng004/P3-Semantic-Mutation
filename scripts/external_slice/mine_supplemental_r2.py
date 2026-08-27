#!/usr/bin/env python3
"""Supplemental mining R2: GraphQL Repository.issues transport and builders."""

from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT_DEFAULT = Path("data/external_slice/supplemental_r2")
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

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
TOKEN_RE = re.compile(
    r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"Bearer\s+[A-Za-z0-9][A-Za-z0-9._-]{15,}|"
    r"Authorization:\s*\S+|sk-[A-Za-z0-9]{20,}",
    re.IGNORECASE,
)
FORBIDDEN_TRANSPORT_RE = re.compile(
    r"(?i)(/search/issues|\bgh\s+search\b|search\s*\(|"
    r"SearchResultItemConnection|/repos/[^/\s]+/[^/\s]+/issues\b|"
    r"pull.?request.?to.?issue|pr.?to.?issue)"
)
PROHIBITED_VOCAB_RE = re.compile(
    r"(?i)(mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|"
    r"\bkill\b|prediction|detection_result|\bfiber\b|\boperator\b|"
    r"(^|[^A-Za-z0-9_])(CE|OS|HP|TF|SI|fiber|stratum)([^A-Za-z0-9_]|$))"
)

GraphQLRunner = Callable[[str, dict[str, Any]], tuple[int, str, str]]


class HardFail(Exception):
    """Transport or identity hard failure; mint diagnostics only."""

    def __init__(self, invariant: str, detail: str = "") -> None:
        self.invariant = invariant
        self.detail = detail
        super().__init__(f"{invariant}: {detail}" if detail else invariant)


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def canonical_sha256(payload: Any) -> str:
    return sha256_bytes(canonical_json_bytes(payload))


def sanitize(text: str) -> str:
    if not text:
        return text
    return TOKEN_RE.sub("<REDACTED>", text)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def atomic_write_json(path: Path, payload: Any) -> None:
    """Write JSON via same-dir tempfile + fsync + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
        # Fsync directory entry for durability on POSIX.
        dir_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_match_text(text: str) -> str:
    return unicodedata.normalize("NFC", text or "").casefold()


def current_checkout_code_commit() -> str:
    """Return the full 40-hex SHA of the current checkout (git HEAD)."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise HardFail("illegal_code_commit", f"git rev-parse failed: {exc}") from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip() or "git rev-parse failed"
        raise HardFail("illegal_code_commit", detail)
    sha = proc.stdout.strip()
    if not FULL_SHA.fullmatch(sha):
        raise HardFail("illegal_code_commit", f"HEAD is not a full SHA: {sha!r}")
    return sha


def resolve_code_commit(cli_value: str | None = None) -> str:
    """Force code_commit to the current checkout SHA; reject conflicts/illegal values."""
    head = current_checkout_code_commit()
    if cli_value is None or cli_value == "":
        return head
    if not isinstance(cli_value, str) or not FULL_SHA.fullmatch(cli_value):
        raise HardFail("illegal_code_commit", f"illegal code_commit: {cli_value!r}")
    if cli_value != head:
        raise HardFail(
            "code_commit_conflict",
            f"cli code_commit {cli_value} != checkout {head}",
        )
    return head


def validate_run_id(run_id: str | None) -> str:
    if not isinstance(run_id, str) or not run_id.strip():
        raise HardFail("illegal_run_id", f"illegal run_id: {run_id!r}")
    text = run_id.strip()
    if any(ch.isspace() for ch in text):
        raise HardFail("illegal_run_id", f"illegal run_id: {run_id!r}")
    return text


def new_run_id() -> str:
    return str(uuid.uuid4())


def init_command_log(
    path: Path,
    *,
    run_id: str,
    code_commit: str,
) -> None:
    run_id = validate_run_id(run_id)
    if not FULL_SHA.fullmatch(code_commit):
        raise HardFail("illegal_code_commit", f"illegal code_commit: {code_commit!r}")
    atomic_write_json(
        path,
        {
            "schema_version": 1,
            "task": "SUPPLEMENTAL_MINING_R2",
            "run_id": run_id,
            "code_commit": code_commit,
            "entries": [],
        },
    )


def append_command_log(
    path: Path,
    entry: dict[str, Any],
    *,
    run_id: str | None = None,
    code_commit: str | None = None,
) -> None:
    if path.exists():
        payload = load_json(path)
    else:
        payload = {
            "schema_version": 1,
            "task": "SUPPLEMENTAL_MINING_R2",
            "entries": [],
        }
    payload.setdefault("schema_version", 1)
    payload.setdefault("task", "SUPPLEMENTAL_MINING_R2")
    payload.setdefault("entries", [])

    bound_run = validate_run_id(run_id) if run_id is not None else payload.get("run_id")
    bound_code = code_commit if code_commit is not None else payload.get("code_commit")
    if bound_run is None or bound_code is None:
        raise HardFail("run_code_unbound", "command log missing run_id/code_commit")
    bound_run = validate_run_id(str(bound_run))
    if not FULL_SHA.fullmatch(str(bound_code)):
        raise HardFail("illegal_code_commit", f"illegal code_commit: {bound_code!r}")

    existing_run = payload.get("run_id")
    existing_code = payload.get("code_commit")
    if existing_run is not None and existing_run != bound_run:
        raise HardFail(
            "run_id_conflict",
            f"log run_id {existing_run} != {bound_run}",
        )
    if existing_code is not None and existing_code != bound_code:
        raise HardFail(
            "code_commit_conflict",
            f"log code_commit {existing_code} != {bound_code}",
        )

    entry_run = entry.get("run_id", bound_run)
    entry_code = entry.get("code_commit", bound_code)
    if entry_run != bound_run:
        raise HardFail(
            "run_id_conflict",
            f"entry run_id {entry_run} != {bound_run}",
        )
    if entry_code != bound_code:
        raise HardFail(
            "code_commit_conflict",
            f"entry code_commit {entry_code} != {bound_code}",
        )

    payload["run_id"] = bound_run
    payload["code_commit"] = bound_code
    bound = dict(entry)
    bound["run_id"] = bound_run
    bound["code_commit"] = bound_code
    payload["entries"].append(bound)
    atomic_write_json(path, payload)


CANDIDATE_CLEANUP_NAMES = (
    "ISSUE_SNAPSHOT.json",
    "REVIEW_QUEUE.json",
    "REVIEW_DECISIONS.json",
    "EVIDENCE_SNAPSHOT.json",
    "admission_sheet.cursor_candidate.csv",
    "HANDOFF_SUPPLEMENTAL_R2.json",
    "PUBLISH_COMMIT.json",
    "transport_pages",
    "admission_evidence",
    ".publish_staging",
)

PUBLISH_DEATH_ENV = "SUPPLEMENTAL_R2_PUBLISH_DEATH_AT"
PUBLISH_DEATH_BOUNDARIES = (
    "after_stage",
    "after_pages_promote",
    "after_snapshot",
    "after_queue",
    "after_publish_commit",
    "after_cleanup",
)


def publish_death_checkpoint(boundary: str) -> None:
    """Real-death hook for promotion-boundary recovery tests (subprocess os._exit)."""
    if boundary not in PUBLISH_DEATH_BOUNDARIES:
        raise HardFail("illegal_publish_boundary", boundary)
    if os.environ.get(PUBLISH_DEATH_ENV, "") == boundary:
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(70)


def build_publish_commit_identity(
    *,
    run_id: str,
    code_commit: str,
    snapshot: dict[str, Any],
    transport_page_sha256: dict[str, str],
) -> dict[str, Any]:
    """Single hash-bound identity sealing retrieve publish completeness.

    Binds snapshot + transport pages (not mutable post-retrieve queue statuses),
    so sequential page/snapshot writes without this seal cannot pass as complete.
    """
    ordered_pages = {
        path: transport_page_sha256[path] for path in sorted(transport_page_sha256)
    }
    body = {
        "schema_version": 1,
        "task": "SUPPLEMENTAL_MINING_R2",
        "run_id": run_id,
        "code_commit": code_commit,
        "snapshot_sha256": canonical_sha256(snapshot),
        "page_manifest_sha256": snapshot.get("page_manifest_sha256"),
        "transport_pages": ordered_pages,
    }
    identity = dict(body)
    identity["publish_commit_sha256"] = canonical_sha256(body)
    return identity


def cleanup_candidate_artifacts(root: Path) -> None:
    for name in CANDIDATE_CLEANUP_NAMES:
        path = root / name
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    # Promote leftovers from interrupted crash-safe publish.
    for leftover in root.glob(".transport_pages.*"):
        if leftover.is_dir():
            shutil.rmtree(leftover)
        elif leftover.exists():
            leftover.unlink()


def publish_staging_root(root: Path) -> Path:
    return root / ".publish_staging"


def clear_orphan_publish_staging(root: Path, *, keep_run_id: str | None = None) -> None:
    staging_root = publish_staging_root(root)
    if not staging_root.is_dir():
        return
    for child in list(staging_root.iterdir()):
        if keep_run_id is not None and child.name == keep_run_id:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def crash_safe_publish(
    root: Path,
    *,
    run_id: str,
    code_commit: str,
    temp_pages: Path,
    snapshot: dict[str, Any],
    queue_payload: dict[str, Any],
) -> dict[str, Any]:
    """Stage pages/snapshot/queue, promote, then seal with PUBLISH_COMMIT.json.

    PUBLISH_COMMIT is the sole completeness identity: snapshot/queue/pages written
    sequentially without a matching commit must not be treated as a full result.
    """
    if snapshot.get("run_id") != run_id or snapshot.get("code_commit") != code_commit:
        raise HardFail("run_code_unbound", "snapshot binding mismatch at publish")
    if (
        queue_payload.get("run_id") != run_id
        or queue_payload.get("code_commit") != code_commit
    ):
        raise HardFail("run_code_unbound", "queue binding mismatch at publish")

    staging = publish_staging_root(root) / run_id
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    staged_pages = staging / "transport_pages"
    staged_pages.mkdir(parents=True)
    page_sha256: dict[str, str] = {}
    for page_file in sorted(temp_pages.glob("*.json")):
        dest = staged_pages / page_file.name
        shutil.copy2(page_file, dest)
        page_sha256[f"transport_pages/{page_file.name}"] = sha256_file(dest)
    publish_commit = build_publish_commit_identity(
        run_id=run_id,
        code_commit=code_commit,
        snapshot=snapshot,
        transport_page_sha256=page_sha256,
    )
    atomic_write_json(staging / "ISSUE_SNAPSHOT.json", snapshot)
    atomic_write_json(staging / "REVIEW_QUEUE.json", queue_payload)
    atomic_write_json(staging / "PUBLISH_COMMIT.json", publish_commit)
    publish_death_checkpoint("after_stage")

    promoting = root / f".transport_pages.{run_id}.promoting"
    old_pages = root / f".transport_pages.{run_id}.old"
    final_pages = root / "transport_pages"
    if promoting.exists():
        shutil.rmtree(promoting)
    shutil.copytree(staged_pages, promoting)
    if old_pages.exists():
        shutil.rmtree(old_pages)
    if final_pages.exists():
        final_pages.rename(old_pages)
    promoting.rename(final_pages)
    publish_death_checkpoint("after_pages_promote")

    atomic_write_json(root / "ISSUE_SNAPSHOT.json", snapshot)
    publish_death_checkpoint("after_snapshot")
    atomic_write_json(root / "REVIEW_QUEUE.json", queue_payload)
    publish_death_checkpoint("after_queue")
    # Seal last: without this identity, sequential artifacts are incomplete.
    atomic_write_json(root / "PUBLISH_COMMIT.json", publish_commit)
    publish_death_checkpoint("after_publish_commit")

    if old_pages.exists():
        shutil.rmtree(old_pages)
    shutil.rmtree(staging)
    staging_root = publish_staging_root(root)
    if staging_root.is_dir() and not any(staging_root.iterdir()):
        staging_root.rmdir()
    publish_death_checkpoint("after_cleanup")
    return publish_commit


def seal_failed_run_archive(
    root: Path,
    *,
    archive_id: str,
    command_log: Path | None = None,
    diagnostic: Path | None = None,
) -> Path:
    """Write-once, hash-bound archive of a failed retrieve log + diagnostic."""
    if not archive_id or any(ch in archive_id for ch in ("/", "\\", "..")):
        raise HardFail("illegal_archive_id", f"illegal archive_id: {archive_id!r}")
    dest = root / "failed_runs" / archive_id
    if dest.exists():
        raise HardFail(
            "archive_exists",
            f"refusing overwrite of sealed archive: {dest.as_posix()}",
        )
    log_src = command_log or (root / "COMMAND_LOG.json")
    diag_src = diagnostic or (root / "RETRIEVAL_HARD_FAIL.json")
    if not log_src.is_file():
        raise HardFail("archive_missing_log", str(log_src))
    if not diag_src.is_file():
        raise HardFail("archive_missing_diagnostic", str(diag_src))

    dest.mkdir(parents=True, exist_ok=False)
    log_dest = dest / "COMMAND_LOG.json"
    diag_dest = dest / "RETRIEVAL_HARD_FAIL.json"
    shutil.copy2(log_src, log_dest)
    shutil.copy2(diag_src, diag_dest)
    log_sha = sha256_file(log_dest)
    diag_sha = sha256_file(diag_dest)
    log_payload = load_json(log_dest)
    diag_payload = load_json(diag_dest)
    entries = log_payload.get("entries") if isinstance(log_payload, dict) else None
    manifest = {
        "schema_version": 1,
        "task": "SUPPLEMENTAL_MINING_R2",
        "archive_id": archive_id,
        "sealed": True,
        "write_once": True,
        "source_timestamp_utc": diag_payload.get("timestamp_utc"),
        "invariant": diag_payload.get("invariant"),
        "artifacts": {
            "COMMAND_LOG.json": {
                "sha256": log_sha,
                "entry_count": len(entries) if isinstance(entries, list) else None,
            },
            "RETRIEVAL_HARD_FAIL.json": {
                "sha256": diag_sha,
            },
        },
        "sealed_at_utc": utc_now(),
    }
    atomic_write_json(dest / "ARCHIVE_MANIFEST.json", manifest)
    for path in (log_dest, diag_dest, dest / "ARCHIVE_MANIFEST.json"):
        os.chmod(path, 0o444)
    try:
        os.chmod(dest, 0o555)
    except OSError:
        pass
    return dest


def write_terminal_failure(
    root: Path,
    *,
    invariant: str,
    detail: str,
    run_id: str,
    code_commit: str,
    command_log: Path,
) -> None:
    hard_fail_path = root / "RETRIEVAL_HARD_FAIL.json"
    record = {
        "schema_version": 1,
        "task": "SUPPLEMENTAL_MINING_R2",
        "invariant": invariant,
        "detail": sanitize(detail),
        "timestamp_utc": utc_now(),
        "run_id": run_id,
        "code_commit": code_commit,
        "terminal": True,
    }
    atomic_write_json(hard_fail_path, record)
    cleanup_candidate_artifacts(root)
    append_command_log(
        command_log,
        {
            "label": "retrieve_terminal_failure",
            "invariant": invariant,
            "detail": sanitize(detail),
            "timestamp_utc": utc_now(),
            "exit_code": 1,
            "terminal": True,
        },
        run_id=run_id,
        code_commit=code_commit,
    )


class RetrieveLock:
    """Non-blocking single-writer lock for live retrieve."""

    def __init__(self, root: Path) -> None:
        self.path = root / "RETRIEVE.lock"
        self._fd: int | None = None

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fd = os.open(str(self.path), os.O_CREAT | os.O_RDWR, 0o644)
        try:
            fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            os.ftruncate(self._fd, 0)
            os.write(
                self._fd,
                f"pid={os.getpid()} ts={utc_now()}\n".encode("utf-8"),
            )
            os.fsync(self._fd)
        except BlockingIOError as exc:
            os.close(self._fd)
            self._fd = None
            raise HardFail(
                "retrieve_lock_held",
                "another retrieve process holds RETRIEVE.lock",
            ) from exc

    def release(self) -> None:
        if self._fd is None:
            return
        try:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
        finally:
            os.close(self._fd)
            self._fd = None


def load_scope(root: Path) -> dict[str, Any]:
    scope = load_json(root / "SCOPE.json")
    if scope.get("task") != "SUPPLEMENTAL_MINING_R2":
        raise HardFail("scope_task", "SCOPE.json task must be SUPPLEMENTAL_MINING_R2")
    return scope


def load_transport(root: Path) -> dict[str, Any]:
    contract = load_json(root / "TRANSPORT_CONTRACT.json")
    if contract.get("task") != "SUPPLEMENTAL_MINING_R2":
        raise HardFail("transport_task", "TRANSPORT_CONTRACT task mismatch")
    doc = contract.get("query_document")
    if not isinstance(doc, str):
        raise HardFail("query_identity_drift", "missing query_document")
    actual = sha256_text(doc)
    expected = contract.get("query_document_sha256")
    if actual != expected:
        raise HardFail(
            "query_identity_drift",
            f"query_document_sha256 mismatch: expected {expected}, got {actual}",
        )
    if contract.get("transport") != "github_graphql_repository_issues":
        raise HardFail("forbidden_transport", "transport must be Repository.issues")
    return contract


def load_quotas(root: Path) -> dict[str, Any]:
    quotas = load_json(root / "QUOTAS.json")
    if quotas.get("task") != "SUPPLEMENTAL_MINING_R2":
        raise HardFail("quota_task", "QUOTAS.json task mismatch")
    return quotas


def refuse_forbidden_transport(command_text: str) -> None:
    if FORBIDDEN_TRANSPORT_RE.search(command_text):
        raise HardFail("forbidden_transport", command_text[:200])


def default_graphql_runner(query: str, variables: dict[str, Any]) -> tuple[int, str, str]:
    refuse_forbidden_transport(query)
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key in ("owner", "name"):
        if key not in variables:
            raise HardFail("query_identity_drift", f"missing variable {key}")
        cmd.extend(["-F", f"{key}={variables[key]}"])
    after = variables.get("after")
    if after is not None:
        cmd.extend(["-F", f"after={after}"])
    refuse_forbidden_transport(" ".join(cmd))
    # Pace live requests to reduce secondary rate-limit hard-fails.
    delay = float(os.environ.get("SUPPLEMENTAL_R2_GRAPHQL_DELAY_S", "0.35"))
    if delay > 0:
        time.sleep(delay)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def scrub_page_payload(payload: Any) -> Any:
    """Credential-scrub nested strings; preserve structure for replay."""
    if isinstance(payload, dict):
        return {k: scrub_page_payload(v) for k, v in payload.items()}
    if isinstance(payload, list):
        return [scrub_page_payload(v) for v in payload]
    if isinstance(payload, str):
        return sanitize(payload)
    return payload


def parse_created_at(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def validate_issue_node(node: Any, *, repository: str) -> dict[str, Any]:
    if not isinstance(node, dict):
        raise HardFail("typename_not_issue", "node is not an object")
    typename = node.get("__typename")
    if typename != "Issue":
        raise HardFail("typename_not_issue", f"got {typename!r}")
    state = node.get("state")
    if state != "CLOSED":
        raise HardFail("state_not_closed", f"got {state!r}")
    if node.get("closedAt") in (None, ""):
        raise HardFail("null_closed_at", f"issue {node.get('number')}")
    url = node.get("url") or ""
    if "/pull/" in url:
        raise HardFail("pull_url", url)
    number = node.get("number")
    if not isinstance(number, int):
        raise HardFail("malformed_json", "issue number missing")
    if "/" not in repository:
        raise HardFail("query_identity_drift", f"bad repository {repository!r}")
    owner, name = repository.split("/", 1)
    expected_url = f"https://github.com/{owner}/{name}/issues/{number}"
    if url != expected_url or "/pull/" in url:
        raise HardFail(
            "url_repository_mismatch",
            f"got {url!r} expected {expected_url!r}",
        )
    labels = node.get("labels") or {}
    page_info = labels.get("pageInfo") or {}
    if page_info.get("hasNextPage") is True:
        raise HardFail("incomplete_labels", f"{repository}#{number}")
    label_nodes = labels.get("nodes")
    if not isinstance(label_nodes, list):
        raise HardFail("incomplete_labels", f"{repository}#{number} labels.nodes")
    for lab in label_nodes:
        if not isinstance(lab, dict) or "name" not in lab:
            raise HardFail("incomplete_labels", f"{repository}#{number} label entry")
    for required in (
        "id",
        "title",
        "bodyText",
        "createdAt",
        "updatedAt",
        "closedAt",
    ):
        if required not in node or node[required] is None:
            raise HardFail("malformed_json", f"missing {required}")
    return node


def validate_page(
    payload: dict[str, Any],
    *,
    repository: str,
    page_index: int,
    expected_after: str | None,
    first_total_count: int | None,
    seen_cursors: set[str],
    seen_ids: set[str],
    seen_numbers: set[int],
    seen_urls: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]], str | None, bool, int]:
    if "errors" in payload and payload["errors"]:
        raise HardFail("graphql_errors", json.dumps(payload["errors"])[:300])
    data = payload.get("data")
    if not isinstance(data, dict):
        raise HardFail("malformed_json", "missing data")
    repo_obj = data.get("repository")
    if repo_obj is None:
        raise HardFail("null_repository", repository)
    issues = repo_obj.get("issues")
    if issues is None:
        raise HardFail("null_issues", repository)
    total_count = issues.get("totalCount")
    if not isinstance(total_count, int):
        raise HardFail("total_count_drift", "totalCount missing")
    if first_total_count is not None and total_count != first_total_count:
        raise HardFail(
            "total_count_drift",
            f"page {page_index}: {total_count} != {first_total_count}",
        )
    page_info = issues.get("pageInfo") or {}
    has_next = bool(page_info.get("hasNextPage"))
    end_cursor = page_info.get("endCursor")
    if expected_after is not None:
        # Continuity is enforced by the caller binding after=prev endCursor.
        pass
    if end_cursor is not None:
        if end_cursor in seen_cursors:
            raise HardFail("cursor_drift", f"repeated endCursor {end_cursor}")
        seen_cursors.add(end_cursor)
    nodes = issues.get("nodes")
    if not isinstance(nodes, list):
        raise HardFail("malformed_json", "issues.nodes missing")
    validated: list[dict[str, Any]] = []
    for node in nodes:
        issue = validate_issue_node(node, repository=repository)
        node_id = issue["id"]
        number = int(issue["number"])
        url = issue["url"]
        if node_id in seen_ids:
            raise HardFail("duplicate_node", node_id)
        if number in seen_numbers:
            raise HardFail("duplicate_number", str(number))
        if url in seen_urls:
            raise HardFail("duplicate_url", url)
        seen_ids.add(node_id)
        seen_numbers.add(number)
        seen_urls.add(url)
        validated.append(issue)
    return issues, validated, end_cursor, has_next, total_count


def match_surfaces(issue: dict[str, Any], phrase: str) -> list[str]:
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
    match_surfaces: dict[str, list[str]],
    source_page_index: int,
    source_page_sha256: str,
    query_document_sha256: str,
    variables_sha256: str,
    node_index: int,
    record_index: int,
) -> dict[str, Any]:
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
            p: list(match_surfaces.get(p, [])) for p in matched_phrases
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
    id_prefix: str,
    issues_with_meta: list[dict[str, Any]],
    query_document_sha256: str,
) -> list[dict[str, Any]]:
    """Apply cutoff, per-phrase top-20, union/dedupe, order, assign IDs."""
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
        # Preserve phrase order from frozen SCOPE phrases.
        matched = [p for p in phrases if p in entry["matched_phrases"]]
        record = build_snapshot_record(
            repository=repository,
            repository_order=repository_order,
            issue=item["issue"],
            matched_phrases=matched,
            match_surfaces=entry["match_surfaces"],
            source_page_index=item["source_page_index"],
            source_page_sha256=item["source_page_sha256"],
            query_document_sha256=query_document_sha256,
            variables_sha256=item["variables_sha256"],
            node_index=item["node_index"],
            record_index=idx,
        )
        records.append(record)
    return records


def build_queue_from_snapshot(
    scope: dict[str, Any], snapshot: dict[str, Any]
) -> list[dict[str, Any]]:
    """Pure function: reconstruct ordered review queue from snapshot records."""
    repos = scope["repositories"]
    prefix_by_repo = {r["repo"]: r["id_prefix"] for r in repos}
    order_by_repo = {r["repo"]: r["order"] for r in repos}
    records = list(snapshot.get("records") or [])
    # Group by repository, preserve snapshot order within each repo.
    by_repo: dict[str, list[dict[str, Any]]] = {r["repo"]: [] for r in repos}
    for rec in records:
        repo = rec["repository"]
        if repo not in by_repo:
            raise HardFail("repository_outside_scope", repo)
        by_repo[repo].append(rec)

    queue: list[dict[str, Any]] = []
    for repo_entry in repos:
        repo = repo_entry["repo"]
        prefix = prefix_by_repo[repo]
        repo_recs = by_repo[repo]
        # Enforce ordering invariant.
        expected = sorted(
            repo_recs,
            key=lambda r: (r["created_at"], int(r["issue_number"])),
            reverse=True,
        )
        if [r["issue_url"] for r in repo_recs] != [r["issue_url"] for r in expected]:
            raise HardFail("reordered_union", repo)
        for union_order, rec in enumerate(repo_recs, start=1):
            neutral_id = f"{prefix}{union_order:02d}"
            row = {
                "neutral_id": neutral_id,
                "union_order": union_order,
                "repository_review_order": union_order,
                "review_status": "PENDING_REVIEW",
                "snapshot_record_id": rec["snapshot_record_id"],
                "snapshot_record_sha256": rec["snapshot_record_sha256"],
                "repository": rec["repository"],
                "repository_order": rec["repository_order"],
                "issue_node_id": rec["issue_node_id"],
                "issue_number": rec["issue_number"],
                "issue_url": rec["issue_url"],
                "state": rec["state"],
                "created_at": rec["created_at"],
                "matched_phrases": list(rec["matched_phrases"]),
                "source_page_sha256": rec["source_page_sha256"],
            }
            if row["repository_order"] != order_by_repo[repo]:
                raise HardFail("repository_order", repo)
            queue.append(row)
    return queue


def earliest_review_stop(
    decisions: list[dict[str, Any]],
    *,
    queue_count: int,
    max_reviewed: int,
    target_pending: int,
) -> tuple[int, str]:
    """Return (prefix_len, reason) at the earliest stop along decisions.

    Stop candidates, in scan order: fifth ADMIT_PENDING_REPRO, 20th reviewed,
    queue exhaustion. ``prefix_len`` is 1-based length; ``0`` means empty queue.
    ``-1`` means the submitted prefix never reaches a stop.
    """
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
    """Return stop reason for a prefix that already matches earliest stop."""
    _stop_at, reason = earliest_review_stop(
        decisions,
        queue_count=queue_count,
        max_reviewed=max_reviewed,
        target_pending=target_pending,
    )
    return reason


def assert_review_stop_rule(
    repo: str,
    *,
    queue_rows: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    max_reviewed: int,
    target_pending: int,
) -> tuple[int, int, str]:
    """Enforce submitted prefix length equals the ordered earliest stop."""
    queue_count = len(queue_rows)
    decision_count = len(decisions)
    pending_count = sum(
        1 for d in decisions if d.get("decision") == "ADMIT_PENDING_REPRO"
    )
    if queue_count == 0:
        if decision_count:
            raise HardFail("empty_queue_decision", repo)
        return 0, 0, "queue_exhausted"
    if decision_count > queue_count:
        raise HardFail("extra_decision", repo)
    if decision_count > max_reviewed:
        raise HardFail("reviewed_over_cap", repo)
    if pending_count > target_pending:
        raise HardFail("pending_over_cap", repo)

    stop_at, reason = earliest_review_stop(
        decisions,
        queue_count=queue_count,
        max_reviewed=max_reviewed,
        target_pending=target_pending,
    )
    if stop_at < 0:
        raise HardFail(
            "review_stop_inconsistent",
            f"{repo}: invalid early stop "
            f"(decisions={decision_count}, queue={queue_count}, "
            f"pending={pending_count})",
        )
    if decision_count != stop_at:
        raise HardFail(
            "review_stop_inconsistent",
            f"{repo}: submitted prefix {decision_count} != earliest stop "
            f"{stop_at} ({reason})",
        )
    return decision_count, pending_count, reason


def apply_review_statuses(
    queue: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    *,
    max_reviewed: int,
    target_pending: int,
) -> list[dict[str, Any]]:
    """Mark REVIEWED for the decision prefix; remainder NOT_REVIEWED_AFTER_STOP."""
    by_repo_q: dict[str, list[dict[str, Any]]] = {}
    for row in queue:
        by_repo_q.setdefault(row["repository"], []).append(row)
    by_repo_d: dict[str, list[dict[str, Any]]] = {}
    for decision in decisions:
        by_repo_d.setdefault(decision["repository"], []).append(decision)

    updated: list[dict[str, Any]] = []
    for repo, rows in by_repo_q.items():
        dreviews = by_repo_d.get(repo, [])
        reviewed_n, _pending, _reason = assert_review_stop_rule(
            repo,
            queue_rows=rows,
            decisions=dreviews,
            max_reviewed=max_reviewed,
            target_pending=target_pending,
        )
        for idx, row in enumerate(rows):
            clone = dict(row)
            if idx < reviewed_n:
                clone["review_status"] = "REVIEWED"
            else:
                clone["review_status"] = "NOT_REVIEWED_AFTER_STOP"
            updated.append(clone)
    order = {
        (r["repository"], r["repository_review_order"]): i for i, r in enumerate(queue)
    }
    updated.sort(key=lambda r: order[(r["repository"], r["repository_review_order"])])
    return updated


def decision_is_valid(
    decision: dict[str, Any],
    *,
    exclusion_classes: set[str],
) -> None:
    a1 = decision.get("crit_real_public_fix")
    a3 = decision.get("crit_in_numerical_scope")
    a2 = decision.get("crit_dual_arm_repro")
    verdict = decision.get("decision")
    excl = decision.get("exclusion_class") or ""
    if a2 != "PENDING":
        raise HardFail("non_pending_a2", str(decision.get("neutral_id")))
    if decision.get("analysis_id") not in (None, ""):
        raise HardFail("nonblank_analysis_id", str(decision.get("neutral_id")))
    for text_key in ("mechanism", "decision_reason"):
        blob = decision.get(text_key) or ""
        if PROHIBITED_VOCAB_RE.search(blob):
            raise HardFail("forbidden_vocabulary", f"{decision.get('neutral_id')}:{text_key}")
    if a1 == "PASS":
        for field in ("buggy_sha", "fixed_sha"):
            if not FULL_SHA.match(str(decision.get(field) or "")):
                raise HardFail("short_sha", f"{decision.get('neutral_id')}:{field}")
        for field in ("public_issue_url", "public_fix_url"):
            if not decision.get(field):
                raise HardFail("missing_public_url", f"{decision.get('neutral_id')}:{field}")
    if verdict == "ADMIT_PENDING_REPRO":
        if a1 != "PASS" or a3 != "PASS" or a2 != "PENDING" or excl:
            raise HardFail("admit_inconsistency", str(decision.get("neutral_id")))
    elif verdict == "EXCLUDED":
        if excl:
            if excl not in exclusion_classes:
                raise HardFail("invalid_exclusion_class", excl)
        elif a1 == "PASS" and a3 == "PASS":
            raise HardFail("excluded_without_reason", str(decision.get("neutral_id")))
    else:
        raise HardFail("invalid_decision", str(verdict))


def validate_decisions_payload(
    *,
    scope: dict[str, Any],
    queue: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
) -> None:
    exclusion_classes = set(scope["exclusion_classes"])
    max_reviewed = int(scope["max_reviewed_per_repo"])
    target_pending = int(scope["target_pending_per_repo"])
    scope_repos = [entry["repo"] for entry in scope["repositories"]]
    scope_set = set(scope_repos)

    by_repo_queue: dict[str, list[dict[str, Any]]] = {repo: [] for repo in scope_repos}
    for row in queue:
        repo = row["repository"]
        if repo not in scope_set:
            raise HardFail("out_of_scope_queue_row", repo)
        by_repo_queue[repo].append(row)

    decisions_by_repo: dict[str, list[dict[str, Any]]] = {
        repo: [] for repo in scope_repos
    }
    for decision in decisions:
        repo = decision["repository"]
        if repo not in scope_set:
            raise HardFail("out_of_scope_decision", repo)
        decisions_by_repo[repo].append(decision)

    copied_fields = [
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

    expected: list[dict[str, Any]] = []
    for repo in scope_repos:
        qrows = by_repo_queue[repo]
        dreviews = decisions_by_repo[repo]
        if not qrows:
            if dreviews:
                raise HardFail("empty_queue_decision", repo)
            continue
        if not dreviews:
            raise HardFail(
                "review_stop_inconsistent",
                f"{repo}: no decisions for non-empty queue",
            )
        for idx, decision in enumerate(dreviews):
            if idx >= len(qrows):
                raise HardFail("extra_decision", repo)
            qrow = qrows[idx]
            # Binding is against the queue prefix order. Prior review_status
            # values may be stale until build-payload recomputes them.
            for field in copied_fields:
                if decision.get(field) != qrow.get(field):
                    raise HardFail(
                        "queue_decision_binding",
                        f"{decision.get('neutral_id')}:{field}",
                    )
            decision_is_valid(decision, exclusion_classes=exclusion_classes)

        assert_review_stop_rule(
            repo,
            queue_rows=qrows,
            decisions=dreviews,
            max_reviewed=max_reviewed,
            target_pending=target_pending,
        )
        expected.extend(dreviews)

    got_ids = [d.get("neutral_id") for d in decisions]
    expected_ids = [d.get("neutral_id") for d in expected]
    if got_ids != expected_ids:
        raise HardFail(
            "decision_prefix_order",
            f"global decisions != legal per-repo prefixes: {got_ids!r} vs {expected_ids!r}",
        )


def sheet_row_from_decision(decision: dict[str, Any]) -> dict[str, str]:
    return {
        "neutral_id": decision["neutral_id"],
        "source_cohort": "supplemental_r2",
        "repository": decision["repository"],
        "issue_url": decision["issue_url"],
        "buggy_sha": decision.get("buggy_sha") or "",
        "fixed_sha": decision.get("fixed_sha") or "",
        "mechanism": decision.get("mechanism") or "",
        "crit_real_public_fix": decision["crit_real_public_fix"],
        "crit_dual_arm_repro": "PENDING",
        "crit_in_numerical_scope": decision["crit_in_numerical_scope"],
        "decision": decision["decision"],
        "decision_reason": decision.get("decision_reason") or "",
        "analysis_id": "",
    }


def evidence_from_decision(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "neutral_id": decision["neutral_id"],
        "snapshot_record_id": decision["snapshot_record_id"],
        "snapshot_record_sha256": decision["snapshot_record_sha256"],
        "repository": decision["repository"],
        "issue_node_id": decision["issue_node_id"],
        "issue_number": decision["issue_number"],
        "issue_url": decision["issue_url"],
        "buggy_sha": decision.get("buggy_sha") or "",
        "fixed_sha": decision.get("fixed_sha") or "",
        "public_issue_url": decision.get("public_issue_url") or "",
        "public_fix_url": decision.get("public_fix_url") or "",
        "mechanism": decision.get("mechanism") or "",
        "exclusion_class": decision.get("exclusion_class") or "",
        "crit_real_public_fix": decision["crit_real_public_fix"],
        "crit_dual_arm_repro": "PENDING",
        "crit_in_numerical_scope": decision["crit_in_numerical_scope"],
        "decision": decision["decision"],
        "source_cohort": "supplemental_r2",
        "analysis_id": "",
    }


def write_sheet(path: Path, rows: list[dict[str, str]]) -> None:
    """Write admission CSV with fixed LF line endings (no CR)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="\n", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=SHEET_HEADER, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def retrieve_repository_pages(
    *,
    root: Path,
    repo_entry: dict[str, Any],
    contract: dict[str, Any],
    runner: GraphQLRunner,
    command_log: Path,
    temp_pages: Path,
    run_id: str,
    code_commit: str,
    seen_ids: set[str],
    seen_urls: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    query = contract["query_document"]
    query_sha = contract["query_document_sha256"]
    if sha256_text(query) != query_sha:
        raise HardFail("query_identity_drift", "inline/changed query document")
    if "search(" in query or "SearchResultItemConnection" in query:
        raise HardFail("forbidden_transport", "search in query document")

    owner = repo_entry["owner"]
    name = repo_entry["name"]
    repository = repo_entry["repo"]
    after: str | None = None
    page_index = 0
    first_total: int | None = None
    seen_cursors: set[str] = set()
    # Issue numbers are unique within a repository; IDs/URLs are global.
    seen_numbers: set[int] = set()
    ids_before = len(seen_ids)
    issues_with_meta: list[dict[str, Any]] = []
    page_manifest: list[dict[str, Any]] = []
    has_next = True

    while has_next:
        variables = {"owner": owner, "name": name, "after": after}
        variables_sha = canonical_sha256(variables)
        started = utc_now()
        exit_code = 1
        stdout = ""
        stderr = ""
        runner_fail: HardFail | None = None
        try:
            exit_code, stdout, stderr = runner(query, variables)
        except HardFail as exc:
            runner_fail = exc
            exit_code = 1
            stdout = ""
            stderr = sanitize(str(exc))
        except Exception as exc:  # noqa: BLE001 — still emit one page record
            runner_fail = HardFail("unexpected_error", str(exc))
            exit_code = 1
            stdout = ""
            stderr = sanitize(str(exc))
        ended = utc_now()
        stdout_s = sanitize(stdout)
        stderr_s = sanitize(stderr)
        response_sha = sha256_text(stdout_s)
        page_entry: dict[str, Any] = {
            "repository": repository,
            "page_index": page_index,
            "operation_name": contract["operation_name"],
            "query_document_sha256": query_sha,
            "variables": variables,
            "variables_sha256": variables_sha,
            "after": after,
            "response_page_sha256": response_sha,
            "exit_code": exit_code,
            "stderr_sha256": sha256_text(stderr_s),
            "started_at_utc": started,
            "ended_at_utc": ended,
            "cli": list(contract["cli"]),
            "page_ok": False,
        }

        hard_fail: HardFail | None = runner_fail
        payload: dict[str, Any] | None = None
        nodes: list[dict[str, Any]] = []
        end_cursor: str | None = None
        total_count = 0
        if hard_fail is None and exit_code != 0:
            hard_fail = HardFail(
                "nonzero_exit",
                f"{repository} page {page_index}: {exit_code}",
            )
        if hard_fail is None:
            try:
                loaded = json.loads(stdout)
            except json.JSONDecodeError as exc:
                hard_fail = HardFail("malformed_json", str(exc))
            else:
                if not isinstance(loaded, dict):
                    hard_fail = HardFail("malformed_json", "page payload not an object")
                else:
                    payload = loaded
        if hard_fail is None and payload is not None:
            try:
                _issues, nodes, end_cursor, has_next, total_count = validate_page(
                    payload,
                    repository=repository,
                    page_index=page_index,
                    expected_after=after,
                    first_total_count=first_total,
                    seen_cursors=seen_cursors,
                    seen_ids=seen_ids,
                    seen_numbers=seen_numbers,
                    seen_urls=seen_urls,
                )
            except HardFail as exc:
                hard_fail = exc

        if hard_fail is None:
            # Verified pageInfo only after validate_page succeeds.
            page_entry["endCursor"] = end_cursor
            page_entry["hasNextPage"] = has_next
            page_entry["page_ok"] = True
            if has_next and not end_cursor:
                hard_fail = HardFail("cursor_drift", "hasNextPage without endCursor")
                page_entry["page_ok"] = False
                page_entry["invariant"] = hard_fail.invariant
                page_entry["detail"] = hard_fail.detail
            else:
                page_entry["invariant"] = None
        else:
            page_entry["invariant"] = hard_fail.invariant
            page_entry["detail"] = sanitize(hard_fail.detail)

        # Exactly one page record per runner invocation, including failures.
        append_command_log(
            command_log,
            page_entry,
            run_id=run_id,
            code_commit=code_commit,
        )
        if hard_fail is not None:
            raise hard_fail

        if first_total is None:
            first_total = total_count
        assert payload is not None
        page_name = (
            f"{repo_entry['order']:02d}_{owner}_{name}_page_{page_index:04d}.json"
        )
        page_path = temp_pages / page_name
        scrubbed = scrub_page_payload(payload)
        write_json(page_path, scrubbed)
        page_sha = sha256_file(page_path)
        page_manifest.append(
            {
                "repository": repository,
                "repository_order": repo_entry["order"],
                "page_index": page_index,
                "path": f"transport_pages/{page_name}",
                "sha256": page_sha,
                "after": after,
                "endCursor": end_cursor,
                "hasNextPage": has_next,
                "totalCount": total_count,
                "node_count": len(nodes),
                "variables_sha256": variables_sha,
                "response_page_sha256": response_sha,
                "variables": variables,
            }
        )
        for node_index, node in enumerate(nodes):
            issues_with_meta.append(
                {
                    "issue": node,
                    "source_page_index": page_index,
                    "source_page_sha256": page_sha,
                    "variables_sha256": variables_sha,
                    "node_index": node_index,
                }
            )
        if has_next:
            # Bind next request after to this verified endCursor.
            after = end_cursor
        page_index += 1

    if first_total is None:
        raise HardFail("incomplete_pagination", f"no pages for {repository}")
    unique_count = len(seen_ids) - ids_before
    if unique_count != first_total:
        raise HardFail(
            "incomplete_pagination",
            f"{repository}: unique={unique_count} totalCount={first_total}",
        )
    # Terminal page already required has_next False by loop exit.
    return page_manifest, issues_with_meta


def cmd_retrieve(
    root: Path,
    *,
    runner: GraphQLRunner | None = None,
    run_id: str | None = None,
    code_commit: str | None = None,
) -> int:
    command_log = root / "COMMAND_LOG.json"
    hard_fail_path = root / "RETRIEVAL_HARD_FAIL.json"

    active_runner = runner or default_graphql_runner
    lock = RetrieveLock(root)
    lock_acquired = False
    log_owned = False
    bound_run_id: str | None = None
    bound_code_commit: str | None = None

    try:
        # Resolve binding before lock so illegal/conflicting code_commit fails
        # closed without claiming the writer lock when possible. Lock losers
        # still must perform zero filesystem mutations (see except paths).
        bound_run_id = validate_run_id(run_id or new_run_id())
        bound_code_commit = resolve_code_commit(code_commit)

        # Non-blocking single-writer lock before any network call / owner write.
        lock.acquire()
        lock_acquired = True

        # Owner recovers orphan staging / promote leftovers from prior crashes.
        clear_orphan_publish_staging(root)
        for leftover in root.glob(".transport_pages.*"):
            if leftover.is_dir():
                shutil.rmtree(leftover)
            elif leftover.exists():
                leftover.unlink()

        # Fresh per-run log bound to immutable run_id + code_commit.
        # Only the lock holder may create/replace this run's command log.
        init_command_log(
            command_log,
            run_id=bound_run_id,
            code_commit=bound_code_commit,
        )
        log_owned = True
        append_command_log(
            command_log,
            {
                "label": "retrieve_start",
                "timestamp_utc": utc_now(),
                "exit_code": 0,
            },
            run_id=bound_run_id,
            code_commit=bound_code_commit,
        )

        scope = load_scope(root)
        contract = load_transport(root)
        load_quotas(root)
        if contract.get("created_cutoff") != scope.get("created_cutoff"):
            raise HardFail("query_identity_drift", "cutoff mismatch scope/transport")
        if contract.get("operation_name") != "SupplementalR2RepositoryIssues":
            raise HardFail("query_identity_drift", "operation_name")
        if contract.get("page_size") != 100:
            raise HardFail("query_identity_drift", "page_size")
        if contract.get("states") != ["CLOSED"]:
            raise HardFail("query_identity_drift", "states")
        if contract.get("order_by") != {"field": "CREATED_AT", "direction": "DESC"}:
            raise HardFail("query_identity_drift", "order_by")

        with tempfile.TemporaryDirectory(prefix="r2_pages_") as tmp:
            temp_pages = Path(tmp)
            all_manifest: list[dict[str, Any]] = []
            all_records: list[dict[str, Any]] = []
            shared_node_ids: set[str] = set()
            shared_urls: set[str] = set()
            for repo_entry in scope["repositories"]:
                manifest, issues_meta = retrieve_repository_pages(
                    root=root,
                    repo_entry=repo_entry,
                    contract=contract,
                    runner=active_runner,
                    command_log=command_log,
                    temp_pages=temp_pages,
                    run_id=bound_run_id,
                    code_commit=bound_code_commit,
                    seen_ids=shared_node_ids,
                    seen_urls=shared_urls,
                )
                all_manifest.extend(manifest)
                records = select_phrase_union(
                    scope=scope,
                    repository=repo_entry["repo"],
                    repository_order=repo_entry["order"],
                    id_prefix=repo_entry["id_prefix"],
                    issues_with_meta=issues_meta,
                    query_document_sha256=contract["query_document_sha256"],
                )
                all_records.extend(records)

            snapshot = {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "run_id": bound_run_id,
                "code_commit": bound_code_commit,
                "query_document_sha256": contract["query_document_sha256"],
                "created_cutoff": scope["created_cutoff"],
                "page_manifest": all_manifest,
                "page_manifest_sha256": canonical_sha256(all_manifest),
                "records": all_records,
            }
            queue_payload = {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "run_id": bound_run_id,
                "code_commit": bound_code_commit,
                "records": build_queue_from_snapshot(scope, snapshot),
            }
            crash_safe_publish(
                root,
                run_id=bound_run_id,
                code_commit=bound_code_commit,
                temp_pages=temp_pages,
                snapshot=snapshot,
                queue_payload=queue_payload,
            )
        if hard_fail_path.exists():
            hard_fail_path.unlink()
        append_command_log(
            command_log,
            {
                "label": "retrieve_success",
                "timestamp_utc": utc_now(),
                "exit_code": 0,
                "terminal": True,
            },
            run_id=bound_run_id,
            code_commit=bound_code_commit,
        )
        return 0
    except HardFail as exc:
        if log_owned:
            assert bound_run_id is not None and bound_code_commit is not None
            write_terminal_failure(
                root,
                invariant=exc.invariant,
                detail=exc.detail,
                run_id=bound_run_id,
                code_commit=bound_code_commit,
                command_log=command_log,
            )
        # Lock loser / pre-ownership failure: zero filesystem mutations.
        print(f"ERROR: {exc.invariant}: {exc.detail}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — fail closed
        if log_owned:
            assert bound_run_id is not None and bound_code_commit is not None
            write_terminal_failure(
                root,
                invariant="unexpected_error",
                detail=str(exc),
                run_id=bound_run_id,
                code_commit=bound_code_commit,
                command_log=command_log,
            )
        # Lock loser / pre-ownership failure: zero filesystem mutations.
        print(f"ERROR: unexpected_error: {exc}", file=sys.stderr)
        return 1
    finally:
        if lock_acquired:
            lock.release()


def cmd_build_queue(root: Path) -> int:
    try:
        scope = load_scope(root)
        snapshot = load_json(root / "ISSUE_SNAPSHOT.json")
        run_id = validate_run_id(snapshot.get("run_id"))
        code_commit = snapshot.get("code_commit")
        if not isinstance(code_commit, str) or not FULL_SHA.fullmatch(code_commit):
            raise HardFail(
                "illegal_code_commit",
                f"snapshot illegal code_commit: {code_commit!r}",
            )
        records = build_queue_from_snapshot(scope, snapshot)
        atomic_write_json(
            root / "REVIEW_QUEUE.json",
            {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "run_id": run_id,
                "code_commit": code_commit,
                "records": records,
            },
        )
        return 0
    except HardFail as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_validate_decisions(root: Path) -> int:
    try:
        scope = load_scope(root)
        queue = load_json(root / "REVIEW_QUEUE.json")["records"]
        decisions = load_json(root / "REVIEW_DECISIONS.json")["decisions"]
        validate_decisions_payload(scope=scope, queue=queue, decisions=decisions)
        print("DECISIONS_OK")
        return 0
    except HardFail as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_build_payload(root: Path) -> int:
    try:
        scope = load_scope(root)
        queue_payload = load_json(root / "REVIEW_QUEUE.json")
        decisions_payload = load_json(root / "REVIEW_DECISIONS.json")
        decisions = decisions_payload["decisions"]
        queue = queue_payload["records"]
        validate_decisions_payload(scope=scope, queue=queue, decisions=decisions)

        # Update review statuses on queue copy for persistence.
        max_reviewed = int(scope["max_reviewed_per_repo"])
        target_pending = int(scope["target_pending_per_repo"])
        updated_queue = apply_review_statuses(
            queue,
            decisions,
            max_reviewed=max_reviewed,
            target_pending=target_pending,
        )
        # Reject decisions that target NOT_REVIEWED_AFTER_STOP rows.
        status_by_id = {r["neutral_id"]: r["review_status"] for r in updated_queue}
        for d in decisions:
            if status_by_id.get(d["neutral_id"]) == "NOT_REVIEWED_AFTER_STOP":
                raise HardFail("decision_for_unreviewed", d["neutral_id"])

        run_id = validate_run_id(queue_payload.get("run_id"))
        code_commit = queue_payload.get("code_commit")
        if not isinstance(code_commit, str) or not FULL_SHA.fullmatch(code_commit):
            raise HardFail(
                "illegal_code_commit",
                f"queue illegal code_commit: {code_commit!r}",
            )
        atomic_write_json(
            root / "REVIEW_QUEUE.json",
            {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "run_id": run_id,
                "code_commit": code_commit,
                "records": updated_queue,
            },
        )

        sheet_rows = [sheet_row_from_decision(d) for d in decisions]
        write_sheet(root / "admission_sheet.cursor_candidate.csv", sheet_rows)

        evidence_root = root / "admission_evidence"
        if evidence_root.exists():
            shutil.rmtree(evidence_root)
        evidence_root.mkdir(parents=True, exist_ok=True)
        manifest: list[dict[str, Any]] = []
        for decision in decisions:
            evidence = evidence_from_decision(decision)
            case_dir = evidence_root / decision["neutral_id"]
            case_dir.mkdir(parents=True, exist_ok=True)
            path = case_dir / "evidence.json"
            write_json(path, evidence)
            rel = f"admission_evidence/{decision['neutral_id']}/evidence.json"
            manifest.append(
                {
                    "neutral_id": decision["neutral_id"],
                    "path": rel,
                    "sha256": sha256_file(path),
                }
            )
        write_json(
            root / "EVIDENCE_SNAPSHOT.json",
            {
                "schema_version": 1,
                "task": "SUPPLEMENTAL_MINING_R2",
                "records": manifest,
            },
        )
        print("PAYLOAD_OK")
        return 0
    except HardFail as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def project_quota_feasibility(
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


def compute_confirmations(
    *,
    root: Path,
    scope: dict[str, Any],
    decisions: list[dict[str, Any]],
    repo_root: Path | None = None,
) -> dict[str, bool]:
    """Prove confirmations from decisions, baseline hashes, command logs, path scan."""
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



def compute_admission_summary(
    *,
    root: Path,
    scope: dict[str, Any],
    quotas: dict[str, Any],
    queue: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Compute decision totals, per-repo counts, stop reasons, and shortfalls."""
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

    feasibility = project_quota_feasibility(quotas, decisions)
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
        "confirmations": compute_confirmations(
            root=root, scope=scope, decisions=decisions, repo_root=repo_root
        ),
    }


def cmd_write_handoff(root: Path, payload_commit: str) -> int:
    try:
        scope = load_scope(root)
        contract = load_transport(root)
        quotas = load_quotas(root)
        decisions = load_json(root / "REVIEW_DECISIONS.json")["decisions"]
        queue = load_json(root / "REVIEW_QUEUE.json")["records"]
        repo_root = Path(__file__).resolve().parents[2]
        summary = compute_admission_summary(
            root=root,
            scope=scope,
            quotas=quotas,
            queue=queue,
            decisions=decisions,
            repo_root=repo_root,
        )

        def rel_sha(name: str) -> str:
            return sha256_file(root / name)

        file_sha256 = {
            "SCOPE.json": rel_sha("SCOPE.json"),
            "TRANSPORT_CONTRACT.json": rel_sha("TRANSPORT_CONTRACT.json"),
            "QUOTAS.json": rel_sha("QUOTAS.json"),
            "ISSUE_SNAPSHOT.json": rel_sha("ISSUE_SNAPSHOT.json"),
            "REVIEW_QUEUE.json": rel_sha("REVIEW_QUEUE.json"),
            "REVIEW_DECISIONS.json": rel_sha("REVIEW_DECISIONS.json"),
            "EVIDENCE_SNAPSHOT.json": rel_sha("EVIDENCE_SNAPSHOT.json"),
            "admission_sheet.cursor_candidate.csv": rel_sha(
                "admission_sheet.cursor_candidate.csv"
            ),
            "COMMAND_LOG.json": rel_sha("COMMAND_LOG.json"),
            "scripts/external_slice/mine_supplemental_r2.py": sha256_file(
                repo_root / "scripts/external_slice/mine_supplemental_r2.py"
            ),
            "scripts/external_slice/check_supplemental_r2_admission.py": sha256_file(
                repo_root / "scripts/external_slice/check_supplemental_r2_admission.py"
            ),
            "scripts/external_slice/check_supplemental_r2_handoff_hashes.py": sha256_file(
                repo_root / "scripts/external_slice/check_supplemental_r2_handoff_hashes.py"
            ),
            "tests/external_slice/test_mine_supplemental_r2.py": sha256_file(
                repo_root / "tests/external_slice/test_mine_supplemental_r2.py"
            ),
            "tests/external_slice/test_check_supplemental_r2_admission.py": sha256_file(
                repo_root / "tests/external_slice/test_check_supplemental_r2_admission.py"
            ),
        }
        if not (root / "VERIFICATION_LOG.json").is_file():
            raise HardFail(
                "missing_verification_log",
                "VERIFICATION_LOG.json is required before write-handoff",
            )
        file_sha256["VERIFICATION_LOG.json"] = rel_sha("VERIFICATION_LOG.json")
        evidence_sha256 = {}
        for path in sorted((root / "admission_evidence").rglob("evidence.json")):
            rel = path.relative_to(root).as_posix()
            evidence_sha256[rel] = sha256_file(path)

        handoff = {
            "schema_version": 1,
            "task": "SUPPLEMENTAL_MINING_R2",
            "gate_requested": EXPECTED_GATE,
            "design_baseline_commit": scope.get("baseline_commit"),
            "payload_commit": payload_commit,
            "handoff_commit": {
                "value": "SELF",
                "direct_parent_required": payload_commit,
                "resolution": (
                    "Resolve immutable handoff SHA with `git rev-parse HEAD`; "
                    "direct parent must equal payload_commit."
                ),
            },
            "file_sha256": file_sha256,
            "evidence_sha256": evidence_sha256,
            "quota_feasibility": summary["quota_feasibility"],
            "decision_totals": summary["decision_totals"],
            "repository_review_counts": summary["repository_review_counts"],
            "verification_log": "VERIFICATION_LOG.json",
            "confirmations": summary["confirmations"],
            "transport": contract.get("transport"),
            "created_at_utc": utc_now(),
        }
        write_json(root / "HANDOFF_SUPPLEMENTAL_R2.json", handoff)
        print("HANDOFF_OK")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_ret = sub.add_parser("retrieve", help="Fetch complete Repository.issues pages")
    p_ret.add_argument("--root", type=Path, default=ROOT_DEFAULT)

    p_q = sub.add_parser("build-queue", help="Rebuild REVIEW_QUEUE from snapshot")
    p_q.add_argument("--root", type=Path, default=ROOT_DEFAULT)

    p_v = sub.add_parser("validate-decisions", help="Validate REVIEW_DECISIONS binding")
    p_v.add_argument("--root", type=Path, default=ROOT_DEFAULT)

    p_b = sub.add_parser("build-payload", help="Build sheet + evidence from decisions")
    p_b.add_argument("--root", type=Path, default=ROOT_DEFAULT)

    p_h = sub.add_parser("write-handoff", help="Write handoff manifest")
    p_h.add_argument("--root", type=Path, default=ROOT_DEFAULT)
    p_h.add_argument("--payload-commit", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root: Path = args.root
    if args.command == "retrieve":
        return cmd_retrieve(root)
    if args.command == "build-queue":
        return cmd_build_queue(root)
    if args.command == "validate-decisions":
        return cmd_validate_decisions(root)
    if args.command == "build-payload":
        return cmd_build_payload(root)
    if args.command == "write-handoff":
        return cmd_write_handoff(root, args.payload_commit)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
