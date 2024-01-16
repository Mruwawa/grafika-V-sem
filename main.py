#!/usr/bin/env python3
import sys
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

viewer = [0, 0, 8.0]
heading = [0, 0, -1]
looking = [0, 0, 0]

triangle_vertices = [(-1, -1, -1), (1, -1, -1), (0, 1, 0), (-0, -1, 1)]
floor_vertices = [(-10, -1, -10), (10, -1, -10), (10, -1, 10), (-10, -1, 10)]

pyramid_rotation = 0.0
sun_rotation = 0.0

pix2angle = 0.5

sun_color = [1, 0.5, 0]

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
    glTexCoord2f(0.0, 0.0)
    glVertex3fv(floor_vertices[0])
    glTexCoord2f(1.0, 0.0)
    glVertex3fv(floor_vertices[1])
    glTexCoord2f(1.0, 1.0)
    glVertex3fv(floor_vertices[2])
    glTexCoord2f(0.0, 1.0)
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
    update_viewport(1280, 720)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)


def point_light(color):
    glPushMatrix()
    glRotatef(sun_rotation, 0.0, 1.0, 0.0)

    light_ambient = [color[0], color[1], color[2], 0.1]
    light_diffuse = [color[0], color[1], color[2], 0.5]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_position = [6.0, 2.0, 0.0, 1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)


    glBindTexture(GL_TEXTURE_2D, sun_tex)
    glTranslatef(light_position[0], light_position[1], light_position[2])
    quadratic = gluNewQuadric()
    gluQuadricTexture(quadratic, GL_TRUE)
    gluQuadricDrawStyle(quadratic, GLU_FILL)
    gluSphere(quadratic, 0.5, 10, 10)
    gluDeleteQuadric(quadratic)
    glBindTexture(GL_TEXTURE_2D, 0)
    glPopMatrix()

    glEnable(GL_LIGHT0)

def directional_light():
    light_ambient = [1, 1, 1, 0.1]
    light_diffuse = [1, 1, 1, 0.5]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_position = [-1.0, 1.0, 0.0, 0.0]

    glLightfv(GL_LIGHT1, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT1, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT1, GL_POSITION, light_position)

    # glEnable(GL_LIGHT1)

def rotate_vector_y_axis(vector, angle_deg):
    angle_rad = np.radians(angle_deg)
    rotation_matrix = np.array([
        [np.cos(angle_rad), 0, np.sin(angle_rad)],
        [0, 1, 0],
        [-np.sin(angle_rad), 0, np.cos(angle_rad)]
    ])
    rotated_vector = np.dot(rotation_matrix, vector)
    return rotated_vector

def rotate_vector_x_axis(vector, angle_deg):
    if vector[2] > 0:
        angle_deg = -angle_deg

    angle_rad = np.radians(angle_deg)

    rotation_matrix = np.array([
        [1, 0, 0],
        [0, np.cos(angle_rad), -np.sin(angle_rad)],
        [0, np.sin(angle_rad), np.cos(angle_rad)]
    ])

    rotated_vector = np.dot(rotation_matrix, vector)
    return rotated_vector

def render(n, metal_tex, sun_tex, marble_tex):
    global pyramid_rotation

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    global looking
    global heading

    looking[0], looking[1], looking[2] = viewer[0] + heading[0], viewer[1] + heading[1], viewer[2] + heading[2]

    gluLookAt(viewer[0], viewer[1], viewer[2],
              looking[0], looking[1], looking[2],
              0.0, 1.0, 0.0)

    magnitude = np.linalg.norm(heading)
    heading = heading / magnitude

    glPushMatrix()
    glRotatef(pyramid_rotation, 0.0, 1.0, 0.0)
    glBindTexture(GL_TEXTURE_2D, metal_tex)
    draw_sierpinski_triangle(triangle_vertices[0], triangle_vertices[1], triangle_vertices[2], triangle_vertices[3], n)
    glBindTexture(GL_TEXTURE_2D, 0)
    glPopMatrix()

    glBindTexture(GL_TEXTURE_2D, marble_tex)
    draw_floor()
    glBindTexture(GL_TEXTURE_2D, 0)

    point_light(sun_color)

    directional_light()


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

def loadTextures(file_name):
    texture_surface = pygame.image.load(file_name)
    texture_data = pygame.image.tostring(texture_surface, 'RGBA', True)
    width, height = texture_surface.get_width(), texture_surface.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    return texture_id

def main():
    global heading
    global pyramid_rotation
    global sun_rotation

    global metal_tex
    global sun_tex
    global marble_tex

    print("How many levels?")
    n = int(input())
    tex_enabled = True
    light_on = True
    clock = pygame.time.Clock()

    pygame.init()
    display = (900, 900)
    center_x, center_y = display[0] // 2, display[1] // 2
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption(__file__)

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    startup()
    metal_tex = loadTextures('metal.jpg')
    sun_tex = loadTextures('sun.jpg')
    marble_tex = loadTextures('marble.jpg')
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHT1)

    update_viewport(display[0], display[1])

    key_a = False
    key_d = False
    key_w = False
    key_s = False
    key_space = False
    key_shift = False

    pyramid_rotating = False
    sun_rotating = False

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
                if event.key == pygame.K_n:
                    light_on = not light_on
                    if light_on:
                        glEnable(GL_LIGHT1)
                    else:
                        glDisable(GL_LIGHT1)
                if event.key == pygame.K_j:
                    change_sun_color()
                if event.key == pygame.K_a:
                    key_a = True
                if event.key == pygame.K_d:
                    key_d = True
                if event.key == pygame.K_w:
                    key_w = True
                if event.key == pygame.K_s:
                    key_s = True
                if event.key == pygame.K_SPACE:
                    key_space = True
                if event.key == pygame.K_LSHIFT:
                    key_shift = True
                if event.key == pygame.K_r:
                    pyramid_rotating = not pyramid_rotating
                if event.key == pygame.K_e:
                    sun_rotating = not sun_rotating
                if event.key == pygame.K_h:
                    heading[0], heading[1], heading[2] = -viewer[0], -viewer[1], -viewer[2]
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    key_a = False
                if event.key == pygame.K_d:
                    key_d = False
                if event.key == pygame.K_w:
                    key_w = False
                if event.key == pygame.K_s:
                    key_s = False
                if event.key == pygame.K_SPACE:
                    key_space = False
                if event.key == pygame.K_LSHIFT:
                    key_shift = False
            elif event.type == pygame.MOUSEMOTION:
                horizontal_angle = -(event.pos[0] - (display[0]/2)) * pix2angle
                heading = rotate_vector_y_axis(heading, horizontal_angle/4)
                vertical_angle = -(event.pos[1] - (display[1]/2)) * pix2angle
                heading[1] = rotate_vector_x_axis(heading, vertical_angle/6)[1]

        if key_w:
            viewer[0], viewer[2] = viewer[0] + heading[0]/4, viewer[2] + heading[2]/4

        if key_s:
            viewer[0], viewer[2] = viewer[0] - heading[0]/4, viewer[2] - heading[2]/4

        if key_a:
            heading_left = rotate_vector_y_axis(heading, 90)
            viewer[0], viewer[2] = viewer[0] + heading_left[0]/4, viewer[2] + heading_left[2]/4

        if key_d:
            heading_right = rotate_vector_y_axis(heading, -90)
            viewer[0], viewer[2] = viewer[0] + heading_right[0] /4, viewer[2] + heading_right[2] /4

        if key_space:
            viewer[1] = viewer[1] + 0.2

        if key_shift:
            viewer[1] = viewer[1] - 0.2

        if pyramid_rotating:
            pyramid_rotation += 0.3

        if sun_rotating:
            sun_rotation += 0.3

        render(n, metal_tex, sun_tex, marble_tex)
        pygame.mouse.set_pos(center_x, center_y)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

def change_sun_color():
    global sun_color

    if sun_color == [1, 0.5, 0]:
        sun_color = [1, 0, 0]
    elif sun_color == [1, 0, 0]:
        sun_color = [0, 1, 0]
    elif sun_color == [0, 1, 0]:
        sun_color = [0, 0, 1]
    elif sun_color == [0, 0, 1]:
        sun_color = [1, 0.5, 0]

if __name__ == '__main__':
    main()

#t - textury on/off
#r - obrot piramidy on/off
#e - obrot slonca on/off
#j - zmiana koloru swiatla punktowego
#n - swiatlo kierunkowe on/off
#h - spojrzenie na srodek
#
#SHIFT - kamera w dol
#SPACE - kamera w gore
#a - kamera w lewo
#d - kamera w prawo
#w - kamera do przodu
#s - kamera do tylu
#mysz - rozgladanie sie