"""
texture_manager.py – Carregamento de Texturas com Pillow (PIL)

Conceitos de CG aplicados:
  • Mapeamento de texturas (glTexImage2D)
  • Modelo de cores RGB
"""

import os
from OpenGL.GL import *
from PIL import Image
import numpy as np


class TextureManager:
    def __init__(self):
        self._cache: dict[str, int] = {}

    def load(self, path: str) -> int | None:
        """Carrega uma textura do disco e retorna o ID OpenGL.
        Retorna None silenciosamente se o arquivo não existir."""
        if path in self._cache:
            return self._cache[path]

        abs_path = os.path.join(os.path.dirname(__file__), path)
        if not os.path.isfile(abs_path):
            # Gera textura procedural de fallback
            return self._procedural_texture(path)

        try:
            img  = Image.open(abs_path).convert("RGB")
            img  = img.transpose(Image.FLIP_TOP_BOTTOM)
            data = np.array(img, dtype=np.uint8)
            tid  = self._upload(data, img.width, img.height)
            self._cache[path] = tid
            return tid
        except Exception as e:
            print(f"[TextureManager] Aviso: não foi possível carregar '{path}': {e}")
            return self._procedural_texture(path)

    # ── Textura procedural (xadrez) ─────────────────────────────────
    def _procedural_texture(self, key: str) -> int:
        size = 64
        data = np.zeros((size, size, 3), dtype=np.uint8)
        for y in range(size):
            for x in range(size):
                c = 180 if (x // 8 + y // 8) % 2 == 0 else 60
                data[y, x] = [c, c, c + 40]
        tid = self._upload(data, size, size)
        self._cache[key] = tid
        return tid

    @staticmethod
    def _upload(data: np.ndarray, w: int, h: int) -> int:
        tid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,     GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,     GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, data)
        from OpenGL.GL import glGenerateMipmap
        glGenerateMipmap(GL_TEXTURE_2D)
        return tid
