from unittest.mock import Mock

import pytest
from src.services.ai_job_service import AIJobService
from src.models.entities import AIJobDTO, TaskDTO
from src.services.bootstrap_options import BootstrapOptions

class TestAIJobService:

    def _create_task(self, code, metadata):
        return TaskDTO(
            code=code,
            feature_code="F01",
            title="Test Task",
            status="pending",
            task_type="backend",
            acceptance="criteria",
            metadata=metadata
        )

    def test_skips_jobs_when_flag_set(self):
        service = AIJobService()
        tasks = [self._create_task(code="T1", metadata={"ai_job": {"type": "code"}})]
        options = BootstrapOptions(skip_ai_jobs=True)
        
        jobs = service.create_ai_jobs(tasks, options)
        assert len(jobs) == 0
        assert service.estimate_ai_job_count(tasks, options) == 0

    def test_creates_job_from_nested_metadata(self):
        service = AIJobService()
        tasks = [
            self._create_task(code="T1", metadata={
                "ai_job": {
                    "type": "review",
                    "prompt": "Check code",
                    "metadata": {"model": "gpt-4"}
                }
            })
        ]
        options = BootstrapOptions(skip_ai_jobs=False)
        
        jobs = service.create_ai_jobs(tasks, options)
        
        assert len(jobs) == 1
        assert jobs[0].task_code == "T1"
        assert jobs[0].job_type == "review"
        assert jobs[0].prompt == "Check code"
        assert jobs[0].metadata == {"model": "gpt-4"}

    def test_creates_job_from_flat_metadata(self):
        service = AIJobService()
        tasks = [
            self._create_task(code="T2", metadata={
                "ai_job_type": "implement",
                "prompt": "Write handlers",
                "ai_metadata": {"tokens": 500}
            })
        ]
        options = BootstrapOptions(skip_ai_jobs=False)
        
        jobs = service.create_ai_jobs(tasks, options)
        
        assert len(jobs) == 1
        assert jobs[0].task_code == "T2"
        assert jobs[0].job_type == "implement"
        assert jobs[0].prompt == "Write handlers"
        assert jobs[0].metadata == {"tokens": 500}

    def test_ignores_tasks_without_ai_metadata(self):
        service = AIJobService()
        tasks = [
            self._create_task(code="T3", metadata={"other": "info"})
        ]
        options = BootstrapOptions(skip_ai_jobs=False)
        
        jobs = service.create_ai_jobs(tasks, options)
        assert len(jobs) == 0

    def test_defaults_to_generic_type_if_missing(self):
        service = AIJobService()
        tasks = [
            self._create_task(code="T4", metadata={"prompt": "Do something"})
        ]
        options = BootstrapOptions(skip_ai_jobs=False)
        
        jobs = service.create_ai_jobs(tasks, options)
        
        assert len(jobs) == 1
        assert jobs[0].job_type == "generic"

    def test_estimate_count_matches_create_logic(self):
        service = AIJobService()
        tasks = [
            self._create_task(code="T1", metadata={"ai_job": {}}),
            self._create_task(code="T2", metadata={"ai_job_type": "code"}),
            self._create_task(code="T3", metadata={})
        ]
        options = BootstrapOptions(skip_ai_jobs=False)
        
        count = service.estimate_ai_job_count(tasks, options)
        jobs = service.create_ai_jobs(tasks, options)
        
        assert count == 2
        assert len(jobs) == 2
