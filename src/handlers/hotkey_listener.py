"""Global chord listener with key-repeat suppression."""

import logging
from typing import Callable

from pynput import keyboard

from src.config.loader import Building


def key_name(key: keyboard.Key | keyboard.KeyCode) -> str | None:
    """Normalize left/right modifier keys and printable hotkeys."""
    if isinstance(key, keyboard.KeyCode):
        if key.char and key.char.isprintable():
            return key.char.lower()
        vk = key.vk
        if vk is not None and 0x41 <= vk <= 0x5A:
            return chr(vk).lower()
        return None
    name = key.name.lower()
    for modifier in ("ctrl", "shift", "alt"):
        if name == modifier or name.startswith(modifier + "_"):
            return modifier
    return "esc" if name == "esc" else name


class HotkeyListener:
    """Dispatch a chord once per physical key press; Pause stops placement."""

    def __init__(self, buildings: tuple[Building, ...],
                 toggle: Callable[[Building], None], stop: Callable[[], None]) -> None:
        self.buildings = {building.hotkey: building for building in buildings}
        self.toggle = toggle
        self.stop = stop
        self.pressed: set[str] = set()
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

    def on_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        """Dispatch a newly completed chord or the global kill switch."""
        name = key_name(key)
        if name is None or name in self.pressed:
            return
        self.pressed.add(name)
        try:
            if name == "pause":
                self.stop()
            else:
                building = self.buildings.get(frozenset(self.pressed))
                if building:
                    self.toggle(building)
        except Exception:
            logging.exception("[ERROR] Échec du raccourci")

    def on_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        """Permit a new activation only after a physical release."""
        name = key_name(key)
        if name is not None:
            self.pressed.discard(name)

    def start(self) -> None:
        """Start the global keyboard hook."""
        self.listener.start()

    def close(self) -> None:
        """Remove the hook and wait for the listener thread."""
        self.listener.stop()
        self.listener.join()
