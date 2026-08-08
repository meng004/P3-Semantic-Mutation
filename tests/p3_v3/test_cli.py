from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/p3_v3/evidence.py"
COMMANDS = {
    "validate-protocol",
    "verify-bridge",
    "build-frames",
    "verify-mr-inventory",
    "build-package",
    "verify-package",
    "run-preflight",
    "verify-run-records",
    "close-phase",
    "verify-evidence",
}
SCIENTIFIC_PLAN_SHA256 = "911562938a14ad3955a6c1e38080185ba78e92dbf4401efcb10d7c169e4a2772"
EVIDENCE_DESIGN_SHA256 = "e2a943b30f8096aa65a72c43aa514df67b8d58e16fcf7209930799ee4444c346"


def _env():
    return {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def test_cli_help_lists_only_frozen_commands():
    result = subprocess.run(
        ["python3", str(CLI), "--help"], capture_output=True, text=True, env=_env()
    )
    assert result.returncode == 0
    line = next(item for item in result.stdout.splitlines() if "{" in item and "}" in item)
    observed = set(line[line.index("{") + 1 : line.index("}")].split(","))
    assert observed == COMMANDS


def test_validate_protocol_prints_one_canonical_json_result(tmp_path):
    body = {
        "schema_version": "p3-protocol-v1",
        "scientific_plan_sha256": SCIENTIFIC_PLAN_SHA256,
        "evidence_design_sha256": EVIDENCE_DESIGN_SHA256,
        "claims_initial_status": "blocked",
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n"
    protocol = tmp_path / "protocol.json"
    protocol.write_text(raw, encoding="utf-8")
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["protocol_sha256"] == __import__("hashlib").sha256(raw.encode()).hexdigest()
    assert result.stdout == json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"


def test_validate_protocol_rejects_a_different_well_formed_plan_hash(tmp_path):
    body = {
        "schema_version": "p3-protocol-v1",
        "scientific_plan_sha256": "a" * 64,
        "evidence_design_sha256": EVIDENCE_DESIGN_SHA256,
        "claims_initial_status": "blocked",
    }
    protocol = tmp_path / "protocol.json"
    protocol.write_text(
        json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_AUTHORITY"


def test_verify_evidence_accepts_canonical_json_and_verified_jsonl_ledger(tmp_path):
    artifact = tmp_path / "artifact.json"
    artifact.write_text('{"status":"blocked"}\n', encoding="utf-8")
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"")
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--artifact",
            str(artifact),
            "--artifact",
            str(ledger),
        ],
        capture_output=True,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    assert len(json.loads(result.stdout)["artifacts"]) == 2
