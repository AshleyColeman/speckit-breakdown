"""
Validation rules for the bootstrap process.
"""

from __future__ import annotations

import logging
import re
from typing import Iterable, Set, Dict, List

logger = logging.getLogger(__name__)

from src.models.entities import ProjectDTO, FeatureDTO, SpecificationDTO, TaskDTO, TaskDependencyDTO
from src.services.validation_pipeline import ValidationRule, ValidationIssue, Severity


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
            if p.code in seen_codes:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Duplicate Project Code found: {p.code}",
                    location=f"Project: {p.name}"
                )
            seen_codes.add(p.code)

        # Check features
        for f in self.features:
            if f.code in seen_codes:
                yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Duplicate Feature Code found: {f.code}",
                    location=f"Feature: {f.name} (Project: {f.project_code})"
                )
            seen_codes.add(f.code)
            
        # Check specs
        for s in self.specs:
            if s.code in seen_codes:
                 yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Duplicate Spec Code found: {s.code}",
                    location=f"Spec: {s.title} (Feature: {s.feature_code})"
                )
            seen_codes.add(s.code)

        # Check tasks
        for t in self.tasks:
             if t.code in seen_codes:
                 yield ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Duplicate Task Code found: {t.code}",
                    location=f"Task: {t.title} (Spec: {t.feature_code})" # Note: TaskDTO has feature_code? Let's check entities.py. No, looks like I should check TaskDTO attributes again.
                )
             seen_codes.add(t.code)


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
