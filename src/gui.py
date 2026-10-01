"""Lightweight Tkinter interface for configuring and running the auto-placer."""

from dataclasses import replace
import logging
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import messagebox, ttk
from time import monotonic

from src.config.loader import BUILDINGS, Config, Building, load_config, parse_hotkey, save_config
from src.game_detector import GameDetector
from src.handlers.hotkey_listener import HotkeyListener
from src.handlers.input_simulator import InputSimulator
from src.handlers.loop_controller import LoopController
from src.utils.assets import load_icon, load_logo


BUILDING_LABELS = {
    "city": "City",
    "factory": "Factory",
    "port": "Port",
    "defense_post": "Defense post",
    "missile_silo": "Missile silo",
    "sam_launcher": "S.A.M. launcher",
    "atom_bomb": "Atomic bomb",
    "warship": "Warship",
    "hydrogen_bomb": "Hydrogen bomb",
    "mirv": "M.I.R.V.",
}


class OpenFrontApp(tk.Tk):
    """Single-window editor and controller for the existing placement logic."""

    def __init__(self, config_path: Path, detector: GameDetector | None = None) -> None:
        super().__init__()
        self.title("OpenFront Auto-Placer")
        self.minsize(760, 560)
        self.config_path = config_path
        self.detector = detector or GameDetector()
        self.settings = load_config(config_path)
        self.controller = LoopController(self.settings, InputSimulator(), self.detector.is_foreground)
        self.listener = HotkeyListener(
            self.settings.buildings, self._on_hotkey, self._stop_from_hotkey
        )
        self.listener.start()
        self._logo = load_logo(self)
        self._icons: dict[str, tk.PhotoImage] = {}
        self._status_until = 0.0
        self._building_vars: dict[str, tuple[tk.BooleanVar, tk.StringVar, tk.StringVar, tk.StringVar]] = {}
        self._general_vars: dict[str, tk.StringVar] = {}
        self._build_widgets()
        self._bind_theme()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(400, self._refresh_status)

    def _build_widgets(self) -> None:
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)
        heading = ttk.Frame(container)
        heading.pack(anchor="w")
        if self._logo is not None:
            ttk.Label(heading, image=self._logo).pack(side="left", padx=(0, 8))
        ttk.Label(
            heading, text="OpenFront Auto-Placer", font=("TkDefaultFont", 16, "bold")
        ).pack(side="left")
        self.status = ttk.Label(container, text="Ready", foreground="#555")
        self.status.pack(anchor="w", pady=(2, 12))

        buildings = ttk.LabelFrame(container, text="Buildings", padding=8)
        buildings.pack(fill="both", expand=True)
        for index, building in enumerate(self.settings.buildings):
            row = ttk.Frame(buildings)
            row.grid(row=index // 2, column=index % 2, sticky="ew", padx=6, pady=4)
            buildings.columnconfigure(index % 2, weight=1)
            active, hotkey, game_key, multiplier = (
                tk.BooleanVar(value=False),
                tk.StringVar(value=self._hotkey_text(building.hotkey)),
                tk.StringVar(value=building.game_key),
                tk.StringVar(value=str(building.multiplier)),
            )
            self._building_vars[building.name] = (active, hotkey, game_key, multiplier)
            icon = load_icon(self, building.name)
            if icon is not None:
                self._icons[building.name] = icon
            ttk.Checkbutton(
                row, text=BUILDING_LABELS[building.name],
                image=icon if icon is not None else "",
                compound="left", variable=active,
                command=lambda name=building.name: self._toggle(name),
            ).grid(row=0, column=0, sticky="w")
            ttk.Label(row, text="Hotkey").grid(row=1, column=0, sticky="e")
            ttk.Entry(row, textvariable=hotkey, width=10).grid(row=1, column=1, padx=3)
            ttk.Label(row, text="Game key").grid(row=1, column=2, sticky="e")
            ttk.Entry(row, textvariable=game_key, width=4).grid(row=1, column=3, padx=3)
            ttk.Label(row, text="×").grid(row=1, column=4, sticky="e")
            ttk.Combobox(
                row, textvariable=multiplier, values=("1", "5"), width=3, state="readonly"
            ).grid(row=1, column=5, padx=3)

        settings = ttk.LabelFrame(container, text="General settings", padding=8)
        settings.pack(fill="x", pady=(12, 8))
        for index, (name, label) in enumerate((
            ("click_delay_ms", "Click delay (ms)"),
            ("double_press_delay_ms", "Double press delay (ms)"),
            ("max_iterations_per_session", "Session limit (0 = unlimited)"),
            ("log_level", "Console log level"),
        )):
            variable = tk.StringVar(value=str(getattr(self.settings, name)))
            self._general_vars[name] = variable
            ttk.Label(settings, text=label).grid(row=0, column=index * 2, sticky="w", padx=(0, 4))
            if name == "log_level":
                ttk.Combobox(
                    settings, textvariable=variable,
                    values=("DEBUG", "INFO", "WARNING", "ERROR"), state="readonly", width=9,
                ).grid(row=0, column=index * 2 + 1, padx=(0, 8))
            else:
                ttk.Entry(settings, textvariable=variable, width=9).grid(
                    row=0, column=index * 2 + 1, padx=(0, 8)
                )

        actions = ttk.Frame(container)
        actions.pack(fill="x")
        ttk.Button(actions, text="Apply", command=self._apply).pack(side="left")
        ttk.Button(actions, text="Save", command=self._save).pack(side="left", padx=6)
        ttk.Button(actions, text="Reset", command=self._reset).pack(side="left")
        ttk.Button(actions, text="Launch game", command=self._launch).pack(side="right")

    @staticmethod
    def _hotkey_text(hotkey: frozenset[str]) -> str:
        return "+".join(sorted(hotkey, key=lambda item: (item not in {"ctrl", "shift", "alt"}, item)))

    def _toggle(self, name: str) -> None:
        building = next(item for item in self.settings.buildings if item.name == name)
        self._apply_hotkey(building)

    def _on_hotkey(self, building: Building) -> None:
        """Queue global-hook work on Tk's event loop."""
        self.after(0, self._apply_hotkey, building)

    def _apply_hotkey(self, building: Building) -> None:
        self.controller.toggle(building)
        for variables in self._building_vars.values():
            variables[0].set(False)
        active = self.controller.active
        if active:
            self._building_vars[active.name][0].set(True)
            self._set_status(f"{BUILDING_LABELS[active.name]} enabled")
        else:
            self._set_status("Auto-placement stopped")

    def _stop_from_hotkey(self) -> None:
        self.after(0, self._stop_ui)

    def _stop_ui(self) -> None:
        self.controller.stop()
        for variables in self._building_vars.values():
            variables[0].set(False)
        self._set_status("Auto-placement stopped")

    def _read_config(self) -> Config:
        try:
            general = {
                name: int(variable.get()) for name, variable in self._general_vars.items()
                if name != "log_level"
            }
            general["log_level"] = self._general_vars["log_level"].get()
            buildings = []
            for name in BUILDINGS:
                _, hotkey, game_key, multiplier = self._building_vars[name]
                buildings.append(
                    Building(name, parse_hotkey(hotkey.get()), game_key.get(), int(multiplier.get()))
                )
            return replace(self.settings, **general, buildings=tuple(buildings))
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
            active, hotkey, game_key, multiplier = self._building_vars[building.name]
            active.set(False)
            hotkey.set(self._hotkey_text(building.hotkey))
            game_key.set(building.game_key)
            multiplier.set(str(building.multiplier))

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
        self.after(2000, self._refresh_status)

    def _launch(self) -> None:
        try:
            self.detector.launch()
            self._set_status("Game launch requested · waiting for OpenFront")
        except OSError as exc:
            messagebox.showerror("Launch game", str(exc))

    def _set_status(self, text: str, duration: float = 3.0) -> None:
        self.status.configure(text=text)
        self._status_until = monotonic() + duration

    def _bind_theme(self) -> None:
        """Apply a readable dark theme while retaining native Tk widgets."""
        self.configure(background="#151923")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background="#151923", foreground="#f1f5f9")
        style.configure("TFrame", background="#151923")
        style.configure("TLabelframe", background="#151923", foreground="#94a3b8")
        style.configure("TLabelframe.Label", background="#151923", foreground="#94a3b8")
        style.configure("TLabel", background="#151923", foreground="#e2e8f0")
        style.configure("TCheckbutton", background="#202633", foreground="#f8fafc",
                        padding=8)
        style.map("TCheckbutton", background=[("active", "#334155")])
        style.configure("TButton", background="#334155", foreground="#f8fafc", padding=7)
        style.configure("TEntry", fieldbackground="#202633", foreground="#f8fafc")
        style.configure("TCombobox", fieldbackground="#202633", foreground="#f8fafc")

    def close(self) -> None:
        self.listener.close()
        self.controller.close()
        self.destroy()


def run(config_path: Path) -> None:
    """Run the GUI using the same config location as the CLI."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    app = OpenFrontApp(config_path)
    app.mainloop()
