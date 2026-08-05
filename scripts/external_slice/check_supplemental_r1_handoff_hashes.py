#!/usr/bin/env python3
"""Recompute every declared supplemental R1 handoff hash and exit nonzero on mismatch."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(rel)
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", type=Path, required=True)
    args = parser.parse_args()

    handoff = load_json(args.handoff)
    root = Path.cwd()
    mismatches: list[str] = []

    files = handoff.get("file_sha256") or {}
    for rel, expected in files.items():
        path = root / rel
        if not path.is_file():
            mismatches.append(f"missing file {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected}, got {actual}")

    trees = handoff.get("tree_sha256") or {}
    for rel, expected in trees.items():
        path = root / rel
        if not path.is_dir():
            mismatches.append(f"missing tree {rel}")
            continue
        actual = sha256_tree(path)
        if actual != expected:
            mismatches.append(f"{rel}/: expected {expected}, got {actual}")

    evidence_map = handoff.get("evidence_sha256") or {}
    for rel, expected in evidence_map.items():
        path = root / rel
        if not path.is_file():
            mismatches.append(f"missing evidence {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected}, got {actual}")

    if mismatches:
        print("HASH_CHECK_FAIL", file=sys.stderr)
        for item in mismatches:
            print(f"ERROR: {item}", file=sys.stderr)
        return 1

    print("HASH_CHECK_OK")
    print(f"checked_files={len(files)} checked_trees={len(trees)} checked_evidence={len(evidence_map)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
