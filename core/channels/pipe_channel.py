# ipc_project/core/channels/pipe_channel.py

from __future__ import annotations

from multiprocessing import Pipe
from multiprocessing.connection import Connection
from typing import List, Any

from core.utils.logger import AppLogger
from core.security import SecurityManager


class PipeChannel:
    """
    Wrapper over multiprocessing.Pipe providing a simple send/receive API
    with security checks and logging.

    For now we treat this as a one-directional pipe:
    - 'sender' writes on the send endpoint
    - 'receiver' reads on the receive endpoint
    """

    def __init__(
        self,
        channel_id: int,
        name: str,
        allowed_senders: List[int],#deque bi directional left right two level 
        allowed_receivers: List[int],
        logger: AppLogger,
        security_manager: SecurityManager,
    ) -> None:
        self.channel_id = channel_id
        self.name = name
        self.allowed_senders = allowed_senders
        self.allowed_receivers = allowed_receivers
        self.logger = logger
        self.security_manager = security_manager

        # Create underlying pipe (unidirectional semantics)
        send_conn, recv_conn = Pipe(duplex=True)
        self._send_conn: Connection = send_conn
        self._recv_conn: Connection = recv_conn

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def send_message(self, sender_id: int, payload: Any) -> bool:
        """
        Send a message through the pipe if the sender is authorized.

        Returns True on success, False if blocked by security layer.
        """
        if not self.security_manager.validate_sender(
            channel_name=self.name,
            sender_id=sender_id,
            allowed_senders=self.allowed_senders,
        ):
            # Security manager already logged the violation
            return False

        try:
            self._send_conn.send(payload)
            self.logger.info(
                f"[Pipe:{self.name}] Sender {sender_id} -> sent payload: {payload!r}"
            )
            return True
        except (EOFError, OSError) as exc:
            self.logger.error(
                f"[Pipe:{self.name}] Failed to send from {sender_id}: {exc!r}"
            )
            return False

    def receive_message(
        self,
        receiver_id: int,
        block: bool = True,
        timeout: float | None = None,
    ) -> Any | None:
        """
        Receive a message through the pipe if the receiver is authorized.

        If block is False and no message is available, returns None.
        If block is True, waits (optionally with timeout) until a message arrives.
        """
        if not self.security_manager.validate_receiver(
            channel_name=self.name,
            receiver_id=receiver_id,
            allowed_receivers=self.allowed_receivers,
        ):
            # Security manager already logged the violation
            return None

        try:
            if not block:
                # Non-blocking receive
                if not self._recv_conn.poll(timeout=timeout):
                    return None
            else:
                # Blocking with optional timeout
                if timeout is not None and not self._recv_conn.poll(timeout=timeout):
                    return None

            msg = self._recv_conn.recv()
            self.logger.info(
                f"[Pipe:{self.name}] Receiver {receiver_id} <- received payload: {msg!r}"
            )
            return msg
        except (EOFError, OSError) as exc:
            self.logger.error(
                f"[Pipe:{self.name}] Failed to receive for {receiver_id}: {exc!r}"
            )
            return None

    def close(self) -> None:
        """
        Close underlying pipe connections.
        """
        try:
            self._send_conn.close()
        except Exception:
            pass

        try:
            self._recv_conn.close()
        except Exception:
            pass

        self.logger.info(f"[Pipe:{self.name}] Channel closed (id={self.channel_id})")
