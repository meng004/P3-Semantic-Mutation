#!/usr/bin/env python3
"""Dual-arm trigger for EXT-statsmodels-01 (statsmodels#9860).

Property: Binomial(n=10).deriv(5) == 0 (== 1 - 2*mu/n).
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path


def evaluate(seed: int) -> dict:
    from statsmodels.genmod.families.varfuncs import Binomial

    _ = seed
    b10 = Binomial(n=10)
    got = float(b10.deriv(5))
    expected = 0.0
    ok = abs(got - expected) < 1e-12
    return {
        "neutral_id": "EXT-statsmodels-01",
        "seed": seed,
        "input": {"n": 10, "mu": 5},
        "observed_output": {"deriv": got, "expected": expected},
        "expected_property": "Binomial(n=10).deriv(5) == 0",
        "property_holds": bool(ok),
        "package_version": {
            "statsmodels": __import__("statsmodels").__version__,
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
