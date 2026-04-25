"""
Scene: tüm shape'lerin listesini ve seçimi yönetir.
Kişi 1 bunu yazar/tamamlar.
Kişi 2 ve 3 sadece kullanır.
"""
from src.utils.constants import HIT_THRESHOLD


class Scene:
    def __init__(self):
        self._shapes = []           # z-order: 0 = en altta
        self.selected = None        # seçili shape referansı
        self._undo_stack = []       # [(action, data), ...]
        self._redo_stack = []

    # ── Shape yönetimi ───────────────────────────────────────

    def add_shape(self, shape):
        self._save_undo("add", shape)
        self._shapes.append(shape)

    def remove_shape(self, shape):
        if shape in self._shapes:
            self._save_undo("remove", (shape, self._shapes.index(shape)))
            self._shapes.remove(shape)
            if self.selected is shape:
                self.selected = None

    def get_shapes(self):
        """Render sırası: alttaki önce."""
        return list(self._shapes)

    # ── Hit-test ─────────────────────────────────────────────

    def get_shape_at(self, x, y):
        """En üstteki (en son eklenen) shape'i döndür."""
        for shape in reversed(self._shapes):
            if shape.contains(x, y):
                return shape
        return None

    def select_at(self, x, y):
        """Verilen koordinatta shape seç, yoksa seçimi kaldır."""
        if self.selected:
            self.selected.selected = False
        self.selected = self.get_shape_at(x, y)
        if self.selected:
            self.selected.selected = True
        return self.selected

    def deselect(self):
        if self.selected:
            self.selected.selected = False
        self.selected = None

    # ── Z-order ──────────────────────────────────────────────

    def bring_to_front(self, shape):
        if shape in self._shapes:
            self._shapes.remove(shape)
            self._shapes.append(shape)

    def send_to_back(self, shape):
        if shape in self._shapes:
            self._shapes.remove(shape)
            self._shapes.insert(0, shape)

    def duplicate(self, shape):
        """Shape'i kopyala, biraz kaydırarak ekle."""
        import copy
        new_shape = copy.deepcopy(shape)
        new_shape.selected = False
        # Offset uygula (shape türüne göre)
        if hasattr(new_shape, 'x'):
            new_shape.x += 20
            new_shape.y += 20
        self.add_shape(new_shape)
        return new_shape

    def delete_selected(self):
        if self.selected:
            self.remove_shape(self.selected)

    # ── Undo / Redo ──────────────────────────────────────────

    def _save_undo(self, action, data):
        self._undo_stack.append((action, data))
        self._redo_stack.clear()  # yeni işlem redo'yu siler

    def undo(self):
        if not self._undo_stack:
            return
        action, data = self._undo_stack.pop()
        if action == "add":
            if data in self._shapes:
                self._shapes.remove(data)
                if self.selected is data:
                    self.selected = None
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
            self._undo_stack.append((action, data))

    # ── Serialization ────────────────────────────────────────

    def to_dict(self):
        return {"shapes": [s.to_dict() for s in self._shapes]}

    def load_from_dict(self, data, shape_factory):
        """shape_factory: type string → shape instance döndüren fonksiyon"""
        self._shapes.clear()
        self.selected = None
        for sd in data.get("shapes", []):
            shape = shape_factory(sd)
            if shape:
                self._shapes.append(shape)