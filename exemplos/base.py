"""
============================================================
 exemplos/base.py
 Classe base para todos os exemplos.
 Cada exemplo deve herdar ExemploBase e implementar:
   draw(surface, fonts)
   update(dt)
   handle_action(action)   ← recebe string do KeyMap
============================================================
"""

import numpy as np
import config as cfg


# ─────────────────────────────────────────────
#  FORMAS GEOMÉTRICAS PADRÃO
# ─────────────────────────────────────────────
SHAPE_L = np.array([          # forma "L" invertido
    [-60, -40], [ 60, -40],
    [ 60,  40], [ 20,  40],
    [ 20,   0], [-20,   0],
    [-20,  40], [-60,  40],
], dtype=float)

SHAPE_ARROW = np.array([      # seta apontando para cima
    [  0,  60], [ 22,  20], [  8,  20],
    [  8, -60], [ -8, -60], [ -8,  20],
    [-22,  20],
], dtype=float)

SHAPE_HOUSE = np.array([      # casinha simples
    [-50,   0], [  0,  50], [ 50,   0],
    [ 50, -40], [-50, -40],
], dtype=float)


# ─────────────────────────────────────────────
#  CLASSE BASE
# ─────────────────────────────────────────────
class ExemploBase:
    NAME  = "Exemplo"
    COLOR = cfg.BLUE          # cor do botão no sidebar

    def __init__(self):
        self.shape     = SHAPE_L.copy()
        self.animating = False
        self.t         = 0.0   # progresso da animação [0..1]

    # ── Interface pública ─────────────────────
    def update(self, dt: float):
        """Atualiza estado. dt em segundos."""
        pass

    def draw(self, surface, fonts: dict):
        """Desenha no canvas."""
        pass

    def handle_action(self, action: str):
        """
        Recebe ação nomeada vinda do KeyMap.
        Sobrescreva para tratar ações específicas.
        """
        if action == 'toggle_anim':
            self.toggle_anim()
        elif action == 'reset':
            self.reset()

    def reset_windows(self):
        """
        Chamado ao redimensionar a janela principal.
        Força _init_windows() na próxima frame, reposicionando
        as janelas flutuantes dentro do novo canvas.
        """
        if hasattr(self, '_mgr'):
            self._mgr = None

    def reset(self):
        self.t         = 0.0
        self.animating = False

    def toggle_anim(self):
        self.animating = not self.animating
        if self.animating:
            self.t = 0.0

    # ── Helpers ───────────────────────────────
    @staticmethod
    def smoothstep(t: float) -> float:
        """Interpolação suave 0→1."""
        t = max(0.0, min(1.0, t))
        return t * t * (3 - 2 * t)

    def advance(self, dt: float, speed=0.6) -> float:
        """
        Avança t e retorna smoothstep(t).
        Para animações simples one-shot.
        """
        if self.animating:
            self.t = min(self.t + dt * speed, 1.0)
            if self.t >= 1.0:
                self.animating = False
        return self.smoothstep(self.t)
