"""Command-line entry points for archive selection, validation and demonstrations."""

from __future__ import annotations

import argparse
import json

from .archives import ExoplanetArchiveClient
from .demo import run_demo
from .registry import load_registry, require_source


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="exolab")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("census", help="query live NASA Exoplanet Archive counts")

    candidates = commands.add_parser("candidates", help="rank current TOI planet candidates")
    candidates.add_argument("--limit", type=int, default=20)
    candidates.add_argument("--max-tmag", type=float, default=12.0)
    candidates.add_argument("--max-radius", type=float, default=6.0)

    demo = commands.add_parser("demo", help="run a deterministic synthetic transit search")
    demo.add_argument("--output", default="outputs/demo")

    commands.add_parser("sources", help="print the versioned public-data source registry")
    source = commands.add_parser("source", help="validate one source for current public use")
    source.add_argument("source_id")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "census":
        snapshot = ExoplanetArchiveClient().census()
        print(json.dumps(snapshot.__dict__, indent=2))
    elif args.command == "candidates":
        frame = ExoplanetArchiveClient().candidate_queue(
            limit=args.limit,
            max_tmag=args.max_tmag,
            max_radius=args.max_radius,
        )
        print(frame.to_csv(index=False))
    elif args.command == "demo":
        signal, vetting, paths = run_demo(args.output)
        print(json.dumps({"signal": signal.as_dict(), "vetting": vetting.as_dict(), "files": [str(p) for p in paths]}, indent=2))
    elif args.command == "sources":
        payload = {
            key: {
                "name": spec.name,
                "status": spec.status,
                "usable_now": spec.usable_now,
            }
            for key, spec in load_registry().items()
        }
        print(json.dumps(payload, indent=2))
    elif args.command == "source":
        spec = require_source(args.source_id)
        print(json.dumps(spec.payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
