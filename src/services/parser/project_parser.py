"""
Project-level parser utilities.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.models.entities import ProjectDTO


def _load_json(path: Path) -> list | dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise ValueError(f"Invalid JSON in {path}") from exc


class ProjectParser:
    """Parses project metadata."""

    def __init__(self, project_file: Path) -> None:
        self._project_file = project_file

    def parse(self) -> ProjectDTO:
        data = _load_json(self._project_file)
        return ProjectDTO(
            code=data["code"],
            name=data["name"],
            description=data.get("description", ""),
            repository_path=data.get("repository_path"),
            metadata=data.get("metadata", {}),
        )
