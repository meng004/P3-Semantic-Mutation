"""Fail-closed content-addressed snapshot-to-revision join."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from p3_v3.artifacts import EvidenceError, validate_sha256

_REPO_RE = re.compile(
    r"^(?:github\.com|gitlab\.com)/[a-z0-9][a-z0-9-]{0,38}/[a-z0-9][a-z0-9._-]{0,99}$"
)


def validate_originating_repository_identity(value: object, field: str) -> str:
    if not isinstance(value, str) or _REPO_RE.fullmatch(value) is None:
        raise EvidenceError("IDENTITY_CONFLICT", f"{field} is not a canonical repository identity")
    return value


def join_unique_content_identities(
    pending: Sequence[Mapping[str, object]],
    candidates: Sequence[Mapping[str, object]],
) -> tuple[dict[str, str], tuple[dict[str, object], ...]]:
    """Join pending snapshots to candidates only on exact archive and tree SHA.

    Each candidate may match at most one snapshot, and each snapshot may match
    at most one candidate. Archive-only or tree-only equality is a conflict.
    """

    pending_rows = []
    pending_ids: set[str] = set()
    archive_to_snapshot: dict[str, str] = {}
    tree_to_snapshot: dict[str, str] = {}
    for index, raw in enumerate(pending):
        snapshot = validate_sha256(raw.get("neutral_snapshot_id"), f"pending[{index}].neutral_snapshot_id")
        archive = validate_sha256(raw.get("source_archive_sha256"), f"pending[{index}].source_archive_sha256")
        tree = validate_sha256(
            raw.get("normalized_source_tree_sha256"),
            f"pending[{index}].normalized_source_tree_sha256",
        )
        if snapshot in pending_ids:
            raise EvidenceError("SOURCE_IDENTITY_CONFLICT", "duplicate pending snapshot")
        if archive in archive_to_snapshot or tree in tree_to_snapshot:
            raise EvidenceError("SOURCE_IDENTITY_CONFLICT", "pending SHA pairs are not unique")
        pending_ids.add(snapshot)
        archive_to_snapshot[archive] = snapshot
        tree_to_snapshot[tree] = snapshot
        pending_rows.append((snapshot, archive, tree))

    snapshot_hits: dict[str, list[dict[str, object]]] = {snapshot: [] for snapshot, _, _ in pending_rows}
    candidate_hits: dict[int, list[str]] = {}

    for index, raw in enumerate(candidates):
        repository = validate_originating_repository_identity(
            raw.get("originating_repository_identity") or raw.get("repository"),
            f"candidates[{index}].repository",
        )
        archive = validate_sha256(raw.get("source_archive_sha256"), f"candidates[{index}].source_archive_sha256")
        tree = validate_sha256(
            raw.get("normalized_source_tree_sha256"),
            f"candidates[{index}].normalized_source_tree_sha256",
        )
        archive_match = archive_to_snapshot.get(archive)
        tree_match = tree_to_snapshot.get(tree)
        if archive_match is None and tree_match is None:
            continue
        if archive_match is None or tree_match is None or archive_match != tree_match:
            raise EvidenceError(
                "SOURCE_IDENTITY_CONFLICT",
                "archive SHA and tree SHA must match the same pending snapshot",
            )
        payload = {
            "neutral_snapshot_id": archive_match,
            "originating_repository_identity": repository,
            "public_ref": raw.get("public_ref") or raw.get("rev") or raw.get("commit"),
            "commit": raw.get("commit"),
            "git_tree_oid": raw.get("git_tree_oid"),
            "source_archive_sha256": archive,
            "normalized_source_tree_sha256": tree,
        }
        snapshot_hits[archive_match].append(payload)
        candidate_hits.setdefault(index, []).append(archive_match)

    unmatched = [snapshot for snapshot, hits in snapshot_hits.items() if not hits]
    multiple = [snapshot for snapshot, hits in snapshot_hits.items() if len(hits) > 1]
    candidate_multi = [index for index, hits in candidate_hits.items() if len(hits) > 1]
    if multiple or candidate_multi:
        raise EvidenceError("SOURCE_IDENTITY_CONFLICT", "content identity join is not bijective")
    if unmatched:
        raise EvidenceError(
            "SOURCE_IDENTITY_JOIN_PARTIAL",
            f"{len(unmatched)} pending snapshot(s) have no unique content match",
        )

    mapping = {
        snapshot: hits[0]["originating_repository_identity"]
        for snapshot, hits in snapshot_hits.items()
    }
    records = tuple(snapshot_hits[snapshot][0] for snapshot, _, _ in pending_rows)
    return mapping, records
