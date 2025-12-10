# ipc_project/core/ipc_manager.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any

from core.utils.logger import AppLogger
from core.security import SecurityManager
from core.channels.pipe_channel import PipeChannel
from core.channels.queue_channel import QueueChannel
#FINAAL BRICK 
from core.channels.shm_channel import SharedMemoryChannel



@dataclass
class IPCChannelInfo:
    id: int
    channel_type: str  # "pipe", "queue", "shared_memory"
    name: str
    allowed_senders: List[int]
    allowed_receivers: List[int]


class IPCManager:
    """
    Central registry for IPC channels.

    Currently supports PipeChannel and QueueChannel.
    """

    def __init__(self, logger: AppLogger, security_manager: SecurityManager) -> None:
        self.logger = logger
        self.security_manager = security_manager

        self._next_id: int = 1
        self._channels_info: Dict[int, IPCChannelInfo] = {}
        self._channels_impl: Dict[int, Any] = {}

    # ------------------------------------------------------------------ #
    # Internal helper                                                     #
    # ------------------------------------------------------------------ #

    def _create_channel_info(
        self,
        channel_type: str,
        name: str,
        allowed_senders: List[int] | None,
        allowed_receivers: List[int] | None,
    ) -> IPCChannelInfo:
        if allowed_senders is None:
            allowed_senders = []
        if allowed_receivers is None:
            allowed_receivers = []

        chan_id = self._next_id
        self._next_id += 1

        info = IPCChannelInfo(
            id=chan_id,
            channel_type=channel_type,
            name=name,
            allowed_senders=allowed_senders,
            allowed_receivers=allowed_receivers,
        )
        self._channels_info[chan_id] = info

        self.logger.info(
            f"IPC channel created: id={chan_id}, type={channel_type}, name={name}"
        )
        return info

    # ------------------------------------------------------------------ #
    # Pipe                                                                #
    # ------------------------------------------------------------------ #

    def create_pipe_channel(
        self,
        name: str,
        allowed_senders: List[int] | None = None,
        allowed_receivers: List[int] | None = None,
    ) -> PipeChannel:
        info = self._create_channel_info(
            channel_type="pipe",
            name=name,
            allowed_senders=allowed_senders,
            allowed_receivers=allowed_receivers,
        )

        pipe = PipeChannel(
            channel_id=info.id,
            name=info.name,
            allowed_senders=info.allowed_senders,
            allowed_receivers=info.allowed_receivers,
            logger=self.logger,
            security_manager=self.security_manager,
        )

        self._channels_impl[info.id] = pipe
        return pipe

    # ------------------------------------------------------------------ #
    # Queue                                                               #
    # ------------------------------------------------------------------ #

    def create_queue_channel(
        self,
        name: str,
        allowed_senders: List[int] | None = None,
        allowed_receivers: List[int] | None = None,
    ) -> QueueChannel:
        info = self._create_channel_info(
            channel_type="queue",
            name=name,
            allowed_senders=allowed_senders,
            allowed_receivers=allowed_receivers,
        )

        q = QueueChannel(
            channel_id=info.id,
            name=info.name,
            allowed_senders=info.allowed_senders,
            allowed_receivers=info.allowed_receivers,
            logger=self.logger,
            security_manager=self.security_manager,
        )

        self._channels_impl[info.id] = q
        return q
        # ------------------------------------------------------------------ #
    # Shared Memory                                                      #
    # ------------------------------------------------------------------ #

    def create_shared_memory_channel(
        self,
        name: str,
        allowed_senders: List[int] | None = None,
        allowed_receivers: List[int] | None = None,
        buffer_size: int = 256,
    ) -> SharedMemoryChannel:
        info = self._create_channel_info(
            channel_type="shared_memory",
            name=name,
            allowed_senders=allowed_senders,
            allowed_receivers=allowed_receivers,
        )

        shm = SharedMemoryChannel(
            channel_id=info.id,
            name=info.name,
            allowed_senders=info.allowed_senders,
            allowed_receivers=info.allowed_receivers,
            logger=self.logger,
            security_manager=self.security_manager,
            buffer_size=buffer_size,
        )

        self._channels_impl[info.id] = shm
        return shm

    # ------------------------------------------------------------------ #
    # Queries                                                             #
    # ------------------------------------------------------------------ #

    def list_channels(self) -> List[IPCChannelInfo]:
        return list(self._channels_info.values())

    def get_channel_impl(self, channel_id: int) -> Any | None:
        return self._channels_impl.get(channel_id)
