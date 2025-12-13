import contextlib

import pytest

from src.services.data_store_gateway import DataStoreGateway


class _FakeCursor:
    def __init__(self, *, existing_tables: set[str], table_columns: dict[str, list[tuple[str, str]]]):
        self._existing_tables = existing_tables
        self._table_columns = table_columns
        self._last_query: str | None = None
        self._last_params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self._last_query = str(sql)
        self._last_params = params

    def fetchall(self):
        if "FROM information_schema.tables" in (self._last_query or ""):
            return [(t,) for t in sorted(self._existing_tables)]

        if "FROM information_schema.columns" in (self._last_query or ""):
            table = None
            if isinstance(self._last_params, tuple) and len(self._last_params) == 1:
                table = self._last_params[0]
            return list(self._table_columns.get(table, []))

        return []


class _FakeConn:
    def __init__(self, cursor: _FakeCursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self._cursor


def test_verify_schema_postgres_success(monkeypatch):
    gateway = DataStoreGateway("postgresql://example", enable_experimental_postgres=True)

    required_tables = {"projects", "features", "specs", "tasks", "task_dependencies"}
    table_columns = {
        "projects": [("id", "uuid"), ("name", "text"), ("description", "text"), ("status", "text")],
        "features": [
            ("id", "uuid"),
            ("project_id", "uuid"),
            ("name", "text"),
            ("description", "text"),
            ("priority", "integer"),
            ("status", "text"),
        ],
        "specs": [("id", "uuid"), ("feature_id", "uuid"), ("name", "text"), ("file_path", "text"), ("status", "text")],
        "tasks": [
            ("id", "uuid"),
            ("name", "text"),
            ("status", "text"),
            ("description", "text"),
            ("metadata", "jsonb"),
            ("feature_id", "uuid"),
            ("project_id", "uuid"),
            ("step_order", "integer"),
        ],
        "task_dependencies": [("predecessor_id", "uuid"), ("successor_id", "uuid")],
    }

    fake_conn = _FakeConn(_FakeCursor(existing_tables=required_tables, table_columns=table_columns))
    monkeypatch.setattr(gateway._backend, "_get_connection", lambda: contextlib.nullcontext(fake_conn))

    gateway.verify_schema()


def test_verify_schema_postgres_fail_fast_message(monkeypatch):
    gateway = DataStoreGateway("postgresql://example", enable_experimental_postgres=True)

    existing_tables = {"projects", "features", "specs", "tasks"}
    table_columns = {
        "projects": [("id", "uuid"), ("name", "text"), ("description", "text"), ("status", "text")],
        "features": [("id", "uuid"), ("project_id", "uuid"), ("name", "text"), ("description", "text"), ("priority", "integer"), ("status", "text")],
        "specs": [("id", "uuid"), ("feature_id", "uuid"), ("name", "text"), ("file_path", "text"), ("status", "text")],
        "tasks": [
            ("id", "uuid"),
            ("name", "text"),
            ("status", "text"),
            ("description", "text"),
            ("metadata", "text"),
            ("feature_id", "uuid"),
            ("project_id", "uuid"),
            ("step_order", "integer"),
        ],
    }

    fake_conn = _FakeConn(_FakeCursor(existing_tables=existing_tables, table_columns=table_columns))
    monkeypatch.setattr(gateway._backend, "_get_connection", lambda: contextlib.nullcontext(fake_conn))

    with pytest.raises(RuntimeError) as exc:
        gateway.verify_schema()

    msg = str(exc.value)
    assert "PostgreSQL schema verification failed" in msg
    assert "Missing tables" in msg
    assert "task_dependencies" in msg
    assert "metadata->>'code'" in msg
