"""
============================================================
 interface/tabs.py
 Barra de abas horizontal — usada dentro de cada exemplo
 para alternar entre Demonstração / Teoria / Resolução.

 TAB_H  : altura da barra de abas (px)
 TabBar : componente reutilizável
============================================================
"""

import pygame
import config as cfg

TAB_H = 36   # altura da barra de abas


class TabBar:
    """
    Barra de abas simples.

    Uso:
        self._tabs = TabBar(["Demonstração", "Teoria"])
        self._tabs.bind_mgr(self._mgr)   # opcional — foca mgr ao clicar aba

    No draw():
        self._tabs.draw(surface, fonts)

    No handle_mouse_*:
        if self._tabs.handle_mouse_down(pos): return True
        self._tabs.handle_mouse_move(pos)
        self._tabs.handle_mouse_up()
    """

    def __init__(self, labels: list[str]):
        self.labels  = labels
        self.active  = 0
        self._hover  = -1
        self._mgr    = None   # WindowManager opcional

    def bind_mgr(self, mgr):
        """Liga um WindowManager — ao trocar aba ele faz bring_to_front."""
        self._mgr = mgr

    # ── Eventos ───────────────────────────────────────────
    def handle_mouse_down(self, pos) -> bool:
        rects = self._tab_rects()
        for i, r in enumerate(rects):
            if r.collidepoint(pos):
                self.active = i
                return True
        return False

    def handle_mouse_move(self, pos):
        rects = self._tab_rects()
        self._hover = -1
        for i, r in enumerate(rects):
            if r.collidepoint(pos):
                self._hover = i
                break

    def handle_mouse_up(self):
        pass   # reservado para drag futuro

    def handle_scroll(self, dy):
        pass   # abas não rolam

    # ── Geometria ─────────────────────────────────────────
    def _tab_rects(self) -> list[pygame.Rect]:
        """Calcula os Rects das abas posicionados no canvas."""
        cx, cy, cw, ch = cfg.canvas_rect()
        n   = len(self.labels)
        tab_w = min(160, cw // max(n, 1))
        rects = []
        for i in range(n):
            rects.append(pygame.Rect(cx + i * tab_w, cy, tab_w, TAB_H))
        return rects

    # ── Draw ──────────────────────────────────────────────
    def draw(self, surface, fonts):
        rects = self._tab_rects()
        font  = fonts.get('tab', fonts.get('sm'))

        for i, (r, label) in enumerate(zip(rects, self.labels)):
            is_active = (i == self.active)
            is_hover  = (i == self._hover) and not is_active

            if is_active:
                bg  = cfg.TAB_ACTIVE
                tc  = cfg.WHITE
                brd = cfg.BORDER
            elif is_hover:
                bg  = cfg.TAB_HOVER
                tc  = cfg.WHITE
                brd = cfg.GRAY2
            else:
                bg  = cfg.TAB_NORMAL
                tc  = cfg.GRAY
                brd = cfg.BORDER

            pygame.draw.rect(surface, bg, r)
            pygame.draw.rect(surface, brd, r, 1)

            # Indicador inferior na aba ativa
            if is_active:
                pygame.draw.rect(surface, cfg.BLUE,
                                 (r.x, r.bottom - 3, r.w, 3))

            txt = font.render(label, True, tc)
            surface.blit(txt, txt.get_rect(center=r.center))
