"""
Configuration loader utilities for the `/speckit.db.prepare` command.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_DOCS_ROOT = Path("specs")
DEFAULT_STORAGE_PATH = Path(".speckit") / "db.sqlite"


@dataclass(frozen=True)
class BootstrapConfig:
    """Resolved configuration for a bootstrap run."""

    docs_root: Path
    storage_path: Path


class ConfigLoader:
    """
    Allocate configuration values for the bootstrap command.

    This class can later be extended to read from TOML/ENV sources without
    rewriting the CLI surface.
    """

    def __init__(
        self,
        docs_root: Optional[Path] = None,
        storage_path: Optional[Path] = None,
    ) -> None:
        self._docs_root = (docs_root or DEFAULT_DOCS_ROOT).expanduser()
        self._storage_path = (storage_path or DEFAULT_STORAGE_PATH).expanduser()

    def materialize(self) -> BootstrapConfig:
        """Return sanitized filesystem paths."""
        docs_root = self._docs_root.resolve()
        if not docs_root.exists():
            raise FileNotFoundError(
                f"Documentation root '{docs_root}' does not exist. "
                "Run this command from the repo root or pass --docs-path."
            )

        storage_path = self._storage_path.resolve()
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        return BootstrapConfig(docs_root=docs_root, storage_path=storage_path)
