"""Utility module for configuring application logging.

This helper provides a single :func:`configure_logging` function that sets up
the Python ``logging`` module with sensible defaults.  It can be imported by
both the GUI and command-line scripts to ensure consistent log formatting.
"""

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
        # Default layout includes time, logger name and severity level
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ``basicConfig`` should only be called once across the application.
    logging.basicConfig(level=level, format=log_format)

