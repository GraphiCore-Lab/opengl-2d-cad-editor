"""
Rectangle shape.
"""
from OpenGL.GL import *
from src.shapes.base import BaseShape


class Rectangle(BaseShape):
    def __init__(self, x=0, y=0, width=100, height=60):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def _points(self):
        return [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height),
        ]

    def _transformed_points(self):
        return [self.get_transformed_point(x, y) for x, y in self._points()]

    def draw(self):
        r, g, b = self.color
        glColor3f(r, g, b)
        glLineWidth(self.line_width)

        points = self._transformed_points()

        if self.fill:
            glBegin(GL_QUADS)
            for x, y in points:
                glVertex2f(x, y)
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
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        })
        return d

    @classmethod
    def from_dict(cls, data):
        s = cls(data["x"], data["y"], data["width"], data["height"])
        s.color = tuple(data["color"])
        s.fill = data["fill"]
        s.line_width = data["line_width"]
        return s