#!/usr/bin/env python3
"""Thin CLI for the P3 v3 minimum evidence foundation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import (  # noqa: E402
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import build_subject_frames, verify_pinned_bridge  # noqa: E402
from p3_v3.packages import build_package, verify_package  # noqa: E402
from p3_v3.preflight import run_preflight  # noqa: E402
from p3_v3.run_records import close_phase, verify_ledger  # noqa: E402


SCIENTIFIC_PLAN_SHA256 = "911562938a14ad3955a6c1e38080185ba78e92dbf4401efcb10d7c169e4a2772"
EVIDENCE_DESIGN_SHA256 = "e2a943b30f8096aa65a72c43aa514df67b8d58e16fcf7209930799ee4444c346"


def _write(payload: dict) -> None:
    sys.stdout.buffer.write(canonical_json_bytes(payload))


def _write_output(path: str | None, payload: dict) -> None:
    if path:
        write_canonical_json(path, payload, exclusive=True)


def _protocol(path: str) -> dict:
    value = read_canonical_json(path)
    schema = {
        "schema_version": str,
        "scientific_plan_sha256": str,
        "evidence_design_sha256": str,
        "claims_initial_status": str,
    }
    validate_exact_object(value, schema, "protocol")
    if value["schema_version"] != "p3-protocol-v1" or value["claims_initial_status"] != "blocked":
        raise EvidenceError("E_PROTOCOL", "protocol version or initial claim status differs")
    validate_sha256(value["scientific_plan_sha256"], "scientific_plan_sha256")
    validate_sha256(value["evidence_design_sha256"], "evidence_design_sha256")
    if (
        value["scientific_plan_sha256"] != SCIENTIFIC_PLAN_SHA256
        or value["evidence_design_sha256"] != EVIDENCE_DESIGN_SHA256
    ):
        raise EvidenceError("E_PROTOCOL_AUTHORITY", "protocol authority hashes differ")
    return value


def _mr_inventory(path: str) -> dict:
    value = read_canonical_json(path)
    schema = {
        "schema_version": str,
        "candidate_frame_sha256": str,
        "custodian_receipt_sha256": str,
        "final_inventory_sha256": str,
        "portfolios_sha256": str,
        "chronology": list,
        "artifact_sha256": str,
    }
    validate_exact_object(value, schema, "mr_inventory")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_MR_INVENTORY_HASH", "MR inventory self-hash differs")
    for field in (
        "candidate_frame_sha256",
        "custodian_receipt_sha256",
        "final_inventory_sha256",
        "portfolios_sha256",
    ):
        validate_sha256(value[field], field)
    if value["chronology"] != [
        "candidate_frame",
        "custodian_receipt",
        "final_inventory",
        "portfolios",
    ]:
        raise EvidenceError("E_MR_CHRONOLOGY", "MR freeze chronology differs")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("validate-protocol")
    command.add_argument("--protocol", required=True)
    command = sub.add_parser("verify-bridge")
    command.add_argument("--repo-root", required=True)
    command.add_argument("--lock", required=True)
    command.add_argument("--output")
    command = sub.add_parser("build-frames")
    command.add_argument("--bridge", required=True)
    command.add_argument("--features", required=True)
    command.add_argument("--output", required=True)
    command = sub.add_parser("verify-mr-inventory")
    command.add_argument("--inventory", required=True)
    command = sub.add_parser("build-package")
    command.add_argument("--role", required=True)
    command.add_argument("--root", required=True)
    command.add_argument("--specs", required=True)
    command.add_argument("--parents", required=True)
    command.add_argument("--output", required=True)
    command = sub.add_parser("verify-package")
    command.add_argument("--root", required=True)
    command.add_argument("--manifest", required=True)
    command = sub.add_parser("run-preflight")
    command.add_argument("--root", required=True)
    command.add_argument("--spec", required=True)
    command.add_argument("--output")
    command = sub.add_parser("verify-run-records")
    command.add_argument("--ledger", required=True)
    command = sub.add_parser("close-phase")
    command.add_argument("--phase-id", required=True)
    command.add_argument("--protocol-sha256", required=True)
    command.add_argument("--expected-jobs", required=True)
    command.add_argument("--ledger", required=True)
    command.add_argument("--output-manifest-sha256", required=True)
    command.add_argument("--output", required=True)
    command = sub.add_parser("verify-evidence")
    command.add_argument("--artifact", action="append", required=True)
    return parser


def dispatch(args: argparse.Namespace) -> dict:
    if args.command == "validate-protocol":
        _protocol(args.protocol)
        return {"status": "PASS", "protocol_sha256": file_sha256(args.protocol)}
    if args.command == "verify-bridge":
        bridge = verify_pinned_bridge(args.repo_root, read_canonical_json(args.lock))
        _write_output(args.output, bridge)
        return {"status": "PASS", "bridge_sha256": canonical_sha256(bridge)}
    if args.command == "build-frames":
        frames = build_subject_frames(
            read_canonical_json(args.bridge), read_canonical_json(args.features)
        )
        _write_output(args.output, frames)
        return {"status": "PASS", "frames_sha256": canonical_sha256(frames)}
    if args.command == "verify-mr-inventory":
        value = _mr_inventory(args.inventory)
        return {"status": "PASS", "inventory_sha256": canonical_sha256(value)}
    if args.command == "build-package":
        manifest = build_package(
            args.role,
            args.root,
            read_canonical_json(args.specs),
            read_canonical_json(args.parents),
        )
        _write_output(args.output, manifest)
        return {"status": "PASS", "manifest_sha256": canonical_sha256(manifest)}
    if args.command == "verify-package":
        verify_package(args.root, read_canonical_json(args.manifest))
        return {"status": "PASS", "manifest_sha256": file_sha256(args.manifest)}
    if args.command == "run-preflight":
        result = run_preflight(args.root, read_canonical_json(args.spec))
        _write_output(args.output, result)
        return result
    if args.command == "verify-run-records":
        events = verify_ledger(args.ledger)
        return {"status": "PASS", "event_count": len(events), "ledger_sha256": file_sha256(args.ledger)}
    if args.command == "close-phase":
        receipt = close_phase(
            args.phase_id,
            args.protocol_sha256,
            read_canonical_json(args.expected_jobs),
            args.ledger,
            args.output_manifest_sha256,
        )
        _write_output(args.output, receipt)
        return {"status": "PASS", "receipt_sha256": canonical_sha256(receipt)}
    if args.command == "verify-evidence":
        artifacts = []
        for raw_path in sorted(set(args.artifact)):
            if Path(raw_path).suffix == ".jsonl":
                verify_ledger(raw_path)
            else:
                read_canonical_json(raw_path)
            artifacts.append({"path": raw_path, "sha256": file_sha256(raw_path)})
        return {"status": "PASS", "artifacts": artifacts}
    raise EvidenceError("E_CLI_COMMAND", f"unsupported command: {args.command}")


def main() -> int:
    try:
        payload = dispatch(build_parser().parse_args())
    except EvidenceError as exc:
        sys.stderr.buffer.write(canonical_json_bytes({"status": "FAIL", "code": exc.code}))
        return 2
    _write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
