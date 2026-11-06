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
    factor_count_reduced,
    max_corr_method,
    mean_method,
    run_iterations,
    triads_method,
)
from ..compui.factors_widget import Ui_MGFWidget
from ..data import Data
from .table_utils import fill_table

METHOD_NAMES = [
    "Max correlation method",
    "Triad's method",
    "Mean's method",
    "Centroid method",
    "Averoid method",
    "Component method",
]


class FactorWidget(QWidget):
    def __init__(self, data: Data):
        super().__init__()
        self.ui = Ui_MGFWidget()
        self.ui.setupUi(self)
        self.data: Data = data
        self.R = np.asarray(self.data.correlation_matrix, dtype=float)

        self.fill_first_step()

        eigenvalues, eigenvectors = evv(self.R)
        self.fill_second_step(eigenvalues, eigenvectors)

        w_first_aprox = aprox_factor_count(eigenvalues)
        self.fill_third_step(w_first_aprox)

        self.fill_fourth_step(w_first_aprox)
        self.fill_fifth_step(w_first_aprox)

        self.iterations: list[IterationRecord] = run_iterations(
            self.R, self.best_a, self.best_f, w_first_aprox
        )

        self.ui.selectionComboBox.addItems(
            [f"{iteration.index}" for iteration in self.iterations]
        )
        self.fill_iteration_view()

        self.ui.selectionComboBox.currentTextChanged.connect(self.fill_iteration_view)

    def fill_first_step(self):
        fill_table(self.ui.corrMatTableWidget, self.R.tolist())

    def fill_second_step(self, eigenvalues: np.ndarray, eigenvectors: np.ndarray):
        vec_header = [f"e{x}" for x in range(len(eigenvalues))]
        fill_table(self.ui.eigenValuesVector, eigenvalues.tolist())
        fill_table(
            self.ui.eigenVectorsTableWidget, eigenvectors.tolist(), header=vec_header
        )

    def fill_third_step(self, w: int):
        fill_table(self.ui.wValue, w)

    def fill_fourth_step(self, w: int):
        self.method_h2 = [
            max_corr_method(self.R),
            triads_method(self.R),
            mean_method(self.R),
            centroid_method(self.R),
            averoid_method(self.R),
            component_method(self.R, w),
        ]
        self.method_rh = [build_reduced_matrix(self.R, h2) for h2 in self.method_h2]

        vec_tables = [
            self.ui.red1VecTableWidget,
            self.ui.red2VecTableWidget,
            self.ui.red3VecTableWidget,
            self.ui.red4VecTableWidget,
            self.ui.red5VecTableWidget,
            self.ui.red6VecTableWidget,
        ]
        mat_tables = [
            self.ui.red1MatTableWidget,
            self.ui.red2MatTableWidget,
            self.ui.red3MatTableWidget,
            self.ui.red4MatTableWidget,
            self.ui.red5MatTableWidget,
            self.ui.red6MatTableWidget,
        ]

        for table, h2 in zip(vec_tables, self.method_h2):
            fill_table(table, h2.tolist())
        for table, rh in zip(mat_tables, self.method_rh):
            fill_table(table, rh.tolist())

    def fill_fifth_step(self, w_low: int):
        self.method_w = []
        results = []
        for rh in self.method_rh:
            lam, _ = evv(rh)
            w = factor_count_reduced(lam, w_low)
            self.method_w.append(w)
            results.append(compute_loadings_and_f(rh, w))

        method_as = [a for a, _ in results]
        method_fs = [f for _, f in results]

        a_tables = [
            self.ui.maxCorrAMatTableWidget,
            self.ui.triadAMatTableWidget,
            self.ui.meanAMatTableWidget,
            self.ui.centroidAMatTableWidget,
            self.ui.averoidAMatTableWidget,
            self.ui.componentAMatTableWidget,
        ]
        f_tables = [
            self.ui.maxCorrfTableWidget,
            self.ui.triadfTableWidget,
            self.ui.meanfTableWidget,
            self.ui.centroidfTableWidget,
            self.ui.averoidfTableWidget,
            self.ui.componentfTableWidget,
        ]

        for table, a in zip(a_tables, method_as):
            fill_table(table, a.tolist())
        for table, f in zip(f_tables, method_fs):
            fill_table(table, f)

        self.best_idx = int(np.argmin(method_fs))
        self.best_w = self.method_w[self.best_idx]
        self.best_a = method_as[self.best_idx]
        self.best_rh = self.method_rh[self.best_idx]
        self.best_f = method_fs[self.best_idx]

        best = f"{METHOD_NAMES[self.best_idx]}, w({self.best_w}), f({self.best_f:.3f})"
        fill_table(self.ui.bestTableWidget, best)

    def fill_iteration_view(self):
        current_index = self.ui.selectionComboBox.currentIndex()
        current_iteration = self.iterations[current_index]

        fill_table(self.ui.viewIterAMatTableWidget, current_iteration.A_hat.tolist())
        fill_table(self.ui.viewIterRhMatTableWidget, current_iteration.R_h.tolist())

        less = "<" if current_iteration.cond_f_decreased else ">="
        c1 = f"{current_iteration.f} {less} {current_iteration.f_prev}"
        fill_table(self.ui.c1TableWidget, c1)

        fill_table(self.ui.c2TableWidget, current_iteration.cond_a_changed)
        fill_table(self.ui.c3TableWidget, current_iteration.cond_h_valid)
