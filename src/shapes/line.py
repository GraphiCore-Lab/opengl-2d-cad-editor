"""
Line shape — Kişi 2'nin başlangıç dosyası.
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
        self.fill = False  # line'da fill anlamsız

    def draw(self):
        r, g, b = self.color
        glColor3f(r, g, b)
        glLineWidth(self.line_width)
        glBegin(GL_LINES)
        glVertex2f(self.x1, self.y1)
        glVertex2f(self.x2, self.y2)
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
        """Noktanın çizgiye mesafesi threshold'dan küçükse True."""
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            dist = math.hypot(x - self.x1, y - self.y1)
        else:
            t = max(0, min(1, ((x - self.x1) * dx + (y - self.y1) * dy) / length_sq))
            proj_x = self.x1 + t * dx
            proj_y = self.y1 + t * dy
            dist = math.hypot(x - proj_x, y - proj_y)
        return dist <= HIT_THRESHOLD

    def get_bounds(self):
        x = min(self.x1, self.x2)
        y = min(self.y1, self.y2)
        w = abs(self.x2 - self.x1)
        h = abs(self.y2 - self.y1)
        return (x - 4, y - 4, w + 8, h + 8)

    def to_dict(self):
        d = super().to_dict()
        d.update({"x1": self.x1, "y1": self.y1,
                  "x2": self.x2, "y2": self.y2})
        return d

    @classmethod
    def from_dict(cls, data):
        s = cls(data["x1"], data["y1"], data["x2"], data["y2"])
        s.color = tuple(data["color"])
        s.line_width = data["line_width"]
        return s