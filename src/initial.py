from itertools import combinations
from math import sqrt
from statistics import mean, stdev

import numpy as np


def mean_vector(columns: list[list[float]]) -> list[float]:
    mean_vector = []
    for vector in columns:
        mean_vector.append(mean(vector))

    return mean_vector


def std_vector(columns: list[list[float]]) -> list[float]:
    std_vector = []
    for vector in columns:
        std_vector.append(stdev(vector))

    return std_vector


def covariance_matrix(
    columns: list[list[float]],
    /,
    n: int | None = None,
    p: int | None = None,
    means: list[float] | None = None,
) -> list[list[float]]:
    if n is None:
        n = len(columns[0])

    if p is None:
        p = len(columns)

    if means is None:
        means = mean_vector(columns)

    cov = [[0.0 for _ in range(p)] for _ in range(p)]

    for i in range(p):
        for j in range(p):
            s = 0.0
            for k in range(n):
                s += (columns[i][k] - means[i]) * (columns[j][k] - means[j])
            cov[i][j] = s / (n - 1)

    return cov


def duo_correlation(cov: float, stddev_psi: float, stddev_eta: float) -> float:
    return (cov) / (stddev_psi * stddev_eta)


def correlation_matrix(
    columns: list[list[float]],
    /,
    p: int | None = None,
    cov_matrix: list[list[float]] | None = None,
    stddev_vector: list[float] | None = None,
) -> list[list[float]]:

    if p is None:
        p = len(columns)

    if cov_matrix is None:
        cov_matrix = covariance_matrix(columns)

    if stddev_vector is None:
        stddev_vector = std_vector(columns)

    d_cor = [[0.0 for _ in range(p)] for _ in range(p)]
    for i in range(p):
        for j in range(p):
            d_cor[j][i] = duo_correlation(
                cov_matrix[i][j], stddev_vector[j], stddev_vector[i]
            )

    return d_cor


def partial_correlation(i: int, j: int, d: int, r: list[list[float]]) -> float:

    return (r[i][j] - (r[i][d] * r[j][d])) / (
        sqrt((1 - (r[i][d] ** 2)) * (1 - (r[j][d] ** 2)))
    )


def partial_correlation_vector(
    columns: list[list[float]],
    /,
    p: int | None = None,
    cor_matrix: list[list[float]] | None = None,
) -> list[float]:

    if p is None:
        p = len(columns)

    if cor_matrix is None:
        cor_matrix = correlation_matrix(columns)

    p_range = range(p)
    p_cor_vector = [0.0 for _ in p_range]
    for e, (i, j) in enumerate(combinations(p_range, p - 1)):
        d = p - i - j
        p_cor_vector[e] = partial_correlation(i, j, d, cor_matrix)

    return p_cor_vector


def det(matrix: list[list[float]]) -> float:
    return np.linalg.det(matrix)


def detk(matrix: list[list[float]], k: int) -> float:
    new_p = len(matrix)
    new = [
        [matrix[i][j] for i in range(new_p) if i != k] for j in range(new_p) if j != k
    ]

    print(k)
    print("#############")
    for row in new:
        print(row)

    print("#############")
    return np.linalg.det(new)


def mult_correlation_vector(
    columns: list[list[float]],
    /,
    p: int | None = None,
    cor_matrix: list[list[float]] | None = None,
) -> list[float]:

    if p is None:
        p = len(columns)

    if cor_matrix is None:
        cor_matrix = correlation_matrix(columns)

    p_range = range(p)
    m_cor_vector = [0.0 for _ in p_range]
    for i, j in combinations(p_range, p - 1):
        d = p - i - j
        m_cor_vector[d] = sqrt(1 - ((det(cor_matrix)) / (detk(cor_matrix, d))))

    return m_cor_vector
