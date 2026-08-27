#!/usr/bin/env python3
"""Foundation-only CLI for the Boost.Math pilot plan."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import EvidenceError, read_canonical_json  # noqa: E402
from p3_v3.pilot import validate_pilot_plan, write_pilot_plan  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pilot")
    sub = parser.add_subparsers(dest="command", required=True)
    write = sub.add_parser("write-plan")
    write.add_argument("--markdown", required=True)
    write.add_argument("--output", required=True)
    validate = sub.add_parser("validate-plan")
    validate.add_argument("--plan", required=True)
    source = sub.add_parser("validate-source")
    source.add_argument("--archive", required=True)
    source.add_argument("--materialize-root", required=True)
    preflight = sub.add_parser("build-preflight")
    preflight.add_argument("--source-root", required=True)
    preflight.add_argument("--build-root", required=True)
    attempt2 = sub.add_parser("build-preflight-attempt-2")
    attempt2.add_argument("--archive", required=True)
    attempt2.add_argument("--source-root", required=True)
    attempt2.add_argument("--build-root", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "write-plan":
            write_pilot_plan(args.markdown, args.output)
        elif args.command == "validate-plan":
            validate_pilot_plan(read_canonical_json(args.plan))
        elif args.command == "validate-source":
            from p3_v3.pilot_source import run_validate_source

            run_validate_source(Path(args.archive), Path(args.materialize_root))
        elif args.command == "build-preflight":
            from p3_v3.pilot_build import run_build_preflight

            run_build_preflight(Path(args.source_root), Path(args.build_root))
        elif args.command == "build-preflight-attempt-2":
            from p3_v3.pilot_build import run_build_preflight_attempt_2

            run_build_preflight_attempt_2(
                Path(args.archive), Path(args.source_root), Path(args.build_root)
            )
        else:
            raise EvidenceError("E_CLI_COMMAND", f"unsupported command: {args.command}")
    except EvidenceError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
