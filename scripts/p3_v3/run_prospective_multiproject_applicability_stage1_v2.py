#!/usr/bin/env python3
"""Fail-closed Stage I CLI. Official execution remains unauthorized."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _path in (_REPO_ROOT, _REPO_ROOT / "src"):
    _text = str(_path)
    if _text not in sys.path:
        sys.path.insert(0, _text)

from p3_v3.artifacts import canonical_json_bytes
from p3_v3.prospective_applicability_census_stage1 import (
    STAGE1_DESIGN_COMMIT,
    STAGE1_OFFICIAL_RELDIR,
    STAGE1_SLICE_ID,
    STAGE1_STAGING_RELDIR,
    STAGE1_SUBJECT_COUNT,
    process_stage1_subject,
    run_stage1_census,
)

OFFICIAL_RUN_AUTHORIZED = False


def unauthorized_stage1_status() -> dict[str, object]:
    return {
        "status": "STAGE1_OFFICIAL_RUN_NOT_AUTHORIZED",
        "slice_id": STAGE1_SLICE_ID,
        "design_commit": STAGE1_DESIGN_COMMIT,
        "official_run_authorized": False,
        "official_terminal_written": False,
        "successor_count": STAGE1_SUBJECT_COUNT,
    }


def main() -> int:
    if len(sys.argv) != 1:
        sys.stdout.buffer.write(canonical_json_bytes({
            "status": "PREFLIGHT_FAIL",
            "slice_id": STAGE1_SLICE_ID,
            "official_terminal_written": False,
        }))
        return 2
    if OFFICIAL_RUN_AUTHORIZED is not True:
        sys.stdout.buffer.write(canonical_json_bytes(unauthorized_stage1_status()))
        return 2
    root = Path(__file__).resolve().parents[2]
    run_stage1_census(
        repo_root=root,
        output_root=root / STAGE1_OFFICIAL_RELDIR,
        staging_root=root / STAGE1_STAGING_RELDIR,
        subject_processor=process_stage1_subject,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
