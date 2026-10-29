"""Application entry point for the Notion desktop task utility."""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QStyle, QSystemTrayIcon

from config import load_settings
from hotkey import GlobalTaskHotkey
from notion_api import NotionClient
from ui import create_app


def main() -> None:
    """Create one shared Notion client and start the setup window."""
    try:
        notion_client = NotionClient(load_settings())
    except RuntimeError:
        # Let the window show setup guidance if .env values are missing.
        notion_client = None

    app, window = create_app(notion_client)
    app.setQuitOnLastWindowClosed(False)

    tray = QSystemTrayIcon(
        app.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon),
        app,
    )
    tray.setToolTip("Notion Task Popup")

    tray_menu = QMenu()
    open_action = QAction("Open task popup", tray_menu)
    open_action.triggered.connect(window.show_from_hotkey)
    quit_action = QAction("Quit", tray_menu)
    quit_action.triggered.connect(app.quit)
    tray_menu.addAction(open_action)
    tray_menu.addSeparator()
    tray_menu.addAction(quit_action)
    tray.setContextMenu(tray_menu)
    tray.activated.connect(
        lambda reason: window.show_from_hotkey()
        if reason == QSystemTrayIcon.ActivationReason.Trigger
        else None
    )

    hotkey = GlobalTaskHotkey(window.show_from_hotkey)
    hotkey.start()
    app.aboutToQuit.connect(hotkey.stop)

    tray.show()
    window.check_connection()
    app.exec()


if __name__ == "__main__":
    main()
