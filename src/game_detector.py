"""Game process detection and launching for the graphical interface."""

import os
import shutil
import subprocess

from src.utils.window_detector import game_is_foreground


class GameDetector:
    """Small adapter keeping process concerns outside the UI."""

    def is_foreground(self) -> bool:
        return game_is_foreground()

    def is_running(self) -> bool:
        """Return whether OpenFront.exe exists, regardless of window focus."""
        if os.name != "nt":
            return False
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq OpenFront.exe", "/NH"],
            capture_output=True, text=True, check=False, creationflags=flags,
        )
        return "OpenFront.exe" in result.stdout

    def launch(self) -> None:
        """Launch through Steam, with a direct-install fallback."""
        if os.name != "nt":
            raise OSError("OpenFront can only be launched from Windows")
        steam = shutil.which("steam.exe")
        if steam:
            os.startfile("steam://rungameid/3560670")  # type: ignore[attr-defined]
            return
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
