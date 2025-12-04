"""
Task dependency parser utilities.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.models.entities import TaskDependencyDTO


def _load_json(path: Path) -> list:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise ValueError(f"Invalid JSON in {path}") from exc


class DependencyParser:
    def __init__(self, dependencies_dir: Path) -> None:
        self._dependencies_dir = dependencies_dir

    def parse(self) -> list[TaskDependencyDTO]:
        data = _load_json(self._dependencies_dir / "dependencies.json")
        return [
            TaskDependencyDTO(task_code=item["task_code"], depends_on=item["depends_on"])
            for item in data
        ]
