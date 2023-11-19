import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

triangle_vertices = [(-1, -1, -1), (1, -1, -1), (0, 1, 0), (-0, -1, 1)]

floor_vertices = [(-2, -1, -2), (2, -1, -2), (2, -1, 2), (-2, -1, 2)]


def draw_floor():
    glBegin(GL_QUADS)
    glVertex3fv(floor_vertices[0])
    glVertex3fv(floor_vertices[1])
    glVertex3fv(floor_vertices[2])
    glVertex3fv(floor_vertices[3])
    glEnd()


def middle(p1, p2):
    return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2


def draw_sierpinski_triangle(p1, p2, p3, p4, level):
    if level == 0:
        glBegin(GL_TRIANGLES)
        glTexCoord2f(0.5, 0.0)
        glVertex3fv(p1)
        glTexCoord2f(1.0, 1.0)
        glVertex3fv(p2)
        glTexCoord2f(0.0, 1.0)
        glVertex3fv(p3)
        glEnd()
        glBegin(GL_TRIANGLES)
        glTexCoord2f(0.5, 0.0)
        glVertex3fv(p1)
        glTexCoord2f(1.0, 1.0)
        glVertex3fv(p2)
        glTexCoord2f(0.0, 1.0)
        glVertex3fv(p4)
        glEnd()
        glBegin(GL_TRIANGLES)
        glTexCoord2f(0.5, 0.0)
        glVertex3fv(p1)
        glTexCoord2f(1.0, 1.0)
        glVertex3fv(p3)
        glTexCoord2f(0.0, 1.0)
        glVertex3fv(p4)
        glEnd()
        glBegin(GL_TRIANGLES)
        glTexCoord2f(0.5, 0.0)
        glVertex3fv(p2)
        glTexCoord2f(1.0, 1.0)
        glVertex3fv(p3)
        glTexCoord2f(0.0, 1.0)
        glVertex3fv(p4)
        glEnd()
    else:
        m1 = middle(p1, p2)
        m2 = middle(p2, p3)
        m3 = middle(p1, p3)
        m4 = middle(p1, p4)
        m5 = middle(p2, p4)
        m6 = middle(p3, p4)
        draw_sierpinski_triangle(p1, m1, m3, m4, level - 1)
        draw_sierpinski_triangle(m1, p2, m2, m5, level - 1)
        draw_sierpinski_triangle(m2, p3, m3, m6, level - 1)
        draw_sierpinski_triangle(m4, m5, m6, p4, level - 1)


def loadTextures():
    texture_surface = pygame.image.load('texture.jpg')
    texture_data = pygame.image.tostring(texture_surface, 'RGBA', True)
    width, height = texture_surface.get_width(), texture_surface.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    return texture_id


def setup_lighting():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    light_ambient = [0.0, 0.5, 0, 1.0]
    light_diffuse = [0.8, 0.8, 0.0, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_position = [5.0, 5.0, 10.0, 5.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)


def main():
    print("How many levels? ")
    n = int(input())

    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(60, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0, 0, -5)

    texture_id = loadTextures()
    setup_lighting()

    rotating = ""
    color = ""
    r = 0
    g = 0.5
    b = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    rotating = "LEFT"
                if event.key == pygame.K_RIGHT:
                    rotating = "RIGHT"
                if event.key == pygame.K_UP:
                    rotating = "UP"
                if event.key == pygame.K_DOWN:
                    rotating = "DOWN"
                if event.key == pygame.K_r:
                    color = "R"
                if event.key == pygame.K_g:
                    color = "G"
                if event.key == pygame.K_b:
                    color = "B"
            if event.type == pygame.KEYUP:
                rotating = ""
                color = ""

        if rotating == "LEFT":
            glRotatef(1, 0, 15, 0)
        if rotating == "RIGHT":
            glRotatef(1, 0, -15, 0)
        if rotating == "UP":
            glRotatef(1, 15, 0, 0)
        if rotating == "DOWN":
            glRotatef(1, -15, 0, 0)

        if color == "R":
            r = (r + 0.05) % 1
            print(r)
        if color == "G":
            g = (g + 0.05) % 1
        if color == "B":
            b = (b + 0.05) % 1
        if color != "":
            light_ambient = [r, g, b, 1.0]
            glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)

        glBindTexture(GL_TEXTURE_2D, texture_id)
        draw_sierpinski_triangle(triangle_vertices[0], triangle_vertices[1], triangle_vertices[2], triangle_vertices[3], n)
        draw_floor()
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == "__main__":
    main()
