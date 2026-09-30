"""Input controller sends a balanced keyboard and mouse action."""

import unittest
from unittest.mock import Mock, patch

from src.handlers.input_simulator import InputSimulator


class InputTests(unittest.TestCase):
    @patch("src.handlers.input_simulator.mouse.Controller")
    @patch("src.handlers.input_simulator.keyboard.Controller")
    def test_press_and_click(self, keyboard_controller: Mock, mouse_controller: Mock) -> None:
        simulator = InputSimulator()
        simulator.press_game_key("1")
        simulator.click()
        keyboard_controller.return_value.press.assert_called_once_with("1")
        keyboard_controller.return_value.release.assert_called_once_with("1")
        self.assertEqual(mouse_controller.return_value.press.call_count, 1)
        self.assertEqual(mouse_controller.return_value.release.call_count, 1)


if __name__ == "__main__":
    unittest.main()
