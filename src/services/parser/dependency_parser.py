"""
Task dependency parser utilities.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import List, Set

from src.models.entities import TaskDependencyDTO

logger = logging.getLogger(__name__)


def _load_json(path: Path) -> list:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise ValueError(f"Invalid JSON in {path}") from exc


class DependencyParser:
    """Parses task dependency relationships from markdown files and normalizes dependency edges."""

    def __init__(self, dependencies_dir: Path, search_recursive: bool = False) -> None:
        self._dependencies_dir = dependencies_dir
        self._search_recursive = search_recursive
        self._dependency_pattern = re.compile(r'Depends on:\s*([^\n]+)', re.IGNORECASE)
        self._task_reference_pattern = re.compile(r'([A-Z]+-\d+|[a-zA-Z0-9-]+)', re.IGNORECASE)
        self._heading_task_code_pattern = re.compile(r'\b([A-Z]+-\d+|T\d+)\b')

    def parse(self) -> list[TaskDependencyDTO]:
        """Parse dependency relationships from markdown files in dependencies/ directory."""
        dependencies = []
        
        if not self._dependencies_dir.exists():
            logger.warning(f"Dependencies directory not found: {self._dependencies_dir}")
            return dependencies
        
        # Determine search pattern
        pattern = "**/dependencies/*.md" if self._search_recursive else "*.md"

        # Look for markdown files
        for dep_file in self._dependencies_dir.glob(pattern):
            try:
                file_deps = self._parse_dependency_file(dep_file)
                dependencies.extend(file_deps)
            except Exception as e:
                raise ValueError(f"Failed to parse dependency file {dep_file}: {e}") from e
        
        # Also look in numbered dependency directories if not recursive
        if not self._search_recursive:
            for dep_dir in self._dependencies_dir.iterdir():
                if dep_dir.is_dir() and dep_dir.name.isdigit():
                    for dep_file in dep_dir.glob("*.md"):
                        try:
                            file_deps = self._parse_dependency_file(dep_file)
                            dependencies.extend(file_deps)
                        except Exception as e:
                            raise ValueError(f"Failed to parse dependency file {dep_file}: {e}") from e
        
        # Fallback to JSON if no markdown files found
        if not dependencies and (self._dependencies_dir / "dependencies.json").exists():
            return self._parse_json_dependencies()
        
        # Normalize and deduplicate dependencies
        return self._normalize_dependencies(dependencies)

    def parse_from_tasks(self, tasks: List[object]) -> list[TaskDependencyDTO]:
        """Extract dependencies from task metadata (alternative to separate dependency files)."""
        dependencies = []
        
        for task in tasks:
            task_code = getattr(task, 'code', '')
            task_metadata = getattr(task, 'metadata', {})
            task_dependencies = task_metadata.get('dependencies', [])
            
            if isinstance(task_dependencies, list):
                for dep in task_dependencies:
                    if isinstance(dep, str):
                        dependencies.append(TaskDependencyDTO(task_code=task_code, depends_on=dep))
                    elif isinstance(dep, dict) and 'code' in dep:
                        dependencies.append(TaskDependencyDTO(task_code=task_code, depends_on=dep['code']))
        
        return self._normalize_dependencies(dependencies)

    def _parse_dependency_file(self, dep_file: Path) -> List[TaskDependencyDTO]:
        """Parse a single dependency markdown file."""
        content = dep_file.read_text(encoding='utf-8')
        dependencies: list[TaskDependencyDTO] = []

        current_task_code: str = ""
        for line in content.splitlines():
            stripped = line.strip()

            if stripped.startswith("#"):
                heading_match = self._heading_task_code_pattern.search(stripped)
                if heading_match:
                    current_task_code = heading_match.group(1).upper()
                continue

            dep_match = self._dependency_pattern.search(stripped)
            if not dep_match:
                continue

            if not current_task_code:
                logger.warning(f"No context task code found in {dep_file}")
                continue

            deps_text = dep_match.group(1).strip()
            task_codes = self._extract_task_codes(deps_text)
            for dep_code in task_codes:
                dependencies.append(TaskDependencyDTO(task_code=current_task_code, depends_on=dep_code))

        return dependencies

    def _parse_json_dependencies(self) -> list[TaskDependencyDTO]:
        """Parse JSON format dependencies file (legacy support)."""
        data = _load_json(self._dependencies_dir / "dependencies.json")
        return [
            TaskDependencyDTO(task_code=item["task_code"], depends_on=item["depends_on"])
            for item in data
        ]

    def _extract_task_codes(self, text: str) -> List[str]:
        """Extract task codes from dependency text."""
        task_codes = []
        
        # Look for patterns like "TASK-123", "feature-name", etc.
        matches = self._task_reference_pattern.findall(text)
        
        for match in matches:
            # Clean up the match and ensure it looks like a task code
            cleaned = match.strip().upper()
            if cleaned and len(cleaned) >= 2:  # Basic validation
                task_codes.append(cleaned)
        
        return task_codes

    def _extract_context_task_code(self, dep_file: Path, content: str) -> str:
        """Extract the context task code from filename or content."""
        # Try to extract from filename first
        filename_code = dep_file.stem.upper().replace('-', '_')
        if self._looks_like_task_code(filename_code):
            return filename_code
        
        # Look for task code patterns in content
        # This could be enhanced with more sophisticated parsing
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith('#') and 'Task' in line:
                # Try to extract task code from heading
                matches = self._task_reference_pattern.findall(line)
                if matches:
                    return matches[0].upper()
        
        return ''

    def _looks_like_task_code(self, code: str) -> bool:
        """Basic validation if a string looks like a task code."""
        return bool(re.match(r'^(T\d+|[A-Z]+-\d+)$', code))

    def _normalize_dependencies(self, dependencies: List[TaskDependencyDTO]) -> List[TaskDependencyDTO]:
        """Normalize and deduplicate dependency relationships."""
        seen = set()
        normalized = []
        
        for dep in dependencies:
            # Create a unique key for deduplication
            key = (dep.task_code.upper(), dep.depends_on.upper())
            
            if key not in seen:
                seen.add(key)
                # Normalize the dependency DTO
                normalized_dep = TaskDependencyDTO(
                    task_code=dep.task_code.upper(),
                    depends_on=dep.depends_on.upper()
                )
                normalized.append(normalized_dep)
        
        return normalized

    def detect_circular_dependencies(self, dependencies: List[TaskDependencyDTO]) -> List[List[str]]:
        """Detect circular dependencies in the dependency graph."""
        # Build adjacency list
        graph = {}
        for dep in dependencies:
            if dep.task_code not in graph:
                graph[dep.task_code] = []
            graph[dep.task_code].append(dep.depends_on)
        
        # Detect cycles using DFS
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if dfs(neighbor):
                    return True
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return cycles
