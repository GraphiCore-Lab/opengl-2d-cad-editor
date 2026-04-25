"""
InputHandler: mouse ve klavye olaylarını işler.
"""
import pygame
from src.utils.constants import (
    TOOL_SELECT, TOOL_LINE, TOOL_RECT, TOOL_CIRCLE,
    TOOL_MOVE, TOOL_ROTATE, TOOL_SCALE,
    CANVAS_X, CANVAS_W, CANVAS_H,
    GRID_SIZE, SNAP_ENABLED,
)
from src.shapes.line import Line
from src.shapes.rectangle import Rectangle
from src.shapes.circle import Circle


def snap(val, grid=GRID_SIZE):
    return round(val / grid) * grid


class InputHandler:
    def __init__(self, scene):
        self.scene = scene
        self.current_tool = TOOL_RECT
        self.current_color = (1.0, 1.0, 1.0)
        self.current_fill = True
        self.current_line_width = 2.0

        self._drawing = False
        self._start_x = 0
        self._start_y = 0
        self._preview = None

        self._moving = False
        self._move_last = (0, 0)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._on_mouse_down(event)
        elif event.type == pygame.MOUSEMOTION:
            self._on_mouse_move(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._on_mouse_up(event)
        elif event.type == pygame.KEYDOWN:
            self._on_key(event)

    def get_preview(self):
        return self._preview

    def _on_mouse_down(self, event):
        if event.button != 1:
            return

        mx, my = self._canvas_pos(event.pos)
        if not self._in_canvas(mx, my):
            return

        if SNAP_ENABLED:
            mx, my = snap(mx), snap(my)

        world_x = mx + CANVAS_X
        world_y = my

        if self.current_tool == TOOL_SELECT:
            selected = self.scene.select_at(world_x, world_y)
            if selected:
                self._moving = True
                self._move_last = (world_x, world_y)

        elif self.current_tool == TOOL_MOVE:
            selected = self.scene.select_at(world_x, world_y)
            if selected:
                self._moving = True
                self._move_last = (world_x, world_y)

        elif self.current_tool in (TOOL_LINE, TOOL_RECT, TOOL_CIRCLE):
            self.scene.deselect()
            self._drawing = True
            self._start_x = world_x
            self._start_y = world_y

    def _on_mouse_move(self, event):
        mx, my = self._canvas_pos(event.pos)

        if not self._in_canvas(mx, my):
            return

        if SNAP_ENABLED:
            mx, my = snap(mx), snap(my)

        world_x = mx + CANVAS_X
        world_y = my

        if self._moving and self.scene.selected:
            last_x, last_y = self._move_last
            dx = world_x - last_x
            dy = world_y - last_y

            self.scene.move_selected(dx, dy)
            self._move_last = (world_x, world_y)

        elif self._drawing:
            self._update_preview(world_x, world_y)

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
        c = self.current_color
        f = self.current_fill
        lw = self.current_line_width

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

        s.color = c
        s.fill = f
        s.line_width = lw
        self._preview = s