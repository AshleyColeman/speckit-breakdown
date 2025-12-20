from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.core.config import SpeckitConfig
from src.validation.rules import *
from src.validation.base import ValidationError

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    
    def has_blocking_errors(self) -> bool:
        return any(error.code.startswith('ERR_') for error in self.errors)

class ProjectValidator:
    """Comprehensive project validation system"""
    
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
        # Ideally we'd dynamically load rules or pass them in, but for now we hardcode the list 
        # based on what we have implemented. 
        # We will populate this list as we implement the rules.
        from src.validation.rules import (
            DirectoryStructureRule, 
            FileNamingRule,
            FrontmatterRule,
            DuplicateCodeRule,
            CrossReferenceRule,
            JsonSchemaRule
        )
        self.rules = [
            DirectoryStructureRule(config, project_root),
            FileNamingRule(config, project_root),
            FrontmatterRule(config, project_root),
            DuplicateCodeRule(config, project_root),
            CrossReferenceRule(config, project_root),
            JsonSchemaRule(config, project_root)
        ]
    
    def validate(self, strict: bool = False) -> ValidationResult:
        """Run all validation rules"""
        errors = []
        warnings = []
        
        for rule in self.rules:
            rule_errors = rule.validate()
            for error in rule_errors:
                if error.code.startswith('ERR_'):
                    errors.append(error)
                else:
                    warnings.append(error)
        
        # In strict mode, warnings are treated as errors for validity check?
        # The guide says "is_valid = len(errors) == 0 if strict else len(errors) == 0" which is same.
        # But typically strict means warnings count as failures.
        # Let's follow the guide's logic but maybe strict affects exit code in CLI.
        # Guide code: is_valid = len(errors) == 0 if strict else len(errors) == 0 
        # Wait, that logic in the guide `is_valid = len(errors) == 0 if strict else len(errors) == 0` is identical.
        # CLI command says: `elif strict and result.warnings: ctx.exit(1)`
        # So is_valid here refers to BLOCKING errors?
        
        is_valid = len(errors) == 0
        
        if strict and len(warnings) > 0:
             is_valid = False

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    def auto_fix(self) -> ValidationResult:
        """Attempt to auto-fix all fixable issues"""
        for rule in self.rules:
            rule.auto_fix()
        
        return self.validate()
