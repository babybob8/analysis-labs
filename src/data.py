from functools import cached_property
from typing import Self

from .analysis.corelation import (
    mult_correlation_significance_vector,
    mult_correlation_vector,
    partial_correlation_significance_intervals_vector,
    partial_correlation_significance_vector,
    partial_correlation_vector,
)
from .analysis.initial import (
    correlation_matrix,
    correlation_significance_matrix,
    covariance_matrix,
    mean_vector,
    std_vector,
)
from .analysis.regression import RegressionModel, regression
from .parser import parse_vectors_file
from .preprocess import (
    standartize as _standartize,
)


class DataMatrix:
    def __init__(
        self,
        rows: list[list[float]] | None = None,
        cols: list[list[float]] | None = None,
    ):
        if rows is None and cols is None:
            raise ValueError("Empty data")

        if rows is not None and cols is not None:
            raise ValueError("Either rows, or cols")

        if cols is not None:
            col_length = len(cols[0])
            for i, col in enumerate(cols):
                if len(col) != col_length:
                    raise ValueError(f"Inconsistent col length at col {i}")

            self._cols = cols
            self._rows = [list(row) for row in zip(*self._cols)]

        elif rows is not None:
            row_length = len(rows[0])
            for i, row in enumerate(rows):
                if len(row) != row_length:
                    raise ValueError(f"Inconsistent row length at row {i}")

            self._rows = rows
            self._cols = [list(col) for col in zip(*self._rows)]

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    @staticmethod
    def standartize(cols: list[list[float]]) -> Self:
        return DataMatrix(cols=_standartize(cols))


class Data:
    def __init__(
        self,
        src: str | DataMatrix | None,
        /,
        alpha: float = 0.05,
        dependent: int | None = None,
    ) -> None:
        if isinstance(src, str):
            self._data_matrix = DataMatrix(rows=parse_vectors_file(src))

        elif isinstance(src, DataMatrix):
            self._data_matrix = src

        else:
            raise ValueError(f"Weird src: {type(src)}\n {src}")

        if dependent is None:
            dependent = self.dimensions - 1

        self._regr_dependent = dependent
        self._alpha = alpha

    @property
    def dimensions(self) -> int:
        if not self._data_matrix:
            raise RuntimeError("No data vectors came in.")

        return len(self._data_matrix.cols)

    @property
    def rows(self) -> list[list[float]]:
        return self._data_matrix.rows

    @property
    def cols(self) -> list[list[float]]:
        return self._data_matrix.cols

    @property
    def alpha(self) -> float:
        return self._alpha

    @property
    def dependent(self) -> int:
        return self._regr_dependent

    @cached_property
    def vector_length(self) -> int:
        if not self._data_matrix:
            raise RuntimeError("No data vectors came in.")

        return len(self._data_matrix.cols[0])

    @cached_property
    def mean_vector(self) -> list[float]:
        return mean_vector(self._data_matrix.cols)

    @cached_property
    def std_vector(self) -> list[float]:
        return std_vector(self._data_matrix.cols)

    @cached_property
    def covariance_matrix(self) -> list[list[float]]:
        return covariance_matrix(
            self.cols, n=self.vector_length, p=self.dimensions, means=self.mean_vector
        )

    @cached_property
    def correlation_matrix(self) -> list[list[float]]:
        return correlation_matrix(
            self.cols,
            p=self.dimensions,
            cov_matrix=self.covariance_matrix,
            stddev_vector=self.std_vector,
        )

    @cached_property
    def correlation_significance_matrix(self) -> list[list[bool]]:
        return correlation_significance_matrix(
            self.cols,
            alpha=self.alpha,
            N=self.vector_length,
            corr_matrix=self.correlation_matrix,
        )

    @cached_property
    def partial_correlation_vector(self) -> list[float]:
        return partial_correlation_vector(
            self.cols, p=self.dimensions, cor_matrix=self.correlation_matrix
        )

    @cached_property
    def partial_correlation_significance_vector(self) -> list[bool]:
        return partial_correlation_significance_vector(
            self.cols,
            N=self.vector_length,
            alpha=self.alpha,
            part_corr_vec=self.partial_correlation_vector,
        )

    @cached_property
    def partial_correlation_significance_intervals_vector(
        self,
    ) -> list[tuple[float, float]]:
        return partial_correlation_significance_intervals_vector(
            self.cols,
            N=self.vector_length,
            alpha=self.alpha,
            part_corr_vec=self.partial_correlation_vector,
            part_corr_sign_vec=self.partial_correlation_significance_vector,
        )

    @cached_property
    def mult_correlation_vector(self) -> list[float]:
        return mult_correlation_vector(
            self.cols, p=self.dimensions, cor_matrix=self.correlation_matrix
        )

    @cached_property
    def mult_correlation_significance_vector(self) -> list[float]:
        return mult_correlation_significance_vector(
            self.cols,
            alpha=self.alpha,
            N=self.vector_length,
            p=self.dimensions,
            mult_corr_vec=self.mult_correlation_vector,
        )

    @cached_property
    def regression_model(self) -> RegressionModel:
        return regression(
            self.cols,
            alpha=self.alpha,
            stdev_vector=self.std_vector,
            dependent=self.dependent,
            length=self.vector_length,
            dim=self.dimensions,
        )
