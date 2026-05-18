from OpenGL.GL import *
import pygame
from src.utils.constants import WIDTH, HEIGHT
from src.utils.fonts import load_ui_fonts


class StatusBar:
    def __init__(self):
        self.mouse_x = 0
        self.mouse_y = 0
        self.height = 30

        pygame.font.init()
        self.font, self.hint_font, _ = load_ui_fonts(body_size=12, title_size=16, small_size=11)

        self.hint_text = ""
        self.hint_started_at = 0
        self.hint_duration_ms = 2400    # Total time a hint stays visible
        self.hint_fade_ms = 550     # Duration of the fade-out at the end

    def update_mouse_position(self, x, y):
        self.mouse_x = x
        self.mouse_y = y

    def show_hint(self, text, duration_ms=None):
        # Calling this again mid-display immediately replaces the old hint
        self.hint_text = text or ""
        self.hint_started_at = pygame.time.get_ticks()

        if duration_ms is not None:
            self.hint_duration_ms = int(duration_ms)

    def draw(self):
        y = HEIGHT - self.height

        glColor3f(0.86, 0.86, 0.86)
        glBegin(GL_QUADS)
        glVertex2f(0, y)
        glVertex2f(WIDTH, y)
        glVertex2f(WIDTH, HEIGHT)
        glVertex2f(0, HEIGHT)
        glEnd()

        glColor3f(0.25, 0.25, 0.25)
        glBegin(GL_LINE_LOOP)
        glVertex2f(0, y)
        glVertex2f(WIDTH, y)
        glVertex2f(WIDTH, HEIGHT)
        glVertex2f(0, HEIGHT)
        glEnd()

        self._draw_hint(y)

    def _draw_hint(self, y):
        if not self.hint_text:
            return

        elapsed = pygame.time.get_ticks() - self.hint_started_at

        # hint_duration_ms reached: clear and stop drawing
        if elapsed >= self.hint_duration_ms:
            self.hint_text = ""
            return

        fade_start = self.hint_duration_ms - self.hint_fade_ms

        if elapsed < fade_start:
            alpha = 255     # Still in the fully visible window
        else:
            # Linearly interpolate alpha from 255 → 0 over the fade window
            fade_progress = (elapsed - fade_start) / max(1, self.hint_fade_ms)
            alpha = max(0, int(255 * (1.0 - fade_progress)))

        # Alert-style popup above the status bar.
        text_surface = self.hint_font.render(self.hint_text, True, (255, 255, 255), None)
        text_surface.set_alpha(alpha)

        pad_x = 12
        pad_y = 4
        box_w = text_surface.get_width() + pad_x * 2
        box_h = text_surface.get_height() + pad_y * 2

        box_w = min(box_w, WIDTH - 20)      # Prevent the popup from overflowing the window edge
        box_x = max(10, (WIDTH - box_w) / 2)    # Center horizontally with a 10px minimum margin
        box_y = y + max(1, (self.height - box_h) / 2)

        bg_alpha = int(alpha * 0.9)     # Background slightly more transparent than the text for contrast
        self._draw_rgba_rect(box_x, box_y, box_w, box_h, (0, 0, 0, bg_alpha))
        self._draw_rgba_border(box_x, box_y, box_w, box_h, (255, 255, 255, alpha), 2.0)

        self._draw_surface(text_surface, box_x + pad_x, box_y + pad_y)

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
            text_data,
        )

        glDisable(GL_BLEND)

    def _draw_rgba_rect(self, x, y, w, h, rgba):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # Normalize 0–255 RGBA tuple to 0.0–1.0 range that OpenGL expects
        glColor4f(rgba[0] / 255.0, rgba[1] / 255.0, rgba[2] / 255.0, rgba[3] / 255.0)

        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

        glDisable(GL_BLEND)

    def _draw_rgba_border(self, x, y, w, h, rgba, line_width=1.0):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(rgba[0] / 255.0, rgba[1] / 255.0, rgba[2] / 255.0, rgba[3] / 255.0)
        glLineWidth(line_width)   

        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

        glLineWidth(1.0)    # Reset line width to default after drawing to avoid affecting other elements
        glDisable(GL_BLEND)