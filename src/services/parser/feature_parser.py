"""
Feature, specification, and task parser utilities.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from src.models.entities import (
    FeatureDTO,
    SpecificationDTO,
    TaskDTO,
)


def _load_json(path: Path) -> list | dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise ValueError(f"Invalid JSON in {path}") from exc


class FeatureParser:
    """Parses feature metadata files."""

    def __init__(self, features_dir: Path) -> None:
        self._features_dir = features_dir

    def parse(self) -> list[FeatureDTO]:
        data = _load_json(self._features_dir / "features.json")
        return [
            FeatureDTO(
                code=item["code"],
                project_code=item["project_code"],
                name=item["name"],
                description=item.get("description", ""),
                priority=item.get("priority", "P2"),
                metadata=item.get("metadata", {}),
            )
            for item in data
        ]


class SpecificationParser:
    """Parses specification metadata."""

    def __init__(self, specs_dir: Path) -> None:
        self._specs_dir = specs_dir

    def parse(self) -> list[SpecificationDTO]:
        data = _load_json(self._specs_dir / "specs.json")
        return [
            SpecificationDTO(
                code=item["code"],
                feature_code=item["feature_code"],
                title=item["title"],
                path=item.get("path", ""),
                metadata=item.get("metadata", {}),
            )
            for item in data
        ]


class TaskParser:
    """Parses task metadata and dependencies."""

    def __init__(self, tasks_dir: Path) -> None:
        self._tasks_dir = tasks_dir

    def parse(self) -> List[TaskDTO]:
        data = _load_json(self._tasks_dir / "tasks.json")
        tasks: List[TaskDTO] = []
        for item in data:
            tasks.append(
                TaskDTO(
                    code=item["code"],
                    feature_code=item["feature_code"],
                    title=item["title"],
                    status=item.get("status", "pending"),
                    task_type=item.get("task_type", "implementation"),
                    acceptance=item.get("acceptance", ""),
                    metadata=item.get("metadata", {}),
                )
            )
        return tasks


def extract_dependencies(tasks_payload: Iterable[dict]) -> list[tuple[str, str]]:
    """Utility to derive dependency tuples from task payloads."""
    deps: list[tuple[str, str]] = []
    for task in tasks_payload:
        for dep in task.get("dependencies", []):
            deps.append((task["code"], dep))
    return deps
