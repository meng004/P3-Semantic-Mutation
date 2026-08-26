#!/usr/bin/env python3
"""Thin CLI for formal C++ header-compilation profiling."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import EvidenceError, read_canonical_json  # noqa: E402
from p3_v3.profiling_runner import run_cxx_header_workload  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="profile")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run-cxx-header-workload")
    run.add_argument("--workload", required=True)
    run.add_argument("--source-root", required=True)
    run.add_argument("--compiler", required=True)
    run.add_argument("--runtime-root", required=True)
    run.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "run-cxx-header-workload":
            workload = read_canonical_json(args.workload)
            run_cxx_header_workload(
                workload,
                source_root=Path(args.source_root),
                compiler=Path(args.compiler),
                runtime_root=Path(args.runtime_root),
                receipt_path=Path(args.output),
            )
        else:
            raise EvidenceError("E_CLI_COMMAND", f"unsupported command: {args.command}")
    except EvidenceError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
