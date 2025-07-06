"""Entry point for the Drone Field Analysis application."""

from drone_field_analysis.gui.main_window import DroneFieldGUI
from drone_field_analysis.utils.logging_utils import configure_logging


def main() -> None:
    """Start the GUI application."""
    configure_logging()
    app = DroneFieldGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
