"""
Scene: tüm shape'lerin listesini ve seçimi yönetir.
Kişi 1 bunu yazar/tamamlar.
Kişi 2 ve 3 sadece kullanır.
"""

import copy
import math
from src.shapes.line import Line
from src.shapes.polyline import Polyline


class Scene:
    def __init__(self):
        self._shapes = []
        self.selected = None
        self._undo_stack = []
        self._redo_stack = []
        self.global_rotation = 0.0

    def add_shape(self, shape):
        self._save_undo("add", shape)
        self._shapes.append(shape)

    def remove_shape(self, shape):
        if shape in self._shapes:
            self._save_undo("remove", (shape, self._shapes.index(shape)))
            self._shapes.remove(shape)

            if self.selected is shape:
                shape.selected = False
                self.selected = None

    def get_shapes(self):
        return list(self._shapes)

    def get_shape_at(self, x, y):
        for shape in reversed(self._shapes):
            if shape.contains(x, y):
                return shape
        return None

    def select_at(self, x, y):
        self.deselect()

        self.selected = self.get_shape_at(x, y)

        if self.selected:
            self.selected.selected = True

        return self.selected

    def deselect(self):
        if self.selected:
            self.selected.selected = False
        self.selected = None

    def bring_to_front(self, shape):
        if shape in self._shapes:
            self._shapes.remove(shape)
            self._shapes.append(shape)

    def send_to_back(self, shape):
        if shape in self._shapes:
            self._shapes.remove(shape)
            self._shapes.insert(0, shape)

    def duplicate(self, shape):
        if shape not in self._shapes:
            return None

        new_shape = copy.deepcopy(shape)
        new_shape.selected = False

        if hasattr(new_shape, "move"):
            new_shape.move(20, 20)

        self.add_shape(new_shape)

        self.deselect()
        self.selected = new_shape
        self.selected.selected = True

        return new_shape

    def delete_selected(self):
        if self.selected:
            self.remove_shape(self.selected)

    def move_selected(self, dx, dy):
        if self.selected and hasattr(self.selected, "move"):
            self.selected.move(dx, dy)

    def rotate_selected(self, angle_deg):
        if self.selected and hasattr(self.selected, "rotate"):
            self.selected.rotate(angle_deg)

    def scale_selected(self, sx, sy):
        if self.selected and hasattr(self.selected, "scale"):
            self.selected.scale(sx, sy)

    def _save_undo(self, action, data):
        self._undo_stack.append((action, data))
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            return

        action, data = self._undo_stack.pop()

        if action == "add":
            if data in self._shapes:
                self._shapes.remove(data)
                if self.selected is data:
                    self.deselect()
            self._redo_stack.append((action, data))

        elif action == "remove":
            shape, index = data
            self._shapes.insert(index, shape)
            self._redo_stack.append((action, data))

    def redo(self):
        if not self._redo_stack:
            return

        action, data = self._redo_stack.pop()

        if action == "add":
            self._shapes.append(data)
            self._undo_stack.append((action, data))

        elif action == "remove":
            shape, _ = data
            if shape in self._shapes:
                self._shapes.remove(shape)
                if self.selected is shape:
                    self.deselect()
            self._undo_stack.append((action, data))

    def to_dict(self):
        return {"shapes": [s.to_dict() for s in self._shapes]}

    def load_from_dict(self, data, shape_factory):
        self._shapes.clear()
        self.deselect()
        self._undo_stack.clear()
        self._redo_stack.clear()

        for sd in data.get("shapes", []):
            shape = shape_factory(sd)
            if shape:
                shape.selected = False
                self._shapes.append(shape)

    def explode_selected(self):
        """Shatters the selected shape into individual Line objects."""
        shape = self.selected
        if not shape or isinstance(shape, Line):
            return # Cannot explode nothing, or a single line
            
        # Get the actual screen coordinates of the shape's vertices
        if hasattr(shape, "get_transformed_points"):
            points = shape.get_transformed_points()
        else:
            return

        is_closed = True
        if isinstance(shape, Polyline) and not shape.closed:
            is_closed = False

        new_lines = []
        for i in range(len(points)):
            # Skip the closing line if it's an open polyline
            if not is_closed and i == len(points) - 1:
                break
                
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            
            # Create a new Line at the exact coordinates
            line = Line(p1[0], p1[1], p2[0], p2[1])
            line.outline_color = shape.outline_color
            line.line_width = shape.line_width
            line.line_style = getattr(shape, "line_style", "solid")
            line.alpha = getattr(shape, "alpha", 1.0)
            
            new_lines.append(line)

        # Delete the original shape and add the new lines
        self.delete_selected()
        for line in new_lines:
            self.add_shape(line)
            
        # Select the first line so the user knows it worked
        if new_lines:
            self.selected = new_lines[0]
            new_lines[0].selected = True

    def join_selected(self):
        """Smart Join: Connects lines, auto-trims sloppy corners safely."""
        start_shape = self.selected
        if not start_shape or not hasattr(start_shape, "get_transformed_points"):
            return

        start_points = start_shape.get_transformed_points()
        if len(start_points) < 2:
            return

        def get_intersection(p1, p2, p3, p4):
            x1, y1 = p1; x2, y2 = p2
            x3, y3 = p3; x4, y4 = p4
            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if den == 0: return None
            px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / den
            py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / den
            return (px, py)

        def get_joint(p_end, p_seg, s_end, s_seg, touch_tol=2.0, trim_tol=25.0):
            # 1. Exact touch
            if math.hypot(p_end[0] - s_end[0], p_end[1] - s_end[1]) <= touch_tol:
                return ((p_end[0] + s_end[0]) / 2.0, (p_end[1] + s_end[1]) / 2.0)

            ix = get_intersection(p_seg, p_end, s_seg, s_end)
            if ix:
                dist_p_end = math.hypot(ix[0] - p_end[0], ix[1] - p_end[1])
                dist_p_seg = math.hypot(ix[0] - p_seg[0], ix[1] - p_seg[1])
                dist_s_end = math.hypot(ix[0] - s_end[0], ix[1] - s_end[1])
                dist_s_seg = math.hypot(ix[0] - s_seg[0], ix[1] - s_seg[1])
                
                # 2. Sloppy corner check
                # THE FIX: The intersection MUST be closer to the ends we are joining 
                # than the far ends of the segments. This prevents shapes from collapsing!
                if dist_p_end <= dist_p_seg and dist_s_end <= dist_s_seg:
                    if dist_p_end <= trim_tol and dist_s_end <= trim_tol:
                        return ix

            return None
        
        touch_tolerance = 2.0
        trim_tolerance = 25.0

        vertices = [(float(p[0]), float(p[1])) for p in start_points]
        shapes_to_remove = [start_shape]

        searching = True
        while searching:
            searching = False

            pt_start = vertices[0]
            pt_start_seg = vertices[1] if len(vertices) > 1 else pt_start
            pt_end = vertices[-1]
            pt_end_seg = vertices[-2] if len(vertices) > 1 else pt_end

            for shape in self.get_shapes():
                if shape in shapes_to_remove: continue
                
                from src.shapes.line import Line
                from src.shapes.polyline import Polyline
                if not isinstance(shape, (Line, Polyline)): continue
                if isinstance(shape, Polyline) and getattr(shape, "closed", False): continue

                sp = [(float(p[0]), float(p[1])) for p in shape.get_transformed_points()]
                if len(sp) < 2: continue

                s_start = sp[0]
                s_start_seg = sp[1] if len(sp) > 1 else s_start
                s_end = sp[-1]
                s_end_seg = sp[-2] if len(sp) > 1 else s_end

                # Check End to Start
                joint = get_joint(pt_end, pt_end_seg, s_start, s_start_seg, touch_tolerance, trim_tolerance)
                if joint:
                    vertices[-1] = joint
                    vertices.extend(sp[1:])
                    shapes_to_remove.append(shape)
                    searching = True; break

                # Check End to End
                joint = get_joint(pt_end, pt_end_seg, s_end, s_end_seg, touch_tolerance, trim_tolerance)
                if joint:
                    vertices[-1] = joint
                    vertices.extend(list(reversed(sp[:-1])))
                    shapes_to_remove.append(shape)
                    searching = True; break

                # Check Start to End
                joint = get_joint(pt_start, pt_start_seg, s_end, s_end_seg, touch_tolerance, trim_tolerance)
                if joint:
                    vertices[0] = joint
                    vertices = sp[:-1] + vertices
                    shapes_to_remove.append(shape)
                    searching = True; break

                # Check Start to Start
                joint = get_joint(pt_start, pt_start_seg, s_start, s_start_seg, touch_tolerance, trim_tolerance)
                if joint:
                    vertices[0] = joint
                    vertices = list(reversed(sp[1:])) + vertices
                    shapes_to_remove.append(shape)
                    searching = True; break

        if len(shapes_to_remove) > 1:
            is_closed = False

            # Auto-Close check for rectangles/triangles
            if len(vertices) >= 3:
                joint = get_joint(vertices[0], vertices[1], vertices[-1], vertices[-2], touch_tolerance, trim_tolerance)
                if joint:
                    vertices[0] = joint
                    vertices.pop()
                    is_closed = True

            polyline = Polyline(vertices=vertices, closed=is_closed)
            polyline.outline_color = start_shape.outline_color
            polyline.line_width = getattr(start_shape, "line_width", 2.0)
            polyline.line_style = getattr(start_shape, "line_style", "solid")

            for s in shapes_to_remove:
                if s in self._shapes:
                    self._shapes.remove(s)
                    
            if self.selected in shapes_to_remove:
                self.selected = None

            self.add_shape(polyline)
            self.selected = polyline
            polyline.selected = True