from statistics import mean
from math import sqrt


def mean_vector(columns: list[list[float]]) -> list[float]:
    mean_vector = []
    for vector in columns:
        mean_vector.append(mean(vector))

    return mean_vector


def covariance_matrix(
    columns: list[list[float]],
    /,
    n: int | None = None,
    p: int | None = None,
    means: list[int] | None = None,
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


def correlation_matrix(
    columns: list[list[float]],
    /,
    p: int | None = None,
    cov: list[list[float]] | None = None,
) -> list[list[float]]:
    if p is None:
        p = len(columns)

    if cov is None:
        cov = covariance_matrix(columns)

    corr = [[0.0 for _ in range(p)] for _ in range(p)]

    std = [sqrt(cov[i][i]) for i in range(p)]

    for i in range(p):
        for j in range(p):
            if std[i] == 0 or std[j] == 0:
                corr[i][j] = 0.0
            else:
                corr[i][j] = cov[i][j] / (std[i] * std[j])

    return corr


def partial_correlation_matrix(columns: list[list[float]]) -> list[list[float]]:
    pass
