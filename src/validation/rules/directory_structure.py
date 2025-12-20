from __future__ import annotations
from pathlib import Path
from typing import List
import logging

from src.core.config import SpeckitConfig
from src.validation.base import ValidationRule, ValidationError

logger = logging.getLogger(__name__)

class DirectoryStructureRule(ValidationRule):
    """Validates directory structure exists and is correct"""
    
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
    
    def validate(self) -> List[ValidationError]:
        errors = []
        
        # Check required directories
        for dir_name, dir_path in self.config.directories.__dict__.items():
            full_path = self.project_root / dir_path
            
            if not full_path.exists():
                errors.append(ValidationError(
                    code="ERR_MISSING_DIR",
                    message=f"Required directory missing: {dir_path}",
                    file_path=full_path,
                    suggestion=f"Create directory: mkdir -p {dir_path}",
                    auto_fixable=True
                ))
            elif not full_path.is_dir():
                errors.append(ValidationError(
                    code="ERR_NOT_DIRECTORY",
                    message=f"Path exists but is not a directory: {dir_path}",
                    file_path=full_path,
                    suggestion=f"Remove file and create directory: rm {full_path} && mkdir -p {dir_path}",
                    auto_fixable=True
                ))
        
        return errors
    
    def auto_fix(self) -> None:
        """Create missing directories automatically"""
        for dir_name, dir_path in self.config.directories.__dict__.items():
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {full_path}")
