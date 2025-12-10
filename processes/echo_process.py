# ipc_project/processes/echo_process.py

from processes.base_process import BaseWorker


class EchoWorker(BaseWorker):
    """
    Reads from a pipe/queue and echoes back uppercase responses.
    """

    def __init__(self, proc_id, name, cmd_queue, out_queue, channel, receiver_id, sender_id):
        super().__init__(proc_id, name, cmd_queue, out_queue)
        self.channel = channel
        self.receiver_id = receiver_id
        self.sender_id = sender_id

    def run_loop(self):
        msg = self.channel.receive_message(self.receiver_id, block=False)
        if msg:
            echo_msg = msg.upper()
            self.channel.send_message(self.sender_id, echo_msg)
            self.log(f"{self.name}: {msg} -> {echo_msg}")
