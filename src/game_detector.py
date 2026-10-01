"""Detect and launch the Windows Steam installation of OpenFront."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess

from src.utils.window_detector import game_is_foreground


def _steam_roots() -> tuple[Path, ...]:
    roots: list[Path] = []
    if os.name == "nt":
        try:
            import winreg
            for hive, key in (
                (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
            ):
                try:
                    with winreg.OpenKey(hive, key) as handle:
                        roots.append(Path(winreg.QueryValueEx(handle, "SteamPath")[0]))
                except OSError:
                    continue
        except ImportError:
            pass
    for variable in ("PROGRAMFILES(X86)", "PROGRAMFILES"):
        if os.environ.get(variable):
            roots.append(Path(os.environ[variable]) / "Steam")
    return tuple(dict.fromkeys(roots))


def find_game_executable() -> Path | None:
    """Locate OpenFront.exe in configured Steam libraries."""
    libraries: list[Path] = []
    for root in _steam_roots():
        libraries.append(root)
        file = root / "steamapps" / "libraryfolders.vdf"
        try:
            text = file.read_text(encoding="utf-8")
        except OSError:
            continue
        libraries.extend(Path(value.replace("\\\\", "\\"))
                         for value in re.findall(r'"path"\s+"([^"]+)"', text))
    for library in dict.fromkeys(libraries):
        common = library / "steamapps" / "common"
        if not common.is_dir():
            continue
        for executable in common.glob("*/OpenFront.exe"):
            if executable.is_file():
                return executable
    return None


def game_is_installed() -> bool:
    return find_game_executable() is not None


def launch_game() -> Path:
    """Launch the discovered executable without invoking a command shell."""
    executable = find_game_executable()
    if executable is None:
        raise FileNotFoundError("OpenFront.exe est introuvable dans les bibliothèques Steam.")
    subprocess.Popen([str(executable)], cwd=executable.parent)
    return executable
