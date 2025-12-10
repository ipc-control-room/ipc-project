# ipc_project/core/channels/queue_channel.py

from __future__ import annotations

from multiprocessing import Queue
from queue import Empty
from typing import Any, List

from core.utils.logger import AppLogger
from core.security import SecurityManager


class QueueChannel:
    """
    Wrapper over multiprocessing.Queue with security checks and logging.

    Supports multiple producers and consumers.
    """

    def __init__(
        self,
        channel_id: int,
        name: str,
        allowed_senders: List[int],
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

        self._queue: Queue[Any] = Queue()

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def send_message(self, sender_id: int, payload: Any) -> bool:
        """
        Enqueue a message if the sender is authorized.
        """
        if not self.security_manager.validate_sender(
            channel_name=self.name,
            sender_id=sender_id,
            allowed_senders=self.allowed_senders,
        ):
            return False

        try:
            self._queue.put(payload)
            self.logger.info(
                f"[Queue:{self.name}] Sender {sender_id} -> enqueued payload: {payload!r}"
            )
            return True
        except Exception as exc:
            self.logger.error(
                f"[Queue:{self.name}] Failed to enqueue from {sender_id}: {exc!r}"
            )
            return False

    def receive_message(
        self,
        receiver_id: int,
        block: bool = False,
        timeout: float | None = None,
    ) -> Any | None:
        """
        Dequeue a message if the receiver is authorized.

        If block=False and queue is empty, returns None.
        """
        if not self.security_manager.validate_receiver(
            channel_name=self.name,
            receiver_id=receiver_id,
            allowed_receivers=self.allowed_receivers,
        ):
            return None

        try:
            if block:
                msg = self._queue.get(timeout=timeout) if timeout is not None else self._queue.get()
            else:
                msg = self._queue.get_nowait()

            self.logger.info(
                f"[Queue:{self.name}] Receiver {receiver_id} <- dequeued payload: {msg!r}"
            )
            return msg
        except Empty:
            # No message available
            return None
        except Exception as exc:
            self.logger.error(
                f"[Queue:{self.name}] Failed to dequeue for {receiver_id}: {exc!r}"
            )
            return None

    def close(self) -> None:
        """
        Close underlying queue.
        """
        try:
            self._queue.close()
            self._queue.join_thread()
        except Exception:
            pass

        self.logger.info(f"[Queue:{self.name}] Channel closed (id={self.channel_id})")
