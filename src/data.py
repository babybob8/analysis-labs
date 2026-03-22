from functools import cached_property

from .initial import (
    correlation_matrix,
    covariance_matrix,
    mean_vector,
    mult_correlation_vector,
    mult_correlation_significance_vector,
    partial_correlation_vector,
    partial_correlation_significance_vector,
    partial_correlation_significance_intervals_vector,
    std_vector,
)


class DataMatrix:
    def __init__(self, rows: list[list[float]]):
        if not rows:
            raise ValueError("Empty data")

        row_length = len(rows[0])
        for i, row in enumerate(rows):
            if len(row) != row_length:
                raise ValueError(f"Inconsistent row length at row {i}")

        self._rows = rows

    @property
    def rows(self):
        return self._rows

    @cached_property
    def cols(self) -> list[list[float]]:
        return [list(col) for col in zip(*self._rows)]


class Data:
    def __init__(self, data_matrix: DataMatrix, alpha: float = 0.05) -> None:
        self._data_matrix = data_matrix
        self._alpha = alpha

    @cached_property
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
