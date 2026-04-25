"""
Base shape interface - tüm shape'ler bunu extends eder.
"""
import numpy as np

from src.core.transform import (
    translation_matrix,
    rotation_matrix,
    scale_matrix,
)


class BaseShape:
    def __init__(self):
        self.color = (1.0, 1.0, 1.0)
        self.fill = True
        self.line_width = 2.0
        self.selected = False
        self.transform = np.identity(3, dtype=float)

    def draw(self):
        raise NotImplementedError

    def contains(self, x, y):
        raise NotImplementedError

    def get_bounds(self):
        raise NotImplementedError

    def apply_transform(self, matrix):
        self.transform = matrix @ self.transform

    def get_transformed_point(self, x, y):
        p = np.array([x, y, 1.0])
        result = self.transform @ p
        return float(result[0]), float(result[1])

    def get_center(self):
        x, y, w, h = self.get_bounds()
        return x + w / 2, y + h / 2

    def move(self, dx, dy):
        self.apply_transform(translation_matrix(dx, dy))

    def rotate(self, angle_deg):
        cx, cy = self.get_center()
        self.apply_transform(rotation_matrix(angle_deg, cx, cy))

    def scale(self, sx, sy):
        cx, cy = self.get_center()
        self.apply_transform(scale_matrix(sx, sy, cx, cy))

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "color": list(self.color),
            "fill": self.fill,
            "line_width": self.line_width,
            "transform": self.transform.tolist(),
        }

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError