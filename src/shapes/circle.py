"""
Circle shape — Kişi 2'nin dosyası.
"""
import math
from OpenGL.GL import *
from src.shapes.base import BaseShape


SEGMENTS = 64  # ne kadar yüksekse o kadar düzgün daire


class Circle(BaseShape):
    def __init__(self, cx=0, cy=0, radius=50):
        super().__init__()
        self.cx = cx
        self.cy = cy
        self.radius = radius

    def draw(self):
        r, g, b = self.color
        glColor3f(r, g, b)
        glLineWidth(self.line_width)

        if self.fill:
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(self.cx, self.cy)  # merkez
            for i in range(SEGMENTS + 1):
                angle = 2 * math.pi * i / SEGMENTS
                glVertex2f(
                    self.cx + self.radius * math.cos(angle),
                    self.cy + self.radius * math.sin(angle),
                )
            glEnd()

        # Outline
        glBegin(GL_LINE_LOOP)
        for i in range(SEGMENTS):
            angle = 2 * math.pi * i / SEGMENTS
            glVertex2f(
                self.cx + self.radius * math.cos(angle),
                self.cy + self.radius * math.sin(angle),
            )
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
        dist = math.hypot(x - self.cx, y - self.cy)
        return dist <= self.radius

    def get_bounds(self):
        pad = 6
        return (self.cx - self.radius - pad,
                self.cy - self.radius - pad,
                (self.radius + pad) * 2,
                (self.radius + pad) * 2)

    def to_dict(self):
        d = super().to_dict()
        d.update({"cx": self.cx, "cy": self.cy, "radius": self.radius})
        return d

    @classmethod
    def from_dict(cls, data):
        s = cls(data["cx"], data["cy"], data["radius"])
        s.color = tuple(data["color"])
        s.fill  = data["fill"]
        s.line_width = data["line_width"]
        return s