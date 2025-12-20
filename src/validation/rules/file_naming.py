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
    
    def auto_fix(self) -> None:
        """Rename files to follow normalization rules"""
        # Fix Features
        features_dir = self.project_root / self.config.directories.features
        if features_dir.exists():
            for file_path in features_dir.glob("*"):
                if not file_path.is_file() or file_path.name.startswith("."):
                    continue
                
                new_name = self._normalize_name(file_path.name)
                if not new_name.endswith(".md"):
                    new_name += ".md"
                
                if new_name != file_path.name:
                    target_path = file_path.parent / new_name
                    if not target_path.exists():
                        file_path.rename(target_path)
                        logger.info(f"Fixed feature naming: {file_path.name} -> {new_name}")

        # Fix Specs
        specs_dir = self.project_root / self.config.directories.specs
        if specs_dir.exists():
            for file_path in specs_dir.glob("*"):
                if not file_path.is_file() or file_path.name.startswith("."):
                    continue
                
                # Ensure it ends with -spec.md
                name_stem = file_path.name
                if name_stem.endswith(".md"):
                    name_stem = name_stem[:-3]
                
                if not name_stem.endswith("-spec"):
                    name_stem += "-spec"
                
                new_name = self._normalize_name(name_stem) + ".md"
                
                if new_name != file_path.name:
                    target_path = file_path.parent / new_name
                    if not target_path.exists():
                        file_path.rename(target_path)
                        logger.info(f"Fixed spec naming: {file_path.name} -> {new_name}")

    def _normalize_name(self, name: str) -> str:
        """Lowercase and replace invalid characters with dashes"""
        name = name.lower()
        # Replace non-alphanumeric (except dots/dashes in extension) with dashes
        return re.sub(r'[^a-z0-9-.]', '-', name).replace('--', '-')

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
                if not file_path.suffix == '.md':
                     errors.append(ValidationError(
                        code="ERR_INVALID_EXT",
                        message=f"Feature file has invalid extension: {file_path.name}",
                        file_path=file_path,
                        suggestion=f"Rename to end with .md",
                        auto_fixable=True
                    ))
                     continue

                if not re.match(r'^[a-z0-9-]+\.md$', file_path.name):
                     errors.append(ValidationError(
                        code="ERR_INVALID_NAME",
                        message=f"Feature file has invalid characters: {file_path.name}",
                        file_path=file_path,
                        suggestion=f"Use only lowercase alphanumeric and dashes, e.g., my-feature.md",
                        auto_fixable=True
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
                if not re.match(r'^[a-z0-9-]+-spec\.md$', file_path.name):
                     errors.append(ValidationError(
                        code="ERR_INVALID_NAME_SPEC",
                        message=f"Spec file must follow 'code-spec.md' convention: {file_path.name}",
                        file_path=file_path,
                        suggestion=f"Rename to match feature code + '-spec.md', e.g., my-feature-spec.md",
                        auto_fixable=True
                    ))

        return errors
