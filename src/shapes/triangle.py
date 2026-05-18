"""
Triangle shape.
"""
from OpenGL.GL import *
from src.shapes.base import BaseShape


class Triangle(BaseShape):
    def __init__(self, x1=0, y1=0, x2=100, y2=100, x3=50, y3=0):
        super().__init__()
        self.x1, self.y1 = x1, y1   # First vertex
        self.x2, self.y2 = x2, y2   # Second vertex
        self.x3, self.y3 = x3, y3   # Third vertex (apex by default)

    def get_points(self):
        return [
            (self.x1, self.y1),
            (self.x2, self.y2),
            (self.x3, self.y3),
        ]

    def draw(self):
        points = self.get_transformed_points()

        if self.fill:
            glColor4f(*self.fill_color, self.alpha)
            glBegin(GL_TRIANGLES)   # GL_TRIANGLES draws a filled triangle from exactly 3 vertices
            for x, y in points:
                glVertex2f(x, y)
            glEnd()

        glColor4f(*self.outline_color, self.alpha)
        glLineWidth(self.line_width)

        style = getattr(self, "line_style", "solid")
        if style == "dashed":
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(3, 0x00FF)
        elif style == "dotted":
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(1, 0xAAAA)

        glBegin(GL_LINE_LOOP)
        for x, y in points:
            glVertex2f(x, y)
        glEnd()

        if style != "solid":
            glDisable(GL_LINE_STIPPLE)

        if self.selected:
            self.draw_selection_box()
            self.draw_rotate_handle()

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "x3": self.x3,
            "y3": self.y3,
        })
        return data

    @classmethod
    def from_dict(cls, data):
        shape = cls(
            data["x1"],
            data["y1"],
            data["x2"],
            data["y2"],
            data["x3"],
            data["y3"],
        )
        shape.load_common_data(data)
        return shape