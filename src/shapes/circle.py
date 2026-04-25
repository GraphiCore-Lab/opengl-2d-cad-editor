"""
Circle shape.
"""
import math
from OpenGL.GL import *
from src.shapes.base import BaseShape
import numpy as np


SEGMENTS = 64


class Circle(BaseShape):
    def __init__(self, cx=0, cy=0, radius=50):
        super().__init__()
        self.cx = cx
        self.cy = cy
        self.radius = radius

    def _circle_points(self):
        points = []
        for i in range(SEGMENTS):
            angle = 2 * math.pi * i / SEGMENTS
            points.append((
                self.cx + self.radius * math.cos(angle),
                self.cy + self.radius * math.sin(angle),
            ))
        return points

    def _transformed_points(self):
        return [self.get_transformed_point(x, y) for x, y in self._circle_points()]

    def _transformed_center(self):
        return self.get_transformed_point(self.cx, self.cy)

    def draw(self):
        r, g, b = self.color
        glColor3f(r, g, b)
        glLineWidth(self.line_width)

        points = self._transformed_points()

        if self.fill:
            cx, cy = self._transformed_center()
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(cx, cy)
            for x, y in points:
                glVertex2f(x, y)
            glVertex2f(points[0][0], points[0][1])
            glEnd()

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
            "cx": self.cx,
            "cy": self.cy,
            "radius": self.radius,
        })
        return d

    @classmethod
    def from_dict(cls, data):
        s = cls(data["cx"], data["cy"], data["radius"])
        s.color = tuple(data.get("color", (1.0, 1.0, 1.0)))
        s.fill = data.get("fill", True)
        s.line_width = data.get("line_width", 2.0)

        if "transform" in data:
            s.transform = np.array(data["transform"], dtype=float)

        return s