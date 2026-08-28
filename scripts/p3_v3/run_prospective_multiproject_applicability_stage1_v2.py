#!/usr/bin/env python3
"""Fail-closed Stage I CLI. Official execution remains unauthorized."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _path in (_REPO_ROOT, _REPO_ROOT / "src"):
    _text = str(_path)
    if _text not in sys.path:
        sys.path.insert(0, _text)

from p3_v3.artifacts import EvidenceError, canonical_json_bytes
from p3_v3.pilot_source import read_authority_snapshot
from p3_v3.prospective_applicability_census_stage1 import (
    STAGE1_DESIGN_COMMIT,
    STAGE1_OFFICIAL_RELDIR,
    STAGE1_SLICE_ID,
    STAGE1_STAGING_RELDIR,
    STAGE1_SUBJECT_COUNT,
    process_stage1_subject,
    run_stage1_census,
)

STAGE1_AUTHORIZATION_PATH = _REPO_ROOT / (
    "data/p3_v3/phase3/inputs/"
    "user-auth-prospective-multiproject-applicability-stage1-v2.txt"
)
STAGE1_AUTHORIZATION_BYTES = (
    b"P3_C3_STAGE1_APPLICABILITY_CENSUS_AUTHORIZED=true\n"
    b"implementation_commit=ee12a75b6dbd3905dcc6acc967beb638ddcc4410\n"
    b"controller_source_sha256="
    b"5ab44c9840f44468c556a94b93a7a294858549688c11ca282e660adb5f71c341\n"
    b"design_file_sha256="
    b"a8828022ee2095b4209261c26d0ecbab66141e59b2c9f18ce3df2045f6dd79c5\n"
)
STAGE1_AUTHORIZATION_SHA256 = (
    "cde781bbe0bd25514b117c55563ac2b88720574da274bf98d3f3f0a56308d60d"
)


def require_stage1_authorization() -> str:
    if not os.path.lexists(STAGE1_AUTHORIZATION_PATH):
        raise EvidenceError("E_STAGE1_AUTH_ABSENT", "authorization is absent")
    raw, digest = read_authority_snapshot(
        STAGE1_AUTHORIZATION_PATH,
        "stage1-applicability-census-auth",
    )
    if raw != STAGE1_AUTHORIZATION_BYTES or digest != STAGE1_AUTHORIZATION_SHA256:
        raise EvidenceError("E_STAGE1_AUTH", "authorization bytes differ")
    return digest


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
    try:
        require_stage1_authorization()
    except EvidenceError:
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
