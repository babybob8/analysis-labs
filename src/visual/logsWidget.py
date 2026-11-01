import logging
from os import walk
from pathlib import Path

from PyQt6.QtCore import QFileSystemWatcher, pyqtSlot
from PyQt6.QtWidgets import QWidget

from ..compui.logs_widget import Ui_LogsWidget


class LogsWidget(QWidget):
    def __init__(self, current_log: Path, logs_dir: Path) -> None:
        super().__init__()
        self.ui = Ui_LogsWidget()
        self.ui.setupUi(self)

        self.logs_dir = logs_dir
        self.current_log = current_log
        self.log_names = []
        self._last_pos = 0

        self.search_logs()

        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.fileChanged.connect(self.on_file_changed)

        self.ui.selectLogBox.currentTextChanged.connect(self.load_log_content)

        self.ui.bottomButton.clicked.connect(self.scroll_to_bottom)

        index = self.ui.selectLogBox.findText(self.current_log.name)
        if index != -1:
            self.ui.selectLogBox.setCurrentIndex(index)
        elif self.log_names:
            self.load_log_content(self.ui.selectLogBox.currentText())

    def search_logs(self) -> None:
        if not self.logs_dir.exists():
            return

        self.log_names = next(walk(self.logs_dir), (None, None, []))[2]
        if self.log_names:
            self.ui.selectLogBox.blockSignals(True)
            self.ui.selectLogBox.clear()
            self.ui.selectLogBox.addItems(self.log_names)
            self.ui.selectLogBox.blockSignals(False)

    @pyqtSlot(str)
    def load_log_content(self, log_filename: str) -> None:
        if not log_filename:
            return

        watched = self.file_watcher.files()
        if watched:
            self.file_watcher.removePaths(watched)

        file_path = self.logs_dir / log_filename

        if file_path.exists() and file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                self.ui.logPlainTextEdit.setPlainText(content)

                self._last_pos = file_path.stat().st_size

                self.file_watcher.addPath(str(file_path.resolve()))

                self.scroll_to_bottom()
            except Exception as e:
                logging.error(f"Error while reading file {log_filename}: {e}")

    @pyqtSlot(str)
    def on_file_changed(self, path: str) -> None:
        file_path = Path(path)
        if not file_path.exists():
            return

        current_size = file_path.stat().st_size

        if current_size < self._last_pos:
            self.load_log_content(file_path.name)
            return

        if current_size > self._last_pos:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(self._last_pos)
                    new_text = f.read()
                    self._last_pos = f.tell()

                self.ui.logPlainTextEdit.appendPlainText(new_text.strip("\r\n"))
                self.scroll_to_bottom()
            except Exception as e:
                logging.error(f"Error while updating log: {e}")

    def scroll_to_bottom(self) -> None:
        scrollbar = self.ui.logPlainTextEdit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
