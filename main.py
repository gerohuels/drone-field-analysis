"""Entry point for the Drone Field Analysis application."""

from drone_field_analysis.gui.main_window import DroneFieldGUI


def main() -> None:
    """Start the GUI application."""
    app = DroneFieldGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
