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
        for project in projects:
            existing = self._matcher.find_existing_project(project)
            if existing:
                if force:
                    logger.info(f"Forcing update of Project {project.code}")
                    self._gateway.create_or_update_projects([project])
                else:
                    logger.info(f"Skipping Project {project.code} (exists)")
                    # Could perform diff check here
            else:
                self._gateway.create_or_update_projects([project])

    def upsert_features(self, features: Sequence[FeatureDTO], force: bool = False) -> None:
        for feature in features:
            existing = self._matcher.find_existing_feature(feature)
            if existing:
                if force:
                    logger.info(f"Forcing update of Feature {feature.code}")
                    self._gateway.create_or_update_features([feature])
                else:
                    logger.info(f"Skipping Feature {feature.code} (exists)")
            else:
                self._gateway.create_or_update_features([feature])

    def upsert_specs(self, specs: Sequence[SpecificationDTO], force: bool = False) -> None:
        for spec in specs:
             existing = self._matcher.find_existing_spec(spec)
             if existing:
                 if force:
                     self._gateway.create_or_update_specs([spec])
                 else:
                     logger.info(f"Skipping Spec {spec.code}")
             else:
                 self._gateway.create_or_update_specs([spec])

    def upsert_tasks(self, tasks: Sequence[TaskDTO], force: bool = False) -> None:
         for task in tasks:
             existing = self._matcher.find_existing_task(task)
             if existing:
                 if force:
                     self._gateway.create_or_update_tasks([task])
                 else:
                     logger.info(f"Skipping Task {task.code}")
             else:
                 self._gateway.create_or_update_tasks([task])
