from ast import iter_child_nodes
from dataclasses import dataclass

import numpy as np


@dataclass
class IterationRecord:
    index: int
    R_h: np.ndarray  # in
    A_hat: np.ndarray  # out
    f_prev: float
    f: float
    h2_new: np.ndarray
    cond_f_decreased: bool
    cond_a_changed: bool
    cond_h_valid: bool
    continue_: bool


def evv(symmetrical_matrix: list[list[float]]):
    vals, vecs = np.linalg.eigh(symmetrical_matrix)
    vals = vals[::-1]
    vecs = vecs[:, ::-1]
    return vals.tolist(), vecs.tolist()


def build_reduced_matrix(R: list[list[float]], h2: list[float]) -> list[list[float]]:
    n = len(R)
    if len(h2) != n:
        raise ValueError

    Rh = [row[:] for row in R]
    for k in range(n):
        Rh[k][k] = h2[k]
    return Rh


def aprox_factor_count(eigen_values: list[float], rh: bool = False) -> int:
    low = 0
    for v in eigen_values:
        if v > 1:
            low += 1

    if rh:
        high = 0
        mean = np.mean(eigen_values)
        for v in eigen_values:
            if v > mean:
                high += 1

        return high if high > low else low

    return low


def max_corr_method(R: list[list[float]]) -> list[float]:
    n = len(R)
    h2 = []
    for k in range(n):
        h2.append(max(abs(R[k][v]) for v in range(n) if v != k))
    return h2


def triads_method(R: list[list[float]]) -> list[float]:
    n = len(R)
    h2 = []
    for k in range(n):
        others = sorted(
            (v for v in range(n) if v != k),
            key=lambda v: abs(R[k][v]),
            reverse=True,
        )
        i, j = others[0], others[1]
        h2.append(abs(R[k][i] * R[k][j] / R[i][j]))
    return h2


def mean_method(R: list[list[float]]) -> list[float]:
    n = len(R)
    h2 = []
    for k in range(n):
        s = sum(abs(R[k][v]) for v in range(n) if v != k)
        h2.append(s / (n - 1))
    return h2


def centroid_method(R: list[list[float]]) -> list[float]:
    n = len(R)

    Rc = [row[:] for row in R]
    for k in range(n):
        Rc[k][k] = max(abs(Rc[k][v]) for v in range(n) if v != k)

    total = sum(abs(Rc[i][j]) for i in range(n) for j in range(n))

    h2 = []
    for k in range(n):
        row_sum = sum(abs(Rc[k][v]) for v in range(n))
        h2.append(row_sum**2 / total)
    return h2


def averoid_method(R: list[list[float]]) -> list[float]:
    n = len(R)
    total = sum(abs(R[i][j]) for i in range(n) for j in range(n))

    h2 = []
    for k in range(n):
        row_sum = sum(abs(R[k][v]) for v in range(n))
        h2.append(n / (n - 1) * row_sum**2 / total)
    return h2


def component_method(R: list[list[float]], w: int | None = None) -> list[float]:
    lam, e = np.linalg.eigh(np.array(R, dtype=float))

    idx = np.argsort(lam)[::-1]
    lam, e = lam[idx], e[:, idx]

    if w is None:
        w = int((lam > 1).sum())

    a = e[:, :w] * np.sqrt(lam[:w])

    return (a**2).sum(axis=1).tolist()


def compute_loadings_and_f(R_h, w: int):
    R_h = np.asarray(R_h, dtype=float)

    lam, E = np.linalg.eigh(R_h)
    idx = np.argsort(lam)[::-1][:w]
    lam_w = np.clip(lam[idx], 0, None)
    A_hat = E[:, idx] * np.sqrt(lam_w)

    R_res = R_h - A_hat @ A_hat.T
    mask = ~np.eye(R_h.shape[0], dtype=bool)
    f = float((R_res[mask] ** 2).sum())

    return A_hat, f


def run_iterations(
    R: list[list[float]],
    A_prev: np.ndarray,
    f_prev: float,
    w: int,
    /,
    eps=1e-6,
    max_iter=100,
) -> list[IterationRecord]:
    records = []
    R_arr = np.asarray(R, dtype=float)
    h2 = (A_prev**2).sum(axis=1)

    for i in range(1, max_iter + 1):
        R_h = np.array(build_reduced_matrix(R_arr.tolist(), h2.tolist()))

        A_hat, f = compute_loadings_and_f(R_h, w)

        signs = np.sign((A_hat * A_prev).sum(axis=0))
        signs[signs == 0] = 1
        A_hat = A_hat * signs

        h2_new = (A_hat**2).sum(axis=1)

        c1 = f < f_prev
        c2 = float(((A_hat - A_prev) ** 2).sum()) > eps
        c3 = bool((h2_new <= 1).all())
        go = c1 and c2 and c3

        records.append(
            IterationRecord(i, R_h, A_hat, f_prev, f, h2_new, c1, c2, c3, go)
        )

        if not go:
            break
        A_prev, f_prev, h2 = A_hat, f, h2_new

    return records
