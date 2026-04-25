from OpenGL.GL import *
import pygame
from src.utils.constants import WIDTH, HEIGHT


class PropertiesPanel:
    def __init__(self):
        self.width = 220
        self.x = WIDTH - self.width
        self.y = 50
        self.height = HEIGHT - 80

        self.buttons = [
            {"name": "fill_toggle", "label": "Fill On/Off", "x": self.x + 20, "y": self.y + 60, "w": 170, "h": 30},
            {"name": "line_width", "label": "Line Width", "x": self.x + 20, "y": self.y + 100, "w": 170, "h": 30},
            {"name": "bring_front", "label": "Bring Front", "x": self.x + 20, "y": self.y + 160, "w": 170, "h": 30},
            {"name": "send_back", "label": "Send Back", "x": self.x + 20, "y": self.y + 200, "w": 170, "h": 30},
            {"name": "duplicate", "label": "Duplicate", "x": self.x + 20, "y": self.y + 240, "w": 170, "h": 30},
            {"name": "delete", "label": "Delete", "x": self.x + 20, "y": self.y + 280, "w": 170, "h": 30},
        ]

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14)
        self.title_font = pygame.font.SysFont("Arial", 16, bold=True)

    def draw(self, selected_shape):
        glColor3f(0.92, 0.92, 0.92)
        self._draw_rect(self.x, self.y, self.width, self.height)

        glColor3f(0.2, 0.2, 0.2)
        self._draw_border(self.x, self.y, self.width, self.height)

        self._draw_text("Properties", self.x + 20, self.y + 20, self.title_font)

        if selected_shape is None:
            self._draw_text("No object selected", self.x + 20, self.y + 42, self.font)
        else:
            self._draw_text("Object selected", self.x + 20, self.y + 42, self.font)

        for button in self.buttons:
            glColor3f(0.72, 0.72, 0.72) if selected_shape is None else glColor3f(0.82, 0.82, 0.82)

            self._draw_rect(button["x"], button["y"], button["w"], button["h"])

            glColor3f(0.25, 0.25, 0.25)
            self._draw_border(button["x"], button["y"], button["w"], button["h"])

            self._draw_text(button["label"], button["x"] + 12, button["y"] + 8, self.font)

    def handle_click(self, x, y):
        for button in self.buttons:
            if button["x"] <= x <= button["x"] + button["w"] and button["y"] <= y <= button["y"] + button["h"]:
                print(f"Panel action: {button['name']}")
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

    def _draw_text(self, text, x, y, font):
        surface = font.render(text, True, (20, 20, 20), None)
        text_data = pygame.image.tostring(surface, "RGBA", True)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glRasterPos2f(x, y + surface.get_height())
        glDrawPixels(surface.get_width(), surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glDisable(GL_BLEND)