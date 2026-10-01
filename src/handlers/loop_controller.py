"""Single-worker toggle state machine with bounded, interruptible waits."""

import logging
from threading import Condition, Thread
from time import monotonic
from typing import Callable, Protocol

from src.config.loader import Building, Config
from src.handlers.input_simulator import presses_per_placement


class Simulator(Protocol):
    """Input operations used by the action loop."""

    def press_game_key(self, key: str) -> None: ...
    def click(self) -> None: ...


class LoopController:
    """Run at most one placement loop, stopping on toggle or safety limit."""

    def __init__(self, config: Config, simulator: Simulator,
                 game_is_foreground: Callable[[], bool]) -> None:
        self.config = config
        self.simulator = simulator
        self.game_is_foreground = game_is_foreground
        self.condition = Condition()
        self.active: Building | None = None
        self.count = 0
        self.last_click = 0.0
        self.closed = False
        self.worker = Thread(target=self._run, name="placement-worker", daemon=True)
        self.worker.start()

    def toggle(self, building: Building) -> None:
        """Toggle a building on/off or switch the active building."""
        with self.condition:
            if self.closed:
                return
            if self.active == building:
                self.active = None
                logging.info("[STOP] Auto-placement DÉSACTIVÉ")
            else:
                self.active = building
                self.count = 0
                logging.info("[START] Auto-placement ACTIVÉ pour %s (x%s)",
                             building.name, building.multiplier)
                if presses_per_placement(building) == 2:
                    logging.info("[INFO] x5 : le jeu ne multiplie que les "
                                 "améliorations et les bombes A ; visez une "
                                 "structure existante à améliorer")
            self.condition.notify_all()

    def stop(self) -> None:
        """Stop placing without terminating the listener."""
        with self.condition:
            if self.active:
                self.active = None
                logging.info("[STOP] Auto-placement DÉSACTIVÉ")
            self.condition.notify_all()

    def close(self) -> None:
        """Signal the worker and wait for it to release its resources."""
        with self.condition:
            self.closed = True
            self.active = None
            self.condition.notify_all()
        self.worker.join()

    def _run(self) -> None:
        missing_game = False
        while True:
            with self.condition:
                while not self.closed and self.active is None:
                    self.condition.wait()
                if self.closed:
                    return
                building = self.active
            try:
                foreground = self.game_is_foreground()
            except Exception:
                logging.exception("[ERROR] Impossible de détecter OpenFront.exe")
                foreground = False
            if not foreground:
                if not missing_game:
                    logging.warning("[ERROR] Impossible de détecter OpenFront.exe au premier plan")
                    missing_game = True
                with self.condition:
                    self.condition.wait(timeout=0.1)
                continue
            missing_game = False
            try:
                with self.condition:
                    if self.closed or self.active != building:
                        continue
                    remaining = self.config.click_delay_ms / 1000 - (monotonic() - self.last_click)
                    if remaining > 0:
                        self.condition.wait(timeout=remaining)
                        continue
                    if not self.game_is_foreground():
                        continue
                    # The game clears its own selection after every placement,
                    # so the first press always selects and the second always
                    # arms x5. Nothing else may be sent in between: a key that
                    # drops the selection also discards the click the game is
                    # still holding back while it validates the preview.
                    double = presses_per_placement(building) == 2
                    self.simulator.press_game_key(building.game_key)
                    logging.debug("[SEND] Touche %s (1/%s)", building.game_key,
                                  2 if double else 1)
                    self.condition.wait(timeout=self.config.double_press_delay_ms / 1000)
                if double:
                    with self.condition:
                        if self.closed or self.active != building:
                            continue
                        if not self.game_is_foreground():
                            continue
                        self.simulator.press_game_key(building.game_key)
                        logging.debug("[SEND] Touche %s (2/2, arme le x5)",
                                      building.game_key)
                        self.condition.wait(timeout=self.config.double_press_delay_ms / 1000)
                with self.condition:
                    if self.closed or self.active != building:
                        continue
                    if not self.game_is_foreground():
                        continue
                    self.simulator.click()
                    self.last_click = monotonic()
                    self.count += 1
                    logging.debug("[SEND] Clic gauche (placement %s)", self.count)
                    limit = self.config.max_iterations_per_session
                    if limit and self.count >= limit:
                        logging.warning("[WARN] Limite max iterations (%s/%s) : arrêt",
                                        self.count, limit)
                        self.active = None
                    elif limit and self.count == limit - min(100, limit // 10):
                        logging.warning("[WARN] Approche limite max iterations (%s/%s)",
                                        self.count, limit)
                    self.condition.wait(timeout=self.config.click_delay_ms / 1000)
            except Exception:
                logging.exception("[ERROR] Échec de la simulation d'entrée")
                self.stop()
