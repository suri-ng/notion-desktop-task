"""Notion API integration for checking application setup."""

from dataclasses import dataclass
import requests

from config import Settings, load_settings

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_API_VERSION = "2026-03-11"


class NotionSetupError(RuntimeError):
    """A safe, user-facing setup or connection error."""


@dataclass(frozen=True)
class ConnectionStatus:
    """Result of checking access to the configured Notion database."""

    connected: bool
    message: str
    database_title: str | None = None


class NotionClient:
    """Small Notion API client for validating credentials and database access."""

    def __init__(self, settings: Settings, session: requests.Session | None = None):
        self.settings = settings
        self.session = session or requests.Session()
        self.data_source_id: str | None = None

    def _headers(self) -> dict[str, str]:
        """Headers required for Notion API requests."""
        return {
            "Authorization": f"Bearer {self.settings.notion_api_key}",
            "Notion-Version": NOTION_API_VERSION,
            "Accept": "application/json",
        }

    def check_connection(self) -> ConnectionStatus:
        """Check credentials and confirm the integration can read its database."""
        self.data_source_id = None
        url = f"{NOTION_API_BASE}/databases/{self.settings.notion_database_id}"
        try:
            response = self.session.get(url, headers=self._headers(), timeout=10)
        except requests.Timeout as exc:
            raise NotionSetupError(
                "Notion did not respond in time. Check your internet connection and try again."
            ) from exc
        except requests.RequestException as exc:
            raise NotionSetupError(
                "Could not reach Notion. Check your internet connection and try again."
            ) from exc

        if not response.ok:
            _raise_api_error(response.status_code, operation="check the database connection")

        try:
            data = response.json()
        except ValueError as exc:
            raise NotionSetupError("Notion returned an unexpected response. Try again.") from exc

        data_sources = data.get("data_sources")
        if not isinstance(data_sources, list) or not data_sources:
            raise NotionSetupError(
                "The database is accessible, but it has no data sources available to add tasks to."
            )

        data_source_id = data_sources[0].get("id") if isinstance(data_sources[0], dict) else None
        if not data_source_id:
            raise NotionSetupError(
                "Notion returned a database data source without an ID. Check the database configuration and try again."
            )

        self.data_source_id = data_source_id
        title = _database_title(data)
        return ConnectionStatus(
            connected=True,
            message="Connected to Notion. Database access is ready.",
            database_title=title,
        )

    def create_task(self, title: str, content: str = "") -> dict:
        """Create a task page in the cached database data source."""
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Task title cannot be blank.")

        if self.data_source_id is None:
            self.check_connection()

        task = {
            "parent": {"data_source_id": self.data_source_id},
            "properties": {
                "Name": {
                    "title": [
                        {"text": {"content": title.strip()}},
                    ]
                },
                "Status": {
                    "select": {"name": "To Do"}
                },
            },
        }
        if isinstance(content, str) and content.strip():
            task["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": content},
                            }
                        ]
                    },
                }
            ]

        try:
            response = self.session.post(
                f"{NOTION_API_BASE}/pages",
                headers=self._headers(),
                json=task,
                timeout=10,
            )
        except requests.RequestException as exc:
            raise NotionSetupError("Could not reach Notion. Check your connection and try again.") from exc

        if not response.ok:
            _raise_api_error(response.status_code, operation="create the task")

        try:
            return response.json()
        except ValueError as exc:
            raise NotionSetupError("Notion created a response we could not read. Check the task in Notion.") from exc


def check_setup() -> ConnectionStatus:
    """Load local settings and verify the Notion database connection."""
    try:
        settings = load_settings()
    except RuntimeError as exc:
        raise NotionSetupError(str(exc)) from exc
    return NotionClient(settings).check_connection()


def _raise_api_error(status_code: int, operation: str) -> None:
    """Raise a clear error for an unsuccessful Notion API response."""
    if status_code == 401:
        message = "Notion rejected the API key. Check NOTION_API_KEY in your .env file."
    elif status_code == 403:
        message = "The integration is not permitted to perform this action. Check its Notion capabilities."
    elif status_code == 404:
        message = "The database or data source was not found or is not shared with this integration."
    elif status_code == 400:
        message = "Notion rejected the request data. Check the database properties and task status option."
    elif status_code == 429:
        message = "Notion is rate limiting requests. Wait a moment and try again."
    else:
        message = f"Notion returned HTTP {status_code}. Try again."
    raise NotionSetupError(f"Could not {operation}: {message}")


def _database_title(data: dict) -> str | None:
    """Extract the display title from a Notion database response."""
    title_parts = data.get("title", [])
    title = "".join(part.get("plain_text", "") for part in title_parts)
    return title or None
