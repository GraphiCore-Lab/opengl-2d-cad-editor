import math
import numpy as np
from OpenGL.GL import *

from src.core.transform import (
    translation_matrix,
    rotation_matrix,
    scale_matrix,
)


class BaseShape:
    """Base class for all shapes, providing common properties and methods."""
    def __init__(self):
        self.outline_color = (1.0, 1.0, 1.0)
        self.fill_color = (0.6, 0.6, 0.6)
        self.fill = True
        self.line_width = 2.0
        self.alpha = 1.0
        self.selected = False
        self.transform = np.identity(3, dtype=float)

    # Required methods 
    def draw(self):
        raise NotImplementedError

    def get_points(self):
        raise NotImplementedError

    def get_bounds(self):
        points = self.get_transformed_points()
        return self.bounds_from_points(points)

    #  Transform helpers 
    def apply_transform(self, matrix):
        self.transform = matrix @ self.transform

    def get_transformed_point(self, x, y):
        p = np.array([x, y, 1.0])
        result = self.transform @ p
        return float(result[0]), float(result[1])

    def get_transformed_points(self):
        return [self.get_transformed_point(x, y) for x, y in self.get_points()]

    def move(self, dx, dy):
        self.apply_transform(translation_matrix(dx, dy))

    def rotate(self, angle_deg):
        cx, cy = self.get_center()
        self.apply_transform(rotation_matrix(angle_deg, cx, cy))

    def scale(self, sx, sy):
        cx, cy = self.get_center()
        self.apply_transform(scale_matrix(sx, sy, cx, cy))

    #  Selection / bounds 
    def bounds_from_points(self, points, pad=6):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        min_x = min(xs) - pad
        min_y = min(ys) - pad
        max_x = max(xs) + pad
        max_y = max(ys) + pad

        return min_x, min_y, max_x - min_x, max_y - min_y

    def contains(self, x, y):
        bx, by, bw, bh = self.get_bounds()
        return bx <= x <= bx + bw and by <= y <= by + bh

    def is_on_selection_border(self, x, y, thickness=8):
        bx, by, bw, bh = self.get_bounds()

        outer = (
            (bx - thickness) <= x <= (bx + bw + thickness)
            and (by - thickness) <= y <= (by + bh + thickness)
        )

        inner = (
            (bx + thickness) <= x <= (bx + bw - thickness)
            and (by + thickness) <= y <= (by + bh - thickness)
        )

        return outer and not inner

    def get_center(self):
        x, y, w, h = self.get_bounds()
        return x + w / 2, y + h / 2

    def draw_selection_box(self):
        x, y, w, h = self.get_bounds()

        glColor3f(0.0, 0.7, 1.0)
        glLineWidth(1.0)
        glLineStipple(2, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)

        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

        glDisable(GL_LINE_STIPPLE)

    #  Rotate handle 
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

        glBegin(GL_LINES)
        glVertex2f(cx, hy + 8)
        glVertex2f(cx, hy + 25)
        glEnd()

        glBegin(GL_LINE_LOOP)
        for i in range(32):
            angle = 2 * math.pi * i / 32
            glVertex2f(hx + 8 * math.cos(angle), hy + 8 * math.sin(angle))
        glEnd()

        glBegin(GL_LINES)
        glVertex2f(hx - 3, hy)
        glVertex2f(hx + 3, hy)
        glVertex2f(hx + 3, hy)
        glVertex2f(hx, hy - 4)
        glEnd()

    #  Serialization 
    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "outline_color": list(self.outline_color),
            "fill_color": list(self.fill_color),
            "fill": self.fill,
            "line_width": self.line_width,
            "alpha": self.alpha,
            "transform": self.transform.tolist(),
        }

    def load_common_data(self, data):
        self.outline_color = tuple(data.get("outline_color", data.get("color", (1.0, 1.0, 1.0))))
        self.fill_color = tuple(data.get("fill_color", data.get("color", (0.6, 0.6, 0.6))))
        self.fill = data.get("fill", True)
        self.line_width = data.get("line_width", 2.0)
        self.alpha = data.get("alpha", 1.0)
        if "transform" in data:
            self.transform = np.array(data["transform"], dtype=float)

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError