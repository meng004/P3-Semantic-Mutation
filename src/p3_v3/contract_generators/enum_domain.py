"""Deterministic enum-domain contract input generator."""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENERATOR_ID = "CONTRACT_ENUM_DOMAIN_V1"
FAILURE_CODE = "CONTRACT_ENUM_DOMAIN_INVALID"


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
    values = domain.get("values") if isinstance(domain, dict) else None
    if not isinstance(values, list) or not values:
        return {"failure_code": FAILURE_CODE}
    return _result({"value": values[seed % len(values)]})

