"""Global keyboard shortcut for reopening the task window."""

from pynput.keyboard import GlobalHotKeys
from PySide6.QtCore import QObject, Signal


class _HotkeyBridge(QObject):
    """Move pynput callbacks safely onto Qt's main thread."""

    activated = Signal()


class GlobalTaskHotkey:
    """Listen for Ctrl+Shift+N and notify the Qt application."""

    def __init__(self, callback) -> None:
        self._bridge = _HotkeyBridge()
        self._bridge.activated.connect(callback)
        self._listener = GlobalHotKeys(
            {"<ctrl>+<alt>+<shift>+n": self._bridge.activated.emit}
        )

    def start(self) -> None:
        """Start listening in pynput's background thread."""
        self._listener.start()

    def stop(self) -> None:
        """Stop the global keyboard listener."""
        self._listener.stop()
