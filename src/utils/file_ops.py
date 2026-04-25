"""
Dosya kaydet / yükle — JSON formatı.
Kişi 3'ün dosyası.
"""
import json
import os

from src.utils.constants import DEFAULT_SAVE_PATH
from src.shapes.line import Line
from src.shapes.rectangle import Rectangle
from src.shapes.circle import Circle


def _shape_factory(data):
    """type string'e göre doğru shape sınıfını döndür."""
    shape_type = data.get("type")

    if shape_type == "Line":
        return Line.from_dict(data)

    if shape_type == "Rectangle":
        return Rectangle.from_dict(data)

    if shape_type == "Circle":
        return Circle.from_dict(data)

    print(f"[load WARNING] Unknown shape type: {shape_type}")
    return None


def save_scene(scene, path=DEFAULT_SAVE_PATH):
    try:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(path, "w", encoding="utf-8") as file:
            json.dump(scene.to_dict(), file, indent=2)

        print(f"[save] {path}")

    except Exception as error:
        print(f"[save ERROR] {error}")


def load_scene(scene, path=DEFAULT_SAVE_PATH):
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        scene.load_from_dict(data, _shape_factory)
        print(f"[load] {path}")

    except FileNotFoundError:
        print(f"[load] Dosya bulunamadı: {path}")

    except json.JSONDecodeError as error:
        print(f"[load ERROR] JSON okunamadı: {error}")

    except Exception as error:
        print(f"[load ERROR] {error}")