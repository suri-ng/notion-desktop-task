"""Task entry window for the Notion desktop task utility."""

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import load_settings
from notion_api import NotionClient, NotionSetupError


class AddTaskWindow(QMainWindow):
    """Window for entering a task and checking its Notion connection."""

    def __init__(self, notion_client: NotionClient | None = None) -> None:
        super().__init__()
        self.notion_client = notion_client
        self.setWindowTitle("Add new task to Notion")
        self.setMinimumWidth(420)

        self.status = QLabel("Check the Notion connection before adding a task.")
        self.status.setWordWrap(True)
        self.status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.title = QLineEdit()
        self.title.setPlaceholderText("Task title")

        self.content = QPlainTextEdit()
        self.content.setPlaceholderText("Optional content...")

        self.add_button = QPushButton("Add task")
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setEnabled(False)

        self.check_button = QPushButton("Check Notion connection")
        self.check_button.setFixedSize(150, 26)
        self.check_button.setToolTip("Check access to the configured Notion database")
        self.check_button.clicked.connect(self.check_connection)

        container = QWidget()
        main_layout = QVBoxLayout(container)

        header = QHBoxLayout()
        header.addWidget(QLabel("New task"))
        header.addStretch()
        header.addWidget(self.check_button)

        main_layout.addLayout(header)
        main_layout.addWidget(self.status)
        main_layout.addWidget(self.title)
        main_layout.addWidget(self.content)
        main_layout.addWidget(self.add_button)
        self.setCentralWidget(container)

    def check_connection(self) -> None:
        """Load settings if needed and verify database access."""
        self.check_button.setEnabled(False)
        self.status.setText("Checking Notion connection...")
        QApplication.processEvents()
        try:
            settings = load_settings()
            if self.notion_client is None or self.notion_client.settings != settings:
                self.notion_client = NotionClient(settings)
            result = self.notion_client.check_connection()
            detail = f"\nDatabase: {result.database_title}" if result.database_title else ""
            self.status.setText(f"Connected. {result.message}{detail}")
            self.add_button.setEnabled(True)
        except (NotionSetupError, RuntimeError) as exc:
            self.status.setText(f"Setup needs attention: {exc}")
            self.add_button.setEnabled(False)
        finally:
            self.check_button.setEnabled(True)

    def title_to_text(self) -> str:
        """Read the task title from its line edit."""
        return self.title.text()

    def content_to_text(self) -> str:
        """Read optional plain text from its multiline editor."""
        return self.content.toPlainText()

    def add_task(self) -> None:
        """Create the task from the form and show the result."""
        if self.notion_client is None:
            self.status.setText("Check the Notion connection before adding a task.")
            return

        self.add_button.setEnabled(False)
        self.status.setText("Adding task to Notion...")
        QApplication.processEvents()
        try:
            self.notion_client.create_task(
                self.title_to_text(),
                self.content_to_text(),
            )
        except (NotionSetupError, ValueError) as exc:
            self.status.setText(f"Could not add task: {exc}")
        else:
            self.status.setText(f"Task added to {self.notion_client.settings.notion_status_value}.")
            self.title.clear()
            self.content.clear()
        finally:
            self.add_button.setEnabled(
                self.notion_client is not None
                and self.notion_client.data_source_id is not None
            )

    @Slot()
    def show_from_hotkey(self) -> None:
        """Show the window, bring it forward, and focus the title field."""
        self.showNormal()
        self.raise_()
        self.activateWindow()
        self.title.setFocus()

    def closeEvent(self, event) -> None:
        """Hide on close so the tray icon and hotkey remain available."""
        self.hide()
        event.ignore()


def create_app(notion_client: NotionClient | None = None) -> tuple[QApplication, AddTaskWindow]:
    """Create the Qt application and task-entry window."""
    app = QApplication.instance() or QApplication([])
    window = AddTaskWindow(notion_client)
    return app, window
