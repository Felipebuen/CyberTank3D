"""
projectile.py – Projéteis do CyberTank 3D
"""

import math
from OpenGL.GL import *
from OpenGL.GLU import *
from config import *


class Projectile:
    def __init__(self, position, direction, owner):
        self.pos    = list(position)
        self.dir    = list(direction)   
        self.owner  = owner
        self.life   = PROJ_LIFE
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.life -= dt
        if self.life <= 0:
            self.active = False
            return
        self.pos[0] += self.dir[0] * PROJ_SPEED * dt
        self.pos[1] += self.dir[1] * PROJ_SPEED * dt
        self.pos[2] += self.dir[2] * PROJ_SPEED * dt

    def draw(self):
        if not self.active:
            return
        glPushMatrix()
        glTranslatef(*self.pos)
        glMaterialfv(GL_FRONT, GL_EMISSION, (*PROJECTILE_COLOR, 1.0))
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (*PROJECTILE_COLOR, 1.0))
        q = gluNewQuadric()
        gluSphere(q, 0.15, 10, 8)
        gluDeleteQuadric(q)
        glMaterialfv(GL_FRONT, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))
        glPopMatrix()


class ProjectileManager:
    def __init__(self):
        self.projectiles: list[Projectile] = []

    def add(self, proj: Projectile):
        self.projectiles.append(proj)

    def update(self, dt, arena, tanks):
        for p in self.projectiles:
            if not p.active:
                continue
            p.update(dt)

            limit = ARENA_SIZE - 0.5
            if abs(p.pos[0]) > limit or abs(p.pos[2]) > limit:
                p.active = False
                continue

            # Colisão contra Obstáculos
            hit_obs = False
            for (ox, oz), r in OBSTACLES:
                if math.hypot(p.pos[0] - ox, p.pos[2] - oz) < r + 0.15:
                    p.active = False
                    hit_obs = True
                    break
            
            if hit_obs:
                continue

            # Colisão contra Tanques
            for tank in tanks:
                if tank is p.owner or not tank.alive:
                    continue
                dx = p.pos[0] - tank.pos[0]
                dz = p.pos[2] - tank.pos[2]
                if math.hypot(dx, dz) < 1.1:
                    tank.take_damage(PROJ_DAMAGE)
                    p.active = False
                    break

        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self):
        for p in self.projectiles:
            p.draw()