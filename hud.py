"""
hud.py – Interface 2D (HUD) do CyberTank 3D
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from config import *
from tank import PlayerTank


class HUD:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h

    def draw(self, player, enemies, proj_mgr):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.w, 0, self.h)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # ── HP do jogador (Canto Superior Esquerdo) ──
        max_hp = getattr(player, 'max_health', TANK_HEALTH)
        self._draw_bar(20, self.h - 40, 200, 20,
                       player.health / max_hp,
                       (0.1, 0.9, 0.3))

        # ── Velocímetro (Canto Inferior Direito) ──
        speed_pct = player.current_speed / (TANK_SPEED * 1.5) # Calcula percentual com base na Vel. Máx com Nitro
        vel_y = 20
        vel_x = self.w - 220
        self._draw_bar(vel_x, vel_y, 200, 20, speed_pct, (0.0, 0.8, 1.0))
        
        # Alerta visual se estiver no Nitro
        if player.nitro_timer > 0:
            glColor3f(0.2, 1.0, 0.2) # Verde Neon
            self._rect(vel_x, vel_y + 25, 200, 5)

        # ── Número de Voltas (Lap) ──
        lap_y = self.h - 80
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glVertex2f(20, lap_y + 20)
        glVertex2f(20, lap_y)
        glVertex2f(20, lap_y)
        glVertex2f(32, lap_y)
        glEnd()
        
        glColor3f(1.0, 0.8, 0.0)
        volta_atual = min(player.lap, MAX_LAPS)
        self._draw_digit(45, lap_y, 15, 20, volta_atual)

        # ── Progresso de Checkpoints ──
        cp_w, cp_spacing = 15, 5
        cp_y = lap_y - 20
        for i in range(len(CHECKPOINTS)):
            if i < player.current_checkpoint:
                glColor3f(0.0, 1.0, 0.0) 
            else:
                glColor3f(0.3, 0.3, 0.3) 
            self._rect(20 + i * (cp_w + cp_spacing), cp_y, cp_w, 8)

        # ── MINIMAPA (Canto Superior Direito) ──
        self._draw_minimap([player] + enemies)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

    def _draw_minimap(self, tanks):
        map_size = 140
        mx = self.w - map_size - 20
        my = self.h - map_size - 20
        
        # Fundo semitransparente
        glColor4f(0.0, 0.0, 0.0, 0.6)
        glEnable(GL_BLEND)
        self._rect(mx, my, map_size, map_size)
        glDisable(GL_BLEND)
        
        # Desenha a pista (linhas interligando os checkpoints)
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for cp in CHECKPOINTS:
            # Mapeia as posições 3D do mundo (-45 a 45) para a tela 2D (0 a map_size)
            px = mx + (cp[0] + ARENA_SIZE) / (ARENA_SIZE * 2) * map_size
            pz = my + (cp[1] + ARENA_SIZE) / (ARENA_SIZE * 2) * map_size
            glVertex2f(px, pz)
        glEnd()
        glLineWidth(1.0)
        
        # Desenha os Tanques
        for t in tanks:
            if not t.alive: continue
            px = mx + (t.pos[0] + ARENA_SIZE) / (ARENA_SIZE * 2) * map_size
            pz = my + (t.pos[2] + ARENA_SIZE) / (ARENA_SIZE * 2) * map_size
            
            if isinstance(t, PlayerTank):
                glColor3f(0.1, 0.8, 1.0) # Azul (Você)
                self._rect(px - 3, pz - 3, 6, 6)
            else:
                glColor3f(1.0, 0.0, 0.0) # Vermelho (Inimigos)
                self._rect(px - 2, pz - 2, 4, 4)

    def _draw_bar(self, x, y, w, h, pct, color):
        glColor4f(0.1, 0.1, 0.1, 0.7)
        self._rect(x, y, w, h)
        glColor3f(*color)
        self._rect(x + 1, y + 1, int((w - 2) * max(0, pct)), h - 2)
        glColor3f(0.8, 0.8, 0.8)
        self._rect_outline(x, y, w, h)

    def _draw_digit(self, x, y, w, h, num):
        segments = {
            0: [0, 1, 2, 3, 4, 5], 1: [1, 2], 2: [0, 1, 6, 4, 3],
            3: [0, 1, 6, 2, 3], 4: [5, 6, 1, 2], 5: [0, 5, 6, 2, 3],
            6: [0, 5, 4, 3, 2, 6], 7: [0, 1, 2], 8: [0, 1, 2, 3, 4, 5, 6],
            9: [0, 1, 2, 3, 5, 6]
        }
        segs = segments.get(num % 10, [])
        glBegin(GL_LINES)
        if 0 in segs: glVertex2f(x, y+h); glVertex2f(x+w, y+h)
        if 1 in segs: glVertex2f(x+w, y+h); glVertex2f(x+w, y+h/2)
        if 2 in segs: glVertex2f(x+w, y+h/2); glVertex2f(x+w, y)
        if 3 in segs: glVertex2f(x, y); glVertex2f(x+w, y)
        if 4 in segs: glVertex2f(x, y+h/2); glVertex2f(x, y)
        if 5 in segs: glVertex2f(x, y+h); glVertex2f(x, y+h/2)
        if 6 in segs: glVertex2f(x, y+h/2); glVertex2f(x+w, y+h/2)
        glEnd()

    @staticmethod
    def _rect(x, y, w, h):
        glBegin(GL_QUADS)
        glVertex2f(x, y); glVertex2f(x + w, y)
        glVertex2f(x + w, y + h); glVertex2f(x, y + h)
        glEnd()

    @staticmethod
    def _rect_outline(x, y, w, h):
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y); glVertex2f(x + w, y)
        glVertex2f(x + w, y + h); glVertex2f(x, y + h)
        glEnd()