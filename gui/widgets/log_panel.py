# ipc_project/gui/widgets/log_panel.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class LogPanel(ttk.Frame):
    """
    Bottom panel displaying security and event logs.
    """

    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        super().__init__(parent, style="Panel.TFrame", *args, **kwargs)

        label = ttk.Label(self, text="Event & Security Log", style="Header.TLabel")
        label.pack(side=tk.TOP, anchor="w", padx=8, pady=(4, 2))

        self.text = tk.Text(
            self,
            height=8,
            bg="#101010",
            fg="#f0f0f0",
            insertbackground="#f0f0f0",
            borderwidth=0,
            highlightthickness=0,
            state="disabled",
            wrap="word",
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=(0, 6))

        scrollbar = ttk.Scrollbar(self, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar.set)

    def append_entry(self, message: str, level: str = "INFO") -> None:
        """
        Append a log entry to the panel.
        Called by the AppLogger via registered sink.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}\n"

        self.text.configure(state="normal")
        self.text.insert(tk.END, line)
        self.text.see(tk.END)
        self.text.configure(state="disabled")
