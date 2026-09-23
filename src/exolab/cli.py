"""Command-line entry points for archive, provenance and demonstration tools."""

from __future__ import annotations

import argparse
import json

from .archives import ExoplanetArchiveClient
from .demo import run_demo
from .provenance import verify_manifest
from .registry import load_registry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="exolab")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("census", help="query live NASA Exoplanet Archive counts")

    candidates = commands.add_parser("candidates", help="rank current TOI planet candidates")
    candidates.add_argument("--limit", type=int, default=20)
    candidates.add_argument("--max-tmag", type=float, default=12.0)
    candidates.add_argument("--max-radius", type=float, default=6.0)

    demo = commands.add_parser("demo", help="run the deterministic transit demonstration")
    demo.add_argument("--output", default="outputs/demo")

    commands.add_parser("sources", help="show the versioned public-data registry")

    verify = commands.add_parser("verify-manifest", help="verify provenance metadata and local checksums")
    verify.add_argument("path")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "census":
        snapshot = ExoplanetArchiveClient().census()
        print(json.dumps(snapshot.__dict__, indent=2))
        return 0

    if args.command == "candidates":
        frame = ExoplanetArchiveClient().candidate_queue(
            limit=args.limit,
            max_tmag=args.max_tmag,
            max_radius=args.max_radius,
        )
        print(frame.to_csv(index=False))
        return 0

    if args.command == "demo":
        signal, vetting, paths = run_demo(args.output)
        print(
            json.dumps(
                {
                    "signal": signal.as_dict(),
                    "vetting": vetting.as_dict(),
                    "files": [str(path) for path in paths],
                },
                indent=2,
            )
        )
        return 0

    if args.command == "sources":
        rows = [
            {
                "id": source.source_id,
                "name": source.name,
                "status": source.status,
                "archive": source.archive,
            }
            for source in load_registry().values()
        ]
        print(json.dumps(rows, indent=2))
        return 0

    if args.command == "verify-manifest":
        valid = verify_manifest(args.path)
        print(json.dumps({"path": args.path, "valid": valid}, indent=2))
        return 0 if valid else 2

    raise RuntimeError(f"Unhandled command {args.command!r}")


if __name__ == "__main__":
    raise SystemExit(main())
