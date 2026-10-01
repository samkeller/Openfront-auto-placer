"""Emit keyboard and mouse events using pynput's Windows input backend."""

from time import sleep

from pynput import keyboard, mouse

from src.config.loader import Building

#: Hold durations so the game sees a complete, human-sized press.
KEY_HOLD_SECONDS = 0.03
CLICK_HOLD_SECONDS = 0.03

#: The game's own "cancel the current selection" key.
CANCEL_KEY = keyboard.Key.esc


def presses_per_placement(building: Building) -> int:
    """Return the number of selection-key presses for a placement.

    The game arms its x5 selection on a *second* consecutive press of the
    building key, so a x5 placement needs two presses and a x1 placement one.
    """
    return 2 if building.stackable and building.multiplier == 5 else 1


def key_code(key: str) -> keyboard.KeyCode:
    """Return the virtual-key code of a configured game key.

    pynput resolves a bare character through the active keyboard layout and
    falls back to a Unicode packet when the character needs a modifier, as
    digits do on AZERTY. Such an event carries no scan code, so the game
    receives an unidentified key and ignores it. Addressing the virtual key
    directly keeps the physical digit and letter keys intact on every layout.
    """
    character = key.lower()
    if "0" <= character <= "9":
        return keyboard.KeyCode.from_vk(0x30 + ord(character) - ord("0"))
    return keyboard.KeyCode.from_vk(0x41 + ord(character) - ord("a"))


class InputSimulator:
    """Send input to the foreground application without moving the pointer."""

    def __init__(self) -> None:
        self.keyboard = keyboard.Controller()
        self.mouse = mouse.Controller()

    def _tap(self, code: keyboard.Key | keyboard.KeyCode) -> None:
        self.keyboard.press(code)
        sleep(KEY_HOLD_SECONDS)
        self.keyboard.release(code)

    def press_game_key(self, key: str) -> None:
        """Press and release the configured in-game selection key."""
        self._tap(key_code(key))

    def cancel_selection(self) -> None:
        """Clear any pending building selection with Escape."""
        self._tap(CANCEL_KEY)

    def click(self) -> None:
        """Click at the current pointer position."""
        self.mouse.press(mouse.Button.left)
        sleep(CLICK_HOLD_SECONDS)
        self.mouse.release(mouse.Button.left)
