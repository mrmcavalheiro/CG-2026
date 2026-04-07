"""
============================================================
 exemplos/aula05/window_viewport.py

 Exemplo interativo: Transformacao Window-Viewport

 Demonstra visualmente:
  - Espaco do mundo com objetos
  - Janela (retangulo verde) definindo o que e visivel
  - Viewport (retangulo laranja) na tela
  - Mapeamento em tempo real de todos os pontos
  - Formula aplicada ponto a ponto

 Controles:
  - Setas: mover a janela pelo mundo
  - W/S:   aumentar/diminuir altura da janela
  - A/D:   aumentar/diminuir largura da janela
  - R:     resetar
============================================================
"""

import pygame
import math
import config as cfg
from exemplos.base import ExemploBase
from interface.ui  import draw_label
from interface.tabs   import TabBar, TAB_H
from interface.doc_view import DocView
from interface.janela import WindowManager, draw_rows_in_win


# ── Objetos no espaco do mundo ───────────────────────────
WORLD_OBJECTS = [
    # (tipo, cor, dados)
    ('circle', (88,166,255),  (  0,   0, 40)),        # circulo azul na origem
    ('circle', (63,185,80),   (120,  80, 25)),         # circulo verde
    ('circle', (247,129,102), (-80,  60, 30)),         # circulo laranja
    ('circle', (188,140,255), ( 60, -90, 20)),         # circulo roxo
    ('circle', (57,213,213),  (-120,-70, 35)),         # circulo ciano
    ('rect',   (227,179,65),  (-50,  30, 60, 40)),     # retangulo amarelo
    ('rect',   (255,80,80),   ( 80, -40, 50, 35)),     # retangulo vermelho
    # eixos (representados como linhas)
    ('line',   (80,90,100),   (-200,0, 200,0)),        # eixo X
    ('line',   (80,90,100),   (0,-150, 0,150)),        # eixo Y
]



class ExWindowViewport(ExemploBase):
    NAME  = "Window-Viewport"
    COLOR = cfg.ORANGE

    # Dimensoes do mundo
    WORLD_W = 400
    WORLD_H = 300

    def __init__(self):
        super().__init__()
        # Janela no espaco do mundo
        self.wn_x  = -100.0   # centro X da janela
        self.wn_y  =    0.0   # centro Y da janela
        self.wn_w  =  160.0   # largura da janela
        self.wn_h  =  120.0   # altura da janela
        self.flash = 0.0
        self._mgr  = None
        self._teoria   = DocView(cfg.root_path("teoria", "Aula_05", "window_viewport.pdf"))
        self._teoria.set_tab_offset(TAB_H)
        self._tabs = TabBar(["Demonstração", "Teoria"])


    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Window-Viewport",
            cax+10, cay+10, 260, 320, color=(180,100,20), closable=False)
        self._win_code = self._mgr.create("Python",
            cax+10, cay+345, 260, 220, color=(60,40,120), closable=False)
        self._tabs.bind_mgr(self._mgr)


    def handle_mouse_down(self, pos):
        if self._tabs.handle_mouse_down(pos): return True
        if self._tabs.active == 0 and self._mgr:
            return self._mgr.handle_mouse_down(pos)
        return False

    def handle_mouse_move(self, pos):
        self._tabs.handle_mouse_move(pos)
        if self._tabs.active == 0 and self._mgr:
            self._mgr.handle_mouse_move(pos)

    def handle_mouse_up(self, pos):
        self._tabs.handle_mouse_up()
        if self._mgr: self._mgr.handle_mouse_up(pos)

    def handle_scroll(self, dy):
        if self._tabs.active == 1:
            self._teoria.handle_scroll(dy)
        elif self._mgr:
            self._mgr.handle_scroll(pygame.mouse.get_pos(), dy)
        else:
            self._tabs.handle_scroll(dy)

    def reset(self):
        self.wn_x  = -100.0
        self.wn_y  =    0.0
        self.wn_w  =  160.0
        self.wn_h  =  120.0
        self.flash = 0.0

    def handle_action(self, action):
        step = 15.0
        if   action == 'reset':     self.reset()
        elif action == 'inc':       self.wn_y += step;  self.flash = 0.3
        elif action == 'dec':       self.wn_y -= step;  self.flash = 0.3
        elif action == 'inc_alt':   self.wn_x += step;  self.flash = 0.3
        elif action == 'dec_alt':   self.wn_x -= step;  self.flash = 0.3

    def handle_extra(self, key):
        """Chamado pelo exemplo para teclas W/S/A/D."""
        step = 10.0
        if   key == pygame.K_w: self.wn_h = min(self.wn_h + step, 280); self.flash=0.3
        elif key == pygame.K_s: self.wn_h = max(self.wn_h - step,  30); self.flash=0.3
        elif key == pygame.K_a: self.wn_w = max(self.wn_w - step,  30); self.flash=0.3
        elif key == pygame.K_d: self.wn_w = min(self.wn_w + step, 380); self.flash=0.3

    def update(self, dt):
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)

    # ── helpers de conversao ─────────────────────────────
    def _world_bounds(self):
        """Retorna (xwmin, xwmax, ywmin, ywmax) da janela."""
        hw = self.wn_w / 2
        hh = self.wn_h / 2
        return (self.wn_x - hw, self.wn_x + hw,
                self.wn_y - hh, self.wn_y + hh)

    def _world_to_minimap(self, xw, yw, map_rect):
        """Converte coord do mundo para o minimapa (esquerda)."""
        mx, my, mw, mh = map_rect
        sx = mw / self.WORLD_W
        sy = mh / self.WORLD_H
        px = int(mx + (xw + self.WORLD_W/2) * sx)
        py = int(my + (self.WORLD_H/2 - yw) * sy)
        return px, py

    def _world_to_viewport(self, xw, yw, vp_rect):
        """Mapeamento Window -> Viewport."""
        xvmin, yvmin, vw, vh = vp_rect
        xvmax = xvmin + vw
        yvmax = yvmin + vh
        xwmin, xwmax, ywmin, ywmax = self._world_bounds()
        if xwmax == xwmin or ywmax == ywmin:
            return xvmin, yvmin
        sx = (xvmax - xvmin) / (xwmax - xwmin)
        sy = (yvmax - yvmin) / (ywmax - ywmin)
        xv = int(xvmin + (xw - xwmin) * sx)
        yv = int(yvmax - (yw - ywmin) * sy)   # Y invertido!
        return xv, yv

    def draw(self, surface, fonts):
        cr  = cfg.canvas_rect()
        cax, cay, caw, cah = cr

        # Fundo já pintado pelo _draw() principal

        # Ajusta área de conteúdo abaixo das abas
        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        cax = drx; cay = dry
        caw = drw; cah = drh

        fn  = fonts['sm']
        fn2 = fonts['tab']

        # ── Layout ──────────────────────────────────────
        # Esquerda: minimapa do mundo (40% da largura)
        # Direita:  viewport resultado (restante - info)
        map_pad  = 20
        map_w    = int(caw * 0.38)
        map_h    = int(map_w * self.WORLD_H / self.WORLD_W)
        map_x    = cax + map_pad
        map_y    = cay + (cah - map_h) // 2
        map_rect = (map_x, map_y, map_w, map_h)

        # Viewport na tela (lado direito)
        vp_margin = 20
        vp_x = cax + map_pad + map_w + 40
        vp_w = int(caw * 0.35)
        vp_h = int(vp_w * self.wn_h / self.wn_w) if self.wn_w > 0 else 200
        vp_h = min(vp_h, cah - 60)
        vp_y = cay + (cah - vp_h) // 2
        vp_rect = (vp_x, vp_y, vp_w, vp_h)

        xwmin, xwmax, ywmin, ywmax = self._world_bounds()

        # ════════════════════════════════════════
        #  1. MINIMAPA — espaco do mundo
        # ════════════════════════════════════════
        pygame.draw.rect(surface, cfg.BG2, (map_x, map_y, map_w, map_h))
        pygame.draw.rect(surface, cfg.BORDER, (map_x, map_y, map_w, map_h), 1)

        # título
        s = fn.render("Espaco do Mundo", True, cfg.GRAY)
        surface.blit(s, (map_x + map_w//2 - s.get_width()//2, map_y - 22))

        # grid do mundo
        for gx in range(-200, 201, 50):
            px, _ = self._world_to_minimap(gx, 0, map_rect)
            pygame.draw.line(surface, cfg.GRAY2,
                             (px, map_y), (px, map_y + map_h), 1)
        for gy in range(-150, 151, 50):
            _, py = self._world_to_minimap(0, gy, map_rect)
            pygame.draw.line(surface, cfg.GRAY2,
                             (map_x, py), (map_x + map_w, py), 1)

        # objetos no mundo
        for obj_type, color, data in WORLD_OBJECTS:
            if obj_type == 'circle':
                cx_w, cy_w, r_w = data
                px, py = self._world_to_minimap(cx_w, cy_w, map_rect)
                r_px   = max(2, int(r_w * map_w / self.WORLD_W))
                pygame.draw.circle(surface, color, (px, py), r_px, 1)
            elif obj_type == 'rect':
                rx, ry, rw, rh = data
                p1 = self._world_to_minimap(rx, ry + rh, map_rect)
                p2 = self._world_to_minimap(rx + rw, ry, map_rect)
                pygame.draw.rect(surface, color,
                                 (p1[0], p1[1],
                                  p2[0]-p1[0], p2[1]-p1[1]), 1)
            elif obj_type == 'line':
                x1, y1, x2, y2 = data
                p1 = self._world_to_minimap(x1, y1, map_rect)
                p2 = self._world_to_minimap(x2, y2, map_rect)
                pygame.draw.line(surface, color, p1, p2, 1)

        # janela (retangulo verde no minimapa)
        win_tl = self._world_to_minimap(xwmin, ywmax, map_rect)
        win_br = self._world_to_minimap(xwmax, ywmin, map_rect)
        win_rect_px = pygame.Rect(win_tl[0], win_tl[1],
                                  win_br[0] - win_tl[0],
                                  win_br[1] - win_tl[1])
        # preenchimento suave
        surf_win = pygame.Surface((win_rect_px.w, win_rect_px.h), pygame.SRCALPHA)
        surf_win.fill((*cfg.GREEN, 25))
        surface.blit(surf_win, win_rect_px.topleft)
        c_flash = cfg.YELLOW if self.flash > 0 else cfg.GREEN
        pygame.draw.rect(surface, c_flash, win_rect_px, 2)
        draw_label(surface, "Janela",
                   win_tl[0]+3, win_tl[1]+2, fn, c_flash, cfg.BG2)

        # seta do minimapa para o viewport
        arrow_x1 = map_x + map_w + 8
        arrow_x2 = vp_x  - 8
        arrow_y  = cay + cah // 2
        pygame.draw.line(surface, cfg.YELLOW,
                         (arrow_x1, arrow_y), (arrow_x2, arrow_y), 2)
        pygame.draw.polygon(surface, cfg.YELLOW, [
            (arrow_x2, arrow_y),
            (arrow_x2-10, arrow_y-5),
            (arrow_x2-10, arrow_y+5),
        ])
        s = fn.render("mapeamento", True, cfg.YELLOW)
        surface.blit(s, ((arrow_x1+arrow_x2)//2 - s.get_width()//2,
                          arrow_y - 18))

        # ════════════════════════════════════════
        #  2. VIEWPORT — resultado mapeado
        # ════════════════════════════════════════
        pygame.draw.rect(surface, cfg.BG2, (vp_x, vp_y, vp_w, vp_h))
        pygame.draw.rect(surface, cfg.ORANGE, (vp_x, vp_y, vp_w, vp_h), 2)

        s = fn.render("Viewport (tela)", True, cfg.ORANGE)
        surface.blit(s, (vp_x + vp_w//2 - s.get_width()//2, vp_y - 22))

        # clip ao viewport
        clip_vp = pygame.Rect(vp_x, vp_y, vp_w, vp_h)
        surface.set_clip(clip_vp)

        # grid no viewport
        grid_step_x = vp_w // 4
        grid_step_y = vp_h // 4
        for i in range(1, 4):
            pygame.draw.line(surface, cfg.GRAY2,
                             (vp_x + i*grid_step_x, vp_y),
                             (vp_x + i*grid_step_x, vp_y + vp_h), 1)
            pygame.draw.line(surface, cfg.GRAY2,
                             (vp_x, vp_y + i*grid_step_y),
                             (vp_x + vp_w, vp_y + i*grid_step_y), 1)

        # renderizar objetos mapeados para o viewport
        for obj_type, color, data in WORLD_OBJECTS:
            if obj_type == 'circle':
                cx_w, cy_w, r_w = data
                # verificar se esta dentro da janela
                if xwmin <= cx_w <= xwmax and ywmin <= cy_w <= ywmax:
                    px, py = self._world_to_viewport(cx_w, cy_w, vp_rect)
                    sx = vp_w / (xwmax - xwmin) if xwmax != xwmin else 1
                    r_px = max(3, int(r_w * sx))
                    pygame.draw.circle(surface, color, (px, py), r_px, 2)
                    pygame.draw.circle(surface, (*color, 50), (px, py), r_px)
            elif obj_type == 'rect':
                rx, ry, rw, rh = data
                cx_r, cy_r = rx + rw/2, ry + rh/2
                if xwmin <= cx_r <= xwmax and ywmin <= cy_r <= ywmax:
                    p1 = self._world_to_viewport(rx, ry + rh, vp_rect)
                    p2 = self._world_to_viewport(rx + rw, ry, vp_rect)
                    pygame.draw.rect(surface, color,
                                     (p1[0], p1[1],
                                      p2[0]-p1[0], p2[1]-p1[1]), 2)
            elif obj_type == 'line':
                x1, y1, x2, y2 = data
                p1 = self._world_to_viewport(x1, y1, vp_rect)
                p2 = self._world_to_viewport(x2, y2, vp_rect)
                pygame.draw.line(surface, color, p1, p2, 1)

        surface.set_clip(None)

        # labels de coordenadas do viewport
        draw_label(surface, f"({vp_x-cax},{vp_y-cay})",
                   vp_x+2, vp_y+2, fn, cfg.GRAY2)
        draw_label(surface, f"({vp_x-cax+vp_w},{vp_y-cay+vp_h})",
                   vp_x+vp_w-80, vp_y+vp_h-16, fn, cfg.GRAY2)

        # ════════════════════════════════════════
        #  3. INFO BOX (lado direito do canvas)
        # ════════════════════════════════════════
        info_x = vp_x + vp_w + 15
        info_w = cax + caw - info_x - 8

        if self._mgr is None:
            self._init_windows()

        self._tabs.draw(surface, fonts)

        vc = cfg.YELLOW if self.flash > 0 else cfg.WHITE
        rows_info = [
            ("Window-Viewport",          cfg.ORANGE),
            ("",                         cfg.WHITE),
            ("Janela (mundo):",          cfg.GREEN),
            (f" xmin={xwmin:.0f}",       vc),
            (f" xmax={xwmax:.0f}",       vc),
            (f" ymin={ywmin:.0f}",       vc),
            (f" ymax={ywmax:.0f}",       vc),
            ("",                         cfg.WHITE),
            ("Viewport (tela):",         cfg.ORANGE),
            (f" {vp_w}x{vp_h} px",      cfg.WHITE),
            ("",                         cfg.WHITE),
            ("[Setas] mover janela",      cfg.YELLOW),
            ("[W/S] altura janela",       cfg.YELLOW),
            ("[A/D] largura janela",      cfg.YELLOW),
            ("[R] Reset",                cfg.YELLOW),
        ]
        rows_code = [
            ("def w2v(xw, yw):",          cfg.WHITE),
            ("  sx=(xvmax-xvmin)/",       cfg.WHITE),
            ("     (xwmax-xwmin)",        cfg.WHITE),
            ("  sy=(yvmax-yvmin)/",       cfg.WHITE),
            ("     (ywmax-ywmin)",        cfg.WHITE),
            ("  xv=xvmin+(xw-xwmin)*sx", cfg.WHITE),
            ("  yv=yvmax-(yw-ywmin)*sy", cfg.WHITE),
            ("  return int(xv),int(yv)",  cfg.WHITE),
        ]
        def _content(win, surf):
            if   win is self._win_info: draw_rows_in_win(surf, win, rows_info)
            elif win is self._win_code: draw_rows_in_win(surf, win, rows_code)
        self._mgr.draw_managed(surface, fonts, _content)


