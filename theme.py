# ipc_project/gui/theme.py

import tkinter as tk
from tkinter import ttk


def apply_dark_theme(root: tk.Tk | tk.Toplevel) -> None:
    """
    Apply a simple dark theme using ttk.Style.
    This will later be extended with richer styling.
    """
    style = ttk.Style(root)

    # Use built-in theme as base
    base_theme = "clam" if "clam" in style.theme_names() else style.theme_use()
    style.theme_use(base_theme)

    # General colors
    bg = "#111111"
    fg = "#f0f0f0"
    accent = "#3aa8ff"
    panel_bg = "#1b1b1b"

    root.configure(bg=bg)

    style.configure(
        ".",
        background=bg,
        foreground=fg,
        fieldbackground=panel_bg,
    )

    style.configure(
        "TFrame",
        background=bg,
    )
    style.configure(
        "Panel.TFrame",
        background=panel_bg,
    )

    style.configure(
        "TLabel",
        background=bg,
        foreground=fg,
    )

    style.configure(
        "Header.TLabel",
        background=bg,
        foreground=accent,
        font=("Segoe UI", 13, "bold"),
    )

    style.configure(
        "TButton",
        padding=6,
        relief="flat",
        background=panel_bg,
        foreground=fg,
    )
    style.map(
        "TButton",
        background=[("active", "#262626")],
        foreground=[("active", fg)],
    )

    style.configure(
        "TNotebook",
        background=bg,
        tabmargins=(2, 5, 2, 0),
    )
    style.configure(
        "TNotebook.Tab",
        padding=(12, 6),
        background=panel_bg,
        foreground=fg,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", accent)],
        foreground=[("selected", "#000000")],
    )
