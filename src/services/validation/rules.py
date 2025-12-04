"""
Validation rules for bootstrap documentation integrity checks.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Iterable, Sequence

from src.models.entities import TaskDTO, TaskDependencyDTO
from src.services.validation_pipeline import Severity, ValidationIssue, ValidationRule


@dataclass(slots=True, frozen=True)
class ValidationContext:
    """Shared data available to validation rules."""

    tasks: Sequence[TaskDTO]
    dependencies: Sequence[TaskDependencyDTO]


class DuplicateTaskCodeRule:
    """Ensures task codes remain unique."""

    name = "duplicate_task_codes"

    def __init__(self, context: ValidationContext) -> None:
        self._context = context

    def run(self) -> Iterable[ValidationIssue]:
        counts = Counter(task.code for task in self._context.tasks)
        for code, count in counts.items():
            if count > 1:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Task code '{code}' appears {count} times.",
                    location="tasks/tasks.json",
                )


class CircularDependencyRule:
    """Detects circular task dependencies."""

    name = "circular_task_dependencies"

    def __init__(self, context: ValidationContext) -> None:
        self._context = context

    def run(self) -> Iterable[ValidationIssue]:
        if not self._context.dependencies:
            return []

        graph = defaultdict(list)
        indegree = Counter()
        task_codes = {task.code for task in self._context.tasks}

        for dep in self._context.dependencies:
            graph[dep.depends_on].append(dep.task_code)
            indegree[dep.task_code] += 1
            if dep.depends_on not in task_codes or dep.task_code not in task_codes:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Dependency '{dep.task_code}' -> '{dep.depends_on}' references an unknown task.",
                    location="dependencies/dependencies.json",
                )

        queue = deque(code for code in task_codes if indegree[code] == 0)
        visited = 0

        while queue:
            current = queue.popleft()
            visited += 1
            for neighbor in graph[current]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if visited != len(task_codes):
            yield ValidationIssue(
                severity=Severity.ERROR,
                message="Circular dependencies detected among tasks.",
                location="dependencies/dependencies.json",
            )


class TaskMetadataRule:
    """Validates required metadata on tasks."""

    name = "task_metadata"

    def __init__(self, context: ValidationContext) -> None:
        self._context = context

    def run(self) -> Iterable[ValidationIssue]:
        for task in self._context.tasks:
            if not task.acceptance.strip():
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Task '{task.code}' is missing acceptance criteria.",
                    location="tasks/tasks.json",
                )
