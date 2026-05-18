"""
Ellipse shape.
"""
import math
from OpenGL.GL import *
from src.shapes.base import BaseShape

class Ellipse(BaseShape):
    def __init__(self, x=0, y=0, width=100, height=60):
        super().__init__()
        self.x = x      # Top-left corner X of the bounding box
        self.y = y      # Top-left corner Y of the bounding box
        self.width = width
        self.height = height

    def get_points(self):
        points = []
        cx = self.x + self.width / 2.0
        cy = self.y + self.height / 2.0
        rx = self.width / 2.0
        ry = self.height / 2.0

        # 60 segments gives it a perfectly smooth curve
        segments = 60 
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            points.append((
                cx + rx * math.cos(angle),      # Parametric ellipse: x = cx + rx*cos(θ)
                cy + ry * math.sin(angle)        # Parametric ellipse: y = cy + ry*sin(θ)
            ))
        return points

    def draw(self):
        points = self.get_transformed_points()

        if self.fill:
            # Transform the logical center point into world space for the fan origin
            cx_base = self.x + self.width / 2.0
            cy_base = self.y + self.height / 2.0
            cx, cy = self.get_transformed_point(cx_base, cy_base)

            glColor4f(*self.fill_color, self.alpha)
            glBegin(GL_TRIANGLE_FAN)        # Fan from center fills the ellipse without tesselation
            glVertex2f(cx, cy)
            for px, py in points:
                glVertex2f(px, py)
            glVertex2f(points[0][0], points[0][1])  # Repeat first vertex to close the fan
            glEnd()

        # Apply the stipple pattern before drawing the outline loop
        glColor4f(*self.outline_color, self.alpha)
        glLineWidth(self.line_width)

        style = getattr(self, "line_style", "solid")
        if style == "dashed":
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(3, 0x00FF)        # Factor 3, alternating 8-bit on/off pattern
        elif style == "dotted":
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(1, 0xAAAA)        # Factor 1, every other pixel produces dots

        glBegin(GL_LINE_LOOP)
        for px, py in points:
            glVertex2f(px, py)
        glEnd()

        if style != "solid":
            glDisable(GL_LINE_STIPPLE)

        # 3. UI Handles
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