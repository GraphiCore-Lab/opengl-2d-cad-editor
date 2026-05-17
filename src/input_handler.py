"""
InputHandler: mouse ve klavye olaylarını işler.
"""

import pygame

from shapes.polygon import Polygon
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
from src.shapes.polygon import Polygon
from src.shapes.star import Star
from src.shapes.ellipse import Ellipse


def snap(val, grid=GRID_SIZE):
    return round(val / grid) * grid


class InputHandler:
    def __init__(self, scene, toolbar=None, properties_panel=None, status_bar=None):
        self.scene = scene
        self.toolbar = toolbar
        self.properties_panel = properties_panel
        self.status_bar = status_bar

        self.current_tool = TOOL_RECT

        self.current_outline_color = (0.0, 0.0, 0.0)
        self.current_fill_color = (0.8, 0.8, 0.8)
        self.current_fill = True
        self.current_line_width = 2.0
        self.current_alpha = 1.0

        self._drawing = False
        self._start_x = 0
        self._start_y = 0
        self._preview = None

        self._moving = False
        self._move_last = (0, 0)

        self._rotating = False
        self._scaling = False
        self._transform_last = (0, 0)

        self._last_click_time = 0
        self._last_click_pos = None

        self.polygon_sides = 6
        self.polygon_input_string = "6"

        self.star_points = 5
        self.star_input_string = "5"

        self.action_hints = {
            "select": "Click on the object you want to select",
            "move": "Click and drag to move the selected object",
            "rotate": "Click and drag horizontally to rotate the selected object",
            "scale": "Click and drag vertically to scale the selected object",
            "line": "Create a line",
            "rect": "Create a rectangle",
            "circle": "Create a circle",
            "triangle": "Create a triangle",

            "fill_toggle": "Click to enable or disable fill for the selected object",
            "line_width": "Adjust line width of the selected object",
            "bring_front": "Bring the selected object to the front",
            "send_back": "Send the selected object to the back",
            "duplicate": "Duplicate the selected object",
            "delete": "Delete the selected object",
            "save_artwork": "Open Save As to export JSON or PNG",
        }

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._on_mouse_down(event)

        elif event.type == pygame.MOUSEMOTION:
            if self.toolbar:
                toolbar_action = self.toolbar.handle_mouse_motion(event.pos[0], event.pos[1])
                if toolbar_action:
                    self._handle_toolbar_action(toolbar_action)

            if self.properties_panel:
                panel_action = self.properties_panel.handle_mouse_motion(event.pos[0], event.pos[1])
                if panel_action:
                    self._handle_panel_action(panel_action)

            self._on_mouse_move(event)

            if self.status_bar:
                self.status_bar.update_mouse_position(event.pos[0], event.pos[1])

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.toolbar:
                self.toolbar.handle_mouse_up()

            if self.properties_panel:
                self.properties_panel.handle_mouse_up()

            self._on_mouse_up(event)

        elif event.type == pygame.KEYDOWN:
            if self.toolbar:
                toolbar_action = self.toolbar.handle_key_down(event)
                if toolbar_action:
                    self._handle_toolbar_action(toolbar_action)
                    return

            self._on_key(event)

    def get_preview(self):
        return self._preview

    def is_rotation_active(self):
        return self._rotating and self.scene.selected is not None

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

            # Edit colors popup açıksa tıklama arkadaki canvas/panele geçmesin
            if getattr(self.toolbar, "color_picker_open", False):
                if clicked_tool:
                    self._handle_toolbar_action(clicked_tool)
                return

            if clicked_tool:
                self._handle_toolbar_action(clicked_tool)
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

        if self._is_double_click(event, real_x, real_y):
            self.scene.select_at(real_x, real_y)
            self._reset_action_states()
            return

        # Selection overlay interactions always take precedence when a shape is selected,
        # even if the current tool is a drawing tool.
        if self.scene.selected:
            selected = self.scene.selected

            if hasattr(selected, "is_on_rotate_handle") and selected.is_on_rotate_handle(real_x, real_y):
                self._reset_action_states()
                self._rotating = True
                self._transform_last = (real_x, real_y)
                return

            if hasattr(selected, "is_on_selection_border") and selected.is_on_selection_border(real_x, real_y):
                self._reset_action_states()
                self._scaling = True
                self._transform_last = (real_x, real_y)
                return

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

        elif self.current_tool in (TOOL_LINE, TOOL_RECT, TOOL_CIRCLE, TOOL_TRIANGLE, "polygon", "star", "ellipse"):
            self.scene.deselect()
            self._reset_action_states()
            self._drawing = True
            self._start_x = real_x
            self._start_y = real_y

    def _is_double_click(self, event, x, y):
        clicks = getattr(event, "clicks", 0)

        if clicks >= 2:
            return True

        now = pygame.time.get_ticks()

        if self._last_click_pos is None:
            self._last_click_time = now
            self._last_click_pos = (x, y)
            return False

        last_x, last_y = self._last_click_pos
        dt = now - self._last_click_time
        dist_sq = (x - last_x) ** 2 + (y - last_y) ** 2

        self._last_click_time = now
        self._last_click_pos = (x, y)

        return dt <= 320 and dist_sq <= 14 * 14

    def _on_mouse_move(self, event):
        # Edit colors popup açıkken arkadaki shape çizim/taşıma/scale/rotate çalışmasın
        if self.toolbar and getattr(self.toolbar, "color_picker_open", False):
            return

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

            self.scene.move_selected(dx, dy)
            self._move_last = (real_x, real_y)

        elif self._rotating and self.scene.selected:
            dx = real_x - self._transform_last[0]
            angle = dx * 0.5

            self.scene.rotate_selected(angle)
            self._transform_last = (real_x, real_y)

        elif self._scaling and self.scene.selected:
            dy = real_y - self._transform_last[1]
            factor = 1.0 + (-dy * 0.01)
            factor = max(0.1, factor)

            self.scene.scale_selected(factor, factor)
            self._transform_last = (real_x, real_y)

        elif self._drawing:
            self._update_preview(real_x, real_y)
    
    def _on_mouse_up(self, event):
        if event.button != 1:
            return

        if self.toolbar and getattr(self.toolbar, "color_picker_open", False):
            self._reset_action_states()
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


    def _handle_toolbar_action(self, action):
        selected = self.scene.selected

        if action.startswith("outline_color:"):
            color = self._parse_rgb_action(action)
            self.current_outline_color = color

            if selected:
                selected.outline_color = color

            return

        if action.startswith("fill_color:"):
            color = self._parse_rgb_action(action)
            self.current_fill_color = color

            if selected:
                selected.fill_color = color

            return

        if action.startswith("width:"):
            width = float(action.split(":")[1])
            self.current_line_width = width

            if selected:
                selected.line_width = width

            return
        
        if action.startswith("current_line_style:"):
            style = action.split(":")[1]
            self.current_line_style = style
            
            # This is the line that actually updates the shape you clicked!
            if selected:
                selected.line_style = style
            return

        self.current_tool = action
        self._reset_action_states()
        self._show_action_hint(action)

    def _parse_rgb_action(self, action):
        values = action.split(":")[1]
        r, g, b = values.split(",")

        return float(r), float(g), float(b)

    def _handle_panel_action(self, action):
        if action == "save_artwork":
            from src.utils.file_ops import save_artwork_dialog
            result = save_artwork_dialog(self.scene)
            self._show_save_result_hint(result)
            return

        selected = self.scene.selected

        if selected is None:
            return

        if action == "fill_toggle":
            selected.fill = not selected.fill
            self.current_fill = selected.fill

        elif action == "line_width":
            selected.line_width += 1

            if selected.line_width > 12:
                selected.line_width = 1

            self.current_line_width = selected.line_width

        elif action.startswith("outline_hex:"):
            hex_code = action.split(":")[1]
            color = self._hex_to_rgb(hex_code)

            selected.outline_color = color
            self.current_outline_color = color

        elif action.startswith("fill_hex:"):
            hex_code = action.split(":")[1]
            color = self._hex_to_rgb(hex_code)

            selected.fill_color = color
            self.current_fill_color = color

        elif action.startswith("selected_alpha:"):
            alpha_val = float(action.split(":")[1])
            self.current_alpha = alpha_val
            if selected:
                selected.alpha = alpha_val
            return


        elif action == "bring_front":
            self.scene.bring_to_front(selected)

        elif action == "send_back":
            self.scene.send_to_back(selected)

        elif action == "duplicate":
            self.scene.duplicate(selected)

        elif action == "delete":
            self.scene.delete_selected()

        self._show_action_hint(action)

    def _show_action_hint(self, action):
        if not self.status_bar:
            return

        hint = self.action_hints.get(action)

        if hint:
            self.status_bar.show_hint(hint)

    def _show_save_result_hint(self, result):
        if not self.status_bar:
            return

        if not result:
            self.status_bar.show_hint("Save cancelled")
            return

        status = result.get("status")
        path = result.get("path")
        message = result.get("message") or "Save finished"

        if status == "saved" and path:
            import os
            self.status_bar.show_hint(f"Saved: {os.path.basename(path)}")
        elif status == "cancelled":
            self.status_bar.show_hint("Save cancelled")
        else:
            self.status_bar.show_hint(f"Save failed: {message}")

    def _on_key(self, event):
        mods = pygame.key.get_mods()
        ctrl = mods & pygame.KMOD_CTRL

        if self.current_tool == "polygon":
            if event.key == pygame.K_BACKSPACE:
                self.polygon_input_string = self.polygon_input_string[:-1]
            elif event.unicode.isdigit():
                self.polygon_input_string += event.unicode

            if len(self.polygon_input_string) > 2:
                self.polygon_input_string = self.polygon_input_string[-2:]

            try:
                val = int(self.polygon_input_string)
                self.polygon_sides = max(3, min(30, val))
            except ValueError:
                self.polygon_sides = 3

        if self.current_tool == "star":
            if event.key == pygame.K_BACKSPACE:
                self.star_input_string = self.star_input_string[:-1]
            elif event.unicode.isdigit():
                self.star_input_string += event.unicode

            if len(self.star_input_string) > 2:
                self.star_input_string = self.star_input_string[-2:]

            try:
                val = int(self.star_input_string)
                self.star_points = max(3, min(40, val)) # Limit to 40 pointed stars max
            except ValueError:
                self.star_points = 3

        # --- GLOBAL ROTATION CONTROLS (Q, E, 0) ---
        if event.key == pygame.K_q:
            if not hasattr(self.scene, "global_rotation"):
                self.scene.global_rotation = 0.0
            self.scene.global_rotation -= 5.0

        elif event.key == pygame.K_e:
            if not hasattr(self.scene, "global_rotation"):
                self.scene.global_rotation = 0.0
            self.scene.global_rotation += 5.0

        elif event.key == pygame.K_0:
            self.scene.global_rotation = 0.0

        elif event.key == pygame.K_DELETE:
            self.scene.delete_selected()

        elif event.key == pygame.K_r:
            if self.scene.selected:
                self.scene.rotate_selected(10)

        elif event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
            if self.scene.selected:
                self.scene.scale_selected(1.1, 1.1)

        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            if self.scene.selected:
                self.scene.scale_selected(0.9, 0.9)

        elif event.key == pygame.K_ESCAPE:
            self.scene.deselect()
            self._reset_action_states()

        elif ctrl and event.key == pygame.K_z:
            self.scene.undo()

        elif ctrl and event.key == pygame.K_y:
            self.scene.redo()

        elif ctrl and event.key == pygame.K_d:
            if self.scene.selected:
                self.scene.duplicate(self.scene.selected)

        elif ctrl and event.key == pygame.K_s:
            from src.utils.file_ops import save_artwork_dialog
            result = save_artwork_dialog(self.scene)
            self._show_save_result_hint(result)

        elif ctrl and event.key == pygame.K_o:
            from src.utils.file_ops import load_scene
            load_scene(self.scene)

        # --- EXPLODE AND JOIN CONTROLS ---
        elif event.key == pygame.K_x:
            self.scene.explode_selected()
            
        elif event.key == pygame.K_j:
            self.scene.join_selected()
            
        # (Your existing Q, E, 0 rotation checks stay here...)

    def _hex_to_rgb(self, hex_code):
        hex_code = hex_code.replace("#", "")

        r = int(hex_code[0:2], 16) / 255
        g = int(hex_code[2:4], 16) / 255
        b = int(hex_code[4:6], 16) / 255

        return r, g, b

    def _canvas_pos(self, pos):
        import math
        sx, sy = pos
        
        # 1. Find the exact center of your canvas
        cx = CANVAS_X + CANVAS_W / 2
        cy = CANVAS_H / 2

        # 2. Get the inverse of the global rotation in radians
        rotation = getattr(self.scene, "global_rotation", 0.0)
        angle_rad = math.radians(-rotation) 
        
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # 3. Apply 2D Rotation matrix around the center point
        rx = cos_a * (sx - cx) - sin_a * (sy - cy) + cx
        ry = sin_a * (sx - cx) + cos_a * (sy - cy) + cy

        return rx - CANVAS_X, ry

    def _in_canvas(self, cx, cy):
        return 0 <= cx <= CANVAS_W and 0 <= cy <= CANVAS_H

    def _update_preview(self, mx, my):
        sx, sy = self._start_x, self._start_y

        if self.current_tool == TOOL_LINE:
            shape = Line(sx, sy, mx, my)

        elif self.current_tool == TOOL_RECT:
            x = min(sx, mx)
            y = min(sy, my)
            width = abs(mx - sx)
            height = abs(my - sy)

            shape = Rectangle(x, y, width, height)

        elif self.current_tool == TOOL_CIRCLE:
            import math

            radius = math.hypot(mx - sx, my - sy)
            shape = Circle(sx, sy, radius)

        elif self.current_tool == TOOL_TRIANGLE:
            x1 = sx
            y1 = my

            x2 = mx
            y2 = my

            x3 = (sx + mx) / 2
            y3 = sy

            shape = Triangle(x1, y1, x2, y2, x3, y3)

        elif self.current_tool == "polygon":
            import math
            radius = math.hypot(mx - sx, my - sy)
            shape = Polygon(sx, sy, radius, self.polygon_sides)

        elif self.current_tool == "star":
            import math
            radius = math.hypot(mx - sx, my - sy)
            shape = Star(sx, sy, radius, self.star_points)

        elif self.current_tool == "ellipse":
            # Calculates the bounding box exactly like a rectangle
            x = min(sx, mx)
            y = min(sy, my)
            width = abs(mx - sx)
            height = abs(my - sy)

            shape = Ellipse(x, y, width, height)

        else:
            return

        shape.outline_color = self.current_outline_color
        shape.fill_color = self.current_fill_color
        shape.fill = self.current_fill
        shape.line_width = self.current_line_width
        shape.alpha = self.current_alpha

        shape.line_style = getattr(self, "current_line_style", "solid")

        self._preview = shape