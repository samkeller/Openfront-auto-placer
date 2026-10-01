"""Load and validate the user-editable TOML configuration."""

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import sys
import tomllib


BUILDINGS = (
    "city", "factory", "port", "defense_post", "missile_silo",
    "sam_launcher", "atom_bomb", "warship", "hydrogen_bomb", "mirv",
)
STACKABLE = frozenset((
    "city", "factory", "port", "missile_silo", "sam_launcher", "atom_bomb",
))
#: The two selection sizes the game itself offers (its x1/x5 toggle).
MULTIPLIERS = frozenset((1, 5))
MODIFIERS = frozenset(("ctrl", "shift", "alt"))
KEYS = frozenset(("pause", "esc", *[f"f{i}" for i in range(1, 13)]))


@dataclass(frozen=True)
class Building:
    """One configured building and its input bindings."""

    name: str
    hotkey: frozenset[str]
    game_key: str
    stackable: bool
    multiplier: int


@dataclass(frozen=True)
class Config:
    """Validated runtime settings."""

    click_delay_ms: int
    double_press_delay_ms: int
    max_iterations_per_session: int
    log_level: str
    buildings: tuple[Building, ...]


def parse_hotkey(value: str) -> frozenset[str]:
    """Normalize a chord to lower-case pynput key names."""
    if not isinstance(value, str):
        raise ValueError("hotkey must be a string")
    parts = [part.strip().lower() for part in value.split("+")]
    if (not parts or len(parts) != len(set(parts))
            or any(part not in MODIFIERS | KEYS | set("abcdefghijklmnopqrstuvwxyz0123456789")
                   for part in parts)
            or sum(part not in MODIFIERS for part in parts) != 1):
        raise ValueError(f"invalid hotkey: {value!r}")
    return frozenset(parts)


def _integer(table: dict, key: str, minimum: int) -> int:
    value = table.get(key)
    if type(value) is not int or value < minimum:
        raise ValueError(f"{key} must be an integer >= {minimum}")
    return value


def load_config(path: Path) -> Config:
    """Create a first-run configuration, then load and validate it."""
    if not path.exists():
        template = (Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
                    / "config.toml.default")
        shutil.copyfile(template, path)
    with path.open("rb") as stream:
        data = tomllib.load(stream)
    general = data.get("general")
    shortcuts = data.get("shortcuts")
    if not isinstance(general, dict) or not isinstance(shortcuts, dict):
        raise ValueError("config needs [general] and [shortcuts] tables")
    delay = _integer(general, "click_delay_ms", 100)
    double_delay = _integer(general, "double_press_delay_ms", 10)
    limit = _integer(general, "max_iterations_per_session", 0)
    level = general.get("log_level")
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise ValueError("log_level must be DEBUG, INFO, WARNING or ERROR")
    if set(shortcuts) != set(BUILDINGS):
        raise ValueError(f"[shortcuts] must contain exactly: {', '.join(BUILDINGS)}")
    seen: set[frozenset[str]] = set()
    buildings = []
    game_keys = set()
    for name in BUILDINGS:
        entry = shortcuts[name]
        if not isinstance(entry, dict):
            raise ValueError(f"{name} must be a TOML table")
        chord = parse_hotkey(entry.get("hotkey"))
        if chord in seen or chord == frozenset(("pause",)):
            raise ValueError(f"duplicate or reserved hotkey for {name}")
        seen.add(chord)
        key = entry.get("game_key")
        if not isinstance(key, str) or not re.fullmatch(r"[a-zA-Z0-9]", key):
            raise ValueError(f"{name}.game_key must be a single letter or digit")
        game_keys.add(key.lower())
        stackable = entry.get("stackable")
        if type(stackable) is not bool or stackable != (name in STACKABLE):
            raise ValueError(f"{name}.stackable must match the building type")
        if "target" in entry:
            raise ValueError(
                f"{name}.target is no longer supported; use multiplier = 1 or 5")
        multiplier = entry.get("multiplier", 1)
        if type(multiplier) is not int or multiplier not in MULTIPLIERS:
            raise ValueError(f"{name}.multiplier must be 1 or 5")
        if multiplier == 5 and not stackable:
            raise ValueError(f"{name} cannot be placed in bulk; multiplier must be 1")
        buildings.append(Building(name, chord, key.lower(), stackable, multiplier))
    if any(key in chord for chord in seen for key in game_keys):
        raise ValueError("a hotkey trigger cannot also be a simulated game key")
    # A x5 placement sends Escape to clear the current selection, which would
    # otherwise fire an Escape hotkey and toggle the tool on every placement.
    if (any(building.multiplier == 5 for building in buildings)
            and any("esc" in chord for chord in seen)):
        raise ValueError("Escape cannot be a hotkey trigger when a building uses "
                         "multiplier = 5")
    return Config(delay, double_delay, limit, level, tuple(buildings))
