"""Input controller sends a balanced keyboard and mouse action."""

import unittest
from unittest.mock import Mock, patch

from pynput import keyboard

from src.handlers.input_simulator import CANCEL_KEY, InputSimulator, key_code


class InputTests(unittest.TestCase):
    @patch("src.handlers.input_simulator.mouse.Controller")
    @patch("src.handlers.input_simulator.keyboard.Controller")
    def test_press_and_click(self, keyboard_controller: Mock, mouse_controller: Mock) -> None:
        simulator = InputSimulator()
        simulator.press_game_key("1")
        simulator.click()
        code = keyboard.KeyCode.from_vk(0x31)
        keyboard_controller.return_value.press.assert_called_once_with(code)
        keyboard_controller.return_value.release.assert_called_once_with(code)
        self.assertEqual(mouse_controller.return_value.press.call_count, 1)
        self.assertEqual(mouse_controller.return_value.release.call_count, 1)

    @patch("src.handlers.input_simulator.mouse.Controller")
    @patch("src.handlers.input_simulator.keyboard.Controller")
    def test_cancel_selection_taps_escape(self, keyboard_controller: Mock, _: Mock) -> None:
        simulator = InputSimulator()
        simulator.cancel_selection()
        keyboard_controller.return_value.press.assert_called_once_with(CANCEL_KEY)
        keyboard_controller.return_value.release.assert_called_once_with(CANCEL_KEY)

    def test_key_code_is_layout_independent(self) -> None:
        """Digits and letters map to their US virtual-key codes, not characters."""
        self.assertEqual(key_code("0").vk, 0x30)
        self.assertEqual(key_code("9").vk, 0x39)
        self.assertEqual(key_code("a").vk, 0x41)
        self.assertEqual(key_code("Z").vk, 0x5A)
        self.assertIsNone(key_code("1").char)


if __name__ == "__main__":
    unittest.main()
