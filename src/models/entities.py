"""
Data transfer objects for bootstrap pipeline entities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional, Any


@dataclass(slots=True, frozen=True)
class ProjectDTO:
    code: str
    name: str
    description: str
    repository_path: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class FeatureDTO:
    code: str
    project_code: str
    name: str
    description: str
    priority: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class SpecificationDTO:
    code: str
    feature_code: str
    title: str
    path: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TaskDTO:
    code: str
    feature_code: str
    title: str
    status: str
    task_type: str
    acceptance: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TaskDependencyDTO:
    task_code: str
    depends_on: str


@dataclass(slots=True, frozen=True)
class TaskRunDTO:
    task_code: str
    status: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AIJobDTO:
    task_code: str
    job_type: str
    prompt: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
