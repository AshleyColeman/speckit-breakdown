from __future__ import annotations
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class DirectoryConfig:
    features: str = "docs/features"
    specs: str = "docs/specs"
    tasks: str = "docs/tasks"
    dependencies: str = "docs/dependencies"

@dataclass
class NamingConfig:
    features: str = "feature-code.md"           # cli-interface.md
    specs: str = "feature-code-spec.md"        # cli-interface-spec.md
    tasks: str = "tasks.json"
    
@dataclass
class ValidationConfig:
    strict: bool = True
    auto_fix: bool = True
    require_frontmatter: bool = True

@dataclass
class SpeckitConfig:
    project: Dict[str, str]
    directories: DirectoryConfig
    naming: NamingConfig
    validation: ValidationConfig
    
    @classmethod
    def load(cls, config_path: Path) -> SpeckitConfig:
        """Load configuration from speckit.yaml file"""
        if not config_path.exists():
            return cls._create_default(config_path)
            
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            
        return cls(
            project=data.get('project', {}),
            directories=DirectoryConfig(**data.get('directories', {})),
            naming=NamingConfig(**data.get('naming', {})),
            validation=ValidationConfig(**data.get('validation', {}))
        )
    
    @classmethod
    def _create_default(cls, config_path: Path) -> SpeckitConfig:
        """Create default configuration file"""
        default_config = {
            'project': {
                'name': 'my-project',
                'structure': 'standard'
            },
            'directories': {
                'features': 'docs/features',
                'specs': 'docs/specs',
                'tasks': 'docs/tasks',
                'dependencies': 'docs/dependencies'
            },
            'naming': {
                'features': 'feature-code.md',
                'specs': 'feature-code-spec.md',
                'tasks': 'tasks.json'
            },
            'validation': {
                'strict': True,
                'auto_fix': True,
                'require_frontmatter': True
            }
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
            
        return cls.load(config_path)
