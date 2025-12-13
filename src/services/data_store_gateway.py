"""
Data storage gateway for Speckit bootstrap operations.
"""

from __future__ import annotations

from pathlib import Path

from src.services.postgres_gateway import PostgresGateway
from src.services.sqlite_gateway import SqliteGateway


class DataStoreGateway:
    """Compatibility shim that selects an appropriate backend implementation."""

    def __init__(self, storage_path: Path | str, enable_experimental_postgres: bool = False) -> None:
        if isinstance(storage_path, str) and storage_path.startswith("postgresql://"):
            if not enable_experimental_postgres:
                raise ValueError(
                    "PostgreSQL support is experimental and disabled by default. "
                    "Re-run with --enable-experimental-postgres (CLI) or pass "
                    "enable_experimental_postgres=True (API). See docs/cli/db_prepare.md."
                )
            self._backend = PostgresGateway(storage_path)
        else:
            self._backend = SqliteGateway(storage_path)

        self._is_postgres = bool(getattr(self._backend, "_is_postgres", False))

    def __getattr__(self, name: str):
        return getattr(self._backend, name)

    def _get_connection(self):
        return self._backend._get_connection()

    def verify_schema(self) -> None:
        return self._backend.verify_schema()
