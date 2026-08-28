from __future__ import annotations

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.content_addressed_source_join import join_unique_content_identities


def _pending(*pairs: tuple[str, str, str]) -> list[dict[str, str]]:
    rows = []
    for snapshot, archive, tree in pairs:
        rows.append(
            {
                "neutral_snapshot_id": snapshot,
                "source_archive_sha256": archive,
                "normalized_source_tree_sha256": tree,
            }
        )
    return rows


def _candidate(repo: str, archive: str, tree: str, commit: str = "c" * 40) -> dict[str, str]:
    return {
        "originating_repository_identity": repo,
        "source_archive_sha256": archive,
        "normalized_source_tree_sha256": tree,
        "commit": commit,
        "git_tree_oid": "t" * 40,
        "public_ref": commit,
    }


A1 = "a" * 64
A2 = "b" * 64
T1 = "c" * 64
T2 = "d" * 64
S1 = "e" * 64
S2 = "f" * 64
X = "1" * 64
Y = "2" * 64


def test_unique_archive_and_tree_pairs_form_a_bijection():
    mapping, records = join_unique_content_identities(
        _pending((S1, A1, T1), (S2, A2, T2)),
        [
            _candidate("github.com/scipy/scipy", A1, T1),
            _candidate("github.com/lammps/lammps", A2, T2),
        ],
    )
    assert mapping == {
        S1: "github.com/scipy/scipy",
        S2: "github.com/lammps/lammps",
    }
    assert [row["neutral_snapshot_id"] for row in records] == [S1, S2]


def test_archive_or_tree_only_match_is_conflict():
    with pytest.raises(EvidenceError, match="SOURCE_IDENTITY_CONFLICT"):
        join_unique_content_identities(
            _pending((S1, A1, T1)),
            [_candidate("github.com/scipy/scipy", A1, X)],
        )
    with pytest.raises(EvidenceError, match="SOURCE_IDENTITY_CONFLICT"):
        join_unique_content_identities(
            _pending((S1, A1, T1)),
            [_candidate("github.com/scipy/scipy", Y, T1)],
        )


def test_duplicate_or_zero_match_is_fail_closed():
    with pytest.raises(EvidenceError, match="SOURCE_IDENTITY_CONFLICT"):
        join_unique_content_identities(
            _pending((S1, A1, T1)),
            [
                _candidate("github.com/scipy/scipy", A1, T1, commit="1" * 40),
                _candidate("github.com/numpy/numpy", A1, T1, commit="2" * 40),
            ],
        )
    with pytest.raises(EvidenceError, match="SOURCE_IDENTITY_JOIN_PARTIAL"):
        join_unique_content_identities(
            _pending((S1, A1, T1), (S2, A2, T2)),
            [_candidate("github.com/scipy/scipy", A1, T1)],
        )
    with pytest.raises(EvidenceError, match="SOURCE_IDENTITY_JOIN_PARTIAL"):
        join_unique_content_identities(_pending((S1, A1, T1)), [])
