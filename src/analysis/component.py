import numpy as np

vec_t = list[float]
mat_t = list[vec_t]


def _center(data: mat_t, mean: vec_t) -> mat_t:
    return [[x - m for x in vec] for vec, m in zip(data, mean)]


def _dc(data: mat_t, length: int) -> np.ndarray:
    X = np.array(data)
    return (1 / length) * (X @ X.T)


def _evv(
    data: mat_t, mean: vec_t, length: int, method: str
) -> tuple[vec_t, np.ndarray, np.ndarray]:
    centered = np.array(_center(data, mean))

    if method == "correlation":
        std = centered.std(axis=1, ddof=0)
        centered = centered / std[:, np.newaxis]
    elif method != "covariance":
        raise ValueError(f"Unknown method: {method}")

    dc = _dc(centered.tolist(), length)

    eigenvalues, eigenvectors = np.linalg.eigh(dc)
    eigenvalues = eigenvalues[::-1]
    eigenvectors = eigenvectors[:, ::-1]

    return eigenvalues.tolist(), eigenvectors, centered


def _to_ortogonal(data: np.ndarray, eigenvectors: np.ndarray) -> mat_t:
    return (data.T @ eigenvectors).tolist()


def _filter(ortogonal: mat_t, keep: int) -> np.ndarray:
    X = np.array(ortogonal)
    return X[:, :keep]


def _from_ortogonal(
    filtered_ortogonal: np.ndarray | mat_t,
    filtered_eigenvectors: np.ndarray,
) -> mat_t:
    return (filtered_ortogonal @ filtered_eigenvectors.T).tolist()


def forward(
    cols: mat_t,
    /,
    mean: vec_t | None = None,
    length: int | None = None,
    method: str = "covariance",
) -> tuple[vec_t, np.ndarray, mat_t]:

    if mean is None:
        mean = [sum(vec) / len(vec) for vec in cols]

    if length is None:
        length = len(cols[0])

    eigenvalues, eigenvectors, transformed = _evv(cols, mean, length, method)

    ortogonal = _to_ortogonal(transformed, eigenvectors)

    return eigenvalues, eigenvectors, ortogonal


def backward(
    ortogonal: mat_t,
    eigenvectors: np.ndarray,
    /,
    keep: int | None = None,
) -> mat_t:
    if keep is None:
        keep = len(ortogonal[0])

    filtered_ortogonal = _filter(ortogonal, keep)
    filtered_eigenvectors = eigenvectors[:, :keep]

    return _from_ortogonal(filtered_ortogonal, filtered_eigenvectors)
