"""Export frozen release products into the compact website data contract."""

from __future__ import annotations

import argparse
from pathlib import Path

from exolab.web_release import write_web_release_data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output", type=Path, default=Path("web/public/data/lab.json")
    )
    args = parser.parse_args()
    path = write_web_release_data(args.repository.resolve(), args.output)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

