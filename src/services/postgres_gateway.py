from __future__ import annotations

import contextlib
import json
import logging
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


class PostgresGateway:
    def __init__(self, connection_string: str) -> None:
        self._is_postgres = True
        self._connection_string = connection_string
        self._pg_column_cache: dict[tuple[str, str], bool] = {}
        self._active_conn = None

    def _get_connection(self):
        if self._active_conn is not None:
            return contextlib.nullcontext(self._active_conn)

        import psycopg2

        return psycopg2.connect(self._connection_string)

    @contextlib.contextmanager
    def transaction(self):
        if self._active_conn is not None:
            yield
            return

        with self._get_connection() as conn:
            self._active_conn = conn
            try:
                conn.autocommit = False
                yield
                conn.commit()
            except Exception:
                try:
                    conn.rollback()
                finally:
                    raise
            finally:
                self._active_conn = None

    def verify_schema(self) -> None:
        required_schema: dict[str, set[str]] = {
            "projects": {"id", "name", "description", "status"},
            "features": {"id", "project_id", "name", "description", "priority", "status"},
            "specs": {"id", "feature_id", "name", "file_path", "status"},
            "tasks": {"id", "name", "status", "description", "metadata", "feature_id", "project_id", "step_order"},
            "task_dependencies": {"predecessor_id", "successor_id"},
        }

        missing_tables: list[str] = []
        missing_columns: dict[str, set[str]] = {}
        metadata_type: str | None = None

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_type = 'BASE TABLE'
                        """
                    )
                    existing_tables = {row[0] for row in cursor.fetchall()}

                    for table, columns in required_schema.items():
                        if table not in existing_tables:
                            missing_tables.append(table)
                            continue

                        cursor.execute(
                            """
                            SELECT column_name, data_type
                            FROM information_schema.columns
                            WHERE table_schema = 'public'
                              AND table_name = %s
                            """,
                            (table,),
                        )
                        col_rows = cursor.fetchall()
                        existing_cols = {row[0] for row in col_rows}
                        missing = columns - existing_cols
                        if missing:
                            missing_columns[table] = missing

                        if table == "tasks" and "metadata" in existing_cols:
                            for col_name, data_type in col_rows:
                                if col_name == "metadata":
                                    metadata_type = data_type
                                    break

                    if missing_tables or missing_columns:
                        raise RuntimeError("PostgreSQL schema contract mismatch")

                    if metadata_type not in {"json", "jsonb"}:
                        raise RuntimeError(
                            "PostgreSQL schema contract mismatch: tasks.metadata must be json/jsonb so we can query "
                            "stable identifiers with metadata->>'code'."
                        )

                    cursor.execute("SELECT metadata->>'code' FROM tasks LIMIT 0")

        except Exception as exc:
            message_lines: list[str] = [
                "PostgreSQL schema verification failed. This backend requires a specific schema contract and refuses to run "
                "if it cannot safely read/write stable identifiers.",
            ]

            if missing_tables:
                message_lines.append(f"Missing tables: {sorted(missing_tables)}")
            if missing_columns:
                for table in sorted(missing_columns.keys()):
                    message_lines.append(f"Table '{table}' missing columns: {sorted(missing_columns[table])}")

            message_lines.extend(
                [
                    "Required semantics:",
                    "- tasks.metadata must be json/jsonb and must support metadata->>'code' lookups.",
                    "- Task stable identifiers are stored in metadata['code']; schema drift here can corrupt links.",
                    "How to fix:",
                    "- Apply/create the expected PostgreSQL schema (see integration tests for the assumed shape).",
                    "- Then re-run the bootstrap.",
                ]
            )

            raise RuntimeError("\n".join(message_lines)) from exc

    def _postgres_has_column(self, cursor, table: str, column: str) -> bool:
        key = (table, column)
        if key in self._pg_column_cache:
            return self._pg_column_cache[key]

        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
              AND column_name = %s
            """,
            (table, column),
        )
        exists = cursor.fetchone() is not None
        self._pg_column_cache[key] = exists
        return exists

    def _postgres_require_metadata_code(self, cursor, table: str) -> None:
        if not self._postgres_has_column(cursor, table, "metadata"):
            raise RuntimeError(
                f"Postgres table '{table}' must have a 'metadata' column to support stable identifier writes. "
                "Refusing to fall back to name-based matching."
            )

    def _postgres_select_one(self, cursor, sql: str, params: tuple, *, entity: str, key: str):
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return self._postgres_single_row(rows, entity=entity, code=key)

    @staticmethod
    def _postgres_single_row(rows, *, entity: str, code: str):
        if not rows:
            return None

        if len(rows) > 1:
            raise RuntimeError(
                f"Ambiguous Postgres match for {entity} code='{code}': expected 1 row, got {len(rows)}. "
                "Refusing to link using heuristics."
            )
        return rows[0]

    def _get_ids_by_codes(self, cursor, table: str, codes: Sequence[str]) -> dict[str, str]:
        normalized = [c.lower() for c in codes if c]
        if not normalized:
            return {}

        sql = f"SELECT metadata->>'code' AS code, id FROM {table} WHERE metadata->>'code' = ANY(%s)"
        cursor.execute(sql, (normalized,))
        rows = cursor.fetchall() or []
        return {row[0]: row[1] for row in rows if row and len(row) >= 2 and row[0]}

    def _get_id_by_code(self, table: str, code: str) -> str | None:
        if not code:
            return None

        sql = f"SELECT id FROM {table} WHERE metadata->>'code' = %s"
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (code,))
                    row = cursor.fetchone()
                    if row:
                        return row[0]
        except Exception as e:
            logger.warning(f"Failed to resolve ID for {table} {code}: {e}")
            return None

        return None

    def create_or_update_projects(self, projects: Sequence[ProjectDTO]) -> None:
        logger.info(f"Upserting {len(projects)} projects (Mode: Postgres)")

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                for p in projects:
                    row = self._postgres_select_one(
                        cursor,
                        "SELECT id FROM projects WHERE name = %s",
                        (p.name,),
                        entity="project",
                        key=p.name,
                    )

                    if row:
                        cursor.execute(
                            """
                            UPDATE projects
                            SET name = %s,
                                description = %s
                            WHERE id = %s
                            """,
                            (p.name, p.description, row[0]),
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO projects (name, description, status)
                            VALUES (%s, %s, 'active')
                            """,
                            (p.name, p.description),
                        )

            if self._active_conn is None:
                conn.commit()

    def create_or_update_features(self, features: Sequence[FeatureDTO]) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                for f in features:
                    proj_row = self._postgres_select_one(
                        cursor,
                        "SELECT id FROM projects WHERE name = %s",
                        (f.project_code,),
                        entity="project",
                        key=f.project_code,
                    )
                    if not proj_row:
                        raise RuntimeError(
                            f"Project not found for feature '{f.name}' (project_code='{f.project_code}')."
                        )
                    p_id = proj_row[0]

                    prio = 0
                    try:
                        prio = int(str(f.priority).replace("P", ""))
                    except Exception:
                        prio = 0

                    row = self._postgres_select_one(
                        cursor,
                        "SELECT id FROM features WHERE project_id = %s AND name = %s",
                        (p_id, f.name),
                        entity="feature",
                        key=f.name,
                    )

                    if row:
                        cursor.execute(
                            """
                            UPDATE features
                            SET name = %s,
                                description = %s,
                                priority = %s
                            WHERE id = %s
                            """,
                            (f.name, f.description, prio, row[0]),
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO features (name, description, priority, project_id, status)
                            VALUES (%s, %s, %s, %s, 'planned')
                            """,
                            (f.name, f.description, prio, p_id),
                        )

            if self._active_conn is None:
                conn.commit()

    def create_or_update_specs(self, specs: Sequence[SpecificationDTO]) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                for s in specs:
                    feat_row = self._postgres_select_one(
                        cursor,
                        "SELECT id FROM features WHERE name = %s",
                        (s.feature_code,),
                        entity="feature",
                        key=s.feature_code,
                    )
                    if not feat_row:
                        raise RuntimeError(f"Feature not found for spec '{s.title}' (feature_code='{s.feature_code}').")
                    f_id = feat_row[0]

                    row = self._postgres_select_one(
                        cursor,
                        "SELECT id FROM specs WHERE feature_id = %s AND name = %s",
                        (f_id, s.title),
                        entity="spec",
                        key=s.title,
                    )

                    if row:
                        cursor.execute(
                            "UPDATE specs SET name = %s, file_path = %s WHERE id = %s",
                            (s.title, s.path, row[0]),
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO specs (name, file_path, feature_id, status) VALUES (%s, %s, %s, 'draft')",
                            (s.title, s.path, f_id),
                        )

            if self._active_conn is None:
                conn.commit()

    def create_or_update_tasks(self, tasks: Sequence[TaskDTO]) -> None:
        from psycopg2.extras import Json

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                for t in tasks:
                    self._postgres_require_metadata_code(cursor, "tasks")

                    feat_row = self._postgres_select_one(
                        cursor,
                        "SELECT id, project_id FROM features WHERE name = %s",
                        (t.feature_code,),
                        entity="feature",
                        key=t.feature_code,
                    )
                    if not feat_row:
                        raise RuntimeError(
                            f"Feature not found for task code='{t.code}' (feature_code='{t.feature_code}')."
                        )
                    feature_id, project_id = feat_row[0], feat_row[1]

                    meta = dict(t.metadata or {})
                    meta["code"] = t.code

                    cursor.execute("SELECT id FROM tasks WHERE metadata->>'code' = %s", (t.code,))
                    row = cursor.fetchone()

                    if row:
                        cursor.execute(
                            """
                            UPDATE tasks
                            SET name = %s,
                                status = %s,
                                description = %s,
                                metadata = %s,
                                feature_id = %s,
                                project_id = %s,
                                step_order = %s
                            WHERE id = %s
                            """,
                            (
                                t.title,
                                t.status,
                                t.acceptance,
                                Json(meta),
                                feature_id,
                                project_id,
                                t.step_order,
                                row[0],
                            ),
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO tasks (name, status, description, metadata, feature_id, project_id, step_order)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (t.title, t.status, t.acceptance, Json(meta), feature_id, project_id, t.step_order),
                        )

            if self._active_conn is None:
                conn.commit()

    def create_task_dependencies(self, dependencies: Iterable[TaskDependencyDTO]) -> None:
        deps_list = list(dependencies)
        if not deps_list:
            return

        from psycopg2.extras import execute_batch

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                codes: list[str] = []
                for d in deps_list:
                    if d.depends_on:
                        codes.append(d.depends_on.lower())
                    if d.task_code:
                        codes.append(d.task_code.lower())

                id_by_code = self._get_ids_by_codes(cursor, "tasks", codes)

                data: list[tuple[str, str]] = []
                for d in deps_list:
                    pred_id = id_by_code.get((d.depends_on or "").lower())
                    succ_id = id_by_code.get((d.task_code or "").lower())
                    if pred_id and succ_id:
                        data.append((pred_id, succ_id))

                if data:
                    execute_batch(
                        cursor,
                        """
                        INSERT INTO task_dependencies (predecessor_id, successor_id)
                        VALUES (%s, %s)
                        ON CONFLICT (predecessor_id, successor_id) DO NOTHING
                        """,
                        data,
                        page_size=1000,
                    )

            if self._active_conn is None:
                conn.commit()

    def create_task_runs(self, task_runs: Sequence[TaskRunDTO]) -> None:
        if not task_runs:
            return

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                for tr in task_runs:
                    payload = {
                        "task_run": {
                            "status": tr.status,
                            "metadata": dict(tr.metadata or {}),
                        }
                    }
                    cursor.execute(
                        """
                        UPDATE tasks
                        SET metadata = COALESCE(metadata, '{}'::jsonb) || (%s)::jsonb
                        WHERE metadata->>'code' = %s
                        """,
                        (json.dumps(payload), (tr.task_code or "").lower()),
                    )
                    if cursor.rowcount == 0:
                        raise RuntimeError(
                            f"Cannot persist task_run: no Postgres task found with metadata->>'code'='{tr.task_code}'."
                        )

            if self._active_conn is None:
                conn.commit()

    def create_ai_jobs(self, ai_jobs: Sequence[AIJobDTO]) -> None:
        if not ai_jobs:
            return

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                for job in ai_jobs:
                    job_payload = {
                        "job_type": job.job_type,
                        "prompt": job.prompt,
                        "metadata": dict(job.metadata or {}),
                    }
                    cursor.execute(
                        """
                        UPDATE tasks
                        SET metadata = jsonb_set(
                            COALESCE(metadata, '{}'::jsonb),
                            '{ai_jobs}',
                            COALESCE(metadata->'ai_jobs', '[]'::jsonb) || (%s)::jsonb,
                            true
                        )
                        WHERE metadata->>'code' = %s
                        """,
                        (json.dumps([job_payload]), (job.task_code or "").lower()),
                    )
                    if cursor.rowcount == 0:
                        raise RuntimeError(
                            f"Cannot persist ai_job: no Postgres task found with metadata->>'code'='{job.task_code}'."
                        )

            if self._active_conn is None:
                conn.commit()

    def get_task(self, code: str) -> TaskDTO | None:
        from psycopg2.extras import DictCursor

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute(
                        "SELECT t.*, f.name AS feature_name "
                        "FROM tasks t "
                        "JOIN features f ON t.feature_id = f.id "
                        "WHERE t.metadata->>'code' = %s",
                        (code,),
                    )
                    row = cursor.fetchone()
                    if not row:
                        return None

                    meta = row["metadata"] if "metadata" in row else None
                    if meta is None:
                        meta = {}
                    elif isinstance(meta, str):
                        meta = json.loads(meta) if meta else {}

                    feature_code = row.get("feature_name") or meta.get("feature_code", "")

                    return TaskDTO(
                        code=code,
                        feature_code=feature_code,
                        title=row.get("name", ""),
                        status=row.get("status", ""),
                        task_type="implementation",
                        acceptance=row.get("description", ""),
                        step_order=row.get("step_order"),
                        metadata=meta,
                    )
        except Exception as e:
            logger.error(f"Postgres get_task failed: {e}")
            return None

    def get_project(self, code: str) -> ProjectDTO | None:
        from psycopg2.extras import DictCursor

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute("SELECT * FROM projects WHERE name = %s", (code,))
                    row = cursor.fetchone()
                    if not row:
                        return None

                    return ProjectDTO(
                        code=row.get("name", code),
                        name=row.get("name", ""),
                        description=row.get("description", "") or "",
                        repository_path=None,
                        metadata={},
                    )
        except Exception as e:
            logger.error(f"Postgres get_project failed: {e}")
            return None

    def get_feature(self, code: str) -> FeatureDTO | None:
        from psycopg2.extras import DictCursor

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute(
                        "SELECT f.*, p.name AS project_name "
                        "FROM features f "
                        "JOIN projects p ON f.project_id = p.id "
                        "WHERE f.name = %s",
                        (code,),
                    )
                    row = cursor.fetchone()
                    if not row:
                        return None

                    prio = row.get("priority")
                    priority = f"P{prio}" if isinstance(prio, int) and prio > 0 else "P2"

                    return FeatureDTO(
                        code=row.get("name", code),
                        project_code=row.get("project_name", ""),
                        name=row.get("name", ""),
                        description=row.get("description", "") or "",
                        priority=priority,
                        metadata={},
                    )
        except Exception as e:
            logger.error(f"Postgres get_feature failed: {e}")
            return None

    def get_spec(self, code: str) -> SpecificationDTO | None:
        from psycopg2.extras import DictCursor

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute(
                        "SELECT s.*, f.name AS feature_name "
                        "FROM specs s "
                        "JOIN features f ON s.feature_id = f.id "
                        "WHERE s.name = %s",
                        (code,),
                    )
                    row = cursor.fetchone()
                    if not row:
                        return None

                    return SpecificationDTO(
                        code=row.get("name", code),
                        feature_code=row.get("feature_name", ""),
                        title=row.get("name", ""),
                        path=row.get("file_path", "") or "",
                        metadata={},
                    )
        except Exception as e:
            logger.error(f"Postgres get_spec failed: {e}")
            return None
