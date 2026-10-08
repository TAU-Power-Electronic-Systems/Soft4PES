"""GUI package for Soft4PES."""

try:
    from .windows.main_window import MainWindow
except ImportError:
    from windows.main_window import MainWindow  # pragma: no cover - direct script execution fallback

__all__ = ["MainWindow"]
