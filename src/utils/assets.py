"""Locate the optional visual assets shipped with the application."""

from pathlib import Path
import sys
import tkinter as tk


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
    path = assets_directory() / ASSET_NAMES[building]
    return path if path.exists() else None


def load_logo(master: tk.Misc) -> tk.PhotoImage | None:
    """Load the bundled logo, keeping the GUI usable if it is unavailable."""
    path = assets_directory() / "Logo.png"
    if not path.exists():
        return None
    try:
        image = tk.PhotoImage(master=master, file=path)
    except tk.TclError:
        # The supplied logo may be encoded as JPEG despite its .png name.
        # Tkinter has no JPEG loader, so the rest of the GUI must still start.
        return None
    scale = max(image.width() // 96, 1)
    return image.subsample(scale, scale)
