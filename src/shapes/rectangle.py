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

    def get_points(self):
        return [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height),
        ]

    def draw(self):
        points = self.get_transformed_points()

        if self.fill:
            glColor3f(*self.fill_color)
            glBegin(GL_QUADS)
            for x, y in points:
                glVertex2f(x, y)
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
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        })
        return data

    @classmethod
    def from_dict(cls, data):
        shape = cls(data["x"], data["y"], data["width"], data["height"])
        shape.load_common_data(data)
        return shape