import sys

try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    from PyQt6.QtWidgets import QApplication  # type: ignore[import-not-found]

try:
    from .windows.main_window import MainWindow
except ImportError:
    from windows.main_window import MainWindow


def main():

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
