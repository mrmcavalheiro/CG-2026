"""
Aula 06 - Solucoes - Bezier
Atividade: Curvas de Bezier dinamicas com multiplos cliques.
"""

import pygame
import config as cfg
from exemplos.base import ExemploBase
from exemplos.docs_teoria import DOCS_TEORIA
from interface.tabs import TabBar, TAB_H
from interface.doc_view import DocView


class ExBezierSolucao(ExemploBase):
    NAME = "Bezier"
    COLOR = cfg.CYAN

    def __init__(self):
        super().__init__()
        self._tabs = TabBar(["Demonstracao", "Teoria"])
        self._pontos = []

        self._teoria = DocView(
            fallback_blocks=DOCS_TEORIA["bezier"],
            download_pdf=cfg.root_path("teoria", "Aula_06", "bezier.pdf"),
        )
        self._teoria.set_tab_offset(TAB_H)

    def reset(self):
        self._pontos.clear()

    def update(self, dt):
        pass

    def handle_extra(self, key):
        if key == pygame.K_c:
            self._pontos.clear()
        elif key == pygame.K_BACKSPACE and self._pontos:
            self._pontos.pop()

    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos):
            return True

        if self._tabs.active == 1:
            return self._teoria.handle_mouse_down(pos, cfg.canvas_rect())

        cax, cay, caw, cah = cfg.canvas_rect()
        area = pygame.Rect(cax, cay + TAB_H, caw, cah - TAB_H)
        if area.collidepoint(pos):
            self._pontos.append((float(pos[0]), float(pos[1])))
            return True
        return False

    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._tabs.active == 1:
            self._teoria.handle_mouse_move(pos)

    def handle_mouse_up(self, pos):
        self._tabs.handle_mouse_up()
        self._teoria.handle_mouse_up()

    def handle_scroll(self, dy):
        if self._tabs.active == 1:
            self._teoria.handle_scroll(dy)

    @staticmethod
    def _bezier_point(points, t):
        work = [pygame.Vector2(p[0], p[1]) for p in points]
        n = len(work)
        while n > 1:
            for i in range(n - 1):
                work[i] = (1.0 - t) * work[i] + t * work[i + 1]
            n -= 1
        return work[0].x, work[0].y

    def _gerar_curva(self, amostras=220):
        if len(self._pontos) < 3:
            return []
        amostras = max(40, amostras)
        pts = []
        for i in range(amostras + 1):
            t = i / amostras
            pts.append(self._bezier_point(self._pontos, t))
        return pts

    def draw(self, surface, fonts):
        self._tabs.draw(surface, fonts)

        if self._tabs.active == 1:
            self._teoria.render(surface)
            return

        cax, cay, caw, cah = cfg.canvas_rect()
        area = pygame.Rect(cax, cay + TAB_H, caw, cah - TAB_H)
        pygame.draw.rect(surface, cfg.BG, area)

        fn = fonts["sm"]
        hint = "Clique para adicionar pontos | Backspace: desfazer | C: limpar"
        s = fn.render(hint, True, cfg.GRAY)
        surface.blit(s, (area.x + 12, area.y + 10))

        # Poligono de controle
        if len(self._pontos) >= 2:
            for i in range(len(self._pontos) - 1):
                pygame.draw.aaline(surface, cfg.GRAY2, self._pontos[i], self._pontos[i + 1])

        # Caso exatamente 2 pontos: linha reta
        if len(self._pontos) == 2:
            pygame.draw.aaline(surface, cfg.YELLOW, self._pontos[0], self._pontos[1])

        # Caso 3+ pontos: curva de Bezier
        if len(self._pontos) >= 3:
            curva = self._gerar_curva(amostras=220)
            for i in range(len(curva) - 1):
                pygame.draw.aaline(surface, cfg.CYAN, curva[i], curva[i + 1])

        # Pontos de controle
        for idx, p in enumerate(self._pontos):
            pygame.draw.circle(surface, cfg.ORANGE, (int(p[0]), int(p[1])), 5)
            lbl = fn.render(str(idx), True, cfg.WHITE)
            surface.blit(lbl, (int(p[0]) + 8, int(p[1]) - 8))

        status = f"Pontos: {len(self._pontos)}"
        st = fn.render(status, True, cfg.GRAY)
        surface.blit(st, (area.x + 12, area.y + 30))
