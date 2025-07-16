"""Utility module for configuring application logging.

This helper provides a single :func:`configure_logging` function that sets up
the Python ``logging`` module with sensible defaults.  It can be imported by
both the GUI and command-line scripts to ensure consistent log formatting.
"""

import logging
import sys
from typing import Optional


def configure_logging(
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    log_file: str = "log.txt",
) -> None:
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
    white = "\033[97m"
    reset = "\033[0m"

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        logging.Formatter(f"{white}{log_format}{reset}")
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format))

    logging.basicConfig(level=level, handlers=[stream_handler, file_handler])

