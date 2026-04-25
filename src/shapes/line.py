"""
Line shape.
"""
import math
from OpenGL.GL import *

from src.shapes.base import BaseShape
from src.utils.constants import HIT_THRESHOLD


class Line(BaseShape):
    def __init__(self, x1=0, y1=0, x2=100, y2=100):
        super().__init__()
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.fill = False

    def get_points(self):
        return [
            (self.x1, self.y1),
            (self.x2, self.y2),
        ]

    def get_transformed_endpoints(self):
        points = self.get_transformed_points()
        return points[0], points[1]

    def draw(self):
        glColor3f(*self.outline_color)
        glLineWidth(self.line_width)

        (x1, y1), (x2, y2) = self.get_transformed_endpoints()

        glBegin(GL_LINES)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()

        if self.selected:
            self.draw_selection_box()
            self.draw_rotate_handle()

    def contains(self, x, y):
        (x1, y1), (x2, y2) = self.get_transformed_endpoints()

        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx * dx + dy * dy

        if length_sq == 0:
            distance = math.hypot(x - x1, y - y1)
        else:
            t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / length_sq))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            distance = math.hypot(x - proj_x, y - proj_y)

        return distance <= HIT_THRESHOLD

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
        })
        return data

    @classmethod
    def from_dict(cls, data):
        shape = cls(data["x1"], data["y1"], data["x2"], data["y2"])
        shape.load_common_data(data)
        shape.fill = False
        return shape