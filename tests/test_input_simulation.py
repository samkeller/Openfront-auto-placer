"""Input controller sends a balanced keyboard and mouse action."""

import unittest
from unittest.mock import Mock, patch

from pynput import keyboard

from src.handlers.input_simulator import InputSimulator, key_code


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

    def test_key_code_is_layout_independent(self) -> None:
        """Digits and letters map to their US virtual-key codes, not characters."""
        self.assertEqual(key_code("0").vk, 0x30)
        self.assertEqual(key_code("9").vk, 0x39)
        self.assertEqual(key_code("a").vk, 0x41)
        self.assertEqual(key_code("Z").vk, 0x5A)
        self.assertIsNone(key_code("1").char)

    def test_key_code_rejects_unsupported_keys(self) -> None:
        for key in ("-", "", "f1", "é"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                key_code(key)


if __name__ == "__main__":
    unittest.main()
