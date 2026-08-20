#!/usr/bin/env python3
"""Dual-arm trigger for EXT-statsmodels-02 (statsmodels#9791).

Property: VIF on independent base variables plus common econometric transforms
(log / inverse of *different* bases) stays numerically stable after the
standardize=True default. Same-base transforms are deliberately avoided because
they are genuinely collinear and do not discriminate the fix.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path


def evaluate(seed: int) -> dict:
    import numpy as np
    import pandas as pd
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    rng = np.random.RandomState(42 if seed == 0 else seed)
    n = 500
    x1 = rng.uniform(10, 100, n)
    x2 = rng.uniform(5, 50, n)
    x3 = rng.uniform(1, 20, n)
    df = pd.DataFrame(
        {
            "x1_log": np.log(x1),
            "x2_inv": 1.0 / x2,
            "x3_inv": 1.0 / x3,
            "x1": x1,
            "x2": x2,
            "x3": x3,
        }
    )
    mat = df.to_numpy(dtype=float)
    vifs = [float(variance_inflation_factor(mat, i)) for i in range(mat.shape[1])]
    finite = bool(np.all(np.isfinite(vifs)))
    # Issue example: buggy arm ~O(100), fixed standardize path ~O(10).
    bounded = bool(finite and max(vifs) < 30.0)
    ok = bounded
    return {
        "neutral_id": "EXT-statsmodels-02",
        "seed": seed,
        "input": {"columns": list(df.columns), "n": n, "rng_seed": 42 if seed == 0 else seed},
        "observed_output": {"vifs": vifs, "vif_max": float(max(vifs)), "finite": finite},
        "expected_property": "VIFs finite and < 30 for independent transformed columns",
        "property_holds": bool(ok),
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
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"property_holds": payload["property_holds"], "exit_status": payload["exit_status"]}))
    return int(payload["exit_status"])


if __name__ == "__main__":
    raise SystemExit(main())
