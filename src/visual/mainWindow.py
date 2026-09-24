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

from ..compui.main_window import Ui_mainWindow
from .statsWidget import StatsWidget
from .loadDialog import LoadDialog
from .graphWidget import GraphWidget, GraphType
from .componentAnWidget import ComponentAnalysisWidget
from .settings_window import SettingsDialog
from ..data import Data, DataMatrix
from ..analysis.component import forward, _from_ortogonal, _filter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
        self.data: Data | None = None
        self.eigenvalues, self.eigenvectors, self.ortogonal = None, None, None
        self.subwindows = []
        self.ui.actionLoad.triggered.connect(self.on_actionLoad)
        self.ui.actionSettings.triggered.connect(self.on_actionSettings)
        self.ui.actionForward.triggered.connect(self.on_actionForward)
        self.ui.actionFilter.triggered.connect(self.on_actionFilter)
        self.ui.actionBackward.triggered.connect(self.on_actionBackward)
        self.ui.actionFull.triggered.connect(self.on_actionFullComponent)
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
        if self.data is None:
            loadDialog = LoadDialog(0.05, 0)

        else:
            loadDialog = LoadDialog(self.data.alpha, self.data.dependent)

        loadDialog.data_submitted.connect(self.set_data)
        loadDialog.exec()

    def set_data(self, data: Data):
        if data is None:
            return

        self.data = data

    def set_settings(self, alpha: float, dependent: int):
        if self.data is None:
            return

        self.data = Data(
            data_matrix=DataMatrix(cols=self.data.cols),
            alpha=alpha,
            dependent=dependent,
        )

    def filter_components(self, keep: int):
        filtered_components = _filter(self.data.rows, keep)
        print(filtered_components.shape)
        self.eigenvectors = self.eigenvectors[:, :keep]  # filtered
        self.set_data(Data(data_matrix=DataMatrix(rows=filtered_components)))

    def on_actionSettings(self):
        if self.data is None:
            return

        dialog = SettingsDialog(alpha=self.data.alpha, dependent=self.data.dependent)
        dialog.settings_submitted.connect(self.set_settings)
        dialog.exec()

    def on_actionForward(self):
        if self.data is None:
            return

        self.eigenvalues, self.eigenvectors, self.ortogonal = forward(
            self.data.cols, self.data.mean_vector, self.data.vector_length
        )

        print(len(self.ortogonal))
        self.set_data(Data(data_matrix=DataMatrix(rows=self.ortogonal)))

    def on_actionFilter(self):
        if (
            self.data is None
            or self.eigenvalues is None
            or self.eigenvectors is None
            or self.ortogonal is None
        ):
            return

        widget = ComponentAnalysisWidget(
            self.data,
            self.eigenvalues,
            self.eigenvectors,
            self.ortogonal,
            send_keep=True,
        )
        widget.keep_submitted.connect(self.filter_components)
        widget.exec()

    def on_actionBackward(self):
        if (
            self.data is None
            or self.eigenvalues is None
            or self.eigenvectors is None
            or self.ortogonal is None
        ):
            return

        back = _from_ortogonal(self.data.rows, self.eigenvectors)
        self.set_data(Data(data_matrix=DataMatrix(rows=back)))

    def on_actionFullComponent(self):
        if self.data is None:
            return

        widget = ComponentAnalysisWidget(self.data)
        widget.filtered_submitted.connect(self.set_data)
        widget.exec()

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
