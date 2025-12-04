"""
Shared bootstrap option dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BootstrapOptions:
    """
    Command-line flags that influence bootstrap execution.
    """

    dry_run: bool = False
    force: bool = False
    project: Optional[str] = None
    skip_task_runs: bool = False
    skip_ai_jobs: bool = False
