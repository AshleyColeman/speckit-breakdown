"""
Resource guard utilities for monitoring CPU/memory/file sizes.
"""

from __future__ import annotations

import logging
import os
import resource
from dataclasses import dataclass
from time import perf_counter

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResourceLimits:
    max_memory_mb: int
    max_cpu_percent: int
    max_file_mb: int


class ResourceGuard:
    def __init__(self, limits: ResourceLimits) -> None:
        self._limits = limits
        self._cpu_window_start = perf_counter()

    def check_memory(self) -> None:
        usage_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if os.name == "posix":
            mem_mb = usage_kb / 1024
        else:  # pragma: no cover
            mem_mb = usage_kb / (1024 * 1024)

        if mem_mb > self._limits.max_memory_mb:
            raise MemoryError(f"Memory usage exceeded limit: {mem_mb:.2f}MB > {self._limits.max_memory_mb}MB")
        logger.debug("Memory usage OK", extra={"usage_mb": mem_mb})

    def check_cpu(self) -> None:
        current = perf_counter()
        elapsed = current - self._cpu_window_start
        if elapsed == 0:
            return
        cpu_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime
        cpu_percent = min(100.0, (cpu_time / elapsed) * 100)
        if cpu_percent > self._limits.max_cpu_percent:
            raise RuntimeError(f"CPU usage exceeded limit: {cpu_percent:.2f}% > {self._limits.max_cpu_percent}%")
        logger.debug("CPU usage OK", extra={"usage_percent": cpu_percent})

    def check_file_size(self, file_path: str) -> None:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > self._limits.max_file_mb:
            raise RuntimeError(f"File size exceeded limit: {size_mb:.2f}MB > {self._limits.max_file_mb}MB")
        logger.debug("File size OK", extra={"path": file_path, "size_mb": size_mb})

    def enforce_all(self) -> None:
        self.check_memory()
        self.check_cpu()
