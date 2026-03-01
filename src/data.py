from .initial import mean_vector


class Data:
    def __init__(self, parsed_data: list[list[float]]) -> None:
        self._outdated = False
        self._data = parsed_data
        self._dim = self.find_dim()
        self._len = self.find_len()

        self._mean_vector = None

    def find_dim(self) -> int:
        if not self._data:
            raise RuntimeError("No data vectors came in.")

        return len(self._data)

    def get_dim(self) -> int:
        if not self._dim:
            raise RuntimeError("No _dim attribute; somehow.")

        return self._dim

    def find_len(self) -> int:
        length = len(self._data[0])
        for i in range(1, self._dim):
            if len(self._data[i]) == length:
                continue
            else:
                raise RuntimeError(
                    f"Length of all data vectors should be the same; \n\
                    (len(data[0]) = {length}) != (len({i}) = {len(self._data[i])})"
                )

        return length

    def get_len(self) -> int:
        if not self._len:
            raise RuntimeError("No _len attribute; somehow.")

        return self._len

    # TODO
    def set_data(self, parsed_data: list[list[float]]) -> None:
        self._outdated = True

        raise NotImplementedError

    def get_data(self) -> list[list[float]]:
        if not self._data:
            raise RuntimeError("No _data attribute; somehow.")

        return self._data

    def is_outdated(self) -> bool:
        return self._outdated

    def set_mean_vector(self, mean_vector: list[float]) -> None:
        if not mean_vector:
            raise RuntimeError("No mean_vector came in; somehow.")

        self._mean_vector = mean_vector

    def get_mean_vector(self) -> list[float] | None:
        if not self._mean_vector:
            return None

        return self._mean_vector

    def mean_vector(self) -> list[float]:
        if not self.is_outdated() and (cached := self.get_mean_vector()) is not None:
            return cached

        cache = mean_vector(self.get_data())
        self.set_mean_vector(cache)
        return cache
