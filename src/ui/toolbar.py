from OpenGL.GL import *
import pygame


class Toolbar:
    def __init__(self):
        self.buttons = [
            {"name": "select", "label": "Select", "x": 10, "y": 10, "w": 90, "h": 30},
            {"name": "line", "label": "Line", "x": 110, "y": 10, "w": 80, "h": 30},
            {"name": "rect", "label": "Rect", "x": 200, "y": 10, "w": 80, "h": 30},
            {"name": "circle", "label": "Circle", "x": 290, "y": 10, "w": 90, "h": 30},
            {"name": "move", "label": "Move", "x": 390, "y": 10, "w": 80, "h": 30},
            {"name": "rotate", "label": "Rotate", "x": 480, "y": 10, "w": 90, "h": 30},
            {"name": "scale", "label": "Scale", "x": 580, "y": 10, "w": 80, "h": 30},
        ]
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14)

    def draw(self, active_tool):
        for button in self.buttons:
            glColor3f(0.55, 0.75, 1.0) if button["name"] == active_tool else glColor3f(0.85, 0.85, 0.85)

            self._draw_rect(button["x"], button["y"], button["w"], button["h"])

            glColor3f(0.2, 0.2, 0.2)
            self._draw_border(button["x"], button["y"], button["w"], button["h"])

            self._draw_text(button["label"], button["x"] + 12, button["y"] + 8)

    def handle_click(self, x, y):
        for button in self.buttons:
            if button["x"] <= x <= button["x"] + button["w"] and button["y"] <= y <= button["y"] + button["h"]:
                print(f"Selected tool: {button['name']}")
                return button["name"]
        return None

    def _draw_rect(self, x, y, w, h):
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

    def _draw_border(self, x, y, w, h):
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

    def _draw_text(self, text, x, y):
        surface = self.font.render(text, True, (20, 20, 20), None)
        text_data = pygame.image.tostring(surface, "RGBA", True)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glRasterPos2f(x, y + surface.get_height())
        glDrawPixels(surface.get_width(), surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glDisable(GL_BLEND)