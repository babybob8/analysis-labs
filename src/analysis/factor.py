import numpy as np


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
