"""Game process detection and launching for the graphical interface."""

import os
import subprocess
from time import monotonic

from src.utils.window_detector import game_is_foreground

STEAM_APP_ID = "3560670"


class GameDetector:
    """Small adapter keeping process concerns outside the UI."""

    def __init__(self) -> None:
        self._running_cache = False
        self._running_checked = float("-inf")

    def is_foreground(self) -> bool:
        return game_is_foreground()

    def is_running(self) -> bool:
        """Return whether OpenFront.exe exists, regardless of window focus."""
        if os.name != "nt":
            return False
        now = monotonic()
        if now - self._running_checked < 3:
            return self._running_cache
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq OpenFront.exe", "/NH"],
            capture_output=True, text=True, check=False, creationflags=flags,
        )
        self._running_cache = "OpenFront.exe" in result.stdout
        self._running_checked = now
        return self._running_cache

    def launch(self) -> None:
        """Launch through Steam, with a direct-install fallback."""
        if os.name != "nt":
            raise OSError("OpenFront can only be launched from Windows")
        try:
            os.startfile(f"steam://rungameid/{STEAM_APP_ID}")  # type: ignore[attr-defined]
            return
        except OSError:
            pass
        candidates = (
            os.environ.get("OPENFRONT_EXE", ""),
            r"C:\Program Files (x86)\Steam\steamapps\common\OpenFront\OpenFront.exe",
            r"C:\Program Files\Steam\steamapps\common\OpenFront\OpenFront.exe",
        )
        for candidate in candidates:
            if candidate and os.path.isfile(candidate):
                subprocess.Popen([candidate], close_fds=True)
                return
        raise OSError(
            "Could not start OpenFront. Steam was unavailable and OpenFront.exe "
            "was not found in the default Steam folders. Set OPENFRONT_EXE to "
            "the executable path."
        )
