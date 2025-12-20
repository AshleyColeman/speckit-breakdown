from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any

from src.core.config import SpeckitConfig
from src.parsing.base_parser import MarkdownParser

class SpecificationParser(MarkdownParser):
    def __init__(self, config: SpeckitConfig, project_root: Path):
        super().__init__(project_root)
        self.config = config
        
    def parse(self) -> List[Dict[str, Any]]:
        specs_dir = self.project_root / self.config.directories.specs
        return self.parse_directory(specs_dir)
