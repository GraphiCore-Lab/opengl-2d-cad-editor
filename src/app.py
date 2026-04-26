"""
app.py — Pygame + OpenGL penceresi ve ana döngü.
Kişi 3'ün dosyası: UI toolbar, properties panel ve status bar burada bağlanır.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from src.utils.constants import WIDTH, HEIGHT, TITLE, FPS, COLOR_BG
from src.core.scene import Scene
from src.renderer import Renderer
from src.input_handler import InputHandler

from src.ui.toolbar import Toolbar
from src.ui.properties_panel import PropertiesPanel
from src.ui.status_bar import StatusBar


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

    scene = Scene()

    toolbar = Toolbar()
    properties_panel = PropertiesPanel()
    status_bar = StatusBar()

    renderer = Renderer(scene, show_grid=True)

    input_handler = InputHandler(
        scene=scene,
        toolbar=toolbar,
        properties_panel=properties_panel,
        status_bar=status_bar
    )

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                input_handler.handle_event(event)

        renderer.render()

        preview = input_handler.get_preview()
        if preview:
            renderer.draw_preview(preview)

        # UI çiziminden önce global line width state'ini sıfırla.
        glLineWidth(1.0)

        toolbar.draw(
            input_handler.current_tool,
            input_handler.current_outline_color,
            input_handler.current_fill_color,
            input_handler.current_line_width
        )

        selected_shape = getattr(scene, "selected", None)
        properties_panel.draw(selected_shape)

        status_bar.draw()

        # Color picker her şeyin üstünde görünsün
        toolbar.draw_overlay()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run()
    