import os

import pygame


def _pixelify_paths():
    base_dir = os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "fonts",
            "Pixelify_Sans",
            "static",
        )
    )
    return (
        os.path.join(base_dir, "PixelifySans-Regular.ttf"),
        os.path.join(base_dir, "PixelifySans-Bold.ttf"),
    )


def load_ui_fonts(body_size=13, title_size=20, small_size=12):
    regular_path, bold_path = _pixelify_paths()

    try:
        if os.path.exists(regular_path) and os.path.exists(bold_path):
            return (
                pygame.font.Font(regular_path, body_size),
                pygame.font.Font(bold_path, title_size),
                pygame.font.Font(regular_path, small_size),
            )
    except pygame.error:
        pass

    return (
        pygame.font.SysFont("Segoe UI", body_size),
        pygame.font.SysFont("Segoe UI", title_size, bold=True),
        pygame.font.SysFont("Segoe UI", small_size),
    )