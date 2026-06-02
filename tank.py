"""
tank.py – Tanque jogador e IA (CyberTank 3D)
"""

import math
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from config import *
from projectile import Projectile

class Tank:
    def __init__(self, position, color):
        self.pos        = list(position)
        self.pos[1]     = 0.4   
        self.color      = color
        self.angle      = 0.0
        self.turret_angle = 0.0
        self.health     = TANK_HEALTH
        self.alive      = True
        self._shoot_timer = 0.0
        
        self.lap = 1
        self.current_checkpoint = 0
        self.wheel_angle = 0.0  
        
        # ── Efeitos Visuais (Juice) e Power-Ups ──
        self.recoil = 0.0
        self.particles = []
        self.nitro_timer = 0.0
        self.current_speed = 0.0
        
        # ── Física de Suspensão (Pitch & Roll) ──
        self.pitch = 0.0
        self.roll = 0.0
        self.target_pitch = 0.0
        self.target_roll = 0.0

    def update_effects(self, dt):
        """Atualiza fumaça, timers, recuo do canhão e suspensão"""
        if not self.alive: return
        
        # Recuperação do tranco do canhão
        self.recoil = max(0.0, self.recoil - dt * 2.0)
        self.nitro_timer = max(0.0, self.nitro_timer - dt)
        
        # Lerp da Suspensão: Move a inclinação atual até o alvo de forma suave
        self.pitch += (self.target_pitch - self.pitch) * 8.0 * dt
        self.roll += (self.target_roll - self.roll) * 8.0 * dt
        
        # Atualiza sistema de partículas (fumaça)
        for p in self.particles:
            p['life'] -= dt
            p['pos'][1] += dt * 1.5  
            p['size'] += dt * 0.1    
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        # Emite fumaça
        if self.current_speed > 0.1 and len(self.particles) < 20:
            if np.random.rand() > 0.5:
                bwd = -self._forward()
                px = self.pos[0] + bwd[0] * 1.2 + (np.random.rand()-0.5)*0.4
                py = 0.2
                pz = self.pos[2] + bwd[2] * 1.2 + (np.random.rand()-0.5)*0.4
                self.particles.append({'pos': [px, py, pz], 'life': 0.8, 'size': 0.15})

    def check_race_progress(self):
        if self.lap > MAX_LAPS: return

        next_cp = CHECKPOINTS[self.current_checkpoint]
        dx = self.pos[0] - next_cp[0]
        dz = self.pos[2] - next_cp[1]
        dist = math.hypot(dx, dz)

        if dist < CHECKPOINT_RADIUS:
            self.current_checkpoint += 1
            if self.current_checkpoint >= len(CHECKPOINTS):
                self.current_checkpoint = 0
                self.lap += 1
                if isinstance(self, PlayerTank):
                    print(f"Você completou a volta! Volta atual: {self.lap}/{MAX_LAPS}")

    def take_damage(self, dmg: int):
        self.health -= dmg
        if self.health <= 0:
            self.respawn()

    def respawn(self):
        self.health = getattr(self, 'max_health', TANK_HEALTH)
        self.nitro_timer = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        respawn_idx = self.current_checkpoint - 1
        if respawn_idx < 0:
            respawn_idx = len(CHECKPOINTS) - 1
        cp = CHECKPOINTS[respawn_idx]
        self.pos[0] = cp[0]
        self.pos[1] = 0.4 
        self.pos[2] = cp[1]

    def _forward(self):
        rad = math.radians(self.angle)
        return np.array([math.sin(rad), 0.0, math.cos(rad)])

    def _turret_forward(self):
        rad = math.radians(self.angle + self.turret_angle)
        return np.array([math.sin(rad), 0.0, math.cos(rad)])

    def shoot(self):
        if self._shoot_timer > 0: return None
        self._shoot_timer = SHOOT_COOLDOWN
        
        self.recoil = 0.5 
        
        fwd   = self._turret_forward()
        origin = [self.pos[0] + fwd[0] * 1.6, self.pos[1] + 0.6, self.pos[2] + fwd[2] * 1.6]
        return Projectile(origin, fwd.tolist(), owner=self)

    def draw(self):
        if not self.alive: return
        
        self._draw_shadow()
        self._draw_particles()
        
        glPushMatrix()
        glTranslatef(*self.pos)
        glRotatef(self.angle, 0, 1, 0)
        
        # ── Aplicação da Suspensão Dinâmica ──
        glRotatef(self.pitch, 1, 0, 0) # Mergulho (Aceleração/Frenagem)
        glRotatef(self.roll, 0, 0, 1)  # Rolagem (Força Centrífuga)

        self._draw_chassis()
        self._draw_wheels()

        glPushMatrix()
        glTranslatef(0.0, 0.55, 0.0)
        glRotatef(self.turret_angle, 0, 1, 0)
        self._draw_turret()

        glPushMatrix()
        glTranslatef(0.0, 0.1, 0.55)
        self._draw_cannon()
        glPopMatrix()

        glPopMatrix()
        glPopMatrix()

    def _draw_shadow(self):
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE) 
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glPushMatrix()
        glTranslatef(self.pos[0], 0.02, self.pos[2])
        glRotatef(self.angle, 0, 1, 0)

        w = 1.0  
        l = 0.9  

        glBegin(GL_TRIANGLE_FAN)
        glColor4f(0.0, 0.0, 0.0, 0.8)
        glVertex3f(0.0, 0.0, 0.0)

        glColor4f(0.0, 0.0, 0.0, 0.0)
        segments = 16
        for i in range(segments + 1):
            theta = 2.0 * math.pi * float(i) / float(segments)
            x = w * math.cos(theta)
            z = l * math.sin(theta)
            glVertex3f(x, 0.0, z)
        glEnd()

        glPopMatrix()
        glDisable(GL_BLEND)
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)

    def _draw_particles(self):
        glDisable(GL_LIGHTING)
        for p in self.particles:
            alpha = p['life'] 
            glColor4f(0.4, 0.4, 0.4, alpha)
            glPushMatrix()
            glTranslatef(*p['pos'])
            glScalef(p['size'], p['size'], p['size'])
            self._draw_box()
            glPopMatrix()
        glEnable(GL_LIGHTING)

    def _set_material(self, diffuse, specular=(1.0, 1.0, 1.0, 1.0), shine=64):
        if self.nitro_timer > 0:
            diffuse = (0.2, 1.0, 0.2)
            
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (*diffuse, 1.0))
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialf(GL_FRONT, GL_SHININESS, shine)

    def _draw_chassis(self):
        self._set_material(self.color)
        glPushMatrix()
        glScalef(1.0, 0.5, 1.2)
        self._draw_box()
        glPopMatrix()
        
    def _draw_wheels(self):
        posicoes_rodas = [
            (-0.7, -0.1,  0.4), ( 0.5, -0.1,  0.4),
            (-0.7, -0.1, -0.4), ( 0.5, -0.1, -0.4)
        ]
        for px, py, pz in posicoes_rodas:
            glPushMatrix()
            glTranslatef(px, py, pz)
            glRotatef(90, 0, 1, 0)
            glRotatef(self.wheel_angle, 0, 0, 1)

            self._set_material((0.15, 0.15, 0.15))
            q = gluNewQuadric()
            gluCylinder(q, 0.3, 0.3, 0.2, 12, 2)
            gluDisk(q, 0.0, 0.3, 12, 1)
            glTranslatef(0, 0, 0.2)
            gluDisk(q, 0.0, 0.3, 12, 1)
            gluDeleteQuadric(q)
            
            self._set_material((0.6, 0.6, 0.6)) 
            glPushMatrix()
            glTranslatef(0.0, 0.0, 0.02) 
            glPushMatrix()
            glScalef(0.4, 0.08, 0.02)
            self._draw_box()
            glPopMatrix()
            glPushMatrix()
            glScalef(0.08, 0.4, 0.02)
            self._draw_box()
            glPopMatrix()
            glPopMatrix()

            glPushMatrix()
            glTranslatef(0.0, 0.0, -0.22)
            glPushMatrix()
            glScalef(0.4, 0.08, 0.02)
            self._draw_box()
            glPopMatrix()
            glPushMatrix()
            glScalef(0.08, 0.4, 0.02)
            self._draw_box()
            glPopMatrix()
            glPopMatrix()

            glPopMatrix()

    def _draw_turret(self):
        self._set_material(tuple(c * 0.85 for c in self.color))
        q = gluNewQuadric()
        gluSphere(q, 0.45, 16, 8)
        gluDeleteQuadric(q)

    def _draw_cannon(self):
        self._set_material(tuple(c * 0.6 for c in self.color))
        glPushMatrix()
        glTranslatef(0.0, 0.0, -self.recoil)
        glRotatef(0, 1, 0, 0)
        q = gluNewQuadric()
        gluCylinder(q, 0.1, 0.07, 0.9, 10, 2)
        gluDeleteQuadric(q)
        glPopMatrix()

    @staticmethod
    def _draw_box():
        verts = [
            [-0.5,-0.5,-0.5], [ 0.5,-0.5,-0.5], [ 0.5, 0.5,-0.5], [-0.5, 0.5,-0.5],
            [-0.5,-0.5, 0.5], [ 0.5,-0.5, 0.5], [ 0.5, 0.5, 0.5], [-0.5, 0.5, 0.5],
        ]
        faces = [
            ([0,1,2,3], ( 0, 0,-1)), ([4,5,6,7], ( 0, 0, 1)),
            ([0,4,7,3], (-1, 0, 0)), ([1,5,6,2], ( 1, 0, 0)),
            ([3,2,6,7], ( 0, 1, 0)), ([0,1,5,4], ( 0,-1, 0)),
        ]
        glBegin(GL_QUADS)
        for idxs, normal in faces:
            glNormal3fv(normal)
            for i in idxs:
                glVertex3fv(verts[i])
        glEnd()

class PlayerTank(Tank):
    def __init__(self, position, color):
        super().__init__(position, color)
        self.max_health = TANK_HEALTH * 3
        self.health = self.max_health

    def handle_input(self, keys, mouse_dx, mouse_dy, dt):
        if not self.alive: return
        self._shoot_timer = max(0.0, self._shoot_timer - dt)

        self.target_pitch = 0.0
        self.target_roll = 0.0

        # Direção e Rolagem (Centrífuga)
        if glfw.KEY_A in keys or glfw.KEY_LEFT in keys: 
            self.angle += TANK_ROT_SPEED * dt
            self.target_roll = -6.0  # Inclina pra direita ao virar à esquerda
        if glfw.KEY_D in keys or glfw.KEY_RIGHT in keys: 
            self.angle -= TANK_ROT_SPEED * dt
            self.target_roll = 6.0   # Inclina pra esquerda ao virar à direita

        fwd = self._forward()
        moved_dist = 0.0
        
        speed_mult = 1.5 if self.nitro_timer > 0 else 1.0
        actual_speed = TANK_SPEED * speed_mult
        
        # Aceleração e Mergulho (Pitch)
        if glfw.KEY_W in keys or glfw.KEY_UP in keys: 
            moved_dist = actual_speed * dt
            self._move(fwd * moved_dist)
            self.current_speed = actual_speed
            self.target_pitch = -3.0 # Acelera: frente levanta
        elif glfw.KEY_S in keys or glfw.KEY_DOWN in keys: 
            moved_dist = -actual_speed * dt
            self._move(fwd * moved_dist)
            self.current_speed = actual_speed
            self.target_pitch = 4.0  # Frea: frente afunda
        else:
            self.current_speed = 0.0

        self.wheel_angle -= moved_dist * 191.0 
        self.turret_angle -= mouse_dx * 0.25

    def _move(self, delta):
        nx, nz = self.pos[0] + delta[0], self.pos[2] + delta[2]
        limit = ARENA_SIZE - 1.2
        self.pos[0] = max(-limit, min(limit, nx))
        self.pos[2] = max(-limit, min(limit, nz))

class EnemyTank(Tank):
    def __init__(self, position, color):
        super().__init__(position, color)
        self._ai_shoot_timer = 0.0
        self.target = None

    def check_race_progress(self):
        if self.lap > MAX_LAPS: return
        next_cp = CHECKPOINTS[self.current_checkpoint]
        dx = self.pos[0] - next_cp[0]
        dz = self.pos[2] - next_cp[1]
        if math.hypot(dx, dz) < CHECKPOINT_RADIUS:
            self.current_checkpoint += 1
            if self.current_checkpoint >= len(CHECKPOINTS):
                self.current_checkpoint = 0
                self.lap += 1

    def update_ai(self, all_tanks: list, dt: float):
        if not self.alive: return
        self._shoot_timer    = max(0.0, self._shoot_timer - dt)
        self._ai_shoot_timer = max(0.0, self._ai_shoot_timer - dt)

        next_cp = CHECKPOINTS[self.current_checkpoint]
        target_angle_chassis = math.degrees(math.atan2(next_cp[0] - self.pos[0], next_cp[1] - self.pos[2]))
        diff_chassis = (target_angle_chassis - self.angle + 540) % 360 - 180
        
        max_rot = AI_ROT_SPEED * dt
        actual_rot = max(-max_rot, min(max_rot, diff_chassis))
        self.angle += actual_rot
        
        # IA também sofre força centrífuga (com proteção contra divisão por zero)
        if max_rot > 0.0:
            self.target_roll = -6.0 * (actual_rot / max_rot)
        else:
            self.target_roll = 0.0

        speed_mult = 1.5 if self.nitro_timer > 0 else 1.0
        current_speed = AI_MOVE_SPEED * speed_mult
        
        if abs(diff_chassis) > 40.0:
            current_speed *= 0.4  
            self.target_pitch = 3.0  # IA freando pra curva (frente abaixa)
        else:
            self.target_pitch = -3.0 # IA acelerando na reta (frente levanta)
            
        spd = current_speed * dt
        self.current_speed = current_speed
        
        self.wheel_angle -= spd * 191.0
        
        nx, nz = self.pos[0] + self._forward()[0] * spd, self.pos[2] + self._forward()[2] * spd
        limit = ARENA_SIZE - 1.2
        self.pos[0] = max(-limit, min(limit, nx))
        self.pos[2] = max(-limit, min(limit, nz))

        closest, min_dist = None, float('inf')
        for t in all_tanks:
            if t is not self and t.alive:
                dist = math.hypot(t.pos[0] - self.pos[0], t.pos[2] - self.pos[2])
                if dist < min_dist:
                    min_dist, closest = dist, t
                    
        self.target = closest
        if self.target:
            target_angle_turret = math.degrees(math.atan2(self.target.pos[0] - self.pos[0], self.target.pos[2] - self.pos[2]))
            diff_turret = (target_angle_turret - self.angle - self.turret_angle + 540) % 360 - 180
            self.turret_angle += max(-max_rot*2, min(max_rot*2, diff_turret))

    def try_shoot(self):
        if not self.alive or not self.target: return None
        dist = math.hypot(self.target.pos[0] - self.pos[0], self.target.pos[2] - self.pos[2])
        if dist < AI_SHOOT_RANGE and self._ai_shoot_timer <= 0:
            self._ai_shoot_timer = AI_SHOOT_COOLDOWN
            return self.shoot()
        return None