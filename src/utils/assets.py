"""Locate the optional visual assets shipped with the application."""

from pathlib import Path
from io import BytesIO
import sys
import tkinter as tk
from PIL import Image


ASSET_NAMES = {
    "city": "CityIconWhite.png",
    "factory": "FactoryIconWhite.png",
    "port": "PortIcon.png",
    "defense_post": "ShieldIconWhite.png",
    "missile_silo": "MissileSiloIconWhite.png",
    "sam_launcher": "SamLauncherIconWhite.png",
    "atom_bomb": "NukeIconWhite.png",
    "warship": "BattleshipIconWhite.png",
    "hydrogen_bomb": "MushroomCloudIconWhite.png",
    "mirv": "MIRVIcon.png",
}


def assets_directory() -> Path:
    """Return the bundled assets directory for source and frozen runs."""
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return root / "assets"


def icon_path(building: str) -> Path | None:
    """Return a building's pre-rendered icon path, if it is present."""
    name = ASSET_NAMES.get(building)
    if name is None:
        return None
    path = assets_directory() / "icons" / name
    return path if path.exists() else None


def load_logo(master: tk.Misc, size: int = 56) -> tk.PhotoImage | None:
    """Load the bundled logo, keeping the GUI usable if it is unavailable."""
    path = assets_directory() / "Logo.jpg"
    if not path.exists():
        return None
    try:
        with Image.open(path) as source:
            stream = BytesIO()
            source.convert("RGBA").save(stream, format="PNG")
        image = tk.PhotoImage(master=master, data=stream.getvalue())
    except (OSError, tk.TclError):
        return None
    scale = max(image.width() // size, 1)
    return image.subsample(scale, scale)


def load_icon(master: tk.Misc, building: str) -> tk.PhotoImage | None:
    """Load a building icon, keeping the GUI usable if it is unavailable."""
    path = icon_path(building)
    if path is None:
        return None
    try:
        return tk.PhotoImage(master=master, file=str(path))
    except tk.TclError:
        return None
