import logging
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QFileDialog

from ..compui.load_file import Ui_Dialog
from ..data import Data, DataMatrix


class LoadDialog(QDialog):
    data_submitted = pyqtSignal(Data)
    default_path = Path("./data/norm3n.txt")

    def __init__(self, alpha: float = 0.05, dependent: int | None = None):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.pathLineEdit.setText(f"{self.default_path}")
        self.ui.loadButton.clicked.connect(self.onButtonLoad)
        self.ui.buttonBox.accepted.connect(self.submit_data)
        self.ui.buttonBox.rejected.connect(self.reject)

        self._alpha = alpha
        self._dependent = dependent

    def onButtonLoad(self):
        fpath, _ = QFileDialog.getOpenFileName(
            self,
            "Choose data-containing file",
            "./data/",
            "All files(*);;Txt files(*.txt)",
        )

        if fpath:
            self.ui.pathLineEdit.setText(fpath)

    def preprocess_data(self, fpath):
        data = Data(fpath, alpha=self._alpha, dependent=self._dependent)
        if self.ui.standartizeButton.isChecked:
            data = Data(
                DataMatrix.standartize(data.cols),
                alpha=self._alpha,
                dependent=self._dependent,
            )

        return data

    def submit_data(self):
        path = self.ui.pathLineEdit.text()
        if path != None:
            data = self.preprocess_data(path)
            self.data_submitted.emit(data)
            logging.debug(f"Loaded data from: {path}")
            self.accept()
        else:
            self.reject()
