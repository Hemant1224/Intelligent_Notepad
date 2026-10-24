class ThemeMixin:
    # ---------------- THEME ----------------

    def apply_theme(self, dark=None):
        """Apply the selected theme. Can be called by the View menu toggle."""
        if dark is not None:
            self.dark_theme = bool(dark)

        self.settings.setValue("dark_theme", self.dark_theme)

        if hasattr(self, "theme_action"):
            self.theme_action.blockSignals(True)
            self.theme_action.setChecked(self.dark_theme)
            self.theme_action.setText("Dark Theme" if self.dark_theme else "Light Theme")
            self.theme_action.blockSignals(False)

        if self.dark_theme:
            stylesheet = """
                QMainWindow { background-color: #1e1e1e; }
                QMenuBar { background-color: #252526; color: white; }
                QMenuBar::item:selected { background-color: #3e3e42; }
                QMenu { background-color: #252526; color: white; border: 1px solid #454545; }
                QMenu::item:selected { background-color: #094771; }
                QToolBar { background-color: #252526; border: none; spacing: 8px; padding: 6px; }
                QToolButton { color: white; padding: 6px; }
                QToolButton:hover { background-color: #3e3e42; }
                QTabWidget::pane { border: none; }
                QTabBar::tab { background-color: #252526; color: #cccccc; padding: 10px 18px; border: none; }
                QTabBar::tab:selected { background-color: #1e1e1e; color: white; border-bottom: 2px solid #007acc; }
                QPlainTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: none; padding: 12px; selection-background-color: #264f78; }
                QStatusBar { background-color: #007acc; color: white; }
                QDialog, QLabel, QCheckBox { color: #eeeeee; }
                QLineEdit { background-color: #333333; color: #eeeeee; border: 1px solid #555555; padding: 5px; }
                QPushButton { background-color: #333333; color: #eeeeee; border: 1px solid #555555; padding: 6px 10px; }
                QPushButton:hover { background-color: #454545; }
            """
        else:
            stylesheet = """
                QMainWindow { background-color: #f3f3f3; }
                QMenuBar { background-color: #ffffff; color: #222222; }
                QMenuBar::item:selected { background-color: #e5e5e5; }
                QMenu { background-color: #ffffff; color: #222222; border: 1px solid #cccccc; }
                QMenu::item:selected { background-color: #dcecff; }
                QToolBar { background-color: #ffffff; border: none; spacing: 8px; padding: 6px; }
                QToolButton { color: #222222; padding: 6px; }
                QToolButton:hover { background-color: #e5e5e5; }
                QTabWidget::pane { border: none; }
                QTabBar::tab { background-color: #e8e8e8; color: #333333; padding: 10px 18px; border: none; }
                QTabBar::tab:selected { background-color: #ffffff; color: #111111; border-bottom: 2px solid #0078d4; }
                QPlainTextEdit { background-color: #ffffff; color: #222222; border: none; padding: 12px; selection-background-color: #b7d7ff; }
                QStatusBar { background-color: #e8e8e8; color: #333333; }
                QDialog, QLabel, QCheckBox { color: #222222; }
                QLineEdit { background-color: #ffffff; color: #222222; border: 1px solid #cccccc; padding: 5px; }
                QPushButton { background-color: #f7f7f7; color: #222222; border: 1px solid #cccccc; padding: 6px 10px; }
                QPushButton:hover { background-color: #e5e5e5; }
            """

        self.setStyleSheet(stylesheet)
