"""
menu.py – Menu Inicial e Tela Final Estilo Arcade Retrô (CyberTank 3D)

Renderização 2D pura via OpenGL ortográfico, usando apenas primitivas GL.
Estética: arcade dos anos 80/90 (scanlines, pixel font simulada, cores neon,
          blocos rígidos, animações com pisca-pisca e contador).
"""

import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from config import *


# ─────────────────────────────────────────────────────────────
#  Mini Pixel Font  (7×5, 0-9 + A-Z + : / !)
#  Cada caractere = lista de (col, lin) dos pixels acesos
# ─────────────────────────────────────────────────────────────
_GLYPHS = {
    '0': [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(0,3),(4,3),(1,4),(2,4),(3,4)],
    '1': [(2,0),(1,1),(2,1),(2,2),(2,3),(1,4),(2,4),(3,4)],
    '2': [(1,0),(2,0),(3,0),(4,1),(2,2),(3,2),(1,3),(1,4),(2,4),(3,4),(4,4)],
    '3': [(0,0),(1,0),(2,0),(3,0),(4,1),(2,2),(3,2),(4,3),(0,4),(1,4),(2,4),(3,4)],
    '4': [(0,0),(3,0),(0,1),(3,1),(0,2),(1,2),(2,2),(3,2),(4,2),(3,3),(3,4)],
    '5': [(0,0),(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(1,2),(2,2),(3,2),(4,3),(0,4),(1,4),(2,4),(3,4)],
    '6': [(1,0),(2,0),(3,0),(0,1),(0,2),(1,2),(2,2),(3,2),(0,3),(4,3),(1,4),(2,4),(3,4)],
    '7': [(0,0),(1,0),(2,0),(3,0),(4,0),(4,1),(3,2),(2,3),(2,4)],
    '8': [(1,0),(2,0),(3,0),(0,1),(4,1),(1,2),(2,2),(3,2),(0,3),(4,3),(1,4),(2,4),(3,4)],
    '9': [(1,0),(2,0),(3,0),(0,1),(4,1),(1,2),(2,2),(3,2),(4,2),(4,3),(1,4),(2,4),(3,4)],
    'A': [(2,0),(1,1),(3,1),(0,2),(4,2),(0,3),(1,3),(2,3),(3,3),(4,3),(0,4),(4,4)],
    'B': [(0,0),(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(1,2),(2,2),(3,2),(0,3),(4,3),(0,4),(1,4),(2,4),(3,4)],
    'C': [(1,0),(2,0),(3,0),(0,1),(0,2),(0,3),(1,4),(2,4),(3,4)],
    'D': [(0,0),(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(0,3),(4,3),(0,4),(1,4),(2,4),(3,4)],
    'E': [(0,0),(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(1,2),(2,2),(0,3),(0,4),(1,4),(2,4),(3,4),(4,4)],
    'F': [(0,0),(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(1,2),(2,2),(0,3),(0,4)],
    'G': [(1,0),(2,0),(3,0),(0,1),(0,2),(2,2),(3,2),(4,2),(0,3),(4,3),(1,4),(2,4),(3,4)],
    'H': [(0,0),(4,0),(0,1),(4,1),(0,2),(1,2),(2,2),(3,2),(4,2),(0,3),(4,3),(0,4),(4,4)],
    'I': [(1,0),(2,0),(3,0),(2,1),(2,2),(2,3),(1,4),(2,4),(3,4)],
    'J': [(3,0),(4,0),(3,1),(3,2),(0,3),(3,3),(1,4),(2,4),(3,4)],
    'K': [(0,0),(3,0),(0,1),(2,1),(0,2),(1,2),(0,3),(2,3),(0,4),(3,4),(4,4)],
    'L': [(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4),(3,4),(4,4)],
    'M': [(0,0),(4,0),(0,1),(1,1),(3,1),(4,1),(0,2),(2,2),(4,2),(0,3),(4,3),(0,4),(4,4)],
    'N': [(0,0),(4,0),(0,1),(1,1),(4,1),(0,2),(2,2),(4,2),(0,3),(3,3),(4,3),(0,4),(4,4)],
    'O': [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(0,3),(4,3),(1,4),(2,4),(3,4)],
    'P': [(0,0),(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(1,2),(2,2),(3,2),(0,3),(0,4)],
    'Q': [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(4,2),(0,3),(3,3),(4,3),(1,4),(2,4),(4,4)],
    'R': [(0,0),(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(1,2),(2,2),(3,2),(0,3),(3,3),(0,4),(4,4)],
    'S': [(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(1,2),(2,2),(3,2),(4,3),(0,4),(1,4),(2,4),(3,4)],
    'T': [(0,0),(1,0),(2,0),(3,0),(4,0),(2,1),(2,2),(2,3),(2,4)],
    'U': [(0,0),(4,0),(0,1),(4,1),(0,2),(4,2),(0,3),(4,3),(1,4),(2,4),(3,4)],
    'V': [(0,0),(4,0),(0,1),(4,1),(0,2),(4,2),(1,3),(3,3),(2,4)],
    'W': [(0,0),(4,0),(0,1),(4,1),(0,2),(2,2),(4,2),(0,3),(1,3),(3,3),(4,3),(0,4),(4,4)],
    'X': [(0,0),(4,0),(1,1),(3,1),(2,2),(1,3),(3,3),(0,4),(4,4)],
    'Y': [(0,0),(4,0),(1,1),(3,1),(2,2),(2,3),(2,4)],
    'Z': [(0,0),(1,0),(2,0),(3,0),(4,0),(3,1),(2,2),(1,3),(0,4),(1,4),(2,4),(3,4),(4,4)],
    ':': [(2,1),(2,3)],
    '/': [(4,0),(3,1),(2,2),(1,3),(0,4)],
    '!': [(2,0),(2,1),(2,2),(2,4)],
    ' ': [],
    '.': [(2,4)],
    '-': [(1,2),(2,2),(3,2)],
    '#': [(1,0),(3,0),(0,1),(1,1),(2,1),(3,1),(4,1),(1,2),(3,2),(0,3),(1,3),(2,3),(3,3),(4,3),(1,4),(3,4)],
    'ST': [],  # sentinel
}


def _draw_pixel_text(text, x, y, scale=2, color=(1,1,1)):
    """Desenha texto usando a mini pixel font."""
    glDisable(GL_LIGHTING)
    glColor3f(*color)
    cx = x
    char_w = 5 * scale
    char_h = 7 * scale
    gap = 2 * scale

    for ch in text.upper():
        glyph = _GLYPHS.get(ch, _GLYPHS[' '])
        for (col, row) in glyph:
            px = cx + col * scale
            py = y - row * scale
            glBegin(GL_QUADS)
            glVertex2f(px,          py)
            glVertex2f(px + scale,  py)
            glVertex2f(px + scale,  py - scale)
            glVertex2f(px,          py - scale)
            glEnd()
        cx += char_w + gap


def _text_width(text, scale=2):
    return len(text) * (5 * scale + 2 * scale)


def _rect(x, y, w, h):
    glBegin(GL_QUADS)
    glVertex2f(x,   y)
    glVertex2f(x+w, y)
    glVertex2f(x+w, y-h)
    glVertex2f(x,   y-h)
    glEnd()


def _rect_outline(x, y, w, h, thickness=2):
    # top
    glBegin(GL_QUADS)
    glVertex2f(x,   y);         glVertex2f(x+w, y)
    glVertex2f(x+w, y-thickness);glVertex2f(x,  y-thickness)
    glEnd()
    # bottom
    glBegin(GL_QUADS)
    glVertex2f(x,   y-h+thickness); glVertex2f(x+w, y-h+thickness)
    glVertex2f(x+w, y-h);           glVertex2f(x,   y-h)
    glEnd()
    # left
    glBegin(GL_QUADS)
    glVertex2f(x,          y);   glVertex2f(x+thickness, y)
    glVertex2f(x+thickness,y-h); glVertex2f(x,           y-h)
    glEnd()
    # right
    glBegin(GL_QUADS)
    glVertex2f(x+w-thickness, y);   glVertex2f(x+w, y)
    glVertex2f(x+w,           y-h); glVertex2f(x+w-thickness, y-h)
    glEnd()


def _enter_2d(w, h):
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()


def _leave_2d():
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)


# ─────────────────────────────────────────────────────────────
#  SCANLINE overlay (efeito CRT)
# ─────────────────────────────────────────────────────────────
def _draw_scanlines(w, h):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0, 0, 0, 0.18)
    y = 0
    while y < h:
        glBegin(GL_QUADS)
        glVertex2f(0, y+1); glVertex2f(w, y+1)
        glVertex2f(w, y);   glVertex2f(0, y)
        glEnd()
        y += 3
    glDisable(GL_BLEND)


# ─────────────────────────────────────────────────────────────
#  Estrelas de fundo (parallax simples)
# ─────────────────────────────────────────────────────────────
import random
random.seed(42)
_STARS = [(random.randint(0, SCREEN_W), random.randint(0, SCREEN_H),
           random.random() * 0.8 + 0.2) for _ in range(120)]


def _draw_stars(t):
    glDisable(GL_LIGHTING)
    for i, (sx, sy, bri) in enumerate(_STARS):
        flicker = 0.6 + 0.4 * math.sin(t * 3.0 + i)
        glColor3f(bri * flicker, bri * flicker, bri * flicker)
        sz = 1 + int(bri * 2)
        _rect(sx, sy, sz, sz)


# ─────────────────────────────────────────────────────────────
#  Silhueta do tanque em 2D (decorativa)
# ─────────────────────────────────────────────────────────────
def _draw_tank_silhouette(cx, cy, scale=1.0, color=(0.1, 0.8, 1.0), alpha=1.0):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(*color, alpha)

    def sq(x, y, w, h):
        _rect(cx + x*scale, cy + y*scale, w*scale, h*scale)

    # Corpo
    sq(-20, -8, 40, 16)
    # Torre
    sq(-12, 8, 24, 14)
    # Canhão
    sq(-3, 22, 6, 20)
    # Rodas (4)
    for wx in [-22, -10, 4, 16]:
        sq(wx, -14, 10, 6)

    glDisable(GL_BLEND)


# ─────────────────────────────────────────────────────────────
#  MENU PRINCIPAL
# ─────────────────────────────────────────────────────────────
class MainMenu:
    """
    Retorna 'start' quando o jogador pressionar ENTER/espaço.
    Chame draw() a cada frame e key_pressed() nos callbacks de teclado.
    """

    def __init__(self, w=SCREEN_W, h=SCREEN_H):
        self.w = w
        self.h = h
        self._t0 = time.time()
        self._option = 0          # 0 = INICIAR, 1 = SAIR
        self._done = False
        self._action = None       # 'start' | 'quit'
        self._flicker = True
        self._road_offset = 0.0
        self._tank_x = -80.0
        self._entered_flash = 0.0

    def key_pressed(self, key):
        import glfw
        if key == glfw.KEY_UP or key == glfw.KEY_W:
            self._option = (self._option - 1) % 2
        elif key == glfw.KEY_DOWN or key == glfw.KEY_S:
            self._option = (self._option + 1) % 2
        elif key in (glfw.KEY_ENTER, glfw.KEY_SPACE, glfw.KEY_KP_ENTER):
            self._entered_flash = 0.25
            if self._option == 0:
                self._action = 'start'
            else:
                self._action = 'quit'

    @property
    def action(self):
        return self._action

    def draw(self, dt):
        t = time.time() - self._t0
        self._road_offset = (self._road_offset + dt * 80) % 40
        self._tank_x += dt * 60
        if self._tank_x > self.w + 100:
            self._tank_x = -80

        if self._entered_flash > 0:
            self._entered_flash -= dt

        _enter_2d(self.w, self.h)

        # ── Fundo escuro ──
        glColor3f(0.02, 0.02, 0.08)
        _rect(0, self.h, self.w, self.h)

        _draw_stars(t)

        # ── Estrada retrô (perspectiva falsa) ──
        self._draw_road(t)

        # ── Tanque voando ──
        _draw_tank_silhouette(
            int(self._tank_x), self.h // 2 - 30,
            scale=0.8,
            color=(0.1, 0.8, 1.0),
            alpha=0.35
        )

        # ── Painel central ──
        pw, ph = 540, 340
        px = (self.w - pw) // 2
        py = self.h - (self.h - ph) // 2

        # Sombra do painel
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.7)
        _rect(px + 6, py - 6, pw, ph)
        glDisable(GL_BLEND)

        # Painel
        glColor3f(0.04, 0.04, 0.15)
        _rect(px, py, pw, ph)

        # Borda dupla neon amarela/branca
        glColor3f(1.0, 0.9, 0.0)
        _rect_outline(px, py, pw, ph, thickness=3)
        glColor3f(0.6, 0.5, 0.0)
        _rect_outline(px+6, py-6, pw-12, ph-12, thickness=1)

        # ── TÍTULO ──
        title = "CYBERTANK 3D"
        ts = 5
        tw = _text_width(title, ts)
        tx = (self.w - tw) // 2
        ty = py - 28

        # Sombra do título
        _draw_pixel_text(title, tx+3, ty-3, scale=ts, color=(0.5, 0.3, 0.0))
        # Brilho animado
        bri = 0.8 + 0.2 * math.sin(t * 4)
        _draw_pixel_text(title, tx, ty, scale=ts, color=(1.0, bri*0.9, 0.0))

        # Subtítulo
        sub = "DEATH RACE"
        ss = 3
        sw = _text_width(sub, ss)
        sx = (self.w - sw) // 2
        _draw_pixel_text(sub, sx, py - 80, scale=ss, color=(0.2, 1.0, 1.0))

        # Linha separadora
        glColor3f(0.3, 0.3, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(px+20, py-108); glVertex2f(px+pw-20, py-108)
        glVertex2f(px+pw-20, py-106); glVertex2f(px+20, py-106)
        glEnd()

        # ── Opções ──
        options = ["INICIAR CORRIDA", "SAIR"]
        oy_start = py - 145

        for i, opt in enumerate(options):
            oy = oy_start - i * 65
            os_ = 3
            ow = _text_width(opt, os_)
            ox = (self.w - ow) // 2

            selected = (i == self._option)

            if selected:
                # Fundo da opção selecionada
                flash = self._entered_flash > 0
                bg_col = (0.9, 0.8, 0.0) if flash else (0.15, 0.15, 0.35)
                glColor3f(*bg_col)
                _rect(ox - 18, oy + 4, ow + 36, os_ * 7 + 10)

                # Setas piscando
                arrow_blink = int(t * 4) % 2 == 0
                a_col = (1.0, 1.0, 0.0) if arrow_blink else (0.6, 0.6, 0.0)
                _draw_pixel_text(">", ox - 15, oy, scale=os_, color=a_col)
                _draw_pixel_text("<", ox + ow + 5, oy, scale=os_, color=a_col)

                txt_col = (0.0, 0.0, 0.0) if flash else (1.0, 1.0, 0.0)
            else:
                txt_col = (0.4, 0.4, 0.6)

            _draw_pixel_text(opt, ox, oy, scale=os_, color=txt_col)

        # ── Instruções ──
        inst_y = py - ph + 36
        inst = "W/S:MOVER  ENTER:CONFIRMAR"
        iw = _text_width(inst, 1)
        ix = (self.w - iw) // 2
        alpha_inst = 0.5 + 0.5 * math.sin(t * 2)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.5, 0.5, 0.7, alpha_inst)
        _draw_pixel_text(inst, ix, inst_y, scale=1, color=(0.5, 0.5, 0.7))
        glDisable(GL_BLEND)

        # ── Copyright ──
        copy = "INSERT COIN  (C) 2025"
        cw = _text_width(copy, 1)
        blink = int(t * 1.5) % 2 == 0
        if blink:
            _draw_pixel_text(copy, (self.w - cw)//2, 22, scale=1, color=(0.3, 0.3, 0.5))

        _draw_scanlines(self.w, self.h)
        _leave_2d()

    def _draw_road(self, t):
        """Estrada com perspectiva falsa deslocando para baixo."""
        ry = self.h // 2 - 80
        horizon = ry + 60

        # Céu gradient
        glBegin(GL_QUADS)
        glColor3f(0.02, 0.02, 0.12); glVertex2f(0, self.h)
        glColor3f(0.02, 0.02, 0.12); glVertex2f(self.w, self.h)
        glColor3f(0.05, 0.02, 0.20); glVertex2f(self.w, horizon)
        glColor3f(0.05, 0.02, 0.20); glVertex2f(0, horizon)
        glEnd()

        # Pista
        road_w_bot = self.w
        road_w_top = 100
        cx = self.w // 2

        glBegin(GL_QUADS)
        glColor3f(0.12, 0.12, 0.12)
        glVertex2f(cx - road_w_bot//2, ry - 30)
        glVertex2f(cx + road_w_bot//2, ry - 30)
        glColor3f(0.08, 0.08, 0.08)
        glVertex2f(cx + road_w_top//2, horizon)
        glVertex2f(cx - road_w_top//2, horizon)
        glEnd()

        # Listras tracejadas (animadas)
        num_strips = 8
        for i in range(num_strips + 1):
            pct = (i / num_strips + (self._road_offset / (self.h // 2))) % 1.0
            # perspectiva: y varia de horizon a ry-30
            strip_y = horizon + pct * (ry - 30 - horizon)
            # largura da faixa na perspectiva
            strip_w = road_w_top + pct * (road_w_bot - road_w_top)
            left = cx - strip_w // 2
            right = cx + strip_w // 2
            center_l = cx - strip_w * 0.08
            center_r = cx + strip_w * 0.08
            h_stripe = max(2, int(pct * 8))

            glColor3f(0.9, 0.9, 0.9)
            glBegin(GL_QUADS)
            glVertex2f(center_l, strip_y)
            glVertex2f(center_r, strip_y)
            glVertex2f(center_r, strip_y - h_stripe)
            glVertex2f(center_l, strip_y - h_stripe)
            glEnd()

            # Bordas verdes
            bord = max(1, int(pct * 4))
            glColor3f(0.1, 0.7, 0.1)
            glBegin(GL_QUADS)
            glVertex2f(left,      strip_y)
            glVertex2f(left+bord, strip_y)
            glVertex2f(left+bord, strip_y-h_stripe)
            glVertex2f(left,      strip_y-h_stripe)
            glEnd()
            glBegin(GL_QUADS)
            glVertex2f(right-bord, strip_y)
            glVertex2f(right,      strip_y)
            glVertex2f(right,      strip_y-h_stripe)
            glVertex2f(right-bord, strip_y-h_stripe)
            glEnd()


# ─────────────────────────────────────────────────────────────
#  TELA FINAL  (Podium / Resultados)
# ─────────────────────────────────────────────────────────────

_TROPHIES = {
    1: (1.0, 0.85, 0.0),   # Ouro
    2: (0.8, 0.8, 0.85),   # Prata
    3: (0.8, 0.5, 0.2),    # Bronze
}

_PLACE_LABEL = {1: "1ST", 2: "2ND", 3: "3RD", 4: "4TH"}
_PLACE_MSG   = {
    1: "VENCEDOR!",
    2: "2  LUGAR",
    3: "3  LUGAR",
    4: "ULTIMO LUGAR!",
}


def _draw_podium(cx, base_y, place, tank_color, name, scale=1.0):
    """
    Desenha bloco do podio crescendo PARA CIMA a partir de base_y.
    _rect(x, y, w, h) em coordenadas Y-up: topo=y, base=y-h.
    Para um bloco com base em base_y e altura h: _rect(bx, base_y+h, w, h).
    """
    heights = {1: 80, 2: 55, 3: 38, 4: 22}
    h  = int(heights.get(place, 20) * scale)
    w  = int(70 * scale)
    bx = cx - w // 2
    block_top = base_y + h   # coordenada Y do topo do bloco

    podium_color = _TROPHIES.get(place, (0.3, 0.3, 0.35))

    # Sombra
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0, 0, 0, 0.30)
    _rect(bx + 5, block_top - 5, w, h)
    glDisable(GL_BLEND)

    # Bloco principal
    glColor3f(*podium_color)
    _rect(bx, block_top, w, h)

    # Borda brilhante
    glColor3f(min(1, podium_color[0]*1.5),
              min(1, podium_color[1]*1.5),
              min(1, podium_color[2]*1.5))
    _rect_outline(bx, block_top, w, h, 2)

    # Numero da posicao centralizado no bloco
    pos_s = max(2, int(3 * scale))
    pos_label = str(place)
    plw = _text_width(pos_label, pos_s)
    num_y = base_y + h // 2 + (pos_s * 7) // 2
    _draw_pixel_text(pos_label, cx - plw // 2, num_y, scale=pos_s, color=(0, 0, 0))

    # Tanque em cima do bloco
    tank_margin = int(55 * scale)
    tank_y = block_top + tank_margin
    _draw_tank_silhouette(cx, tank_y, scale=0.55 * scale, color=tank_color, alpha=0.95)

    # Nome acima do tanque
    ns = max(1, int(2 * scale))
    nw = _text_width(name, ns)
    name_y = tank_y + int(52 * scale)
    _draw_pixel_text(name, cx - nw // 2, name_y, scale=ns, color=(0.9, 0.9, 0.9))


class EndScreen:
    """
    Tela de resultados estilo arcade.

    Parâmetros:
        player_place  – posição final do jogador (1-4)
        tank_color    – cor RGB do tanque do jogador
        lap_times     – lista de floats com o tempo de cada volta (opcional)
        victory       – True se o jogador ganhou (place == 1)
    """

    def __init__(self, player_place: int, tank_color=(0.1, 0.8, 1.0),
                 lap_times=None, victory=True, w=SCREEN_W, h=SCREEN_H):
        self.w = w
        self.h = h
        self.player_place = player_place
        self.tank_color   = tank_color
        self.lap_times    = lap_times or []
        self.victory      = victory
        self._t0    = time.time()
        self._done  = False
        self._action = None
        self._reveal = 0.0    # 0..1 anima entrada do painel
        self._confetti = self._gen_confetti() if victory else []

    # ── Confete (somente vitória) ──────────────────────────
    def _gen_confetti(self):
        rng = random.Random(7)
        items = []
        for _ in range(80):
            items.append({
                'x': rng.randint(0, self.w),
                'y': rng.randint(0, self.h),
                'vy': rng.uniform(30, 80),
                'vx': rng.uniform(-20, 20),
                'color': (rng.random(), rng.random(), rng.random()),
                'size': rng.randint(4, 10),
                'angle': rng.random() * 360,
                'spin':  rng.uniform(-200, 200),
            })
        return items

    def _update_confetti(self, dt):
        for c in self._confetti:
            c['y'] -= c['vy'] * dt
            c['x'] += c['vx'] * dt
            c['angle'] += c['spin'] * dt
            if c['y'] < 0:
                c['y'] = self.h + 10
                c['x'] = random.randint(0, self.w)

    def key_pressed(self, key):
        import glfw
        if key in (glfw.KEY_ENTER, glfw.KEY_SPACE, glfw.KEY_ESCAPE, glfw.KEY_KP_ENTER):
            self._action = 'menu'

    @property
    def action(self):
        return self._action

    def draw(self, dt):
        t = time.time() - self._t0
        self._reveal = min(1.0, self._reveal + dt * 2.5)

        if self.victory:
            self._update_confetti(dt)

        _enter_2d(self.w, self.h)

        # ── Fundo ──
        if self.victory:
            r = 0.03 + 0.02 * math.sin(t * 1.5)
            g = 0.03 + 0.02 * math.sin(t * 1.7)
            b = 0.10
        else:
            r = 0.06 + 0.02 * math.sin(t)
            g = 0.01
            b = 0.02

        glColor3f(r, g, b)
        _rect(0, self.h, self.w, self.h)

        _draw_stars(t)

        # ── Confete ──
        for c in self._confetti:
            glColor3f(*c['color'])
            _rect(int(c['x']), int(c['y']), c['size'], c['size'])

        # ── Layout geral ──
        # Coordenadas: Y=0 base, Y=h topo. _rect(x,y,w,h) desenha de y PARA CIMA.
        #
        #  h ┌─────────────────────────────┐
        #    │  título / colocação          │  zona superior  (h-60 .. h)
        #    │  painel azul escuro          │
        #    │    blocos do pódio           │  zona do pódio  (220 .. h-120)
        #    │    tanques + nomes           │
        #    │  linha vermelha              │  base_line = 220
        #    │  tempos de volta             │  zona inferior  (60 .. 220)
        #  0 └─────────────────────────────┘  "PRESSIONE ENTER"

        pad       = 40
        base_line = 220   # linha vermelha / base dos blocos do pódio
        top_zone  = self.h - 60  # topo do painel interno

        # Dados dos 4 participantes (player na posição correta, inimigos nos outros)
        all_colors = [None] * 4
        all_names  = [None] * 4
        all_colors[self.player_place - 1] = self.tank_color
        all_names [self.player_place - 1] = "PLAYER"
        enemy_names = ["ENEMY1", "ENEMY2", "ENEMY3"]
        ei = 0
        for i in range(4):
            if all_colors[i] is None:
                all_colors[i] = ENEMY_COLORS[ei % len(ENEMY_COLORS)]
                all_names [i] = enemy_names[ei]
                ei += 1

        bord_col = (1.0, 0.9, 0.0) if self.victory else (0.8, 0.1, 0.1)

        reveal_y = int((1.0 - self._reveal) * -self.h)
        glPushMatrix()
        glTranslatef(0, reveal_y, 0)

        # ── Painel de fundo (cobre zona do pódio e superior) ──
        panel_h = self.h - base_line + 40   # de base_line-20 até topo
        glColor3f(0.04, 0.04, 0.14)
        _rect(pad, base_line - 20, self.w - pad*2, panel_h)

        glColor3f(*bord_col)
        _rect_outline(pad, base_line - 20, self.w - pad*2, panel_h, 3)

        # ── Linha vermelha (chão do pódio) ──
        glColor3f(0.9, 0.05, 0.05)
        _rect(pad, base_line, self.w - pad*2, 4)

        # ── Pódios ──
        # Ordens visuais clássicas: 2, 1, 3, 4
        visual_order = [2, 1, 3, 4]
        n_slots = 4
        slot_w = self.w // (n_slots + 1)

        for vi, place in enumerate(visual_order):
            cx = slot_w * (vi + 1)
            tank_col = all_colors[place - 1]
            name     = all_names [place - 1]
            _draw_podium(cx, base_line, place, tank_col, name, scale=0.9)

        # ── Título / Mensagem (topo do painel) ──
        main_msg = _PLACE_MSG.get(self.player_place, "FIM DE JOGO")
        ms = 5
        mw = _text_width(main_msg, ms)
        mx = (self.w - mw) // 2
        title_y = self.h - pad - 10

        pulse = 0.85 + 0.15 * math.sin(t * 5)
        if self.victory:
            tc = (1.0, pulse * 0.9, 0.0)
        else:
            tc = (pulse, 0.1, 0.1)

        _draw_pixel_text(main_msg, mx + 3, title_y - 3, scale=ms, color=(0.2, 0.2, 0.0))
        _draw_pixel_text(main_msg, mx, title_y, scale=ms, color=tc)

        # ── Posição do jogador (abaixo do título) ──
        place_label = _PLACE_LABEL.get(self.player_place, f"{self.player_place}TH")
        ps = 4
        pw_l = _text_width(place_label, ps)
        px_l = (self.w - pw_l) // 2
        py_l = self.h - pad - 60

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glow = 0.4 + 0.2 * math.sin(t * 6)
        glColor4f(*bord_col, glow * 0.25)
        _rect(px_l - 16, py_l - ps*7 - 8, pw_l + 32, ps*7 + 16)
        glDisable(GL_BLEND)

        _draw_pixel_text(place_label, px_l + 2, py_l - 2, scale=ps, color=(0.3, 0.2, 0.0))
        _draw_pixel_text(place_label, px_l, py_l, scale=ps, color=bord_col)

        # ── Tempos de volta (abaixo da linha vermelha) ──
        if self.lap_times:
            lt_y = base_line - 30
            lt_x = pad + 20
            _draw_pixel_text("TEMPOS:", lt_x, lt_y, scale=2, color=(0.6, 0.6, 1.0))
            for i, lt in enumerate(self.lap_times[:MAX_LAPS]):
                mins = int(lt) // 60
                secs = int(lt) % 60
                cent = int((lt - int(lt)) * 100)
                label = f"V{i+1}: {mins:01d}:{secs:02d}:{cent:02d}"
                _draw_pixel_text(label, lt_x + 110 + i*220, lt_y, scale=2,
                                 color=(0.9, 0.9, 0.5))

        glPopMatrix()

        # ── "PRESSIONE ENTER" piscando ──
        blink = int(t * 2) % 2 == 0
        if blink:
            press_txt = "PRESSIONE ENTER PARA CONTINUAR"
            ptw = _text_width(press_txt, 2)
            _draw_pixel_text(press_txt, (self.w - ptw)//2, 30, scale=2,
                             color=(0.6, 0.6, 0.8))

        _draw_scanlines(self.w, self.h)
        _leave_2d()