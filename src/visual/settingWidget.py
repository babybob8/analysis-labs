from .compui.alpha_setting import Ui_alphaDialog
from .compui.dependent_setting import Ui_dependentDialog
from ..data import Data, DataMatrix

from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import pyqtSignal

from pathlib import Path
from typing import Any


class SettingDialog(QDialog):
    alpha_submitted = pyqtSignal(float)
    dependent_submitted = pyqtSignal(int)

    def __init__(
        self,
        setting: str,
        /,
        alpha: float | None = None,
        dependent: float | None = None,
    ):
        super().__init__()
        if setting == "alpha":
            if alpha is None:
                raise ValueError("Alpha cant be None")

            self.ui = Ui_alphaDialog()
            self.ui.setupUi(self)
            self.ui.doubleSpinBox.setValue(alpha)

        elif setting == "dependent":
            if dependent is None:
                raise ValueError("Dependent cant be None")

            self.ui = Ui_dependentDialog()
            self.ui.setupUi(self)
            self.ui.spinBox.setValue(dependent)

        self.setting = setting
        self.ui.buttonBox.accepted.connect(self.submit_data)
        self.ui.buttonBox.rejected.connect(self.reject)

    def submit_data(self):
        if self.setting == "alpha":
            data = self.ui.doubleSpinBox.value()
            if data != None:
                self.alpha_submitted.emit(data)
                self.accept()
            else:
                self.reject()

        elif self.setting == "dependent":
            data = self.ui.spinBox.value()
            if data != None:
                self.dependent_submitted.emit(data)
                self.accept()
            else:
                self.reject()
