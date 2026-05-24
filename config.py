"""
config.py – Constantes globais do CyberTank 3D
"""

# ── Janela ──────────────────────────────────────────────────────────────
SCREEN_W  = 1280
SCREEN_H  = 720
FOV       = 60.0
BG_COLOR  = (0.05, 0.05, 0.1, 1.0)   

# ── Arena ───────────────────────────────────────────────────────────────
ARENA_SIZE   = 45.0   
WALL_HEIGHT  = 3.0

# ── Corrida e Checkpoints (Formato baseado em Interlagos) ───────────────
MAX_LAPS = 3
CHECKPOINTS = [
    ( -10.0, -25.0), # START / Reta dos Boxes
    ( -30.0, -15.0), # Curva 1 (S do Senna)
    ( -25.0,  10.0), # Curva 2 / 3 (Curva do Sol)
    (  25.0,  25.0), # Curva 4 (Reta Oposta)
    (  15.0,  10.0), # Curva 5 (Descida do Lago)
    ( -15.0,   0.0), # Curva 6 / 7 (Ferradura)
    (  -5.0, -15.0), # Curva 8 / 9 (Laranjinha)
    (  15.0, -15.0), # Curva 10 (Pinheirinho)
    (  10.0,  -5.0), # Curva 11 (Bico de Pato)
    (  35.0,   5.0), # Curva 12 / 13 (Mergulho)
    (  30.0, -25.0), # Curva 14 (Junção)
    (   5.0, -30.0), # Curva 15 (Subida dos Boxes)
]
CHECKPOINT_RADIUS = 7.5 

# ── Obstáculos na Pista ─────────────────────────────────────────────────
OBSTACLES = [
    ((-20.0, -20.0), 1.5), 
    ((  0.0,  17.5), 1.8), 
    ((  0.0,   5.0), 1.5), 
    ((  5.0, -15.0), 1.5), 
    (( 32.5, -10.0), 1.8), 
]

# ── Power-Ups (Nitro) ───────────────────────────────────────────────────
POWER_UPS = [
    (-25.0,  -5.0), # Após o S do Senna
    ( 15.0,  25.0), # Na Reta Oposta
    ( 10.0, -15.0), # Antes do Bico de Pato
    ( 15.0, -25.0)  # Reta principal
]

# ── Tanque ──────────────────────────────────────────────────────────────
TANK_SPEED        = 10.0
TANK_ROT_SPEED    = 100.0
TURRET_ROT_SPEED  = 120.0
TANK_HEALTH       = 100
SHOOT_COOLDOWN    = 0.5

# ── Projétil ────────────────────────────────────────────────────────────
PROJ_SPEED   = 30.0
PROJ_DAMAGE  = 25
PROJ_LIFE    = 3.0

# ── Câmera terceira pessoa ───────────────────────────────────────────────
CAM_DISTANCE   = 10.0
CAM_HEIGHT     = 5.0
CAM_LAG        = 8.0

# ── Iluminação ──────────────────────────────────────────────────────────
AMBIENT_LIGHT   = (0.15, 0.15, 0.25, 1.0)
DIFFUSE_LIGHT   = (0.9,  0.9,  1.0,  1.0)
SUN_POSITION    = (10.0, 20.0, 10.0, 1.0)

# ── Cores ───────────────────────────────────────────────────────────────
PLAYER_COLOR    = (0.1, 0.8, 1.0)
ENEMY_COLORS    = [
    (1.0, 0.2, 0.1),
    (0.8, 0.1, 0.8),
    (1.0, 0.8, 0.1),
    (0.2, 1.0, 0.3)
]
PROJECTILE_COLOR= (1.0, 1.0, 0.0)
FLOOR_COLOR     = (0.1, 0.4, 0.1)    # Gramado
WALL_COLOR      = (0.1,  0.1,  0.3)
GRID_COLOR      = (0.05, 0.25, 0.05)
TRACK_COLOR     = (0.12, 0.12, 0.12) # Asfalto

# ── IA dos inimigos ──────────────────────────────────────────────────────
AI_SHOOT_RANGE  = 25.0
AI_MOVE_SPEED   = 8.0
AI_ROT_SPEED    = 150.0  
AI_SHOOT_COOLDOWN = 1.5