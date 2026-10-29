"""Application entry point for the Notion desktop task utility."""

from config import load_settings
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
    window.show()
    window.check_connection()
    app.exec()


if __name__ == "__main__":
    main()
