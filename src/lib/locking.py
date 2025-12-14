"""
Filesystem locking utilities for coordinating bootstrap runs.
"""

from __future__ import annotations

import contextlib
import fcntl
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class LockConfig:
    lock_dir: Path

    def ensure_dir(self) -> None:
        self.lock_dir.mkdir(parents=True, exist_ok=True)


class FileLock:
    """
    Simple advisory file lock using fcntl.
    """

    def __init__(self, lock_path: Path) -> None:
        self._lock_path = lock_path
        self._fd: int | None = None
        self._file = None

    def acquire(self, *, non_blocking: bool = False) -> None:
        lock_file = open(self._lock_path, "w+")  # noqa: SIM115
        try:
            flags = fcntl.LOCK_EX | (fcntl.LOCK_NB if non_blocking else 0)
            fcntl.flock(lock_file.fileno(), flags)
        except Exception:
            lock_file.close()
            raise
        self._fd = lock_file.fileno()
        self._file = lock_file

    def release(self) -> None:
        if self._fd is None:
            return
        fcntl.flock(self._fd, fcntl.LOCK_UN)
        if self._file is not None:
            self._file.close()
            self._file = None
        self._fd = None

    def __enter__(self) -> "FileLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()


@contextlib.contextmanager
def queue_lock(lock_config: LockConfig, queue_name: str, *, non_blocking: bool = False) -> Iterator[None]:
    """
    Acquire a lock for a given queue name.
    """

    lock_config.ensure_dir()
    lock_path = lock_config.lock_dir / f"{queue_name}.lock"
    lock = FileLock(lock_path)
    lock.acquire(non_blocking=non_blocking)
    try:
        yield
    finally:
        lock.release()
