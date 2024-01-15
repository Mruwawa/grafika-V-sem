#!/usr/bin/env python3
import sys
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

viewer = [0, 0, 8.0]

triangle_vertices = [(-1, -1, -1), (1, -1, -1), (0, 1, 0), (-0, -1, 1)]
floor_vertices = [(-2, -1, -2), (2, -1, -2), (2, -1, 2), (-2, -1, 2)]

theta = 0.0
pix2angle = 1.0

alpha = 0.0

looking = [0, 0, 0]

left_mouse_button_pressed = 0
mouse_x_pos_old = 0
delta_x = 0

mat_ambient = [1.0, 1.0, 1.0, 1.0]
mat_diffuse = [1.0, 1.0, 1.0, 1.0]
mat_specular = [1.0, 1.0, 1.0, 1.0]
mat_shininess = 20.0

light_ambient = [0.1, 0.1, 0.1, 1.0]
light_diffuse = [0.8, 0.8, 0.8, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [0.0, 0.0, 8.0, 1.0]

att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001

def middle(p1, p2):
    return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2

def calculate_normal(p1, p2, p3):
    # Calculate vectors
    u = np.array(p3) - np.array(p1)
    v = np.array(p2) - np.array(p1)

    normal = np.cross(u, v)
    norm = np.linalg.norm(normal)
    if norm == 0:
       return (0,0,0)
    return normal / norm

def draw_floor():
    A = np.array(floor_vertices[2])
    B = np.array(floor_vertices[1])
    C = np.array(floor_vertices[0])
    AB = B - A
    AC = C - A

    normal = np.cross(AB, AC)

    normal_unit = normal / np.linalg.norm(normal)

    glBegin(GL_QUADS)
    glNormal3fv(normal_unit)
    glVertex3fv(floor_vertices[0])
    glVertex3fv(floor_vertices[1])
    glVertex3fv(floor_vertices[2])
    glVertex3fv(floor_vertices[3])
    glEnd()

def draw_sierpinski_triangle(p1, p2, p3, p4, level):
    if level == 0:
        normal1 = calculate_normal(p1, p2, p3)
        normal2 = calculate_normal(p1, p4, p2)
        normal3 = calculate_normal(p3, p4, p1)
        normal4 = calculate_normal(p4, p3, p2)

        glBegin(GL_TRIANGLES)
        glNormal3fv(normal1)
        glTexCoord2f(0.0, 0.0)
        glVertex3fv(p1)
        glTexCoord2f(1.0, 0.0)
        glVertex3fv(p2)
        glTexCoord2f(0.5, 1.0)
        glVertex3fv(p3)
        glEnd()

        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_TRIANGLES)
        glNormal3fv(normal2)
        glTexCoord2f(0.0, 0.0)
        glVertex3fv(p1)
        glTexCoord2f(1.0, 0.0)
        glVertex3fv(p2)
        glTexCoord2f(0.5, 1.0)
        glVertex3fv(p4)
        glEnd()
        glColor3f(1, 1, 1)

        glBegin(GL_TRIANGLES)
        glNormal3fv(normal3)
        glTexCoord2f(0.0, 0.0)
        glVertex3fv(p1)
        glTexCoord2f(1.0, 0.0)
        glVertex3fv(p3)
        glTexCoord2f(0.5, 1.0)
        glVertex3fv(p4)
        glEnd()

        glBegin(GL_TRIANGLES)
        glNormal3fv(normal4)
        glTexCoord2f(0.0, 0.0)
        glVertex3fv(p2)
        glTexCoord2f(1.0, 0.0)
        glVertex3fv(p3)
        glTexCoord2f(0.5, 1.0)
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

def startup():
    update_viewport(600, 800)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, att_quadratic)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

def render(n):
    global theta
    global alpha

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    global looking

    gluLookAt(viewer[0], viewer[1], viewer[2],
              looking[0], looking[1], looking[2], 0.0, 1.0, 0.0)

    if left_mouse_button_pressed:
        theta += delta_x * pix2angle

    glRotatef(theta, 0.0, 1.0, 0.0)

    draw_sierpinski_triangle(triangle_vertices[0], triangle_vertices[1], triangle_vertices[2], triangle_vertices[3], n)
    draw_floor()

    glFlush()

def update_viewport(width, height):
    global pix2angle
    pix2angle = 360.0 / width

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(70, 1.0, 0.1, 300.0)

    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def loadTextures():
    texture_surface = pygame.image.load('metal.jpg')
    texture_data = pygame.image.tostring(texture_surface, 'RGBA', True)
    width, height = texture_surface.get_width(), texture_surface.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    return texture_id

def main():
    print("How many levels?")
    n = int(input())
    tex_enabled = True

    global alpha
    alpha = 0.1
    pygame.init()
    display = (400, 400)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption(__file__)

    startup()
    texture_id = loadTextures()
    if tex_enabled:
        glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    update_viewport(display[0], display[1])

    clock = pygame.time.Clock()
    global left_mouse_button_pressed
    global mouse_x_pos_old
    global delta_x

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_t:
                    tex_enabled = not tex_enabled
                    if tex_enabled:
                        glEnable(GL_TEXTURE_2D)
                    else:
                        glDisable(GL_TEXTURE_2D)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    left_mouse_button_pressed = 1
                    mouse_x_pos_old = event.pos[0]
                if event.button == 4:
                    viewer[2] = viewer[2] + 0.5
                elif event.button == 5:
                    viewer[2] = viewer[2] - 0.5
                    if viewer[2] < 1:
                        viewer[2] = 1
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    left_mouse_button_pressed = 0
            elif event.type == pygame.MOUSEMOTION:
                if left_mouse_button_pressed:
                    delta_x = event.pos[0] - mouse_x_pos_old
                    mouse_x_pos_old = event.pos[0]

        render(n)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
