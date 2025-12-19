from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Optional

from src.models.entities import TaskDTO
from src.services.parser.parser_utils import (
    MissingYAMLDependencyError,
    _load_json,
    parse_markdown_key_values,
    parse_yaml_frontmatter,
)

logger = logging.getLogger(__name__)


class TaskParser:
    """Parses task metadata and dependencies from markdown files in tasks/ directory."""

    def __init__(self, tasks_dir: Path, search_recursive: bool = False) -> None:
        self._tasks_dir = tasks_dir
        self._search_recursive = search_recursive
        self._title_pattern = re.compile(r'^#\s+(.+)$', re.MULTILINE)
        self._frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---', re.MULTILINE | re.DOTALL)
        self._acceptance_pattern = re.compile(
            r'## Acceptance Criteria\s*\n(.*?)(?=\n##|\n#|\n(?i:depends on:)\s*|\Z)',
            re.MULTILINE | re.DOTALL,
        )
        self._dependency_pattern = re.compile(r'Depends on:\s*([^\n]+)', re.IGNORECASE)
        self._task_code_heading_pattern = re.compile(r'^#\s*([A-Za-z]+\d+|[A-Za-z]+-\d+)\b', re.MULTILINE)

    @staticmethod
    def _is_numbered_prefix_dir(path: Path) -> bool:
        return path.is_dir() and bool(re.match(r"^\d+", path.name))

    def parse(self) -> List[TaskDTO]:
        tasks: list[TaskDTO] = []

        if not self._tasks_dir.exists():
            logger.warning(f"Tasks directory not found: {self._tasks_dir}")
            return tasks

        # Determine search pattern
        # If recursive, we look for tasks in any subdirectory called 'tasks'
        pattern = "**/tasks/*.md" if self._search_recursive else "*.md"

        for task_file in self._tasks_dir.glob(pattern):
            # If not recursive, skip numbered prefix directories (already handled separately or intended to be skipped)
            # If recursive, we want everything but may still want to skip some things?
            # Workflows put them in specs/NUMBER-name/tasks/ - we want those.
            
            # Legacy check: skip direct children if they are numbered prefix (handled below)
            if not self._search_recursive and task_file.parent.name.isdigit():
                continue

            try:
                task = self._parse_task_file(task_file)
                tasks.append(task)
            except MissingYAMLDependencyError:
                raise
            except Exception as e:
                raise ValueError(f"Failed to parse task file {task_file}: {e}") from e

        # Handle legacy flat structure with numbered subdirs if not recursive
        if not self._search_recursive:
            for task_dir in self._tasks_dir.iterdir():
                if self._is_numbered_prefix_dir(task_dir):
                    for task_file in task_dir.glob("*.md"):
                        try:
                            task = self._parse_task_file(task_file)
                            tasks.append(task)
                        except MissingYAMLDependencyError:
                            raise
                        except Exception as e:
                            raise ValueError(f"Failed to parse task file {task_file}: {e}") from e

        if not tasks and (self._tasks_dir / "tasks.json").exists():
            return self._parse_json_tasks()

        return tasks

    def _parse_task_file(self, task_file: Path) -> TaskDTO:
        content = task_file.read_text(encoding="utf-8")

        title = self._extract_title(content, task_file)
        metadata = self._extract_frontmatter(content)

        feature_code = metadata.get("feature_code", "")
        if not feature_code:
            feature_code = self._extract_feature_code_from_path(task_file)
        else:
            feature_code = str(feature_code).strip()
            if not any(ch.isspace() for ch in feature_code):
                feature_code = feature_code.lower()

        status = metadata.get("status", "pending")
        task_type = metadata.get("task_type", "implementation")

        acceptance = self._extract_acceptance_criteria(content)
        if not acceptance:
            acceptance = metadata.get("acceptance", "")

        dependencies = self._extract_dependencies(content)
        if dependencies:
            metadata["dependencies"] = dependencies

        heading_code = self._extract_task_code_from_heading(content)
        task_code = heading_code or self._generate_task_code(task_file)

        return TaskDTO(
            code=task_code,
            feature_code=feature_code,
            title=title,
            status=status,
            task_type=task_type,
            acceptance=acceptance,
            metadata=metadata,
        )

    def _parse_json_tasks(self) -> List[TaskDTO]:
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

    def _extract_title(self, content: str, task_file: Path) -> str:
        match = self._title_pattern.search(content)
        if match:
            return match.group(1).strip()

        return task_file.stem.replace("-", " ").replace("_", " ").title()

    def _extract_frontmatter(self, content: str) -> dict[str, str]:
        metadata: dict = {}

        match = self._frontmatter_pattern.search(content)
        if match:
            frontmatter_text = match.group(1)
            try:
                metadata = parse_yaml_frontmatter(frontmatter_text)
            except ValueError as e:
                logger.warning(f"Failed to parse YAML frontmatter: {e}")
                metadata = self._parse_simple_frontmatter(frontmatter_text)

        markdown_metadata = parse_markdown_key_values(content)
        for k, v in markdown_metadata.items():
            if k not in metadata:
                metadata[k] = v

        normalized_metadata: dict[str, str] = {}
        for k, v in metadata.items():
            normalized_k = k.lower().replace(" ", "_")
            normalized_metadata[normalized_k] = v
            normalized_metadata[k] = v

        return normalized_metadata

    def _parse_simple_frontmatter(self, frontmatter_text: str) -> dict[str, str]:
        metadata: dict[str, str] = {}
        for line in frontmatter_text.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip().strip('"\'')
        return metadata

    def _extract_acceptance_criteria(self, content: str) -> str:
        content = self._frontmatter_pattern.sub("", content).strip()

        match = self._acceptance_pattern.search(content)
        if match:
            criteria_text = match.group(1).strip()
            lines = [line.strip() for line in criteria_text.split("\n") if line.strip()]
            return "\n".join(lines)

        return ""

    def _extract_dependencies(self, content: str) -> List[str]:
        dependencies: list[str] = []

        match = self._dependency_pattern.search(content)
        if match:
            deps_text = match.group(1).strip()
            deps = [dep.strip() for dep in deps_text.split(",")]
            dependencies.extend([dep for dep in deps if dep])

        return dependencies

    def _extract_feature_code_from_path(self, task_file: Path) -> str:
        # 1. Check direct parent (legacy/flat)
        if bool(re.match(r"^\d+", task_file.parent.name)):
            suffix = re.sub(r"^\d+[-_]*", "", task_file.parent.name)
            return suffix.lower().replace(" ", "-").replace("_", "-")

        # 2. In nested mode, look at the grandparent or higher (e.g. specs/001-login/tasks/t1.md)
        if self._search_recursive:
            current = task_file.parent
            # Look up to 3 levels up for a directory starting with digits
            for _ in range(3):
                if current == current.parent:
                    break
                if bool(re.match(r"^\d+", current.name)):
                    suffix = re.sub(r"^\d+[-_]*", "", current.name)
                    return suffix.lower().replace(" ", "-").replace("_", "-")
                current = current.parent

        # 3. Fallback to stem
        return task_file.stem.lower().replace("-", "").replace("_", "")

    def _extract_task_code_from_heading(self, content: str) -> Optional[str]:
        match = self._task_code_heading_pattern.search(content)
        if not match:
            return None
        return match.group(1).strip().upper()

    def _generate_task_code(self, task_file: Path) -> str:
        return task_file.stem.lower().replace(" ", "-").replace("_", "-")
