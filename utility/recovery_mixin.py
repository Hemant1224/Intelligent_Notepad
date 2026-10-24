import json
from pathlib import Path
from PySide6.QtWidgets import QMessageBox


class RecoveryMixin:
    # ---------------- AUTOSAVE / CRASH RECOVERY ----------------

    @property
    def recovery_directory(self):
        """Directory used for recovery snapshots of untitled documents."""
        return Path.home() / ".mynotepad" / "recovery"

    def recovery_file(self, editor):
        return self.recovery_directory / f"{editor.recovery_id}.json"

    def remove_recovery_file(self, editor):
        try:
            self.recovery_file(editor).unlink(missing_ok=True)
        except OSError:
            pass

    def autosave_documents(self):
        """Save named files and snapshot untitled documents for crash recovery."""
        saved_count = 0

        for index in range(self.tabs.count()):
            editor = self.tabs.widget(index)
            if editor is None or editor.loading:
                continue

            content = editor.toPlainText()
            if content == editor.saved_text:
                self.remove_recovery_file(editor)
                continue

            if editor.file_path:
                # Existing files are autosaved directly after a short pause.
                if self.write_file(editor, editor.file_path, autosave=True):
                    saved_count += 1
            else:
                # Untitled documents are not assigned a real filename; keep a
                # recovery snapshot without forcing a Save As dialog.
                try:
                    self.recovery_directory.mkdir(parents=True, exist_ok=True)
                    payload = {"content": content, "title": self.tabs.tabText(index)}
                    self.recovery_file(editor).write_text(
                        json.dumps(payload, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    saved_count += 1
                except OSError as error:
                    self.status.showMessage(
                        f"Autosave recovery failed: {error}", 5000
                    )

        if saved_count:
            self.status.showMessage("Autosaved changes", 2500)

    def restore_recovery_documents(self):
        """Offer to restore untitled documents left by an unexpected exit."""
        try:
            recovery_files = list(self.recovery_directory.glob("*.json"))
        except OSError:
            return

        if not recovery_files:
            return

        answer = QMessageBox.question(
            self,
            "Recover Documents",
            f"Found {len(recovery_files)} autosaved recovery document(s).\n"
            "Would you like to restore them?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if answer != QMessageBox.StandardButton.Yes:
            for recovery_file in recovery_files:
                try:
                    recovery_file.unlink(missing_ok=True)
                except OSError:
                    pass
            return

        for recovery_file in recovery_files:
            try:
                payload = json.loads(recovery_file.read_text(encoding="utf-8"))
                content = payload.get("content", "")
                if not isinstance(content, str):
                    continue

                self.new_tab()
                editor = self.current_editor()
                editor.loading = True
                editor.setPlainText(content)
                editor.saved_text = ""
                editor.loading = False
                # Reuse the snapshot ID so future autosaves replace this file.
                editor.recovery_id = recovery_file.stem
                self.update_tab_title(editor)
            except (OSError, json.JSONDecodeError, AttributeError) as error:
                self.status.showMessage(
                    f"Could not restore {recovery_file.name}: {error}", 5000
                )

        self.update_status()

