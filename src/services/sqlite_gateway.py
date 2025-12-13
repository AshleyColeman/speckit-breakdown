from __future__ import annotations

import contextlib
import json
import logging
import sqlite3
from pathlib import Path
from typing import Iterable, Sequence

from src.models.entities import (
    AIJobDTO,
    FeatureDTO,
    ProjectDTO,
    SpecificationDTO,
    TaskDTO,
    TaskDependencyDTO,
    TaskRunDTO,
)

logger = logging.getLogger(__name__)


class SqliteGateway:
    def __init__(self, storage_path: Path | str) -> None:
        self._is_postgres = False
        self._storage_path = Path(storage_path) if isinstance(storage_path, str) else storage_path
        self._active_conn: sqlite3.Connection | None = None
        self._init_sqlite_db()

    def _sqlite_connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._storage_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_sqlite_db(self) -> None:
        if self._storage_path.parent:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)

        with self._sqlite_connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    code TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    metadata TEXT
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS features (
                    code TEXT PRIMARY KEY,
                    project_code TEXT,
                    name TEXT,
                    description TEXT,
                    priority TEXT,
                    metadata TEXT,
                    FOREIGN KEY(project_code) REFERENCES projects(code)
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS specs (
                    code TEXT PRIMARY KEY,
                    feature_code TEXT,
                    title TEXT,
                    path TEXT,
                    metadata TEXT,
                    FOREIGN KEY(feature_code) REFERENCES features(code)
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    code TEXT PRIMARY KEY,
                    feature_code TEXT,
                    title TEXT,
                    status TEXT,
                    task_type TEXT,
                    acceptance TEXT,
                    step_order INTEGER,
                    metadata TEXT,
                    FOREIGN KEY(feature_code) REFERENCES features(code)
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    task_code TEXT,
                    depends_on TEXT,
                    PRIMARY KEY (task_code, depends_on),
                    FOREIGN KEY(task_code) REFERENCES tasks(code) ON DELETE CASCADE,
                    FOREIGN KEY(depends_on) REFERENCES tasks(code) ON DELETE CASCADE
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS task_runs (
                    task_code TEXT PRIMARY KEY,
                    status TEXT,
                    metadata TEXT,
                    FOREIGN KEY(task_code) REFERENCES tasks(code)
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_jobs (
                    task_code TEXT,
                    job_type TEXT,
                    prompt TEXT,
                    metadata TEXT,
                    PRIMARY KEY (task_code, job_type),
                    FOREIGN KEY(task_code) REFERENCES tasks(code)
                )
            """
            )

            conn.commit()

    def _log_entities(self, entity_type: str, entities: Sequence[object]) -> None:
        if not logger.isEnabledFor(logging.DEBUG):
            return
        logger.debug("Persisting %s: %s", entity_type, [getattr(e, "code", None) for e in entities])

    def verify_schema(self) -> None:
        required_schema = {
            "projects": {"code", "name", "description", "metadata"},
            "features": {"code", "project_code", "name", "description", "priority", "metadata"},
            "specs": {"code", "feature_code", "title", "path", "metadata"},
            "tasks": {"code", "feature_code", "title", "status", "task_type", "acceptance", "step_order", "metadata"},
            "task_dependencies": {"task_code", "depends_on"},
            "task_runs": {"task_code", "status", "metadata"},
            "ai_jobs": {"task_code", "job_type", "prompt", "metadata"},
        }

        with self._sqlite_connect() as conn:
            cursor = conn.cursor()
            for table, columns in required_schema.items():
                try:
                    cursor.execute(f"PRAGMA table_info({table})")
                    rows = cursor.fetchall()
                    if not rows:
                        raise Exception(f"Schema drift detected: Missing table '{table}'")

                    existing_cols = {row[1] for row in rows}
                    missing_cols = columns - existing_cols

                    if missing_cols:
                        raise Exception(f"Schema drift detected: Table '{table}' missing columns {missing_cols}")
                except sqlite3.OperationalError as e:
                    raise Exception(f"Schema check failed for {table}: {e}")

    @staticmethod
    def _retry_sqlite_operation(retries: int = 3, delay: float = 0.1):
        import time
        from functools import wraps

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                last_exc = None
                for i in range(retries):
                    try:
                        return func(self, *args, **kwargs)
                    except sqlite3.OperationalError as e:
                        if "database is locked" in str(e):
                            last_exc = e
                            time.sleep(delay * (i + 1))
                        else:
                            raise
                raise last_exc

            return wrapper

        return decorator

    def _get_connection(self):
        if self._active_conn is not None:
            return contextlib.nullcontext(self._active_conn)
        return self._sqlite_connect()

    @contextlib.contextmanager
    def transaction(self):
        if self._active_conn is not None:
            yield
            return

        with self._get_connection() as conn:
            self._active_conn = conn
            try:
                conn.execute("BEGIN")
                yield
                conn.commit()
            except Exception:
                try:
                    conn.rollback()
                finally:
                    raise
            finally:
                self._active_conn = None

    def _execute_upsert(self, table: str, columns: list[str], data: list[tuple], unique_key: str = "code"):
        if not data:
            return

        cols_str = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT OR REPLACE INTO {table} ({cols_str}) VALUES ({placeholders})"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(sql, data)
            if self._active_conn is None:
                conn.commit()

    @_retry_sqlite_operation()
    def create_or_update_projects(self, projects: Sequence[ProjectDTO]) -> None:
        self._log_entities("projects", projects)
        data = [(p.code, p.name, p.description, json.dumps(p.metadata)) for p in projects]
        self._execute_upsert("projects", ["code", "name", "description", "metadata"], data)

    @_retry_sqlite_operation()
    def create_or_update_features(self, features: Sequence[FeatureDTO]) -> None:
        self._log_entities("features", features)
        data = [(f.code, f.project_code, f.name, f.description, f.priority, json.dumps(f.metadata)) for f in features]
        self._execute_upsert(
            "features", ["code", "project_code", "name", "description", "priority", "metadata"], data
        )

    @_retry_sqlite_operation()
    def create_or_update_specs(self, specs: Sequence[SpecificationDTO]) -> None:
        self._log_entities("specifications", specs)
        data = [(s.code, s.feature_code, s.title, s.path, json.dumps(s.metadata)) for s in specs]
        self._execute_upsert("specs", ["code", "feature_code", "title", "path", "metadata"], data)

    @_retry_sqlite_operation()
    def create_or_update_tasks(self, tasks: Sequence[TaskDTO]) -> None:
        self._log_entities("tasks", tasks)
        data = [
            (t.code, t.feature_code, t.title, t.status, t.task_type, t.acceptance, t.step_order, json.dumps(t.metadata))
            for t in tasks
        ]
        self._execute_upsert(
            "tasks",
            ["code", "feature_code", "title", "status", "task_type", "acceptance", "step_order", "metadata"],
            data,
        )

    def create_task_dependencies(self, dependencies: Iterable[TaskDependencyDTO]) -> None:
        self._log_entities("task_dependencies", dependencies)
        deps_list = list(dependencies)
        if not deps_list:
            return

        sql = (
            "INSERT INTO task_dependencies (task_code, depends_on) VALUES (?, ?) "
            "ON CONFLICT(task_code, depends_on) DO NOTHING"
        )
        data = [(d.task_code, d.depends_on) for d in deps_list]
        with self._get_connection() as conn:
            conn.cursor().executemany(sql, data)
            if self._active_conn is None:
                conn.commit()

    def create_task_runs(self, task_runs: Sequence[TaskRunDTO]) -> None:
        self._log_entities("task_runs", task_runs)
        if not task_runs:
            return

        data = [(tr.task_code, tr.status, json.dumps(tr.metadata)) for tr in task_runs]
        self._execute_upsert("task_runs", ["task_code", "status", "metadata"], data, unique_key="task_code")

    def create_ai_jobs(self, ai_jobs: Sequence[AIJobDTO]) -> None:
        self._log_entities("ai_jobs", ai_jobs)
        if not ai_jobs:
            return

        data = [(job.task_code, job.job_type, job.prompt, json.dumps(job.metadata)) for job in ai_jobs]
        self._execute_upsert(
            "ai_jobs",
            ["task_code", "job_type", "prompt", "metadata"],
            data,
            unique_key="task_code",
        )

    def get_task(self, code: str) -> TaskDTO | None:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE code = ?", (code,))
            row = cursor.fetchone()
            if row:
                return TaskDTO(
                    code=row["code"],
                    feature_code=row["feature_code"],
                    title=row["title"],
                    status=row["status"],
                    task_type=row["task_type"],
                    acceptance=row["acceptance"],
                    step_order=row["step_order"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                )
        return None

    def get_project(self, code: str) -> ProjectDTO | None:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE code = ?", (code,))
            row = cursor.fetchone()
            if row:
                meta = json.loads(row["metadata"]) if row["metadata"] else {}
                return ProjectDTO(
                    code=row["code"],
                    name=row["name"],
                    description=row["description"],
                    repository_path=meta.get("repository_path") or meta.get("repository"),
                    metadata=meta,
                )
        return None

    def get_feature(self, code: str) -> FeatureDTO | None:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM features WHERE code = ?", (code,))
            row = cursor.fetchone()
            if row:
                return FeatureDTO(
                    code=row["code"],
                    project_code=row["project_code"],
                    name=row["name"],
                    description=row["description"],
                    priority=row["priority"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                )
        return None

    def get_spec(self, code: str) -> SpecificationDTO | None:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM specs WHERE code = ?", (code,))
            row = cursor.fetchone()
            if row:
                return SpecificationDTO(
                    code=row["code"],
                    feature_code=row["feature_code"],
                    title=row["title"],
                    path=row["path"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                )
        return None
