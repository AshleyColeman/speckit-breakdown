"""
Documentation discovery service utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

REQUIRED_PATHS: Mapping[str, str] = {
    "project": "project.md",
    "features": "features",
    "specs": "specs",
    "tasks": "tasks",
    "dependencies": "dependencies",
}


@dataclass(frozen=True)
class DiscoveryResult:
    """Normalized documentation paths."""

    project_file: Path
    features_dir: Path
    specs_dir: Path
    tasks_dir: Path
    dependencies_dir: Path

    def all_paths(self) -> Iterable[Path]:
        return (
            self.project_file,
            self.features_dir,
            self.specs_dir,
            self.tasks_dir,
            self.dependencies_dir,
        )


class DocumentationDiscoveryService:
    """Validates required documentation directories for bootstrap."""

    def __init__(self, docs_root: Path) -> None:
        self._docs_root = docs_root

    def verify_structure(self) -> DiscoveryResult:
        missing: list[str] = []
        resolved: dict[str, Path] = {}

        for key, rel_path in REQUIRED_PATHS.items():
            path = (self._docs_root / rel_path).resolve()
            exists = path.exists()
            resolved[key] = path

            if key == "project":
                if not (exists and path.is_file()):
                    missing.append(f"{rel_path} (file)")
            else:
                if not (exists and path.is_dir()):
                    missing.append(f"{rel_path}/ (dir)")

        if missing:
            missing_str = ", ".join(missing)
            raise FileNotFoundError(
                f"Documentation root '{self._docs_root}' is missing required items: {missing_str}"
            )

        return DiscoveryResult(
            project_file=resolved["project"],
            features_dir=resolved["features"],
            specs_dir=resolved["specs"],
            tasks_dir=resolved["tasks"],
            dependencies_dir=resolved["dependencies"],
        )
