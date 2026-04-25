from OpenGL.GL import *


class Toolbar:
    def __init__(self):
        self.buttons = [
            {"name": "select", "x": 10, "y": 10, "w": 70, "h": 30},
            {"name": "line", "x": 90, "y": 10, "w": 70, "h": 30},
            {"name": "rect", "x": 170, "y": 10, "w": 70, "h": 30},
            {"name": "circle", "x": 250, "y": 10, "w": 70, "h": 30},
            {"name": "move", "x": 330, "y": 10, "w": 70, "h": 30},
            {"name": "rotate", "x": 410, "y": 10, "w": 70, "h": 30},
            {"name": "scale", "x": 490, "y": 10, "w": 70, "h": 30},
        ]

    def draw(self, active_tool):
        for button in self.buttons:
            if button["name"] == active_tool:
                glColor3f(0.55, 0.75, 1.0)
            else:
                glColor3f(0.85, 0.85, 0.85)

            self._draw_rect(button["x"], button["y"], button["w"], button["h"])

            glColor3f(0.2, 0.2, 0.2)
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