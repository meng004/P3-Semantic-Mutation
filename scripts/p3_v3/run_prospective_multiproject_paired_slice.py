#!/usr/bin/env python3
"""Fail-closed multiproject CLI with unique production binder and processor."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _path in (_REPO_ROOT, _REPO_ROOT / "src"):
    _text = str(_path)
    if _text not in sys.path:
        sys.path.insert(0, _text)

from p3_v3.artifacts import canonical_json_bytes
from p3_v3.prospective_multiproject import (
    CLI_RELPATH,
    CONTROLLER_RELPATH,
    DESIGN_COMMIT,
    MAXIMUM_ATTEMPTS,
    SLICE_ID,
    load_frozen_successors,
    production_project_binder,
    production_subject_processor,
    run_multiproject_search,
    validate_multiproject_preflight,
)


def _unique_production_seams(repo_root: Path):
    return (
        production_project_binder(repo_root=repo_root),
        production_subject_processor(repo_root=repo_root),
    )


def main() -> int:
    if len(sys.argv) != 1:
        sys.stdout.buffer.write(canonical_json_bytes({
            "status": "PREFLIGHT_FAIL",
            "slice_id": SLICE_ID,
            "official_terminal_written": False,
        }))
        return 2
    root = Path(__file__).resolve().parents[2]
    validate_multiproject_preflight(
        repo_root=root,
        controller_path=root / CONTROLLER_RELPATH,
    )
    _unique_production_seams(root)
    sys.stdout.buffer.write(canonical_json_bytes({
        "status": "MULTIPROJECT_OFFICIAL_RUN_NOT_AUTHORIZED",
        "slice_id": SLICE_ID,
        "design_commit": DESIGN_COMMIT,
        "official_terminal_written": False,
        "successor_count": MAXIMUM_ATTEMPTS,
    }))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
