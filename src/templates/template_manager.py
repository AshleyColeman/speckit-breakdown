from __future__ import annotations
import logging
from pathlib import Path
from typing import Dict, Any

from src.core.config import SpeckitConfig
from src.templates.file_templates import FileTemplates

logger = logging.getLogger(__name__)

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
        project_code = self.config.project.get('name', 'my-project').lower().replace(' ', '-')
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
    
    def create_project_file(self, project_code: str, project_name: str) -> Path:
        """Create the mandatory project.md file"""
        # project.md goes into the root of the docs folder, not features/
        # docs_dir is usually parent of features_dir
        docs_dir = self.project_root / self.config.directories.features
        if docs_dir.name == 'features':
            docs_dir = docs_dir.parent
            
        file_path = docs_dir / "project.md"
        content = FileTemplates.project_template(project_code, project_name)
        
        file_path.write_text(content, encoding='utf-8')
        logger.info(f"Created project file: {file_path}")
        return file_path

    def create_tasks_file(self) -> Path:
        """Create a tasks.json file from template"""
        tasks_dir = self.project_root / self.config.directories.tasks
        tasks_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = tasks_dir / "tasks.json"
        content = FileTemplates.tasks_template()
        
        file_path.write_text(content, encoding='utf-8')
        return file_path
