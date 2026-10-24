import uuid
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QPlainTextEdit, QTabWidget, QToolBar, QStatusBar,
    QFileDialog, QMessageBox,
)
from PySide6.QtCore import QTimer, QSettings
from PySide6.QtGui import QAction, QFont, QKeySequence

from .search_mixin import SearchMixin
from .recovery_mixin import RecoveryMixin
from .theme_mixin import ThemeMixin


class MyNotepad(SearchMixin, RecoveryMixin, ThemeMixin, QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MyNotepad")
        self.resize(1100, 700)

        # Persist small app preferences (such as the selected theme).
        self.settings = QSettings("HemantApps", "MyNotepad")
        self.dark_theme = self.settings.value("dark_theme", True, type=bool)

        # Autosave after the user has stopped typing briefly.
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.setInterval(1500)
        self.autosave_timer.timeout.connect(self.autosave_documents)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)

        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_status)

        self.setCentralWidget(self.tabs)

        self.create_menu()
        self.create_toolbar()
        self.create_status_bar()
        self.apply_theme(self.dark_theme)

        self.new_tab()
        self.restore_recovery_documents()

    # ---------------- MENU ----------------

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")

        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.new_tab)

        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_file)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_file)

        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(
            QKeySequence("Ctrl+Shift+S")
        )
        save_as_action.triggered.connect(self.save_file_as)

        close_action = QAction("Close Tab", self)
        close_action.setShortcut(QKeySequence("Ctrl+W"))
        close_action.triggered.connect(self.close_current_tab)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(close_action)
        file_menu.addAction(exit_action)

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        undo_action.triggered.connect(self.undo)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence("Ctrl+Y"))
        redo_action.triggered.connect(self.redo)

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        select_all_action.triggered.connect(self.select_all)

        find_action = QAction("Find...", self)
        find_action.setShortcut(QKeySequence("Ctrl+F"))
        find_action.triggered.connect(self.show_find)

        replace_action = QAction("Find and Replace...", self)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        replace_action.triggered.connect(self.show_find_replace)

        
        edit_menu.addAction(find_action)
        edit_menu.addAction(replace_action)
        edit_menu.addSeparator()
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(select_all_action)

        self.theme_action = QAction("Dark Theme", self)
        self.theme_action.setCheckable(True)
        self.theme_action.setChecked(self.dark_theme)
        self.theme_action.toggled.connect(self.apply_theme)
        view_menu.addAction(self.theme_action)

    # ---------------- TOOLBAR ----------------

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)

        self.addToolBar(toolbar)

        actions = [
            ("New", self.new_tab),
            ("Open", self.open_file),
            ("Save", self.save_file),
        ]

        for label, callback in actions:
            action = QAction(label, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)

    # ---------------- STATUS BAR ----------------

    def create_status_bar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    # ---------------- DOCUMENT MANAGEMENT ----------------

    def new_tab(self):
        editor = QPlainTextEdit()

        editor.setFont(QFont("Consolas", 12))
        editor.setPlaceholderText("Start writing...")

        # Metadata for this individual document.
        editor.file_path = None
        editor.saved_text = ""
        editor.loading = False
        editor.recovery_id = str(uuid.uuid4())

        editor.textChanged.connect(
            lambda e=editor: self.document_changed(e)
        )

        editor.cursorPositionChanged.connect(
            self.update_status
        )

        index = self.tabs.addTab(editor, "Untitled")
        self.tabs.setCurrentIndex(index)

        editor.setFocus()
        self.update_status()

    def current_editor(self):
        return self.tabs.currentWidget()

    def document_changed(self, editor):
        if editor.loading:
            return

        self.update_tab_title(editor)

        if editor is self.current_editor():
            self.update_status()

        # Restart the debounce timer whenever the user edits a document.
        self.autosave_timer.start()

    def update_tab_title(self, editor):
        index = self.tabs.indexOf(editor)

        if index == -1:
            return

        if editor.file_path:
            filename = Path(editor.file_path).name
        else:
            filename = "Untitled"

        modified = editor.toPlainText() != editor.saved_text

        if modified:
            filename = "*" + filename

        self.tabs.setTabText(index, filename)

        if editor is self.current_editor():
            self.setWindowTitle(f"{filename} - MyNotepad")

    def update_status(self, *_):
        editor = self.current_editor()

        if editor is None:
            self.status.showMessage("Ready")
            return

        cursor = editor.textCursor()

        self.status.showMessage(
            f"Line: {cursor.blockNumber() + 1}  |  "
            f"Column: {cursor.columnNumber() + 1}  |  "
            f"Characters: {len(editor.toPlainText())}"
        )

        self.update_tab_title(editor)

    # ---------------- OPEN FILE ----------------

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Text Files (*.txt);;Python Files (*.py);;"
            "Markdown Files (*.md);;All Files (*)"
        )

        if not path:
            return

        # Avoid opening the same file in multiple tabs.
        for index in range(self.tabs.count()):
            editor = self.tabs.widget(index)

            if (
                editor.file_path
                and Path(editor.file_path).resolve()
                == Path(path).resolve()
            ):
                self.tabs.setCurrentIndex(index)
                return

        try:
            content = Path(path).read_text(encoding="utf-8")

        except (OSError, UnicodeError) as error:
            QMessageBox.critical(
                self,
                "Open Error",
                f"Could not open the file:\n{error}"
            )
            return

        self.new_tab()
        editor = self.current_editor()

        editor.loading = True
        editor.setPlainText(content)
        editor.file_path = path
        editor.saved_text = content
        editor.loading = False

        self.update_tab_title(editor)
        self.update_status()

    # ---------------- SAVE FILE ----------------

    def save_file(self):
        editor = self.current_editor()

        if editor is None:
            return False

        if editor.file_path is None:
            return self.save_file_as()

        return self.write_file(editor, editor.file_path)

    def save_file_as(self):
        editor = self.current_editor()

        if editor is None:
            return False

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "Text Files (*.txt);;Python Files (*.py);;"
            "Markdown Files (*.md);;All Files (*)"
        )

        if not path:
            return False

        return self.write_file(editor, path)

    def write_file(self, editor, path, autosave=False):
        try:
            content = editor.toPlainText()

            Path(path).write_text(
                content,
                encoding="utf-8"
            )

            editor.file_path = path
            editor.saved_text = content
            self.remove_recovery_file(editor)

            self.update_tab_title(editor)
            self.update_status()

            self.status.showMessage(
                f"Autosaved: {Path(path).name}" if autosave else f"Saved: {Path(path).name}",
                2500 if autosave else 3000,
            )

            return True

        except OSError as error:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Could not save the file:\n{error}"
            )
            return False

    # ---------------- UNSAVED CHANGES ----------------

    def confirm_save(self, editor):
        if editor.toPlainText() == editor.saved_text:
            return True

        filename = (
            Path(editor.file_path).name
            if editor.file_path
            else "Untitled"
        )

        result = QMessageBox.question(
            self,
            "Unsaved Changes",
            f"Save changes to {filename}?",
            (
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel
            ),
            QMessageBox.StandardButton.Save
        )

        if result == QMessageBox.StandardButton.Save:
            # Only save if this is the active editor.
            if editor is not self.current_editor():
                self.tabs.setCurrentWidget(editor)

            return self.save_file()

        if result == QMessageBox.StandardButton.Discard:
            return True

        return False

    def close_tab(self, index):
        editor = self.tabs.widget(index)

        if editor is None:
            return

        if not self.confirm_save(editor):
            return

        self.remove_recovery_file(editor)
        self.tabs.removeTab(index)
        editor.deleteLater()

        if self.tabs.count() == 0:
            self.new_tab()
        else:
            self.update_status()

    def close_current_tab(self):
        index = self.tabs.currentIndex()

        if index >= 0:
            self.close_tab(index)

    def closeEvent(self, event):
        # Confirm every document before removing any tabs.
        editors = [self.tabs.widget(i) for i in range(self.tabs.count())]

        for editor in editors:
            if not self.confirm_save(editor):
                event.ignore()
                return

        self.autosave_timer.stop()
        while self.tabs.count() > 0:
            editor = self.tabs.widget(0)
            self.remove_recovery_file(editor)
            self.tabs.removeTab(0)
            editor.deleteLater()

        event.accept()

    # ---------------- EDITING ----------------

    def undo(self):
        editor = self.current_editor()

        if editor:
            editor.undo()

    def redo(self):
        editor = self.current_editor()

        if editor:
            editor.redo()

    def select_all(self):
        editor = self.current_editor()

        if editor:
            editor.selectAll()

