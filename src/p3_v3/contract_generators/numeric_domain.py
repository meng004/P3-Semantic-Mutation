"""Deterministic numeric-domain contract input generator."""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENERATOR_ID = "CONTRACT_NUMERIC_DOMAIN_V1"
FAILURE_CODE = "CONTRACT_NUMERIC_DOMAIN_INVALID"


def _unit(seed: int) -> float:
    block = hashlib.sha256(seed.to_bytes(8, "big", signed=False)).digest()
    return int.from_bytes(block[:8], "big") / ((1 << 64) - 1)


def _result(payload: dict[str, Any]) -> dict[str, Any]:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return {
        "envelope": {
            "schema_version": "p3-contract-input-envelope-v1",
            "generator_id": GENERATOR_ID,
            "payload": payload,
        },
        "raw_payload_sha256": hashlib.sha256(raw).hexdigest(),
    }


def generate(schema_bytes: bytes, seed: int) -> dict[str, Any]:
    try:
        domain = json.loads(schema_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"failure_code": FAILURE_CODE}
    if not isinstance(domain, dict):
        return {"failure_code": FAILURE_CODE}
    lower, upper = domain.get("lower"), domain.get("upper")
    if isinstance(lower, bool) or isinstance(upper, bool):
        return {"failure_code": FAILURE_CODE}
    if not isinstance(lower, (int, float)) or not isinstance(upper, (int, float)) or lower >= upper:
        return {"failure_code": FAILURE_CODE}
    return _result({"value": lower + (upper - lower) * _unit(seed)})

