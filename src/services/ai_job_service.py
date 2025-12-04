"""
AI job derivation utilities.
"""

from __future__ import annotations

from typing import Sequence

from src.models.entities import AIJobDTO, TaskDTO
from src.services.bootstrap_options import BootstrapOptions


class AIJobService:
    """Creates AI job DTOs from task metadata."""

    def create_ai_jobs(self, tasks: Sequence[TaskDTO], options: BootstrapOptions) -> list[AIJobDTO]:
        if options.skip_ai_jobs:
            return []

        jobs: list[AIJobDTO] = []
        for task in tasks:
            metadata = task.metadata or {}
            ai_info = metadata.get("ai_job")
            if not isinstance(ai_info, dict):
                continue

            jobs.append(
                AIJobDTO(
                    task_code=task.code,
                    job_type=ai_info.get("type", "generic"),
                    prompt=ai_info.get("prompt"),
                    metadata=ai_info.get("metadata", {}),
                )
            )
        return jobs
