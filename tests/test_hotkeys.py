"""Hotkey dispatch without a global keyboard hook."""

import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

from src.config.loader import load_config
from tests.test_config import TEMPLATE


class HotkeyTests(unittest.TestCase):
    @patch("src.handlers.hotkey_listener.keyboard.Listener")
    def test_toggle_once_per_press_and_pause(self, listener_class: Mock) -> None:
        from src.handlers.hotkey_listener import HotkeyListener

        toggle, stop = Mock(), Mock()
        hotkeys = HotkeyListener(load_config(TEMPLATE).buildings, toggle, stop)
        f1 = SimpleNamespace(name="f1")
        pause = SimpleNamespace(name="pause")
        hotkeys.on_press(f1)
        hotkeys.on_press(f1)
        toggle.assert_called_once()
        hotkeys.on_release(f1)
        hotkeys.on_press(f1)
        self.assertEqual(toggle.call_count, 2)
        hotkeys.on_press(pause)
        stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
