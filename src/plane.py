import logging
from typing import NamedTuple

import numpy as np


class Plane(NamedTuple):
    a: float
    b: float
    c: float
    d: float


def validate_points(points) -> np.ndarray:
    array = np.asarray(points, dtype=float)
    if array.ndim != 2 or array.shape[1] != 3 or array.shape[0] < 3:
        logging.error("Expected an array of shape (N, 3) with N >= 3")
        raise ValueError("Expected an array of shape (N, 3) with N >= 3")
    return array


def farthest_from(origin: np.ndarray, points: np.ndarray) -> np.ndarray:
    return points[np.argmax(np.linalg.norm(points - origin, axis=1))]


def widest_normal(p1: np.ndarray, p2: np.ndarray, points: np.ndarray) -> np.ndarray:
    normals = np.cross(p2 - p1, points - p1)
    return normals[np.argmax(np.linalg.norm(normals, axis=1))]


def plane_equation(points, tol: float = 1e-9, normalize: bool = True) -> Plane:
    array = validate_points(points)
    p1 = array[0]
    p2 = farthest_from(p1, array)
    normal = widest_normal(p1, p2, array)

    span = float(np.linalg.norm(p2 - p1))
    length = float(np.linalg.norm(normal))
    if span == 0.0 or length <= tol * span**2:
        logging.error("Points are collinear, plane is undefined")
        raise ValueError("Points are collinear, plane is undefined")

    n = normal / length if normalize else normal
    d = -float(n @ p1)
    return Plane(float(n[0]), float(n[1]), float(n[2]), d)


def point_plane_distances(points, plane: Plane) -> np.ndarray:
    array = validate_points(points)
    n = np.array(plane[:3])
    return (array @ n + plane.d) / np.linalg.norm(n)
