"""
Task run generation utilities.
"""

from __future__ import annotations

from typing import Sequence

from src.models.entities import TaskDTO, TaskRunDTO
from src.services.bootstrap_options import BootstrapOptions


class TaskRunService:
    """Derives task-run DTOs from parsed tasks."""

    def create_task_runs(self, tasks: Sequence[TaskDTO], options: BootstrapOptions) -> list[TaskRunDTO]:
        if options.skip_task_runs:
            return []
        return [TaskRunDTO(task_code=task.code, status=task.status) for task in tasks]
