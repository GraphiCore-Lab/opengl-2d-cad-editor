from OpenGL.GL import *
from src.utils.constants import WIDTH, HEIGHT


class StatusBar:
    def __init__(self):
        self.mouse_x = 0
        self.mouse_y = 0
        self.height = 30

    def update_mouse_position(self, x, y):
        self.mouse_x = x
        self.mouse_y = y

    def draw(self):
        y = HEIGHT - self.height

        glColor3f(0.86, 0.86, 0.86)
        glBegin(GL_QUADS)
        glVertex2f(0, y)
        glVertex2f(WIDTH, y)
        glVertex2f(WIDTH, HEIGHT)
        glVertex2f(0, HEIGHT)
        glEnd()

        glColor3f(0.25, 0.25, 0.25)
        glBegin(GL_LINE_LOOP)
        glVertex2f(0, y)
        glVertex2f(WIDTH, y)
        glVertex2f(WIDTH, HEIGHT)
        glVertex2f(0, HEIGHT)
        glEnd()