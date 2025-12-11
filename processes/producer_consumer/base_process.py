# ipc_project/processes/base_process.py

from __future__ import annotations
from multiprocessing import Process, Queue
import time
import traceback


class BaseWorker(Process):
    """
    Base class for all test processes.

    Each worker:
    - Receives commands via cmd_queue.
    - Sends logs/output back via out_queue.
    - Runs a user-defined loop (run_loop).
    """

    def __init__(self, proc_id: int, name: str, cmd_queue: Queue, out_queue: Queue):
        super().__init__()
        self.proc_id = proc_id
        self.name = name
        self.cmd_queue = cmd_queue
        self.out_queue = out_queue
        self._running = True

    def log(self, message: str):
        """
        Send a log/output message back to the main GUI.
        """
        self.out_queue.put((self.proc_id, message))

    def stop(self):
        self._running = False

    # ---------------------------------------------------------
    # Worker main loop
    # ---------------------------------------------------------
    def run(self):
        self.log(f"{self.name}: started")

        try:
            while self._running:
                # Process commands
                try:
                    cmd = self.cmd_queue.get_nowait()
                    if cmd == "stop":
                        self.log(f"{self.name}: stopping")
                        self._running = False
                        break
                    self.handle_command(cmd)
                except Exception:
                    pass

                # User-defined loop implementation
                self.run_loop()

                time.sleep(0.1)

        except Exception as e:
            self.out_queue.put((self.proc_id, f"ERROR: {e}"))
            traceback.print_exc()

        self.log(f"{self.name}: terminated")

    # ---------------------------------------------------------
    # To be overridden in subclasses
    # ---------------------------------------------------------
    def handle_command(self, cmd):
        pass

    def run_loop(self):
        pass
