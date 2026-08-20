#!/usr/bin/env python3
"""Dual-arm trigger for EXT-scikit-learn-01 (scikit-learn#26766).

Property: sigmoid CalibratedClassifierCV on SGDClassifier with extremely large
decision scores retains ranking (mean CV ROC AUC well above chance). The bug
collapses sigmoid calibration to ~0.5 AUC; the rescale fix restores ~1.0.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path


def evaluate(seed: int) -> dict:
    import numpy as np
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.linear_model import SGDClassifier
    from sklearn.model_selection import cross_val_score

    rng = np.random.default_rng(42 if seed == 0 else seed)
    r = 0.67
    n = 1000
    y = np.array([1] * int(n * r) + [0] * (n - int(n * r)))
    x = 1e5 * y.reshape((-1, 1)) + rng.normal(size=n).reshape((-1, 1))
    model = CalibratedClassifierCV(
        SGDClassifier(loss="squared_hinge", random_state=42),
        method="sigmoid",
    )
    scores = cross_val_score(model, x, y, scoring="roc_auc", cv=5)
    auc_mean = float(np.mean(scores))
    ok = bool(np.isfinite(auc_mean) and auc_mean >= 0.90)
    return {
        "neutral_id": "EXT-scikit-learn-01",
        "seed": seed,
        "input": {
            "n": n,
            "method": "sigmoid",
            "base": "SGDClassifier(squared_hinge)",
            "feature_scale": 1e5,
            "cv": 5,
        },
        "observed_output": {
            "auc_mean": auc_mean,
            "auc_folds": [float(s) for s in scores],
        },
        "expected_property": "sigmoid calibration mean CV AUC >= 0.90 despite huge scores",
        "property_holds": ok,
        "package_version": {
            "sklearn": __import__("sklearn").__version__,
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
