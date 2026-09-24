from ..compui.settings_window import Ui_settingsDialog

from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import pyqtSignal


class SettingsDialog(QDialog):
    settings_submitted = pyqtSignal(float, int)

    def __init__(
        self,
        /,
        alpha: float | None = None,
        dependent: float | None = None,
    ):
        super().__init__()
        if alpha is None:
            raise ValueError("Alpha cant be None")

        if dependent is None:
            raise ValueError("Dependent cant be None")

        self.ui = Ui_settingsDialog()
        self.ui.setupUi(self)

        self.ui.alpha_doubleSpinBox.setValue(alpha)
        self.ui.dependent_spinBox.setValue(dependent)

        self.ui.buttonBox.accepted.connect(self.submit_data)
        self.ui.buttonBox.rejected.connect(self.reject)

    def submit_data(self):
        alpha = self.ui.alpha_doubleSpinBox.value()
        dependent = self.ui.dependent_spinBox.value()

        if alpha != None and dependent != None:
            self.settings_submitted.emit(alpha, dependent)
            self.accept()
        else:
            self.reject()
