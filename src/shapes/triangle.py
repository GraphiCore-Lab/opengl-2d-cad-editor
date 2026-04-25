"""
Triangle shape.
"""
from OpenGL.GL import *
from src.shapes.base import BaseShape
import numpy as np


class Triangle(BaseShape):
    def __init__(self, x1=0, y1=0, x2=100, y2=100, x3=50, y3=0):
        super().__init__()
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.x3, self.y3 = x3, y3

    def _points(self):
        return [
            (self.x1, self.y1),
            (self.x2, self.y2),
            (self.x3, self.y3),
        ]

    def _transformed_points(self):
        return [self.get_transformed_point(x, y) for x, y in self._points()]

    def draw(self):
        points = self._transformed_points()

        if self.fill:
            r, g, b = self.fill_color
            glColor3f(r, g, b)

            glBegin(GL_TRIANGLES)
            for x, y in points:
                glVertex2f(x, y)
            glEnd()

        r, g, b = self.outline_color
        glColor3f(r, g, b)
        glLineWidth(self.line_width)

        glBegin(GL_LINE_LOOP)
        for x, y in points:
            glVertex2f(x, y)
        glEnd()

        if self.selected:
            self._draw_selection_box()

    def _draw_selection_box(self):
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

    def contains(self, x, y):
        bx, by, bw, bh = self.get_bounds()
        return bx <= x <= bx + bw and by <= y <= by + bh

    def get_bounds(self):
        pad = 6
        points = self._transformed_points()

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        min_x = min(xs) - pad
        min_y = min(ys) - pad
        max_x = max(xs) + pad
        max_y = max(ys) + pad

        return min_x, min_y, max_x - min_x, max_y - min_y

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "x3": self.x3,
            "y3": self.y3,
        })
        return d

    @classmethod
    def from_dict(cls, data):
        s = cls(
            data["x1"],
            data["y1"],
            data["x2"],
            data["y2"],
            data["x3"],
            data["y3"],
        )

        s.outline_color = tuple(data.get("outline_color", data.get("color", (1.0, 1.0, 1.0))))
        s.fill_color = tuple(data.get("fill_color", data.get("color", (0.6, 0.6, 0.6))))
        s.fill = data.get("fill", True)
        s.line_width = data.get("line_width", 2.0)

        if "transform" in data:
            s.transform = np.array(data["transform"], dtype=float)

        return s