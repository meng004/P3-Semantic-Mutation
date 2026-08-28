"""Deterministic ordered-relation-pair contract input generator."""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENERATOR_ID = "CONTRACT_RELATION_PAIR_DOMAIN_V1"
FAILURE_CODE = "CONTRACT_RELATION_PAIR_DOMAIN_INVALID"


def _unit(seed: int, counter: int) -> float:
    raw = seed.to_bytes(8, "big", signed=False) + counter.to_bytes(8, "big")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") / ((1 << 64) - 1)


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
    lower, upper, integer = domain.get("lower"), domain.get("upper"), domain.get("integer")
    if (
        isinstance(lower, bool)
        or isinstance(upper, bool)
        or not isinstance(lower, (int, float))
        or not isinstance(upper, (int, float))
        or lower >= upper
        or type(integer) is not bool
    ):
        return {"failure_code": FAILURE_CODE}
    values = sorted(lower + (upper - lower) * _unit(seed, index) for index in range(2))
    if integer:
        values = sorted(int(round(value)) for value in values)
    return _result({"left": values[0], "right": values[1]})
