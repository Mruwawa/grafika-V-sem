#!/usr/bin/env python3
import sys
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

viewer = [0, 0, 8.0]
heading = [0,0,-1]

triangle_vertices = [(-1, -1, -1), (1, -1, -1), (0, 1, 0), (-0, -1, 1)]
floor_vertices = [(-2, -1, -2), (2, -1, -2), (2, -1, 2), (-2, -1, 2)]

theta = 0.0
pix2angle = 0.5

alpha = 0.0

looking = [0, 0, 0]

mouse_x_pos_old = 0
delta_x = 0

mouse_y_pos_old = 0
delta_y = 0

a = 0

h_camera_angle = 0

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
    update_viewport(1280, 720)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    point_light([1, 0, 0])

    directional_light()

    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)


def point_light(color):
    light_ambient = [color[0], color[1], color[2], 0.1]
    light_diffuse = [color[0], color[1], color[2], 0.5]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_position = [10.0, 0.0, 0.0, 1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glPushMatrix()
    glTranslatef(light_position[0], light_position[1], light_position[2])
    quadratic = gluNewQuadric()
    gluQuadricDrawStyle(quadratic, GLU_FILL)
    gluSphere(quadratic, 1, 10, 10)
    gluDeleteQuadric(quadratic)
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

    glEnable(GL_LIGHT1)

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
    angle_rad = np.radians(angle_deg)

    rotation_matrix = np.array([
        [1, 0, 0],
        [0, np.cos(angle_rad), -np.sin(angle_rad)],
        [0, np.sin(angle_rad), np.cos(angle_rad)]
    ])

    rotated_vector = np.dot(rotation_matrix, vector)
    return rotated_vector

def render(n):
    global theta

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

    glRotatef(theta, 0.0, 1.0, 0.0)

    draw_sierpinski_triangle(triangle_vertices[0], triangle_vertices[1], triangle_vertices[2], triangle_vertices[3], n)
    draw_floor()

    point_light([1, 0, 0])
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

    pygame.init()
    display = (1280, 720)
    center_x, center_y = display[0] // 2, display[1] // 2
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption(__file__)

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    startup()
    texture_id = loadTextures()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    update_viewport(display[0], display[1])

    clock = pygame.time.Clock()
    global mouse_x_pos_old
    global delta_x
    global mouse_y_pos_old
    global delta_y
    global h_camera_angle
    global heading
    global theta
    global looking

    key_a = False
    key_d = False
    key_w = False
    key_s = False
    key_space = False
    key_shift = False

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
                delta_x = event.pos[0]
                horizontal_angle = -(delta_x - (display[0]/2)) * pix2angle

                heading = rotate_vector_y_axis(heading, horizontal_angle/4)
                delta_y = event.pos[1]

                vertical_angle = -(delta_y - (display[1]/2)) * pix2angle
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

        render(n)
        pygame.mouse.set_pos(center_x, center_y)
        pygame.display.flip()
        clock.tick(60)

    theta = theta + 0.1
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
