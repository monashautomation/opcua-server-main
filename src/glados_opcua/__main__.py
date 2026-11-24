"""Command-line entry point.

    python -m glados_opcua --validate
    python -m glados_opcua --docs docs/index.md
    python -m glados_opcua

Configuration errors are reported with exit code 2 before any socket is opened.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from . import __version__
from .docs import build_docs
from .logging_config import configure_logging
from .server import run
from .validation import ConfigurationError, load_manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glados-opcua", description="GLaDOS OPC UA server v2")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--config",
        default=None,
        help="configuration directory (default: $GLADOS_CONFIG_DIR or config)",
    )
    parser.add_argument("--validate", action="store_true", help="validate configuration and exit")
    parser.add_argument(
        "--docs", nargs="?", const="docs/index.md", metavar="PATH", help="generate documentation and exit"
    )
    parser.add_argument("--check-docs", action="store_true", help="verify docs/index.md is current and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config_dir = args.config or os.environ.get("GLADOS_CONFIG_DIR", "config")
    try:
        manifest = load_manifest(config_dir)
    except (ConfigurationError, ValueError) as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2

    configure_logging(manifest.server.log_level, manifest.server.log_json)

    if args.validate:
        print(json.dumps(manifest.summary(), indent=2, sort_keys=True))
        return 0
    if args.check_docs:
        from .docs import main as docs_main

        return docs_main(["--config", config_dir, "--check"])
    if args.docs is not None:
        output = Path(args.docs)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(build_docs(manifest), encoding="utf-8")
        print(f"wrote {output}")
        return 0

    try:
        asyncio.run(run(manifest))
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
