"""Locate the optional visual assets shipped with the application."""

from pathlib import Path
from io import BytesIO
import sys
import tkinter as tk
from PIL import Image
import cairosvg


ASSET_NAMES = {
    "city": "CityIconWhite.svg",
    "factory": "FactoryIconWhite.svg",
    "port": "PortIcon.svg",
    "defense_post": "ShieldIconWhite.svg",
    "missile_silo": "MissileSiloIconWhite.svg",
    "sam_launcher": "SamLauncherIconWhite.svg",
    "atom_bomb": "NukeIconWhite.svg",
    "warship": "BattleshipIconWhite.svg",
    "hydrogen_bomb": "MushroomCloudIconWhite.svg",
    "mirv": "MIRVIcon.svg",
}


def assets_directory() -> Path:
    """Return the bundled assets directory for source and frozen runs."""
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return root / "assets"


def icon_path(building: str) -> Path | None:
    """Return a building's supplied SVG path, if it is present."""
    name = ASSET_NAMES.get(building)
    if name is None:
        return None
    path = assets_directory() / name
    return path if path.exists() else None


def load_logo(master: tk.Misc) -> tk.PhotoImage | None:
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
    scale = max(image.width() // 96, 1)
    return image.subsample(scale, scale)


def load_icon(master: tk.Misc, building: str) -> tk.PhotoImage | None:
    """Rasterize a supplied SVG for Tkinter without modifying the source asset."""
    path = icon_path(building)
    if path is None:
        return None
    try:
        data = cairosvg.svg2png(url=str(path), output_width=32, output_height=32)
        return tk.PhotoImage(master=master, data=data)
    except (OSError, ValueError, tk.TclError):
        return None
