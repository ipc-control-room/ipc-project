# ipc_project/core/process_manager.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from core.utils.logger import AppLogger
from multiprocessing import Queue
from processes.ping_process import PingWorker
from processes.echo_process import EchoWorker



@dataclass
class ProcessInfo:
    id: int
    name: str
    role: str
    status: str = "created"


class ProcessManager:
    """
    Manages processes (for now: logical/test processes).
    Later, this will spawn actual multiprocessing.Process workers.
    """

    def __init__(self, logger: AppLogger) -> None:
        self.logger = logger
        self._next_id: int = 1
        self._processes: Dict[int, ProcessInfo] = {}

    def create_dummy_process(self, name: str | None = None, role: str = "Test") -> Dict:
        """
        For early GUI work: create a fake process entry and return its info as dict.
        Later, replace with real process spawning.
        """
        proc_id = self._next_id
        self._next_id += 1

        if name is None:
            name = f"proc_{proc_id}"

        info = ProcessInfo(id=proc_id, name=name, role=role, status="running")
        self._processes[proc_id] = info

        self.logger.info(f"Process registered: id={proc_id}, name={name}, role={role}")
        return {
            "id": proc_id,
            "name": name,
            "role": role,
            "status": info.status,
        }

    def list_processes(self) -> List[ProcessInfo]:
        return list(self._processes.values())

    def terminate_process(self, proc_id: int) -> bool:
        """
        Placeholder for termination logic.
        """
        info = self._processes.get(proc_id)
        if not info:
            self.logger.warning(f"Terminate requested for unknown process: {proc_id}")
            return False

        info.status = "terminated"
        self.logger.info(f"Process terminated: id={proc_id}, name={info.name}")
        # Later, actually kill the underlying multiprocessing.Process
        return True
    def create_ping_process(self, channel, sender_id):
        """
        Create a ping process that sends PING every second.
        """
        proc_id = self._next_id
        self._next_id += 1

        cmd_q = Queue()
        out_q = Queue()

        worker = PingWorker(proc_id, f"Ping_{proc_id}", cmd_q, out_q, channel, sender_id)
        worker.start()

        self._processes[proc_id] = worker

        self.logger.info(f"Ping process started (id={proc_id})")
        return proc_id, worker, out_q


    def create_echo_process(self, channel, receiver_id, sender_id):
        """
        Create an echo worker that echoes messages it receives.
        """
        proc_id = self._next_id
        self._next_id += 1

        cmd_q = Queue()
        out_q = Queue()

        worker = EchoWorker(proc_id, f"Echo_{proc_id}", cmd_q, out_q, channel, receiver_id, sender_id)
        worker.start()

        self._processes[proc_id] = worker

        self.logger.info(f"Echo process started (id={proc_id})")
        return proc_id, worker, out_q
