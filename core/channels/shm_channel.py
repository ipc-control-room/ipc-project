# ipc_project/core/channels/shm_channel.py

from __future__ import annotations

from multiprocessing import shared_memory, Lock
from typing import List, Any

from core.utils.logger import AppLogger
from core.security import SecurityManager


class SharedMemoryChannel:
    """
    Shared memory IPC channel.

    - Uses a fixed-size byte buffer.
    - Stores UTF-8 encoded text (truncated if too long).
    - Uses a Lock to provide safe, atomic read/write.
    """

    def __init__(
        self,
        channel_id: int,
        name: str,
        allowed_senders: List[int],
        allowed_receivers: List[int],
        logger: AppLogger,
        security_manager: SecurityManager,
        buffer_size: int = 256,
    ) -> None:
        self.channel_id = channel_id
        self.name = name
        self.allowed_senders = allowed_senders
        self.allowed_receivers = allowed_receivers
        self.logger = logger
        self.security_manager = security_manager
        self.buffer_size = buffer_size

        self._lock = Lock()
        # Create a new shared memory block
        self._shm = shared_memory.SharedMemory(create=True, size=self.buffer_size)
        self._clear_buffer()

        self.logger.info(
            f"[SHM:{self.name}] Shared memory created (id={self.channel_id}, size={self.buffer_size})"
        )

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _clear_buffer(self) -> None:
        """
        Zero out the shared memory buffer.
        """
        buf = self._shm.buf
        buf[:] = b"\x00" * self.buffer_size

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #

    def write_value(self, sender_id: int, text: str) -> bool:
        """
        Write a string value into shared memory.

        Returns True on success, False if blocked or failed.
        """
        if not self.security_manager.validate_sender(
            channel_name=self.name,
            sender_id=sender_id,
            allowed_senders=self.allowed_senders,
        ):
            return False

        encoded = text.encode("utf-8")
        if len(encoded) >= self.buffer_size:
            # Truncate to fit with final null terminator
            encoded = encoded[: self.buffer_size - 1]

        try:
            with self._lock:
                buf = self._shm.buf
                # Clear buffer
                buf[:] = b"\x00" * self.buffer_size
                # Write data
                buf[: len(encoded)] = encoded

            self.logger.info(
                f"[SHM:{self.name}] Sender {sender_id} -> wrote value: {text!r}"
            )
            return True
        except Exception as exc:
            self.logger.error(
                f"[SHM:{self.name}] Failed to write from {sender_id}: {exc!r}"
            )
            return False

    def read_value(self, receiver_id: int) -> str | None:
        """
        Read the current string value from shared memory.

        Returns the string or None on error / unauthorized.
        """
        if not self.security_manager.validate_receiver(
            channel_name=self.name,
            receiver_id=receiver_id,
            allowed_receivers=self.allowed_receivers,
        ):
            return None

        try:
            with self._lock:
                buf = self._shm.buf
                # Read up to first null byte
                raw = bytes(buf[:])
            # split at first null
            if b"\x00" in raw:
                raw = raw.split(b"\x00", 1)[0]

            if not raw:
                value = ""
            else:
                value = raw.decode("utf-8", errors="replace")

            self.logger.info(
                f"[SHM:{self.name}] Receiver {receiver_id} <- read value: {value!r}"
            )
            return value
        except Exception as exc:
            self.logger.error(
                f"[SHM:{self.name}] Failed to read for {receiver_id}: {exc!r}"
            )
            return None

    def close(self) -> None:
        """
        Close and unlink the shared memory block.
        """
        try:
            self._shm.close()
        except Exception:
            pass

        try:
            self._shm.unlink()
        except Exception:
            pass

        self.logger.info(f"[SHM:{self.name}] Channel closed (id={self.channel_id})")
