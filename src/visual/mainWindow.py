from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QDialog,
    QFileDialog,
    QMdiArea,
    QMdiSubWindow,
)
from PyQt6.QtCore import pyqtSignal
import sys
import pyqtgraph as pg

from .compui.main_window import Ui_mainWindow
from .statsWidget import StatsWidget
from .loadDialog import LoadDialog
from .graphWidget import GraphWidget, GraphType


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
        self.data = None
        self.subwindows = []
        self.ui.actionLoad.triggered.connect(self.on_actionLoad)
        
        self.ui.actionStats.triggered.connect(self.open_stats)
        
        self.ui.actionScatter_plot.triggered.connect(lambda: self.open_graph(GraphType.SCATTER))
        self.ui.actionParallel_coordinates.triggered.connect(lambda: self.open_graph(GraphType.PARALLEL))
        self.ui.actionHeatmap.triggered.connect(lambda: self.open_graph(GraphType.HEATMAP))
        self.ui.actionBubble_chart.triggered.connect(lambda: self.open_graph(GraphType.BUBBLE))
        
        self.ui.actionCloseAll.triggered.connect(self.on_actionCloseAll)

    def on_actionLoad(self):
        loadDialog = LoadDialog()
        loadDialog.data_submitted.connect(self.set_data)
        loadDialog.exec()

    def set_data(self, data):
        self.data = data

    def on_actionCloseAll(self):
        self.ui.mdiArea.closeAllSubWindows()

    def open_stats(self):
        stats = StatsWidget(self.data)
        sub = QMdiSubWindow()
        sub.setWidget(stats)
        self.ui.mdiArea.addSubWindow(sub)
        sub.show()
        self.subwindows.append((sub, stats))
        
    def open_graph(self, gtype: GraphType):
        graph = GraphWidget(gtype, self.data)
        sub = QMdiSubWindow()
        sub.setWidget(graph)
        self.ui.mdiArea.addSubWindow(sub)
        sub.show()
        self.subwindows.append((sub, graph))
        
    
