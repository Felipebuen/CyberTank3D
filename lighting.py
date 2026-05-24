"""
lighting.py – Modelo de Iluminação de Phong + Luzes Dinâmicas

Conceitos de CG aplicados:
  • Modelo RGB
  • Iluminação de Phong (ambiente + difusa + especular)
  • Luzes dinâmicas vinculadas aos projéteis (GL_LIGHT1..GL_LIGHT7)
"""

from OpenGL.GL import *
from config import *


def setup_lighting():
    """Configura a luz solar principal (GL_LIGHT0) no modelo Phong."""
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, AMBIENT_LIGHT)

    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, SUN_POSITION)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  DIFFUSE_LIGHT)
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))


def update_dynamic_lights(projectiles):
    """
    Associa até 7 projéteis a luzes dinâmicas (GL_LIGHT1 … GL_LIGHT7).
    Luzes piscam amarelo/laranja no ponto do projétil.
    """
    # Desliga todas as luzes dinâmicas primeiro
    for i in range(1, 8):
        glDisable(GL_LIGHT0 + i)

    active = [p for p in projectiles if p.active][:7]

    for i, proj in enumerate(active):
        light = GL_LIGHT1 + i
        glEnable(light)
        glLightfv(light, GL_POSITION, (*proj.pos, 1.0))
        glLightfv(light, GL_DIFFUSE,  (1.0, 0.9, 0.2, 1.0))
        glLightfv(light, GL_SPECULAR, (1.0, 0.8, 0.1, 1.0))
        # Atenuação: luz forte perto, fraca longe
        glLightf(light, GL_CONSTANT_ATTENUATION,  0.1)
        glLightf(light, GL_LINEAR_ATTENUATION,    0.2)
        glLightf(light, GL_QUADRATIC_ATTENUATION, 0.05)
