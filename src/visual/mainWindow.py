from PyQt6.QtWidgets import QMainWindow, QApplication, QDialog, QFileDialog,  QMdiArea, QMdiSubWindow
from PyQt6.QtCore import pyqtSignal
import sys
import pyqtgraph as pg

from .compui.main_window import Ui_MainWindow
from .statsWidget import StatsWidget
from .loadDialog import LoadDialog


"""
діаграми розкиду - 168
паралельні координати - 170
теплова карта - 173
бульбашкова діаграма - 174
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.__post_init__()

    def __post_init__(self):
        self.data = None
        self.subwindows = []
        self.ui.actionLoad.triggered.connect(self.on_actionLoad)
        self.ui.actionStats.triggered.connect(self.open_stats)
        self.ui.actionClose_All.triggered.connect(self.on_actionCloseAll)

    def on_actionLoad(self):
        loadDialog = LoadDialog()
        loadDialog.data_submitted.connect(self.handleFpath)
        loadDialog.exec()
    
    def handleFpath(self, fpath):
        print(fpath)
        self.data = fpath

    def on_actionCloseAll(self):
        self.ui.mdiArea.closeAllSubWindows()


    def open_stats(self):
        stats = StatsWidget()
        sub = QMdiSubWindow()
        sub.setWidget(stats)
        self.ui.mdiArea.addSubWindow(sub)
        sub.show()
        self.subwindows.append((sub, stats))

# // Debug
if __name__ == "__main__":
    main()

def main():
    app = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec())