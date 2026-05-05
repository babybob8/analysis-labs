import numpy as np


vec_t = list[float]
mat_t = list[vec_t]


def _center(data: mat_t, mean: vec_t) -> mat_t:
    return [[x - m for x in vec] for vec, m in zip(data, mean)]


def _dc(data: mat_t, length: int) -> np.ndarray:
    X = np.array(data)
    return (1 / length) * (X @ X.T)


def _ewv(data: mat_t, mean: vec_t, length: int) -> tuple[vec_t, np.ndarray]:
    centered = _center(data, mean)
    dc = _dc(centered, length)
    eigenvalues, eigenvectors = np.linalg.eigh(dc)
    eigenvalues = eigenvalues[::-1]
    eigenvectors = eigenvectors[:, ::-1]
    return eigenvalues.tolist(), eigenvectors


def _to_ortogonal(data: mat_t, eigenvectors: np.ndarray) -> mat_t:
    X = np.array(data).T
    return (X @ eigenvectors).tolist()


def _from_ortogonal(ortogonal: mat_t, eigenvectors: np.ndarray, keep: int) -> mat_t:
    X = np.array(ortogonal)
    filtered = X[:, :keep]
    eigenvectors_reduced = eigenvectors[:, :keep]
    return (filtered @ eigenvectors_reduced.T).tolist()


def forward(
    cols: mat_t, /, mean: vec_t | None = None, length: int | None = None
) -> tuple[vec_t, np.ndarray, mat_t]:
    if mean is None:
        mean = [sum(vec) / len(vec) for vec in cols]

    if length is None:
        length = len(cols[0])

    eigenvalues, eigenvectors = _ewv(cols, mean, length)
    ortogonal = _to_ortogonal(cols, eigenvectors)
    return eigenvalues, eigenvectors, ortogonal


def backward(
    ortogonal: mat_t, eigenvectors: np.ndarray, /, keep: int | None = None
) -> mat_t:
    if keep is None:
        keep = len(ortogonal)

    return _from_ortogonal(ortogonal, eigenvectors, keep)
