#!/usr/bin/env python3
"""Dual-arm trigger for EXT-statsmodels-03 (statsmodels#2969).

Property (both required):
1. two-sample proportions_ztest works with value=None (null difference 0);
2. one-sample proportions_ztest rejects value=None and requires an explicit null.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path


def evaluate(seed: int) -> dict:
    import numpy as np
    from statsmodels.stats.proportion import proportions_ztest

    _ = seed
    count = np.array([5, 12])
    nobs = np.array([83, 99])
    two_sample_ok = False
    two_sample_err = None
    two_stat = two_pval = None
    try:
        two_stat, two_pval = proportions_ztest(count, nobs, value=None)
        two_sample_ok = bool(
            np.isfinite(two_stat) and np.isfinite(two_pval)
        )
    except Exception as exc:  # noqa: BLE001
        two_sample_err = repr(exc)

    one_sample_requires_value = False
    one_sample_err = None
    try:
        proportions_ztest(5, 83, value=None)
        # Negative escape: two-sample success alone is insufficient when
        # one-sample incorrectly accepts value=None.
        one_sample_requires_value = False
        one_sample_err = "one-sample accepted value=None"
    except Exception as exc:  # noqa: BLE001
        one_sample_requires_value = True
        one_sample_err = repr(exc)

    ok = bool(two_sample_ok and one_sample_requires_value)
    return {
        "neutral_id": "EXT-statsmodels-03",
        "seed": seed,
        "input": {
            "count": count.tolist(),
            "nobs": nobs.tolist(),
            "value": None,
        },
        "observed_output": {
            "two_sample_ok": two_sample_ok,
            "two_stat": None if two_stat is None else float(two_stat),
            "two_pval": None if two_pval is None else float(two_pval),
            "two_sample_err": two_sample_err,
            "one_sample_requires_value": one_sample_requires_value,
            "one_sample_err": one_sample_err,
        },
        "expected_property": (
            "two-sample proportions_ztest works with value=None "
            "(null diff 0) AND one-sample requires an explicit value"
        ),
        "property_holds": ok,
        "package_version": {
            "statsmodels": __import__("statsmodels").__version__,
            "numpy": np.__version__,
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
    args.json_out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "property_holds": payload["property_holds"],
                "exit_status": payload["exit_status"],
            }
        )
    )
    return int(payload["exit_status"])


if __name__ == "__main__":
    raise SystemExit(main())
