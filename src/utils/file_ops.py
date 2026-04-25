"""
Dosya kaydet / yükle — JSON formatı.
Kişi 3'ün dosyası.
"""
import json
from src.utils.constants import DEFAULT_SAVE_PATH
from src.shapes.line import Line
from src.shapes.rectangle import Rectangle
from src.shapes.circle import Circle


def _shape_factory(data):
    """type string'e göre doğru shape sınıfını döndür."""
    t = data.get("type")
    if t == "Line":
        return Line.from_dict(data)
    elif t == "Rectangle":
        return Rectangle.from_dict(data)
    elif t == "Circle":
        return Circle.from_dict(data)
    return None


def save_scene(scene, path=DEFAULT_SAVE_PATH):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scene.to_dict(), f, indent=2)
        print(f"[save] {path}")
    except Exception as e:
        print(f"[save ERROR] {e}")


def load_scene(scene, path=DEFAULT_SAVE_PATH):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        scene.load_from_dict(data, _shape_factory)
        print(f"[load] {path}")
    except FileNotFoundError:
        print(f"[load] Dosya bulunamadı: {path}")
    except Exception as e:
        print(f"[load ERROR] {e}")