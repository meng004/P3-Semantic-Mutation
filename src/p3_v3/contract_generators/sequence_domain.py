"""Deterministic filename-sequence contract input generator."""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENERATOR_ID = "CONTRACT_SEQUENCE_DOMAIN_V1"
FAILURE_CODE = "CONTRACT_SEQUENCE_DOMAIN_INVALID"


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
    accepted = domain.get("accepted_suffixes")
    rejected = domain.get("rejected_suffixes")
    count = domain.get("entry_count")
    if (
        not isinstance(accepted, list)
        or not accepted
        or not all(isinstance(item, str) and item.startswith(".") for item in accepted)
        or not isinstance(rejected, list)
        or not rejected
        or not all(isinstance(item, str) and item.startswith(".") for item in rejected)
        or not isinstance(count, int)
        or isinstance(count, bool)
        or count < 2
    ):
        return {"failure_code": FAILURE_CODE}
    prefix = hashlib.sha256(seed.to_bytes(8, "big", signed=False)).hexdigest()[:12]
    suffixes = [accepted[seed % len(accepted)], rejected[seed % len(rejected)]]
    pool = accepted + rejected
    suffixes.extend(pool[(seed + index) % len(pool)] for index in range(count - 2))
    return _result({"entries": [f"{prefix}-{index}{suffix}" for index, suffix in enumerate(suffixes)]})

