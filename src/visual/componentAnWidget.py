from .compui.msc_widget import Ui_mainWidget
from ..data import Data, DataMatrix

from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

from pathlib import Path
from typing import Any

from ..analysis.component import forward, backward

from .table_utils import fill_table
from .graphWidget import GraphType, GraphWidget

class ComponentAnalysisWidget(QDialog):
    filtered_submitted = pyqtSignal(Data)

    def __init__(
        self,
        data: Data
    ):
        super().__init__()
        self.ui = Ui_mainWidget()
        self.ui.setupUi(self)
        
        self.data = data
        
        self.ui.keepSpinBox.setMinimum(1)
        self.ui.keepSpinBox.setMaximum(self.data.dimensions)
        self.ui.keepSpinBox.setValue(self.data.dimensions)
        
        self.ui.filterButtonBox.accepted.connect(self.submit_filtered)
        self.ui.filterButtonBox.rejected.connect(self.reject)
        
        self.eigenvalues, self.eigenvectors, self.ortogonal = forward(self.data.cols, self.data.mean_vector, self.data.vector_length)
        self.fill_match_table()
        self.fill_scatter()
        
    def submit_filtered(self):
        keep = self.ui.keepSpinBox.value()
        back = backward(self.ortogonal, self.eigenvectors, keep)
        self.filtered_submitted.emit(Data(data_matrix=DataMatrix(rows=back)))
        self.accept()
    
    def fill_scatter(self):
        graph = GraphWidget(GraphType.SCATTER, Data(data_matrix=DataMatrix(rows=self.ortogonal)))
        
        layout = QVBoxLayout(self.ui.scatterWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(graph)
    
    def fill_match_table(self):
        uheader = [f"x{i}'" for i in range(1, self.data.dimensions + 1)]
        lheader = [f"x{j}" for j in range(1, self.data.dimensions + 1)]
        lheader.append(r"eigenvalue")
        lheader.append(r"% of")
        lheader.append(r"comb %")
        total = sum(self.eigenvalues)
        pct = [v / total * 100 for v in self.eigenvalues]
        cumulative = []
        acc = 0
        for p in pct:
            acc += p
            cumulative.append(acc)

        filler = (
            self.eigenvectors.T.tolist()
            + [self.eigenvalues]
            + [pct]
            + [cumulative]
        )
        
        fill_table(self.ui.matchTableWidget, filler, uheader, lheader)