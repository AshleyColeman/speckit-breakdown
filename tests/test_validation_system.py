import pytest
from pathlib import Path
import tempfile
import shutil
import yaml
import json

from src.core.config import SpeckitConfig
from src.validation.validator import ProjectValidator

class TestValidationSystem:
    
    @pytest.fixture
    def temp_project(self):
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create config
        config = SpeckitConfig._create_default(temp_dir / 'speckit.yaml')
        
        yield temp_dir
        shutil.rmtree(temp_dir)
        
    def test_missing_directories(self, temp_project):
        config = SpeckitConfig.load(temp_project / 'speckit.yaml')
        # Ensure it doesn't exist (it shouldn't by default from _create_default, but let's be sure)
        features_dir = temp_project / config.directories.features
        if features_dir.exists():
            shutil.rmtree(features_dir)
        
        validator = ProjectValidator(config, temp_project)
        result = validator.validate()
        
        assert not result.is_valid
        assert any("ERR_MISSING_DIR" in e.code for e in result.errors)
        
    def test_valid_project(self, temp_project):
        config = SpeckitConfig.load(temp_project / 'speckit.yaml')
        validator = ProjectValidator(config, temp_project)
        # Even without files, structure should be valid (if empty dirs allowed)
        # But wait, empty dirs are created by default config creation?
        # SpeckitConfig._create_default does NOT create the directories, it just creates config file?
        # Let's check src/core/config.py: _create_default writes config file.
        # But my init command creates dirs.
        # So I need to create dirs here.
        
        for dir_path in config.directories.__dict__.values():
            (temp_project / dir_path).mkdir(parents=True, exist_ok=True)
            
        result = validator.validate()
        assert result.is_valid

    def test_file_naming(self, temp_project):
        config = SpeckitConfig.load(temp_project / 'speckit.yaml')
        for dir_path in config.directories.__dict__.values():
            (temp_project / dir_path).mkdir(parents=True, exist_ok=True)

        features_dir = temp_project / config.directories.features
        (features_dir / "BadName.txt").write_text("content")
        
        validator = ProjectValidator(config, temp_project)
        result = validator.validate()
        
        assert not result.is_valid
        assert any("ERR_INVALID_EXT" in e.code for e in result.errors)

    def test_duplicate_code(self, temp_project):
        config = SpeckitConfig.load(temp_project / 'speckit.yaml')
        for dir_path in config.directories.__dict__.values():
            (temp_project / dir_path).mkdir(parents=True, exist_ok=True)
            
        features_dir = temp_project / config.directories.features
        
        content = "---\ncode: my-feature\n---\n# Feature"
        (features_dir / "f1.md").write_text(content)
        (features_dir / "f2.md").write_text(content)
        
        validator = ProjectValidator(config, temp_project)
        result = validator.validate()
        
        assert not result.is_valid
        assert any("ERR_DUPLICATE_CODE" in e.code for e in result.errors)

if __name__ == "__main__":
    # Manually run if pytest not available
    pass
