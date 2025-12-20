from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import json

from src.core.config import SpeckitConfig

class TaskParser:
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
        
    def parse(self) -> List[Dict[str, Any]]:
        tasks_path = self.project_root / self.config.directories.tasks / self.config.naming.tasks
        if not tasks_path.exists():
            return []
            
        try:
            with open(tasks_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
        return []
