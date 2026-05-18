from OpenGL.GL import *
import pygame
import colorsys
import os

from src.utils.fonts import load_ui_fonts


class Toolbar:
    def __init__(self):
        self.height = 92

        self.buttons = [
            {"name": "select", "label": "Select", "x": 12, "y": 12, "w": 72, "h": 32},
            {"name": "move", "label": "Move", "x": 88, "y": 12, "w": 72, "h": 32},
            {"name": "rotate", "label": "Rotate", "x": 164, "y": 12, "w": 72, "h": 32},
            {"name": "scale", "label": "Scale", "x": 240, "y": 12, "w": 72, "h": 32},

            {"name": "line", "label": "Line", "x": 326, "y": 12, "w": 58, "h": 32},
            {"name": "rect", "label": "Rect", "x": 388, "y": 12, "w": 58, "h": 32},
            {"name": "circle", "label": "Circle", "x": 450, "y": 12, "w": 58, "h": 32},
            {"name": "triangle", "label": "Tri", "x": 512, "y": 12, "w": 58, "h": 32},
            {"name": "shape_dropdown", "label": "Extras", "x": 574, "y": 12, "w": 58, "h": 32},
        ]

        self.shape_dropdown_open = False
        self.dropdown_hovered_item = None
        self.dropdown_items = [
            {"name": "ellipse", "label": "Ellipse"},
            {"name": "polygon", "label": "Polygon"},
            {"name": "star", "label": "Star"},
        ]

        self.stroke_min = 1
        self.stroke_mid = 6     # Midpoint maps to 50% of the slider — gives finer control in the 1–6 range
        self.stroke_max = 12
        self.dragging_stroke_slider = False
        self.stroke_slider_rect = {"x": 650, "y": 18, "w": 200, "h": 18}

        self.active_line_style = "solid"
        
        style_base_x = 680  
        style_base_y = 52  
        
        self.style_buttons = [
            {"id": "solid", "label": "Solid", "x": style_base_x, "y": style_base_y, "w": 55, "h": 20},
            {"id": "dashed", "label": "Dash", "x": style_base_x + 65, "y": style_base_y, "w": 55, "h": 20},
            {"id": "dotted", "label": "Dot", "x": style_base_x + 130, "y": style_base_y, "w": 55, "h": 20}
        ]

        self.color_target = "outline"

        self.color_buttons = [
            {"name": "target:outline", "label": "Outline", "x": 916, "y": 12, "w": 86, "h": 32},
            {"name": "target:fill", "label": "Fill", "x": 1010, "y": 12, "w": 86, "h": 32},
            {"name": "open_color_picker", "label": "Edit colors", "x": 1104, "y": 12, "w": 96, "h": 32},
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

        self.current_hue = 0.55     # H in HSV, range [0.0, 1.0]
        self.current_saturation = 0.65      # S in HSV, range [0.0, 1.0]
        self.current_value = 0.65       # V in HSV, range [0.0, 1.0]
        # Convert initial HSV to RGB for OpenGL
        self.selected_color = colorsys.hsv_to_rgb(
            self.current_hue,
            self.current_saturation,
            self.current_value
        )

        self.dragging_gradient = False
        self.dragging_value = False

        self.active_input = None
        self.input_text = ""
        self.hovered_button = None

        self.basic_colors = [
            (0.96, 0.45, 0.45), (1.0, 0.15, 0.1), (0.45, 0.25, 0.25),
            (0.55, 0.22, 0.18), (0.25, 0.02, 0.0), (0.45, 0.9, 0.9),
            (0.3, 0.85, 0.85), (0.1, 0.45, 0.9), (0.0, 0.1, 0.9),
            (1.0, 1.0, 0.45), (1.0, 1.0, 0.1), (0.95, 0.55, 0.25),
            (0.95, 0.42, 0.2), (0.5, 0.25, 0.05), (0.45, 1.0, 0.45),
            (0.9, 0.35, 0.65), (0.85, 0.35, 0.9), (1.0, 1.0, 1.0),
        ]
        self.custom_colors = [None] * 12
        self.selected_custom_slot = None

        pygame.font.init()
        self.font, self.title_font, self.small_font = load_ui_fonts(
            body_size=12,
            title_size=22,
            small_size=11,
        )
        self.picker_font, self.picker_title_font, self.picker_small_font = load_ui_fonts(
            body_size=14,
            title_size=26,
            small_size=13,
        )

        self.icon_size = 24
        self.icons = self._load_toolbar_icons()

    def draw(self, active_tool, current_outline=None, current_fill=None, line_width=2):
        self._draw_toolbar_background()

        self._draw_group_title("Tools", 12, 74)
        self._draw_group_title("Shapes", 330, 74)
        self._draw_group_title("Size & Style", 680, 74)
        self._draw_group_title("Colors", 930, 74)

        for button in self.buttons:
            active = button["name"] == active_tool
            hovered = button["name"] == self.hovered_button

            self._draw_button(button, active, hovered=hovered)

        self._draw_stroke_slider(line_width)

        for btn in self.style_buttons:
            is_active = self.active_line_style == btn["id"]

            if is_active:
                glColor3f(0.72, 0.86, 1.0) # Light blue 
            else:
                glColor3f(0.985, 0.985, 0.985) # White/gray
                
            self._draw_rounded_rect(btn["x"], btn["y"], btn["w"], btn["h"], 3)

            if is_active:
                glColor3f(0.1, 0.45, 0.8) 
            else:
                glColor3f(0.72, 0.72, 0.72)
                
            self._draw_rounded_border(btn["x"], btn["y"], btn["w"], btn["h"], 3)

            text_x = btn["x"] + 10
            text_y = btn["y"] + 6
            self._draw_text(btn["label"], text_x, text_y, self.small_font)

        for button in self.color_buttons:
            active = button["name"] == f"target:{self.color_target}"
            hovered = button["name"] == self.hovered_button
            indicator_color = None

            if button["name"] == "target:outline":
                indicator_color = current_outline
            elif button["name"] == "target:fill":
                indicator_color = current_fill

            self._draw_button(button, active, hovered=hovered, indicator_color=indicator_color)

    def draw_overlay(self):
        if self.shape_dropdown_open:
            self._draw_shape_dropdown()

        if self.color_picker_open:
            self._draw_color_picker()

    def _draw_shape_dropdown(self):
        dd_x = 574 
        dd_y = 46  
        item_h = 30
        dd_w = 90
        dd_h = len(self.dropdown_items) * item_h

        self._draw_shadow(dd_x, dd_y, dd_w, dd_h)

        glColor3f(0.98, 0.98, 0.98)
        self._draw_rect(dd_x, dd_y, dd_w, dd_h)
        glColor3f(0.75, 0.75, 0.75)
        self._draw_border(dd_x, dd_y, dd_w, dd_h)

        for i, item in enumerate(self.dropdown_items):
            item_y = dd_y + i * item_h
            
            if self.dropdown_hovered_item == item["name"]:
                glColor3f(0.85, 0.9, 0.95) # Light blue highlight
                self._draw_rect(dd_x + 1, item_y + 1, dd_w - 2, item_h - 2)

            self._draw_text(item["label"], dd_x + 10, item_y + 8, self.font)

    def handle_click(self, x, y):
        if self.color_picker_open:
            return self._handle_color_picker_click(x, y)
        
        if self.shape_dropdown_open:
            dd_x, dd_y, item_h, dd_w = 574, 46, 30, 90
            dd_h = len(self.dropdown_items) * item_h

            if self._point_in_rect(x, y, dd_x, dd_y, dd_w, dd_h):
                rel_y = y - dd_y
                index = int(rel_y // item_h)

                if 0 <= index < len(self.dropdown_items):
                    self.shape_dropdown_open = False
                    return self.dropdown_items[index]["name"] 
                
            self.shape_dropdown_open = False
            return None

        if self._inside(self.stroke_slider_rect, x, y):
            self.dragging_stroke_slider = True
            width = self._width_from_slider_x(x)
            return f"width:{width}"
        
        for btn in self.style_buttons:
            if self._inside(btn, x, y):
                self.active_line_style = btn["id"]
                return f"current_line_style:{btn['id']}"

        for button in self.buttons:
            if self._inside(button, x, y):
                if button["name"] == "shape_dropdown":
                    self.shape_dropdown_open = True
                    return None
                
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
            self._update_hovered_button(x, y)

        if self.dragging_stroke_slider and not self.color_picker_open:
            width = self._width_from_slider_x(x)
            return f"width:{width}"

        if not self.color_picker_open:
            return None

        self.hovered_button = None

        if self.dragging_gradient:
            self._select_from_gradient(x, y)
            return None

        if self.dragging_value:
            self._select_from_value_slider(y)
            return None

        if self.shape_dropdown_open:
            dd_x, dd_y, item_h, dd_w = 574, 46, 30, 90
            dd_h = len(self.dropdown_items) * item_h
            self.dropdown_hovered_item = None
            
            if self._point_in_rect(x, y, dd_x, dd_y, dd_w, dd_h):
                rel_y = y - dd_y
                index = int(rel_y // item_h)
                if 0 <= index < len(self.dropdown_items):
                    self.dropdown_hovered_item = self.dropdown_items[index]["name"]
            
            return None

        return None

    def handle_mouse_up(self):
        self.dragging_stroke_slider = False
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

        basic_index = self._get_clicked_basic_color_index(x, y)
        if basic_index is not None:
            self.selected_color = self.basic_colors[basic_index]
            self._sync_hsv_from_rgb()
            return self._color_action()

        custom_index = self._get_clicked_custom_color_index(x, y)
        if custom_index is not None:
            self.selected_custom_slot = custom_index

            saved = self.custom_colors[custom_index]
            if saved is not None:
                self.selected_color = saved
                self._sync_hsv_from_rgb()
                return self._color_action()

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
            if self.selected_custom_slot is not None:
                self.custom_colors[self.selected_custom_slot] = self.selected_color

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

        self._draw_text("Edit colors", self.picker_x + 25, self.picker_y + 34, self.picker_title_font)
        self._draw_text("×", self.picker_x + self.picker_w - 28, self.picker_y + 13, self.picker_font)

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

        # X-axis maps to hue, Y-axis maps to saturation (inverted: top = fully saturated)
        for ix in range(steps_x):
            hue = ix / (steps_x - 1)

            for iy in range(steps_y):
                saturation = 1.0 - (iy / (steps_y - 1))
                r, g, b = colorsys.hsv_to_rgb(hue, saturation, self.current_value)

                x = self.gradient_x + ix * cell_w
                y = self.gradient_y + iy * cell_h

                glColor3f(r, g, b)
                glVertex2f(x, y)
                # Slightly oversize each cell by +1px to eliminate seams between quads
                glVertex2f(x + cell_w + 1, y)
                glVertex2f(x + cell_w + 1, y + cell_h + 1)
                glVertex2f(x, y + cell_h + 1)

        glEnd()

        glColor3f(0.75, 0.75, 0.75)
        self._draw_border(self.gradient_x, self.gradient_y, self.gradient_w, self.gradient_h)

        marker_x = self.gradient_x + self.current_hue * self.gradient_w
        marker_y = self.gradient_y + (1.0 - self.current_saturation) * self.gradient_h

        # Crosshair marker: black outer ring + white inner ring for visibility on any color
        glColor3f(0.0, 0.0, 0.0)
        self._draw_circle(marker_x, marker_y, 7, fill=False)

        glColor3f(1.0, 1.0, 1.0)
        self._draw_circle(marker_x, marker_y, 5, fill=False)

    def _draw_value_slider(self):
        steps = 100
        cell_h = self.value_h / steps

        glBegin(GL_QUADS)

        # V channel only; H and S stay fixed so the strip shows dark→bright for the current color
        for i in range(steps):
            value = 1.0 - (i / (steps - 1))     # Top = 1.0 (bright), bottom = 0.0 (black)
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

            self._draw_text(labels[key], box["x"] + 105, box["y"] + 7, self.picker_font)

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
        self._draw_text("Basic colors", self.picker_x + 25, self.picker_y + 332, self.picker_small_font)

        for i, dot in enumerate(self._basic_color_dots()):
            color = self.basic_colors[i]
            cx, cy, radius = dot["cx"], dot["cy"], dot["radius"]

            glColor3f(*color)
            self._draw_circle(cx, cy, radius, fill=True)

            glColor3f(0.45, 0.45, 0.45)
            self._draw_circle(cx, cy, radius, fill=False)

    def _draw_custom_color_dots(self):
        self._draw_text("Custom colors", self.picker_x + 375, self.picker_y + 332, self.picker_small_font)

        for i, dot in enumerate(self._custom_color_dots()):
            cx, cy, radius = dot["cx"], dot["cy"], dot["radius"]
            saved = self.custom_colors[i]

            if saved is None:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(*saved)

            self._draw_circle(cx, cy, radius, fill=True)

            if i == self.selected_custom_slot:
                glColor3f(0.0, 0.45, 0.5)
                self._draw_circle(cx, cy, radius + 2, fill=False)

            glColor3f(0.65, 0.65, 0.65)
            self._draw_circle(cx, cy, radius, fill=False)

    def _basic_color_dots(self):
        start_x = self.picker_x + 25
        start_y = self.picker_y + 360
        size = 17
        gap = 10
        dots = []

        for i in range(18):
            col = i % 9
            row = i // 9
            cx = start_x + col * (size + gap) + size / 2
            cy = start_y + row * (size + gap) + size / 2
            dots.append({"cx": cx, "cy": cy, "radius": size / 2})

        return dots

    def _custom_color_dots(self):
        start_x = self.picker_x + 375
        start_y = self.picker_y + 360
        size = 17
        gap = 10
        dots = []

        for i in range(12):
            col = i % 6
            row = i // 6
            cx = start_x + col * (size + gap) + size / 2
            cy = start_y + row * (size + gap) + size / 2
            dots.append({"cx": cx, "cy": cy, "radius": size / 2})

        return dots

    def _get_clicked_basic_color_index(self, x, y):
        for i, dot in enumerate(self._basic_color_dots()):
            dx = x - dot["cx"]
            dy = y - dot["cy"]
            if dx * dx + dy * dy <= (dot["radius"] + 2) ** 2:
                return i

        return None

    def _get_clicked_custom_color_index(self, x, y):
        for i, dot in enumerate(self._custom_color_dots()):
            dx = x - dot["cx"]
            dy = y - dot["cy"]
            if dx * dx + dy * dy <= (dot["radius"] + 2) ** 2:
                return i

        return None

    def _draw_toolbar_background(self):
        glColor3f(0.96, 0.96, 0.96)
        self._draw_rect(0, 0, 1200, self.height)

        glColor3f(0.78, 0.78, 0.78)
        glBegin(GL_LINES)
        glVertex2f(0, self.height)
        glVertex2f(1200, self.height)
        glEnd()

        for x in [318, 636, 900]:
            glColor3f(0.82, 0.82, 0.82)
            glBegin(GL_LINES)
            glVertex2f(x, 8)
            glVertex2f(x, 84)
            glEnd()

    def _draw_button(self, button, active=False, hovered=False, indicator_color=None):
        if active:
            glColor3f(0.72, 0.86, 1.0)
        elif hovered:
            glColor3f(0.93, 0.93, 0.93)
        else:
            glColor3f(0.985, 0.985, 0.985)

        self._draw_rounded_rect(button["x"], button["y"], button["w"], button["h"], 4)

        if active:
            glColor3f(0.1, 0.45, 0.8)
        elif hovered:
            glColor3f(0.58, 0.58, 0.58)
        else:
            glColor3f(0.72, 0.72, 0.72)

        self._draw_rounded_border(button["x"], button["y"], button["w"], button["h"], 4)

        icon = self.icons.get(button["name"])
        icon_padding_right = 6
        text_x = button["x"] + 8
        text_limit_x = button["x"] + button["w"] - 8

        if icon is not None:
            icon_x = button["x"] + button["w"] - icon_padding_right - icon.get_width()
            icon_y = button["y"] + (button["h"] - icon.get_height()) / 2
            self._draw_surface(icon, icon_x, icon_y)
            text_limit_x = min(text_limit_x, icon_x - 4)

        if indicator_color is not None:
            cx = button["x"] + button["w"] - 13
            cy = button["y"] + button["h"] / 2

            glColor3f(*indicator_color)
            self._draw_circle(cx, cy, 8, fill=True)

            glColor3f(0.2, 0.2, 0.2)
            self._draw_circle(cx, cy, 8, fill=False)
            text_limit_x = min(text_limit_x, cx - 12)

        max_text_width = max(8, text_limit_x - text_x)
        label_text, label_font = self._fit_label(button["label"], max_text_width)
        self._draw_text(label_text, text_x, button["y"] + 9, label_font)

    def _draw_stroke_slider(self, line_width):
        sx = self.stroke_slider_rect["x"]
        sy = self.stroke_slider_rect["y"]
        sw = self.stroke_slider_rect["w"]
        sh = self.stroke_slider_rect["h"]

        track_y = sy + sh / 2
        ratio = self._slider_ratio_from_width(line_width)
        handle_x = sx + ratio * sw
        max_thickness = float(self.stroke_max)
        base_y = track_y + max_thickness / 2

        # Right-angled tapered track: flat bottom, sloped top.
        glColor3f(0.78, 0.78, 0.78)
        glBegin(GL_TRIANGLES)
        glVertex2f(sx, base_y)
        glVertex2f(sx + sw, base_y)
        glVertex2f(sx + sw, base_y - max_thickness)
        glEnd()

        glColor3f(0.52, 0.52, 0.52)
        glBegin(GL_LINE_LOOP)
        glVertex2f(sx, base_y)
        glVertex2f(sx + sw, base_y)
        glVertex2f(sx + sw, base_y - max_thickness)
        glEnd()

        # Middle marker: center visually maps to 6 px.
        mid_x = sx + sw / 2
        glColor3f(0.48, 0.48, 0.48)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(mid_x, base_y - max_thickness - 2)
        glVertex2f(mid_x, base_y + 2)
        glEnd()

        local_thickness = max(self.stroke_min, min(self.stroke_max, float(line_width)))
        handle_size = max(12.0, local_thickness + 6.0)
        handle_center_y = base_y - (local_thickness / 2.0)

        glColor3f(0.985, 0.985, 0.985)
        self._draw_rect(
            handle_x - handle_size / 2,
            handle_center_y - handle_size / 2,
            handle_size,
            handle_size,
        )
        glColor3f(0.35, 0.35, 0.35)
        self._draw_border(
            handle_x - handle_size / 2,
            handle_center_y - handle_size / 2,
            handle_size,
            handle_size,
        )

        self._draw_text(f"{int(round(line_width))}px", sx + sw + 8, sy - 1, self.font)
        self._draw_text("1", sx - 3, sy + 22, self.small_font)
        self._draw_text("6", mid_x - 3, sy + 22, self.small_font)
        self._draw_text("12", sx + sw - 7, sy + 22, self.small_font)

        glLineWidth(1.0)

    def _slider_ratio_from_width(self, width):
        width = max(self.stroke_min, min(self.stroke_max, float(width)))

        if width <= self.stroke_mid:
            return ((width - self.stroke_min) / (self.stroke_mid - self.stroke_min)) * 0.5

        return 0.5 + ((width - self.stroke_mid) / (self.stroke_max - self.stroke_mid)) * 0.5

    def _width_from_slider_x(self, x):
        sx = self.stroke_slider_rect["x"]
        sw = self.stroke_slider_rect["w"]
        # Inverse of _slider_ratio_from_width: screen X position → pixel width
        ratio = (x - sx) / sw
        ratio = max(0.0, min(1.0, ratio))   # Clamp to [0, 1] so dragging outside bounds is safe

        if ratio <= 0.5:
            width = self.stroke_min + (ratio / 0.5) * (self.stroke_mid - self.stroke_min)
        else:
            width = self.stroke_mid + ((ratio - 0.5) / 0.5) * (self.stroke_max - self.stroke_mid)

        return int(round(width))

    def _load_toolbar_icons(self):
        icon_dir = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
        )

        icon_files = {
            "select": "icon_select.png",
            "move": "icon_move.png",
            "rotate": "icon_rotate.png",
            "scale": "icon_scale.png",
            "line": "icon_line.png",
            "rect": "icon_rect.png",
            "circle": "icon_circle.png",
            "triangle": "icon_triangle.png",
            "open_color_picker": "icon_edit_colors.png",
        }

        loaded_icons = {}

        for button_name, file_name in icon_files.items():
            icon_path = os.path.join(icon_dir, file_name)

            if not os.path.exists(icon_path):
                continue

            try:
                image = pygame.image.load(icon_path).convert_alpha()
                width, height = image.get_size()

                if width <= 0 or height <= 0:
                    continue

                scale_factor = self.icon_size / max(width, height)
                target_w = max(1, int(round(width * scale_factor)))
                target_h = max(1, int(round(height * scale_factor)))

                loaded_icons[button_name] = pygame.transform.scale(image, (target_w, target_h))
            except pygame.error:
                continue

        return loaded_icons

    def _fit_label(self, label, max_width):
        if self.font.size(label)[0] <= max_width:
            return label, self.font

        if self.small_font.size(label)[0] <= max_width:
            return label, self.small_font

        # Progressively truncate the label until it fits, then append "." as an ellipsis indicator
        candidate = label
        while len(candidate) > 1 and self.small_font.size(candidate + ".")[0] > max_width:
            candidate = candidate[:-1]

        if not candidate:
            return "", self.small_font

        return candidate + ".", self.small_font

    def _update_hovered_button(self, x, y):
        self.hovered_button = None

        for button in self.buttons:
            if self._inside(button, x, y):
                self.hovered_button = button["name"]
                return

        for button in self.color_buttons:
            if self._inside(button, x, y):
                self.hovered_button = button["name"]
                return

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

        self._draw_rounded_rect(x, y, w, h, 4)

        glColor3f(0.75, 0.75, 0.75)
        self._draw_rounded_border(x, y, w, h, 4)

        color = (255, 255, 255) if active else (30, 30, 30)
        self._draw_text_custom_color(text, x + w / 2 - 20, y + 7, self.picker_font, color)

    def _draw_input_box(self, x, y, w, h, text, active=False):
        glColor3f(1.0, 1.0, 1.0)
        self._draw_rounded_rect(x, y, w, h, 4)

        if active:
            glColor3f(0.0, 0.45, 0.5)
        else:
            glColor3f(0.82, 0.82, 0.82)

        self._draw_rounded_border(x, y, w, h, 4)
        self._draw_text(text, x + 8, y + 6, self.picker_font)

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

    def _rounded_rect_points(self, x, y, w, h, radius, segments=6):
        r = max(0.0, min(float(radius), w / 2.0, h / 2.0))

        if r == 0:
            return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

        points = []
        corner_data = [
            (x + w - r, y + r, -1.5707963, 0.0),
            (x + w - r, y + h - r, 0.0, 1.5707963),
            (x + r, y + h - r, 1.5707963, 3.1415926),
            (x + r, y + r, 3.1415926, 4.7123890),
        ]

        for cx, cy, start_a, end_a in corner_data:
            for i in range(segments + 1):
                t = i / segments
                a = start_a + (end_a - start_a) * t
                points.append((cx + r * pygame.math.Vector2(1, 0).rotate_rad(a).x,
                               cy + r * pygame.math.Vector2(1, 0).rotate_rad(a).y))

        return points

    def _draw_rounded_rect(self, x, y, w, h, radius):
        points = self._rounded_rect_points(x, y, w, h, radius)
        glBegin(GL_POLYGON)
        for px, py in points:
            glVertex2f(px, py)
        glEnd()

    def _draw_rounded_border(self, x, y, w, h, radius):
        points = self._rounded_rect_points(x, y, w, h, radius)
        glBegin(GL_LINE_LOOP)
        for px, py in points:
            glVertex2f(px, py)
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

        self._draw_surface(surface, x, y)

    def _draw_surface(self, surface, x, y):
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