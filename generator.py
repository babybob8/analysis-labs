from collections.abc import Callable
from dataclasses import dataclass
from functools import partial, reduce
from operator import matmul

import numpy as np


@dataclass(frozen=True)
class Variant:
    n: int
    sigma_z1: float
    sigma_z2: float
    sigma_eps: float
    phi_deg: float
    psi_deg: float
    mu: tuple[float, float, float]


VARIANTS = dict(
    enumerate(
        (
            Variant(*row)
            for row in [
                (150, 10, 4, 0.5, 30, 45, (5, 10, 15)),
                (200, 12, 5, 0.8, 45, 30, (0, 20, 10)),
                (120, 8, 3, 0.3, 60, 15, (10, 0, 5)),
                (250, 15, 6, 1.0, 25, 60, (20, 15, 0)),
                (180, 9, 4, 0.6, 40, 120, (3, 7, 12)),
                (300, 11, 2, 0.4, 50, 75, (15, 5, 20)),
                (100, 7, 3, 0.2, 35, 135, (8, 12, 4)),
                (220, 14, 7, 1.2, 20, 90, (0, 0, 25)),
                (160, 10, 5, 0.7, 55, 150, (12, 18, 6)),
                (280, 13, 3, 0.5, 70, 20, (25, 10, 15)),
            ]
        ),
        start=1,
    )
)


def compose(*fs: Callable) -> Callable:
    return lambda x: reduce(lambda acc, f: f(acc), fs, x)


def rotation_x(angle: float) -> np.ndarray:
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])


def rotation_z(angle: float) -> np.ndarray:
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def sample_latent(seed: int, variant: Variant) -> np.ndarray:
    rng = np.random.default_rng(seed)
    sigmas = (variant.sigma_z1, variant.sigma_z2, variant.sigma_eps)
    return np.vstack([rng.normal(0.0, s, variant.n) for s in sigmas])


def rotate(variant: Variant, y: np.ndarray) -> np.ndarray:
    rz = rotation_z(np.deg2rad(variant.psi_deg))
    rx = rotation_x(np.deg2rad(variant.phi_deg))
    return reduce(matmul, (rz, rx, y))


def shift(variant: Variant, x: np.ndarray) -> np.ndarray:
    return x + np.asarray(variant.mu, dtype=float).reshape(3, 1)


def skew_third_feature(x: np.ndarray) -> np.ndarray:
    return np.vstack((x[0], x[1], np.exp(x[2] / 10.0)))


def to_rows(x: np.ndarray) -> np.ndarray:
    return x.T


def generate(variant: Variant, seed: int) -> np.ndarray:
    pipeline = compose(
        partial(sample_latent, seed),
        partial(rotate, variant),
        partial(shift, variant),
        skew_third_feature,
        to_rows,
    )
    return pipeline(variant)


def save(path: str, data: np.ndarray) -> str:
    np.savetxt(
        path,
        data,
        delimiter=",",
        header="x1,x2,x3_star",
        comments="",
        fmt="%.10f",
    )
    return path


def main(
    variant_id: int = 1,
    seed: int = 42,
    path: str = "data.csv",
    /,
    save_in_data: bool = False,
) -> None:
    variant = VARIANTS[variant_id]
    path = rf"variant{variant_id}_{path}"
    if save_in_data:
        path = rf"data/{path}"

    saved = save(path, generate(variant, seed))
    print(f"Variant: variant{variant_id}, samples: {variant.n}, saved to: {saved}")


if __name__ == "__main__":
    main(9, 67, save_in_data=True)
