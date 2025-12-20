import pytest
from pathlib import Path
import tempfile
import shutil

from src.core.config import SpeckitConfig
from src.parsing.unified_parser import UnifiedParser
from src.templates.template_manager import TemplateManager

class TestUnifiedParser:
    
    @pytest.fixture
    def temp_project(self):
        temp_dir = Path(tempfile.mkdtemp())
        config = SpeckitConfig._create_default(temp_dir / 'speckit.yaml')
        
        # Create structure
        for dir_path in config.directories.__dict__.values():
            (temp_dir / dir_path).mkdir(parents=True, exist_ok=True)
            
        # Create project.md
        docs_dir = temp_dir / config.directories.features
        if docs_dir.name == 'features': docs_dir = docs_dir.parent
        (docs_dir / "project.md").write_text("---\ncode: parser-project\n---")
            
        yield temp_dir
        shutil.rmtree(temp_dir)
        
    def test_parse_valid_project(self, temp_project):
        config = SpeckitConfig.load(temp_project / 'speckit.yaml')
        tm = TemplateManager(config, temp_project)
        
        tm.create_feature_file("f1", "Feature 1")
        tm.create_spec_file("f1", "Feature 1")
        tm.create_tasks_file()
        
        # Note: default tasks.json has "feature_code": "feature-code"
        # We need to fix it to "f1" or it will fail cross-validation
        tasks_path = temp_project / config.directories.tasks / config.naming.tasks
        import json
        with open(tasks_path, 'r') as f:
            data = json.load(f)
        data[0]['feature_code'] = "f1"
        with open(tasks_path, 'w') as f:
            json.dump(data, f)
            
        parser = UnifiedParser(config, temp_project)
        result = parser.parse()
        
        assert len(result.features) == 1
        assert len(result.specs) == 1
        assert len(result.tasks) > 0
        assert result.validation_result.is_valid

    def test_parse_missing_feature_ref(self, temp_project):
        config = SpeckitConfig.load(temp_project / 'speckit.yaml')
        tm = TemplateManager(config, temp_project)
        
        # Spec refers to f1, but f1 doesn't exist
        tm.create_spec_file("f1", "Feature 1")
        
        parser = UnifiedParser(config, temp_project)
        # Validator catches broken references now as blocking errors
        with pytest.raises(ValueError, match="Project structure validation failed"):
            parser.parse()
