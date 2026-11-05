import numpy as np
from PyQt6.QtWidgets import QWidget

from ..analysis.factor import (
    IterationRecord,
    aprox_factor_count,
    averoid_method,
    build_reduced_matrix,
    centroid_method,
    component_method,
    compute_loadings_and_f,
    evv,
    max_corr_method,
    mean_method,
    run_iterations,
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

        self.fill_fifth_step(w_first_aprox)

        self.iterations: list[IterationRecord] = run_iterations(
            self.data.correlation_matrix, self.best_a, self.best_f, w_first_aprox
            # self.best_rh, self.best_a, self.best_f, w_first_aprox
        )

        self.ui.selectionComboBox.addItems(
            [f"{iteration.index}" for iteration in self.iterations]
        )
        self.fill_iteration_view()

        self.ui.selectionComboBox.currentTextChanged.connect(self.fill_iteration_view)

    def fill_first_step(self):
        fill_table(
            self.ui.corrMatTableWidget,
            self.data.correlation_matrix,
        )

    def fill_second_step(self, eigenvalues, eigenvectors):        
        vec_header = [f"e{x}" for x in range(len(eigenvalues))]
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

        self.triad_h2 = triads_method(self.data.correlation_matrix)
        self.triad_rh = build_reduced_matrix(
            self.data.correlation_matrix, self.triad_h2
        )

        fill_table(self.ui.red2VecTableWidget, self.triad_h2)
        fill_table(self.ui.red2MatTableWidget, self.triad_rh)

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

        self.method_h2 = [
            self.max_corr_h2,
            self.triad_h2,
            self.mean_h2,
            self.centroid_h2,
            self.averoid_h2,
            self.component_h2,
        ]
        self.method_rh = [
            self.max_corr_rh,
            self.triad_rh,
            self.mean_rh,
            self.centroid_rh,
            self.averoid_rh,
            self.component_rh,
        ]

    def fill_fifth_step(self, w):
        max_corr_ahat, max_corr_f = compute_loadings_and_f(self.max_corr_rh, w)
        triad_ahat, triad_f = compute_loadings_and_f(self.triad_rh, w)
        mean_ahat, mean_f = compute_loadings_and_f(self.mean_rh, w)
        centroid_ahat, centroid_f = compute_loadings_and_f(self.centroid_rh, w)
        averoid_ahat, averoid_f = compute_loadings_and_f(self.averoid_rh, w)
        component_ahat, component_f = compute_loadings_and_f(self.component_rh, w)

        fill_table(self.ui.maxCorrAMatTableWidget, max_corr_ahat.tolist())
        fill_table(self.ui.triadAMatTableWidget, triad_ahat.tolist())
        fill_table(self.ui.meanAMatTableWidget, mean_ahat.tolist())
        fill_table(self.ui.centroidAMatTableWidget, centroid_ahat.tolist())
        fill_table(self.ui.averoidAMatTableWidget, averoid_ahat.tolist())
        fill_table(self.ui.componentAMatTableWidget, component_ahat.tolist())

        fill_table(self.ui.maxCorrfTableWidget, max_corr_f)
        fill_table(self.ui.triadfTableWidget, triad_f)
        fill_table(self.ui.meanfTableWidget, mean_f)
        fill_table(self.ui.centroidfTableWidget, centroid_f)
        fill_table(self.ui.averoidfTableWidget, averoid_f)
        fill_table(self.ui.componentfTableWidget, component_f)

        method_fs = [max_corr_f, triad_f, mean_f, centroid_f, averoid_f, component_f]
        method_as = [
            max_corr_ahat,
            triad_ahat,
            mean_ahat,
            centroid_ahat,
            averoid_ahat,
            component_ahat,
        ]
        method_names = [
            "Max correlation method",
            "Triad's method",
            "Mean's method",
            "Centroid method",
            "Averoid method",
            "Component method",
        ]
        self.best_idx = np.argmin(method_fs)
        self.best_a = method_as[self.best_idx]
        self.best_rh = self.method_rh[self.best_idx]
        self.best_f = method_fs[self.best_idx]
        best = f"{method_names[self.best_idx]}, f({self.best_f:.3f})"

        fill_table(self.ui.bestTableWidget, best)

    def fill_iteration_view(self):
        current_index = self.ui.selectionComboBox.currentIndex()
        current_iteration = self.iterations[current_index]
        fill_table(
            self.ui.viewIterAMatTableWidget,
            current_iteration.A_hat.tolist(),
        )
        fill_table(
            self.ui.viewIterRhMatTableWidget,
            current_iteration.R_h.tolist(),
        )

        less = "<" if current_iteration.cond_f_decreased else ">="
        c1 = f"{current_iteration.f} {less} {current_iteration.f_prev}"
        fill_table(self.ui.c1TableWidget, c1)

        fill_table(self.ui.c2TableWidget, current_iteration.cond_a_changed)
        fill_table(self.ui.c3TableWidget, current_iteration.cond_h_valid)
