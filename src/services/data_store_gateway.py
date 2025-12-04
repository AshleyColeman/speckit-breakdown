"""
Data storage gateway for Speckit bootstrap operations.
"""

from __future__ import annotations

import logging
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


class DataStoreGateway:
    """
    Abstracts storage operations (SQLite today, pluggable later).
    """

    def __init__(self, storage_path: Path) -> None:
        self._storage_path = storage_path

    def create_or_update_projects(self, projects: Sequence[ProjectDTO]) -> None:
        self._log_entities("projects", projects)

    def create_or_update_features(self, features: Sequence[FeatureDTO]) -> None:
        self._log_entities("features", features)

    def create_or_update_specs(self, specs: Sequence[SpecificationDTO]) -> None:
        self._log_entities("specifications", specs)

    def create_or_update_tasks(self, tasks: Sequence[TaskDTO]) -> None:
        self._log_entities("tasks", tasks)

    def create_task_dependencies(self, dependencies: Iterable[TaskDependencyDTO]) -> None:
        self._log_entities("task_dependencies", dependencies)

    def create_task_runs(self, task_runs: Iterable[TaskRunDTO]) -> None:
        self._log_entities("task_runs", task_runs)

    def create_ai_jobs(self, ai_jobs: Iterable[AIJobDTO]) -> None:
        self._log_entities("ai_jobs", ai_jobs)

    def _log_entities(self, entity_name: str, entities: Iterable[object]) -> None:
        count = len(tuple(entities))
        logger.info(
            "Gateway queued operations",
            extra={"entity": entity_name, "count": count, "storage": str(self._storage_path)},
        )
