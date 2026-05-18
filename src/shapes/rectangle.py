"""
Rectangle shape.
"""
from OpenGL.GL import *
from src.shapes.base import BaseShape


class Rectangle(BaseShape):
    def __init__(self, x=0, y=0, width=100, height=60):
        super().__init__()
        self.x = x    # Top-left corner X 
        self.y = y    # Top-left corner Y
        self.width = width
        self.height = height

    def get_points(self):
        # Vertices listed counter-clockwise starting from top-left
        return [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height),
        ]

    def draw(self):
        points = self.get_transformed_points()

        if self.fill:
            glColor4f(*self.fill_color, self.alpha)
            glBegin(GL_QUADS)       # GL_QUADS draws a filled quadrilateral from exactly 4 vertices
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