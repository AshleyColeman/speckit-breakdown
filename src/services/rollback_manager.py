"""
Rollback management utilities.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable, Iterator, List

logger = logging.getLogger(__name__)


@dataclass
class RollbackAction:
    description: str
    fn: Callable[[], None]


@dataclass
class RollbackManager:
    actions: List[RollbackAction] = field(default_factory=list)

    def add_action(self, description: str, fn: Callable[[], None]) -> None:
        logger.debug("Registering rollback action", extra={"description": description})
        self.actions.append(RollbackAction(description=description, fn=fn))

    def rollback(self) -> None:
        logger.warning("Rolling back operations", extra={"count": len(self.actions)})
        while self.actions:
            action = self.actions.pop()
            try:
                action.fn()
            except Exception as exc:  # pragma: no cover
                logger.exception("Rollback action failed", extra={"action": action.description, "error": str(exc)})


@contextmanager
def transactional_context(manager: RollbackManager) -> Iterator[None]:
    try:
        yield
    except Exception:
        manager.rollback()
        raise
