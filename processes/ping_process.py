# ipc_project/processes/ping_process.py

from processes.base_process import BaseWorker
import time


class PingWorker(BaseWorker):
    """
    Sends "PING" once every second to a pipe or queue channel.
    """

    def __init__(self, proc_id, name, cmd_queue, out_queue, channel, sender_id):
        super().__init__(proc_id, name, cmd_queue, out_queue)
        self.channel = channel
        self.sender_id = sender_id
        self._last_ping = 0

    def run_loop(self):
        # Send ping every 1 second
        now = time.time()
        if now - self._last_ping >= 1:
            self.channel.send_message(self.sender_id, "PING")
            self.log(f"{self.name} -> sent PING")
            self._last_ping = now
