"""Visual tokens and ttk styling shared by every GUI module."""

import tkinter as tk
from tkinter import ttk


BG = "#0d1117"
SURFACE = "#161b26"
SURFACE_ACTIVE = "#12251b"
INPUT_BG = "#0b0f16"
BORDER = "#252d3d"
BORDER_ACTIVE = "#2ea043"
ACCENT = "#4c8dff"
ACCENT_HOVER = "#6ba1ff"
GHOST = "#1d2534"
GHOST_HOVER = "#273041"
SUCCESS = "#2ea043"
IDLE_DOT = "#2b3545"
TEXT = "#e6edf3"
MUTED = "#8b96a8"
FONT = "Segoe UI"


def apply_theme(root: tk.Misc) -> None:
    """Apply the flat dark theme to the only ttk widget left: the entry."""
    root.configure(background=BG)
    style = ttk.Style(root)
    style.theme_use("clam")
    for name, surface in (("Dark.TEntry", SURFACE), ("Active.TEntry", SURFACE_ACTIVE)):
        # background paints the corner pixels left over by the 1px border.
        style.configure(name, background=surface, fieldbackground=INPUT_BG,
                        foreground=TEXT, insertcolor=TEXT, bordercolor=BORDER,
                        lightcolor=BORDER, darkcolor=BORDER, borderwidth=1,
                        relief="flat", padding=5)
        style.map(name,
                  bordercolor=[("focus", ACCENT)],
                  lightcolor=[("focus", ACCENT)],
                  darkcolor=[("focus", ACCENT)])
