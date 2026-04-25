"""
Scene: tüm shape'lerin listesini ve seçimi yönetir.
Kişi 1 bunu yazar/tamamlar.
Kişi 2 ve 3 sadece kullanır.
"""

import copy


class Scene:
    def __init__(self):
        self._shapes = []
        self.selected = None
        self._undo_stack = []
        self._redo_stack = []

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