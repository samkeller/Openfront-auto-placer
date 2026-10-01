"""Card widget exposing one building's hotkey, game key and multiplier."""

from typing import Callable
import tkinter as tk
from tkinter import ttk

from src.config.loader import Building, parse_hotkey
from src.gui.labels import BUILDING_LABELS
from src.gui.theme import (
    BG, BORDER, BORDER_ACTIVE, FONT, IDLE_DOT, MUTED, SUCCESS, SURFACE,
    SURFACE_ACTIVE, TEXT,
)
from src.gui.widgets import Card, Dot, Segmented


MODIFIERS = {"ctrl", "shift", "alt"}


def hotkey_text(hotkey: frozenset[str]) -> str:
    """Render a hotkey with its modifiers first, matching the config format."""
    return "+".join(sorted(hotkey, key=lambda item: (item not in MODIFIERS, item)))


class BuildingCard(Card):
    """Rounded, clickable card holding the editable fields of one building."""

    def __init__(self, master: tk.Misc, building: Building,
                 on_toggle: Callable[[str], None],
                 icon: tk.PhotoImage | None = None) -> None:
        super().__init__(master, BG, padding=13)
        self.name = building.name
        self.active = tk.BooleanVar(value=False)
        self.hotkey = tk.StringVar(value=hotkey_text(building.hotkey))
        self.game_key = tk.StringVar(value=building.game_key)
        self.multiplier = tk.StringVar(value=str(building.multiplier))

        self.body.columnconfigure(1, weight=1)
        self._entries: list[ttk.Entry] = []
        if icon is not None:
            tk.Label(self.body, image=icon, bg=SURFACE).grid(
                row=0, column=0, rowspan=2, padx=(0, 14), sticky="n"
            )
        title = tk.Label(self.body, text=BUILDING_LABELS[building.name], bg=SURFACE,
                         fg=TEXT, font=(FONT, 11, "bold"))
        title.grid(row=0, column=1, sticky="w")
        self._dot = Dot(self.body, SURFACE, IDLE_DOT)
        self._dot.grid(row=0, column=2, sticky="ne", pady=3)

        controls = tk.Frame(self.body, bg=SURFACE)
        controls.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(9, 0))
        self._field(controls, "HOTKEY", self.hotkey, 11).pack(side="left")
        self._field(controls, "KEY", self.game_key, 3).pack(side="left", padx=10)
        count = tk.Frame(controls, bg=SURFACE)
        count.pack(side="left")
        tk.Label(count, text="COUNT", bg=SURFACE, fg=MUTED,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 4))
        Segmented(count, self.multiplier, (("1", "×1"), ("5", "×5")),
                  parent_bg=SURFACE).pack()

        for widget in (self.body, title):
            widget.bind("<Button-1>", lambda _event: on_toggle(self.name))
        self.active.trace_add("write", lambda *_: self._refresh())

    def _field(self, parent: tk.Misc, caption: str, variable: tk.StringVar,
               width: int) -> tk.Frame:
        cell = tk.Frame(parent, bg=SURFACE)
        tk.Label(cell, text=caption, bg=SURFACE, fg=MUTED,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 4))
        entry = ttk.Entry(cell, textvariable=variable, width=width, style="Dark.TEntry")
        entry.pack()
        self._entries.append(entry)
        return cell

    def _refresh(self) -> None:
        running = self.active.get()
        self.recolor(SURFACE_ACTIVE if running else SURFACE,
                     BORDER_ACTIVE if running else BORDER)
        self._dot.recolor(SUCCESS if running else IDLE_DOT)
        for entry in self._entries:
            entry.configure(style="Active.TEntry" if running else "Dark.TEntry")

    def reset(self, building: Building) -> None:
        """Restore the card to the values of a freshly loaded configuration."""
        self.active.set(False)
        self.hotkey.set(hotkey_text(building.hotkey))
        self.game_key.set(building.game_key)
        self.multiplier.set(str(building.multiplier))

    def to_building(self) -> Building:
        return Building(self.name, parse_hotkey(self.hotkey.get()),
                        self.game_key.get(), int(self.multiplier.get()))
