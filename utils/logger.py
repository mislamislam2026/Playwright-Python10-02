"""Project-wide logger."""
from __future__ import annotations

import logging


def get_logger(name: str = "webtours") -> logging.Logger:
    """Return a configured logger (handlers are added only once)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
