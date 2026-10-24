from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QCheckBox,
    QHBoxLayout, QVBoxLayout, QTextEdit,
)
from PySide6.QtGui import QTextCursor, QTextDocument, QColor


class SearchMixin:
    # ---------------- FIND AND REPLACE ----------------

    def show_find(self):
        self.open_search_dialog(replace_mode=False)


    def show_find_replace(self):
        self.open_search_dialog(replace_mode=True)


    def open_search_dialog(self, replace_mode=False):
        editor = self.current_editor()

        if editor is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(
            "Find and Replace" if replace_mode else "Find"
        )
        dialog.setMinimumWidth(430)

        layout = QVBoxLayout(dialog)

        # Search input
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))

        find_input = QLineEdit()
        find_input.setPlaceholderText("Enter text to find...")
        find_layout.addWidget(find_input)

        layout.addLayout(find_layout)

        # Replacement input
        replace_input = QLineEdit()

        if replace_mode:
            replace_layout = QHBoxLayout()
            replace_layout.addWidget(QLabel("Replace:"))

            replace_input.setPlaceholderText("Replace with...")
            replace_layout.addWidget(replace_input)

            layout.addLayout(replace_layout)

        # Search options
        case_checkbox = QCheckBox("Case sensitive")
        layout.addWidget(case_checkbox)

        # Buttons
        button_layout = QHBoxLayout()

        previous_button = QPushButton("Previous")
        next_button = QPushButton("Next")

        button_layout.addWidget(previous_button)
        button_layout.addWidget(next_button)

        replace_button = None
        replace_all_button = None

        if replace_mode:
            replace_button = QPushButton("Replace")
            replace_all_button = QPushButton("Replace All")

            button_layout.addWidget(replace_button)
            button_layout.addWidget(replace_all_button)

        layout.addLayout(button_layout)

        # Search state
        state = {"last_query": ""}

        def search_flags():
            flags = QTextDocument.FindFlag()

            if case_checkbox.isChecked():
                flags |= QTextDocument.FindFlag.FindCaseSensitively

            return flags

        def clear_highlights():
            editor.setExtraSelections([])

        def highlight_matches():
            query = find_input.text()
            clear_highlights()

            if not query:
                state["last_query"] = ""
                return

            selections = []
            document = editor.document()
            cursor = QTextCursor(document)
            flags = search_flags()

            while True:
                cursor = document.find(query, cursor, flags)

                if cursor.isNull():
                    break

                selection = QTextEdit.ExtraSelection()
                selection.cursor = cursor
                selection.format.setBackground(
                    QColor("#665c00")
                )
                selection.format.setForeground(
                    QColor("#ffffff")
                )

                selections.append(selection)

            editor.setExtraSelections(selections)
            state["last_query"] = query

        def find_text(backward=False):
            query = find_input.text()

            if not query:
                return

            flags = search_flags()

            if backward:
                flags |= QTextDocument.FindFlag.FindBackward

            cursor = editor.textCursor()

            # Continue from the current selection.
            cursor = editor.document().find(
                query,
                cursor,
                flags
            )

            # Wrap around when the end or beginning is reached.
            if cursor.isNull():
                cursor = QTextCursor(editor.document())

                if backward:
                    cursor.movePosition(
                        QTextCursor.MoveOperation.End
                    )
                else:
                    cursor.movePosition(
                        QTextCursor.MoveOperation.Start
                    )

                cursor = editor.document().find(
                    query,
                    cursor,
                    flags
                )

            if cursor.isNull():
                self.status.showMessage("No matches found", 3000)
                return

            editor.setTextCursor(cursor)
            editor.ensureCursorVisible()

        def replace_current():
            query = find_input.text()

            if not query:
                return

            cursor = editor.textCursor()

            # Replace only if the selection matches the search query.
            flags = search_flags()

            selected_text = cursor.selectedText()

            matches = (
                selected_text == query
                if case_checkbox.isChecked()
                else selected_text.casefold() == query.casefold()
            )

            if not cursor.hasSelection() or not matches:
                find_text()
                cursor = editor.textCursor()

                selected_text = cursor.selectedText()

                matches = (
                    selected_text == query
                    if case_checkbox.isChecked()
                    else selected_text.casefold() == query.casefold()
                )

            if cursor.hasSelection() and matches:
                cursor.insertText(replace_input.text())
                editor.setTextCursor(cursor)

                highlight_matches()
                find_text()

        def replace_all():
            query = find_input.text()

            if not query:
                return

            replacement = replace_input.text()
            document = editor.document()
            cursor = QTextCursor(document)

            flags = search_flags()
            count = 0

            cursor.beginEditBlock()

            try:
                while True:
                    found = document.find(
                        query,
                        cursor,
                        flags
                    )

                    if found.isNull():
                        break

                    found.insertText(replacement)
                    cursor = found
                    count += 1

            finally:
                cursor.endEditBlock()

            highlight_matches()

            self.status.showMessage(
                f"Replaced {count} occurrence(s)",
                4000
            )

        # Connect buttons
        previous_button.clicked.connect(
            lambda: find_text(backward=True)
        )

        next_button.clicked.connect(find_text)

        find_input.textChanged.connect(
            lambda _: highlight_matches()
        )

        case_checkbox.toggled.connect(
            lambda _: highlight_matches()
        )

        find_input.returnPressed.connect(find_text)

        if replace_mode:
            replace_button.clicked.connect(replace_current)
            replace_all_button.clicked.connect(replace_all)

        # Close the dialog and remove search highlights.
        dialog.finished.connect(
            lambda _: clear_highlights()
        )

        # Prefill with selected text, if available.
        selected_text = editor.textCursor().selectedText()

        if selected_text:
            find_input.setText(selected_text)

        find_input.setFocus()
        dialog.exec()
        

