import pytest

from src.services.parser.task_parser import TaskParser


@pytest.fixture
def tasks_dir(tmp_path):
    tasks = tmp_path / "tasks"
    tasks.mkdir()

    task_dir = tasks / "001-user-auth"
    task_dir.mkdir()

    task_file = task_dir / "t001.md"
    task_file.write_text(
        """# T001 Implement login

## Acceptance Criteria
- Works
- Has tests

Depends on: T000
""",
        encoding="utf-8",
    )

    return tasks


def test_task_parser_extracts_heading_code_acceptance_and_deps(tasks_dir):
    parser = TaskParser(tasks_dir)
    tasks = parser.parse()

    assert len(tasks) == 1
    task = tasks[0]

    assert task.code == "T001"
    assert task.feature_code == "user-auth"
    assert task.title == "T001 Implement login"
    assert task.acceptance == "- Works\n- Has tests"
    assert task.metadata.get("dependencies") == ["T000"]
