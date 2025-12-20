from __future__ import annotations
from pathlib import Path
from typing import List
import yaml
import logging

from src.core.config import SpeckitConfig
from src.validation.base import ValidationRule, ValidationError

logger = logging.getLogger(__name__)

class FrontmatterRule(ValidationRule):
    """Validates that markdown files have valid frontmatter"""
    
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
    
    def validate(self) -> List[ValidationError]:
        errors = []
        
        # Check all markdown files in features and specs
        dirs_to_check = [
            self.project_root / self.config.directories.features,
            self.project_root / self.config.directories.specs
        ]
        
        for dir_path in dirs_to_check:
            if not dir_path.exists():
                continue
                
            for file_path in dir_path.glob("*.md"):
                if not file_path.is_file():
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if not content.startswith('---'):
                        if self.config.validation.require_frontmatter:
                             errors.append(ValidationError(
                                code="ERR_NO_FRONTMATTER",
                                message=f"File missing YAML frontmatter: {file_path.name}",
                                file_path=file_path,
                                suggestion=f"Add '---\\ncode: ...\\n---' to the top of the file",
                                auto_fixable=False
                            ))
                        continue
                        
                    # Parse frontmatter
                    parts = content.split('---', 2)
                    if len(parts) < 3:
                         errors.append(ValidationError(
                            code="ERR_INVALID_FRONTMATTER_FORMAT",
                            message=f"Invalid frontmatter format: {file_path.name}",
                            file_path=file_path,
                            suggestion=f"Ensure frontmatter is enclosed in '---' blocks",
                            auto_fixable=False
                        ))
                    else:
                        frontmatter_content = parts[1]
                        try:
                            data = yaml.safe_load(frontmatter_content)
                            if not isinstance(data, dict):
                                 errors.append(ValidationError(
                                    code="ERR_INVALID_FRONTMATTER_YAML",
                                    message=f"Frontmatter is not a dictionary: {file_path.name}",
                                    file_path=file_path,
                                    auto_fixable=False
                                ))
                            else:
                                # Standardized Field Validation
                                if "features" in str(dir_path):
                                    if 'code' not in data:
                                        errors.append(ValidationError(
                                            code="ERR_MISSING_FIELD_CODE",
                                            message=f"Feature missing mandatory 'code' field: {file_path.name}",
                                            file_path=file_path,
                                            suggestion="Add 'code: <unique-id>' to frontmatter",
                                            auto_fixable=False
                                        ))
                                elif "specs" in str(dir_path):
                                    if 'code' not in data:
                                        errors.append(ValidationError(
                                            code="ERR_MISSING_FIELD_CODE",
                                            message=f"Spec missing mandatory 'code' field: {file_path.name}",
                                            file_path=file_path,
                                            suggestion="Add 'code: <unique-id>-spec' to frontmatter",
                                            auto_fixable=False
                                        ))
                                    if 'feature_code' not in data:
                                        errors.append(ValidationError(
                                            code="ERR_MISSING_FIELD_FEATURE_REF",
                                            message=f"Spec missing 'feature_code' reference: {file_path.name}",
                                            file_path=file_path,
                                            suggestion="Add 'feature_code: <feature-unique-id>' to frontmatter",
                                            auto_fixable=False
                                        ))

                        except yaml.YAMLError as e:
                             errors.append(ValidationError(
                                code="ERR_INVALID_YAML",
                                message=f"Invalid YAML in frontmatter: {e}",
                                file_path=file_path,
                                auto_fixable=False
                            ))
                            
                except Exception as e:
                     errors.append(ValidationError(
                        code="ERR_READ_FILE",
                        message=f"Could not check frontmatter: {e}",
                        file_path=file_path,
                        auto_fixable=False
                    ))
        
        return errors
