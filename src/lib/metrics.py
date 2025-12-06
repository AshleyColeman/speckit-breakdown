"""
Lightweight metrics helpers for bootstrap runs.
"""
from __future__ import annotations

import logging
from dataclasses import asdict

logger = logging.getLogger(__name__)


def emit_bootstrap_summary(summary) -> None:
    """Log a structured bootstrap summary."""
    try:
        payload = asdict(summary)
    except Exception:  # pragma: no cover
        payload = summary.__dict__  # type: ignore
    logger.info("Bootstrap summary", extra=payload)
