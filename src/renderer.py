"""
Renderer: her frame'de sahneyi OpenGL ile çizer.
Kişi 1 + UI entegrasyonu (Kişi 3 uyumlu)
"""

from OpenGL.GL import *
import math

from src.utils.constants import (
    CANVAS_X, CANVAS_W, CANVAS_H,
    COLOR_CANVAS, COLOR_GRID, COLOR_GRID_MAJOR,
    GRID_SIZE
)


def _rgb(color_tuple):
    """0-255 → 0.0-1.0"""
    return tuple(c / 255 for c in color_tuple)


class Renderer:
    def __init__(self, scene, show_grid=True):
        self.scene = scene
        self.show_grid = show_grid

        import pygame
        pygame.font.init()
        self.input_font = pygame.font.SysFont("segoeui", 12)

    # ─────────────────────────────────────────────

    def render(self):
        """Ana render fonksiyonu — her frame çağrılır."""
        glClear(GL_COLOR_BUFFER_BIT)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glPushMatrix()
        self._apply_global_transform()

        self._draw_canvas_bg()
        if self.show_grid:
            self._draw_grid()
        for shape in self.scene.get_shapes():
            shape.draw()

        
        
        # Canvas
        self._draw_canvas_bg()

        # Grid
        if self.show_grid:
            self._draw_grid()

        # Shape’ler (z-order)
        for shape in self.scene.get_shapes():
            shape.draw()

        glPopMatrix()
    # ─────────────────────────────────────────────

    def _draw_canvas_bg(self):
        r, g, b = _rgb(COLOR_CANVAS)
        glColor3f(r, g, b)
        
        # Draw a massive quad that extends way off-screen 
        # so you never see the black void when rotating
        glBegin(GL_QUADS)
        glVertex2f(-4000, -4000)
        glVertex2f(4000, -4000)
        glVertex2f(4000, 4000)
        glVertex2f(-4000, 4000)

        glEnd()

    # ─────────────────────────────────────────────

    def _draw_grid(self):
        # Define massive boundaries for the infinite canvas effect
        start_bound = -4000
        end_bound = 4000

        # --- İnce grid (Minor Grid) ---
        r, g, b = _rgb(COLOR_GRID)
        glColor3f(r, g, b)
        glLineWidth(1.0)

        glBegin(GL_LINES)

        # Dikey (Vertical)
        # We step backwards from CANVAS_X to ensure the grid stays perfectly locked
        x = CANVAS_X
        while x > start_bound:
            x -= GRID_SIZE
            
        while x <= end_bound:
            glVertex2f(x, start_bound)
            glVertex2f(x, end_bound)
            x += GRID_SIZE

        # Yatay (Horizontal)
        # We step backwards from 0
        y = 0
        while y > start_bound:
            y -= GRID_SIZE

        while y <= end_bound:
            glVertex2f(start_bound, y)
            glVertex2f(end_bound, y)
            y += GRID_SIZE

        glEnd()

        # --- Kalın grid (Major Grid - her 5 karede bir) ---
        r, g, b = _rgb(COLOR_GRID_MAJOR)
        glColor3f(r, g, b)
        glLineWidth(2.0)

        glBegin(GL_LINES)

        # Dikey (Vertical)
        x = CANVAS_X
        # Step backwards by exactly 5 grid chunks so the major lines don't lose sync
        while x > start_bound:
            x -= GRID_SIZE * 5
            
        while x <= end_bound:
            glVertex2f(x, start_bound)
            glVertex2f(x, end_bound)
            x += GRID_SIZE * 5

        # Yatay (Horizontal)
        y = 0
        while y > start_bound:
            y -= GRID_SIZE * 5

        while y <= end_bound:
            glVertex2f(start_bound, y)
            glVertex2f(end_bound, y)
            y += GRID_SIZE * 5

        glEnd()

        glLineWidth(1.0)

    def draw_preview(self, shape):
        """
        Çizim sırasında geçici shape (mouse basılıyken)
        """
        if shape is None:
            return
        
        glPushMatrix()
        self._apply_global_transform() # Apply rotation here too!
        
        target_alpha = getattr(shape, "alpha", 1.0)
        preview_alpha = target_alpha * 0.5 
        
        glColor4f(*shape.outline_color, preview_alpha)
        shape.draw()
        
        glPopMatrix()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(*shape.outline_color, 0.5)
        shape.draw()

        glDisable(GL_BLEND)

    def draw_rotation_pivot(self, shape):
        if shape is None:
            return

        glPushMatrix()
        self._apply_global_transform()
        cx, cy = shape.get_center()

        glColor3f(0.0, 0.7, 1.0)
        glLineWidth(2.0)

        glBegin(GL_LINES)
        glVertex2f(cx - 8, cy)
        glVertex2f(cx + 8, cy)
        glVertex2f(cx, cy - 8)
        glVertex2f(cx, cy + 8)
        glEnd()

        glBegin(GL_LINE_LOOP)
        for i in range(24):
            angle = 2 * 3.14159 * i / 24
            glVertex2f(cx + 5 * math.cos(angle), cy + 5 * math.sin(angle))
        glEnd()

        glLineWidth(1.0)

        glPopMatrix()

    def draw_dynamic_input(self, tool, value_string):
        """Draws an AutoCAD-style floating input box next to the cursor."""
        if tool not in ("polygon", "star"):
            return
            
        import pygame
        mx, my = pygame.mouse.get_pos()
        
        # Box positioning (offset slightly bottom-right from cursor)
        box_x = mx + 15
        box_y = my + 15
        box_w = 60
        box_h = 24
        
        # Enable blending for a sleek, semi-transparent HUD look
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Draw dark semi-transparent background
        glColor4f(0.1, 0.1, 0.15, 0.85)
        glBegin(GL_QUADS)
        glVertex2f(box_x, box_y)
        glVertex2f(box_x + box_w, box_y)
        glVertex2f(box_x + box_w, box_y + box_h)
        glVertex2f(box_x, box_y + box_h)
        glEnd()
        
        # Draw precise blue border
        glColor4f(0.3, 0.6, 1.0, 1.0)
        glLineWidth(1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(box_x, box_y)
        glVertex2f(box_x + box_w, box_y)
        glVertex2f(box_x + box_w, box_y + box_h)
        glVertex2f(box_x, box_y + box_h)
        glEnd()
        
        glDisable(GL_BLEND)

        label_text = "Sides" if tool == "polygon" else "Points"
        

        # We need to borrow Pygame's font renderer briefly
        font = pygame.font.SysFont("segoeui", 12)
        text_surface = self.input_font.render(f"{label_text}: {value_string}", True, (255, 255, 255))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        glEnable(GL_BLEND)
        glRasterPos2f(box_x + 4, box_y + 16) # Align text inside box
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glDisable(GL_BLEND)

    def _apply_global_transform(self):
        from src.utils.constants import CANVAS_X, CANVAS_W, CANVAS_H
        cx = CANVAS_X + CANVAS_W / 2
        cy = CANVAS_H / 2
        
        # Move to center, rotate, move back
        glTranslatef(cx, cy, 0)
        rotation = getattr(self.scene, "global_rotation", 0.0)
        glRotatef(rotation, 0, 0, 1)
        glTranslatef(-cx, -cy, 0)