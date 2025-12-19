"""
Structured logging helpers for Speckit CLI tooling.
"""

from __future__ import annotations

import json
import logging
import sys
from enum import Enum
from typing import Any, TypedDict

class LogFormat(str, Enum):
    HUMAN = "human"
    JSON = "json"


class _JsonRecord(TypedDict, total=False):
    level: str
    message: str
    name: str
    module: str
    lineno: int
    extras: dict[str, Any]


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload: _JsonRecord = {
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "module": record.module,
            "lineno": record.lineno,
        }

        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord("", 0, "", 0, "", (), None).__dict__
        }
        if extras:
            payload["extras"] = extras

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: int = logging.INFO, fmt: LogFormat = "human") -> None:
    """
    Configure root logging with the requested format.
    """

    handler = logging.StreamHandler(stream=sys.stdout)
    if fmt == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)s | %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    logging.basicConfig(level=level, handlers=[handler], force=True)
