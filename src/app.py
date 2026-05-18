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

    # Set up a top-left origin 2D projection matching the window's pixel dimensions
    gluOrtho2D(0, WIDTH, HEIGHT, 0) # Y-axis flipped: (0,0) = top-left, (WIDTH,HEIGHT) = bottom-right

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    r, g, b = (c / 255 for c in COLOR_BG)
    glClearColor(r, g, b, 1.0)

    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)  # Anti-alias lines at the cost of some performance

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def run():
    pygame.init()
    pygame.display.set_caption(TITLE)
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)    # DOUBLEBUF prevents screen tearing

    clock = pygame.time.Clock()

    init_opengl()

    scene = Scene()

    toolbar = Toolbar()
    properties_panel = PropertiesPanel()
    status_bar = StatusBar()

    # Draw order matters: scene → preview → UI (UI always on top)
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
            renderer.draw_preview(preview)  # Ghost shape shown while mouse button is held

        if input_handler.is_rotation_active() and scene.selected:
            renderer.draw_rotation_pivot(scene.selected)    # Pivot crosshair only during active rotation

        glLineWidth(1.0)     # Reset before UI draw so panel/toolbar lines aren't affected by shape state

        toolbar.draw(
            input_handler.current_tool,
            input_handler.current_outline_color,
            input_handler.current_fill_color,
            input_handler.current_line_width
        )

        selected_shape = getattr(scene, "selected", None)
        properties_panel.draw(selected_shape)

        status_bar.draw()

        toolbar.draw_overlay()  # Color picker and dropdowns rendered last so they appear above everything

        #DYNAMIC INPUT UI
        if input_handler.current_tool == "polygon" and hasattr(input_handler, "polygon_input_string"):
            renderer.draw_dynamic_input("polygon", input_handler.polygon_input_string)
        elif input_handler.current_tool == "star" and hasattr(input_handler, "star_input_string"):
            renderer.draw_dynamic_input("star", input_handler.star_input_string)

        pygame.display.flip()   # Swap front/back buffer to display the completed frame
        clock.tick(FPS) # Cap framerate to avoid unnecessary CPU/GPU usage

    pygame.quit()


if __name__ == "__main__":
    run()