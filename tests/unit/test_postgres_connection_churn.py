import pytest

from src.services.postgres_gateway import PostgresGateway


class _FakeCursor:
    def __init__(self) -> None:
        self._queries: list[tuple[str, object]] = []
        self._last_query: str | None = None
        self._last_params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self._last_query = str(sql)
        self._last_params = params
        self._queries.append((self._last_query, params))

    def fetchall(self):
        query = self._last_query or ""
        if "FROM information_schema.tables" in query:
            return [(t,) for t in ["features", "projects", "specs", "task_dependencies", "tasks"]]

        if "FROM information_schema.columns" in query:
            table = None
            if isinstance(self._last_params, tuple) and len(self._last_params) == 1:
                table = self._last_params[0]

            columns: dict[str, list[tuple[str, str]]] = {
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

            return list(columns.get(table, []))

        return []

    def fetchone(self):
        return None


class _FakeConn:
    def __init__(self) -> None:
        self.autocommit = True
        self._cursor = _FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self, *args, **kwargs):
        return self._cursor

    def commit(self):
        return None

    def rollback(self):
        return None


def test_postgres_reuses_single_connection_in_transaction(monkeypatch):
    psycopg2 = pytest.importorskip("psycopg2")
    gateway = PostgresGateway("postgresql://example")

    connect_calls: list[str] = []

    def _fake_connect(_conn_str: str):
        connect_calls.append(_conn_str)
        return _FakeConn()

    monkeypatch.setattr(psycopg2, "connect", _fake_connect)

    with gateway.transaction():
        # These methods should all reuse the active transaction connection
        gateway.verify_schema()
        gateway.create_or_update_projects([])
        gateway.create_or_update_features([])
        gateway.create_or_update_specs([])
        gateway.create_or_update_tasks([])
        gateway.create_task_dependencies([])

    assert len(connect_calls) == 1
