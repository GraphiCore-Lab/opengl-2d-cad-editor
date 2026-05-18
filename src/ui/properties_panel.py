from OpenGL.GL import *
import pygame
import os
from src.utils.constants import WIDTH, HEIGHT
from src.utils.fonts import load_ui_fonts


class PropertiesPanel:
    def __init__(self):
        self.width = 220
        self.x = WIDTH - self.width
        self.y = 92
        self.height = HEIGHT - 122

        self.buttons = [
            {"name": "fill_toggle", "label": "Fill On/Off", "x": self.x + 20, "y": self.y + 65, "w": 170, "h": 30},
            {"name": "line_width", "label": "Line Width", "x": self.x + 20, "y": self.y + 105, "w": 170, "h": 30},

            {"name": "bring_front", "label": "Bring Front", "x": self.x + 20, "y": self.y + 340, "w": 170, "h": 30},
            {"name": "send_back", "label": "Send Back", "x": self.x + 20, "y": self.y + 380, "w": 170, "h": 30},
            {"name": "duplicate", "label": "Duplicate", "x": self.x + 20, "y": self.y + 420, "w": 170, "h": 30},
            {"name": "delete", "label": "Delete", "x": self.x + 20, "y": self.y + 460, "w": 170, "h": 30},

            {"name": "save_artwork", "label": "Save this Artwork!", "x": self.x + 20, "y": self.y + self.height - 52, "w": 170, "h": 34},
        ]

        pygame.font.init()
        self.font, self.title_font, _ = load_ui_fonts(
            body_size=13,
            title_size=18,
            small_size=11,
        )

        self.icon_size = 24
        self.icons = self._load_panel_icons()

        self.alpha_slider_x = self.x + 20
        self.alpha_slider_y = self.y + 165  
        self.alpha_slider_w = 170
        self.alpha_slider_h = 6
        self.is_dragging_alpha = False      # Tracks whether the user is actively dragging the opacity slider

    def draw(self, selected_shape):
        glColor3f(0.96, 0.96, 0.96)
        self._draw_rect(self.x, self.y, self.width, self.height)

        glColor3f(0.78, 0.78, 0.78)
        self._draw_border(self.x, self.y, self.width, self.height)

        self._draw_text("Properties", self.x + 20, self.y + 20, self.title_font)

        # Dim all edit buttons when nothing is selected to signal they are inactive
        if selected_shape is None:
            self._draw_text("No object selected", self.x + 20, self.y + 45, self.font)
        else:
            self._draw_text("Object selected", self.x + 20, self.y + 45, self.font)

        for button in self.buttons:
            if button["name"] == "save_artwork":
                glColor3f(0.78, 0.92, 0.82)
            elif selected_shape is None:
                glColor3f(0.88, 0.88, 0.88)
            else:
                glColor3f(0.985, 0.985, 0.985)

            self._draw_rounded_rect(button["x"], button["y"], button["w"], button["h"], 4)

            if button["name"] == "save_artwork":
                glColor3f(0.22, 0.5, 0.32)
            else:
                glColor3f(0.72, 0.72, 0.72)
            self._draw_rounded_border(button["x"], button["y"], button["w"], button["h"], 4)

            icon = self.icons.get(button["name"])
            text_x = button["x"] + 10

            if icon is not None:
                # Position the icon flush to the right edge of the button with 8px padding
                icon_x = button["x"] + button["w"] - 8 - icon.get_width()
                icon_y = button["y"] + (button["h"] - icon.get_height()) / 2
                self._draw_surface(icon, icon_x, icon_y)

            label_y = button["y"] + (9 if button["name"] == "save_artwork" else 7)
            self._draw_text(button["label"], text_x, label_y, self.font)

        self._draw_text("Opacity", self.alpha_slider_x, self.alpha_slider_y - 20, self.font)
        
        glColor3f(0.8, 0.8, 0.8)
        self._draw_rounded_rect(self.alpha_slider_x, self.alpha_slider_y, self.alpha_slider_w, self.alpha_slider_h, 3) 
        
        # Read alpha from the selected shape; default to fully opaque if none selected
        current_alpha = 1.0
        if selected_shape and hasattr(selected_shape, "alpha"):
            current_alpha = selected_shape.alpha
        
        glColor3f(0.4, 0.6, 0.8) # Blue-ish fill
        active_w = self.alpha_slider_w * current_alpha
        if active_w > 0:
            self._draw_rounded_rect(self.alpha_slider_x, self.alpha_slider_y, active_w, self.alpha_slider_h, 3)
        
        thumb_w = 12
        thumb_h = 16
        thumb_rect_x = self.alpha_slider_x + active_w - (thumb_w / 2)
        # Center the thumb vertically over the thin track
        thumb_rect_y = self.alpha_slider_y - (thumb_h - self.alpha_slider_h) / 2
        
        glColor3f(1.0, 1.0, 1.0)
        self._draw_rounded_rect(thumb_rect_x, thumb_rect_y, thumb_w, thumb_h, 3)
        glColor3f(0.5, 0.5, 0.5)
        self._draw_rounded_border(thumb_rect_x, thumb_rect_y, thumb_w, thumb_h, 3)

        # Horizontal separator visually isolates the destructive Save button from edit tools
        sep_y = self.y + self.height - 66
        glColor3f(0.75, 0.75, 0.75)
        glBegin(GL_LINES)
        glVertex2f(self.x + 16, sep_y)
        glVertex2f(self.x + self.width - 16, sep_y)
        glEnd()

    def handle_click(self, x, y):
        for button in self.buttons:
            if button["x"] <= x <= button["x"] + button["w"] and button["y"] <= y <= button["y"] + button["h"]:
                return button["name"]

        # Expand the slider's hit area by 10px on all sides for easier mouse targeting
        pad = 10
        if (self.alpha_slider_x - pad <= x <= self.alpha_slider_x + self.alpha_slider_w + pad and 
            self.alpha_slider_y - pad <= y <= self.alpha_slider_y + self.alpha_slider_h + pad):
            
            self.is_dragging_alpha = True
            return self._calc_alpha_action(x)
        
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

    def _rounded_rect_points(self, x, y, w, h, radius, segments=6):
        # Clamp radius so it never exceeds half the shortest side (prevents geometric artifacts)
        r = max(0.0, min(float(radius), w / 2.0, h / 2.0))

        if r == 0:
            return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

        points = []
        # corner_data: (arc center x, arc center y, start angle, end angle) for each corner
        corner_data = [
            (x + w - r, y + r, -1.5707963, 0.0),        # Top-right corner (start pointing up, end pointing right)
            (x + w - r, y + h - r, 0.0, 1.5707963),     # Bottom-right corner (start pointing right, end pointing down)
            (x + r, y + h - r, 1.5707963, 3.1415926),   # Bottom-left corner (start pointing down, end pointing left)
            (x + r, y + r, 3.1415926, 4.7123890),       # Top-left corner (start pointing left, end pointing up)
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

    def _load_panel_icons(self):
        icon_dir = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
        )

        icon_files = {
            "bring_front": "icon_bringFront.png",
            "send_back": "icon_sendBack.png",
            "duplicate": "icon_duplicate.png",
            "delete": "icon_cancel.png",
        }

        loaded_icons = {}

        for action_name, file_name in icon_files.items():
            path = os.path.join(icon_dir, file_name)

            if not os.path.exists(path):
                continue

            try:
                image = pygame.image.load(path).convert_alpha()
                width, height = image.get_size()

                if width <= 0 or height <= 0:
                    continue

                scale_factor = self.icon_size / max(width, height)
                target_w = max(1, int(round(width * scale_factor)))
                target_h = max(1, int(round(height * scale_factor)))

                loaded_icons[action_name] = pygame.transform.scale(image, (target_w, target_h))
            except pygame.error:
                continue

        return loaded_icons

    def _draw_text(self, text, x, y, font):
        surface = font.render(text, True, (30, 30, 30), None)
        self._draw_surface(surface, x, y)

    def _calc_alpha_action(self, x):
        # Clamp x to slider bounds then normalize to [0.0, 1.0]
        clamped_x = max(self.alpha_slider_x, min(x, self.alpha_slider_x + self.alpha_slider_w))
        alpha_val = (clamped_x - self.alpha_slider_x) / self.alpha_slider_w
        return f"selected_alpha:{alpha_val:.2f}"        # Returns an action string parsed by InputHandler

    def handle_mouse_motion(self, x, y):
        if getattr(self, "is_dragging_alpha", False):
            return self._calc_alpha_action(x)
        return None

    def handle_mouse_up(self):
        self.is_dragging_alpha = False

    def _draw_surface(self, surface, x, y):
        # Convert Pygame surface to raw RGBA bytes for OpenGL to consume via glDrawPixels
        text_data = pygame.image.tostring(surface, "RGBA", True)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # Standard transparency blending

        # glRasterPos sets the screen anchor; +height flips the Y because OpenGL origin is bottom-left
        glRasterPos2f(x, y + surface.get_height())
        glDrawPixels(
            surface.get_width(),
            surface.get_height(),
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            text_data
        )

        glDisable(GL_BLEND)