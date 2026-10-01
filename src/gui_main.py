"""Executable entry point for the OpenFront Auto-Placer GUI."""

from pathlib import Path
import os
import sys

from src.gui import run


def main() -> int:
    if os.name != "nt":
        print("OpenFront auto-placer requires Windows.", file=sys.stderr)
        return 1
    directory = (
        Path(sys.executable).parent
        if getattr(sys, "frozen", False)
        else Path(__file__).resolve().parents[1]
    )
    run(directory / "config.toml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
