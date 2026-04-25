from OpenGL.GL import *
import pygame


class Toolbar:
    def __init__(self):
        self.buttons = [
            {"name": "select", "label": "🖱 Select", "x": 10, "y": 10, "w": 95, "h": 30},
            {"name": "shapes_menu", "label": "🧩 Shapes ▼", "x": 115, "y": 10, "w": 120, "h": 30},
            {"name": "move", "label": "↔ Move", "x": 245, "y": 10, "w": 85, "h": 30},
            {"name": "rotate", "label": "🔄 Rotate", "x": 340, "y": 10, "w": 100, "h": 30},
            {"name": "scale", "label": "🔍 Scale", "x": 450, "y": 10, "w": 90, "h": 30},
        ]

        self.shape_dropdown_open = False

        self.shape_buttons = [
            {"name": "line", "label": "Line", "x": 115, "y": 45, "w": 120, "h": 28},
            {"name": "rect", "label": "Rectangle", "x": 115, "y": 75, "w": 120, "h": 28},
            {"name": "circle", "label": "Circle", "x": 115, "y": 105, "w": 120, "h": 28},
            {"name": "triangle", "label": "Triangle", "x": 115, "y": 135, "w": 120, "h": 28},
        ]

        pygame.font.init()
        self.font = pygame.font.SysFont("Segoe UI Emoji", 14)

    def draw(self, active_tool):
        for button in self.buttons:
            if button["name"] == active_tool:
                glColor3f(0.45, 0.68, 1.0)
            else:
                glColor3f(0.86, 0.86, 0.86)

            self._draw_rect(button["x"], button["y"], button["w"], button["h"])
            glColor3f(0.2, 0.2, 0.2)
            self._draw_border(button["x"], button["y"], button["w"], button["h"])
            self._draw_text(button["label"], button["x"] + 10, button["y"] + 8)

        if self.shape_dropdown_open:
            for button in self.shape_buttons:
                if button["name"] == active_tool:
                    glColor3f(0.55, 0.75, 1.0)
                else:
                    glColor3f(0.96, 0.96, 0.96)

                self._draw_rect(button["x"], button["y"], button["w"], button["h"])
                glColor3f(0.25, 0.25, 0.25)
                self._draw_border(button["x"], button["y"], button["w"], button["h"])
                self._draw_text(button["label"], button["x"] + 12, button["y"] + 7)

    def handle_click(self, x, y):
        for button in self.buttons:
            if button["x"] <= x <= button["x"] + button["w"] and button["y"] <= y <= button["y"] + button["h"]:
                if button["name"] == "shapes_menu":
                    self.shape_dropdown_open = not self.shape_dropdown_open
                    return None

                self.shape_dropdown_open = False
                print(f"Selected tool: {button['name']}")
                return button["name"]

        if self.shape_dropdown_open:
            for button in self.shape_buttons:
                if button["x"] <= x <= button["x"] + button["w"] and button["y"] <= y <= button["y"] + button["h"]:
                    self.shape_dropdown_open = False
                    print(f"Selected shape: {button['name']}")
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