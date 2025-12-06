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

            # Support flat metadata keys for convenience
            if not isinstance(ai_info, dict):
                ai_job_type = metadata.get("ai_job_type")
                prompt = metadata.get("prompt")
                if ai_job_type or prompt:
                    ai_info = {
                        "type": ai_job_type or "generic",
                        "prompt": prompt,
                        "metadata": metadata.get("ai_metadata", {}),
                    }
                else:
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

    def estimate_ai_job_count(self, tasks: Sequence[TaskDTO], options: BootstrapOptions) -> int:
        """Lightweight counter used for dry-run summaries."""
        if options.skip_ai_jobs:
            return 0
        count = 0
        for task in tasks:
            metadata = task.metadata or {}
            if isinstance(metadata.get("ai_job"), dict):
                count += 1
                continue
            if metadata.get("ai_job_type") or metadata.get("prompt"):
                count += 1
        return count
