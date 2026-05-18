"""
Dosya kaydet / yükle — JSON formatı.
Kişi 3'ün dosyası.
"""
import json
import os
import tkinter as tk
from tkinter import filedialog

import pygame
from OpenGL.GL import glReadPixels, GL_RGBA, GL_UNSIGNED_BYTE

from src.utils.constants import (
    DEFAULT_SAVE_PATH,
    WIDTH,
    HEIGHT,
    CANVAS_X,
    CANVAS_W,
    TOOLBAR_HEIGHT,
    STATUS_BAR_HEIGHT,
)
from src.shapes.line import Line
from src.shapes.rectangle import Rectangle
from src.shapes.circle import Circle
from src.shapes.triangle import Triangle


def _shape_factory(data):
    """Routes a deserialized dict to the correct shape class based on its type string."""
    shape_type = data.get("type")

    if shape_type == "Line":
        return Line.from_dict(data)

    if shape_type == "Rectangle":
        return Rectangle.from_dict(data)

    if shape_type == "Circle":
        return Circle.from_dict(data)

    if shape_type == "Triangle":
        return Triangle.from_dict(data)

    print(f"[load WARNING] Unknown shape type: {shape_type}")
    return None     # Unrecognized shapes are skipped gracefully rather than crashing the load

def save_scene(scene, path=DEFAULT_SAVE_PATH):
    try:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)   # Create parent directories if they don't exist yet

        with open(path, "w", encoding="utf-8") as file:
            json.dump(scene.to_dict(), file, indent=2)  # Create parent directories if they don't exist yet

        print(f"[save] {path}")
        return True, None

    except Exception as error:
        print(f"[save ERROR] {error}")
        return False, str(error)


def save_artwork_dialog(scene):
    root = tk.Tk()
    root.withdraw()     # Hide the Tk root window — only the file dialog should be visible

    try:
        path = filedialog.asksaveasfilename(
            title="Save this Artwork",
            defaultextension=".json",
            initialfile="scene.json",
            filetypes=[
                ("JSON Scene", "*.json"),
                ("PNG Image", "*.png"),
            ],
        )
    finally:
        root.destroy()

    if not path:
        return {
            "status": "cancelled",
            "path": None,
            "message": "Save cancelled",
        }

    ext = os.path.splitext(path)[1].lower()

    if ext == ".png":
        ok, error = save_artwork_png(path)
        if ok:
            return {
                "status": "saved",
                "path": path,
                "message": "Saved artwork as PNG",
            }
        return {
            "status": "error",
            "path": None,
            "message": error or "Failed to save PNG",
        }

    if ext == "":
        path = f"{path}.json"   # Append .json if the user typed a name without an extension

    ok, error = save_scene(scene, path)
    if ok:
        return {
            "status": "saved",
            "path": path,
            "message": "Saved scene as JSON",
        }

    return {
        "status": "error",
        "path": None,
        "message": error or "Failed to save JSON",
    }


def save_artwork_png(path):
    try:
        surface = pygame.display.get_surface()
        if surface is None:
            raise RuntimeError("No active display surface")

        # Read the current OpenGL framebuffer as raw RGBA bytes
        frame_bytes = glReadPixels(0, 0, WIDTH, HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE)
        # True flag in fromstring flips the image vertically (OpenGL origin is bottom-left, Pygame is top-left)
        frame = pygame.image.fromstring(frame_bytes, (WIDTH, HEIGHT), "RGBA", True)

        # Crop out the toolbar and status bar so only the drawing canvas is saved
        artwork_h = HEIGHT - TOOLBAR_HEIGHT - STATUS_BAR_HEIGHT
        crop_rect = pygame.Rect(CANVAS_X, TOOLBAR_HEIGHT, CANVAS_W, artwork_h)
        crop_rect = crop_rect.clip(frame.get_rect())    # Clamp to frame bounds to prevent out-of-bounds blit

        artwork = pygame.Surface((crop_rect.width, crop_rect.height), pygame.SRCALPHA)
        artwork.blit(frame, (0, 0), crop_rect)

        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        pygame.image.save(artwork, path)
        print(f"[save png] {path}")
        return True, None

    except Exception as error:
        print(f"[save PNG ERROR] {error}")
        return False, str(error)


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