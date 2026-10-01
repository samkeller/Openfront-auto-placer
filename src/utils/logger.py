"""Developer console and user-interface logging."""

import logging
from queue import Queue


UI_LOGGER = "openfront.ui"


class QueueHandler(logging.Handler):
    """Send formatted user messages to a thread-safe queue."""

    def __init__(self, messages: Queue[str]) -> None:
        super().__init__(logging.INFO)
        self.messages = messages

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.messages.put_nowait(self.format(record))
        except Exception:
            self.handleError(record)


def setup_logging(level: str) -> None:
    """Configure timestamped console output."""
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s",
                        force=True)


def setup_ui_logging(messages: Queue[str]) -> logging.Logger:
    """Configure the dedicated logger used for non-technical UI feedback."""
    logger = logging.getLogger(UI_LOGGER)
    logger.handlers.clear()
    handler = QueueHandler(messages)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
