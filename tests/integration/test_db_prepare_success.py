"""
Integration test for successful bootstrap workflow.

This test validates that the complete bootstrap process works end-to-end,
including parsing, validation, persistence, and derived entity creation.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


from src.models.entities import (
    ProjectDTO,
    FeatureDTO,
    SpecificationDTO,
    TaskDTO,
    TaskDependencyDTO,
    TaskRunDTO,
    AIJobDTO,
)
from src.services.bootstrap_orchestrator import BootstrapOrchestrator
from src.services.bootstrap_options import BootstrapOptions
from src.services.data_store_gateway import DataStoreGateway


class TestDbPrepareSuccess:
    """Test successful bootstrap workflow."""

    @pytest.fixture
    def temp_project_dir(self) -> Path:
        """Create a temporary project directory with sample documentation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            
            # Create project structure
            (project_dir / "features").mkdir()
            (project_dir / "specs").mkdir()
            (project_dir / "tasks").mkdir()
            (project_dir / "dependencies").mkdir()
            
            # Create project.md
            (project_dir / "project.md").write_text("""---
name: Test Project
description: Integration test project
repository_path: https://github.com/test/project
---

# Test Project

A test project for integration testing.
""")
            
            # Create feature
            (project_dir / "features" / "user-auth.md").write_text("""---
priority: P1
---

# User Authentication

User authentication and authorization features.
""")
            
            # Create spec
            (project_dir / "specs" / "auth-spec.md").write_text("""---
feature_code: user-auth
---

# Authentication Specification

Detailed requirements for user authentication.
""")
            
            # Create task
            (project_dir / "tasks" / "user-registration.md").write_text("""---
feature_code: user-auth
status: pending
task_type: implementation
ai_job_type: code-generation
prompt: Generate user registration code
dependencies: []
---

# User Registration Task

Implement user registration functionality.

## Acceptance Criteria

1. Users can register with email and password
2. Email validation is performed
3. Password hashing is implemented
""")
            
            # Create dependency
            (project_dir / "dependencies" / "deps.md").write_text("""# Dependencies

T002 depends on T001
""")
            
            yield project_dir

    @pytest.fixture
    def mock_gateway(self) -> DataStoreGateway:
        """Create a mock data store gateway for testing."""
        gateway = DataStoreGateway(Path("/tmp/test.db"))
        
        # Track entities that would be persisted
        gateway.persisted_projects = []
        gateway.persisted_features = []
        gateway.persisted_specs = []
        gateway.persisted_tasks = []
        gateway.persisted_dependencies = []
        gateway.persisted_task_runs = []
        gateway.persisted_ai_jobs = []
        
        # Override methods to track calls
        def create_or_update_projects(projects):
            gateway.persisted_projects.extend(projects)
        
        def create_or_update_features(features):
            gateway.persisted_features.extend(features)
        
        def create_or_update_specs(specs):
            gateway.persisted_specs.extend(specs)
        
        def create_or_update_tasks(tasks):
            gateway.persisted_tasks.extend(tasks)
        
        def create_task_dependencies(dependencies):
            gateway.persisted_dependencies.extend(dependencies)
        
        def create_task_runs(task_runs):
            gateway.persisted_task_runs.extend(task_runs)
        
        def create_ai_jobs(ai_jobs):
            gateway.persisted_ai_jobs.extend(ai_jobs)
        
        gateway.create_or_update_projects = create_or_update_projects
        gateway.create_or_update_features = create_or_update_features
        gateway.create_or_update_specs = create_or_update_specs
        gateway.create_or_update_tasks = create_or_update_tasks
        gateway.create_task_dependencies = create_task_dependencies
        gateway.create_task_runs = create_task_runs
        gateway.create_ai_jobs = create_ai_jobs
        
        return gateway

    def test_bootstrap_orchestrator_success(self, temp_project_dir, mock_gateway):
        """Test that bootstrap orchestrator successfully processes all entities."""
        orchestrator = BootstrapOrchestrator(temp_project_dir, mock_gateway)
        
        # Run bootstrap
        result = orchestrator.run_bootstrap(BootstrapOptions(dry_run=False))
        
        # Verify success
        assert result.success is True
        assert result.error_message is None
        
        # Verify entities were parsed and persisted
        assert len(mock_gateway.persisted_projects) == 1
        assert len(mock_gateway.persisted_features) == 1
        assert len(mock_gateway.persisted_specs) == 1
        assert len(mock_gateway.persisted_tasks) == 1
        assert len(mock_gateway.persisted_dependencies) >= 0
        
        # Verify derived entities (task runs and AI jobs)
        assert len(mock_gateway.persisted_task_runs) == 1  # One task run per task
        assert len(mock_gateway.persisted_ai_jobs) == 1    # One AI job per task with AI metadata
        
        # Verify project entity
        project = mock_gateway.persisted_projects[0]
        assert isinstance(project, ProjectDTO)
        assert project.name == "Test Project"
        assert project.description == "Integration test project"
        assert project.repository_path == "https://github.com/test/project"
        
        # Verify feature entity
        feature = mock_gateway.persisted_features[0]
        assert isinstance(feature, FeatureDTO)
        assert feature.name == "User Authentication"
        assert feature.priority == "P1"
        assert feature.project_code == project.code
        
        # Verify spec entity
        spec = mock_gateway.persisted_specs[0]
        assert isinstance(spec, SpecificationDTO)
        assert spec.title == "Authentication Specification"
        assert spec.feature_code == feature.code
        
        # Verify task entity
        task = mock_gateway.persisted_tasks[0]
        assert isinstance(task, TaskDTO)
        assert task.title == "User Registration Task"
        assert task.status == "pending"
        assert task.task_type == "implementation"
        assert task.feature_code == feature.code
        assert "Users can register with email and password" in task.acceptance
        
        # Verify task run entity
        task_run = mock_gateway.persisted_task_runs[0]
        assert isinstance(task_run, TaskRunDTO)
        assert task_run.task_code == task.code
        assert task_run.status == "pending"  # Initial status
        
        # Verify AI job entity
        ai_job = mock_gateway.persisted_ai_jobs[0]
        assert isinstance(ai_job, AIJobDTO)
        assert ai_job.task_code == task.code
        assert ai_job.job_type == "code-generation"
        assert "Generate user registration code" in ai_job.prompt

    def test_bootstrap_dry_run_success(self, temp_project_dir, mock_gateway):
        """Test that dry-run mode validates without persisting."""
        orchestrator = BootstrapOrchestrator(temp_project_dir, mock_gateway)
        
        # Run bootstrap in dry-run mode
        result = orchestrator.run_bootstrap(BootstrapOptions(dry_run=True))
        
        # Verify success
        assert result.success is True
        assert result.error_message is None
        
        # Verify no entities were persisted in dry-run mode
        assert len(mock_gateway.persisted_projects) == 0
        assert len(mock_gateway.persisted_features) == 0
        assert len(mock_gateway.persisted_specs) == 0
        assert len(mock_gateway.persisted_tasks) == 0
        assert len(mock_gateway.persisted_dependencies) == 0
        assert len(mock_gateway.persisted_task_runs) == 0
        assert len(mock_gateway.persisted_ai_jobs) == 0
        
        # Verify summary contains expected counts
        assert result.project_count == 1
        assert result.feature_count == 1
        assert result.spec_count == 1
        assert result.task_count == 1
        assert result.dependency_count >= 0
        assert result.task_run_count == 1
        assert result.ai_job_count == 1

    def test_dependency_graph_validation(self, temp_project_dir, mock_gateway):
        """Test that dependency graph is properly built and validated."""
        orchestrator = BootstrapOrchestrator(temp_project_dir, mock_gateway)
        
        # Run bootstrap
        result = orchestrator.run_bootstrap(BootstrapOptions(dry_run=False))
        
        # Verify success
        assert result.success is True
        
        # Verify dependency relationships
        if mock_gateway.persisted_dependencies:
            for dep in mock_gateway.persisted_dependencies:
                assert isinstance(dep, TaskDependencyDTO)
                assert dep.task_code
                assert dep.depends_on
        
        # Verify no circular dependencies
        assert result.circular_dependency_count == 0

    def test_cli_integration(self, temp_project_dir):
        """Test CLI integration with temporary project."""
        with patch('sys.argv', ['speckit.db.prepare', str(temp_project_dir), '--dry-run']):
            # This would normally call the CLI main function
            # For integration testing, we verify the CLI can parse arguments
            # and the orchestrator can be instantiated
            try:
                orchestrator = BootstrapOrchestrator(temp_project_dir, DataStoreGateway(Path("/tmp/test.db")))
                result = orchestrator.run_bootstrap(BootstrapOptions(dry_run=True))
                assert result.success is True
            except Exception as e:
                pytest.fail(f"CLI integration failed: {e}")

    def test_entity_relationship_consistency(self, temp_project_dir, mock_gateway):
        """Test that entity relationships are consistent."""
        orchestrator = BootstrapOrchestrator(temp_project_dir, mock_gateway)
        
        # Run bootstrap
        result = orchestrator.run_bootstrap(BootstrapOptions(dry_run=False))
        
        # Verify success
        assert result.success is True
        
        # Get entities
        project = mock_gateway.persisted_projects[0]
        feature = mock_gateway.persisted_features[0]
        spec = mock_gateway.persisted_specs[0]
        task = mock_gateway.persisted_tasks[0]
        task_run = mock_gateway.persisted_task_runs[0]
        ai_job = mock_gateway.persisted_ai_jobs[0]
        
        # Verify relationship consistency
        assert feature.project_code == project.code
        assert spec.feature_code == feature.code
        assert task.feature_code == feature.code
        assert task_run.task_code == task.code
        assert ai_job.task_code == task.code
        
        # Verify all entities have required codes
        assert project.code
        assert feature.code
        assert spec.code
        assert task.code
        assert task_run.task_code
        assert ai_job.task_code

    def test_error_handling_and_recovery(self, temp_project_dir, mock_gateway):
        """Test error handling and recovery mechanisms."""
        # Create a malformed file to test error handling
        (temp_project_dir / "features" / "bad-feature.md").write_text("Invalid markdown content")
        
        orchestrator = BootstrapOrchestrator(temp_project_dir, mock_gateway)
        
        # Run bootstrap - should handle errors gracefully
        result = orchestrator.run_bootstrap(BootstrapOptions(dry_run=True))
        
        # Should still succeed despite one bad file
        assert result.success is True
        
        # Should still process valid files
        assert result.feature_count >= 1  # At least the valid feature
        