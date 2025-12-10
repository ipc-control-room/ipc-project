# ipc_project/core/utils/logger.py

from __future__ import annotations

from typing import Callable, List


class AppLogger:
    """
    Central logger that sends log messages to registered sinks (e.g., GUI log panel).
    """

    def __init__(self) -> None:
        self._sinks: List[Callable[[str, str], None]] = []

    def register_sink(self, sink: Callable[[str, str], None]) -> None:
        """
        Register a sink callback. Signature: sink(message: str, level: str).
        """
        self._sinks.append(sink)

    def _emit(self, message: str, level: str) -> None:
        for sink in self._sinks:
            try:
                sink(message, level)
            except Exception:
                # Avoid crashing logger because of one faulty sink
                pass

    def info(self, message: str) -> None:
        self._emit(message, "INFO")

    def warning(self, message: str) -> None:
        self._emit(message, "WARN")

    def error(self, message: str) -> None:
        self._emit(message, "ERROR")

    def security(self, message: str) -> None:
        self._emit(message, "SECURITY")
