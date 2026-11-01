import datetime
import logging
import sys
from pathlib import Path

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QMainWindow,
    QMdiArea,
    QMdiSubWindow,
)

from ..analysis.component import _filter, _from_ortogonal, forward
from ..compui.main_window import Ui_mainWindow
from ..data import Data, DataMatrix
from ..filter import filter_3sigma
from .componentAnWidget import ComponentAnalysisWidget
from .factorWidget import FactorWidget
from .graphWidget import GraphType, GraphWidget
from .loadDialog import LoadDialog
from .logsWidget import LogsWidget
from .settings_window import SettingsDialog
from .statsWidget import StatsWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
        self.data: Data | None = None
        self.eigenvalues, self.eigenvectors, self.ortogonal = None, None, None
        self.current_log: str | None = None
        self.subwindows = []

        self.logs_dir = None
        self.log_file_path = None
        self.setup_logs()
        self.on_actionLogs()

        self.ui.actionLoad.triggered.connect(self.on_actionLoad)
        self.ui.actionSettings.triggered.connect(self.on_actionSettings)
        self.ui.actionForward.triggered.connect(self.on_actionForward)
        self.ui.actionFilter.triggered.connect(self.on_actionFilter)
        self.ui.actionBackward.triggered.connect(self.on_actionBackward)
        self.ui.actionFull.triggered.connect(self.on_actionFullComponent)
        self.ui.actionFactor.triggered.connect(self.on_actionFactor)
        self.ui.actionStats.triggered.connect(self.open_stats)
        self.ui.action3_sigma.triggered.connect(self.on_action3sigma)
        self.ui.actionLogs.triggered.connect(self.on_actionLogs)

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
            DataMatrix(cols=self.data.cols),
            alpha=alpha,
            dependent=dependent,
        )
        logging.debug(f"Set settings to: alpha({alpha}), dependent({dependent})")

    def filter_components(self, keep: int):
        filtered_components = _filter(self.data.rows, keep)
        self.eigenvectors = self.eigenvectors[:, :keep]  # filtered
        self.set_data(Data(DataMatrix(rows=filtered_components)))

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

        self.set_data(Data(DataMatrix(rows=self.ortogonal)))

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
        self.set_data(Data(DataMatrix(rows=back)))

    def on_actionFullComponent(self):
        if self.data is None:
            return

        widget = ComponentAnalysisWidget(self.data)
        widget.filtered_submitted.connect(self.set_data)
        widget.exec()

    def on_actionFactor(self):
        if self.data is None:
            return

        self.open_factor()

    def on_action3sigma(self):
        if self.data is None:
            return

        self.data = filter_3sigma(self.data)
        logging.debug("Filtered data with 3sigma filter")

    def on_actionCloseAll(self):
        self.ui.mdiArea.closeAllSubWindows()
        logging.debug("Closed all subwindows")

    def on_actionLogs(self):
        if (self.log_file_path is None) or (self.logs_dir is None):
            logging.error("Uninitialized params: self.log_file_path, self.logs_dir")

        logs = LogsWidget(self.log_file_path, self.logs_dir)
        sub = QMdiSubWindow()
        sub.setWidget(logs)
        self.ui.mdiArea.addSubWindow(sub)
        sub.show()
        self.subwindows.append((sub, logs))

    def setup_logs(self):
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

        current_log_name = (
            f"mst_{datetime.datetime.now().strftime(r'%d-%m-%Y_%H:%M:%S')}.log"
        )
        self.log_file_path = self.logs_dir / current_log_name

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(module)s.%(funcName)s: %(message)s",
            handlers=[
                logging.FileHandler(self.log_file_path, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

    def open_stats(self):
        stats = StatsWidget(self.data)
        sub = QMdiSubWindow()
        sub.setWidget(stats)
        self.ui.mdiArea.addSubWindow(sub)
        sub.show()
        self.subwindows.append((sub, stats))
        logging.debug("Opened stats widget")

    def open_factor(self):
        factor = FactorWidget(self.data)
        sub = QMdiSubWindow()
        sub.setWidget(factor)
        self.ui.mdiArea.addSubWindow(sub)
        sub.show()
        self.subwindows.append((sub, factor))
        logging.debug("Opened factor widget")

    def open_graph(self, gtype: GraphType):
        graph = GraphWidget(gtype, self.data)
        sub = QMdiSubWindow()
        sub.setWidget(graph)
        sub.resize(600, 600)
        self.ui.mdiArea.addSubWindow(sub)
        sub.show()
        self.subwindows.append((sub, graph))
        logging.debug(f"Opened graph widget: {gtype.name}")
