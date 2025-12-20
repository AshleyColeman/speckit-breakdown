from __future__ import annotations
from pathlib import Path
from typing import List
import json
import logging

from src.core.config import SpeckitConfig
from src.validation.base import ValidationRule, ValidationError

logger = logging.getLogger(__name__)

class JsonSchemaRule(ValidationRule):
    """Validates tasks.json schema"""
    
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
    
    def validate(self) -> List[ValidationError]:
        errors = []
        
        tasks_path = self.project_root / self.config.directories.tasks / self.config.naming.tasks
        
        if not tasks_path.exists():
             # DirectoryStructureRule handles the directory missing, but if the file is missing?
             # Guide doesn't explicitly say tasks.json must exist, but usually it does.
             # Let's say it's fine if it doesn't exist yet, or maybe it should exist.
             # Given "tasks: str = 'tasks.json'", maybe we expect it.
             # I'll check if parent dir exists at least.
             pass
        else:
            try:
                with open(tasks_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if not isinstance(data, list):
                     errors.append(ValidationError(
                        code="ERR_TASKS_NOT_LIST",
                        message=f"tasks.json root must be a list",
                        file_path=tasks_path,
                        auto_fixable=False
                    ))
                else:
                    for i, item in enumerate(data):
                        if not isinstance(item, dict):
                            errors.append(ValidationError(
                                code="ERR_TASK_ITEM_NOT_DICT",
                                message=f"Task item {i} is not a dictionary",
                                file_path=tasks_path,
                                auto_fixable=False
                            ))
                            continue
                            
                        # Check required fields
                        required = ['code', 'feature_code', 'title', 'status']
                        missing = [f for f in required if f not in item]
                        if missing:
                             errors.append(ValidationError(
                                code="ERR_TASK_MISSING_FIELDS",
                                message=f"Task item {i} missing fields: {missing}",
                                file_path=tasks_path,
                                auto_fixable=False
                            ))
            except json.JSONDecodeError as e:
                 errors.append(ValidationError(
                    code="ERR_INVALID_JSON",
                    message=f"Invalid JSON in tasks.json: {e}",
                    file_path=tasks_path,
                    auto_fixable=False
                ))
            except Exception as e:
                 errors.append(ValidationError(
                    code="ERR_READ_TASKS",
                    message=f"Could not read tasks.json: {e}",
                    file_path=tasks_path,
                    auto_fixable=False
                ))
                
        return errors
