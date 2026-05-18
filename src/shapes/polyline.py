"""
Polyline shape (Joined lines).
"""
import math
from OpenGL.GL import *
from src.shapes.base import BaseShape
from src.utils.constants import HIT_THRESHOLD

class Polyline(BaseShape):
    def __init__(self, vertices=None, closed=False):
        super().__init__()
        self.vertices = vertices if vertices else []
        self.closed = closed    # If True, last vertex connects back to first
        self.fill = False # Polylines default to no fill unless specifically requested
        
        # Seed self.x/self.y so BaseShape selection/handle logic has a valid anchor
        if self.vertices:
            cx, cy = self.get_center()
            self.x = cx
            self.y = cy
        else:
            self.x = 0
            self.y = 0

    def get_points(self):
        return self.vertices

    def get_center(self):
        """Calculates the exact middle of the polyline bounds."""
        if not self.vertices:
            return (0, 0)
        xs = [p[0] for p in self.vertices]
        ys = [p[1] for p in self.vertices]
        return (sum(xs) / len(xs), sum(ys) / len(ys))
    
    #Polyline stores absolute world coordinates directly in self.vertices,
    #so transforms are applied in-place instead of through the base matrix pipeline.
    def get_transformed_points(self):
        return self.vertices 

    def move(self, dx, dy):
        """Permanently moves all vertices by dx, dy."""
        self.vertices = [(x + dx, y + dy) for x, y in self.vertices]
        self.x += dx
        self.y += dy

    def rotate(self, angle_deg):
        """Spins all vertices perfectly around the calculated center."""
        cx, cy = self.get_center()
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        new_verts = []
        for x, y in self.vertices:
            nx = cos_a * (x - cx) - sin_a * (y - cy) + cx
            ny = sin_a * (x - cx) + cos_a * (y - cy) + cy
            new_verts.append((nx, ny))
        self.vertices = new_verts

    def scale(self, sx, sy):
        """Expands/Shrinks all vertices away from the calculated center."""
        cx, cy = self.get_center()
        new_verts = []
        for x, y in self.vertices:
            nx = cx + (x - cx) * sx
            ny = cy + (y - cy) * sy
            new_verts.append((nx, ny))
        self.vertices = new_verts

    def draw(self):
        if not self.vertices:
            return

        points = self.get_transformed_points()

        # 1. Fill (Only if closed and fill is on)
        if self.closed and getattr(self, "fill", False) and len(points) >= 3:
            glColor4f(*self.fill_color, self.alpha)
            glBegin(GL_POLYGON)
            for x, y in points:
                glVertex2f(x, y)
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

        # Use LINE_LOOP if closed, otherwise LINE_STRIP (open path)
        draw_mode = GL_LINE_LOOP if self.closed else GL_LINE_STRIP
        glBegin(draw_mode)
            
        for x, y in points:
            glVertex2f(x, y)
        glEnd()

        if style != "solid":
            glDisable(GL_LINE_STIPPLE)

        # 3. UI Handles
        if self.selected:
            self.draw_selection_box()
            self.draw_rotate_handle()

    def contains(self, x, y):
        # Precise hit detection for every segment of the polyline
        points = self.get_transformed_points()
        if len(points) < 2: return False

        for i in range(len(points)):
            if not self.closed and i == len(points) - 1:
                break   # Open path: skip the wraparound segment back to vertex 0
                
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length_sq = dx * dx + dy * dy
            
            if length_sq == 0: continue # Skip zero-length degenerate segments
            
            t = max(0, min(1, ((x - p1[0]) * dx + (y - p1[1]) * dy) / length_sq))
            proj_x = p1[0] + t * dx
            proj_y = p1[1] + t * dy
            distance = math.hypot(x - proj_x, y - proj_y)
            
            if distance <= HIT_THRESHOLD:
                return True
        return False