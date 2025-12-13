from __future__ import annotations

import logging
from typing import Sequence

from src.models.entities import ProjectDTO, FeatureDTO, SpecificationDTO, TaskDTO
from src.services.matchers.entity_matcher import EntityMatcher

logger = logging.getLogger(__name__)

class UpsertService:
    """Handles idempotent upsert operations for entities."""

    def __init__(self, matcher: EntityMatcher, gateway: object): # gateway type hint omitted for circular dep risk?
        self._matcher = matcher
        self._gateway = gateway

    def upsert_projects(self, projects: Sequence[ProjectDTO], force: bool = False) -> None:
        to_upsert: list[ProjectDTO] = []
        for project in projects:
            existing = self._matcher.find_existing_project(project)
            if existing:
                if force:
                    logger.info(f"Forcing update of Project {project.code}")
                    to_upsert.append(project)
                else:
                    logger.info(f"Skipping Project {project.code} (exists)")
            else:
                to_upsert.append(project)

        if to_upsert:
            self._gateway.create_or_update_projects(to_upsert)

    def upsert_features(self, features: Sequence[FeatureDTO], force: bool = False) -> None:
        to_upsert: list[FeatureDTO] = []
        for feature in features:
            existing = self._matcher.find_existing_feature(feature)
            if existing:
                if force:
                    logger.info(f"Forcing update of Feature {feature.code}")
                    to_upsert.append(feature)
                else:
                    logger.info(f"Skipping Feature {feature.code} (exists)")
            else:
                to_upsert.append(feature)

        if to_upsert:
            self._gateway.create_or_update_features(to_upsert)

    def upsert_specs(self, specs: Sequence[SpecificationDTO], force: bool = False) -> None:
        to_upsert: list[SpecificationDTO] = []
        for spec in specs:
            existing = self._matcher.find_existing_spec(spec)
            if existing:
                if force:
                    to_upsert.append(spec)
                else:
                    logger.info(f"Skipping Spec {spec.code}")
            else:
                to_upsert.append(spec)

        if to_upsert:
            self._gateway.create_or_update_specs(to_upsert)

    def upsert_tasks(self, tasks: Sequence[TaskDTO], force: bool = False) -> None:
        to_upsert: list[TaskDTO] = []
        for task in tasks:
            existing = self._matcher.find_existing_task(task)
            if existing:
                if force:
                    to_upsert.append(task)
                else:
                    logger.info(f"Skipping Task {task.code}")
            else:
                to_upsert.append(task)

        if to_upsert:
            self._gateway.create_or_update_tasks(to_upsert)
