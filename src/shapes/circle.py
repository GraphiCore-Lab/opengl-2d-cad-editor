"""
Circle shape.
"""
import math
from OpenGL.GL import *
from src.shapes.base import BaseShape

#64-segment polygon to smoothly approximate a circle since OpenGL lacks a native circle primitive
SEGMENTS = 64


class Circle(BaseShape):
    #Inherits from BaseShape to utilize the universal transform matrix for uniform scaling and translation
    def __init__(self, cx=0, cy=0, radius=50):
        super().__init__()
        #Local coordinates are stored while world positioning is handled dynamically by the BaseShape transform matrix
        self.cx = cx
        self.cy = cy
        self.radius = radius

    def get_points(self):
        #Polar-to-Cartesian conversion across 2*PI radians generates an evenly spaced array of perimeter vertices
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
        #Fill and outline rendering are separated to allow independent styling and alpha-blending
        points = self.get_transformed_points()

        if self.fill:
            cx, cy = self.get_transformed_center()

            glColor4f(*self.fill_color, self.alpha)

            #GL_TRIANGLE_FAN is the most computationally efficient way to fill a convex, center-origin shape
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(cx, cy)

            for x, y in points:
                glVertex2f(x, y)

            glVertex2f(points[0][0], points[0][1])
            glEnd()

        glColor4f(*self.outline_color, self.alpha)
        glLineWidth(self.line_width)

        #Dynamically enables bitwise line stippling for dashed or dotted stroke styles
        style = getattr(self, "line_style", "solid")
        if style == "dashed":
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(3, 0x00FF)
        elif style == "dotted":
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(1, 0xAAAA)

        #GL_LINE_LOOP automatically connects the last vertex back to the first to close the perimeter
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
        #Saves the local geometric parameters alongside the inherited transformation matrices for accurate serialization
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