from __future__ import annotations
from pathlib import Path
from typing import List, Dict
import yaml
import logging

from src.core.config import SpeckitConfig
from src.validation.base import ValidationRule, ValidationError

logger = logging.getLogger(__name__)

class DuplicateCodeRule(ValidationRule):
    """Validates that codes (features, specs) are unique across the project"""
    
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
    
    def validate(self) -> List[ValidationError]:
        errors = []
        seen_codes: Dict[str, Path] = {}
        
        # Check features
        features_dir = self.project_root / self.config.directories.features
        if features_dir.exists():
            self._check_dir(features_dir, seen_codes, errors, "code")
            
        # Check specs
        specs_dir = self.project_root / self.config.directories.specs
        if specs_dir.exists():
            self._check_dir(specs_dir, seen_codes, errors, "code")
            
        return errors
        
    def _check_dir(self, dir_path: Path, seen_codes: Dict[str, Path], errors: List[ValidationError], key: str):
        for file_path in dir_path.glob("*.md"):
            if not file_path.is_file():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Quick frontmatter parsing
                    content = f.read()
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 2:
                            data = yaml.safe_load(parts[1])
                            if isinstance(data, dict) and key in data:
                                # Case-insensitive collision detection
                                code = str(data[key]).lower()
                                if code in seen_codes:
                                    prev_path = seen_codes[code]
                                    errors.append(ValidationError(
                                        code="ERR_DUPLICATE_CODE",
                                        message=f"Duplicate code found (case-insensitive): '{code}' in {file_path.name} and {prev_path.name}",
                                        file_path=file_path,
                                        suggestion=f"Change the code in one of the files to be unique",
                                        auto_fixable=False
                                    ))
                                else:
                                    seen_codes[code] = file_path
            except Exception:
                # Parsing errors handled by FrontmatterRule
                pass
