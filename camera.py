"""
camera.py – Câmera em Terceira Pessoa com Interpolação Linear

Conceitos de CG aplicados:
  • gluLookAt para definição da view matrix
  • Lerp suave para eliminar jitter (câmera "lag")
"""

import math
from OpenGL.GLU import *
from config import *


class Camera:
    def __init__(self):
        self._eye  = [0.0, CAM_HEIGHT, CAM_DISTANCE]
        self._look = [0.0, 0.0, 0.0]

    def follow(self, tank, dt):
        """Atualiza posição da câmera seguindo a mira (torre) do jogador."""
        # A câmera agora usa a soma do ângulo do tanque com o da torre
        total_angle = tank.angle + tank.turret_angle
        rad  = math.radians(total_angle)
        
        # Posição desejada: atrás e acima, alinhada com a mira do mouse
        tx = tank.pos[0] - math.sin(rad) * CAM_DISTANCE
        ty = tank.pos[1] + CAM_HEIGHT
        tz = tank.pos[2] - math.cos(rad) * CAM_DISTANCE

        # Interpolação linear suave (lag da câmera)
        alpha = min(1.0, CAM_LAG * dt)
        self._eye[0] += (tx - self._eye[0]) * alpha
        self._eye[1] += (ty - self._eye[1]) * alpha
        self._eye[2] += (tz - self._eye[2]) * alpha

        # Câmera sempre olha para a posição do tanque
        self._look = list(tank.pos)

    def apply(self):
        """Aplica a view matrix via gluLookAt."""
        gluLookAt(
            *self._eye,   # posição do observador
            *self._look,  # ponto de interesse
            0.0, 1.0, 0.0 # vetor up
        )
