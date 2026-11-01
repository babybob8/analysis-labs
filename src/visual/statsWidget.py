import logging
from itertools import combinations

from PyQt6.QtWidgets import QWidget

from ..compui.stats_widget import Ui_statsWidget
from ..data import Data
from .table_utils import fill_table


class StatsWidget(QWidget):
    def __init__(self, data: Data | None = None):
        super().__init__()
        self.ui = Ui_statsWidget()
        self.ui.setupUi(self)

        if data is not None:
            self.data = data
            self.fill_stats()

    def _fill_initial(self):
        fill_table(self.ui.lenValue, self.data.vector_length)
        fill_table(self.ui.dimValue, self.data.dimensions)
        fill_table(self.ui.meansVector, self.data.mean_vector)
        fill_table(self.ui.rootSquareMeansVector, self.data.std_vector)
        fill_table(self.ui.corrMatrix, self.data.correlation_matrix)
        fill_table(self.ui.corrSignifMatrix, self.data.correlation_significance_matrix)

    # def _fill_corr(self):
    #     if self.data.dimensions > 3:
    #         return

    #     fill_table(self.ui.covarMatrix, self.data.covariance_matrix)

    #     part_corr_vectors = [
    #         [interval[0], estimate, interval[1]]
    #         for interval, estimate in zip(
    #             self.data.partial_correlation_significance_intervals_vector,
    #             self.data.partial_correlation_vector,
    #         )
    #     ]
    #     part_corr_vectors_header = ["Lower", "Est.", "Upper"]
    #     fill_table(self.ui.partCorrMatrix, part_corr_vectors, part_corr_vectors_header)

    #     part_corr_header = [
    #         f"{a}x{b}" for a, b in combinations(range(self.data.dimensions), 2)
    #     ]
    #     fill_table(
    #         self.ui.partCorrSignifVector,
    #         self.data.partial_correlation_significance_vector,
    #         part_corr_header,
    #     )

    #     mult_corr_header = [
    #         f"{d}x({', '.join(str(i) for i in range(self.data.dimensions) if i != d)})"
    #         for d in range(self.data.dimensions)
    #     ]

    #     fill_table(
    #         self.ui.multCorrVector,
    #         self.data.mult_correlation_vector,
    #         header=mult_corr_header,
    #     )

    def _fill_corr(self):
        fill_table(self.ui.covarMatrix, self.data.covariance_matrix)

        part_corr_vectors = [
            [interval[0], estimate, interval[1]]
            for interval, estimate in zip(
                self.data.partial_correlation_significance_intervals_vector,
                self.data.partial_correlation_vector,
            )
        ]
        part_corr_vectors_header = ["Lower", "Est.", "Upper"]
        part_corr_header = [
            f"{a}x{b}" for a, b in list(combinations(range(self.data.dimensions), 2))
        ]

        fill_table(
            self.ui.partCorrMatrix,
            part_corr_vectors,
            part_corr_vectors_header,
            part_corr_header,
        )

        fill_table(
            self.ui.partCorrSignifVector,
            self.data.partial_correlation_significance_vector,
            part_corr_header,
        )

        mult_corr_header = [
            f"{d}x({', '.join(str(i) for i in range(self.data.dimensions) if i != d)})"
            for d in range(self.data.dimensions)
        ]

        fill_table(
            self.ui.multCorrVector,
            self.data.mult_correlation_vector,
            header=mult_corr_header,
        )

    def _fill_regr(self):
        regr_coefs_u_header = ["Lower", "Est.", "Upper"]
        regr_coefs_l_header = [
            f"a{idx}"
            for idx in range(self.data.dimensions + 1)
            if idx != self.data.dependent + 1
        ]
        regr_coefs_intervals = [
            [
                self.data.regression_model.A_lows[i],
                self.data.regression_model.A_hat[i],
                self.data.regression_model.A_uppers[i],
            ]
            for i in range(self.data.dimensions)
        ]
        fill_table(
            self.ui.regrCoefsIntervals,
            regr_coefs_intervals,
            regr_coefs_u_header,
            regr_coefs_l_header,
        )

        fill_table(
            self.ui.regrCoefsSignif,
            self.data.regression_model.A_signif,
            header=regr_coefs_l_header,
        )

        regr_std_coefs_header = [
            f"a{idx}"
            for idx in range(self.data.dimensions + 1)
            if idx != self.data.dependent + 1 and idx != 0
        ]
        fill_table(
            self.ui.regrStdCoefs,
            self.data.regression_model.std_A_hat,
            header=regr_std_coefs_header,
        )

        fill_table(self.ui.determinationCoef, self.data.regression_model.R2)
        fill_table(self.ui.modelSignif, self.data.regression_model.model_signif)
        fill_table(
            self.ui.stdInterval,
            [*self.data.regression_model.std_err_of_estimate_interval],
            header=regr_coefs_u_header,
        )

        lowers, uppers = self.data.regression_model.Y_intervals
        modelIntervals = [
            [low, est, up]
            for low, est, up in zip(lowers, self.data.regression_model.Y_hat, uppers)
        ]
        fill_table(self.ui.modelInterval, modelIntervals, header=regr_coefs_u_header)

    def fill_stats(self):
        self._fill_initial()
        self._fill_corr()
        self._fill_regr()
