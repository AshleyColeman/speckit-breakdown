"""
Error reporting utilities for validation failures.
"""

from __future__ import annotations

from typing import List, Dict
from src.services.validation_pipeline import ValidationResult, Severity

class ErrorReporter:
    """Formats validation results for CLI output."""

    @staticmethod
    def format_report(result: ValidationResult) -> str:
        """
        Generates a human-readable report string from a ValidationResult.
        """
        lines = []
        
        # Group issues by severity
        errors = [i for i in result.issues if i.severity in (Severity.ERROR, Severity.CRITICAL)]
        warnings = [i for i in result.issues if i.severity == Severity.WARNING]

        if errors:
            lines.append("\n❌ VALIDATION ERRORS (BLOCKING)")
            lines.append("==============================")
            for issue in errors:
                loc = f" [{issue.location}]" if issue.location else ""
                lines.append(f"• {issue.message}{loc}")
        
        if warnings:
            lines.append("\n⚠️  VALIDATION WARNINGS")
            lines.append("=======================")
            for issue in warnings:
                loc = f" [{issue.location}]" if issue.location else ""
                lines.append(f"• {issue.message}{loc}")

        if not errors and not warnings:
            lines.append("✅ No validation issues found.")
            
        return "\n".join(lines)
