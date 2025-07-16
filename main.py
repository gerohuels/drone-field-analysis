"""Entry point for the Drone Field Analysis application.

This module simply configures logging and launches the Tkinter based GUI.
"""

from drone_field_analysis.gui.main_window import DroneFieldGUI
from drone_field_analysis.utils.logging_utils import configure_logging


def main() -> None:
    """Start the GUI application.

    All heavy lifting is done in :class:`~drone_field_analysis.gui.main_window.DroneFieldGUI`.
    This function merely sets up logging and instantiates the GUI class.
    """
    # Configure the root logger before any other modules create loggers
    configure_logging(log_file="log.txt")

    # Instantiate the window and start Tkinter's event loop which blocks
    # until the user exits the program
    app = DroneFieldGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
