"""Console entry point for the Windows OpenFront auto-placer."""

import logging
import os
from pathlib import Path
import sys
from threading import Event

from src.config.loader import load_config
from src.handlers.hotkey_listener import HotkeyListener
from src.handlers.input_simulator import InputSimulator
from src.handlers.loop_controller import LoopController
from src.utils.logger import setup_logging
from src.utils.window_detector import game_is_foreground


def main() -> int:
    """Start the listener and keep the process alive until Ctrl+C."""
    if os.name != "nt":
        print("OpenFront auto-placer requires Windows.", file=sys.stderr)
        return 1
    directory = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
    try:
        config = load_config(directory / "config.toml")
    except (OSError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    setup_logging(config.log_level)
    controller = LoopController(config, InputSimulator(), game_is_foreground)
    listener = HotkeyListener(config.buildings, controller.toggle, controller.stop)
    try:
        listener.start()
        logging.info("Prêt. Pause/Break = arrêt immédiat; Ctrl+C = quitter.")
        while listener.listener.is_alive():
            Event().wait(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        listener.close()
        controller.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
