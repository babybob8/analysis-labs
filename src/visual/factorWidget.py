from PyQt6.QtWidgets import QWidget

from ..analysis.factor import (
    aprox_factor_count,
    averoid_method,
    build_reduced_matrix,
    centroid_method,
    component_method,
    evv,
    max_corr_method,
    mean_method,
    triads_method,
)
from ..compui.factors_widget import Ui_MGFWidget
from ..data import Data
from .table_utils import fill_table


class FactorWidget(QWidget):
    def __init__(self, data: Data):
        super().__init__()
        self.ui = Ui_MGFWidget()
        self.ui.setupUi(self)
        self.data: Data = data

        self.fill_first_step()

        eigenvalues, eigenvectors = evv(self.data.correlation_matrix)
        self.fill_second_step(eigenvalues, eigenvectors)

        w_first_aprox = aprox_factor_count(eigenvalues)
        self.fill_third_step(w_first_aprox)

        self.fill_fourth_step(w_first_aprox)

    def fill_first_step(self):
        fill_table(
            self.ui.corrMatTableWidget,
            self.data.correlation_matrix,
        )

    def fill_second_step(self, eigenvalues, eigenvectors):
        vec_header = [f"x{x}" for x in range(len(eigenvalues))]
        fill_table(self.ui.eigenValuesVector, eigenvalues)
        fill_table(self.ui.eigenVectorsTableWidget, eigenvectors, header=vec_header)

    def fill_third_step(self, w):
        fill_table(self.ui.wValue, w)

    def fill_fourth_step(self, w):
        self.max_corr_h2 = max_corr_method(self.data.correlation_matrix)
        self.max_corr_rh = build_reduced_matrix(
            self.data.correlation_matrix, self.max_corr_h2
        )

        fill_table(self.ui.red1VecTableWidget, self.max_corr_h2)
        fill_table(self.ui.red1MatTableWidget, self.max_corr_rh)

        self.triads_h2 = triads_method(self.data.correlation_matrix)
        self.triads_rh = build_reduced_matrix(
            self.data.correlation_matrix, self.triads_h2
        )

        fill_table(self.ui.red2VecTableWidget, self.triads_h2)
        fill_table(self.ui.red2MatTableWidget, self.triads_rh)

        self.mean_h2 = mean_method(self.data.correlation_matrix)
        self.mean_rh = build_reduced_matrix(self.data.correlation_matrix, self.mean_h2)

        fill_table(self.ui.red3VecTableWidget, self.mean_h2)
        fill_table(self.ui.red3MatTableWidget, self.mean_rh)

        self.centroid_h2 = centroid_method(self.data.correlation_matrix)
        self.centroid_rh = build_reduced_matrix(
            self.data.correlation_matrix, self.centroid_h2
        )

        fill_table(self.ui.red4VecTableWidget, self.centroid_h2)
        fill_table(self.ui.red4MatTableWidget, self.centroid_rh)

        self.averoid_h2 = averoid_method(self.data.correlation_matrix)
        self.averoid_rh = build_reduced_matrix(
            self.data.correlation_matrix, self.averoid_h2
        )

        fill_table(self.ui.red5VecTableWidget, self.averoid_h2)
        fill_table(self.ui.red5MatTableWidget, self.averoid_rh)

        self.component_h2 = component_method(self.data.correlation_matrix, w)
        self.component_rh = build_reduced_matrix(
            self.data.correlation_matrix, self.component_h2
        )

        fill_table(self.ui.red6VecTableWidget, self.component_h2)
        fill_table(self.ui.red6MatTableWidget, self.component_rh)

    def fill_fifth_step(self):
        # TODO
        pass
