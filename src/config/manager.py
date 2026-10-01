"""Persistent, validated configuration management for the GUI."""

from __future__ import annotations

from pathlib import Path
import os
import shutil
import tempfile

from src.config.loader import BUILDINGS, Building, Config, load_config, parse_hotkey


def format_hotkey(keys: frozenset[str]) -> str:
    """Return a stable, user-facing representation of a hotkey chord."""
    order = {"ctrl": 0, "shift": 1, "alt": 2}
    return "+".join(part.title() if part.startswith("f") else part.capitalize()
                    for part in sorted(keys, key=lambda part: (order.get(part, 3), part)))


def serialize_config(config: Config) -> str:
    """Serialize a validated runtime configuration without extra dependencies."""
    lines = [
        "[general]",
        f"click_delay_ms = {config.click_delay_ms}",
        f"double_press_delay_ms = {config.double_press_delay_ms}",
        f"max_iterations_per_session = {config.max_iterations_per_session}",
        f'log_level = "{config.log_level}"',
        "",
        "[shortcuts]",
    ]
    by_name = {building.name: building for building in config.buildings}
    for name in BUILDINGS:
        building = by_name[name]
        lines.append(
            f'{name} = {{ hotkey = "{format_hotkey(building.hotkey)}", '
            f'game_key = "{building.game_key}", multiplier = {building.multiplier} }}'
        )
    return "\n".join(lines) + "\n"


class ConfigManager:
    """Load, validate, atomically save, and reset the local configuration."""

    def __init__(self, path: Path, template: Path | None = None) -> None:
        self.path = path
        self.template = template

    def load(self) -> Config:
        return load_config(self.path)

    def validate(self, config: Config) -> Config:
        """Validate a candidate through the canonical loader."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            prefix=".openfront-config-", suffix=".toml", dir=self.path.parent
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(serialize_config(config))
            return load_config(Path(temporary))
        finally:
            Path(temporary).unlink(missing_ok=True)

    def save(self, config: Config) -> Config:
        """Validate and atomically replace config.toml."""
        validated = self.validate(config)
        descriptor, temporary = tempfile.mkstemp(
            prefix=".config-", suffix=".toml", dir=self.path.parent
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(serialize_config(validated))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            Path(temporary).unlink(missing_ok=True)
        return validated

    def reset(self) -> Config:
        """Restore the distributed template and return its validated contents."""
        template = self.template
        if template is None:
            import sys
            template = (
                Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
                / "config.toml.default"
            )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f".{self.path.name}.reset")
        try:
            shutil.copyfile(template, temporary)
            restored = load_config(temporary)
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)
        return restored


def make_config(general: dict[str, str], shortcuts: dict[str, dict[str, str]]) -> Config:
    """Convert editable GUI values to a candidate configuration."""
    try:
        buildings = tuple(
            Building(
                name,
                parse_hotkey(shortcuts[name]["hotkey"]),
                shortcuts[name]["game_key"].lower(),
                int(shortcuts[name]["multiplier"]),
            )
            for name in BUILDINGS
        )
        return Config(
            int(general["click_delay_ms"]),
            int(general["double_press_delay_ms"]),
            int(general["max_iterations_per_session"]),
            general["log_level"],
            buildings,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Tous les champs doivent contenir des valeurs valides.") from exc
