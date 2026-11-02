from types import SimpleNamespace

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ui import AddTaskWindow


class FakeNotionClient:
    def __init__(self):
        self.settings = SimpleNamespace(notion_status_value="To Do")
        self.created_tasks = []
        self.data_source_id = "source-id"

    def create_task(self, title, content):
        self.created_tasks.append((title, content))


def test_tab_then_enter_adds_task():
    app = QApplication.instance() or QApplication([])
    notion_client = FakeNotionClient()
    window = AddTaskWindow(notion_client)
    window.add_button.setEnabled(True)
    window.title.setText("Keyboard task")
    window.content.setPlainText("Task notes")
    window.show()
    window.title.setFocus()
    app.processEvents()

    QTest.keyClick(window.title, Qt.Key.Key_Tab)
    assert app.focusWidget() is window.content

    QTest.keyClick(window.content, Qt.Key.Key_Tab)
    assert app.focusWidget() is window.add_button

    QTest.keyClick(window.add_button, Qt.Key.Key_Return)

    assert notion_client.created_tasks == [("Keyboard task", "Task notes")]
    window.close()


def test_enter_in_title_submits_task():
    app = QApplication.instance() or QApplication([])
    notion_client = FakeNotionClient()
    window = AddTaskWindow(notion_client)
    window.add_button.setEnabled(True)
    window.title.setText("Title submission")
    window.show()
    window.title.setFocus()
    app.processEvents()

    QTest.keyClick(window.title, Qt.Key.Key_Return)

    assert notion_client.created_tasks == [("Title submission", "")]
    window.close()


def test_enter_in_notes_submits_and_shift_enter_adds_newline():
    app = QApplication.instance() or QApplication([])
    notion_client = FakeNotionClient()
    window = AddTaskWindow(notion_client)
    window.add_button.setEnabled(True)
    window.title.setText("Notes submission")
    window.content.setFocus()
    app.processEvents()

    QTest.keyClick(window.content, Qt.Key.Key_Return, Qt.KeyboardModifier.ShiftModifier)
    QTest.keyClicks(window.content, "Task notes")
    QTest.keyClick(window.content, Qt.Key.Key_Return)

    assert notion_client.created_tasks == [("Notes submission", "\nTask notes")]
    window.close()
