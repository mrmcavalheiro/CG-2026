"""
============================================================
 exemplos/translacao.py
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
from interface.ui       import draw_grid, draw_axes, world_to_screen, \
                               draw_polygon, draw_arrow_line



class ExTranslacao(ExemploBase):
    NAME  = "Translação"
    COLOR = cfg.BLUE

    def __init__(self):
        super().__init__()
        self.tx = 120
        self.ty =  80
        self.flash = 0.0
        self._mgr  = None
        self._tabs = TabBar(["Demonstração", "Teoria"])
        self._teoria = DocView(fallback_blocks=DOCS_TEORIA["translacao"],
                               download_pdf=cfg.root_path("teoria","Aula_04","translacao.pdf"))
        self._teoria.set_tab_offset(TAB_H)

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        cay = cay + TAB_H
        cah = cah - TAB_H
        self._win_info   = self._mgr.create("Translação 2D",
            cax+10, cay+10, 260, 210, color=(30,80,180), closable=False)
        self._win_matriz = self._mgr.create("Notação Matricial",
            cax+10, cay+235, 260, 115, color=(20,80,100), closable=False)
        self._win_code   = self._mgr.create("Python — NumPy",
            cax+10, cay+365, 280, 230, color=(60,40,120), closable=False)
        self._tabs.bind_mgr(self._mgr)

    def reset(self):
        super().reset()

    def update(self, dt):
        self.advance(dt, speed=0.6)
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)

    def handle_action(self, action):
        super().handle_action(action)
        if action == 'inc':       self.ty += 10
        elif action == 'dec':     self.ty -= 10
        elif action == 'inc_alt': self.tx += 10
        elif action == 'dec_alt': self.tx -= 10

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

        cr_full = cfg.canvas_rect()

        drx, dry, drw, drh = cfg.draw_rect()
        cr = (drx, dry + TAB_H, drw, drh - TAB_H)
        cx = drw // 2
        cy = (drh - TAB_H) // 2

        draw_grid(surface, cr, cx, cy)
        draw_axes(surface, cr, cx, cy, font=fonts['sm'])

        ease   = self.smoothstep(self.t)
        tx_now = self.tx * ease
        ty_now = self.ty * ease

        orig_s = world_to_screen(self.shape, cr, cx, cy)
        draw_polygon(surface, orig_s, cfg.GRAY2, width=1,
                     fill=cfg.GRAY2, fill_alpha=25)
        moved   = self.shape + np.array([tx_now, ty_now])
        moved_s = world_to_screen(moved, cr, cx, cy)
        draw_polygon(surface, moved_s, cfg.BLUE, width=2,
                     fill=cfg.BLUE, fill_alpha=50)

        ox = cr[0] + cx; oy = cr[1] + cy
        if abs(tx_now) > 2 or abs(ty_now) > 2:
            draw_arrow_line(surface, (ox, oy),
                (int(ox+tx_now), int(oy-ty_now)), cfg.YELLOW, 2)
        pygame.draw.circle(surface, cfg.WHITE, (ox, oy), 4)

        vc = cfg.YELLOW if self.flash > 0 else cfg.WHITE
        rows_info = [
            ("Translacao 2D",                      cfg.BLUE),
            (f"  Tx = {self.tx}   Ty = {self.ty}", vc),
            (f"  x' = x + {self.tx}",              cfg.GRAY),
            (f"  y' = y + {self.ty}",              cfg.GRAY),
            ("",                                   cfg.WHITE),
            ("[ESP] Animar  [R] Reset",             cfg.YELLOW),
            ("[Setas] Ajustar Tx/Ty",               cfg.YELLOW),
        ]
        rows_matriz = [
            ("Notacao Matricial 3D:",   cfg.CYAN),
            (" [x' y' z'] =",         cfg.WHITE),
            (" [x  y  z] + [Tx Ty 0]", cfg.WHITE),
        ]
        rows_code = [
            ("import numpy as np",                  (188,140,255)),
            ("",                                    cfg.WHITE),
            (f"T  = np.array([{self.tx}, {self.ty}])", cfg.WHITE),
            ("P  = np.array([x, y])",               cfg.WHITE),
            ("",                                    cfg.WHITE),
            ("P_new = P + T",                       cfg.WHITE),
            ("# x' = x + Tx",                      (100,140,100)),
            ("# y' = y + Ty",                      (100,140,100)),
        ]

        def _content(win, surf):
            if   win is self._win_info:   draw_rows_in_win(surf, win, rows_info)
            elif win is self._win_matriz: draw_rows_in_win(surf, win, rows_matriz)
            elif win is self._win_code:   draw_rows_in_win(surf, win, rows_code)

        self._mgr.draw_managed(surface, fonts, _content)
