"""Unit tests for input sequencing and state transitions."""

from dataclasses import replace
from threading import Event
import time
import unittest

from src.config.loader import load_config
from src.handlers.loop_controller import LoopController
from tests.test_config import TEMPLATE


class FakeInput:
    def __init__(self) -> None:
        self.events: list[str] = []
        self.clicked = Event()

    def press_game_key(self, key: str) -> None:
        self.events.append(f"key:{key}")

    def click(self) -> None:
        self.events.append("click")
        self.clicked.set()


class ControllerTests(unittest.TestCase):
    def test_toggle_and_stop(self) -> None:
        config = replace(load_config(TEMPLATE), double_press_delay_ms=10)
        simulator = FakeInput()
        controller = LoopController(config, simulator, lambda: True)
        try:
            city = config.buildings[0]
            controller.toggle(city)
            self.assertTrue(simulator.clicked.wait(1))
            controller.toggle(city)
            self.assertIsNone(controller.active)
            count = len(simulator.events)
            time.sleep(0.15)
            self.assertEqual(len(simulator.events), count)
            controller.toggle(city)
            self.assertTrue(controller.active)
            controller.stop()
            self.assertIsNone(controller.active)
        finally:
            controller.close()

    def test_double_press_sends_only_the_building_key(self) -> None:
        """Nothing may be sent between the paired presses and the click."""
        config = load_config(TEMPLATE)
        config = replace(config, max_iterations_per_session=1,
                         double_press_delay_ms=10,
                         buildings=(replace(config.buildings[0], multiplier=5),))
        simulator = FakeInput()
        controller = LoopController(config, simulator, lambda: True)
        try:
            controller.toggle(config.buildings[0])
            self.assertTrue(simulator.clicked.wait(1))
            self.assertEqual(simulator.events, ["key:1", "key:1", "click"])
            self.assertIsNone(controller.active)
        finally:
            controller.close()

    def test_single_press_sends_one_key(self) -> None:
        config = load_config(TEMPLATE)
        config = replace(config, max_iterations_per_session=1,
                         double_press_delay_ms=10,
                         buildings=(replace(config.buildings[0], multiplier=1),))
        simulator = FakeInput()
        controller = LoopController(config, simulator, lambda: True)
        try:
            controller.toggle(config.buildings[0])
            self.assertTrue(simulator.clicked.wait(1))
            self.assertEqual(simulator.events, ["key:1", "click"])
        finally:
            controller.close()

    def test_no_input_when_game_is_not_foreground(self) -> None:
        config = load_config(TEMPLATE)
        simulator = FakeInput()
        controller = LoopController(config, simulator, lambda: False)
        try:
            controller.toggle(config.buildings[0])
            self.assertFalse(simulator.clicked.wait(0.2))
            self.assertEqual(simulator.events, [])
        finally:
            controller.close()

    def test_input_error_does_not_stop_placement(self) -> None:
        config = replace(load_config(TEMPLATE), click_delay_ms=10)

        class FailOnceInput(FakeInput):
            failed = False

            def press_game_key(self, key: str) -> None:
                if not self.failed:
                    self.failed = True
                    raise RuntimeError("transient input error")
                super().press_game_key(key)

        simulator = FailOnceInput()
        controller = LoopController(config, simulator, lambda: True)
        try:
            building = config.buildings[0]
            controller.toggle(building)
            self.assertTrue(simulator.clicked.wait(1))
            self.assertIs(controller.active, building)
            self.assertEqual(simulator.events, ["key:1", "click"])
        finally:
            controller.close()


if __name__ == "__main__":
    unittest.main()
