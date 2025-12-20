import pytest
import time
from pathlib import Path
import tempfile
import shutil

from src.parsing.unified_parser import UnifiedParser
from src.core.config import SpeckitConfig

class TestPerformance:
    """Performance tests for large projects"""
    
    @pytest.fixture
    def large_project(self):
        """Create a large project with many files"""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Setup config
        config = SpeckitConfig._create_default(temp_dir / 'speckit.yaml')
        
        # Create directories
        for dir_path in config.directories.__dict__.values():
            (temp_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create many features (simulating large project)
        from src.templates.template_manager import TemplateManager
        template_manager = TemplateManager(config, temp_dir)
        
        for i in range(100):  # 100 features
            template_manager.create_feature_file(f"feature-{i:03d}", f"Feature {i}")
            template_manager.create_spec_file(f"feature-{i:03d}", f"Feature {i}")
        
        template_manager.create_tasks_file()
        
        # Fix task feature_code for valid parse
        tasks_path = temp_dir / config.directories.tasks / config.naming.tasks
        import json
        with open(tasks_path, 'r') as f:
            data = json.load(f)
        data[0]['feature_code'] = "feature-000"
        with open(tasks_path, 'w') as f:
            json.dump(data, f)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_parse_large_project_performance(self, large_project):
        """Test parsing performance with large project"""
        config = SpeckitConfig.load(large_project / 'speckit.yaml')
        parser = UnifiedParser(config, large_project)
        
        start_time = time.time()
        result = parser.parse()
        end_time = time.time()
        
        parse_time = end_time - start_time
        
        # Should parse 100 features in under 5 seconds
        assert parse_time < 5.0, f"Parsing took too long: {parse_time:.2f}s"
        assert len(result.features) == 100
        assert len(result.specs) == 100
