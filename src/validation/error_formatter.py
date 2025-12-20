from __future__ import annotations
from typing import List
from pathlib import Path

from src.validation.validator import ValidationError, ValidationResult

class ErrorFormatter:
    """Formats validation errors for user consumption"""
    
    @staticmethod
    def format_validation_result(result: ValidationResult) -> str:
        """Format validation result with clear, actionable messages"""
        output = []
        
        if result.is_valid:
            output.append("✅ Project structure is valid!")
            return "\n".join(output)
        
        # Group errors by type
        blocking_errors = [e for e in result.errors if e.code.startswith('ERR_')]
        warnings = [e for e in result.errors if not e.code.startswith('ERR_')]
        
        if blocking_errors:
            output.append("❌ Validation Errors (Blocking)")
            output.append("=" * 40)
            
            for error in blocking_errors:
                output.append(f"• {error.message}")
                if error.file_path:
                    output.append(f"   → {error.file_path}")
                if error.suggestion:
                    output.append(f"   💡 Solution: {error.suggestion}")
                if error.auto_fixable:
                    output.append(f"   🔧 Auto-fix available: speckit validate --fix")
                output.append("")
        
        if warnings:
            output.append("⚠️  Warnings")
            output.append("=" * 20)
            for warning in warnings:
                output.append(f"• {warning.message}")
                if warning.suggestion:
                    output.append(f"   💡 {warning.suggestion}")
                output.append("")
        
        # Add summary
        output.append("📊 Summary")
        output.append(f"   Errors: {len(blocking_errors)}")
        output.append(f"   Warnings: {len(warnings)}")
        
        if any(e.auto_fixable for e in blocking_errors):
            output.append("")
            output.append("🔧 Auto-fix available")
            output.append("   Run: speckit validate --fix")
        
        return "\n".join(output)
