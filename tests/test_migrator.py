import pytest
from pathlib import Path
import tempfile
import shutil

from src.migration.migrator import ProjectMigrator

class TestProjectMigrator:
    
    @pytest.fixture
    def temp_project(self):
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create a non-standard structure
        (temp_dir / "old_features").mkdir()
        (temp_dir / "old_specs").mkdir()
        
        feature_content = "---\ncode: f1\n---\n# Feature 1"
        (temp_dir / "old_features" / "f1.md").write_text(feature_content)
        
        spec_content = "---\nfeature_code: f1\n---\n# Spec 1"
        (temp_dir / "old_specs" / "f1-spec.md").write_text(spec_content)
        
        (temp_dir / "tasks.json").write_text("[]")
        
        yield temp_dir
        shutil.rmtree(temp_dir)
        
    def test_plan_migration(self, temp_project):
        migrator = ProjectMigrator(temp_project)
        plan = migrator.plan_migration("old", "standard")
        
        assert any("f1.md -> docs/features/f1.md" in item for item in plan)
        assert any("f1-spec.md -> docs/specs/f1-spec.md" in item for item in plan)
        assert any("tasks.json -> docs/tasks/tasks.json" in item for item in plan)
        
    def test_execute_migration(self, temp_project):
        migrator = ProjectMigrator(temp_project)
        executed = migrator.execute_migration("old", "standard")
        
        assert len(executed) == 3
        assert (temp_project / "docs/features/f1.md").exists()
        assert (temp_project / "docs/specs/f1-spec.md").exists()
        assert (temp_project / "docs/tasks/tasks.json").exists()
        
        # Original files should be gone
        assert not (temp_project / "old_features/f1.md").exists()
        assert not (temp_project / "tasks.json").exists()
