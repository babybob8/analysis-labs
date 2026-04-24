from statistics import mean, stdev
from math import sqrt
from scipy.stats import t


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


def correlation_significance_matrix(
    columns: list[list[float]],
    /,
    alpha: float = 0.05,
    N: int | None = None,
    corr_matrix: list[list[float]] | None = None,
) -> list[list[bool]]:
    if N is None:
        N = len(columns[0])

    if corr_matrix is None:
        corr_matrix = correlation_matrix(columns)

    q = t.ppf(1 - (alpha / 2), df=N - 2)

    t_mat = [
        [
            float("inf")
            if abs(1 - r**2) < 1e-12
            else (r * sqrt(N - 2)) / sqrt(1 - r**2)
            for r in row
        ]
        for row in corr_matrix
    ]
    res_mat = [[True if abs(t) > q else False for t in row] for row in t_mat]
    return res_mat
