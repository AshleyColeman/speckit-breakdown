"""
Feature, specification, and task parser utilities.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable

from src.models.entities import (
    FeatureDTO,
)
from src.services.parser.parser_utils import MissingYAMLDependencyError, _load_json, parse_markdown_key_values
from src.services.parser.parser_utils import parse_yaml_frontmatter
from src.services.parser.spec_parser import SpecificationParser
from src.services.parser.task_parser import TaskParser

logger = logging.getLogger(__name__)

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
            except MissingYAMLDependencyError:
                raise
            except Exception as e:
                raise ValueError(f"Failed to parse feature file {feature_file}: {e}") from e
        
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
        raw_description = metadata.get('description', '')
        if isinstance(raw_description, list):
            description = '\n'.join(map(str, raw_description))
        else:
            description = str(raw_description)

        if not description:
            description = self._extract_description_from_content(content)
        
        # Extract priority from metadata or default to P2
        priority = str(metadata.get('priority', 'P2'))
        
        # Generate feature code from filename
        feature_code = metadata.get('code')
        if not feature_code:
            feature_code = self._generate_feature_code(feature_file)
        else:
            feature_code = str(feature_code).strip().lower()
        
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
                metadata = parse_yaml_frontmatter(frontmatter_text)
            except ValueError as e:
                raise ValueError(f"Invalid YAML frontmatter: {e}") from e
                
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
        name = feature_file.stem
        raw_name = name
        # Strip leading F01_ or 01- or similar numbered prefixes
        if bool(re.match(r"^[A-Za-z]?\d+", name)):
            name = re.sub(r"^[A-Za-z]?\d+[-_]*", "", name)
            
        # If stripping everything resulted in empty string (e.g. f01.md), keep the raw name
        if not name:
            name = raw_name
            
        return name.lower().replace(' ', '-').replace('_', '-')


def extract_dependencies(tasks_payload: Iterable[dict]) -> list[tuple[str, str]]:
    """Utility to derive dependency tuples from task payloads."""
    deps: list[tuple[str, str]] = []
    for task in tasks_payload:
        for dep in task.get("dependencies", []):
            deps.append((task["code"], dep))
    return deps
