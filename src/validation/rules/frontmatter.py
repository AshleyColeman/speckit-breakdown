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
                                    elif not str(data['code']).islower():
                                         errors.append(ValidationError(
                                            code="ERR_FIELD_CASE",
                                            message=f"Feature 'code' must be lowercase: {data['code']}",
                                            file_path=file_path,
                                            suggestion=f"Change to '{str(data['code']).lower()}'",
                                            auto_fixable=True
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
                                    elif not str(data['code']).islower():
                                         errors.append(ValidationError(
                                            code="ERR_FIELD_CASE",
                                            message=f"Spec 'code' must be lowercase: {data['code']}",
                                            file_path=file_path,
                                            suggestion=f"Change to '{str(data['code']).lower()}'",
                                            auto_fixable=True
                                        ))

                                    if 'feature_code' not in data:
                                        errors.append(ValidationError(
                                            code="ERR_MISSING_FIELD_FEATURE_REF",
                                            message=f"Spec missing 'feature_code' reference: {file_path.name}",
                                            file_path=file_path,
                                            suggestion="Add 'feature_code: <feature-unique-id>' to frontmatter",
                                            auto_fixable=False
                                        ))
                                    elif not str(data['feature_code']).islower():
                                         errors.append(ValidationError(
                                            code="ERR_FIELD_CASE",
                                            message=f"Spec 'feature_code' must be lowercase: {data['feature_code']}",
                                            file_path=file_path,
                                            suggestion=f"Change to '{str(data['feature_code']).lower()}'",
                                            auto_fixable=True
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
    
    def auto_fix(self) -> None:
        """Fix field casing in frontmatter"""
        dirs_to_check = [
            self.project_root / self.config.directories.features,
            self.project_root / self.config.directories.specs
        ]
        
        for dir_path in dirs_to_check:
            if not dir_path.exists(): continue
            for file_path in dir_path.glob("*.md"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if not content.startswith('---'): continue
                    
                    parts = content.split('---', 2)
                    if len(parts) < 3: continue
                    
                    data = yaml.safe_load(parts[1])
                    if not isinstance(data, dict): continue
                    
                    changed = False
                    for key in ['code', 'feature_code', 'project_code']:
                        if key in data and str(data[key]) != str(data[key]).lower():
                            data[key] = str(data[key]).lower()
                            changed = True
                    
                    if changed:
                        new_frontmatter = yaml.dump(data, default_flow_style=False)
                        new_content = f"--- \n{new_frontmatter}---{parts[2]}"
                        file_path.write_text(new_content, encoding='utf-8')
                        logger.info(f"Fixed frontmatter casing in {file_path.name}")
                        
                except Exception:
                    continue
