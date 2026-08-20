#!/usr/bin/env python3
"""Dual-arm trigger for EXT-numpy-01 (numpy#18378).

Property: (0)**array([1-1j]) is finite complex zero when Re(z)>0.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path


def evaluate(seed: int) -> dict:
    import numpy as np

    _ = seed
    got = (0) ** np.array([1 - 1j])
    val = complex(got.reshape(-1)[0])
    finite = bool(np.isfinite(val.real) and np.isfinite(val.imag))
    near_zero = abs(val) < 1e-12
    ok = finite and near_zero
    return {
        "neutral_id": "EXT-numpy-01",
        "seed": seed,
        "input": {"expr": "(0)**np.array([1-1j])"},
        "observed_output": {
            "value": [val.real, val.imag],
            "finite": finite,
            "near_zero": near_zero,
        },
        "expected_property": "finite complex zero for zero base with Re(z)>0",
        "property_holds": bool(ok),
        "package_version": {
            "numpy": getattr(np, "__version__", None),
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "exit_status": 0 if ok else 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    payload = evaluate(args.seed)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"property_holds": payload["property_holds"], "exit_status": payload["exit_status"]}))
    return int(payload["exit_status"])


if __name__ == "__main__":
    raise SystemExit(main())
