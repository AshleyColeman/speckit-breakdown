"""
Documentation discovery service utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

@dataclass(frozen=True)
class DiscoveryResult:
    """Normalized documentation paths."""

    project_file: Path
    features_dir: Path
    specs_dir: Path
    tasks_dir: Path
    dependencies_dir: Path
    is_nested: bool = False

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

        # Mandatory core items
        mandatory = {
            "project": "project.md",
            "features": "features",
            "specs": "specs",
        }

        for key, rel_path in mandatory.items():
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

        # Optional/Nested items
        is_nested = False
        for key in ["tasks", "dependencies"]:
            rel_path = key
            path = (self._docs_root / rel_path).resolve()
            
            if not path.exists() or not path.is_dir():
                # Check for nested structure in specs/
                specs_path = resolved["specs"]
                # If we suspect nested, we point the dir to the specs root and mark as nested
                # The parsers will then search recursively.
                resolved[key] = specs_path
                is_nested = True
            else:
                resolved[key] = path

        return DiscoveryResult(
            project_file=resolved["project"],
            features_dir=resolved["features"],
            specs_dir=resolved["specs"],
            tasks_dir=resolved["tasks"],
            dependencies_dir=resolved["dependencies"],
            is_nested=is_nested
        )
