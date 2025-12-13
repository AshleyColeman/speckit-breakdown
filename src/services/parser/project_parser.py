"""
Project parser for extracting project metadata from project.md files.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Optional

from src.models.entities import ProjectDTO
from src.services.parser.parser_utils import parse_yaml_frontmatter

logger = logging.getLogger(__name__)


def _load_json(path: Path) -> list | dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise ValueError(f"Invalid JSON in {path}") from exc


class ProjectParser:
    """Parses project.md files to extract project metadata."""

    def __init__(self, project_file: Path) -> None:
        self._project_file = project_file
        self._title_pattern = re.compile(r'^#\s+(.+)$', re.MULTILINE)
        self._frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---', re.MULTILINE | re.DOTALL)

    def parse(self) -> ProjectDTO:
        """
        Parse a project.md file and return a ProjectDTO.
        
        Args:
            project_file: Path to the project.md file (passed via __init__)
            
        Returns:
            ProjectDTO with extracted metadata
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not self._project_file.exists():
            raise ValueError(f"Project file not found: {self._project_file}")
        
        # Check if it's JSON (legacy) or markdown
        if self._project_file.suffix == '.json':
            return self._parse_json()
        
        return self._parse_markdown()

    def _parse_json(self) -> ProjectDTO:
        """Parse JSON format project file (legacy support)."""
        data = _load_json(self._project_file)
        return ProjectDTO(
            code=data["code"],
            name=data["name"],
            description=data.get("description", ""),
            repository_path=data.get("repository_path"),
            metadata=data.get("metadata", {}),
        )

    def _parse_markdown(self) -> ProjectDTO:
        """Parse markdown project.md file."""
        content = self._project_file.read_text(encoding='utf-8')
        
        # Extract title from first # heading or filename
        title = self._extract_title(content)
        
        # Extract frontmatter metadata
        metadata = self._extract_frontmatter(content)
        
        # Extract description from frontmatter or content
        description = metadata.get('description', '')
        if not description:
            description = self._extract_description_from_content(content)
        
        # Generate project code from directory name or metadata
        project_code = metadata.get('id') or metadata.get('code') or self._generate_project_code()
        
        # Extract repository path if available
        repository_path = metadata.get('repository_path') or metadata.get('repository')
        
        return ProjectDTO(
            code=project_code,
            name=title,
            description=description,
            repository_path=repository_path,
            metadata=metadata
        )

    def _extract_title(self, content: str) -> str:
        """Extract title from content or fallback to filename."""
        match = self._title_pattern.search(content)
        if match:
            return match.group(1).strip()
        
        # Fallback to filename without extension
        return self._project_file.stem.replace('-', ' ').replace('_', ' ').title()

    def _extract_frontmatter(self, content: str) -> dict[str, str]:
        """Extract YAML frontmatter from markdown content."""
        match = self._frontmatter_pattern.search(content)
        if match:
            frontmatter_text = match.group(1)
            try:
                return parse_yaml_frontmatter(frontmatter_text)
            except ValueError as e:
                logger.warning(f"Failed to parse YAML frontmatter: {e}")
                return self._parse_simple_frontmatter(frontmatter_text)
        return {}

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

    def _generate_project_code(self) -> str:
        """Generate project code from directory structure."""
        # Get parent directory name (should be the project directory)
        project_dir = self._project_file.parent
        if project_dir.name == 'specs':
            # If project.md is directly in specs/, use parent directory
            return project_dir.parent.name.lower().replace(' ', '-').replace('_', '-')
        else:
            # Otherwise use the directory containing project.md
            return project_dir.name.lower().replace(' ', '-').replace('_', '-')
