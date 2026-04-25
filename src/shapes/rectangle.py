"""
Rectangle shape — Kişi 2'nin dosyası.
"""
from OpenGL.GL import *
from src.shapes.base import BaseShape


class Rectangle(BaseShape):
    def __init__(self, x=0, y=0, width=100, height=60):
        super().__init__()
        self.x = x
        self.y = y
        self.width  = width
        self.height = height

    def draw(self):
        r, g, b = self.color
        glColor3f(r, g, b)
        glLineWidth(self.line_width)

        if self.fill:
            glBegin(GL_QUADS)
            glVertex2f(self.x,              self.y)
            glVertex2f(self.x + self.width, self.y)
            glVertex2f(self.x + self.width, self.y + self.height)
            glVertex2f(self.x,              self.y + self.height)
            glEnd()

        # Outline her zaman çiz
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.x,              self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x,              self.y + self.height)
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
        glVertex2f(x,     y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x,     y + h)
        glEnd()
        glDisable(GL_LINE_STIPPLE)

    def contains(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def get_bounds(self):
        pad = 6
        return (self.x - pad, self.y - pad,
                self.width + pad * 2, self.height + pad * 2)

    def to_dict(self):
        d = super().to_dict()
        d.update({"x": self.x, "y": self.y,
                  "width": self.width, "height": self.height})
        return d

    @classmethod
    def from_dict(cls, data):
        s = cls(data["x"], data["y"], data["width"], data["height"])
        s.color = tuple(data["color"])
        s.fill  = data["fill"]
        s.line_width = data["line_width"]
        return s