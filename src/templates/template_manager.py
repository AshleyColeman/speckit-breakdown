from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

from src.core.config import SpeckitConfig
from src.templates.file_templates import FileTemplates

class TemplateManager:
    """Manages file creation from templates"""
    
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
    
    def create_feature_file(self, feature_code: str, feature_name: str) -> Path:
        """Create a new feature file from template"""
        features_dir = self.project_root / self.config.directories.features
        features_dir.mkdir(parents=True, exist_ok=True)
        
        feature_code = feature_code.lower()
        file_path = features_dir / f"{feature_code}.md"
        content = FileTemplates.feature_template(feature_code, feature_name)
        
        # Replace project code placeholder
        project_code = self.config.project.get('name', 'my-project')
        content = content.replace('{{project_code}}', project_code)
        
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def create_spec_file(self, feature_code: str, feature_name: str) -> Path:
        """Create a new spec file from template"""
        specs_dir = self.project_root / self.config.directories.specs
        specs_dir.mkdir(parents=True, exist_ok=True)
        
        feature_code = feature_code.lower()
        file_path = specs_dir / f"{feature_code}-spec.md"
        content = FileTemplates.spec_template(feature_code, feature_name)
        
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def create_tasks_file(self) -> Path:
        """Create a tasks.json file from template"""
        tasks_dir = self.project_root / self.config.directories.tasks
        tasks_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = tasks_dir / "tasks.json"
        content = FileTemplates.tasks_template()
        
        file_path.write_text(content, encoding='utf-8')
        return file_path
