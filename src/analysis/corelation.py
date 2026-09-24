from itertools import combinations
from math import sqrt, log, exp
from scipy.stats import t, norm
import numpy as np


from .initial import correlation_matrix


def _det(matrix: list[list[float]]) -> float:
    return np.linalg.det(matrix)


def _detk(matrix: list[list[float]], k: int) -> float:
    new_p = len(matrix)
    new = [
        [matrix[i][j] for i in range(new_p) if i != k] for j in range(new_p) if j != k
    ]
    return np.linalg.det(new)


def partial_correlation(
    i: int, j: int, cond: frozenset, r: list[list[float]], cache: dict | None = None
) -> float:
    if cache is None:
        cache = {}

    key = (frozenset((i, j)), cond)
    if key in cache:
        return cache[key]

    if not cond:
        value = r[i][j]
    else:
        d = next(iter(cond))
        rest = cond - {d}

        r_ij = partial_correlation(i, j, rest, r, cache)
        r_id = partial_correlation(i, d, rest, r, cache)
        r_jd = partial_correlation(j, d, rest, r, cache)

        value = (r_ij - r_id * r_jd) / sqrt((1 - r_id**2) * (1 - r_jd**2))

    cache[key] = value
    return value


def partial_correlation_matrix(
    columns: list[list[float]],
    /,
    p: int | None = None,
    cor_matrix: list[list[float]] | None = None,
) -> list[float]:
    if p is None:
        p = len(columns)

    if cor_matrix is None:
        cor_matrix = correlation_matrix(columns)

    cache = {}
    full = frozenset(range(p))
    result = [[0.0] * p for _ in range(p)]

    for i, j in combinations(range(p), 2):
        cond = full - {i, j}
        value = partial_correlation(i, j, cond, cor_matrix, cache)
        value = max(-1.0 + 1e-15, min(1.0 - 1e-15, value))
        result[i][j] = result[j][i] = value

    return result


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

    matrix = partial_correlation_matrix(columns, p, cor_matrix)
    vector = [matrix[i][j] for i, j in list(combinations(range(p), 2))]

    return vector


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
        (coef * sqrt(v)) / sqrt(max(0.0, 1 - coef**2)) if abs(coef) < 1.0 else float('inf')
        for coef in part_corr_vec
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

    det_r = _det(cor_matrix)
    return [sqrt(max(0.0, 1 - det_r / _detk(cor_matrix, d))) for d in range(p)]


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
