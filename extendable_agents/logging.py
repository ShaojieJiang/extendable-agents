"""Logging module."""

import logging


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def get_logger(name: str) -> logging.Logger:
    """Get a logger."""
    logger = logging.getLogger(name)
    return logger
