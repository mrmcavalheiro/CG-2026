"""
============================================================
 exemplos/cisalhamento.py
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
from interface.ui       import draw_grid, draw_axes, world_to_screen, draw_polygon, draw_line_alpha



class ExCisalhamento(ExemploBase):
    NAME  = "Cisalhamento"
    COLOR = cfg.ORANGE

    def __init__(self):
        super().__init__()
        self.shx   = 0.8
        self.shy   = 0.0
        self.flash = 0.0
        self._mgr  = None
        self._tabs = TabBar(["Demonstração", "Teoria"])
        self._teoria = DocView(fallback_blocks=DOCS_TEORIA["cisalhamento"],
                               download_pdf=cfg.root_path("teoria","Aula_04","cisalhamento.pdf"))
        self._teoria.set_tab_offset(TAB_H)

    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        cay = cay + TAB_H
        cah = cah - TAB_H

        # Janelas maiores e responsivas para facilitar leitura.
        left_x = cax + 10
        top_y = cay + 10
        gap = 12

        info_w = min(380, max(300, int(caw * 0.34)))
        info_h = min(260, max(220, int(cah * 0.33)))
        mat_h = min(210, max(170, int(cah * 0.24)))
        code_w = min(420, max(320, int(caw * 0.38)))
        code_h = min(300, max(230, int(cah * 0.33)))

        y_info = top_y
        y_matriz = y_info + info_h + gap
        y_code = y_matriz + mat_h + gap

        max_bottom = cay + cah - 10
        if y_code + code_h > max_bottom:
            code_h = max(170, max_bottom - y_code)

        self._win_info   = self._mgr.create("Cisalhamento (Shearing)",
            left_x, y_info, info_w, info_h, color=(180,80,20), closable=False)
        self._win_matriz = self._mgr.create("Matriz de Cisalhamento",
            left_x, y_matriz, info_w, mat_h, color=(20,80,100), closable=False)
        self._win_code   = self._mgr.create("Python — NumPy",
            left_x, y_code, code_w, code_h, color=(60,40,120), closable=False)
        self._tabs.bind_mgr(self._mgr)

    def update(self, dt):
        self.advance(dt, speed=0.5)
        if self.flash > 0: self.flash = max(0.0, self.flash - dt)

    def handle_action(self, action):
        super().handle_action(action)
        step = 0.1
        if action == 'inc':
            self.shy = round(self.shy + step, 2); self.flash = 0.4
        elif action == 'dec':
            self.shy = round(self.shy - step, 2); self.flash = 0.4
        elif action == 'inc_alt':
            self.shx = round(self.shx + step, 2); self.flash = 0.4
        elif action == 'dec_alt':
            self.shx = round(self.shx - step, 2); self.flash = 0.4

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

        ease    = self.smoothstep(self.t)
        shx_now = self.shx * ease
        shy_now = self.shy * ease

        orig_s = world_to_screen(self.shape, cr, cx, cy)
        draw_polygon(surface, orig_s, cfg.GRAY2, 1, fill=cfg.GRAY2, fill_alpha=25)
        sheared = self.shape.copy()
        sheared[:, 0] = self.shape[:, 0] + shx_now * self.shape[:, 1]
        sheared[:, 1] = self.shape[:, 1] + shy_now * self.shape[:, 0]
        shear_s = world_to_screen(sheared, cr, cx, cy)
        draw_polygon(surface, shear_s, cfg.ORANGE, 2, fill=cfg.ORANGE, fill_alpha=50)
        if self.t > 0.05:
            for p1, p2 in zip(orig_s, shear_s):
                draw_line_alpha(surface, cfg.YELLOW, p1, p2, 1, alpha=60)

        vc = cfg.YELLOW if self.flash > 0 else cfg.WHITE
        rows_info = [
            ("Cisalhamento (Shearing)",            cfg.ORANGE),
            (f"  Shx={self.shx}  Shy={self.shy}", vc),
            ("  x' = x + Shx*y",                 cfg.GRAY),
            ("  y' = y + Shy*x",                 cfg.GRAY),
            ("",                                  cfg.WHITE),
            ("[ESP] Animar  [R] Reset",            cfg.YELLOW),
            ("[Setas] Ajustar Shx/Shy",            cfg.YELLOW),
        ]
        rows_matriz = [
            ("Matriz de Cisalhamento:", cfg.CYAN),
            (" | 1    Shx  0 |",       cfg.WHITE),
            (" | Shy  1    0 |",       cfg.WHITE),
            (" | 0    0    1 |",       cfg.WHITE),
            (f"  Shx={self.shx} Shy={self.shy}", cfg.GRAY),
        ]
        rows_code = [
            ("import numpy as np",                     (188,140,255)),
            ("",                                       cfg.WHITE),
            (f"Shx, Shy = {self.shx}, {self.shy}",    cfg.WHITE),
            ("M = np.array([[1,   Shx, 0],",           cfg.WHITE),
            ("              [Shy, 1,   0],",            cfg.WHITE),
            ("              [0,   0,   1]])",           cfg.WHITE),
            ("P_new = M @ [x, y, 1]",                  cfg.WHITE),
        ]

        def _content(win, surf):
            if   win is self._win_info:   draw_rows_in_win(surf, win, rows_info)
            elif win is self._win_matriz: draw_rows_in_win(surf, win, rows_matriz)
            elif win is self._win_code:   draw_rows_in_win(surf, win, rows_code)

        self._mgr.draw_managed(surface, fonts, _content)

