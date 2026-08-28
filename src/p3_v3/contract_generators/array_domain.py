"""Deterministic symmetric-positive-definite array contract generator."""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENERATOR_ID = "CONTRACT_ARRAY_DOMAIN_V1"
FAILURE_CODE = "CONTRACT_ARRAY_DOMAIN_INVALID"


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
    size = domain.get("matrix_size")
    diagonal_min = domain.get("diagonal_min")
    off_max = domain.get("off_diagonal_max")
    if (
        not isinstance(size, int)
        or isinstance(size, bool)
        or not 2 <= size <= 8
        or isinstance(diagonal_min, bool)
        or not isinstance(diagonal_min, (int, float))
        or diagonal_min <= 0
        or isinstance(off_max, bool)
        or not isinstance(off_max, (int, float))
        or off_max < 0
    ):
        return {"failure_code": FAILURE_CODE}
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    counter = 0
    scale = off_max / max(1, size * 2)
    for row in range(size):
        for column in range(row + 1, size):
            value = (2.0 * _unit(seed, counter) - 1.0) * scale
            counter += 1
            matrix[row][column] = value
            matrix[column][row] = value
    for row in range(size):
        radius = sum(abs(value) for column, value in enumerate(matrix[row]) if column != row)
        matrix[row][row] = float(diagonal_min) + radius + _unit(seed, counter)
        counter += 1
    return _result({"matrix": matrix})

