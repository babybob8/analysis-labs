from .initial import mean_vector
from functools import cached_property

class DataMatrix:
    def __init__(self, rows: list[list[float]]):
        self._rows = rows

    @property
    def rows(self):
        return self._rows

    @cached_property
    def cols(self):
        return [list(col) for col in zip(*self._rows)]

class Data:
    def __init__(self, data_matrix: DataMatrix) -> None:
        self._data_matrix = data_matrix
        
    @cached_property
    def dimensions(self) -> int:
        if not self._data_matrix:
            raise RuntimeError("No data vectors came in.")

        return len(self._data_matrix.cols)

    @cached_property
    def vector_length(self) -> int:
        length = len(self._data_matrix.cols[0])
        for i in range(1, self.dimensions):
            if len(self._data_matrix.cols[i]) == length:
                continue
            else:
                raise RuntimeError(
                    f"Length of all data vectors should be the same; \n\
                    (len(data[0]) = {length}) != (len({i}) = {len(self._data_matrix[i])})"
                )

        return length
    
    @cached_property
    def mean_vector(self) -> list[float]:
        return mean_vector(self._data_matrix.cols)