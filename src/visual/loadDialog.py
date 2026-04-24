from .compui.load_file import Ui_Dialog
from ..data import Data, DataMatrix

from PyQt6.QtWidgets import QDialog, QFileDialog
from PyQt6.QtCore import pyqtSignal


class LoadDialog(QDialog):
    data_submitted = pyqtSignal(Data)

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.pathLineEdit.setText("Empty file path")
        self.ui.loadButton.clicked.connect(self.onButtonLoad)
        self.ui.buttonBox.accepted.connect(self.submit_data)
        self.ui.buttonBox.rejected.connect(self.reject)

        self._flags = []
        self.ui.standartizeButton.clicked.connect(lambda: self.set_flag("standartize"))

    def set_flag(self, flag: str = "undef"):
        if flag == "undef":
            return

        elif flag == "standartize":
            self._flags.append("standartize")


    def onButtonLoad(self):
        fpath, _ = QFileDialog.getOpenFileName(
            self,
            "Choose data-containing file",
            "./data/",
            "All files(*);;Txt files(*.txt)"
        )
        
        if fpath:
            self.ui.pathLineEdit.setText(fpath)

    def preprocess_data(self, fpath):
        data = Data(fpath)
        if "standartize" in self._flags:
            data = Data(data_matrix=DataMatrix.standartize(data.cols, data.rows))

        return data


    def submit_data(self):
        data = self.ui.pathLineEdit.text()
        if data != "Empty file path":
            data = self.preprocess_data(data)
            self.data_submitted.emit(data)
            self.accept()
        else:
            self.reject()