# ipc_project/processes/__init__.py

"""
Process workers package.

Do NOT import any GUI modules from here.
"""

from .base_process import BaseWorker  # optional
from .ping_process import PingWorker  # optional
from .echo_process import EchoWorker  # optional

__all__ = ["BaseWorker", "PingWorker", "EchoWorker"]
