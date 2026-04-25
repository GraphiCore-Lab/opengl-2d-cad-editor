"""
Base shape interface - tüm shape'ler bunu extends eder.
"""
import math
import numpy as np
from OpenGL.GL import *

from src.core.transform import (
    translation_matrix,
    rotation_matrix,
    scale_matrix,
)


class BaseShape:
    def __init__(self):
        self.outline_color = (1.0, 1.0, 1.0)
        self.fill_color = (0.6, 0.6, 0.6)
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

    def get_rotate_handle_pos(self):
        x, y, w, h = self.get_bounds()
        return x + w / 2, y - 25

    def is_on_rotate_handle(self, x, y):
        hx, hy = self.get_rotate_handle_pos()
        return math.hypot(x - hx, y - hy) <= 10

    def draw_rotate_handle(self):
        hx, hy = self.get_rotate_handle_pos()
        cx, _ = self.get_center()

        glColor3f(0.0, 0.7, 1.0)
        glLineWidth(2.0)

        # bağlantı çizgisi
        glBegin(GL_LINES)
        glVertex2f(cx, hy + 8)
        glVertex2f(cx, hy + 25)
        glEnd()

        # yuvarlak handle
        glBegin(GL_LINE_LOOP)
        for i in range(32):
            angle = 2 * math.pi * i / 32
            glVertex2f(hx + 8 * math.cos(angle), hy + 8 * math.sin(angle))
        glEnd()

        # küçük ok görünümü
        glBegin(GL_LINES)
        glVertex2f(hx - 3, hy)
        glVertex2f(hx + 3, hy)
        glVertex2f(hx + 3, hy)
        glVertex2f(hx, hy - 4)
        glEnd()

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "outline_color": list(self.outline_color),
            "fill_color": list(self.fill_color),
            "fill": self.fill,
            "line_width": self.line_width,
            "transform": self.transform.tolist(),
        }

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError