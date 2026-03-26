from itertools import combinations
from math import sqrt, log, exp
from statistics import mean, stdev
from scipy.stats import t, norm
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
            d_cor[j][i] = d_cor[j][i] if d_cor[j][i] < 1 else 0.99999999999999

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
    
    q = t.ppf(1 - (alpha / 2), df=N-2)
    t_mat = [[((r*sqrt(N-2)) / sqrt(1-r**2)) for r in row] for row in corr_matrix]
    res_mat = [[True if abs(t) > q else False for t in row] for row in t_mat]
    return res_mat


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


def partial_correlation_significance_vector(
    columns: list[list[float]],
    /,
    alpha: float = 0.05,
    N: int | None = None,
    part_corr_vec: list[float] | None = None,
    w: int = 1,
) -> list[bool]:
    if N is None:
        N = len(columns[0])

    if part_corr_vec is None:
        part_corr_vec = partial_correlation_vector(columns)

    v = N - w - 2
    if v <= 0:
        raise ValueError("Not enough degrees of freedom")

    t_stat_vec: list[float] = [
        (coef * sqrt(v)) / (sqrt(1 - (coef**2))) for coef in part_corr_vec
    ]
    q = t.ppf(1 - (alpha / 2), df=v)

    return [True if abs(t_stat) > q else False for t_stat in t_stat_vec]


def partial_correlation_significance_intervals_vector(
    columns: list[list[float]],
    /,
    alpha: float = 0.05,
    N: int | None = None,
    part_corr_vec: list[float] | None = None,
    part_corr_sign_vec: list[bool] | None = None,
    w: int = 1,
) -> list[tuple[float, float]]:
    if N is None:
        N = len(columns[0])

    if part_corr_vec is None:
        part_corr_vec = partial_correlation_vector(columns)

    if part_corr_sign_vec is None:
        part_corr_sign_vec = partial_correlation_significance_vector(
            columns, N=N, alpha=alpha, part_corr_vec=part_corr_vec, w=w
        )

    v = N - w - 3
    if v <= 0:
        raise ValueError("Not enough degrees of freedom")

    v_1_vec = [
        (log((1 + part_corr) / (1 - part_corr)) / 2)
        - (norm.ppf(1 - (alpha / 2)) / sqrt(v))
        for part_corr, signif in zip(part_corr_vec, part_corr_sign_vec)
    ]
    v_2_vec = [
        (log((1 + part_corr) / (1 - part_corr)) / 2)
        + (norm.ppf(1 - (alpha / 2)) / sqrt(v))
        for part_corr in part_corr_vec
    ]

    low_vec = [
        ((exp(2 * v1) - 1) / (exp(2 * v1) + 1)) if significant else float("inf")
        for v1, significant in zip(v_1_vec, part_corr_sign_vec)
    ]
    high_vec = [
        ((exp(2 * v2) - 1) / (exp(2 * v2) + 1)) if significant else float("inf")
        for v2, significant in zip(v_2_vec, part_corr_sign_vec)
    ]

    return list(zip(low_vec, high_vec))


def det(matrix: list[list[float]]) -> float:
    return np.linalg.det(matrix)


def detk(matrix: list[list[float]], k: int) -> float:
    new_p = len(matrix)
    new = [
        [matrix[i][j] for i in range(new_p) if i != k] for j in range(new_p) if j != k
    ]
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


def mult_correlation_significance_vector(
    columns: list[list[float]],
    /,
    alpha: float = 0.05,
    N: int | None = None,
    p: int | None = None,
    mult_corr_vec: list[float] | None = None,
) -> list[float]:
    if p is None:
        p = len(columns)

    if N is None:
        N = len(columns[0])

    if mult_corr_vec is None:
        mult_corr_vec = mult_correlation_vector(columns, p=p)

    f_stat_vec = [
        (((N - p - 1) / (p)) * ((coef**2) / (1 - (coef**2)))) for coef in mult_corr_vec
    ]

    raise NotImplementedError
