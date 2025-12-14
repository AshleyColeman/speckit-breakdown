from __future__ import annotations

from multiprocessing import Event, Process
from pathlib import Path

from typer.testing import CliRunner

from src.cli import app
from src.cli.commands.db_prepare import _lock_name_for_run
from src.lib.config_loader import ConfigLoader
from src.lib.locking import FileLock
from tests.fixtures.projects.full_project import create_full_project

runner = CliRunner()


def _hold_lock(lock_path: Path, ready: Event, release: Event) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(lock_path)
    lock.acquire()
    ready.set()
    release.wait(10)
    lock.release()


def test_lock_prevents_concurrent_runs(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    create_full_project(project_dir)

    db_path = tmp_path / "test_db.sqlite"
    config = ConfigLoader(docs_root=project_dir, storage_path=db_path).materialize()

    queue_name = _lock_name_for_run(config, str(config.storage_path))
    lock_path = config.storage_path.parent / ".locks" / f"{queue_name}.lock"

    ready = Event()
    release = Event()
    process = Process(target=_hold_lock, args=(lock_path, ready, release))
    process.start()

    try:
        assert ready.wait(5)

        result = runner.invoke(app, ["--docs-path", str(project_dir), "--storage-path", str(db_path)])
        assert result.exit_code == 1
        assert "already in progress" in result.stdout.lower()
    finally:
        release.set()
        process.join(timeout=5)
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
