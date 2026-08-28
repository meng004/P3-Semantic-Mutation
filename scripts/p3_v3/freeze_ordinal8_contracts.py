#!/usr/bin/env python3
"""Freeze ordinal 8 contracts and E_CONTRACT inputs after explicit authorization."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from p3_v3.artifacts import EvidenceError, read_canonical_json, write_canonical_json
from p3_v3.bridge_and_frames import validate_contract_generator_registry
from p3_v3.contract_authority import freeze_ordinal8_package


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closure-root", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--generator-root", required=True)
    parser.add_argument("--output-root", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    closure_root = Path(args.closure_root)
    output_root = Path(args.output_root)
    staging_root = output_root.with_name(output_root.name + ".staging")
    if output_root.exists():
        raise EvidenceError("E_CONTRACT_OUTPUT", "output root already exists")
    if staging_root.exists():
        raise EvidenceError("E_CONTRACT_OUTPUT", "staging root already exists")

    closure_paths = sorted(closure_root.glob("slot-closure-*.json"))
    closures = [read_canonical_json(path) for path in closure_paths]
    registry = validate_contract_generator_registry(
        read_canonical_json(args.registry), Path(args.generator_root)
    )
    package = freeze_ordinal8_package(closures=closures, registry=registry)

    staging_root.mkdir(parents=True, exist_ok=False)
    write_canonical_json(
        staging_root / "contracts.json", package["contracts"], exclusive=True
    )
    for slot_id, inventory in package["inventories"].items():
        write_canonical_json(
            staging_root / f"evaluation-inputs-contract-{slot_id}.json",
            inventory,
            exclusive=True,
        )
    os.replace(staging_root, output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
