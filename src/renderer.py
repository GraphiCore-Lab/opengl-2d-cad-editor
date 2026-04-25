"""
Renderer: her frame'de sahneyi OpenGL ile çizer.
Kişi 1 + UI entegrasyonu (Kişi 3 uyumlu)
"""

from OpenGL.GL import *

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

    # ─────────────────────────────────────────────

    def render(self):
        """Ana render fonksiyonu — her frame çağrılır."""
        glClear(GL_COLOR_BUFFER_BIT)

        # Canvas
        self._draw_canvas_bg()

        # Grid
        if self.show_grid:
            self._draw_grid()

        # Shape’ler (z-order)
        for shape in self.scene.get_shapes():
            shape.draw()

    # ─────────────────────────────────────────────

    def _draw_canvas_bg(self):
        r, g, b = _rgb(COLOR_CANVAS)

        glColor3f(r, g, b)
        glBegin(GL_QUADS)

        glVertex2f(CANVAS_X, 0)
        glVertex2f(CANVAS_X + CANVAS_W, 0)
        glVertex2f(CANVAS_X + CANVAS_W, CANVAS_H)
        glVertex2f(CANVAS_X, CANVAS_H)

        glEnd()

    # ─────────────────────────────────────────────

    def _draw_grid(self):
        # İnce grid
        r, g, b = _rgb(COLOR_GRID)
        glColor3f(r, g, b)
        glLineWidth(1.0)

        glBegin(GL_LINES)

        # Dikey
        x = CANVAS_X
        while x <= CANVAS_X + CANVAS_W:
            glVertex2f(x, 0)
            glVertex2f(x, CANVAS_H)
            x += GRID_SIZE

        # Yatay
        y = 0
        while y <= CANVAS_H:
            glVertex2f(CANVAS_X, y)
            glVertex2f(CANVAS_X + CANVAS_W, y)
            y += GRID_SIZE

        glEnd()

        # Kalın grid (her 5 karede bir)
        r, g, b = _rgb(COLOR_GRID_MAJOR)
        glColor3f(r, g, b)
        glLineWidth(2.0)

        glBegin(GL_LINES)

        x = CANVAS_X
        i = 0
        while x <= CANVAS_X + CANVAS_W:
            if i % 5 == 0:
                glVertex2f(x, 0)
                glVertex2f(x, CANVAS_H)
            x += GRID_SIZE
            i += 1

        y = 0
        i = 0
        while y <= CANVAS_H:
            if i % 5 == 0:
                glVertex2f(CANVAS_X, y)
                glVertex2f(CANVAS_X + CANVAS_W, y)
            y += GRID_SIZE
            i += 1

        glEnd()

        glLineWidth(1.0)

    # ─────────────────────────────────────────────

    def draw_preview(self, shape):
        """
        Çizim sırasında geçici shape (mouse basılıyken)
        """
        if shape is None:
            return

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(*shape.color, 0.5)
        shape.draw()

        glDisable(GL_BLEND)