"""
High-level persistence helpers for bootstrap entities.
"""

from __future__ import annotations

from typing import Sequence

from src.models.entities import FeatureDTO, ProjectDTO, SpecificationDTO, TaskDTO
from src.services.data_store_gateway import DataStoreGateway


class UpsertService:
    """Wraps gateway operations with type-friendly helpers."""

    def __init__(self, gateway: DataStoreGateway) -> None:
        self._gateway = gateway

    def persist_project(self, project: ProjectDTO) -> None:
        self._gateway.create_or_update_projects([project])

    def persist_features(self, features: Sequence[FeatureDTO]) -> None:
        if features:
            self._gateway.create_or_update_features(features)

    def persist_specs(self, specs: Sequence[SpecificationDTO]) -> None:
        if specs:
            self._gateway.create_or_update_specs(specs)

    def persist_tasks(self, tasks: Sequence[TaskDTO]) -> None:
        if tasks:
            self._gateway.create_or_update_tasks(tasks)
