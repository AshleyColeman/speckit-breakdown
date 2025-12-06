"""
Feature, specification, and task parser utilities.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Iterable, List, Optional

from src.models.entities import (
    FeatureDTO,
    SpecificationDTO,
    TaskDTO,
)

logger = logging.getLogger(__name__)


def _load_json(path: Path) -> list | dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise ValueError(f"Invalid JSON in {path}") from exc


def parse_markdown_key_values(content: str) -> dict[str, str]:
    """Scan content for **Key**: Value patterns common in agent outputs."""
    metadata = {}
    # Scan first 50 lines only to avoid false positives in deep descriptions
    lines = content.split('\n')[:50]
    
    # Regex for "**Key**: Value" or "*Key*: Value" or "Key: Value" (at start of line)
    # We accept:
    # **Priority**: P1
    # **Business Value**: 8/10
    # Project Code: PROJ-001
    pattern = re.compile(r'^\s*[*_]{0,2}([a-zA-Z0-9 _-]+?)[*_]{0,2}:\s*(.+)$')
    
    for line in lines:
        line = line.strip()
        # Skip headers, lists, code blocks
        if line.startswith('#') or line.startswith('-') or line.startswith('`'):
            continue
            
        match = pattern.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            # Filter out likely false positives (sentences that happen to have a colon)
            # Heuristic: Key shouldn't be too long (> 40 chars)
            if len(key) > 40:
                continue
                
            metadata[key] = value
            
    return metadata
class FeatureParser:
    """Parses feature metadata from markdown files in features/ directory."""

    def __init__(self, features_dir: Path, project_code: str) -> None:
        self._features_dir = features_dir
        self._project_code = project_code
        self._title_pattern = re.compile(r'^#\s+(.+)$', re.MULTILINE)
        self._frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---', re.MULTILINE | re.DOTALL)

    def parse(self) -> list[FeatureDTO]:
        """Parse all feature markdown files in the features directory."""
        features = []
        
        if not self._features_dir.exists():
            logger.warning(f"Features directory not found: {self._features_dir}")
            return features
        
        # Look for markdown files
        for feature_file in self._features_dir.glob("*.md"):
            try:
                feature = self._parse_feature_file(feature_file)
                features.append(feature)
            except Exception as e:
                logger.error(f"Failed to parse feature file {feature_file}: {e}")
                continue
        
        # Fallback to JSON if no markdown files found
        if not features and (self._features_dir / "features.json").exists():
            return self._parse_json_features()
        
        return features

    def _parse_feature_file(self, feature_file: Path) -> FeatureDTO:
        """Parse a single feature markdown file."""
        content = feature_file.read_text(encoding='utf-8')
        
        # Extract title from first # heading or filename
        title = self._extract_title(content, feature_file)
        
        # Extract frontmatter metadata
        metadata = self._extract_frontmatter(content)
        
        # Extract description from frontmatter or content
        description = metadata.get('description', '')
        if not description:
            description = self._extract_description_from_content(content)
        
        # Extract priority from metadata or default to P2
        priority = metadata.get('priority', 'P2')
        
        # Generate feature code from filename
        feature_code = self._generate_feature_code(feature_file)
        
        return FeatureDTO(
            code=feature_code,
            project_code=metadata.get('project_id') or metadata.get('project_code') or self._project_code,
            name=title,
            description=description,
            priority=priority,
            metadata=metadata
        )

    def _parse_json_features(self) -> list[FeatureDTO]:
        """Parse JSON format features file (legacy support)."""
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

    def _extract_title(self, content: str, feature_file: Path) -> str:
        """Extract title from content or fallback to filename."""
        match = self._title_pattern.search(content)
        if match:
            return match.group(1).strip()
        
        # Fallback to filename without extension
        return feature_file.stem.replace('-', ' ').replace('_', ' ').title()

    def _extract_frontmatter(self, content: str) -> dict[str, str]:
        """Extract metadata from YAML frontmatter or markdown key-value pairs."""
        metadata = {}
        
        # 1. Try YAML frontmatter first
        match = self._frontmatter_pattern.search(content)
        if match:
            frontmatter_text = match.group(1)
            try:
                import yaml
                metadata = yaml.safe_load(frontmatter_text) or {}
            except ImportError:
                logger.warning("PyYAML not available, parsing frontmatter manually")
                metadata = self._parse_simple_frontmatter(frontmatter_text)
            except Exception as e:
                logger.warning(f"Failed to parse YAML frontmatter: {e}")
                metadata = self._parse_simple_frontmatter(frontmatter_text)
                
        # 2. Markdown Key-Values fallback/merge
        markdown_metadata = parse_markdown_key_values(content)
        
        # Merge, preferring frontmatter if conflict
        for k, v in markdown_metadata.items():
            if k not in metadata:
                metadata[k] = v
                
        # Normalize keys (handle case sensitivity)
        normalized_metadata = {}
        for k, v in metadata.items():
            normalized_k = k.lower().replace(' ', '_')
            normalized_metadata[normalized_k] = v
            normalized_metadata[k] = v
            
        return normalized_metadata

    def _parse_simple_frontmatter(self, frontmatter_text: str) -> dict[str, str]:
        """Simple key: value parser for basic frontmatter without yaml."""
        metadata = {}
        for line in frontmatter_text.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
        return metadata



    def _extract_description_from_content(self, content: str) -> str:
        """Extract description from content paragraphs."""
        # Remove frontmatter
        content = self._frontmatter_pattern.sub('', content).strip()
        
        # Find first paragraph after title
        lines = content.split('\n')
        description_lines = []
        
        skip_next_line = False
        for line in lines:
            line = line.strip()
            
            if skip_next_line:
                skip_next_line = False
                continue
                
            # Skip title lines
            if line.startswith('#'):
                skip_next_line = True
                continue
                
            # Skip empty lines and code blocks
            if not line or line.startswith('```'):
                continue
                
            # Stop at next heading
            if line.startswith('#'):
                break
                
            description_lines.append(line)
            
            # Stop after a reasonable description length
            if len(' '.join(description_lines)) > 200:
                break
        
        description = ' '.join(description_lines)
        return description[:200] + ('...' if len(description) > 200 else '')

    def _generate_feature_code(self, feature_file: Path) -> str:
        """Generate feature code from filename."""
        return feature_file.stem.lower().replace(' ', '-').replace('_', '-')


class SpecificationParser:
    """Parses specification metadata from markdown files in specs/ directory."""

    def __init__(self, specs_dir: Path) -> None:
        self._specs_dir = specs_dir
        self._title_pattern = re.compile(r'^#\s+(.+)$', re.MULTILINE)
        self._frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---', re.MULTILINE | re.DOTALL)

    def parse(self) -> list[SpecificationDTO]:
        """Parse all specification markdown files in the specs directory."""
        specs = []
        
        if not self._specs_dir.exists():
            logger.warning(f"Specs directory not found: {self._specs_dir}")
            return specs
        
        # Look for markdown files (excluding subdirectories with numeric prefixes)
        for spec_file in self._specs_dir.glob("*.md"):
            # Skip if this is a spec directory with numeric prefix
            if spec_file.parent.name.isdigit():
                continue
                
            try:
                spec = self._parse_spec_file(spec_file)
                specs.append(spec)
            except Exception as e:
                logger.error(f"Failed to parse spec file {spec_file}: {e}")
                continue
        
        # Also look in numbered spec directories
        for spec_dir in self._specs_dir.iterdir():
            if spec_dir.is_dir() and spec_dir.name.isdigit():
                for spec_file in spec_dir.glob("*.md"):
                    try:
                        spec = self._parse_spec_file(spec_file)
                        specs.append(spec)
                    except Exception as e:
                        logger.error(f"Failed to parse spec file {spec_file}: {e}")
                        continue
        
        # Fallback to JSON if no markdown files found
        if not specs and (self._specs_dir / "specs.json").exists():
            return self._parse_json_specs()
        
        return specs

    def _parse_spec_file(self, spec_file: Path) -> SpecificationDTO:
        """Parse a single specification markdown file."""
        content = spec_file.read_text(encoding='utf-8')
        
        # Extract title from first # heading or filename
        title = self._extract_title(content, spec_file)
        
        # Extract frontmatter metadata
        metadata = self._extract_frontmatter(content)
        
        # Extract feature code from metadata or directory structure
        feature_code = metadata.get('feature_code', '')
        if not feature_code:
            feature_code = self._extract_feature_code_from_path(spec_file)
        
        # Generate spec code from filename
        spec_code = self._generate_spec_code(spec_file)
        
        return SpecificationDTO(
            code=spec_code,
            feature_code=feature_code,
            title=title,
            path=str(spec_file.relative_to(self._specs_dir.parent)),
            metadata=metadata
        )

    def _parse_json_specs(self) -> list[SpecificationDTO]:
        """Parse JSON format specs file (legacy support)."""
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

    def _extract_title(self, content: str, spec_file: Path) -> str:
        """Extract title from content or fallback to filename."""
        match = self._title_pattern.search(content)
        if match:
            return match.group(1).strip()
        
        # Fallback to filename without extension
        return spec_file.stem.replace('-', ' ').replace('_', ' ').title()

    def _extract_frontmatter(self, content: str) -> dict[str, str]:
        """Extract metadata from YAML frontmatter or markdown key-value pairs."""
        metadata = {}
        
        match = self._frontmatter_pattern.search(content)
        if match:
            frontmatter_text = match.group(1)
            try:
                import yaml
                metadata = yaml.safe_load(frontmatter_text) or {}
            except ImportError:
                logger.warning("PyYAML not available, parsing frontmatter manually")
                metadata = self._parse_simple_frontmatter(frontmatter_text)
            except Exception as e:
                logger.warning(f"Failed to parse YAML frontmatter: {e}")
                metadata = self._parse_simple_frontmatter(frontmatter_text)

        # Markdown Key-Values fallback/merge
        markdown_metadata = parse_markdown_key_values(content)
        for k, v in markdown_metadata.items():
            if k not in metadata:
                metadata[k] = v
                
        # Normalize
        normalized_metadata = {}
        for k, v in metadata.items():
            normalized_k = k.lower().replace(' ', '_')
            normalized_metadata[normalized_k] = v
            normalized_metadata[k] = v
            
        return normalized_metadata

    def _parse_simple_frontmatter(self, frontmatter_text: str) -> dict[str, str]:
        """Simple key: value parser for basic frontmatter without yaml."""
        metadata = {}
        for line in frontmatter_text.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
        return metadata

    def _extract_feature_code_from_path(self, spec_file: Path) -> str:
        """Extract feature code from file path structure."""
        # If spec is in a numbered directory, use that directory name
        if spec_file.parent.name.isdigit():
            return spec_file.parent.name.lower().replace('-', '').replace('_', '')
        
        # Otherwise try to infer from filename
        return spec_file.stem.lower().replace('-', '').replace('_', '')

    def _generate_spec_code(self, spec_file: Path) -> str:
        """Generate spec code from filename."""
        return spec_file.stem.lower().replace(' ', '-').replace('_', '-')


class TaskParser:
    """Parses task metadata and dependencies from markdown files in tasks/ directory."""

    def __init__(self, tasks_dir: Path) -> None:
        self._tasks_dir = tasks_dir
        self._title_pattern = re.compile(r'^#\s+(.+)$', re.MULTILINE)
        self._frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---', re.MULTILINE | re.DOTALL)
        self._acceptance_pattern = re.compile(r'## Acceptance Criteria\s*\n(.*?)(?=\n##|\n#|\Z)', re.MULTILINE | re.DOTALL)
        self._dependency_pattern = re.compile(r'Depends on:\s*([^\n]+)', re.IGNORECASE)

    def parse(self) -> List[TaskDTO]:
        """Parse all task markdown files in the tasks directory."""
        tasks = []
        
        if not self._tasks_dir.exists():
            logger.warning(f"Tasks directory not found: {self._tasks_dir}")
            return tasks
        
        # Look for markdown files (excluding subdirectories with numeric prefixes)
        for task_file in self._tasks_dir.glob("*.md"):
            # Skip if this is a task directory with numeric prefix
            if task_file.parent.name.isdigit():
                continue
                
            try:
                task = self._parse_task_file(task_file)
                tasks.append(task)
            except Exception as e:
                logger.error(f"Failed to parse task file {task_file}: {e}")
                continue
        
        # Also look in numbered task directories
        for task_dir in self._tasks_dir.iterdir():
            if task_dir.is_dir() and task_dir.name.isdigit():
                for task_file in task_dir.glob("*.md"):
                    try:
                        task = self._parse_task_file(task_file)
                        tasks.append(task)
                    except Exception as e:
                        logger.error(f"Failed to parse task file {task_file}: {e}")
                        continue
        
        # Fallback to JSON if no markdown files found
        if not tasks and (self._tasks_dir / "tasks.json").exists():
            return self._parse_json_tasks()
        
        return tasks

    def _parse_task_file(self, task_file: Path) -> TaskDTO:
        """Parse a single task markdown file."""
        content = task_file.read_text(encoding='utf-8')
        
        # Extract title from first # heading or filename
        title = self._extract_title(content, task_file)
        
        # Extract frontmatter metadata
        metadata = self._extract_frontmatter(content)
        
        # Extract feature code from metadata or directory structure
        feature_code = metadata.get('feature_code', '')
        if not feature_code:
            feature_code = self._extract_feature_code_from_path(task_file)
        
        # Extract status from metadata or default to pending
        status = metadata.get('status', 'pending')
        
        # Extract task type from metadata or default to implementation
        task_type = metadata.get('task_type', 'implementation')
        
        # Extract acceptance criteria
        acceptance = self._extract_acceptance_criteria(content)
        if not acceptance:
            acceptance = metadata.get('acceptance', '')
        
        # Extract dependencies and store in metadata
        dependencies = self._extract_dependencies(content)
        if dependencies:
            metadata['dependencies'] = dependencies
        
        # Generate task code from filename
        task_code = self._generate_task_code(task_file)
        
        return TaskDTO(
            code=task_code,
            feature_code=feature_code,
            title=title,
            status=status,
            task_type=task_type,
            acceptance=acceptance,
            metadata=metadata
        )

    def _parse_json_tasks(self) -> List[TaskDTO]:
        """Parse JSON format tasks file (legacy support)."""
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
        """Extract title from content or fallback to filename."""
        match = self._title_pattern.search(content)
        if match:
            return match.group(1).strip()
        
        # Fallback to filename without extension
        return task_file.stem.replace('-', ' ').replace('_', ' ').title()

    def _extract_frontmatter(self, content: str) -> dict[str, str]:
        """Extract metadata from YAML frontmatter or markdown key-value pairs."""
        metadata = {}
        
        match = self._frontmatter_pattern.search(content)
        if match:
            frontmatter_text = match.group(1)
            try:
                import yaml
                metadata = yaml.safe_load(frontmatter_text) or {}
            except ImportError:
                logger.warning("PyYAML not available, parsing frontmatter manually")
                metadata = self._parse_simple_frontmatter(frontmatter_text)
            except Exception as e:
                logger.warning(f"Failed to parse YAML frontmatter: {e}")
                metadata = self._parse_simple_frontmatter(frontmatter_text)

        # Markdown Key-Values fallback/merge
        markdown_metadata = parse_markdown_key_values(content)
        for k, v in markdown_metadata.items():
            if k not in metadata:
                metadata[k] = v
                
        # Normalize
        normalized_metadata = {}
        for k, v in metadata.items():
            normalized_k = k.lower().replace(' ', '_')
            normalized_metadata[normalized_k] = v
            normalized_metadata[k] = v
            
        return normalized_metadata

    def _parse_simple_frontmatter(self, frontmatter_text: str) -> dict[str, str]:
        """Simple key: value parser for basic frontmatter without yaml."""
        metadata = {}
        for line in frontmatter_text.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
        return metadata

    def _extract_acceptance_criteria(self, content: str) -> str:
        """Extract acceptance criteria from content."""
        # Remove frontmatter
        content = self._frontmatter_pattern.sub('', content).strip()
        
        match = self._acceptance_pattern.search(content)
        if match:
            criteria_text = match.group(1).strip()
            # Clean up the criteria text
            lines = [line.strip() for line in criteria_text.split('\n') if line.strip()]
            return '\n'.join(lines)
        
        return ''

    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract task dependencies from content."""
        dependencies = []
        
        # Look for explicit dependency declarations
        match = self._dependency_pattern.search(content)
        if match:
            deps_text = match.group(1).strip()
            # Split by commas and clean up
            deps = [dep.strip() for dep in deps_text.split(',')]
            dependencies.extend([dep for dep in deps if dep])
        
        # Also check frontmatter for dependencies
        return dependencies

    def _extract_feature_code_from_path(self, task_file: Path) -> str:
        """Extract feature code from file path structure."""
        # If task is in a numbered directory, use that directory name
        if task_file.parent.name.isdigit():
            return task_file.parent.name.lower().replace('-', '').replace('_', '')
        
        # Otherwise try to infer from filename
        return task_file.stem.lower().replace('-', '').replace('_', '')

    def _generate_task_code(self, task_file: Path) -> str:
        """Generate task code from filename."""
        return task_file.stem.lower().replace(' ', '-').replace('_', '-')


def extract_dependencies(tasks_payload: Iterable[dict]) -> list[tuple[str, str]]:
    """Utility to derive dependency tuples from task payloads."""
    deps: list[tuple[str, str]] = []
    for task in tasks_payload:
        for dep in task.get("dependencies", []):
            deps.append((task["code"], dep))
    return deps
