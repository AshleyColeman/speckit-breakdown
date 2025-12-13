import builtins

import pytest

from src.services.parser.feature_parser import FeatureParser
from src.services.parser.parser_utils import MissingYAMLDependencyError
from src.services.parser.spec_parser import SpecificationParser
from src.services.parser.task_parser import TaskParser


def _block_yaml_import(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "yaml":
            raise ImportError("blocked for test")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import)


def test_task_parser_fails_fast_when_pyyaml_missing(tmp_path, monkeypatch):
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()

    feature_dir = tasks_dir / "001-user-auth"
    feature_dir.mkdir()

    task_file = feature_dir / "t001.md"
    task_file.write_text(
        """---
feature_code: user-auth
status: pending
---

# T001 Test
""",
        encoding="utf-8",
    )

    _block_yaml_import(monkeypatch)

    parser = TaskParser(tasks_dir)
    with pytest.raises(MissingYAMLDependencyError):
        parser.parse()


def test_spec_parser_fails_fast_when_pyyaml_missing(tmp_path, monkeypatch):
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()

    spec_dir = specs_dir / "001-user-auth"
    spec_dir.mkdir()

    spec_file = spec_dir / "spec.md"
    spec_file.write_text(
        """---
feature_code: user-auth
---

# Spec Title
""",
        encoding="utf-8",
    )

    _block_yaml_import(monkeypatch)

    parser = SpecificationParser(specs_dir)
    with pytest.raises(MissingYAMLDependencyError):
        parser.parse()


def test_feature_parser_fails_fast_when_pyyaml_missing(tmp_path, monkeypatch):
    feature_file = tmp_path / "feature-01.md"
    feature_file.write_text(
        """---
priority: P1
---

# Feature Title
""",
        encoding="utf-8",
    )

    _block_yaml_import(monkeypatch)

    parser = FeatureParser(tmp_path, "DEFAULT")
    with pytest.raises(MissingYAMLDependencyError):
        parser.parse()
