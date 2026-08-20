#!/usr/bin/env python3
"""Dual-arm trigger for EXT-scipy-01 (scipy#24551).

Property: exponnorm with tiny K has CDF in [0,1] and finite logpdf.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path


def evaluate(seed: int) -> dict:
    import numpy as np
    from scipy import stats

    _ = seed
    dist = stats.exponnorm(K=1e-11)
    x = np.linspace(-3.0, 3.0, 21)
    cdf = dist.cdf(x)
    logpdf = dist.logpdf(x)
    sf = dist.sf(x)
    cdf_ok = bool(np.all(np.isfinite(cdf)) and np.all(cdf >= -1e-12) and np.all(cdf <= 1 + 1e-12))
    logpdf_ok = bool(np.all(np.isfinite(logpdf)))
    sf_ok = bool(np.all(np.isfinite(sf)) and np.all(sf >= -1e-12) and np.all(sf <= 1 + 1e-12))
    ok = cdf_ok and logpdf_ok and sf_ok
    return {
        "neutral_id": "EXT-scipy-01",
        "seed": seed,
        "input": {"K": 1e-11, "x": x.tolist()},
        "observed_output": {
            "cdf_min": float(np.min(cdf)),
            "cdf_max": float(np.max(cdf)),
            "logpdf_finite": logpdf_ok,
            "sf_min": float(np.min(sf)),
            "sf_max": float(np.max(sf)),
        },
        "expected_property": "exponnorm tiny-K CDF/SF in [0,1] and finite logpdf",
        "property_holds": bool(ok),
        "package_version": {
            "scipy": getattr(stats, "__version__", None) or getattr(__import__("scipy"), "__version__", None),
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
