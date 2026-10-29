"""Tests for Notion setup verification."""

import pytest
import requests

from config import Settings
from notion_api import NotionClient, NotionSetupError, check_setup


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self.payload = payload or {}

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.request = None

    def get(self, url, headers, timeout):
        self.request = (url, headers, timeout)
        if self.error:
            raise self.error
        return self.response


def make_client(response=None, error=None):
    session = FakeSession(response=response, error=error)
    client = NotionClient(Settings("secret-token", "database-id"), session=session)
    return client, session


def test_missing_settings_are_actionable(monkeypatch):
    monkeypatch.setattr("notion_api.load_settings", lambda: (_ for _ in ()).throw(
        RuntimeError("Missing required setting(s): NOTION_API_KEY, NOTION_DATABASE_ID. Copy .env.example to .env and fill in the values.")
    ))

    with pytest.raises(NotionSetupError, match="NOTION_API_KEY"):
        check_setup()


def test_successful_database_access_reports_connected():
    client, session = make_client(FakeResponse(200, {
        "title": [{"plain_text": "Tasks"}],
        "data_sources": [{"id": "source-id"}],
    }))

    result = client.check_connection()

    assert result.connected is True
    assert client.data_source_id == "source-id"
    assert result.database_title == "Tasks"
    assert session.request[0].endswith("/databases/database-id")
    assert session.request[1]["Notion-Version"] == "2026-03-11"
    assert session.request[1]["Authorization"] == "Bearer secret-token"
    assert session.request[2] == 10


@pytest.mark.parametrize(
    ("status", "message"),
    [
        (401, "Notion rejected the API key"),
        (404, "not found or is not shared"),
    ],
)
def test_invalid_key_and_inaccessible_database_are_explained(status, message):
    client, _ = make_client(FakeResponse(status))

    with pytest.raises(NotionSetupError, match=message):
        client.check_connection()


def test_forbidden_database_access_is_explained():
    client, _ = make_client(FakeResponse(403))

    with pytest.raises(NotionSetupError, match="cannot read this database"):
        client.check_connection()


def test_network_failure_does_not_expose_secret():
    client, _ = make_client(error=requests.ConnectionError("connection failed"))

    with pytest.raises(NotionSetupError, match="Could not reach Notion") as exc:
        client.check_connection()

    assert "secret-token" not in str(exc.value)
