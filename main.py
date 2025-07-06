"""Entry point for the Drone Field Analysis application."""

from drone_field_analysis.gui.main_window import DroneFieldGUI
from drone_field_analysis.utils.logging_utils import configure_logging


def main() -> None:
    """Start the GUI application."""
    # Configure the root logger before any other modules create loggers
    configure_logging()
    app = DroneFieldGUI()
    # Hand control over to Tkinter's event loop
    app.mainloop()


if __name__ == "__main__":
    main()
