"""Utility to configure application logging."""

import logging
from typing import Optional


def configure_logging(level: int = logging.INFO, log_format: Optional[str] = None) -> None:
    """Configure basic logging for the application.

    Parameters
    ----------
    level:
        Logging level to use. Defaults to ``logging.INFO``.
    log_format:
        Optional logging format string. If not provided, a reasonable
        default is used.
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=level, format=log_format)

