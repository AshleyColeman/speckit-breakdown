from __future__ import annotations

import logging
import re
from pathlib import Path

from src.models.entities import SpecificationDTO
from src.services.parser.parser_utils import (
    MissingYAMLDependencyError,
    _load_json,
    parse_markdown_key_values,
    parse_yaml_frontmatter,
)

logger = logging.getLogger(__name__)


class SpecificationParser:
    """Parses specification metadata from markdown files in specs/ directory."""

    def __init__(self, specs_dir: Path, search_recursive: bool = False) -> None:
        self._specs_dir = specs_dir
        self._search_recursive = search_recursive
        self._title_pattern = re.compile(r'^#\s+(.+)$', re.MULTILINE)
        self._frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---', re.MULTILINE | re.DOTALL)

    @staticmethod
    def _is_numbered_prefix_dir(path: Path) -> bool:
        return path.is_dir() and bool(re.match(r"^\d+", path.name))

    def parse(self) -> list[SpecificationDTO]:
        specs: list[SpecificationDTO] = []

        if not self._specs_dir.exists():
            logger.warning(f"Specs directory not found: {self._specs_dir}")
            return specs

        # Determine search pattern
        # If recursive, look for md in any subdirectory called 'specs' or 'spec'
        pattern = "**/specs/*.md" if self._search_recursive else "*.md"

        for pattern in (["**/specs/*.md", "**/spec.md"] if self._search_recursive else ["*.md"]):
            for spec_file in self._specs_dir.glob(pattern):
                # Legacy check: skip direct children if they are numbered prefix (handled below)
                if not self._search_recursive and spec_file.parent.name.isdigit():
                    continue

                try:
                    spec = self._parse_spec_file(spec_file)
                    specs.append(spec)
                except MissingYAMLDependencyError:
                    raise
                except Exception as e:
                    raise ValueError(f"Failed to parse spec file {spec_file}: {e}") from e

        # Handle legacy flat structure with numbered subdirs if not recursive
        if not self._search_recursive:
            for spec_dir in self._specs_dir.iterdir():
                if self._is_numbered_prefix_dir(spec_dir):
                    for spec_file in spec_dir.glob("*.md"):
                        try:
                            spec = self._parse_spec_file(spec_file)
                            specs.append(spec)
                        except MissingYAMLDependencyError:
                            raise
                        except Exception as e:
                            raise ValueError(f"Failed to parse spec file {spec_file}: {e}") from e

        if not specs and (self._specs_dir / "specs.json").exists():
            return self._parse_json_specs()

        return specs

    def _parse_spec_file(self, spec_file: Path) -> SpecificationDTO:
        content = spec_file.read_text(encoding="utf-8")

        title = self._extract_title(content, spec_file)
        metadata = self._extract_frontmatter(content)

        feature_code = metadata.get("feature_code", "")
        if not feature_code:
            feature_code = self._extract_feature_code_from_path(spec_file)
        else:
            feature_code = str(feature_code).strip()
            if not any(ch.isspace() for ch in feature_code):
                feature_code = feature_code.lower()

        spec_code = self._generate_spec_code(spec_file)

        return SpecificationDTO(
            code=spec_code,
            feature_code=feature_code,
            title=title,
            path=str(spec_file.relative_to(self._specs_dir.parent)),
            metadata=metadata,
        )

    def _parse_json_specs(self) -> list[SpecificationDTO]:
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
        match = self._title_pattern.search(content)
        if match:
            return match.group(1).strip()

        return spec_file.stem.replace("-", " ").replace("_", " ").title()

    def _extract_frontmatter(self, content: str) -> dict[str, str]:
        metadata: dict[str, str] = {}

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

    def _extract_feature_code_from_path(self, spec_file: Path) -> str:
        # 1. Check direct parent (legacy/flat)
        if bool(re.match(r"^\d+", spec_file.parent.name)):
            suffix = re.sub(r"^\d+[-_]*", "", spec_file.parent.name)
            return suffix.lower().replace(" ", "-").replace("_", "-")

        # 2. In nested mode, look at the grandparent (e.g. specs/001-login/specs/s1.md)
        if self._search_recursive:
            current = spec_file.parent
            # Look up to 3 levels for a directory starting with digits
            for _ in range(3):
                if current == current.parent:
                    break
                if bool(re.match(r"^\d+", current.name)):
                    suffix = re.sub(r"^\d+[-_]*", "", current.name)
                    return suffix.lower().replace(" ", "-").replace("_", "-")
                current = current.parent

        # 3. Fallback to stem
        return spec_file.stem.lower().replace("-", "").replace("_", "")

    def _generate_spec_code(self, spec_file: Path) -> str:
        return spec_file.stem.lower().replace(" ", "-").replace("_", "-")
