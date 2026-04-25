from OpenGL.GL import *
import pygame
import colorsys


class Toolbar:
    def __init__(self):
        self.height = 92

        self.buttons = [
            {"name": "select", "label": "Select", "x": 12, "y": 12, "w": 75, "h": 32},
            {"name": "move", "label": "Move", "x": 92, "y": 12, "w": 65, "h": 32},
            {"name": "rotate", "label": "Rotate", "x": 162, "y": 12, "w": 75, "h": 32},
            {"name": "scale", "label": "Scale", "x": 242, "y": 12, "w": 65, "h": 32},

            {"name": "line", "label": "Line", "x": 330, "y": 12, "w": 55, "h": 32},
            {"name": "rect", "label": "Rect", "x": 390, "y": 12, "w": 55, "h": 32},
            {"name": "circle", "label": "Circle", "x": 450, "y": 12, "w": 65, "h": 32},
            {"name": "triangle", "label": "Tri", "x": 520, "y": 12, "w": 50, "h": 32},

            {"name": "width:1", "label": "1px", "x": 590, "y": 12, "w": 45, "h": 32},
            {"name": "width:2", "label": "2px", "x": 640, "y": 12, "w": 45, "h": 32},
            {"name": "width:4", "label": "4px", "x": 690, "y": 12, "w": 45, "h": 32},
            {"name": "width:6", "label": "6px", "x": 740, "y": 12, "w": 45, "h": 32},
        ]

        self.color_target = "outline"

        self.color_buttons = [
            {"name": "target:outline", "label": "Outline", "x": 805, "y": 12, "w": 82, "h": 32},
            {"name": "target:fill", "label": "Fill", "x": 895, "y": 12, "w": 62, "h": 32},
            {"name": "open_color_picker", "label": "Edit colors", "x": 965, "y": 12, "w": 110, "h": 32},
        ]

        self.color_picker_open = False

        self.picker_x = 125
        self.picker_y = 130
        self.picker_w = 610
        self.picker_h = 470

        self.gradient_x = self.picker_x + 25
        self.gradient_y = self.picker_y + 70
        self.gradient_w = 260
        self.gradient_h = 255

        self.value_x = self.gradient_x + self.gradient_w + 15
        self.value_y = self.gradient_y
        self.value_w = 42
        self.value_h = self.gradient_h

        self.current_hue = 0.55
        self.current_saturation = 0.65
        self.current_value = 0.65
        self.selected_color = colorsys.hsv_to_rgb(
            self.current_hue,
            self.current_saturation,
            self.current_value
        )

        self.dragging_gradient = False
        self.dragging_value = False

        self.active_input = None
        self.input_text = ""

        pygame.font.init()
        self.font = pygame.font.SysFont("Segoe UI", 13)
        self.title_font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.small_font = pygame.font.SysFont("Segoe UI", 12)

    def draw(self, active_tool, current_outline=None, current_fill=None, line_width=2):
        self._draw_toolbar_background()

        self._draw_group_title("Tools", 12, 72)
        self._draw_group_title("Shapes", 330, 72)
        self._draw_group_title("Size", 590, 72)
        self._draw_group_title("Colors", 805, 72)

        for button in self.buttons:
            active = button["name"] == active_tool

            if button["name"].startswith("width:"):
                width_value = int(button["name"].split(":")[1])
                active = width_value == int(line_width)

            self._draw_button(button, active)

        for button in self.color_buttons:
            active = button["name"] == f"target:{self.color_target}"
            self._draw_button(button, active)

        self._draw_color_preview(805, 50, current_outline, "Outline")
        self._draw_color_preview(895, 50, current_fill, "Fill")

    def draw_overlay(self):
        if self.color_picker_open:
            self._draw_color_picker()

    def handle_click(self, x, y):
        if self.color_picker_open:
            return self._handle_color_picker_click(x, y)

        for button in self.buttons:
            if self._inside(button, x, y):
                return button["name"]

        for button in self.color_buttons:
            if self._inside(button, x, y):
                if button["name"] == "target:outline":
                    self.color_target = "outline"
                    return None

                if button["name"] == "target:fill":
                    self.color_target = "fill"
                    return None

                if button["name"] == "open_color_picker":
                    self.color_picker_open = True
                    return None

        return None

    def handle_mouse_motion(self, x, y):
        if not self.color_picker_open:
            return None

        if self.dragging_gradient:
            self._select_from_gradient(x, y)
            return None

        if self.dragging_value:
            self._select_from_value_slider(y)
            return None

        return None

    def handle_mouse_up(self):
        self.dragging_gradient = False
        self.dragging_value = False

    def handle_key_down(self, event):
        if not self.color_picker_open or self.active_input is None:
            return None

        if event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
            return None

        if event.key == pygame.K_RETURN:
            return self._commit_active_input()

        if event.key == pygame.K_ESCAPE:
            self.active_input = None
            self.input_text = ""
            return None

        char = event.unicode

        if self.active_input == "hex":
            if char and char.upper() in "0123456789ABCDEF#":
                self.input_text += char.upper()

        elif self.active_input in ("r", "g", "b"):
            if char and char.isdigit():
                self.input_text += char

        return None

    def _handle_color_picker_click(self, x, y):
        clicked_input = self._get_clicked_input(x, y)

        if clicked_input:
            self.active_input = clicked_input

            if clicked_input == "hex":
                self.input_text = self._rgb_to_hex(self.selected_color)
            elif clicked_input == "r":
                self.input_text = str(int(self.selected_color[0] * 255))
            elif clicked_input == "g":
                self.input_text = str(int(self.selected_color[1] * 255))
            elif clicked_input == "b":
                self.input_text = str(int(self.selected_color[2] * 255))

            return None

        if self._point_in_rect(x, y, self.gradient_x, self.gradient_y, self.gradient_w, self.gradient_h):
            self.active_input = None
            self.input_text = ""
            self.dragging_gradient = True
            self._select_from_gradient(x, y)
            return None

        if self._point_in_rect(x, y, self.value_x, self.value_y, self.value_w, self.value_h):
            self.active_input = None
            self.input_text = ""
            self.dragging_value = True
            self._select_from_value_slider(y)
            return None

        ok_button = {
            "x": self.picker_x + 25,
            "y": self.picker_y + self.picker_h - 50,
            "w": 280,
            "h": 30,
        }

        cancel_button = {
            "x": self.picker_x + 315,
            "y": self.picker_y + self.picker_h - 50,
            "w": 270,
            "h": 30,
        }

        close_button = {
            "x": self.picker_x + self.picker_w - 35,
            "y": self.picker_y + 10,
            "w": 25,
            "h": 25,
        }

        if self._inside(ok_button, x, y):
            self.color_picker_open = False
            self.active_input = None
            self.input_text = ""
            return self._color_action()

        if self._inside(cancel_button, x, y):
            self.color_picker_open = False
            self.active_input = None
            self.input_text = ""
            return None

        if self._inside(close_button, x, y):
            self.color_picker_open = False
            self.active_input = None
            self.input_text = ""
            return None

        return None

    def _select_from_gradient(self, x, y):
        local_x = max(0, min(self.gradient_w, x - self.gradient_x))
        local_y = max(0, min(self.gradient_h, y - self.gradient_y))

        self.current_hue = local_x / self.gradient_w
        self.current_saturation = 1.0 - (local_y / self.gradient_h)

        self._update_selected_color()

    def _select_from_value_slider(self, y):
        local_y = max(0, min(self.value_h, y - self.value_y))
        self.current_value = 1.0 - (local_y / self.value_h)

        self._update_selected_color()

    def _update_selected_color(self):
        self.selected_color = colorsys.hsv_to_rgb(
            self.current_hue,
            self.current_saturation,
            self.current_value
        )

    def _sync_hsv_from_rgb(self):
        self.current_hue, self.current_saturation, self.current_value = colorsys.rgb_to_hsv(
            self.selected_color[0],
            self.selected_color[1],
            self.selected_color[2]
        )

    def _commit_active_input(self):
        try:
            if self.active_input == "hex":
                text = self.input_text.strip().replace("#", "")

                if len(text) != 6:
                    return None

                r = int(text[0:2], 16) / 255
                g = int(text[2:4], 16) / 255
                b = int(text[4:6], 16) / 255

                self.selected_color = (r, g, b)
                self._sync_hsv_from_rgb()

            elif self.active_input in ("r", "g", "b"):
                value = max(0, min(255, int(self.input_text or "0")))

                r = int(self.selected_color[0] * 255)
                g = int(self.selected_color[1] * 255)
                b = int(self.selected_color[2] * 255)

                if self.active_input == "r":
                    r = value
                elif self.active_input == "g":
                    g = value
                elif self.active_input == "b":
                    b = value

                self.selected_color = (r / 255, g / 255, b / 255)
                self._sync_hsv_from_rgb()

            self.active_input = None
            self.input_text = ""

            return self._color_action()

        except ValueError:
            return None

    def _color_action(self):
        r, g, b = self.selected_color

        if self.color_target == "outline":
            return f"outline_color:{r},{g},{b}"

        return f"fill_color:{r},{g},{b}"

    def _draw_color_picker(self):
        self._draw_shadow(self.picker_x, self.picker_y, self.picker_w, self.picker_h)

        glColor3f(0.97, 0.97, 0.97)
        self._draw_rect(self.picker_x, self.picker_y, self.picker_w, self.picker_h)

        glColor3f(0.68, 0.68, 0.68)
        self._draw_border(self.picker_x, self.picker_y, self.picker_w, self.picker_h)

        self._draw_text("Edit colors", self.picker_x + 25, self.picker_y + 35, self.title_font)
        self._draw_text("×", self.picker_x + self.picker_w - 28, self.picker_y + 13, self.font)

        self._draw_gradient_area()
        self._draw_value_slider()
        self._draw_selected_color_preview()
        self._draw_rgb_inputs()
        self._draw_basic_color_dots()
        self._draw_custom_color_dots()

        self._draw_dialog_button(
            self.picker_x + 25,
            self.picker_y + self.picker_h - 50,
            280,
            30,
            "OK",
            active=True
        )

        self._draw_dialog_button(
            self.picker_x + 315,
            self.picker_y + self.picker_h - 50,
            270,
            30,
            "Cancel",
            active=False
        )

    def _draw_gradient_area(self):
        steps_x = 80
        steps_y = 80
        cell_w = self.gradient_w / steps_x
        cell_h = self.gradient_h / steps_y

        glBegin(GL_QUADS)

        for ix in range(steps_x):
            hue = ix / (steps_x - 1)

            for iy in range(steps_y):
                saturation = 1.0 - (iy / (steps_y - 1))
                r, g, b = colorsys.hsv_to_rgb(hue, saturation, self.current_value)

                x = self.gradient_x + ix * cell_w
                y = self.gradient_y + iy * cell_h

                glColor3f(r, g, b)
                glVertex2f(x, y)
                glVertex2f(x + cell_w + 1, y)
                glVertex2f(x + cell_w + 1, y + cell_h + 1)
                glVertex2f(x, y + cell_h + 1)

        glEnd()

        glColor3f(0.75, 0.75, 0.75)
        self._draw_border(self.gradient_x, self.gradient_y, self.gradient_w, self.gradient_h)

        marker_x = self.gradient_x + self.current_hue * self.gradient_w
        marker_y = self.gradient_y + (1.0 - self.current_saturation) * self.gradient_h

        glColor3f(0.0, 0.0, 0.0)
        self._draw_circle(marker_x, marker_y, 7, fill=False)

        glColor3f(1.0, 1.0, 1.0)
        self._draw_circle(marker_x, marker_y, 5, fill=False)

    def _draw_value_slider(self):
        steps = 100
        cell_h = self.value_h / steps

        glBegin(GL_QUADS)

        for i in range(steps):
            value = 1.0 - (i / (steps - 1))
            r, g, b = colorsys.hsv_to_rgb(
                self.current_hue,
                self.current_saturation,
                value
            )

            x = self.value_x
            y = self.value_y + i * cell_h

            glColor3f(r, g, b)
            glVertex2f(x, y)
            glVertex2f(x + self.value_w, y)
            glVertex2f(x + self.value_w, y + cell_h + 1)
            glVertex2f(x, y + cell_h + 1)

        glEnd()

        glColor3f(0.75, 0.75, 0.75)
        self._draw_border(self.value_x, self.value_y, self.value_w, self.value_h)

        marker_y = self.value_y + (1.0 - self.current_value) * self.value_h

        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex2f(self.value_x, marker_y)
        glVertex2f(self.value_x + self.value_w, marker_y)
        glEnd()
        glLineWidth(1)

    def _draw_selected_color_preview(self):
        x = self.value_x + 70
        y = self.value_y
        w = 45
        h = self.value_h

        glColor3f(*self.selected_color)
        self._draw_rect(x, y, w, h)

        glColor3f(0.75, 0.75, 0.75)
        self._draw_border(x, y, w, h)

        hex_box = self._get_input_boxes()["hex"]
        hex_text = self.input_text if self.active_input == "hex" else self._rgb_to_hex(self.selected_color)

        self._draw_input_box(
            hex_box["x"],
            hex_box["y"],
            hex_box["w"],
            hex_box["h"],
            hex_text,
            active=self.active_input == "hex"
        )

    def _draw_rgb_inputs(self):
        boxes = self._get_input_boxes()

        r = int(self.selected_color[0] * 255)
        g = int(self.selected_color[1] * 255)
        b = int(self.selected_color[2] * 255)

        values = {
            "r": self.input_text if self.active_input == "r" else str(r),
            "g": self.input_text if self.active_input == "g" else str(g),
            "b": self.input_text if self.active_input == "b" else str(b),
        }

        labels = {
            "r": "Red",
            "g": "Green",
            "b": "Blue",
        }

        for key in ("r", "g", "b"):
            box = boxes[key]

            self._draw_input_box(
                box["x"],
                box["y"],
                box["w"],
                box["h"],
                values[key],
                active=self.active_input == key
            )

            self._draw_text(labels[key], box["x"] + 105, box["y"] + 7, self.font)

    def _get_input_boxes(self):
        hex_x = self.value_x + 155
        hex_y = self.value_y

        rgb_x = self.value_x + 155
        rgb_y = self.value_y + 84

        return {
            "hex": {"x": hex_x, "y": hex_y, "w": 110, "h": 30},
            "r": {"x": rgb_x, "y": rgb_y, "w": 95, "h": 28},
            "g": {"x": rgb_x, "y": rgb_y + 40, "w": 95, "h": 28},
            "b": {"x": rgb_x, "y": rgb_y + 80, "w": 95, "h": 28},
        }

    def _get_clicked_input(self, x, y):
        for name, box in self._get_input_boxes().items():
            if self._inside(box, x, y):
                return name

        return None

    def _draw_basic_color_dots(self):
        self._draw_text("Basic colors", self.picker_x + 25, self.picker_y + 320, self.small_font)

        colors = [
            (0.96, 0.45, 0.45), (1.0, 0.15, 0.1), (0.45, 0.25, 0.25),
            (0.55, 0.22, 0.18), (0.25, 0.02, 0.0), (0.45, 0.9, 0.9),
            (0.3, 0.85, 0.85), (0.1, 0.45, 0.9), (0.0, 0.1, 0.9),

            (1.0, 1.0, 0.45), (1.0, 1.0, 0.1), (0.95, 0.55, 0.25),
            (0.95, 0.42, 0.2), (0.5, 0.25, 0.05), (0.45, 1.0, 0.45),
            (0.9, 0.35, 0.65), (0.85, 0.35, 0.9), (1.0, 1.0, 1.0),
        ]

        start_x = self.picker_x + 25
        start_y = self.picker_y + 345
        size = 17
        gap = 10

        for i, color in enumerate(colors):
            col = i % 9
            row = i // 9

            cx = start_x + col * (size + gap)
            cy = start_y + row * (size + gap)

            glColor3f(*color)
            self._draw_circle(cx + size / 2, cy + size / 2, size / 2, fill=True)

            glColor3f(0.45, 0.45, 0.45)
            self._draw_circle(cx + size / 2, cy + size / 2, size / 2, fill=False)

    def _draw_custom_color_dots(self):
        self._draw_text("Custom colors", self.picker_x + 375, self.picker_y + 320, self.small_font)

        start_x = self.picker_x + 375
        start_y = self.picker_y + 345
        size = 17
        gap = 10

        for row in range(2):
            for col in range(6):
                cx = start_x + col * (size + gap)
                cy = start_y + row * (size + gap)

                glColor3f(1.0, 1.0, 1.0)
                self._draw_circle(cx + size / 2, cy + size / 2, size / 2, fill=True)

                glColor3f(0.65, 0.65, 0.65)
                self._draw_circle(cx + size / 2, cy + size / 2, size / 2, fill=False)

    def _draw_toolbar_background(self):
        glColor3f(0.96, 0.96, 0.96)
        self._draw_rect(0, 0, 1200, self.height)

        glColor3f(0.78, 0.78, 0.78)
        glBegin(GL_LINES)
        glVertex2f(0, self.height)
        glVertex2f(1200, self.height)
        glEnd()

        for x in [318, 580, 795]:
            glColor3f(0.82, 0.82, 0.82)
            glBegin(GL_LINES)
            glVertex2f(x, 8)
            glVertex2f(x, 84)
            glEnd()

    def _draw_button(self, button, active=False):
        if active:
            glColor3f(0.72, 0.86, 1.0)
        else:
            glColor3f(0.985, 0.985, 0.985)

        self._draw_rect(button["x"], button["y"], button["w"], button["h"])

        if active:
            glColor3f(0.1, 0.45, 0.8)
        else:
            glColor3f(0.72, 0.72, 0.72)

        self._draw_border(button["x"], button["y"], button["w"], button["h"])
        self._draw_text(button["label"], button["x"] + 8, button["y"] + 9, self.font)

    def _draw_color_preview(self, x, y, color, label):
        if color is None:
            color = (0.0, 0.0, 0.0)

        glColor3f(*color)
        self._draw_circle(x + 12, y + 12, 12, fill=True)

        glColor3f(0.2, 0.2, 0.2)
        self._draw_circle(x + 12, y + 12, 12, fill=False)

        self._draw_text(label, x + 30, y + 4, self.small_font)

    def _draw_dialog_button(self, x, y, w, h, text, active=False):
        if active:
            glColor3f(0.0, 0.45, 0.5)
        else:
            glColor3f(1.0, 1.0, 1.0)

        self._draw_rect(x, y, w, h)

        glColor3f(0.75, 0.75, 0.75)
        self._draw_border(x, y, w, h)

        color = (255, 255, 255) if active else (30, 30, 30)
        self._draw_text_custom_color(text, x + w / 2 - 20, y + 7, self.font, color)

    def _draw_input_box(self, x, y, w, h, text, active=False):
        glColor3f(1.0, 1.0, 1.0)
        self._draw_rect(x, y, w, h)

        if active:
            glColor3f(0.0, 0.45, 0.5)
        else:
            glColor3f(0.82, 0.82, 0.82)

        self._draw_border(x, y, w, h)
        self._draw_text(text, x + 8, y + 6, self.font)

    def _draw_shadow(self, x, y, w, h):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(0.0, 0.0, 0.0, 0.18)
        self._draw_rect(x + 7, y + 7, w, h)

        glDisable(GL_BLEND)

    def _draw_group_title(self, text, x, y):
        self._draw_text(text, x, y, self.small_font)

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

    def _draw_circle(self, cx, cy, radius, fill=True):
        if fill:
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(cx, cy)
        else:
            glBegin(GL_LINE_LOOP)

        for i in range(40):
            angle = 2 * 3.14159 * i / 40
            vec = pygame.math.Vector2(1, 0).rotate_rad(angle)
            glVertex2f(cx + radius * vec.x, cy + radius * vec.y)

        glEnd()

    def _draw_text(self, text, x, y, font):
        self._draw_text_custom_color(text, x, y, font, (30, 30, 30))

    def _draw_text_custom_color(self, text, x, y, font, color):
        surface = font.render(text, True, color, None)
        text_data = pygame.image.tostring(surface, "RGBA", True)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glRasterPos2f(x, y + surface.get_height())
        glDrawPixels(
            surface.get_width(),
            surface.get_height(),
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            text_data
        )

        glDisable(GL_BLEND)

    def _inside(self, button, x, y):
        return (
            button["x"] <= x <= button["x"] + button["w"]
            and button["y"] <= y <= button["y"] + button["h"]
        )

    def _point_in_rect(self, px, py, x, y, w, h):
        return x <= px <= x + w and y <= py <= y + h

    def _rgb_to_hex(self, rgb):
        r = int(rgb[0] * 255)
        g = int(rgb[1] * 255)
        b = int(rgb[2] * 255)

        return f"#{r:02X}{g:02X}{b:02X}"