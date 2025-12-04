"""
Bootstrap orchestration pipeline for US1.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.lib.config_loader import BootstrapConfig
from src.services.bootstrap_options import BootstrapOptions
from src.services.data_store_gateway import DataStoreGateway
from src.services.doc_discovery import DocumentationDiscoveryService
from src.services.parser.project_parser import ProjectParser
from src.services.parser.feature_parser import FeatureParser, SpecificationParser, TaskParser
from src.services.parser.dependency_parser import DependencyParser
from src.services.task_run_service import TaskRunService
from src.services.ai_job_service import AIJobService
from src.services.upsert_service import UpsertService
from src.services.validation.rules import (
    ValidationContext,
    DuplicateTaskCodeRule,
    CircularDependencyRule,
    TaskMetadataRule,
)
from src.services.validation_pipeline import ValidationPipeline, ValidationException


@dataclass(slots=True, frozen=True)
class BootstrapSummary:
    project_count: int = 0
    feature_count: int = 0
    spec_count: int = 0
    task_count: int = 0
    dependency_count: int = 0
    task_run_count: int = 0
    ai_job_count: int = 0

    @classmethod
    def empty(cls) -> "BootstrapSummary":
        return cls()


class BootstrapOrchestrator:
    """Coordinates discovery, parsing, and persistence for bootstrap runs."""

    def __init__(
        self,
        discovery_service: DocumentationDiscoveryService,
        upsert_service: UpsertService,
        task_run_service: TaskRunService,
        ai_job_service: AIJobService,
        gateway: DataStoreGateway,
    ) -> None:
        self._discovery_service = discovery_service
        self._upsert_service = upsert_service
        self._task_run_service = task_run_service
        self._ai_job_service = ai_job_service
        self._gateway = gateway

    def run(self, config: BootstrapConfig, options: BootstrapOptions) -> BootstrapSummary:
        docs = self._discovery_service.verify_structure()

        project = ProjectParser(docs.project_file).parse()
        if options.project and project.code != options.project:
            return BootstrapSummary.empty()

        features = FeatureParser(docs.features_dir).parse()
        specs = SpecificationParser(docs.specs_dir).parse()
        tasks = TaskParser(docs.tasks_dir).parse()
        dependencies = DependencyParser(docs.dependencies_dir).parse()

        self._run_validation(tasks, dependencies)

        self._upsert_service.persist_project(project)
        self._upsert_service.persist_features(features)
        self._upsert_service.persist_specs(specs)
        self._upsert_service.persist_tasks(tasks)

        if dependencies:
            self._gateway.create_task_dependencies(dependencies)

        task_runs = self._task_run_service.create_task_runs(tasks, options)
        if task_runs:
            self._gateway.create_task_runs(task_runs)

        ai_jobs = self._ai_job_service.create_ai_jobs(tasks, options)
        if ai_jobs:
            self._gateway.create_ai_jobs(ai_jobs)

        return BootstrapSummary(
            project_count=1,
            feature_count=len(features),
            spec_count=len(specs),
            task_count=len(tasks),
            dependency_count=len(dependencies),
            task_run_count=len(task_runs),
            ai_job_count=len(ai_jobs),
        )

    def _run_validation(
        self,
        tasks: Sequence[TaskDTO],
        dependencies: Sequence[TaskDependencyDTO],
    ) -> None:
        context = ValidationContext(tasks=tasks, dependencies=dependencies)
        pipeline = ValidationPipeline(
            rules=[
                DuplicateTaskCodeRule(context),
                CircularDependencyRule(context),
                TaskMetadataRule(context),
            ]
        )
        result = pipeline.execute()
        if result.has_blocking_errors:
            raise ValidationException(result)
