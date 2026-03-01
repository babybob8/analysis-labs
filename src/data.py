from .initial import mean_vector, covariance_matrix, correlation_matrix
from functools import cached_property


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
    def __init__(self, data_matrix: DataMatrix) -> None:
        self._data_matrix = data_matrix

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

    @cached_property
    def vector_length(self) -> int:
        if not self._data_matrix:
            raise RuntimeError("No data vectors came in.")

        return len(self._data_matrix.cols[0])

    @cached_property
    def mean_vector(self) -> list[float]:
        return mean_vector(self._data_matrix.cols)

    @cached_property
    def covariance_matrix(self) -> list[list[float]]:
        return covariance_matrix(
            self.cols, n=self.vector_length, p=self.dimensions, means=self.mean_vector
        )

    @cached_property
    def correlation_matrix(self) -> list[list[float]]:
        return correlation_matrix(
            self.cols, p=self.dimensions, cov=self.covariance_matrix
        )
