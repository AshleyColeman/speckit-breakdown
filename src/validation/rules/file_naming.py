from __future__ import annotations
from pathlib import Path
from typing import List
import re
import logging

from src.core.config import SpeckitConfig
from src.validation.base import ValidationRule, ValidationError

logger = logging.getLogger(__name__)

class FileNamingRule(ValidationRule):
    """Validates that files follow the naming conventions"""
    
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
    
    def validate(self) -> List[ValidationError]:
        errors = []
        
        # Validate Feature Files
        features_dir = self.project_root / self.config.directories.features
        if features_dir.exists():
            for file_path in features_dir.glob("*"):
                if not file_path.is_file():
                    continue
                if file_path.name.startswith("."): # Ignore dotfiles
                    continue
                    
                # Expecting something like "some-feature.md"
                # The config says "feature-code.md", implying [a-z0-9-]+\.md
                if not file_path.suffix == '.md':
                     errors.append(ValidationError(
                        code="ERR_INVALID_EXT",
                        message=f"Feature file has invalid extension: {file_path.name}",
                        file_path=file_path,
                        suggestion=f"Rename to end with .md",
                        auto_fixable=False
                    ))
                     continue

                if not re.match(r'^[a-z0-9-]+\.md$', file_path.name):
                     errors.append(ValidationError(
                        code="ERR_INVALID_NAME",
                        message=f"Feature file has invalid characters: {file_path.name}",
                        file_path=file_path,
                        suggestion=f"Use only lowercase alphanumeric and dashes, e.g., my-feature.md",
                        auto_fixable=False
                    ))

        # Validate Spec Files
        specs_dir = self.project_root / self.config.directories.specs
        if specs_dir.exists():
            for file_path in specs_dir.glob("*"):
                if not file_path.is_file():
                    continue
                if file_path.name.startswith("."):
                    continue
                
                # Expecting "some-feature-spec.md"
                if not file_path.name.endswith("-spec.md"):
                     errors.append(ValidationError(
                        code="ERR_INVALID_NAME_SPEC",
                        message=f"Spec file must end with '-spec.md': {file_path.name}",
                        file_path=file_path,
                        suggestion=f"Rename to match feature code + '-spec.md', e.g., my-feature-spec.md",
                        auto_fixable=False
                    ))

        return errors
