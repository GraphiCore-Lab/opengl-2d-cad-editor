"""
Transform: 2D homogeneous koordinat matrisleri.
Kişi 1 yazar. Kişi 2 shape'lere uygular.
"""
import numpy as np
import math


def translation_matrix(dx, dy):
    """Öteleme matrisi."""
    m = np.identity(3, dtype=float)
    m[0, 2] = dx
    m[1, 2] = dy
    return m


def rotation_matrix(angle_deg, cx=0.0, cy=0.0):
    """
    Döndürme matrisi.
    cx, cy: döndürme merkezi (varsayılan orijin)
    """
    angle = math.radians(angle_deg)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    # Merkeze taşı → döndür → geri taşı
    to_origin = translation_matrix(-cx, -cy)
    rotate = np.array([
        [cos_a, -sin_a, 0],
        [sin_a,  cos_a, 0],
        [0,      0,     1],
    ], dtype=float)
    from_origin = translation_matrix(cx, cy)
    return from_origin @ rotate @ to_origin


def scale_matrix(sx, sy, cx=0.0, cy=0.0):
    """
    Ölçekleme matrisi.
    cx, cy: ölçekleme merkezi
    """
    to_origin = translation_matrix(-cx, -cy)
    scale = np.array([
        [sx, 0,  0],
        [0,  sy, 0],
        [0,  0,  1],
    ], dtype=float)
    from_origin = translation_matrix(cx, cy)
    return from_origin @ scale @ to_origin


def apply(matrix, x, y):
    """3x3 matrisi bir noktaya uygula, (x', y') döndür."""
    p = np.array([x, y, 1.0])
    r = matrix @ p
    return r[0], r[1]


def identity():
    return np.identity(3, dtype=float)