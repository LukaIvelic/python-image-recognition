"""
Hand Gesture Recognition Application
Main entry point for the application.
"""

from src.app import HandGestureApp


def main():
    """Run the hand gesture recognition application."""
    app = HandGestureApp()
    app.run()


if __name__ == "__main__":
    main()

