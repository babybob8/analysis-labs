from dataclasses import dataclass

import numpy as np


@dataclass
class IterationRecord:
    index: int
    R_h: np.ndarray
    A_hat: np.ndarray
    f_prev: float
    f: float
    h2_new: np.ndarray
    cond_f_decreased: bool
    cond_a_changed: bool
    cond_h_valid: bool
    continue_: bool


def evv(symmetrical_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    vals, vecs = np.linalg.eigh(np.asarray(symmetrical_matrix, dtype=float))
    return vals[::-1], vecs[:, ::-1]


def build_reduced_matrix(R: np.ndarray, h2: np.ndarray) -> np.ndarray:
    R = np.asarray(R, dtype=float)
    h2 = np.asarray(h2, dtype=float)
    if h2.shape[0] != R.shape[0]:
        raise ValueError("h2 length must be equal to n")

    R_h = R.copy()
    np.fill_diagonal(R_h, h2)
    return R_h


def factor_count_reduced(eigen_values: np.ndarray, w_low: int) -> int:
    eigen_values = np.asarray(eigen_values, dtype=float)
    w_high = int((eigen_values > eigen_values.mean()).sum())
    return max(w_low, w_high)


def aprox_factor_count(eigen_values: np.ndarray) -> int:
    return int((np.asarray(eigen_values, dtype=float) > 1).sum())


def max_corr_method(R: np.ndarray) -> np.ndarray:
    off_diag = np.abs(np.asarray(R, dtype=float))
    np.fill_diagonal(off_diag, 0.0)
    return off_diag.max(axis=1)


def triads_method(R: np.ndarray) -> np.ndarray:
    R = np.asarray(R, dtype=float)
    n = R.shape[0]
    h2 = np.empty(n)
    for k in range(n):
        row = np.abs(R[k]).copy()
        row[k] = -1.0
        i, j = np.argsort(row)[::-1][:2]
        h2[k] = abs(R[k, i] * R[k, j] / R[i, j])
    return h2


def mean_method(R: np.ndarray) -> np.ndarray:
    R = np.asarray(R, dtype=float)
    n = R.shape[0]
    off_diag = np.abs(R)
    np.fill_diagonal(off_diag, 0.0)
    return off_diag.sum(axis=1) / (n - 1)


def centroid_method(R: np.ndarray) -> np.ndarray:
    R = np.asarray(R, dtype=float)
    R_c = R.copy()
    np.fill_diagonal(R_c, max_corr_method(R))

    abs_c = np.abs(R_c)
    return abs_c.sum(axis=1) ** 2 / abs_c.sum()


def averoid_method(R: np.ndarray) -> np.ndarray:
    R = np.asarray(R, dtype=float)
    n = R.shape[0]
    abs_r = np.abs(R)
    return n / (n - 1) * abs_r.sum(axis=1) ** 2 / abs_r.sum()


def component_method(R: np.ndarray, w: int | None = None) -> np.ndarray:
    lam, vecs = evv(R)

    if w is None:
        w = int((lam > 1).sum())

    a = vecs[:, :w] * np.sqrt(np.clip(lam[:w], 0, None))
    return (a**2).sum(axis=1)


def _align_signs(A_new: np.ndarray, A_old: np.ndarray) -> np.ndarray:
    k = min(A_new.shape[1], A_old.shape[1])
    signs = np.ones(A_new.shape[1])
    dots = (A_new[:, :k] * A_old[:, :k]).sum(axis=0)
    signs[:k] = np.where(dots < 0, -1.0, 1.0)
    return A_new * signs


def _a_changed(A_new: np.ndarray, A_old: np.ndarray, eps: float) -> bool:
    w = max(A_new.shape[1], A_old.shape[1])
    n = A_new.shape[0]
    new_p = np.zeros((n, w))
    old_p = np.zeros((n, w))
    new_p[:, : A_new.shape[1]] = A_new
    old_p[:, : A_old.shape[1]] = A_old
    return bool(((new_p - old_p) ** 2).sum() > eps)


def compute_loadings_and_f(R_h: np.ndarray, w: int) -> tuple[np.ndarray, float]:
    R_h = np.asarray(R_h, dtype=float)

    lam, vecs = evv(R_h)
    lam_w = np.clip(lam[:w], 0, None)
    A_hat = vecs[:, :w] * np.sqrt(lam_w)

    R_res = R_h - A_hat @ A_hat.T
    mask = ~np.eye(R_h.shape[0], dtype=bool)
    f = float((R_res[mask] ** 2).sum())

    return A_hat, f


def run_iterations(
    R: np.ndarray,
    A_prev: np.ndarray,
    f_prev: float,
    w_low: int,
    /,
    eps: float = 1e-6,
    max_iter: int = 100,
) -> list[IterationRecord]:
    records: list[IterationRecord] = []
    R = np.asarray(R, dtype=float)
    h2 = (A_prev**2).sum(axis=1)

    for i in range(1, max_iter + 1):
        R_h = build_reduced_matrix(R, h2)

        lam, _ = evv(R_h)
        w = factor_count_reduced(lam, w_low)
        A_hat, f = compute_loadings_and_f(R_h, w)
        A_hat = _align_signs(A_hat, A_prev)

        h2_new = (A_hat**2).sum(axis=1)

        c1 = bool(f < f_prev)
        c2 = _a_changed(A_hat, A_prev, eps)
        c3 = bool((h2_new <= 1).all())
        go = c1 and c2 and c3

        records.append(
            IterationRecord(i, R_h, A_hat, f_prev, f, h2_new, c1, c2, c3, go)
        )

        if not go:
            break
        A_prev, f_prev, h2 = A_hat, f, h2_new

    return records
