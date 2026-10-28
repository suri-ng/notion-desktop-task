"""Application settings and Notion database mappings."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

# Load a project-local .env for desktop launches from any working directory.
load_dotenv(Path(__file__).resolve().parent / ".env")


@dataclass(frozen=True)
class Settings:
    """Configuration loaded from environment variables."""

    notion_api_key: str
    notion_database_id: str


def load_settings() -> Settings:
    """Read required Notion settings, raising a clear error when missing."""
    api_key = os.getenv("NOTION_API_KEY", "").strip()
    database_id = os.getenv("NOTION_DATABASE_ID", "").strip()

    missing = []
    if not api_key:
        missing.append("NOTION_API_KEY")
    if not database_id:
        missing.append("NOTION_DATABASE_ID")
    if missing:
        raise RuntimeError(
            "Missing required setting(s): " + ", ".join(missing)
            + ". Copy .env.example to .env and fill in the values."
        )

    return Settings(notion_api_key=api_key, notion_database_id=database_id)
