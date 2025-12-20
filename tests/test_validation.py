import pytest
from pathlib import Path
import tempfile
import shutil

from src.core.config import SpeckitConfig
from src.validation.validator import ProjectValidator

class TestProjectValidator:
    """Comprehensive validation tests"""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project for testing"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_missing_directories_detected(self, temp_project):
        """Test that missing directories are detected"""
        config = SpeckitConfig._create_default(temp_project / 'speckit.yaml')
        validator = ProjectValidator(config, temp_project)
        
        result = validator.validate()
        
        assert not result.is_valid
        assert any("ERR_MISSING_DIR" in error.code for error in result.errors)
    
    def test_auto_fix_creates_directories(self, temp_project):
        """Test that auto-fix creates missing directories"""
        config = SpeckitConfig._create_default(temp_project / 'speckit.yaml')
        validator = ProjectValidator(config, temp_project)
        
        # Auto-fix should create directories
        validator.auto_fix()
        
        # Verify directories exist
        for dir_path in config.directories.__dict__.values():
            full_path = temp_project / dir_path
            assert full_path.exists()
            assert full_path.is_dir()
    
    def test_duplicate_codes_detected(self, temp_project):
        """Test that duplicate codes are detected"""
        # Setup project with duplicate spec codes
        config = SpeckitConfig._create_default(temp_project / 'speckit.yaml')
        
        # Create directories
        for dir_path in config.directories.__dict__.values():
            (temp_project / dir_path).mkdir(parents=True, exist_ok=True)
            
        specs_dir = temp_project / config.directories.specs
        
        # Create two specs with same code
        spec_content = "---\ncode: duplicate-spec\nfeature_code: test\n---\n# Test"
        (specs_dir / "file1.md").write_text(spec_content)
        (specs_dir / "file2.md").write_text(spec_content)
        
        validator = ProjectValidator(config, temp_project)
        result = validator.validate()
        
        assert not result.is_valid
        assert any("duplicate" in error.message.lower() for error in result.errors)

# Integration tests
class TestEndToEnd:
    """End-to-end workflow tests"""
    
    @pytest.fixture
    def complete_project(self):
        """Create a complete, valid project"""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize project
        config = SpeckitConfig._create_default(temp_dir / 'speckit.yaml')
        
        # Create directories
        for dir_path in config.directories.__dict__.values():
            (temp_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create valid files
        from src.templates.template_manager import TemplateManager
        template_manager = TemplateManager(config, temp_dir)
        
        # Create feature first so spec ref is valid
        template_manager.create_feature_file("test-feature", "Test Feature")
        template_manager.create_spec_file("test-feature", "Test Feature")
        template_manager.create_tasks_file()
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_complete_workflow(self, complete_project):
        """Test complete validation and parsing workflow"""
        from src.parsing.unified_parser import UnifiedParser
        
        config = SpeckitConfig.load(complete_project / 'speckit.yaml')
        
        # Fix task feature_code for valid parse
        tasks_path = complete_project / config.directories.tasks / config.naming.tasks
        import json
        with open(tasks_path, 'r') as f:
            data = json.load(f)
        data[0]['feature_code'] = "test-feature"
        with open(tasks_path, 'w') as f:
            json.dump(data, f)
            
        parser = UnifiedParser(config, complete_project)
        result = parser.parse()
        
        assert len(result.features) == 1
        assert len(result.specs) == 1
        assert len(result.tasks) > 0
        assert result.validation_result.is_valid
