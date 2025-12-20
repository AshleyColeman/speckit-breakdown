from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Set
import yaml
import logging

from src.core.config import SpeckitConfig
from src.validation.base import ValidationRule, ValidationError

logger = logging.getLogger(__name__)

class CrossReferenceRule(ValidationRule):
    """Validates cross-references between features, specs, and tasks"""
    
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
    
    def validate(self) -> List[ValidationError]:
        errors = []
        
        # 1. Collect all valid feature codes
        feature_codes = self._collect_feature_codes()
        
        # 2. Check that all specs reference valid features
        specs_dir = self.project_root / self.config.directories.specs
        if specs_dir.exists():
            for file_path in specs_dir.glob("*.md"):
                if not file_path.is_file(): continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 2:
                                data = yaml.safe_load(parts[1])
                                if isinstance(data, dict):
                                    spec_feature_code = data.get('feature_code')
                                    if spec_feature_code:
                                        if spec_feature_code not in feature_codes:
                                             errors.append(ValidationError(
                                                code="ERR_BROKEN_REF_FEATURE",
                                                message=f"Spec references missing feature: '{spec_feature_code}'",
                                                file_path=file_path,
                                                suggestion=f"Ensure feature '{spec_feature_code}' exists in features directory",
                                                auto_fixable=False
                                            ))
                                    else:
                                         errors.append(ValidationError(
                                            code="ERR_MISSING_REF_FEATURE",
                                            message=f"Spec missing 'feature_code' field",
                                            file_path=file_path,
                                            suggestion=f"Add 'feature_code: ...' to frontmatter",
                                            auto_fixable=False
                                        ))
                except Exception:
                    pass # Handled by FrontmatterRule
                    
        return errors

    def _collect_feature_codes(self) -> Set[str]:
        codes = set()
        features_dir = self.project_root / self.config.directories.features
        if not features_dir.exists():
            return codes
            
        for file_path in features_dir.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 2:
                            data = yaml.safe_load(parts[1])
                            if isinstance(data, dict) and 'code' in data:
                                codes.add(data['code'])
            except Exception:
                pass
        return codes
