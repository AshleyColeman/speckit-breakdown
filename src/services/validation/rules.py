"""
Validation rules for the bootstrap process.
"""

from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Sequence, Set

from src.models.entities import FeatureDTO, ProjectDTO, SpecificationDTO, TaskDTO, TaskDependencyDTO
from src.services.validation_pipeline import ValidationIssue, Severity

logger = logging.getLogger(__name__)


class RequiredFieldsRule:
    """Validates that required entity fields exist and are non-empty."""

    name = "required_fields_rule"

    def __init__(
        self,
        project: ProjectDTO,
        features: Iterable[FeatureDTO],
        specs: Iterable[SpecificationDTO],
        tasks: Iterable[TaskDTO],
    ) -> None:
        self._project = project
        self._features = list(features)
        self._specs = list(specs)
        self._tasks = list(tasks)

    @staticmethod
    def _is_blank(value: object) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False

    def run(self) -> Iterable[ValidationIssue]:
        if self._is_blank(self._project.code):
            yield ValidationIssue(severity=Severity.CRITICAL, message="Project code is required", location="Project")
        if self._is_blank(self._project.name):
            yield ValidationIssue(severity=Severity.ERROR, message="Project name is required", location="Project")

        for feature in self._features:
            if self._is_blank(feature.code):
                yield ValidationIssue(
                    severity=Severity.CRITICAL,
                    message="Feature code is required",
                    location=f"Feature: {feature.name}",
                )
            if self._is_blank(feature.project_code):
                yield ValidationIssue(
                    severity=Severity.CRITICAL,
                    message=f"Feature '{feature.code}' is missing project_code",
                    location=f"Feature: {feature.code}",
                )
            if self._is_blank(feature.name):
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Feature '{feature.code}' is missing name",
                    location=f"Feature: {feature.code}",
                )

        for spec in self._specs:
            if self._is_blank(spec.code):
                yield ValidationIssue(
                    severity=Severity.CRITICAL,
                    message="Specification code is required",
                    location=f"Spec: {spec.title}",
                )
            if self._is_blank(spec.feature_code):
                yield ValidationIssue(
                    severity=Severity.CRITICAL,
                    message=f"Specification '{spec.code}' is missing feature_code",
                    location=f"Spec: {spec.code}",
                )
            if self._is_blank(spec.title):
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Specification '{spec.code}' is missing title",
                    location=f"Spec: {spec.code}",
                )
            if self._is_blank(spec.path):
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Specification '{spec.code}' is missing path",
                    location=f"Spec: {spec.code}",
                )

        for task in self._tasks:
            if self._is_blank(task.code):
                yield ValidationIssue(severity=Severity.CRITICAL, message="Task code is required", location="Task")
            if self._is_blank(task.feature_code):
                yield ValidationIssue(
                    severity=Severity.CRITICAL,
                    message=f"Task '{task.code}' is missing feature_code",
                    location=f"Task: {task.code}",
                )
            if self._is_blank(task.title):
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Task '{task.code}' is missing title",
                    location=f"Task: {task.code}",
                )
            if self._is_blank(task.status):
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Task '{task.code}' is missing status",
                    location=f"Task: {task.code}",
                )
            if self._is_blank(task.task_type):
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Task '{task.code}' is missing task_type",
                    location=f"Task: {task.code}",
                )


class ReferentialIntegrityRule:
    """Validates references between entities (feature->project, spec->feature, task->feature)."""

    name = "referential_integrity_rule"

    def __init__(
        self,
        project: ProjectDTO,
        features: Iterable[FeatureDTO],
        specs: Iterable[SpecificationDTO],
        tasks: Iterable[TaskDTO],
    ) -> None:
        self._project = project
        self._features = list(features)
        self._specs = list(specs)
        self._tasks = list(tasks)

    def run(self) -> Iterable[ValidationIssue]:
        project_code = (self._project.code or "").strip()
        project_name = (self._project.name or "").strip()

        def _normalize(value: str) -> str:
            return value.strip().lower()

        feature_identifiers = {
            _normalize(v)
            for f in self._features
            for v in (f.code, f.name)
            if isinstance(v, str) and v.strip()
        }

        for feature in self._features:
            feature_project = (feature.project_code or "").strip()
            if feature_project and _normalize(feature_project) not in {
                _normalize(project_code),
                _normalize(project_name),
            }:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=(
                        f"Feature '{feature.code}' references project '{feature.project_code}' "
                        f"but active project is '{project_code}'."
                    ),
                    location=f"Feature: {feature.code}",
                )

        for spec in self._specs:
            if _normalize(spec.feature_code or "") not in feature_identifiers:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Spec '{spec.code}' references missing feature '{spec.feature_code}'.",
                    location=f"Spec: {spec.code}",
                )

        for task in self._tasks:
            if _normalize(task.feature_code or "") not in feature_identifiers:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Task '{task.code}' references missing feature '{task.feature_code}'.",
                    location=f"Task: {task.code}",
                )


class InvalidDependencyReferenceRule:
    """Reports dependency edges referencing tasks that do not exist."""

    name = "invalid_dependency_reference_rule"

    def __init__(self, invalid_dependencies: Sequence[TaskDependencyDTO]) -> None:
        self._invalid_dependencies = list(invalid_dependencies)

    def run(self) -> Iterable[ValidationIssue]:
        for dep in self._invalid_dependencies:
            yield ValidationIssue(
                severity=Severity.ERROR,
                message=f"Dependency references unknown task(s): {dep.task_code} depends on {dep.depends_on}",
                location=f"Dependency: {dep.task_code} -> {dep.depends_on}",
            )


class DuplicateEntityRule:
    """Checks for duplicate entity IDs across the dataset."""

    name = "duplicate_entity_rule"

    def __init__(self, projects: Iterable[ProjectDTO], features: Iterable[FeatureDTO], specs: Iterable[SpecificationDTO], tasks: Iterable[TaskDTO]):
        self.projects = projects
        self.features = features
        self.specs = specs
        self.tasks = tasks

    def run(self) -> Iterable[ValidationIssue]:
        seen_codes: Set[str] = set()
        
        # Check projects
        for p in self.projects:
            code = (p.code or "").strip().upper()
            if code in seen_codes:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Duplicate Project Code found: {p.code}",
                    location=f"Project: {p.name}"
                )
            if code:
                seen_codes.add(code)

        # Check features
        for f in self.features:
            code = (f.code or "").strip().upper()
            if code in seen_codes:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Duplicate Feature Code found: {f.code}",
                    location=f"Feature: {f.name} (Project: {f.project_code})"
                )
            if code:
                seen_codes.add(code)
            
        # Check specs
        for s in self.specs:
            code = (s.code or "").strip().upper()
            if code in seen_codes:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Duplicate Spec Code found: {s.code}",
                    location=f"Spec: {s.title} (Feature: {s.feature_code})"
                )
            if code:
                seen_codes.add(code)

        # Check tasks
        for t in self.tasks:
            code = (t.code or "").strip().upper()
            if code in seen_codes:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Duplicate Task Code found: {t.code}",
                    location=f"Task: {t.title} (Feature: {t.feature_code})"
                )
            if code:
                seen_codes.add(code)


class CircularDependencyRule:
    """Checks for circular dependencies in tasks."""

    name = "circular_dependency_rule"

    def __init__(self, tasks: Iterable[TaskDTO], dependencies: Iterable[TaskDependencyDTO]):
        self.tasks = {t.code: t for t in tasks}
        self.dependencies = list(dependencies)

    def run(self) -> Iterable[ValidationIssue]:
        # Build adjacency list
        graph: Dict[str, List[str]] = {}
        for dep in self.dependencies:
            if dep.task_code not in graph:
                graph[dep.task_code] = []
            graph[dep.task_code].append(dep.depends_on)

        visited = set()
        path = set()
        
        def detect_cycle(current_node: str, current_path: List[str]) -> List[str] | None:
            visited.add(current_node)
            path.add(current_node)
            current_path.append(current_node)

            for neighbor in graph.get(current_node, []):
                if neighbor not in visited:
                    cycle = detect_cycle(neighbor, current_path)
                    if cycle:
                        return cycle
                elif neighbor in path:
                     # Cycle detected
                     return current_path[current_path.index(neighbor):] + [neighbor]
            
            path.remove(current_node)
            current_path.pop()
            return None

        # Check for cycles
        for task_code in list(graph.keys()):
             if task_code not in visited:
                cycle_nodes = detect_cycle(task_code, [])
                if cycle_nodes:
                     cycle_str = " -> ".join(cycle_nodes)
                     yield ValidationIssue(
                        severity=Severity.ERROR,
                        message=f"Circular dependency detected: {cycle_str}",
                        location=f"Task Cycle starting at {cycle_nodes[0]}"
                    )

class MalformedDocRule:
    """Checks for general malformation issues (placeholders, missing required fields not caught by parser)."""
    
    name = "malformed_doc_rule"
    
    def __init__(self, tasks: Iterable[TaskDTO]):
        self.tasks = tasks
        
    def run(self) -> Iterable[ValidationIssue]:
        for task in self.tasks:
            if "TODO" in task.title or "TBD" in task.title:
                yield ValidationIssue(
                    severity=Severity.WARNING,
                    message=f"Task title contains placeholder (TODO/TBD): {task.title}",
                    location=f"Task: {task.code}"
                )
            
            if not task.acceptance or len(task.acceptance.strip()) < 5:
                yield ValidationIssue(
                    severity=Severity.WARNING,
                    message=f"Task acceptance criteria is missing or too short: {task.code}",
                    location=f"Task: {task.code}"
                )

class DependencyStatusRule:
    """
    Validates that tasks obey dependency status logic.
    A task cannot be 'ready' or 'completed' unless all its dependencies are 'completed'.
    """
    
    name = "dependency_status_rule"
    
    def __init__(self, tasks: Iterable[TaskDTO], dependencies: Iterable[TaskDependencyDTO]):
        # Normalize task map keys to lowercase
        self.tasks = {t.code.lower(): t for t in tasks}
        self.dependencies = list(dependencies)
        
    def run(self) -> Iterable[ValidationIssue]:
        # Map task_code -> list of dependency codes
        dep_map: Dict[str, List[str]] = {}
        for dep in self.dependencies:
            # Normalize codes to lowercase
            t_code = dep.task_code.lower()
            d_code = dep.depends_on.lower()
            
            if t_code not in dep_map:
                dep_map[t_code] = []
            dep_map[t_code].append(d_code)
            
        for task_code, task in self.tasks.items():
            # We only care if the current task is 'ready' or 'completed'
            # If it's 'pending', it's allowed to wait.
            if task.status.lower() in ('ready', 'completed'):
                start_dependencies = dep_map.get(task_code, [])
                
                for dependency_code in start_dependencies:
                    dependency_task = self.tasks.get(dependency_code)
                    
                    # If dependency is missing (handled by other rules?), skip
                    if not dependency_task:
                        continue
                        
                    # If dependency is NOT completed, this task cannot be ready/completed
                    if dependency_task.status.lower() != 'completed':
                         yield ValidationIssue(
                            severity=Severity.ERROR,
                            message=f"Task '{task.code}' is '{task.status}' but dependency '{dependency_code}' is '{dependency_task.status}'. Dependencies must be 'completed' before successor starts.",
                            location=f"Task: {task.code}"
                        )
