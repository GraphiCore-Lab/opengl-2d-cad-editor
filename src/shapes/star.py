"""
Star shape.
"""
import math
from OpenGL.GL import *
from src.shapes.base import BaseShape

class Star(BaseShape):
    def __init__(self, cx=0, cy=0, radius=50, points=5):
        super().__init__()
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.points = max(3, points) # Minimum 3-pointed star
        self.inner_ratio = 0.4       # 0.4 gives a classic star proportion

    def get_points(self):
        vertex_points = []
        total_vertices = self.points * 2
        
        for i in range(total_vertices):
            # Alternate between outer radius and inner radius
            current_radius = self.radius if i % 2 == 0 else self.radius * self.inner_ratio
            
            # Angle step is pi / points (half a slice per vertex)
            angle = (math.pi / self.points) * i - (math.pi / 2)
            
            vertex_points.append((
                self.cx + current_radius * math.cos(angle),
                self.cy + current_radius * math.sin(angle),
            ))
        return vertex_points

    def get_transformed_center(self):
        return self.get_transformed_point(self.cx, self.cy)

    def draw(self):
        points = self.get_transformed_points()

        # 1. Fill
        if self.fill:
            cx, cy = self.get_transformed_center()
            glColor4f(*self.fill_color, self.alpha)
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(cx, cy)
            for x, y in points:
                glVertex2f(x, y)
            glVertex2f(points[0][0], points[0][1]) # Close the loop
            glEnd()

        # 2. Outline with Stipple Support
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

        # 3. UI Handles
        if self.selected:
            self.draw_selection_box()
            self.draw_rotate_handle()

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "cx": self.cx,
            "cy": self.cy,
            "radius": self.radius,
            "points": self.points,
        })
        return data

    @classmethod
    def from_dict(cls, data):
        shape = cls(data["cx"], data["cy"], data["radius"], data["points"])
        shape.load_common_data(data)
        return shape