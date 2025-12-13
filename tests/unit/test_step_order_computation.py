from __future__ import annotations

import inspect
import time
from pathlib import Path
from unittest.mock import Mock

from src.models.entities import TaskDTO, TaskDependencyDTO
from src.services.bootstrap_orchestrator import BootstrapOrchestrator


def _task(code: str) -> TaskDTO:
    return TaskDTO(
        code=code,
        feature_code="F01",
        title="Test Task",
        status="pending",
        task_type="backend",
        acceptance="criteria",
        metadata={},
    )


class TestStepOrderComputation:
    def test_calculate_step_orders_correctness(self) -> None:
        gateway = Mock()
        orchestrator = BootstrapOrchestrator(Path("."), gateway)

        tasks = [_task("A"), _task("B"), _task("C"), _task("D"), _task("E")]
        deps = [
            TaskDependencyDTO(task_code="B", depends_on="A"),
            TaskDependencyDTO(task_code="C", depends_on="A"),
            TaskDependencyDTO(task_code="D", depends_on="B"),
            TaskDependencyDTO(task_code="D", depends_on="C"),
            TaskDependencyDTO(task_code="E", depends_on="D"),
        ]

        updated = orchestrator._calculate_step_orders(tasks, deps)
        by_code = {t.code: t for t in updated}

        assert by_code["A"].step_order == 1
        assert by_code["B"].step_order == 2
        assert by_code["C"].step_order == 2
        assert by_code["D"].step_order == 3
        assert by_code["E"].step_order == 4

    def test_calculate_step_orders_scalability_and_no_pop0(self) -> None:
        src = inspect.getsource(BootstrapOrchestrator._calculate_step_orders)
        assert "pop(0)" not in src

        gateway = Mock()
        orchestrator = BootstrapOrchestrator(Path("."), gateway)

        n = 20000
        tasks = [_task(f"T{i:05d}") for i in range(n)]
        deps = [
            TaskDependencyDTO(task_code=f"T{i:05d}", depends_on=f"T{i - 1:05d}")
            for i in range(1, n)
        ]

        start = time.perf_counter()
        updated = orchestrator._calculate_step_orders(tasks, deps)
        elapsed = time.perf_counter() - start

        assert len(updated) == n
        by_code = {t.code: t.step_order for t in updated[:3] + updated[-3:]}
        assert by_code["T00000"] == 1
        assert by_code["T00001"] == 2
        assert by_code["T00002"] == 3
        assert by_code[f"T{n - 3:05d}"] == n - 2
        assert by_code[f"T{n - 2:05d}"] == n - 1
        assert by_code[f"T{n - 1:05d}"] == n

        assert elapsed < 5.0
