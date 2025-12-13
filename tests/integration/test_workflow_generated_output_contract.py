from __future__ import annotations

import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from src.cli import app
from tests.fixtures.projects.full_project import create_full_project


runner = CliRunner()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _has_yaml_frontmatter(text: str) -> bool:
    return bool(re.match(r"^---\s*\n.*?\n---\s*\n", text, flags=re.DOTALL))


def _extract_frontmatter_block(text: str) -> str:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if not match:
        return ""
    return match.group(1)


def _frontmatter_has_key(frontmatter_block: str, key: str) -> bool:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*.+$", flags=re.MULTILINE)
    return bool(pattern.search(frontmatter_block))


def _assert_markdown_has_heading(text: str, heading: str) -> None:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", flags=re.MULTILINE)
    assert pattern.search(text), f"Missing required heading: ## {heading}"


def _assert_output_contract(docs_root: Path) -> None:
    project_file = docs_root / "project.md"
    assert project_file.exists(), "Missing project.md"
    project_text = _read_text(project_file)
    assert _has_yaml_frontmatter(project_text), "project.md must include YAML frontmatter"
    project_frontmatter = _extract_frontmatter_block(project_text)
    assert _frontmatter_has_key(project_frontmatter, "name"), "project.md frontmatter must include name"
    assert _frontmatter_has_key(
        project_frontmatter, "description"
    ), "project.md frontmatter must include description"

    for dirname in ("features", "specs", "tasks"):
        assert (docs_root / dirname).exists(), f"Missing required directory: {dirname}/"

    feature_files = sorted((docs_root / "features").glob("*.md"))
    assert feature_files, "Expected at least one feature markdown file"
    for path in feature_files:
        text = _read_text(path)
        assert _has_yaml_frontmatter(text), f"{path.name} must include YAML frontmatter"
        frontmatter = _extract_frontmatter_block(text)
        assert _frontmatter_has_key(frontmatter, "feature_code"), f"{path.name} must include feature_code"
        assert _frontmatter_has_key(frontmatter, "priority"), f"{path.name} must include priority"

    spec_files = sorted((docs_root / "specs").rglob("*.md"))
    assert spec_files, "Expected at least one spec markdown file"
    for path in spec_files:
        text = _read_text(path)
        assert _has_yaml_frontmatter(text), f"{path.relative_to(docs_root)} must include YAML frontmatter"
        frontmatter = _extract_frontmatter_block(text)
        assert _frontmatter_has_key(frontmatter, "feature_code"), f"{path.name} must include feature_code"

    task_files = sorted((docs_root / "tasks").rglob("*.md"))
    assert task_files, "Expected at least one task markdown file"
    for path in task_files:
        text = _read_text(path)
        assert _has_yaml_frontmatter(text), f"{path.relative_to(docs_root)} must include YAML frontmatter"
        frontmatter = _extract_frontmatter_block(text)
        assert _frontmatter_has_key(frontmatter, "feature_code"), f"{path.name} must include feature_code"
        assert _frontmatter_has_key(frontmatter, "status"), f"{path.name} must include status"
        assert _frontmatter_has_key(frontmatter, "task_type"), f"{path.name} must include task_type"
        _assert_markdown_has_heading(text, "Description")
        _assert_markdown_has_heading(text, "Acceptance Criteria")


def test_workflow_output_contract_full_project(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    create_full_project(project_dir)

    result = runner.invoke(app, ["--docs-path", str(project_dir), "--dry-run"])

    assert result.exit_code == 0
    assert "Bootstrap completed successfully" in result.stdout

    _assert_output_contract(project_dir)


def test_workflow_output_contract_detects_missing_task_acceptance(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    create_full_project(project_dir)

    task_file = next((project_dir / "tasks").rglob("*.md"))
    original = _read_text(task_file)
    mutated = re.sub(r"^##\s+Acceptance Criteria\s*$", "## Criteria", original, flags=re.MULTILINE)
    task_file.write_text(mutated, encoding="utf-8")

    result = runner.invoke(app, ["--docs-path", str(project_dir), "--dry-run"])
    assert result.exit_code == 0

    with pytest.raises(AssertionError):
        _assert_output_contract(project_dir)
