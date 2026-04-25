"""
Line shape.
"""
import math
from OpenGL.GL import *
from src.shapes.base import BaseShape
from src.utils.constants import HIT_THRESHOLD
import numpy as np


class Line(BaseShape):
    def __init__(self, x1=0, y1=0, x2=100, y2=100):
        super().__init__()
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.fill = False

    def _transformed_endpoints(self):
        p1 = self.get_transformed_point(self.x1, self.y1)
        p2 = self.get_transformed_point(self.x2, self.y2)
        return p1, p2

    def draw(self):
        r, g, b = self.color
        glColor3f(r, g, b)
        glLineWidth(self.line_width)

        (x1, y1), (x2, y2) = self._transformed_endpoints()

        glBegin(GL_LINES)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
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
        (x1, y1), (x2, y2) = self._transformed_endpoints()

        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx * dx + dy * dy

        if length_sq == 0:
            dist = math.hypot(x - x1, y - y1)
        else:
            t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / length_sq))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            dist = math.hypot(x - proj_x, y - proj_y)

        return dist <= HIT_THRESHOLD

    def get_bounds(self):
        pad = 6
        (x1, y1), (x2, y2) = self._transformed_endpoints()

        min_x = min(x1, x2) - pad
        min_y = min(y1, y2) - pad
        max_x = max(x1, x2) + pad
        max_y = max(y1, y2) + pad

        return min_x, min_y, max_x - min_x, max_y - min_y

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
        })
        return d

    @classmethod
    def from_dict(cls, data):
        s = cls(data["x1"], data["y1"], data["x2"], data["y2"])
        s.color = tuple(data.get("color", (1.0, 1.0, 1.0)))
        s.line_width = data.get("line_width", 2.0)
        s.fill = False

        if "transform" in data:
            s.transform = np.array(data["transform"], dtype=float)

        return s