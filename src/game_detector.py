"""Game process detection and launching for the graphical interface."""

import os
import subprocess

from src.utils.window_detector import game_is_foreground


class GameDetector:
    """Small adapter keeping process concerns outside the UI."""

    def is_foreground(self) -> bool:
        return game_is_foreground()

    def launch(self) -> None:
        """Ask Windows to launch the installed game."""
        if os.name != "nt":
            raise OSError("OpenFront can only be launched from Windows")
        os.startfile("OpenFront.exe")  # type: ignore[attr-defined]

