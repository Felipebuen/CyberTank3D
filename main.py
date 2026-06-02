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
from menu import MainMenu, EndScreen


# ─────────────────────────────────────────────────────────────
#  Power-ups
# ─────────────────────────────────────────────────────────────
class PowerUpManager:
    def __init__(self):
        self.items = [{'pos': p, 'active': True, 'angle': 0.0} for p in POWER_UPS]
        
    def update(self, dt, tanks):
        for item in self.items:
            if not item['active']: continue
            item['angle'] += 100 * dt
            for t in tanks:
                if t.alive and math.hypot(t.pos[0] - item['pos'][0], t.pos[2] - item['pos'][1]) < 2.5:
                    t.nitro_timer = 4.0
                    item['active'] = False
                    break
                    
    def draw(self):
        glDisable(GL_LIGHTING)
        for item in self.items:
            if not item['active']: continue
            glPushMatrix()
            y_float = 0.8 + math.sin(math.radians(item['angle'])) * 0.2
            glTranslatef(item['pos'][0], y_float, item['pos'][1])
            glRotatef(item['angle'], 0, 1, 0)
            glRotatef(45, 1, 0, 0)
            glColor3f(0.2, 1.0, 0.2)
            glScalef(0.6, 0.6, 0.6)
            Tank._draw_box()
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


# ─────────────────────────────────────────────────────────────
#  Calcula posição final do jogador na corrida
# ─────────────────────────────────────────────────────────────
def get_player_place(player, enemies):
    """
    Rankeia todos os tanques: mais voltas + mais checkpoints = melhor colocação.
    Retorna posição do jogador (1 = primeiro).
    """
    all_tanks = [player] + enemies

    def race_score(t):
        return (t.lap, t.current_checkpoint)

    ranking = sorted(all_tanks, key=race_score, reverse=True)
    for place, t in enumerate(ranking, start=1):
        if t is player:
            return place
    return len(all_tanks)


# ─────────────────────────────────────────────────────────────
#  Estado da corrida para calcular tempos de volta
# ─────────────────────────────────────────────────────────────
class LapTimer:
    def __init__(self):
        self._lap_start = time.time()
        self.lap_times  = []

    def lap_completed(self):
        now = time.time()
        self.lap_times.append(now - self._lap_start)
        self._lap_start = now


# ─────────────────────────────────────────────────────────────
#  Cria / reinicia objetos do jogo
# ─────────────────────────────────────────────────────────────
def create_game_objects(tex_mgr):
    arena = Arena(tex_mgr)
    start_pos = [CHECKPOINTS[0][0], 0.4, CHECKPOINTS[0][1]]
    player  = PlayerTank(position=[start_pos[0]-2, start_pos[1], start_pos[2]-2], color=PLAYER_COLOR)
    enemies = [
        EnemyTank(position=[start_pos[0]+2, start_pos[1], start_pos[2]+2], color=ENEMY_COLORS[0]),
        EnemyTank(position=[start_pos[0]-2, start_pos[1], start_pos[2]+2], color=ENEMY_COLORS[1]),
        EnemyTank(position=[start_pos[0]+2, start_pos[1], start_pos[2]-2], color=ENEMY_COLORS[2]),
    ]
    proj_mgr     = ProjectileManager()
    power_up_mgr = PowerUpManager()
    camera       = Camera()
    hud          = HUD(SCREEN_W, SCREEN_H)
    lap_timer    = LapTimer()
    return arena, player, enemies, proj_mgr, power_up_mgr, camera, hud, lap_timer


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
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

    # ── Máquina de estados: 'menu' | 'game' | 'end' ──
    STATE = 'menu'

    main_menu  = MainMenu(SCREEN_W, SCREEN_H)
    end_screen = None

    arena = player = enemies = proj_mgr = None
    power_up_mgr = camera = hud = lap_timer = None

    keys  = set()
    mouse = {"last_x": SCREEN_W // 2, "last_y": SCREEN_H // 2,
             "dx": 0.0, "dy": 0.0, "first": True}

    # ── Callbacks de teclado ──
    def key_cb(win, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, True)
            return

        if STATE == 'menu':
            if action == glfw.PRESS:
                main_menu.key_pressed(key)
            return

        if STATE == 'end':
            if action == glfw.PRESS:
                end_screen.key_pressed(key)
            return

        # STATE == 'game'
        if action == glfw.PRESS:
            keys.add(key)
            if key == glfw.KEY_SPACE:
                proj = player.shoot()
                if proj: proj_mgr.add(proj)
        if action == glfw.RELEASE:
            keys.discard(key)

    def cursor_cb(win, xpos, ypos):
        if mouse["first"]:
            mouse["last_x"], mouse["last_y"] = xpos, ypos
            mouse["first"] = False
        mouse["dx"] = xpos - mouse["last_x"]
        mouse["dy"] = mouse["last_y"] - ypos
        mouse["last_x"], mouse["last_y"] = xpos, ypos

    glfw.set_key_callback(window, key_cb)
    glfw.set_cursor_pos_callback(window, cursor_cb)

    prev_time = time.time()
    prev_lap  = 1   # rastreia troca de volta para lap timer

    while not glfw.window_should_close(window):
        now = time.time()
        dt  = min(now - prev_time, 0.05)
        prev_time = now

        glfw.poll_events()

        # ════════════════════════════════════════════
        #  MENU
        # ════════════════════════════════════════════
        if STATE == 'menu':
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Setup ortho para menu
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, SCREEN_W, 0, SCREEN_H)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            main_menu.draw(dt)
            glfw.swap_buffers(window)

            if main_menu.action == 'start':
                # Inicializa objetos do jogo
                arena, player, enemies, proj_mgr, power_up_mgr, camera, hud, lap_timer = \
                    create_game_objects(tex_mgr)
                prev_lap = 1
                mouse["first"] = True
                keys.clear()
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                STATE = 'game'
            elif main_menu.action == 'quit':
                break
            continue

        # ════════════════════════════════════════════
        #  END SCREEN
        # ════════════════════════════════════════════
        if STATE == 'end':
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluOrtho2D(0, SCREEN_W, 0, SCREEN_H)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            end_screen.draw(dt)
            glfw.swap_buffers(window)

            if end_screen.action == 'menu':
                # Volta ao menu e cria um novo menu zerado
                main_menu = MainMenu(SCREEN_W, SCREEN_H)
                end_screen = None
                STATE = 'menu'
            continue

        # ════════════════════════════════════════════
        #  JOGO
        # ════════════════════════════════════════════
        player.handle_input(keys, mouse["dx"], mouse["dy"], dt)
        player.check_race_progress()
        mouse["dx"] = mouse["dy"] = 0.0

        # Rastreia volta completada para o timer
        if player.lap > prev_lap and player.lap <= MAX_LAPS + 1:
            lap_timer.lap_completed()
            prev_lap = player.lap

        all_tanks = [player] + enemies

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

        # ── Verifica fim de corrida ──
        race_over   = False
        victory     = False

        if player.lap > MAX_LAPS:
            race_over = True
            victory   = True

        if not race_over:
            for enemy in enemies:
                if enemy.lap > MAX_LAPS:
                    race_over = True
                    victory   = False
                    break

        if race_over:
            place = get_player_place(player, enemies)
            end_screen = EndScreen(
                player_place = place,
                tank_color   = PLAYER_COLOR,
                lap_times    = lap_timer.lap_times,
                victory      = victory,
                w = SCREEN_W, h = SCREEN_H
            )
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            keys.clear()
            STATE = 'end'

    glfw.terminate()


if __name__ == "__main__":
    main()