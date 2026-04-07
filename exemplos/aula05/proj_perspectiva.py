"""
============================================================
 exemplos/aula05/proj_perspectiva.py

 Exemplo interativo: Projecao em Perspectiva

 Demonstra:
  - Cubo 3D com projecao perspectiva real
  - Ponto de fuga visivel
  - Slider interativo para distancia focal (d)
  - Comparacao lado a lado: Ortogonal vs Perspectiva
  - Formula: xv = d*x/z,  yv = d*y/z

 Controles:
  - Setas cima/baixo: aumentar/diminuir distancia focal d
  - Setas esq/dir:    rotacionar Y
  - ESPACO:           rotacao automatica
  - R:                resetar
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
from exemplos.aula05.proj_ortogonal import (CUBE_VERTS, CUBE_EDGES,
                                             rot_x, rot_y)



class ExProjPerspectiva(ExemploBase):
    NAME  = "Proj. Perspectiva"
    COLOR = cfg.ORANGE

    def __init__(self):
        super().__init__()
        self.angle_x   = 0.3
        self.angle_y   = 0.5
        self.dist_d    = 3.0     # distancia focal
        self.auto_spin = False
        self.flash     = 0.0
        self._mgr      = None
        self._teoria   = DocView(cfg.root_path("teoria", "Aula_05", "proj_perspectiva.pdf"))
        self._teoria.set_tab_offset(TAB_H)
        self._tabs     = TabBar(["Demonstração", "Teoria"])


    def _init_windows(self):
        cax, cay, caw, cah = cfg.canvas_rect()
        cay += TAB_H; cah -= TAB_H
        self._mgr = WindowManager(cfg.canvas_rect_tabs)
        self._win_info = self._mgr.create("Perspectiva vs Ortogonal",
            cax+10, cay+10, 260, 300, color=(180,80,20), closable=False)
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
        self.angle_x   = 0.3
        self.angle_y   = 0.5
        self.dist_d    = 3.0
        self.auto_spin = False

    def toggle_anim(self):
        self.auto_spin = not self.auto_spin

    def handle_action(self, action):
        if   action == 'toggle_anim': self.toggle_anim()
        elif action == 'reset':       self.reset()
        elif action == 'inc':
            self.dist_d = min(self.dist_d + 0.2, 12.0); self.flash = 0.3
        elif action == 'dec':
            self.dist_d = max(self.dist_d - 0.2,  0.5); self.flash = 0.3
        elif action == 'inc_alt':
            self.angle_y += math.radians(5)
        elif action == 'dec_alt':
            self.angle_y -= math.radians(5)

    def update(self, dt):
        if self.auto_spin:
            self.angle_y += 0.7 * dt
            self.angle_x += 0.2 * dt
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)

    def _project(self, verts, cx, cy, scale, d):
        pts = []
        for x, y, z in verts:
            dz = z + d + 2    # afasta o objeto da camera
            if abs(dz) < 0.01:
                dz = 0.01
            xp = int(cx + (d * x / dz) * scale)
            yp = int(cy - (d * y / dz) * scale)
            pts.append((xp, yp))
        return pts

    def _project_ortho(self, verts, cx, cy, scale):
        return [(int(cx + v[0]*scale), int(cy - v[1]*scale))
                for v in verts]

    def draw(self, surface, fonts):
        cr  = cfg.canvas_rect()
        cax, cay, caw, cah = cr

        # Fundo já pintado pelo _draw() principal

        # Ajusta área de conteúdo abaixo das abas
        drx, dry, drw, drh = cfg.draw_rect()
        dry += TAB_H; drh -= TAB_H
        cax = drx; cay = dry
        caw = drw; cah = drh

        # Rotacionar vertices
        verts = list(CUBE_VERTS)
        verts = rot_x(verts, self.angle_x)
        verts = rot_y(verts, self.angle_y)

        half_w = int(caw * 0.48)
        pad    = 10
        scale  = int(min(caw, cah) * 0.22)

        # ── Painel ORTOGONAL (esquerda) ──────────────────
        ox = cax + pad
        oy = cay + pad
        ow = half_w
        oh = cah - 20

        pygame.draw.rect(surface, cfg.BG2, (ox, oy, ow, oh))
        pygame.draw.rect(surface, cfg.BLUE, (ox, oy, ow, oh), 1)

        s = fonts['tab'].render("Ortogonal", True, cfg.BLUE)
        surface.blit(s, (ox + ow//2 - s.get_width()//2, oy + 8))

        # eixos
        cx_o = ox + ow // 2
        cy_o = oy + oh // 2
        pygame.draw.line(surface, cfg.GRAY2, (ox+10, cy_o), (ox+ow-10, cy_o), 1)
        pygame.draw.line(surface, cfg.GRAY2, (cx_o, oy+10), (cx_o, oy+oh-10), 1)

        pts_o = self._project_ortho(verts, cx_o, cy_o, scale)
        # arestas
        for a, b in CUBE_EDGES:
            depth = (verts[a][2] + verts[b][2]) / 2
            alpha = int(120 + 135 * (depth + 1.5) / 3)
            alpha = max(80, min(255, alpha))
            pygame.draw.line(surface, cfg.BLUE, pts_o[a], pts_o[b], 2)

        # linhas de projecao paralelas (so nos vertices frontais)
        proj_top = oy + 35
        for i, (px, py) in enumerate(pts_o):
            for t in range(0, 6, 2):
                ty = py - t * 8
                if ty > proj_top:
                    pygame.draw.circle(surface, (*cfg.GRAY2, 50),
                                       (px, ty), 1)

        # label formula
        f = fonts['sm'].render("xv = x * E  |  yv = y * E", True, cfg.BLUE)
        surface.blit(f, (cx_o - f.get_width()//2, oy + oh - 30))
        f2 = fonts['sm'].render("(Z ignorado)", True, cfg.GRAY)
        surface.blit(f2, (cx_o - f2.get_width()//2, oy + oh - 16))

        # ── Painel PERSPECTIVA (direita) ──────────────────
        px_ = cax + pad + half_w + pad * 2
        py_ = cay + pad
        pw  = half_w
        ph  = cah - 20

        pygame.draw.rect(surface, cfg.BG2, (px_, py_, pw, ph))
        pygame.draw.rect(surface, cfg.ORANGE, (px_, py_, pw, ph), 1)

        s = fonts['tab'].render("Perspectiva", True, cfg.ORANGE)
        surface.blit(s, (px_ + pw//2 - s.get_width()//2, py_ + 8))

        cx_p = px_ + pw // 2
        cy_p = py_ + ph // 2

        pygame.draw.line(surface, cfg.GRAY2, (px_+10, cy_p), (px_+pw-10, cy_p), 1)
        pygame.draw.line(surface, cfg.GRAY2, (cx_p, py_+10), (cx_p, py_+ph-10), 1)

        pts_p = self._project(verts, cx_p, cy_p, scale, self.dist_d)

        # ponto de fuga
        pygame.draw.circle(surface, cfg.YELLOW, (cx_p, cy_p), 6)
        pygame.draw.circle(surface, cfg.BG2, (cx_p, cy_p), 4)
        draw_label(surface, "ponto de fuga",
                   cx_p + 8, cy_p - 16, fonts['sm'], cfg.YELLOW, cfg.BG2)

        # linhas convergindo ao ponto de fuga (tracejadas)
        for px_v, py_v in pts_p:
            for t in range(2, 9, 3):
                fx = int(cx_p + (px_v - cx_p) * t / 10)
                fy = int(cy_p + (py_v - cy_p) * t / 10)
                pygame.draw.circle(surface, (*cfg.YELLOW, 40), (fx, fy), 1)

        # arestas em perspectiva
        for a, b in CUBE_EDGES:
            pygame.draw.line(surface, cfg.ORANGE, pts_p[a], pts_p[b], 2)

        # slider distancia focal
        sl_x = px_ + 15
        sl_y = py_ + ph - 55
        sl_w = pw - 30
        d_norm = (self.dist_d - 0.5) / 11.5
        sl_pos = int(sl_x + d_norm * sl_w)

        pygame.draw.rect(surface, cfg.GRAY2,
                         (sl_x, sl_y + 8, sl_w, 4), border_radius=2)
        pygame.draw.rect(surface, cfg.ORANGE,
                         (sl_x, sl_y + 8, int(d_norm * sl_w), 4),
                         border_radius=2)
        pygame.draw.circle(surface, cfg.ORANGE, (sl_pos, sl_y + 10), 7)

        dc = cfg.YELLOW if self.flash > 0 else cfg.WHITE
        s_d = fonts['sm'].render(f"d = {self.dist_d:.1f}  (focal)", True, dc)
        surface.blit(s_d, (px_ + pw//2 - s_d.get_width()//2, sl_y - 14))

        f = fonts['sm'].render("xv=d*x/z  |  yv=d*y/z", True, cfg.ORANGE)
        surface.blit(f, (cx_p - f.get_width()//2, py_ + ph - 16))

        if self._mgr is None:
            self._init_windows()

        self._tabs.draw(surface, fonts)

        rows_info = [
            ("Perspectiva vs Ortogonal", cfg.ORANGE),
            ("",                        cfg.WHITE),
            ("d = distancia focal",     cfg.GRAY),
            ("d alto  -> menos persp.", cfg.GRAY),
            ("d baixo -> mais persp.",  cfg.GRAY),
            ("",                        cfg.WHITE),
            (f"d atual = {self.dist_d:.1f}", dc),
            ("",                        cfg.WHITE),
            ("[Cima/Baixo] ajustar d",  cfg.YELLOW),
            ("[Esq/Dir] rotacionar",    cfg.YELLOW),
            ("[ESP] auto-rotacao",      cfg.YELLOW),
        ]
        def _content(win, surf):
            if win is self._win_info: draw_rows_in_win(surf, win, rows_info)
        self._mgr.draw_managed(surface, fonts, _content)


