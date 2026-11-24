"""Structured logging setup.

``configure_logging`` is the only entry point.  It is idempotent and safe to
call from the CLI and from tests.  JSON output is one object per line so log
collectors can parse it; text output stays human-readable in a terminal.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime

_RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {
    "message",
    "asctime",
    "taskName",
}


class JsonFormatter(logging.Formatter):
    """Render each record as a single JSON object with stable keys."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, sort_keys=True)


def configure_logging(level: str = "INFO", json_output: bool = False) -> None:
    """Install a single stderr handler at ``level``.

    Existing handlers are removed so repeated calls (test harness, CLI) do not
    duplicate lines.  ``asyncua`` logs at WARNING unless this package is at
    DEBUG, which keeps the default output readable.
    """
    logger = logging.getLogger()
    logger.setLevel(level.upper())
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        JsonFormatter() if json_output else logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(handler)
    logging.getLogger("asyncua").setLevel(logging.DEBUG if logger.level <= logging.DEBUG else logging.WARNING)
