"""
Pytest configuration helpers.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Callable

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def project_fixture(tmp_path: Path) -> Callable[[str], Path]:
    """
    Copy a project fixture directory into an isolated temp dir.
    """

    def _copy(name: str) -> Path:
        source = Path("tests/fixtures/projects") / name
        destination = tmp_path / name
        shutil.copytree(source, destination)
        return destination

    return _copy
