"""
app.py — Pygame + OpenGL penceresi ve ana döngü.
Kişi 3'ün dosyası (UI toolbar ile birlikte genişletecek).
"""
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from src.utils.constants import WIDTH, HEIGHT, TITLE, FPS, COLOR_BG
from src.core.scene import Scene
from src.renderer import Renderer
from src.input_handler import InputHandler


def init_opengl():
    """OpenGL 2D ortho projeksiyonu kur."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Sol üst (0,0), sağ alt (WIDTH, HEIGHT)
    gluOrtho2D(0, WIDTH, HEIGHT, 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    r, g, b = (c / 255 for c in COLOR_BG)
    glClearColor(r, g, b, 1.0)

    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)


def run():
    pygame.init()
    pygame.display.set_caption(TITLE)
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    clock = pygame.time.Clock()

    init_opengl()

    scene        = Scene()
    renderer     = Renderer(scene, show_grid=True)
    input_handler = InputHandler(scene)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                input_handler.handle_event(event)

        # ── Render ──────────────────────────────────────────
        renderer.render()

        # Önizleme (çizilmekte olan shape)
        preview = input_handler.get_preview()
        if preview:
            renderer.draw_preview(preview)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()