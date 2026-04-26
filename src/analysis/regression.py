from numpy.linalg import inv
from scipy.stats import f, t, chi2
from dataclasses import dataclass
import numpy as np
from .initial import std_vector


vector_t = list[float]
matrix_t = list[list[float]]


def _cutmat(mat: matrix_t, idx: int) -> tuple[matrix_t, vector_t]:
    if idx < 0 or idx >= len(mat):
        raise ValueError("Bad dependent index")

    Y = mat[idx][:]
    cut = [col[:] for i, col in enumerate(mat) if i != idx]
    return cut, Y


def _cutvec(vec: vector_t, idx: int) -> tuple[vector_t, float]:
    if idx < 0 or idx >= len(vec):
        raise ValueError("Bad dependent index")

    Y = vec[idx]
    cut = [val for i, val in enumerate(vec) if i != idx]
    return cut, Y


def _regress_nd(pred: matrix_t, Y: vector_t):
    X = np.array(pred).T
    X_design = np.c_[np.ones(len(Y)), X]
    y = np.array(Y).reshape(-1, 1)

    A_hat = inv(X_design.T @ X_design) @ (X_design.T @ y)

    y_hat = (X_design @ A_hat).flatten().tolist()

    return y_hat, A_hat.flatten().tolist(), X_design


def _r2_coef(Y: vector_t, Y_hat: vector_t) -> tuple[float, float]:
    Y = np.array(Y)
    Y_hat = np.array(Y_hat)
    y_mean = Y.mean()
    SS_tot = np.sum((Y - y_mean) ** 2)
    SS_res = np.sum((Y - Y_hat) ** 2)
    return 1 - SS_res / SS_tot if SS_tot != 0 else 0.0, SS_res


def _regression_significance(
    r2: float, length: int, dim: int, alpha: float = 0.05
) -> bool:
    v1 = dim - 1
    v2 = length - v1
    F = (r2 / (1 - r2)) * (v2 / v1)
    _f = f.ppf(1 - alpha, v1, v2)
    return True if F > _f else False


def _regression_coefs_signif_intervals(
    Y: vector_t,
    Y_hat: vector_t,
    A_hat: vector_t,
    X_design: np.ndarray,
    SS_res: float,
    alpha: float,
    length: int,
    dim: int,
) -> tuple[list[bool], list[float], list[float]]:
    Y = np.array(Y, dtype=float)
    Y_hat = np.array(Y_hat, dtype=float)
    A_hat = np.array(A_hat, dtype=float)

    v = length - dim - 1
    dispersion = SS_res / v

    C = inv(X_design.T @ X_design)
    cov_A = dispersion * C
    ssckk = np.sqrt(np.diag(cov_A))

    t_stats = A_hat / ssckk
    t_crit: float = t.ppf(1 - (alpha / 2), v)

    signif = [abs(t_stat) > t_crit for t_stat in t_stats.tolist()]

    lower = (A_hat - t_crit * ssckk).flatten().tolist()
    upper = (A_hat + t_crit * ssckk).flatten().tolist()

    return signif, lower, upper


def _regression_coefs_standartized(
    A_hat: vector_t, stdev_vector: vector_t, dependent: int
) -> vector_t:
    stdev_x_vec, stdev_y = _cutvec(stdev_vector, dependent)
    return [
        (a_hat * stdev_x) / stdev_y for a_hat, stdev_x in zip(A_hat[1:], stdev_x_vec)
    ]


def _regression_res_var_interval(
    SS_res: float,
    alpha: float,
    length: int,
    dim: int,
) -> tuple[float, float, float]:
    v = length - (dim - 1)
    dispersion_hat = SS_res / v
    alpha1, alpha2 = (1 + (1 - alpha)) / 2, (1 - (1 - alpha)) / 2
    chi2lower, chi2upper = chi2.ppf(alpha2, v), chi2.ppf(alpha1, v)
    lower, upper = SS_res / chi2upper, SS_res / chi2lower

    return (np.sqrt(lower), np.sqrt(dispersion_hat), np.sqrt(upper))


def _regression_val_interval(
    X_design: np.ndarray,
    A_hat: vector_t,
    SS_res: float,
    alpha: float,
    length: int,
    dim: int,
) -> tuple[vector_t, vector_t, vector_t]:
    v = length - dim - 1
    sigma_hat = np.sqrt(SS_res / v)
    C = inv(X_design.T @ X_design)
    t_crit = t.ppf(1 - alpha / 2, v)

    lowers, uppers = [], []
    for x_vec in X_design:
        margin = t_crit * sigma_hat * np.sqrt(1 + (x_vec @ C @ x_vec))
        y_hat_i = np.array(A_hat) @ x_vec
        lowers.append(y_hat_i - margin)
        uppers.append(y_hat_i + margin)

    return lowers, uppers


def _model_error(Y: vector_t, Y_hat: vector_t) -> vector_t:
    return [y - yl for y, yl in zip(Y, Y_hat)]


@dataclass
class RegressionModel:
    Y: vector_t
    Y_hat: vector_t
    A_hat: vector_t
    R2: float
    model_signif: bool
    A_signif: list[bool]
    A_lows: vector_t
    A_uppers: vector_t
    std_A_hat: vector_t
    std_err_of_estimate_interval: tuple[float, float, float]
    Y_intervals: list[tuple[float, float]]
    model_error: vector_t


def regression(
    cols: matrix_t,
    /,
    alpha: float = 0.05,
    stdev_vector: vector_t | None = None,
    dependent: int | None = None,
    length: int | None = None,
    dim: int | None = None,
) -> RegressionModel:
    if dim is None:
        dim = len(cols)

    if length is None:
        length = len(cols[0])

    elif dim != len(cols):
        raise ValueError("dim != len(cols) ??")

    if stdev_vector is None:
        stdev_vector = std_vector(cols)

    if dependent is None:
        dependent = dim - 1

    pred, Y = _cutmat(cols, dependent)
    Y_hat, A_hat, X_design = _regress_nd(pred, Y)
    R2, SS_res = _r2_coef(Y, Y_hat)
    model_signif = _regression_significance(R2, length, dim, alpha)
    A_signif, A_lows, A_uppers = _regression_coefs_signif_intervals(
        Y, Y_hat, A_hat, X_design, SS_res, alpha, length, dim
    )
    A_standartized = _regression_coefs_standartized(A_hat, stdev_vector, dependent)
    res_var_interval = _regression_res_var_interval(SS_res, alpha, length, dim)
    val_intervals = _regression_val_interval(
        X_design, A_hat, SS_res, alpha, length, dim
    )
    err = _model_error(Y, Y_hat)

    return RegressionModel(
        Y,
        Y_hat,
        A_hat,
        R2,
        model_signif,
        A_signif,
        A_lows,
        A_uppers,
        A_standartized,
        res_var_interval,
        val_intervals,
        err,
    )
