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
from .componentAnWidget import ComponentAnalysisWidget
from .settingWidget import SettingDialog
from ..data import Data


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
        self.data = None
        self.alpha = 0.05
        self.dependent = 0
        self.subwindows = []
        self.ui.actionLoad.triggered.connect(self.on_actionLoad)
        self.ui.actionAlpha.triggered.connect(self.on_actionAlpha)
        self.ui.actionDependent.triggered.connect(self.on_actionDependent)
        self.ui.actionComponent.triggered.connect(self.on_actionComponent)
        self.ui.actionStats.triggered.connect(self.open_stats)

        self.ui.actionScatter_plot.triggered.connect(
            lambda: self.open_graph(GraphType.SCATTER)
        )
        self.ui.actionParallel_coordinates.triggered.connect(
            lambda: self.open_graph(GraphType.PARALLEL)
        )
        self.ui.actionHeatmap.triggered.connect(
            lambda: self.open_graph(GraphType.HEATMAP)
        )
        self.ui.actionBubble_chart.triggered.connect(
            lambda: self.open_graph(GraphType.BUBBLE)
        )
        self.ui.actionCorrelation_field.triggered.connect(
            lambda: self.open_graph(GraphType.CORRFIELD)
        )
        self.ui.actionDiagnostic_diagram.triggered.connect(
            lambda: self.open_graph(GraphType.DIAGNOSTIC)
        )

        self.ui.actionCloseAll.triggered.connect(self.on_actionCloseAll)

    def on_actionLoad(self):
        loadDialog = LoadDialog(self.alpha, self.dependent)
        loadDialog.data_submitted.connect(self.set_data)
        loadDialog.exec()

    def set_data(self, data):
        self.data = data
        self.alpha = self.data.alpha
        self.dependent = self.data.dependent

    def on_actionAlpha(self):
        dialog = SettingDialog("alpha", alpha=self.alpha)
        dialog.alpha_submitted.connect(self.set_alpha)
        dialog.exec()

    def on_actionDependent(self):
        dialog = SettingDialog("dependent", dependent=self.dependent)
        dialog.dependent_submitted.connect(self.set_dependent)
        dialog.exec()

    def on_actionComponent(self):
        if self.data is None:
            return
        
        widget = ComponentAnalysisWidget(self.data)
        widget.filtered_submitted.connect(self.set_data)
        widget.exec()

    def set_alpha(self, alpha):
        self.alpha = alpha

    def set_dependent(self, dependent):
        self.dependent = dependent

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
