"""
Data store assertion helpers for testing.

Provides utilities for validating the state of the data storage after bootstrap operations.
"""

from __future__ import annotations

from typing import List, Optional
from pathlib import Path
import json

from src.models.entities import (
    ProjectDTO,
    FeatureDTO,
    SpecificationDTO,
    TaskDTO,
    TaskDependencyDTO,
    TaskRunDTO,
    AIJobDTO,
)


class DataStoreAssertions:
    """Helper methods for asserting data store state."""

    @staticmethod
    def assert_project_exists(
        projects: List[ProjectDTO], 
        name: str,
        description: Optional[str] = None
    ) -> ProjectDTO:
        """Assert a project exists and return it."""
        for project in projects:
            if project.name == name:
                if description is None or project.description == description:
                    return project
        
        assert False, f"Project '{name}' not found"

    @staticmethod
    def assert_feature_exists(
        features: List[FeatureDTO],
        name: str,
        project_code: Optional[str] = None
    ) -> FeatureDTO:
        """Assert a feature exists and return it."""
        for feature in features:
            if feature.name == name:
                if project_code is None or feature.project_code == project_code:
                    return feature
        
        assert False, f"Feature '{name}' not found"

    @staticmethod
    def assert_spec_exists(
        specs: List[SpecificationDTO],
        title: str,
        feature_code: Optional[str] = None
    ) -> SpecificationDTO:
        """Assert a specification exists and return it."""
        for spec in specs:
            if spec.title == title:
                if feature_code is None or spec.feature_code == feature_code:
                    return spec
        
        assert False, f"Specification '{title}' not found"

    @staticmethod
    def assert_task_exists(
        tasks: List[TaskDTO],
        title: str,
        feature_code: Optional[str] = None
    ) -> TaskDTO:
        """Assert a task exists and return it."""
        for task in tasks:
            if task.title == title:
                if feature_code is None or task.feature_code == feature_code:
                    return task
        
        assert False, f"Task '{title}' not found"

    @staticmethod
    def assert_dependency_exists(
        dependencies: List[TaskDependencyDTO],
        task_code: str,
        depends_on: str
    ) -> TaskDependencyDTO:
        """Assert a dependency exists and return it."""
        for dep in dependencies:
            if dep.task_code == task_code and dep.depends_on == depends_on:
                return dep
        
        assert False, f"Dependency {task_code} -> {depends_on} not found"

    @staticmethod
    def assert_task_run_exists(
        task_runs: List[TaskRunDTO],
        task_code: str,
        status: Optional[str] = None
    ) -> TaskRunDTO:
        """Assert a task run exists and return it."""
        for task_run in task_runs:
            if task_run.task_code == task_code:
                if status is None or task_run.status == status:
                    return task_run
        
        assert False, f"Task run for task '{task_code}' not found"

    @staticmethod
    def assert_ai_job_exists(
        ai_jobs: List[AIJobDTO],
        task_code: str,
        job_type: Optional[str] = None
    ) -> AIJobDTO:
        """Assert an AI job exists and return it."""
        for ai_job in ai_jobs:
            if ai_job.task_code == task_code:
                if job_type is None or ai_job.job_type == job_type:
                    return ai_job
        
        assert False, f"AI job for task '{task_code}' not found"

    @staticmethod
    def assert_entity_relationships(
        project: ProjectDTO,
        feature: FeatureDTO,
        spec: SpecificationDTO,
        task: TaskDTO,
        task_run: TaskRunDTO,
        ai_job: AIJobDTO
    ) -> None:
        """Assert all entity relationships are consistent."""
        assert feature.project_code == project.code
        assert spec.feature_code == feature.code
        assert task.feature_code == feature.code
        assert task_run.task_code == task.code
        assert ai_job.task_code == task.code

    @staticmethod
    def load_snapshot(path: Path) -> dict:
        """Load a golden snapshot from file."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def assert_matches_snapshot(
        entities: List[object], 
        snapshot: dict,
        entity_type: str
    ) -> None:
        """Assert entities match a golden snapshot."""
        snapshot_entities = snapshot.get(entity_type, [])
        assert len(entities) == len(snapshot_entities), \
            f"Expected {len(snapshot_entities)} {entity_type}, got {len(entities)}"
        
        for entity, snapshot_entity in zip(entities, snapshot_entities):
            for key, expected_value in snapshot_entity.items():
                actual_value = getattr(entity, key, None)
                assert actual_value == expected_value, \
                    f"{entity_type} {key} mismatch: expected {expected_value}, got {actual_value}"