"""
Formatting utilities for surfacing validation issues to operators.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from src.services.validation_pipeline import Severity, ValidationIssue, ValidationResult


def format_validation_report(result: ValidationResult) -> str:
    """
    Render validation issues grouped by severity and location.
    """

    grouped: dict[Severity, list[ValidationIssue]] = defaultdict(list)
    for issue in result.issues:
        grouped[issue.severity].append(issue)

    lines: list[str] = []
    order = [Severity.CRITICAL, Severity.ERROR, Severity.WARNING, Severity.INFO]
    for severity in order:
        items = grouped.get(severity)
        if not items:
            continue
        lines.append(f"{severity.value.upper()} ({len(items)}):")
        for issue in items:
            location = f" [{issue.location}]" if issue.location else ""
            lines.append(f"  - {issue.message}{location}")
        lines.append("")

    if not lines:
        return "No validation issues detected."
    return "\n".join(lines).rstrip()
