"""Emit keyboard and mouse events using pynput's Windows input backend."""

from pynput import keyboard, mouse

from src.config.loader import Building


def presses_per_placement(building: Building) -> int:
    """Return the number of selection-key presses for a placement."""
    return 2 if building.stackable and building.target > 5 else 1


class InputSimulator:
    """Send input to the foreground application without moving the pointer."""

    def __init__(self) -> None:
        self.keyboard = keyboard.Controller()
        self.mouse = mouse.Controller()

    def press_game_key(self, key: str) -> None:
        """Press and release the configured in-game selection key."""
        self.keyboard.press(key)
        self.keyboard.release(key)

    def click(self) -> None:
        """Click at the current pointer position."""
        self.mouse.press(mouse.Button.left)
        self.mouse.release(mouse.Button.left)
