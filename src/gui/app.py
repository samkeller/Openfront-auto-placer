"""Main window wiring the configuration, hotkeys and placement loop together."""

from dataclasses import replace
import logging
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import messagebox, ttk
from time import monotonic

from src.config.loader import BUILDINGS, Config, Building, load_config, save_config
from src.game_detector import GameDetector
from src.gui.building_card import BuildingCard
from src.gui.labels import BUILDING_LABELS
from src.gui.theme import (
    ACCENT, ACCENT_HOVER, BG, BORDER, FONT, GHOST, GHOST_HOVER, IDLE_DOT, MUTED,
    SUCCESS, SURFACE, TEXT, apply_theme,
)
from src.gui.widgets import Card, Dot, FlatButton, Segmented
from src.handlers.hotkey_listener import HotkeyListener
from src.handlers.input_simulator import InputSimulator
from src.handlers.loop_controller import LoopController
from src.utils.assets import load_icon, load_logo


NUMERIC_FIELDS = (
    ("click_delay_ms", "Click delay (ms)"),
    ("double_press_delay_ms", "Double press delay (ms)"),
    ("max_iterations_per_session", "Session limit (0 = unlimited)"),
)
LOG_LEVELS = tuple((level, level) for level in ("DEBUG", "INFO", "WARNING", "ERROR"))


class OpenFrontApp(tk.Tk):
    """Single-window editor and controller for the existing placement logic."""

    def __init__(self, config_path: Path, detector: GameDetector | None = None) -> None:
        super().__init__()
        self.title("OpenFront Auto-Placer")
        self.minsize(900, 720)
        self.config_path = config_path
        self.detector = detector or GameDetector()
        self.settings = load_config(config_path)
        self.controller = LoopController(self.settings, InputSimulator(), self.detector.is_foreground)
        self.listener = HotkeyListener(
            self.settings.buildings, self._on_hotkey, self._stop_from_hotkey
        )
        self.listener.start()
        apply_theme(self)
        self._logo = load_logo(self)
        self._icons: dict[str, tk.PhotoImage] = {}
        self._cards: dict[str, BuildingCard] = {}
        self._general_vars: dict[str, tk.StringVar] = {}
        self._status_until = 0.0
        self._build_widgets()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(400, self._refresh_status)

    def _build_widgets(self) -> None:
        container = tk.Frame(self, bg=BG, padx=22, pady=18)
        container.pack(fill="both", expand=True)
        self._build_header(container)
        self._build_buildings(container)
        self._build_settings(container)
        self._build_actions(container)

    def _build_header(self, parent: tk.Misc) -> None:
        header = tk.Frame(parent, bg=BG)
        header.pack(fill="x")
        identity = tk.Frame(header, bg=BG)
        identity.pack(side="left")
        if self._logo is not None:
            tk.Label(identity, image=self._logo, bg=BG).pack(side="left", padx=(0, 14))
        titles = tk.Frame(identity, bg=BG)
        titles.pack(side="left")
        tk.Label(titles, text="OpenFront Auto-Placer", bg=BG, fg=TEXT,
                 font=(FONT, 17, "bold")).pack(anchor="w")
        tk.Label(titles, text="Assign a hotkey, then place buildings automatically",
                 bg=BG, fg=MUTED, font=(FONT, 10)).pack(anchor="w", pady=(2, 0))

        pill = Card(header, BG, radius=16, padding=10)
        pill.pack(side="right", anchor="n")
        self._status_dot = Dot(pill.body, SURFACE, IDLE_DOT)
        self._status_dot.pack(side="left", padx=(2, 8))
        self.status = tk.Label(pill.body, text="Ready", bg=SURFACE, fg=MUTED,
                               font=(FONT, 10, "bold"))
        self.status.pack(side="left", padx=(0, 4))

    def _build_buildings(self, parent: tk.Misc) -> None:
        self._section(parent, "BUILDINGS")
        grid = tk.Frame(parent, bg=BG)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1), weight=1, uniform="cards")
        for index, building in enumerate(self.settings.buildings):
            icon = load_icon(self, building.name)
            if icon is not None:
                self._icons[building.name] = icon
            card = BuildingCard(grid, building, self._toggle, icon)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", pady=4,
                      padx=(0, 5) if index % 2 == 0 else (5, 0))
            self._cards[building.name] = card

    def _build_settings(self, parent: tk.Misc) -> None:
        self._section(parent, "GENERAL SETTINGS")
        settings = Card(parent, BG, padding=14)
        settings.pack(fill="x")
        for column, (name, label) in enumerate(NUMERIC_FIELDS):
            settings.body.columnconfigure(column, weight=1, uniform="settings")
            variable = tk.StringVar(value=str(getattr(self.settings, name)))
            self._general_vars[name] = variable
            cell = tk.Frame(settings.body, bg=SURFACE)
            cell.grid(row=0, column=column, sticky="ew",
                      padx=(0, 16) if column < len(NUMERIC_FIELDS) - 1 else 0)
            tk.Label(cell, text=label.upper(), bg=SURFACE, fg=MUTED,
                     font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 5))
            ttk.Entry(cell, textvariable=variable, style="Dark.TEntry").pack(fill="x")

        level = tk.StringVar(value=self.settings.log_level)
        self._general_vars["log_level"] = level
        cell = tk.Frame(settings.body, bg=SURFACE)
        cell.grid(row=1, column=0, columnspan=len(NUMERIC_FIELDS), sticky="w", pady=(14, 0))
        tk.Label(cell, text="CONSOLE LOG LEVEL", bg=SURFACE, fg=MUTED,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 5))
        Segmented(cell, level, LOG_LEVELS, parent_bg=SURFACE).pack(anchor="w")

    def _build_actions(self, parent: tk.Misc) -> None:
        actions = tk.Frame(parent, bg=BG)
        actions.pack(fill="x", pady=(16, 0))
        FlatButton(actions, "Save", self._save, parent_bg=BG, fill=ACCENT,
                   hover=ACCENT_HOVER, fg="#ffffff").pack(side="left")
        FlatButton(actions, "Apply", self._apply, parent_bg=BG, fill=GHOST,
                   hover=GHOST_HOVER, fg=TEXT).pack(side="left", padx=10)
        FlatButton(actions, "Reset", self._reset, parent_bg=BG, fill=BG,
                   hover=GHOST, fg=MUTED, outline=BORDER).pack(side="left")
        FlatButton(actions, "Launch game", self._launch, parent_bg=BG, fill=BG,
                   hover=GHOST, fg=ACCENT, outline=ACCENT).pack(side="right")

    @staticmethod
    def _section(parent: tk.Misc, title: str) -> None:
        tk.Label(parent, text=title, bg=BG, fg=MUTED,
                 font=(FONT, 9, "bold")).pack(anchor="w", pady=(18, 7))

    def _toggle(self, name: str) -> None:
        building = next(item for item in self.settings.buildings if item.name == name)
        self._apply_hotkey(building)

    def _on_hotkey(self, building: Building) -> None:
        """Queue global-hook work on Tk's event loop."""
        self.after(0, self._apply_hotkey, building)

    def _apply_hotkey(self, building: Building) -> None:
        self.controller.toggle(building)
        for card in self._cards.values():
            card.active.set(False)
        active = self.controller.active
        if active:
            self._cards[active.name].active.set(True)
            self._set_status(f"{BUILDING_LABELS[active.name]} enabled")
        else:
            self._set_status("Auto-placement stopped")

    def _stop_from_hotkey(self) -> None:
        self.after(0, self._stop_ui)

    def _stop_ui(self) -> None:
        self.controller.stop()
        for card in self._cards.values():
            card.active.set(False)
        self._set_status("Auto-placement stopped")

    def _read_config(self) -> Config:
        try:
            general: dict[str, object] = {
                name: int(variable.get()) for name, variable in self._general_vars.items()
                if name != "log_level"
            }
            general["log_level"] = self._general_vars["log_level"].get()
            buildings = tuple(self._cards[name].to_building() for name in BUILDINGS)
            return replace(self.settings, **general, buildings=buildings)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid configuration value: {exc}") from exc

    def _apply(self, persist: bool = False) -> None:
        try:
            config = self._read_config()
            # Validate every cross-field rule using the same loader as the CLI.
            with tempfile.TemporaryDirectory() as directory:
                candidate = Path(directory) / "config.toml"
                save_config(candidate, config)
                validated = load_config(candidate)
            if persist:
                save_config(self.config_path, validated)
            self.settings = validated
            self._sync_vars()
            self.listener.close()
            self.controller.close()
            self.controller = LoopController(
                self.settings, InputSimulator(), self.detector.is_foreground
            )
            self.listener = HotkeyListener(
                self.settings.buildings, self._on_hotkey, self._stop_from_hotkey
            )
            self.listener.start()
            self._set_status("Settings applied")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Configuration error", str(exc))

    def _save(self) -> None:
        self._apply(persist=True)

    def _reset(self) -> None:
        try:
            self.settings = load_config(self.config_path)
            self._sync_vars()
            self._set_status("Settings reloaded")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Configuration error", str(exc))

    def _sync_vars(self) -> None:
        for name, variable in self._general_vars.items():
            variable.set(str(getattr(self.settings, name)))
        for building in self.settings.buildings:
            self._cards[building.name].reset(building)

    def _refresh_status(self) -> None:
        if not self.winfo_exists():
            return
        if monotonic() < self._status_until:
            self.after(2000, self._refresh_status)
            return
        active = self.controller.active
        detected = self.detector.is_running()
        if active:
            self.status.configure(
                text=f"{BUILDING_LABELS[active.name]} enabled · "
                f"{'game detected' if detected else 'game not detected'}"
            )
        else:
            self.status.configure(text="Game detected" if detected else "Game not detected")
        self.status.configure(fg=TEXT if detected else MUTED)
        self._status_dot.recolor(SUCCESS if detected else IDLE_DOT)
        self.after(2000, self._refresh_status)

    def _launch(self) -> None:
        try:
            self.detector.launch()
            self._set_status("Game launch requested · waiting for OpenFront")
        except OSError as exc:
            messagebox.showerror("Launch game", str(exc))

    def _set_status(self, text: str, duration: float = 3.0) -> None:
        self.status.configure(text=text, fg=TEXT)
        self._status_dot.recolor(ACCENT)
        self._status_until = monotonic() + duration

    def close(self) -> None:
        self.listener.close()
        self.controller.close()
        self.destroy()


def run(config_path: Path) -> None:
    """Run the GUI using the same config location as the CLI."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    app = OpenFrontApp(config_path)
    app.mainloop()
