from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
import logging

logger = logging.getLogger(__name__)

class MarkdownParser:
    """Base class for parsing markdown files with YAML frontmatter"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def parse_directory(self, directory: Path, pattern: str = "**/*.md") -> List[Dict[str, Any]]:
        """Recursively parse all markdown files in a directory"""
        results = []
        if not directory.exists():
            return results
            
        for file_path in directory.glob(pattern):
            if not file_path.is_file():
                continue
                
            data = self.parse_file(file_path)
            if data:
                results.append(data)
                
        return results
        
    def parse_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a single markdown file for frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.startswith('---'):
                return None
                
            parts = content.split('---', 2)
            if len(parts) < 3:
                return None
                
            data = yaml.safe_load(parts[1])
            if not isinstance(data, dict):
                return None
                
            # Add metadata
            data['_file_path'] = str(file_path.relative_to(self.project_root))
            data['_file_name'] = file_path.name
            
            return data
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return None
