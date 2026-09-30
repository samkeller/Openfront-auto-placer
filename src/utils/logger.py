"""Console status messages."""

import logging


def setup_logging(level: str) -> None:
    """Configure timestamped console output."""
    logging.basicConfig(level=level, format="%(asctime)s %(message)s")
