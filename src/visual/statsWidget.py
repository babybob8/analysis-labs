from PyQt6.QtWidgets import QWidget
from .compui.stats_widget import Ui_statsWidget

from ..data import Data

class StatsWidget(QWidget):
    # def __init__(self, data: Data):
    def __init__(self):
        super().__init__()
        self.ui = Ui_statsWidget()
        self.ui.setupUi(self)

    def stats():
        pass