"""
arena.py – Arena do CyberTank 3D
"""

import math
from OpenGL.GL import *
from OpenGL.GLU import *
from config import *


class Arena:
    def __init__(self, tex_mgr=None):
        self._tex_mgr  = tex_mgr
        self._floor_id = tex_mgr.load("textures/floor.png")  if tex_mgr else None
        self._wall_id  = tex_mgr.load("textures/wall.png")   if tex_mgr else None

    def draw(self):
        self._draw_floor()
        self._draw_track()
        self._draw_walls()
        self._draw_grid()

    def _draw_floor(self):
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (*FLOOR_COLOR, 1.0))
        glMaterialfv(GL_FRONT, GL_SPECULAR,  (0.1, 0.1, 0.1, 1.0))
        glMaterialf (GL_FRONT, GL_SHININESS, 10)
        glMaterialfv(GL_FRONT, GL_EMISSION,  (0.0, 0.0, 0.0, 1.0))

        s = ARENA_SIZE
        tile = 4.0

        if self._floor_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self._floor_id)

        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 0);         glVertex3f(-s, 0,  s)
        glTexCoord2f(s/tile, 0);    glVertex3f( s, 0,  s)
        glTexCoord2f(s/tile, s/tile);glVertex3f( s, 0, -s)
        glTexCoord2f(0, s/tile);    glVertex3f(-s, 0, -s)
        glEnd()

        if self._floor_id:
            glDisable(GL_TEXTURE_2D)

    def _draw_track(self):
        glDisable(GL_LIGHTING)
        y = 0.01 
        w = 4.5 # Largura do asfalto
        
        # 1. Pista Cinza Escura (Curvas preenchidas com Polígonos)
        glColor3f(*TRACK_COLOR)
        
        # Desenha as juntas (círculos) para arredondar as curvas
        for cx, cz in CHECKPOINTS:
            glBegin(GL_POLYGON)
            for i in range(36):
                ang = math.radians(i * 10)
                glVertex3f(cx + math.cos(ang)*w, y, cz + math.sin(ang)*w)
            glEnd()

        # Desenha os segmentos retos interligando os pontos
        glBegin(GL_QUADS)
        for i in range(len(CHECKPOINTS)):
            p1 = CHECKPOINTS[i]
            p2 = CHECKPOINTS[(i+1) % len(CHECKPOINTS)]
            dx, dz = p2[0]-p1[0], p2[1]-p1[1]
            length = math.hypot(dx, dz)
            if length == 0: continue
            
            nx, nz = -dz/length, dx/length
            
            glVertex3f(p1[0] + nx*w, y, p1[1] + nz*w)
            glVertex3f(p1[0] - nx*w, y, p1[1] - nz*w)
            glVertex3f(p2[0] - nx*w, y, p2[1] - nz*w)
            glVertex3f(p2[0] + nx*w, y, p2[1] + nz*w)
        glEnd()

        # 2. Linha Tracejada (Faixa da rodovia)
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(4.0)
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(4, 0x00FF) 
        
        y_line = 0.02
        glBegin(GL_LINE_LOOP)
        for cp in CHECKPOINTS:
            glVertex3f(cp[0], y_line, cp[1])
        glEnd()
        
        glDisable(GL_LINE_STIPPLE)
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
        
        # 3. Desenha os Obstáculos em 3D
        self._draw_obstacles()

    def _draw_obstacles(self):
        # Cilindros de Concreto pintados de vermelho
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.8, 0.1, 0.1, 1.0))
        glMaterialfv(GL_FRONT, GL_SPECULAR, (0.2, 0.2, 0.2, 1.0))
        
        for (ox, oz), r in OBSTACLES:
            glPushMatrix()
            glTranslatef(ox, 0.0, oz)
            glRotatef(-90, 1, 0, 0) # Coloca o cilindro em pé (Z para Y)
            
            q = gluNewQuadric()
            gluCylinder(q, r, r, 2.0, 16, 2) # Base e altura
            
            # Tampa de cima do obstáculo
            glTranslatef(0, 0, 2.0)
            gluDisk(q, 0.0, r, 16, 1)
            
            gluDeleteQuadric(q)
            glPopMatrix()

    def _draw_walls(self):
        s = ARENA_SIZE
        h = WALL_HEIGHT
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (*WALL_COLOR, 1.0))
        glMaterialfv(GL_FRONT, GL_SPECULAR,  (0.5, 0.5, 0.8, 1.0))
        glMaterialf (GL_FRONT, GL_SHININESS, 64)

        if self._wall_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self._wall_id)

        walls = [
            (-s, -s,  s, -s, (0, 0,  1)),
            ( s, -s,  s,  s, (-1, 0, 0)),
            ( s,  s, -s,  s, (0, 0, -1)),
            (-s,  s, -s, -s, (1, 0,  0)),
        ]
        for (x0, z0, x1, z1, nm) in walls:
            length = max(abs(x1-x0), abs(z1-z0))
            glBegin(GL_QUADS)
            glNormal3fv(nm)
            glTexCoord2f(0, 0);            glVertex3f(x0, 0, z0)
            glTexCoord2f(length/4, 0);     glVertex3f(x1, 0, z1)
            glTexCoord2f(length/4, h/2);   glVertex3f(x1, h, z1)
            glTexCoord2f(0, h/2);          glVertex3f(x0, h, z0)
            glEnd()

        if self._wall_id:
            glDisable(GL_TEXTURE_2D)

    def _draw_grid(self):
        glDisable(GL_LIGHTING)
        glColor3f(*GRID_COLOR)
        glLineWidth(0.8)
        s = ARENA_SIZE
        step = 2.0
        y = 0.03
        glBegin(GL_LINES)
        x = -s
        while x <= s + 0.001:
            glVertex3f(x, y,  s)
            glVertex3f(x, y, -s)
            x += step
        z = -s
        while z <= s + 0.001:
            glVertex3f( s, y, z)
            glVertex3f(-s, y, z)
            z += step
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)