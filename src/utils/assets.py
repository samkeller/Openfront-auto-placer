"""Optional local icon loading with safe text fallbacks."""

from __future__ import annotations

from pathlib import Path
import sys
import tkinter as tk


def resource_path(*parts: str) -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return root.joinpath(*parts)


def load_icons(master: tk.Misc) -> dict[str, tk.PhotoImage]:
    """Load individually verified PNG icons when bundled."""
    directory = resource_path("resources", "icons")
    icons: dict[str, tk.PhotoImage] = {}
    if not directory.is_dir():
        return icons
    for path in directory.glob("*.png"):
        try:
            icons[path.stem] = tk.PhotoImage(master=master, file=path)
        except tk.TclError:
            continue
    return icons
