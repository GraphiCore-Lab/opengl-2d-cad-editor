from OpenGL.GL import *
from src.utils.constants import WIDTH, HEIGHT


class PropertiesPanel:
    def __init__(self):
        self.width = 220
        self.x = WIDTH - self.width
        self.y = 50
        self.height = HEIGHT - 80

        self.buttons = [
            {"name": "fill_toggle", "x": self.x + 20, "y": self.y + 40, "w": 170, "h": 30},
            {"name": "line_width", "x": self.x + 20, "y": self.y + 80, "w": 170, "h": 30},
            {"name": "bring_front", "x": self.x + 20, "y": self.y + 130, "w": 170, "h": 30},
            {"name": "send_back", "x": self.x + 20, "y": self.y + 170, "w": 170, "h": 30},
            {"name": "duplicate", "x": self.x + 20, "y": self.y + 210, "w": 170, "h": 30},
            {"name": "delete", "x": self.x + 20, "y": self.y + 250, "w": 170, "h": 30},
        ]

    def draw(self, selected_shape):
        glColor3f(0.92, 0.92, 0.92)
        self._draw_rect(self.x, self.y, self.width, self.height)

        glColor3f(0.2, 0.2, 0.2)
        self._draw_border(self.x, self.y, self.width, self.height)

        for button in self.buttons:
            if selected_shape is None:
                glColor3f(0.75, 0.75, 0.75)
            else:
                glColor3f(0.82, 0.82, 0.82)

            self._draw_rect(button["x"], button["y"], button["w"], button["h"])

            glColor3f(0.25, 0.25, 0.25)
            self._draw_border(button["x"], button["y"], button["w"], button["h"])

    def handle_click(self, x, y):
        for button in self.buttons:
            if (
                button["x"] <= x <= button["x"] + button["w"]
                and button["y"] <= y <= button["y"] + button["h"]
            ):
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