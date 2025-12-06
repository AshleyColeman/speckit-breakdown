"""
Bootstrap orchestration pipeline for US1.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from src.models.entities import TaskDTO, TaskDependencyDTO
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
    DuplicateEntityRule,
    CircularDependencyRule,
    MalformedDocRule,
    DependencyStatusRule,
)
from src.services.matchers.entity_matcher import EntityMatcher
from src.services.validation_pipeline import ValidationPipeline, ValidationException

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class BootstrapSummary:
    project_count: int = 0
    feature_count: int = 0
    spec_count: int = 0
    task_count: int = 0
    dependency_count: int = 0
    task_run_count: int = 0
    ai_job_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    circular_dependency_count: int = 0
    skipped_count: int = 0
    overwritten_count: int = 0
    success: bool = True
    error_message: Optional[str] = None
    validation_result: Optional[object] = None

    @classmethod
    def empty(cls) -> "BootstrapSummary":
        return cls()


class BootstrapOrchestrator:
    """Coordinates discovery, parsing, validation, and persistence for bootstrap runs."""

    def __init__(self, project_path: Path, gateway: DataStoreGateway) -> None:
        self._project_path = project_path
        self._gateway = gateway
        self._discovery_service = DocumentationDiscoveryService(project_path)
        self._matcher = EntityMatcher(gateway)
        self._upsert_service = UpsertService(self._matcher, gateway)
        self._task_run_service = TaskRunService()
        self._ai_job_service = AIJobService()

    def run_bootstrap(self, options: BootstrapOptions) -> BootstrapSummary:
        """
        Execute the complete bootstrap workflow.
        """
        try:
            docs = self._discovery_service.verify_structure()

            project = ProjectParser(docs.project_file).parse()
            if options.project and project.code != options.project:
                return BootstrapSummary.empty()

            features = FeatureParser(docs.features_dir, project.code).parse()
            specs = SpecificationParser(docs.specs_dir).parse()
            tasks = TaskParser(docs.tasks_dir).parse()

            # Apply scoping filters if project is specified
            if options.project:
                features = [f for f in features if f.project_code == options.project]
                valid_feature_codes = {f.code for f in features}
                
                specs = [s for s in specs if s.feature_code in valid_feature_codes]
                tasks = [t for t in tasks if t.feature_code in valid_feature_codes]

            dep_parser = DependencyParser(docs.dependencies_dir)
            dependencies = dep_parser.parse()
            task_dependencies = dep_parser.parse_from_tasks(tasks)
            all_dependencies = list(dependencies) + list(task_dependencies)
            
            # Filter dependencies to only include those relevant to filtered tasks
            if options.project:
                valid_task_codes = {t.code for t in tasks}
                all_dependencies = [
                    d for d in all_dependencies 
                    if d.task_code in valid_task_codes
                ]

            validation_result = self._run_validation(
                project=project,
                features=features,
                specs=specs,
                tasks=tasks,
                dependencies=all_dependencies
            )

            # Calculate step orders based on dependencies
            tasks = self._calculate_step_orders(tasks, all_dependencies)

            if options.dry_run:
                return BootstrapSummary(
                    project_count=1,
                    feature_count=len(features),
                    spec_count=len(specs),
                    task_count=len(tasks),
                    dependency_count=len(all_dependencies),
                    task_run_count=len(tasks) if not options.skip_task_runs else 0,
                    ai_job_count=0 if options.skip_ai_jobs else self._ai_job_service.estimate_ai_job_count(tasks, options),
                    warning_count=validation_result.warning_count,
                    error_count=validation_result.error_count,
                    circular_dependency_count=validation_result.circular_dependency_count,
                    validation_result=validation_result,
                )

            self._persist_entities(project, features, specs, tasks, all_dependencies, options)
            
            task_runs = []
            if not options.skip_task_runs:
                task_runs = self._task_run_service.create_task_runs(tasks, options)
                if task_runs:
                    self._gateway.create_task_runs(task_runs)

            ai_jobs = []
            if not options.skip_ai_jobs:
                ai_jobs = self._ai_job_service.create_ai_jobs(tasks, options)
                if ai_jobs:
                    self._gateway.create_ai_jobs(ai_jobs)

            return BootstrapSummary(
                project_count=1,
                feature_count=len(features),
                spec_count=len(specs),
                task_count=len(tasks),
                dependency_count=len(all_dependencies),
                task_run_count=len(task_runs),
                ai_job_count=len(ai_jobs),
                warning_count=validation_result.warning_count,
                error_count=validation_result.error_count,
                circular_dependency_count=validation_result.circular_dependency_count,
                validation_result=validation_result,
            )

        except ValidationException as exc:
            logger.error("Validation failed", exc_info=True)
            return BootstrapSummary(
                success=False,
                error_message="Validation passed with errors.",
                warning_count=exc.result.warning_count,
                error_count=exc.result.error_count,
                circular_dependency_count=exc.result.circular_dependency_count,
                validation_result=exc.result
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Bootstrap failed", exc_info=True)
            return BootstrapSummary(success=False, error_message=str(exc))

    def _persist_entities(
        self,
        project,
        features,
        specs,
        tasks,
        dependencies,
        options: BootstrapOptions,
    ) -> None:
        self._upsert_service.upsert_projects([project], force=options.force)
        self._upsert_service.upsert_features(features, force=options.force)
        self._upsert_service.upsert_specs(specs, force=options.force)
        self._upsert_service.upsert_tasks(tasks, force=options.force)

        if dependencies:
            self._gateway.create_task_dependencies(dependencies)

    def _run_validation(
        self,
        project,
        features,
        specs,
        tasks,
        dependencies,
    ):
        pipeline = ValidationPipeline(
            rules=[
                DuplicateEntityRule([project], features, specs, tasks),
                CircularDependencyRule(tasks, dependencies),
                MalformedDocRule(tasks),
                DependencyStatusRule(tasks, dependencies),
            ]
        )
        result = pipeline.execute()
        if result.has_blocking_errors:
            raise ValidationException(result)
        return result

    def _calculate_step_orders(self, tasks: Sequence[TaskDTO], dependencies: Sequence[TaskDependencyDTO]) -> Sequence[TaskDTO]:
        """
        Calculate step order for each task based on topological dependency depth.
        Task with no dependencies = 1.
        Task with dependencies = max(dependency.step_order) + 1.
        """
        # Map task codes to objects (lowercase keys)
        task_map = {t.code.lower(): t for t in tasks}
        
        # Build adjacency list (pred -> succ) and in-degree count
        adj = {code: [] for code in task_map}
        in_degree = {code: 0 for code in task_map}
        
        for dep in dependencies:
            pred = dep.depends_on.lower()
            succ = dep.task_code.lower()
            
            if pred in task_map and succ in task_map:
                adj[pred].append(succ)
                in_degree[succ] += 1
                
        # Zero in-degree nodes vary start at step 1
        step_orders = {code: 1 for code in task_map}

        # Topological Sort (Kahn's algorithmish)
        # We process nodes with in-degree 0, then their neighbors.
        # But for 'longest path' (critical path), we can just relax edges.
        # Since it's a DAG (validated by CircularDependencyRule), we can iterate.
        
        # Initialize queue with all source nodes
        queue = [code for code in task_map if in_degree[code] == 0]
        
        processed_count = 0
        total_tasks = len(task_map)
        
        while queue:
            u = queue.pop(0)
            processed_count += 1
            
            current_step = step_orders[u]
            
            for v in adj[u]:
                # Relax edge: Successor step is at least current step + 1
                if step_orders[v] < current_step + 1:
                    step_orders[v] = current_step + 1
                
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        # Reconstruct TaskDTOs with step_order
        updated_tasks = []
        for t in tasks:
            code = t.code.lower()
            order = step_orders.get(code, 1)
            
            new_t = TaskDTO(
                code=t.code,
                feature_code=t.feature_code,
                title=t.title,
                status=t.status,
                task_type=t.task_type,
                acceptance=t.acceptance,
                step_order=order,
                metadata=t.metadata
            )
            updated_tasks.append(new_t)
            
        return updated_tasks
