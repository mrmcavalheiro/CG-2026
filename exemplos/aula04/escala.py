"""
============================================================
 exemplos/escala.py
============================================================
"""
import pygame
import numpy as np
import config as cfg
from exemplos.base      import ExemploBase
from exemplos.docs_teoria import DOCS_TEORIA
from interface.tabs     import TabBar, TAB_H
from interface.doc_view import DocView
from interface.janela   import WindowManager, draw_rows_in_win
from interface.ui       import draw_grid, draw_axes, world_to_screen, draw_polygon



class ExEscala(ExemploBase):
    NAME  = "Escala"
    COLOR = cfg.GREEN

    def __init__(self):
        super().__init__()
        self.ex    = 2.0
        self.ey    = 1.5
        self.flash = 0.0
        self._mgr  = None
        self._tabs = TabBar(["Demonstração", "Teoria"])
        self._teoria = DocView(fallback_blocks=DOCS_TEORIA["escala"],
                               download_pdf=cfg.root_path("teoria","Aula_04","escala.pdf"))
        self._teoria.set_tab_offset(TAB_H)

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        cay = cay + TAB_H
        cah = cah - TAB_H
        self._win_info   = self._mgr.create("Escala 2D",
            cax+10, cay+10, 260, 215, color=(30,120,50), closable=False)
        self._win_matriz = self._mgr.create("Matricial 3D",
            cax+10, cay+240, 260, 155, color=(20,80,100), closable=False)
        self._win_code   = self._mgr.create("Python — NumPy",
            cax+10, cay+410, 280, 225, color=(60,40,120), closable=False)
        self._tabs.bind_mgr(self._mgr)

    def update(self, dt):
        self.advance(dt, speed=0.5)
        if self.flash > 0: self.flash = max(0.0, self.flash - dt)

    def handle_action(self, action):
        super().handle_action(action)
        step = 0.1
        if action == 'inc':
            self.ey = round(self.ey + step, 2); self.flash = 0.4
        elif action == 'dec':
            self.ey = round(max(0.1, self.ey - step), 2); self.flash = 0.4
        elif action == 'inc_alt':
            self.ex = round(self.ex + step, 2); self.flash = 0.4
        elif action == 'dec_alt':
            self.ex = round(max(0.1, self.ex - step), 2); self.flash = 0.4

    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 1:
            return self._teoria.handle_mouse_down(pos, cfg.canvas_rect())
        if self._tabs.active == 0 and self._mgr:
            return self._mgr.handle_mouse_down(pos)
        return False
    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._tabs.active == 1:
            self._teoria.handle_mouse_move(pos)
        elif self._mgr:
            self._mgr.handle_mouse_move(pos)
    def handle_mouse_up(self, pos):
        self._tabs.handle_mouse_up()
        self._teoria.handle_mouse_up()
        if self._mgr: self._mgr.handle_mouse_up(pos)

    def handle_scroll(self, dy):
        self._tabs.handle_scroll(dy)
        if self._tabs.active == 1:
            self._teoria.handle_scroll(dy)
        elif self._mgr:
            self._mgr.handle_scroll(pygame.mouse.get_pos(), dy)

    def draw(self, surface, fonts):
        if self._mgr is None:
            self._init_windows()

        self._tabs.draw(surface, fonts)

        # Aba Teoria — renderiza conteúdo rico
        if self._tabs.active == 1:
            self._teoria.render(surface)
            return

        drx, dry, drw, drh = cfg.draw_rect()
        cr = (drx, dry + TAB_H, drw, drh - TAB_H)
        cx = drw // 2; cy = (drh - TAB_H) // 2
        draw_grid(surface, cr, cx, cy)
        draw_axes(surface, cr, cx, cy, font=fonts['sm'])

        ease   = self.smoothstep(self.t)
        ex_now = 1.0 + (self.ex - 1.0) * ease
        ey_now = 1.0 + (self.ey - 1.0) * ease

        orig_s = world_to_screen(self.shape, cr, cx, cy)
        draw_polygon(surface, orig_s, cfg.GRAY2, 1, fill=cfg.GRAY2, fill_alpha=25)
        scaled   = self.shape * np.array([ex_now, ey_now])
        scaled_s = world_to_screen(scaled, cr, cx, cy)
        draw_polygon(surface, scaled_s, cfg.GREEN, 2, fill=cfg.GREEN, fill_alpha=50)
        if self.t > 0.05:
            for p1, p2 in zip(orig_s, scaled_s):
                pygame.draw.line(surface, (*cfg.YELLOW, 70), p1, p2, 1)

        vc = cfg.YELLOW if self.flash > 0 else cfg.WHITE
        rows_info = [
            ("Escala 2D",                           cfg.GREEN),
            (f"  Ex = {self.ex}   Ey = {self.ey}", vc),
            (f"  x' = x * {self.ex}",              cfg.GRAY),
            (f"  y' = y * {self.ey}",              cfg.GRAY),
            ("",                                   cfg.WHITE),
            ("[ESP] Animar  [R] Reset",             cfg.YELLOW),
            ("[Setas] Ajustar Ex/Ey",               cfg.YELLOW),
        ]
        rows_matriz = [
            ("Matricial 3D:",          cfg.CYAN),
            (" [x' y' z'] =",        cfg.WHITE),
            (" [x*Ex  y*Ey  z*Ez]",   cfg.WHITE),
            ("",                      cfg.WHITE),
            (" Ex,Ey > 1 -> Aumenta", cfg.GREEN),
            (" Ex,Ey < 1 -> Diminui", cfg.ORANGE),
        ]
        rows_code = [
            ("import numpy as np",                   (188,140,255)),
            ("",                                     cfg.WHITE),
            (f"S = np.array([{self.ex}, {self.ey}])", cfg.WHITE),
            ("P = np.array([x, y])",                 cfg.WHITE),
            ("",                                     cfg.WHITE),
            ("P_new = P * S",                        cfg.WHITE),
            ("# x' = x * Ex",                       (100,140,100)),
            ("# y' = y * Ey",                       (100,140,100)),
        ]

        def _content(win, surf):
            if   win is self._win_info:   draw_rows_in_win(surf, win, rows_info)
            elif win is self._win_matriz: draw_rows_in_win(surf, win, rows_matriz)
            elif win is self._win_code:   draw_rows_in_win(surf, win, rows_code)

        self._mgr.draw_managed(surface, fonts, _content)
