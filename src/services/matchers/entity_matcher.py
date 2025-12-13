from __future__ import annotations

from typing import Iterable, Optional, Protocol, TypeVar

from src.models.entities import ProjectDTO, FeatureDTO, SpecificationDTO, TaskDTO

T = TypeVar("T")

class DataStoreReader(Protocol):
    """Protocol for reading entities from the datastore."""
    
    def get_project(self, code: str) -> Optional[ProjectDTO]: ...
    def get_feature(self, code: str) -> Optional[FeatureDTO]: ...
    def get_spec(self, code: str) -> Optional[SpecificationDTO]: ...
    def get_task(self, code: str) -> Optional[TaskDTO]: ...

class EntityMatcher:
    """Matches incoming entities against existing ones in the datastore to determine sync status."""

    def __init__(self, reader: DataStoreReader):
        self._reader = reader

    def _is_postgres_backend(self) -> bool:
        return bool(getattr(self._reader, "_is_postgres", False))

    def find_existing_project(self, project: ProjectDTO) -> Optional[ProjectDTO]:
        identifier = project.name if self._is_postgres_backend() else project.code
        return self._reader.get_project(identifier)

    def find_existing_feature(self, feature: FeatureDTO) -> Optional[FeatureDTO]:
        identifier = feature.name if self._is_postgres_backend() else feature.code
        return self._reader.get_feature(identifier)

    def find_existing_spec(self, spec: SpecificationDTO) -> Optional[SpecificationDTO]:
        identifier = spec.title if self._is_postgres_backend() else spec.code
        return self._reader.get_spec(identifier)
    
    def find_existing_task(self, task: TaskDTO) -> Optional[TaskDTO]:
        return self._reader.get_task(task.code)
