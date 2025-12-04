"""
Validation pipeline scaffolding for bootstrap operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Protocol, Sequence


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(slots=True, frozen=True)
class ValidationIssue:
    severity: Severity
    message: str
    location: str | None = None


@dataclass(slots=True, frozen=True)
class ValidationResult:
    issues: Sequence[ValidationIssue]

    @property
    def has_blocking_errors(self) -> bool:
        return any(issue.severity in (Severity.ERROR, Severity.CRITICAL) for issue in self.issues)


class ValidationRule(Protocol):
    """Protocol describing validation rules."""

    name: str

    def run(self) -> Iterable[ValidationIssue]:
        ...


class ValidationPipeline:
    """
    Minimal validation pipeline used to sequence rule evaluation.
    """

    def __init__(self, rules: Sequence[ValidationRule]) -> None:
        self._rules = list(rules)

    def execute(self) -> ValidationResult:
        issues: List[ValidationIssue] = []
        for rule in self._rules:
            issues.extend(rule.run())
        return ValidationResult(issues=issues)


class ValidationException(Exception):
    """Raised when blocking validation issues are detected."""

    def __init__(self, result: ValidationResult) -> None:
        super().__init__("Validation failed")
        self.result = result
