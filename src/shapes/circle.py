"""
Circle shape.
"""
import math
from OpenGL.GL import *
from src.shapes.base import BaseShape


SEGMENTS = 64


class Circle(BaseShape):
    def __init__(self, cx=0, cy=0, radius=50):
        super().__init__()
        self.cx = cx
        self.cy = cy
        self.radius = radius

    def get_points(self):
        points = []

        for i in range(SEGMENTS):
            angle = 2 * math.pi * i / SEGMENTS
            points.append((
                self.cx + self.radius * math.cos(angle),
                self.cy + self.radius * math.sin(angle),
            ))

        return points

    def get_transformed_center(self):
        return self.get_transformed_point(self.cx, self.cy)

    def draw(self):
        points = self.get_transformed_points()

        if self.fill:
            cx, cy = self.get_transformed_center()

            glColor3f(*self.fill_color)
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(cx, cy)

            for x, y in points:
                glVertex2f(x, y)

            glVertex2f(points[0][0], points[0][1])
            glEnd()

        glColor3f(*self.outline_color)
        glLineWidth(self.line_width)

        glBegin(GL_LINE_LOOP)
        for x, y in points:
            glVertex2f(x, y)
        glEnd()

        if self.selected:
            self.draw_selection_box()
            self.draw_rotate_handle()

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "cx": self.cx,
            "cy": self.cy,
            "radius": self.radius,
        })
        return data

    @classmethod
    def from_dict(cls, data):
        shape = cls(data["cx"], data["cy"], data["radius"])
        shape.load_common_data(data)
        return shape