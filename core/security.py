# ipc_project/core/security.py

from __future__ import annotations

from typing import List

from core.utils.logger import AppLogger


class SecurityManager:
    """
    Security layer that can be consulted before sending/receiving on channels.
    For now, it just checks process IDs against allowed lists.
    """

    def __init__(self, logger: AppLogger) -> None:
        self.logger = logger

    def validate_sender(self, channel_name: str, sender_id: int, allowed_senders: List[int]) -> bool:
        if not allowed_senders or sender_id in allowed_senders:
            return True

        self.logger.security(
            f"Unauthorized send attempt: process {sender_id} on channel '{channel_name}'"
        )
        return False

    def validate_receiver(
        self, channel_name: str, receiver_id: int, allowed_receivers: List[int]
    ) -> bool:
        if not allowed_receivers or receiver_id in allowed_receivers:
            return True

        self.logger.security(
            f"Unauthorized receive attempt: process {receiver_id} on channel '{channel_name}'"
        )
        return False
