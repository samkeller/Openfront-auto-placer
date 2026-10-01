"""Configuration parsing and first-run behavior."""

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from src.config.loader import load_config, parse_hotkey
from src.handlers.input_simulator import presses_per_placement


TEMPLATE = Path(__file__).resolve().parents[1] / "config.toml.default"


class ConfigTests(unittest.TestCase):
    def test_creates_persistent_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            config = load_config(path)
            self.assertTrue(path.exists())
            self.assertEqual(len(config.buildings), 10)
            self.assertEqual(config.buildings[-1].hotkey, frozenset(("f10",)))
            path.write_text(path.read_text().replace("click_delay_ms = 100", "click_delay_ms = 150"))
            self.assertEqual(load_config(path).click_delay_ms, 150)
            path.write_text(path.read_text().replace("click_delay_ms = 150", "click_delay_ms = 10"))
            self.assertEqual(load_config(path).click_delay_ms, 10)

    def test_invalid_configuration(self) -> None:
        for before, after in (
            ("click_delay_ms = 100", "click_delay_ms = 1"),
            ("max_iterations_per_session = 5000", "max_iterations_per_session = -1"),
            ('hotkey = "F2"', 'hotkey = "F1"'),
            ('hotkey = "F1"', 'hotkey = "1"'),
            ("multiplier = 1", "multiplier = 2"),
            ('defense_post = { hotkey = "F4", game_key = "4", multiplier = 1 }',
             'defense_post = { hotkey = "F4", game_key = "4", multiplier = 5 }'),
        ):
            with self.subTest(after=after), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "config.toml"
                path.write_text(TEMPLATE.read_text().replace(before, after, 1))
                with self.assertRaises(ValueError):
                    load_config(path)

    def test_bulk_multiplier_accepted_for_bulk_capable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            path.write_text(TEMPLATE.read_text().replace(
                'game_key = "1", multiplier = 5',
                'game_key = "1", multiplier = 1'))
            self.assertEqual(load_config(path).buildings[0].multiplier, 1)

    def test_chords_and_press_count(self) -> None:
        self.assertEqual(parse_hotkey("Ctrl+Shift+V"), frozenset(("ctrl", "shift", "v")))
        with self.assertRaises(ValueError):
            parse_hotkey("Ctrl+Ctrl+V")
        city, *_ = load_config(TEMPLATE).buildings
        self.assertEqual(presses_per_placement(city), 2)
        self.assertEqual(presses_per_placement(replace(city, multiplier=1)), 1)


if __name__ == "__main__":
    unittest.main()
