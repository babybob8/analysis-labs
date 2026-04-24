from itertools import combinations

from PyQt6.QtWidgets import QWidget
from .compui.stats_widget import Ui_statsWidget
from .table_utils import fill_table
from ..data import Data


class StatsWidget(QWidget):
    def __init__(self, data: Data | None):
        super().__init__()
        self.ui = Ui_statsWidget()
        self.ui.setupUi(self)

        if data is not None:
            self.data = data
            self.fill_stats()

    def fill_stats(self):
        
        fill_table(self.ui.lenValue, self.data.vector_length)
        fill_table(self.ui.dimValue, self.data.dimensions)
        fill_table(self.ui.meansVector, self.data.mean_vector)
        fill_table(self.ui.rootSquareMeansVector, self.data.std_vector)
        fill_table(self.ui.corrMatrix, self.data.correlation_matrix)
        fill_table(self.ui.corrSignifMatrix, self.data.correlation_significance_matrix)

        fill_table(self.ui.covarMatrix, self.data.covariance_matrix)

        part_corr_vectors = [
            [interval[0], estimate, interval[1]]
            for interval, estimate in zip(
                self.data.partial_correlation_significance_intervals_vector,
                self.data.partial_correlation_vector,
            )
        ]
        part_corr_vectors_header = ["Lower",  "Est.", "Upper"]
        fill_table(self.ui.partCorrMatrix, part_corr_vectors, part_corr_vectors_header)

        part_corr_header = [
            f"{a}x{b}"
            for a, b in combinations(
                range(self.data.dimensions), self.data.dimensions - 1
            )
        ]
        fill_table(
            self.ui.partCorrSignifVector,
            self.data.partial_correlation_significance_vector,
            part_corr_header,
        )
        
        mult_corr_header = ["" for _ in range(self.data.dimensions)]
        for i, j in combinations(range(self.data.dimensions), self.data.dimensions-1):
            d = self.data.dimensions - i - j
            mult_corr_header[d] = f"{d}x({i}, {j})"

        fill_table(self.ui.multCorrVector, self.data.mult_correlation_vector, header=mult_corr_header)