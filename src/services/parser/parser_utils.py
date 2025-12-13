from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class MissingYAMLDependencyError(RuntimeError):
    pass


def parse_yaml_frontmatter(frontmatter_text: str) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        raise MissingYAMLDependencyError(
            "PyYAML is required for YAML frontmatter parsing. Install PyYAML to ensure deterministic parsing behavior."
        ) from exc

    try:
        loaded = yaml.safe_load(frontmatter_text)
    except Exception as exc:
        raise ValueError(f"Invalid YAML frontmatter: {exc}") from exc

    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError("YAML frontmatter must be a mapping (top-level object must be a dict).")
    return loaded


def _load_json(path: Path) -> list | dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise ValueError(f"Invalid JSON in {path}") from exc


def parse_markdown_key_values(content: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    lines = content.split("\n")[:50]

    pattern = re.compile(r"^\s*[*_]{0,2}([a-zA-Z0-9 _-]+?)[*_]{0,2}:\s*(.+)$")

    for line in lines:
        line = line.strip()
        if line.startswith("#") or line.startswith("-") or line.startswith("`"):
            continue

        match = pattern.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()

            if len(key) > 40:
                continue

            metadata[key] = value

    return metadata
