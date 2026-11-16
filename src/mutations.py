import logging
from collections.abc import Callable
from dataclasses import dataclass
from functools import reduce

import numpy as np

from .data import Data

Mutation = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class MutationRequest:
    features: tuple[int, ...]
    addition: float | None = None
    multiplication: float | None = None
    apply_ln: bool = False

    @property
    def has_mutations(self) -> bool:
        return (
            self.addition is not None
            or self.multiplication is not None
            or self.apply_ln
        )


def compose(*mutations: Mutation) -> Mutation:
    return lambda column: reduce(lambda acc, f: f(acc), mutations, column)


def add(value: float) -> Mutation:
    return lambda column: column + value


def multiply(value: float) -> Mutation:
    return lambda column: column * value


def natural_log(column: np.ndarray) -> np.ndarray:
    if np.any(column <= 0):
        logging.error("ln requires strictly positive values")
        raise ValueError("ln requires strictly positive values")
    return np.log(column)


def build_mutations(request: MutationRequest) -> tuple[Mutation, ...]:
    candidates = (
        add(request.addition) if request.addition is not None else None,
        (
            multiply(request.multiplication)
            if request.multiplication is not None
            else None
        ),
        natural_log if request.apply_ln else None,
    )
    return tuple(m for m in candidates if m is not None)


def apply_request(data: np.ndarray, request: MutationRequest) -> Data:
    pipeline = compose(*build_mutations(request))
    selected = frozenset(request.features)

    result = np.asarray(data, dtype=float).copy()

    for index in selected:
        result[index] = pipeline(result[index])

    return Data(result.tolist())
