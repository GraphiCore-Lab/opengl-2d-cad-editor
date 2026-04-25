"""
InputHandler: mouse ve klavye olaylarını işler.
Kişi 3'ün dosyası: Toolbar, properties panel ve status bar bağlantıları eklendi.
"""

import pygame

from src.utils.constants import (
    TOOL_SELECT, TOOL_LINE, TOOL_RECT, TOOL_CIRCLE,
    TOOL_MOVE, TOOL_ROTATE, TOOL_SCALE,
    CANVAS_X, CANVAS_W, CANVAS_H,
    GRID_SIZE, SNAP_ENABLED
)

from src.shapes.line import Line
from src.shapes.rectangle import Rectangle
from src.shapes.circle import Circle


def snap(val, grid=GRID_SIZE):
    return round(val / grid) * grid


class InputHandler:
    def __init__(self, scene, toolbar=None, properties_panel=None, status_bar=None):
        self.scene = scene

        self.toolbar = toolbar
        self.properties_panel = properties_panel
        self.status_bar = status_bar

        self.current_tool = TOOL_SELECT
        self.current_color = (1.0, 1.0, 1.0)
        self.current_fill = True
        self.current_line_width = 2.0

        # Çizim state
        self._drawing = False
        self._start_x = 0
        self._start_y = 0
        self._preview = None

        # Move state
        self._moving = False
        self._move_last = (0, 0)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._on_mouse_down(event)

        elif event.type == pygame.MOUSEMOTION:
            self._on_mouse_move(event)

            if self.status_bar:
                self.status_bar.update_mouse_position(event.pos[0], event.pos[1])

        elif event.type == pygame.MOUSEBUTTONUP:
            self._on_mouse_up(event)

        elif event.type == pygame.KEYDOWN:
            self._on_key(event)

    def get_preview(self):
        return self._preview

    def _on_mouse_down(self, event):
        if event.button != 1:
            return

        x, y = event.pos

        # 1. Önce toolbar kontrol edilir
        if self.toolbar:
            clicked_tool = self.toolbar.handle_click(x, y)
            if clicked_tool:
                self.current_tool = clicked_tool
                return

        # 2. Sonra properties panel kontrol edilir
        if self.properties_panel:
            panel_action = self.properties_panel.handle_click(x, y)
            if panel_action:
                self._handle_panel_action(panel_action)
                return

        # 3. Sonra canvas işlemleri yapılır
        mx, my = self._canvas_pos(event.pos)

        if not self._in_canvas(mx, my):
            return

        if SNAP_ENABLED:
            mx, my = snap(mx), snap(my)

        real_x = mx + CANVAS_X
        real_y = my

        if self.current_tool == TOOL_SELECT:
            selected = self.scene.select_at(real_x, real_y)
            if selected:
                self._moving = True
                self._move_last = (real_x, real_y)
            self.scene.select_at(real_x, real_y)

        elif self.current_tool == TOOL_MOVE:
            selected = self.scene.select_at(real_x, real_y)
            if selected:
                self._moving = True
                self._move_last = (real_x, real_y)
            sel = self.scene.selected
            if sel and sel.contains(real_x, real_y):
                self._moving = True
                self._move_last = (mx, my)

        elif self.current_tool in (TOOL_LINE, TOOL_RECT, TOOL_CIRCLE):
            self.scene.deselect()
            self._drawing = True
            self._start_x = real_x
            self._start_y = real_y

    def _on_mouse_move(self, event):
        mx, my = self._canvas_pos(event.pos)


        if not self._in_canvas(mx, my):
            return

        if SNAP_ENABLED:
            mx, my = snap(mx), snap(my)

        real_x = mx + CANVAS_X
        real_y = my

        if self._moving and self.scene.selected:
            dx = mx - self._move_last[0]
            dy = my - self._move_last[1]

            sel = self.scene.selected

            if hasattr(sel, "x1"):  # Line
                sel.x1 += dx
                sel.y1 += dy
                sel.x2 += dx
                sel.y2 += dy

            elif hasattr(sel, "cx"):  # Circle
                sel.cx += dx
                sel.cy += dy

            elif hasattr(sel, "x"):  # Rectangle
                sel.x += dx
                sel.y += dy

            self._move_last = (mx, my)

        elif self._drawing:
            self._update_preview(real_x, real_y)

    def _on_mouse_up(self, event):
        if event.button != 1:
            return

        if self._moving:
            self._moving = False
            return

        if self._drawing:
            self._drawing = False

            if self._preview:
                self.scene.add_shape(self._preview)
                self.scene.select_at(*self._preview.get_center())
                self._preview = None

    # ── Properties Panel Actions ─────────────────────────────

    def _handle_panel_action(self, action):
        selected = self.scene.selected

        if selected is None:
            return

        if action == "fill_toggle":
            if hasattr(selected, "fill"):
                selected.fill = not selected.fill

        elif action == "line_width":
            if hasattr(selected, "line_width"):
                selected.line_width += 1
                if selected.line_width > 6:
                    selected.line_width = 1

        elif action == "bring_front":
            if hasattr(self.scene, "bring_to_front"):
                self.scene.bring_to_front(selected)

        elif action == "send_back":
            if hasattr(self.scene, "send_to_back"):
                self.scene.send_to_back(selected)

        elif action == "duplicate":
            if hasattr(self.scene, "duplicate"):
                self.scene.duplicate(selected)
            elif hasattr(self.scene, "duplicate_shape"):
                self.scene.duplicate_shape(selected)

        elif action == "delete":
            if hasattr(self.scene, "delete_selected"):
                self.scene.delete_selected()

    # ── Klavye ───────────────────────────────────────────────

    def _on_key(self, event):
        mods = pygame.key.get_mods()
        ctrl = mods & pygame.KMOD_CTRL

        if event.key == pygame.K_DELETE:
            self.scene.delete_selected()

        elif event.key == pygame.K_r:
            self.scene.rotate_selected(10)

        elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
            self.scene.scale_selected(1.1, 1.1)

        elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
            self.scene.scale_selected(0.9, 0.9)

        elif event.key == pygame.K_ESCAPE:
            self.scene.deselect()

        elif ctrl and event.key == pygame.K_z:
            self.scene.undo()

        elif ctrl and event.key == pygame.K_y:
            self.scene.redo()

        elif ctrl and event.key == pygame.K_d:
            if self.scene.selected:
                self.scene.duplicate(self.scene.selected)

        elif ctrl and event.key == pygame.K_s:
            from src.utils.file_ops import save_scene
            save_scene(self.scene)

        elif ctrl and event.key == pygame.K_o:
            from src.utils.file_ops import load_scene
            load_scene(self.scene)

    def _canvas_pos(self, pos):
        return pos[0] - CANVAS_X, pos[1]

    def _in_canvas(self, cx, cy):
        return 0 <= cx <= CANVAS_W and 0 <= cy <= CANVAS_H

    def _update_preview(self, mx, my):
        sx, sy = self._start_x, self._start_y

        if self.current_tool == TOOL_LINE:
            s = Line(sx, sy, mx, my)

        elif self.current_tool == TOOL_RECT:
            x = min(sx, mx)
            y = min(sy, my)
            w = abs(mx - sx)
            h = abs(my - sy)
            s = Rectangle(x, y, w, h)

        elif self.current_tool == TOOL_CIRCLE:
            import math
            r = math.hypot(mx - sx, my - sy)
            s = Circle(sx, sy, r)

        else:
            return

        s.color = self.current_color
        s.fill = self.current_fill
        s.line_width = self.current_line_width

        self._preview = s