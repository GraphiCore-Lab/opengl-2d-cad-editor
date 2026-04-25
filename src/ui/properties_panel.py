from OpenGL.GL import *
import pygame
from src.utils.constants import WIDTH, HEIGHT


HEX_COLORS = [
    ("#FF0000", (1.0, 0.0, 0.0)),
    ("#00FF00", (0.0, 1.0, 0.0)),
    ("#0000FF", (0.0, 0.0, 1.0)),
    ("#FFFF00", (1.0, 1.0, 0.0)),
    ("#FF00FF", (1.0, 0.0, 1.0)),
    ("#00FFFF", (0.0, 1.0, 1.0)),
    ("#000000", (0.0, 0.0, 0.0)),
    ("#FFFFFF", (1.0, 1.0, 1.0)),
]


class PropertiesPanel:
    def __init__(self):
        self.width = 220
        self.x = WIDTH - self.width
        self.y = 50
        self.height = HEIGHT - 80

        self.color_menu_open = False
        self.color_target = "outline"

        self.buttons = [
            {"name": "fill_toggle", "label": "Fill On/Off", "x": self.x + 20, "y": self.y + 65, "w": 170, "h": 30},
            {"name": "line_width", "label": "Line Width", "x": self.x + 20, "y": self.y + 105, "w": 170, "h": 30},

            {"name": "color_outline_menu", "label": "🎨 Outline Color", "x": self.x + 20, "y": self.y + 155, "w": 170, "h": 30},
            {"name": "color_fill_menu", "label": "🪣 Fill Color", "x": self.x + 20, "y": self.y + 195, "w": 170, "h": 30},

            {"name": "bring_front", "label": "Bring Front", "x": self.x + 20, "y": self.y + 340, "w": 170, "h": 30},
            {"name": "send_back", "label": "Send Back", "x": self.x + 20, "y": self.y + 380, "w": 170, "h": 30},
            {"name": "duplicate", "label": "Duplicate", "x": self.x + 20, "y": self.y + 420, "w": 170, "h": 30},
            {"name": "delete", "label": "Delete", "x": self.x + 20, "y": self.y + 460, "w": 170, "h": 30},
        ]

        self.color_buttons = []
        self._build_color_buttons()

        pygame.font.init()
        self.font = pygame.font.SysFont("Segoe UI Emoji", 14)
        self.title_font = pygame.font.SysFont("Segoe UI Emoji", 16, bold=True)

    def _build_color_buttons(self):
        self.color_buttons.clear()

        start_x = self.x + 20
        start_y = self.y + 235
        size = 35
        gap = 8

        for i, (hex_code, color) in enumerate(HEX_COLORS):
            col = i % 4
            row = i // 4

            self.color_buttons.append({
                "name": f"hex_color:{hex_code}",
                "hex": hex_code,
                "color": color,
                "x": start_x + col * (size + gap),
                "y": start_y + row * (size + gap),
                "w": size,
                "h": size,
            })

    def draw(self, selected_shape):
        glColor3f(0.94, 0.94, 0.94)
        self._draw_rect(self.x, self.y, self.width, self.height)

        glColor3f(0.22, 0.22, 0.22)
        self._draw_border(self.x, self.y, self.width, self.height)

        self._draw_text("Properties", self.x + 20, self.y + 20, self.title_font)

        if selected_shape is None:
            self._draw_text("No object selected", self.x + 20, self.y + 45, self.font)
        else:
            self._draw_text("Object selected", self.x + 20, self.y + 45, self.font)

        for button in self.buttons:
            if selected_shape is None:
                glColor3f(0.72, 0.72, 0.72)
            else:
                glColor3f(0.86, 0.86, 0.86)

            self._draw_rect(button["x"], button["y"], button["w"], button["h"])

            glColor3f(0.25, 0.25, 0.25)
            self._draw_border(button["x"], button["y"], button["w"], button["h"])

            self._draw_text(button["label"], button["x"] + 10, button["y"] + 8, self.font)

        if self.color_menu_open:
            self._draw_text("Select HEX Color", self.x + 20, self.y + 230, self.font)

            for button in self.color_buttons:
                glColor3f(*button["color"])
                self._draw_rect(button["x"], button["y"], button["w"], button["h"])

                glColor3f(0.2, 0.2, 0.2)
                self._draw_border(button["x"], button["y"], button["w"], button["h"])

            target_text = "Target: Outline" if self.color_target == "outline" else "Target: Fill"
            self._draw_text(target_text, self.x + 20, self.y + 320, self.font)

        if selected_shape is not None:
            outline = getattr(selected_shape, "outline_color", None)
            fill = getattr(selected_shape, "fill_color", None)
            line_width = getattr(selected_shape, "line_width", None)

            self._draw_text(f"Outline: {outline}", self.x + 20, self.y + 505, self.font)
            self._draw_text(f"Fill: {fill}", self.x + 20, self.y + 525, self.font)
            self._draw_text(f"Width: {line_width}", self.x + 20, self.y + 545, self.font)

    def handle_click(self, x, y):
        for button in self.buttons:
            if button["x"] <= x <= button["x"] + button["w"] and button["y"] <= y <= button["y"] + button["h"]:
                if button["name"] == "color_outline_menu":
                    self.color_target = "outline"
                    self.color_menu_open = not self.color_menu_open
                    return None

                if button["name"] == "color_fill_menu":
                    self.color_target = "fill"
                    self.color_menu_open = not self.color_menu_open
                    return None

                print(f"Panel action: {button['name']}")
                return button["name"]

        if self.color_menu_open:
            for button in self.color_buttons:
                if button["x"] <= x <= button["x"] + button["w"] and button["y"] <= y <= button["y"] + button["h"]:
                    hex_code = button["hex"]

                    if self.color_target == "outline":
                        return f"outline_hex:{hex_code}"

                    return f"fill_hex:{hex_code}"

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