from functools import cached_property
from typing import Self
from math import sqrt

from .parser import parse_vectors_file

from .analysis.initial import (
    correlation_matrix,
    correlation_significance_matrix,
    covariance_matrix,
    mean_vector,
    std_vector,
)

from .analysis.corelation import (
    mult_correlation_vector,
    mult_correlation_significance_vector,
    partial_correlation_vector,
    partial_correlation_significance_vector,
    partial_correlation_significance_intervals_vector,
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

    @staticmethod
    def standartize(cols, rows) -> Self:

        means = []
        stds = []

        for col in cols:
            mean = sum(col) / len(col)
            variance = sum((x - mean) ** 2 for x in col) / len(col)
            std = sqrt(variance)

            means.append(mean)
            stds.append(std)

        new_rows = []
        for row in rows:
            new_row = []
            for j, x in enumerate(row):
                std = stds[j]
                if std == 0:
                    new_row.append(0.0)
                else:
                    new_row.append((x - means[j]) / std)
            new_rows.append(new_row)

        return DataMatrix(new_rows)


class Data:
    def __init__(self, fpath: str, alpha: float = 0.05, /, data_matrix: DataMatrix | None = None) -> None:
        if data_matrix:
            self._data_matrix = data_matrix

        else:
            self._data_matrix = DataMatrix(parse_vectors_file(fpath))

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
    def correlation_significance_matrix(self) -> list[list[float]]:
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
