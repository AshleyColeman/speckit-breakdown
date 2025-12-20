from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Set
import yaml
import logging
import re

from src.core.config import SpeckitConfig
from src.validation.base import ValidationRule, ValidationError

logger = logging.getLogger(__name__)

class ReferentialIntegrityRule(ValidationRule):
    """Validates references between Features, Specs, and Tasks"""
    
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
        
    def validate(self) -> List[ValidationError]:
        errors = []
        
        # 1. Collect all valid Feature Codes
        feature_codes = self._collect_feature_codes()
        
        # 2. Validate Spec -> Feature references
        errors.extend(self._validate_spec_references(feature_codes))
        
        # 3. Validate Task -> Feature references
        errors.extend(self._validate_task_references(feature_codes))
        
        return errors

    def _collect_feature_codes(self) -> Set[str]:
        feature_codes = set()
        features_dir = self.project_root / self.config.directories.features
        if not features_dir.exists():
            return feature_codes
            
        for file_path in features_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        data = yaml.safe_load(parts[1])
                        if isinstance(data, dict) and 'code' in data:
                            feature_codes.add(str(data['code']).lower())
            except Exception:
                continue
        return feature_codes

    def _validate_spec_references(self, feature_codes: Set[str]) -> List[ValidationError]:
        errors = []
        specs_dir = self.project_root / self.config.directories.specs
        if not specs_dir.exists():
            return errors
            
        for file_path in specs_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        data = yaml.safe_load(parts[1])
                        if isinstance(data, dict) and 'feature_code' in data:
                            f_code = str(data['feature_code']).lower()
                            if f_code not in feature_codes:
                                errors.append(ValidationError(
                                    code="ERR_REF_INVALID_FEATURE",
                                    message=f"Spec '{file_path.name}' references non-existent feature: '{f_code}'",
                                    file_path=file_path,
                                    suggestion="Check the 'feature_code' in frontmatter",
                                    auto_fixable=False
                                ))
            except Exception:
                continue
        return errors

    def _validate_task_references(self, feature_codes: Set[str]) -> List[ValidationError]:
        errors = []
        tasks_path = self.project_root / self.config.directories.tasks / "tasks.json"
        if not tasks_path.exists():
            return errors
            
        try:
            import json
            with open(tasks_path, 'r') as f:
                tasks_data = json.load(f)
                
            if isinstance(tasks_data, list):
                all_task_codes = {str(t.get('code', '')).upper() for t in tasks_data if t.get('code')}
                
                for i, task in enumerate(tasks_data):
                    t_code = task.get('code', f'Index {i}')
                    
                    # Check feature reference
                    f_code = task.get('feature_code')
                    if f_code and str(f_code).lower() not in feature_codes:
                         errors.append(ValidationError(
                            code="ERR_REF_INVALID_FEATURE",
                            message=f"Task '{t_code}' references non-existent feature: '{f_code}'",
                            file_path=tasks_path,
                            suggestion="Check 'feature_code' in tasks.json",
                            auto_fixable=False
                        ))
                    
                    # Check task dependencies
                    deps = task.get('metadata', {}).get('dependencies', [])
                    for dep in deps:
                        if str(dep).upper() not in all_task_codes:
                             errors.append(ValidationError(
                                code="ERR_REF_INVALID_TASK",
                                message=f"Task '{t_code}' depends on unknown task: '{dep}'",
                                file_path=tasks_path,
                                suggestion="Ensure the dependency code matches an existing task code",
                                auto_fixable=False
                            ))
        except Exception as e:
            logger.error(f"Failed to validate tasks referential integrity: {e}")
            
        return errors
