"""
CyberTank 3D - Jogo de Combate de Tanques em Arena
"""

import sys
import math
import time

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from config import *
from arena import Arena
from tank import Tank, PlayerTank, EnemyTank
from projectile import ProjectileManager
from lighting import setup_lighting, update_dynamic_lights
from camera import Camera
from hud import HUD
from texture_manager import TextureManager


class PowerUpManager:
    def __init__(self):
        self.items = [{'pos': p, 'active': True, 'angle': 0.0} for p in POWER_UPS]
        
    def update(self, dt, tanks):
        for item in self.items:
            if not item['active']: continue
            
            item['angle'] += 100 * dt # Gira o cubo
            
            # Checa colisão com tanques
            for t in tanks:
                if t.alive and math.hypot(t.pos[0] - item['pos'][0], t.pos[2] - item['pos'][1]) < 2.5:
                    t.nitro_timer = 4.0 # 4 Segundos de Nitro!
                    item['active'] = False
                    break
                    
    def draw(self):
        glDisable(GL_LIGHTING)
        for item in self.items:
            if not item['active']: continue
            
            glPushMatrix()
            # Flutua para cima e para baixo usando Seno
            y_float = 0.8 + math.sin(math.radians(item['angle'])) * 0.2
            glTranslatef(item['pos'][0], y_float, item['pos'][1])
            
            glRotatef(item['angle'], 0, 1, 0) # Gira
            glRotatef(45, 1, 0, 0)            # Fica inclinado
            
            glColor3f(0.2, 1.0, 0.2) # Verde Neon
            glScalef(0.6, 0.6, 0.6)
            Tank._draw_box() # Reutiliza a função da caixa do Tank!
            glPopMatrix()
            
        glEnable(GL_LIGHTING)


def resolve_tank_collisions(tanks):
    collision_radius = 1.3 
    
    for i in range(len(tanks)):
        for j in range(i + 1, len(tanks)):
            t1, t2 = tanks[i], tanks[j]
            if not t1.alive or not t2.alive: continue

            dx, dz = t2.pos[0] - t1.pos[0], t2.pos[2] - t1.pos[2]
            dist = math.hypot(dx, dz)
            min_dist = collision_radius * 2

            if dist < min_dist and dist > 0.001:
                overlap = min_dist - dist
                nx, nz = dx / dist, dz / dist
                push_amount = overlap / 2.0
                t1.pos[0] -= nx * push_amount
                t1.pos[2] -= nz * push_amount
                t2.pos[0] += nx * push_amount
                t2.pos[2] += nz * push_amount

    for t in tanks:
        if not t.alive: continue
        for (ox, oz), r in OBSTACLES:
            dx = t.pos[0] - ox
            dz = t.pos[2] - oz
            dist = math.hypot(dx, dz)
            min_dist = r + collision_radius - 0.2
            
            if dist < min_dist and dist > 0.001:
                overlap = min_dist - dist
                nx, nz = dx / dist, dz / dist
                t.pos[0] += nx * overlap
                t.pos[2] += nz * overlap


def main():
    if not glfw.init():
        sys.exit("Falha ao inicializar GLFW")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.SAMPLES, 4)

    window = glfw.create_window(SCREEN_W, SCREEN_H, "CyberTank 3D - Death Race", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Falha ao criar janela GLFW")

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)
    glEnable(GL_MULTISAMPLE)
    glShadeModel(GL_SMOOTH)
    glClearColor(*BG_COLOR)

    tex_mgr = TextureManager()
    arena   = Arena(tex_mgr)
    
    start_pos = [CHECKPOINTS[0][0], 0.4, CHECKPOINTS[0][1]]
    
    player  = PlayerTank(position=[start_pos[0]-2, start_pos[1], start_pos[2]-2], color=PLAYER_COLOR)
    enemies = [
        EnemyTank(position=[start_pos[0]+2, start_pos[1], start_pos[2]+2], color=ENEMY_COLORS[0]),
        EnemyTank(position=[start_pos[0]-2, start_pos[1], start_pos[2]+2], color=ENEMY_COLORS[1]),
        EnemyTank(position=[start_pos[0]+2, start_pos[1], start_pos[2]-2], color=ENEMY_COLORS[2]),
    ]
    
    proj_mgr = ProjectileManager()
    power_up_mgr = PowerUpManager()
    camera   = Camera()
    hud      = HUD(SCREEN_W, SCREEN_H)

    keys   = set()
    mouse  = {"last_x": SCREEN_W // 2, "last_y": SCREEN_H // 2, "dx": 0.0, "dy": 0.0, "first": True}

    def key_cb(win, key, scancode, action, mods):
        if action == glfw.PRESS:
            keys.add(key)
            if key == glfw.KEY_SPACE:
                proj = player.shoot()
                if proj: proj_mgr.add(proj)
        if action == glfw.RELEASE: keys.discard(key)
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, True)

    def cursor_cb(win, xpos, ypos):
        if mouse["first"]:
            mouse["last_x"], mouse["last_y"] = xpos, ypos
            mouse["first"] = False
        mouse["dx"] = xpos - mouse["last_x"]
        mouse["dy"] = mouse["last_y"] - ypos
        mouse["last_x"], mouse["last_y"] = xpos, ypos

    glfw.set_key_callback(window, key_cb)
    glfw.set_cursor_pos_callback(window, cursor_cb)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    prev_time = time.time()

    while not glfw.window_should_close(window):
        now  = time.time()
        dt   = min(now - prev_time, 0.05)
        prev_time = now

        glfw.poll_events()

        player.handle_input(keys, mouse["dx"], mouse["dy"], dt)
        player.check_race_progress()
        mouse["dx"] = mouse["dy"] = 0.0

        all_tanks = [player] + enemies
        
        # Atualiza a IA e aplica os efeitos novos (recuo, fumaça, timer do nitro)
        for t in all_tanks:
            if isinstance(t, EnemyTank):
                t.update_ai(all_tanks, dt)
                t.check_race_progress()
                shot = t.try_shoot()
                if shot: proj_mgr.add(shot)
            
            t.update_effects(dt)

        proj_mgr.update(dt, arena, all_tanks)
        power_up_mgr.update(dt, all_tanks)
        resolve_tank_collisions(all_tanks)
        camera.follow(player, dt)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, SCREEN_W / SCREEN_H, 0.1, 200.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        camera.apply()

        setup_lighting()
        update_dynamic_lights(proj_mgr.projectiles)

        arena.draw()
        power_up_mgr.draw()
        for t in all_tanks: t.draw()
        proj_mgr.draw()
        
        hud.draw(player, enemies, proj_mgr)

        glfw.swap_buffers(window)

        if player.lap > MAX_LAPS:
            print("VITÓRIA – Você completou a corrida em 1º lugar!")
            time.sleep(3)
            break
            
        for enemy in enemies:
            if enemy.lap > MAX_LAPS:
                print("GAME OVER – Um inimigo venceu a corrida!")
                time.sleep(3)
                break

    glfw.terminate()

if __name__ == "__main__":
    main()