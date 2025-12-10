# ipc_project/main.py

import tkinter as tk  # (kept if you need anything from tk before app init)

from core.process_manager import ProcessManager
from core.ipc_manager import IPCManager
from core.security import SecurityManager
from core.utils.logger import AppLogger
from gui.dashboard import ControlRoomApp


def main() -> None:
    # Core app components
    logger = AppLogger()
    security_manager = SecurityManager(logger=logger)
    process_manager = ProcessManager(logger=logger)
    ipc_manager = IPCManager(logger=logger, security_manager=security_manager)

    # GUI application
    app = ControlRoomApp(
        process_manager=process_manager,
        ipc_manager=ipc_manager,
        security_manager=security_manager,
        logger=logger,
    )
    app.mainloop()


if __name__ == "__main__":
    main()
