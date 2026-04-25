"""
InputHandler: mouse ve klavye olaylarını işler.
"""

import pygame

from src.utils.constants import (
    TOOL_SELECT, TOOL_LINE, TOOL_RECT, TOOL_CIRCLE, TOOL_TRIANGLE,
    TOOL_MOVE, TOOL_ROTATE, TOOL_SCALE,
    CANVAS_X, CANVAS_W, CANVAS_H,
    GRID_SIZE, SNAP_ENABLED
)

from src.shapes.line import Line
from src.shapes.rectangle import Rectangle
from src.shapes.circle import Circle
from src.shapes.triangle import Triangle


def snap(val, grid=GRID_SIZE):
    return round(val / grid) * grid


class InputHandler:
    def __init__(self, scene, toolbar=None, properties_panel=None, status_bar=None):
        self.scene = scene
        self.toolbar = toolbar
        self.properties_panel = properties_panel
        self.status_bar = status_bar

        self.current_tool = TOOL_RECT
        self.current_color = (1.0, 0.0, 0.0)
        self.current_fill = True
        self.current_line_width = 2.0

        self._drawing = False
        self._start_x = 0
        self._start_y = 0
        self._preview = None

        self._moving = False
        self._move_last = (0, 0)

        self._rotating = False
        self._scaling = False
        self._transform_last = (0, 0)

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

    def _reset_action_states(self):
        self._moving = False
        self._rotating = False
        self._scaling = False

    def _on_mouse_down(self, event):
        if event.button != 1:
            return

        x, y = event.pos

        if self.toolbar:
            clicked_tool = self.toolbar.handle_click(x, y)
            if clicked_tool:
                self.current_tool = clicked_tool
                self._reset_action_states()
                return

        if self.properties_panel:
            panel_action = self.properties_panel.handle_click(x, y)
            if panel_action:
                self._handle_panel_action(panel_action)
                return

        mx, my = self._canvas_pos(event.pos)

        if not self._in_canvas(mx, my):
            self._reset_action_states()
            return

        if SNAP_ENABLED:
            mx, my = snap(mx), snap(my)

        real_x = mx + CANVAS_X
        real_y = my

        if self.current_tool in (TOOL_SELECT, TOOL_MOVE):
            selected = self.scene.select_at(real_x, real_y)

            if selected:
                self._moving = True
                self._move_last = (real_x, real_y)
            else:
                self._reset_action_states()

        elif self.current_tool == TOOL_ROTATE:
            selected = self.scene.select_at(real_x, real_y)

            if selected:
                self._rotating = True
                self._transform_last = (real_x, real_y)
            else:
                self._reset_action_states()

        elif self.current_tool == TOOL_SCALE:
            selected = self.scene.select_at(real_x, real_y)

            if selected:
                self._scaling = True
                self._transform_last = (real_x, real_y)
            else:
                self._reset_action_states()

        elif self.current_tool in (TOOL_LINE, TOOL_RECT, TOOL_CIRCLE, TOOL_TRIANGLE):
            self.scene.deselect()
            self._reset_action_states()
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
            dx = real_x - self._move_last[0]
            dy = real_y - self._move_last[1]

            if hasattr(self.scene, "move_selected"):
                self.scene.move_selected(dx, dy)
            else:
                self.scene.selected.move(dx, dy)

            self._move_last = (real_x, real_y)

        elif self._rotating and self.scene.selected:
            dx = real_x - self._transform_last[0]
            angle = dx * 0.5

            if hasattr(self.scene, "rotate_selected"):
                self.scene.rotate_selected(angle)
            else:
                self.scene.selected.rotate(angle)

            self._transform_last = (real_x, real_y)

        elif self._scaling and self.scene.selected:
            dy = real_y - self._transform_last[1]
            factor = 1.0 + (-dy * 0.01)
            factor = max(0.1, factor)

            if hasattr(self.scene, "scale_selected"):
                self.scene.scale_selected(factor, factor)
            else:
                self.scene.selected.scale(factor, factor)

            self._transform_last = (real_x, real_y)

        elif self._drawing:
            self._update_preview(real_x, real_y)

    def _on_mouse_up(self, event):
        if event.button != 1:
            return

        if self._moving or self._rotating or self._scaling:
            self._reset_action_states()
            return

        if self._drawing:
            self._drawing = False

            if self._preview:
                self.scene.add_shape(self._preview)
                self.scene.select_at(*self._preview.get_center())
                self._preview = None

    def _handle_panel_action(self, action):
        selected = self.scene.selected

        if selected is None:
            return

        if action == "fill_toggle":
            selected.fill = not selected.fill

        elif action == "line_width":
            selected.line_width += 1
            if selected.line_width > 6:
                selected.line_width = 1

        elif action.startswith("outline_hex:"):
            hex_code = action.split(":")[1]
            selected.outline_color = self._hex_to_rgb(hex_code)

        elif action.startswith("fill_hex:"):
            hex_code = action.split(":")[1]
            selected.fill_color = self._hex_to_rgb(hex_code)

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

    def _on_key(self, event):
        mods = pygame.key.get_mods()
        ctrl = mods & pygame.KMOD_CTRL

        if event.key == pygame.K_DELETE:
            self.scene.delete_selected()

        elif event.key == pygame.K_r:
            if self.scene.selected:
                if hasattr(self.scene, "rotate_selected"):
                    self.scene.rotate_selected(10)
                else:
                    self.scene.selected.rotate(10)

        elif event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
            if self.scene.selected:
                if hasattr(self.scene, "scale_selected"):
                    self.scene.scale_selected(1.1, 1.1)
                else:
                    self.scene.selected.scale(1.1, 1.1)

        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            if self.scene.selected:
                if hasattr(self.scene, "scale_selected"):
                    self.scene.scale_selected(0.9, 0.9)
                else:
                    self.scene.selected.scale(0.9, 0.9)

        elif event.key == pygame.K_ESCAPE:
            self.scene.deselect()
            self._reset_action_states()

        elif ctrl and event.key == pygame.K_z:
            self.scene.undo()

        elif ctrl and event.key == pygame.K_y:
            self.scene.redo()

        elif ctrl and event.key == pygame.K_d:
            if self.scene.selected:
                if hasattr(self.scene, "duplicate"):
                    self.scene.duplicate(self.scene.selected)
                elif hasattr(self.scene, "duplicate_shape"):
                    self.scene.duplicate_shape(self.scene.selected)

        elif ctrl and event.key == pygame.K_s:
            from src.utils.file_ops import save_scene
            save_scene(self.scene)

        elif ctrl and event.key == pygame.K_o:
            from src.utils.file_ops import load_scene
            load_scene(self.scene)

    def _hex_to_rgb(self, hex_code):
        hex_code = hex_code.replace("#", "")

        r = int(hex_code[0:2], 16) / 255
        g = int(hex_code[2:4], 16) / 255
        b = int(hex_code[4:6], 16) / 255

        return (r, g, b)

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

        elif self.current_tool == TOOL_TRIANGLE:
            x1 = sx
            y1 = my
            x2 = mx
            y2 = my
            x3 = (sx + mx) / 2
            y3 = sy
            s = Triangle(x1, y1, x2, y2, x3, y3)

        else:
            return

        s.outline_color = self.current_color
        s.fill_color = self.current_color
        s.fill = self.current_fill
        s.line_width = self.current_line_width

        self._preview = s